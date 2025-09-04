import pandas as pd
import statsapi

SEASON = 2025
TEAM_NAMES = [
    "Baltimore Orioles","Red Sox","Rays","Jays","Yankees",
    "White Sox","Guardians","Tigers","Royals","Twins",
    "Astros","Angels","Rangers","Athletics","Mariners",
    "Braves","Marlins","Mets","Nationals","Phillies",
    "Brewers","Cardinals","Cubs","Pirates","Reds",
    "Diamondbacks","Dodgers","Giants","Padres","Rockies"
]

def get_team_id(name: str) -> int:
    teams = statsapi.lookup_team(name)
    for t in teams:
        if t.get("sport", {}).get("id") == 1:  # MLB
            return t["id"]
    return teams[0]["id"]

def is_regular_final(g: dict) -> bool:
    return (g.get("game_type") == "R") and ("final" in (g.get("status","").lower()))

def compute_home_away(team_name: str, season: int):
    team_id = get_team_id(team_name)
    games = statsapi.schedule(
        team=team_id,
        start_date=f"{season}-02-01",
        end_date=f"{season}-12-31"
    )
    home_w = home_l = away_w = away_l = 0
    for g in games:
        if not is_regular_final(g):
            continue
        is_home = (g.get("home_id") == team_id)
        hs = int(g.get("home_score") or 0)
        as_ = int(g.get("away_score") or 0)
        won = (hs > as_) if is_home else (as_ > hs)

        if is_home:
            if won: home_w += 1
            else:   home_l += 1
        else:
            if won: away_w += 1
            else:   away_l += 1
    return home_w, home_l, away_w, away_l

def main():
    rows = []
    for team_name in TEAM_NAMES:
        hw, hl, aw, al = compute_home_away(team_name, SEASON)
        total_w, total_l = hw + aw, hl + al
        total_home = hw + hl
        total_road = aw + al

        home_win_pct = round(hw / total_home, 3) if total_home > 0 else None
        road_loss_pct = round(al / total_road, 3) if total_road > 0 else None

        rows.append({
            "Team": team_name,
            "Record": f"{total_w}-{total_l}",
            "Home_Wins": hw,
            "Home_Losses": hl,
            "Home_Win%": home_win_pct,
            "Road_Wins": aw,
            "Road_Losses": al,
            "Road_Loss%": road_loss_pct,
        })

    df = pd.DataFrame(rows, columns=[
        "Team","Record",
        "Home_Wins","Home_Losses","Home_Win%",
        "Road_Wins","Road_Losses","Road_Loss%"
    ])
    df = df.sort_values("Team", ignore_index=True)
    print(df)
    # df.to_csv(f"team_records_{SEASON}.csv", index=False)

if __name__ == "__main__":
    main()
