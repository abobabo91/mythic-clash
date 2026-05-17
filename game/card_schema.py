"""
Structured card schema for Mythic Clash's next rules layer.

This module does not replace the current headless engine yet. It gives us a
multiplayer-safe, extensible shape for cards, abilities, and effects so we can
translate the current figure dataset incrementally instead of rewriting the
whole project at once.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from enum import StrEnum
from typing import Any


class CardType(StrEnum):
    HERO = "hero"
    FIGURE = "figure"
    SPELL = "spell"
    RELIC = "relic"
    TOKEN = "token"


class Speed(StrEnum):
    SLOW = "slow"
    FAST = "fast"
    BURST = "burst"


class AbilityTiming(StrEnum):
    PASSIVE = "passive"
    SLOW = "slow"
    FAST = "fast"
    BURST = "burst"
    ACTIVATED = "activated"


class AbilityTrigger(StrEnum):
    ON_PLAY = "on_play"
    ON_SUMMON = "on_summon"
    ON_ATTACK_DECLARED = "on_attack_declared"
    ON_STRIKE = "on_strike"
    ON_DAMAGE_DEALT = "on_damage_dealt"
    ON_DAMAGE_TAKEN = "on_damage_taken"
    ON_DEATH = "on_death"
    ON_TURN_START = "on_turn_start"
    ON_TURN_END = "on_turn_end"
    ON_FRIENDLY_PLAY = "on_friendly_play"
    ON_ENEMY_PLAY = "on_enemy_play"
    ON_RELIC_PLAY = "on_relic_play"
    ON_HEAL = "on_heal"
    ON_DRAW = "on_draw"
    MANUAL = "manual"


class TargetRule(StrEnum):
    NONE = "none"
    SELF = "self"
    FRIENDLY_FIGURE = "friendly_figure"
    FRIENDLY_HERO = "friendly_hero"
    FRIENDLY_CHARACTER = "friendly_character"
    ALLY_FIGURE = "ally_figure"
    ALLY_HERO = "ally_hero"
    ALLY_CHARACTER = "ally_character"
    ENEMY_FIGURE = "enemy_figure"
    ENEMY_HERO = "enemy_hero"
    ENEMY_CHARACTER = "enemy_character"
    ENEMY_TEAM_FIGURE = "enemy_team_figure"
    ENEMY_TEAM_HERO = "enemy_team_hero"
    ENEMY_TEAM_CHARACTER = "enemy_team_character"
    ANY_FIGURE = "any_figure"
    ANY_CHARACTER = "any_character"
    ADJACENT_FRIENDLY_FIGURE = "adjacent_friendly_figure"
    DAMAGED_ENEMY_FIGURE = "damaged_enemy_figure"
    RANDOM_ENEMY_FIGURE = "random_enemy_figure"
    EMPTY_FRIENDLY_SLOT = "empty_friendly_slot"
    FRIENDLY_RELIC = "friendly_relic"
    ENEMY_RELIC = "enemy_relic"
    ALL_ENEMY_FIGURES = "all_enemy_figures"
    ALL_ENEMY_HEROES = "all_enemy_heroes"
    ALL_ENEMY_CHARACTERS = "all_enemy_characters"
    ALL_FRIENDLY_TEAM_FIGURES = "all_friendly_team_figures"
    ALL_FRIENDLY_TEAM_CHARACTERS = "all_friendly_team_characters"


class ConditionKind(StrEnum):
    IF_YOU_CONTROL_TRAIT = "if_you_control_trait"
    IF_TARGET_IS_DAMAGED = "if_target_is_damaged"
    IF_YOU_HAVE_EMPTY_BOARD_SLOT = "if_you_have_empty_board_slot"
    IF_THIS_SURVIVED_DAMAGE = "if_this_survived_damage"
    IF_YOU_CAST_SPELL_THIS_TURN = "if_you_cast_spell_this_turn"
    IF_ENEMY_HAS_GUARD = "if_enemy_has_guard"
    IF_YOU_HAVE_RELIC = "if_you_have_relic"
    IF_CARD_DRAWN_THIS_TURN = "if_card_drawn_this_turn"
    IF_PRIMARY_CULTURE_MATCHES = "if_primary_culture_matches"
    IF_SECONDARY_CULTURE_PRESENT = "if_secondary_culture_present"
    IF_HEALTH_BELOW = "if_health_below"
    IF_TURN_NUMBER_AT_LEAST = "if_turn_number_at_least"


class EffectKind(StrEnum):
    DEAL_DAMAGE = "deal_damage"
    HEAL = "heal"
    DRAW_CARDS = "draw_cards"
    SUMMON_TOKEN = "summon_token"
    GRANT_STATS = "grant_stats"
    SET_STATS = "set_stats"
    GRANT_KEYWORD = "grant_keyword"
    REMOVE_KEYWORD = "remove_keyword"
    SILENCE = "silence"
    DESTROY = "destroy"
    RETURN_TO_HAND = "return_to_hand"
    RETURN_FROM_DISCARD = "return_from_discard"
    READY = "ready"
    EXHAUST = "exhaust"
    FREEZE = "freeze"
    GAIN_ARMOR = "gain_armor"
    GAIN_RITUAL_MANA = "gain_ritual_mana"
    REDUCE_COST = "reduce_cost"
    DISCOVER_FROM_POOL = "discover_from_pool"
    CREATE_IN_HAND = "create_in_hand"
    COPY_CARD = "copy_card"
    REPLACE_RELIC = "replace_relic"
    MOVE_POSITION = "move_position"
    BUFF_ADJACENT = "buff_adjacent"
    TRIGGER_AGAIN = "trigger_again"
    SET_GUARD_IGNORE = "set_guard_ignore"
    SET_CANT_ATTACK = "set_cant_attack"
    SET_CANT_BE_TARGETED = "set_cant_be_targeted"
    PREVENT_DAMAGE = "prevent_damage"
    BANISH_UNTIL = "banish_until"
    MARK_TARGET = "mark_target"
    REVEAL_HIDDEN = "reveal_hidden"
    SWAP_STATS = "swap_stats"
    STEAL_MODIFIER = "steal_modifier"


@dataclass(slots=True)
class ConditionSpec:
    kind: ConditionKind | str
    value: int | str | None = None


@dataclass(slots=True)
class EffectSpec:
    kind: EffectKind | str
    amount: int | None = None
    attack: int | None = None
    health: int | None = None
    keyword: str | None = None
    duration: str | None = None
    scope: str | None = None
    pool: str | None = None
    card_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AbilitySpec:
    id: str
    label: str
    timing: AbilityTiming | str
    trigger: AbilityTrigger | str
    target_rule: TargetRule | str
    resource_cost: int | None = None
    conditions: list[ConditionSpec] = field(default_factory=list)
    effects: list[EffectSpec] = field(default_factory=list)
    limit: str | None = None


@dataclass(slots=True)
class CardSpec:
    id: str
    name: str
    card_type: CardType | str
    culture_slug: str
    rarity: str
    alignment: str
    traits: list[str]
    rules_text: str
    cost: int | None = None
    speed: Speed | str | None = None
    subtypes: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    unique: bool = False
    legendary: bool = False
    token: bool = False
    collectible: bool = True
    set_code: str = ""
    flavor_text: str = ""
    attack: int | None = None
    health: int | None = None
    abilities: list[AbilitySpec] = field(default_factory=list)

    def validate(self) -> None:
        if self.card_type in {CardType.FIGURE, CardType.TOKEN}:
            if self.cost is None or self.attack is None or self.health is None:
                raise ValueError(f"{self.id} is missing figure stats.")
        if self.card_type == CardType.SPELL and self.speed is None:
            raise ValueError(f"{self.id} is missing spell speed.")
        if self.card_type == CardType.HERO and self.cost is not None:
            raise ValueError(f"{self.id} should not have a mana cost as a hero.")


def dataclass_to_dict(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if is_dataclass(value):
        return {field_.name: dataclass_to_dict(getattr(value, field_.name)) for field_ in fields(value)}
    if isinstance(value, list):
        return [dataclass_to_dict(item) for item in value]
    if isinstance(value, dict):
        return {key: dataclass_to_dict(item) for key, item in value.items()}
    return value


def _coerce_enum(enum_cls: type[StrEnum], value: Any) -> Any:
    if isinstance(value, enum_cls):
        return value
    if isinstance(value, str):
        try:
            return enum_cls(value)
        except ValueError:
            return value
    return value


def condition_from_dict(payload: dict[str, Any]) -> ConditionSpec:
    return ConditionSpec(
        kind=_coerce_enum(ConditionKind, payload["kind"]),
        value=payload.get("value"),
    )


def effect_from_dict(payload: dict[str, Any]) -> EffectSpec:
    return EffectSpec(
        kind=_coerce_enum(EffectKind, payload["kind"]),
        amount=payload.get("amount"),
        attack=payload.get("attack"),
        health=payload.get("health"),
        keyword=payload.get("keyword"),
        duration=payload.get("duration"),
        scope=payload.get("scope"),
        pool=payload.get("pool"),
        card_id=payload.get("card_id"),
        extra=payload.get("extra", {}),
    )


def ability_from_dict(payload: dict[str, Any]) -> AbilitySpec:
    return AbilitySpec(
        id=payload["id"],
        label=payload["label"],
        timing=_coerce_enum(AbilityTiming, payload["timing"]),
        trigger=_coerce_enum(AbilityTrigger, payload["trigger"]),
        target_rule=_coerce_enum(TargetRule, payload["target_rule"]),
        resource_cost=payload.get("resource_cost"),
        conditions=[condition_from_dict(item) for item in payload.get("conditions", [])],
        effects=[effect_from_dict(item) for item in payload.get("effects", [])],
        limit=payload.get("limit"),
    )


def card_spec_from_dict(payload: dict[str, Any]) -> CardSpec:
    card = CardSpec(
        id=payload["id"],
        name=payload["name"],
        card_type=_coerce_enum(CardType, payload["card_type"]),
        culture_slug=payload["culture_slug"],
        rarity=payload["rarity"],
        alignment=payload["alignment"],
        traits=payload.get("traits", []),
        rules_text=payload.get("rules_text", ""),
        cost=payload.get("cost"),
        speed=_coerce_enum(Speed, payload["speed"]) if payload.get("speed") is not None else None,
        subtypes=payload.get("subtypes", []),
        keywords=payload.get("keywords", []),
        unique=payload.get("unique", False),
        legendary=payload.get("legendary", False),
        token=payload.get("token", False),
        collectible=payload.get("collectible", True),
        set_code=payload.get("set_code", ""),
        flavor_text=payload.get("flavor_text", ""),
        attack=payload.get("attack"),
        health=payload.get("health"),
        abilities=[ability_from_dict(item) for item in payload.get("abilities", [])],
    )
    card.validate()
    return card
