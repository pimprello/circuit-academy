# Circuit Academy

Automated electronics-education YouTube Shorts: one component per video, animated with
[Manim](https://www.manim.community/), voiced by a neural narrator, captions burned in,
built and uploaded by GitHub Actions.

**Status: style stage.** Only the Wire episode exists; YouTube uploading is added once the style is agreed.

- `ca/short_wire.py` – the Wire Short (animation, beats, cinematic ending)
- `ca/symbols.py` – schematic symbols (IEEE / IEC conventions) with real pin positions
- `ca/captions.py` – word-by-word captions, auto-fit so they never leave the screen
- `ca/tts.py` – narrator (Microsoft neural voice via edge-tts) with word timings
- `make_short.py` – voice → animation → captions → final mp4
- `.github/workflows/preview.yml` – builds the voiced preview into the `previews` branch

Safe zones: nothing above 330 px (iPhone Dynamic Island + YouTube icons); captions stay within 860 px wide.
