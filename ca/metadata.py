"""One template for every upload, so the channel looks consistent:

  Title        <curiosity hook> ⚡ #electronics #shorts          (max 100 chars)
  Description  hook line / what you'll learn / series line / next episode / hashtags
  Tags         shared channel tags + the episode's own (max 500 chars total)

Each episode only supplies "youtube": {"hook": ..., "learn": ..., "tags": [...]}."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHANNEL_TAGS = ["electronics", "electronics for beginners", "learn electronics", "electronic components",
                "how it works", "circuits", "physics", "engineering", "stem", "shorts"]
CATEGORY_EDUCATION = "27"


def _order():
    return json.loads((ROOT / "episodes" / "curriculum.json").read_text())["order"]


def build(ep):
    yt = ep["youtube"]
    order = _order()
    slugs = [e["slug"] for e in order]
    i = slugs.index(ep["slug"])
    nxt = order[i + 1]["name"].title() if i + 1 < len(order) else None

    title = f"{yt['hook']} ⚡ #electronics #shorts"
    if len(title) > 100:
        title = f"{yt['hook']} ⚡ #shorts"[:100]

    hashtag = "#" + ep["slug"].replace("-", "").replace(" ", "")
    lines = [yt["hook"], "", yt["learn"], "",
             "⚡ A new electronics component explained in under a minute, twice a day.",
             f"🔔 Next up: {nxt}. Subscribe so you don't miss it." if nxt else "🔔 Subscribe for more electronics explained simply.",
             "", f"#electronics {hashtag} #learnelectronics #engineering #physics #stem #shorts"]
    description = "\n".join(lines)

    tags, total = [], 0
    for t in list(dict.fromkeys(yt.get("tags", []) + CHANNEL_TAGS)):
        if total + len(t) + 2 > 480:
            break
        tags.append(t)
        total += len(t) + 2
    return {"title": title, "description": description, "tags": tags, "categoryId": CATEGORY_EDUCATION}


if __name__ == "__main__":
    import sys
    for slug in sys.argv[1:] or ["wire"]:
        ep = json.loads((ROOT / "episodes" / f"{slug}.json").read_text(encoding="utf-8"))
        print(json.dumps(build(ep), indent=1, ensure_ascii=False))
