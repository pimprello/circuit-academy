"""Upload one finished episode to YouTube, set its hand-drawn thumbnail, record it in state/uploads.json.

Needs repository secrets YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (see README).
Usage: python scripts/upload.py <slug>      (expects out/<slug>.mp4 and out/<slug>_thumb.jpg)"""
import datetime as dt
import json, os, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from ca.metadata import build

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build as yt_build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube"]


def client():
    creds = Credentials(None, refresh_token=os.environ["YT_REFRESH_TOKEN"], token_uri="https://oauth2.googleapis.com/token",
                        client_id=os.environ["YT_CLIENT_ID"], client_secret=os.environ["YT_CLIENT_SECRET"], scopes=SCOPES)
    return yt_build("youtube", "v3", credentials=creds, cache_discovery=False)


def upload(slug):
    ep = json.loads((ROOT / "episodes" / f"{slug}.json").read_text(encoding="utf-8"))
    meta = build(ep)
    video = ROOT / "out" / f"{slug}.mp4"
    thumb = ROOT / "out" / f"{slug}_thumb.jpg"
    yt = client()
    body = {"snippet": {"title": meta["title"], "description": meta["description"], "tags": meta["tags"],
                        "categoryId": meta["categoryId"], "defaultLanguage": "en", "defaultAudioLanguage": "en"},
            "status": {"privacyStatus": os.environ.get("YT_PRIVACY", "public"), "selfDeclaredMadeForKids": False,
                       "embeddable": True}}
    req = yt.videos().insert(part="snippet,status", body=body,
                             media_body=MediaFileUpload(str(video), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True))
    resp, tries = None, 0
    while resp is None:
        try:
            status, resp = req.next_chunk()
            if status:
                print(f"  uploading {slug}: {int(status.progress() * 100)}%")
        except HttpError as e:
            if e.resp.status in (500, 502, 503, 504) and tries < 5:
                tries += 1
                time.sleep(2 ** tries)
                continue
            raise
    vid = resp["id"]
    print(f"uploaded {slug}: https://youtube.com/shorts/{vid}")

    thumb_ok = False
    for attempt in range(3):
        try:
            yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute()
            thumb_ok = True
            print("  thumbnail set")
            break
        except HttpError as e:
            msg = e.content.decode(errors="ignore")[:300]
            print(f"  thumbnail not set (attempt {attempt + 1}): {e.resp.status} {msg}")
            if e.resp.status == 403:
                print("  -> custom thumbnails need a verified channel: youtube.com/verify")
                break
            time.sleep(5)

    # keep the thumbnail in the repo so it can be attached later if YouTube refused it now
    keep = ROOT / "state" / "thumbs" / f"{slug}.jpg"
    keep.parent.mkdir(parents=True, exist_ok=True)
    keep.write_bytes(thumb.read_bytes())

    state_p = ROOT / "state" / "uploads.json"
    state = json.loads(state_p.read_text())
    state["uploaded"].append({"slug": slug, "video_id": vid, "title": meta["title"], "thumbnail": thumb_ok,
                              "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")})
    state_p.write_text(json.dumps(state, indent=1, ensure_ascii=False))


def backfill_thumbnails():
    """Attach thumbnails to earlier uploads that went up before the channel was verified."""
    state_p = ROOT / "state" / "uploads.json"
    state = json.loads(state_p.read_text())
    todo = [u for u in state["uploaded"] if not u.get("thumbnail")]
    if not todo:
        return
    yt = client()
    for u in todo:
        img = ROOT / "state" / "thumbs" / f"{u['slug']}.jpg"
        if not img.exists():
            continue
        try:
            yt.thumbnails().set(videoId=u["video_id"], media_body=MediaFileUpload(str(img), mimetype="image/jpeg")).execute()
            u["thumbnail"] = True
            print(f"  thumbnail added to earlier video {u['slug']}")
        except HttpError as e:
            print(f"  earlier thumbnails still refused ({e.resp.status}) - verify the channel at youtube.com/verify")
            break
    state_p.write_text(json.dumps(state, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    if sys.argv[1:] == ["--backfill"]:
        backfill_thumbnails()
    else:
        for s in sys.argv[1:]:
            upload(s)
