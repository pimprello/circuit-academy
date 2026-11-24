"""One scene for every episode.  The episode file (episodes/<slug>.json) lists the beats:
what the narrator says and which visual to show.  Visual types:

  hook       big drawn component crackling with electricity, flash, title slam   {"part"}
  picture    drawn component with callout labels                               {"part", "labels":[{"text","colour","side","at":[x,y]}]}
  symbol     schematic symbol, big, with pin labels and notes                  {"part", "pins":{"a":"+"}, "notes":[...], "tag"}
  circuit    named circuit (ca/circuits.py) drawn, then current flows          {"circuit", "tag"}
  compare    two cards side by side, each a symbol or picture                  {"left":{...}, "right":{...}}
  formula    a big equation                                                    {"text", "note"}
  outro      cinematic next-episode reveal + subscribe and bell (no captions)  (automatic)
  wire_*     the Wire episode's own hand-made beats

Render:  EPISODE=wire manim -r 1080,1920 ca/engine.py EpisodeShort   (make_short.py does it all)"""
import json
import os
from pathlib import Path
import numpy as np
from manim import *
from ca import style as S
from ca.symbols import P, Battery, Lamp, poly
from ca.kit import (FH, TOP_SAFE, H, B, neon, glow_disc, label_chip, background, copper_wire, cross_section,
                    flow_dots, stop_flow, bell_icon, cursor, point_cursor, title_mob)
from ca import parts as PARTS
from ca import circuits as CIRCUITS

ROOT = Path(__file__).resolve().parent.parent
WPS = 2.7


def load_episode(slug):
    return json.loads((ROOT / "episodes" / f"{slug}.json").read_text(encoding="utf-8"))


def next_episode(slug):
    order = json.loads((ROOT / "episodes" / "curriculum.json").read_text())["order"]
    i = [e["slug"] for e in order].index(slug)
    return order[i + 1] if i + 1 < len(order) else None


def beat_durations(ep):
    out = []
    for b in ep["beats"]:
        f = ROOT / "narration" / f"{ep['slug']}_{b['key']}.json"
        if f.exists():
            out.append(json.loads(f.read_text())["duration"] + 0.35)
        else:
            out.append(len(b["say"].split()) / WPS + 0.6)
        if b["show"]["type"] == "outro":
            out[-1] = max(out[-1], 9.2)    # the cinematic ending needs room to breathe
    return out


def bolt(a, b, jag=0.3, forks=1, rng=np.random):
    """Jagged electric arc from a to b with a little fork or two (three glow layers)."""
    a, b = np.array(a, float), np.array(b, float)
    n = 9
    d = b - a
    nrm = np.array([-d[1], d[0], 0]) / (np.linalg.norm(d) + 1e-9)
    pts = [a] + [a + d * i / n + nrm * rng.uniform(-jag, jag) for i in range(1, n)] + [b]
    paths = [pts]
    for _ in range(forks):
        k = rng.randint(2, n - 1)
        f = [pts[k]]
        for _ in range(3):
            f.append(f[-1] + P(rng.uniform(-0.15, 0.2), rng.choice([-1, 1]) * rng.uniform(0.08, 0.2)))
        paths.append(f)
    g = VGroup()
    for path in paths:
        k = 1 if path is pts else 0.6
        for w, o, c in ((24, 0.10, S.CYAN), (11, 0.35, S.CYAN), (4, 1, WHITE)):
            m = VMobject(stroke_color=c, stroke_width=w * k, stroke_opacity=o)
            m.set_points_as_corners(path)
            g.add(m)
    return g


class EpisodeShort(Scene):
    def construct(self):
        np.random.seed(7)
        self.ep = load_episode(os.environ.get("EPISODE", "wire"))
        durs = beat_durations(self.ep)
        self.add(background())

        title = title_mob(self.ep["title"], self.ep.get("accent_from", 3))
        title.move_to(P(0, TOP_SAFE - 0.6))
        accent = Line(P(-1.6, 0), P(1.6, 0), stroke_color=S.CYAN, stroke_width=6).next_to(title, DOWN, buff=0.18)
        self.header = VGroup(neon(accent, S.CYAN), accent, title)
        self.title, self.accent = title, accent
        self.header_home = self.header.get_center()
        self.hook_t0 = self.renderer.time

        for b, d in zip(self.ep["beats"], durs):
            t0 = self.renderer.time
            getattr(self, "beat_" + b["show"]["type"].replace("-", "_"))(d, b)
            left = d - (self.renderer.time - t0)
            if left > 0.02:
                self.wait(left)

    # ── shared pieces ────────────────────────────────────────────────────
    def title_slam(self, stage):
        """White flash, title drops in with a bounce, small screen shake."""
        flash = Rectangle(width=9, height=FH + 1, stroke_width=0, fill_color=WHITE, fill_opacity=0.85)
        self.title.scale(1.8).set_opacity(0)
        self.add(flash)
        self.play(FadeOut(flash), self.title.animate.scale(1 / 1.8).set_opacity(1), Create(self.accent),
                  FadeIn(self.header[0]), run_time=0.35, rate_func=rate_functions.ease_out_back)
        home = stage.get_center()
        for v in (P(0.08, -0.05), P(-0.12, 0.06), P(0.06, 0.04), P(-0.02, -0.05)):
            self.play(stage.animate.shift(v), self.header.animate.shift(v * 0.5), run_time=0.045)
        self.play(stage.animate.move_to(home), self.header.animate.move_to(self.header_home), run_time=0.08)

    def wait_until(self, t0, d, keep=0.0):
        rest = d - (self.renderer.time - t0) - keep
        if rest > 0.03:
            self.wait(rest)

    def show_circuit(self, c, tag=None, flow=True):
        """Draw a circuit, then run current round it and light its loads. Returns things to fade out."""
        items = [c]
        if tag:
            chip = label_chip(tag, S.CYAN).move_to(P(0, 2.95))
            items.append(chip)
            self.play(FadeIn(chip, shift=DOWN * 0.2), run_time=0.3)
        self.play(*[Create(p) for p in c.parts], FadeIn(c.labels), run_time=0.8)
        self.play(*[Create(w) for w in c.wires], run_time=1.0, rate_func=smooth)
        if flow and c.loops:
            halo = neon(c.wires, S.YELLOW, 0.8)
            glows = [glow_disc(col, r, 12, 0.2).move_to(p) for p, col, r in c.glows]
            for g in glows:
                g.set_z_index(1)
            c.parts.set_z_index(2); c.labels.set_z_index(2)
            flows = [flow_dots(l, 18, 0.2) for l in c.loops]
            for dots, tr in flows:
                dots.set_z_index(3)
                self.add(dots, tr)
            self.add(halo)
            self.play(c.wires.animate.set_stroke(S.WIRE, 5), FadeIn(halo), *[FadeIn(g, scale=0.6) for g in glows],
                      run_time=0.6)
            items += [halo, *glows, *[f[0] for f in flows]]
            self._flows = flows
        return items

    def end_flows(self):
        for dots, tr in getattr(self, "_flows", []):
            stop_flow(self, dots, tr)
        self._flows = []

    # ── generic beats ────────────────────────────────────────────────────
    def beat_hook(self, d, b):
        """Frame one already moving: the component crackles with electricity, then flash + title slam."""
        t0 = self.renderer.time
        part = b["show"]["part"]
        pic = PARTS.picture(part)
        pic.scale_to_fit_width(min(6.6, pic.width * 1.25)).move_to(P(0, 0.4))
        halo = glow_disc(PARTS.colour(part), 2.8, 14, 0.12).move_to(pic)
        R = max(pic.width, pic.height) / 2 + 0.35
        rng = np.random.RandomState(11)
        c = pic.get_center()

        def aura():
            g = VGroup()
            for _ in range(3):
                a = rng.uniform(0, TAU)
                p0 = c + np.array([np.cos(a) * pic.width / 2 * 0.9, np.sin(a) * pic.height / 2 * 0.9, 0])
                p1 = c + np.array([np.cos(a + rng.uniform(-0.5, 0.5)) * R * 1.25, np.sin(a) * R * 0.9 + rng.uniform(-0.4, 0.4), 0])
                g.add(bolt(p0, p1, 0.18, 1, rng))
            return g
        arcs = aura()
        arcs.add_updater(lambda m, dt: m.become(aura()))
        self.add(halo, pic, arcs)
        self.play(pic.animate.scale(0.92), halo.animate.scale(1.15), run_time=0.6, rate_func=smooth)
        self.title_slam(pic)
        self.play(halo.animate.scale(0.9), run_time=max(0.2, d - (self.renderer.time - t0) - 0.5), rate_func=there_and_back)
        arcs.clear_updaters()
        self.play(FadeOut(VGroup(arcs, halo, pic), shift=UP * 0.3), run_time=0.45)

    def beat_picture(self, d, b):
        t0 = self.renderer.time
        sh = b["show"]
        pic = PARTS.picture(sh["part"])
        pic.scale_to_fit_width(min(6.4, pic.width)).move_to(P(0, 1.0))
        self.play(FadeIn(pic, shift=LEFT * 1.5), run_time=0.6, rate_func=smooth)
        extras = []
        for lab in sh.get("labels", []):
            col = getattr(S, lab.get("colour", "TEXT").upper(), lab.get("colour", S.TEXT))
            chip = label_chip(lab["text"], col)
            target = pic.get_center() + P(*lab["at"])
            side = -1 if lab.get("side", "left") == "left" else 1
            chip.move_to(P(side * 2.05, lab.get("y", -1.0)))
            line = VGroup(Line(chip.get_edge_center(-side * LEFT if side < 0 else LEFT), target, stroke_color=col, stroke_width=4),
                          Dot(target, radius=0.08, color=col))
            self.play(Create(line), FadeIn(chip, shift=UP * 0.2), run_time=0.5)
            extras += [chip, line]
        self.wait_until(t0, d, 0.45)
        self.play(FadeOut(VGroup(pic, *extras), shift=UP * 0.4), run_time=0.45)

    def beat_symbol(self, d, b):
        t0 = self.renderer.time
        sh = b["show"]
        sym = PARTS.symbol(sh["part"]).scale(sh.get("scale", 2.0)).move_to(P(0, 0.7))
        items = [sym]
        if sh.get("tag"):
            chip = label_chip(sh["tag"], S.CYAN).move_to(P(0, 2.95))
            items.append(chip)
            self.play(FadeIn(chip, shift=DOWN * 0.2), run_time=0.3)
        glow = glow_disc(PARTS.colour(sh["part"]), 2.2, 12, 0.07).move_to(sym)
        self.play(FadeIn(glow), Create(sym), run_time=1.0)
        items.append(glow)
        for pin, text in sh.get("pins", {}).items():
            if not hasattr(sym, "pin"):
                break
            p = sym.pin(pin)
            t = H(text, 96, S.YELLOW).move_to(p + (p - sym.get_center()) / max(np.linalg.norm(p - sym.get_center()), 1e-6) * 0.6)
            self.play(FadeIn(t, scale=1.6), run_time=0.3)
            items.append(t)
        for i, note in enumerate(sh.get("notes", [])):
            n = label_chip(note, S.YELLOW).move_to(P(0, -1.2 - i * 0.75))
            self.play(FadeIn(n, shift=UP * 0.2), run_time=0.35)
            items.append(n)
        self.wait_until(t0, d, 0.45)
        self.play(FadeOut(VGroup(*items)), run_time=0.45)

    def beat_circuit(self, d, b):
        t0 = self.renderer.time
        sh = b["show"]
        c = CIRCUITS.build(sh["circuit"])
        items = self.show_circuit(c, sh.get("tag"), sh.get("flow", True))
        self.wait_until(t0, d, 0.45)
        self.end_flows()
        self.play(FadeOut(VGroup(*items)), run_time=0.45)

    def beat_compare(self, d, b):
        t0 = self.renderer.time
        sh = b["show"]
        cards = []
        for side, x in (("left", -2.0), ("right", 2.0)):
            spec = sh[side]
            col = getattr(S, spec.get("colour", "CYAN").upper(), S.CYAN)
            card = RoundedRectangle(width=3.45, height=4.4, corner_radius=0.3, stroke_color=col, stroke_width=3,
                                    fill_color=col, fill_opacity=0.06).move_to(P(x, 0.15))
            ttl = B(spec["title"], 26, col).move_to(P(x, 1.85))
            vis = (PARTS.picture(spec["part"]) if spec.get("picture") else PARTS.symbol(spec["part"]))
            vis.scale_to_fit_width(min(2.8, vis.width)).move_to(P(x, 0.2))
            sub = B(spec.get("note", ""), 24, S.TEXT).move_to(P(x, -1.55)) if spec.get("note") else VGroup()
            self.play(FadeIn(card, scale=0.9), FadeIn(ttl), Create(vis), FadeIn(sub), run_time=0.7)
            cards += [card, ttl, vis, sub]
            if side == "left":
                self.wait(max(0, d * 0.4 - 0.7))
        self.wait_until(t0, d, 0.45)
        self.play(FadeOut(VGroup(*cards)), run_time=0.45)

    def beat_formula(self, d, b):
        t0 = self.renderer.time
        sh = b["show"]
        eq = H(sh["text"], 150, S.YELLOW).move_to(P(0, 0.9))
        if eq.width > 7.2:
            eq.scale_to_fit_width(7.2)
        box = RoundedRectangle(width=eq.width + 0.8, height=eq.height + 0.7, corner_radius=0.3, stroke_color=S.YELLOW,
                               stroke_width=3, fill_color=S.YELLOW, fill_opacity=0.06).move_to(eq)
        items = [eq, box]
        self.play(Create(box), Write(eq), run_time=0.9)
        if sh.get("note"):
            n = label_chip(sh["note"], S.CYAN).next_to(box, DOWN, buff=0.45)
            self.play(FadeIn(n, shift=UP * 0.2), run_time=0.35)
            items.append(n)
        self.wait_until(t0, d, 0.45)
        self.play(FadeOut(VGroup(*items)), run_time=0.45)

    def beat_outro(self, d, b):
        """Cinematic ending (no captions): next-episode reveal, then subscribe + bell with the mouse on top."""
        t0 = self.renderer.time
        nxt_ep = next_episode(self.ep["slug"]) or {"slug": "wire", "name": "MORE PARTS", "part": "wire"}
        dim = Rectangle(width=9, height=FH + 1, stroke_width=0, fill_color="#02040A", fill_opacity=0)
        self.add(dim)
        self.play(FadeOut(self.header, shift=UP * 0.3), dim.animate.set_fill(opacity=0.45), run_time=0.6, rate_func=smooth)

        nxt = Text("N E X T   T I M E", font=S.BODY_FONT, weight=BOLD, font_size=30, color=S.MUTED).move_to(P(0, 4.15))
        line_l = Line(P(-3.3, 4.15), P(-2.35, 4.15), stroke_color=S.MUTED, stroke_width=2)
        line_r = Line(P(2.35, 4.15), P(3.3, 4.15), stroke_color=S.MUTED, stroke_width=2)
        self.play(FadeIn(nxt, shift=UP * 0.15), Create(line_l), Create(line_r), run_time=0.55)

        col = PARTS.colour(nxt_ep["part"])
        sym = PARTS.symbol(nxt_ep["part"])
        sym.scale_to_fit_width(min(3.4, sym.width * 1.7)).move_to(P(0, 2.5))
        cg = glow_disc(col, 1.3, 12, 0.05).move_to(sym)
        self.play(Create(sym), FadeIn(cg, scale=0.5), run_time=0.7)

        name = H(nxt_ep["name"], 160, col).move_to(P(0, 0.55))
        if name.width > 7.4:
            name.scale_to_fit_width(7.4)
        name_glow = name.copy().set_fill(opacity=0).set_stroke(col, 12, 0.06)
        sweep = VGroup(*[Rectangle(width=w, height=2.4, stroke_width=0, fill_color=WHITE, fill_opacity=o)
                         for w, o in ((0.9, 0.05), (0.45, 0.09), (0.15, 0.22))]).rotate(-18 * DEGREES).move_to(P(-4.6, 0.55))
        self.play(FadeIn(name, scale=1.2), FadeIn(name_glow), run_time=0.5, rate_func=rush_from)
        self.add(sweep)
        self.play(sweep.animate.move_to(P(4.6, 0.55)), run_time=0.65, rate_func=smooth)
        self.remove(sweep)

        btn = RoundedRectangle(width=4.6, height=1.25, corner_radius=0.62, stroke_width=0, fill_color="#FF1E1E", fill_opacity=1)
        shine = RoundedRectangle(width=4.3, height=0.42, corner_radius=0.21, stroke_width=0,
                                 fill_color=WHITE, fill_opacity=0.14).shift(UP * 0.3)
        btn_t = B("SUBSCRIBE", 50, WHITE)
        btn_glow = glow_disc("#FF1E1E", 1.5, 10, 0.05).stretch(1.9, 0)
        sub = VGroup(btn_glow, btn, shine, btn_t).move_to(P(0, -1.55))
        self.play(FadeIn(sub, scale=0.4), run_time=0.5, rate_func=rate_functions.ease_out_back)

        # the mouse glides in on a curve and lands ON the button, hovers, clicks
        cur = point_cursor(cursor(), P(3.0, -4.2))
        target = btn.get_center() + P(0.9, -0.12)
        start = cur.tip.get_center()
        path = CubicBezier(start, P(3.5, -2.9), target + P(1.5, -1.0), target)
        self.play(FadeIn(cur, shift=UP * 0.2), run_time=0.2)
        self.play(UpdateFromAlphaFunc(cur, lambda m, a: point_cursor(m, path.point_from_proportion(smooth(a)))), run_time=0.85)
        self.play(sub.animate.scale(1.05), run_time=0.15)
        self.play(cur.animate.scale(0.82, about_point=cur.tip.get_center()), sub.animate.scale(0.92 / 1.05), run_time=0.08)
        ripple = Circle(radius=0.15, stroke_color=WHITE, stroke_width=6).move_to(target)
        sparks = VGroup(*[Line(ORIGIN, 0.28 * np.array([np.cos(a), np.sin(a), 0]), stroke_color=c, stroke_width=5)
                          .shift(0.45 * np.array([np.cos(a), np.sin(a), 0]))
                          for a, c in zip(np.linspace(0, TAU, 13)[:-1], [S.YELLOW, S.CYAN, S.PINK] * 4)]).move_to(target)
        self.play(cur.animate.scale(1 / 0.82, about_point=cur.tip.get_center()), sub.animate.scale(1 / 0.92),
                  ripple.animate.scale(6).set_stroke(opacity=0), sparks.animate.scale(2.0).set_opacity(0), run_time=0.35)
        done_t = B("SUBSCRIBED", 46, "#D6DBE6").move_to(btn.get_center())
        self.play(btn.animate.set_fill("#2A3247"), shine.animate.set_fill(opacity=0.05),
                  FadeOut(btn_glow), Transform(btn_t, done_t), run_time=0.3)

        # bell slides in; the mouse moves onto it and rings it
        bell = bell_icon().scale(0.95)
        bell_bg = Circle(radius=0.62, stroke_width=0, fill_color="#2A3247", fill_opacity=1)
        bell_g = VGroup(bell_bg, bell).move_to(P(2.35, -1.55))
        self.play(sub.animate.shift(LEFT * 0.7), FadeIn(bell_g, shift=LEFT * 0.4, scale=0.6),
                  cur.animate.shift(LEFT * 0.7), run_time=0.4)
        bt = bell_g.get_center() + P(0.05, -0.05)
        self.play(cur.animate.shift(bt - cur.tip.get_center()), run_time=0.45, rate_func=smooth)
        self.play(cur.animate.scale(0.82, about_point=cur.tip.get_center()), run_time=0.08)
        ring2 = Circle(radius=0.62, stroke_color=S.YELLOW, stroke_width=5).move_to(bell_g)
        self.play(cur.animate.scale(1 / 0.82, about_point=cur.tip.get_center()), bell_bg.animate.set_fill(S.YELLOW),
                  bell.animate.set_fill("#1A1F2E"), ring2.animate.scale(1.8).set_stroke(opacity=0), run_time=0.3)
        self.play(Wiggle(bell, scale_value=1.15, rotation_angle=0.12 * TAU, n_wiggles=4), run_time=0.7)
        self.wait_until(t0, d)


    # ── the Wire episode's own beats ─────────────────────────────────────
    def beat_wire_hook(self, d, b=None):
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

    def beat_wire_inside(self, d, b=None):
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

    def beat_wire_symbol(self, d, b=None):
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

    def beat_wire_joins(self, d, b=None):
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

    def beat_wire_thick(self, d, b=None):
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

