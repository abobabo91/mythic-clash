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


def build_cherokee() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "cherokee"
    set_code = "cherokee-v1"
    hero_id = "cherokee-hero-selu-cornmother"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Selu, Corn Mother",
            alignment="light",
            traits=["fertility", "earth", "motherhood", "healing"],
            rules_text="Hero Power - Harvest Gift (2): Heal a friendly Figure for 2. Give it +1/+1.",
            abilities=[
                ability(
                    id=f"{hero_id}-1",
                    label="Harvest Gift",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.HEAL, amount=2),
                        effect(EffectKind.GRANT_STATS, attack=1, health=1),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-001"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=6,
            attack=5,
            health=7,
            rules_text="On play: Summon two Elder Shades. Heal all friendly Figures for 2.",
            abilities=[
                ability(
                    id="cherokee-001-1",
                    label="First Breath",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[
                        effect(EffectKind.SUMMON_TOKEN, card_id="cherokee-token-elder-shade"),
                        effect(EffectKind.SUMMON_TOKEN, card_id="cherokee-token-elder-shade"),
                    ],
                ),
                ability(
                    id="cherokee-001-2",
                    label="First Breath",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                ),
            ],
        ),
        translated_figure(
            source=source["cherokee-002"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=7,
            rules_text="At the end of your turn, heal all friendly Figures for 1.",
            abilities=[
                ability(
                    id="cherokee-002-1",
                    label="Golden Grain",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_TURN_END,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=1)],
                )
            ],
        ),
        translated_figure(source=source["cherokee-003"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=4, rules_text="Rush.", keywords=["rush"]),
        translated_figure(
            source=source["cherokee-004"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Deal 1 damage to all enemy Figures.",
            abilities=[
                ability(
                    id="cherokee-004-1",
                    label="Ember Thread",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_enemy_figures",
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-005"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=5,
            health=5,
            rules_text="On play: Deal 3 damage to an enemy Figure. Deal 1 damage to the enemy Hero.",
            abilities=[
                ability(
                    id="cherokee-005-1",
                    label="Thunder Spear",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=3)],
                ),
                ability(
                    id="cherokee-005-2",
                    label="Thunder Spear",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DEAL_DAMAGE, amount=1, scope="enemy_hero")],
                ),
            ],
        ),
        translated_figure(source=source["cherokee-006"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=5, rules_text="Poisonous.", keywords=["poisonous"]),
        translated_figure(
            source=source["cherokee-007"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=3,
            health=6,
            rules_text="Guard. On play: Give a friendly Figure Ward this turn.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="cherokee-007-1",
                    label="Elder Memory",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")],
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-008"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Summon a Wild Scout.",
            abilities=[
                ability(
                    id="cherokee-008-1",
                    label="Wildwood Pact",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="cherokee-token-wild-scout")],
                )
            ],
        ),
        translated_figure(source=source["cherokee-009"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=6, rules_text="Poisonous. Lifesteal.", keywords=["poisonous", "lifesteal"]),
        translated_figure(source=source["cherokee-010"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=6, rules_text="Guard.", keywords=["guard"]),
        translated_figure(
            source=source["cherokee-011"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=3,
            health=2,
            rules_text="On play: Return an enemy Figure that costs 2 or less to its owner's hand.",
            abilities=[
                ability(
                    id="cherokee-011-1",
                    label="Rabbit Trick",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 2})],
                )
            ],
        ),
        translated_figure(source=source["cherokee-012"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="Rush.", keywords=["rush"]),
        translated_figure(
            source=source["cherokee-013"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=4,
            rules_text="Rush. On play: Give another friendly Figure +1 Attack.",
            keywords=["rush"],
            abilities=[
                ability(
                    id="cherokee-013-1",
                    label="Mountain Hunt",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1)],
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-014"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=4,
            health=3,
            rules_text="On play: Destroy a damaged enemy Figure.",
            abilities=[
                ability(
                    id="cherokee-014-1",
                    label="Night Terror",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.DAMAGED_ENEMY_FIGURE,
                    effects=[effect(EffectKind.DESTROY)],
                )
            ],
        ),
        translated_figure(source=source["cherokee-015"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=3, health=2, rules_text=""),
        translated_figure(
            source=source["cherokee-016"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=3,
            rules_text="On play: Heal a friendly Figure for 2.",
            abilities=[
                ability(
                    id="cherokee-016-1",
                    label="Forest Guidance",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.HEAL, amount=2)],
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-017"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=5,
            rules_text="Guard. On play: Restore 2 Health to your Hero.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="cherokee-017-1",
                    label="River Shelter",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")],
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-018"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=2,
            attack=2,
            health=2,
            rules_text="On play: Draw a card.",
            abilities=[
                ability(
                    id="cherokee-018-1",
                    label="Night Warning",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.NONE,
                    effects=[effect(EffectKind.DRAW_CARDS, amount=1)],
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-019"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="Guard. On play: Give a friendly Figure +1 Attack.",
            keywords=["guard"],
            abilities=[
                ability(
                    id="cherokee-019-1",
                    label="Council Fire",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1)],
                )
            ],
        ),
        translated_figure(
            source=source["cherokee-020"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=3,
            attack=2,
            health=4,
            rules_text="On play: Heal all friendly Figures for 2.",
            abilities=[
                ability(
                    id="cherokee-020-1",
                    label="Healing Wind",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.ON_PLAY,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                )
            ],
        ),
        token(culture_slug=culture_slug, set_code=set_code, id="cherokee-token-elder-shade", name="Elder Shade", attack=1, health=2, subtype="spirit", traits=["ancestor", "spirit", "protection"], rules_text="Guard.", keywords=["guard"]),
        token(culture_slug=culture_slug, set_code=set_code, id="cherokee-token-wild-scout", name="Wild Scout", attack=2, health=1, subtype="spirit", traits=["forest", "spirit", "trickster"], rules_text="Stealth.", keywords=["stealth"]),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="cherokee-spell-corn-blessing",
            name="Corn Blessing",
            cost=2,
            speed=Speed.BURST,
            rarity="common",
            traits=["fertility", "healing", "earth"],
            rules_text="Heal all friendly Figures for 2.",
            abilities=[
                ability(
                    id="cherokee-spell-corn-blessing-1",
                    label="Corn Blessing",
                    timing=AbilityTiming.BURST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule="all_friendly_figures",
                    effects=[effect(EffectKind.HEAL, amount=2)],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="cherokee-spell-thunder-path",
            name="Thunder Path",
            cost=3,
            speed=Speed.FAST,
            rarity="common",
            traits=["storm", "thunder", "war"],
            rules_text="Deal 3 damage to an enemy Figure. Gain 1 Ritual Mana.",
            abilities=[
                ability(
                    id="cherokee-spell-thunder-path-1",
                    label="Thunder Path",
                    timing=AbilityTiming.FAST,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=3),
                        effect(EffectKind.GAIN_RITUAL_MANA, amount=1),
                    ],
                )
            ],
        ),
        spell(
            culture_slug=culture_slug,
            set_code=set_code,
            id="cherokee-spell-sacred-council",
            name="Sacred Council",
            cost=2,
            speed=Speed.BURST,
            rarity="common",
            traits=["ritual", "wisdom", "spirit"],
            rules_text="Draw a card. Give a friendly Figure +1 Attack this turn.",
            abilities=[
                ability(
                    id="cherokee-spell-sacred-council-1",
                    label="Sacred Council",
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
            id="cherokee-relic-council-fire",
            name="Council Fire",
            cost=3,
            rarity="rare",
            traits=["fire", "ritual", "order"],
            rules_text="Once each turn, after a friendly Figure attacks, give it +1/+1.",
            abilities=[
                ability(
                    id="cherokee-relic-council-fire-1",
                    label="Shared Courage",
                    timing=AbilityTiming.PASSIVE,
                    trigger=AbilityTrigger.ON_ATTACK_DECLARED,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    effects=[effect(EffectKind.GRANT_STATS, attack=1, health=1)],
                    limit="once_each_turn",
                )
            ],
        ),
    ]

    pack = pack_payload(
        set_code=set_code,
        culture_slug=culture_slug,
        primary_family="Wildhost",
        secondary_family="Tempest",
        hero_id=hero_id,
        notes=[
            "Wave-three translation keeps Cherokee readable as nature-board growth with a bounded storm finish layer.",
            "Midgame anchors live in Selu, Unetlanvhi, Thunder Boys, and the guard-heal shell.",
        ],
        cards=cards,
    )
    deck = deck_payload(
        name="Selu Harvest Storm",
        hero_id=hero_id,
        notes=["Midrange Wildhost deck with healing glue, board anchors, and visible thunder finish tools."],
        cards=[
            {"id": "cherokee-016", "count": 2},
            {"id": "cherokee-019", "count": 2},
            {"id": "cherokee-004", "count": 2},
            {"id": "cherokee-008", "count": 2},
            {"id": "cherokee-020", "count": 2},
            {"id": "cherokee-017", "count": 2},
            {"id": "cherokee-007", "count": 2},
            {"id": "cherokee-005", "count": 2},
            {"id": "cherokee-002", "count": 1},
            {"id": "cherokee-001", "count": 1},
            {"id": "cherokee-spell-corn-blessing", "count": 2},
            {"id": "cherokee-spell-thunder-path", "count": 2},
            {"id": "cherokee-spell-sacred-council", "count": 1},
            {"id": "cherokee-relic-council-fire", "count": 1},
        ],
    )
    return pack, deck, str(CARDS_DIR / "cherokee-v1.json"), str(DECKS_DIR / "cherokee-selu-harvest-storm.json")


def build_muisca_colombian() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "muisca-colombian"
    set_code = "muisca-colombian-v1"
    hero_id = "muisca-colombian-hero-bochica-lawgiver"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Bochica, Lawgiver of Light",
            alignment="light",
            traits=["wisdom", "justice", "civilization", "light"],
            rules_text="Hero Power - Ancient Counsel (2): Draw a card from your top 3 cards. Give a friendly Figure +1 Health.",
            abilities=[
                ability(
                    id=f"{hero_id}-1",
                    label="Ancient Counsel",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.FRIENDLY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.DISCOVER_FROM_POOL, amount=1),
                        effect(EffectKind.GRANT_STATS, health=1),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        translated_figure(
            source=source["muisca-colombian-001"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=6,
            attack=4,
            health=8,
            rules_text="On play: Summon a Sunbird. Heal all friendly Figures for 2.",
            abilities=[
                ability(id="muisca-colombian-001-1", label="World Light", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="muisca-token-sunbird")]),
                ability(id="muisca-colombian-001-2", label="World Light", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)]),
            ],
        ),
        translated_figure(
            source=source["muisca-colombian-002"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=5,
            attack=4,
            health=6,
            rules_text="On play: Draw a card from your top 3 cards. Restore 3 Health to your Hero.",
            abilities=[
                ability(id="muisca-colombian-002-1", label="Path of Law", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1), effect(EffectKind.HEAL, amount=3, scope="friendly_hero")]),
            ],
        ),
        translated_figure(
            source=source["muisca-colombian-003"],
            culture_slug=culture_slug,
            set_code=set_code,
            cost=4,
            attack=3,
            health=6,
            rules_text="On play: Heal all friendly Figures for 2 and summon a Lake Child.",
            abilities=[
                ability(id="muisca-colombian-003-1", label="First Family", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)]),
                ability(id="muisca-colombian-003-2", label="First Family", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="muisca-token-lake-child")]),
            ],
        ),
        translated_figure(source=source["muisca-colombian-004"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="On play: Freeze an enemy Figure.", abilities=[ability(id="muisca-colombian-004-1", label="Moonlit Veil", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.FREEZE)])]),
        translated_figure(source=source["muisca-colombian-005"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="On play: Deal 4 damage to an enemy Figure.", abilities=[ability(id="muisca-colombian-005-1", label="Solar Verdict", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        translated_figure(source=source["muisca-colombian-006"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=4, rules_text="On play: Return an enemy Figure that costs 4 or less to its owner's hand.", abilities=[ability(id="muisca-colombian-006-1", label="Clever Reversal", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 4})])]),
        translated_figure(source=source["muisca-colombian-007"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=7, rules_text="Guard. On play: Heal your Hero for 3.", keywords=["guard"], abilities=[ability(id="muisca-colombian-007-1", label="Rainfather", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=3, scope="friendly_hero")])]),
        translated_figure(source=source["muisca-colombian-008"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Heal a friendly Figure for 4. Give it Ward this turn.", abilities=[ability(id="muisca-colombian-008-1", label="Rainbow Restoration", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=4), effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["muisca-colombian-009"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["muisca-colombian-010"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=4, rules_text="On play: Draw a card. Give a friendly Figure +1 Attack.", abilities=[ability(id="muisca-colombian-010-1", label="Festival Counsel", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.DRAW_CARDS, amount=1), effect(EffectKind.GRANT_STATS, attack=1)])]),
        translated_figure(source=source["muisca-colombian-011"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="Guard.", keywords=["guard"]),
        translated_figure(source=source["muisca-colombian-012"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Freeze an enemy Figure.", abilities=[ability(id="muisca-colombian-012-1", label="Dream Sleep", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.FREEZE)])]),
        translated_figure(source=source["muisca-colombian-013"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=5, rules_text="On play: Give another friendly Figure +1/+1.", abilities=[ability(id="muisca-colombian-013-1", label="Golden Charge", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1, health=1)])]),
        translated_figure(source=source["muisca-colombian-014"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Heal all friendly Figures for 1.", abilities=[ability(id="muisca-colombian-014-1", label="Questing Mercy", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["muisca-colombian-015"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="Reborn.", keywords=["reborn"]),
        translated_figure(source=source["muisca-colombian-016"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Gain 1 Ritual Mana.", abilities=[ability(id="muisca-colombian-016-1", label="Hidden Offering", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.GAIN_RITUAL_MANA, amount=1)])]),
        translated_figure(source=source["muisca-colombian-017"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=3, rules_text="On play: Draw a card from your top 3 cards.", abilities=[ability(id="muisca-colombian-017-1", label="Road of Light", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1)])]),
        translated_figure(source=source["muisca-colombian-018"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="On play: Freeze an enemy Figure.", abilities=[ability(id="muisca-colombian-018-1", label="Moon Warning", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.FREEZE)])]),
        translated_figure(source=source["muisca-colombian-019"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard.", keywords=["guard"]),
        translated_figure(source=source["muisca-colombian-020"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. When this dies, summon a Lake Child.", keywords=["guard"], abilities=[ability(id="muisca-colombian-020-1", label="Birth Lake", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_DEATH, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="muisca-token-lake-child")])]),
        token(culture_slug=culture_slug, set_code=set_code, id="muisca-token-sunbird", name="Sunbird", attack=2, health=2, subtype="spirit", traits=["sun", "light", "sky"], rules_text="Rush.", keywords=["rush"]),
        token(culture_slug=culture_slug, set_code=set_code, id="muisca-token-lake-child", name="Lake Child", attack=1, health=2, subtype="spirit", traits=["water", "ritual", "creation"], rules_text="Guard.", keywords=["guard"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="muisca-colombian-spell-golden-counsel", name="Golden Counsel", cost=2, speed=Speed.BURST, rarity="common", traits=["wisdom", "light", "law"], rules_text="Draw a card from your top 3 cards.", abilities=[ability(id="muisca-colombian-spell-golden-counsel-1", label="Golden Counsel", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="muisca-colombian-spell-rainbow-restoration", name="Rainbow Restoration", cost=2, speed=Speed.BURST, rarity="common", traits=["rainbow", "healing", "water"], rules_text="Heal a friendly Figure for 3. Give it Ward this turn.", abilities=[ability(id="muisca-colombian-spell-rainbow-restoration-1", label="Rainbow Restoration", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=3), effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="muisca-colombian-spell-sun-verdict", name="Sun Verdict", cost=4, speed=Speed.FAST, rarity="common", traits=["sun", "light", "justice"], rules_text="Deal 4 damage to an enemy Figure.", abilities=[ability(id="muisca-colombian-spell-sun-verdict-1", label="Sun Verdict", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="muisca-colombian-relic-golden-raft", name="Golden Raft", cost=3, rarity="rare", traits=["gold", "water", "ritual"], rules_text="At the end of your turn, heal a friendly Figure for 1.", abilities=[ability(id="muisca-colombian-relic-golden-raft-1", label="Ceremonial Offering", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_TURN_END, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=1)])]),
    ]

    pack = pack_payload(
        set_code=set_code,
        culture_slug=culture_slug,
        primary_family="Sanctuary",
        secondary_family="Oracle",
        hero_id=hero_id,
        notes=[
            "Wave-three translation keeps Muisca readable as healing-light control with bounded draw and freeze tools.",
            "Midgame stability comes from Bachue, Chibchacum, Sue, and the guard-heal raft shell.",
        ],
        cards=cards,
    )
    deck = deck_payload(
        name="Bochica Golden Bastion",
        hero_id=hero_id,
        notes=["Sanctuary deck with heal loops, careful draw smoothing, and visible light-based answers."],
        cards=[
            {"id": "muisca-colombian-015", "count": 2},
            {"id": "muisca-colombian-016", "count": 2},
            {"id": "muisca-colombian-008", "count": 2},
            {"id": "muisca-colombian-003", "count": 2},
            {"id": "muisca-colombian-020", "count": 2},
            {"id": "muisca-colombian-007", "count": 2},
            {"id": "muisca-colombian-005", "count": 2},
            {"id": "muisca-colombian-019", "count": 2},
            {"id": "muisca-colombian-002", "count": 1},
            {"id": "muisca-colombian-001", "count": 1},
            {"id": "muisca-colombian-spell-golden-counsel", "count": 2},
            {"id": "muisca-colombian-spell-rainbow-restoration", "count": 2},
            {"id": "muisca-colombian-spell-sun-verdict", "count": 1},
            {"id": "muisca-colombian-relic-golden-raft", "count": 1},
        ],
    )
    return pack, deck, str(CARDS_DIR / "muisca-colombian-v1.json"), str(DECKS_DIR / "muisca-colombian-bochica-golden-bastion.json")


def build_yanomami() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "yanomami"
    set_code = "yanomami-v1"
    hero_id = "yanomami-hero-omama-forest-breath"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Omama, Forest Breath",
            alignment="light",
            traits=["creation", "forest", "healing", "wisdom"],
            rules_text="Hero Power - Forest Breath (2): Summon a Forest Spirit.",
            abilities=[
                ability(
                    id=f"{hero_id}-1",
                    label="Forest Breath",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.NONE,
                    resource_cost=2,
                    effects=[effect(EffectKind.SUMMON_TOKEN, card_id="yanomami-token-forest-spirit")],
                    limit="once_each_turn",
                )
            ],
        ),
        translated_figure(source=source["yanomami-001"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=4, health=8, rules_text="On play: Summon two Forest Spirits. Heal all friendly Figures for 2.", abilities=[ability(id="yanomami-001-1", label="World Canopy", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="yanomami-token-forest-spirit"), effect(EffectKind.SUMMON_TOKEN, card_id="yanomami-token-forest-spirit")]), ability(id="yanomami-001-2", label="World Canopy", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        translated_figure(source=source["yanomami-002"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=6, rules_text="On play: Return a friendly Figure that costs 4 or less from your discard pile to your hand.", abilities=[ability(id="yanomami-002-1", label="Grave Call", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.RETURN_FROM_DISCARD, extra={"max_cost": 4})])]),
        translated_figure(source=source["yanomami-003"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=3, rules_text="Stealth.", keywords=["stealth"]),
        translated_figure(source=source["yanomami-004"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Summon a Forest Spirit.", abilities=[ability(id="yanomami-004-1", label="Teaching Feast", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="yanomami-token-forest-spirit")])]),
        translated_figure(source=source["yanomami-005"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="Ward. On play: Restore 3 Health to your Hero.", keywords=["ward"], abilities=[ability(id="yanomami-005-1", label="Otherworld Touch", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=3, scope="friendly_hero")])]),
        translated_figure(source=source["yanomami-006"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="Ward.", keywords=["ward"]),
        translated_figure(source=source["yanomami-007"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=5, rules_text="On play: Return a friendly Figure that costs 4 or less from your discard pile to your hand.", abilities=[ability(id="yanomami-007-1", label="Night Sickness", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.RETURN_FROM_DISCARD, extra={"max_cost": 4})])]),
        translated_figure(source=source["yanomami-008"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=3, rules_text="On play: Give a friendly Figure Ward this turn.", abilities=[ability(id="yanomami-008-1", label="Radiant Change", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["yanomami-009"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="Once each turn, after you play another friendly Figure, gain +1 Attack.", abilities=[ability(id="yanomami-009-1", label="Family March", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_FRIENDLY_PLAY, target_rule=TargetRule.SELF, effects=[effect(EffectKind.GRANT_STATS, attack=1)], limit="once_each_turn")]),
        translated_figure(source=source["yanomami-010"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["yanomami-011"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=3, rules_text="Reborn.", keywords=["reborn"]),
        translated_figure(source=source["yanomami-012"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=1, health=4, rules_text="Lifesteal.", keywords=["lifesteal"]),
        translated_figure(source=source["yanomami-013"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=3, health=2, rules_text=""),
        translated_figure(source=source["yanomami-014"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard.", keywords=["guard"]),
        translated_figure(source=source["yanomami-015"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Heal a friendly Figure for 2.", abilities=[ability(id="yanomami-015-1", label="River Mending", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=2)])]),
        translated_figure(source=source["yanomami-016"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="When this dies, summon a Spirit Ancestor.", abilities=[ability(id="yanomami-016-1", label="Ancestor Return", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_DEATH, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="yanomami-token-spirit-ancestor")])]),
        translated_figure(source=source["yanomami-017"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Draw a card and restore 1 Health to your Hero.", abilities=[ability(id="yanomami-017-1", label="Vision Draft", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1), effect(EffectKind.HEAL, amount=1, scope="friendly_hero")])]),
        translated_figure(source=source["yanomami-018"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Deal 1 damage to all other Figures.", abilities=[ability(id="yanomami-018-1", label="Dry Season Heat", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_other_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)])]),
        translated_figure(source=source["yanomami-019"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="On play: Freeze an enemy Figure. Restore 2 Health to your Hero.", abilities=[ability(id="yanomami-019-1", label="Rain Season", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.FREEZE)]), ability(id="yanomami-019-2", label="Rain Season", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["yanomami-020"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=3, health=7, rules_text="Guard. At the end of your turn, heal all friendly Figures for 1.", keywords=["guard"], abilities=[ability(id="yanomami-020-1", label="Watoriki Shelter", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_TURN_END, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        token(culture_slug=culture_slug, set_code=set_code, id="yanomami-token-forest-spirit", name="Forest Spirit", attack=1, health=2, subtype="spirit", traits=["forest", "spirit", "healing"]),
        token(culture_slug=culture_slug, set_code=set_code, id="yanomami-token-spirit-ancestor", name="Spirit Ancestor", attack=2, health=2, subtype="spirit", traits=["ancestor", "spirit", "memory"], rules_text="Guard.", keywords=["guard"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="yanomami-spell-shamanic-gathering", name="Shamanic Gathering", cost=3, speed=Speed.SLOW, rarity="common", traits=["ritual", "forest", "spirit"], rules_text="Summon two Forest Spirits.", abilities=[ability(id="yanomami-spell-shamanic-gathering-1", label="Shamanic Gathering", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="yanomami-token-forest-spirit"), effect(EffectKind.SUMMON_TOKEN, card_id="yanomami-token-forest-spirit")])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="yanomami-spell-ancestral-recall", name="Ancestral Recall", cost=2, speed=Speed.BURST, rarity="common", traits=["ancestor", "ritual", "memory"], rules_text="Return a friendly Figure that costs 4 or less from your discard pile to your hand.", abilities=[ability(id="yanomami-spell-ancestral-recall-1", label="Ancestral Recall", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.NONE, effects=[effect(EffectKind.RETURN_FROM_DISCARD, extra={"max_cost": 4})])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="yanomami-spell-canopy-renewal", name="Canopy Renewal", cost=2, speed=Speed.BURST, rarity="common", traits=["healing", "forest", "renewal"], rules_text="Heal all friendly Figures for 2.", abilities=[ability(id="yanomami-spell-canopy-renewal-1", label="Canopy Renewal", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="yanomami-relic-yakoana-smoke", name="Yakoana Smoke", cost=3, rarity="rare", traits=["ritual", "vision", "spirit"], rules_text="Once each turn, after you play a friendly Figure, restore 1 Health to your Hero and give that Figure +1 Attack.", abilities=[ability(id="yanomami-relic-yakoana-smoke-1", label="Vision Breath", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_FRIENDLY_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=1, scope="friendly_hero"), effect(EffectKind.GRANT_STATS, attack=1)], limit="once_each_turn")]),
    ]

    pack = pack_payload(
        set_code=set_code,
        culture_slug=culture_slug,
        primary_family="Wildhost",
        secondary_family="Gravebound",
        hero_id=hero_id,
        notes=[
            "Wave-three translation keeps Yanomami readable as spirit-swarm resilience rather than hidden combo recursion.",
            "Midgame anchors live in Omama, Yoasi, Nomasiri, and the guard-heal shelter shell.",
        ],
        cards=cards,
    )
    deck = deck_payload(
        name="Omama Spirit Renewal",
        hero_id=hero_id,
        notes=["Wildhost deck with recursive glue, steady token pressure, and visible healing recovery."],
        cards=[
            {"id": "yanomami-015", "count": 2},
            {"id": "yanomami-016", "count": 2},
            {"id": "yanomami-004", "count": 2},
            {"id": "yanomami-014", "count": 2},
            {"id": "yanomami-019", "count": 2},
            {"id": "yanomami-020", "count": 2},
            {"id": "yanomami-007", "count": 2},
            {"id": "yanomami-010", "count": 2},
            {"id": "yanomami-001", "count": 1},
            {"id": "yanomami-002", "count": 1},
            {"id": "yanomami-spell-shamanic-gathering", "count": 2},
            {"id": "yanomami-spell-ancestral-recall", "count": 2},
            {"id": "yanomami-spell-canopy-renewal", "count": 1},
            {"id": "yanomami-relic-yakoana-smoke", "count": 1},
        ],
    )
    return pack, deck, str(CARDS_DIR / "yanomami-v1.json"), str(DECKS_DIR / "yanomami-omama-spirit-renewal.json")


def write_payload(path: str, payload: dict[str, object]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    builds = [build_cherokee(), build_muisca_colombian(), build_yanomami()]
    summary: list[dict[str, object]] = []
    for pack, deck, pack_path, deck_path in builds:
        write_payload(pack_path, pack)
        write_payload(deck_path, deck)
        summary.append(
            {
                "pack": pack_path,
                "deck": deck_path,
                "cards": len(pack["cards"]),
                "collectible_non_hero_cards": sum(1 for card in pack["cards"] if card["card_type"] != "hero" and card.get("collectible", True)),
                "sample_deck_cards": sum(int(card["count"]) for card in deck["cards"]),
            }
        )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
