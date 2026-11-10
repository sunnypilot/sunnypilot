# Achievements and the community log

Everything here runs on the car. Nothing is uploaded yet: the uploads are a dry run that writes files.

| File | What it does |
| --- | --- |
| `achievementsd.py` | Onroad process. Feeds car messages to the engine and the community log. |
| `engine.py`, `catalog.py`, `catalog.json` | Driving stats and achievement unlocks (Phase 1). |
| `community.py` | Community log in `community.db`: 6 km tiles, drive start/end tiles, daily totals, region per day. Also the privacy filter and the report builders. |
| `preview.py` | Writes what the car would send, plus `map.html`, to `preview/`. |
| `h3lite.py` | The H3 functions we need, in pure Python (sunnypilot doesn't add packages). Same cell ids as Uber's H3. |
| `regions.py`, `regions.json.gz` | Tile to home region (`US-OH`, `CA-ON`, `GB`). Built by `tools/build_regions.py`. |
| `replay.py` | Runs everything over drives already saved on the car. |
| `simulate.py` | Made-up drives for tests and a demo. |

## Privacy rules (from the build plan)

- Positions only become H3 resolution 6 tiles (about 6 km). No coordinates, times of day or routes are stored.
- A tile where drives start or end on 3+ days is a frequent stop. It and the 6 tiles around it never leave the car.
- Other start and end tiles wait 14 days.
- Hidden tiles never leave the car.
- The tile batch is sorted and has no dates. It is separate from the daily report.
- Others only ever see resolution 4 blocks (about 45 km).
- Home region: where you drove most on most days in the last 90 days. A detected change is sent at most every 30 days; a change you make goes right away.

## Files on the car

All under `/data/media/0/achievements/`:

- `state.json`: achievement progress.
- `community.db`: the community log.
- `community_settings.json` (optional): `{"level": 0-3, "region": "auto" | "country" | "hidden" | "US-OH"}`. Level 0 (off) is the default.
- `preview/`: `daily-YYYY-MM-DD.json`, `tiles.json`, `delete.json`, `map.html`. Rewritten after every drive.

`map.html` shows your frequent stops. It is for you only.

## See it on your own drives

```sh
ssh comma@<car ip>
cd /data/openpilot
python -m openpilot.sunnypilot.achievements.replay    # qlogs in /data/media/0/realdata; add --days 30 or --rlog
# on your computer:
scp comma@<car ip>:/data/media/0/achievements/replay/preview/map.html .
```

The replay writes to `achievements/replay/` and doesn't touch live progress.

## Tests

```sh
python -m pytest openpilot/sunnypilot/achievements/tests
```

With `h3` installed (`pip install h3`), the H3 tests also compare random points against the real library.
