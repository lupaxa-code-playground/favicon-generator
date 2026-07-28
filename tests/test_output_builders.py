from __future__ import annotations

import json

from lupaxa.favicon_generator.output import build_html, build_manifest


def test_build_html_includes_core_tags() -> None:
    html = build_html(
        prefix="icons/",
        theme_colour="#112233",
        include_svg=True,
        include_ico=True,
        include_manifest=True,
    )
    assert 'rel="icon" href="icons/favicon.svg"' in html
    assert 'href="icons/favicon.ico"' in html
    assert 'sizes="32x32"' in html
    assert 'apple-touch-icon' in html
    assert 'href="icons/site.webmanifest"' in html
    assert 'content="#112233"' in html


def test_build_manifest_icons() -> None:
    raw = build_manifest(
        prefix="",
        name="Demo",
        short_name="Demo",
        theme_colour="#112233",
        background_colour="#112233",
    )
    data = json.loads(raw)
    assert data["name"] == "Demo"
    purposes = {icon["purpose"] for icon in data["icons"]}
    assert purposes == {"any", "maskable"}
    assert len(data["icons"]) == 3
