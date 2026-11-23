"""Burned-in Shorts captions (ASS subtitles, rendered by ffmpeg/libass).

Words appear in chunks of up to 3; the word being spoken turns yellow and
pops.  Every caption line is measured with the real font and shrunk if needed
so it always stays inside the safe width (never runs off screen)."""
from pathlib import Path
from PIL import ImageFont

FONT = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "BarlowCondensed-ExtraBoldItalic.ttf"
SAFE_W = 860          # px of the 1080 frame a caption may use (YouTube's side buttons sit on the right)
POP = 1.16            # active word scale

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Barlow Condensed ExtraBold,{size},&H00FBF5F2,&H00FFFFFF,&H00000000,&H96000000,0,1,0,0,100,100,1,0,1,{outline},4,5,40,40,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

YELLOW = "&H003FD2FF&"   # ASS colours are &HBBGGRR


def ts(t):
    t = max(0.0, t)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def chunk(words, max_words=3, max_chars=16):
    out, cur = [], []
    for i, w in enumerate(words):
        if cur and len(" ".join(words[j]["text"] for j in cur + [i])) > max_chars:
            out.append(cur); cur = []
        cur.append(i)
        if len(cur) == max_words or w["text"][-1] in ".,?!:;":
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


_fonts = {}


def width_px(text, size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(str(FONT), size)
    return _fonts[size].getlength(text)


def fit_size(text, size, outline):
    w = width_px(text, size) * POP + 2 * outline + 10
    return size if w <= SAFE_W else int(size * SAFE_W / w)


def even_words(text, t0, dur):
    ws = text.split()
    per = dur / len(ws)
    return [{"text": w, "start": t0 + i * per, "end": t0 + (i + 1) * per} for i, w in enumerate(ws)]


def build_ass(words, y=1350, size=140, outline=11):
    """words: list of {text, start, end} in seconds over the whole video."""
    lines = [HEADER.format(size=size, outline=outline)]
    for ch in chunk(words):
        fs = fit_size(" ".join(words[j]["text"].upper() for j in ch), size, outline)
        for k, idx in enumerate(ch):
            start = words[idx]["start"]
            end = words[ch[k + 1]]["start"] if k + 1 < len(ch) else words[idx]["end"] + 0.12
            parts = []
            for j in ch:
                w = words[j]["text"].upper().replace("{", "(").replace("}", ")")
                if j == idx:
                    w = r"{\c" + YELLOW + r"\fscx100\fscy100\t(0,90,\fscx116\fscy116)}" + w + r"{\r\fs" + str(fs) + "}"
                parts.append(w)
            pre = r"{\an5\pos(540," + str(y) + r")\fs" + str(fs) + "}"
            lines.append(f"Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{pre}{' '.join(parts)}")
    return "\n".join(lines) + "\n"
