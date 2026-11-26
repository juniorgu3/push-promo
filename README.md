# push-promo

Show promo kit for Junior and The Push, Push Lite and Junior Guthrie. The weekly promo run uses this repo, so nothing has to come from Junior's Mac.

## What's here

- `kit/`: poster kit. **Current style (approved Nov 20 2026): `bold.py`** — bold Hatch Show letterpress: huge wood-type headline, big torn-print photo, "★ LIVE AT ★" in block letters, venue logo as hero, date/time on a ribbon banner. Band/Junior: cream paper, red headline w/ navy offset shadow, navy ribbon. Push Lite: its own colors — slate-navy base (not black), silver Push/gold LITE logo, gold headline + gold ribbon; dark-ink venue logos auto-switch to their `-white.png` version or get inverted.
  - Render: `cd kit && python3 bold.py specs.json out/` (older styles: `heritage.py`, `render.py`)
  - Optional `at_label` replaces "LIVE AT" (e.g. "LAST WEEKEND AT" on a THANK YOU post).
  - Song reels with a cover card: `cd kit && python3 reel_card.py reels.json out/` (spec: act, song, artist, clip, hook with | line breaks, sub, optional photo/tagline, out). Makes `<out>.mp4` (0.5 s cover card, then a slow push-in, audio delayed 0.5 s), `<out>-cover.jpg` (use as the custom thumbnail) and `<out>-frame.jpg`. Keeps every key element in x 90–950, y 430–1310 even at full push-in and prints ok or what's outside.
  - Multi-show ("THIS WEEKEND") posts: same bold.py, spec with `headline`, `follow` and `shows:[{date,time,end,venue,venue_logo,town}]`.
  - Stories (format story) keep everything inside the safe zone (top 250px / bottom 300px clear).
  - Needs: `pip install --break-system-packages playwright rembg onnxruntime opencv-python-headless scipy pillow numpy`, Chrome at `/usr/bin/google-chrome`
  - Venue logos live in `kit/assets/` as `t-venue-<name>.png`
- `songs/`: short hook clips of Junior's own recordings for reels, plus `reel-songs.json` (rotation list and exclusions).
- `renders/<date>/`: finished posters, stories and reels for each week, with the `specs.json` that made them.

## Posting from the cloud

Files committed here are public at:

`https://raw.githubusercontent.com/juniorgu3/push-promo/main/renders/<date>/<file>`

vidIQ takes these links directly:
- images: `vidiq_upload_image` with `image` set to the raw URL
- reels: `vidiq_video_upload` with `url` set to the raw URL

So the weekly run can render, commit, upload and schedule without anyone at the Mac.

## Stories

vidIQ can't post stories. Those go through Meta Business Suite in Chrome on Junior's Mac (the Mac must be on with Chrome open). Each story uses the matching `*-story.jpg` from `renders/<date>/`, with a swipe-up link to the act's site.
