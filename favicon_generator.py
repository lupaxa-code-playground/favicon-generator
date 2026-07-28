#!/usr/bin/env python3
"""
Generate a modern favicon set from a single source image (PNG/JPEG/WebP/SVG).

Examples:
    python favicon_generator.py logo.png
    python favicon_generator.py logo.svg --output-dir site/assets/favicons
    python favicon_generator.py logo.png --background "#FFFFFF" --padding 0.08
    python favicon_generator.py logo.png --fit cover --no-html --no-ico --no-manifest

Dependencies:
    python -m pip install Pillow cairosvg
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Final

from PIL import Image, ImageColor, ImageOps, UnidentifiedImageError

SVG_RASTER_SIZE: Final[int] = 1024


@dataclass(frozen=True)
class IconSpec:
    filename: str
    width: int
    height: int


PNG_ICONS: Final[tuple[IconSpec, ...]] = (
    IconSpec("favicon-16x16.png", 16, 16),
    IconSpec("favicon-32x32.png", 32, 32),
    IconSpec("apple-touch-icon.png", 180, 180),
    IconSpec("icon-192.png", 192, 192),
    IconSpec("icon-512.png", 512, 512),
)

MASKABLE_ICON: Final[IconSpec] = IconSpec("icon-maskable-512.png", 512, 512)

# Extra fractional padding applied on top of --padding for maskable icons
# so the logo stays inside the Android safe zone (~80% of the canvas).
MASKABLE_EXTRA_PADDING: Final[float] = 0.1

ICO_SIZES: Final[tuple[tuple[int, int], ...]] = (
    (16, 16),
    (32, 32),
    (48, 48),
)

HEX_COLOUR_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?$"
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate modern favicons (PNG, ICO, Apple touch, PWA icons), "
            "site.webmanifest, and an HTML snippet from one source image."
        )
    )
    parser.add_argument(
        "source",
        type=Path,
        help="Source image: PNG, JPEG, WebP, or SVG.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path("favicons"),
        help="Output directory. Default: ./favicons",
    )
    parser.add_argument(
        "--fit",
        choices=("contain", "cover", "stretch"),
        default="contain",
        help=(
            "How to fit the source into each icon: contain preserves the whole "
            "image, cover fills and crops, stretch forces the exact dimensions. "
            "Default: contain"
        ),
    )
    parser.add_argument(
        "--background",
        default="transparent",
        help=(
            "Canvas background: transparent, a CSS colour name, or a hex colour "
            "such as #FFFFFF. Default: transparent"
        ),
    )
    parser.add_argument(
        "--padding",
        type=float,
        default=0.0,
        help=(
            "Fractional padding around the image, from 0.0 to 0.45. "
            "For example, 0.08 adds 8%% padding on every side. Default: 0"
        ),
    )
    parser.add_argument(
        "--theme-colour",
        default="#FFFFFF",
        help="theme-color / manifest theme_color. Default: #FFFFFF",
    )
    parser.add_argument(
        "--background-colour",
        default=None,
        help=(
            "Manifest background_color. Default: same as --theme-colour."
        ),
    )
    parser.add_argument(
        "--name",
        default=None,
        help="App name for the web manifest. Default: source file stem or 'App'.",
    )
    parser.add_argument(
        "--short-name",
        default=None,
        help="Manifest short_name. Default: same as --name.",
    )
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        help="Do not generate site.webmanifest.",
    )
    parser.add_argument(
        "--prefix",
        default="",
        help=(
            "Optional URL prefix used in generated HTML, for example "
            "'assets/favicons/' or '/favicons/'."
        ),
    )
    parser.add_argument(
        "--html-file",
        default="favicon-links.html",
        help="Generated HTML snippet filename. Default: favicon-links.html",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Do not generate the HTML snippet.",
    )
    parser.add_argument(
        "--no-ico",
        action="store_true",
        help="Do not generate the multi-resolution favicon.ico file.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing generated files.",
    )
    return parser.parse_args()


def normalise_colour(value: str) -> tuple[int, int, int, int]:
    if value.lower() == "transparent":
        return (0, 0, 0, 0)

    try:
        rgb_or_rgba = ImageColor.getcolor(value, "RGBA")
    except ValueError as exc:
        raise ValueError(
            f"Invalid colour {value!r}. Use 'transparent', a CSS colour name, "
            "or a value such as '#FFFFFF'."
        ) from exc

    return rgb_or_rgba


def validate_hex_colour(value: str, flag_name: str) -> str:
    if not HEX_COLOUR_PATTERN.fullmatch(value):
        raise ValueError(
            f"{flag_name} must be a six- or eight-digit hex colour, "
            "for example #FFFFFF."
        )
    return value.upper()


def load_svg_as_rgba(path: Path) -> Image.Image:
    try:
        import cairosvg
    except ImportError as exc:
        raise ValueError(
            "SVG input requires cairosvg. Install with: "
            "python -m pip install cairosvg"
        ) from exc

    try:
        png_bytes = cairosvg.svg2png(
            url=path.as_uri(),
            output_width=SVG_RASTER_SIZE,
            output_height=SVG_RASTER_SIZE,
        )
    except Exception as exc:  # cairosvg raises various errors per SVG
        raise ValueError(f"Failed to render SVG: {path}: {exc}") from exc

    if not png_bytes:
        raise ValueError(f"Failed to render SVG (empty output): {path}")

    with Image.open(io.BytesIO(png_bytes)) as image:
        image.load()
        return image.convert("RGBA")


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
            f"Refusing to overwrite existing file: {destination}. "
            "Use --overwrite to replace it."
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
            f"Refusing to overwrite existing file: {destination}. "
            "Use --overwrite to replace it."
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
        background=background,
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
            f"Refusing to overwrite existing file: {destination}. "
            "Use --overwrite to replace it."
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


def url_for(prefix: str, filename: str) -> str:
    if not prefix:
        return filename
    return f"{prefix.rstrip('/')}/{filename}"


def build_html(prefix: str, application_name: str, tile_colour: str) -> str:
    raise NotImplementedError("rewritten in Task 4")


def write_html(
    output_dir: Path,
    filename: str,
    content: str,
    overwrite: bool,
) -> Path:
    destination = output_dir / filename

    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {destination}. "
            "Use --overwrite to replace it."
        )

    destination.write_text(content, encoding="utf-8")
    return destination


def main() -> int:
    args = parse_arguments()

    try:
        if not 0.0 <= args.padding <= 0.45:
            raise ValueError("--padding must be between 0.0 and 0.45.")

        background = normalise_colour(args.background)
        validate_hex_colour(args.theme_colour, "--theme-colour")
        if args.background_colour is not None:
            validate_hex_colour(args.background_colour, "--background-colour")
        source, _source_is_svg = prepare_source(args.source)

        args.output_dir.mkdir(parents=True, exist_ok=True)

        generated = generate_png_icons(
            source=source,
            output_dir=args.output_dir,
            fit=args.fit,
            background=background,
            padding=args.padding,
            overwrite=args.overwrite,
        )

        if not args.no_ico:
            generated.append(
                generate_ico(
                    source=source,
                    output_dir=args.output_dir,
                    fit=args.fit,
                    background=background,
                    padding=args.padding,
                    overwrite=args.overwrite,
                )
            )

        # HTML/manifest wiring rewritten in Task 4
        if not args.no_html:
            raise NotImplementedError("HTML generation rewritten in Task 4")

        print(f"Generated {len(generated)} files in {args.output_dir.resolve()}:")
        for path in generated:
            print(f"  {path.name}")

        return 0

    except (FileNotFoundError, FileExistsError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
