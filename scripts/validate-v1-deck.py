"""
Validate a v1 deck list against a card pack and report a quick gameplay summary.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.card_schema import CardType, card_spec_from_dict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate a Mythic Clash v1 deck list.")
    parser.add_argument("--pack", required=True, help="Path to a card pack JSON file.")
    parser.add_argument("--deck", required=True, help="Path to a deck JSON file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pack_path = Path(args.pack)
    deck_path = Path(args.deck)

    pack_payload = json.loads(pack_path.read_text(encoding="utf-8"))
    deck_payload = json.loads(deck_path.read_text(encoding="utf-8"))

    cards_by_id = {}
    for payload in pack_payload["cards"]:
        card = card_spec_from_dict(payload)
        cards_by_id[card.id] = card

    hero_id = deck_payload["hero_id"]
    if hero_id not in cards_by_id:
        raise ValueError(f"Hero {hero_id} is not present in the supplied pack.")

    hero = cards_by_id[hero_id]
    if hero.card_type != CardType.HERO:
        raise ValueError(f"Deck hero {hero_id} is not a hero card.")

    counts = Counter()
    curve = Counter()
    card_names = []
    copies_ok = True

    for entry in deck_payload["cards"]:
        card = cards_by_id.get(entry["id"])
        if card is None:
            raise ValueError(f"Deck references missing card id {entry['id']}.")
        count = entry["count"]
        counts[card.card_type] += count
        if card.cost is not None:
            curve[card.cost] += count
        card_names.append((card.name, count))
        max_copies = 1 if card.legendary or card.unique else 2
        if count > max_copies:
            copies_ok = False

    total_main = sum(entry["count"] for entry in deck_payload["cards"])
    primary_culture_cards = sum(
        entry["count"]
        for entry in deck_payload["cards"]
        if cards_by_id[entry["id"]].culture_slug == hero.culture_slug
    )

    errors = []
    if total_main != 24:
        errors.append(f"Deck contains {total_main} main-deck cards instead of 24.")
    if counts[CardType.FIGURE] < 14:
        errors.append(f"Deck has only {counts[CardType.FIGURE]} figures; minimum is 14.")
    if counts[CardType.SPELL] > 8:
        errors.append(f"Deck has {counts[CardType.SPELL]} spells; maximum is 8.")
    if counts[CardType.RELIC] > 2:
        errors.append(f"Deck has {counts[CardType.RELIC]} relics; maximum is 2.")
    if primary_culture_cards < 12:
        errors.append(f"Deck has only {primary_culture_cards} cards from the primary culture.")
    if not copies_ok:
        errors.append("One or more cards exceed the allowed copy limit.")

    average_cost = round(sum(cost * count for cost, count in curve.items()) / total_main, 2) if total_main else 0
    summary = {
        "deck_name": deck_payload["name"],
        "hero": hero.name,
        "valid": not errors,
        "errors": errors,
        "main_deck_cards": total_main,
        "primary_culture_cards": primary_culture_cards,
        "type_counts": {str(key): value for key, value in counts.items()},
        "mana_curve": {str(key): curve[key] for key in sorted(curve)},
        "average_cost": average_cost,
        "card_list": [f"{count}x {name}" for name, count in card_names],
    }

    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
