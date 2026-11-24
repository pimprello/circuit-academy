"""Channel branding in the same look as the Shorts.
  BRAND=pfp    manim -s -r 800,800   ca/brand.py Pfp
  BRAND=banner manim -s -r 2560,1440 ca/brand.py Banner"""
import os
import numpy as np
from manim import *
from ca import style as S
from ca.symbols import P, Resistor, Capacitor, LED, NPN, Battery, Inductor, Diode
from ca.kit import glow_disc, neon

if os.environ.get("BRAND") == "pfp":
    config.frame_width, config.frame_height = 8, 8
else:
    config.frame_width, config.frame_height = 16, 9
config.background_color = S.BG


def grid(w, h, step=0.5, col=S.GRID, op=0.8):
    g = VGroup()
    for x in np.arange(-w / 2, w / 2 + 0.01, step):
        g.add(Line(P(x, -h / 2), P(x, h / 2), stroke_color=col, stroke_width=1.2, stroke_opacity=op))
    for y in np.arange(-h / 2, h / 2 + 0.01, step):
        g.add(Line(P(-w / 2, y), P(w / 2, y), stroke_color=col, stroke_width=1.2, stroke_opacity=op))
    return g


def trace(*pts, col=S.CYAN, w=5, node=True):
    """PCB-style trace with a pad at each end, plus a soft neon halo."""
    m = VMobject(stroke_color=col, stroke_width=w)
    m.set_points_as_corners([P(*p) for p in pts])
    g = VGroup(neon(m, col, 0.7), m)
    if node:
        for p in (pts[0], pts[-1]):
            g.add(Circle(radius=0.09, stroke_color=col, stroke_width=4, fill_color=S.BG, fill_opacity=1).move_to(P(*p)))
    return g


def bolt(h=3.0):
    pts = [(0.25, 0.5), (-0.35, -0.05), (-0.03, -0.05), (-0.22, -0.5), (0.38, 0.1), (0.05, 0.1)]
    b = Polygon(*[P(x * h, y * h) for x, y in pts], stroke_color="#FFF6C9", stroke_width=5)
    b.set_fill(["#FFF27A", "#FFC21A", "#FF9A1A"], 1).set_sheen_direction(DOWN)
    return b


class Pfp(Scene):
    def construct(self):
        self.add(grid(8, 8, 0.5, S.GRID, 0.6))
        self.add(glow_disc("#1F4FBF", 3.8, 18, 0.13))
        # ring of circuit traces running out from the emblem
        ring = Circle(radius=2.45, stroke_color=S.CYAN, stroke_width=10)
        self.add(neon(ring, S.CYAN, 1.0), ring)
        inner = Circle(radius=2.05, stroke_color=S.CYAN, stroke_width=3, stroke_opacity=0.5)
        self.add(inner)
        for a in np.linspace(0, TAU, 9)[:-1] + PI / 8:
            u = np.array([np.cos(a), np.sin(a), 0])
            n = np.array([-u[1], u[0], 0])
            p0 = u * 2.45
            p1 = u * 3.05
            p2 = p1 + n * 0.45
            m = VMobject(stroke_color=S.CYAN, stroke_width=5, stroke_opacity=0.85)
            m.set_points_as_corners([p0, p1, p2])
            self.add(m, Circle(radius=0.1, stroke_color=S.CYAN, stroke_width=4, fill_color=S.BG, fill_opacity=1).move_to(p2))
        self.add(glow_disc(S.YELLOW, 1.9, 14, 0.16))
        b = bolt(3.3)
        self.add(b.copy().set_fill(BLACK, 0.5).set_stroke(width=0).shift(P(0.08, -0.1)), b)


class Banner(Scene):
    def construct(self):
        np.random.seed(5)
        # 16 x 9 units = 2560 x 1440 px; YouTube's always-visible safe area is the centre 1546 x 423 px
        # = 9.66 x 2.64 units. Name + tagline live inside it; decoration extends outwards.
        self.add(grid(16, 9, 0.5, S.GRID, 0.7))
        self.add(glow_disc("#1F4FBF", 6.5, 20, 0.11).stretch(1.7, 0))

        # glowing circuit traces running out to the edges
        for ys, side in ((0.95, 1), (-0.95, 1), (0.95, -1), (-0.95, -1)):
            x0 = side * 5.0
            self.add(trace((x0, ys), (side * 6.2, ys), (side * 6.7, ys + np.sign(ys) * 0.5), (side * 8.2, ys + np.sign(ys) * 0.5),
                           col=S.CYAN if ys > 0 else S.PURPLE))
        # schematic symbols floating either side of the name (outside the text, inside the frame)
        syms = [(Resistor(color=S.ORANGE), (-6.3, 0.0)), (LED(), (6.3, 0.05)), (Capacitor(), (-7.4, 2.4)),
                (NPN(), (7.05, -2.3)), (Battery(cells=2), (-7.3, -2.4)), (Diode(), (7.35, 2.45)),
                (Inductor(), (-3.9, 3.4)), (Resistor(color=S.ORANGE), (4.1, -3.4))]
        for s, at in syms:
            s.scale(0.75).move_to(P(*at))
            self.add(glow_disc(s.color_, 0.9, 8, 0.07).move_to(s), s)

        name_l = Text("CIRCUIT", font=S.HEAD_FONT, weight=ULTRABOLD, slant=ITALIC, font_size=210, color=S.TEXT)
        name_r = Text("ACADEMY", font=S.HEAD_FONT, weight=ULTRABOLD, slant=ITALIC, font_size=210)
        name_r.set_color_by_gradient("#FFF27A", "#FFC21A", "#FF9A1A")
        name = VGroup(name_l, name_r).arrange(RIGHT, buff=0.35)
        name.scale_to_fit_width(7.9)
        b = bolt(1.1).next_to(name, LEFT, buff=0.28)
        VGroup(b, name).move_to(P(0, 0.42))          # bolt + name together stay inside the mobile-safe centre
        sh = name.copy().set_fill(BLACK, 0.55).shift(P(0.07, -0.08))
        accent = Line(P(-3.2, 0), P(3.2, 0), stroke_color=S.CYAN, stroke_width=7).next_to(name, DOWN, buff=0.17)
        tag = Text("Electronics explained in under a minute  ·  a new part twice a day",
                   font=S.BODY_FONT, weight=MEDIUM, font_size=40, color="#B9C6E4")
        tag.scale_to_fit_width(min(tag.width, 8.0)).next_to(accent, DOWN, buff=0.2)
        block = VGroup(b, name, accent)            # tagline removed (style decision)
        block.move_to(P(0, 0.05))
        accent.set_x(name.get_x())
        sh = name.copy().set_fill(BLACK, 0.55).shift(P(0.07, -0.08))
        self.add(sh, name, neon(accent, S.CYAN), accent, b)
