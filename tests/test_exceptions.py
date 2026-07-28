from __future__ import annotations

import pytest

from lupaxa.favicon_generator.exceptions import (
    FaviconGeneratorError,
    InputError,
    OutputError,
)


def test_exception_hierarchy() -> None:
    assert issubclass(InputError, FaviconGeneratorError)
    assert issubclass(OutputError, FaviconGeneratorError)
    assert issubclass(FaviconGeneratorError, Exception)


def test_exceptions_are_raisable() -> None:
    with pytest.raises(InputError):
        raise InputError("bad input")
    with pytest.raises(OutputError):
        raise OutputError("bad output")
