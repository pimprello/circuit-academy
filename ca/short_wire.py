"""Style prototype: a YouTube Short about THE WIRE (1080x1920).

Run:  python make_short.py
Beat timings use a word-rate estimate until real narration timings exist
(narration/<beat>.json from the TTS step replaces them)."""
import json
import os
import numpy as np
from manim import *
from ca import style as S
from ca.symbols import Battery, Lamp, poly, P

config.frame_width = 8
config.frame_height = 8 * 16 / 9
config.background_color = S.BG

FH = config.frame_height              # 14.22
TOP_SAFE = FH / 2 - 330 / 1920 * FH   # nothing above this (iPhone Dynamic Island / notch + YouTube's top icons)

BEATS = [
    ("hook",   "Every circuit you have ever used depends on this one simple part."),
    ("inside", "A wire is a path for electric current. Usually copper inside, with plastic insulation outside."),
    ("symbol", "In a circuit diagram, a wire is just a straight line. Close the loop, and current flows."),
    ("joins",  "Where wires connect, we draw a dot. Lines that cross with no dot are not connected."),
    ("thick",  "Thicker wire has less resistance, so it carries more current without getting hot."),
    ("outro",  "Next time: the cell. Subscribe so you don't miss it."),
]
WPS = 2.7   # placeholder speaking rate (words per second)


def beat_durations():
    out = []
    for key, text in BEATS:
        f = os.path.join("narration", f"wire_{key}.json")
        if os.path.exists(f):
            out.append(json.load(open(f))["duration"] + 0.35)
        else:
            out.append(len(text.split()) / WPS + 0.6)
    out[-1] = max(out[-1], 9.2)    # the cinematic ending needs room to breathe
    return out


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
    pts = [(0, 0), (0, -0.78), (0.19, -0.6), (0.33, -0.92), (0.45, -0.86), (0.31, -0.56), (0.56, -0.56)]
    arrow = Polygon(*[P(*p) for p in pts], stroke_color=BLACK, stroke_width=4, fill_color=WHITE, fill_opacity=1)
    shadow = arrow.copy().set_stroke(width=0).set_fill(BLACK, 0.35).shift(P(0.05, -0.06))
    return VGroup(shadow, arrow)


# ───────────────────────────────── scene ─────────────────────────────────
class WireShort(Scene):
    def construct(self):
        np.random.seed(7)
        durs = beat_durations()
        self.add(background())

        title = H("THE WIRE", 132, S.TEXT)
        title[3:].set_color(S.YELLOW)
        title.move_to(P(0, TOP_SAFE - 0.6))
        accent = Line(P(-1.6, 0), P(1.6, 0), stroke_color=S.CYAN, stroke_width=6).next_to(title, DOWN, buff=0.18)
        self.header = VGroup(neon(accent, S.CYAN), accent, title)
        self.title, self.accent = title, accent

        self.header_home = self.header.get_center()
        self.hook_t0 = self.renderer.time
        for (key, _), d in zip(BEATS, durs):
            t0 = self.renderer.time
            getattr(self, "beat_" + key)(d)
            left = d - (self.renderer.time - t0)
            if left > 0.02:
                self.wait(left)

    # ── beats ────────────────────────────────────────────────────────────
    def beat_hook(self, d):
        """First seconds: motion from frame one. Two live wires, an electric arc cracking between them,
        current racing along, a white flash and the title slamming in."""
        left = copper_wire(3.4).move_to(P(-2.35, 0.6))
        right = copper_wire(3.4).rotate(PI).move_to(P(2.35, 0.6))
        tip_l = left[0].get_right() + LEFT * 0.05
        tip_r = right[0].get_left() + RIGHT * 0.05
        stage = VGroup(left, right).scale(1.2, about_point=P(0, 0.6))
        tip_l, tip_r = left[0].get_right() + LEFT * 0.05, right[0].get_left() + RIGHT * 0.05

        def bolt():
            pts = [tip_l]
            n = 9
            for i in range(1, n):
                q = tip_l + (tip_r - tip_l) * i / n
                pts.append(q + UP * np.random.uniform(-0.38, 0.38))
            pts.append(tip_r)
            paths = [pts]
            for _ in range(2):   # little forks crackling off the main bolt
                k = np.random.randint(2, n - 1)
                p0 = pts[k]
                f = [p0]
                for j in range(3):
                    f.append(f[-1] + P(np.random.uniform(-0.12, 0.2), np.random.choice([-1, 1]) * np.random.uniform(0.1, 0.22)))
                paths.append(f)
            g = VGroup()
            for path in paths:
                for w, o, c in ((24, 0.10, S.CYAN), (11, 0.35, S.CYAN), (4, 1, WHITE)):
                    m = VMobject(stroke_color=c, stroke_width=w * (1 if path is pts else 0.6), stroke_opacity=o)
                    m.set_points_as_corners(path)
                    g.add(m)
            return g

        arc = bolt()
        arc.add_updater(lambda m, dt: m.become(bolt()))
        spark_glow = glow_disc(S.CYAN, 1.2, 10, 0.18).move_to((tip_l + tip_r) / 2)
        # current racing along both wires toward the gap
        run_l = Line(left.get_left() + RIGHT * 0.3, tip_l)
        run_r = Line(right.get_right() + LEFT * 0.3, tip_r)
        dl, tl = flow_dots(run_l, 6, 0.9, S.YELLOW, 0.06)
        dr, tr = flow_dots(run_r, 6, 0.9, S.YELLOW, 0.06)
        self.add(stage, spark_glow, arc, dl, tl, dr, tr)
        # frame one is already busy: push in slightly while the arc crackles
        self.play(stage.animate.scale(0.9, about_point=P(0, 0.6)), spark_glow.animate.scale(1.3),
                  run_time=0.6, rate_func=smooth)
        # white flash + title slams down with a small screen shake
        flash = Rectangle(width=9, height=FH + 1, stroke_width=0, fill_color=WHITE, fill_opacity=0.85)
        self.title.scale(1.8).set_opacity(0)
        self.add(flash)
        self.play(FadeOut(flash), self.title.animate.scale(1 / 1.8).set_opacity(1), Create(self.accent),
                  FadeIn(self.header[0]), run_time=0.35, rate_func=rate_functions.ease_out_back)
        for v in (P(0.08, -0.05), P(-0.12, 0.06), P(0.06, 0.04), P(-0.02, -0.05)):
            self.play(stage.animate.shift(v), self.header.animate.shift(v * 0.5), run_time=0.045)
        self.play(stage.animate.move_to(P(0, 0.6)), self.header.animate.move_to(self.header_home), run_time=0.08)
        rest = d - (self.renderer.time - self.hook_t0) - 0.55
        if rest > 0.05:
            self.wait(rest)
        # wires join: the arc closes into one wire for the next beat
        arc.clear_updaters()
        stop_flow(self, dl, tl); stop_flow(self, dr, tr)
        wire = copper_wire(6.4).rotate(-12 * DEGREES).move_to(P(0, 0.8))
        self.play(FadeOut(VGroup(arc, spark_glow, dl, dr)), ReplacementTransform(stage, wire), run_time=0.55)
        self.hook_wire = wire

    def beat_inside(self, d):
        wire = self.hook_wire
        self.play(wire.animate.rotate(12 * DEGREES).scale(0.82).move_to(P(0, 2.25)), run_time=0.7)
        xs = cross_section().move_to(P(-1.55, -0.35))
        cu = label_chip("Copper core", "#FFB070").move_to(P(1.75, 0.35))
        ins = label_chip("Insulation", "#7FB2FF").move_to(P(1.75, -1.05))
        l1 = VGroup(Line(cu.get_left(), P(-1.2, -0.25), stroke_color="#FFB070", stroke_width=4),
                    Dot(P(-1.2, -0.25), radius=0.07, color="#FFB070"))
        l2 = VGroup(Line(ins.get_left(), P(-0.55, -0.95), stroke_color="#7FB2FF", stroke_width=4),
                    Dot(P(-0.55, -0.95), radius=0.07, color="#7FB2FF"))
        self.play(FadeIn(xs, scale=0.6), run_time=0.7, rate_func=smooth)
        self.play(Create(l1), FadeIn(cu, shift=LEFT * 0.3), run_time=0.5)
        self.play(Create(l2), FadeIn(ins, shift=LEFT * 0.3), run_time=0.5)
        self.play(Rotate(xs[3], angle=PI / 6), run_time=max(0.3, d - 3.0), rate_func=smooth)
        self.play(FadeOut(VGroup(wire, xs, cu, ins, l1, l2), shift=UP * 0.4), run_time=0.45)

    def beat_symbol(self, d):
        L, R, T, Bt = -2.2, 2.2, 2.0, -2.0
        bat = Battery(cells=2).scale(1.3).place((L, 0.0), -90)
        lamp = Lamp().scale(1.3).place((R, 0.0), -90)
        bl = B("9 V", 38, S.GREEN).next_to(bat, LEFT, buff=0.28)
        wires = VGroup(poly((L, 1.3), (L, T), (R, T), (R, 1.3)), poly((R, -1.3), (R, Bt), (L, Bt), (L, -1.3)))
        wires.set_stroke(S.CYAN, 7)
        tag = label_chip("wire  =  straight line", S.CYAN).move_to(P(0, 2.6))
        self.play(FadeIn(tag, shift=DOWN * 0.2), Create(bat), Create(lamp), FadeIn(bl), run_time=0.8)
        self.play(Create(wires[0]), Create(wires[1]), run_time=1.1, rate_func=smooth)
        loop = poly((L, Bt), (L, T), (R, T), (R, Bt), closed=True)
        dots, tr = flow_dots(loop, 18, 0.2)
        halo = neon(wires, S.YELLOW, 0.8)
        lg = glow_disc(S.YELLOW, 1.15, 12, 0.2).move_to(lamp)
        lg.set_z_index(1); lamp.set_z_index(2); bat.set_z_index(2); dots.set_z_index(3)
        self.add(halo, dots, tr)
        self.play(wires.animate.set_stroke(S.WIRE, 5), FadeIn(halo), FadeIn(lg, scale=0.6),
                  lamp.body.animate.set_stroke(S.YELLOW), run_time=0.6)
        self.wait(max(0, d - 3.0))
        stop_flow(self, dots, tr)
        self.play(FadeOut(VGroup(bat, lamp, bl, wires, tag, dots, halo, lg)), run_time=0.45)

    def beat_joins(self, d):
        yes = VGroup(poly((-3.4, 1.0), (-0.6, 1.0)), poly((-2.0, 1.0), (-2.0, -0.9)))
        dot = Dot(P(-2.0, 1.0), radius=0.15, color=S.WIRE)
        no = VGroup(poly((0.6, 0.05), (3.4, 0.05)), poly((2.0, 1.45), (2.0, -1.35)))
        card_l = RoundedRectangle(width=3.45, height=4.4, corner_radius=0.3, stroke_color=S.GREEN, stroke_width=3,
                                  fill_color=S.GREEN, fill_opacity=0.05).move_to(P(-2.0, 0.15))
        card_r = card_l.copy().set_stroke(S.RED).set_fill(S.RED, 0.05).move_to(P(2.0, 0.15))
        lyes = B("CONNECTED", 26, S.GREEN).move_to(P(-2.0, 1.85))
        lno = B("NOT CONNECTED", 26, S.RED).move_to(P(2.0, 1.85))
        tick = Text("✓", font=S.BODY_FONT, font_size=76, color=S.GREEN).move_to(P(-2.0, -1.5))
        cross = Text("✕", font=S.BODY_FONT, font_size=66, color=S.RED).move_to(P(2.0, -1.65))
        self.play(FadeIn(card_l, scale=0.9), FadeIn(lyes), Create(yes), run_time=0.7)
        ring = Circle(radius=0.15, stroke_color=S.GREEN, stroke_width=5).move_to(dot)
        self.play(GrowFromCenter(dot), FadeIn(tick, scale=1.6), run_time=0.45)
        self.play(ring.animate.scale(4).set_stroke(opacity=0), run_time=0.5)
        self.wait(max(0, d * 0.45 - 1.65))
        self.play(FadeIn(card_r, scale=0.9), FadeIn(lno), Create(no), run_time=0.7)
        self.play(FadeIn(cross, scale=1.6), Wiggle(cross, scale_value=1.2), run_time=0.6)
        self.wait(max(0, d * 0.55 - 1.75))
        self.play(FadeOut(VGroup(card_l, card_r, yes, dot, no, lyes, lno, tick, cross, ring)), run_time=0.45)

    def beat_thick(self, d):
        thin = copper_wire(5.6, r=0.12, strip=0.9, colour=("#FF8A80", "#C62828")).move_to(P(0, 1.7))
        thick = copper_wire(5.6, r=0.42, strip=0.9, colour=("#6FB0FF", "#1E4FCC")).move_to(P(0, -0.85))
        lt = label_chip("THIN  ·  more resistance", S.RED).next_to(thin, UP, buff=0.35)
        lk = label_chip("THICK  ·  less resistance", S.GREEN).next_to(thick, UP, buff=0.4)
        self.play(FadeIn(thin, shift=RIGHT * 1.5), FadeIn(lt), run_time=0.55)
        self.play(FadeIn(thick, shift=RIGHT * 1.5), FadeIn(lk), run_time=0.55)
        p1 = Line(thin.get_left() + RIGHT * 0.2, thin.get_right() + LEFT * 0.2)
        d1, t1 = flow_dots(p1, 5, 0.22, S.YELLOW, 0.045)
        rows = [flow_dots(Line(thick.get_left() + RIGHT * 0.25 + UP * yy, thick.get_right() + LEFT * 0.25 + UP * yy),
                          6, 0.22, S.YELLOW, 0.05) for yy in (-0.22, 0, 0.22)]
        heat = glow_disc("#FF5A1A", 1.0, 10, 0.25).stretch_to_fit_width(6.2).stretch_to_fit_height(1.0).move_to(thin)
        self.add(d1, t1, *[x for r in rows for x in r])
        self.play(FadeIn(heat), thin[0].animate.set_fill(["#FFF1B0", "#FF7A1A", "#C73A00"]),
                  run_time=max(0.5, d - 1.95))
        stop_flow(self, d1, t1)
        for r in rows:
            stop_flow(self, *r)
        self.play(FadeOut(VGroup(thin, thick, lt, lk, d1, heat, *[r[0] for r in rows])), run_time=0.45)

    def beat_outro(self, d):
        """Cinematic ending (no captions): next-episode reveal, then subscribe + bell with a mouse."""
        t0 = self.renderer.time
        dim = Rectangle(width=9, height=FH + 1, stroke_width=0, fill_color="#02040A", fill_opacity=0)
        self.add(dim)
        self.play(FadeOut(self.header, shift=UP * 0.3), dim.animate.set_fill(opacity=0.45), run_time=0.6, rate_func=smooth)

        nxt = Text("N E X T   T I M E", font=S.BODY_FONT, weight=BOLD, font_size=30, color=S.MUTED).move_to(P(0, 4.15))
        line_l = Line(P(-3.3, 4.15), P(-2.35, 4.15), stroke_color=S.MUTED, stroke_width=2)
        line_r = Line(P(2.35, 4.15), P(3.3, 4.15), stroke_color=S.MUTED, stroke_width=2)
        self.play(FadeIn(nxt, shift=UP * 0.15), Create(line_l), Create(line_r), run_time=0.55)

        cell = Battery(cells=1).scale(1.7).move_to(P(0, 2.5))
        cg = glow_disc(S.GREEN, 1.3, 12, 0.05).move_to(cell)
        self.play(Create(cell), FadeIn(cg, scale=0.5), run_time=0.7)

        name = H("THE CELL", 160, S.GREEN).move_to(P(0, 0.55))
        name_glow = name.copy().set_fill(opacity=0).set_stroke(S.GREEN, 12, 0.06)
        sweep = VGroup(*[Rectangle(width=w, height=2.4, stroke_width=0, fill_color=WHITE, fill_opacity=o)
                         for w, o in ((0.9, 0.05), (0.45, 0.09), (0.15, 0.22))]).rotate(-18 * DEGREES).move_to(P(-4.6, 0.55))
        self.play(FadeIn(name, scale=1.2), FadeIn(name_glow), run_time=0.5, rate_func=rush_from)
        self.add(sweep)
        self.play(sweep.animate.move_to(P(4.6, 0.55)), run_time=0.65, rate_func=smooth)
        self.remove(sweep)

        # subscribe button pops in with a little bounce
        btn = RoundedRectangle(width=4.6, height=1.25, corner_radius=0.62, stroke_width=0,
                               fill_color="#FF1E1E", fill_opacity=1)
        shine = RoundedRectangle(width=4.3, height=0.42, corner_radius=0.21, stroke_width=0,
                                 fill_color=WHITE, fill_opacity=0.14).shift(UP * 0.3)
        btn_t = B("SUBSCRIBE", 50, WHITE)
        btn_glow = glow_disc("#FF1E1E", 1.5, 10, 0.05).stretch(1.9, 0)
        sub = VGroup(btn_glow, btn, shine, btn_t).move_to(P(0, -1.55))
        self.play(FadeIn(sub, scale=0.4), run_time=0.5, rate_func=rate_functions.ease_out_back)

        # the mouse glides in on a curve, hovers (button brightens), clicks
        cur = cursor().move_to(P(3.0, -4.0))
        target = btn.get_center() + P(1.2, -0.3)
        path = CubicBezier(cur.get_center(), P(3.4, -2.6), target + P(1.4, -0.9), target + P(0.27, -0.45))
        self.play(FadeIn(cur, shift=UP * 0.2), run_time=0.2)
        self.play(MoveAlongPath(cur, path), run_time=0.85, rate_func=smooth)
        self.play(sub.animate.scale(1.05), run_time=0.15)
        self.play(cur.animate.scale(0.8), sub.animate.scale(0.92 / 1.05), run_time=0.08)
        ripple = Circle(radius=0.15, stroke_color=WHITE, stroke_width=6).move_to(target)
        sparks = VGroup(*[Line(ORIGIN, 0.28 * np.array([np.cos(a), np.sin(a), 0]), stroke_color=c, stroke_width=5)
                          .shift(0.45 * np.array([np.cos(a), np.sin(a), 0]))
                          for a, c in zip(np.linspace(0, TAU, 13)[:-1], [S.YELLOW, S.CYAN, S.PINK] * 4)]).move_to(target)
        self.play(cur.animate.scale(1 / 0.8), sub.animate.scale(1 / 0.92),
                  ripple.animate.scale(6).set_stroke(opacity=0), sparks.animate.scale(2.0).set_opacity(0), run_time=0.35)
        done_t = B("SUBSCRIBED", 46, "#D6DBE6").move_to(btn.get_center())
        self.play(btn.animate.set_fill("#2A3247"), shine.animate.set_fill(opacity=0.05),
                  FadeOut(btn_glow), Transform(btn_t, done_t), run_time=0.3)

        # bell slides in beside the button; the mouse hops over and rings it
        bell = bell_icon().scale(0.95)
        bell_bg = Circle(radius=0.62, stroke_width=0, fill_color="#2A3247", fill_opacity=1)
        bell_g = VGroup(bell_bg, bell)
        self.play(sub.animate.shift(LEFT * 0.7), FadeIn(bell_g.move_to(P(2.35, -1.55)), shift=LEFT * 0.4, scale=0.6),
                  cur.animate.shift(LEFT * 0.7), run_time=0.4)
        bt = bell_g.get_center() + P(0.12, -0.15)
        self.play(cur.animate.move_to(bt + P(0.27, -0.45)), run_time=0.45, rate_func=smooth)
        self.play(cur.animate.scale(0.8), run_time=0.08)
        ring2 = Circle(radius=0.62, stroke_color=S.YELLOW, stroke_width=5).move_to(bell_g)
        self.play(cur.animate.scale(1 / 0.8), bell_bg.animate.set_fill(S.YELLOW), bell.animate.set_fill("#1A1F2E"),
                  ring2.animate.scale(1.8).set_stroke(opacity=0), run_time=0.3)
        self.play(Wiggle(bell, scale_value=1.15, rotation_angle=0.12 * TAU, n_wiggles=4), run_time=0.7)
        self.play(cur.animate.shift(P(0.7, -0.9)).set_opacity(0), run_time=0.45)
        if d - (self.renderer.time - t0) > 0.03:
            self.wait(d - (self.renderer.time - t0))
