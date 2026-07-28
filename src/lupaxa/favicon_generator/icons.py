"""Icon size specifications for lupaxa.favicon_generator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final


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
