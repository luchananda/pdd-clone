# Putting the clone on pdd.luisafernanda.space (repo luchananda/luisafernanda-space, Cloudflare Pages)

Nothing needs to be copied into that repo. Its workflow checks this repo out and runs our two scripts, writing the page into its own `pdd/` folder.

## What changes in `.github/workflows/pdd-refresh.yml` of luisafernanda-space (updated 19 Nov after LuWeb's reply: `pdd.yml` no longer exists)
The current workflow refreshes `pdd/index.html` every 8 hours with `python3 scripts/pdd_space/refresh_pdd.py`. LuWeb decides whether to keep that or switch to ours. To switch, replace that step with these steps (keep the commit step that follows; add `pdd` to `git add`):

```yaml
      - uses: actions/checkout@v4
        with:
          repository: luchananda/pdd-clone
          path: pdd-clone
      - run: python3 -m pip install --quiet pillow
      - name: Refresh the data (NASA, JPL, MPC)
        run: python3 pdd-clone/Marketing/reports/nea/refresh_data.py
      - name: Build the page from the live paper
        run: python3 pdd-clone/Marketing/reports/nea/build_clone.py pdd
```
and change the cron to hourly if wanted (`7 * * * *`). The commit step becomes `git add pdd`.

## What the build does
- Downloads the live front page of planetary-defense-daily.newsroomfloor.com, makes its links absolute, replaces the paper's own "Space watch" band with ours (Asteroids today, Close approaches, Impact risk) and writes `pdd/index.html`, plus `pdd/charts/`, `pdd/img/`, `pdd/d3.min.js`, `pdd/topojson-client.min.js`.
- The two tables, the map points and the Discovered table are rebuilt from the data files on every run.
- The chart PNGs live in `Marketing/reports/home/charts/` of this repo. They are drawn on the owner's Mac (macOS fonts and emoji) and pushed here; the carousels in `pdd-home-v8.html` are rebuilt with `pdd_carousels.py`.

## Notes
- The existing `pdd/` page (Planetary Defense Watch, `build_pd_watch.py`) would be replaced by this build; keep it under another folder name if it is still wanted.
- Optional secret `NASA_API_KEY` for the NeoWs feed (free at api.nasa.gov); without it the feed uses DEMO_KEY and may be rate limited. A failing step keeps the previous data.
