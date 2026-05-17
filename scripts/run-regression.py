"""
Seed-controlled regression simulation for Mythic Clash.

Runs a fixed set of matchups at fixed seeds, saves a structured snapshot,
and optionally diffs against a previous snapshot to detect balance shifts.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.engine import apply_action, create_v1_game, legal_actions
from game.players import RolloutPlayer

CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"
BENCHMARKS_DIR = ROOT / "data" / "benchmarks"

REGRESSION_SEEDS = [1, 7, 13, 31, 42, 59, 73, 97]

REGRESSION_MATCHUPS = [
    ("ancient-greek", "norse-viking"),
    ("ancient-greek", "haitian-vodou"),
    ("ancient-greek", "inuit"),
    ("norse-viking", "haitian-vodou"),
    ("norse-viking", "inuit"),
    ("haitian-vodou", "inuit"),
    ("ancient-greek", "slavic"),
    ("ancient-greek", "ancient-egyptian"),
    ("norse-viking", "ancient-egyptian"),
    ("slavic", "ancient-egyptian"),
]


def find_pack_and_deck(slug: str) -> tuple[Path, Path]:
    pack = CARDS_DIR / f"{slug}-v1.json"
    if not pack.exists():
        raise FileNotFoundError(f"Pack not found: {pack}")
    decks = sorted(DECKS_DIR.glob(f"{slug}-*.json"))
    if not decks:
        raise FileNotFoundError(f"No deck found for {slug}")
    return pack, decks[0]


def run_match(pack_a: Path, deck_a: Path, pack_b: Path, deck_b: Path, seed: int, max_steps: int = 160) -> dict:
    bot = RolloutPlayer()
    state = create_v1_game(pack_a, deck_a, pack_b, deck_b, seed=seed)
    steps = 0
    while state.winner is None and steps < max_steps:
        active = state.active_player
        actions = legal_actions(state, active)
        if not actions:
            break
        choice = bot.choose_action(state, active, actions)
        apply_action(state, choice)
        steps += 1
    return {
        "winner_index": state.winner,
        "turn": state.turn_number,
        "steps": steps,
        "health": [state.players[i].health for i in range(2)],
        "armor": [state.players[i].armor for i in range(2)],
    }


def run_regression(seeds: list[int], max_steps: int = 160) -> dict:
    results = []
    culture_wins = {}
    total_games = 0

    for slug_a, slug_b in REGRESSION_MATCHUPS:
        pack_a, deck_a = find_pack_and_deck(slug_a)
        pack_b, deck_b = find_pack_and_deck(slug_b)
        matchup_key = f"{slug_a} vs {slug_b}"
        matchup_results = []

        for seed in seeds:
            result = run_match(pack_a, deck_a, pack_b, deck_b, seed, max_steps)
            winner_slug = slug_a if result["winner_index"] == 0 else slug_b if result["winner_index"] == 1 else "draw"
            result["seed"] = seed
            result["winner_slug"] = winner_slug
            matchup_results.append(result)
            total_games += 1

            culture_wins.setdefault(slug_a, {"wins": 0, "losses": 0, "games": 0})
            culture_wins.setdefault(slug_b, {"wins": 0, "losses": 0, "games": 0})
            culture_wins[slug_a]["games"] += 1
            culture_wins[slug_b]["games"] += 1
            if result["winner_index"] == 0:
                culture_wins[slug_a]["wins"] += 1
                culture_wins[slug_b]["losses"] += 1
            elif result["winner_index"] == 1:
                culture_wins[slug_b]["wins"] += 1
                culture_wins[slug_a]["losses"] += 1

        a_wins = sum(1 for r in matchup_results if r["winner_index"] == 0)
        b_wins = sum(1 for r in matchup_results if r["winner_index"] == 1)
        results.append({
            "matchup": matchup_key,
            "a_slug": slug_a,
            "b_slug": slug_b,
            "a_wins": a_wins,
            "b_wins": b_wins,
            "games": len(matchup_results),
            "avg_turns": round(sum(r["turn"] for r in matchup_results) / len(matchup_results), 1),
            "details": matchup_results,
        })

    return {
        "seeds": seeds,
        "total_games": total_games,
        "matchups": results,
        "culture_summary": {
            slug: {
                "wins": data["wins"],
                "losses": data["losses"],
                "games": data["games"],
                "win_rate": round(data["wins"] / data["games"], 3) if data["games"] > 0 else 0,
            }
            for slug, data in sorted(culture_wins.items())
        },
    }


def diff_snapshots(current: dict, previous: dict) -> list[str]:
    diffs = []
    prev_matchups = {m["matchup"]: m for m in previous.get("matchups", [])}
    for matchup in current.get("matchups", []):
        key = matchup["matchup"]
        if key not in prev_matchups:
            continue
        prev = prev_matchups[key]
        if matchup["a_wins"] != prev["a_wins"] or matchup["b_wins"] != prev["b_wins"]:
            diffs.append(
                f"{key}: {prev['a_wins']}-{prev['b_wins']} -> {matchup['a_wins']}-{matchup['b_wins']}"
            )

    prev_culture = previous.get("culture_summary", {})
    for slug, data in current.get("culture_summary", {}).items():
        if slug in prev_culture:
            old_wr = prev_culture[slug]["win_rate"]
            new_wr = data["win_rate"]
            delta = new_wr - old_wr
            if abs(delta) >= 0.1:
                diffs.append(f"{slug} win rate: {old_wr:.3f} -> {new_wr:.3f} ({delta:+.3f})")
    return diffs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run seed-controlled regression simulation.")
    parser.add_argument("--output", default="", help="Output snapshot path.")
    parser.add_argument("--compare", default="", help="Previous snapshot to diff against.")
    parser.add_argument("--max-steps", type=int, default=160)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Running {len(REGRESSION_MATCHUPS)} matchups x {len(REGRESSION_SEEDS)} seeds = {len(REGRESSION_MATCHUPS) * len(REGRESSION_SEEDS)} games...")
    snapshot = run_regression(REGRESSION_SEEDS, args.max_steps)

    print(f"\nCompleted {snapshot['total_games']} games.\n")
    print("Culture win rates:")
    for slug, data in snapshot["culture_summary"].items():
        print(f"  {slug:25s}  {data['wins']:2d}W / {data['losses']:2d}L  ({data['win_rate']:.1%})")

    print("\nMatchup results:")
    for matchup in snapshot["matchups"]:
        print(f"  {matchup['matchup']:45s}  {matchup['a_wins']}-{matchup['b_wins']}  avg {matchup['avg_turns']} turns")

    if args.compare:
        prev = json.loads(Path(args.compare).read_text(encoding="utf-8"))
        diffs = diff_snapshots(snapshot, prev)
        if diffs:
            print(f"\nRegressions detected ({len(diffs)}):")
            for diff in diffs:
                print(f"  {diff}")
        else:
            print("\nNo regressions detected.")

    output_path = Path(args.output) if args.output else BENCHMARKS_DIR / "regression-snapshot.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSnapshot saved to {output_path}")


if __name__ == "__main__":
    main()
