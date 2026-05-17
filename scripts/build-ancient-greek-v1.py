"""
Build the first curated v1 card pack for Ancient Greek.

This is intentionally a manual translation pass from the current figure roster
into the structured card schema and exact-rules direction.
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
    EffectSpec,
    EffectKind,
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
        culture_slug="ancient-greek",
        rarity=rarity,
        alignment=alignment,
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        subtypes=[subtype],
        keywords=keywords or [],
        unique=rarity == "legendary",
        legendary=rarity == "legendary",
        set_code="ancient-greek-v1",
        attack=attack,
        health=health,
        abilities=abilities or [],
    )
    card.validate()
    return card


def token_figure(
    *,
    id: str,
    name: str,
    attack: int,
    health: int,
    subtype: str,
    traits: list[str],
    rules_text: str = "",
    keywords: list[str] | None = None,
    abilities: list[AbilitySpec] | None = None,
) -> CardSpec:
    card = CardSpec(
        id=id,
        name=name,
        card_type=CardType.TOKEN,
        culture_slug="ancient-greek",
        rarity="token",
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=0,
        subtypes=[subtype],
        keywords=keywords or [],
        token=True,
        collectible=False,
        set_code="ancient-greek-v1",
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
        culture_slug="ancient-greek",
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        speed=speed,
        set_code="ancient-greek-v1",
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
        culture_slug="ancient-greek",
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        set_code="ancient-greek-v1",
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
        culture_slug="ancient-greek",
        rarity="legendary",
        alignment="light",
        traits=traits,
        rules_text=rules_text,
        unique=True,
        legendary=True,
        set_code="ancient-greek-v1",
        abilities=abilities,
    )
    card.validate()
    return card


def build_pack() -> tuple[dict[str, object], dict[str, object]]:
    cards: list[CardSpec] = [
        hero(
            id="ancient-greek-hero-athena-parthenos",
            name="Athena Parthenos",
            traits=["wisdom", "war", "strategy", "protection"],
            rules_text="Hero Power - Strategic Counsel (2): Give a friendly Figure +1 Attack and Guard this turn.",
            abilities=[
                ability(
                    id="ancient-greek-hero-athena-parthenos-1",
                    label="Strategic Counsel",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=1, duration="turn"),
                        effect(EffectKind.GRANT_KEYWORD, keyword="guard", duration="turn"),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        figure(
            id="ancient-greek-001",
            name="Zeus",
            cost=6,
            attack=5,
            health=7,
            rarity="legendary",
            alignment="neutral",
            subtype="god",
            traits=["sky", "thunder", "kingship", "justice"],
            rules_text="On play: Deal 3 damage to an enemy Figure. If it dies this turn, deal 2 damage to the enemy Hero.",
            abilities=[
                ability(
                    id="ancient-greek-001-1",
                    label="Thunderbolt Edict",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=3),
                        effect(EffectKind.MARK_TARGET, extra={"follow_up_damage_to_enemy_hero": 2}),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-002",
            name="Athena, Battlefield Sage",
            cost=5,
            attack=4,
            health=7,
            rarity="legendary",
            alignment="light",
            subtype="goddess",
            traits=["wisdom", "war", "crafts", "strategy"],
            rules_text="Ward. On play: Give another friendly Figure +1/+2 and Guard this turn.",
            keywords=["ward"],
            abilities=[
                ability(
                    id="ancient-greek-002-1",
                    label="Aegis Guidance",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=1, health=2, duration="turn"),
                        effect(EffectKind.GRANT_KEYWORD, keyword="guard", duration="turn"),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-003",
            name="Poseidon",
            cost=5,
            attack=4,
            health=7,
            rarity="rare",
            alignment="neutral",
            subtype="god",
            traits=["sea", "earthquakes", "horses"],
            rules_text="On play: Deal 2 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="ancient-greek-003-1",
                    label="Earth-Shaker",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ALL_ENEMY_FIGURES,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        figure(
            id="ancient-greek-004",
            name="Hades",
            cost=4,
            attack=4,
            health=6,
            rarity="rare",
            alignment="dark",
            subtype="god",
            traits=["underworld", "death", "wealth"],
            rules_text="On play: Return a friendly non-Legendary Figure that costs 3 or less from your discard to your hand.",
            abilities=[
                ability(
                    id="ancient-greek-004-1",
                    label="Helm of Invisibility",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="friendly_discard_figure",
                    effects=[
                        effect(
                            EffectKind.RETURN_FROM_DISCARD,
                            extra={"max_cost": 3, "legendary_allowed": False},
                        )
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-005",
            name="Apollo",
            cost=4,
            attack=4,
            health=5,
            rarity="rare",
            alignment="light",
            subtype="god",
            traits=["sun", "prophecy", "music", "healing"],
            rules_text="On play: Deal 3 damage to an enemy Figure. Restore 3 Health to your Hero or another friendly Figure.",
            abilities=[
                ability(
                    id="ancient-greek-005-1",
                    label="Silver Bow",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=3),
                        effect(EffectKind.HEAL, amount=3, scope="friendly_character"),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-006",
            name="Artemis",
            cost=4,
            attack=4,
            health=4,
            rarity="rare",
            alignment="neutral",
            subtype="goddess",
            traits=["hunt", "moon", "wilderness"],
            rules_text="Rush. On play: Deal 2 damage to an enemy Figure.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="ancient-greek-006-1",
                    label="Moonsilver Arrow",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        figure(
            id="ancient-greek-007",
            name="Hermes",
            cost=2,
            attack=2,
            health=3,
            rarity="rare",
            alignment="neutral",
            subtype="god",
            traits=["messengers", "travel", "thieves", "commerce"],
            rules_text="On play: Ready another friendly Figure. Give it +1 Attack this combat.",
            abilities=[
                ability(
                    id="ancient-greek-007-1",
                    label="Winged Sandals",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.READY),
                        effect(EffectKind.GRANT_STATS, attack=1, duration="combat"),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-008",
            name="Ares",
            cost=3,
            attack=4,
            health=4,
            rarity="uncommon",
            alignment="dark",
            subtype="god",
            traits=["war", "bloodshed", "violence"],
            rules_text="When Ares attacks, he gets +2 Attack this combat.",
            abilities=[
                ability(
                    id="ancient-greek-008-1",
                    label="Battle Frenzy",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="combat")],
                )
            ],
        ),
        figure(
            id="ancient-greek-009",
            name="Aphrodite",
            cost=2,
            attack=1,
            health=4,
            rarity="uncommon",
            alignment="light",
            subtype="goddess",
            traits=["love", "beauty", "desire"],
            rules_text="On play: An enemy Figure can't attack next turn. Restore 2 Health to your Hero.",
            abilities=[
                ability(
                    id="ancient-greek-009-1",
                    label="Golden Apple",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.SET_CANT_ATTACK, duration="next_turn"),
                        effect(EffectKind.HEAL, amount=2, scope="friendly_hero"),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-010",
            name="Hephaestus",
            cost=3,
            attack=3,
            health=5,
            rarity="uncommon",
            alignment="neutral",
            subtype="god",
            traits=["fire", "forge", "crafts"],
            rules_text="On play: Give a friendly Figure +1/+2. If it has no keywords, give it Guard.",
            abilities=[
                ability(
                    id="ancient-greek-010-1",
                    label="Divine Forgefire",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=1, health=2, duration="permanent"),
                        effect(EffectKind.GRANT_KEYWORD, keyword="guard", duration="permanent", extra={"if_target_has_no_keywords": True}),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-011",
            name="Dionysus",
            cost=2,
            attack=2,
            health=3,
            rarity="uncommon",
            alignment="neutral",
            subtype="god",
            traits=["wine", "theatre", "celebration"],
            rules_text="On play: Draw a card. Exhaust an enemy Figure.",
            abilities=[
                ability(
                    id="ancient-greek-011-1",
                    label="Sacred Frenzy",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DRAW_CARDS, amount=1),
                        effect(EffectKind.EXHAUST),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-012",
            name="Demeter",
            cost=3,
            attack=3,
            health=4,
            rarity="uncommon",
            alignment="light",
            subtype="goddess",
            traits=["harvest", "fertility", "seasons"],
            rules_text="On play: Restore 4 Health to your Hero. If you have an empty slot, summon a 1/1 Seedling with Guard.",
            abilities=[
                ability(
                    id="ancient-greek-012-1",
                    label="Harvest Boon",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_HERO,
                    effects=[
                        effect(EffectKind.HEAL, amount=4),
                        effect(
                            EffectKind.SUMMON_TOKEN,
                            card_id="ancient-greek-token-seedling",
                            extra={"if_empty_slot": True},
                        ),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-013",
            name="Herakles",
            cost=5,
            attack=5,
            health=6,
            rarity="rare",
            alignment="neutral",
            subtype="hero",
            traits=["strength", "heroism", "endurance"],
            rules_text="Rush. The first damage Herakles takes each turn is reduced by 2.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="ancient-greek-013-1",
                    label="Twelve Labors",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_DAMAGE_TAKEN,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.PREVENT_DAMAGE, amount=2)],
                    limit="once_each_turn",
                )
            ],
        ),
        figure(
            id="ancient-greek-014",
            name="Achilles",
            cost=4,
            attack=5,
            health=4,
            rarity="rare",
            alignment="neutral",
            subtype="hero",
            traits=["war", "speed", "glory", "tragedy"],
            rules_text="Rush. When Achilles strikes an enemy Figure, deal 2 damage to the enemy Hero.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="ancient-greek-014-1",
                    label="Aristeia",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_STRIKE,
                    target_rule=TargetRule.ENEMY_HERO,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                    conditions=[{"kind": "if_struck_figure"}],
                )
            ],
        ),
        figure(
            id="ancient-greek-015",
            name="Prometheus",
            cost=4,
            attack=3,
            health=5,
            rarity="rare",
            alignment="light",
            subtype="titan",
            traits=["fire", "knowledge", "defiance"],
            rules_text="On play: Gain 1 Ritual Mana. Draw a card.",
            abilities=[
                ability(
                    id="ancient-greek-015-1",
                    label="Stolen Fire",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[
                        effect(EffectKind.GAIN_RITUAL_MANA, amount=1),
                        effect(EffectKind.DRAW_CARDS, amount=1),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-016",
            name="Typhon",
            cost=7,
            attack=7,
            health=7,
            rarity="legendary",
            alignment="dark",
            subtype="monster",
            traits=["chaos", "storms", "destruction"],
            rules_text="On play: Deal 2 damage to all other characters.",
            abilities=[
                ability(
                    id="ancient-greek-016-1",
                    label="Hundredfold Assault",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_other_characters",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        figure(
            id="ancient-greek-017",
            name="Medusa",
            cost=3,
            attack=3,
            health=4,
            rarity="uncommon",
            alignment="dark",
            subtype="monster",
            traits=["petrification", "serpents", "death"],
            rules_text="On play: Silence an enemy Figure and Freeze it.",
            abilities=[
                ability(
                    id="ancient-greek-017-1",
                    label="Stone Gaze",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.SILENCE),
                        effect(EffectKind.FREEZE),
                    ],
                )
            ],
        ),
        figure(
            id="ancient-greek-018",
            name="Cerberus",
            cost=3,
            attack=3,
            health=5,
            rarity="uncommon",
            alignment="dark",
            subtype="beast",
            traits=["underworld", "guardianship"],
            rules_text="Guard. On play: Freeze an enemy Figure with 3 or less Attack.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="ancient-greek-018-1",
                    label="Three-Headed Watch",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.FREEZE)],
                    conditions=[{"kind": "if_target_attack_at_most", "value": 3}],
                )
            ],
        ),
        figure(
            id="ancient-greek-019",
            name="Chimera",
            cost=2,
            attack=3,
            health=2,
            rarity="common",
            alignment="dark",
            subtype="monster",
            traits=["fire", "chaos", "hybrid"],
            rules_text="Poisonous. On play: Deal 1 damage to any character.",
            keywords=["poisonous"],
            abilities=[
                ability(
                    id="ancient-greek-019-1",
                    label="Tri-Form Breath",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ANY_CHARACTER,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)],
                )
            ],
        ),
        figure(
            id="ancient-greek-020",
            name="Minotaur",
            cost=3,
            attack=4,
            health=4,
            rarity="common",
            alignment="dark",
            subtype="monster",
            traits=["labyrinth", "sacrifice", "duality"],
            rules_text="Charge. On play: Deal 2 damage to an enemy Figure.",
            keywords=["charge"],
            abilities=[
                ability(
                    id="ancient-greek-020-1",
                    label="Labyrinth Charge",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        token_figure(
            id="ancient-greek-token-seedling",
            name="Seedling Guardian",
            attack=1,
            health=1,
            subtype="spirit",
            traits=["harvest", "fertility"],
            rules_text="Guard.",
            keywords=["guard"],
        ),
        spell(
            id="ancient-greek-spell-delphic-counsel",
            name="Delphic Counsel",
            cost=2,
            speed=Speed.SLOW,
            rarity="common",
            traits=["prophecy", "wisdom"],
            rules_text="Look at the top 3 cards of your deck. Put one into your hand. Give a friendly Figure +1/+1.",
            abilities=[
                ability(
                    id="ancient-greek-spell-delphic-counsel-1",
                    label="Delphic Counsel",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.DISCOVER_FROM_POOL, amount=1, pool="top_3_deck"),
                        effect(EffectKind.GRANT_STATS, attack=1, health=1, duration="turn"),
                    ],
                )
            ],
        ),
        spell(
            id="ancient-greek-spell-phalanx-formation",
            name="Phalanx Formation",
            cost=2,
            speed=Speed.FAST,
            rarity="common",
            traits=["war", "discipline"],
            rules_text="Give a friendly Figure +2/+2 this combat. If it has Guard, Ready it.",
            abilities=[
                ability(
                    id="ancient-greek-spell-phalanx-formation-1",
                    label="Phalanx Formation",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=2, health=2, duration="combat"),
                        effect(EffectKind.READY, extra={"if_target_has_keyword": "guard"}),
                    ],
                )
            ],
        ),
        spell(
            id="ancient-greek-spell-olympian-judgment",
            name="Olympian Judgment",
            cost=4,
            speed=Speed.SLOW,
            rarity="rare",
            traits=["thunder", "justice"],
            rules_text="Deal 4 damage to an enemy Figure. If you control a Guard or Legendary Figure, deal 6 instead.",
            abilities=[
                ability(
                    id="ancient-greek-spell-olympian-judgment-1",
                    label="Olympian Judgment",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=4),
                        effect(
                            EffectKind.DEAL_DAMAGE,
                            amount=2,
                            extra={"if_you_control_keyword": "guard", "or_if_you_control_rarity": "legendary"},
                        ),
                    ],
                )
            ],
        ),
        relic(
            id="ancient-greek-relic-aegis-of-athena",
            name="Aegis of Athena",
            cost=3,
            rarity="rare",
            traits=["protection", "strategy"],
            rules_text="Once each turn, the first time you target a friendly Figure with a spell or hero power, give it Ward this turn.",
            abilities=[
                ability(
                    id="ancient-greek-relic-aegis-of-athena-1",
                    label="Aegis of Athena",
                    timing=AbilityTiming.PASSIVE,
                    trigger="on_friendly_targeted_by_spell_or_hero_power",
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")],
                    limit="once_each_turn",
                )
            ],
        ),
    ]

    pack = {
        "set_code": "ancient-greek-v1",
        "culture_slug": "ancient-greek",
        "primary_family": "Vanguard",
        "secondary_family": "Oracle",
        "hero_id": "ancient-greek-hero-athena-parthenos",
        "notes": [
            "First manual translation pass from the current figure roster into the exact-rules v1 card schema.",
            "Designed to preserve Greek tactical-combat identity while retiring the old five-stat ability language.",
        ],
        "cards": [dataclass_to_dict(card) for card in cards],
    }

    deck = {
        "name": "Athena Midrange",
        "format": "mythic-clash-v1",
        "hero_id": "ancient-greek-hero-athena-parthenos",
        "notes": [
            "Board-first mono-culture deck used to test whether the translated Greek package feels readable and coherent.",
            "Leans on cheap disruptive figures, tactical buffs, and a few precise top-end legends.",
        ],
        "cards": [
            {"id": "ancient-greek-011", "count": 2},
            {"id": "ancient-greek-019", "count": 2},
            {"id": "ancient-greek-020", "count": 2},
            {"id": "ancient-greek-008", "count": 2},
            {"id": "ancient-greek-010", "count": 2},
            {"id": "ancient-greek-005", "count": 2},
            {"id": "ancient-greek-017", "count": 2},
            {"id": "ancient-greek-002", "count": 1},
            {"id": "ancient-greek-004", "count": 1},
            {"id": "ancient-greek-014", "count": 1},
            {"id": "ancient-greek-001", "count": 1},
            {"id": "ancient-greek-spell-delphic-counsel", "count": 2},
            {"id": "ancient-greek-spell-phalanx-formation", "count": 2},
            {"id": "ancient-greek-spell-olympian-judgment", "count": 1},
            {"id": "ancient-greek-relic-aegis-of-athena", "count": 1},
        ],
    }
    return pack, deck


def main() -> None:
    pack, deck = build_pack()
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    DECKS_DIR.mkdir(parents=True, exist_ok=True)

    pack_path = CARDS_DIR / "ancient-greek-v1.json"
    deck_path = DECKS_DIR / "ancient-greek-athena-midrange.json"
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
