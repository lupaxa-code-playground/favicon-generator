"""
Lupaxa favicon generator package.

Exposes a programmatic API and a CLI via :mod:`lupaxa.favicon_generator.cli`.
"""

from __future__ import annotations

from .exceptions import FaviconGeneratorError, InputError, OutputError
from .icons import ICO_SIZES, MASKABLE_ICON, PNG_ICONS, IconSpec
from .output import build_html, build_manifest
from .render import generate_ico, generate_png_icons, prepare_source, render_icon
from .version import get_version as version

__all__ = [
    "FaviconGeneratorError",
    "InputError",
    "OutputError",
    "IconSpec",
    "PNG_ICONS",
    "MASKABLE_ICON",
    "ICO_SIZES",
    "prepare_source",
    "render_icon",
    "generate_png_icons",
    "generate_ico",
    "build_html",
    "build_manifest",
    "version",
]
