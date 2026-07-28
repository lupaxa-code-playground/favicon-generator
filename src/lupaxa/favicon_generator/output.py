"""HTML snippet and webmanifest generation."""

from __future__ import annotations

import json
from pathlib import Path


def url_for(prefix: str, filename: str) -> str:
    if not prefix:
        return filename
    return f"{prefix.rstrip('/')}/{filename}"


def build_html(
    *,
    prefix: str,
    theme_colour: str,
    include_svg: bool,
    include_ico: bool,
    include_manifest: bool,
) -> str:
    lines: list[str] = []

    if include_svg:
        lines.append(
            f'<link rel="icon" href="{url_for(prefix, "favicon.svg")}" type="image/svg+xml" />'
        )

    if include_ico:
        lines.append(f'<link rel="icon" href="{url_for(prefix, "favicon.ico")}" sizes="48x48" />')

    lines.extend(
        (
            (
                '<link rel="icon" type="image/png" sizes="32x32" '
                f'href="{url_for(prefix, "favicon-32x32.png")}" />'
            ),
            (
                '<link rel="icon" type="image/png" sizes="16x16" '
                f'href="{url_for(prefix, "favicon-16x16.png")}" />'
            ),
            (
                '<link rel="apple-touch-icon" sizes="180x180" '
                f'href="{url_for(prefix, "apple-touch-icon.png")}" />'
            ),
        )
    )

    if include_manifest:
        lines.append(f'<link rel="manifest" href="{url_for(prefix, "site.webmanifest")}" />')

    lines.append(f'<meta name="theme-color" content="{theme_colour}" />')
    return "\n".join(lines) + "\n"


def build_manifest(
    *,
    prefix: str,
    name: str,
    short_name: str,
    theme_colour: str,
    background_colour: str,
) -> str:
    payload = {
        "name": name,
        "short_name": short_name,
        "theme_color": theme_colour,
        "background_color": background_colour,
        "icons": [
            {
                "src": url_for(prefix, "icon-192.png"),
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(prefix, "icon-512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any",
            },
            {
                "src": url_for(prefix, "icon-maskable-512.png"),
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "maskable",
            },
        ],
    }
    return json.dumps(payload, indent=2) + "\n"


def write_manifest(
    output_dir: Path,
    content: str,
    overwrite: bool,
) -> Path:
    destination = output_dir / "site.webmanifest"
    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {destination}. Use --overwrite to replace it."
        )
    destination.write_text(content, encoding="utf-8")
    return destination


def write_html(
    output_dir: Path,
    filename: str,
    content: str,
    overwrite: bool,
) -> Path:
    destination = output_dir / filename

    if destination.exists() and not overwrite:
        raise FileExistsError(
            f"Refusing to overwrite existing file: {destination}. Use --overwrite to replace it."
        )

    destination.write_text(content, encoding="utf-8")
    return destination
