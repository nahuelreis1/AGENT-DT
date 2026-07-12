"""Convert raw API-Football v3 data for Argentina vs Switzerland (fixture 1582681)
into mock data files organized by 7 momentos (0=pre, 1=15, 2=30, 3=ht, 4=60, 5=75, 6=ft).

Reads from: live_data/
Writes to:  mock_data_arg_sui/

Momento mapping:
  0 (pre) — NS status, no events, no stats, predictions + h2h + injuries
  1 (15')  — events <= 15', 1H stats (approx), final player stats (approx)
  2 (30')  — events <= 30', 1H stats (approx), final player stats (approx)
  3 (ht)   — events <= 45', 1H stats (EXACT), final player stats (approx)
  4 (60')  — events <= 60', 2H stats (approx), final player stats (approx)
  5 (75')  — events <= 75', 2H stats (approx), final player stats (approx)
  6 (ft)   — all events, full stats (EXACT), final player stats (EXACT)
"""
import json
import os
from pathlib import Path

LIVE_DATA = Path(__file__).parent / "live_data"
OUT_DIR = Path(__file__).parent / "mock_data_arg_sui"

# ─── helpers ──────────────────────────────────────────────────────────────

def load_json(name: str) -> dict:
    """Load a JSON file from live_data/, handling BOM."""
    with open(LIVE_DATA / name, encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(name: str, data: dict) -> None:
    """Save a JSON file to OUT_DIR in the v3 envelope format."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / name, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def v3_envelope(response: list) -> dict:
    """Wrap a response list in the standard v3 envelope."""
    return {
        "get": "",
        "parameters": {},
        "errors": [],
        "results": len(response),
        "paging": {"current": 1, "total": 1},
        "response": response,
    }


# ─── load raw API data ────────────────────────────────────────────────────

print("Loading raw API data...")
all_in_one = load_json("fixture_all_in_one.json")
fixture_data = all_in_one["response"][0]
all_events = fixture_data.get("events", [])
all_lineups = fixture_data.get("lineups", [])
all_statistics = fixture_data.get("statistics", [])
all_players = fixture_data.get("players", [])

stats_half = load_json("statistics_half.json")
stats_1h = stats_half["response"][0].get("statistics_1h", [])
stats_1h_away = stats_half["response"][1].get("statistics_1h", [])
stats_2h = stats_half["response"][0].get("statistics_2h", [])
stats_2h_away = stats_half["response"][1].get("statistics_2h", [])
stats_full = all_statistics[0].get("statistics", [])
stats_full_away = all_statistics[1].get("statistics", [])

predictions_data = load_json("predictions.json")
injuries_data = load_json("injuries.json")
h2h_data = load_json("h2h.json")

print(f"  Events: {len(all_events)}")
print(f"  Lineups: {len(all_lineups)} teams")
print(f"  Statistics: {len(all_statistics)} teams")
print(f"  Players: {len(all_players)} teams")
print(f"  Predictions: {len(predictions_data['response'])} prediction")
print(f"  Injuries: {len(injuries_data['response'])} injuries")
print(f"  H2H: {len(h2h_data['response'])} matches")

# ─── fixture.json (skeleton with NS status for pre-partido) ──────────────

print("\nGenerating fixture.json (NS status for pre-partido)...")
fixture_skeleton = {
    "fixture": {
        "id": fixture_data["fixture"]["id"],
        "referee": fixture_data["fixture"]["referee"],
        "timezone": fixture_data["fixture"]["timezone"],
        "date": fixture_data["fixture"]["date"],
        "timestamp": fixture_data["fixture"]["timestamp"],
        "periods": fixture_data["fixture"]["periods"],
        "venue": fixture_data["fixture"]["venue"],
        "status": {
            "long": "Not Started",
            "short": "NS",
            "elapsed": 0,
        },
    },
    "league": fixture_data["league"],
    "teams": fixture_data["teams"],
    "goals": {"home": 0, "away": 0},
    "score": {
        "halftime": {"home": None, "away": None},
        "fulltime": {"home": None, "away": None},
        "extratime": {"home": None, "away": None},
        "penalty": {"home": None, "away": None},
    },
}
# Strip events/lineups/statistics/players from the skeleton
save_json("fixture.json", v3_envelope([fixture_skeleton]))
print("  fixture.json saved (NS status)")

# ─── lineups.json ──────────────────────────────────────────────────────────

print("Generating lineups.json...")
save_json("lineups.json", v3_envelope(all_lineups))
print(f"  lineups.json saved ({len(all_lineups)} teams)")

# ─── predictions.json ─────────────────────────────────────────────────────

print("Generating predictions.json...")
pred_response = predictions_data["response"][0]
save_json("predictions.json", v3_envelope([pred_response]))
print("  predictions.json saved")

# ─── injuries.json ────────────────────────────────────────────────────────

print("Generating injuries.json...")
save_json("injuries.json", v3_envelope(injuries_data["response"]))
print(f"  injuries.json saved ({len(injuries_data['response'])} injuries)")

# ─── h2h.json ─────────────────────────────────────────────────────────────

print("Generating h2h.json...")
save_json("h2h.json", v3_envelope(h2h_data["response"]))
print(f"  h2h.json saved ({len(h2h_data['response'])} matches)")

# ─── split events by momento ─────────────────────────────────────────────

print("\nSplitting events by momento...")
MOMENTO_CUTOFFS = {
    0: 0,    # pre: no events
    1: 15,   # 15': events up to minute 15
    2: 30,   # 30': events up to minute 30
    3: 45,   # ht: events up to minute 45 (+ stoppage)
    4: 60,   # 60': events up to minute 60
    5: 75,   # 75': events up to minute 75
    6: 999,  # ft: all events
}
MOMENTO_KEYS = {0: "pre", 1: "15", 2: "30", 3: "ht", 4: "60", 5: "75", 6: "ft"}

for momento, cutoff in MOMENTO_CUTOFFS.items():
    key = MOMENTO_KEYS[momento]
    if cutoff == 0:
        filtered = []
    elif cutoff == 999:
        filtered = all_events
    else:
        filtered = [
            e for e in all_events
            if e["time"]["elapsed"] <= cutoff
        ]
    save_json(f"events_{key}.json", v3_envelope(filtered))
    print(f"  events_{key}.json: {len(filtered)} events")

# ─── statistics by momento ───────────────────────────────────────────────

print("\nMapping statistics by momento...")
# Build the team-statistics structure for each momento
# Format: [{"team": {...}, "statistics": [{type, value}, ...]}, ...]

for momento in range(7):
    key = MOMENTO_KEYS[momento]

    if momento == 0:
        # Pre: no stats
        home_stats = []
        away_stats = []
    elif momento in (1, 2, 3):
        # 1H stats for momentos 1, 2, 3 (1-45')
        home_stats = stats_1h
        away_stats = stats_1h_away
    elif momento in (4, 5):
        # 2H stats for momentos 4, 5 (46-90+')
        home_stats = stats_2h
        away_stats = stats_2h_away
    else:  # momento 6
        # Full stats for FT
        home_stats = stats_full
        away_stats = stats_full_away

    home_team = all_statistics[0]["team"]
    away_team = all_statistics[1]["team"]

    save_json(f"statistics_{key}.json", v3_envelope([
        {"team": home_team, "statistics": home_stats},
        {"team": away_team, "statistics": away_stats},
    ]))
    print(f"  statistics_{key}.json: {len(home_stats)} stats/team")

# ─── players by momento ──────────────────────────────────────────────────

print("\nCopying player stats to all momentos (API only provides final)...")
for momento in range(7):
    key = MOMENTO_KEYS[momento]

    if momento == 0:
        # Pre: no player stats (only lineups exist)
        save_json(f"players_{key}.json", v3_envelope([]))
        print(f"  players_{key}.json: 0 players (pre-partido)")
    else:
        # All momentos use the same final player stats
        save_json(f"players_{key}.json", v3_envelope(all_players))
        player_count = sum(len(t["players"]) for t in all_players)
        print(f"  players_{key}.json: {player_count} players (final stats)")

# ─── summary ──────────────────────────────────────────────────────────────

print(f"\n✅ Done! All files written to {OUT_DIR}")
print(f"\nFiles generated:")
for f in sorted(OUT_DIR.iterdir()):
    print(f"  {f.name} — {f.stat().st_size // 1024} KB")

print(f"\nMomento structure:")
print(f"  0 (pre) — predictions, h2h, injuries, no match data")
print(f"  1 (15') — {len([e for e in all_events if e['time']['elapsed'] <= 15])} events, 1H stats")
print(f"  2 (30') — {len([e for e in all_events if e['time']['elapsed'] <= 30])} events, 1H stats")
print(f"  3 (ht)  — {len([e for e in all_events if e['time']['elapsed'] <= 45])} events, 1H stats (exact)")
print(f"  4 (60') — {len([e for e in all_events if e['time']['elapsed'] <= 60])} events, 2H stats")
print(f"  5 (75') — {len([e for e in all_events if e['time']['elapsed'] <= 75])} events, 2H stats")
print(f"  6 (ft)  — {len(all_events)} events, full stats (exact)")
