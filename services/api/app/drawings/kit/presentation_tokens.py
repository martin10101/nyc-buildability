"""Generated presentation tokens (architect presentation contract, section 5).

Source of truth: docs/design/presentation-tokens.json
Generator: apps/web/scripts/presentation-tokens.mjs (task M5-T148).
Do not edit by hand; regenerate and commit the JSON, this module and the
globals.css block together. The server drawing kit and the PDF read these.
"""

TOKENS = {
    "color": {
        "ink": "#182B3A",
        "supporting": "#52616C",
        "action": "#18577A",
        "page": "#F2F5F6",
        "surface": "#FFFFFF",
        "divider": "#D8E0E5",
        "selected": "#EEF4F7",
        "caution-ink": "#795318",
        "caution-surface": "#FBF4E7",
    },
    "spacing": {
        "4": 4,
        "8": 8,
        "12": 12,
        "16": 16,
        "24": 24,
        "32": 32,
        "48": 48,
    },
    "control": {
        "height": 44,
        "radius": 6,
    },
    "radius": {
        "panel": 8,
    },
    "font": {
        "family": "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
    },
    "type": {
        "property-title": {
            "screen_px": 28,
            "line_height": 1.2,
            "weight": 700,
            "print_pt": 22,
        },
        "headline-value": {
            "screen_px": 40,
            "line_height": 1.1,
            "weight": 700,
            "print_pt": 30,
        },
        "section-title": {
            "screen_px": 18,
            "line_height": 1.3,
            "weight": 600,
            "print_pt": 12,
        },
        "body": {
            "screen_px": 16,
            "line_height": 1.5,
            "weight": 400,
            "print_pt": 10.5,
            "print_line_height": 1.4,
        },
        "compact": {
            "screen_px": 14,
            "line_height": 1.35,
            "weight": 400,
            "print_pt": 9.5,
        },
        "source-note": {
            "screen_px": 13,
            "line_height": 1.4,
            "weight": 400,
            "print_pt": 8.5,
        },
        "drawing-label": {
            "screen_px": 14,
            "line_height": 1.2,
            "weight": 400,
            "print_pt": 8.5,
            "print_pt_preferred": 9.5,
        },
    },
    "status": {
        "settled": {
            "marker": False,
        },
        "conditional": {
            "marker": True,
            "color_role": "secondary",
            "ink": "#795318",
            "surface": "#FBF4E7",
        },
        "not-known": {
            "marker": True,
            "color_role": "secondary",
            "ink": "#52616C",
            "surface": "#F2F5F6",
        },
    },
}

COLOR = TOKENS["color"]
SPACING = TOKENS["spacing"]
CONTROL = TOKENS["control"]
RADIUS = TOKENS["radius"]
FONT = TOKENS["font"]
TYPE = TOKENS["type"]
STATUS = TOKENS["status"]
