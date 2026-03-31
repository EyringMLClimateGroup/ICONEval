"""Jinja2 template loader for HTML output."""

from __future__ import annotations

from importlib import resources

from jinja2 import Environment, FileSystemLoader

# Get the templates package
_templates_pkg = resources.files("iconeval.output_handling.templates")


def get_jinja_env() -> Environment:
    """Get a Jinja2 environment for HTML templates.

    Returns
    -------
        Jinja2 Environment configured to load templates from html/ directory
    """
    templates_dir = _templates_pkg.joinpath("html")

    # Create a FileSystemLoader that can handle package resources
    # We need to convert the package resources path to a string path
    try:
        # For installed packages, this works
        template_path = str(templates_dir)
        return Environment(autoescape=True, loader=FileSystemLoader(template_path))
    except OSError:
        # Fallback: use the package files directly
        return Environment(
            autoescape=True,
            loader=_PackageTemplateLoader(str(_templates_pkg)),
        )


class _PackageTemplateLoader:
    """Custom loader for package resources."""

    def __init__(self, package_path: str) -> None:
        """Initialize loader.

        Args:
            package_path: Path to the templates package
        """
        self.package_path = package_path

    def get_source(self, _environment: Environment, template: str) -> tuple:
        """Get template source.

        Args:
            _environment: Jinja2 environment (unused, required by interface)
            template: Template filename

        Returns
        -------
            Tuple of (source, path, uptodate_func)
        """
        template_file = _templates_pkg.joinpath("html", template)
        source = template_file.read_text(encoding="utf-8")
        return source, str(template_file), lambda: True


def render_template(template_name: str, **context: object) -> str:
    """Render a Jinja2 template with the given context.

    Args:
        template_name: Name of the template file
        **context: Variables to pass to the template

    Returns
    -------
        Rendered HTML string
    """
    env = get_jinja_env()
    template = env.get_template(template_name)
    return template.render(**context)
