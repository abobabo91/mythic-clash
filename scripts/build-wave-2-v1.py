"""
Build the next curated v1 culture wave.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from game.card_schema import (  # noqa: E402
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
FIGURES_DIR = ROOT / "data" / "figures"


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


def source_index(culture_slug: str) -> dict[str, dict[str, object]]:
    payload = json.loads((FIGURES_DIR / f"{culture_slug}.json").read_text(encoding="utf-8"))
    return {figure["id"]: figure for figure in payload["figures"]}


def translated_figure(
    *,
    source: dict[str, object],
    culture_slug: str,
    set_code: str,
    cost: int,
    attack: int,
    health: int,
    rules_text: str,
    keywords: list[str] | None = None,
    abilities: list[AbilitySpec] | None = None,
) -> CardSpec:
    card = CardSpec(
        id=str(source["id"]),
        name=str(source["name"]),
        card_type=CardType.FIGURE,
        culture_slug=culture_slug,
        rarity=str(source["rarity"]),
        alignment=str(source["alignment"]),
        traits=list(source["domains"]),
        rules_text=rules_text,
        cost=cost,
        subtypes=[str(source["type"])],
        keywords=keywords or [],
        unique=str(source["rarity"]) == "legendary",
        legendary=str(source["rarity"]) == "legendary",
        set_code=set_code,
        attack=attack,
        health=health,
        abilities=abilities or [],
    )
    card.validate()
    return card


def hero(
    *,
    culture_slug: str,
    set_code: str,
    id: str,
    name: str,
    alignment: str,
    traits: list[str],
    rules_text: str,
    abilities: list[AbilitySpec],
) -> CardSpec:
    card = CardSpec(
        id=id,
        name=name,
        card_type=CardType.HERO,
        culture_slug=culture_slug,
        rarity="legendary",
        alignment=alignment,
        traits=traits,
        rules_text=rules_text,
        unique=True,
        legendary=True,
        set_code=set_code,
        abilities=abilities,
    )
    card.validate()
    return card


def spell(
    *,
    culture_slug: str,
    set_code: str,
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
        culture_slug=culture_slug,
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        speed=speed,
        set_code=set_code,
        abilities=abilities,
    )
    card.validate()
    return card


def relic(
    *,
    culture_slug: str,
    set_code: str,
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
        culture_slug=culture_slug,
        rarity=rarity,
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=cost,
        set_code=set_code,
        unique=rarity == "legendary",
        legendary=rarity == "legendary",
        abilities=abilities,
    )
    card.validate()
    return card


def token(
    *,
    culture_slug: str,
    set_code: str,
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
        culture_slug=culture_slug,
        rarity="token",
        alignment="neutral",
        traits=traits,
        rules_text=rules_text,
        cost=0,
        subtypes=[subtype],
        keywords=keywords or [],
        token=True,
        collectible=False,
        set_code=set_code,
        attack=attack,
        health=health,
        abilities=abilities or [],
    )
    card.validate()
    return card


def pack_payload(
    *,
    set_code: str,
    culture_slug: str,
    primary_family: str,
    secondary_family: str,
    hero_id: str,
    notes: list[str],
    cards: list[CardSpec],
) -> dict[str, object]:
    return {
        "set_code": set_code,
        "culture_slug": culture_slug,
        "primary_family": primary_family,
        "secondary_family": secondary_family,
        "hero_id": hero_id,
        "notes": notes,
        "cards": [dataclass_to_dict(card) for card in cards],
    }


def deck_payload(
    *,
    name: str,
    hero_id: str,
    notes: list[str],
    cards: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "name": name,
        "format": "mythic-clash-v1",
        "hero_id": hero_id,
        "notes": notes,
        "cards": cards,
    }


def build_zoroastrian_persian() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "zoroastrian-persian"
    set_code = "zoroastrian-persian-v1"
    hero_id = "zoroastrian-persian-hero-ahura-mazda"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Ahura Mazda, Radiant Judge",
            alignment="light",
            traits=["light", "wisdom", "creation", "justice"],
            rules_text="Hero Power - Radiant Counsel (2): Heal a friendly Figure for 2. Give it Ward this turn.",
            abilities=[
                ability(
                    id=f"{hero_id}-1",
                    label="Radiant Counsel",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.HEAL, amount=2),
                        effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn"),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-001"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=7,
            rules_text="On play: Heal all friendly Figures for 2. Then give a friendly Figure Ward this turn.",
            abilities=[
                ability(
                    id="zoroastrian-persian-001-1",
                    label="Radiant Aegis",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                ),
                ability(
                    id="zoroastrian-persian-001-2",
                    label="Radiant Aegis",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")],
                ),
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-002"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=6,
            attack=5,
            health=6,
            rules_text="On play: Deal 3 damage to a damaged enemy Figure. Restore 2 Health to your Hero.",
            abilities=[
                ability(
                    id="zoroastrian-persian-002-1",
                    label="Shadow Eclipse",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=3)],
                ),
                ability(
                    id="zoroastrian-persian-002-2",
                    label="Shadow Eclipse",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")],
                ),
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-003"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=5,
            rules_text="On play: Heal a friendly Figure for 3. Then give it +1 Attack.",
            abilities=[
                ability(
                    id="zoroastrian-persian-003-1",
                    label="Spenta Grace",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.HEAL, amount=3),
                        effect(EffectKind.GRANT_STATS, attack=1),
                    ],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-004"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Heal all friendly Figures for 2.",
            abilities=[
                ability(
                    id="zoroastrian-persian-004-1",
                    label="Tidal Ward",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-005"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=5,
            rules_text="Rush. When Mithra attacks, he gains +2 Attack this combat.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="zoroastrian-persian-005-1",
                    label="Solar Oath",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="combat")],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-006"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=5,
            rules_text="On play: Deal 2 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="zoroastrian-persian-006-1",
                    label="Ember Wrath",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-007"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=4,
            rules_text="Rush. When Verethragna attacks, he gains +1/+1 this combat.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="zoroastrian-persian-007-1",
                    label="Battle Surge",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, health=1, duration="combat")],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-008"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Restore 3 Health to your Hero and give a friendly Figure +1 Health.",
            abilities=[
                ability(
                    id="zoroastrian-persian-008-1",
                    label="Monsoon Blessing",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.HEAL, amount=3, scope="friendly_hero")],
                ),
                ability(
                    id="zoroastrian-persian-008-2",
                    label="Monsoon Blessing",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, health=1)],
                ),
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-009"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="On play: Draw a card.",
            abilities=[
                ability(
                    id="zoroastrian-persian-009-1",
                    label="Sacred Insight",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DRAW_CARDS, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-010"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=4,
            rules_text="On play: Exhaust an enemy Figure. If it is damaged, it cannot attack next turn.",
            abilities=[
                ability(
                    id="zoroastrian-persian-010-1",
                    label="Just Measure",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.EXHAUST),
                        effect(EffectKind.SET_CANT_ATTACK, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-011"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=4,
            rules_text="On play: Heal a friendly Figure for 4.",
            abilities=[
                ability(
                    id="zoroastrian-persian-011-1",
                    label="Haoma Rite",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.HEAL, amount=4)],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-012"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=3,
            rules_text="Rush. On play: Give a friendly Figure Ward this turn.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="zoroastrian-persian-012-1",
                    label="Winds of Purity",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-013"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Heal all friendly Figures for 2.",
            abilities=[
                ability(
                    id="zoroastrian-persian-013-1",
                    label="Haurvatat's Mercy",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-014"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=3,
            health=5,
            rules_text="At the end of your turn, restore 1 Health to your Hero.",
            abilities=[
                ability(
                    id="zoroastrian-persian-014-1",
                    label="Deathless Garden",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_TURN_END,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.HEAL, amount=1, scope="friendly_hero")],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-015"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=1,
            health=4,
            rules_text="Guard. When this dies, give a friendly Figure Ward this turn.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="zoroastrian-persian-015-1",
                    label="Elder Shelter",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_DEATH,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-016"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="On play: Discover from your top 3 cards.",
            abilities=[
                ability(
                    id="zoroastrian-persian-016-1",
                    label="Daena's Reading",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1, pool="top_3_deck")],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-017"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=5,
            rules_text="Guard. On play: Exhaust an enemy Figure.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="zoroastrian-persian-017-1",
                    label="Bridgekeeper's Halt",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.EXHAUST)],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-018"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=5,
            rules_text="On play: Give a friendly Figure +1/+2 and Ward this turn.",
            abilities=[
                ability(
                    id="zoroastrian-persian-018-1",
                    label="Royal Shelter",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=1, health=2),
                        effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn"),
                    ],
                )
            ],
        ),
        translated_figure(
            source=source["zoroastrian-persian-019"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=4,
            health=3,
            rules_text="Rush.",
            keywords=["rush"],
        ),
        translated_figure(
            source=source["zoroastrian-persian-020"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=6,
            rules_text="On play: Return a Figure from your discard pile to your hand.",
            abilities=[
                ability(
                    id="zoroastrian-persian-020-1",
                    label="Sky Memorial",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="friendly_discard_figure",
                    effects=[effect(EffectKind.RETURN_FROM_DISCARD)],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="zoroastrian-persian-spell-purifying-flame",
            name="Purifying Flame",
            cost=2,
            speed=Speed.FAST,
            rarity="common",
            traits=["fire", "purification", "light"],
            rules_text="Deal 2 damage to an enemy Figure. If it was already damaged, destroy it.",
            abilities=[
                ability(
                    id="zoroastrian-persian-spell-purifying-flame-1",
                    label="Purifying Flame",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=2),
                        effect(EffectKind.DESTROY, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="zoroastrian-persian-spell-river-of-truth",
            name="River of Truth",
            cost=2,
            speed=Speed.BURST,
            rarity="common",
            traits=["water", "truth", "healing"],
            rules_text="Heal a friendly Figure for 3. Give it Ward this turn.",
            abilities=[
                ability(
                    id="zoroastrian-persian-spell-river-of-truth-1",
                    label="River of Truth",
                    timing=AbilityTiming.BURST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.HEAL, amount=3),
                        effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn"),
                    ],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="zoroastrian-persian-spell-verdict-of-light",
            name="Verdict of Light",
            cost=4,
            speed=Speed.SLOW,
            rarity="rare",
            traits=["light", "judgment", "fire"],
            rules_text="Deal 2 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="zoroastrian-persian-spell-verdict-of-light-1",
                    label="Verdict of Light",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        relic(
            culture_slug=culture_slug,
            set_code=set_code,
            id="zoroastrian-persian-relic-fire-temple",
            name="Fire Temple of Truth",
            cost=3,
            rarity="rare",
            traits=["fire", "justice", "sanctuary"],
            rules_text="Once each turn, after a friendly Figure is targeted by a spell or Hero Power, give it +1 Attack and Ward this turn.",
            abilities=[
                ability(
                    id="zoroastrian-persian-relic-fire-temple-1",
                    label="Temple Blessing",
                    timing=AbilityTiming.PASSIVE,
                    trigger="on_friendly_targeted_by_spell_or_hero_power",
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=1, duration="turn"),
                        effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn"),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
    ]

    pack = pack_payload(
        set_code=set_code,
        culture_slug=culture_slug,
        primary_family="Sanctuary",
        secondary_family="Vanguard",
        hero_id=hero_id,
        notes=[
            "Manual translation wave-two pass focused on visible stabilization, telegraphed lethality, and low complexity.",
            "Designed to read as righteous protection first and disciplined combat second.",
        ],
        cards=cards,
    )
    deck = deck_payload(
        name="Ahura Bastion",
        hero_id=hero_id,
        notes=[
            "Sanctuary-first test deck for the stricter rollout rubric.",
            "Uses healing, guard, and precise battle figures instead of hidden burst.",
        ],
        cards=[
            {"id": "zoroastrian-persian-009", "count": 2},
            {"id": "zoroastrian-persian-011", "count": 2},
            {"id": "zoroastrian-persian-015", "count": 2},
            {"id": "zoroastrian-persian-016", "count": 2},
            {"id": "zoroastrian-persian-017", "count": 2},
            {"id": "zoroastrian-persian-018", "count": 2},
            {"id": "zoroastrian-persian-005", "count": 2},
            {"id": "zoroastrian-persian-010", "count": 2},
            {"id": "zoroastrian-persian-001", "count": 1},
            {"id": "zoroastrian-persian-006", "count": 1},
            {"id": "zoroastrian-persian-spell-purifying-flame", "count": 2},
            {"id": "zoroastrian-persian-spell-river-of-truth", "count": 2},
            {"id": "zoroastrian-persian-spell-verdict-of-light", "count": 1},
            {"id": "zoroastrian-persian-relic-fire-temple", "count": 1},
        ],
    )
    return pack, deck, f"{culture_slug}-v1.json", "zoroastrian-persian-ahura-bastion.json"


def build_japanese_shinto() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "japanese-shinto"
    set_code = "japanese-shinto-v1"
    hero_id = "japanese-shinto-hero-amaterasu"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Amaterasu, Mirror of Dawn",
            alignment="light",
            traits=["sun", "light", "purification", "imperial"],
            rules_text="Hero Power - Dawn Spark (2): Deal 1 damage to an enemy Figure. If it survives, Freeze it.",
            abilities=[
                ability(
                    id=f"{hero_id}-1",
                    label="Dawn Spark",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=1),
                        effect(EffectKind.FREEZE, extra={"if_target_survived_damage": True}),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-001"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=6,
            rules_text="On play: Heal all friendly Figures for 2, then deal 1 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="japanese-shinto-001-1",
                    label="Dawn Return",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                ),
                ability(
                    id="japanese-shinto-001-2",
                    label="Dawn Return",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)],
                ),
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-002"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=5,
            health=5,
            rules_text="Rush. When Susanoo attacks, he gains +2 Attack this combat.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="japanese-shinto-002-1",
                    label="Orochi Slayer",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.SELF,
                    effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="combat")],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-003"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=4,
            rules_text="On play: Heal a friendly Figure for 3 and give it Ward this turn.",
            abilities=[
                ability(
                    id="japanese-shinto-003-1",
                    label="Purification Rite",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.HEAL, amount=3),
                        effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn"),
                    ],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-004"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=3,
            health=5,
            rules_text="On play: An enemy Figure cannot attack next turn. If it is damaged, deal 2 to it.",
            abilities=[
                ability(
                    id="japanese-shinto-004-1",
                    label="Death Curse",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.SET_CANT_ATTACK),
                        effect(EffectKind.DEAL_DAMAGE, amount=2, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-005"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=3,
            rules_text="Stealth. On play: Draw a card.",
            keywords=["stealth"],
            abilities=[
                ability(
                    id="japanese-shinto-005-1",
                    label="Night Division",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DRAW_CARDS, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-006"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=3,
            health=4,
            rules_text="On play: Deal 2 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="japanese-shinto-006-1",
                    label="Thunder Drums",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-007"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="On play: Exhaust an enemy Figure.",
            abilities=[
                ability(
                    id="japanese-shinto-007-1",
                    label="Wind Release",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.EXHAUST)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-008"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Summon a Divine Fox.",
            abilities=[
                ability(
                    id="japanese-shinto-008-1",
                    label="Fox Messenger",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="japanese-shinto-token-divine-fox")],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-009"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=6,
            attack=5,
            health=7,
            rules_text="Overwhelm. On play: Deal 1 damage to all other Figures.",
            keywords=["overwhelm"],
            abilities=[
                ability(
                    id="japanese-shinto-009-1",
                    label="Eightfold Ruin",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_other_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-010"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=4,
            rules_text="Deathrattle: Summon a Fire Spirit.",
            abilities=[
                ability(
                    id="japanese-shinto-010-1",
                    label="Fire Birth",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_DEATH,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="japanese-shinto-token-fire-spirit")],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-011"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="On play: Draw a card.",
            abilities=[
                ability(
                    id="japanese-shinto-011-1",
                    label="Music of the Court",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DRAW_CARDS, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-012"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=1,
            health=4,
            rules_text="On play: Gain 1 Ritual Mana.",
            abilities=[
                ability(
                    id="japanese-shinto-012-1",
                    label="Lucky Tide",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.GAIN_RITUAL_MANA, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-013"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=4,
            health=2,
            rules_text="Rush.",
            keywords=["rush"],
        ),
        translated_figure(
            source=source["japanese-shinto-014"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="Lifesteal.",
            keywords=["lifesteal"],
        ),
        translated_figure(
            source=source["japanese-shinto-015"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=3,
            rules_text="On play: Deal 2 damage to an enemy Figure.",
            abilities=[
                ability(
                    id="japanese-shinto-015-1",
                    label="Oni Club",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-016"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=1,
            health=3,
            rules_text="On play: Summon an Illusion Fox.",
            abilities=[
                ability(
                    id="japanese-shinto-016-1",
                    label="Shifting Laughter",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="japanese-shinto-token-illusion-fox")],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-017"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Freeze an enemy Figure.",
            abilities=[
                ability(
                    id="japanese-shinto-017-1",
                    label="Winter Veil",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.FREEZE)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-018"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=7,
            rules_text="Guard. On play: Deal 2 damage to an enemy Figure.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="japanese-shinto-018-1",
                    label="Immovable Flame",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-019"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=4,
            rules_text="On play: Heal all friendly Figures for 1.",
            abilities=[
                ability(
                    id="japanese-shinto-019-1",
                    label="Blessed Water Song",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["japanese-shinto-020"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=2,
            rules_text="On play: Give a friendly Figure +1/+1 and Ward this turn.",
            abilities=[
                ability(
                    id="japanese-shinto-020-1",
                    label="Festival Lure",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.GRANT_STATS, attack=1, health=1),
                        effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn"),
                    ],
                )
            ],
        ),
        token(
            culture_slug=culture_slug,
            set_code=set_code,
            id="japanese-shinto-token-divine-fox",
            name="Divine Fox",
            attack=2,
            health=1,
            subtype="spirit",
            traits=["fox", "light", "trickery"],
            rules_text="Stealth.",
            keywords=["stealth"],
        ),
        token(
            culture_slug=culture_slug,
            set_code=set_code,
            id="japanese-shinto-token-fire-spirit",
            name="Fire Spirit",
            attack=2,
            health=1,
            subtype="spirit",
            traits=["fire", "spirit"],
            rules_text="Rush.",
            keywords=["rush"],
        ),
        token(
            culture_slug=culture_slug,
            set_code=set_code,
            id="japanese-shinto-token-illusion-fox",
            name="Illusion Fox",
            attack=1,
            health=1,
            subtype="spirit",
            traits=["illusion", "fox", "trickery"],
            rules_text="Stealth.",
            keywords=["stealth"],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="japanese-shinto-spell-stormcall-volley",
            name="Stormcall Volley",
            cost=3,
            speed=Speed.FAST,
            rarity="common",
            traits=["storm", "thunder", "tempo"],
            rules_text="Deal 2 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="japanese-shinto-spell-stormcall-volley-1",
                    label="Stormcall Volley",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="japanese-shinto-spell-sacred-purification",
            name="Sacred Purification",
            cost=2,
            speed=Speed.BURST,
            rarity="common",
            traits=["light", "purification", "water"],
            rules_text="Heal a friendly Figure for 3. Give it Ward this turn.",
            abilities=[
                ability(
                    id="japanese-shinto-spell-sacred-purification-1",
                    label="Sacred Purification",
                    timing=AbilityTiming.BURST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.HEAL, amount=3),
                        effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn"),
                    ],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="japanese-shinto-spell-sun-door-rite",
            name="Sun Door Rite",
            cost=2,
            speed=Speed.BURST,
            rarity="common",
            traits=["sun", "ritual", "insight"],
            rules_text="Draw a card. Give a friendly Figure +1 Attack this turn.",
            abilities=[
                ability(
                    id="japanese-shinto-spell-sun-door-rite-1",
                    label="Sun Door Rite",
                    timing=AbilityTiming.BURST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.DRAW_CARDS, amount=1),
                        effect(EffectKind.GRANT_STATS, attack=1, duration="turn"),
                    ],
                )
            ],
        ),
        relic(
            culture_slug=culture_slug,
            set_code=set_code,
            id="japanese-shinto-relic-drum-bridge",
            name="Drum Bridge of Storms",
            cost=3,
            rarity="rare",
            traits=["storm", "festival", "thunder"],
            rules_text="Once each turn, after a friendly Figure attacks, give it +1 Attack this turn.",
            abilities=[
                ability(
                    id="japanese-shinto-relic-drum-bridge-1",
                    label="Festival Beat",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, duration="turn")],
                    limit="once_each_turn",
                )
            ],
        ),
    ]

    pack = pack_payload(
        set_code=set_code,
        culture_slug=culture_slug,
        primary_family="Tempest",
        secondary_family="Tidebound",
        hero_id=hero_id,
        notes=[
            "Wave-two translation focused on visible tempo swings instead of hidden blowout damage.",
            "Keeps Shinto readable as storm-sun pressure with bounded freeze and token support.",
        ],
        cards=cards,
    )
    deck = deck_payload(
        name="Amaterasu Tempo",
        hero_id=hero_id,
        notes=[
            "Tempest-first test deck under the stricter launch constraints.",
            "Leans on board pressure, freeze windows, and a small token package instead of combo lethals.",
        ],
        cards=[
            {"id": "japanese-shinto-007", "count": 2},
            {"id": "japanese-shinto-017", "count": 2},
            {"id": "japanese-shinto-008", "count": 2},
            {"id": "japanese-shinto-015", "count": 2},
            {"id": "japanese-shinto-004", "count": 2},
            {"id": "japanese-shinto-006", "count": 2},
            {"id": "japanese-shinto-010", "count": 2},
            {"id": "japanese-shinto-018", "count": 2},
            {"id": "japanese-shinto-001", "count": 1},
            {"id": "japanese-shinto-002", "count": 1},
            {"id": "japanese-shinto-spell-stormcall-volley", "count": 2},
            {"id": "japanese-shinto-spell-sacred-purification", "count": 2},
            {"id": "japanese-shinto-spell-sun-door-rite", "count": 1},
            {"id": "japanese-shinto-relic-drum-bridge", "count": 1},
        ],
    )
    return pack, deck, f"{culture_slug}-v1.json", "japanese-shinto-amaterasu-tempo.json"


def build_maori() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "maori"
    set_code = "maori-v1"
    hero_id = "maori-hero-maui"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Maui, Hook of Tides",
            alignment="light",
            traits=["trickster", "sea", "quest", "sun"],
            rules_text="Hero Power - Tidal Hook (2): Exhaust an enemy Figure and deal 1 damage to it.",
            abilities=[
                ability(
                    id=f"{hero_id}-1",
                    label="Tidal Hook",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    resource_cost=2,
                    effects=[effect(EffectKind.EXHAUST), effect(EffectKind.DEAL_DAMAGE, amount=1)],
                    limit="once_each_turn",
                )
            ],
        ),
        translated_figure(
            source=source["maori-001"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=7,
            rules_text="On play: Summon a Wild Sapling and restore 3 Health to your Hero.",
            abilities=[
                ability(
                    id="maori-001-1",
                    label="Wildwood Pact",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[
                        effect(EffectKind.SUMMON_TOKEN, card_id="maori-token-wild-sapling"),
                        effect(EffectKind.HEAL, amount=3, scope="friendly_hero"),
                    ],
                )
            ],
        ),
        translated_figure(
            source=source["maori-002"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=5,
            rules_text="On play: Ready a friendly Figure. If it is damaged, heal it for 2.",
            abilities=[
                ability(
                    id="maori-002-1",
                    label="Clever Reversal",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[
                        effect(EffectKind.READY),
                        effect(EffectKind.HEAL, amount=2, extra={"if_target_is_damaged": True}),
                    ],
                )
            ],
        ),
        translated_figure(
            source=source["maori-003"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=4,
            rules_text="On play: Exhaust an enemy Figure.",
            abilities=[
                ability(
                    id="maori-003-1",
                    label="Ocean's Claim",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.EXHAUST)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-004"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=5,
            rules_text="On play: Deal 2 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="maori-004-1",
                    label="Storm Crown",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-005"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=4,
            rules_text="Rush.",
            keywords=["rush"],
        ),
        translated_figure(
            source=source["maori-006"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=5,
            rules_text="On play: Heal all friendly Figures for 2.",
            abilities=[
                ability(
                    id="maori-006-1",
                    label="Harvest Plenty",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-007"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=3,
            health=6,
            rules_text="Guard. Deathrattle: Deal 2 damage to all enemy Figures.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="maori-007-1",
                    label="Earthshock Return",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_DEATH,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-008"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=5,
            rules_text="On play: Return a Figure from your discard pile to your hand.",
            abilities=[
                ability(
                    id="maori-008-1",
                    label="Night Recall",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="friendly_discard_figure",
                    effects=[effect(EffectKind.RETURN_FROM_DISCARD)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-009"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="On play: Discover from your top 3 cards.",
            abilities=[
                ability(
                    id="maori-009-1",
                    label="Sky Reading",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1, pool="top_3_deck")],
                )
            ],
        ),
        translated_figure(
            source=source["maori-010"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=5,
            rules_text="Guard. On play: Give a friendly Figure +0/+2.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="maori-010-1",
                    label="Earth Mother's Shelter",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, health=2)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-011"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=4,
            rules_text="On play: Heal your Hero for 2.",
            abilities=[
                ability(
                    id="maori-011-1",
                    label="Field Bounty",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")],
                )
            ],
        ),
        translated_figure(
            source=source["maori-012"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=2,
            rules_text="Stealth. Lifesteal.",
            keywords=["stealth", "lifesteal"],
        ),
        translated_figure(
            source=source["maori-013"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=5,
            health=4,
            rules_text="On play: Deal 3 damage to an enemy Figure.",
            abilities=[
                ability(
                    id="maori-013-1",
                    label="Thunder Split",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=3)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-014"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=3,
            health=4,
            rules_text="On play: Give a friendly Figure +2 Attack this turn.",
            abilities=[
                ability(
                    id="maori-014-1",
                    label="Rainbow Charge",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="turn")],
                )
            ],
        ),
        translated_figure(
            source=source["maori-015"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="On play: Return an enemy Figure with cost 3 or less to its owner's hand.",
            abilities=[
                ability(
                    id="maori-015-1",
                    label="Coastal Pull",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 3})],
                )
            ],
        ),
        translated_figure(
            source=source["maori-016"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=3,
            health=4,
            rules_text="On play: Heal a friendly Figure for 4.",
            abilities=[
                ability(
                    id="maori-016-1",
                    label="Stellar Mercy",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.HEAL, amount=4)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-017"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Summon a Spirit Ancestor.",
            abilities=[
                ability(
                    id="maori-017-1",
                    label="First Shape",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="maori-token-spirit-ancestor")],
                )
            ],
        ),
        translated_figure(
            source=source["maori-018"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="Stealth. On play: Restore 2 Health to your Hero.",
            keywords=["stealth"],
            abilities=[
                ability(
                    id="maori-018-1",
                    label="Moonbound Return",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")],
                )
            ],
        ),
        translated_figure(
            source=source["maori-019"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=1,
            health=4,
            rules_text="On play: Exhaust an enemy Figure.",
            abilities=[
                ability(
                    id="maori-019-1",
                    label="Sea's Grip",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.EXHAUST)],
                )
            ],
        ),
        translated_figure(
            source=source["maori-020"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=5,
            rules_text="Guard. On play: Restore 2 Health to your Hero.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="maori-020-1",
                    label="Deep Shelter",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")],
                )
            ],
        ),
        token(
            culture_slug=culture_slug,
            set_code=set_code,
            id="maori-token-wild-sapling",
            name="Wild Sapling",
            attack=2,
            health=2,
            subtype="spirit",
            traits=["forest", "growth", "light"],
            rules_text="Guard.",
            keywords=["guard"],
        ),
        token(
            culture_slug=culture_slug,
            set_code=set_code,
            id="maori-token-spirit-ancestor",
            name="Spirit Ancestor",
            attack=2,
            health=1,
            subtype="ancestor",
            traits=["spirit", "ancestor", "guidance"],
            rules_text="Stealth.",
            keywords=["stealth"],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="maori-spell-ocean-pull",
            name="Ocean Pull",
            cost=2,
            speed=Speed.FAST,
            rarity="common",
            traits=["sea", "tempo", "movement"],
            rules_text="Return an enemy Figure with cost 3 or less to its owner's hand.",
            abilities=[
                ability(
                    id="maori-spell-ocean-pull-1",
                    label="Ocean Pull",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 3})],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="maori-spell-forest-chorus",
            name="Forest Chorus",
            cost=2,
            speed=Speed.BURST,
            rarity="common",
            traits=["forest", "growth", "healing"],
            rules_text="Summon a Wild Sapling and restore 2 Health to your Hero.",
            abilities=[
                ability(
                    id="maori-spell-forest-chorus-1",
                    label="Forest Chorus",
                    timing=AbilityTiming.BURST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.NONE,
                    effects=[
                        effect(EffectKind.SUMMON_TOKEN, card_id="maori-token-wild-sapling"),
                        effect(EffectKind.HEAL, amount=2, scope="friendly_hero"),
                    ],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="maori-spell-sky-breaker",
            name="Sky Breaker",
            cost=4,
            speed=Speed.SLOW,
            rarity="rare",
            traits=["storm", "sky", "pressure"],
            rules_text="Deal 2 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="maori-spell-sky-breaker-1",
                    label="Sky Breaker",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)],
                )
            ],
        ),
        relic(
            culture_slug=culture_slug,
            set_code=set_code,
            id="maori-relic-fishing-grounds",
            name="Ancestral Fishing Grounds",
            cost=3,
            rarity="rare",
            traits=["sea", "ancestor", "provision"],
            rules_text="Once each turn, after a friendly Figure attacks, give it +1/+1 this turn.",
            abilities=[
                ability(
                    id="maori-relic-fishing-grounds-1",
                    label="Tidal Provision",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, health=1, duration="turn")],
                    limit="once_each_turn",
                )
            ],
        ),
    ]

    pack = pack_payload(
        set_code=set_code,
        culture_slug=culture_slug,
        primary_family="Tidebound",
        secondary_family="Wildhost",
        hero_id=hero_id,
        notes=[
            "Wave-two translation focused on motion, token-backed resilience, and readable stabilization.",
            "Keeps Maori inside the shared grammar while preserving sea-led pressure and creation flavor.",
        ],
        cards=cards,
    )
    deck = deck_payload(
        name="Maui Tidal Growth",
        hero_id=hero_id,
        notes=[
            "Tidebound and Wildhost test deck for the tightened rollout rubric.",
            "Uses bounce, exhaust, and small token pressure instead of opaque stat tricks.",
        ],
        cards=[
            {"id": "maori-003", "count": 2},
            {"id": "maori-006", "count": 2},
            {"id": "maori-004", "count": 2},
            {"id": "maori-005", "count": 2},
            {"id": "maori-007", "count": 2},
            {"id": "maori-008", "count": 2},
            {"id": "maori-015", "count": 2},
            {"id": "maori-017", "count": 2},
            {"id": "maori-001", "count": 1},
            {"id": "maori-002", "count": 1},
            {"id": "maori-spell-ocean-pull", "count": 2},
            {"id": "maori-spell-forest-chorus", "count": 2},
            {"id": "maori-spell-sky-breaker", "count": 1},
            {"id": "maori-relic-fishing-grounds", "count": 1},
        ],
    )
    return pack, deck, f"{culture_slug}-v1.json", "maori-maui-tidal-growth.json"


def main() -> None:
    CARDS_DIR.mkdir(parents=True, exist_ok=True)
    DECKS_DIR.mkdir(parents=True, exist_ok=True)

    outputs = []
    for builder in (build_zoroastrian_persian, build_japanese_shinto, build_maori):
        pack, deck, pack_name, deck_name = builder()
        pack_path = CARDS_DIR / pack_name
        deck_path = DECKS_DIR / deck_name
        pack_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
        deck_path.write_text(json.dumps(deck, ensure_ascii=False, indent=2), encoding="utf-8")
        outputs.append(
            {
                "pack": str(pack_path),
                "deck": str(deck_path),
                "cards": len(pack["cards"]),
                "collectible_non_hero_cards": sum(
                    1 for card in pack["cards"] if card["card_type"] != "hero" and card.get("collectible", True)
                ),
                "sample_deck_cards": sum(entry["count"] for entry in deck["cards"]),
            }
        )

    print(json.dumps(outputs, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
