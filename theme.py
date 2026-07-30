#!/usr/bin/env python3
"""Shared theme resolution for the web build and the print build.

Both renderers read the same palette out of card.json so a printed card can never
drift from the web card. Anything the user omits falls back to a neutral slate.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).parent

THEME_DEFAULTS = {
    "accent": "#4F7CFF",
    "accent_deep": "#3D63D8",
    "accent_bright": "#7CA0FF",
    "accent_text": "#2F4FA8",
    "ink": "#1A1A1A",
    # Text on top of the accent-filled button. Check this pair for contrast when you
    # change the accent — a light accent needs dark text to stay readable outdoors.
    "ink_on_accent": "#FFFFFF",
    "paper": "#FAFAFA",
    "surface": "#FFFFFF",
    "muted": "#4B5563",
    "line": "rgba(26,26,26,.10)",
    "dark_ink": "#F5F3EE",
    "dark_paper": "#0E0E0E",
    "dark_surface": "#161616",
    "dark_muted": "#9C9689",
    "dark_line": "rgba(245,243,238,.12)",
    "font_sans": 'Inter,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif',
    "font_mono": '"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace',
    "google_fonts": "Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@400;500;700",
}


def load(path=None):
    """Return (card_dict, theme_dict) from card.json."""
    card = json.loads((pathlib.Path(path) if path else ROOT / "card.json").read_text())
    return card, {**THEME_DEFAULTS, **card.get("theme", {})}
