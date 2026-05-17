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


def ability(*, id: str, label: str, timing: AbilityTiming | str, trigger: AbilityTrigger | str, target_rule: TargetRule | str, effects: list[EffectSpec], resource_cost: int | None = None, conditions: list[dict[str, object]] | None = None, limit: str | None = None) -> AbilitySpec:
    return AbilitySpec(id=id, label=label, timing=timing, trigger=trigger, target_rule=target_rule, resource_cost=resource_cost, conditions=[] if conditions is None else conditions, effects=effects, limit=limit)


def effect(kind: EffectKind | str, **kwargs: object) -> EffectSpec:
    payload = dict(kwargs)
    payload.setdefault("extra", {})
    return EffectSpec(kind=kind, **payload)


def source_index(culture_slug: str) -> dict[str, dict[str, object]]:
    payload = json.loads((FIGURES_DIR / f"{culture_slug}.json").read_text(encoding="utf-8"))
    return {figure["id"]: figure for figure in payload["figures"]}


def translated_figure(*, source: dict[str, object], culture_slug: str, set_code: str, cost: int, attack: int, health: int, rules_text: str, keywords: list[str] | None = None, abilities: list[AbilitySpec] | None = None) -> CardSpec:
    card = CardSpec(id=str(source["id"]), name=str(source["name"]), card_type=CardType.FIGURE, culture_slug=culture_slug, rarity=str(source["rarity"]), alignment=str(source["alignment"]), traits=list(source["domains"]), rules_text=rules_text, cost=cost, subtypes=[str(source["type"])], keywords=keywords or [], unique=str(source["rarity"]) == "legendary", legendary=str(source["rarity"]) == "legendary", set_code=set_code, attack=attack, health=health, abilities=abilities or [])
    card.validate()
    return card


def hero(*, culture_slug: str, set_code: str, id: str, name: str, alignment: str, traits: list[str], rules_text: str, abilities: list[AbilitySpec]) -> CardSpec:
    card = CardSpec(id=id, name=name, card_type=CardType.HERO, culture_slug=culture_slug, rarity="legendary", alignment=alignment, traits=traits, rules_text=rules_text, unique=True, legendary=True, set_code=set_code, abilities=abilities)
    card.validate()
    return card


def spell(*, culture_slug: str, set_code: str, id: str, name: str, cost: int, speed: Speed, rarity: str, traits: list[str], rules_text: str, abilities: list[AbilitySpec]) -> CardSpec:
    card = CardSpec(id=id, name=name, card_type=CardType.SPELL, culture_slug=culture_slug, rarity=rarity, alignment="neutral", traits=traits, rules_text=rules_text, cost=cost, speed=speed, set_code=set_code, abilities=abilities)
    card.validate()
    return card


def relic(*, culture_slug: str, set_code: str, id: str, name: str, cost: int, rarity: str, traits: list[str], rules_text: str, abilities: list[AbilitySpec]) -> CardSpec:
    card = CardSpec(id=id, name=name, card_type=CardType.RELIC, culture_slug=culture_slug, rarity=rarity, alignment="neutral", traits=traits, rules_text=rules_text, cost=cost, set_code=set_code, unique=rarity == "legendary", legendary=rarity == "legendary", abilities=abilities)
    card.validate()
    return card


def token(*, culture_slug: str, set_code: str, id: str, name: str, attack: int, health: int, subtype: str, traits: list[str], rules_text: str = "", keywords: list[str] | None = None, abilities: list[AbilitySpec] | None = None) -> CardSpec:
    card = CardSpec(id=id, name=name, card_type=CardType.TOKEN, culture_slug=culture_slug, rarity="token", alignment="neutral", traits=traits, rules_text=rules_text, cost=0, subtypes=[subtype], keywords=keywords or [], token=True, collectible=False, set_code=set_code, attack=attack, health=health, abilities=abilities or [])
    card.validate()
    return card


def pack_payload(*, set_code: str, culture_slug: str, primary_family: str, secondary_family: str, hero_id: str, notes: list[str], cards: list[CardSpec]) -> dict[str, object]:
    return {"set_code": set_code, "culture_slug": culture_slug, "primary_family": primary_family, "secondary_family": secondary_family, "hero_id": hero_id, "notes": notes, "cards": [dataclass_to_dict(card) for card in cards]}


def deck_payload(*, name: str, hero_id: str, notes: list[str], cards: list[dict[str, object]]) -> dict[str, object]:
    return {"name": name, "format": "mythic-clash-v1", "hero_id": hero_id, "notes": notes, "cards": cards}


def build_guarani() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "guarani"
    set_code = "guarani-v1"
    hero_id = "guarani-hero-tupa-stormfather"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Tupa, Stormfather of the First Sky",
            alignment="light",
            traits=["creation", "storm", "sky", "light"],
            rules_text="Hero Power - Rolling Sky (2): Deal 1 damage to an enemy Figure. If it survives, summon a Forest Wisp.",
            abilities=[
                ability(id=f"{hero_id}-1", label="Rolling Sky", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, resource_cost=2, effects=[effect(EffectKind.DEAL_DAMAGE, amount=1), effect(EffectKind.SUMMON_TOKEN, card_id="guarani-token-forest-wisp", extra={"if_target_survived_damage": True})], limit="once_each_turn")
            ],
        ),
        translated_figure(source=source["guarani-001"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=7, rules_text="On play: Summon a Storm Hawk and deal 2 damage to all enemy Figures.", abilities=[ability(id="guarani-001-1", label="First Thunder", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="guarani-token-storm-hawk")]), ability(id="guarani-001-2", label="First Thunder", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        translated_figure(source=source["guarani-002"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=6, rules_text="Stealth. At the end of your turn, heal your Hero for 2.", keywords=["stealth"], abilities=[ability(id="guarani-002-1", label="Moon Garden", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_TURN_END, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["guarani-003"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Return an enemy Figure that costs 4 or less to its owner's hand.", abilities=[ability(id="guarani-003-1", label="Shadow Eclipse", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 4})])]),
        translated_figure(source=source["guarani-004"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Give a friendly Figure +2/+2 this turn.", abilities=[ability(id="guarani-004-1", label="Night Blessing", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=2, health=2, duration="turn")])]),
        translated_figure(source=source["guarani-005"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Deal 1 damage to all enemy Figures.", abilities=[ability(id="guarani-005-1", label="Burning Maw", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)])]),
        translated_figure(source=source["guarani-006"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="Poisonous.", keywords=["poisonous"]),
        translated_figure(source=source["guarani-007"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="On play: Deal 4 damage to an enemy Figure.", abilities=[ability(id="guarani-007-1", label="Ruinous Blow", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        translated_figure(source=source["guarani-008"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=3, rules_text="Stealth. On play: Summon a Forest Wisp.", keywords=["stealth"], abilities=[ability(id="guarani-008-1", label="Sleepy Trickster", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="guarani-token-forest-wisp")])]),
        translated_figure(source=source["guarani-009"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=4, rules_text="On play: Heal all friendly Figures for 1.", abilities=[ability(id="guarani-009-1", label="Forest Plenty", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["guarani-010"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Summon a Forest Wisp.", abilities=[ability(id="guarani-010-1", label="Night Hunger", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="guarani-token-forest-wisp")])]),
        translated_figure(source=source["guarani-011"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=5, rules_text="On play: Return a friendly Figure that costs 4 or less from your discard pile to your hand.", abilities=[ability(id="guarani-011-1", label="Ghost Return", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.RETURN_FROM_DISCARD, extra={"max_cost": 4})])]),
        translated_figure(source=source["guarani-012"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="Stealth. On play: Summon a Forest Wisp.", keywords=["stealth"], abilities=[ability(id="guarani-012-1", label="Pombero's Path", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="guarani-token-forest-wisp")])]),
        translated_figure(source=source["guarani-013"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard. On play: Draw a card.", keywords=["guard"], abilities=[ability(id="guarani-013-1", label="Law of the Grove", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["guarani-014"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Give a friendly Figure Ward this turn.", abilities=[ability(id="guarani-014-1", label="Radiant Virtue", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["guarani-015"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="Ward.", keywords=["ward"]),
        translated_figure(source=source["guarani-016"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Draw a card.", abilities=[ability(id="guarani-016-1", label="Moon Crafter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["guarani-017"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Summon a Forest Wisp and heal your Hero for 2.", abilities=[ability(id="guarani-017-1", label="Herbal Spirit", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="guarani-token-forest-wisp"), effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["guarani-018"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Summon a Forest Wisp.", keywords=["guard"], abilities=[ability(id="guarani-018-1", label="First Father", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="guarani-token-forest-wisp")])]),
        translated_figure(source=source["guarani-019"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Heal a friendly Figure for 3.", keywords=["guard"], abilities=[ability(id="guarani-019-1", label="Earth Mother", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=3)])]),
        translated_figure(source=source["guarani-020"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=3, rules_text="On play: Deal 2 damage to an enemy Figure.", abilities=[ability(id="guarani-020-1", label="Fire Serpent", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        token(culture_slug=culture_slug, set_code=set_code, id="guarani-token-forest-wisp", name="Forest Wisp", attack=1, health=1, subtype="spirit", traits=["forest", "spirit", "trickster"], rules_text="Stealth.", keywords=["stealth"]),
        token(culture_slug=culture_slug, set_code=set_code, id="guarani-token-storm-hawk", name="Storm Hawk", attack=2, health=1, subtype="spirit", traits=["storm", "sky", "bird"], rules_text="Rush.", keywords=["rush"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="guarani-spell-tempest-surge", name="Tempest Surge", cost=3, speed=Speed.FAST, rarity="common", traits=["storm", "sky", "tempo"], rules_text="Deal 2 damage to all enemy Figures.", abilities=[ability(id="guarani-spell-tempest-surge-1", label="Tempest Surge", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="guarani-spell-moon-veil", name="Moon Veil", cost=2, speed=Speed.BURST, rarity="common", traits=["moon", "trickery", "night"], rules_text="Give a friendly Figure Stealth this turn. Draw a card.", abilities=[ability(id="guarani-spell-moon-veil-1", label="Moon Veil", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="stealth", duration="turn"), effect(EffectKind.DRAW_CARDS, amount=1)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="guarani-spell-rain-blessing", name="Rain Blessing", cost=2, speed=Speed.BURST, rarity="common", traits=["forest", "fertility", "healing"], rules_text="Heal all friendly Figures for 2.", abilities=[ability(id="guarani-spell-rain-blessing-1", label="Rain Blessing", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="guarani-relic-thunder-shrine", name="Thunder Shrine", cost=3, rarity="rare", traits=["storm", "ritual", "sky"], rules_text="Once each turn, after a friendly Figure attacks, deal 1 damage to the enemy Hero.", abilities=[ability(id="guarani-relic-thunder-shrine-1", label="Echoing Sky", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_ATTACK_DECLARED, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=1, scope="enemy_hero")], limit="once_each_turn")]),
    ]

    pack = pack_payload(set_code=set_code, culture_slug=culture_slug, primary_family="Wildhost", secondary_family="Tempest", hero_id=hero_id, notes=["Wave-four translation keeps Guarani readable as trickster-swarm pressure with visible storm finishers.", "Midgame anchors live in Tupa, Tupa's storm package, Monai, and the guard-heal shell."], cards=cards)
    deck = deck_payload(name="Tupa Wild Tempest", hero_id=hero_id, notes=["Swarm-pressure deck with token glue, storm clears, and straightforward burn follow-through."], cards=[
        {"id": "guarani-012", "count": 2},
        {"id": "guarani-015", "count": 2},
        {"id": "guarani-016", "count": 2},
        {"id": "guarani-017", "count": 2},
        {"id": "guarani-013", "count": 2},
        {"id": "guarani-020", "count": 2},
        {"id": "guarani-018", "count": 2},
        {"id": "guarani-005", "count": 2},
        {"id": "guarani-007", "count": 1},
        {"id": "guarani-001", "count": 1},
        {"id": "guarani-spell-tempest-surge", "count": 2},
        {"id": "guarani-spell-moon-veil", "count": 2},
        {"id": "guarani-spell-rain-blessing", "count": 1},
        {"id": "guarani-relic-thunder-shrine", "count": 1},
    ])
    return pack, deck, str(CARDS_DIR / "guarani-v1.json"), str(DECKS_DIR / "guarani-tupa-wild-tempest.json")


def build_mapuche() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "mapuche"
    set_code = "mapuche-v1"
    hero_id = "mapuche-hero-ngenechen-earth-sky"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Ngenechen, Earth and Sky",
            alignment="light",
            traits=["creation", "earth", "spirit", "wisdom"],
            rules_text="Hero Power - Stone and Storm (2): Deal 1 damage to an enemy Figure. Freeze it.",
            abilities=[
                ability(
                    id=f"{hero_id}-1",
                    label="Stone and Storm",
                    timing=AbilityTiming.SLOW,
                    trigger=AbilityTrigger.MANUAL,
                    target_rule=TargetRule.ENEMY_FIGURE,
                    resource_cost=2,
                    effects=[
                        effect(EffectKind.DEAL_DAMAGE, amount=1),
                        effect(EffectKind.FREEZE),
                    ],
                    limit="once_each_turn",
                )
            ],
        ),
        translated_figure(source=source["mapuche-001"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=8, rules_text="On play: Summon a Mapu Spirit and draw a card.", abilities=[ability(id="mapuche-001-1", label="World Seed", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="mapuche-token-mapu-spirit"), effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["mapuche-002"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=6, rules_text="On play: Deal 4 damage to an enemy Figure.", abilities=[ability(id="mapuche-002-1", label="Solar Ascendance", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        translated_figure(source=source["mapuche-003"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="Stealth. At the end of your turn, restore 2 Health to your Hero.", keywords=["stealth"], abilities=[ability(id="mapuche-003-1", label="Moonlit Veil", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_TURN_END, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["mapuche-004"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=6, rules_text="On play: Deal 2 damage to all enemy Figures.", abilities=[ability(id="mapuche-004-1", label="Ember Wrath", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        translated_figure(source=source["mapuche-005"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Draw a card.", abilities=[ability(id="mapuche-005-1", label="Vault of Heaven", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["mapuche-006"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=3, health=8, rules_text="Guard. On play: Heal all friendly Figures for 1.", keywords=["guard"], abilities=[ability(id="mapuche-006-1", label="Stoneheart Guard", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["mapuche-007"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=5, rules_text="On play: Return an enemy Figure that costs 4 or less to its owner's hand.", abilities=[ability(id="mapuche-007-1", label="Ocean's Claim", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 4})])]),
        translated_figure(source=source["mapuche-008"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Deal 1 damage to all other Figures.", abilities=[ability(id="mapuche-008-1", label="Volcanic Burst", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_other_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)])]),
        translated_figure(source=source["mapuche-009"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=3, rules_text="On play: Deal 2 damage to an enemy Figure.", abilities=[ability(id="mapuche-009-1", label="Shadow Eclipse", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        translated_figure(source=source["mapuche-010"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Give a friendly Figure Ward this turn.", abilities=[ability(id="mapuche-010-1", label="Radiant Aegis", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["mapuche-011"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=3, rules_text="Rush. On play: Give a friendly Figure +1 Attack.", keywords=["rush"], abilities=[ability(id="mapuche-011-1", label="Mythic Presence", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1)])]),
        translated_figure(source=source["mapuche-012"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=6, rules_text="On play: Deal 2 damage to all enemy Figures. Deal 1 damage to the enemy Hero.", abilities=[ability(id="mapuche-012-1", label="Storm Crown", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)]), ability(id="mapuche-012-2", label="Storm Crown", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=1, scope="enemy_hero")])]),
        translated_figure(source=source["mapuche-013"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard. On play: Restore 2 Health to your Hero.", keywords=["guard"], abilities=[ability(id="mapuche-013-1", label="Tidal Ward", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["mapuche-014"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["mapuche-015"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Heal a friendly Figure for 3.", abilities=[ability(id="mapuche-015-1", label="Restoring Rite", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=3)])]),
        translated_figure(source=source["mapuche-016"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Deal 1 damage to all enemy Figures.", abilities=[ability(id="mapuche-016-1", label="Ember Wrath", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)])]),
        translated_figure(source=source["mapuche-017"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Draw a card from your top 3 cards.", abilities=[ability(id="mapuche-017-1", label="Ancient Counsel", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1)])]),
        translated_figure(source=source["mapuche-018"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard. On play: Give a friendly Figure +1/+1.", keywords=["guard"], abilities=[ability(id="mapuche-018-1", label="Elder Memory", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1, health=1)])]),
        translated_figure(source=source["mapuche-019"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Give a friendly Figure Ward this turn.", keywords=["guard"], abilities=[ability(id="mapuche-019-1", label="Stoneheart Guard", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["mapuche-020"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="Poisonous. On play: Freeze an enemy Figure.", keywords=["poisonous"], abilities=[ability(id="mapuche-020-1", label="Coiled Fate", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.FREEZE)])]),
        token(culture_slug=culture_slug, set_code=set_code, id="mapuche-token-mapu-spirit", name="Mapu Spirit", attack=1, health=2, subtype="spirit", traits=["earth", "spirit", "protection"], rules_text="Guard.", keywords=["guard"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="mapuche-spell-serpent-flood", name="Serpent Flood", cost=3, speed=Speed.FAST, rarity="common", traits=["sea", "serpent", "tempo"], rules_text="Return an enemy Figure that costs 4 or less to its owner's hand.", abilities=[ability(id="mapuche-spell-serpent-flood-1", label="Serpent Flood", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 4})])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="mapuche-spell-machi-rite", name="Machi Rite", cost=2, speed=Speed.BURST, rarity="common", traits=["ritual", "healing", "spirit"], rules_text="Heal all friendly Figures for 2.", abilities=[ability(id="mapuche-spell-machi-rite-1", label="Machi Rite", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="mapuche-spell-pillan-judgment", name="Pillan's Judgment", cost=4, speed=Speed.FAST, rarity="common", traits=["storm", "fire", "justice"], rules_text="Deal 4 damage to an enemy Figure.", abilities=[ability(id="mapuche-spell-pillan-judgment-1", label="Pillan's Judgment", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="mapuche-relic-kultrun-heights", name="Kultrun of the Heights", cost=3, rarity="rare", traits=["ritual", "mountain", "wisdom"], rules_text="Once each turn, after you play a friendly Figure, restore 1 Health to your Hero and give that Figure +1 Health.", abilities=[ability(id="mapuche-relic-kultrun-heights-1", label="Mountain Rhythm", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_FRIENDLY_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=1, scope="friendly_hero"), effect(EffectKind.GRANT_STATS, health=1)], limit="once_each_turn")]),
    ]

    pack = pack_payload(set_code=set_code, culture_slug=culture_slug, primary_family="Tempest", secondary_family="Sanctuary", hero_id=hero_id, notes=["Wave-four translation keeps Mapuche readable as storm-control with serpent tempo and sturdy earth protection.", "Midgame anchors live in Pillan, Tren Tren Vilu, Peripillan, and the guard-plus-freeze shell."], cards=cards)
    deck = deck_payload(name="Ngenechen Storm Bastion", hero_id=hero_id, notes=["Control-tempo deck with serpent bounce, storm clears, and visible guard-based stabilization."], cards=[
        {"id": "mapuche-014", "count": 2},
        {"id": "mapuche-015", "count": 2},
        {"id": "mapuche-017", "count": 2},
        {"id": "mapuche-013", "count": 2},
        {"id": "mapuche-018", "count": 2},
        {"id": "mapuche-007", "count": 2},
        {"id": "mapuche-019", "count": 2},
        {"id": "mapuche-006", "count": 2},
        {"id": "mapuche-004", "count": 1},
        {"id": "mapuche-012", "count": 1},
        {"id": "mapuche-spell-serpent-flood", "count": 2},
        {"id": "mapuche-spell-machi-rite", "count": 2},
        {"id": "mapuche-spell-pillan-judgment", "count": 1},
        {"id": "mapuche-relic-kultrun-heights", "count": 1},
    ])
    return pack, deck, str(CARDS_DIR / "mapuche-v1.json"), str(DECKS_DIR / "mapuche-ngenechen-storm-bastion.json")


def write_payload(path: str, payload: dict[str, object]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    builds = [build_guarani(), build_mapuche()]
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
