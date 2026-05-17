"""
Helpers for translating the current raw figure dataset into the structured card
schema used by the next Mythic Clash rules layer.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
import re
from typing import Any

from .card_schema import (
    AbilitySpec,
    AbilityTiming,
    AbilityTrigger,
    CardSpec,
    CardType,
    EffectKind,
    EffectSpec,
    TargetRule,
)
from .rules import effect_scale, minion_attack, minion_cost, minion_health


KEYWORD_MAP = {
    "taunt": "guard",
    "divine_shield": "ward",
    "rush": "rush",
    "charge": "charge",
    "lifesteal": "lifesteal",
    "poisonous": "poisonous",
    "reborn": "reborn",
}

UNSUPPORTED_CONCEPT_PATTERNS: dict[str, tuple[str, ...]] = {
    "five_stat_system": (
        "power",
        "defense",
        "speed",
        "magic",
        "wisdom",
        "all stats",
        "highest stat",
        "lowest stat",
    ),
    "alignment_subsystem": (
        "light-aligned",
        "dark-aligned",
        "alignment",
    ),
    "hidden_info_subsystem": (
        "hidden enemy",
        "hidden enemies",
        "enemy hand",
        "view enemy strategy",
        "omniscience",
    ),
    "board_geometry_subsystem": (
        "front row",
        "back row",
        "reserve",
        "swap positions",
        "move any ally to any position",
    ),
    "resource_subsystem": (
        "resource token",
        "resource tokens",
        "resource growth",
        "double resource growth",
    ),
    "special_ability_subsystem": (
        "special abilities",
        "special ability",
        "cannot use magic abilities",
        "cannot use summon abilities",
    ),
    "non_launch_status_terms": (
        "accuracy",
        "escape abilities",
        "flee",
        "ecstasy",
        "petrify",
        "confused",
        "paralysis",
    ),
}


@dataclass(slots=True)
class FigureTranslation:
    card: CardSpec
    inferred_effect_kinds: list[str] = field(default_factory=list)
    inferred_target_rule: str = TargetRule.NONE.value
    unsupported_concepts: list[str] = field(default_factory=list)
    ability_blueprint_ready: bool = False


def normalize_trait(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")


def normalize_keywords(keywords: list[str]) -> list[str]:
    return [KEYWORD_MAP[keyword] for keyword in keywords if keyword in KEYWORD_MAP]


def infer_effect_kinds(text: str) -> list[EffectKind]:
    lower = text.lower()
    kinds: list[EffectKind] = []
    checks: list[tuple[tuple[str, ...], EffectKind]] = [
        (("deal", "damage", "strike", "burn"), EffectKind.DEAL_DAMAGE),
        (("heal", "restore"), EffectKind.HEAL),
        (("draw",), EffectKind.DRAW_CARDS),
        (("summon", "create"), EffectKind.SUMMON_TOKEN),
        (("grant", "gain +", "+", "buff"), EffectKind.GRANT_STATS),
        (("freeze", "stun", "sleep"), EffectKind.FREEZE),
        (("destroy",), EffectKind.DESTROY),
        (("return", "bounce"), EffectKind.RETURN_TO_HAND),
        (("resurrect", "revive"), EffectKind.RETURN_FROM_DISCARD),
        (("copy",), EffectKind.COPY_CARD),
        (("shield", "negate", "prevent"), EffectKind.PREVENT_DAMAGE),
        (("steal",), EffectKind.STEAL_MODIFIER),
        (("move", "pull", "push", "swap position"), EffectKind.MOVE_POSITION),
        (("reveal", "look at"), EffectKind.REVEAL_HIDDEN),
        (("banish",), EffectKind.BANISH_UNTIL),
        (("mark",), EffectKind.MARK_TARGET),
        (("swap the highest and lowest stats", "swap one of your card's stats"), EffectKind.SWAP_STATS),
    ]
    for needles, kind in checks:
        if any(needle in lower for needle in needles):
            kinds.append(kind)
    deduped: list[EffectKind] = []
    for kind in kinds:
        if kind not in deduped:
            deduped.append(kind)
    return deduped


def infer_target_rule(text: str) -> TargetRule:
    lower = text.lower()
    if "all enemies" in lower:
        return TargetRule.ALL_ENEMY_FIGURES
    if "all allies" in lower:
        return TargetRule.ALL_FRIENDLY_TEAM_CHARACTERS
    if "one enemy" in lower or "target enemy" in lower:
        return TargetRule.ENEMY_FIGURE
    if "one ally" in lower or "friendly figure" in lower or "one allied" in lower:
        return TargetRule.FRIENDLY_FIGURE
    if "all dark enemies" in lower:
        return TargetRule.ALL_ENEMY_FIGURES
    if "your hero" in lower:
        return TargetRule.FRIENDLY_HERO
    return TargetRule.NONE


def detect_unsupported_concepts(text: str) -> list[str]:
    lower = text.lower()
    found: list[str] = []
    for label, patterns in UNSUPPORTED_CONCEPT_PATTERNS.items():
        if any(pattern in lower for pattern in patterns):
            found.append(label)
    return found


def build_simple_ability_blueprint(card_id: str, label: str, text: str) -> tuple[list[AbilitySpec], bool]:
    effect_kinds = infer_effect_kinds(text)
    unsupported = detect_unsupported_concepts(text)
    if not effect_kinds or unsupported:
        return [], False

    abilities = [
        AbilitySpec(
            id=f"{card_id}-battlecry-1",
            label=label,
            timing=AbilityTiming.SLOW,
            trigger=AbilityTrigger.ON_PLAY,
            target_rule=infer_target_rule(text),
            effects=[EffectSpec(kind=kind) for kind in effect_kinds],
        )
    ]
    return abilities, True


def translate_raw_figure(figure: dict[str, Any], keywords: list[str] | None = None) -> FigureTranslation:
    stats = figure["stats"]
    attack = minion_attack(stats["power"], stats["speed"])
    health = minion_health(stats["defense"], stats["wisdom"])
    total_stats = sum(stats.values())
    rules_text = f"{figure['ability']['name']}: {figure['ability']['description']}"
    normalized_keywords = normalize_keywords(keywords or [])
    abilities, blueprint_ready = build_simple_ability_blueprint(figure["id"], figure["ability"]["name"], figure["ability"]["description"])
    card = CardSpec(
        id=figure["id"],
        name=figure["name"],
        card_type=CardType.FIGURE,
        culture_slug=figure["culture_slug"],
        rarity=figure["rarity"],
        alignment=figure["alignment"],
        traits=[normalize_trait(item) for item in figure["domains"]],
        rules_text=rules_text,
        cost=minion_cost(total_stats, figure["rarity"]),
        subtypes=[normalize_trait(figure["type"])],
        keywords=normalized_keywords,
        legendary=figure["rarity"] == "legendary",
        unique=figure["rarity"] == "legendary",
        attack=attack,
        health=health,
        abilities=abilities,
    )
    card.validate()
    return FigureTranslation(
        card=card,
        inferred_effect_kinds=[kind.value for kind in infer_effect_kinds(figure["ability"]["description"])],
        inferred_target_rule=infer_target_rule(figure["ability"]["description"]).value,
        unsupported_concepts=detect_unsupported_concepts(figure["ability"]["description"]),
        ability_blueprint_ready=blueprint_ready,
    )


def summarize_unsupported_concepts(translations: list[FigureTranslation]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for translation in translations:
        counter.update(translation.unsupported_concepts)
    return counter

