# save as: make_dk_template.py
import argparse
import pandas as pd
import statsapi
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo  # Python 3.9+

ET = ZoneInfo("America/New_York")

def fetch_schedule_rows(date_str: str):
    rows = []
    resp = statsapi.get("schedule", {"sportId": 1, "date": date_str})
    for d in resp.get("dates", []):
        for g in d.get("games", []):
            away_team = g["teams"]["away"]["team"]["name"]
            home_team = g["teams"]["home"]["team"]["name"]
            game_pk   = g["gamePk"]  # unique MLB game id

            # Convert MLB UTC gameDate -> ET "HH:MM"
            # gameDate example: "2025-08-29T23:07:00Z"
            dt_utc = datetime.fromisoformat(g["gameDate"].replace("Z", "+00:00"))
            dt_et  = dt_utc.astimezone(ET)
            game_time_et = dt_et.strftime("%H:%M")

            rows.append({
                "away_team": away_team,
                "home_team": home_team,
                "game_id": game_pk,          # your requested id column
                "game_time_et": game_time_et,# NEW: start time in ET
                "away_ml": "",               # fill in manually
                "home_ml": "",
                "total": "",
                "O": "",
                "U": "",
                "game_pk": game_pk,          # optional helper for other scripts
            })
    # Sort by time then home team for readability
    rows.sort(key=lambda r: (r["game_time_et"], r["home_team"]))
    return rows

def main():
    parser = argparse.ArgumentParser(description="Create DK input template for an MLB date")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD (default: today)")
    parser.add_argument("--out", default=None, help="Output CSV path (default: dk_template_<date>.csv)")
    args = parser.parse_args()

    out_path = args.out or f"dk_template_{args.date}.csv"
    rows = fetch_schedule_rows(args.date)
    if not rows:
        print(f"No MLB games found for {args.date}.")
        return

    df = pd.DataFrame(rows, columns=[
        "away_team","home_team","game_id","game_time_et","away_ml","home_ml","total","O","U","game_pk"
    ])
    # If you ONLY want the 8 original columns (plus time) and NOT game_pk, uncomment:
    # df = df[["away_team","home_team","game_id","game_time_et","away_ml","home_ml","total","O","U"]]

    df.to_csv(out_path, index=False)
    print(f"Saved {len(df)} rows to {out_path}")

if __name__ == "__main__":
    main()
#python big_kahuna.py --date 2025-09-03 --dk-csv dk_template_2025-09-03_entered.csv --blend-w 0.7 --auto-blend --export-xlsx "C:\Users\public\big_kahuna_2025-09-03.xlsx"
