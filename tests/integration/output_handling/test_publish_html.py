from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import call

import pytest
import requests
from swiftclient.service import ClientException, SwiftError

import iconeval.output_handling.publish_html
from iconeval.output_handling.publish_html import main, publish_esmvaltool_html
from tests.integration import assert_output, copy_to_tmp_path

if TYPE_CHECKING:
    from unittest.mock import Mock

    import pytest_mock


def test_main(mocker: pytest_mock.MockerFixture) -> None:
    mocked_logger = mocker.patch.object(iconeval.output_handling.publish_html, "logger")
    mocked_fire = mocker.patch.object(iconeval.output_handling.publish_html, "fire")
    main()
    mocked_logger.remove.assert_called_once_with()
    mocked_fire.Fire.assert_called_once_with(publish_esmvaltool_html)


def test_publish_esmvaltool_html_multiple_recipes(
    sample_data_path: Path,
    mocked_requests: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    tmp_path: Path,
) -> None:
    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        url = publish_esmvaltool_html(esmvaltool_output, log_file=None)
        expected_dir_contents = list(esmvaltool_output.rglob("*"))

    assert (
        url == "url/to/swift_storage/my_folder/iconeval/recipes_zonal-means/index.html"
    )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_called_once_with(
        "url/to/swift_storage/my_folder",
        "this_is_a_very_nice_token",
    )
    mocked_swift_service.assert_any_call(
        {
            "os_auth_token": "this_is_a_very_nice_token",
            "os_storage_url": "url/to/swift_storage/my_folder",
        },
    )
    mocked_service_instance = mocked_swift_service.return_value.__enter__.return_value
    assert mocked_service_instance.post.mock_calls == [
        call(container="iconeval"),
        call(container="iconeval", options={"read_acl": ".r:*"}),
    ]
    assert mocked_service_instance.upload.call_count == 1
    upload_call = mocked_service_instance.upload.mock_calls[0]
    assert upload_call.args == ()
    assert len(upload_call.kwargs) == 2  # noqa: PLR2004
    assert upload_call.kwargs["container"] == "iconeval"
    objects_to_upload = [
        (str(f), str(Path("recipes_zonal-means") / f.relative_to(esmvaltool_output)))
        for f in expected_dir_contents
    ]
    assert set(upload_call.kwargs["objects"]) == set(objects_to_upload)


def test_publish_esmvaltool_html_single_recipe(
    sample_data_path: Path,
    mocked_requests: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    tmp_path: Path,
) -> None:
    sample_dir = (
        sample_data_path
        / "esmvaltool_output"
        / "recipes_zonal-means"
        / "recipe_basics_zonal_mean_lines_20260318_093429"
    )

    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        url = publish_esmvaltool_html(esmvaltool_output, log_file=None)
        expected_dir_contents = list(esmvaltool_output.rglob("*"))

    assert (
        url == "url/to/swift_storage/my_folder/iconeval/"
        "recipe_basics_zonal_mean_lines_20260318_093429/index.html"
    )

    mocked_requests.get.assert_not_called()
    mocked_swift_head_account.assert_called_once_with(
        "url/to/swift_storage/my_folder",
        "this_is_a_very_nice_token",
    )
    mocked_swift_service.assert_any_call(
        {
            "os_auth_token": "this_is_a_very_nice_token",
            "os_storage_url": "url/to/swift_storage/my_folder",
        },
    )
    mocked_service_instance = mocked_swift_service.return_value.__enter__.return_value
    assert mocked_service_instance.post.mock_calls == [
        call(container="iconeval"),
        call(container="iconeval", options={"read_acl": ".r:*"}),
    ]
    assert mocked_service_instance.upload.call_count == 1
    upload_call = mocked_service_instance.upload.mock_calls[0]
    assert upload_call.args == ()
    assert len(upload_call.kwargs) == 2  # noqa: PLR2004
    assert upload_call.kwargs["container"] == "iconeval"
    objects_to_upload = [
        (
            str(f),
            str(
                Path("recipe_basics_zonal_mean_lines_20260318_093429")
                / f.relative_to(esmvaltool_output),
            ),
        )
        for f in expected_dir_contents
    ]
    assert set(upload_call.kwargs["objects"]) == set(objects_to_upload)


def test_publish_esmvaltool_html_files_to_large(
    sample_data_path: Path,
    caplog: pytest.LogCaptureFixture,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Avoid overwriting existing tokens
    swift_token = tmp_path / "swift" / "swiftenv"
    swift_token.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(iconeval.output_handling.publish_html, "SWIFTENV", swift_token)

    # Make all files to large
    monkeypatch.setattr(
        iconeval.output_handling.publish_html,
        "MAX_FILE_SIZE_FOR_UPLOAD",
        -1,
    )

    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"

    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        url = publish_esmvaltool_html(esmvaltool_output, log_file=None)

    assert url == "my-x-storage-url/iconeval/recipes_zonal-means/index.html"

    mocked_requests.get.assert_called_once_with(
        "url/to/swift_storage/auth/v1.0",
        headers={
            "X-Auth-User": "user input:user input",
            "X-Auth-Key": "super secret password",
        },
        timeout=30,
    )
    mocked_swift_head_account.assert_not_called()
    mocked_swift_service.assert_any_call(
        {
            "os_auth_token": "my-x-auth-token",
            "os_storage_url": "my-x-storage-url",
        },
    )
    mocked_service_instance = mocked_swift_service.return_value.__enter__.return_value
    assert mocked_service_instance.post.mock_calls == [
        call(container="iconeval"),
        call(container="iconeval", options={"read_acl": ".r:*"}),
    ]
    mocked_service_instance.upload.assert_called_once_with(
        container="iconeval",
        objects=[],
    )

    # Check logging output
    assert "(> 4.5 GB)" in caplog.text


def test_publish_esmvaltool_html_force(
    pytestconfig: pytest.Config,
    expected_output_dir: Path,
    sample_data_path: Path,
    tmp_path: Path,
    mocked_requests: Mock,
    mocked_swift_head_account: Mock,
    mocked_swift_service: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        # Do not overwrite existing swiftenv sample file, copy existing token to
        # make sure it is overwritten by force_new_token=True
        swift_token = esmvaltool_output / "swiftenv"
        shutil.copy(sample_data_path / "swift" / "swiftenv", swift_token)
        monkeypatch.setattr(
            iconeval.output_handling.publish_html,
            "SWIFTENV",
            swift_token,
        )

        url = publish_esmvaltool_html(
            esmvaltool_output,
            container_name="my_container",
            dir_name="my_dir",
            log_level="debug",
            log_file=None,
            summary_description="this is a nice summary of the output",
            force_new_token=True,
        )
        expected_dir_contents = list(esmvaltool_output.rglob("*"))

    assert url == "my-x-storage-url/my_container/my_dir/index.html"

    # Check mock calls
    mocked_requests.get.assert_called_once_with(
        "url/to/swift_storage/auth/v1.0",
        headers={
            "X-Auth-User": "user input:user input",
            "X-Auth-Key": "super secret password",
        },
        timeout=30,
    )
    mocked_swift_head_account.assert_not_called()
    mocked_swift_service.assert_any_call(
        {
            "os_auth_token": "my-x-auth-token",
            "os_storage_url": "my-x-storage-url",
        },
    )
    mocked_service_instance = mocked_swift_service.return_value.__enter__.return_value
    assert mocked_service_instance.post.mock_calls == [
        call(container="my_container"),
        call(container="my_container", options={"read_acl": ".r:*"}),
    ]
    assert mocked_service_instance.upload.call_count == 1
    upload_call = mocked_service_instance.upload.mock_calls[0]
    assert upload_call.args == ()
    assert len(upload_call.kwargs) == 2  # noqa: PLR2004
    assert upload_call.kwargs["container"] == "my_container"
    objects_to_upload = [
        (str(f), str(Path("my_dir") / f.relative_to(esmvaltool_output)))
        for f in expected_dir_contents
    ]
    assert set(upload_call.kwargs["objects"]) == set(objects_to_upload)

    # Check output; for this, we remove the previously created subdirectories
    assert oct(swift_token.stat().st_mode)[-3:] == "600"
    assert_output(
        tmp_path,
        esmvaltool_output,
        expected_output_dir / "test_publish_esmvaltool_html_force",
        generate_expected_output=pytestconfig.getoption("generate_expected_output"),
    )


def test_publish_esmvaltool_html_no_dir_fail(
    sample_data_path: Path,
    tmp_path: Path,
) -> None:
    esmvaltool_output = sample_data_path / "esmvaltool_output" / "non_existing_dir"
    msg = r"is not a directory"
    with pytest.raises(NotADirectoryError, match=re.escape(msg)):
        publish_esmvaltool_html(esmvaltool_output, log_file=None)


def test_publish_esmvaltool_invalid_token_fail(
    sample_data_path: Path,
    tmp_path: Path,
    mocked_requests: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Force creating new token by using expired token. Copy expired token to
    # temporary location to avoid overwriting existing files.
    swift_token = tmp_path / "swift" / "swiftenv"
    swift_token.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(sample_data_path / "swift" / "expired_swiftenv", swift_token)
    monkeypatch.setattr(iconeval.output_handling.publish_html, "SWIFTENV", swift_token)

    # Raise error when token is created
    mocked_requests.get.return_value.headers["x-auth-token"] = None

    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        msg = r"Failed to create new swift token"
        with pytest.raises(ValueError, match=re.escape(msg)):
            publish_esmvaltool_html(esmvaltool_output, log_file=None)


def test_publish_esmvaltool_invalid_request_fail(
    sample_data_path: Path,
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    mocked_requests: Mock,
    mocked_swift_head_account: Mock,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Do not overwrite existing swiftenv sample file
    swift_token = tmp_path / "swift" / "swiftenv"
    swift_token.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(sample_data_path / "swift" / "swiftenv", swift_token)
    monkeypatch.setattr(iconeval.output_handling.publish_html, "SWIFTENV", swift_token)

    # Raise error when checking token to force creation of new token
    mocked_swift_head_account.side_effect = ClientException("corrupted token")

    # Raise error when token is created
    mocked_requests.get.return_value.raise_for_status.side_effect = (
        requests.RequestException("failed request")
    )

    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        msg = r"Failed to create new swift token: failed request"
        with pytest.raises(requests.RequestException, match=re.escape(msg)):
            publish_esmvaltool_html(
                esmvaltool_output,
                log_file=None,
            )

    # Check logging output
    assert "is corrupted" in caplog.text


def test_publish_esmvaltool_upload_fail(
    sample_data_path: Path,
    mocked_swift_service: Mock,
    tmp_path: Path,
) -> None:
    mocked_service_instance = mocked_swift_service.return_value.__enter__.return_value
    mocked_service_instance.upload.return_value = [{"success": False, "error": 42}]

    sample_dir = sample_data_path / "esmvaltool_output" / "recipes_zonal-means"
    with copy_to_tmp_path(tmp_path, sample_dir) as esmvaltool_output:
        msg = r"Upload of {'success': False, 'error': 42} failed: 42"
        with pytest.raises(SwiftError, match=re.escape(msg)):
            publish_esmvaltool_html(
                esmvaltool_output,
                log_file=None,
            )
