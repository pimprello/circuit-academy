"""Sound effects, synthesised in code (no stock files, no licences), and the mixer that
lays them on a timeline.  The animation logs each cue as (time, name, gain) into
out/<slug>_sfx.json; build_track() turns that into one wav that sits under the narrator."""
import json
import numpy as np
from pathlib import Path

SR = 48000
_rng = np.random.default_rng(1)


def _env(n, attack=0.005, release=None, curve=4.0):
    t = np.linspace(0, 1, n)
    a = max(1, int(attack * SR))
    e = np.exp(-curve * t) if release is None else np.ones(n)
    e[:a] *= np.linspace(0, 1, a)
    if release:
        r = max(1, int(release * SR))
        e[-r:] *= np.linspace(1, 0, r) ** 2
    return e


def _bandpass(x, lo, hi):
    """FFT band-pass (good enough for short effects)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def _sweep_noise(dur, f0, f1, width=0.6, seg=2048):
    """Noise whose pass-band glides from f0 to f1 (block-wise band-pass)."""
    n = int(dur * SR)
    m = -(-n // seg) * seg
    noise = _rng.standard_normal(m)
    out = np.zeros(m)
    for i in range(0, m, seg):
        c = f0 + (f1 - f0) * (i / m)
        out[i:i + seg] = _bandpass(noise[i:i + seg], c * (1 - width), c * (1 + width))
    return out[:n]


def whoosh(dur=0.45, up=True):
    n = int(dur * SR)
    x = _sweep_noise(dur, 300 if up else 2600, 2600 if up else 300)
    t = np.linspace(0, 1, n)
    env = np.sin(np.pi * t ** (0.6 if up else 1.4)) ** 2
    return 0.5 * x * env / (np.abs(x).max() + 1e-9)


def pop(f0=900, f1=320, dur=0.09):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return 0.55 * np.sin(ph) * _env(n, 0.002, curve=7)


def click():
    """Mouse click: a crisp press then a softer release a few ms later."""
    def tick(gain, hp):
        n = int(0.012 * SR)
        x = _bandpass(_rng.standard_normal(n), hp, 9000) * _env(n, 0.0005, curve=18)
        body = np.sin(2 * np.pi * 1900 * np.arange(n) / SR) * _env(n, 0.0005, curve=25) * 0.4
        return gain * (x / (np.abs(x).max() + 1e-9) + body)
    out = np.zeros(int(0.09 * SR))
    a = tick(0.9, 2500)
    b = tick(0.45, 3500)
    out[:len(a)] += a
    o = int(0.055 * SR)
    out[o:o + len(b)] += b
    return out


def bell():
    """Notification-bell 'ding': inharmonic bell partials with long decays plus a bright strike."""
    dur = 1.6
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 1318.5   # E6
    out = np.zeros(n)
    for ratio, amp, dec in ((1.0, 1.0, 2.2), (2.0, 0.45, 3.0), (2.76, 0.35, 4.0), (5.4, 0.18, 6.0), (8.93, 0.08, 9.0)):
        out += amp * np.sin(2 * np.pi * f * ratio * t + _rng.uniform(0, 6)) * np.exp(-dec * t)
    strike = _bandpass(_rng.standard_normal(int(0.01 * SR)), 3000, 12000) * _env(int(0.01 * SR), 0.0003, curve=12)
    out[:len(strike)] += 0.3 * strike / (np.abs(strike).max() + 1e-9)
    out *= np.minimum(1, t / 0.002)
    return 0.32 * out / np.abs(out).max()


def shimmer(dur=0.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, f in enumerate((2093, 2637, 3136, 4186)):
        start = k * 0.07
        e = np.where(t >= start, np.exp(-5 * (t - start)), 0)
        out += np.sin(2 * np.pi * f * t) * e
    return 0.12 * out / np.abs(out).max()


def impact():
    """Soft cinematic hit: low thump + airy noise tail (for the title / next-episode reveal)."""
    dur = 1.1
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 95 * np.exp(-6 * t) + 45
    thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-5 * t)
    air = _bandpass(_rng.standard_normal(n), 800, 9000) * np.exp(-7 * t) * 0.25
    return 0.6 * (thump + air) / np.abs(thump + air).max()


def riser(dur=1.0):
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = _sweep_noise(dur, 400, 5000, 0.4) * t ** 2
    tone = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (2 * t)) / SR) * t ** 3 * 0.25
    y = x / (np.abs(x).max() + 1e-9) + tone
    return 0.35 * y / np.abs(y).max()


def power_on():
    """Bulb/LED lights: quick rising 'bloop' with a soft glassy top."""
    dur = 0.35
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = 330 * 2 ** (1.2 * t / dur)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(2 * np.pi * 2 * np.cumsum(f) / SR)
    return 0.3 * y * _env(n, 0.01, curve=3.5)


def hum(dur=3.0):
    """Gentle electric hum while current flows (50 Hz mains-style with soft harmonics, faded in/out)."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * 50 * h * t) for h, a in ((2, 1), (4, 0.5), (6, 0.25), (8, 0.12)))
    y *= 1 + 0.15 * np.sin(2 * np.pi * 3 * t)
    return 0.08 * y / np.abs(y).max() * _env(n, 0.25, release=0.35)


def sizzle(dur=1.5):
    n = int(dur * SR)
    x = _bandpass(_rng.standard_normal(n), 2500, 11000)
    crackle = (_rng.random(n) > 0.9985) * _rng.uniform(-1, 1, n) * 6
    y = x / np.abs(x).max() + crackle
    y /= np.abs(y).max()
    return 0.14 * y * _env(n, 0.3, release=0.4)


def error():
    """Soft low two-note 'nope' for things that are wrong / not connected."""
    out = []
    for f in (330, 262):
        n = int(0.13 * SR)
        t = np.arange(n) / SR
        out.append(np.sin(2 * np.pi * f * t) * _env(n, 0.004, curve=6) + 0.3 * np.sin(2 * np.pi * 2 * f * t) * _env(n, 0.004, curve=9))
    return 0.25 * np.concatenate(out)


def success():
    out = []
    for f in (784, 1175):
        n = int(0.11 * SR)
        t = np.arange(n) / SR
        out.append(np.sin(2 * np.pi * f * t) * _env(n, 0.003, curve=6))
    return 0.22 * np.concatenate(out)


SOUNDS = {"whoosh": whoosh, "whoosh_down": lambda: whoosh(up=False), "pop": pop, "pop_hi": lambda: pop(1400, 600, 0.07),
          "click": click, "bell": bell, "shimmer": shimmer, "impact": impact, "riser": riser,
          "power_on": power_on, "hum": hum, "hum_long": lambda: hum(5.0), "sizzle": sizzle,
          "error": error, "success": success}


def build_track(cues, total, path):
    """cues: [(time_s, name, gain)] -> mono wav of `total` seconds at path."""
    import soundfile as sf
    out = np.zeros(int((total + 2) * SR))
    cache = {}
    for t, name, gain in cues:
        if name not in cache:
            cache[name] = SOUNDS[name]()
        s = cache[name] * gain
        i = int(t * SR)
        if i >= len(out):
            continue
        out[i:i + len(s)] += s[:len(out) - i]
    out = out[:int(total * SR)]
    peak = np.abs(out).max()
    if peak > 0.95:
        out *= 0.95 / peak
    sf.write(str(path), out.astype(np.float32), SR)
    return path


def load_cues(slug):
    p = Path("out") / f"{slug}_sfx.json"
    return json.loads(p.read_text()) if p.exists() else []
