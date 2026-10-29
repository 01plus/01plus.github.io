# 01+ 名校背景提升 · Website

Static site for **01plus.github.io**, built by `./build.sh` (→ `build.py`).

## Sources (edit these)
- `src/index.html` — landing page. No document skeleton; this file is also published as the claude.ai artifact.
- `src/case-carvetrack.html` — the 30-month sample project film (CarveTrack).
- `src/case-template.html` + `cases/cases.json` — one case-study page per entry in the JSON.
- `assets/` — photos, school seals (`assets/logos/`), case images (`assets/cases/`), fonts (`assets/fonts/`).

## Built (do not edit by hand)
- `index.html`, `case/*.html`, `404.html`, `sitemap.xml`, `robots.txt`, `llms.txt`.
- The build adds the SEO head (title, description, canonical, Open Graph, JSON-LD), swaps the inline
  base64 fonts in the sources for the shared `assets/fonts/*.woff2` files, and converts generated case
  PNGs to web JPGs (1400px, 720px, and 1200×630 share images).

## Workflow
1. Edit a source or `cases/cases.json`.
2. If any text changed, re-subset the fonts (the subsetter also writes `assets/fonts/*.woff2`).
3. `./build.sh`, then commit sources and built files together.

Case images are generated with the OpenAI Images API from the `img` prompts in `cases/cases.json`
(`gpt-image-2`, 1536×1024); drop a PNG named `assets/cases/<slug>-{hero,s1,s2,s3}.png` to replace one.
