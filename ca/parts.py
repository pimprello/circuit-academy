"""Every component the channel can teach: its schematic symbol, a drawn 'real life'
picture, and its colour.  Add a component here once and every beat type, the
next-episode teaser and the thumbnail can use it."""
import numpy as np
from manim import *
from ca import style as S
from ca.symbols import (P, Resistor, Potentiometer, Thermistor, LDR, Fuse, Capacitor, Inductor, Crystal,
                        Diode, Zener, LED, Photodiode, NPN, PNP, NMOS, Battery, ACSource, Lamp, Motor,
                        Switch, PushButton, Transformer, Relay, OpAmp, ICBox, poly)
from ca.kit import copper_wire, glow_disc


def _wire_symbol():
    return VGroup(poly((-1.4, 0), (1.4, 0)).set_stroke(S.WIRE, 6))


SYMBOLS = {
    "wire": _wire_symbol,
    "cell": lambda: Battery(cells=1),
    "battery": lambda: Battery(cells=3),
    "resistor": lambda: Resistor(),
    "potentiometer": lambda: Potentiometer(),
    "thermistor": lambda: Thermistor(),
    "ldr": lambda: LDR(),
    "fuse": lambda: Fuse(),
    "capacitor": lambda: Capacitor(),
    "inductor": lambda: Inductor(),
    "crystal": lambda: Crystal(),
    "diode": lambda: Diode(),
    "zener": lambda: Zener(),
    "led": lambda: LED(),
    "photodiode": lambda: Photodiode(),
    "transistor": lambda: NPN(),
    "mosfet": lambda: NMOS(),
    "lamp": lambda: Lamp(),
    "motor": lambda: Motor(),
    "switch": lambda: Switch(),
    "button": lambda: PushButton(),
    "transformer": lambda: Transformer(),
    "relay": lambda: Relay(),
    "op-amp": lambda: OpAmp(),
    "555 timer": lambda: ICBox("555", left=[("dis", "7"), ("thr", "6"), ("trig", "2")], right=[("out", "3")],
                               top=[("vcc", "8"), ("rst", "4")], bottom=[("gnd", "1"), ("cv", "5")]),
    "ac": lambda: ACSource(),
}

COLOURS = {"wire": S.CYAN, "cell": S.GREEN, "battery": S.GREEN, "resistor": S.ORANGE, "capacitor": S.CYAN,
           "led": S.RED, "diode": S.PINK, "switch": S.YELLOW, "transistor": S.CYAN, "lamp": S.YELLOW}


def symbol(name):
    return SYMBOLS[name]()


def colour(name):
    return COLOURS.get(name, S.CYAN)


# ───────────────────────── drawn 'real life' pictures ─────────────────────────
def aa_cell(length=4.6, h=1.45):
    """A 1.5 V cylindrical cell lying on its side: + nub on the right, flat - end on the left."""
    body = RoundedRectangle(width=length, height=h, corner_radius=0.18, stroke_width=0)
    body.set_fill(["#5BF2A6", "#18A862", "#0B5E36"], 1).set_sheen_direction(DOWN)
    band = Rectangle(width=length * 0.34, height=h, stroke_width=0).move_to(P(length * 0.33, 0))
    band.set_fill(["#3A3F4C", "#1B1E26", "#0C0E13"], 1).set_sheen_direction(DOWN)
    cap_r = RoundedRectangle(width=0.26, height=h * 0.98, corner_radius=0.1, stroke_width=0).move_to(P(length / 2 - 0.08, 0))
    cap_r.set_fill(["#F4F6FA", "#A9B0BC", "#6B7280"], 1).set_sheen_direction(DOWN)
    nub = RoundedRectangle(width=0.32, height=h * 0.42, corner_radius=0.07, stroke_width=0).move_to(P(length / 2 + 0.18, 0))
    nub.set_fill(["#FFFFFF", "#B9C0CC", "#7C8494"], 1).set_sheen_direction(DOWN)
    cap_l = RoundedRectangle(width=0.2, height=h * 0.96, corner_radius=0.08, stroke_width=0).move_to(P(-length / 2 + 0.05, 0))
    cap_l.set_fill(["#E6E9EF", "#9AA2AF", "#5F6673"], 1).set_sheen_direction(DOWN)
    hi = RoundedRectangle(width=length - 0.5, height=h * 0.16, corner_radius=0.05, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.28).move_to(P(-0.05, h * 0.3))
    plus = Text("+", font=S.BODY_FONT, weight=BOLD, font_size=60, color=WHITE).move_to(P(length * 0.33, 0.02))
    volts = Text("1.5 V", font=S.HEAD_FONT, weight=ULTRABOLD, slant=ITALIC, font_size=64, color="#06341E").move_to(P(-0.55, -0.02))
    g = VGroup(body, band, cap_r, nub, cap_l, hi, plus, volts)
    g.plus_end = nub
    g.minus_end = cap_l
    return g


BAND = {0: "#111111", 1: "#7B3F12", 2: "#E0352B", 3: "#FF8A1F", 4: "#FFD21F", 5: "#2FB54A",
        6: "#2F6DF5", 7: "#8E44D9", 8: "#8A8F99", 9: "#F5F5F5", "gold": "#D9A93B"}


def resistor_pic(bands=(1, 0, 2, "gold"), length=4.2):
    """Through-hole resistor: dog-bone body with colour bands (default brown-black-red-gold = 1 kΩ ±5 %)."""
    leads = VGroup(Line(P(-length / 2 - 1.1, 0), P(-length / 2 + 0.2, 0), stroke_color="#C9CED8", stroke_width=10),
                   Line(P(length / 2 - 0.2, 0), P(length / 2 + 1.1, 0), stroke_color="#C9CED8", stroke_width=10))
    body = VGroup(
        Ellipse(width=1.1, height=1.25, stroke_width=0).move_to(P(-length / 2 + 0.5, 0)),
        Rectangle(width=length - 1.6, height=0.92, stroke_width=0),
        Ellipse(width=1.1, height=1.25, stroke_width=0).move_to(P(length / 2 - 0.5, 0)))
    for m in body:
        m.set_fill(["#F6DDB0", "#D9B47A", "#9C7A45"], 1).set_sheen_direction(DOWN)
    xs = [-length / 2 + 0.55, -0.55, -0.05, length / 2 - 0.6]
    bands_m = VGroup()
    for x, b in zip(xs, bands):
        hgt = 1.2 if abs(x) > length / 2 - 0.8 else 0.9
        r = Rectangle(width=0.24, height=hgt, stroke_width=0, fill_color=BAND[b], fill_opacity=1).move_to(P(x, 0))
        bands_m.add(r)
    hi = RoundedRectangle(width=length - 1.2, height=0.14, corner_radius=0.05, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.35).move_to(P(0, 0.26))
    return VGroup(leads, body, bands_m, hi)


def lamp_pic():
    bulb = Circle(radius=1.0, stroke_color="#E8EEF7", stroke_width=4, fill_color="#FFF3C4", fill_opacity=0.25)
    neck = Rectangle(width=0.9, height=0.7, stroke_width=0).move_to(P(0, -1.15))
    neck.set_fill(["#E6E9EF", "#8F97A4"], 1).set_sheen_direction(RIGHT)
    fil = VGroup(poly((-0.3, -0.7), (-0.3, 0.1), (-0.15, 0.25), (0, 0.1), (0.15, 0.25), (0.3, 0.1), (0.3, -0.7)))
    fil.set_stroke("#FFB347", 5)
    return VGroup(glow_disc(S.YELLOW, 1.6, 10, 0.12), bulb, neck, fil)


PICTURES = {
    "wire": lambda: copper_wire(6.0),
    "cell": aa_cell,
    "resistor": resistor_pic,
    "lamp": lamp_pic,
}


def picture(name):
    """Drawn 'real' look of a part; parts without one yet get a big glowing symbol."""
    if name in PICTURES:
        return PICTURES[name]()
    s = symbol(name).scale(1.6)
    return VGroup(glow_disc(colour(name), 1.8, 12, 0.08).move_to(s), s)
