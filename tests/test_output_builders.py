from __future__ import annotations

import json
from pathlib import Path

import pytest

from lupaxa.favicon_generator.output import (
    build_html,
    build_manifest,
    url_for,
    write_html,
    write_manifest,
)


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
    assert "apple-touch-icon" in html
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


def test_url_for_without_and_with_prefix() -> None:
    assert url_for("", "a.png") == "a.png"
    assert url_for("assets/", "a.png") == "assets/a.png"
    assert url_for("assets", "a.png") == "assets/a.png"


def test_build_html_omits_optional_links() -> None:
    html = build_html(
        prefix="",
        theme_colour="#ABCDEF",
        include_svg=False,
        include_ico=False,
        include_manifest=False,
    )
    assert "favicon.svg" not in html
    assert "favicon.ico" not in html
    assert "site.webmanifest" not in html
    assert 'sizes="16x16"' in html
    assert 'content="#ABCDEF"' in html


def test_write_html_and_manifest_success(tmp_path: Path) -> None:
    html_path = write_html(tmp_path, "links.html", "<html/>\n", overwrite=False)
    assert html_path.read_text(encoding="utf-8") == "<html/>\n"
    man_path = write_manifest(tmp_path, '{"x":1}\n', overwrite=False)
    assert man_path.name == "site.webmanifest"
    assert man_path.read_text(encoding="utf-8") == '{"x":1}\n'


def test_write_html_refuses_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "links.html"
    target.write_text("old", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_html(tmp_path, "links.html", "new", overwrite=False)


def test_write_manifest_refuses_overwrite(tmp_path: Path) -> None:
    (tmp_path / "site.webmanifest").write_text("old", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_manifest(tmp_path, "{}", overwrite=False)
