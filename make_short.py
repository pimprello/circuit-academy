"""Make THE WIRE Short: narrator voice -> animation timed to the voice ->
captions burned in -> final mp4 with sound (out/wire.mp4)."""
import os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from ca.short_wire import BEATS
from ca.captions import build_ass, even_words

# 1. narrator, one clip per beat (falls back to estimated timing if the voice service can't be reached)
voiced = True
try:
    from ca.tts import speak
    narr = [speak(text, f"wire_{key}") for key, text in BEATS]
except Exception as e:
    print("no narrator voice available here:", e)
    voiced = False

from ca.short_wire import beat_durations   # reads narration/*.json when present
durs = beat_durations()

# 2. captions from the real word timings
words, t, starts = [], 0.0, []
for i, ((key, text), d) in enumerate(zip(BEATS, durs)):
    starts.append(t)
    if key == "outro":          # cinematic ending: no captions
        pass
    elif voiced:
        words += [{"text": w["text"], "start": t + w["start"], "end": t + w["end"]} for w in narr[i]["words"]]
    else:
        words += even_words(text, t, d - 0.35)
    t += d
Path("out").mkdir(exist_ok=True)
Path("out/wire.ass").write_text(build_ass(words), encoding="utf-8")

# 3. animation
env = dict(os.environ, PYTHONPATH=str(ROOT))
subprocess.run(["manim", "-r", "1080,1920", "--fps", "30", "--disable_caching", "-o", "wire_raw.mp4",
                "ca/short_wire.py", "WireShort"], check=True, env=env,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
raw = "media/videos/short_wire/1920p30/wire_raw.mp4"

# 4. narration track: each beat's clip placed at its start time, then loudness-normalised
cmd = ["ffmpeg", "-v", "error", "-y", "-i", raw]
if voiced:
    for key, _ in BEATS:
        cmd += ["-i", f"narration/wire_{key}.mp3"]
    delays = "".join(f"[{i + 1}:a]adelay={int(s * 1000)}|{int(s * 1000)}[a{i}];" for i, s in enumerate(starts))
    mix = "".join(f"[a{i}]" for i in range(len(BEATS)))
    fc = (f"[0:v]subtitles=out/wire.ass:fontsdir=assets/fonts[v];{delays}{mix}amix=inputs={len(BEATS)}:normalize=0,"
          f"loudnorm=I=-14:TP=-1.5:LRA=11,apad[a]")
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-ar", "48000"]
else:
    cmd += ["-vf", "subtitles=out/wire.ass:fontsdir=assets/fonts"]
cmd += ["-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-shortest", "out/wire.mp4"]
subprocess.run(cmd, check=True)
print("done: out/wire.mp4", "(with narrator)" if voiced else "(silent)")

# 5. custom thumbnail
subprocess.run(["manim", "-s", "-r", "1080,1920", "--disable_caching", "-o", "thumb", "ca/thumb_wire.py", "ThumbWire"],
               check=True, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "media/images/thumb_wire/thumb.png", "-q:v", "2", "out/thumb_wire.jpg"], check=True)
print("done: out/thumb_wire.jpg")
