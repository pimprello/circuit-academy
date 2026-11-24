"""Narrator with word timings for the captions.

Main voice: Kokoro (open neural TTS, runs on GitHub's machine, no key) — natural, human-sounding
delivery with real per-word timestamps.  Fallback if Kokoro can't run: Microsoft neural voices
via edge-tts.  Writes narration/<name>.wav|mp3 + narration/<name>.json
({"duration": s, "words": [{"text", "start", "end"}], "file": ...})."""
import asyncio
import json
import subprocess
from pathlib import Path

KOKORO_VOICE = "af_heart"      # warmest, most natural Kokoro voice; male option: "am_michael"
KOKORO_SPEED = 1.05
EDGE_VOICES = ["en-US-AndrewMultilingualNeural", "en-US-AndrewNeural", "en-US-GuyNeural"]

_pipe = None


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return float(out.strip())


def _kokoro(text, wav):
    global _pipe
    import numpy as np
    import soundfile as sf
    from kokoro import KPipeline
    if _pipe is None:
        _pipe = KPipeline(lang_code="a", repo_id="hexgrad/Kokoro-82M")
    audio, words, offset = [], [], 0.0
    for res in _pipe(text, voice=KOKORO_VOICE, speed=KOKORO_SPEED, split_pattern=r"\n+"):
        a = res.audio.cpu().numpy() if hasattr(res.audio, "cpu") else np.asarray(res.audio)
        cur = None
        for t in (res.tokens or []):
            if cur is None:
                cur = {"text": "", "start": None, "end": None}
            cur["text"] += t.text
            if t.start_ts is not None:
                cur["start"] = cur["start"] if cur["start"] is not None else offset + t.start_ts
            if t.end_ts is not None:
                cur["end"] = offset + t.end_ts
            if t.whitespace:
                if any(ch.isalnum() for ch in cur["text"]) and cur["start"] is not None:
                    words.append(cur)
                cur = None
        if cur and any(ch.isalnum() for ch in cur["text"]) and cur["start"] is not None:
            words.append(cur)
        audio.append(a)
        offset += len(a) / 24000
    sf.write(str(wav), np.concatenate(audio), 24000)
    for w in words:
        w["end"] = w["end"] if w["end"] is not None else w["start"] + 0.25
    return words


async def _edge(text, voice, mp3):
    import edge_tts
    com = edge_tts.Communicate(text, voice, rate="+4%", boundary="WordBoundary")
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
    meta = out / f"{name}.json"
    if meta.exists():
        old = json.loads(meta.read_text())
        if old.get("text") == text and Path(old["file"]).exists():
            return old
    words, f, engine = None, None, None
    try:
        f = out / f"{name}.wav"
        words = _kokoro(text, f)
        engine = f"kokoro:{KOKORO_VOICE}"
    except Exception as e:
        print("kokoro unavailable, using edge-tts:", repr(e)[:200])
        f = out / f"{name}.mp3"
        for v in EDGE_VOICES:
            try:
                words = asyncio.run(_edge(text, v, f))
                if f.stat().st_size > 1000:
                    engine = f"edge:{v}"
                    break
            except Exception as e2:
                print("edge voice failed:", v, repr(e2)[:120])
        if engine is None:
            raise RuntimeError("no narrator voice available")
    # captions show the script's own words (with punctuation) when the counts line up
    src = text.split()
    if len(src) == len(words):
        for w, s in zip(words, src):
            w["text"] = s
    data = {"text": text, "engine": engine, "file": str(f), "duration": duration(f), "words": words}
    meta.write_text(json.dumps(data, indent=1))
    print(f"  voice {name}: {engine}, {data['duration']:.2f}s, {len(words)} words")
    return data
