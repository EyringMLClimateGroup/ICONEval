"""Publish ESMValTool results on public website using DKRZ's swift module."""

import logging
import time
from datetime import UTC, datetime
from getpass import getpass
from pathlib import Path

import fire
import requests
from loguru import logger
from swiftclient import ClientException
from swiftclient.client import head_account
from swiftclient.service import SwiftError, SwiftService, SwiftUploadObject

from iconeval._logging import configure_logging
from iconeval.output_handling._summarize import summarize

logger = logger.opt(colors=True)

_SWIFT_BASE = "https://swift.dkrz.de/"
_SWIFTENV = Path().home() / ".swiftenv"
_SWIFT = {}

_MAX_FILE_SIZE_FOR_UPLOAD = 4_500_000_000  # 4.5 GB


def publish_esmvaltool_html(
    esmvaltool_output_dir: str | Path,
    container_name: str | None = None,
    dir_name: str | None = None,
    log_level: str = "info",
    log_file: str | Path | None = "~/.iconeval/debug.log",
    summary_description: str | None = None,
    *,
    force_new_token: bool = False,
    force_new_summary: bool = False,
    setup_logging: bool = True,
) -> str:
    """Publish ESMValTool summary HTML on a **public** website using swift.

    This uses an ESMValTool utility function to create a summary HTML
    (https://docs.esmvaltool.org/en/latest/utils.html#overview-of-recipe-runs)
    and publishes this using DKRZ's Python-swiftclient
    (https://docs.dkrz.de/doc/datastorage/swift/python-swiftclient.html).

    Warning
    -------
    The resulting website will be publicly accessible (with a very complicated
    link, though)!

    Parameters
    ----------
    esmvaltool_output_dir:
        A directory that contains one or more ESMValTool output directories.
    container_name:
        Name of the swift container. If `None`, use `iconeval`.
    dir_name:
        Name of the partent directory in the swift container. If `None`, use
        the `esmvaltool_output_dir`.
    log_level:
        Log level. Must be one of `debug`, `info`, `warning`, `error`.
    log_file:
        File where ICONEval debug output is logged. If `None`, do not log to a
        file. New messages are attached to existing files.
    summary_description:
        Additional description for the summary HTML. Only used if
        `esmvaltool_output_dir` contains multiple ESMValTool output
        directories. Ignored otherwise.
    force_new_token:
        If `True`, force the creation of a new swift token; if `False`, reuse
        an existing one if possible.
    force_new_summary:
        If `True`, force the creation of a new summary HTML; if `False`, only
        create it if necessary.
    setup_logging:
        If `True`, set up new logging handlers; if `False`, skip that step
        (`log_level` and `log_file` are ignored in that case).

    Returns
    -------
    :
        Website URL.

    Raises
    ------
    ChildProcessError
        ESMValTool summary HTML creation failed.
    NotADirectoryError
        ``esmvaltool_output_dir`` is not a directory.
    requests.RequestException
        Swift token creation request failed.
    swiftclient.service.SwiftError
        Swift upload failed.
    ValueError
        Log level not supported.
    ValueError
        Swift token creation failed.

    """
    if setup_logging:
        configure_logging(log_level, log_file=log_file)

    esmvaltool_output_dir = Path(esmvaltool_output_dir).expanduser().resolve()
    if not esmvaltool_output_dir.is_dir():
        msg = f"'{esmvaltool_output_dir}' is not a directory"
        raise NotADirectoryError(msg)

    # Load swift token
    if force_new_token or not _valid_swift_token_available():
        _create_swift_token()
    _load_swiftenv()

    # Create summary HTML if necessary
    summary_file = esmvaltool_output_dir / "index.html"
    if force_new_summary or not summary_file.is_file():
        summarize(esmvaltool_output_dir, description=summary_description)
    else:
        logger.debug(
            f"Found existing {summary_file}, skipping creation of summary HTML",
        )

    # Publish summary HTML
    return _publish_html(
        esmvaltool_output_dir,
        container_name=container_name,
        dir_name=dir_name,
    )


def _create_swift_token() -> None:
    """Create new swift token.

    Taken from
    /sw/spack-levante/py-python-swiftclient-3.12.0-weclvr/bin/swift-token.

    """
    logger.info(f"Creating new swift token ({_SWIFTENV})")
    account = input("DKRZ account (can be username or project account): ")
    username = input("DKRZ username: ")
    password = getpass()

    expires = None
    token = None
    storage_url = None

    try:
        response = requests.get(
            _SWIFT_BASE + "auth/v1.0",
            headers={
                "X-Auth-User": f"{account}:{username}",
                "X-Auth-Key": password,
            },
            timeout=30,
        )
        response.raise_for_status()

        token = response.headers["x-auth-token"]
        storage_url = response.headers["x-storage-url"]
        expires_in = int(response.headers["x-auth-token-expires"])
        expires_at = datetime.fromtimestamp(time.time() + expires_in, tz=UTC)
        expires = expires_at.strftime("%a %d. %b %H:%M:%S UTC %Y")

        if expires and token and storage_url:
            _SWIFTENV.write_text(
                f"#token expires on: {expires}\n"
                f"setenv OS_AUTH_TOKEN {token}\n"
                f"setenv OS_STORAGE_URL {storage_url}\n"
                f'setenv OS_AUTH_URL " "\n'
                f'setenv OS_USERNAME " "\n'
                f'setenv OS_PASSWORD " "\n',
            )
            _SWIFTENV.chmod(0o600)
        else:
            msg = "Failed to create new swift token"
            raise ValueError(msg)
    except requests.RequestException as exc:
        msg = f"Failed to create new swift token: {exc}"
        raise requests.RequestException(msg) from exc
    else:
        logger.info(
            f"Successfully created new swift token (expires {expires})",
        )


def _load_swiftenv() -> None:
    """Load swiftenv into global SWIFT dict."""
    (token, url, _expire_dt) = _read_swiftenv()
    _SWIFT["TOKEN"] = token
    _SWIFT["OS_AUTH_TOKEN"] = token
    _SWIFT["OS_STORAGE_URL"] = url


def _publish_html(
    esmvaltool_output_dir: Path,
    container_name: str | None = None,
    dir_name: str | None = None,
) -> str:
    """Publish ESMValTool summary HTML using swift."""
    if container_name is None:
        container_name = "iconeval"
    if dir_name is None:
        dir_name = esmvaltool_output_dir.name

    logging.getLogger("swiftclient").setLevel(logging.WARNING)
    swift_opts = {
        "os_auth_token": _SWIFT["OS_AUTH_TOKEN"],
        "os_storage_url": _SWIFT["OS_STORAGE_URL"],
    }
    with SwiftService(swift_opts) as swift:
        logger.info("File upload started (this may take a while)")

        # Create container (will do nothing if that already exists)
        swift.post(container=container_name)

        # Upload all elements <= 4.5 GB (swift limits individual files to be <
        # 5 GB; segmenting does not work on the HTML output)
        files_to_upload = []
        for file in esmvaltool_output_dir.rglob("*"):
            if file.stat().st_size > _MAX_FILE_SIZE_FOR_UPLOAD:
                logger.warning(f"Ignoring {file} (> 4.5 GB)")
            else:
                files_to_upload.append(file)
        objects = [
            SwiftUploadObject(
                str(f),
                object_name=str(
                    Path(dir_name) / f.relative_to(esmvaltool_output_dir),
                ),
            )
            for f in files_to_upload
        ]
        uploads = swift.upload(container=container_name, objects=objects)
        for upload in uploads:
            if not upload["success"]:
                msg = f"Upload of {upload} failed: {upload['error']}"
                raise SwiftError(msg)

        # Make container publicly accessible
        swift.post(container=container_name, options={"read_acl": ".r:*"})

    logger.debug(
        f"Successfully uploaded contents of {esmvaltool_output_dir} to swift "
        f"container '{container_name}' under directory '{dir_name}'",
    )

    url = f"{_SWIFT['OS_STORAGE_URL']}/{container_name}/{dir_name}/index.html"
    logger.info(f"Published HTML to <cyan>{url}</cyan>")

    return url


def _read_swiftenv() -> tuple[str, str, datetime]:
    """Read .swiftenv file."""
    swiftenv_content = _SWIFTENV.read_text()
    swiftenv_lines = swiftenv_content.split("\n")

    expire_str = " ".join(swiftenv_lines[0].split(" ")[3:])
    expire_dt = datetime.strptime(expire_str, "%a %d. %b %H:%M:%S %Z %Y")

    token = " ".join(swiftenv_lines[1].split(" ")[2:3])
    url = " ".join(swiftenv_lines[2].split(" ")[2:3])

    return (token, url, expire_dt)


def _valid_swift_token_available() -> bool:
    """Check if valid swift token is available."""
    if not _SWIFTENV.is_file():
        logger.debug("No swift token available")
        return False

    (token, url, expire_dt) = _read_swiftenv()

    # Check expiration
    now = datetime.now()
    if now > expire_dt:
        logger.info(f"Swift token ({_SWIFTENV}) expired on {expire_dt}")
        return False

    # Check token itself
    try:
        head_account(url, token)
    except ClientException:
        logger.warning(f"Swift token ({_SWIFTENV}) is corrupted")
        return False

    return True


def main() -> None:
    """Invoke ``fire`` to process command line arguments."""
    logger.remove()  # remove any potential handlers
    fire.Fire(publish_esmvaltool_html)


if __name__ == "__main__":  # pragma: no cover
    main()
