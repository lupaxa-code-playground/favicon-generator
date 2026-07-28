"""Exception types for lupaxa.favicon_generator."""

from __future__ import annotations


class FaviconGeneratorError(Exception):
    """Base error for favicon generation failures."""


class InputError(FaviconGeneratorError):
    """Invalid or unsupported input (source image, colours, flags)."""


class OutputError(FaviconGeneratorError):
    """Output path conflicts or write failures."""
