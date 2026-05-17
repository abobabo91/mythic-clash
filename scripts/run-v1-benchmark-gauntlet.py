"""
Run a reusable benchmark gauntlet for a v1 culture deck.
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
from game.players import BenchmarkPlayer, HeuristicPlayer, RolloutPlayer


@dataclass(frozen=True)
class BenchmarkDeck:
    slug: str
    label: str
    pack: Path
    deck: Path


BENCHMARKS: dict[str, BenchmarkDeck] = {
    "ancient-greek": BenchmarkDeck(
        slug="ancient-greek",
        label="Ancient Greek",
        pack=ROOT / "data" / "cards-v1" / "ancient-greek-v1.json",
        deck=ROOT / "data" / "decks-v1" / "ancient-greek-athena-midrange.json",
    ),
    "haitian-vodou": BenchmarkDeck(
        slug="haitian-vodou",
        label="Haitian Vodou",
        pack=ROOT / "data" / "cards-v1" / "haitian-vodou-v1.json",
        deck=ROOT / "data" / "decks-v1" / "haitian-vodou-legba-spirits.json",
    ),
    "inuit": BenchmarkDeck(
        slug="inuit",
        label="Inuit",
        pack=ROOT / "data" / "cards-v1" / "inuit-v1.json",
        deck=ROOT / "data" / "decks-v1" / "inuit-sedna-tidehunt.json",
    ),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Mythic Clash v1 benchmark gauntlet.")
    parser.add_argument("--pack", required=True, help="Candidate pack JSON path.")
    parser.add_argument("--deck", required=True, help="Candidate deck JSON path.")
    parser.add_argument("--candidate-name", default="", help="Optional display name for the candidate.")
    parser.add_argument(
        "--benchmarks",
        default="ancient-greek,haitian-vodou",
        help="Comma-separated benchmark slugs. Available: ancient-greek, haitian-vodou, inuit.",
    )
    parser.add_argument(
        "--seeds",
        default="31,47",
        help="Comma-separated integer seeds to use for each matchup.",
    )
    parser.add_argument("--max-steps", type=int, default=250)
    parser.add_argument(
        "--seat-mode",
        choices=["single", "both"],
        default="single",
        help="Run the candidate only as Player A, or as both Player A and Player B.",
    )
    parser.add_argument(
        "--player-kind",
        choices=["heuristic", "rollout", "benchmark"],
        default="benchmark",
        help="Controller used for both sides during gauntlet runs.",
    )
    parser.add_argument("--output", default="", help="Optional summary output path.")
    return parser.parse_args()


def parse_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_seeds(value: str) -> list[int]:
    return [int(item) for item in parse_csv(value)]


def run_match(
    *,
    candidate_pack: Path,
    candidate_deck: Path,
    benchmark: BenchmarkDeck,
    seed: int,
    max_steps: int,
    candidate_seat: str,
    player_kind: str,
) -> dict[str, object]:
    if candidate_seat == "a":
        game = create_v1_game(
            str(candidate_pack),
            str(candidate_deck),
            str(benchmark.pack),
            str(benchmark.deck),
            player_a="Candidate",
            player_b=benchmark.label,
            seed=seed,
        )
        candidate_index = 0
    else:
        game = create_v1_game(
            str(benchmark.pack),
            str(benchmark.deck),
            str(candidate_pack),
            str(candidate_deck),
            player_a=benchmark.label,
            player_b="Candidate",
            seed=seed,
        )
        candidate_index = 1

    if player_kind == "benchmark":
        player_cls = BenchmarkPlayer
    elif player_kind == "rollout":
        player_cls = RolloutPlayer
    else:
        player_cls = HeuristicPlayer
    controllers = [player_cls(), player_cls()]
    steps = 0
    while game.winner is None and steps < max_steps:
        active = game.active_player
        actions = legal_actions(game, active)
        if not actions:
            break
        choice = controllers[active].choose_action(game, active, actions)
        apply_action(game, choice)
        steps += 1

    candidate_player = game.players[candidate_index]
    benchmark_player = game.players[1 - candidate_index]
    winner_name = None if game.winner is None else game.players[game.winner].name
    result = "draw"
    if game.winner == candidate_index:
        result = "win"
    elif game.winner is not None:
        result = "loss"

    return {
        "benchmark": benchmark.slug,
        "benchmark_label": benchmark.label,
        "seed": seed,
        "candidate_seat": candidate_seat,
        "result": result,
        "winner": winner_name,
        "turn_number": game.turn_number,
        "steps": steps,
        "candidate_health": candidate_player.health,
        "benchmark_health": benchmark_player.health,
    }


def summarize_runs(candidate_name: str, benchmark_slugs: list[str], seeds: list[int], runs: list[dict[str, object]]) -> dict[str, object]:
    by_benchmark: dict[str, dict[str, object]] = {}
    total_wins = total_losses = total_draws = 0

    for slug in benchmark_slugs:
        benchmark_runs = [run for run in runs if run["benchmark"] == slug]
        wins = sum(1 for run in benchmark_runs if run["result"] == "win")
        losses = sum(1 for run in benchmark_runs if run["result"] == "loss")
        draws = sum(1 for run in benchmark_runs if run["result"] == "draw")
        avg_turn = round(sum(int(run["turn_number"]) for run in benchmark_runs) / len(benchmark_runs), 2) if benchmark_runs else 0
        by_benchmark[slug] = {
            "label": BENCHMARKS[slug].label,
            "wins": wins,
            "losses": losses,
            "draws": draws,
            "average_turn": avg_turn,
            "runs": benchmark_runs,
        }
        total_wins += wins
        total_losses += losses
        total_draws += draws

    return {
        "candidate": candidate_name,
        "benchmarks": benchmark_slugs,
        "seeds": seeds,
        "overall_record": {
            "wins": total_wins,
            "losses": total_losses,
            "draws": total_draws,
        },
        "by_benchmark": by_benchmark,
    }


def main() -> None:
    args = parse_args()
    candidate_pack = Path(args.pack)
    candidate_deck = Path(args.deck)
    benchmark_slugs = parse_csv(args.benchmarks)
    seeds = parse_seeds(args.seeds)
    seat_order = ["a"] if args.seat_mode == "single" else ["a", "b"]

    for slug in benchmark_slugs:
        if slug not in BENCHMARKS:
            raise ValueError(f"Unknown benchmark slug: {slug}")

    candidate_name = args.candidate_name or candidate_deck.stem
    runs: list[dict[str, object]] = []
    for slug in benchmark_slugs:
        benchmark = BENCHMARKS[slug]
        for seed in seeds:
            for seat in seat_order:
                runs.append(
                    run_match(
                        candidate_pack=candidate_pack,
                        candidate_deck=candidate_deck,
                        benchmark=benchmark,
                        seed=seed,
                        max_steps=args.max_steps,
                        candidate_seat=seat,
                        player_kind=args.player_kind,
                    )
                )

    summary = summarize_runs(candidate_name, benchmark_slugs, seeds, runs)
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote benchmark summary to {output_path}")


if __name__ == "__main__":
    main()
