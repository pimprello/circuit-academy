"""Make one episode Short: narrator voice -> animation timed to the voice -> captions
burned in -> final mp4 with sound, plus its hand-drawn thumbnail.

    python make_short.py cell          (or EPISODE=cell; default: wire)
Outputs: out/<slug>.mp4, out/<slug>_thumb.jpg"""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

slug = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("EPISODE", "wire")).strip()
os.environ["EPISODE"] = slug
from ca.engine import load_episode, beat_durations
from ca.captions import build_ass, even_words

ep = load_episode(slug)
beats = ep["beats"]

# 1. narrator, one clip per beat (falls back to estimated timing if no voice can be reached)
voiced = True
try:
    from ca.tts import speak
    narr = [speak(b["say"], f"{slug}_{b['key']}") for b in beats]
except Exception as e:
    print("no narrator voice available here:", e)
    voiced = False
durs = beat_durations(ep)
total = sum(durs)

# 2. captions from the real word timings (none on the cinematic ending)
words, t, starts = [], 0.0, []
for i, (b, d) in enumerate(zip(beats, durs)):
    starts.append(t)
    if b["show"]["type"] != "outro":
        if voiced:
            words += [{"text": w["text"], "start": t + w["start"], "end": t + w["end"]} for w in narr[i]["words"]]
        else:
            words += even_words(b["say"], t, d - 0.35)
    t += d
Path("out").mkdir(exist_ok=True)
ass = f"out/{slug}.ass"
Path(ass).write_text(build_ass(words), encoding="utf-8")

# 3. animation
env = dict(os.environ, PYTHONPATH=str(ROOT))
quiet = dict(stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) if not os.environ.get("VERBOSE") else {}
subprocess.run(["manim", "-r", "1080,1920", "--fps", "30", "--disable_caching", "-o", f"{slug}_raw.mp4",
                "ca/engine.py", "EpisodeShort"], check=True, env=env, **quiet)
raw = f"media/videos/engine/1920p30/{slug}_raw.mp4"

# 4. narration track: each beat's clip at its start time; light polish so it sits like a recorded voice
cmd = ["ffmpeg", "-v", "error", "-y", "-i", raw]
if voiced:
    for n in narr:
        cmd += ["-i", n["file"]]
    delays = "".join(f"[{i + 1}:a]aresample=48000,adelay={int(s * 1000)}|{int(s * 1000)}[a{i}];" for i, s in enumerate(starts))
    mix = "".join(f"[a{i}]" for i in range(len(beats)))
    voice_fx = ("highpass=f=75,equalizer=f=200:t=q:w=1:g=1.5,equalizer=f=3200:t=q:w=1.2:g=2,"
                "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2,"
                "aecho=0.8:0.6:28:0.08")   # a touch of room so it doesn't sound bone-dry / synthetic
    fc = (f"[0:v]subtitles={ass}:fontsdir=assets/fonts[v];{delays}{mix}amix=inputs={len(beats)}:normalize=0,"
          f"{voice_fx},loudnorm=I=-14:TP=-1.5:LRA=11,apad=whole_dur={total:.3f}[a]")
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
else:
    cmd += ["-vf", f"subtitles={ass}:fontsdir=assets/fonts"]
cmd += ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-t", f"{total:.3f}", f"out/{slug}.mp4"]
subprocess.run(cmd, check=True)
print(f"done: out/{slug}.mp4", "(with narrator)" if voiced else "(silent)")

# 5. hand-drawn thumbnail
subprocess.run(["manim", "-s", "-r", "1080,1920", "--disable_caching", "-o", f"{slug}_thumb", "ca/thumb.py", "Thumb"],
               check=True, env=env, **quiet)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"media/images/thumb/{slug}_thumb.png", "-q:v", "2",
                f"out/{slug}_thumb.jpg"], check=True)
print(f"done: out/{slug}_thumb.jpg")
