"""
Run a Mythic Clash prototype self-play match.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.engine import apply_action, build_deck_from_cultures, create_game, legal_actions
from game.players import AgenticLLMPlayer, HeuristicPlayer, PromptLLMPlayer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Mythic Clash self-play.")
    parser.add_argument("--cultures-a", default="ancient-greek,roman", help="Comma-separated culture slugs for player A deck.")
    parser.add_argument("--cultures-b", default="aztec-mexica,maya", help="Comma-separated culture slugs for player B deck.")
    parser.add_argument("--player-a", default="heuristic", choices=["heuristic", "llm", "agentic-llm"])
    parser.add_argument("--player-b", default="heuristic", choices=["heuristic", "llm", "agentic-llm"])
    parser.add_argument("--model-a", default="gpt-4o-mini")
    parser.add_argument("--model-b", default="gpt-4o-mini")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--output", default="", help="Optional transcript output path.")
    return parser.parse_args()


def build_player(kind: str, model: str):
    if kind == "heuristic":
        return HeuristicPlayer()
    if kind == "llm":
        return PromptLLMPlayer(model=model)
    if kind == "agentic-llm":
        return AgenticLLMPlayer(model=model)
    raise ValueError(kind)


def main() -> None:
    args = parse_args()

    deck_a = build_deck_from_cultures([slug.strip() for slug in args.cultures_a.split(",") if slug.strip()])
    deck_b = build_deck_from_cultures([slug.strip() for slug in args.cultures_b.split(",") if slug.strip()])
    game = create_game(deck_a, deck_b, player_a="Player A", player_b="Player B", seed=args.seed)

    controllers = [
        build_player(args.player_a, args.model_a),
        build_player(args.player_b, args.model_b),
    ]

    steps = 0
    while game.winner is None and steps < args.max_steps:
        active = game.active_player
        actions = legal_actions(game, active)
        if not actions:
            break
        choice = controllers[active].choose_action(game, active, actions)
        reason = choice.get("llm_reason")
        if reason:
            game.history.append(f"{game.players[active].name} thought: {reason}")
        apply_action(game, choice)
        steps += 1

    summary = {
        "winner": None if game.winner is None else game.players[game.winner].name,
        "turn_number": game.turn_number,
        "steps": steps,
        "player_a_health": game.players[0].health,
        "player_a_armor": game.players[0].armor,
        "player_b_health": game.players[1].health,
        "player_b_armor": game.players[1].armor,
        "history": game.history,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote transcript to {output_path}")


if __name__ == "__main__":
    main()
