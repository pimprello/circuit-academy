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


def cells_series(L=-1.7, R=2.5, T=2.6, Bt=-2.6):
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
