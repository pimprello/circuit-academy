"""Shared look + building blocks for every episode (Shorts, 1080x1920)."""
import numpy as np
from manim import *
from ca import style as S
from ca.symbols import P

config.frame_width = 8
config.frame_height = 8 * 16 / 9
config.background_color = S.BG

FH = config.frame_height              # 14.22
TOP_SAFE = FH / 2 - 330 / 1920 * FH   # nothing above this (iPhone Dynamic Island / notch + YouTube's top icons)


# ───────────────────────────── style helpers ─────────────────────────────
def H(text, size=96, color=S.TEXT):
    return Text(text, font=S.HEAD_FONT, weight=ULTRABOLD, slant=ITALIC, font_size=size, color=color)


def B(text, size=34, color=S.TEXT, weight=BOLD):
    return Text(text, font=S.BODY_FONT, weight=weight, font_size=size, color=color)


def neon(m, color, strength=1.0):
    """Soft neon halo behind any stroked shape (wider, faint copies underneath)."""
    halo = VGroup()
    for w, o in ((26, 0.06), (16, 0.10), (9, 0.18)):
        c = m.copy().set_fill(opacity=0).set_stroke(color, width=w, opacity=o * strength)
        halo.add(c)
    return halo


def glow_disc(colour, r=1.0, layers=12, peak=0.16):
    return VGroup(*[Circle(radius=r * (0.25 + 0.75 * i / layers), stroke_width=0, fill_color=colour,
                           fill_opacity=peak * (1 - i / layers) ** 0.6) for i in range(layers)])


def label_chip(text, colour):
    t = B(text, 30, colour)
    box = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.32, corner_radius=0.2,
                           stroke_color=colour, stroke_width=2.5, fill_color=colour, fill_opacity=0.12)
    return VGroup(box, t)


def background():
    g = VGroup()
    for x in np.arange(-4, 4.01, 0.5):
        g.add(Line(P(x, -FH / 2), P(x, FH / 2), stroke_color=S.GRID, stroke_width=1.1, stroke_opacity=0.8))
    for y in np.arange(-7.5, 7.51, 0.5):
        g.add(Line(P(-4, y), P(4, y), stroke_color=S.GRID, stroke_width=1.1, stroke_opacity=0.8))
    centre = glow_disc("#2A4FA8", 6.0, 18, 0.10).move_to(P(0, 0.8))
    # vignette: darken the edges so the eye goes to the middle
    vig = VGroup(*[Annulus(inner_radius=r, outer_radius=r + 0.6, stroke_width=0, fill_color="#03060F",
                           fill_opacity=min(0.55, 0.07 * i)).move_to(P(0, 0.4)) for i, r in enumerate(np.arange(4.6, 10, 0.6))])
    dust = VGroup(*[Dot(P(np.random.uniform(-3.9, 3.9), np.random.uniform(-7, 7)), radius=np.random.uniform(0.012, 0.03),
                        color=S.CYAN, fill_opacity=np.random.uniform(0.15, 0.45)) for _ in range(46)])
    speeds = np.random.uniform(0.05, 0.16, len(dust))

    def drift(m, dt):
        for d, v in zip(m, speeds):
            d.shift(UP * v * dt)
            if d.get_y() > FH / 2:
                d.set_y(-FH / 2)
    dust.add_updater(drift)
    return VGroup(g, centre, dust, vig)


def copper_wire(length=5.0, r=0.32, strip=1.1, colour=("#6FB0FF", "#1E4FCC")):
    """Side view of an insulated wire with a stripped, shiny copper end."""
    core = RoundedRectangle(width=length, height=r * 1.1, corner_radius=r * 0.5, stroke_width=0)
    core.set_fill(["#FFD2A0", "#D97A2B", "#8E4614"], opacity=1).set_sheen_direction(DOWN)
    strands = VGroup(*[Line(P(length / 2 - strip + 0.08, y), P(length / 2 - 0.08, y), stroke_color="#7A3A10",
                            stroke_width=1.4, stroke_opacity=0.55) for y in np.linspace(-r * 0.35, r * 0.35, 4)])
    ins = RoundedRectangle(width=length - strip, height=r * 2, corner_radius=r, stroke_width=0)
    ins.set_fill(list(colour) if isinstance(colour, tuple) else colour, opacity=1).set_sheen_direction(DOWN).shift(LEFT * strip / 2)
    hi = RoundedRectangle(width=length - strip - 0.35, height=r * 0.36, corner_radius=0.08, stroke_width=0,
                          fill_color=WHITE, fill_opacity=0.32).shift(LEFT * strip / 2 + UP * r * 0.5)
    lip = Ellipse(width=r * 0.55, height=r * 2, stroke_width=0, fill_color=colour[1] if isinstance(colour, tuple) else colour,
                  fill_opacity=1).move_to(ins.get_right() + LEFT * r * 0.2)
    return VGroup(core, strands, ins, hi, lip)


def cross_section(r=1.2):
    ins = Circle(radius=r, stroke_width=0)
    ins.set_fill(["#7DB8FF", "#1E4FCC"], opacity=1).set_sheen_direction(DL)
    ring = Circle(radius=r, stroke_color=WHITE, stroke_width=3, stroke_opacity=0.25)
    core = VGroup()
    pts = [ORIGIN] + [0.36 * r * np.array([np.cos(a), np.sin(a), 0]) for a in np.linspace(0, TAU, 7)[:-1]]
    for p in pts:   # 7-strand copper core, like real flexible cable
        c = Circle(radius=0.17 * r, stroke_color="#6E340C", stroke_width=2).move_to(p)
        c.set_fill(["#FFD9AE", "#C9691F"], opacity=1).set_sheen_direction(DL)
        core.add(c)
    return VGroup(glow_disc("#2F7BFF", r * 1.7, 10, 0.12), ins, ring, core)


def flow_dots(path, n, speed, colour=S.YELLOW, radius=0.07):
    """Glowing current dots running round `path` (conventional current)."""
    tr = ValueTracker(0)
    dots = VGroup(*[VGroup(Dot(radius=radius * 2.8, color=colour, fill_opacity=0.18),
                           Dot(radius=radius * 1.7, color=colour, fill_opacity=0.3),
                           Dot(radius=radius, color=WHITE).set_fill(interpolate_color(ManimColor(colour), WHITE, 0.55)))
                    for _ in range(n)])

    def upd(g):
        for i, d in enumerate(g):
            d.move_to(path.point_from_proportion((tr.get_value() + i / n) % 1))
    dots.add_updater(upd)
    upd(dots)
    tr.add_updater(lambda m, dt: m.increment_value(dt * speed))
    return dots, tr


def stop_flow(scene, dots, tr):
    scene.remove(tr)
    dots.clear_updaters()


def bell_icon(colour=WHITE):
    """Notification bell: dome + flared skirt, knob on top, clapper below."""
    pts = [(-0.34, -0.22), (-0.27, -0.12), (-0.24, 0.08), (-0.18, 0.24), (0, 0.32), (0.18, 0.24),
           (0.24, 0.08), (0.27, -0.12), (0.34, -0.22)]
    body = VMobject(stroke_width=0, fill_color=colour, fill_opacity=1)
    body.set_points_smoothly([P(*p) for p in pts])
    body.add_line_to(P(-0.34, -0.22))
    knob = Circle(radius=0.05, stroke_width=0, fill_color=colour, fill_opacity=1).move_to(P(0, 0.35))
    clap = Circle(radius=0.07, stroke_width=0, fill_color=colour, fill_opacity=1).move_to(P(0, -0.3))
    return VGroup(body, knob, clap)


def cursor():
    """Mouse pointer with a black outline and a soft drop shadow. `cursor.tip` is the hot spot:
    move it with point_cursor(cur, point)."""
    pts = [(0, 0), (0, -0.78), (0.19, -0.6), (0.33, -0.92), (0.45, -0.86), (0.31, -0.56), (0.56, -0.56)]
    arrow = Polygon(*[P(*p) for p in pts], stroke_color=BLACK, stroke_width=4.5, fill_color=WHITE, fill_opacity=1)
    arrow.set_stroke(BLACK, 4.5).round_corners(0.02)
    shadow = VGroup(*[arrow.copy().set_fill(BLACK, o).set_stroke(BLACK, w, o).shift(P(0.07, -0.09))
                      for w, o in ((18, 0.06), (10, 0.12), (3, 0.3))])
    tip = Dot(P(0, 0), radius=0.001, fill_opacity=0)
    g = VGroup(shadow, arrow, tip)
    g.tip = tip
    g.set_z_index(20)
    return g


def point_cursor(cur, point):
    """Shift so the pointer's tip sits on `point`."""
    return cur.shift(np.array(point) - cur.tip.get_center())


def title_mob(name, accent_from):
    t = H(name, 132, S.TEXT)
    t[accent_from:].set_color(S.YELLOW)
    if t.width > 7.2:
        t.scale_to_fit_width(7.2)
    return t
