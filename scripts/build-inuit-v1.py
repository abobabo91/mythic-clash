"""
Build the first curated v1 card pack for Inuit.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.card_schema import (
    AbilitySpec,
    AbilityTiming,
    AbilityTrigger,
    CardSpec,
    CardType,
    EffectKind,
    EffectSpec,
    Speed,
    TargetRule,
    dataclass_to_dict,
)


CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"


def ability(
    *,
    id: str,
    label: str,
    timing: AbilityTiming | str,
    trigger: AbilityTrigger | str,
    target_rule: TargetRule | str,
    effects: list[EffectSpec],
    resource_cost: int | None = None,
    conditions: list[dict[str, object]] | None = None,
    limit: str | None = None,
) -> AbilitySpec:
    return AbilitySpec(
        id=id,
        label=label,
        timing=timing,
        trigger=trigger,
        target_rule=target_rule,
        resource_cost=resource_cost,
        conditions=[] if conditions is None else conditions,  # type: ignore[arg-type]
        effects=effects,
        limit=limit,
    )


def effect(kind: EffectKind | str, **kwargs: object) -> EffectSpec:
    payload = dict(kwargs)
    payload.setdefault("extra", {})
    return EffectSpec(kind=kind, **payload)


def figure(
    *,
    id: str,
    name: str,
    cost: int,
    attack: int,
    health: int,
    rarity: str,
    alignment: str,
    subtype: str,
    traits: list[str],
    rules_text: str,
    keywords: list[str] | None = None,
    abilities: list[AbilitySpec] | None = None,
) -> CardSpec:
    card = CardSpec(
        id=id,
        name=name,
        card_type=CardType.FIGURE,
        culture_slug="inuit",
        rarity=rarity,
        alignment=alignment,
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        subtypes=[subtype],
        keywords=keywords or [],
        unique=rarity == "legendary",
        legendary=rarity == "legendary",
        set_code="inuit-v1",
        attack=attack,
        health=health,
        abilities=abilities or [],
    )
    card.validate()
    return card


def spell(
    *,
    id: str,
    name: str,
    cost: int,
    speed: Speed,
    rarity: str,
    traits: list[str],
    rules_text: str,
    abilities: list[AbilitySpec],
) -> CardSpec:
    card = CardSpec(
        id=id,
        name=name,
        card_type=CardType.SPELL,
        culture_slug="inuit",
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        speed=speed,
        set_code="inuit-v1",
        abilities=abilities,
    )
    card.validate()
    return card


def relic(
    *,
    id: str,
    name: str,
    cost: int,
    rarity: str,
    traits: list[str],
    rules_text: str,
    abilities: list[AbilitySpec],
) -> CardSpec:
    card = CardSpec(
        id=id,
        name=name,
        card_type=CardType.RELIC,
        culture_slug="inuit",
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        set_code="inuit-v1",
        unique=rarity == "legendary",
        legendary=rarity == "legendary",
        abilities=abilities,
    )
    card.validate()
    return card


def hero(
    *,
    id: str,
    name: str,
    traits: list[str],
    rules_text: str,
    abilities: list[AbilitySpec],
) -> CardSpec:
    card = CardSpec(
        id=id,
        name=name,
        card_type=CardType.HERO,
        culture_slug="inuit",
        rarity="legendary",
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        unique=True,
        legendary=True,
        set_code="inuit-v1",
        abilities=abilities,
    )
    card.validate()
    return card


def build_pack() -> tuple[dict[str, object], dict[str, object]]:
    cards: list[CardSpec] = [
        hero(
            id="inuit-hero-sedna",
            name="Sedna, Queen Below",
            traits=["sea", "underworld", "water", "animal"],
            rules_text="Hero Power - Tidal Seizure (2): Exhaust an enemy Figure. If it is already damaged, return it to its owner's hand instead.",
            abilities=[
                ability(
                    id="inuit-hero-sedna-1",
                    label="Tidal Seizure",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.EXHAUST),
                        effect(EffectKind.RETURN_TO_HAND, extra={"if_target_is_damaged": True}),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        figure(
            id="inuit-001",
            name="Sedna",
            cost=5,
            attack=4,
            health=7,
            rarity="legendary",
            alignment="dark",
            subtype="spirit",
            traits=["sea", "underworld", "animal", "water"],
            rules_text="On play: Exhaust an enemy Figure. If it is already damaged, return it to its owner's hand instead.",
            abilities=[
                ability(
                    id="inuit-001-1",
                    label="Ocean's Claim",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.EXHAUST),
                        effect(EffectKind.RETURN_TO_HAND, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        figure(
            id="inuit-002",
            name="Nanook",
            cost=5,
            attack=5,
            health=6,
            rarity="legendary",
            alignment="light",
            subtype="beast",
            traits=["animal", "ice", "hunting", "survival"],
            rules_text="Charge. When Nanook attacks, he gets +1 Attack this combat.",
            keywords=["charge"],
            abilities=[
                ability(
                    id="inuit-002-1",
                    label="Primal Charge",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, duration="combat")],
                )
            ],
        ),
        figure(
            id="inuit-003",
            name="Sila",
            cost=4,
            attack=3,
            health=6,
            rarity="rare",
            alignment="neutral",
            subtype="spirit",
            traits=["sky", "wind", "spirit", "wisdom"],
            rules_text="On play: Draw a card. Gain 1 Ritual Mana.",
            abilities=[
                ability(
                    id="inuit-003-1",
                    label="Vault of Heaven",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[
                        effect(EffectKind.DRAW_CARDS, amount=1),
                        effect(EffectKind.GAIN_RITUAL_MANA, amount=1),
                    ],
                )
            ],
        ),
        figure(
            id="inuit-004",
            name="Anguta",
            cost=4,
            attack=4,
            health=6,
            rarity="rare",
            alignment="dark",
            subtype="spirit",
            traits=["underworld", "death", "judgment", "sea"],
            rules_text="Reborn. On play: Deal 2 damage to a damaged enemy Figure.",
            keywords=["reborn"],
            abilities=[
                ability(
                    id="inuit-004-1",
                    label="Chthonic Gate",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        figure(
            id="inuit-005",
            name="Pinga",
            cost=4,
            attack=4,
            health=6,
            rarity="rare",
            alignment="light",
            subtype="spirit",
            traits=["hunting", "fertility", "animal", "protection"],
            rules_text="Guard. On play: Another friendly Figure gets +1/+2 this turn.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="inuit-005-1",
                    label="Hunter's Mark",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, health=2, duration="turn")],
                )
            ],
        ),
        figure(
            id="inuit-006",
            name="Qalupalik",
            cost=3,
            attack=4,
            health=4,
            rarity="rare",
            alignment="dark",
            subtype="monster",
            traits=["sea", "monster", "night", "fear"],
            rules_text="Rush. On play: Exhaust an enemy Figure.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="inuit-006-1",
                    label="Ocean's Claim",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.EXHAUST)],
                )
            ],
        ),
        figure(
            id="inuit-007",
            name="Mahaha",
            cost=3,
            attack=4,
            health=3,
            rarity="rare",
            alignment="dark",
            subtype="monster",
            traits=["ice", "trickster", "monster", "night"],
            rules_text="On play: Freeze an enemy Figure. If it is already damaged, deal 1 damage to it.",
            abilities=[
                ability(
                    id="inuit-007-1",
                    label="Clever Reversal",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.FREEZE),
                        effect(EffectKind.DEAL_DAMAGE, amount=1, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        figure(
            id="inuit-008",
            name="Tornarsuk",
            cost=3,
            attack=3,
            health=5,
            rarity="rare",
            alignment="neutral",
            subtype="spirit",
            traits=["spirit", "strength", "protection", "night"],
            rules_text="Guard. The first damage Tornarsuk takes each turn is reduced by 2.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="inuit-008-1",
                    label="Otherworld Touch",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_DAMAGE_TAKEN,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.PREVENT_DAMAGE, amount=2)],
                    limit="once_each_turn",
                )
            ],
        ),
        figure(
            id="inuit-009",
            name="Ijiraq",
            cost=2,
            attack=2,
            health=3,
            rarity="uncommon",
            alignment="neutral",
            subtype="spirit",
            traits=["shapechanging", "speed", "ice", "mystery"],
            rules_text="Rush. On play: Give a friendly Figure Ward this turn.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="inuit-009-1",
                    label="Mythic Presence",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")],
                )
            ],
        ),
        figure(
            id="inuit-010",
            name="Amarok",
            cost=4,
            attack=5,
            health=4,
            rarity="uncommon",
            alignment="dark",
            subtype="beast",
            traits=["wolf", "animal", "night", "hunting"],
            rules_text="Charge.",
            keywords=["charge"],
        ),
        figure(
            id="inuit-011",
            name="Akhlut",
            cost=3,
            attack=3,
            health=5,
            rarity="uncommon",
            alignment="neutral",
            subtype="monster",
            traits=["sea", "wolf", "shapechanging", "water"],
            rules_text="On play: Return a damaged enemy Figure that costs 2 or less to its owner's hand.",
            abilities=[
                ability(
                    id="inuit-011-1",
                    label="Ocean's Claim",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 2})],
                )
            ],
        ),
        figure(
            id="inuit-012",
            name="Adlet",
            cost=3,
            attack=4,
            health=4,
            rarity="uncommon",
            alignment="dark",
            subtype="monster",
            traits=["monster", "dog", "war", "snow"],
            rules_text="When Adlet attacks, it gets +2 Attack this combat.",
            abilities=[
                ability(
                    id="inuit-012-1",
                    label="Battle Surge",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="combat")],
                )
            ],
        ),
        figure(
            id="inuit-013",
            name="Aningan",
            cost=3,
            attack=2,
            health=5,
            rarity="uncommon",
            alignment="light",
            subtype="spirit",
            traits=["moon", "night", "sky", "cycle"],
            rules_text="On play: Restore 3 Health to your Hero. Draw a card.",
            abilities=[
                ability(
                    id="inuit-013-1",
                    label="Moonlit Veil",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_HERO,
                    effects=[
                        effect(EffectKind.HEAL, amount=3),
                        effect(EffectKind.DRAW_CARDS, amount=1),
                    ],
                )
            ],
        ),
        figure(
            id="inuit-014",
            name="Malina",
            cost=4,
            attack=3,
            health=6,
            rarity="uncommon",
            alignment="light",
            subtype="spirit",
            traits=["sun", "light", "sky", "flight"],
            rules_text="On play: Deal 3 damage to an enemy Figure. If it was already damaged, deal 1 more.",
            abilities=[
                ability(
                    id="inuit-014-1",
                    label="Solar Ascendance",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=3),
                        effect(EffectKind.DEAL_DAMAGE, amount=1, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        figure(
            id="inuit-015",
            name="Pana",
            cost=2,
            attack=2,
            health=4,
            rarity="common",
            alignment="neutral",
            subtype="spirit",
            traits=["ice", "music", "night", "spirit"],
            rules_text="On play: Gain 1 Ritual Mana.",
            abilities=[
                ability(
                    id="inuit-015-1",
                    label="Otherworld Touch",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.GAIN_RITUAL_MANA, amount=1)],
                )
            ],
        ),
        figure(
            id="inuit-016",
            name="Tekkeitsertok",
            cost=3,
            attack=4,
            health=5,
            rarity="common",
            alignment="light",
            subtype="hunter",
            traits=["animal", "hunting", "strength", "protection"],
            rules_text="Guard. Rush.",
            keywords=["guard", "rush"],
        ),
        figure(
            id="inuit-017",
            name="Tupilak",
            cost=3,
            attack=3,
            health=4,
            rarity="common",
            alignment="dark",
            subtype="monster",
            traits=["monster", "magic", "revenge", "water"],
            rules_text="Ward. On play: Deal 1 damage to any character.",
            keywords=["ward"],
            abilities=[
                ability(
                    id="inuit-017-1",
                    label="Tidal Ward",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ANY_CHARACTER,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)],
                )
            ],
        ),
        figure(
            id="inuit-018",
            name="Torngarsuk",
            cost=2,
            attack=2,
            health=4,
            rarity="common",
            alignment="neutral",
            subtype="spirit",
            traits=["spirit", "guardian", "night", "power"],
            rules_text="Guard.",
            keywords=["guard"],
        ),
        figure(
            id="inuit-019",
            name="Kiviuq",
            cost=3,
            attack=3,
            health=5,
            rarity="common",
            alignment="neutral",
            subtype="hero",
            traits=["voyage", "sea", "survival", "quest"],
            rules_text="On play: Return a damaged enemy Figure that costs 3 or less to its owner's hand.",
            abilities=[
                ability(
                    id="inuit-019-1",
                    label="Ocean's Claim",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 3})],
                )
            ],
        ),
        figure(
            id="inuit-020",
            name="Polar Bear Ancestor",
            cost=4,
            attack=4,
            health=6,
            rarity="uncommon",
            alignment="light",
            subtype="ancestor",
            traits=["animal", "ice", "strength", "protection"],
            rules_text="Guard. On play: Another friendly Figure gets +1/+1.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="inuit-020-1",
                    label="Primal Charge",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, health=1, duration="permanent")],
                )
            ],
        ),
        spell(
            id="inuit-spell-iceflow-ambush",
            name="Iceflow Ambush",
            cost=2,
            speed=Speed.FAST,
            rarity="common",
            traits=["ice", "sea", "ambush"],
            rules_text="Exhaust an enemy Figure. If it is already damaged, return it to its owner's hand instead.",
            abilities=[
                ability(
                    id="inuit-spell-iceflow-ambush-1",
                    label="Iceflow Ambush",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.EXHAUST),
                        effect(EffectKind.RETURN_TO_HAND, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        spell(
            id="inuit-spell-hunters-trail",
            name="Hunter's Trail",
            cost=2,
            speed=Speed.FAST,
            rarity="common",
            traits=["hunting", "survival"],
            rules_text="Give a friendly Figure +2/+1 this combat. Ready it.",
            abilities=[
                ability(
                    id="inuit-spell-hunters-trail-1",
                    label="Hunter's Trail",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=2, health=1, duration="combat"),
                        effect(EffectKind.READY),
                    ],
                )
            ],
        ),
        spell(
            id="inuit-spell-white-horizon",
            name="White Horizon",
            cost=3,
            speed=Speed.SLOW,
            rarity="rare",
            traits=["sky", "ice", "wisdom"],
            rules_text="Draw 2 cards.",
            abilities=[
                ability(
                    id="inuit-spell-white-horizon-1",
                    label="White Horizon",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DRAW_CARDS, amount=2)],
                )
            ],
        ),
        relic(
            id="inuit-relic-harpoon-rack",
            name="Harpoon Rack",
            cost=2,
            rarity="rare",
            traits=["hunting", "war", "craft"],
            rules_text="The first friendly Figure that attacks each turn gets +1 Attack this combat.",
            abilities=[
                ability(
                    id="inuit-relic-harpoon-rack-1",
                    label="Harpoon Rack",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, duration="combat")],
                    limit="once_each_turn",
                )
            ],
        ),
    ]

    pack = {
        "set_code": "inuit-v1",
        "culture_slug": "inuit",
        "primary_family": "Tidebound",
        "secondary_family": "Vanguard",
        "hero_id": "inuit-hero-sedna",
        "notes": [
            "Third manual translation pass from the current figure roster into the exact-rules v1 card schema.",
            "Designed to preserve Inuit tempo-control and hunting pressure while keeping the gameplay language readable.",
        ],
        "cards": [dataclass_to_dict(card) for card in cards],
    }
    deck = {
        "name": "Sedna Tidehunt",
        "format": "mythic-clash-v1",
        "hero_id": "inuit-hero-sedna",
        "notes": [
            "Mono-culture sample deck for checking whether Inuit plays as a readable tide-tempo deck with a hunting edge.",
            "Leans on early tempo bodies, exhaust and bounce effects, and efficient attack-based closes.",
        ],
        "cards": [
            {"id": "inuit-009", "count": 2},
            {"id": "inuit-015", "count": 2},
            {"id": "inuit-006", "count": 2},
            {"id": "inuit-007", "count": 2},
            {"id": "inuit-011", "count": 2},
            {"id": "inuit-012", "count": 2},
            {"id": "inuit-016", "count": 2},
            {"id": "inuit-019", "count": 2},
            {"id": "inuit-002", "count": 1},
            {"id": "inuit-001", "count": 1},
            {"id": "inuit-spell-iceflow-ambush", "count": 2},
            {"id": "inuit-spell-hunters-trail", "count": 2},
            {"id": "inuit-spell-white-horizon", "count": 1},
            {"id": "inuit-relic-harpoon-rack", "count": 1},
        ],
    }
    return pack, deck


def main() -> None:
    pack, deck = build_pack()
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    DECKS_DIR.mkdir(parents=True, exist_ok=True)

    pack_path = CARDS_DIR / "inuit-v1.json"
    deck_path = DECKS_DIR / "inuit-sedna-tidehunt.json"
    pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    deck_path.write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        json.dumps(
            {
                "pack": str(pack_path),
                "deck": str(deck_path),
                "cards": len(pack["cards"]),
                "collectible_non_hero_cards": sum(
                    1 for card in pack["cards"] if card["card_type"] != "hero" and card.get("collectible", True)
                ),
                "sample_deck_cards": sum(entry["count"] for entry in deck["cards"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
