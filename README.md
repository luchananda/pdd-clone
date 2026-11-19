# PDD clone (pdd.luisafernanda.space)

The live Planetary Defense Daily front page (planetary-defense-daily.newsroomfloor.com) with our Space Watch band: Asteroids today (map), Close approaches and Impact risk.

- `Marketing/reports/nea/build_clone.py` fetches the live page, makes its links absolute, swaps the paper's own Space watch band for ours and writes `site/index.html`.
- `Marketing/reports/nea/refresh_data.py` refreshes the data (NeoWs, MPC, Horizons, JPL Sentry). The tables, the map and the Discovered list are rebuilt from it on every run.
- The charts (`Marketing/reports/home/charts/`) are drawn by `nea_charts_v11.py` on the owner's Mac (macOS fonts and emoji) and pushed here; the carousels in `pdd-home-v8.html` are rebuilt with `pdd_carousels.py`.
- A GitHub Action (`.github/workflows/clone.yml`) rebuilds and deploys to GitHub Pages every hour.
- Handoff notes: `HANDOFF.md`.

Optional secret: `NASA_API_KEY` (free at api.nasa.gov; without it the NeoWs feed uses DEMO_KEY, which is rate limited).
