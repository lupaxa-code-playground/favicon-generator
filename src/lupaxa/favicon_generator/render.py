"""Image loading and favicon raster generation."""

from __future__ import annotations

import io
import re
import shutil
from pathlib import Path
from typing import Final, cast

from PIL import Image, ImageColor, ImageOps, UnidentifiedImageError

from .icons import (
    ICO_SIZES,
    MASKABLE_EXTRA_PADDING,
    MASKABLE_ICON,
    PNG_ICONS,
)

SVG_RASTER_SIZE: Final[int] = 1024
CAIRO_DEPENDENCY_ERROR: Final[str] = (
    "SVG input requires cairosvg and the native Cairo library. Install with: "
    "python -m pip install cairosvg; macOS: brew install cairo; "
    "Debian/Ubuntu: apt install libcairo2"
)

HEX_COLOUR_PATTERN: Final[re.Pattern[str]] = re.compile(r"^#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?$")


def normalise_colour(value: str) -> tuple[int, int, int, int]:
    if value.lower() == "transparent":
        return (0, 0, 0, 0)

    try:
        rgb_or_rgba = cast(
            tuple[int, int, int, int],
            ImageColor.getcolor(value, "RGBA"),
        )
    except ValueError as exc:
        raise ValueError(
            f"Invalid colour {value!r}. Use 'transparent', a CSS colour name, "
            "or a value such as '#FFFFFF'."
        ) from exc

    return rgb_or_rgba


def validate_hex_colour(value: str, flag_name: str) -> str:
    if not HEX_COLOUR_PATTERN.fullmatch(value):
        raise ValueError(
            f"{flag_name} must be a six- or eight-digit hex colour, for example #FFFFFF."
        )
    return value.upper()


def load_svg_as_rgba(path: Path) -> Image.Image:
    try:
        import cairosvg
    except (ImportError, OSError) as exc:
        raise ValueError(CAIRO_DEPENDENCY_ERROR) from exc

    try:
        png_bytes = cairosvg.svg2png(
            url=path.resolve().as_uri(),
            output_width=SVG_RASTER_SIZE,
            output_height=SVG_RASTER_SIZE,
        )
    except OSError as exc:
        raise ValueError(CAIRO_DEPENDENCY_ERROR) from exc
    except Exception as exc:  # cairosvg raises various errors per SVG
        raise ValueError(f"Failed to render SVG: {path}: {exc}") from exc

    if not png_bytes:
        raise ValueError(f"Failed to render SVG (empty output): {path}")

    with Image.open(io.BytesIO(png_bytes)) as image:
        image.load()
        converted: Image.Image = image.convert("RGBA")
        return converted


def prepare_source(path: Path) -> tuple[Image.Image, bool]:
    if not path.exists():
        raise FileNotFoundError(f"Source image does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Source path is not a file: {path}")

    if path.suffix.lower() == ".svg":
        return load_svg_as_rgba(path), True

    try:
        with Image.open(path) as image:
            image.load()
            image = ImageOps.exif_transpose(image)
            return image.convert("RGBA"), False
    except UnidentifiedImageError as exc:
        raise ValueError(f"Unsupported or invalid image file: {path}") from exc


def copy_favicon_svg(source: Path, output_dir: Path, overwrite: bool) -> Path:
    destination = output_dir / "favicon.svg"
    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {destination}. Use --overwrite to replace it."
        )
    shutil.copy2(source, destination)
    return destination


def inner_dimensions(
    width: int,
    height: int,
    padding: float,
) -> tuple[int, int]:
    inner_width = max(1, round(width * (1.0 - (padding * 2.0))))
    inner_height = max(1, round(height * (1.0 - (padding * 2.0))))
    return inner_width, inner_height


def render_icon(
    source: Image.Image,
    width: int,
    height: int,
    fit: str,
    background: tuple[int, int, int, int],
    padding: float,
) -> Image.Image:
    target = (width, height)
    inner_size = inner_dimensions(width, height, padding)
    canvas = Image.new("RGBA", target, background)

    if fit == "stretch":
        rendered = source.resize(inner_size, Image.Resampling.LANCZOS)
    elif fit == "cover":
        rendered = ImageOps.fit(
            source,
            inner_size,
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        )
    else:
        rendered = ImageOps.contain(
            source,
            inner_size,
            method=Image.Resampling.LANCZOS,
        )

    x = (width - rendered.width) // 2
    y = (height - rendered.height) // 2
    canvas.alpha_composite(rendered, (x, y))
    return canvas


def save_png(image: Image.Image, destination: Path, overwrite: bool) -> None:
    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {destination}. Use --overwrite to replace it."
        )

    image.save(destination, format="PNG", optimize=True)


def generate_png_icons(
    source: Image.Image,
    output_dir: Path,
    fit: str,
    background: tuple[int, int, int, int],
    padding: float,
    overwrite: bool,
) -> list[Path]:
    generated: list[Path] = []

    for spec in PNG_ICONS:
        destination = output_dir / spec.filename
        icon = render_icon(
            source=source,
            width=spec.width,
            height=spec.height,
            fit=fit,
            background=background,
            padding=padding,
        )
        save_png(icon, destination, overwrite)
        generated.append(destination)

    maskable_padding = min(0.45, padding + MASKABLE_EXTRA_PADDING)
    maskable_dest = output_dir / MASKABLE_ICON.filename
    maskable = render_icon(
        source=source,
        width=MASKABLE_ICON.width,
        height=MASKABLE_ICON.height,
        fit=fit,
        background=(255, 255, 255, 255) if background[3] == 0 else background,
        padding=maskable_padding,
    )
    save_png(maskable, maskable_dest, overwrite)
    generated.append(maskable_dest)

    return generated


def generate_ico(
    source: Image.Image,
    output_dir: Path,
    fit: str,
    background: tuple[int, int, int, int],
    padding: float,
    overwrite: bool,
) -> Path:
    destination = output_dir / "favicon.ico"

    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {destination}. Use --overwrite to replace it."
        )

    largest_width, largest_height = max(ICO_SIZES)
    base = render_icon(
        source=source,
        width=largest_width,
        height=largest_height,
        fit=fit,
        background=background,
        padding=padding,
    )
    base.save(destination, format="ICO", sizes=list(ICO_SIZES))
    return destination
