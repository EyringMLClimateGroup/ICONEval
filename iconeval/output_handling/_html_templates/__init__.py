"""Manage jinja2 templates."""

from __future__ import annotations

from typing import Any

from jinja2 import Environment, PackageLoader

# Use Jinja2's PackageLoader which works with importlib.resources
_LOADER = PackageLoader("iconeval.output_handling", package_path="_html_templates")
_ENV = Environment(autoescape=True, loader=_LOADER)


def render_template(template_name: str, **context: Any) -> str:
    """Render a Jinja2 template with the given context."""
    template = _ENV.get_template(template_name)
    return template.render(**context)
