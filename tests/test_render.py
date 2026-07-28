from __future__ import annotations

import io
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from PIL import Image

from lupaxa.favicon_generator.icons import MASKABLE_ICON, PNG_ICONS
from lupaxa.favicon_generator.render import (
    CAIRO_DEPENDENCY_ERROR,
    generate_ico,
    generate_png_icons,
    load_svg_as_rgba,
    normalise_colour,
    prepare_source,
    render_icon,
    save_png,
    validate_hex_colour,
)


def test_normalise_colour_transparent_and_hex() -> None:
    assert normalise_colour("transparent") == (0, 0, 0, 0)
    assert normalise_colour("#FF0000") == (255, 0, 0, 255)


def test_normalise_colour_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid colour"):
        normalise_colour("not-a-colour")


def test_validate_hex_colour() -> None:
    assert validate_hex_colour("#aabbcc", "--theme-colour") == "#AABBCC"
    with pytest.raises(ValueError, match="--theme-colour"):
        validate_hex_colour("red", "--theme-colour")


def test_prepare_source_png(png_source: Path) -> None:
    image, is_svg = prepare_source(png_source)
    assert is_svg is False
    assert image.mode == "RGBA"
    assert image.size == (64, 64)


def test_prepare_source_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        prepare_source(tmp_path / "missing.png")


def test_prepare_source_directory(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a file"):
        prepare_source(tmp_path)


def test_render_icon_fit_modes(png_source: Path) -> None:
    source, _ = prepare_source(png_source)
    bg = (0, 0, 0, 0)
    for fit in ("contain", "cover", "stretch"):
        icon = render_icon(source, 32, 32, fit, bg, 0.0)
        assert icon.size == (32, 32)
        assert icon.mode == "RGBA"


def test_render_icon_with_padding(png_source: Path) -> None:
    source, _ = prepare_source(png_source)
    icon = render_icon(source, 100, 100, "contain", (255, 255, 255, 255), 0.1)
    assert icon.size == (100, 100)


def test_generate_png_and_ico(png_source: Path, tmp_path: Path) -> None:
    source, _ = prepare_source(png_source)
    bg = (0, 0, 0, 0)
    out = tmp_path / "out"
    out.mkdir()
    paths = generate_png_icons(source, out, "contain", bg, 0.0, overwrite=False)
    names = {path.name for path in paths}
    assert {spec.filename for spec in PNG_ICONS}.issubset(names)
    assert MASKABLE_ICON.filename in names
    with Image.open(out / MASKABLE_ICON.filename) as maskable:
        assert maskable.getpixel((0, 0))[3] == 255
    ico = generate_ico(source, out, "contain", bg, 0.0, overwrite=False)
    assert ico.name == "favicon.ico"
    assert ico.exists()


def test_save_png_overwrite_guard(png_source: Path, tmp_path: Path) -> None:
    source, _ = prepare_source(png_source)
    dest = tmp_path / "x.png"
    save_png(source, dest, overwrite=False)
    with pytest.raises(FileExistsError):
        save_png(source, dest, overwrite=False)
    save_png(source, dest, overwrite=True)


def _rgba_png_bytes(size: int = 32) -> bytes:
    buf = io.BytesIO()
    Image.new("RGBA", (size, size), (1, 2, 3, 255)).save(buf, format="PNG")
    return buf.getvalue()


def test_load_svg_with_patched_cairosvg(
    svg_source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_mod = types.ModuleType("cairosvg")
    fake_mod.svg2png = MagicMock(return_value=_rgba_png_bytes(128))
    monkeypatch.setitem(sys.modules, "cairosvg", fake_mod)

    image = load_svg_as_rgba(svg_source)

    assert image.mode == "RGBA"
    fake_mod.svg2png.assert_called_once()
    called_url = fake_mod.svg2png.call_args.kwargs["url"]
    assert called_url == svg_source.resolve().as_uri()


def test_load_svg_import_error(
    svg_source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setitem(sys.modules, "cairosvg", None)

    with pytest.raises(ValueError, match="cairosvg") as excinfo:
        load_svg_as_rgba(svg_source)

    assert str(excinfo.value) == CAIRO_DEPENDENCY_ERROR


def test_prepare_source_svg_mocked(
    svg_source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_mod = types.ModuleType("cairosvg")
    fake_mod.svg2png = MagicMock(return_value=_rgba_png_bytes())
    monkeypatch.setitem(sys.modules, "cairosvg", fake_mod)

    image, is_svg = prepare_source(svg_source)

    assert is_svg is True
    assert image.mode == "RGBA"


def test_load_svg_oserror_on_svg2png(
    svg_source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake_mod = types.ModuleType("cairosvg")
    fake_mod.svg2png = MagicMock(side_effect=OSError("libcairo missing"))
    monkeypatch.setitem(sys.modules, "cairosvg", fake_mod)

    with pytest.raises(ValueError, match="cairosvg") as excinfo:
        load_svg_as_rgba(svg_source)

    assert str(excinfo.value) == CAIRO_DEPENDENCY_ERROR


def test_generate_png_overwrite_guard(png_source: Path, tmp_path: Path) -> None:
    source, _ = prepare_source(png_source)
    out = tmp_path / "out"
    out.mkdir()
    bg = (255, 255, 255, 255)
    generate_png_icons(source, out, "contain", bg, 0.0, overwrite=False)
    with pytest.raises(FileExistsError):
        generate_png_icons(source, out, "contain", bg, 0.0, overwrite=False)
