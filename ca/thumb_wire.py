"""Hand-drawn custom thumbnail for THE WIRE (1080x1920, vertical for Shorts).

Built as its own illustration, not a frame from the video:
- a sunburst of light behind a big 3D cut wire seen end-on, copper strands glowing hot
- a hand-drawn red marker ring + curved arrow on the copper
- a two-line curiosity headline with a gradient fill, thick outline and drop shadow
Everything important sits in the middle of the frame so it still reads when the feed crops it."""
import numpy as np
from manim import *
from ca import style as S
from ca.symbols import P
from ca.short_wire import glow_disc

config.frame_width = 8
config.frame_height = 8 * 16 / 9
config.background_color = "#061226"


def headline(text, size, colours, stroke=16, shadow=0.12):
    t = Text(text, font=S.HEAD_FONT, weight=ULTRABOLD, slant=ITALIC, font_size=size)
    t.set_color_by_gradient(*colours)
    t.set_stroke(BLACK, stroke, background=True)
    sh = t.copy().set_fill(BLACK, 0.55).set_stroke(BLACK, stroke, 0.55, background=True).shift(P(shadow, -shadow))
    return VGroup(sh, t)


def sunburst(centre, n=22, r=9, colour="#FFB347", opacity=0.10):
    rays = VGroup()
    for i in range(n):
        a0 = TAU * i / n
        w = TAU / n * 0.42
        rays.add(Polygon(centre, centre + r * np.array([np.cos(a0), np.sin(a0), 0]),
                         centre + r * np.array([np.cos(a0 + w), np.sin(a0 + w), 0]),
                         stroke_width=0, fill_color=colour, fill_opacity=opacity))
    return rays


def _rot(v, a):
    return np.array([v[0] * np.cos(a) - v[1] * np.sin(a), v[0] * np.sin(a) + v[1] * np.cos(a), 0])


def wire_end_on(centre, rx=1.3, ry=1.55, length=6.0, angle=-28 * DEGREES):
    """A thick cable coming towards the viewer, cut clean: body + insulation face + 7 copper strands."""
    d = np.array([np.cos(angle), np.sin(angle), 0])          # the cable runs away from us this way
    n = np.array([-d[1], d[0], 0])
    far = centre + d * length
    body = Polygon(centre + n * ry, far + n * ry * 0.8, far - n * ry * 0.8, centre - n * ry, stroke_width=0)
    body.set_fill(["#7CB8FF", "#1D4FC9", "#0E2C7A"], 1).set_sheen_direction(-n)
    hi = Polygon(centre + n * ry * 0.72, far + n * ry * 0.6, far + n * ry * 0.45, centre + n * ry * 0.5,
                 stroke_width=0, fill_color=WHITE, fill_opacity=0.28)
    face = Ellipse(width=2 * rx, height=2 * ry, stroke_width=0).rotate(angle).move_to(centre)
    face.set_fill(["#A8D2FF", "#2E66DD"], 1).set_sheen_direction(UL)
    rim = face.copy().set_fill(opacity=0).set_stroke(WHITE, 5, 0.5)
    inner = Ellipse(width=2 * rx * 0.68, height=2 * ry * 0.68, stroke_width=0, fill_color="#3A1A05",
                    fill_opacity=1).rotate(angle).move_to(centre)
    strands = VGroup()
    sx, sy = rx * 0.21, ry * 0.21
    offs = [(0, 0)] + [(np.cos(a) * 2.05, np.sin(a) * 2.05) for a in np.linspace(0, TAU, 7)[:-1]]
    for ox, oy in offs:
        c = centre + _rot(np.array([ox * sx, oy * sy, 0]), angle)
        e = Ellipse(width=2 * sx * 0.95, height=2 * sy * 0.95, stroke_color="#7A360A", stroke_width=2.5)
        e.rotate(angle).move_to(c)
        e.set_fill(["#FFF0D2", "#FFB25A", "#C4601B"], 1).set_sheen_direction(UL)
        spec = Ellipse(width=sx * 0.6, height=sy * 0.38, stroke_width=0, fill_color=WHITE, fill_opacity=0.75)
        spec.rotate(angle).move_to(c + P(-sx * 0.3, sy * 0.35))
        strands.add(VGroup(e, spec))
    heat = glow_disc("#FF9A3C", ry * 1.1, 14, 0.2).move_to(centre)
    return VGroup(body, hi, face, rim, inner, heat, strands)


def sparks(centre, n=18, seed=4):
    rng = np.random.default_rng(seed)
    g = VGroup()
    for _ in range(n):
        a = rng.uniform(0, TAU)
        r0 = rng.uniform(1.75, 2.3)
        ln = rng.uniform(0.25, 0.7)
        u = np.array([np.cos(a), np.sin(a), 0])
        g.add(Line(centre + r0 * u, centre + (r0 + ln) * u, stroke_color=str(rng.choice(["#FFE08A", "#FFFFFF", "#FFB347"])),
                   stroke_width=rng.uniform(3, 7)))
    return g


def scribble_circle(centre, rx, ry, colour="#FF2E2E"):
    """Slightly wobbly marker ring, drawn 1.15 times round like a real hand-drawn circle."""
    ts = np.linspace(0, TAU * 1.15, 120)
    pts = [centre + np.array([rx * (1 + 0.04 * np.sin(5 * t)) * np.cos(t + 0.3),
                              ry * (1 + 0.05 * np.cos(3 * t)) * np.sin(t + 0.3), 0]) for t in ts]
    m = VMobject(stroke_color=colour, stroke_width=16)
    m.set_points_smoothly(pts)
    return m


class ThumbWire(Scene):
    def construct(self):
        hero_c = P(0.45, -1.35)
        self.add(glow_disc("#0F4C75", 7.5, 20, 0.12).move_to(P(0, -0.5)))
        self.add(sunburst(hero_c))
        self.add(glow_disc("#FF7A1A", 3.6, 18, 0.14).move_to(hero_c))
        self.add(wire_end_on(hero_c), sparks(hero_c))

        ring = scribble_circle(hero_c, 1.15, 1.25)
        lab = headline("COPPER!", 100, ["#FFE2BC", "#FF9A3C"], stroke=12, shadow=0.08).rotate(8 * DEGREES)
        lab.move_to(P(-1.45, 1.3))
        arrow = CurvedArrow(P(-2.45, 0.7), hero_c + P(-1.2, 0.25), angle=0.9, stroke_width=14,
                            color="#FF2E2E", tip_length=0.42)
        self.add(ring, arrow, lab)

        vig = VGroup(*[Annulus(inner_radius=r, outer_radius=r + 0.6, stroke_width=0, fill_color=BLACK,
                               fill_opacity=min(0.6, 0.08 * i)).move_to(P(0, -0.6))
                       for i, r in enumerate(np.arange(4.4, 11, 0.6))])
        self.add(vig)

        l1 = headline("WHAT'S INSIDE", 150, ["#FFFFFF", "#DDE7FF"])
        l2 = headline("A WIRE?", 262, ["#FFF27A", "#FFC21A", "#FF9A1A"], stroke=20, shadow=0.16)
        head = VGroup(l1, l2).arrange(DOWN, buff=-0.05)
        head.scale_to_fit_width(7.4).rotate(-3 * DEGREES).move_to(P(0, 4.0))
        self.add(head)

        bolt = Polygon(P(0.12, 0.5), P(-0.28, -0.05), P(-0.02, -0.05), P(-0.16, -0.5), P(0.28, 0.08), P(0.02, 0.08),
                       stroke_color=BLACK, stroke_width=6, fill_color="#FFE14D", fill_opacity=1)
        badge = VGroup(Circle(radius=0.62, stroke_color=BLACK, stroke_width=6, fill_color="#FF2E2E", fill_opacity=1),
                       bolt.scale(1.05)).rotate(12 * DEGREES).move_to(P(2.9, 1.75))
        self.add(badge)
