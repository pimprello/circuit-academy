"""Print the next N episode slugs to upload (in curriculum order, skipping ones already uploaded).
Usage: python scripts/pick_next.py [N]"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
order = [e["slug"] for e in json.loads((ROOT / "episodes" / "curriculum.json").read_text())["order"]]
done = {u["slug"] for u in json.loads((ROOT / "state" / "uploads.json").read_text())["uploaded"]}
todo = [s for s in order if s not in done and (ROOT / "episodes" / f"{s}.json").exists()]
print(" ".join(todo[:n]))
