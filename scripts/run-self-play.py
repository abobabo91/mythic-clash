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

from game.engine import apply_action, build_deck_from_cultures, create_game, create_v1_game, legal_actions
from game.players import AgenticLLMPlayer, BenchmarkPlayer, HeuristicPlayer, PromptLLMPlayer, RolloutPlayer, ThinkingLLMPlayer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Mythic Clash self-play.")
    parser.add_argument("--cultures-a", default="ancient-greek,roman", help="Comma-separated culture slugs for player A deck.")
    parser.add_argument("--cultures-b", default="aztec-mexica,maya", help="Comma-separated culture slugs for player B deck.")
    parser.add_argument("--player-a", default="heuristic", choices=["heuristic", "rollout", "benchmark", "llm", "thinking-llm"])
    parser.add_argument("--player-b", default="heuristic", choices=["heuristic", "rollout", "benchmark", "llm", "thinking-llm"])
    parser.add_argument("--model-a", default="gpt-4o-mini")
    parser.add_argument("--model-b", default="gpt-4o-mini")
    parser.add_argument("--pack-a", default="", help="Optional v1 pack JSON path for player A.")
    parser.add_argument("--deck-a", default="", help="Optional v1 deck JSON path for player A.")
    parser.add_argument("--pack-b", default="", help="Optional v1 pack JSON path for player B.")
    parser.add_argument("--deck-b", default="", help="Optional v1 deck JSON path for player B.")
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--output", default="", help="Optional transcript output path.")
    return parser.parse_args()


def build_player(kind: str, model: str):
    if kind == "heuristic":
        return HeuristicPlayer()
    if kind == "rollout":
        return RolloutPlayer()
    if kind == "benchmark":
        return BenchmarkPlayer()
    if kind == "llm":
        return ThinkingLLMPlayer(model=model)
    if kind == "thinking-llm":
        return ThinkingLLMPlayer(model=model)
    raise ValueError(kind)


def main() -> None:
    args = parse_args()

    if args.pack_a and args.deck_a and args.pack_b and args.deck_b:
        game = create_v1_game(args.pack_a, args.deck_a, args.pack_b, args.deck_b, player_a="Player A", player_b="Player B", seed=args.seed)
    else:
        deck_a = build_deck_from_cultures([slug.strip() for slug in args.cultures_a.split(",") if slug.strip()])
        deck_b = build_deck_from_cultures([slug.strip() for slug in args.cultures_b.split(",") if slug.strip()])
        game = create_game(deck_a, deck_b, player_a="Player A", player_b="Player B", seed=args.seed)

    controllers = [
        build_player(args.player_a, args.model_a),
        build_player(args.player_b, args.model_b),
    ]

    metrics = {
        "actions": [[], []],
        "mana_spent": [0, 0],
        "cards_played": [0, 0],
        "minions_played": [0, 0],
        "spells_cast": [0, 0],
        "relics_played": [0, 0],
        "attacks_made": [0, 0],
        "hero_powers_used": [0, 0],
        "damage_to_hero": [0, 0],
        "minions_killed": [0, 0],
        "turns_played": [0, 0],
    }

    steps = 0
    while game.winner is None and steps < args.max_steps:
        active = game.active_player
        actions = legal_actions(game, active)
        if not actions:
            break
        choice = controllers[active].choose_action(game, active, actions)
        reason = choice.get("llm_reason")
        plan = choice.get("llm_plan", "")
        if reason:
            game.history.append(f"{game.players[active].name} thought: {reason}")
        if plan:
            game.history.append(f"{game.players[active].name} plan: {plan}")

        enemy_health_before = game.players[1 - active].health + game.players[1 - active].armor
        enemy_board_before = len(game.players[1 - active].board)

        apply_action(game, choice)

        action_type = choice["type"]
        metrics["actions"][active].append({"turn": game.turn_number, "type": action_type, "id": choice.get("id", "")})

        if action_type == "play":
            metrics["cards_played"][active] += 1
            metrics["minions_played"][active] += 1
        elif action_type == "play_spell":
            metrics["cards_played"][active] += 1
            metrics["spells_cast"][active] += 1
        elif action_type == "play_relic":
            metrics["cards_played"][active] += 1
            metrics["relics_played"][active] += 1
        elif action_type == "attack":
            metrics["attacks_made"][active] += 1
        elif action_type == "hero_power":
            metrics["hero_powers_used"][active] += 1
        elif action_type == "pass":
            metrics["turns_played"][active] += 1

        enemy_health_after = game.players[1 - active].health + game.players[1 - active].armor
        enemy_board_after = len(game.players[1 - active].board)
        damage_dealt = max(0, enemy_health_before - enemy_health_after)
        kills = max(0, enemy_board_before - enemy_board_after)
        metrics["damage_to_hero"][active] += damage_dealt
        metrics["minions_killed"][active] += kills

        steps += 1

    for i in range(2):
        metrics["mana_spent"][i] = sum(
            a.get("cost", 0) for a in metrics["actions"][i]
            if a["type"] in ("play", "play_spell", "play_relic", "hero_power")
        )

    summary = {
        "winner": None if game.winner is None else game.players[game.winner].name,
        "winner_index": game.winner,
        "turn_number": game.turn_number,
        "steps": steps,
        "players": [
            {
                "name": game.players[i].name,
                "health": game.players[i].health,
                "armor": game.players[i].armor,
                "ritual_mana": game.players[i].ritual_mana,
                "cards_played": metrics["cards_played"][i],
                "minions_played": metrics["minions_played"][i],
                "spells_cast": metrics["spells_cast"][i],
                "relics_played": metrics["relics_played"][i],
                "attacks_made": metrics["attacks_made"][i],
                "hero_powers_used": metrics["hero_powers_used"][i],
                "damage_to_hero": metrics["damage_to_hero"][i],
                "minions_killed": metrics["minions_killed"][i],
                "turns_played": metrics["turns_played"][i],
            }
            for i in range(2)
        ],
        "history": game.history,
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote transcript to {output_path}")


if __name__ == "__main__":
    main()
