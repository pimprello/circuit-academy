"""Named circuits for the `circuit` beat.  Each builder returns a Circuit: the drawing,
the current loop(s) for the flowing dots, and the parts that light up when current flows.
Coordinates are for the Shorts frame (8 wide); circuits sit centred on y = 0."""
from manim import *
from ca import style as S
from ca.symbols import P, poly, Battery, Lamp, Resistor, LED, Switch
from ca.kit import B, glow_disc


class Circuit(VGroup):
    def __init__(self):
        super().__init__()
        self.parts, self.wires, self.labels = VGroup(), VGroup(), VGroup()
        self.loops, self.glows = [], []
        self.add(self.wires, self.parts, self.labels)

    def part(self, p, at, angle=0, scale=1.0):
        p.scale(scale).place(at, angle)
        self.parts.add(p)
        return p

    def wire(self, *pts):
        w = poly(*pts)
        self.wires.add(w)
        return w

    def label(self, text, at, colour=S.TEXT, size=34):
        t = B(text, size, colour).move_to(P(*at))
        self.labels.add(t)
        return t

    def loop(self, *corners):
        self.loops.append(poly(*corners, closed=True))

    def glow(self, part, colour=S.YELLOW, r=1.15):
        self.glows.append((part, colour, r))


def battery_lamp(volts="9 V", cells=2, L=-1.7, R=2.5, T=2.0, Bt=-2.0):
    c = Circuit()
    bat = c.part(Battery(cells=cells), (L, 0), -90, 1.3)
    lamp = c.part(Lamp(), (R, 0), -90, 1.3)
    c.label(volts, (L - 1.3, 0), S.GREEN, 38)
    c.wire((L, 1.3), (L, T), (R, T), (R, 1.3))
    c.wire((R, -1.3), (R, Bt), (L, Bt), (L, -1.3))
    c.loop((L, Bt), (L, T), (R, T), (R, Bt))
    c.glow(lamp)
    return c


def cell_lamp():
    return battery_lamp("1.5 V", cells=1)


def cells_series(L=-1.7, R=2.5, T=2.3, Bt=-2.3):
    """Two 1.5 V cells, + to -, feeding a lamp: 3 V in total."""
    c = Circuit()
    c.part(Battery(cells=1), (L, 1.1), -90, 1.0)
    c.part(Battery(cells=1), (L, -1.1), -90, 1.0)
    lamp = c.part(Lamp(), (R, 0), -90, 1.3)
    c.wire((L, 0.1), (L, -0.1))
    c.wire((L, 2.1), (L, T), (R, T), (R, 1.3))
    c.wire((R, -1.3), (R, Bt), (L, Bt), (L, -2.1))
    c.label("1.5 V", (L - 1.2, 1.1), S.GREEN, 32)
    c.label("1.5 V", (L - 1.2, -1.1), S.GREEN, 32)
    c.label("= 3 V", ((L + R) / 2, 0), S.YELLOW, 52)
    c.loop((L, Bt), (L, T), (R, T), (R, Bt))
    c.glow(lamp, r=1.35)
    return c


def led_resistor(L=-2.2, R=2.2, T=2.2, Bt=-2.2):
    """9 V battery, 470 Ω current-limiting resistor, red LED (anode at the top)."""
    c = Circuit()
    c.part(Battery(cells=2), (L, 0), -90, 1.2)
    c.part(Resistor(), (0, T), 0, 1.0)
    led = c.part(LED(), (R, 0), -90, 1.2)
    c.label("9 V", (L - 1.0, 0), S.GREEN, 36)
    c.label("470 Ω", (0, T + 0.62), S.ORANGE, 34)
    c.wire((L, 1.2), (L, T), (-1, T))
    c.wire((1, T), (R, T), (R, 1.2))
    c.wire((R, -1.2), (R, Bt), (L, Bt), (L, -1.2))
    c.loop((L, Bt), (L, T), (R, T), (R, Bt))
    c.glow(led, S.RED, 1.0)
    return c


def switch_lamp(L=-2.2, R=2.2, T=2.0, Bt=-2.0):
    c = Circuit()
    c.part(Battery(cells=2), (L, 0), -90, 1.3)
    sw = c.part(Switch(), (0, T), 0, 1.0)
    lamp = c.part(Lamp(), (R, 0), -90, 1.3)
    c.wire((L, 1.3), (L, T), (-1, T)); c.wire((1, T), (R, T), (R, 1.3))
    c.wire((R, -1.3), (R, Bt), (L, Bt), (L, -1.3))
    c.loop((L, Bt), (L, T), (R, T), (R, Bt))
    c.glow(lamp)
    c.switch = sw
    return c


CIRCUITS = {"battery_lamp": battery_lamp, "cell_lamp": cell_lamp, "cells_series": cells_series,
            "led_resistor": led_resistor, "switch_lamp": switch_lamp}


def build(name):
    return CIRCUITS[name]()


# ───────────────────────── reusable layouts ─────────────────────────
from ca.symbols import (Fuse, Diode, Zener, Capacitor, Potentiometer, LDR, Thermistor, Motor, PushButton,
                        NPN, NMOS, ACSource, Transformer)


def loop(source, top=(), right=None, right_angle=-90, src_label=None, top_labels=(), right_label=None,
         L=-1.7, R=2.5, T=2.1, Bt=-2.1, glow=None, glow_colour=S.YELLOW):
    """Series loop: source on the left (+ at the top), parts along the top, one part on the right."""
    c = Circuit()
    src = c.part(source, (L, 0), -90, 1.2)
    if src_label:
        c.label(src_label, (L - 1.25, 0), S.GREEN, 34)
    xs = []
    n = len(top)
    span = R - L
    for i, p in enumerate(top):
        x = L + span * (i + 1) / (n + 1)
        c.part(p, (x, T), 0, 0.9)
        xs.append(x)
        if i < len(top_labels) and top_labels[i]:
            c.label(top_labels[i], (x, T + 0.6), S.ORANGE, 30)
    rp = c.part(right, (R, 0), right_angle, 1.2)
    if right_label:
        c.label(right_label, (R - 1.15, 0), S.TEXT, 30)
    # wires along the top, between the parts
    pts = [(L, 1.2), (L, T)]
    for x in xs:
        pts.append((x - 0.9, T))
        c.wire(*pts)
        pts = [(x + 0.9, T)]
    pts += [(R, T), (R, 1.2)]
    c.wire(*pts)
    c.wire((R, -1.2), (R, Bt), (L, Bt), (L, -1.2))
    c.loop((L, Bt), (L, T), (R, T), (R, Bt))
    if glow is not None:
        c.glow(rp if glow == "right" else glow, glow_colour, 1.1)
    return c


def divider(top, bottom, volts="9 V", vout="Vout", L=-2.4, X=0.6, T=2.1, Bt=-2.1):
    """Voltage divider: two parts in series across the supply, output taken from the middle."""
    c = Circuit()
    c.part(Battery(cells=2), (L, 0), -90, 1.2)
    c.label(volts, (L - 1.25, 0), S.GREEN, 34)
    c.part(top, (X, 1.05), -90, 1.05)
    c.part(bottom, (X, -1.05), -90, 1.05)
    c.wire((L, 1.2), (L, T), (X, T), (X, 2.1))
    c.wire((X, -2.1), (X, Bt), (L, Bt), (L, -1.2))
    c.wire((X, 0), (X + 1.7, 0))
    c.wires.add(Circle(radius=0.12, stroke_color=S.WIRE, stroke_width=4, fill_color=S.BG, fill_opacity=1).move_to(P(X + 1.82, 0)))
    c.parts.add(Dot(P(X, 0), radius=0.09, color=S.WIRE))
    c.label(vout, (X + 2.5, 0), S.YELLOW, 34)
    c.loop((L, Bt), (L, T), (X, T), (X, Bt))
    return c


def diode_lamp():
    return loop(Battery(cells=2), top=[Diode()], right=Lamp(), src_label="9 V", glow="right")


def fuse_lamp():
    return loop(Battery(cells=2), top=[Fuse()], right=Lamp(), src_label="9 V", top_labels=["1 A fuse"], glow="right")


def button_led():
    return loop(Battery(cells=2), top=[PushButton(), Resistor()], right=LED(), src_label="9 V",
                top_labels=["", "470 Ω"], glow="right", glow_colour=S.RED)


def motor_switch():
    return loop(Battery(cells=2), top=[Switch(closed=True)], right=Motor(), src_label="6 V", glow="right", glow_colour=S.GREEN)


def rc_charge():
    return loop(Battery(cells=2), top=[Switch(closed=True), Resistor()], right=Capacitor(), src_label="9 V",
                top_labels=["", "10 kΩ"], right_label="100 µF")


def zener_regulator():
    c = loop(Battery(cells=3), top=[Resistor()], right=Zener(), right_angle=90, src_label="12 V", top_labels=["330 Ω"])
    c.label("5.1 V", (1.3, 0), S.YELLOW, 38)
    return c


def pot_divider():
    c = Circuit()
    L, X, T, Bt = -2.4, 0.6, 2.1, -2.1
    c.part(Battery(cells=2), (L, 0), -90, 1.2)
    c.label("9 V", (L - 1.25, 0), S.GREEN, 34)
    pot = c.part(Potentiometer(), (X, 0), -90, 1.6)      # wiper now points right
    c.wire((L, 1.2), (L, T), (X, T), (X, 1.6))
    c.wire((X, -1.6), (X, Bt), (L, Bt), (L, -1.2))
    w = pot.pin("w")
    c.wire(tuple(w[:2]), (X + 2.2, w[1]))
    c.wires.add(Circle(radius=0.12, stroke_color=S.WIRE, stroke_width=4, fill_color=S.BG, fill_opacity=1).move_to(P(X + 2.32, w[1])))
    c.label("0 – 9 V", (X + 2.4, w[1] + 0.55), S.YELLOW, 32)
    c.loop((L, Bt), (L, T), (X, T), (X, Bt))
    return c


def ldr_divider():
    return divider(Resistor(), LDR())


def thermistor_divider():
    return divider(Resistor(), Thermistor())


def npn_led():
    """NPN transistor switching an LED: the switch only feeds a small current into the base,
    which turns on the bigger collector current through the LED."""
    c = Circuit()
    B0, T, Bt = -2.9, 2.9, -3.1
    c.part(Battery(cells=2), (B0, 0), -90, 1.0)
    c.label("9 V", (B0 - 0.65, 0), S.GREEN, 26)
    c.part(Resistor(), (1.3, 2.0), -90, 0.9)           # collector resistor  2.9 -> 1.1
    led = c.part(LED(), (1.3, 0.2), -90, 0.9)          # LED                 1.1 -> -0.7
    c.part(NPN(), (1.0, -1.7), 0, 1.0)                 # c (1.3,-0.7)  e (1.3,-2.7)  b (0,-1.7)
    c.part(Switch(closed=True), (-1.6, 1.4), -90, 0.7) # base switch         2.1 -> 0.7
    c.part(Resistor(), (-0.75, -1.7), 0, 0.8)          # base resistor      -1.55 -> 0.05
    c.label("1 kΩ", (2.3, 2.0), S.ORANGE, 26)
    c.label("10 kΩ", (-0.75, -1.15), S.ORANGE, 26)
    c.wire((B0, 1.0), (B0, T), (1.3, T))
    c.wire((-1.6, T), (-1.6, 2.1))
    c.wire((-1.6, 0.7), (-1.6, -1.7), (-1.55, -1.7))
    c.wire((1.3, -2.7), (1.3, Bt), (B0, Bt), (B0, -1.0))
    c.parts.add(Dot(P(-1.6, T), radius=0.08, color=S.WIRE))
    c.loop((B0, Bt), (B0, T), (1.3, T), (1.3, Bt))
    c.glow(led, S.RED, 0.9)
    return c


def transformer_lamp():
    c = Circuit()
    L, R, T, Bt = -2.6, 2.6, 2.1, -2.1
    c.part(ACSource(), (L, 0), -90, 1.0)
    c.label("230 V", (L, 1.45), S.GREEN, 28)
    c.part(Transformer(), (0, 0), 0, 1.3)              # p1 (-1.3, 0.78) p2 (-1.3,-0.78) s1 (1.3,0.78) s2 (1.3,-0.78)
    lamp = c.part(Lamp(), (R, 0), -90, 1.0)
    c.label("12 V", (R, 1.45), S.YELLOW, 28)
    c.wire((L, 1.0), (L, T), (-1.3, T), (-1.3, 0.78))
    c.wire((L, -1.0), (L, Bt), (-1.3, Bt), (-1.3, -0.78))
    c.wire((1.3, 0.78), (1.3, T), (R, T), (R, 1.0))
    c.wire((1.3, -0.78), (1.3, Bt), (R, Bt), (R, -1.0))
    c.loop((L, Bt), (L, T), (-1.3, T), (-1.3, Bt))
    c.loop((1.3, Bt), (1.3, T), (R, T), (R, Bt))
    c.glow(lamp, S.YELLOW, 1.0)
    return c


CIRCUITS.update({"diode_lamp": diode_lamp, "fuse_lamp": fuse_lamp, "button_led": button_led,
                 "motor_switch": motor_switch, "rc_charge": rc_charge, "zener_regulator": zener_regulator,
                 "pot_divider": pot_divider, "ldr_divider": ldr_divider, "thermistor_divider": thermistor_divider,
                 "npn_led": npn_led, "transformer_lamp": transformer_lamp})
