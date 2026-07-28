from __future__ import annotations

from lupaxa.favicon_generator.icons import (
    ICO_SIZES,
    MASKABLE_EXTRA_PADDING,
    MASKABLE_ICON,
    PNG_ICONS,
)


def test_png_icon_filenames_and_sizes() -> None:
    expected = {
        ("favicon-16x16.png", 16, 16),
        ("favicon-32x32.png", 32, 32),
        ("apple-touch-icon.png", 180, 180),
        ("icon-192.png", 192, 192),
        ("icon-512.png", 512, 512),
    }
    assert {(i.filename, i.width, i.height) for i in PNG_ICONS} == expected


def test_maskable_and_ico() -> None:
    assert MASKABLE_ICON.filename == "icon-maskable-512.png"
    assert MASKABLE_ICON.width == MASKABLE_ICON.height == 512
    assert MASKABLE_EXTRA_PADDING == 0.1
    assert ICO_SIZES == ((16, 16), (32, 32), (48, 48))
