# Circuit Academy

Automated electronics-education YouTube Shorts. One component per Short, **two uploads a day**
(about 12:00 and 19:00 London), each one the next part in `episodes/curriculum.json`, with a
hand-drawn custom thumbnail.

## Every episode has the same shape

1. **Hook**: the part on screen from frame one, energy rings, light sweep, title eases in
2. **What it looks like / does**: drawn real part with labels, or its symbol
3. **Circuit symbol**: big, with notes (or a side-by-side comparison)
4. **In a circuit**: a real circuit draws itself, then current flows and loads light up
5. **Key fact**: a formula or comparison card
6. **Cinematic ending**: "Next time: …" reveal, the mouse clicks Subscribe and rings the bell (no captions)

Throughout: word-by-word captions, narrator (Kokoro "af_heart"), synthesised sound effects,
nothing in the top 330 px (iPhone notch + YouTube icons).

**Titles, descriptions and tags** all come from one template (`ca/metadata.py`):

- Title: `<curiosity hook> ⚡ #electronics #shorts`
- Description: hook / what you'll learn / series line / "Next up" / hashtags
- Tags: the episode's own tags plus the channel's shared tags

## Files

| Path | What it is |
|---|---|
| `episodes/curriculum.json` | upload order |
| `episodes/<slug>.json` | one episode: narrator lines + which visual for each, thumbnail text, YouTube hook/learn/tags |
| `ca/engine.py` | the one scene every episode uses (all beat types + ending) |
| `ca/parts.py` | every component: symbol, drawn picture, colour |
| `ca/circuits.py` | named circuits for the `circuit` beat |
| `ca/thumb.py` | hand-drawn thumbnail template |
| `ca/sfx.py` | sound effects, synthesised in code |
| `ca/tts.py` | narrator (Kokoro, falls back to Microsoft voices) |
| `make_short.py` | voice → animation → captions → sound → mp4 + thumbnail |
| `scripts/upload.py` | YouTube upload + thumbnail, records `state/uploads.json` |
| `get_youtube_token.py` | run once on your computer (IDLE, F5) to get the refresh token |

## YouTube setup (once)

1. In Google Cloud Console (the same project as the Clash channels is fine), make sure the
   **YouTube Data API v3** is enabled and you have an OAuth client of type **Desktop app**.
2. Open `get_youtube_token.py` in IDLE and press **F5**. Paste the client ID and secret, sign in
   with the **electronics channel's** account in the browser, and allow access.
3. On GitHub: **circuit-academy → Settings → Secrets and variables → Actions → New repository secret**,
   and add `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
4. **Custom thumbnails need a verified channel**: verify the channel by phone at youtube.com/verify.
   Until then the video still uploads; only the thumbnail is skipped, and the log says why.

Uploads start at the next scheduled time after the secrets exist. To upload one straight away,
go to **Actions → Upload to YouTube → Run workflow**. To pause, disable that workflow in the Actions tab.

## Previews

Every push builds the next two episodes due, with the narrator, into the `previews` branch.
