# Push Promo Kit (all 3 acts)
Render: python3 render.py specs.json out   (needs: pip install playwright; Chrome at /usr/bin/google-chrome or set executable_path)
Spec fields: act (band|lite|junior), step (announce|3wk|10d|tomorrow|tonight), format (feed|story),
venue, venue_logo (file in assets/, trimmed transparent PNG preferred; null = venue name set in type),
town, date YYYY-MM-DD, time HH:MM (24h), address, optional tag (e.g. "Free Steelers Tailgate"),
optional photo/photo_top/photo_h/photo_pos, out.
System: dark #0D0E10 base, toned photo w/ grain, act logo top, solid ribbon (band red #C8102E / Push Lite gold #E9B53B / Junior black w/ gold #D4A845),
venue logo on cream card #F3F0E9 (venue = hero), Big Shoulders Display 800/900 + Inter 500/700 only. No gradients on text, no tagline on graphics.
Venue logo rules: use the venue's real logo from its official site; trim padding; must be >=400px wide, else set venue name in type.
Always LOOK at every render: no heads under logo/ribbon, nothing clipped (renderer prints OVERFLOW if so).
