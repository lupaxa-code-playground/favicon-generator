from __future__ import annotations

from pathlib import Path

import pytest

from lupaxa.favicon_generator.cli import main


def test_main_happy_path_png(
    png_source: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    out = tmp_path / "favicons"
    monkeypatch.setattr(
        "sys.argv",
        [
            "favicon-generator",
            str(png_source),
            "-o",
            str(out),
            "--name",
            "Demo",
            "--overwrite",
        ],
    )
    assert main() == 0
    captured = capsys.readouterr()
    assert "Generated" in captured.out
    assert (out / "favicon-16x16.png").exists()
    assert (out / "favicon.ico").exists()
    assert (out / "site.webmanifest").exists()
    assert (out / "favicon-links.html").exists()
    assert not (out / "favicon.svg").exists()


def test_main_no_optional_outputs(
    png_source: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "favicons"
    monkeypatch.setattr(
        "sys.argv",
        [
            "favicon-generator",
            str(png_source),
            "-o",
            str(out),
            "--no-ico",
            "--no-html",
            "--no-manifest",
            "--overwrite",
        ],
    )
    assert main() == 0
    assert (out / "icon-512.png").exists()
    assert not (out / "favicon.ico").exists()
    assert not (out / "site.webmanifest").exists()
    assert not list(out.glob("*.html"))


def test_main_missing_source(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        ["favicon-generator", str(tmp_path / "nope.png"), "-o", str(tmp_path / "o")],
    )
    assert main() == 1
    err = capsys.readouterr().err
    assert err.startswith("Error:")


def test_main_bad_padding(
    png_source: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "favicon-generator",
            str(png_source),
            "-o",
            str(tmp_path / "o"),
            "--padding",
            "0.9",
        ],
    )
    assert main() == 1
    assert "padding" in capsys.readouterr().err.lower()


def test_main_bad_theme_colour(
    png_source: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(
        "sys.argv",
        [
            "favicon-generator",
            str(png_source),
            "-o",
            str(tmp_path / "o"),
            "--theme-colour",
            "nope",
        ],
    )
    assert main() == 1
    assert "Error:" in capsys.readouterr().err
