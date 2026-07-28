"""Command-line interface for lupaxa.favicon_generator."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .output import build_html, build_manifest, write_html, write_manifest
from .render import (
    copy_favicon_svg,
    generate_ico,
    generate_png_icons,
    normalise_colour,
    prepare_source,
    validate_hex_colour,
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
        help="Manifest background_color. Default: same as --theme-colour.",
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
            "Optional URL prefix used in generated HTML and the webmanifest, "
            "for example 'assets/favicons/' or '/favicons/'."
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


def main() -> int:
    args = parse_arguments()

    try:
        if not 0.0 <= args.padding <= 0.45:
            raise ValueError("--padding must be between 0.0 and 0.45.")

        background = normalise_colour(args.background)
        theme_colour = validate_hex_colour(args.theme_colour, "--theme-colour")
        background_colour_raw = (
            args.background_colour
            if args.background_colour is not None
            else args.theme_colour
        )
        background_colour = validate_hex_colour(
            background_colour_raw, "--background-colour"
        )

        source, source_is_svg = prepare_source(args.source)

        app_name = args.name if args.name is not None else (args.source.stem or "App")
        short_name = args.short_name if args.short_name is not None else app_name

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

        if source_is_svg:
            generated.append(
                copy_favicon_svg(args.source, args.output_dir, args.overwrite)
            )

        if not args.no_manifest:
            generated.append(
                write_manifest(
                    output_dir=args.output_dir,
                    content=build_manifest(
                        prefix=args.prefix,
                        name=app_name,
                        short_name=short_name,
                        theme_colour=theme_colour,
                        background_colour=background_colour,
                    ),
                    overwrite=args.overwrite,
                )
            )

        if not args.no_html:
            generated.append(
                write_html(
                    output_dir=args.output_dir,
                    filename=args.html_file,
                    content=build_html(
                        prefix=args.prefix,
                        theme_colour=theme_colour,
                        include_svg=source_is_svg,
                        include_ico=not args.no_ico,
                        include_manifest=not args.no_manifest,
                    ),
                    overwrite=args.overwrite,
                )
            )

        print(f"Generated {len(generated)} files in {args.output_dir.resolve()}:")
        for path in generated:
            print(f"  {path.name}")

        return 0

    except (FileNotFoundError, FileExistsError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
