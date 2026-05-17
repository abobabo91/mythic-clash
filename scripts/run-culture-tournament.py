"""
Run a 50-game culture tournament with LLM players.

Each of the 100 cultures plays exactly once (50 matchups, 2 cultures per game).
Both sides use the LLM player. Collects structured results for analysis.

Usage:
    python scripts/run-culture-tournament.py
    python scripts/run-culture-tournament.py --model gemini-lite --max-steps 180
"""

from __future__ import annotations

import argparse
import io
import json
import random
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
elif hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.engine import apply_action, apply_action_interactive, create_v1_game, current_priority_player, legal_actions
from game.players import RolloutPlayer, ThinkingLLMPlayer

CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"
OUTPUT_DIR = ROOT / "data" / "benchmarks"


def find_pack_and_deck(slug: str) -> tuple[Path, Path] | None:
    pack = CARDS_DIR / f"{slug}-v1.json"
    if not pack.exists():
        return None
    decks = sorted(DECKS_DIR.glob(f"{slug}-*.json"))
    if not decks:
        return None
    regular = [d for d in decks if "anti-pressure" not in d.name]
    return pack, (regular[0] if regular else decks[0])


def get_all_playable_cultures() -> list[str]:
    cultures = []
    for pack_file in sorted(CARDS_DIR.glob("*-v1.json")):
        slug = pack_file.stem.replace("-v1", "")
        if slug in ("neutral-core", "domain-support"):
            continue
        if find_pack_and_deck(slug) is not None:
            cultures.append(slug)
    return cultures


GATE_OPPONENTS = ["ancient-greek", "norse-viking", "haitian-vodou"]


def make_matchups(cultures: list[str], count: int, seed: int = 42, mode: str = "llm-vs-llm") -> list[tuple[str, str]]:
    rng = random.Random(seed)
    if mode == "llm-vs-bot":
        # Each culture plays as LLM (player A) vs a random gate opponent (bot, player B)
        shuffled = list(cultures)
        rng.shuffle(shuffled)
        matchups = []
        for slug in shuffled[:count]:
            opponent = rng.choice([g for g in GATE_OPPONENTS if g != slug] or GATE_OPPONENTS)
            matchups.append((slug, opponent))
        return matchups
    else:
        shuffled = list(cultures)
        rng.shuffle(shuffled)
        matchups = []
        for i in range(0, min(len(shuffled) - 1, count * 2), 2):
            matchups.append((shuffled[i], shuffled[i + 1]))
            if len(matchups) >= count:
                break
        while len(matchups) < count and len(shuffled) > len(matchups) * 2:
            idx = len(matchups) * 2
            if idx + 1 < len(shuffled):
                matchups.append((shuffled[idx], shuffled[idx + 1]))
            else:
                break
        return matchups


def run_game(slug_a: str, slug_b: str, player_a, player_b, seed: int, max_steps: int) -> dict:
    paths_a = find_pack_and_deck(slug_a)
    paths_b = find_pack_and_deck(slug_b)
    if paths_a is None or paths_b is None:
        return {"error": f"Missing pack/deck for {slug_a} or {slug_b}"}

    pack_a, deck_a = paths_a
    pack_b, deck_b = paths_b

    try:
        state = create_v1_game(pack_a, deck_a, pack_b, deck_b, seed=seed)
    except Exception as e:
        return {"error": str(e)}

    controllers = [player_a, player_b]
    steps = 0
    errors = 0

    while state.winner is None and steps < max_steps:
        # Determine who has priority (may be non-active player during response)
        priority = current_priority_player(state)
        actions = legal_actions(state, priority)
        if not actions:
            break
        try:
            choice = controllers[priority].choose_action(state, priority, actions)
        except Exception as e:
            errors += 1
            import traceback
            print(f"    [ERROR step {steps}] Player {priority}: {e}", flush=True)
            traceback.print_exc()
            # Fallback to pass
            choice = next((a for a in actions if a["type"] == "pass"), actions[-1])
        apply_action_interactive(state, choice, priority)
        steps += 1

    winner_slug = None
    if state.winner == 0:
        winner_slug = slug_a
    elif state.winner == 1:
        winner_slug = slug_b

    # Collect LLM turn logs if available
    llm_logs_a = getattr(player_a, "turn_log", [])
    llm_logs_b = getattr(player_b, "turn_log", [])

    return {
        "slug_a": slug_a,
        "slug_b": slug_b,
        "winner_index": state.winner,
        "winner_slug": winner_slug,
        "turns": state.turn_number,
        "steps": steps,
        "health_a": state.players[0].health,
        "armor_a": state.players[0].armor,
        "health_b": state.players[1].health,
        "armor_b": state.players[1].armor,
        "board_a": len(state.players[0].board),
        "board_b": len(state.players[1].board),
        "errors": errors,
        "history": state.history,
        "llm_logs_a": llm_logs_a,
        "llm_logs_b": llm_logs_b,
    }


def analyze(results: list[dict]) -> dict:
    culture_stats: dict[str, dict] = {}
    total_turns = []
    total_steps = []
    errors_total = 0
    draws = 0

    for r in results:
        if "error" in r and "slug_a" not in r:
            continue
        slug_a = r["slug_a"]
        slug_b = r["slug_b"]
        for slug in (slug_a, slug_b):
            if slug not in culture_stats:
                culture_stats[slug] = {"wins": 0, "losses": 0, "draws": 0, "games": 0, "total_health_remaining": 0}

        culture_stats[slug_a]["games"] += 1
        culture_stats[slug_b]["games"] += 1

        if r["winner_index"] == 0:
            culture_stats[slug_a]["wins"] += 1
            culture_stats[slug_b]["losses"] += 1
            culture_stats[slug_a]["total_health_remaining"] += r["health_a"] + r["armor_a"]
        elif r["winner_index"] == 1:
            culture_stats[slug_b]["wins"] += 1
            culture_stats[slug_a]["losses"] += 1
            culture_stats[slug_b]["total_health_remaining"] += r["health_b"] + r["armor_b"]
        else:
            culture_stats[slug_a]["draws"] += 1
            culture_stats[slug_b]["draws"] += 1
            draws += 1

        total_turns.append(r["turns"])
        total_steps.append(r["steps"])
        errors_total += r.get("errors", 0)

    # Sort by win rate
    ranked = sorted(
        culture_stats.items(),
        key=lambda x: (x[1]["wins"] / max(1, x[1]["games"]), x[1]["total_health_remaining"]),
        reverse=True,
    )

    avg_turns = sum(total_turns) / len(total_turns) if total_turns else 0
    avg_steps = sum(total_steps) / len(total_steps) if total_steps else 0

    return {
        "games_played": len(results),
        "cultures_tested": len(culture_stats),
        "avg_turns": round(avg_turns, 1),
        "avg_steps": round(avg_steps, 1),
        "draws": draws,
        "llm_errors": errors_total,
        "ranked": ranked,
        "turn_distribution": {
            "min": min(total_turns) if total_turns else 0,
            "max": max(total_turns) if total_turns else 0,
            "under_8": sum(1 for t in total_turns if t < 8),
            "8_to_12": sum(1 for t in total_turns if 8 <= t <= 12),
            "13_to_20": sum(1 for t in total_turns if 13 <= t <= 20),
            "over_20": sum(1 for t in total_turns if t > 20),
        },
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="gemini-lite")
    parser.add_argument("--games", type=int, default=50)
    parser.add_argument("--max-steps", type=int, default=180)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="")
    parser.add_argument("--mode", default="llm-vs-bot", choices=["llm-vs-llm", "llm-vs-bot"],
                        help="llm-vs-bot uses RolloutBot for player B (much faster)")
    parser.add_argument("--start", type=int, default=0, help="Start from game N (0-indexed)")
    parser.add_argument("--count", type=int, default=0, help="Run only N games (0=all remaining)")
    parser.add_argument("--append", default="", help="Append results to JSONL file for batched runs")
    parser.add_argument("--analyze-jsonl", default="", help="Skip games, just analyze a JSONL results file")
    return parser.parse_args()


def main():
    args = parse_args()

    # Analyze-only mode: load JSONL and print analysis
    if args.analyze_jsonl:
        jsonl_path = Path(args.analyze_jsonl)
        results = [json.loads(line) for line in jsonl_path.read_text(encoding="utf-8").strip().splitlines()]
        analysis = analyze(results)
        total_time = sum(r.get("time", 0) for r in results)
        print(f"\n{'='*70}")
        print(f"  TOURNAMENT RESULTS (from {jsonl_path.name})")
        print(f"{'='*70}")
        print(f"  Games: {analysis['games_played']}  |  Cultures: {analysis['cultures_tested']}  |  Time: {total_time:.0f}s")
        print(f"  Avg turns: {analysis['avg_turns']}  |  Avg steps: {analysis['avg_steps']}  |  Draws: {analysis['draws']}")
        print(f"  LLM errors: {analysis['llm_errors']}")
        print(f"  Turn distribution: <8={analysis['turn_distribution']['under_8']}, 8-12={analysis['turn_distribution']['8_to_12']}, 13-20={analysis['turn_distribution']['13_to_20']}, >20={analysis['turn_distribution']['over_20']}")
        print(f"\n  CULTURE RANKINGS (by win rate):")
        print(f"  {'Culture':<28s} W   L   D   HP left")
        print(f"  {'-'*60}")
        winners = [(slug, s) for slug, s in analysis["ranked"] if s["wins"] > 0]
        losers = [(slug, s) for slug, s in analysis["ranked"] if s["wins"] == 0]
        for slug, stats in winners:
            print(f"  {slug:<28s} {stats['wins']}   {stats['losses']}   {stats['draws']}   {stats['total_health_remaining']}")
        if losers:
            print(f"  --- lost ---")
            for slug, stats in losers:
                print(f"  {slug:<28s} {stats['wins']}   {stats['losses']}   {stats['draws']}   {stats['total_health_remaining']}")
        return

    cultures = get_all_playable_cultures()
    print(f"Found {len(cultures)} playable cultures")

    all_matchups = make_matchups(cultures, args.games, seed=args.seed, mode=args.mode)

    # Slice for batched runs
    start = args.start
    count = args.count if args.count > 0 else len(all_matchups) - start
    matchups = all_matchups[start:start + count]

    print(f"Generated {len(all_matchups)} matchups, running [{start}..{start+len(matchups)-1}] ({len(matchups)} games)")
    print(f"Model: {args.model}")
    print()

    results = []
    t_start = time.time()

    for j, (slug_a, slug_b) in enumerate(matchups):
        i = start + j  # global index
        player_a = ThinkingLLMPlayer(model=args.model)
        player_b = ThinkingLLMPlayer(model=args.model) if args.mode == "llm-vs-llm" else RolloutPlayer()

        t0 = time.time()
        result = run_game(slug_a, slug_b, player_a, player_b, seed=args.seed + i, max_steps=args.max_steps)
        elapsed = time.time() - t0

        result["time"] = round(elapsed, 1)
        results.append(result)

        winner = result.get("winner_slug", "draw")
        turns = result.get("turns", "?")
        err = f" ({result['errors']} errs)" if result.get("errors") else ""
        print(f"  [{i+1:2d}/{len(all_matchups)}] {slug_a:25s} vs {slug_b:25s} -> {winner or 'draw':25s} T{turns} {elapsed:.0f}s{err}")

        # Append to JSONL for batched runs
        if args.append:
            append_path = Path(args.append)
            append_path.parent.mkdir(parents=True, exist_ok=True)
            with open(append_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")

    total_time = time.time() - t_start

    # Analyze
    analysis = analyze(results)

    print(f"\n{'='*70}")
    print(f"  TOURNAMENT COMPLETE")
    print(f"{'='*70}")
    print(f"  Games: {analysis['games_played']}  |  Cultures: {analysis['cultures_tested']}  |  Time: {total_time:.0f}s")
    print(f"  Avg turns: {analysis['avg_turns']}  |  Avg steps: {analysis['avg_steps']}  |  Draws: {analysis['draws']}")
    print(f"  LLM errors: {analysis['llm_errors']}")
    print(f"  Turn distribution: <8={analysis['turn_distribution']['under_8']}, 8-12={analysis['turn_distribution']['8_to_12']}, 13-20={analysis['turn_distribution']['13_to_20']}, >20={analysis['turn_distribution']['over_20']}")

    print(f"\n  CULTURE RANKINGS (by win rate):")
    print(f"  {'Culture':<28s} W   L   D   HP left")
    print(f"  {'-'*60}")
    winners = [(slug, s) for slug, s in analysis["ranked"] if s["wins"] > 0]
    losers = [(slug, s) for slug, s in analysis["ranked"] if s["wins"] == 0]

    for slug, stats in winners:
        print(f"  {slug:<28s} {stats['wins']}   {stats['losses']}   {stats['draws']}   {stats['total_health_remaining']}")
    if losers:
        print(f"  --- lost ---")
        for slug, stats in losers:
            print(f"  {slug:<28s} {stats['wins']}   {stats['losses']}   {stats['draws']}   {stats['total_health_remaining']}")

    # Save
    output_path = Path(args.output) if args.output else OUTPUT_DIR / "culture-tournament.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "model": args.model,
        "games": len(results),
        "total_time": round(total_time, 1),
        "analysis": {
            "avg_turns": analysis["avg_turns"],
            "avg_steps": analysis["avg_steps"],
            "draws": analysis["draws"],
            "llm_errors": analysis["llm_errors"],
            "turn_distribution": analysis["turn_distribution"],
        },
        "rankings": [
            {"culture": slug, **stats}
            for slug, stats in analysis["ranked"]
        ],
        "results": results,
    }
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  Saved to {output_path}")


if __name__ == "__main__":
    main()
