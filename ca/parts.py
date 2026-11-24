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
    "resistor_iec": lambda: Resistor(iec=True),
    "diode_rev": lambda: Diode().rotate(PI),
    "inductor_core": lambda: Inductor(core=True),
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
    g = VGroup(leads, body, bands_m, hi)
    _anchor(g, "bands", P(-0.55, -0.45)); _anchor(g, "gold", P(length / 2 - 0.6, -0.6))
    return g


def lamp_pic():
    bulb = Circle(radius=1.0, stroke_color="#E8EEF7", stroke_width=4, fill_color="#FFF3C4", fill_opacity=0.25)
    neck = Rectangle(width=0.9, height=0.7, stroke_width=0).move_to(P(0, -1.15))
    neck.set_fill(["#E6E9EF", "#8F97A4"], 1).set_sheen_direction(RIGHT)
    fil = VGroup(poly((-0.3, -0.7), (-0.3, 0.1), (-0.15, 0.25), (0, 0.1), (0.15, 0.25), (0.3, 0.1), (0.3, -0.7)))
    fil.set_stroke("#FFB347", 5)
    g = VGroup(glow_disc(S.YELLOW, 1.6, 10, 0.12), bulb, neck, fil)
    _anchor(g, "filament", P(0.3, 0.1)); _anchor(g, "glass", P(-0.75, 0.55))
    return g


def _anchor(g, name, point):
    d = Dot(point, radius=0.001, fill_opacity=0, stroke_opacity=0)
    g.add(d)
    if not hasattr(g, "anchors"):
        g.anchors = {}
    g.anchors[name] = d
    return g


def led_pic():
    """5 mm LED: red dome with a flat rim, long anode leg, short cathode leg."""
    dome = VGroup(Rectangle(width=1.5, height=1.3, stroke_width=0).move_to(P(0, 0.35)),
                  Circle(radius=0.75).move_to(P(0, 1.0)))
    body = Union(*dome, stroke_width=0)
    body.set_fill(["#FF8A80", "#E53935", "#8E1B1B"], 0.95).set_sheen_direction(RIGHT)
    rim = RoundedRectangle(width=1.85, height=0.28, corner_radius=0.06, stroke_width=0).move_to(P(0, -0.35))
    rim.set_fill(["#FF6F61", "#B71C1C"], 1).set_sheen_direction(RIGHT)
    hi = Ellipse(width=0.3, height=0.9, stroke_width=0, fill_color=WHITE, fill_opacity=0.35).move_to(P(-0.4, 0.75))
    anode = Line(P(0.3, -0.5), P(0.3, -3.2), stroke_color="#C9CED8", stroke_width=9)
    cathode = Line(P(-0.3, -0.5), P(-0.3, -2.5), stroke_color="#C9CED8", stroke_width=9)
    g = VGroup(glow_disc("#FF3B30", 1.5, 10, 0.12).move_to(P(0, 0.7)), anode, cathode, body, rim, hi)
    _anchor(g, "anode", P(0.3, -2.9)); _anchor(g, "cathode", P(-0.3, -2.3))
    return g


def diode_pic(length=3.6):
    """Through-hole rectifier diode: black body, silver band at the cathode end."""
    leads = VGroup(Line(P(-length / 2 - 1.0, 0), P(-length / 2 + 0.1, 0), stroke_color="#C9CED8", stroke_width=9),
                   Line(P(length / 2 - 0.1, 0), P(length / 2 + 1.0, 0), stroke_color="#C9CED8", stroke_width=9))
    body = RoundedRectangle(width=length, height=0.95, corner_radius=0.2, stroke_width=0)
    body.set_fill(["#4A4F5C", "#1C1F26", "#08090C"], 1).set_sheen_direction(DOWN)
    band = Rectangle(width=0.35, height=0.95, stroke_width=0).move_to(P(length / 2 - 0.55, 0))
    band.set_fill(["#F4F6FA", "#A9B0BC", "#6B7280"], 1).set_sheen_direction(DOWN)
    hi = RoundedRectangle(width=length - 0.4, height=0.12, corner_radius=0.05, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.25).move_to(P(0, 0.26))
    g = VGroup(leads, body, band, hi)
    _anchor(g, "band", P(length / 2 - 0.55, -0.3)); _anchor(g, "anode", P(-length / 2 - 0.6, 0))
    return g


def capacitor_pic():
    """Electrolytic capacitor: blue can, light stripe marking the negative leg, two legs."""
    can = RoundedRectangle(width=1.9, height=3.0, corner_radius=0.2, stroke_width=0).move_to(P(0, 0.4))
    can.set_fill(["#6FA8FF", "#1E4FCC", "#0E2C7A"], 1).set_sheen_direction(RIGHT)
    stripe = Rectangle(width=0.45, height=3.0, stroke_width=0, fill_color="#C9D8F5", fill_opacity=0.9).move_to(P(-0.55, 0.4))
    minus = VGroup(*[Line(P(-0.67, y), P(-0.43, y), stroke_color="#1E4FCC", stroke_width=6) for y in (1.3, 0.6, -0.1, -0.8)])
    top = Ellipse(width=1.9, height=0.4, stroke_width=0, fill_color="#B8C4D9", fill_opacity=1).move_to(P(0, 1.9))
    vent = VGroup(Line(P(-0.4, 1.9), P(0.4, 1.9)), Line(P(0, 1.78), P(0, 2.02))).set_stroke("#7D8AA3", 4)
    legs = VGroup(Line(P(-0.45, -1.1), P(-0.45, -2.7), stroke_color="#C9CED8", stroke_width=9),
                  Line(P(0.45, -1.1), P(0.45, -3.2), stroke_color="#C9CED8", stroke_width=9))
    g = VGroup(legs, can, stripe, minus, top, vent)
    _anchor(g, "stripe", P(-0.55, 0.2)); _anchor(g, "negative", P(-0.45, -2.5))
    return g


def fuse_pic(length=4.0):
    """Glass cartridge fuse: metal end caps, thin wire through a clear tube."""
    tube = RoundedRectangle(width=length - 0.8, height=1.0, corner_radius=0.45, stroke_color="#DDE7F5",
                            stroke_width=3, fill_color="#9FC3FF", fill_opacity=0.15)
    caps = VGroup(*[RoundedRectangle(width=0.8, height=1.15, corner_radius=0.12, stroke_width=0).move_to(P(sx * (length / 2 - 0.4), 0))
                    for sx in (-1, 1)])
    for c in caps:
        c.set_fill(["#F4F6FA", "#A9B0BC", "#6B7280"], 1).set_sheen_direction(DOWN)
    wire = Line(P(-length / 2 + 0.8, 0), P(length / 2 - 0.8, 0), stroke_color="#FFB347", stroke_width=3)
    hi = RoundedRectangle(width=length - 1.2, height=0.12, corner_radius=0.05, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.35).move_to(P(0, 0.3))
    g = VGroup(tube, wire, caps, hi)
    _anchor(g, "wire", P(0.3, 0)); _anchor(g, "cap", P(length / 2 - 0.4, -0.45))
    return g


def switch_pic():
    """Toggle switch: metal body, threaded bushing, lever flipped up."""
    body = RoundedRectangle(width=2.6, height=1.6, corner_radius=0.15, stroke_width=0).move_to(P(0, -0.8))
    body.set_fill(["#3A3F4C", "#1B1E26"], 1).set_sheen_direction(DOWN)
    bush = Rectangle(width=1.0, height=0.6, stroke_width=0).move_to(P(0, 0.3))
    bush.set_fill(["#F4F6FA", "#9AA2AF", "#5F6673"], 1).set_sheen_direction(RIGHT)
    threads = VGroup(*[Line(P(-0.5, y), P(0.5, y), stroke_color="#6B7280", stroke_width=2) for y in (0.12, 0.24, 0.36, 0.48)])
    lever = RoundedRectangle(width=0.32, height=2.0, corner_radius=0.16, stroke_width=0).move_to(P(0, 1.5)).rotate(-25 * DEGREES, about_point=P(0, 0.6))
    lever.set_fill(["#FFFFFF", "#B9C0CC", "#7C8494"], 1).set_sheen_direction(RIGHT)
    pins = VGroup(*[Line(P(x, -1.6), P(x, -2.6), stroke_color="#C9CED8", stroke_width=9) for x in (-0.8, 0, 0.8)])
    g = VGroup(pins, body, bush, threads, lever)
    _anchor(g, "lever", P(0.35, 2.0)); _anchor(g, "pins", P(-0.8, -2.3))
    return g


PICTURES = {
    "wire": lambda: copper_wire(6.0, r=0.45, strip=1.3),
    "cell": aa_cell,
    "resistor": resistor_pic,
    "lamp": lamp_pic,
    "led": led_pic,
    "diode": diode_pic,
    "capacitor": capacitor_pic,
    "fuse": fuse_pic,
    "switch": switch_pic,
}


def picture(name):
    """Drawn 'real' look of a part; parts without one yet get a big glowing symbol."""
    if name in PICTURES:
        return PICTURES[name]()
    s = symbol(name).scale(1.6)
    return VGroup(glow_disc(colour(name), 1.8, 12, 0.08).move_to(s), s)
