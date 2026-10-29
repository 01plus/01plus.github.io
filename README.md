# 01+ 名校背景提升 · Website

Static site for **01plus.github.io**.

- `src/index.html` — landing page source (no document skeleton; this is what gets published as the claude.ai artifact).
- `src/case-carvetrack.html` — CarveTrack case-study page source (the scroll-driven 30-month film). Asset links in it are `../assets/`.
- `index.html`, `case/carvetrack.html` — standalone pages served by GitHub Pages. **Generated** by `./build.sh`; do not edit by hand.
- `assets/` — photos, QR code, logo, favicons.

Both sources embed subsetted webfonts between `/*FONTS-START*/` and `/*FONTS-END*/`; re-subset after changing any text.
After editing a source, run `./build.sh` and commit the sources and the built pages together.
