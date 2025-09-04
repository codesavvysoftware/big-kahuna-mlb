# Big Kahuna — MLB Daily Modeling Toolkit

Python tools to build daily MLB matchup tables (schedule + probables + your inputs for park/wRC+/bullpen + DraftKings lines), compute simple & modeled win probabilities, and export to Excel. Includes an optional performance tab to track strategy results.

> **Heads-up**: This project uses public MLB Stats API via `statsapi` (no API keys). Betting examples are for analysis only — wager responsibly.

---

## Features
- Pull **today’s schedule & probables** (`statsapi`)
- Compute:
  - **Simple model**: (home win% at home + road opponent loss% on road) / 2
  - **Expected runs** using your **wRC+ L/R splits**, **starter/bullpen ERAs**, and **park factors**
  - **Bill James Pythagorean** win probabilities
  - Optional **blended** probability (simple ↔ modeled) via logit blend
- **DraftKings CSV** ingestion (american odds, total, O/U)
- **Excel export** with 3–4 tabs:
  - `Schedule_Bets` — lines + simple edge
  - `Model_Detail` — pitchers, expected runs, splits
  - `Blended` — combined probabilities
  - `Performance` — (optional) ROI summaries & per-game ledger
- Optional **scores ingestion** to grade results later

---

## Repo Layout

big-kahuna-mlb/
├─ big_kahuna.py # main script
├─ scores_on_date.py # optional helper (pulls scores by date)
├─ configs/
│ └─ example_config.yaml # tweakable parameters
├─ data/
│ └─ dk_template_YYYY-MM-DD.csv # safe example template (no real odds)
├─ outputs/ # Excel/CSV outputs (gitignored)
├─ .mlb_cache/ # optional request cache (gitignored)
├─ Pipfile / Pipfile.lock # Pipenv (preferred)
├─ requirements.txt # optional fallback
├─ .gitignore
├─ LICENSE
└─ README.md


---

## Setup

### Python
- Python **3.10+** recommended (works on 3.9+ if `zoneinfo` available)

### Option A: Pipenv (recommended)
```bash
pipenv install
pipenv install XlsxWriter  # for Excel export
# (optional) pipenv install pyyaml  # if you’ll use config files

Option B: venv + pip

python -m venv .venv
. .venv/Scripts/activate   # Windows
# or: source .venv/bin/activate
pip install -r requirements.txt


Minimal requirements.txt

mlb-statsapi
pandas
XlsxWriter
PyYAML



You can generate a same-day template from your schedule in your own workflow, then hand-fill odds.

Run

# Pipenv examples
pipenv run python big_kahuna.py \
  --date 2025-09-03 \
  --dk-csv data/dk_template_2025-09-03.csv \
  --blend-w 0.7 --auto-blend \
  --export-xlsx outputs/big_kahuna_2025-09-03.xlsx
Useful flags (exact set depends on your current script):

--date YYYY-MM-DD : target slate

--dk-csv PATH : DraftKings CSV with odds

--blend-w 0.70 + --auto-blend : enable blended prob

--export-xlsx PATH : write Excel with 3–4 tabs

(optional) --config configs/config.yaml : load defaults

(optional) --finals-only : when using scores_on_date.py

Output (Excel Tabs)

Schedule_Bets:
Date, ET time, away/home short names, MLs, (optional) DK totals, simple model %, buy/sell edges.

Model_Detail:
Starters & hands, expected IP, SP/BP ERAs, wRC+ vs hand, park factor, expected runs (home/away), Pythagorean p_home/p_away.

Blended:
Blended p_home/p_away if enabled.

Performance (optional):
Summary ROI for Home, Away, Favorites, Underdogs (1u flat), model Brier scores, and per-game ledger.

Scores Helper (optional)
pipenv run python scores_on_date.py --date 2025-08-31 --csv outputs/scores_2025-08-31.csv


You can merge by game_pk to grade lines or compute ROI.

Config File (optional)

See configs/example_config.yaml for tunable knobs (league averages, park mode, blend weight, performance tab, file paths). CLI flags always override config values.

Troubleshooting

ModuleNotFoundError: XlsxWriter
pipenv install XlsxWriter (or switch engine to openpyxl in the writer)

KeyError: 'some_column' not in index
Check your column list and make sure you actually add the field into the rows.append({...}) dict before building the DataFrame slice.

404 ... /people?personIds=...
Ensure you’re passing pitcher personIds, not gamePk. From schedule hydrate:
hp_id = g["teams"]["home"]["probablePitcher"]["id"] (when present).

TBD pitchers
When probablePitcher is missing, fall back to team-average splits or carry forward previous starter IP assumptions.

Notes & Credits

Uses mlb-statsapi
 (public MLB Stats API wrapper).

Park factors, bullpen ERA, and wRC+ splits are provided by you (static dictionaries or config). Update periodically.

This repo does not provide betting advice. Use outputs for analysis only.

License

MIT — see LICENSE.


# 5) LICENSE (MIT template)
Create `LICENSE` with:

MIT License

Copyright (c) 2025 <Your Name>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
