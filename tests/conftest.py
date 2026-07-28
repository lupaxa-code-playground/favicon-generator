from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image


@pytest.fixture
def png_source(tmp_path: Path) -> Path:
    path = tmp_path / "logo.png"
    Image.new("RGBA", (64, 64), (20, 120, 200, 255)).save(path)
    return path


@pytest.fixture
def svg_source(tmp_path: Path) -> Path:
    path = tmp_path / "logo.svg"
    path.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
        '<circle cx="50" cy="50" r="40" fill="#e74c3c"/></svg>',
        encoding="utf-8",
    )
    return path
