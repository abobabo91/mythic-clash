"""
Run an LLM vs LLM game in Mythic Clash.

Usage:
    python scripts/test-llm-vs-llm.py --model-a sonnet --model-b haiku
"""

from __future__ import annotations

import argparse
import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.engine import apply_action, create_v1_game, legal_actions
from game.players import ThinkingLLMPlayer

CARDS = ROOT / "data" / "cards-v1"
DECKS = ROOT / "data" / "decks-v1"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-a", default="sonnet")
    parser.add_argument("--model-b", default="haiku")
    parser.add_argument("--culture-a", default="ancient-greek")
    parser.add_argument("--culture-b", default="norse-viking")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-steps", type=int, default=250)
    return parser.parse_args()


def find_pack_and_deck(slug):
    pack = CARDS / f"{slug}-v1.json"
    decks = sorted(DECKS.glob(f"{slug}-*.json"))
    # prefer non-anti-pressure deck
    regular = [d for d in decks if "anti-pressure" not in d.name]
    return pack, (regular[0] if regular else decks[0])


def main():
    args = parse_args()

    pack_a, deck_a = find_pack_and_deck(args.culture_a)
    pack_b, deck_b = find_pack_and_deck(args.culture_b)

    llm_a = ThinkingLLMPlayer(model=args.model_a)
    llm_b = ThinkingLLMPlayer(model=args.model_b)
    controllers = [llm_a, llm_b]
    labels = [f"A ({args.model_a} / {args.culture_a})", f"B ({args.model_b} / {args.culture_b})"]

    state = create_v1_game(pack_a, deck_a, pack_b, deck_b, seed=args.seed)

    print(f"Player A: {args.model_a} playing {args.culture_a}")
    print(f"Player B: {args.model_b} playing {args.culture_b}")
    print(f"Seed: {args.seed}")
    print()

    steps = 0
    while state.winner is None and steps < args.max_steps:
        active = state.active_player
        actions = legal_actions(state, active)
        if not actions:
            break
        choice = controllers[active].choose_action(state, active, actions)

        if choice["type"] != "pass":
            reason = choice.get("llm_reason", "")
            plan = choice.get("llm_plan", "")
            tag = labels[active]
            print(f"  T{state.turn_number} {tag}: {choice.get('label', choice['id'])}")
            if reason:
                print(f"       Reason: {reason[:150]}")
            if plan:
                print(f"       Plan: {plan[:150]}")
        else:
            print(f"  T{state.turn_number} {labels[active]}: End turn")

        apply_action(state, choice)
        steps += 1

    print()
    print("=" * 70)
    if state.winner is not None:
        winner_label = labels[state.winner]
        print(f"  WINNER: {winner_label}")
    else:
        print("  No winner (timeout/draw)")
    print(f"  Turns: {state.turn_number}  |  Steps: {steps}")
    print(f"  A health: {state.players[0].health}+{state.players[0].armor}  |  B health: {state.players[1].health}+{state.players[1].armor}")
    print(f"  A thinking entries: {len(llm_a.turn_log)}  |  B thinking entries: {len(llm_b.turn_log)}")
    print("=" * 70)


if __name__ == "__main__":
    main()
