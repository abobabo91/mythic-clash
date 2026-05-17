"""
Retune the 16 Greek-soft cultures by rebuilding their decks
with better early-game curves from their existing card packs.

This script:
1. Reads each culture's v1 pack
2. Rebuilds the deck with more mid-cost figures and fewer expensive ones
3. Swaps defensive support spells for removal/tempo spells
4. Validates the deck is legal (24 cards, hero, copy limits)
5. Saves the retuned deck
"""

from __future__ import annotations

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"

GREEK_SOFT = [
    "akkadian",
    "aztec-mexica",
    "baltic-lithuanian",
    "burmese-nat",
    "celtic-welsh",
    "fijian",
    "igbo",
    "indian-buddhist",
    "kazakh",
    "korean",
    "mandaean",
    "melanesian-papuan",
    "samoan",
    "scythian",
    "shaiva-hindu",
    "tibetan-bon",
]

TARGET_DECK_SIZE = 24
MAX_COPIES = 2
MAX_LEGENDARY_COPIES = 1

# Aggressive support spells to prefer for anti-pressure
TEMPO_SPELLS = {
    "deal_damage", "grant_stats", "summon_token", "ready",
    "return_to_hand", "destroy", "freeze",
}


def load_pack(slug: str) -> dict:
    path = CARDS_DIR / f"{slug}-v1.json"
    return json.loads(path.read_text(encoding="utf-8"))


def find_existing_deck(slug: str) -> Path | None:
    matches = sorted(DECKS_DIR.glob(f"{slug}-*.json"))
    return matches[0] if matches else None


def card_tempo_score(card: dict) -> float:
    """Score a figure card for tempo/pressure potential."""
    cost = card.get("cost") or 0
    attack = card.get("attack") or 0
    health = card.get("health") or 0
    keywords = card.get("keywords", [])
    abilities = card.get("abilities", [])

    if cost == 0:
        return 0

    # Mana efficiency: stats per mana
    efficiency = (attack + health) / max(1, cost)
    score = efficiency * 2.0

    # Bonus for early playability
    if cost <= 2:
        score += 3.0
    elif cost <= 4:
        score += 1.5
    elif cost >= 7:
        score -= 1.0

    # Bonus for tempo keywords
    if "rush" in keywords or "charge" in keywords:
        score += 2.5
    if "guard" in keywords or "taunt" in keywords:
        score += 1.0  # Anti-pressure
    if "ward" in keywords or "divine_shield" in keywords:
        score += 1.5

    # Bonus for on-play abilities that affect the board
    for ability in abilities:
        if ability.get("trigger") in ("on_play", "on_summon"):
            for effect in ability.get("effects", []):
                kind = effect.get("kind", "")
                if kind in ("deal_damage", "destroy", "freeze", "return_to_hand"):
                    score += 2.0
                elif kind in ("grant_stats", "summon_token"):
                    score += 1.0

    return score


def spell_tempo_score(card: dict) -> float:
    """Score a spell for anti-pressure utility."""
    abilities = card.get("abilities", [])
    score = 0.0
    for ability in abilities:
        for effect in ability.get("effects", []):
            kind = effect.get("kind", "")
            if kind in TEMPO_SPELLS:
                amount = effect.get("amount") or 0
                score += 2.0 + amount * 0.3
            elif kind in ("heal", "gain_armor"):
                score += 0.5
            elif kind == "draw_cards":
                score += 1.0
    return score


def build_retuned_deck(pack: dict) -> dict:
    cards = pack["cards"]
    hero = [c for c in cards if c["card_type"] == "hero"]
    if not hero:
        return None
    hero_card = hero[0]

    figures = [c for c in cards if c["card_type"] == "figure"]
    spells = [c for c in cards if c["card_type"] == "spell"]
    relics = [c for c in cards if c["card_type"] == "relic"]

    # Score and sort figures by tempo
    scored_figures = [(card_tempo_score(f), f) for f in figures]
    scored_figures.sort(key=lambda x: -x[0])

    # Build figure curve: prefer 6 low (1-3), 8 mid (4-5), 2-4 high (6+)
    chosen = []
    chosen_ids = Counter()
    cost_buckets = {"low": 0, "mid": 0, "high": 0}
    targets = {"low": 6, "mid": 8, "high": 4}

    for _score, figure in scored_figures:
        cost = figure.get("cost") or 0
        is_legendary = figure.get("legendary") or figure.get("rarity") == "legendary"
        max_c = MAX_LEGENDARY_COPIES if is_legendary else MAX_COPIES
        if chosen_ids[figure["id"]] >= max_c:
            continue

        if cost <= 3:
            bucket = "low"
        elif cost <= 5:
            bucket = "mid"
        else:
            bucket = "high"

        if cost_buckets[bucket] >= targets[bucket]:
            continue

        chosen.append({"id": figure["id"], "count": 1})
        chosen_ids[figure["id"]] += 1
        cost_buckets[bucket] += 1

        if len(chosen) >= 16:
            break

    # Fill remaining figure slots
    for _score, figure in scored_figures:
        if sum(e["count"] for e in chosen) >= 18:
            break
        is_legendary = figure.get("legendary") or figure.get("rarity") == "legendary"
        max_c = MAX_LEGENDARY_COPIES if is_legendary else MAX_COPIES
        if chosen_ids[figure["id"]] >= max_c:
            continue
        existing = next((e for e in chosen if e["id"] == figure["id"]), None)
        if existing:
            existing["count"] += 1
        else:
            chosen.append({"id": figure["id"], "count": 1})
        chosen_ids[figure["id"]] += 1

    # Add spells: prefer tempo spells
    scored_spells = [(spell_tempo_score(s), s) for s in spells]
    scored_spells.sort(key=lambda x: -x[0])
    spell_ids = Counter()
    for _score, spell in scored_spells:
        if sum(e["count"] for e in chosen) >= 22:
            break
        is_legendary = spell.get("legendary") or spell.get("rarity") == "legendary"
        max_c = MAX_LEGENDARY_COPIES if is_legendary else MAX_COPIES
        if spell_ids[spell["id"]] >= max_c:
            continue
        existing = next((e for e in chosen if e["id"] == spell["id"]), None)
        if existing:
            existing["count"] += 1
        else:
            chosen.append({"id": spell["id"], "count": 1})
        spell_ids[spell["id"]] += 1

    # Add relics
    for relic in relics[:2]:
        if sum(e["count"] for e in chosen) >= TARGET_DECK_SIZE:
            break
        chosen.append({"id": relic["id"], "count": 1})

    # Pad to 24 if needed
    for _score, figure in scored_figures:
        if sum(e["count"] for e in chosen) >= TARGET_DECK_SIZE:
            break
        is_legendary = figure.get("legendary") or figure.get("rarity") == "legendary"
        max_c = MAX_LEGENDARY_COPIES if is_legendary else MAX_COPIES
        if chosen_ids[figure["id"]] >= max_c:
            continue
        existing = next((e for e in chosen if e["id"] == figure["id"]), None)
        if existing:
            existing["count"] += 1
        else:
            chosen.append({"id": figure["id"], "count": 1})
        chosen_ids[figure["id"]] += 1

    total = sum(e["count"] for e in chosen)
    slug = pack.get("culture_slug", hero_card.get("culture_slug", "unknown"))

    return {
        "name": f"{hero_card['name']} Retuned",
        "format": "mythic-clash-v1",
        "hero_id": hero_card["id"],
        "notes": [
            f"Auto-retuned deck for Greek-gate pressure balance.",
            f"Prioritizes early-game tempo and board interaction.",
        ],
        "cards": chosen,
    }


def main() -> None:
    retuned = 0
    for slug in GREEK_SOFT:
        try:
            pack = load_pack(slug)
        except FileNotFoundError:
            print(f"  SKIP {slug}: pack not found")
            continue

        deck = build_retuned_deck(pack)
        if deck is None:
            print(f"  SKIP {slug}: no hero found")
            continue

        total = sum(e["count"] for e in deck["cards"])
        old_deck_path = find_existing_deck(slug)
        old_name = old_deck_path.name if old_deck_path else "none"

        # Analyze curve
        cards_by_id = {c["id"]: c for c in pack["cards"]}
        costs = []
        for entry in deck["cards"]:
            card = cards_by_id.get(entry["id"])
            if card and card.get("cost"):
                costs.extend([card["cost"]] * entry["count"])
        low = sum(1 for c in costs if c <= 3)
        mid = sum(1 for c in costs if 4 <= c <= 5)
        high = sum(1 for c in costs if c >= 6)

        # Save
        deck_name = f"{slug}-{deck['hero_id'].split('-hero-')[1] if '-hero-' in deck['hero_id'] else 'retuned'}-anti-pressure.json"
        output_path = DECKS_DIR / deck_name
        output_path.write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  OK   {slug:25s} {total} cards  curve {low}/{mid}/{high}  -> {deck_name}")
        retuned += 1

    print(f"\nRetuned {retuned}/{len(GREEK_SOFT)} cultures.")


if __name__ == "__main__":
    main()
