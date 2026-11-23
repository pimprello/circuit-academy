"""Custom thumbnail for THE WIRE (1080x1920, vertical for Shorts).
Big curiosity question, one bold hero visual, high contrast. Key content sits in the
middle of the frame so it still reads when YouTube crops the thumbnail in the feed."""
import numpy as np
from manim import *
from ca import style as S
from ca.symbols import P
from ca.short_wire import FH, TOP_SAFE, H, copper_wire, cross_section, glow_disc, background, neon

config.frame_width = 8
config.frame_height = 8 * 16 / 9
config.background_color = S.BG


class ThumbWire(Scene):
    def construct(self):
        np.random.seed(3)
        bg = background()
        bg[2].clear_updaters()
        self.add(bg)
        self.add(glow_disc("#FF8A2B", 4.2, 16, 0.10).move_to(P(0.4, -1.8)))
        self.add(glow_disc(S.CYAN, 3.0, 14, 0.08).move_to(P(1.8, 3.0)))

        # hero: stripped wire across the frame + big glowing cross-section
        wire = copper_wire(8.5, r=0.42, strip=2.2).rotate(18 * DEGREES).move_to(P(-0.2, -4.2))
        self.add(wire)
        xs = cross_section(r=1.85).move_to(P(0.75, -1.75))
        hot = VGroup(*[glow_disc("#FFB25A", 0.5, 6, 0.25).move_to(c) for c in xs[3]])
        self.add(xs, hot)

        # arrow + label pointing at the copper
        lab = Text("COPPER", font=S.HEAD_FONT, weight=ULTRABOLD, slant=ITALIC, font_size=96, color="#FFB070")
        lab.set_stroke(BLACK, 10, background=True).rotate(-6 * DEGREES).move_to(P(-1.55, 0.75))
        arr = Arrow(P(-1.9, 0.2), P(0.25, -1.45), buff=0, stroke_color="#FF3B3B", stroke_width=22,
                    max_tip_length_to_length_ratio=0.32, max_stroke_width_to_length_ratio=12)
        self.add(neon(arr[0], "#FF3B3B"), arr, lab)

        # headline (below the notch safe line)
        l1 = H("WHAT'S INSIDE", 150, S.TEXT)
        l2 = H("A WIRE?", 250, S.YELLOW)
        for t in (l1, l2):
            t.set_stroke(BLACK, 14, background=True)
        head = VGroup(l1, l2).arrange(DOWN, buff=0.05).move_to(P(0, TOP_SAFE - 1.9))
        if head.width > 7.4:
            head.scale_to_fit_width(7.4)
        self.add(head)
