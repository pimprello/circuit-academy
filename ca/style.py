"""Shared look for every video: colours, fonts, sizes."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"

BG = "#0A0F1E"
GRID = "#16203A"
WIRE = "#DCE6F5"
TEXT = "#F2F5FB"
MUTED = "#8C9AB8"
CYAN = "#38E1FF"
YELLOW = "#FFD23F"
PINK = "#FF4D8D"
GREEN = "#4DFF9A"
ORANGE = "#FF9F43"
PURPLE = "#A78BFA"
RED = "#FF5A5A"

HEAD_FONT = "Barlow Condensed"   # bundled (assets/fonts), bold headlines
BODY_FONT = "Inter"              # apt: fonts-inter
MONO_FONT = "JetBrains Mono"     # apt: fonts-jetbrains-mono

STROKE = 4          # schematic line width
WIRE_STROKE = 4

# colour per component family (used for the symbol body + highlights)
PART_COLOURS = {
    "resistor": ORANGE, "capacitor": CYAN, "inductor": PURPLE, "diode": PINK,
    "led": RED, "zener": PINK, "battery": GREEN, "switch": YELLOW,
    "transistor": CYAN, "mosfet": CYAN, "relay": YELLOW, "transformer": PURPLE,
    "fuse": ORANGE, "lamp": YELLOW, "motor": GREEN, "ic": CYAN, "meter": TEXT,
}
