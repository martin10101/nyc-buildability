"""Deterministic color arithmetic for face shading (sRGB hex, integer rounding)."""

from __future__ import annotations

__all__ = ["mix", "parse_hex", "relative_luminance", "to_hex"]


def parse_hex(color: str) -> tuple[int, int, int]:
    text = color.lstrip("#")
    if len(text) != 6:
        raise ValueError(f"not a #RRGGBB color: {color!r}")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def mix(color: str, toward: str, amount: float) -> str:
    """``color`` moved ``amount`` (0..1) of the way to ``toward``, channel-wise."""
    a, b = parse_hex(color), parse_hex(toward)
    return to_hex(tuple(round(x + (y - x) * amount) for x, y in zip(a, b, strict=True)))


def relative_luminance(color: str) -> float:
    """WCAG relative luminance (0 black .. 1 white)."""

    def channel(value: int) -> float:
        c = value / 255.0
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(v) for v in parse_hex(color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b
