"""Record the narrator for one or more episodes (narration/<slug>_<beat>.wav + .json).
Runs on its own (no Manim needed):  python make_voice.py wire cell"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from ca.tts import speak

for slug in sys.argv[1:] or ["wire"]:
    ep = json.loads((ROOT / "episodes" / f"{slug}.json").read_text(encoding="utf-8"))
    for b in ep["beats"]:
        speak(b["say"], f"{slug}_{b['key']}", out_dir=str(ROOT / "narration"))
