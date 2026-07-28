from __future__ import annotations

from lupaxa.favicon_generator.version import __version__, get_version


def test_version_is_semver_like() -> None:
    assert __version__ == "0.1.0"
    assert get_version() == __version__
