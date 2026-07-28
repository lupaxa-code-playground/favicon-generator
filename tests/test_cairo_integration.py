from __future__ import annotations

from pathlib import Path

import pytest

from lupaxa.favicon_generator.cli import main


def _cairo_works() -> bool:
    try:
        import cairosvg

        png = cairosvg.svg2png(
            bytestring=b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10">'
            b'<rect width="10" height="10" fill="red"/></svg>'
        )
        return bool(png)
    except Exception:
        return False


pytestmark = pytest.mark.cairo


@pytest.mark.skipif(not _cairo_works(), reason="native Cairo / cairosvg unavailable")
def test_cli_svg_generates_favicon_svg(
    svg_source: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    out = tmp_path / "favicons"
    monkeypatch.setattr(
        "sys.argv",
        [
            "favicon-generator",
            str(svg_source),
            "-o",
            str(out),
            "--overwrite",
            "--name",
            "SvgDemo",
        ],
    )
    assert main() == 0
    assert (out / "favicon.svg").exists()
    html = (out / "favicon-links.html").read_text(encoding="utf-8")
    assert "favicon.svg" in html
    assert (out / "apple-touch-icon.png").exists()
