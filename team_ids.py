import statsapi
import pandas as pd
from datetime import date

SEASON = date.today().year  # or hardcode, e.g. 2025

def main():
    payload = statsapi.get("teams", {"sportId": 1, "season": SEASON})
    teams = payload.get("teams", [])
    rows = []
    for t in teams:
        rows.append({
            "team_id": t["id"],
            "name": t.get("name"),
            "abbr": t.get("abbreviation"),
            "teamCode": t.get("teamCode"),
            "league": (t.get("league") or {}).get("name"),
            "division": (t.get("division") or {}).get("name"),
        })

    df = pd.DataFrame(rows).sort_values("name").reset_index(drop=True)
    print("\n=== MLB Teams & IDs ===")
    print(df.to_string(index=False))

    # Uncomment to save a CSV
    # df.to_csv(f"mlb_team_ids_{SEASON}.csv", index=False)

    # ---- Dict templates (keyed by team_id) ----
    ids_and_names = [(r["team_id"], r["name"]) for r in rows]

    def emit_template(title):
        print(f"\n# {title}")
        print(f"{title.upper().replace(' ', '_')} = {{")
        for tid, name in sorted(ids_and_names, key=lambda x: x[1]):
            print(f"    {tid}: None,  # {name}")
        print("}")

    emit_template("Bullpen ERA")        # BULLPEN_ERA
    emit_template("Ballpark Factor")    # BALLPARK_FACTOR
    emit_template("wRC+ vs L")          # WRC__VS_L
    emit_template("wRC+ vs R")          # WRC__VS_R

    print("\n# Example DraftKings lines are game-specific; keep those keyed by game_pk, not team_id.")
    print("# DK_LINES = { 776549: {'away_ml': +115, 'home_ml': -135}, ... }")

if __name__ == "__main__":
    main()
