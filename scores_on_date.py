# scores_on_date.py
import statsapi, pandas as pd, argparse
from datetime import datetime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")

def fetch_scores(date_str: str, finals_only=False):
    resp = statsapi.get("schedule", {"sportId": 1, "date": date_str, "hydrate": "linescore"})
    rows = []
    for d in resp.get("dates", []):
        for g in d.get("games", []):
            status = g["status"]["detailedState"]
            if finals_only and "Final" not in status:
                continue
            rows.append({
                "game_pk": g["gamePk"],
                "away": g["teams"]["away"]["team"]["name"],
                "home": g["teams"]["home"]["team"]["name"],
                "away_score": g["teams"]["away"].get("score"),
                "home_score": g["teams"]["home"].get("score"),
                "status": status,
                "start_et": datetime.fromisoformat(g["gameDate"].replace("Z","")).astimezone(ET).strftime("%Y-%m-%d %I:%M %p ET"),
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--finals-only", action="store_true")
    p.add_argument("--csv", default=None, help="Optional output CSV path")
    args = p.parse_args()

    df = fetch_scores(args.date, finals_only=args.finals_only).sort_values(["start_et","home"], ignore_index=True)
    print(df.to_string(index=False))
    if args.csv:
        df.to_csv(args.csv, index=False)
        print(f"\nSaved → {args.csv}")
