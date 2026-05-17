"""
Build the first curated v1 card pack for Haitian Vodou.
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
        culture_slug="haitian-vodou",
        rarity=rarity,
        alignment=alignment,
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        subtypes=[subtype],
        keywords=keywords or [],
        unique=rarity == "legendary",
        legendary=rarity == "legendary",
        set_code="haitian-vodou-v1",
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
        culture_slug="haitian-vodou",
        rarity="token",
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=0,
        subtypes=[subtype],
        keywords=keywords or [],
        token=True,
        collectible=False,
        set_code="haitian-vodou-v1",
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
        culture_slug="haitian-vodou",
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        speed=speed,
        set_code="haitian-vodou-v1",
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
        culture_slug="haitian-vodou",
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        set_code="haitian-vodou-v1",
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
        culture_slug="haitian-vodou",
        rarity="legendary",
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        unique=True,
        legendary=True,
        set_code="haitian-vodou-v1",
        abilities=abilities,
    )
    card.validate()
    return card


def build_pack() -> tuple[dict[str, object], dict[str, object]]:
    cards: list[CardSpec] = [
        hero(
            id="haitian-vodou-hero-papa-legba",
            name="Papa Legba, Keeper of Crossroads",
            traits=["spirit", "threshold", "crossroads", "wisdom"],
            rules_text="Hero Power - Crossroads Toll (2): Deal 1 damage to a friendly Figure. If it survives, draw a card.",
            abilities=[
                ability(
                    id="haitian-vodou-hero-papa-legba-1",
                    label="Crossroads Toll",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=1),
                        effect(EffectKind.DRAW_CARDS, amount=1, extra={"if_target_survived_damage": True}),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        figure(
            id="haitian-vodou-001",
            name="Papa Legba",
            cost=5,
            attack=4,
            health=7,
            rarity="legendary",
            alignment="neutral",
            subtype="loa",
            traits=["spirit", "threshold", "wisdom", "crossroads"],
            rules_text="On play: Draw a card. If a friendly Figure died this turn, gain 1 Ritual Mana.",
            abilities=[
                ability(
                    id="haitian-vodou-001-1",
                    label="Otherworld Touch",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[
                        effect(EffectKind.DRAW_CARDS, amount=1),
                        effect(EffectKind.GAIN_RITUAL_MANA, amount=1, extra={"if_friendly_died_this_turn": True}),
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-002",
            name="Baron Samedi",
            cost=6,
            attack=5,
            health=7,
            rarity="legendary",
            alignment="dark",
            subtype="loa",
            traits=["death", "underworld", "night", "spirit"],
            rules_text="Reborn. On play: Return a friendly non-Legendary Figure that costs 2 or less from your discard to the battlefield exhausted.",
            keywords=["reborn"],
            abilities=[
                ability(
                    id="haitian-vodou-002-1",
                    label="Grave Call",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="friendly_discard_figure",
                    effects=[
                        effect(
                            EffectKind.RETURN_FROM_DISCARD,
                            extra={"max_cost": 2, "legendary_allowed": False, "to_battlefield": True, "exhausted": True},
                        )
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-003",
            name="Erzulie Freda",
            cost=3,
            attack=2,
            health=5,
            rarity="rare",
            alignment="light",
            subtype="loa",
            traits=["love", "beauty", "luxury", "water"],
            rules_text="On play: Restore 3 Health to your Hero or another friendly Figure. Give it +1 Attack this turn.",
            abilities=[
                ability(
                    id="haitian-vodou-003-1",
                    label="Binding Charm",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_CHARACTER,
                    effects=[
                        effect(EffectKind.HEAL, amount=3),
                        effect(EffectKind.GRANT_STATS, attack=1, duration="turn"),
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-004",
            name="Erzulie Dantor",
            cost=4,
            attack=4,
            health=6,
            rarity="rare",
            alignment="light",
            subtype="loa",
            traits=["motherhood", "war", "protection", "fire"],
            rules_text="Guard. On play: Another friendly Figure gets +2 Attack this turn.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="haitian-vodou-004-1",
                    label="Battle Surge",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="turn")],
                )
            ],
        ),
        figure(
            id="haitian-vodou-005",
            name="Ogou Feray",
            cost=4,
            attack=5,
            health=5,
            rarity="rare",
            alignment="neutral",
            subtype="loa",
            traits=["war", "iron", "fire", "strength"],
            rules_text="Rush. When Ogou Feray attacks, he gets +1 Attack this combat.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="haitian-vodou-005-1",
                    label="Battle Surge",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, duration="combat")],
                )
            ],
        ),
        figure(
            id="haitian-vodou-006",
            name="Damballa",
            cost=4,
            attack=3,
            health=6,
            rarity="rare",
            alignment="light",
            subtype="loa",
            traits=["serpent", "creation", "wisdom", "water"],
            rules_text="Poisonous. On play: Exhaust an enemy Figure.",
            keywords=["poisonous"],
            abilities=[
                ability(
                    id="haitian-vodou-006-1",
                    label="Coiled Fate",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.EXHAUST)],
                )
            ],
        ),
        figure(
            id="haitian-vodou-007",
            name="Ayida Wedo",
            cost=4,
            attack=3,
            health=6,
            rarity="rare",
            alignment="light",
            subtype="loa",
            traits=["rainbow", "water", "fertility", "sky"],
            rules_text="Ward. On play: Restore 2 Health to all friendly Figures.",
            keywords=["ward"],
            abilities=[
                ability(
                    id="haitian-vodou-007-1",
                    label="Tidal Ward",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                )
            ],
        ),
        figure(
            id="haitian-vodou-008",
            name="Agwe",
            cost=4,
            attack=3,
            health=6,
            rarity="rare",
            alignment="neutral",
            subtype="loa",
            traits=["sea", "voyage", "water", "command"],
            rules_text="On play: Return a damaged enemy Figure that costs 3 or less to its owner's hand.",
            abilities=[
                ability(
                    id="haitian-vodou-008-1",
                    label="Ocean's Claim",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 3})],
                )
            ],
        ),
        figure(
            id="haitian-vodou-009",
            name="Simbi",
            cost=3,
            attack=2,
            health=5,
            rarity="uncommon",
            alignment="neutral",
            subtype="loa",
            traits=["water", "magic", "wisdom", "serpent"],
            rules_text="On play: Gain 1 Ritual Mana. Restore 2 Health to your Hero.",
            abilities=[
                ability(
                    id="haitian-vodou-009-1",
                    label="Ritual Current",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_HERO,
                    effects=[
                        effect(EffectKind.GAIN_RITUAL_MANA, amount=1),
                        effect(EffectKind.HEAL, amount=2),
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-010",
            name="Loko",
            cost=3,
            attack=3,
            health=5,
            rarity="uncommon",
            alignment="light",
            subtype="loa",
            traits=["healing", "trees", "ritual", "earth"],
            rules_text="Lifesteal. On play: Restore 3 Health to another friendly Figure.",
            keywords=["lifesteal"],
            abilities=[
                ability(
                    id="haitian-vodou-010-1",
                    label="Restoring Rite",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.HEAL, amount=3)],
                )
            ],
        ),
        figure(
            id="haitian-vodou-011",
            name="Ayizan",
            cost=2,
            attack=2,
            health=3,
            rarity="uncommon",
            alignment="light",
            subtype="loa",
            traits=["market", "initiation", "ritual", "wisdom"],
            rules_text="On play: Look at the top 3 cards of your deck. Put one into your hand and the rest on the bottom in any order.",
            abilities=[
                ability(
                    id="haitian-vodou-011-1",
                    label="Ancient Counsel",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1, pool="top_3_deck")],
                )
            ],
        ),
        figure(
            id="haitian-vodou-012",
            name="Ghede Nibo",
            cost=3,
            attack=3,
            health=3,
            rarity="uncommon",
            alignment="dark",
            subtype="spirit",
            traits=["death", "youth", "cemetery", "night"],
            rules_text="Reborn. Death: Deal 1 damage to the enemy Hero.",
            keywords=["reborn"],
            abilities=[
                ability(
                    id="haitian-vodou-012-1",
                    label="Grave Echo",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_DEATH,
                    target_rule=TargetRule.ENEMY_HERO,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)],
                )
            ],
        ),
        figure(
            id="haitian-vodou-013",
            name="Marinette",
            cost=4,
            attack=4,
            health=4,
            rarity="uncommon",
            alignment="dark",
            subtype="spirit",
            traits=["fire", "rage", "night", "darkness"],
            rules_text="On play: Deal 1 damage to all other Figures.",
            abilities=[
                ability(
                    id="haitian-vodou-013-1",
                    label="Ember Wrath",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_other_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)],
                )
            ],
        ),
        figure(
            id="haitian-vodou-014",
            name="Kalfu",
            cost=4,
            attack=4,
            health=5,
            rarity="uncommon",
            alignment="dark",
            subtype="loa",
            traits=["darkness", "crossroads", "chaos", "night"],
            rules_text="On play: Freeze an enemy Figure. If it is already damaged, deal 2 damage to it.",
            abilities=[
                ability(
                    id="haitian-vodou-014-1",
                    label="Shadow Eclipse",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.FREEZE),
                        effect(EffectKind.DEAL_DAMAGE, amount=2, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-015",
            name="Azaka",
            cost=2,
            attack=2,
            health=4,
            rarity="common",
            alignment="light",
            subtype="loa",
            traits=["agriculture", "earth", "harvest", "simplicity"],
            rules_text="On play: Summon a 1/1 Spirit token.",
            abilities=[
                ability(
                    id="haitian-vodou-015-1",
                    label="Field Blessing",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.EMPTY_FRIENDLY_SLOT,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="haitian-vodou-token-spirit")],
                )
            ],
        ),
        figure(
            id="haitian-vodou-016",
            name="Bosou",
            cost=3,
            attack=4,
            health=4,
            rarity="common",
            alignment="dark",
            subtype="loa",
            traits=["strength", "bull", "war", "power"],
            rules_text="Rush. If a friendly Figure died this turn, Bosou gets +1/+1.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="haitian-vodou-016-1",
                    label="Battle Surge",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_SUMMON,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, health=1, duration="permanent")],
                    conditions=[{"kind": "if_friendly_died_this_turn"}],
                )
            ],
        ),
        figure(
            id="haitian-vodou-017",
            name="La Sirene",
            cost=3,
            attack=2,
            health=4,
            rarity="common",
            alignment="light",
            subtype="spirit",
            traits=["sea", "beauty", "song", "water"],
            rules_text="On play: Exhaust an enemy Figure. Restore 2 Health to your Hero.",
            abilities=[
                ability(
                    id="haitian-vodou-017-1",
                    label="Ocean's Claim",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.EXHAUST),
                        effect(EffectKind.HEAL, amount=2, scope="friendly_hero"),
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-018",
            name="Gran Bwa",
            cost=4,
            attack=4,
            health=6,
            rarity="common",
            alignment="light",
            subtype="spirit",
            traits=["forest", "healing", "spirit", "earth"],
            rules_text="On play: Summon a 1/1 Spirit token. Restore 2 Health to your Hero.",
            abilities=[
                ability(
                    id="haitian-vodou-018-1",
                    label="Wildwood Pact",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.EMPTY_FRIENDLY_SLOT,
                    effects=[
                        effect(EffectKind.SUMMON_TOKEN, card_id="haitian-vodou-token-spirit"),
                        effect(EffectKind.HEAL, amount=2, scope="friendly_hero"),
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-019",
            name="Ti Jean Petro",
            cost=2,
            attack=3,
            health=2,
            rarity="common",
            alignment="dark",
            subtype="spirit",
            traits=["fire", "trickster", "speed", "rage"],
            rules_text="Rush. On play: Deal 1 damage to your Hero and 2 damage to an enemy Figure.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="haitian-vodou-019-1",
                    label="Ember Wrath",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=1, scope="friendly_hero"),
                        effect(EffectKind.DEAL_DAMAGE, amount=2),
                    ],
                )
            ],
        ),
        figure(
            id="haitian-vodou-020",
            name="Maman Brigitte",
            cost=4,
            attack=4,
            health=5,
            rarity="uncommon",
            alignment="dark",
            subtype="loa",
            traits=["death", "graveyard", "fire", "justice"],
            rules_text="Reborn. On play: Deal 2 damage to a damaged enemy Figure.",
            keywords=["reborn"],
            abilities=[
                ability(
                    id="haitian-vodou-020-1",
                    label="Grave Call",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        token_figure(
            id="haitian-vodou-token-spirit",
            name="Restless Spirit",
            attack=1,
            health=1,
            subtype="spirit",
            traits=["spirit", "death"],
        ),
        spell(
            id="haitian-vodou-spell-crossroads-bargain",
            name="Crossroads Bargain",
            cost=2,
            speed=Speed.SLOW,
            rarity="common",
            traits=["crossroads", "ritual"],
            rules_text="Deal 1 damage to a friendly Figure. Draw 2 cards.",
            abilities=[
                ability(
                    id="haitian-vodou-spell-crossroads-bargain-1",
                    label="Crossroads Bargain",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=1),
                        effect(EffectKind.DRAW_CARDS, amount=2),
                    ],
                )
            ],
        ),
        spell(
            id="haitian-vodou-spell-saltwater-passage",
            name="Saltwater Passage",
            cost=2,
            speed=Speed.FAST,
            rarity="common",
            traits=["sea", "water", "flow"],
            rules_text="Return a damaged enemy Figure that costs 3 or less to its owner's hand.",
            abilities=[
                ability(
                    id="haitian-vodou-spell-saltwater-passage-1",
                    label="Saltwater Passage",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 3})],
                )
            ],
        ),
        spell(
            id="haitian-vodou-spell-ghede-procession",
            name="Ghede Procession",
            cost=4,
            speed=Speed.SLOW,
            rarity="rare",
            traits=["death", "procession", "spirit"],
            rules_text="Return a friendly non-Legendary Figure that costs 3 or less from your discard to your hand. Summon a 1/1 Spirit token.",
            abilities=[
                ability(
                    id="haitian-vodou-spell-ghede-procession-1",
                    label="Ghede Procession",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule="friendly_discard_figure",
                    effects=[
                        effect(
                            EffectKind.RETURN_FROM_DISCARD,
                            extra={"max_cost": 3, "legendary_allowed": False, "to_hand": True},
                        ),
                        effect(EffectKind.SUMMON_TOKEN, card_id="haitian-vodou-token-spirit"),
                    ],
                )
            ],
        ),
        spell(
            id="haitian-vodou-spell-cemetery-feast",
            name="Cemetery Feast",
            cost=4,
            speed=Speed.SLOW,
            rarity="rare",
            traits=["death", "justice", "ritual"],
            rules_text="Destroy a damaged enemy Figure. Restore 3 Health to your Hero.",
            abilities=[
                ability(
                    id="haitian-vodou-spell-cemetery-feast-1",
                    label="Cemetery Feast",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DESTROY),
                        effect(EffectKind.HEAL, amount=3, scope="friendly_hero"),
                    ],
                )
            ],
        ),
        relic(
            id="haitian-vodou-relic-funeral-drums",
            name="Funeral Drums",
            cost=2,
            rarity="rare",
            traits=["spirit", "death", "ritual"],
            rules_text="The first time a friendly Figure dies each turn, summon a 1/1 Spirit token.",
            abilities=[
                ability(
                    id="haitian-vodou-relic-funeral-drums-1",
                    label="Funeral Drums",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_DEATH,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="haitian-vodou-token-spirit")],
                    limit="once_each_turn",
                )
            ],
        ),
    ]

    pack = {
        "set_code": "haitian-vodou-v1",
        "culture_slug": "haitian-vodou",
        "primary_family": "Gravebound",
        "secondary_family": "Tidebound",
        "hero_id": "haitian-vodou-hero-papa-legba",
        "notes": [
            "Second manual translation pass from the current figure roster into the exact-rules v1 card schema.",
            "Designed to preserve Haitian Vodou spirit-recursion identity while keeping the timing and board language readable.",
        ],
        "cards": [dataclass_to_dict(card) for card in cards],
    }
    deck = {
        "name": "Legba Spirits",
        "format": "mythic-clash-v1",
        "hero_id": "haitian-vodou-hero-papa-legba",
        "notes": [
            "Mono-culture sample deck for checking whether Haitian Vodou plays as a readable death-value deck instead of a confusing supernatural mix.",
            "Leans on cheap setup, recursive threats, spirit generation, and selective tide-style disruption.",
        ],
        "cards": [
            {"id": "haitian-vodou-011", "count": 2},
            {"id": "haitian-vodou-015", "count": 2},
            {"id": "haitian-vodou-019", "count": 2},
            {"id": "haitian-vodou-012", "count": 2},
            {"id": "haitian-vodou-009", "count": 2},
            {"id": "haitian-vodou-016", "count": 2},
            {"id": "haitian-vodou-003", "count": 2},
            {"id": "haitian-vodou-017", "count": 2},
            {"id": "haitian-vodou-006", "count": 1},
            {"id": "haitian-vodou-002", "count": 1},
            {"id": "haitian-vodou-spell-crossroads-bargain", "count": 1},
            {"id": "haitian-vodou-spell-saltwater-passage", "count": 2},
            {"id": "haitian-vodou-spell-ghede-procession", "count": 1},
            {"id": "haitian-vodou-spell-cemetery-feast", "count": 1},
            {"id": "haitian-vodou-relic-funeral-drums", "count": 1},
        ],
    }
    return pack, deck


def main() -> None:
    pack, deck = build_pack()
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    DECKS_DIR.mkdir(parents=True, exist_ok=True)

    pack_path = CARDS_DIR / "haitian-vodou-v1.json"
    deck_path = DECKS_DIR / "haitian-vodou-legba-spirits.json"
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
