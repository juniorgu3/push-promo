# push-promo

Show promo kit for Junior and The Push, Push Lite and Junior Guthrie. The weekly promo run uses this repo, so nothing has to come from Junior's Mac.

## What's here

- `kit/`: the locked-in poster kit (Nov 14 2026): cream concert-poster layout, torn-print photo, each act's logo and colors. See `kit/README.md`.
  - Render: `cd kit && python3 heritage.py specs.json out/`
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
