# big_kahuna.py
import argparse
import os
import math
import pandas as pd
import statsapi
from datetime import datetime, date
from zoneinfo import ZoneInfo  # Python 3.9+

# =========================
# Config / Static Inputs
# =========================
SEASON = 2025
TODAY = date.today().isoformat()
ET = ZoneInfo("America/New_York")

LEAGUE_RPG = 4.75   # average runs per team per game
LEAGUE_ERA = 4.48   # league average ERA
PYTH_EXP    = 1.83  # Bill James Pythag exponent
MLB_HOME_WIN_PCT = .55
MLB_ROAD_WIN_PCT = 1.0 - MLB_HOME_WIN_PCT


BALLPARK_FACTOR = {
    109: 1.03, 133: 1.09, 144: 1.00, 110: 1.01, 111: 1.04, 112: 0.96, 145: 0.98,
    113: 1.02, 114: 0.97, 115: 1.12, 116: 1.00, 117: 1.00, 118: 1.02, 108: 1.01,
    119: 1.02, 146: 1.01, 158: 0.97, 142: 1.02, 121: 0.98, 147: 1.00, 143: 1.01,
    134: 0.99, 135: 0.98, 137: 0.96, 136: 0.91, 138: 1.01, 139: 1.02, 140: 0.98,
    141: 1.00, 120: 1.01,
}

#BULLPEN_ERA = {
#    109: 4.79, 133: 4.89, 144: 4.07, 110: 4.69, 111: 3.40, 112: 3.80, 145: 3.99,
#    113: 3.90, 114: 3.61, 115: 5.10, 116: 3.97, 117: 3.78, 118: 3.72, 108: 4.84,
#    119: 4.19, 146: 4.06, 158: 3.79, 142: 4.19, 121: 3.95, 147: 4.32, 143: 4.29,
#    134: 4.11, 135: 2.87, 137: 3.31, 136: 3.82, 138: 3.65, 139: 3.82, 140: 3.61,
#    141: 3.88, 120: 5.66,
#}

BULLPEN_ERA = {
    133: 3.31, #ATH
    134: 5.29, #PIT
    135: 2.56, #SDP
    136: 4.95, #SEA
    137: 3.71, #SFG
    138: 4.15, #STL
    139: 3.66, #TBR
    140: 4.70, #TEX
    141: 5.11, #TOR
    142: 5.79, #MIN
    143: 4.28, #PHI
    144: 3.17, #ATL
    145: 5.53, #CHW
    146: 5.78, #MIA
    147: 4.87, #NYY
    158: 3.80, #MIL
    108: 3.83, #LAA
    109: 3.99, #ARI
    110: 3.81, #BAL
    111: 3.82, #BOS
    112: 4.41, #CHC
    113: 3.94, #CIN
    114: 3.95, #CLE
    115: 5.81, #COL
    116: 3.62, #DET
    117: 4.76, #HOU
    118: 3.46, #KCR
    119: 4.09, #LAD
    120: 4.89, #WSN
    121: 5.15, #NYM
}
WRC_PLUS_VS_L = {
    109: 1.24, #ARI
    133: 1.24, #ATH
    144: 1.11, #ATL
    110: 1.02, #BAL
    111: 0.98, #BOS
    112: 0.87, #CHC
    145: 1.10, #CHW
    113: 0.81, #CIN
    114: 0.72, #CLE
    115: 1.03, #COL
    116: 1.33, #DET
    117: 0.95, #HOU
    118: 0.92, #KCR
    108: 1.21, #LAA
    119: 0.99, #LAD
    146: 0.69, #MIA
    158: 1.25, #MIL
    142: 1.04, #MIN
    121: 1.37, #NYM
    147: 1.34, #NYY
    143: 1.01, #PHI
    134: 0.87, #PIT
    135: 1.07, #SDP
    137: 0.85, #SFG
    136: 0.99, #SEA
    138: 1.16, #STL
    139: 0.75, #TBR
    140: 1.07, #TEX
    141: 1.48, #TOR
    120: 0.59, #WSN
}

#WRC_PLUS_VS_L = {
#    109: 0.99, 133: 1.04, 144: 0.91, 110: 0.84, 111: 1.06, 112: 1.07, 145: 0.93,
#    113: 0.76, 114: 0.79, 115: 0.76, 116: 1.15, 117: 1.12, 118: 0.81, 108: 0.93,
#    119: 1.10, 146: 0.76, 158: 1.07, 142: 0.90, 121: 0.97, 147: 1.20, 143: 1.03,
#    134: 0.76, 135: 0.93, 137: 0.74, 136: 1.01, 138: 0.95, 139: 0.79, 140: 0.80,
#    141: 1.15, 120: 0.83,
#}
WRC_PLUS_VS_R = {
    109: 0.99, #ARI
    133: 1.05, #ATH
    144: 1.01, #ATL
    110: 0.89, #BAL
    111: 1.02, #BOS
    112: 0.86, #CHC
    145: 1.04, #CHW
    113: 0.66, #CIN
    114: 0.72, #CLE
    115: 0.85, #COL
    116: 0.98, #DET
    117: 0.93, #HOU
    118: 1.11, #KCR
    108: 0.75, #LAA
    119: 1.07, #LAD
    146: 1.06, #MIA
    158: 1.35, #MIL
    142: 0.92, #MIN
    121: 1.47, #NYM
    147: 1.20, #NYY
    143: 1.25, #PHI
    134: 1.03, #PIT
    135: 1.11, #SDP
    137: 1.29, #SFG
    136: 1.06, #SEA
    138: 0.75, #STL
    139: 1.05, #TBR
    140: 1.12, #TEX
    141: 1.31, #TOR
    120: 1.08, #WSN
}

#WRC_PLUS_VS_R = {
#    109: 1.16, 133: 1.04, 144: 1.07, 110: 1.03, 111: 1.03, 112: 1.10, 145: 0.86,
#   113: 0.98, 114: 0.89, 115: 0.78, 116: 1.03, 117: 0.97, 118: 0.93, 108: 0.98,
#    119: 1.14, 146: 1.03, 158: 1.07, 142: 0.99, 121: 1.17, 147: 1.15, 143: 1.09,
#    134: 0.84, 135: 1.04, 137: 1.02, 136: 1.12, 138: 1.01, 139: 1.05, 140: 0.97,
#    141: 1.12, 120: 0.99,
#}

# Initial DK lines (can be overridden by CSV or prompts)
DK_LINES = {
    776551: {'away_ml': +118, 'home_ml': -143, 'total': 9.0,  'O': +100, 'U': -121},
    776552: {'away_ml': +157, 'home_ml': -193, 'total': 9.0,  'O': -119, 'U': -102},
    776545: {'away_ml': -144, 'home_ml': +118, 'total': 9.0,  'O': -115, 'U': -105},
    776546: {'away_ml': +112, 'home_ml': -137, 'total': 7.5,  'O': -117, 'U': -103},
    776547: {'away_ml': -164, 'home_ml': +134, 'total': 7.5,  'O': -118, 'U': -103},
    776548: {'away_ml': +154, 'home_ml': -169, 'total': 7.5,  'O': -119, 'U': -102},
    776549: {'away_ml': -101, 'home_ml': -120, 'total': 8.0,  'O': -105, 'U': -115},
    776544: {'away_ml': -231, 'home_ml': +185, 'total': 9.0,  'O': -108, 'U': -111},
    776543: {'away_ml': +138, 'home_ml': -169, 'total': 9.0,  'O': -101, 'U': -120},
    776540: {'away_ml': +101, 'home_ml': -123, 'total': 9.0,  'O': -115, 'U': -105},
    776541: {'away_ml': -132, 'home_ml': +108, 'total': 8.5,  'O': -120, 'U': -101},
    776542: {'away_ml': -238, 'home_ml': +191, 'total': 11.0, 'O': -108, 'U': -113},
    776538: {'away_ml': +123, 'home_ml': -149, 'total': 10.0, 'O': -115, 'U': -105},
    776534: {'away_ml': +162, 'home_ml': -200, 'total': 8.5,  'O': -110, 'U': -110},
    776533: {'away_ml': +122, 'home_ml': -149, 'total': 7.5,  'O': -109, 'U': -112},
}

TEAM_NAMES = [
    "Baltimore Orioles","Red Sox","Rays","Jays","Yankees",
    "White Sox","Guardians","Tigers","Royals","Twins",
    "Astros","Angels","Rangers","Athletics","Mariners",
    "Braves","Marlins","Mets","Nationals","Phillies",
    "Brewers","Cardinals","Cubs","Pirates","Reds",
    "Diamondbacks","Dodgers","Giants","Padres","Rockies"
]

ALIAS_MAP = {
    "Toronto Blue Jays": "Jays", "Tampa Bay Rays": "Rays", "Boston Red Sox": "Red Sox",
    "New York Yankees": "Yankees", "Chicago White Sox": "White Sox", "Cleveland Guardians": "Guardians",
    "Detroit Tigers": "Tigers", "Kansas City Royals": "Royals", "Minnesota Twins": "Twins",
    "Houston Astros": "Astros", "Los Angeles Angels": "Angels", "Texas Rangers": "Rangers",
    "Oakland Athletics": "Athletics", "Seattle Mariners": "Mariners", "Atlanta Braves": "Braves",
    "Miami Marlins": "Marlins", "New York Mets": "Mets", "Washington Nationals": "Nationals",
    "Philadelphia Phillies": "Phillies", "Milwaukee Brewers": "Brewers", "St. Louis Cardinals": "Cardinals",
    "Chicago Cubs": "Cubs", "Pittsburgh Pirates": "Pirates", "Cincinnati Reds": "Reds",
    "Arizona Diamondbacks": "Diamondbacks", "Los Angeles Dodgers": "Dodgers",
    "San Francisco Giants": "Giants", "San Diego Padres": "Padres", "Colorado Rockies": "Rockies",
    "Baltimore Orioles": "Baltimore Orioles",
}

# =========================
# Helpers
# =========================
def get_team_id(name: str) -> int:
    teams = statsapi.lookup_team(name)
    for t in teams:
        if t.get("sport", {}).get("id") == 1:
            return t["id"]
    return teams[0]["id"]

def ip_str_to_outs(ip):
    if not ip:
        return 0
    whole, frac = (str(ip).split('.') + ['0'])[:2]
    try:
        return int(whole) * 3 + int(frac)  # frac in {0,1,2}
    except Exception:
        return 0

def expected_sp_ip(ip_str, gs):
    if not ip_str or not gs or gs == 0:
        return None
    outs = ip_str_to_outs(ip_str)
    return round((outs / 3.0) / gs, 2)

def american_to_implied_prob(odds):
    if odds is None:
        return None
    if odds > 0:
        return 100.0 / (odds + 100.0)
    elif odds < 0:
        return (-odds) / ((-odds) + 100.0)
    else:
        return None

def prob_to_american(p: float | None) -> int | None:
    if p is None or p <= 0 or p >= 1:
        return None
    # p < 0.5 => plus odds; p >= 0.5 => minus odds
    return round(100 * (1 - p) / p) if p < 0.5 else round(-100 * p / (1 - p))

def round_total_line(x: float | None) -> float | None:
    """
    Band rounding to whole/half using .25/.75 thresholds:
      <= .25 -> round down to .0
      .26-.74 -> round to .5
      >= .75 -> round up to next .0
    """
    if x is None:
        return None
    n = math.floor(x)
    frac = x - n
    if frac <= 0.25:
        return float(n)
    elif frac < 0.75:
        return n + 0.5
    else:
        return float(n + 1)

def build_team_meta(season=SEASON):
    meta = {}
    payload = statsapi.get("teams", {"sportId": 1, "season": season})
    for t in payload.get("teams", []):
        tid = t["id"]
        name = t.get("name")
        abbr = t.get("abbreviation")
        tname = t.get("teamName")
        sname = t.get("shortName")
        short = tname or abbr or sname or name
        meta[tid] = {"name": name, "abbr": abbr, "teamName": tname, "short": short}
    return meta

def build_team_metrics():
    def is_regular_final(g):
        return (g.get("game_type") == "R") and ("final" in (g.get("status","").lower()))
    def compute_home_away(team_name, season):
        team_id = get_team_id(team_name)
        games = statsapi.schedule(team=team_id,
                                  start_date=f"{season}-02-01",
                                  end_date=f"{season}-12-31")
        hw = hl = aw = al = 0
        for g in games:
            if not is_regular_final(g):
                continue
            is_home = (g.get("home_id") == team_id)
            hs = int(g.get("home_score") or 0); as_ = int(g.get("away_score") or 0)
            won = (hs > as_) if is_home else (as_ > hs)
            if is_home:
                hw += 1 if won else 0
                hl += 0 if won else 1
            else:
                aw += 1 if won else 0
                al += 0 if won else 1
        return hw, hl, aw, al

    metrics = {}
    for team in TEAM_NAMES:
        hw, hl, aw, al = compute_home_away(team, SEASON)
        th, tr = hw + hl, aw + al
        home_win = round(hw / th, 3) if th > 0 else None
        road_loss = round(al / tr, 3) if tr > 0 else None
        metrics[team] = {"Home_Win%": home_win, "Road_Loss%": road_loss}
    return metrics

def fetch_probable_pitchers_people(prob_pitcher_ids):
    """
    pid -> {'hand': 'R'/'L', 'ip': '123.2', 'gs': 25, 'era': float}
    """
    result = {}
    if not prob_pitcher_ids:
        return result
    ids = [str(i) for i in prob_pitcher_ids]
    BATCH = 50
    for i in range(0, len(ids), BATCH):
        chunk = ids[i:i+BATCH]
        people = statsapi.get("people", {
            "personIds": ",".join(chunk),
            "hydrate": "stats(group=[pitching],type=[season])"
        })
        for p in people.get("people", []):
            pid = p["id"]
            hand = (p.get("pitchHand") or {}).get("code")
            ip = gs = era = None
            for block in p.get("stats", []):
                if (block.get("group", {}).get("displayName", "").lower() == "pitching" and
                    block.get("type",  {}).get("displayName", "").lower() == "season"):
                    splits = block.get("splits", [])
                    if splits:
                        stat = splits[0].get("stat", {}) or {}
                        ip  = stat.get("inningsPitched")
                        gs  = stat.get("gamesStarted")
                        try:
                            era = float(stat.get("era")) if stat.get("era") is not None else None
                        except Exception:
                            era = None
                    break
            result[pid] = {"hand": hand, "ip": ip, "gs": gs, "era": era}
    return result

def todays_schedule(date_str, team_meta):
    raw = statsapi.get("schedule", {
        "sportId": 1, "date": date_str, "hydrate": "probablePitcher(note)"
    })
    flat = statsapi.schedule(start_date=date_str, end_date=date_str)
    pk_to_probables = {
        int(f["game_id"]): {
            "home": f.get("home_probable_pitcher"),
            "away": f.get("away_probable_pitcher"),
        }
        for f in flat if "game_id" in f
    }

    games, prob_ids = [], set()
    for d in raw.get("dates", []):
        for g in d.get("games", []):
            home_team = g["teams"]["home"]["team"]
            away_team = g["teams"]["away"]["team"]
            hid, aid = home_team["id"], away_team["id"]

            home_p_obj = g["teams"]["home"].get("probablePitcher") or {}
            away_p_obj = g["teams"]["away"].get("probablePitcher") or {}
            home_p = home_p_obj.get("fullName")
            away_p = away_p_obj.get("fullName")
            home_pid = home_p_obj.get("id")
            away_pid = away_p_obj.get("id")

            if not home_p or not away_p:
                pks = pk_to_probables.get(g["gamePk"], {})
                home_p = home_p or pks.get("home") or "TBD"
                away_p = away_p or pks.get("away") or "TBD"

            if home_pid: prob_ids.add(home_pid)
            if away_pid: prob_ids.add(away_pid)

            dt_utc = datetime.fromisoformat(g["gameDate"].replace("Z","+00:00"))
            dt_et  = dt_utc.astimezone(ET)
            game_date = dt_et.strftime("%Y-%m-%d")
            game_time = dt_et.strftime("%H:%M")

            games.append({
                "Game_Date": game_date,
                "Game_Time_ET": game_time,
                "game_pk": g["gamePk"],

                "home_team": home_team["name"], "home_team_id": hid,
                "away_team": away_team["name"], "away_team_id": aid,

                "home_team_short": team_meta.get(hid, {}).get("short") or home_team["name"],
                "away_team_short": team_meta.get(aid, {}).get("short") or away_team["name"],

                "home_pitcher": home_p, "home_pitcher_id": home_pid,
                "away_pitcher": away_p, "away_pitcher_id": away_pid,
            })

    return games, prob_ids

# ---------- DK CSV (smart) ----------
def _to_int_or_none(x):
    if pd.isna(x) or x == "" or x is None:
        return None
    try:
        return int(str(x).strip())
    except Exception:
        return None

def _to_float_or_none(x):
    if pd.isna(x) or x == "" or x is None:
        return None
    try:
        return float(str(x).strip())
    except Exception:
        return None

def _norm_team(s: str | None) -> str:
    return (s or "").strip().lower()

def _norm_time(s: str | None) -> str:
    s = (s or "").strip()
    return s[:5] if len(s) >= 5 else s

def load_dk_csv_smart(path: str, games: list[dict]) -> dict[int, dict]:
    """
    Load DK numbers from CSV. Prefer direct match on game_pk/game_id.
    If missing, fuzzy match by (away_team, home_team, game_time_et) from CSV
    against today's schedule (away_team/home_team + Game_Time_ET).
    Returns: {game_pk: {"away_ml": int|None, "home_ml": int|None, "total": float|None, "O": int|None, "U": int|None}}
    """
    df = pd.read_csv(path)

    sched_index: dict[tuple[str, str, str], int] = {}
    for g in games:
        key = (_norm_team(g.get("away_team")),
               _norm_team(g.get("home_team")),
               _norm_time(g.get("Game_Time_ET")))
        sched_index[key] = g["game_pk"]

    out: dict[int, dict] = {}
    for _, r in df.iterrows():
        # direct id match
        pk = None
        for col in ("game_pk", "game_id"):
            if col in df.columns and pd.notna(r.get(col)):
                try:
                    pk = int(r.get(col))
                    break
                except Exception:
                    pk = None
        if pk is None:
            # fuzzy by teams + time
            away = _norm_team(r.get("away_team"))
            home = _norm_team(r.get("home_team"))
            t    = _norm_time(r.get("game_time_et") or r.get("game_time") or r.get("Game_Time_ET"))
            pk = sched_index.get((away, home, t))
        if pk is None:
            # skip unmatched rows quietly (could log here)
            continue

        out[pk] = {
            "away_ml": _to_int_or_none(r.get("away_ml")),
            "home_ml": _to_int_or_none(r.get("home_ml")),
            "total":   _to_float_or_none(r.get("total")),
            "O":       _to_int_or_none(r.get("O")),
            "U":       _to_int_or_none(r.get("U")),
        }
    return out

def prompt_missing_dk(games, dk_map: dict[int, dict]):
    """Prompt user for away/home ML for any games missing in dk_map."""
    print("\nEnter DraftKings ML (press Enter to skip a field):")
    for g in sorted(games, key=lambda x: (x["Game_Date"], x["Game_Time_ET"], x["home_team_short"])):
        pk = g["game_pk"]
        info = dk_map.get(pk, {})
        if info.get("away_ml") is not None and info.get("home_ml") is not None:
            continue
        print(f"  {g['Game_Date']} {g['Game_Time_ET']}  {g['away_team_short']} @ {g['home_team_short']}  (game_pk={pk})")
        try:
            a = input("    Away ML (e.g., +120 / -135): ").strip()
            h = input("    Home ML (e.g., +120 / -135): ").strip()
        except EOFError:
            a = h = ""
        if pk not in dk_map:
            dk_map[pk] = {}
        if a:
            try: dk_map[pk]["away_ml"] = int(a)
            except: pass
        if h:
            try: dk_map[pk]["home_ml"] = int(h)
            except: pass

# ---------- Blending helpers ----------
EPS = 1e-6

def _clip_prob(p):
    if p is None:
        return None
    return max(EPS, min(1.0 - EPS, float(p)))

def logit(p):
    p = _clip_prob(p)
    return None if p is None else math.log(p / (1.0 - p))

def inv_logit(z):
    if z is None:
        return None
    return 1.0 / (1.0 + math.exp(-z))

def blend_logit(p_pyth, p_simple, w):
    """Logit-space average: logit(p*) = w*logit(p_pyth) + (1-w)*logit(p_simple)."""
    if p_pyth is None and p_simple is None:
        return None
    if p_pyth is None:
        return p_simple
    if p_simple is None:
        return p_pyth
    z = w * logit(p_pyth) + (1.0 - w) * logit(p_simple)
    return inv_logit(z)

def fetch_scores(date_str: str, games, finals_only=True):
    """Attach scores/status to each scheduled game dict in-place."""
    resp = statsapi.get("schedule", {"sportId": 1, "date": date_str, "hydrate": "linescore"})
    pk_to_score = {}
    for d in resp.get("dates", []):
        for g in d.get("games", []):
            pk = g["gamePk"]
            status = g["status"]["detailedState"]
            if finals_only and "Final" not in status:
                pk_to_score[pk] = {"away_score": "TBD", "home_score": "TBD", "status": status}
            else:
                pk_to_score[pk] = {
                    "away_score": g["teams"]["away"].get("score"),
                    "home_score": g["teams"]["home"].get("score"),
                    "status": status,
                }

    # merge into your game dicts
    for g in games:
        s = pk_to_score.get(g["game_pk"], {})
        g.update(s)

# =========================
# Main
# =========================
def main():
    parser = argparse.ArgumentParser(description="MLB model: schedule + bets + modeled runs/odds + blended probs")
    parser.add_argument("--date", default=TODAY, help="YYYY-MM-DD (default: today)")
    parser.add_argument("--dk-csv", default=None, help="CSV with DK odds: game_pk,away_ml,home_ml[,total,O,U][,game_time_et]")
    parser.add_argument("--ask-dk", action="store_true", help="Prompt for any missing DK odds")
    parser.add_argument("--blend-w", type=float, default=0.7,
                        help="Weight for Pythag model in logit blend (0..1). Default 0.7")
    parser.add_argument("--auto-blend", action="store_true",
                        help="Auto-reduce weight if pitching info is shaky (e.g., TBD/low GS)")
    parser.add_argument(
        "--export-xlsx",
        default=None,
        help="Path to write an Excel workbook with 3 tabs (Schedule_Bets, Model_Detail, Blended)."
    )
    args = parser.parse_args()

    # Team info, schedule, pitcher stats
    team_meta    = build_team_meta()
    team_metrics = build_team_metrics()
    games, prob_ids = todays_schedule(args.date, team_meta)
    pid_info = fetch_probable_pitchers_people(prob_ids)

    # DK lines (CSV overrides -> prompt)
    dk_runtime: dict[int, dict] = {k: dict(v) for k, v in DK_LINES.items()}
    if args.dk_csv:
        dk_csv_map = load_dk_csv_smart(args.dk_csv, games)
        dk_runtime.update(dk_csv_map)
    if args.ask_dk:
        prompt_missing_dk(games, dk_runtime)

    fetch_scores(args.date, games)

    rows = []
    for g in games:
        hk = ALIAS_MAP.get(g["home_team"], g["home_team"])
        ak = ALIAS_MAP.get(g["away_team"], g["away_team"])
        hm = team_metrics.get(hk); am = team_metrics.get(ak)
        home_win_pct = hm["Home_Win%"] if hm else None
        away_road_loss_pct = am["Road_Loss%"] if am else None
        simple_model = (home_win_pct + away_road_loss_pct)/2 if (home_win_pct is not None and away_road_loss_pct is not None) else None
        home_to_mlb_factor = home_win_pct / MLB_HOME_WIN_PCT if (home_win_pct is not None and away_road_loss_pct is not None) else None
        road_to_mlb_factor = (1.0 - away_road_loss_pct)/ MLB_ROAD_WIN_PCT if (home_win_pct is not None and away_road_loss_pct is not None) else None

        # Probable pitcher details
        home_pid = g["home_pitcher_id"]; away_pid = g["away_pitcher_id"]
        home_hand = (pid_info.get(home_pid) or {}).get("hand")
        away_hand = (pid_info.get(away_pid) or {}).get("hand")
        home_ip = (pid_info.get(home_pid) or {}).get("ip");     home_gs = (pid_info.get(home_pid) or {}).get("gs")
        away_ip = (pid_info.get(away_pid) or {}).get("ip");     away_gs = (pid_info.get(away_pid) or {}).get("gs")
        home_sp_era = (pid_info.get(home_pid) or {}).get("era"); away_sp_era = (pid_info.get(away_pid) or {}).get("era")
        home_exp_ip = expected_sp_ip(home_ip, home_gs) or 5.5
        away_exp_ip = expected_sp_ip(away_ip, away_gs) or 5.5
        home_exp_ip = max(3.0, min(7.0, home_exp_ip))
        away_exp_ip = max(3.0, min(7.0, away_exp_ip))

        # Static team fields
        hid, aid = g["home_team_id"], g["away_team_id"]
        home_bp = BULLPEN_ERA.get(hid); away_bp = BULLPEN_ERA.get(aid)
        park    = BALLPARK_FACTOR.get(hid, 1.00)  # home park

        # Offense vs opponent SP hand
        def model_team_wrc(wrc_rhp, wrc_lhp, sp_handiness):
            """
            Returns (wRC+ vs starting pitcher hand, wRC+ vs bullpen mix).
            Falls back sensibly when data/hand is missing.
            """
            wr = 1.0 if wrc_rhp is None else float(wrc_rhp)
            wl = 1.0 if wrc_lhp is None else float(wrc_lhp)

            if sp_handiness == "R":
                wrc_vs_sp = wr
            elif sp_handiness == "L":
                wrc_vs_sp = wl
            else:
                # unknown/TBD → average the two
                wrc_vs_sp = (wr + wl) / 2.0

            # bullpen mix (tweakable): ~67% RHP, 33% LHP
            bp_rhp_ratio = 0.67
            wrc_vs_bp = wr * bp_rhp_ratio + wl * (1.0 - bp_rhp_ratio)
            return (wrc_vs_sp, wrc_vs_bp)

        home_wrc_vs_opp_sp, home_wrc_vs_opp_bp = model_team_wrc( WRC_PLUS_VS_R.get(hid),  WRC_PLUS_VS_L.get(hid), home_hand)
        away_wrc_vs_opp_sp, away_wrc_vs_opp_bp = model_team_wrc( WRC_PLUS_VS_R.get(aid),  WRC_PLUS_VS_L.get(aid), away_hand)

        def model_eras(sp_era, bp_era):
            return(sp_era, bp_era)
        home_sp_era, home_bp_era = model_eras(home_sp_era, home_bp)
        away_sp_era, away_bp_era = model_eras(away_sp_era, away_bp)

        def model_league_rpg():
            return LEAGUE_RPG
        league_rpg = model_league_rpg()

        def model_league_era():
            return LEAGUE_ERA
        league_era = model_league_era()



        def model_exp_runs(
            wrc_plus_sp, wrc_plus_bp,
            opp_sp_era, opp_bp_era,
            exp_ip,
            league_rpg, league_era,
            park
        ):
            # required inputs present?
            required = [wrc_plus_sp, wrc_plus_bp, opp_sp_era, opp_bp_era, exp_ip, league_rpg, league_era, park]

            if any(x is None for x in required):
                return None
            # cast to floats and catch bad values
            try:
                wrc_plus_sp = float(wrc_plus_sp)
                wrc_plus_bp = float(wrc_plus_bp)
                opp_sp_era  = float(opp_sp_era)
                opp_bp_era  = float(opp_bp_era)
                exp_ip      = float(exp_ip)
                league_rpg  = float(league_rpg)
                league_era  = float(league_era)
                park        = float(park)
            except (TypeError, ValueError):
                return None
            if league_era == 0.0:
                return None

            # optional: cap wild ERAs to avoid extreme outputs
            opp_sp_era = max(2.0, min(opp_sp_era, 7.5))
            opp_bp_era = max(2.0, min(opp_bp_era, 7.5))

            # innings split with sane bounds
            exp_ip = max(0.0, min(9.0, exp_ip))
            bp_ip  = max(0.0, 9.0 - exp_ip)

            # per-team park factor
            pf_team = math.sqrt(park)

            # exposure in ERA*IP/9 scaled by wRC+ vs that staff component
            sp_term = wrc_plus_sp * (exp_ip * opp_sp_era / 9.0)
            bp_term = wrc_plus_bp * (bp_ip  * opp_bp_era / 9.0)
            exposure_era = sp_term + bp_term

            # map ERA exposure to runs
            runs_per_era = league_rpg / league_era
            return round(exposure_era * runs_per_era * pf_team, 2)

        exp_runs_away = model_exp_runs(away_wrc_vs_opp_sp, away_wrc_vs_opp_bp, home_sp_era, home_bp_era, home_exp_ip,league_rpg, league_era, park)
        exp_runs_home = model_exp_runs(home_wrc_vs_opp_sp, home_wrc_vs_opp_bp, away_sp_era, away_bp_era, away_exp_ip, league_rpg, league_era, park)

        total_runs = round((exp_runs_away or 0) + (exp_runs_home or 0), 2) if (exp_runs_away is not None and exp_runs_home is not None) else None
        total_line = round_total_line(total_runs)


        # Combined pitching ERA the offenses face
        def combined_era(sp_era, exp_ip, bp_era):
            if sp_era is None or bp_era is None:
                return LEAGUE_ERA
            bp_ip = max(0.0, 9.0 - exp_ip)
            return (sp_era * exp_ip + bp_era * bp_ip) / 9.0

        home_comb_def_era = combined_era(home_sp_era, home_exp_ip, home_bp)  # faced by AWAY offense
        away_comb_def_era = combined_era(away_sp_era, away_exp_ip, away_bp)  # faced by HOME offense


        # Pythagorean win probabilities -> model ML
        def pyth(p_runs, o_runs):
            if p_runs is None or o_runs is None or (p_runs == 0 and o_runs == 0):
                return None
            a = p_runs ** PYTH_EXP
            b = o_runs ** PYTH_EXP
            return a / (a + b)

        p_home = pyth(exp_runs_home, exp_runs_away)
        p_away = (1.0 - p_home) if p_home is not None else None
        ml_home = prob_to_american(p_home)
        ml_away = prob_to_american(p_away)

        # DK lines
        dk = dk_runtime.get(g["game_pk"], {})
        away_ml_dk = dk.get("away_ml"); home_ml_dk = dk.get("home_ml")
        dk_total = dk.get("total")
        dk_O = dk.get("O")
        dk_U = dk.get("U")

        # Simple-model edges (percentage points vs DK implied)
        p_home_imp = american_to_implied_prob(home_ml_dk)
        p_away_imp = american_to_implied_prob(away_ml_dk)
        simple_model_pct = round(simple_model * 100.0, 1) if simple_model is not None else None
        home_edge_pp = None; away_edge_pp = None
        if simple_model is not None and p_home_imp is not None:
            dd = (simple_model - p_home_imp) * 100.0
            home_edge_pp = round(dd, 1) if dd > 3.0 else None
        if simple_model is not None and p_away_imp is not None:
            dd = ((1.0 - simple_model) - p_away_imp) * 100.0
            away_edge_pp = round(dd, 1) if dd > 3.0 else None

        # Run-diff indicator
        run_diff = (abs(exp_runs_home - exp_runs_away) if (exp_runs_home is not None and exp_runs_away is not None) else None)
        gap_ge_2 = (run_diff is not None and run_diff >= 2.0)

        # --- Logit blend of pyth vs simple model ---
        p_simple = simple_model  # already a probability (0..1) or None
        w = args.blend_w
        if args.auto_blend:
            shaky_pitching = (
                (g["home_pitcher"] == "TBD" or g["away_pitcher"] == "TBD") or
                (home_sp_era is None) or (away_sp_era is None) or
                (home_gs in (None, 0)) or (away_gs in (None, 0))
            )
            if shaky_pitching:
                w = min(w, 0.5)

        p_home_blend = blend_logit(p_home, p_simple, w)
        p_away_blend = (1.0 - p_home_blend) if p_home_blend is not None else None
        ml_home_blend = prob_to_american(p_home_blend)
        ml_away_blend = prob_to_american(p_away_blend)

        # edges vs DK using blended prob
        home_edge_blend_pp = away_edge_blend_pp = None
        if p_home_blend is not None and p_home_imp is not None:
            home_edge_blend_pp = round((p_home_blend - p_home_imp) * 100.0, 1)
        if p_away_blend is not None and p_away_imp is not None:
            away_edge_blend_pp = round((p_away_blend - p_away_imp) * 100.0, 1)

                # --- Results evaluation ---
        model_prediction = ""
        ou_result = ""
        ou_prediction = ""
        model_ou_prediction = ""
        if g["away_score"] != "TBD" and g["home_score"] != "TBD":
            road_runs = int(g["away_score"])
            home_runs = int(g["home_score"])

            # --- Moneyline (model vs actual winner) ---
            actual_winner = "HOME" if home_runs > road_runs else "AWAY"
            model_winner = None
            if exp_runs_home is not None and exp_runs_away is not None:
                model_winner = "HOME" if exp_runs_home > exp_runs_away else "AWAY"
                model_picked_fave = False
                if model_winner == "HOME":
                    if home_ml_dk < 0 :
                        model_picked_fave = True
                else:
                    if away_ml_dk < 0 :
                        model_picked_fave = True



                expected_runs_total = exp_runs_home+exp_runs_away
                total_scored = road_runs + home_runs
                if expected_runs_total < dk_total :
                    model_ou_prediction = "UNDER"
                elif expected_runs_total > dk_total:
                    model_ou_prediction = "OVER"
                else:
                    model_ou_prediction = "PUSH"

                if total_scored < dk_total :
                    ou_result = "UNDER"
                elif total_scored > dk_total:
                    ou_result = "OVER"
                else:
                    ou_result = "PUSH"

                if model_ou_prediction != ou_result :
                    ou_prediction = "LOST"

                if model_winner:
                    if model_winner == actual_winner:
                        model_prediction = "WON"
                    else:
                        model_prediction = "LOST"


            print(f"        Final Score: {road_runs}-{home_runs} (Actual Winner: {actual_winner})")
            print(f"        ou_result:{ou_result}")
            print(f"        total_scored:{total_scored}")

            if model_winner:
                print(f"        Model Winner: {model_winner} → {model_prediction}")
            if total_line is not None:
                print(f"        Model Total Line: {total_line}, Actual Total: {total_scored} → {ou_result}")
            if dk_total is not None:
                print(f"        DK Total: {dk_total}, OU Prediction: {ou_prediction}")



        rows.append({
            "Game_Date": g["Game_Date"], "Game_Time_ET": g["Game_Time_ET"], "game_pk": g["game_pk"],
            "away_team_short": g["away_team_short"], "home_team_short": g["home_team_short"],
            "away_team_id": aid, "home_team_id": hid,
            "away_team": g["away_team"], "home_team": g["home_team"],

            "away_pitcher": g["away_pitcher"], "home_pitcher": g["home_pitcher"],
            "away_pitcher_hand": away_hand, "home_pitcher_hand": home_hand,
            "away_SP_IP": away_ip, "home_SP_IP": home_ip,
            "away_SP_GS": away_gs, "home_SP_GS": home_gs,
            "away_SP_ExpIP": away_exp_ip, "home_SP_ExpIP": home_exp_ip,
            "away_SP_ERA": away_sp_era, "home_SP_ERA": home_sp_era,

            "away_bp_era": away_bp, "home_bp_era": home_bp,
            "home_park_factor": park,

            "away_wrc_vs_oppSP": away_wrc_vs_opp_sp, "home_wrc_vs_oppSP": home_wrc_vs_opp_sp,

            "Home_Win%": home_win_pct, "Away_Road_Loss%": away_road_loss_pct, "simple_model": simple_model,

            # DK odds (Table 1)
            "away_ml": away_ml_dk, "home_ml": home_ml_dk,
            "dk_total": dk_total, "dk_O": dk_O, "dk_U": dk_U,

            # Modeling outputs:
            "exp_runs_away": exp_runs_away, "exp_runs_home": exp_runs_home,
            "total_runs": total_runs, "total_line": total_line,
            "p_home": p_home, "p_away": p_away,
            "ml_home": ml_home, "ml_away": ml_away,

            # defenses each offense faces:
            "away_combined_def_era": home_comb_def_era,
            "home_combined_def_era": away_comb_def_era,

            # Simple-model bet edges
            "home_team_bet_pp": home_edge_pp, "away_team_bet_pp": away_edge_pp,
            "simple_model_pct": simple_model_pct,

            # Run gap indicator
            "run_diff": run_diff, "gap_ge_2": gap_ge_2,

            # Blended outputs
            "p_home_blend": p_home_blend, "p_away_blend": p_away_blend,
            "ml_home_blend": ml_home_blend, "ml_away_blend": ml_away_blend,
            "home_edge_blend_pp": home_edge_blend_pp, "away_edge_blend_pp": away_edge_blend_pp,

            #Results
            "model_game_prediction" : model_prediction,
            "o/u prediction": ou_prediction, "fave_picked" : model_picked_fave,
            "away_score": g.get("away_score"),
            "home_score": g.get("home_score"),
       })

    df = pd.DataFrame(rows)

    # -------- Table 1: Schedule + bets --------
    df_sched = df[[
        "Game_Date","Game_Time_ET",
        "away_team_short","home_team_short",
        "away_ml","home_ml","dk_total","dk_O","dk_U",
        "simple_model_pct",
        "home_team_bet_pp","away_team_bet_pp",
    ]].sort_values(["Game_Date","Game_Time_ET","home_team_short"], ignore_index=True)

    print("\n=== SCHEDULE & BETS ===")
    print(df_sched.to_string(index=False, na_rep=""))

    # -------- Table 2: Pitching + modeled runs/odds (order as requested) --------
    df_details = df[[
        "Game_Date","Game_Time_ET",
        "away_team_short","home_team_short",
        "exp_runs_away","exp_runs_home","total_runs",
        "p_home","p_away","ml_home","ml_away",
        "total_line","run_diff","gap_ge_2",
        "away_pitcher","home_pitcher",
        "away_pitcher_hand","home_pitcher_hand",
        "away_SP_ExpIP","home_SP_ExpIP",
        "away_SP_ERA","home_SP_ERA",
        "away_bp_era","home_bp_era",
        "home_park_factor",
        "away_wrc_vs_oppSP","home_wrc_vs_oppSP",
        "away_combined_def_era","home_combined_def_era",
    ]].sort_values(["Game_Date","Game_Time_ET","home_team_short"], ignore_index=True)

    print("\n=== PITCHING • EXPECTED RUNS • ODDS ===")
    print(df_details.to_string(index=False, na_rep=""))

    # -------- Table 3: Blended probs & model MLs --------
    df_blend = df[[
        "Game_Date","Game_Time_ET",
        "away_team_short","home_team_short",
        "simple_model_pct",           # simple model in %
        "p_home","p_away",            # pythag probs (0..1)
        "p_home_blend","p_away_blend",
        "ml_home_blend","ml_away_blend",
        "home_ml","away_ml",
        "home_edge_blend_pp","away_edge_blend_pp",
    ]].copy()

    # pretty formatting for display
    def _fmt_pct(p):
        return "" if pd.isna(p) else f"{p:.1f}"

    df_blend["simple_model_pct"] = df_blend["simple_model_pct"].map(_fmt_pct)
    for c in ["p_home","p_away","p_home_blend","p_away_blend"]:
        df_blend[c] = df_blend[c].map(lambda x: "" if pd.isna(x) else f"{x*100:.1f}%")

    df_blend = df_blend.sort_values(["Game_Date","Game_Time_ET","home_team_short"], ignore_index=True)

    print("\n=== BLENDED PROBABILITIES (LOGIT) ===")
    print(df_blend.to_string(index=False, na_rep=""))

    # -------- Results --------
    df_results = df[[
        "Game_Date","Game_Time_ET",
        "away_team_short","home_team_short",
        "exp_runs_away","exp_runs_home","total_runs",
        "p_home","p_away","ml_home","home_ml","away_ml","model_picked_fave",
        "model_game_prediction","o/u prediction",
    ]].copy()
    ml_roi = 0.0
    for idx, row in df_results.iterrows():
        ml_roi_val = 0.0
        if row["model_game_prediction"] == "WON":
            if row["model_picked_fave"] :
                if row["home_ml"] < 0 :
                    ml_roi_val = -row["home_ml"]/(100.0-row["home_ml"])
                else :
                    ml_roi_val = -row["away_ml"]/(100.0-row["away_ml"])
            else:
                if row["home_ml"] < 0 :
                    ml_roi_val = row["away_ml"]/100.0
                else :
                    ml_roi_val = row["home_ml"]/100.0
        else:
            if row["model_picked_fave"] :
                if row["home_ml"] < 0 :
                    ml_roi_val = row["home_ml"]/100.0
                else :
                    ml_roi_val = row["away_ml"]/100.0
            else:
                ml_roi_val = -1
        ml_roi += ml_roi_val
        print(f"\n[roi_val_used]: {ml_roi_val}")
        print(f"\n[current ROI]: {ml_roi}")



    # Actual scores
    df_results["actual_away_score"] = df["away_score"]
    df_results["actual_home_score"] = df["home_score"]

    # Actual winner
    def _winner(row):
        if pd.isna(row["actual_home_score"]) or pd.isna(row["actual_away_score"]):
            return ""
        if row["actual_home_score"] > row["actual_away_score"]:
            return "HOME"
        elif row["actual_home_score"] < row["actual_away_score"]:
            return "AWAY"
        else:
            return "TIE"
    df_results["actual_winner"] = df_results.apply(_winner, axis=1)

    # Model winner
    def _model_winner(row):
        if pd.isna(row["exp_runs_home"]) or pd.isna(row["exp_runs_away"]):
            return ""
        if row["exp_runs_home"] > row["exp_runs_away"]:
            return "HOME"
        elif row["exp_runs_home"] < row["exp_runs_away"]:
            return "AWAY"
        else:
            return "TIE"
    df_results["model_winner"] = df_results.apply(_model_winner, axis=1)

    # O/U correctness
    def _ou_correct(row):
        if not row["o/u prediction"] or pd.isna(row["actual_home_score"]) or pd.isna(row["actual_away_score"]):
            return ""
        total_scored = row["actual_home_score"] + row["actual_away_score"]
        if pd.isna(row["total_runs"]):
            return ""
        if total_scored < row["total_runs"]:
            actual_ou = "UNDER"
        elif total_scored > row["total_runs"]:
            actual_ou = "OVER"
        else:
            actual_ou = "PUSH"

        if row["o/u prediction"] == "PUSH" and actual_ou == "PUSH":
            return "PUSH"
        elif row["o/u prediction"] == "WON":
            return "WON"
        elif row["o/u prediction"] == "LOST":
            return "LOST"
        else:
            return ""
    df_results["o/u_prediction_correct"] = df_results.apply(_ou_correct, axis=1)

    # --- Accuracy summary ---
    ml_total = df_results["model_game_prediction"].isin(["WON", "LOST"]).sum()
    ml_correct = (df_results["model_game_prediction"] == "WON").sum()
    ml_acc = round(ml_correct / ml_total * 100, 1) if ml_total > 0 else None

    ou_total = df_results["o/u_prediction_correct"].isin(["WON", "LOST"]).sum()
    ou_correct = (df_results["o/u_prediction_correct"] == "WON").sum()
    ou_acc = round(ou_correct / ou_total * 100, 1) if ou_total > 0 else None

    summary_row = {
        "Game_Date": "SUMMARY",
        "Game_Time_ET": "",
        "away_team_short": "",
        "home_team_short": "",
        "exp_runs_away": "",
        "exp_runs_home": "",
        "total_runs": "",
        "p_home": "",
        "p_away": "",
        "ml_home": "",
        "model_game_prediction": f"ML Acc: {ml_acc}%" if ml_acc is not None else "",
        "o/u prediction": f"OU Acc: {ou_acc}%" if ou_acc is not None else "",
        "actual_away_score": "",
        "actual_home_score": "",
        "actual_winner": "",
        "model_winner": "",
        "o/u_prediction_correct": "",
    }

    df_results = pd.concat([df_results, pd.DataFrame([summary_row])], ignore_index=True)

    # Clean up formatting
    df_results = df_results.sort_values(
        ["Game_Date","Game_Time_ET","home_team_short"],
        ignore_index=True
    )

    print("\n=== Results ===")
    print(df_results.to_string(index=False, na_rep=""))
    if ml_acc is not None:
        print(f"\n[SUMMARY] Moneyline Accuracy: {ml_acc}% ({ml_correct}/{ml_total})")
    if ou_acc is not None:
        print(f"[SUMMARY] O/U Accuracy: {ou_acc}% ({ou_correct}/{ou_total})")
   # -------- Export all tables to one Excel (optional) --------
    if args.export_xlsx:
        out_path = args.export_xlsx
        # create parent folder if needed
        folder = os.path.dirname(out_path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        with pd.ExcelWriter(out_path, engine="xlsxwriter") as xl:
            df_sched.to_excel(xl, sheet_name="Schedule_Bets", index=False)
            df_details.to_excel(xl, sheet_name="Model_Detail", index=False)
            df_blend.to_excel(xl, sheet_name="Blended", index=False)
            df_results.to_excel(xl, sheet_name="Results", index=False)
        print(f"\nSaved Excel workbook → {out_path}")
   # -------- Optional exports --------
    # with pd.ExcelWriter(f"games_{args.date}.xlsx", engine="xlsxwriter") as xl:
    #     df_sched.to_excel(xl, sheet_name="Schedule_Bets", index=False)
    #     df_details.to_excel(xl, sheet_name="Model_Detail", index=False)
    #     df_blend.to_excel(xl, sheet_name="Blended", index=False)

    # Save combined DK set back out (merged CSV + prompts + built-ins)
    dk_out = []
    for g in games:
        pk = g["game_pk"];
        d = dk_runtime.get(pk, {})
        dk_out.append({"game_pk": pk, "away_ml": d.get("away_ml"), "home_ml": d.get("home_ml"),
                       "total": d.get("total"), "O": d.get("O"), "U": d.get("U")})
    pd.DataFrame(dk_out).to_csv(f"dk_lines_{args.date}.csv", index=False)


if __name__ == "__main__":
    main()
