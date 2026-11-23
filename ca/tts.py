"""Narrator: Microsoft neural voices through edge-tts (free, no key), with word
timings for the captions.  Writes narration/<name>.mp3 + narration/<name>.json
({"duration": s, "words": [{"text", "start", "end"}]})."""
import asyncio
import json
import subprocess
from pathlib import Path

VOICES = ["en-US-AndrewMultilingualNeural", "en-US-AndrewNeural", "en-US-GuyNeural"]
RATE = "+4%"


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


async def _speak(text, voice, mp3):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate=RATE, boundary="WordBoundary")
    words = []
    with open(mp3, "wb") as f:
        async for c in com.stream():
            if c["type"] == "audio":
                f.write(c["data"])
            elif c["type"] == "WordBoundary":
                s = c["offset"] / 1e7
                words.append({"text": c["text"], "start": s, "end": s + c["duration"] / 1e7})
    return words


def speak(text, name, out_dir="narration"):
    out = Path(out_dir); out.mkdir(exist_ok=True)
    mp3, meta = out / f"{name}.mp3", out / f"{name}.json"
    if mp3.exists() and meta.exists() and json.loads(meta.read_text()).get("text") == text:
        return json.loads(meta.read_text())
    last = None
    for v in VOICES:
        try:
            words = asyncio.run(_speak(text, v, mp3))
            if mp3.stat().st_size > 1000:
                break
        except Exception as e:   # voice unavailable / network hiccup: try the next one
            last = e
    else:
        raise RuntimeError(f"narration failed: {last}")
    # put the punctuation back on the caption words (the voice service strips it)
    src = text.split()
    if len(src) == len(words):
        for w, s in zip(words, src):
            w["text"] = s
    data = {"text": text, "voice": v, "duration": duration(mp3), "words": words}
    meta.write_text(json.dumps(data, indent=1))
    return data
