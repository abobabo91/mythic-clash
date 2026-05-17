"""
Test LLM players on simple tactical scenarios across multiple models.

Usage:
    python scripts/test-llm-player.py --models sonnet,haiku
    python scripts/test-llm-player.py --models sonnet --test full
    python scripts/test-llm-player.py --models sonnet,haiku,gpt-4o-mini --test simple
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.engine import (
    CardTemplate,
    apply_action,
    create_game,
    create_v1_game,
    game_state_view,
    legal_actions,
    summon_minion,
)
from game.players import MODEL_PRESETS, RolloutPlayer, ThinkingLLMPlayer


def make_minion(name, cost, attack, health, keywords=None, culture="test", text=""):
    return CardTemplate(
        id=f"test-{name.lower().replace(' ', '-')}",
        name=name,
        culture_slug=culture,
        source="test",
        card_type="minion",
        cost=cost,
        rarity="common",
        alignment="neutral",
        text=text,
        attack=attack,
        health=health,
        keywords=list(keywords or []),
    )


def divider(title=""):
    print(f"\n{'='*70}")
    if title:
        print(f"  {title}")
        print(f"{'='*70}")
    print()


def setup_lethal_scenario():
    """LLM has a 6/4 ready minion, enemy hero at 5 HP. Lethal is available."""
    deck_a = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    deck_b = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    state = create_game(deck_a, deck_b, seed=1)
    state.players[0].board.clear()
    state.players[1].board.clear()
    state.players[0].hand.clear()
    state.players[1].health = 5
    state.players[0].mana = 0
    big = make_minion("Thundergod", 5, 6, 4, text="A mighty divine figure")
    summon_minion(state, 0, big, sleeping=False)
    return state, "Lethal Check: 6/4 ready vs enemy at 5 HP", lambda c: c.get("target") == "hero" and c["type"] == "attack"


def setup_trade_scenario():
    """LLM has 3/2 ready. Enemy has 2/1 Imp and 4/5 Giant. Best trade is into the Imp."""
    deck_a = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    deck_b = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    state = create_game(deck_a, deck_b, seed=2)
    state.players[0].board.clear()
    state.players[1].board.clear()
    state.players[0].hand.clear()
    state.players[0].mana = 0
    summon_minion(state, 0, make_minion("Warrior", 2, 3, 2), sleeping=False)
    imp = summon_minion(state, 1, make_minion("Imp", 1, 2, 1))
    summon_minion(state, 1, make_minion("Giant", 5, 4, 5))
    return state, "Trade Check: 3/2 ready vs 2/1 Imp + 4/5 Giant", lambda c: c.get("target_unit_id") == imp.unit_id


def setup_play_on_curve():
    """
    Turn 3, 3 mana. Hand has a 1-cost 1/2, a 3-cost 3/4, and a 5-cost 5/5.
    Best play: the 3-cost on curve (uses all mana).
    """
    deck_a = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    deck_b = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    state = create_game(deck_a, deck_b, seed=3)
    state.players[0].board.clear()
    state.players[1].board.clear()
    state.players[0].hand.clear()
    state.players[0].mana = 3
    state.players[0].max_mana = 3
    state.turn_number = 3

    small = make_minion("Scout", 1, 1, 2, text="A small explorer")
    mid = make_minion("Knight", 3, 3, 4, text="A reliable warrior")
    big = make_minion("Dragon", 5, 5, 5, text="A powerful beast")
    state.players[0].hand = [small, mid, big]

    return state, "Curve Check: 3 mana, hand has 1/3/5 cost minions", lambda c: c["type"] == "play" and c.get("hand_index") == 1


def setup_taunt_respect():
    """
    LLM has a 5/3 ready. Enemy has a 1/4 Taunt and the hero at 3 HP.
    Must attack the taunt - cannot go face.
    """
    deck_a = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    deck_b = [make_minion(f"Filler{i}", 3, 2, 3) for i in range(18)]
    state = create_game(deck_a, deck_b, seed=4)
    state.players[0].board.clear()
    state.players[1].board.clear()
    state.players[0].hand.clear()
    state.players[0].mana = 0
    state.players[1].health = 3
    summon_minion(state, 0, make_minion("Attacker", 3, 5, 3), sleeping=False)
    taunt = summon_minion(state, 1, make_minion("Wall", 2, 1, 4, keywords=["taunt"]))
    return state, "Taunt Respect: 5/3 ready, enemy has 1/4 Taunt, hero at 3 HP", lambda c: c.get("target_unit_id") == taunt.unit_id


SCENARIOS = [
    setup_lethal_scenario,
    setup_trade_scenario,
    setup_play_on_curve,
    setup_taunt_respect,
]


def test_model_on_scenarios(model_name: str) -> list[dict]:
    divider(f"MODEL: {model_name}")
    try:
        llm = ThinkingLLMPlayer(model=model_name)
    except RuntimeError as e:
        print(f"  SKIP: {e}")
        return []

    results = []
    for setup_fn in SCENARIOS:
        state, description, check_fn = setup_fn()
        actions = legal_actions(state, 0)

        print(f"\n  Scenario: {description}")
        print(f"  Actions available: {len(actions)}")

        t0 = time.time()
        try:
            choice = llm.choose_action(state, 0, actions)
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({"scenario": description, "correct": False, "error": str(e)})
            continue
        elapsed = time.time() - t0

        correct = check_fn(choice)
        reason = choice.get("llm_reason", "")
        plan = choice.get("llm_plan", "")
        thinking = choice.get("llm_thinking", "")

        print(f"  Chose: {choice['id']}")
        print(f"  Correct: {'YES' if correct else 'NO'}")
        print(f"  Time: {elapsed:.1f}s")
        if reason:
            print(f"  Reason: {reason[:200]}")
        if plan:
            print(f"  Plan: {plan[:200]}")
        if thinking:
            print(f"  Thinking preview: {thinking[:300]}...")

        results.append({
            "scenario": description,
            "correct": correct,
            "action": choice["id"],
            "reason": reason,
            "plan": plan,
            "thinking_length": len(thinking),
            "time": round(elapsed, 1),
        })

    return results


def test_full_game(model_name: str):
    divider(f"FULL GAME: {model_name} vs RolloutBot")

    CARDS = ROOT / "data" / "cards-v1"
    DECKS = ROOT / "data" / "decks-v1"

    try:
        llm = ThinkingLLMPlayer(model=model_name)
    except RuntimeError as e:
        print(f"  SKIP: {e}")
        return

    state = create_v1_game(
        CARDS / "ancient-greek-v1.json",
        DECKS / "ancient-greek-athena-midrange.json",
        CARDS / "norse-viking-v1.json",
        DECKS / "norse-viking-thor-bifrost-charge.json",
        seed=42,
    )
    bot = RolloutPlayer()
    controllers = [llm, bot]

    print(f"  Player A (LLM {model_name}): Ancient Greek")
    print(f"  Player B (RolloutBot): Norse Viking\n")

    steps = 0
    while state.winner is None and steps < 200:
        active = state.active_player
        actions = legal_actions(state, active)
        if not actions:
            break
        choice = controllers[active].choose_action(state, active, actions)
        if active == 0 and choice["type"] != "pass":
            reason = choice.get("llm_reason", "")
            print(f"  T{state.turn_number} LLM: {choice.get('label', choice['id'])}")
            if reason:
                print(f"       -> {reason[:120]}")
        apply_action(state, choice)
        steps += 1

    divider("RESULT")
    winner = "LLM" if state.winner == 0 else "Bot" if state.winner == 1 else "None"
    print(f"  Winner: {winner}  |  Turns: {state.turn_number}  |  Steps: {steps}")
    print(f"  LLM health: {state.players[0].health}+{state.players[0].armor}  |  Bot health: {state.players[1].health}+{state.players[1].armor}")
    print(f"  LLM thinking log entries: {len(llm.turn_log)}")


def parse_args():
    available = ", ".join(MODEL_PRESETS.keys())
    parser = argparse.ArgumentParser(description=f"Test LLM players. Available presets: {available}")
    parser.add_argument("--models", default="sonnet", help="Comma-separated model names or presets")
    parser.add_argument("--test", default="simple", choices=["simple", "full", "both"])
    return parser.parse_args()


def main():
    args = parse_args()
    models = [m.strip() for m in args.models.split(",")]

    if args.test in ("simple", "both"):
        all_results: dict[str, list[dict]] = {}
        for model in models:
            all_results[model] = test_model_on_scenarios(model)

        divider("COMPARISON SUMMARY")
        header = f"{'Scenario':<50s}"
        for model in models:
            header += f" {model:>12s}"
        print(header)
        print("-" * len(header))

        if all_results:
            first = all_results[models[0]]
            for i, result in enumerate(first):
                row = f"{result['scenario'][:48]:<50s}"
                for model in models:
                    if i < len(all_results.get(model, [])):
                        r = all_results[model][i]
                        mark = "YES" if r["correct"] else "NO"
                        row += f" {mark + ' ' + str(r.get('time', '?')) + 's':>12s}"
                    else:
                        row += f" {'SKIP':>12s}"
                print(row)

            print()
            for model in models:
                results = all_results.get(model, [])
                correct = sum(1 for r in results if r.get("correct"))
                total = len(results)
                print(f"  {model}: {correct}/{total} correct")

    if args.test in ("full", "both"):
        for model in models:
            test_full_game(model)


if __name__ == "__main__":
    main()
