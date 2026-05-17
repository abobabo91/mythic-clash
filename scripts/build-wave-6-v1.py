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


def build_taino_caribbean() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "taino-caribbean"
    set_code = "taino-caribbean-v1"
    hero_id = "taino-caribbean-hero-yucahu-sea-root"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Yucahu, Sea Root Father",
            alignment="light",
            traits=["cassava", "sea", "fertility", "life"],
            rules_text="Hero Power - Guiding Tide (2): Heal a friendly Figure for 2. Give it +1 Attack this turn.",
            abilities=[ability(id=f"{hero_id}-1", label="Guiding Tide", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.FRIENDLY_FIGURE, resource_cost=2, effects=[effect(EffectKind.HEAL, amount=2), effect(EffectKind.GRANT_STATS, attack=1, duration="turn")], limit="once_each_turn")],
        ),
        translated_figure(source=source["taino-caribbean-001"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=7, rules_text="On play: Return an enemy Figure that costs 4 or less to its owner's hand. Heal your Hero for 2.", abilities=[ability(id="taino-caribbean-001-1", label="Sea Root Father", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 4})]), ability(id="taino-caribbean-001-2", label="Sea Root Father", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["taino-caribbean-002"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=7, rules_text="At the end of your turn, heal all friendly Figures for 1.", abilities=[ability(id="taino-caribbean-002-1", label="Mother Waters", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_TURN_END, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["taino-caribbean-003"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=6, rules_text="On play: Deal 2 damage to all enemy Figures.", abilities=[ability(id="taino-caribbean-003-1", label="Juracan's Wake", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        translated_figure(source=source["taino-caribbean-004"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=6, rules_text="On play: Deal 1 damage to all enemy Figures. Freeze an enemy Figure.", abilities=[ability(id="taino-caribbean-004-1", label="Hurricane Rage", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)]), ability(id="taino-caribbean-004-2", label="Hurricane Rage", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.FREEZE)])]),
        translated_figure(source=source["taino-caribbean-005"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="On play: Heal all friendly Figures for 2.", abilities=[ability(id="taino-caribbean-005-1", label="Rainfall Plenty", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        translated_figure(source=source["taino-caribbean-006"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="On play: Deal 4 damage to an enemy Figure.", abilities=[ability(id="taino-caribbean-006-1", label="Clear Sky Flame", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        translated_figure(source=source["taino-caribbean-007"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="On play: Deal 4 damage to an enemy Figure. Deal 1 damage to the enemy Hero.", abilities=[ability(id="taino-caribbean-007-1", label="Thunder Warning", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)]), ability(id="taino-caribbean-007-2", label="Thunder Warning", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=1, scope="enemy_hero")])]),
        translated_figure(source=source["taino-caribbean-008"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="On play: Heal all friendly Figures for 1 and restore 2 Health to your Hero.", abilities=[ability(id="taino-caribbean-008-1", label="Flood Shelter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)]), ability(id="taino-caribbean-008-2", label="Flood Shelter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["taino-caribbean-009"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=5, rules_text="On play: An enemy Figure can't attack next turn.", abilities=[ability(id="taino-caribbean-009-1", label="Underworld Hound", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.SET_CANT_ATTACK)])]),
        translated_figure(source=source["taino-caribbean-010"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=3, rules_text="Stealth. On play: Draw a card.", keywords=["stealth"], abilities=[ability(id="taino-caribbean-010-1", label="Clever Shell", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["taino-caribbean-011"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Deal 1 damage to all enemy Figures.", abilities=[ability(id="taino-caribbean-011-1", label="Fire From Memory", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)])]),
        translated_figure(source=source["taino-caribbean-012"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard. On play: Restore 2 Health to your Hero.", keywords=["guard"], abilities=[ability(id="taino-caribbean-012-1", label="Birth Cavern", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["taino-caribbean-013"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=5, rules_text="On play: Return a friendly Figure that costs 4 or less from your discard pile to your hand.", abilities=[ability(id="taino-caribbean-013-1", label="Night Recall", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.RETURN_FROM_DISCARD, extra={"max_cost": 4})])]),
        translated_figure(source=source["taino-caribbean-014"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Heal a friendly Figure for 3.", abilities=[ability(id="taino-caribbean-014-1", label="Cassava Rite", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=3)])]),
        translated_figure(source=source["taino-caribbean-015"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Summon a Cemi Spirit.", keywords=["guard"], abilities=[ability(id="taino-caribbean-015-1", label="First Cavern", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="taino-caribbean-token-cemi-spirit")])]),
        translated_figure(source=source["taino-caribbean-016"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Draw a card.", abilities=[ability(id="taino-caribbean-016-1", label="Sea Messenger", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["taino-caribbean-017"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["taino-caribbean-018"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Give a friendly Figure Ward this turn.", abilities=[ability(id="taino-caribbean-018-1", label="Water Bond", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["taino-caribbean-019"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="On play: Summon a Cemi Spirit and gain 1 Ritual Mana.", abilities=[ability(id="taino-caribbean-019-1", label="Sky Creation", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="taino-caribbean-token-cemi-spirit"), effect(EffectKind.GAIN_RITUAL_MANA, amount=1)])]),
        translated_figure(source=source["taino-caribbean-020"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard.", keywords=["guard"]),
        token(culture_slug=culture_slug, set_code=set_code, id="taino-caribbean-token-cemi-spirit", name="Cemi Spirit", attack=1, health=2, subtype="spirit", traits=["ancestor", "spirit", "protection"], rules_text="Guard.", keywords=["guard"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="taino-caribbean-spell-hurricane-path", name="Hurricane Path", cost=3, speed=Speed.FAST, rarity="common", traits=["storm", "wind", "sea"], rules_text="Deal 2 damage to all enemy Figures.", abilities=[ability(id="taino-caribbean-spell-hurricane-path-1", label="Hurricane Path", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="taino-caribbean-spell-freshwater-blessing", name="Freshwater Blessing", cost=2, speed=Speed.BURST, rarity="common", traits=["water", "healing", "life"], rules_text="Heal all friendly Figures for 2.", abilities=[ability(id="taino-caribbean-spell-freshwater-blessing-1", label="Freshwater Blessing", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="taino-caribbean-spell-cemi-guidance", name="Cemi Guidance", cost=2, speed=Speed.BURST, rarity="common", traits=["ritual", "ancestor", "guidance"], rules_text="Draw a card from your top 3 cards.", abilities=[ability(id="taino-caribbean-spell-cemi-guidance-1", label="Cemi Guidance", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="taino-caribbean-relic-sea-zemi", name="Sea Zemi", cost=3, rarity="rare", traits=["sea", "ancestor", "ritual"], rules_text="Once each turn, after you play a friendly Figure, give that Figure +1 Health and restore 1 Health to your Hero.", abilities=[ability(id="taino-caribbean-relic-sea-zemi-1", label="Ancestral Current", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_FRIENDLY_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, health=1), effect(EffectKind.HEAL, amount=1, scope="friendly_hero")], limit="once_each_turn")]),
    ]

    pack = pack_payload(set_code=set_code, culture_slug=culture_slug, primary_family="Tidebound", secondary_family="Sanctuary", hero_id=hero_id, notes=["Wave-five translation keeps Taino Caribbean readable as tide-heal tempo with storm bursts and sturdy ritual bodies.", "Midgame anchors live in Atabey, Juracan, Yucahu, and the Cemi guard shell."], cards=cards)
    deck = deck_payload(name="Yucahu Tide Shelter", hero_id=hero_id, notes=["Tidebound deck with bounce, healing, storm clears, and visible board stabilization."], cards=[
        {"id": "taino-caribbean-017", "count": 2},
        {"id": "taino-caribbean-016", "count": 2},
        {"id": "taino-caribbean-018", "count": 2},
        {"id": "taino-caribbean-012", "count": 2},
        {"id": "taino-caribbean-020", "count": 2},
        {"id": "taino-caribbean-005", "count": 2},
        {"id": "taino-caribbean-015", "count": 2},
        {"id": "taino-caribbean-008", "count": 2},
        {"id": "taino-caribbean-001", "count": 1},
        {"id": "taino-caribbean-003", "count": 1},
        {"id": "taino-caribbean-spell-hurricane-path", "count": 2},
        {"id": "taino-caribbean-spell-freshwater-blessing", "count": 2},
        {"id": "taino-caribbean-spell-cemi-guidance", "count": 1},
        {"id": "taino-caribbean-relic-sea-zemi", "count": 1},
    ])
    return pack, deck, str(CARDS_DIR / "taino-caribbean-v1.json"), str(DECKS_DIR / "taino-caribbean-yucahu-tide-shelter.json")


def build_candomble_afro_brazilian() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "candomble-afro-brazilian"
    set_code = "candomble-afro-brazilian-v1"
    hero_id = "candomble-afro-brazilian-hero-exu-crossroads"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Exu, Crossroads Fire",
            alignment="neutral",
            traits=["trickster", "crossroads", "fire", "speech"],
            rules_text="Hero Power - Crossroads Spark (2): Deal 1 damage to an enemy Figure. Gain 1 Ritual Mana.",
            abilities=[ability(id=f"{hero_id}-1", label="Crossroads Spark", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, resource_cost=2, effects=[effect(EffectKind.DEAL_DAMAGE, amount=1), effect(EffectKind.GAIN_RITUAL_MANA, amount=1)], limit="once_each_turn")],
        ),
        translated_figure(source=source["candomble-afro-brazilian-001"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=6, rules_text="On play: Return an enemy Figure that costs 4 or less to its owner's hand.", abilities=[ability(id="candomble-afro-brazilian-001-1", label="Crossroads Turn", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 4})])]),
        translated_figure(source=source["candomble-afro-brazilian-002"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=7, rules_text="On play: Summon a Sacred Attendant and draw a card.", abilities=[ability(id="candomble-afro-brazilian-002-1", label="Peaceful Dawn", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="candomble-afro-brazilian-token-sacred-attendant"), effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["candomble-afro-brazilian-003"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=7, rules_text="At the end of your turn, heal all friendly Figures for 1.", abilities=[ability(id="candomble-afro-brazilian-003-1", label="Sea Mother", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_TURN_END, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["candomble-afro-brazilian-004"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="Rush. On play: Give another friendly Figure +1 Attack.", keywords=["rush"], abilities=[ability(id="candomble-afro-brazilian-004-1", label="Forged March", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1)])]),
        translated_figure(source=source["candomble-afro-brazilian-005"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="On play: Deal 4 damage to an enemy Figure. Deal 1 damage to the enemy Hero.", abilities=[ability(id="candomble-afro-brazilian-005-1", label="Royal Thunder", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)]), ability(id="candomble-afro-brazilian-005-2", label="Royal Thunder", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=1, scope="enemy_hero")])]),
        translated_figure(source=source["candomble-afro-brazilian-006"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Restore 2 Health to your Hero and draw a card.", abilities=[ability(id="candomble-afro-brazilian-006-1", label="River Grace", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero"), effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["candomble-afro-brazilian-007"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=6, rules_text="On play: Deal 2 damage to all enemy Figures.", abilities=[ability(id="candomble-afro-brazilian-007-1", label="Storm Queen", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        translated_figure(source=source["candomble-afro-brazilian-008"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=6, rules_text="Lifesteal.", keywords=["lifesteal"]),
        translated_figure(source=source["candomble-afro-brazilian-009"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Give a friendly Figure Ward this turn.", keywords=["guard"], abilities=[ability(id="candomble-afro-brazilian-009-1", label="Ancient Shelter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["candomble-afro-brazilian-010"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=3, rules_text="On play: Deal 2 damage to an enemy Figure.", abilities=[ability(id="candomble-afro-brazilian-010-1", label="Hunter's Mark", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        translated_figure(source=source["candomble-afro-brazilian-011"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=4, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["candomble-afro-brazilian-012"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Summon a Sacred Attendant.", abilities=[ability(id="candomble-afro-brazilian-012-1", label="Herb Keeper", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="candomble-afro-brazilian-token-sacred-attendant")])]),
        translated_figure(source=source["candomble-afro-brazilian-013"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=5, rules_text="On play: Give a friendly Figure +2 Attack this turn.", abilities=[ability(id="candomble-afro-brazilian-013-1", label="War Oath", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="turn")])]),
        translated_figure(source=source["candomble-afro-brazilian-014"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="On play: Draw a card.", abilities=[ability(id="candomble-afro-brazilian-014-1", label="Twin Fortune", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["candomble-afro-brazilian-015"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="Stealth.", keywords=["stealth"]),
        translated_figure(source=source["candomble-afro-brazilian-016"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["candomble-afro-brazilian-017"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="Poisonous.", keywords=["poisonous"]),
        translated_figure(source=source["candomble-afro-brazilian-018"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard.", keywords=["guard"]),
        translated_figure(source=source["candomble-afro-brazilian-019"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard. On play: Draw a card.", keywords=["guard"], abilities=[ability(id="candomble-afro-brazilian-019-1", label="Ancestor Drum", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["candomble-afro-brazilian-020"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=7, rules_text="On play: Heal all friendly Figures for 2.", abilities=[ability(id="candomble-afro-brazilian-020-1", label="Earth Renewal", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        token(culture_slug=culture_slug, set_code=set_code, id="candomble-afro-brazilian-token-sacred-attendant", name="Sacred Attendant", attack=1, health=2, subtype="spirit", traits=["ancestor", "ritual", "protection"], rules_text="Guard.", keywords=["guard"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="candomble-afro-brazilian-spell-crossroads-bargain", name="Crossroads Bargain", cost=2, speed=Speed.BURST, rarity="common", traits=["trickster", "speech", "ritual"], rules_text="Draw a card from your top 3 cards. Gain 1 Ritual Mana.", abilities=[ability(id="candomble-afro-brazilian-spell-crossroads-bargain-1", label="Crossroads Bargain", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1), effect(EffectKind.GAIN_RITUAL_MANA, amount=1)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="candomble-afro-brazilian-spell-thunder-axe", name="Thunder Axe", cost=4, speed=Speed.FAST, rarity="common", traits=["thunder", "fire", "justice"], rules_text="Deal 4 damage to an enemy Figure.", abilities=[ability(id="candomble-afro-brazilian-spell-thunder-axe-1", label="Thunder Axe", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="candomble-afro-brazilian-spell-river-offering", name="River Offering", cost=2, speed=Speed.BURST, rarity="common", traits=["river", "water", "healing"], rules_text="Heal all friendly Figures for 2.", abilities=[ability(id="candomble-afro-brazilian-spell-river-offering-1", label="River Offering", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="candomble-afro-brazilian-relic-orisha-drums", name="Drums of the Orixas", cost=3, rarity="rare", traits=["ritual", "ancestor", "speech"], rules_text="Once each turn, after you play a friendly Figure, give that Figure +1 Attack and restore 1 Health to your Hero.", abilities=[ability(id="candomble-afro-brazilian-relic-orisha-drums-1", label="Ritual Cadence", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_FRIENDLY_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1), effect(EffectKind.HEAL, amount=1, scope="friendly_hero")], limit="once_each_turn")]),
    ]

    pack = pack_payload(set_code=set_code, culture_slug=culture_slug, primary_family="Trickster", secondary_family="Sanctuary", hero_id=hero_id, notes=["Wave-five translation keeps Candomble readable as crossroads tempo backed by healing, guards, and selective thunder removal.", "Midgame anchors live in Iemanja, Xango, Iansa, and the guarded ancestor shell."], cards=cards)
    deck = deck_payload(name="Exu Crossroads Cadence", hero_id=hero_id, notes=["Tempo-support deck with bounce, ritual mana smoothing, guarded healing bodies, and visible thunder finishers."], cards=[
        {"id": "candomble-afro-brazilian-011", "count": 2},
        {"id": "candomble-afro-brazilian-014", "count": 2},
        {"id": "candomble-afro-brazilian-006", "count": 2},
        {"id": "candomble-afro-brazilian-012", "count": 2},
        {"id": "candomble-afro-brazilian-013", "count": 2},
        {"id": "candomble-afro-brazilian-009", "count": 2},
        {"id": "candomble-afro-brazilian-018", "count": 2},
        {"id": "candomble-afro-brazilian-020", "count": 2},
        {"id": "candomble-afro-brazilian-001", "count": 1},
        {"id": "candomble-afro-brazilian-007", "count": 1},
        {"id": "candomble-afro-brazilian-spell-crossroads-bargain", "count": 2},
        {"id": "candomble-afro-brazilian-spell-thunder-axe", "count": 2},
        {"id": "candomble-afro-brazilian-spell-river-offering", "count": 1},
        {"id": "candomble-afro-brazilian-relic-orisha-drums", "count": 1},
    ])
    return pack, deck, str(CARDS_DIR / "candomble-afro-brazilian-v1.json"), str(DECKS_DIR / "candomble-afro-brazilian-exu-crossroads-cadence.json")


def build_apache() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "apache"
    set_code = "apache-v1"
    hero_id = "apache-hero-killer-of-enemies"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Killer of Enemies, Dawn Champion",
            alignment="light",
            traits=["war", "justice", "sun", "strength"],
            rules_text="Hero Power - Dawn Strike (2): Give a friendly Figure +2 Attack this turn.",
            abilities=[ability(id=f"{hero_id}-1", label="Dawn Strike", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.FRIENDLY_FIGURE, resource_cost=2, effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="turn")], limit="once_each_turn")],
        ),
        translated_figure(source=source["apache-001"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=7, rules_text="On play: Summon a Sky Spirit and draw a card.", abilities=[ability(id="apache-001-1", label="Sky Birth", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="apache-token-sky-spirit"), effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["apache-002"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=7, rules_text="At the end of your turn, heal all friendly Figures for 1.", abilities=[ability(id="apache-002-1", label="Living Beauty", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_TURN_END, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["apache-003"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="Rush. On play: Give another friendly Figure +1 Attack.", keywords=["rush"], abilities=[ability(id="apache-003-1", label="Sun Justice", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1)])]),
        translated_figure(source=source["apache-004"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Restore 2 Health to your Hero.", keywords=["guard"], abilities=[ability(id="apache-004-1", label="River Shelter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["apache-005"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Heal all friendly Figures for 1.", keywords=["guard"], abilities=[ability(id="apache-005-1", label="Mountain Rite", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["apache-006"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Give a friendly Figure Ward this turn.", keywords=["guard"], abilities=[ability(id="apache-006-1", label="Night Shelter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["apache-007"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Draw a card.", abilities=[ability(id="apache-007-1", label="White Counsel", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["apache-008"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="On play: Heal all friendly Figures for 2.", abilities=[ability(id="apache-008-1", label="Rain Blessing", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        translated_figure(source=source["apache-009"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="Stealth.", keywords=["stealth"]),
        translated_figure(source=source["apache-010"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=5, rules_text="On play: Return a friendly Figure that costs 4 or less from your discard pile to your hand.", abilities=[ability(id="apache-010-1", label="Night Recall", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.RETURN_FROM_DISCARD, extra={"max_cost": 4})])]),
        translated_figure(source=source["apache-011"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=3, rules_text="Stealth. On play: Draw a card.", keywords=["stealth"], abilities=[ability(id="apache-011-1", label="Coyote Trail", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["apache-012"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=2, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["apache-013"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Deal 1 damage to all enemy Figures.", abilities=[ability(id="apache-013-1", label="Fire Circle", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)])]),
        translated_figure(source=source["apache-014"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard.", keywords=["guard"]),
        translated_figure(source=source["apache-015"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="Rush.", keywords=["rush"]),
        translated_figure(source=source["apache-016"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=5, rules_text="Poisonous.", keywords=["poisonous"]),
        translated_figure(source=source["apache-017"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="On play: Deal 4 damage to an enemy Figure.", abilities=[ability(id="apache-017-1", label="Thunder Chase", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        translated_figure(source=source["apache-018"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Give a friendly Figure Ward this turn.", abilities=[ability(id="apache-018-1", label="Turquoise Shield", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        translated_figure(source=source["apache-019"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Give a friendly Figure +1 Health.", abilities=[ability(id="apache-019-1", label="Enduring Aid", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, health=1)])]),
        translated_figure(source=source["apache-020"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Deal 2 damage to an enemy Figure.", keywords=["guard"], abilities=[ability(id="apache-020-1", label="Sunrise Ward", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        token(culture_slug=culture_slug, set_code=set_code, id="apache-token-sky-spirit", name="Sky Spirit", attack=2, health=1, subtype="spirit", traits=["sky", "spirit", "guidance"], rules_text="Rush.", keywords=["rush"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="apache-spell-war-cry", name="War Cry", cost=2, speed=Speed.BURST, rarity="common", traits=["war", "sun", "strength"], rules_text="Give a friendly Figure +2 Attack this turn.", abilities=[ability(id="apache-spell-war-cry-1", label="War Cry", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=2, duration="turn")])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="apache-spell-rain-dance", name="Rain Dance", cost=2, speed=Speed.BURST, rarity="common", traits=["rain", "water", "healing"], rules_text="Heal all friendly Figures for 2.", abilities=[ability(id="apache-spell-rain-dance-1", label="Rain Dance", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="apache-spell-thunder-path", name="Thunder Path", cost=4, speed=Speed.FAST, rarity="common", traits=["storm", "war", "sky"], rules_text="Deal 4 damage to an enemy Figure.", abilities=[ability(id="apache-spell-thunder-path-1", label="Thunder Path", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="apache-relic-mountain-drum", name="Mountain Drum", cost=3, rarity="rare", traits=["ritual", "mountain", "war"], rules_text="Once each turn, after you play a friendly Figure, give that Figure +1 Attack and restore 1 Health to your Hero.", abilities=[ability(id="apache-relic-mountain-drum-1", label="Marching Echo", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_FRIENDLY_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1), effect(EffectKind.HEAL, amount=1, scope="friendly_hero")], limit="once_each_turn")]),
    ]

    pack = pack_payload(set_code=set_code, culture_slug=culture_slug, primary_family="Vanguard", secondary_family="Sanctuary", hero_id=hero_id, notes=["Wave-six translation keeps Apache readable as heroic combat pressure with mountain guards and healing backup.", "Midgame anchors live in White Painted Woman, Ussen, Thunder Runner, and the guard-heal shell."], cards=cards)
    deck = deck_payload(name="Killer of Enemies Dawn March", hero_id=hero_id, notes=["Vanguard deck with rush pressure, guarded stabilizers, and visible combat buffs."], cards=[
        {"id": "apache-012", "count": 2},
        {"id": "apache-019", "count": 2},
        {"id": "apache-007", "count": 2},
        {"id": "apache-018", "count": 2},
        {"id": "apache-004", "count": 2},
        {"id": "apache-014", "count": 2},
        {"id": "apache-015", "count": 2},
        {"id": "apache-020", "count": 2},
        {"id": "apache-002", "count": 1},
        {"id": "apache-017", "count": 1},
        {"id": "apache-spell-war-cry", "count": 2},
        {"id": "apache-spell-rain-dance", "count": 2},
        {"id": "apache-spell-thunder-path", "count": 1},
        {"id": "apache-relic-mountain-drum", "count": 1},
    ])
    return pack, deck, str(CARDS_DIR / "apache-v1.json"), str(DECKS_DIR / "apache-killer-of-enemies-dawn-march.json")


def build_navajo_dine() -> tuple[dict[str, object], dict[str, object], str, str]:
    culture_slug = "navajo-dine"
    set_code = "navajo-dine-v1"
    hero_id = "navajo-dine-hero-spider-woman"
    source = source_index(culture_slug)

    cards: list[CardSpec] = [
        hero(
            culture_slug=culture_slug,
            set_code=set_code,
            id=hero_id,
            name="Spider Woman, Blessed Weaver",
            alignment="light",
            traits=["wisdom", "craft", "spirit", "creation"],
            rules_text="Hero Power - Blessed Thread (2): Heal a friendly Figure for 2. Give it Ward this turn.",
            abilities=[ability(id=f"{hero_id}-1", label="Blessed Thread", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.FRIENDLY_FIGURE, resource_cost=2, effects=[effect(EffectKind.HEAL, amount=2), effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")], limit="once_each_turn")],
        ),
        translated_figure(source=source["navajo-dine-001"], culture_slug=culture_slug, set_code=set_code, cost=6, attack=5, health=8, rules_text="On play: Summon a Holy Weaver and heal all friendly Figures for 2.", abilities=[ability(id="navajo-dine-001-1", label="Changing Blessing", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="navajo-dine-token-holy-weaver")]), ability(id="navajo-dine-001-2", label="Changing Blessing", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        translated_figure(source=source["navajo-dine-002"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="Rush. On play: Give another friendly Figure +1 Attack.", keywords=["rush"], abilities=[ability(id="navajo-dine-002-1", label="Monster Hunt", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, attack=1)])]),
        translated_figure(source=source["navajo-dine-003"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Restore 2 Health to your Hero.", keywords=["guard"], abilities=[ability(id="navajo-dine-003-1", label="Brother's Shield", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["navajo-dine-004"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=2, health=5, rules_text="On play: Draw a card from your top 3 cards.", abilities=[ability(id="navajo-dine-004-1", label="Ancient Counsel", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1)])]),
        translated_figure(source=source["navajo-dine-005"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Summon a Holy Weaver.", keywords=["guard"], abilities=[ability(id="navajo-dine-005-1", label="First Shelter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.SUMMON_TOKEN, card_id="navajo-dine-token-holy-weaver")])]),
        translated_figure(source=source["navajo-dine-006"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard. On play: Heal a friendly Figure for 3.", keywords=["guard"], abilities=[ability(id="navajo-dine-006-1", label="First Grace", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=3)])]),
        translated_figure(source=source["navajo-dine-007"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=5, rules_text="On play: Deal 1 damage to all enemy Figures.", abilities=[ability(id="navajo-dine-007-1", label="Starfire", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_enemy_figures", effects=[effect(EffectKind.DEAL_DAMAGE, amount=1)])]),
        translated_figure(source=source["navajo-dine-008"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="On play: Give a friendly Figure Ward this turn and restore 2 Health to your Hero.", abilities=[ability(id="navajo-dine-008-1", label="Shell Protection", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")]), ability(id="navajo-dine-008-2", label="Shell Protection", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["navajo-dine-009"], culture_slug=culture_slug, set_code=set_code, cost=2, attack=2, health=3, rules_text="On play: Draw a card.", abilities=[ability(id="navajo-dine-009-1", label="Talking Breath", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["navajo-dine-010"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=3, health=6, rules_text="Guard.", keywords=["guard"]),
        translated_figure(source=source["navajo-dine-011"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Heal all friendly Figures for 1.", abilities=[ability(id="navajo-dine-011-1", label="Water Sprinkler", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=1)])]),
        translated_figure(source=source["navajo-dine-012"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=3, rules_text="Stealth. On play: Draw a card.", keywords=["stealth"], abilities=[ability(id="navajo-dine-012-1", label="Traveler's Wit", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DRAW_CARDS, amount=1)])]),
        translated_figure(source=source["navajo-dine-013"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=3, health=3, rules_text="On play: Return an enemy Figure that costs 2 or less to its owner's hand.", abilities=[ability(id="navajo-dine-013-1", label="Coyote Turn", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.RETURN_TO_HAND, extra={"max_cost": 2})])]),
        translated_figure(source=source["navajo-dine-014"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Heal a friendly Figure for 3.", abilities=[ability(id="navajo-dine-014-1", label="Sacred Dance", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.HEAL, amount=3)])]),
        translated_figure(source=source["navajo-dine-015"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=5, health=5, rules_text="On play: Deal 4 damage to an enemy Figure.", abilities=[ability(id="navajo-dine-015-1", label="Horned Assault", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        translated_figure(source=source["navajo-dine-016"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=5, rules_text="Guard.", keywords=["guard"]),
        translated_figure(source=source["navajo-dine-017"], culture_slug=culture_slug, set_code=set_code, cost=5, attack=4, health=5, rules_text="On play: Return a friendly Figure that costs 4 or less from your discard pile to your hand.", abilities=[ability(id="navajo-dine-017-1", label="Owl Recall", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.RETURN_FROM_DISCARD, extra={"max_cost": 4})])]),
        translated_figure(source=source["navajo-dine-018"], culture_slug=culture_slug, set_code=set_code, cost=4, attack=4, health=4, rules_text="On play: Deal 2 damage to an enemy Figure.", abilities=[ability(id="navajo-dine-018-1", label="Bat Shadow", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=2)])]),
        translated_figure(source=source["navajo-dine-019"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=5, rules_text="Guard. On play: Restore 2 Health to your Hero.", keywords=["guard"], abilities=[ability(id="navajo-dine-019-1", label="Salt Shelter", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.NONE, effects=[effect(EffectKind.HEAL, amount=2, scope="friendly_hero")])]),
        translated_figure(source=source["navajo-dine-020"], culture_slug=culture_slug, set_code=set_code, cost=3, attack=2, health=4, rules_text="On play: Give a friendly Figure Ward this turn.", abilities=[ability(id="navajo-dine-020-1", label="Turquoise Blessing", timing=AbilityTiming.SLOW, trigger=AbilityTrigger.ON_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_KEYWORD, keyword="ward", duration="turn")])]),
        token(culture_slug=culture_slug, set_code=set_code, id="navajo-dine-token-holy-weaver", name="Holy Weaver", attack=1, health=2, subtype="spirit", traits=["spirit", "craft", "protection"], rules_text="Guard.", keywords=["guard"]),
        spell(culture_slug=culture_slug, set_code=set_code, id="navajo-dine-spell-blessing-rain", name="Blessing Rain", cost=2, speed=Speed.BURST, rarity="common", traits=["rain", "healing", "ritual"], rules_text="Heal all friendly Figures for 2.", abilities=[ability(id="navajo-dine-spell-blessing-rain-1", label="Blessing Rain", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule="all_friendly_figures", effects=[effect(EffectKind.HEAL, amount=2)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="navajo-dine-spell-spider-counsel", name="Spider Counsel", cost=2, speed=Speed.BURST, rarity="common", traits=["wisdom", "craft", "spirit"], rules_text="Draw a card from your top 3 cards.", abilities=[ability(id="navajo-dine-spell-spider-counsel-1", label="Spider Counsel", timing=AbilityTiming.BURST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.NONE, effects=[effect(EffectKind.DISCOVER_FROM_POOL, amount=1)])]),
        spell(culture_slug=culture_slug, set_code=set_code, id="navajo-dine-spell-monster-banishing", name="Monster Banishing", cost=4, speed=Speed.FAST, rarity="common", traits=["justice", "sun", "war"], rules_text="Deal 4 damage to an enemy Figure.", abilities=[ability(id="navajo-dine-spell-monster-banishing-1", label="Monster Banishing", timing=AbilityTiming.FAST, trigger=AbilityTrigger.MANUAL, target_rule=TargetRule.ENEMY_FIGURE, effects=[effect(EffectKind.DEAL_DAMAGE, amount=4)])]),
        relic(culture_slug=culture_slug, set_code=set_code, id="navajo-dine-relic-sacred-loom", name="Sacred Loom", cost=3, rarity="rare", traits=["craft", "ritual", "spirit"], rules_text="Once each turn, after you play a friendly Figure, give that Figure +1 Health and restore 1 Health to your Hero.", abilities=[ability(id="navajo-dine-relic-sacred-loom-1", label="Woven Shelter", timing=AbilityTiming.PASSIVE, trigger=AbilityTrigger.ON_FRIENDLY_PLAY, target_rule=TargetRule.FRIENDLY_FIGURE, effects=[effect(EffectKind.GRANT_STATS, health=1), effect(EffectKind.HEAL, amount=1, scope="friendly_hero")], limit="once_each_turn")]),
    ]

    pack = pack_payload(set_code=set_code, culture_slug=culture_slug, primary_family="Sanctuary", secondary_family="Oracle", hero_id=hero_id, notes=["Wave-six translation keeps Navajo-Dine readable as healing ritual control with steady draw and monster-answer tools.", "Midgame anchors live in Changing Woman, First Man, First Woman, and the guarded ritual shell."], cards=cards)
    deck = deck_payload(name="Spider Woman Blessed Loom", hero_id=hero_id, notes=["Sanctuary deck with card selection, healing, guards, and clean monster answers."], cards=[
        {"id": "navajo-dine-009", "count": 2},
        {"id": "navajo-dine-011", "count": 2},
        {"id": "navajo-dine-012", "count": 2},
        {"id": "navajo-dine-014", "count": 2},
        {"id": "navajo-dine-019", "count": 2},
        {"id": "navajo-dine-005", "count": 2},
        {"id": "navajo-dine-006", "count": 2},
        {"id": "navajo-dine-008", "count": 2},
        {"id": "navajo-dine-001", "count": 1},
        {"id": "navajo-dine-015", "count": 1},
        {"id": "navajo-dine-spell-blessing-rain", "count": 2},
        {"id": "navajo-dine-spell-spider-counsel", "count": 2},
        {"id": "navajo-dine-spell-monster-banishing", "count": 1},
        {"id": "navajo-dine-relic-sacred-loom", "count": 1},
    ])
    return pack, deck, str(CARDS_DIR / "navajo-dine-v1.json"), str(DECKS_DIR / "navajo-dine-spider-woman-blessed-loom.json")


def write_payload(path: str, payload: dict[str, object]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    builds = [build_apache(), build_navajo_dine()]
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
