import statsapi
import pandas as pd
from datetime import date

# --- Pick your day ---
day = date.today().isoformat()          # e.g., "2025-04-15"
season_year = date.today().year

# --- 1) Get raw schedule (with probable pitchers) ---
resp = statsapi.get("schedule", {
    "sportId": 1,
    "date": day,
    "hydrate": "probablePitcher(note)"
})

games = []
pitcher_ids = set()

for d in resp.get("dates", []):
    for g in d.get("games", []):
        home = g["teams"]["home"]
        away = g["teams"]["away"]

        home_team = home["team"]["name"]
        away_team = away["team"]["name"]

        home_p = home.get("probablePitcher") or {}
        away_p = away.get("probablePitcher") or {}

        if "id" in home_p: pitcher_ids.add(str(home_p["id"]))
        if "id" in away_p: pitcher_ids.add(str(away_p["id"]))

        games.append({
            "game_pk": g["gamePk"],
            "date": g["gameDate"],
            "away_team": away_team,
            "home_team": home_team,
            "away_pitcher": away_p.get("fullName") or "TBD",
            "away_pitcher_id": away_p.get("id"),
            "home_pitcher": home_p.get("fullName") or "TBD",
            "home_pitcher_id": home_p.get("id"),
        })

# --- 2) Hydrate pitcher season stats (ERA, GS, IP) + hand ---
def extract_season_pitching_line(p):
    """Return dict with era, gamesStarted, inningsPitched from season pitching stats if present."""
    era = gs = ip = None
    for block in p.get("stats", []):
        # we just need season pitching; names vary slightly, so check loosely
        if block.get("group", {}).get("displayName", "").lower() == "pitching" and \
           block.get("type",  {}).get("displayName", "").lower() in ("season", "by year", "year by year"):
            splits = block.get("splits", [])
            if splits:
                stat = splits[0].get("stat", {})
                era = stat.get("era")
                gs  = stat.get("gamesStarted")
                ip  = stat.get("inningsPitched")
                break
    return {"era": era, "gs": gs, "ip": ip}

id_to_stats = {}   # pid -> {era, gs, ip, hand}

if pitcher_ids:
    people = statsapi.get("people", {
        "personIds": ",".join(pitcher_ids),
        "hydrate": "stats(group=[pitching],type=[season])"
    })
    for p in people.get("people", []):
        pid   = p["id"]
        hand  = p.get("pitchHand", {}).get("code")  # "R" or "L"
        line  = extract_season_pitching_line(p)
        line["hand"] = hand
        id_to_stats[pid] = line

# --- 3) Build DataFrame ---
rows = []
for g in games:
    a_id = g["away_pitcher_id"]
    h_id = g["home_pitcher_id"]
    a = id_to_stats.get(a_id, {})
    h = id_to_stats.get(h_id, {})

    rows.append({
        "date": g["date"],
        "game_pk": g["game_pk"],
        "away_team": g["away_team"],
        "home_team": g["home_team"],

        "away_pitcher": g["away_pitcher"],
        "away_hand": a.get("hand"),
        "away_era": a.get("era"),
        "away_gs": a.get("gs"),
        "away_ip": a.get("ip"),

        "home_pitcher": g["home_pitcher"],
        "home_hand": h.get("hand"),
        "home_era": h.get("era"),
        "home_gs": h.get("gs"),
        "home_ip": h.get("ip"),
    })

df = pd.DataFrame(rows)
print(df)
# df.to_csv("mlb_starters_today.csv", index=False)  # optional save
