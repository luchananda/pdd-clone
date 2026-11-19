"""Captions (HTML, with links) for every current NEA chart (set v11). Used by the review page and the newspaper's Charts section."""
import os, datetime as _dt
UPD = _dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nea_log.json')), _dt.timezone.utc).strftime('%d %b %Y, %H:%M UTC')
A = lambda u, t: f'<a href="{u}" target="_blank" rel="noopener">{t}</a>'
CA = A('https://cneos.jpl.nasa.gov/ca/', 'NASA/JPL CNEOS close-approach data')
NEOWS = A('https://api.nasa.gov/', 'NASA NeoWs feed')
MPCNEO = A('https://www.minorplanetcenter.net/iau/NEO/toconfirm_tabular.html', 'MPC NEO Confirmation page')
NEOWS_END = f' The data was obtained using the {NEOWS}.'
SBDB = A('https://ssd.jpl.nasa.gov/tools/sbdb_lookup.html', 'JPL Small-Body Database')
PHA = A('https://cneos.jpl.nasa.gov/about/neo_groups.html', 'potentially hazardous asteroid (PHA)')
SENTRY = A('https://cneos.jpl.nasa.gov/sentry/', 'Sentry')
SENTRY_INTRO = A('https://cneos.jpl.nasa.gov/sentry/intro.html', 'how Sentry works')
TORINO = A('https://cneos.jpl.nasa.gov/sentry/torino_scale.html', 'Torino scale')
PALERMO = A('https://cneos.jpl.nasa.gov/sentry/palermo_scale.html', 'Palermo scale')
SIZEEST = A('https://cneos.jpl.nasa.gov/tools/ast_size_est.html', 'size from absolute magnitude (CNEOS)')
MPC = A('https://minorplanetcenter.net/', 'Minor Planet Center')
LDDEF = f'LD = lunar distance, 384,400 km, the average Earth–Moon distance ({CA})'
SCI = 'Large and small numbers are written in scientific notation: 1.9E<sup>7</sup> means 1.9 × 10<sup>7</sup>.'
DATA = f'Data: {MPCNEO} and the {SBDB}; the 15 closest objects passing in the next 7 days, refreshed automatically every 8 hours.'
SENTRYDATA = f'Data: {A("https://cneos.jpl.nasa.gov/sentry/", "JPL Sentry risk table")} (top 15 by Palermo value) and {CA}, refreshed automatically every 8 hours.'
TYPES = ('Symbols: 💥 potentially hazardous asteroid, 🪨 near-Earth asteroid (NEA), ☄️ comet, 🥔 main-belt asteroid. '
         f'A {PHA} is larger than about 140 m and can pass within about 19.5 LD of Earth’s orbit.')
COLORS = ('Circle colour = size class, in km: blue, 1E<sup>-3</sup>–1E<sup>-2</sup> km (1–10 m); green, 1E<sup>-2</sup>–1E<sup>-1</sup> km (10–100 m); yellow, 1E<sup>-1</sup>–1E<sup>0</sup> km (100 m–1 km); pink, over 1E<sup>0</sup> km (1 km).')
LIMITS = 'Axis limits are calculated from the data at every refresh, leaving free space around the highest and lowest values.'
IMPACT_MATH = (f'<b>How the impact probability is calculated.</b> The orbit of an object is fitted to its observations, but the measurements are uncertain, so JPL’s {SENTRY} system studies a whole cloud of orbits that all fit the data. '
               'The impact probability p<sub>i</sub> is the share (statistical weight) of that cloud whose orbits hit Earth on the date shown. '
               f'The {PALERMO} compares it with the background risk: PS = log<sub>10</sub>( p<sub>i</sub> / (f<sub>B</sub> × T) ), where T is the years until the possible impact and f<sub>B</sub> = 0.03 × E<sup>−0.8</sup> per year is the yearly chance of an impact of at least the same energy E (in megatons). '
               f'PS below −2 is no cause for concern; 0 means as likely as the background. The {TORINO} (0–10) combines probability and energy for the public ({SENTRY_INTRO}).')
HOTNOTE = 'In the enlarged view, click any object to open a card beside it with all the data we have; its name links to the JPL Small-Body Database (SSD), with the Minor Planet Center link below.'

COLORS_M = 'Circle colour = size class: blue, 1–10 m; green, 10–100 m; yellow, 100 m–1 km; pink, over 1 km.'
COLORS_KM = 'Circle colour = size class, in kilometres: blue, 0.001–0.01 km; green, 0.01–0.1 km; yellow, 0.1–1 km; pink, over 1 km.'
CUMDATA = f'Data: {MPCNEO} and the {SBDB}; refreshed automatically every 8 hours. {HOTNOTE} The data was obtained using the {NEOWS}.'
ALERT = ('The title follows the most critical object in JPL’s Sentry feed (highest Torino and cumulative Palermo value): '
         'Tier 4 (Torino 8 or more, or Palermo 2.0 or more) “Lets see what happens!” in bright red, flashing every 0.2 s; '
         'Tier 3 (Torino 5–7, or Palermo 0.0–1.99) “Time for everyone to look up!” in pink, 0.3 s; '
         'Tier 2 (Torino 2–4, or Palermo −2.0 to −0.01) “We are checking stuff out” in gold, 0.5 s; '
         'Tier 1 (Torino 0–1 and Palermo below −2.0) “All Good, we keep looking up!” in green, 0.7 s. Only the part after “IMPACT RISK” changes colour and flashes.')

def caption(fn):
    from nea_captions2 import parts
    t, sm, body = parts(fn)
    if body: return t, f'<span class="cs1">{sm}</span>' + body
    t, c = _caption(fn)
    if fn.startswith(('imp1', 'imp2', 'imp3', '07-', '08-')) or not c: return t, c
    return t, c + NEOWS_END

def _caption(fn):
    if fn.startswith('1-3-'):
        return ('Distance vs velocity and size · logarithmic', f'Each circle is one of the 15 closest NEAs. Left axis: relative velocity to Earth in km/s. Bottom axis: lunar distance in LD; top axis: the same distances in km (scientific notation). Both axes are logarithmic, so equal steps are equal ratios. Circle area follows the object’s mean size. Numbers match the boxed list on the right, sorted from fastest to slowest. {COLORS} {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('1-3c'):
        return ('Distance vs velocity and size · logarithmic, legends boxed', f'Same chart with the legends in a dotted box, left-aligned with the velocity axis title; the arrows point from LEGENDS to the object list (object types) and to the legend box (sizes). Both axes are logarithmic. Circle area follows the object’s mean size. {COLORS_M} {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('1-3d'):
        return ('Distance vs velocity and size · linear, legends boxed', f'Same chart on linear axes that start at 0, with the legends in a dotted box, left-aligned with the velocity axis title; the arrows point from LEGENDS to the object list (object types) and to the legend box (sizes). {COLORS_M} {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('1-3b'):
        return ('Distance vs velocity and size · linear', f'Same data as the logarithmic chart, on linear axes that start at 0. Left axis: relative velocity in km/s. Bottom axis: lunar distance in LD, in steps of 10; top axis: the same distances in km. Numbers match the list on the right, sorted from fastest to slowest. {COLORS} {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('2-3c'):
        return ('Size, distance and velocity · LD values on the top edge', f'Same three measurements as the other 3D chart, with the lunar-distance values (LD | km) written along the top edge of the distance axis and its name on the bottom edge. Horizontal: object size in km, from 0. Depth: lunar distance, from 1 LD. Vertical: relative velocity in km/s, from 0. Light dotted lines show each object’s velocity; the single dotted line from the LD axis shows its distance. The list gives each object’s velocity. {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('2-3-3d'):
        grid = ' Faint dotted grid lines help to read the values.' if 'grid' in fn else ''
        return ('Size, distance and velocity', f'Three measurements in one picture. Horizontal: object size in km, from 0. Depth axis: lunar distance in LD | km, from 1 LD (an object can never be at a negative distance). Vertical: relative velocity in km/s, from 0. The light dotted line from each object down to the floor shows its velocity; the single dotted line from the LD axis shows where its distance sits. The distance values (LD | km) are turned 90° clockwise beside the axis, whose name runs parallel to it. Numbers match the list on the right, sorted by velocity, which gives only each object’s velocity.{grid} '
                'How the three values relate: distance in km = LD × 384,400; the time the object needs to cover that distance at its relative velocity is t = d / v; its apparent angular size from Earth is about θ ≈ D / d; and, for a given density ρ, its kinetic energy is E = ½ m v² with m = (π/6) ρ D³, so energy grows with the cube of the size and the square of the velocity. '
                f'Sizes are estimated from absolute magnitude ({SIZEEST}). {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('3-'):
        return ('Diameter vs distance · logarithmic', f'Each horizontal line is the error margin of one object’s size, from its smallest to its largest estimate; the symbol marks the mean. Bottom axis: object size in km, in scientific notation. Left axis: lunar distance in LD. Right axis: the same distance in km (scientific notation). All three axes are logarithmic. The vertical end bars [ | ] mark the smallest and largest estimate. Sizes are estimated from absolute magnitude ({SIZEEST}). {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('3b'):
        return ('Diameter vs distance · linear', f'Same data on linear axes that start at 0. Each horizontal line is the error margin of one object’s size (smallest to largest estimate); the symbol marks the mean. Bottom axis: object size in km (scientific notation), in steps of 0.05. The vertical end bars [ | ] mark the smallest and largest estimate. Left axis: lunar distance in LD. Right axis: the same distance in km. {TYPES} {LDDEF}. {SCI} {LIMITS} {DATA} {HOTNOTE}')
    if fn.startswith('07-'):
        return ('Cumulative NEAs since first capture · logarithmic', f'Running count of distinct near-Earth asteroids by close-approach date since 1 November 2026, all listed on the {MPCNEO}. 🪨 marks all NEAs and 💥 the {PHA}s. The vertical axis is logarithmic. The chart is redrawn automatically every 8 hours, when the data refreshes, and the date labels thin out as days are added. Last updated: {UPD}. {CUMDATA}')
    if fn.startswith('08-'):
        return ('Cumulative NEAs since first capture · linear', f'Same count on a linear vertical axis: distinct near-Earth asteroids by close-approach date since 1 November 2026, all listed on the {MPCNEO}. 🪨 marks all NEAs and 💥 the {PHA}s. The chart is redrawn automatically every 8 hours, when the data refreshes, and the date labels thin out as the series grows. Last updated: {UPD}. {CUMDATA}')
    if fn.startswith('imp1'):
        return ('Impact risk · distance vs Torino and Palermo scales', f'The objects with the highest impact risk on JPL’s {SENTRY} list (ranked by Palermo value); those with a known close-approach distance are plotted. Bottom axis: lunar distance in LD (logarithmic); top axis: the same distance in km (logarithmic). Left axis: 🎯 the {TORINO}, 0–10, which combines impact probability and consequences (0 = no hazard). Right axis: the object’s own symbol sits at its {PALERMO} value; a dotted line joins the two. ⚠️ marks the three objects with the highest impact probability. Numbers are the Palermo rank (1 = highest). {COLORS} {TYPES} {LDDEF}. {LIMITS} {SENTRYDATA} {HOTNOTE}')
    if fn.startswith('imp2'):
        return ('Impact risk · possible impact year vs probability and diameter', f'Each object on the {SENTRY} list at its possible impact year (bottom axis: years counted from today, logarithmic, with the calendar year in brackets, so that near and distant dates are spread out) and its impact probability (left axis, logarithmic, scientific notation). The white dot on the right axis is its diameter in km (logarithmic, estimated from absolute magnitude), joined to the object by a grey dotted line. ⚠️ marks the three highest probabilities; numbers are the Palermo rank. {TYPES} {SCI} {LIMITS} {SENTRYDATA} {IMPACT_MATH} {HOTNOTE}')
    if fn.startswith('imp3b'):
        return ('Impact risk · alert level and timeline by century', f'The century timeline of the {SENTRY} list with a live alert in the title. {ALERT} Height: impact probability (logarithmic, scientific notation). Circle size and colour: diameter. ⚠️ marks the three highest probabilities; numbers are the Palermo rank. {COLORS_KM} {TYPES} {SCI} {LIMITS} {SENTRYDATA} {IMPACT_MATH} {HOTNOTE}')
    if fn.startswith('imp3'):
        return ('Impact risk · timeline by century', f'The same objects on a timeline where each column is a century and empty centuries are skipped, so decades and the far future are readable together. Height: impact probability (logarithmic, scientific notation, one digit before the E). Circle size and colour: diameter. ⚠️ marks the three highest probabilities; numbers are the Palermo rank. {COLORS_KM} {TYPES} {SCI} {LIMITS} {SENTRYDATA} {IMPACT_MATH} {HOTNOTE}')
    return (fn, '')
