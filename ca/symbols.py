"""Schematic symbols drawn to the standard IEEE / ANSI conventions used in most
textbooks (with IEC variants where the UK/EU symbol differs).

Every part is a VGroup built in local coordinates with its pins as invisible
marker dots, so after any shift/rotate/scale `part.pin("a")` still returns the
right point to wire to.  Two-terminal parts run along the x-axis from pin "a"
(-1, 0) to pin "b" (+1, 0); their length is 2 units.
"""
import numpy as np
from manim import (VGroup, VMobject, Dot, Circle, Line, Arc, Polygon, Rectangle,
                   Text, ArcBetweenPoints, DashedLine, RoundedRectangle,
                   ORIGIN, UP, DOWN, LEFT, RIGHT, PI, DEGREES)
from . import style as S


def P(x, y):
    return np.array([x, y, 0.0])


def poly(*pts, color=S.WIRE, width=S.STROKE, closed=False):
    m = VMobject(stroke_color=color, stroke_width=width)
    pts = [P(*p) if len(p) == 2 else np.array(p) for p in pts]
    if closed:
        pts = pts + [pts[0]]
    m.set_points_as_corners(pts)
    return m


def arrow_head(tip, direction, size=0.16, color=S.WIRE):
    d = np.array(direction, dtype=float)
    d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0], 0.0])
    tip = np.array(tip, dtype=float)
    base = tip - d * size
    tri = Polygon(tip, base + n * size * 0.55, base - n * size * 0.55,
                  stroke_color=color, stroke_width=2, fill_color=color, fill_opacity=1)
    return tri


def small_arrow(start, end, color=S.YELLOW, width=3, head=0.13):
    start, end = np.array(start, float), np.array(end, float)
    shaft = Line(start, end - (end - start) / np.linalg.norm(end - start) * head * 0.6,
                 stroke_color=color, stroke_width=width)
    return VGroup(shaft, arrow_head(end, end - start, head, color))


class Part(VGroup):
    kind = "part"

    def __init__(self, color=None, **kw):
        super().__init__(**kw)
        self.color_ = color or S.PART_COLOURS.get(self.kind, S.WIRE)
        self._pins = {}
        self.body = VGroup()
        self.leads = VGroup()
        self.extras = VGroup()
        self.under = VGroup()      # glows etc. drawn beneath the symbol
        self.build()
        self.add(self.under, self.leads, self.body, self.extras)
        for name, xy in self.pin_points().items():
            d = Dot(P(*xy), radius=0.001, fill_opacity=0, stroke_opacity=0)
            self._pins[name] = d
            self.add(d)

    # subclasses fill these
    def build(self):
        pass

    def pin_points(self):
        return {"a": (-1, 0), "b": (1, 0)}

    def pin(self, name):
        return self._pins[name].get_center()

    def place(self, at=(0, 0), angle=0):
        """angle in degrees, counter-clockwise; at = where the part's centre goes."""
        if angle:
            self.rotate(angle * DEGREES, about_point=ORIGIN)
        self.shift(P(*at))
        return self

    def lead(self, *pts):
        self.leads.add(poly(*pts, color=S.WIRE))


# ───────────────────────────── passive parts ──────────────────────────────
class Resistor(Part):
    kind = "resistor"

    def __init__(self, iec=False, **kw):
        self.iec = iec
        super().__init__(**kw)

    def build(self):
        if self.iec:
            self.lead((-1, 0), (-0.5, 0)); self.lead((0.5, 0), (1, 0))
            self.body.add(Rectangle(width=1.0, height=0.36, stroke_color=self.color_,
                                    stroke_width=S.STROKE))
        else:
            self.lead((-1, 0), (-0.55, 0)); self.lead((0.55, 0), (1, 0))
            pts = [(-0.55, 0)]
            n = 6
            for i in range(n):
                x = -0.55 + (i + 0.5) * (1.1 / n)
                pts.append((x, 0.2 if i % 2 == 0 else -0.2))
            pts.append((0.55, 0))
            self.body.add(poly(*pts, color=self.color_))


class Potentiometer(Resistor):
    """Resistor with a wiper arrow; pin "w" is the wiper (above the middle)."""

    def build(self):
        super().build()
        self.body.add(poly((0, 0.9), (0, 0.42), color=S.WIRE))
        self.body.add(arrow_head(P(0, 0.26), DOWN, 0.2, self.color_))

    def pin_points(self):
        return {"a": (-1, 0), "b": (1, 0), "w": (0, 0.9)}


class Thermistor(Resistor):
    """IEC thermistor: box crossed by a line with a flat 'hockey-stick' end, -t° (NTC)."""

    def __init__(self, **kw):
        super().__init__(iec=True, **kw)

    def build(self):
        super().build()
        self.body.add(poly((-0.75, -0.42), (-0.5, -0.42), (0.6, 0.45), color=S.WIRE, width=3))
        self.body.add(Text("-t°", font=S.BODY_FONT, font_size=18, color=S.TEXT).move_to(P(0.78, -0.42)))


class LDR(Resistor):
    """Light-dependent resistor: resistor with two light arrows pointing in."""

    def __init__(self, **kw):
        super().__init__(iec=True, **kw)

    def build(self):
        super().build()
        for dx in (-0.25, 0.15):
            self.body.add(small_arrow(P(dx - 0.45, 0.95), P(dx - 0.05, 0.32), S.YELLOW))


class Fuse(Part):
    kind = "fuse"

    def build(self):
        self.lead((-1, 0), (-0.45, 0)); self.lead((0.45, 0), (1, 0))
        self.body.add(Rectangle(width=0.9, height=0.32, stroke_color=self.color_, stroke_width=S.STROKE))
        self.body.add(poly((-0.45, 0), (0.45, 0), color=self.color_, width=3))


class Capacitor(Part):
    kind = "capacitor"

    def __init__(self, polarised=False, **kw):
        self.polarised = polarised
        super().__init__(**kw)

    def build(self):
        g = 0.13
        self.lead((-1, 0), (-g, 0)); self.lead((g, 0), (1, 0))
        self.body.add(poly((-g, 0.42), (-g, -0.42), color=self.color_, width=S.STROKE + 1))
        if self.polarised:
            arc = ArcBetweenPoints(P(g + 0.12, 0.42), P(g + 0.12, -0.42), angle=-50 * DEGREES,
                                   stroke_color=self.color_, stroke_width=S.STROKE + 1)
            self.body.add(arc)
            self.body.add(Text("+", font=S.BODY_FONT, font_size=26, color=S.TEXT).move_to(P(-0.38, 0.42)))
        else:
            self.body.add(poly((g, 0.42), (g, -0.42), color=self.color_, width=S.STROKE + 1))


class Inductor(Part):
    kind = "inductor"

    def __init__(self, core=False, **kw):
        self.core = core
        super().__init__(**kw)

    def build(self):
        n, r = 4, 0.15
        x0 = -n * r
        self.lead((-1, 0), (x0, 0)); self.lead((-x0, 0), (1, 0))
        for i in range(n):
            a = P(x0 + 2 * r * i, 0)
            b = P(x0 + 2 * r * (i + 1), 0)
            self.body.add(ArcBetweenPoints(a, b, angle=-PI, stroke_color=self.color_, stroke_width=S.STROKE))
        if self.core:
            for y in (0.26, 0.34):
                self.body.add(poly((x0, y), (-x0, y), color=S.WIRE, width=3))


class Crystal(Part):
    kind = "ic"

    def build(self):
        self.lead((-1, 0), (-0.28, 0)); self.lead((0.28, 0), (1, 0))
        self.body.add(poly((-0.28, 0.4), (-0.28, -0.4), color=self.color_))
        self.body.add(poly((0.28, 0.4), (0.28, -0.4), color=self.color_))
        self.body.add(Rectangle(width=0.3, height=0.62, stroke_color=self.color_, stroke_width=S.STROKE))


# ───────────────────────────── semiconductors ─────────────────────────────
class Diode(Part):
    """Anode = pin "a" (left), cathode = pin "b" (right, the bar)."""
    kind = "diode"

    def build(self):
        self.lead((-1, 0), (-0.3, 0)); self.lead((0.3, 0), (1, 0))
        self.tri = Polygon(P(-0.3, 0.32), P(-0.3, -0.32), P(0.3, 0), stroke_color=self.color_,
                           stroke_width=S.STROKE, fill_color=self.color_, fill_opacity=0.25)
        self.body.add(self.tri)
        self.body.add(self.bar())

    def bar(self):
        return poly((0.3, 0.34), (0.3, -0.34), color=self.color_, width=S.STROKE + 1)


class Zener(Diode):
    kind = "zener"

    def bar(self):
        return poly((0.18, 0.44), (0.3, 0.34), (0.3, -0.34), (0.42, -0.44), color=self.color_, width=S.STROKE + 1)


class LED(Diode):
    kind = "led"

    def build(self):
        super().build()
        self.rays = VGroup(small_arrow(P(0.0, 0.45), P(0.4, 0.95), self.color_),
                           small_arrow(P(0.3, 0.38), P(0.7, 0.88), self.color_))
        self.extras.add(self.rays)
        # glow disc, invisible until lit (scene animates its opacity)
        self.glow = Circle(radius=0.55, stroke_width=0, fill_color=self.color_, fill_opacity=0).move_to(P(0, 0))
        self.under.add(self.glow)


class Photodiode(Diode):
    def build(self):
        super().build()
        self.extras.add(small_arrow(P(0.75, 1.0), P(0.3, 0.45), S.YELLOW),
                        small_arrow(P(1.05, 0.9), P(0.6, 0.38), S.YELLOW))


class NPN(Part):
    """Pins: "b" base (left), "c" collector (top), "e" emitter (bottom)."""
    kind = "transistor"
    pnp = False

    def build(self):
        self.body.add(Circle(radius=0.62, stroke_color=self.color_, stroke_width=3).move_to(P(0.08, 0)))
        self.lead((-1, 0), (-0.22, 0))
        self.body.add(poly((-0.22, 0.38), (-0.22, -0.38), color=self.color_, width=S.STROKE + 2))
        self.body.add(poly((-0.22, 0.16), (0.3, 0.46), color=S.WIRE))
        self.lead((0.3, 0.46), (0.3, 1.0))
        self.body.add(poly((-0.22, -0.16), (0.3, -0.46), color=S.WIRE))
        self.lead((0.3, -0.46), (0.3, -1.0))
        a, b = P(-0.22, -0.16), P(0.3, -0.46)
        if self.pnp:   # arrow points IN towards the base
            self.body.add(arrow_head(a + (b - a) * 0.3, a - b, 0.2, S.WIRE))
        else:          # arrow points OUT of the emitter
            self.body.add(arrow_head(a + (b - a) * 0.85, b - a, 0.2, S.WIRE))

    def pin_points(self):
        return {"b": (-1, 0), "c": (0.3, 1.0), "e": (0.3, -1.0)}


class PNP(NPN):
    pnp = True

    def pin_points(self):   # for PNP the emitter is drawn on top (connects to +)
        return {"b": (-1, 0), "e": (0.3, -1.0), "c": (0.3, 1.0)}


class NMOS(Part):
    """Enhancement-mode N-channel MOSFET. Pins: "g" gate, "d" drain (top), "s" source (bottom).
    Body arrow points in (N-channel) and the body is tied to the source."""
    kind = "mosfet"

    def build(self):
        self.lead((-1, 0), (-0.38, 0))
        self.body.add(poly((-0.38, 0.4), (-0.38, -0.4), color=self.color_, width=S.STROKE + 1))   # gate plate
        for y0, y1 in ((0.26, 0.48), (-0.11, 0.11), (-0.48, -0.26)):                       # broken channel
            self.body.add(poly((-0.22, y0), (-0.22, y1), color=self.color_, width=S.STROKE + 2))
        self.body.add(poly((-0.22, 0.37), (0.3, 0.37), color=S.WIRE))
        self.lead((0.3, 0.37), (0.3, 1.0))
        self.body.add(poly((-0.22, -0.37), (0.3, -0.37), color=S.WIRE))
        self.lead((0.3, -0.37), (0.3, -1.0))
        self.body.add(poly((-0.22, 0), (0.3, 0), (0.3, -0.37), color=S.WIRE))
        self.body.add(arrow_head(P(-0.2, 0), LEFT, 0.2, S.WIRE))
        self.body.add(Circle(radius=0.62, stroke_color=self.color_, stroke_width=3).move_to(P(0.02, 0)))

    def pin_points(self):
        return {"g": (-1, 0), "d": (0.3, 1.0), "s": (0.3, -1.0)}


# ───────────────────────────── sources & switches ─────────────────────────
class Battery(Part):
    """Pin "a" is POSITIVE (long plate side), pin "b" negative."""
    kind = "battery"

    def __init__(self, cells=2, **kw):
        self.cells = cells
        super().__init__(**kw)

    def build(self):
        step = 0.22
        total = (self.cells * 2 - 1) * step
        x = -total / 2
        self.lead((-1, 0), (x, 0))
        for i in range(self.cells):
            self.body.add(poly((x, 0.45), (x, -0.45), color=self.color_, width=S.STROKE))           # long +
            self.body.add(poly((x + step, 0.22), (x + step, -0.22), color=self.color_, width=S.STROKE + 3))  # short -
            if i < self.cells - 1:
                self.body.add(DashedLine(P(x + step, 0), P(x + 2 * step, 0), stroke_color=S.MUTED,
                                         stroke_width=2, dash_length=0.04) if self.cells > 3 else
                              poly((x + step, 0), (x + 2 * step, 0)))
            x += 2 * step
        self.lead((x - step, 0), (1, 0))
        self.extras.add(Text("+", font=S.BODY_FONT, font_size=26, color=S.TEXT).move_to(P(-total / 2 - 0.22, 0.42)))


class ACSource(Part):
    kind = "battery"

    def build(self):
        self.lead((-1, 0), (-0.45, 0)); self.lead((0.45, 0), (1, 0))
        self.body.add(Circle(radius=0.45, stroke_color=self.color_, stroke_width=S.STROKE))
        xs = np.linspace(-0.27, 0.27, 40)
        self.body.add(poly(*[(x, 0.14 * np.sin(x / 0.27 * PI)) for x in xs], color=self.color_, width=3).rotate(90 * DEGREES))


class Lamp(Part):
    kind = "lamp"

    def build(self):
        self.lead((-1, 0), (-0.4, 0)); self.lead((0.4, 0), (1, 0))
        self.glow = Circle(radius=0.62, stroke_width=0, fill_color=S.YELLOW, fill_opacity=0)
        self.under.add(self.glow)
        self.body.add(Circle(radius=0.4, stroke_color=self.color_, stroke_width=S.STROKE))
        d = 0.4 / np.sqrt(2)
        self.body.add(poly((-d, -d), (d, d), color=self.color_), poly((-d, d), (d, -d), color=self.color_))


class Motor(Part):
    kind = "motor"

    def build(self):
        self.lead((-1, 0), (-0.45, 0)); self.lead((0.45, 0), (1, 0))
        self.body.add(Circle(radius=0.45, stroke_color=self.color_, stroke_width=S.STROKE))
        self.body.add(Text("M", font=S.BODY_FONT, weight="BOLD", font_size=30, color=self.color_))


class Meter(Part):
    kind = "meter"

    def __init__(self, letter="V", **kw):
        self.letter = letter
        super().__init__(**kw)

    def build(self):
        self.lead((-1, 0), (-0.42, 0)); self.lead((0.42, 0), (1, 0))
        self.body.add(Circle(radius=0.42, stroke_color=self.color_, stroke_width=S.STROKE))
        self.body.add(Text(self.letter, font=S.BODY_FONT, weight="BOLD", font_size=28, color=self.color_))


class Switch(Part):
    """SPST switch. `switch.blade` is the moving part; use `toggle_target()` for the closed pose."""
    kind = "switch"

    def __init__(self, closed=False, **kw):
        self.closed = closed
        super().__init__(**kw)

    def build(self):
        self.lead((-1, 0), (-0.45, 0)); self.lead((0.45, 0), (1, 0))
        for x in (-0.45, 0.45):
            self.body.add(Circle(radius=0.06, stroke_color=self.color_, stroke_width=3,
                                 fill_color=S.BG, fill_opacity=1).move_to(P(x, 0)))
        ang = 0 if self.closed else 30 * DEGREES
        self.blade = Line(P(-0.45, 0), P(-0.45 + 0.92 * np.cos(ang), 0.92 * np.sin(ang)),
                          stroke_color=self.color_, stroke_width=S.STROKE)
        self.body.add(self.blade)

    def pin_points(self):
        return {"a": (-1, 0), "b": (1, 0), "_closed": (0.47, 0)}


class PushButton(Part):
    """Normally-open push-to-make button. `button.cap` moves down 0.2 when pressed."""
    kind = "switch"

    def build(self):
        self.lead((-1, 0), (-0.45, 0)); self.lead((0.45, 0), (1, 0))
        for x in (-0.45, 0.45):
            self.body.add(Circle(radius=0.06, stroke_color=self.color_, stroke_width=3,
                                 fill_color=S.BG, fill_opacity=1).move_to(P(x, 0)))
        self.cap = VGroup(poly((-0.5, 0.28), (0.5, 0.28), color=self.color_),
                          poly((0, 0.28), (0, 0.62), color=self.color_),
                          poly((-0.2, 0.62), (0.2, 0.62), color=self.color_))
        self.body.add(self.cap)

    def pin_points(self):
        return {"a": (-1, 0), "b": (1, 0), "_up": (0, 0.28), "_down": (0, 0.07)}


class Ground(Part):
    kind = "meter"

    def build(self):
        self.lead((0, 0), (0, -0.35))
        for i, w in enumerate((0.5, 0.32, 0.14)):
            y = -0.35 - i * 0.12
            self.body.add(poly((-w / 2, y), (w / 2, y), color=S.WIRE))

    def pin_points(self):
        return {"g": (0, 0)}


# ───────────────────────────── multi-pin parts ────────────────────────────
class Transformer(Part):
    """Pins: p1/p2 primary (left, top/bottom), s1/s2 secondary (right)."""
    kind = "transformer"

    def build(self):
        n, r = 4, 0.15
        y0 = n * r
        for side, x in ((-1, -0.32), (1, 0.32)):
            for i in range(n):
                a, b = P(x, y0 - 2 * r * i), P(x, y0 - 2 * r * (i + 1))
                self.body.add(ArcBetweenPoints(a, b, angle=PI * (1 if side < 0 else -1),
                                               stroke_color=self.color_, stroke_width=S.STROKE))
            xp = 1.0 * side
            self.lead((x, y0), (xp, y0)); self.lead((x, -y0), (xp, -y0))
        for x in (-0.05, 0.05):
            self.body.add(poly((x, y0 + 0.1), (x, -y0 - 0.1), color=S.WIRE, width=3))

    def pin_points(self):
        return {"p1": (-1, 0.6), "p2": (-1, -0.6), "s1": (1, 0.6), "s2": (1, -0.6)}


class Relay(Part):
    """Coil (box, pins c1 top / c2 bottom on the left) mechanically linked to a
    normally-open contact (pins com / no on the right). `relay.blade` moves."""
    kind = "relay"

    def build(self):
        self.body.add(Rectangle(width=0.5, height=0.9, stroke_color=self.color_, stroke_width=S.STROKE).move_to(P(-0.7, 0)))
        self.body.add(poly((-0.95, -0.45), (-0.45, 0.45), color=self.color_, width=3))
        self.lead((-0.7, 0.45), (-0.7, 1.0)); self.lead((-0.7, -0.45), (-0.7, -1.0))
        # contact: com at bottom right, NO contact at top right
        for y in (-0.35, 0.35):
            self.body.add(Circle(radius=0.06, stroke_color=self.color_, stroke_width=3,
                                 fill_color=S.BG, fill_opacity=1).move_to(P(0.7, y)))
        self.lead((0.7, 0.41), (0.7, 1.0)); self.lead((0.7, -0.41), (0.7, -1.0))
        self.blade = Line(P(0.7, -0.35), P(0.7 + 0.62 * np.sin(-35 * DEGREES) * -1, -0.35 + 0.62 * np.cos(35 * DEGREES)),
                          stroke_color=self.color_, stroke_width=S.STROKE)
        self.body.add(self.blade)
        self.link = DashedLine(P(-0.45, 0), P(0.9, 0), stroke_color=S.MUTED, stroke_width=2, dash_length=0.08)
        self.body.add(self.link)

    def pin_points(self):
        return {"c1": (-0.7, 1.0), "c2": (-0.7, -1.0), "no": (0.7, 1.0), "com": (0.7, -1.0),
                "_closed": (0.7, 0.33)}


class Inverter(Part):
    """NOT gate / inverting amplifier. Pins: "in", "out"."""
    kind = "ic"

    def build(self):
        self.body.add(Polygon(P(-0.6, 0.55), P(-0.6, -0.55), P(0.5, 0), stroke_color=self.color_,
                              stroke_width=S.STROKE, fill_color=self.color_, fill_opacity=0.08))
        self.body.add(Circle(radius=0.1, stroke_color=self.color_, stroke_width=S.STROKE).move_to(P(0.6, 0)))
        self.lead((-1.3, 0), (-0.6, 0)); self.lead((0.7, 0), (1.3, 0))

    def pin_points(self):
        return {"in": (-1.3, 0), "out": (1.3, 0)}


class OpAmp(Part):
    """Pins: "inv" (-) top input, "non" (+) bottom input, "out"."""
    kind = "ic"

    def build(self):
        self.body.add(Polygon(P(-0.75, 0.9), P(-0.75, -0.9), P(0.95, 0), stroke_color=self.color_,
                              stroke_width=S.STROKE, fill_color=self.color_, fill_opacity=0.08))
        self.lead((-1.3, 0.45), (-0.75, 0.45)); self.lead((-1.3, -0.45), (-0.75, -0.45))
        self.lead((0.95, 0), (1.3, 0))
        self.body.add(Text("−", font=S.BODY_FONT, font_size=32, color=S.TEXT).move_to(P(-0.52, 0.45)))
        self.body.add(Text("+", font=S.BODY_FONT, font_size=30, color=S.TEXT).move_to(P(-0.52, -0.45)))

    def pin_points(self):
        return {"inv": (-1.3, 0.45), "non": (-1.3, -0.45), "out": (1.3, 0)}


class ICBox(Part):
    """Generic chip: name in the middle; pins given as lists of (pin_id, label)
    per side. Pin points sit 0.45 outside the box edge."""
    kind = "ic"

    def __init__(self, name, left=(), right=(), top=(), bottom=(), w=2.2, h=None, **kw):
        self.chip_name, self.sides = name, dict(left=left, right=right, top=top, bottom=bottom)
        self.w = w
        self.h = h or max(1.6, 0.55 * (max(len(left), len(right)) + 1))
        super().__init__(**kw)

    def _coords(self):
        out = {}
        w, h = self.w, self.h
        for side, pins in self.sides.items():
            n = len(pins)
            for i, (pid, lab) in enumerate(pins):
                t = (i + 1) / (n + 1)
                if side == "left":
                    out[pid] = ((-w / 2, h / 2 - t * h), (-w / 2 - 0.45, h / 2 - t * h), lab, RIGHT)
                elif side == "right":
                    out[pid] = ((w / 2, h / 2 - t * h), (w / 2 + 0.45, h / 2 - t * h), lab, LEFT)
                elif side == "top":
                    out[pid] = ((-w / 2 + t * w, h / 2), (-w / 2 + t * w, h / 2 + 0.45), lab, DOWN)
                else:
                    out[pid] = ((-w / 2 + t * w, -h / 2), (-w / 2 + t * w, -h / 2 - 0.45), lab, UP)
        return out

    def build(self):
        self.body.add(RoundedRectangle(width=self.w, height=self.h, corner_radius=0.08, stroke_color=self.color_,
                                       stroke_width=S.STROKE, fill_color=self.color_, fill_opacity=0.07))
        self.body.add(Text(self.chip_name, font=S.HEAD_FONT, weight="BOLD", font_size=34, color=self.color_))
        for pid, (edge, tip, lab, inward) in self._coords().items():
            self.lead(edge, tip)
            if lab:
                t = Text(lab, font=S.MONO_FONT, font_size=15, color=S.MUTED)
                t.move_to(P(*edge) + inward * (0.12 + t.width / 2 if inward[1] == 0 else 0.15))
                self.body.add(t)

    def pin_points(self):
        return {pid: c[1] for pid, c in self._coords().items()}
