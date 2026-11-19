# Handoff: PDD "Space Watch" band and "Asteroids today" side panel

Everything is in this folder (paths below are relative to it). Reference page: open `Marketing/reports/home/pdd-home-v8.html` in a browser (it loads `charts/`, `d3.min.js`, `topojson-client.min.js` from its own folder). A working example of reusing the band inside ANOTHER page (the live PDD front page) is `site/index.html`, built by `Marketing/reports/nea/build_clone.py`. Data as of 19 Nov 2026. Owner: Luisa (Planetary Defense Daily, built on Newsroom Floor).

## What to build
Put two things into your template: (1) a **SPACE WATCH** band with two collapsible blocks, (2) an **Asteroids today** side panel / band (map, discovered list, cumulative chart carousel).

### Space Watch (in `pdd-home-v8.html`: `<section id="space-watch">`)
- Heading SPACE WATCH. Two `<details>`, closed on load; the open sign is 5x the text size. Each block is a 50/50 grid.
- Block 1 **CLOSE APPROACHES · TOP 15 NEXT 7 DAYS**: carousel of 6 plots on the left, table on the right. Table caption above the table: **COMING NOT SO CLOSE!** (all caps) plus a description (what it is, data sources, refresh every 8 h, last updated, "click a column heading to sort").
- Block 2 **IMPACT RISK**: table left (own description above), carousel of 2 plots right.
- The chart caption sits below the grid at 100% width and follows the active slide; captions are collapsed by default (first line + arrow). Carousel arrows and the "1 / 6" counter are large. Tables sort on any column (`data-v` on each cell holds the sort value). Clicking a plot opens an enlarged view; objects are clickable (card beside the object, light purple 60%, black text).

Close approaches table columns: Closest (UTC) · Object (JPL link) · LD · Size (m) · Abs. mag. (H) · First seen · Velocity (km/s). Source: `Marketing/reports/nea/nea_log.json` (`rows[]`: `approach_utc`, `designation`, `jpl_url`, `miss_ld`, `diam_min_m`, `diam_max_m`, `H_mag`, `first_seen`, `rel_velocity_kms`); take rows whose `approach_date` is within today..today+6, sort by `miss_ld`, keep 15.

Impact risk table columns: # · Object (link to cneos.jpl.nasa.gov/sentry/details.html#?des=...) · Impact year(s) · Prob. · Palermo · Torino · LD. Source `sentry15.json`, built by `step_sentry()` in `refresh_all.py` from the Sentry SUMMARY endpoint `https://ssd-api.jpl.nasa.gov/sentry.api` (fields `ps_cum`, `ip`, `ts_max` (null = 0), `range`, `h`, `diameter`). Do not use `?all=1` (per-virtual-impactor values gave wrong Palermo numbers).

### Charts (all dark background, in `Marketing/reports/home/charts/`, each with a same-name `.json` for the clickable objects)
| Where | File | Shows |
| --- | --- | --- |
| Close approaches 1 | `3-diameter-vs-distance-log-dark.png` | size range vs distance, log |
| Close approaches 2 | `3b-diameter-vs-distance-linear-dark.png` | same, linear |
| Close approaches 3 | `2-3-3d-dark-grid.png` | size, distance, velocity (3D, grid) |
| Close approaches 4 | `2-3d-3d-swapped-axes-dark.png` | same, LD vertical and velocity in depth |
| Close approaches 5 | `1-3c-distance-velocity-size-log-legends-dark.png` | distance vs velocity, bubble = size, log |
| Close approaches 6 | `1-3d-distance-velocity-size-linear-legends-dark.png` | same, linear |
| Impact risk 1 | `imp3b-timeline-century-alert-dark.png` | century timeline; animated alert title (APNG) |
| Impact risk 2 | `imp1b-distance-torino-palermo-table-dark.png` | distance vs Torino/Palermo + table (taller image; keep its aspect ratio in the lightbox) |
| Side panel | `07-cumulative-log-dark.png`, `08-cumulative-linear-dark.png` | cumulative NEAs since 1 Nov 2026 |

Charts are made by `Marketing/reports/nea/nea_charts_v11.py` (Python + Pillow; needs macOS fonts and Apple Color Emoji; run `python3 nea_charts_v11.py OUTDIR`). Do not regenerate on Linux. Type emoji: 💥 PHA, 🪨 NEA, ☄️ comet, 🥔 main-belt asteroid, ⚠️ top-3 probability, 🎯 Torino. Size colours: blue 1-10 m, green 10-100 m, yellow 100 m-1 km, pink over 1 km.

Impact alert (title of the timeline): tier from the highest Torino / cumulative Palermo among objects that can hit within 200 years. Tier 4 "Lets see what happens!" #FF6961 (Torino>=8 or Palermo>=2.0, 1.2 s); Tier 3 "Time for everyone to look up!" #FFB6C1 (Torino 5-7 or Palermo 0-1.99, 1.3 s); Tier 2 "We are checking stuff out" #FDFD96 (Torino 2-4 or Palermo -2 to -0.01, 1.5 s); Tier 1 "All Good, we keep looking up!" #77DD77 (otherwise, 1.7 s). Today: tier 2, caused by 101955 Bennu (Palermo -1.40), which flashes with the title.

Captions: `nea/nea_captions2.py` `parts(filename)` returns (title, one-line summary, HTML body). Order DATA, SCALES, SYMBOLS, REFERENCES. They are already baked into the carousel markup of `pdd-home-v8.html`.

### Asteroids today (in `pdd-home-v8.html`: `<aside class="side">`; in the clone it is a band under Space Watch)
1. Map: d3 Natural Earth (`d3.min.js`, `topojson-client.min.js`; world data is embedded in the page script). Data `WATCH` = `Marketing/reports/home/watch-data.json` (`time`, `sun{lat,lon}` for the night shading (90° circle around the anti-sun point), `pts[]` with `des`, `mpec`, `date`, `pha`, `neo`, `impact`, `lat`, `lon`). Dots are emoji (🪨 NEO, 💥 PHA, ☄️ atmospheric entry). Enlarge button + click on the map opens it big; clicking a dot opens a card (designation links to JPL SBDB; type, date, MPEC, position, links to SBDB and Minor Planet Center).
2. Discovered today: designations announced the latest day (from `pts[]`), `designation · MPC · MPEC n`, click opens the card.
3. Rare finds (Amazon affiliate tile; owner will supply items) with "(Affiliate link)".
4. Cumulative NEAs: carousel of the two cumulative charts, auto-advance 7 s, collapsed caption.
5. Three ads: Subscribe, Newsroom Floor (newsroomfloor.com), Follow on X (x.com/newtons_in_laws).

## Style (PDD navy theme)
Background #0b1526, card #16233a / #121e33, ink #eef2fa, ink 2 #cbd5e6, dim #a2afc6, rule #2c3b57, accent #de7c7c, link #8ab7ea, gold #ffc904. Headings Playfair Display 700/900, body Helvetica Neue. Body text 21 px, tables 14.5-16 px, captions 14 px or more. 50/50 grids at 900 px and wider, one column below.

## Reusing it in another template (how the clone does it)
`Marketing/reports/nea/build_clone.py` is a complete example: it fetches the live paper's front page, makes its links absolute, replaces the paper's own "Space watch" band with ours, regenerates the two tables and the map data from the JSON files at build time, scopes all our CSS under one wrapper id (`#swx`, function `scope()`) so the host styles stay untouched, and writes `site/index.html` (+ `site/charts/`, `d3.min.js`, `topojson-client.min.js`). Copy that approach: wrapper id + scoped CSS, the lightbox element `#clb`, the map overlay `#mlb` and card `#ocard`, and the small scripts (carousel `show`/`step`, table sorting, chart lightbox, map cards).

## Data refresh
GitHub Action `refresh-home.yml` runs `refresh_all.py` every 8 h in the owner's repo (Sentry, close approaches, sky map); charts are only regenerated on the owner's Mac. Sources: MPC NEO Confirmation page, JPL Small-Body Database, JPL Sentry, NASA/JPL CNEOS close approaches, NASA NeoWs.

## Limits and open items
- Newsroom Floor's own templates cannot hold custom HTML/tables/carousels (only band order and up to 8 text/link/button/picture blocks), so this has to live in a page you host.
- Not done: an impact plot showing the Torino and Palermo axes together, a megaton pop-out in the impact caption, the diameter-chart legend aligned with its subtitle.
- Header font Playfair Display is not installed on the owner's Mac, so chart text uses Arial/Didot.
