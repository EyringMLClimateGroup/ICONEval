"""Collect all plots of an ESMValTool output directory in a single PDF."""

from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import fire
import yaml
from loguru import logger
from prov.model import ProvDocument, ProvEntity
from pylatex import (
    Command,
    Document,
    Figure,
    Itemize,
    NewPage,
    NoEscape,
    Package,
    Subsection,
)
from pylatex.base_classes import CommandBase

from iconeval._logging import configure_logging

if TYPE_CHECKING:
    from collections.abc import Iterable

logger = logger.opt(colors=True)

SEP = "__"  # string that replaces dots in filenames not supported by pylatex
SUPPORTED_FILE_TYPES = ["png", "pdf"]
GEOMETRY_OPTIONS = {
    "top": "2.0cm",
    "bottom": "2.0cm",
    "left": "2.0cm",
    "right": "2.0cm",
}


def plots2pdf(
    input_dir: str | Path,
    log_level: str = "info",
    ignore: str | Iterable[str] | None = None,
    max_figures: int | None = None,
    output_dir: str | Path | None = None,
    *,
    save_tex: bool = False,
    overwrite: bool = False,
    setup_logging: bool = True,
) -> Path:
    """Collect ESMValTool plots in a single PDF.

    Collect all plots of an ESMValTool output directory (considering all
    subdirectories) in a single PDF (one page per figure). If provenance
    information is specified, use this to create captions for the figures.

    Note
    ----
    Currently supported file types for the plots: `png`, `pdf`.

    Parameters
    ----------
    input_dir:
        ESMValTool output directory used as input directory for this script.
        This is the directory that contains the `run`, `preproc`, `work`, and
        `plots` subdirectories.
    log_level:
        Log level. Must be one of `debug`, `info`, `warning`, `error`.
    ignore:
        Ignore files. Unix shell-style wildcards like `*` are allowed. If
        `None`, no files are ignored. To ignore multiple patterns use the
        syntax `--ignore='("*/pattern1.pdf", "pattern2/*.png")'` and pay
        attention to the quotes.
    max_figures:
        Maximum number of figures included in the PDF. If `None`, consider all
        figures.
    output_dir:
        Output directory where the output (PDF and TEX) is stored. If `None`
        use the current working directory.
    save_tex:
        If `True`, save TEX file in addition to PDF; if `False`, only save PDF.
    overwrite:
        If `True`, overwrite existing PDF and/or TEX files; if `False`, do not
        overwrite any existing file.
    setup_logging:
        If `True`, set up new logging handlers; if `False`, skip that step.

    Returns
    -------
    :
        Path of the resulting PDF document.

    Raises
    ------
    FileExistsError
        Output directory already contains output PDF file (and/or TEX file if
        ``save_tex=True``) and ``overwrite=False``.
    ValueError
        Log level not supported or no valid plots found.

    """
    # Setup logging
    if setup_logging:
        configure_logging(log_level)

    # Resolve input directory
    input_dir = Path(input_dir).expanduser().resolve()
    logger.debug(f"Creating PDF for input directory {input_dir}")

    # Resolve output directory and make sure that directory exists and files do
    # not exist
    if output_dir is None:
        output_dir = Path.cwd()
    output_dir = Path(output_dir).expanduser().resolve()
    logger.debug(f"Writing output to {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / input_dir.stem
    pdf_file = output_dir / f"{input_dir.stem}.pdf"
    tex_file = output_dir / f"{input_dir.stem}.tex"
    if pdf_file.exists():
        if not overwrite:
            msg = (
                f"PDF file {pdf_file} already exists, remove it before "
                f"running this script or use --overwrite=True"
            )
            raise FileExistsError(msg)
        logger.info(
            f"Overwriting existing file {pdf_file} since --overwrite=True",
        )
    if save_tex and tex_file.exists():
        if not overwrite:
            msg = (
                f"TEX file {tex_file} already exists, remove it before "
                f"running this script or use --overwrite=True"
            )
            raise FileExistsError(msg)
        logger.info(
            f"Overwriting existing file {tex_file} since --overwrite=True",
        )

    # Setup other command line arguments
    if ignore is None:
        ignore = []
    elif isinstance(ignore, str):
        ignore = [ignore]
    if ignore:
        logger.debug(
            f"Ignoring files that match at least one of the following "
            f"patterns: {ignore}",
        )
    if max_figures is not None:
        logger.debug(f"Including at most {max_figures} figures into the PDF")

    # Get plot files and recipe information
    all_plot_files = _get_all_plot_files(input_dir, ignore, max_figures)
    recipe_info = _get_recipe_info(input_dir)

    # Create PDF
    document = _create_document(input_dir, all_plot_files, recipe_info)

    # Save PDF (and TEX if desired)
    logger.debug("Creating PDF")
    silent = log_level != "debug"
    document.generate_pdf(output_file, clean_tex=not save_tex, silent=silent)
    logger.info(f"Saved <cyan>{pdf_file}</cyan>")
    if save_tex:
        logger.info(f"Saved <cyan>{tex_file}</cyan>")

    return pdf_file


class _SeqsplitCommand(CommandBase):
    """Allow linebreaks in long character sequences (e.g., paths)."""

    _latex_name: str = "seqsplit"
    packages: ClassVar = [Package("seqsplit")]


def _create_document(
    input_dir: Path,
    all_plot_files: dict[str | Path, dict],
    recipe_info: dict[str, Any],
) -> Document:
    """Create :class:`pylatex.Document`.

    Parameters
    ----------
    input_dir:
        ESMValTool output directory used as input directory for this script.
    all_plot_files:
        Paths to plots (keys) with additional metadata for each plot read from
        provenance information (:obj:`dict`; values).
    recipe_info:
        Recipe information. Should include the key ``title``; may include the
        keys ``description``, ``authors``, ``maintainer`, ``references``,
        ``projects``.

    Returns
    -------
    :
        Output document.

    """
    doc = Document(geometry_options=GEOMETRY_OPTIONS)

    # Write doc
    _write_header(doc, recipe_info, input_dir)
    _write_figures(doc, all_plot_files, input_dir)

    return doc


def _get_all_plot_files(
    input_dir: Path,
    ignore: Iterable[str],
    max_figures: int | None = None,
) -> dict[str | Path, dict]:
    """Recursively retrieve all plot files.

    Note
    ----
    This function ignores symbolic links to plot files created by this tool in
    earlier runs. This symbolic links are created in :func:`_write_figures`
    since :mod:`pylatex` has troubles with dots in image file names. As a
    workaround, a symbolic link to each plot file is created that does not
    contain dots.

    Parameters
    ----------
    input_dir:
        ESMValTool output directory used as input directory for this script.
    ignore:
        Ignore files (Unix shell-style wildcards like * are allowed). If an
        empty :obj:`list` is given, no files are ignored.
    max_figures:
        Maximum number of figures included in the PDF. If ``None``, consider
        all figures.

    Returns
    -------
    :
        Paths to plots (keys) with additional metadata for each plot read from
        provenance information (:obj:`dict`; values).

    """
    logger.debug(f"Searching for all plots in {input_dir}")
    all_plot_files: dict[str | Path, dict] = {}

    # Iterate over all allowed file types
    for file_type in SUPPORTED_FILE_TYPES:
        all_files = sorted(input_dir.rglob(f"*.{file_type}"))
        logger.debug(
            f"Found {len(all_files)} '{file_type}' file(s) prior to ignore",
        )

        # Iterate over all files
        for file in all_files:
            # Skip ignored files
            for pattern in ignore:
                if fnmatch(file, pattern):  # type: ignore[type-var]
                    skip_file = True
                    break
            else:
                skip_file = False
            if skip_file:
                continue

            # Skip symlinks created by this tool in earlier runs
            skip_file = all(
                [
                    file.is_symlink(),
                    _replace_sep(file) != file,
                    _replace_sep(file) in all_files,
                ],
            )
            if skip_file:
                logger.debug(
                    f"Ignored symbolic link {file} that has been created by this "
                    f"tool in an earlier run",
                )
                continue

            # Read provenance information for each plot file if possible
            prov_file = file.with_name(file.stem + "_provenance.xml")
            prov_info = {}
            if prov_file.exists():
                provenance = ProvDocument.deserialize(prov_file, format="xml")

                # Due to unresolved paths in the provenance record the
                # identifier of the plot file can be different from the path we
                # found here. For this reason we only use the relative path
                # (relative to the input directory) to check for the
                # provenance record.
                rel_file = file.relative_to(input_dir)
                for record in provenance.get_records(ProvEntity):
                    if str(rel_file) in str(record.identifier):
                        prov_attributes = record.attributes
                        break
                else:
                    prov_attributes = []
                for attr, value in prov_attributes:
                    prov_info[attr.localpart] = value

            all_plot_files[str(file)] = prov_info

            # Stop if maximum number of plots is reached
            if max_figures is not None and len(all_plot_files) >= max_figures:
                logger.info(
                    f"Maximum number of figures ({max_figures}) reached, skipping all "
                    "remaining plots",
                )
                break

        # Do not consider other file types if maximum number of plots is
        # reached
        if max_figures is not None and len(all_plot_files) >= max_figures:
            break

    logger.info(
        f"Found {len(all_plot_files)} plot file(s) in total (after ignoring)",
    )

    return all_plot_files


def _get_recipe_file(input_dir: Path) -> Path | None:
    """Get recipe file from ESMValTool output directory."""
    recipe_files = list(input_dir.rglob("recipe_*.yml"))

    # More recent versions of ESMValTool also save a "_filled" version of the
    # original recipe. This is fine; both versions of the recipe can be used
    if len(recipe_files) == 2:  # noqa: PLR2004
        recipe_name_0 = recipe_files[0].stem
        recipe_name_1 = recipe_files[1].stem
        filled_version_available = any(
            [
                recipe_name_0 == f"{recipe_name_1}_filled",
                recipe_name_1 == f"{recipe_name_0}_filled",
            ],
        )
        if filled_version_available:
            recipe_files = recipe_files[0:1]

    # Issue warning if not exactly one recipe has been found
    if len(recipe_files) == 1:
        logger.debug(
            f"Found recipe file {recipe_files[0]} to determine header of PDF",
        )
        return recipe_files[0]
    logger.warning(
        f"Expected exactly 1 recipe file (using pattern 'recipe_*.yml'), found "
        f"{len(recipe_files)}: {recipe_files}. Cannot determine header of PDF",
    )
    return None


def _get_recipe_info(input_dir: Path) -> dict[str, Any]:
    """Get information from recipe file.

    Note
    ----
    Uses pattern ``recipe_*.yml`` to find recipes.

    Parameters
    ----------
    input_dir:
        ESMValTool output directory used as input directory for this script.

    Returns
    -------
    :
        Recipe information. Includes the key ``title``; may include the keys
        ``description``, ``authors``, ``maintainer`, ``references``,
        ``projects``.

    """
    recipe_file = _get_recipe_file(input_dir)

    # Collect recipe information
    recipe_info = {}
    if recipe_file is None:
        recipe_info["title"] = input_dir.name
    else:
        with recipe_file.open(encoding="utf-8") as file:
            recipe = yaml.safe_load(file)
        recipe_info.update(recipe["documentation"])

    # Strip additional whitespace from strings
    for key, val in recipe_info.items():
        if isinstance(val, str):
            recipe_info[key] = val.replace("\n", "")
            recipe_info[key] = recipe_info[key].strip()

    return recipe_info


def _replace_dots(path: str | Path) -> str | Path:
    """Replace dots in file names with SEP."""
    if isinstance(path, str):
        return path.replace(".", SEP)
    return path.parent / f"{path.stem.replace('.', SEP)}{path.suffix}"


def _replace_sep(path: str | Path) -> str | Path:
    """Replace SEP in file names with dots."""
    if isinstance(path, str):
        return path.replace(SEP, ".")
    return path.parent / f"{path.stem.replace(SEP, '.')}{path.suffix}"


def _write_figures(
    doc: Document,
    all_plot_files: dict[str | Path, dict],
    input_dir: Path,
) -> None:
    """Write figures for PDF.

    Note
    ----
    :mod:`pylatex` has troubles with dots in image file names. As a workaround,
    a symbolic link to each plot file is created that does not contain dots.

    """
    # Iterate over all plots
    for plot_file, plot_info in all_plot_files.items():
        plot_file = Path(plot_file).resolve()
        plot_name = plot_file.name
        rel_path = plot_file.relative_to(input_dir)

        # Create symlink for paths that include dots (pylatex cannot handle
        # them properly)
        symlink_name = _replace_dots(plot_file)
        if symlink_name != plot_name:  # path includes dots
            plot_file_tex = Path(plot_file.parent) / symlink_name
            if not plot_file_tex.exists():
                plot_file_tex.symlink_to(Path(plot_file.name))
                logger.debug(
                    f"Created symbolic link {plot_file_tex} for file {plot_file} "
                    f"that includes dots in file name",
                )
        else:  # path does not include dots
            plot_file_tex = plot_file

        # Create plots
        with doc.create(Figure(position="h!")) as figure:
            figure.add_image(
                str(plot_file_tex),
                width=NoEscape(r"\textwidth"),
            )
            caption = plot_info.get("caption", plot_name)
            figure.add_caption(caption)
        doc.append(Command("vspace", "1cm"))
        doc.append("Path to plot:\n")
        doc.append(Command("ttfamily"))
        doc.append(_SeqsplitCommand(f"$ROOT/{rel_path!s}"))
        doc.append(Command("rmfamily"))

        # Use new page for each plot
        doc.append(NewPage())


def _write_header(
    doc: Document,
    recipe_info: dict[str, Any],
    input_dir: Path,
) -> None:
    """Write header of PDF."""
    doc.preamble.append(Command("title", recipe_info["title"]))
    doc.preamble.append(Command("date", NoEscape(r"PDF created on \today")))
    doc.append(NoEscape(r"\maketitle"))
    if "description" in recipe_info:
        doc.append(recipe_info["description"])
    with doc.create(Subsection("Root Directory", numbering=False)):
        doc.append(Command("ttfamily"))
        doc.append(_SeqsplitCommand(f"ROOT={input_dir!s}"))
        doc.append(Command("rmfamily"))
    if "authors" in recipe_info:
        with (
            doc.create(Subsection("Recipe Authors", numbering=False)),
            doc.create(Itemize()) as itemize,
        ):
            for author in recipe_info["authors"]:
                itemize.add_item(author)
    if "references" in recipe_info:
        with (
            doc.create(Subsection("References", numbering=False)),
            doc.create(Itemize()) as itemize,
        ):
            for ref in recipe_info["references"]:
                itemize.add_item(ref)
    if "projects" in recipe_info:
        with (
            doc.create(Subsection("Projects", numbering=False)),
            doc.create(Itemize()) as itemize,
        ):
            for project in recipe_info["projects"]:
                itemize.add_item(project)
    doc.append(NewPage())


def main() -> None:
    """Invoke ``fire`` to process command line arguments."""
    logger.remove()  # remove any potential handlers
    fire.Fire(plots2pdf)


if __name__ == "__main__":
    main()
