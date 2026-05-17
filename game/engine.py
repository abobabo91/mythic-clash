"""
Hearthstone-like headless engine for Mythic Clash.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
import json
import random
from pathlib import Path
from typing import Any

from .card_schema import card_spec_from_dict
from .rules import (
    HERO_HEALTH,
    HERO_POWER_COST,
    MAX_BOARD_SIZE,
    MAX_HAND_SIZE,
    MAX_MANA,
    MAX_TURNS,
    RULES_TEXT,
    STARTING_HAND_FIRST,
    STARTING_HAND_SECOND,
    DESPERATE_DRAW_THRESHOLD,
    LAST_STAND_THRESHOLD,
    SURVIVAL_INSTINCT_THRESHOLD,
    effect_scale,
    minion_attack,
    minion_cost,
    minion_health,
    spell_cost,
)


ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = ROOT / "data" / "figures"
CARDS_V1_DIR = ROOT / "data" / "cards-v1"
DECKS_V1_DIR = ROOT / "data" / "decks-v1"
NEUTRAL_CORE_PATH = CARDS_V1_DIR / "neutral-core-v1.json"
DOMAIN_SUPPORT_PATH = CARDS_V1_DIR / "domain-support-v1.json"


@dataclass
class CardTemplate:
    id: str
    name: str
    culture_slug: str
    source: str
    card_type: str
    cost: int
    rarity: str
    alignment: str
    text: str
    attack: int = 0
    health: int = 0
    keywords: list[str] = field(default_factory=list)
    battlecry: str | None = None
    deathrattle: str | None = None
    spell_kind: str | None = None
    speed: str | None = None
    value: int = 0
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class MinionState:
    unit_id: str
    owner: int
    card: CardTemplate
    attack: int
    health: int
    max_health: int
    damage_taken: int = 0
    sleeping: bool = True
    attacks_this_turn: int = 0
    divine_shield: bool = False
    reborn_available: bool = False
    enchant_attack: int = 0
    enchant_health: int = 0
    temp_attack: int = 0
    temp_health: int = 0
    temp_keywords: set[str] = field(default_factory=set)
    summoned_turn: int = 0
    silenced: bool = False
    skip_ready_once: bool = False
    cant_attack_turns: int = 0
    damage_reduction_once: int = 0
    damage_reduction_available: bool = False

    @property
    def current_attack(self) -> int:
        return max(0, self.attack + self.enchant_attack + self.temp_attack)

    @property
    def current_health(self) -> int:
        return self.health + self.enchant_health + self.temp_health - self.damage_taken

    @property
    def runtime_keywords(self) -> set[str]:
        keywords = set()
        if not self.silenced:
            keywords.update(self.card.keywords)
        keywords.update(self.temp_keywords)
        return keywords

    @property
    def taunt(self) -> bool:
        return "taunt" in self.runtime_keywords or "guard" in self.runtime_keywords

    @property
    def rush(self) -> bool:
        return "rush" in self.runtime_keywords

    @property
    def charge(self) -> bool:
        return "charge" in self.runtime_keywords

    @property
    def lifesteal(self) -> bool:
        return "lifesteal" in self.runtime_keywords

    @property
    def poisonous(self) -> bool:
        return "poisonous" in self.runtime_keywords

    def can_attack(self) -> bool:
        return self.current_attack > 0 and not self.sleeping and self.attacks_this_turn == 0 and self.cant_attack_turns <= 0

    def summary(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "name": self.card.name,
            "culture": self.card.culture_slug,
            "attack": self.current_attack,
            "health": self.current_health,
            "max_health": self.health + self.enchant_health + self.temp_health,
            "sleeping": self.sleeping,
            "can_attack": self.can_attack(),
            "keywords": sorted(self.runtime_keywords),
            "battlecry": self.card.battlecry,
            "deathrattle": self.card.deathrattle,
            "text": self.card.text,
            "divine_shield": self.divine_shield,
            "reborn_available": self.reborn_available,
        }


@dataclass
class PlayerState:
    name: str
    health: int = HERO_HEALTH
    armor: int = 0
    mana: int = 0
    max_mana: int = 0
    fatigue: int = 1
    deck: list[CardTemplate] = field(default_factory=list)
    hand: list[CardTemplate] = field(default_factory=list)
    board: list[MinionState] = field(default_factory=list)
    relics: list[CardTemplate] = field(default_factory=list)
    discard: list[CardTemplate] = field(default_factory=list)
    hero_power_used: bool = False
    hero_power_kind: str = "ping"
    hero_power_name: str = "Heroic Spark"
    hero_power_data: dict[str, Any] = field(default_factory=dict)
    hero_card: CardTemplate | None = None
    ritual_mana: int = 0
    flags: dict[str, Any] = field(default_factory=dict)

    @property
    def effective_life(self) -> int:
        return self.health + self.armor


@dataclass
class GameState:
    players: list[PlayerState]
    active_player: int = 0
    turn_number: int = 1
    winner: int | None = None
    history: list[str] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
    next_unit_id: int = 1
    card_registry: dict[str, CardTemplate] = field(default_factory=dict)
    phase: str = "main"  # "main", "response_defender", "response_attacker"
    pending_attack: dict[str, Any] | None = None
    priority_player: int | None = None  # who gets to act next (None = active_player)


def derive_keywords(figure: dict[str, Any], attack: int, health: int) -> list[str]:
    ability_text = f"{figure['ability']['name']} {figure['ability']['description']}".lower()
    domains = set(figure["domains"])
    keywords: list[str] = []

    if "shield" in ability_text or "ward" in ability_text or "barrier" in ability_text:
        keywords.append("divine_shield")

    # Taunt: explicit protective domains, or guardian figures with protective context
    if "protection" in domains or "mountain" in domains:
        keywords.append("taunt")
    elif "earth" in domains and health >= 9:
        keywords.append("taunt")
    elif "guardian" in figure["type"] or (
        "guardian" in ability_text
        and any(word in ability_text for word in ("protect", "defend", "block", "shield", "intercept"))
    ):
        keywords.append("taunt")

    if "drain" in ability_text or "heal self" in ability_text or "healing" in domains:
        keywords.append("lifesteal")

    # Poisonous: require venom/poison/toxic signal, not just serpent domain
    if "plague" in domains or "poison" in ability_text or "venom" in ability_text or "toxic" in ability_text:
        keywords.append("poisonous")
    elif "serpent" in domains and any(word in ability_text for word in ("poison", "venom", "toxic", "bite", "sting", "corrode")):
        keywords.append("poisonous")

    # Reborn: require explicit resurrection language, not just death domain + health
    if "rebirth" in ability_text or "revive" in ability_text or "resurrection" in ability_text:
        keywords.append("reborn")
    elif ("death" in domains or "underworld" in domains) and any(
        word in ability_text for word in ("return", "rise", "reborn", "revive", "undying", "resurrect")
    ):
        keywords.append("reborn")

    if "wind" in domains or "speed" in ability_text or (attack >= 8 and "hero" in figure["type"]):
        keywords.append("rush")

    # Charge: require lightning/thunder domain signal, not narrative uses of "charge"
    if "lightning" in ability_text or "thunderbolt" in ability_text:
        keywords.append("charge")
    elif "wind" in domains and attack >= 7:
        keywords.append("charge")

    deduped = []
    for keyword in keywords:
        if keyword not in deduped:
            deduped.append(keyword)
    if "charge" in deduped and "rush" in deduped:
        deduped.remove("rush")
    return deduped


def derive_battlecry(figure: dict[str, Any], keywords: list[str]) -> str | None:
    text = f"{figure['ability']['name']} {figure['ability']['description']}".lower()
    if "draw" in text or "reveal" in text:
        return "draw"
    if "heal" in text or "restore" in text:
        return "heal"
    if "summon" in text or "create" in text:
        return "summon_token"
    if "buff" in text or "+2" in text or "grant" in text or "boost" in text:
        return "buff_friendly"
    if "destroy" in text or "deal" in text or "damage" in text or "drain" in text or "strike" in text:
        return "damage_enemy"
    if "stun" in text or "cannot attack" in text:
        return "freeze_like"
    if "divine_shield" in keywords:
        return "self_shield"
    return None


def derive_deathrattle(figure: dict[str, Any]) -> str | None:
    text = f"{figure['ability']['name']} {figure['ability']['description']} {' '.join(figure['domains'])}".lower()
    domains = set(figure["domains"])
    if "death" in domains or "underworld" in domains:
        if "summon" in text or "spirit" in domains:
            return "summon_token"
        return "damage_enemy"
    return None


def value_from_figure(figure: dict[str, Any]) -> int:
    stats = figure["stats"]
    return effect_scale(stats["power"], stats["magic"], stats["wisdom"])


def figure_to_minion(figure: dict[str, Any]) -> CardTemplate:
    stats = figure["stats"]
    attack = minion_attack(stats["power"], stats["speed"])
    health = minion_health(stats["defense"], stats["wisdom"])
    total = sum(stats.values())
    keywords = derive_keywords(figure, attack, health)
    return CardTemplate(
        id=figure["id"],
        name=figure["name"],
        culture_slug=figure["culture_slug"],
        source="figure",
        card_type="minion",
        cost=minion_cost(total, figure["rarity"]),
        rarity=figure["rarity"],
        alignment=figure["alignment"],
        text=f"{figure['ability']['name']}: {figure['ability']['description']}",
        attack=attack,
        health=health,
        keywords=keywords,
        battlecry=derive_battlecry(figure, keywords),
        deathrattle=derive_deathrattle(figure),
        value=value_from_figure(figure),
        extra={"domains": figure["domains"], "type": figure["type"]},
    )


def generated_spells() -> list[CardTemplate]:
    return [
        CardTemplate("spell-mythic-bolt", "Mythic Bolt", "neutral", "generated", "spell", spell_cost(2), "common", "neutral", "Deal 3 damage.", spell_kind="damage", value=3),
        CardTemplate("spell-ancient-blessing", "Ancient Blessing", "neutral", "generated", "spell", spell_cost(2), "common", "light", "Give a friendly minion +2/+2.", spell_kind="buff", value=2),
        CardTemplate("spell-spirit-mend", "Spirit Mend", "neutral", "generated", "spell", spell_cost(2), "common", "light", "Restore 4 Health.", spell_kind="heal", value=4),
        CardTemplate("spell-chaos-volley", "Chaos Volley", "neutral", "generated", "spell", spell_cost(3), "rare", "chaos", "Deal 1 damage to three random enemies.", spell_kind="random_missiles", value=3),
        CardTemplate("spell-oracle-insight", "Oracle Insight", "neutral", "generated", "spell", spell_cost(3), "uncommon", "neutral", "Draw 2 cards.", spell_kind="draw", value=2),
        CardTemplate("spell-guardian-oath", "Guardian Oath", "neutral", "generated", "spell", spell_cost(4), "rare", "light", "Summon two 2/2 Guardian tokens with Taunt.", spell_kind="summon_pair", value=2),
        CardTemplate("spell-underworld-verdict", "Underworld Verdict", "neutral", "generated", "spell", spell_cost(4), "rare", "dark", "Destroy a damaged enemy minion.", spell_kind="execute_damaged", value=0),
        CardTemplate("spell-sunfire-burst", "Sunfire Burst", "neutral", "generated", "spell", spell_cost(5), "rare", "light", "Deal 2 damage to all enemy minions.", spell_kind="aoe_enemy", value=2),
        CardTemplate("spell-the-coin", "The Coin", "neutral", "generated", "spell", 0, "common", "neutral", "Gain 1 temporary mana this turn.", spell_kind="coin", value=1),
    ]


def guardian_token() -> CardTemplate:
    return CardTemplate(
        id="token-guardian",
        name="Guardian Echo",
        culture_slug="neutral",
        source="generated",
        card_type="minion",
        cost=1,
        rarity="common",
        alignment="neutral",
        text="Taunt",
        attack=2,
        health=2,
        keywords=["taunt"],
    )


def normalize_runtime_keywords(keywords: list[str]) -> list[str]:
    normalized: list[str] = []
    mapping = {"guard": "taunt", "ward": "divine_shield"}
    for keyword in keywords:
        runtime_keyword = mapping.get(keyword, keyword)
        if runtime_keyword not in normalized:
            normalized.append(runtime_keyword)
    return normalized


def card_spec_to_template(payload: dict[str, Any]) -> CardTemplate:
    card = card_spec_from_dict(payload)
    card_type_map = {
        "figure": "minion",
        "token": "minion",
        "spell": "spell",
        "relic": "relic",
        "hero": "hero",
    }
    return CardTemplate(
        id=card.id,
        name=card.name,
        culture_slug=card.culture_slug,
        source="v1",
        card_type=card_type_map.get(str(card.card_type), str(card.card_type)),
        cost=0 if card.cost is None else card.cost,
        rarity=card.rarity,
        alignment=card.alignment,
        text=card.rules_text,
        attack=0 if card.attack is None else card.attack,
        health=0 if card.health is None else card.health,
        keywords=normalize_runtime_keywords(card.keywords),
        speed=str(card.speed) if card.speed is not None else None,
        extra={
            "traits": list(card.traits),
            "subtypes": list(card.subtypes),
            "set_code": card.set_code,
            "legendary": card.legendary,
            "unique": card.unique,
            "collectible": card.collectible,
            "abilities": [dataclass_to_runtime_ability(item) for item in card.abilities],
        },
    )


def dataclass_to_runtime_ability(ability: Any) -> dict[str, Any]:
    return {
        "id": ability.id,
        "label": ability.label,
        "timing": str(ability.timing),
        "trigger": str(ability.trigger),
        "target_rule": str(ability.target_rule),
        "resource_cost": ability.resource_cost,
        "conditions": [{"kind": str(item.kind), "value": item.value} for item in ability.conditions],
        "effects": [
            {
                "kind": str(effect.kind),
                "amount": effect.amount,
                "attack": effect.attack,
                "health": effect.health,
                "keyword": effect.keyword,
                "duration": effect.duration,
                "scope": effect.scope,
                "pool": effect.pool,
                "card_id": effect.card_id,
                "extra": dict(effect.extra),
            }
            for effect in ability.effects
        ],
        "limit": ability.limit,
    }


def load_v1_cards(pack_path: str | Path) -> dict[str, CardTemplate]:
    payload = json.loads(Path(pack_path).read_text(encoding="utf-8"))
    cards: dict[str, CardTemplate] = {}
    for item in payload["cards"]:
        template = card_spec_to_template(item)
        cards[template.id] = template
    return cards


def load_support_packs() -> dict[str, CardTemplate]:
    cards: dict[str, CardTemplate] = {}
    for path in (NEUTRAL_CORE_PATH, DOMAIN_SUPPORT_PATH):
        if path.exists():
            cards.update(load_v1_cards(path))
    return cards


SUPPORT_CARDS: dict[str, CardTemplate] = load_support_packs()

DECK_SIZE = 24
MIN_FIGURES = 14
MAX_SPELLS = 8
MAX_RELICS = 2
MAX_COPIES = 2
MAX_LEGENDARY_COPIES = 1


def validate_deck(
    deck_cards: list[CardTemplate],
    hero: CardTemplate | None = None,
) -> list[str]:
    """Validate a deck against the v1 rules. Returns a list of violations (empty = legal)."""
    errors: list[str] = []
    total = len(deck_cards)
    if total != DECK_SIZE:
        errors.append(f"Deck has {total} cards, expected {DECK_SIZE}.")

    figures = sum(1 for c in deck_cards if c.card_type == "minion")
    spells = sum(1 for c in deck_cards if c.card_type == "spell")
    relics = sum(1 for c in deck_cards if c.card_type == "relic")

    if figures < MIN_FIGURES:
        errors.append(f"Only {figures} Figures, need at least {MIN_FIGURES}.")
    if spells > MAX_SPELLS:
        errors.append(f"{spells} Spells exceeds max {MAX_SPELLS}.")
    if relics > MAX_RELICS:
        errors.append(f"{relics} Relics exceeds max {MAX_RELICS}.")

    name_counts: dict[str, int] = {}
    for card in deck_cards:
        name_counts[card.name] = name_counts.get(card.name, 0) + 1
    for name, count in name_counts.items():
        card = next(c for c in deck_cards if c.name == name)
        is_legendary = card.rarity == "legendary" or card.extra.get("legendary") or card.extra.get("unique")
        limit = MAX_LEGENDARY_COPIES if is_legendary else MAX_COPIES
        if count > limit:
            errors.append(f"{name} appears {count} times (max {limit}).")

    return errors


def build_v1_deck(pack_path: str | Path, deck_path: str | Path, inject_neutral: bool = True) -> tuple[CardTemplate, list[CardTemplate], dict[str, CardTemplate]]:
    cards = load_v1_cards(pack_path)
    deck_payload = json.loads(Path(deck_path).read_text(encoding="utf-8"))
    hero = cards[deck_payload["hero_id"]]
    deck: list[CardTemplate] = []
    for entry in deck_payload["cards"]:
        template = cards[entry["id"]]
        for _ in range(entry["count"]):
            deck.append(deepcopy(template))
    if inject_neutral and SUPPORT_CARDS:
        deck = inject_neutral_core(deck)
    return deepcopy(hero), deck, cards


def inject_neutral_core(deck: list[CardTemplate]) -> list[CardTemplate]:
    """Replace some culture cards with neutral fillers to fill mana curve gaps.

    Rules: up to 6 neutral/core cards, deck stays at 24, at least 14 figures.
    Strategy: fill gaps in early game, defense, and interaction based on what the deck lacks.
    """
    # Analyze what the deck is missing
    has_1drop = any(c.cost <= 1 and c.card_type == "minion" for c in deck)
    two_drop_count = sum(1 for c in deck if c.cost == 2 and c.card_type == "minion")
    has_guard = any("taunt" in c.keywords or "guard" in c.keywords for c in deck if c.card_type == "minion")
    has_heal = any(c.card_type == "spell" and "heal" in (c.text or "").lower() for c in deck)
    has_aoe = any("all_enemy" in str(c.extra.get("abilities", "")) for c in deck)
    has_fast_removal = any(c.card_type == "spell" and c.speed == "fast" for c in deck)

    # Collect available neutral cards by role
    nc = SUPPORT_CARDS
    neutral_1drops = sorted([c for c in nc.values() if c.card_type == "minion" and c.cost == 1 and not c.extra.get("token")], key=lambda c: c.name)
    neutral_guard = next((c for c in nc.values() if c.id == "nc-border-sentinel"), None)  # 1/4 Guard
    neutral_bolt = next((c for c in nc.values() if c.id == "nc-mythic-bolt"), None)  # Fast removal
    neutral_heal = next((c for c in nc.values() if c.id == "nc-spirit-mend"), None)  # Heal 4
    neutral_aoe = next((c for c in nc.values() if c.id == "nc-flame-wave"), None)  # Deal 1 to all
    neutral_guard_oath = next((c for c in nc.values() if c.id == "nc-guardian-oath"), None)  # Summon 2 taunts

    inject: list[CardTemplate] = []

    # Priority 1: Early game — add 1-drops if missing
    if not has_1drop:
        for c in neutral_1drops[:2]:
            inject.append(deepcopy(c))

    # Priority 2: Defense — EVERY deck needs Guard figures for comeback potential
    guard_count = sum(1 for c in deck if c.card_type == "minion" and ("taunt" in c.keywords or "guard" in c.keywords))
    if guard_count < 2 and neutral_guard:
        inject.append(deepcopy(neutral_guard))
    if guard_count < 1 and neutral_guard:
        # Add a second copy for decks with zero guards
        inject.append(deepcopy(neutral_guard))

    # Priority 3: Emergency wall — Guardian Oath summons 2 Guard tokens instantly
    if guard_count < 3 and neutral_guard_oath:
        inject.append(deepcopy(neutral_guard_oath))

    # Priority 4: Stabilization — add heal if the deck has none
    if not has_heal and neutral_heal:
        inject.append(deepcopy(neutral_heal))

    # Priority 4: Anti-wide — add AoE if the deck has none
    if not has_aoe and neutral_aoe:
        inject.append(deepcopy(neutral_aoe))

    # Priority 5: Interaction — add removal if no Fast spells
    if not has_fast_removal and neutral_bolt:
        inject.append(deepcopy(neutral_bolt))

    # Cap at 5 neutral injections (rules allow 6, but keep culture identity)
    inject = inject[:5]

    if not inject:
        return deck

    # Remove the weakest duplicated culture cards to make room
    # Prefer removing 2nd copies of expensive cards
    name_counts: dict[str, int] = {}
    for c in deck:
        name_counts[c.name] = name_counts.get(c.name, 0) + 1

    removable: list[int] = []
    for i, c in enumerate(deck):
        if name_counts.get(c.name, 0) >= 2 and c.card_type == "minion":
            removable.append(i)

    # Sort removable by cost descending (remove expensive duplicates first)
    removable.sort(key=lambda i: deck[i].cost, reverse=True)

    # Also consider removing duplicate spells
    if len(removable) < len(inject):
        for i, c in enumerate(deck):
            if i not in removable and name_counts.get(c.name, 0) >= 2 and c.card_type == "spell":
                removable.append(i)

    # Remove cards and add neutrals
    to_remove = removable[:len(inject)]
    if len(to_remove) < len(inject):
        # Not enough removable duplicates — just inject what we can
        inject = inject[:len(to_remove)]

    # Remove in reverse index order to avoid shifting
    for i in sorted(to_remove, reverse=True):
        deck.pop(i)
        # Decrement name count
        removed_name = None
        for c in deck:
            if c.name not in name_counts:
                continue
        # Name counts are stale but we only used them for selection

    deck.extend(inject)
    return deck


def choose_hero_power(deck: list[CardTemplate]) -> tuple[str, str]:
    domains = Counter()
    for card in deck:
        for domain in card.extra.get("domains", []):
            domains[domain] += 1
    top = {name for name, _count in domains.most_common(4)}
    if {"war", "fire", "storm"} & top:
        return "ping", "War Spark"
    if {"light", "wisdom", "healing"} & top:
        return "bless", "Sacred Blessing"
    if {"water", "fertility", "earth"} & top:
        return "heal", "Living Water"
    return "armor", "Stone Resolve"


def auto_hero_from_deck(deck: list[CardTemplate]) -> CardTemplate:
    """Create a synthetic hero card from the deck's legendary figure or theme."""
    legends = [c for c in deck if c.rarity == "legendary" and c.card_type == "minion"]
    base = legends[0] if legends else deck[0]
    culture = base.culture_slug
    kind, power_name = choose_hero_power(deck)
    return CardTemplate(
        id=f"{culture}-auto-hero",
        name=base.name,
        culture_slug=culture,
        source="auto",
        card_type="hero",
        cost=0,
        rarity="legendary",
        alignment=base.alignment,
        text=f"Hero Power - {power_name} (2)",
        extra={"domains": base.extra.get("domains", [])},
    )


def load_cards() -> dict[str, CardTemplate]:
    cards: dict[str, CardTemplate] = {}
    for fp in sorted(FIGURES_DIR.glob("*.json")):
        payload = json.loads(fp.read_text(encoding="utf-8"))
        for figure in payload["figures"]:
            card = figure_to_minion(figure)
            cards[card.id] = card
    for spell in generated_spells():
        cards[spell.id] = spell
    return cards


ALL_CARDS = load_cards()


def build_deck_from_cultures(culture_slugs: list[str], size: int = 18) -> list[CardTemplate]:
    pool = [card for card in ALL_CARDS.values() if card.card_type == "minion" and card.culture_slug in culture_slugs]
    if not pool:
        raise ValueError(f"No minion cards found for cultures: {culture_slugs}")

    low = sorted([card for card in pool if card.cost <= 2], key=lambda c: (-c.attack - c.health, c.name))
    mid = sorted([card for card in pool if 3 <= card.cost <= 4], key=lambda c: (-c.attack - c.health, c.name))
    high = sorted([card for card in pool if card.cost >= 5], key=lambda c: (-c.attack - c.health, c.name))
    legends = sorted([card for card in pool if card.rarity == "legendary"], key=lambda c: (-c.attack - c.health, c.name))

    chosen: list[CardTemplate] = []
    seen: set[str] = set()
    for bucket, target in ((legends, 2), (high, 3), (mid, 6), (low, 3)):
        added = 0
        for card in bucket:
            if card.id in seen:
                continue
            chosen.append(card)
            seen.add(card.id)
            added += 1
            if added >= target:
                break

    rest = sorted(pool, key=lambda c: (c.cost, -(c.attack + c.health), c.name))
    for card in rest:
        if card.id in seen:
            continue
        chosen.append(card)
        seen.add(card.id)
        if len(chosen) >= 14:
            break

    dominant = Counter()
    for card in chosen:
        for domain in card.extra.get("domains", []):
            dominant[domain] += 1
    top = {name for name, _count in dominant.most_common(4)}
    spell_ids = ["spell-mythic-bolt", "spell-ancient-blessing", "spell-spirit-mend", "spell-oracle-insight"]
    if {"war", "fire", "storm"} & top:
        spell_ids = ["spell-mythic-bolt", "spell-chaos-volley", "spell-ancient-blessing", "spell-sunfire-burst"]
    elif {"death", "underworld", "darkness"} & top:
        spell_ids = ["spell-mythic-bolt", "spell-underworld-verdict", "spell-chaos-volley", "spell-oracle-insight"]
    elif {"water", "fertility", "earth"} & top:
        spell_ids = ["spell-spirit-mend", "spell-ancient-blessing", "spell-guardian-oath", "spell-oracle-insight"]
    elif {"light", "wisdom", "creation"} & top:
        spell_ids = ["spell-spirit-mend", "spell-ancient-blessing", "spell-oracle-insight", "spell-sunfire-burst"]

    chosen.extend(ALL_CARDS[spell_id] for spell_id in spell_ids)
    return chosen[:size]


def shuffle_deck(deck: list[CardTemplate], seed: int | None = None) -> list[CardTemplate]:
    cards = deck[:]
    rng = random.Random(seed)
    rng.shuffle(cards)
    return cards


def mulligan_priority(card: CardTemplate) -> tuple[int, int]:
    if card.card_type == "minion":
        if card.cost <= 2:
            return (0, -card.cost)
        if card.cost == 3:
            return (1, -card.attack - card.health)
        if card.cost == 4:
            return (2, -card.attack - card.health)
        return (4, -card.attack - card.health)
    if card.card_type == "spell":
        if card.cost <= 2:
            return (2, -card.cost)
        if card.cost == 3:
            return (3, -card.cost)
        return (5, -card.cost)
    if card.card_type == "relic":
        return (3, -card.cost)
    return (6, 0)


def should_mulligan_card(card: CardTemplate, kept_cards: list[CardTemplate], player_index: int) -> bool:
    low_curve_kept = sum(1 for kept in kept_cards if kept.card_type == "minion" and kept.cost <= 2)
    if card.card_type == "minion":
        if card.cost >= 5:
            return True
        if card.cost == 4 and low_curve_kept == 0:
            return True
        return False
    if card.card_type == "spell":
        if card.cost >= 4:
            return True
        if card.cost >= 3 and low_curve_kept == 0:
            return True
        return False
    if card.card_type == "relic":
        return card.cost >= 4 or (card.cost >= 3 and low_curve_kept == 0)
    return False


def perform_mulligan(state: GameState, player_index: int) -> None:
    player = state.players[player_index]
    if not player.hand:
        return
    ordered = sorted(player.hand, key=mulligan_priority)
    kept_cards: list[CardTemplate] = []
    to_replace: list[CardTemplate] = []
    for card in ordered:
        if should_mulligan_card(card, kept_cards, player_index):
            to_replace.append(card)
        else:
            kept_cards.append(card)

    if not to_replace:
        state.history.append(f"{player.name} keeps the opening hand.")
        return

    player.hand = [card for card in player.hand if card not in to_replace]
    player.deck.extend(to_replace)
    state.rng.shuffle(player.deck)
    replacements = min(len(to_replace), len(player.deck))
    for _ in range(replacements):
        player.hand.append(player.deck.pop(0))
    state.history.append(f"{player.name} mulligans {len(to_replace)} card(s).")


def build_hero_runtime(hero_card: CardTemplate | None, fallback_deck: list[CardTemplate]) -> tuple[str, str, dict[str, Any]]:
    if hero_card is None:
        kind, name = choose_hero_power(fallback_deck)
        return kind, name, {}
    abilities = hero_card.extra.get("abilities", [])
    power = abilities[0] if abilities else {}
    return "structured", hero_card.name, power


def create_game(
    deck_a: list[CardTemplate],
    deck_b: list[CardTemplate],
    player_a: str = "Player A",
    player_b: str = "Player B",
    seed: int | None = None,
    hero_a: CardTemplate | None = None,
    hero_b: CardTemplate | None = None,
    card_registry: dict[str, CardTemplate] | None = None,
) -> GameState:
    if hero_a is None:
        hero_a = auto_hero_from_deck(deck_a)
    if hero_b is None:
        hero_b = auto_hero_from_deck(deck_b)
    power_a = build_hero_runtime(hero_a, deck_a)
    power_b = build_hero_runtime(hero_b, deck_b)
    players = [
        PlayerState(
            name=player_a,
            deck=shuffle_deck(deck_a, seed),
            hero_power_kind=power_a[0],
            hero_power_name=power_a[1],
            hero_power_data=power_a[2],
            hero_card=deepcopy(hero_a) if hero_a is not None else None,
        ),
        PlayerState(
            name=player_b,
            deck=shuffle_deck(deck_b, None if seed is None else seed + 1),
            hero_power_kind=power_b[0],
            hero_power_name=power_b[1],
            hero_power_data=power_b[2],
            hero_card=deepcopy(hero_b) if hero_b is not None else None,
        ),
    ]
    registry = {} if card_registry is None else {key: deepcopy(value) for key, value in card_registry.items()}
    state = GameState(players=players, rng=random.Random(seed), card_registry=registry)
    for _ in range(STARTING_HAND_FIRST):
        draw_card(state, 0)
    for _ in range(STARTING_HAND_SECOND):
        draw_card(state, 1)
    perform_mulligan(state, 0)
    perform_mulligan(state, 1)
    players[1].hand.append(ALL_CARDS["spell-the-coin"])
    # Second-player compensation: start with 1 Ritual Mana (per design docs)
    players[1].ritual_mana = 1
    start_turn(state, 0)
    return state


def create_v1_game(
    pack_a_path: str | Path,
    deck_a_path: str | Path,
    pack_b_path: str | Path,
    deck_b_path: str | Path,
    player_a: str = "Player A",
    player_b: str = "Player B",
    seed: int | None = None,
) -> GameState:
    hero_a, deck_a, cards_a = build_v1_deck(pack_a_path, deck_a_path)
    hero_b, deck_b, cards_b = build_v1_deck(pack_b_path, deck_b_path)
    registry = {**SUPPORT_CARDS, **cards_a, **cards_b, **ALL_CARDS}
    return create_game(
        deck_a,
        deck_b,
        player_a=player_a,
        player_b=player_b,
        seed=seed,
        hero_a=hero_a,
        hero_b=hero_b,
        card_registry=registry,
    )


def draw_card(state: GameState, player_index: int) -> None:
    player = state.players[player_index]
    if player.deck:
        drawn = player.deck.pop(0)
        if len(player.hand) >= MAX_HAND_SIZE:
            player.discard.append(drawn)
            state.history.append(f"{player.name} burns {drawn.name} because the hand is full.")
        else:
            player.hand.append(drawn)
    else:
        player.health -= player.fatigue
        state.history.append(f"{player.name} takes {player.fatigue} fatigue damage.")
        player.fatigue += 1
        if player.health <= 0:
            state.winner = 1 - player_index


def start_turn(state: GameState, player_index: int) -> None:
    player = state.players[player_index]
    state.active_player = player_index
    player.max_mana = min(MAX_MANA, player.max_mana + 1)
    player.mana = player.max_mana
    player.hero_power_used = False
    player.flags = {"friendly_died_this_turn": False}
    draw_card(state, player_index)
    if state.winner is not None:
        return
    # Survival Instinct (<=15 HP): extra draw; <=5 HP draws 2 extra
    if player.health <= SURVIVAL_INSTINCT_THRESHOLD and player.health > 0:
        if player.health <= DESPERATE_DRAW_THRESHOLD:
            state.history.append(f"{player.name} triggers Desperate Survival! (draw 2 extra at {player.health} HP)")
            draw_card(state, player_index)
            if state.winner is not None:
                return
            draw_card(state, player_index)
            if state.winner is not None:
                return
        else:
            state.history.append(f"{player.name} triggers Survival Instinct! (extra draw at {player.health} HP)")
            draw_card(state, player_index)
            if state.winner is not None:
                return
    # Last Stand (<=10 HP): figures enter play ready (no sleeping)
    if player.health <= LAST_STAND_THRESHOLD and player.health > 0:
        state.history.append(f"{player.name} enters Last Stand! (figures enter ready at {player.health} HP)")
        player.flags["survival_no_sleeping"] = True
    for minion in player.board:
        if minion.skip_ready_once:
            minion.sleeping = True
            minion.skip_ready_once = False
        else:
            minion.sleeping = False
        minion.attacks_this_turn = 0
        minion.damage_reduction_available = minion.damage_reduction_once > 0
    state.history.append(
        f"Turn {state.turn_number}: {player.name} starts with {player.health} health, {player.armor} armor, {player.mana} mana, and {player.ritual_mana} Ritual Mana."
    )
    for relic in list(player.relics):
        trigger_structured_abilities(state, player_index, None, relic, "on_turn_start")


def end_turn(state: GameState) -> None:
    for relic in list(state.players[state.active_player].relics):
        trigger_structured_abilities(state, state.active_player, None, relic, "on_turn_end")
    expire_end_of_turn_effects(state, state.active_player)
    next_player = 1 - state.active_player
    if next_player == 0:
        state.turn_number += 1
    if state.turn_number > MAX_TURNS:
        apply_overtime_fatigue(state)
        if state.winner is not None:
            return
    start_turn(state, next_player)


def expire_end_of_turn_effects(state: GameState, player_index: int) -> None:
    player = state.players[player_index]
    unused = player.mana
    player.ritual_mana = min(2, player.ritual_mana + unused)
    player.mana = 0
    for minion in list(player.board):
        minion.temp_attack = 0
        minion.temp_health = 0
        minion.temp_keywords.clear()
        if minion.cant_attack_turns > 0:
            minion.cant_attack_turns -= 1
        if minion.current_health <= 0:
            remove_minion(state, minion)


def resolve_timeout_winner(state: GameState) -> None:
    a, b = state.players
    if a.effective_life > b.effective_life:
        state.winner = 0
    elif b.effective_life > a.effective_life:
        state.winner = 1
    else:
        a_board = sum(max(0, minion.current_attack + minion.current_health) for minion in a.board)
        b_board = sum(max(0, minion.current_attack + minion.current_health) for minion in b.board)
        state.winner = 0 if a_board >= b_board else 1
    state.history.append("The game ends on the turn limit.")


def apply_overtime_fatigue(state: GameState) -> None:
    """Both players take escalating fatigue each turn past MAX_TURNS."""
    overtime = state.turn_number - MAX_TURNS
    damage = overtime * 2
    for player_index in range(2):
        player = state.players[player_index]
        player.health -= damage
        state.history.append(f"{player.name} takes {damage} overtime fatigue (turn {state.turn_number}).")
        if player.health <= 0:
            state.winner = 1 - player_index
    if state.players[0].health <= 0 and state.players[1].health <= 0:
        state.winner = state.active_player


def summon_minion(state: GameState, player_index: int, card: CardTemplate, position: int | None = None, sleeping: bool = True) -> MinionState | None:
    player = state.players[player_index]
    if len(player.board) >= MAX_BOARD_SIZE:
        return None
    minion = MinionState(
        unit_id=f"M{state.next_unit_id}",
        owner=player_index,
        card=card,
        attack=card.attack,
        health=card.health,
        max_health=card.health,
        sleeping=sleeping,
        divine_shield="divine_shield" in card.keywords,
        reborn_available="reborn" in card.keywords,
        summoned_turn=state.turn_number,
    )
    for ability in structured_abilities(card, "on_damage_taken"):
        for effect in ability.get("effects", []):
            if effect.get("kind") == "prevent_damage":
                minion.damage_reduction_once = int(effect.get("amount") or 0)
                minion.damage_reduction_available = True
    state.next_unit_id += 1
    position = len(player.board) if position is None else max(0, min(position, len(player.board)))
    player.board.insert(position, minion)
    trigger_structured_abilities(state, player_index, minion, card, "on_summon", context={"summoned": True})
    return minion


def find_minion(state: GameState, unit_id: str) -> MinionState | None:
    for player in state.players:
        for minion in player.board:
            if minion.unit_id == unit_id:
                return minion
    return None


def remove_minion(state: GameState, minion: MinionState) -> None:
    player = state.players[minion.owner]
    if minion in player.board:
        player.board.remove(minion)
        player.discard.append(minion.card)
        player.flags["friendly_died_this_turn"] = True
        state.history.append(f"{minion.card.name} dies.")
        trigger_structured_abilities(state, minion.owner, minion, minion.card, "on_death")
        for relic in list(player.relics):
            trigger_structured_abilities(state, minion.owner, None, relic, "on_death")
        if minion.card.deathrattle:
            resolve_minion_effect(state, minion.owner, minion, minion.card.deathrattle, minion.card.value, trigger="deathrattle")
        if minion.reborn_available:
            minion.reborn_available = False
            reborn_card = deepcopy(minion.card)
            revived = summon_minion(state, minion.owner, reborn_card, position=len(player.board), sleeping=True)
            if revived:
                revived.damage_taken = revived.max_health - 1
                revived.reborn_available = False
                state.history.append(f"{revived.card.name} returns with Reborn.")


def deal_damage_to_hero(state: GameState, player_index: int, amount: int, source_name: str = "") -> int:
    player = state.players[player_index]
    absorbed = min(player.armor, amount)
    player.armor -= absorbed
    amount -= absorbed
    player.health -= amount
    if source_name:
        state.history.append(f"{source_name} deals {absorbed + amount} to {player.name}.")
    return absorbed + amount


def deal_damage_to_minion(state: GameState, minion: MinionState, amount: int, poisonous: bool = False) -> int:
    if amount <= 0:
        return 0
    if minion.divine_shield:
        minion.divine_shield = False
        return 0
    if minion.damage_reduction_available and minion.damage_reduction_once > 0:
        amount = max(0, amount - minion.damage_reduction_once)
        minion.damage_reduction_available = False
        if amount <= 0:
            return 0
    minion.damage_taken += amount
    if poisonous and amount > 0:
        minion.damage_taken = minion.max_health + minion.enchant_health + minion.temp_health
    return amount


def heal_hero(player: PlayerState, amount: int) -> int:
    before = player.health
    player.health = min(HERO_HEALTH, player.health + amount)
    return player.health - before


def heal_minion(minion: MinionState, amount: int) -> int:
    before = minion.damage_taken
    minion.damage_taken = max(0, minion.damage_taken - amount)
    return before - minion.damage_taken


def structured_abilities(card: CardTemplate, trigger: str) -> list[dict[str, Any]]:
    return [ability for ability in card.extra.get("abilities", []) if ability.get("trigger") == trigger]


def has_open_board_slot(state: GameState, player_index: int) -> bool:
    return len(state.players[player_index].board) < MAX_BOARD_SIZE


def all_minions(state: GameState, player_index: int) -> list[MinionState]:
    return list(state.players[player_index].board)


def card_matches_conditions(card: CardTemplate, max_cost: int | None = None, allow_legendary: bool = True) -> bool:
    if max_cost is not None and card.cost > max_cost:
        return False
    if not allow_legendary and (card.rarity == "legendary" or card.extra.get("legendary")):
        return False
    return True


def resolve_runtime_target(state: GameState, owner: int, target_ref: str | None) -> tuple[str, Any] | None:
    if target_ref is None:
        return None
    if target_ref == "friendly_hero":
        return ("hero", owner)
    if target_ref == "enemy_hero":
        return ("hero", 1 - owner)
    if target_ref == "hero":
        return ("hero", 1 - owner)
    minion = find_minion(state, target_ref)
    if minion:
        return ("minion", minion)
    return None


def is_friendly_target(state: GameState, owner: int, target_ref: str | None) -> bool:
    target = resolve_runtime_target(state, owner, target_ref)
    if target is None:
        return False
    if target[0] == "hero":
        return target[1] == owner
    return target[1].owner == owner


def _check_ability_limit_available(state: GameState, owner: int, ability: dict[str, Any]) -> bool:
    """Read-only check: can this ability still be used this turn?"""
    if ability.get("limit") != "once_each_turn":
        return True
    key = f"{owner}:{ability['id']}:{state.turn_number}:{state.active_player}"
    used = state.players[owner].flags.get("ability_limits", set())
    return key not in used


def ability_ready_for_limit(state: GameState, owner: int, ability: dict[str, Any]) -> bool:
    """Check AND mark: can this ability be used? If yes, marks it as used."""
    if ability.get("limit") != "once_each_turn":
        return True
    key = f"{owner}:{ability['id']}:{state.turn_number}:{state.active_player}"
    used = state.players[owner].flags.setdefault("ability_limits", set())
    if key in used:
        return False
    used.add(key)
    return True


def condition_matches(
    state: GameState,
    owner: int,
    source: MinionState | None,
    target_ref: str | None,
    condition: dict[str, Any],
    context: dict[str, Any],
) -> bool:
    kind = condition.get("kind")
    value = condition.get("value")
    target = resolve_runtime_target(state, owner, target_ref)
    if kind == "if_friendly_died_this_turn":
        return bool(state.players[owner].flags.get("friendly_died_this_turn"))
    if kind == "if_target_is_damaged":
        return target is not None and target[0] == "minion" and target[1].damage_taken > 0
    if kind == "if_target_attack_at_most":
        return target is not None and target[0] == "minion" and target[1].current_attack <= int(value or 0)
    if kind == "if_struck_figure":
        return context.get("struck_figure", False)
    return True


def ability_conditions_match(
    state: GameState,
    owner: int,
    source: MinionState | None,
    target_ref: str | None,
    ability: dict[str, Any],
    context: dict[str, Any],
) -> bool:
    return all(condition_matches(state, owner, source, target_ref, condition, context) for condition in ability.get("conditions", []))


def consume_ritual_mana(player: PlayerState, amount: int) -> int:
    spent = min(player.ritual_mana, amount)
    player.ritual_mana -= spent
    return amount - spent


def summon_runtime_token(state: GameState, owner: int, card_id: str, sleeping: bool = True) -> MinionState | None:
    template = state.card_registry.get(card_id)
    if template is None:
        return None
    return summon_minion(state, owner, deepcopy(template), sleeping=sleeping)


def pick_discard_card(player: PlayerState, max_cost: int | None = None, allow_legendary: bool = True) -> CardTemplate | None:
    candidates = [card for card in player.discard if card.card_type == "minion" and card_matches_conditions(card, max_cost, allow_legendary)]
    if not candidates:
        return None
    candidates.sort(key=lambda card: (card.cost, card.attack + card.health, card.name), reverse=True)
    return candidates[0]


def grant_keyword_to_minion(minion: MinionState, keyword: str, duration: str | None = None) -> None:
    runtime_keyword = normalize_runtime_keywords([keyword])[0]
    if duration in {"turn", "combat"}:
        minion.temp_keywords.add(runtime_keyword)
        if runtime_keyword == "divine_shield":
            minion.divine_shield = True
    else:
        if runtime_keyword not in minion.card.keywords:
            minion.card.keywords.append(runtime_keyword)
        if runtime_keyword == "divine_shield":
            minion.divine_shield = True


def apply_structured_effect(
    state: GameState,
    owner: int,
    source: MinionState | None,
    ability: dict[str, Any],
    effect: dict[str, Any],
    target_ref: str | None,
    context: dict[str, Any],
) -> None:
    player = state.players[owner]
    enemy = state.players[1 - owner]
    target = resolve_runtime_target(state, owner, target_ref)
    kind = effect["kind"]
    extra = effect.get("extra", {})
    amount = int(effect.get("amount") or 0)

    if extra.get("if_target_survived_damage") and not context.get("last_target_survived"):
        return
    if extra.get("if_empty_slot") and not has_open_board_slot(state, owner):
        return
    if extra.get("if_target_has_keyword"):
        if target is None or target[0] != "minion" or extra["if_target_has_keyword"] not in target[1].runtime_keywords:
            return
    if extra.get("if_you_control_keyword"):
        if not any(extra["if_you_control_keyword"] in minion.runtime_keywords for minion in player.board):
            if extra.get("or_if_you_control_rarity") != "legendary" or not any(minion.card.rarity == "legendary" for minion in player.board):
                return
    if extra.get("if_target_is_damaged") and not (target is not None and target[0] == "minion" and target[1].damage_taken > 0):
        return

    if kind == "deal_damage":
        targets: list[tuple[str, Any]] = []
        target_rule = ability.get("target_rule")
        if target_rule == "all_enemy_figures":
            targets = [("minion", minion) for minion in list(enemy.board)]
        elif target_rule == "all_friendly_figures":
            targets = [("minion", minion) for minion in list(player.board)]
        elif target_rule == "all_other_figures":
            targets = [("minion", minion) for index in range(2) for minion in list(state.players[index].board) if minion is not source]
        elif target_rule == "all_other_characters":
            targets = [("hero", 0), ("hero", 1)] + [("minion", minion) for index in range(2) for minion in list(state.players[index].board) if minion is not source]
        elif effect.get("scope") == "friendly_hero":
            targets = [("hero", owner)]
        elif target is not None:
            targets = [target]
        for target_kind, target_value in targets:
            if target_kind == "hero":
                dealt = deal_damage_to_hero(state, target_value, amount, source.card.name if source else ability["label"])
                context["last_damage_dealt"] = dealt
            else:
                dealt = deal_damage_to_minion(state, target_value, amount, poisonous="poisonous" in (source.runtime_keywords if source else []))
                context["last_damage_dealt"] = dealt
                context["last_target_survived"] = target_value.current_health > 0
                if target_value.current_health <= 0:
                    remove_minion(state, target_value)
        return

    if kind == "heal":
        if ability.get("target_rule") == "all_friendly_figures":
            for minion in list(player.board):
                heal_minion(minion, amount)
            return
        if target is None and effect.get("scope") == "friendly_character":
            if player.board:
                heal_minion(player.board[0], amount)
            else:
                heal_hero(player, amount)
            return
        if target is None and effect.get("scope") == "friendly_hero":
            heal_hero(player, amount)
            return
        if target is not None and target[0] == "hero":
            heal_hero(state.players[target[1]], amount)
        elif target is not None and target[0] == "minion":
            heal_minion(target[1], amount)
        return

    if kind == "draw_cards":
        for _ in range(max(1, amount)):
            draw_card(state, owner)
        return

    if kind == "summon_token":
        summoned = summon_runtime_token(state, owner, effect["card_id"], sleeping=True)
        if summoned:
            state.history.append(f"{(source.card.name if source else ability['label'])} summons {summoned.card.name}.")
        return

    if kind == "grant_stats":
        scope = effect.get("scope")
        attack = int(effect.get("attack") or 0)
        health = int(effect.get("health") or 0)
        duration = effect.get("duration")

        # Handle scope-based targeting
        if scope == "random_friendly_figure":
            friendly = list(state.players[owner].board)
            if friendly:
                chosen = state.rng.choice(friendly)
                chosen.enchant_attack += attack
                chosen.enchant_health += health
                state.history.append(f"{ability['label']} gives +{attack}/+{health} to {chosen.card.name}.")
            return
        if scope == "all_friendly_figures":
            for m in list(state.players[owner].board):
                if duration in {"turn", "combat"}:
                    m.temp_attack += attack
                    m.temp_health += health
                else:
                    m.enchant_attack += attack
                    m.enchant_health += health
            return

        if target is None or target[0] != "minion":
            return
        if duration in {"turn", "combat"}:
            target[1].temp_attack += attack
            target[1].temp_health += health
        else:
            target[1].enchant_attack += attack
            target[1].enchant_health += health
        return

    if kind == "grant_keyword":
        if target is None or target[0] != "minion" or extra.get("if_target_has_no_keywords") and target[1].runtime_keywords:
            return
        grant_keyword_to_minion(target[1], effect["keyword"], effect.get("duration"))
        return

    if kind == "ready":
        if target is not None and target[0] == "minion":
            target[1].sleeping = False
            target[1].attacks_this_turn = 0
        return

    if kind == "exhaust":
        if target is not None and target[0] == "minion":
            target[1].sleeping = True
        return

    if kind == "freeze":
        if target is not None and target[0] == "minion":
            target[1].sleeping = True
            target[1].skip_ready_once = True
        return

    if kind == "return_to_hand":
        if target is not None and target[0] == "minion":
            max_cost = extra.get("max_cost")
            if max_cost is None or target[1].card.cost <= max_cost:
                owner_index = target[1].owner
                returned_card = target[1].card
                state.players[owner_index].board.remove(target[1])
                if len(state.players[owner_index].hand) < MAX_HAND_SIZE:
                    state.players[owner_index].hand.append(returned_card)
                else:
                    state.players[owner_index].discard.append(returned_card)
        return

    if kind == "return_from_discard":
        choice = pick_discard_card(player, max_cost=extra.get("max_cost"), allow_legendary=extra.get("legendary_allowed", True))
        if choice is None:
            return
        player.discard.remove(choice)
        if extra.get("to_battlefield"):
            summoned = summon_minion(state, owner, deepcopy(choice), sleeping=bool(extra.get("exhausted", True)))
            if summoned and extra.get("exhausted"):
                summoned.sleeping = True
        else:
            if len(player.hand) < MAX_HAND_SIZE:
                player.hand.append(deepcopy(choice))
            else:
                player.discard.append(choice)
        return

    if kind == "gain_ritual_mana":
        player.ritual_mana = min(2, player.ritual_mana + max(1, amount))
        return

    if kind == "discover_from_pool":
        top = player.deck[:3]
        if not top:
            return
        chosen = top[0]
        player.deck = player.deck[3:] + top[1:]
        if len(player.hand) < MAX_HAND_SIZE:
            player.hand.append(chosen)
        else:
            player.discard.append(chosen)
        return

    if kind == "destroy":
        if target is not None and target[0] == "minion":
            remove_minion(state, target[1])
        return

    if kind == "silence":
        if target is not None and target[0] == "minion":
            target[1].silenced = True
            target[1].divine_shield = False
            target[1].reborn_available = False
            target[1].temp_keywords.clear()
        return

    if kind == "set_cant_attack":
        if target is not None and target[0] == "minion":
            target[1].cant_attack_turns = max(target[1].cant_attack_turns, 1)
        return

    if kind == "replace_relic":
        if enemy.relics:
            destroy_relic(state, 1 - owner, enemy.relics[0])
        return

    if kind == "gain_armor":
        player.armor += max(1, amount)
        return


def resolve_structured_ability(
    state: GameState,
    owner: int,
    source: MinionState | None,
    ability: dict[str, Any],
    target_ref: str | None = None,
    context: dict[str, Any] | None = None,
) -> None:
    if not ability_ready_for_limit(state, owner, ability):
        return
    ctx = {} if context is None else context
    if not ability_conditions_match(state, owner, source, target_ref, ability, ctx):
        return
    for effect in ability.get("effects", []):
        apply_structured_effect(state, owner, source, ability, effect, target_ref, ctx)


def trigger_structured_abilities(
    state: GameState,
    owner: int,
    source: MinionState | None,
    card: CardTemplate,
    trigger: str,
    target_ref: str | None = None,
    context: dict[str, Any] | None = None,
) -> None:
    if source is not None and source.silenced:
        return
    for ability in structured_abilities(card, trigger):
        resolve_structured_ability(state, owner, source, ability, target_ref=target_ref, context=context)


def primary_manual_ability(card: CardTemplate) -> dict[str, Any] | None:
    abilities = card.extra.get("abilities", [])
    for ability in abilities:
        if ability.get("trigger") in {"manual", "on_play"}:
            return ability
    return None


def structured_target_options(state: GameState, owner: int, target_rule: str) -> list[dict[str, Any]]:
    player = state.players[owner]
    enemy = state.players[1 - owner]
    if target_rule in {"none", "all_enemy_figures", "all_friendly_figures", "all_other_characters", "all_other_figures", "empty_friendly_slot", "friendly_discard_figure"}:
        return [{}]
    if target_rule == "friendly_figure":
        return [{"target_unit_id": minion.unit_id} for minion in player.board]
    if target_rule == "friendly_character":
        return [{"target_unit_id": minion.unit_id} for minion in player.board] + [{"target": "friendly_hero"}]
    if target_rule == "friendly_hero":
        return [{"target": "friendly_hero"}]
    if target_rule == "enemy_figure":
        return [{"target_unit_id": minion.unit_id} for minion in enemy.board]
    if target_rule == "damaged_enemy_figure":
        return [{"target_unit_id": minion.unit_id} for minion in enemy.board if minion.damage_taken > 0]
    if target_rule == "enemy_character":
        return [{"target_unit_id": minion.unit_id} for minion in enemy.board] + [{"target": "hero"}]
    if target_rule == "enemy_hero":
        return [{"target": "hero"}]
    if target_rule == "any_character":
        return (
            [{"target_unit_id": minion.unit_id} for minion in player.board + enemy.board]
            + [{"target": "friendly_hero"}, {"target": "hero"}]
        )
    return [{}]


def choose_default_target_ref(state: GameState, owner: int, source: MinionState | None, target_rule: str) -> str | None:
    player = state.players[owner]
    enemy = state.players[1 - owner]
    if target_rule in {"none", "all_enemy_figures", "all_friendly_figures", "all_other_figures", "all_other_characters", "empty_friendly_slot", "friendly_discard_figure"}:
        return None
    if target_rule == "enemy_figure":
        candidates = [minion for minion in enemy.board if minion.taunt] or list(enemy.board)
        if not candidates:
            return None
        candidates.sort(key=lambda minion: (minion.damage_taken == 0, -(minion.current_attack + minion.current_health)))
        return candidates[0].unit_id
    if target_rule == "damaged_enemy_figure":
        candidates = [minion for minion in enemy.board if minion.damage_taken > 0]
        if not candidates:
            return None
        candidates.sort(key=lambda minion: (minion.current_attack + minion.current_health), reverse=True)
        return candidates[0].unit_id
    if target_rule == "friendly_figure":
        candidates = [minion for minion in player.board if minion is not source]
        if not candidates and source is not None:
            return source.unit_id
        if not candidates:
            return None
        candidates.sort(key=lambda minion: (minion.damage_taken > 0, minion.current_attack + minion.current_health), reverse=True)
        return candidates[0].unit_id
    if target_rule == "friendly_character":
        candidates = [minion for minion in player.board if minion is not source]
        if candidates:
            candidates.sort(key=lambda minion: (minion.damage_taken > 0, minion.current_attack + minion.current_health), reverse=True)
            return candidates[0].unit_id
        return "friendly_hero"
    if target_rule == "friendly_hero":
        return "friendly_hero"
    if target_rule == "enemy_hero":
        return "hero"
    if target_rule == "any_character":
        if not [minion for minion in enemy.board if minion.taunt]:
            return "hero"
        if enemy.board:
            return enemy.board[0].unit_id
        return "hero"
    return None


def resolve_minion_effect(
    state: GameState,
    owner: int,
    source: MinionState | None,
    effect_kind: str,
    value: int,
    target: str | None = None,
    trigger: str = "battlecry",
) -> None:
    enemy = 1 - owner
    source_name = source.card.name if source else "Spell"
    if effect_kind == "damage_enemy":
        if target == "hero" or not state.players[enemy].board:
            deal_damage_to_hero(state, enemy, value, source_name)
            return
        target_minion = find_minion(state, target) if target else state.players[enemy].board[0]
        if target_minion:
            dealt = deal_damage_to_minion(state, target_minion, value)
            state.history.append(f"{source_name} deals {dealt} damage to {target_minion.card.name}.")
            if target_minion.current_health <= 0:
                remove_minion(state, target_minion)
        return

    if effect_kind == "heal":
        if target == "hero":
            healed = heal_hero(state.players[owner], value + 1)
            state.history.append(f"{source_name} heals {state.players[owner].name} for {healed}.")
            return
        target_minion = find_minion(state, target) if target else (state.players[owner].board[0] if state.players[owner].board else None)
        if target_minion:
            healed = heal_minion(target_minion, value + 1)
            state.history.append(f"{source_name} heals {target_minion.card.name} for {healed}.")
        return

    if effect_kind == "draw":
        draw_card(state, owner)
        draw_card(state, owner)
        state.history.append(f"{source_name} draws 2 cards.")
        return

    if effect_kind == "buff_friendly":
        target_minion = find_minion(state, target) if target else (state.players[owner].board[0] if state.players[owner].board else None)
        if target_minion:
            target_minion.enchant_attack += 2
            target_minion.enchant_health += 2
            state.history.append(f"{source_name} grants +2/+2 to {target_minion.card.name}.")
        return

    if effect_kind == "self_shield":
        if source:
            source.divine_shield = True
            state.history.append(f"{source_name} gains Divine Shield.")
        return

    if effect_kind == "summon_token":
        summoned = summon_minion(state, owner, guardian_token(), sleeping=True)
        if summoned:
            state.history.append(f"{source_name} summons {summoned.card.name}.")
        return

    if effect_kind == "freeze_like":
        target_minion = find_minion(state, target) if target else (state.players[enemy].board[0] if state.players[enemy].board else None)
        if target_minion:
            target_minion.sleeping = True
            state.history.append(f"{source_name} freezes the tempo of {target_minion.card.name}.")
        return


def resolve_spell(state: GameState, owner: int, card: CardTemplate, target: str | None = None) -> None:
    enemy = 1 - owner
    if card.spell_kind == "coin":
        state.players[owner].mana = min(MAX_MANA, state.players[owner].mana + 1)
        state.history.append(f"{state.players[owner].name} plays The Coin.")
        return

    if card.spell_kind == "damage":
        if target == "hero":
            deal_damage_to_hero(state, enemy, card.value, card.name)
            return
        target_minion = find_minion(state, target) if target else None
        if target_minion:
            dealt = deal_damage_to_minion(state, target_minion, card.value)
            state.history.append(f"{card.name} deals {dealt} to {target_minion.card.name}.")
            if target_minion.current_health <= 0:
                remove_minion(state, target_minion)
        return

    if card.spell_kind == "buff":
        target_minion = find_minion(state, target) if target else None
        if target_minion:
            target_minion.enchant_attack += card.value
            target_minion.enchant_health += card.value
            state.history.append(f"{card.name} gives +{card.value}/+{card.value} to {target_minion.card.name}.")
        return

    if card.spell_kind == "heal":
        if target == "hero":
            healed = heal_hero(state.players[owner], card.value)
            state.history.append(f"{card.name} heals {state.players[owner].name} for {healed}.")
            return
        target_minion = find_minion(state, target) if target else None
        if target_minion:
            healed = heal_minion(target_minion, card.value)
            state.history.append(f"{card.name} heals {target_minion.card.name} for {healed}.")
        return

    if card.spell_kind == "draw":
        draw_card(state, owner)
        draw_card(state, owner)
        state.history.append(f"{state.players[owner].name} casts {card.name} and draws 2 cards.")
        return

    if card.spell_kind == "random_missiles":
        for _ in range(3):
            candidates: list[str | None] = [minion.unit_id for minion in state.players[enemy].board] + ["hero"]
            if not candidates:
                break
            chosen = state.rng.choice(candidates)
            if chosen == "hero":
                deal_damage_to_hero(state, enemy, 1, card.name)
            else:
                minion = find_minion(state, chosen)
                if minion:
                    dealt = deal_damage_to_minion(state, minion, 1)
                    state.history.append(f"{card.name} pings {minion.card.name} for {dealt}.")
                    if minion.current_health <= 0:
                        remove_minion(state, minion)
        return

    if card.spell_kind == "summon_pair":
        for _ in range(2):
            summoned = summon_minion(state, owner, guardian_token(), sleeping=True)
            if summoned:
                state.history.append(f"{card.name} summons {summoned.card.name}.")
        return

    if card.spell_kind == "execute_damaged":
        target_minion = find_minion(state, target) if target else None
        if target_minion and target_minion.damage_taken > 0:
            state.history.append(f"{card.name} destroys {target_minion.card.name}.")
            remove_minion(state, target_minion)
        return

    if card.spell_kind == "aoe_enemy":
        for minion in list(state.players[enemy].board):
            dealt = deal_damage_to_minion(state, minion, card.value)
            state.history.append(f"{card.name} deals {dealt} to {minion.card.name}.")
            if minion.current_health <= 0:
                remove_minion(state, minion)
        return


def _speed_allowed_in_phase(speed: str | None, phase: str) -> bool:
    if phase == "main":
        return True
    # response phases: only fast and burst
    return speed in ("fast", "burst")


def legal_actions(state: GameState, player_index: int | None = None) -> list[dict[str, Any]]:
    if state.winner is not None:
        return []
    player_index = state.active_player if player_index is None else player_index
    player = state.players[player_index]
    enemy = state.players[1 - player_index]
    actions: list[dict[str, Any]] = []
    enemy_taunts = [minion for minion in enemy.board if minion.taunt]
    in_response = state.phase.startswith("response")

    for hand_index, card in enumerate(player.hand):
        if card.card_type == "minion":
            if in_response:
                continue
            if card.cost > player.mana:
                continue
            if len(player.board) >= MAX_BOARD_SIZE:
                continue
            for position in range(len(player.board) + 1):
                actions.append({"id": f"play:{hand_index}:{position}", "type": "play", "hand_index": hand_index, "position": position, "label": f"Play {card.name} at position {position}"})
        elif card.card_type == "relic":
            if in_response:
                continue
            if card.cost > player.mana:
                continue
            if len(player.relics) >= 2:
                continue
            actions.append({"id": f"relic:{hand_index}", "type": "play_relic", "hand_index": hand_index, "label": f"Play {card.name}"})
        else:
            if card.cost > player.mana + player.ritual_mana:
                continue
            if not _speed_allowed_in_phase(card.speed, state.phase):
                continue
            if card.extra.get("abilities"):
                manual_abilities = [a for a in card.extra["abilities"] if a.get("trigger") in ("manual", "on_play")]
                if not manual_abilities:
                    continue
                for abi_idx, ability in enumerate(manual_abilities):
                    options = structured_target_options(state, player_index, ability.get("target_rule", "none"))
                    mode_label = ability.get("label", card.name)
                    for option in options:
                        target_label = option.get("target_unit_id") or option.get("target") or "none"
                        modal_suffix = f":{abi_idx}" if len(manual_abilities) > 1 else ""
                        actions.append(
                            {
                                "id": f"spell:{hand_index}:{target_label}{modal_suffix}",
                                "type": "play_spell",
                                "hand_index": hand_index,
                                "target_unit_id": option.get("target_unit_id"),
                                "target": option.get("target"),
                                "ability_index": abi_idx if len(manual_abilities) > 1 else None,
                                "label": f"Cast {card.name} — {mode_label}" if len(manual_abilities) > 1 else f"Cast {card.name}",
                            }
                        )
            elif card.spell_kind in {"draw", "random_missiles", "summon_pair", "coin", "aoe_enemy"}:
                actions.append({"id": f"spell:{hand_index}:none", "type": "play_spell", "hand_index": hand_index, "label": f"Cast {card.name}"})
            elif card.spell_kind == "damage":
                targets = enemy_taunts or enemy.board
                for minion in targets:
                    actions.append({"id": f"spell:{hand_index}:{minion.unit_id}", "type": "play_spell", "hand_index": hand_index, "target_unit_id": minion.unit_id, "label": f"Cast {card.name} on {minion.card.name}"})
                if not enemy_taunts:
                    actions.append({"id": f"spell:{hand_index}:hero", "type": "play_spell", "hand_index": hand_index, "target": "hero", "label": f"Cast {card.name} on enemy hero"})
            elif card.spell_kind in {"buff", "heal"}:
                for minion in player.board:
                    actions.append({"id": f"spell:{hand_index}:{minion.unit_id}", "type": "play_spell", "hand_index": hand_index, "target_unit_id": minion.unit_id, "label": f"Cast {card.name} on {minion.card.name}"})
                if card.spell_kind == "heal":
                    actions.append({"id": f"spell:{hand_index}:hero", "type": "play_spell", "hand_index": hand_index, "target": "hero", "label": f"Cast {card.name} on your hero"})
            elif card.spell_kind == "execute_damaged":
                for minion in enemy_taunts or enemy.board:
                    if minion.damage_taken > 0:
                        actions.append({"id": f"spell:{hand_index}:{minion.unit_id}", "type": "play_spell", "hand_index": hand_index, "target_unit_id": minion.unit_id, "label": f"Cast {card.name} on {minion.card.name}"})

    # Attacks and hero powers are only available during the main phase for the active player
    if not in_response and player_index == state.active_player:
        for minion in player.board:
            if not minion.can_attack():
                continue
            valid_targets = enemy_taunts or enemy.board
            for target in valid_targets:
                actions.append({"id": f"attack:{minion.unit_id}:{target.unit_id}", "type": "attack", "unit_id": minion.unit_id, "target_unit_id": target.unit_id, "label": f"Attack {target.card.name} with {minion.card.name}"})
            rush_locked = minion.rush and minion.summoned_turn == state.turn_number
            if not enemy_taunts and not rush_locked:
                actions.append({"id": f"attack:{minion.unit_id}:hero", "type": "attack", "unit_id": minion.unit_id, "target": "hero", "label": f"Attack enemy hero with {minion.card.name}"})

    hero_power_cost = HERO_POWER_COST if player.hero_power_kind != "structured" else int(player.hero_power_data.get("resource_cost") or HERO_POWER_COST)
    available_mana = player.mana + player.ritual_mana
    if not in_response and not player.hero_power_used and available_mana >= hero_power_cost:
        if player.hero_power_kind == "structured":
            options = structured_target_options(state, player_index, player.hero_power_data.get("target_rule", "none"))
            for option in options:
                target_label = option.get("target_unit_id") or option.get("target") or "none"
                actions.append(
                    {
                        "id": f"hero_power:{target_label}",
                        "type": "hero_power",
                        "target_unit_id": option.get("target_unit_id"),
                        "target": option.get("target"),
                        "label": f"Use {player.hero_power_name}",
                    }
                )
        elif player.hero_power_kind == "ping":
            targets = enemy_taunts or enemy.board
            for minion in targets:
                actions.append({"id": f"hero_power:{minion.unit_id}", "type": "hero_power", "target_unit_id": minion.unit_id, "label": f"Use {player.hero_power_name} on {minion.card.name}"})
            if not enemy_taunts:
                actions.append({"id": "hero_power:hero", "type": "hero_power", "target": "hero", "label": f"Use {player.hero_power_name} on enemy hero"})
        elif player.hero_power_kind == "bless":
            for minion in player.board:
                actions.append({"id": f"hero_power:{minion.unit_id}", "type": "hero_power", "target_unit_id": minion.unit_id, "label": f"Use {player.hero_power_name} on {minion.card.name}"})
        else:
            actions.append({"id": "hero_power:none", "type": "hero_power", "label": f"Use {player.hero_power_name}"})

    if not in_response:
        for relic_index, relic in enumerate(player.relics):
            for ability in relic.extra.get("abilities", []):
                if ability.get("trigger") != "manual":
                    continue
                relic_cost = int(ability.get("resource_cost") or 0)
                if relic_cost > available_mana:
                    continue
                if ability.get("limit") == "once_each_turn" and not _check_ability_limit_available(state, player_index, ability):
                    continue
                options = structured_target_options(state, player_index, ability.get("target_rule", "none"))
                for option in options:
                    target_label = option.get("target_unit_id") or option.get("target") or "none"
                    actions.append(
                        {
                            "id": f"activate_relic:{relic_index}:{target_label}",
                            "type": "activate_relic",
                            "relic_index": relic_index,
                            "target_unit_id": option.get("target_unit_id"),
                            "target": option.get("target"),
                            "label": f"Activate {relic.name}",
                        }
                    )

    if in_response:
        actions.append({"id": "pass", "type": "pass", "label": "Pass (no response)"})
    else:
        actions.append({"id": "pass", "type": "pass", "label": "End turn"})
    return actions


def play_card(state: GameState, hand_index: int, position: int) -> None:
    player = state.players[state.active_player]
    enemy = state.players[1 - state.active_player]
    card = player.hand.pop(hand_index)
    player.mana -= card.cost
    has_haste = "charge" in card.keywords or "rush" in card.keywords
    survival_ready = player.flags.get("survival_no_sleeping", False)
    minion = summon_minion(state, state.active_player, card, position=position, sleeping=not (has_haste or survival_ready))
    if minion:
        state.history.append(f"{player.name} plays {card.name}.")
        if card.extra.get("abilities"):
            for ability in structured_abilities(card, "on_play"):
                target_ref = choose_default_target_ref(state, state.active_player, minion, ability.get("target_rule", "none"))
                resolve_structured_ability(state, state.active_player, minion, ability, target_ref=target_ref)
        elif card.battlecry:
            resolve_minion_effect(state, state.active_player, minion, card.battlecry, card.value)
        for relic in list(player.relics):
            trigger_structured_abilities(state, state.active_player, None, relic, "on_friendly_play", target_ref=minion.unit_id)
        for friendly_minion in list(player.board):
            if friendly_minion is minion:
                continue
            trigger_structured_abilities(state, state.active_player, friendly_minion, friendly_minion.card, "on_friendly_play", target_ref=minion.unit_id)
        for relic in list(enemy.relics):
            trigger_structured_abilities(state, 1 - state.active_player, None, relic, "on_enemy_play", target_ref=minion.unit_id)
        for enemy_minion in list(enemy.board):
            trigger_structured_abilities(state, 1 - state.active_player, enemy_minion, enemy_minion.card, "on_enemy_play", target_ref=minion.unit_id)


def play_spell(state: GameState, hand_index: int, target: str | None = None, caster_index: int | None = None, ability_index: int | None = None) -> None:
    caster = caster_index if caster_index is not None else state.active_player
    player = state.players[caster]
    if hand_index >= len(player.hand):
        return  # Safety: hand index no longer valid
    card = player.hand.pop(hand_index)
    remaining_cost = consume_ritual_mana(player, card.cost)
    player.mana -= remaining_cost
    state.history.append(f"{player.name} casts {card.name}.")
    if card.extra.get("abilities"):
        if is_friendly_target(state, caster, target):
            for relic in list(player.relics):
                trigger_structured_abilities(state, caster, None, relic, "on_friendly_targeted_by_spell_or_hero_power", target_ref=target)
        # Modal cards: use the specific ability chosen
        if ability_index is not None:
            manual_abilities = [a for a in card.extra["abilities"] if a.get("trigger") in ("manual", "on_play")]
            if ability_index < len(manual_abilities):
                resolve_structured_ability(state, caster, None, manual_abilities[ability_index], target_ref=target)
        else:
            ability = primary_manual_ability(card)
            if ability is not None:
                resolve_structured_ability(state, caster, None, ability, target_ref=target)
    else:
        resolve_spell(state, state.active_player, card, target=target)

    # Trigger on_spell_cast for relics (e.g., Aegis of Athena)
    for relic in list(player.relics):
        trigger_structured_abilities(state, caster, None, relic, "on_spell_cast")


def play_relic(state: GameState, hand_index: int) -> None:
    player = state.players[state.active_player]
    card = player.hand.pop(hand_index)
    remaining_cost = consume_ritual_mana(player, card.cost)
    player.mana -= remaining_cost
    player.relics.append(card)
    state.history.append(f"{player.name} plays relic {card.name}.")
    trigger_structured_abilities(state, state.active_player, None, card, "on_relic_play")


def activate_relic(state: GameState, relic_index: int, target: str | None = None) -> None:
    player = state.players[state.active_player]
    if relic_index >= len(player.relics):
        return
    relic = player.relics[relic_index]
    for ability in relic.extra.get("abilities", []):
        if ability.get("trigger") != "manual":
            continue
        cost = int(ability.get("resource_cost") or 0)
        remaining = consume_ritual_mana(player, cost)
        player.mana -= remaining
        state.history.append(f"{player.name} activates {relic.name}.")
        resolve_structured_ability(state, state.active_player, None, ability, target_ref=target)
        break


def destroy_relic(state: GameState, player_index: int, relic: CardTemplate) -> None:
    player = state.players[player_index]
    if relic in player.relics:
        player.relics.remove(relic)
        player.discard.append(relic)
        state.history.append(f"{relic.name} is destroyed.")


def declare_attack(state: GameState, attacker_id: str, target: str | None) -> None:
    """Phase 1: declare attack, open response window. Defender gets priority first."""
    attacker = find_minion(state, attacker_id)
    if attacker is None or attacker.owner != state.active_player or not attacker.can_attack():
        return
    trigger_structured_abilities(state, attacker.owner, attacker, attacker.card, "on_attack_declared", target_ref=attacker.unit_id)
    for relic in list(state.players[attacker.owner].relics):
        trigger_structured_abilities(state, attacker.owner, None, relic, "on_attack_declared", target_ref=attacker.unit_id)
    attacker.attacks_this_turn += 1
    attacker.sleeping = False
    defender_index = 1 - attacker.owner
    state.pending_attack = {"attacker_id": attacker_id, "target": target, "owner": attacker.owner, "defender_passed": False, "attacker_passed": False}
    state.phase = "response_defender"
    state.priority_player = defender_index
    state.history.append(f"{attacker.card.name} declares attack.")


def resolve_pending_attack(state: GameState) -> None:
    """Phase 2: resolve the declared attack after both players pass in response."""
    if state.pending_attack is None:
        return
    attacker_id = state.pending_attack["attacker_id"]
    target = state.pending_attack["target"]
    owner = state.pending_attack["owner"]
    state.pending_attack = None
    state.phase = "main"
    state.priority_player = None

    attacker = find_minion(state, attacker_id)
    if attacker is None:
        return
    enemy_index = 1 - owner

    if target == "hero":
        deal_damage_to_hero(state, enemy_index, attacker.current_attack, attacker.card.name)
        if attacker.lifesteal:
            healed = heal_hero(state.players[owner], attacker.current_attack)
            state.history.append(f"{attacker.card.name} lifesteals for {healed}.")
        return

    defender = find_minion(state, target or "")
    if defender is None:
        return
    dealt = deal_damage_to_minion(state, defender, attacker.current_attack, poisonous=attacker.poisonous)
    returned = deal_damage_to_minion(state, attacker, defender.current_attack, poisonous=defender.poisonous)
    state.history.append(f"{attacker.card.name} and {defender.card.name} trade {dealt} and {returned}.")
    # Overwhelm: excess damage spills to enemy hero
    if "overwhelm" in attacker.runtime_keywords and defender.current_health <= 0:
        # excess = attack power minus the health the defender had before combat
        defender_had = dealt  # dealt = actual damage applied (may be 0 if divine shield)
        if dealt > 0:
            # The defender's health before this hit was (current_health + dealt) since damage was already applied
            health_before_hit = defender.current_health + dealt
            excess = attacker.current_attack - health_before_hit
            if excess > 0:
                deal_damage_to_hero(state, enemy_index, excess, f"{attacker.card.name} (overwhelm)")
                state.history.append(f"{attacker.card.name} overwhelms for {excess} to the enemy hero.")
    if attacker.lifesteal and dealt > 0:
        healed = heal_hero(state.players[owner], dealt)
        state.history.append(f"{attacker.card.name} lifesteals for {healed}.")
    if defender.lifesteal and returned > 0:
        healed = heal_hero(state.players[defender.owner], returned)
        state.history.append(f"{defender.card.name} lifesteals for {healed}.")
    trigger_structured_abilities(
        state,
        owner,
        attacker,
        attacker.card,
        "on_strike",
        context={"struck_figure": True, "dealt_damage": dealt},
    )
    if defender.current_health <= 0:
        remove_minion(state, defender)
    if attacker.current_health <= 0:
        remove_minion(state, attacker)


def attack_with_minion(state: GameState, attacker_id: str, target: str | None) -> None:
    """Shortcut: declare + immediately resolve (no interactive response window).
    Used by non-interactive game loops. Interactive loops use declare_attack + pass_response instead."""
    declare_attack(state, attacker_id, target)
    resolve_pending_attack(state)


def pass_response(state: GameState, player_index: int) -> None:
    """A player passes during a response window. If both pass, combat resolves."""
    if state.pending_attack is None:
        return
    if player_index == state.pending_attack["owner"]:
        state.pending_attack["attacker_passed"] = True
    else:
        state.pending_attack["defender_passed"] = True

    if state.pending_attack["defender_passed"] and state.pending_attack["attacker_passed"]:
        # Both passed — resolve combat
        resolve_pending_attack(state)
    elif state.phase == "response_defender" and state.pending_attack["defender_passed"]:
        # Defender passed, give attacker a chance to respond
        state.phase = "response_attacker"
        state.priority_player = state.pending_attack["owner"]
    elif state.phase == "response_attacker" and state.pending_attack["attacker_passed"]:
        # Attacker passed after defender, resolve
        resolve_pending_attack(state)


def response_action_played(state: GameState, player_index: int) -> None:
    """Called after a Fast/Burst spell is played during a response window.
    Resets both pass flags so both players get another chance."""
    if state.pending_attack is None:
        return
    state.pending_attack["defender_passed"] = False
    state.pending_attack["attacker_passed"] = False
    # After playing a response, priority passes to the other player
    other = 1 - player_index
    state.priority_player = other
    if other == state.pending_attack["owner"]:
        state.phase = "response_attacker"
    else:
        state.phase = "response_defender"


def current_priority_player(state: GameState) -> int:
    """Return which player currently has priority to act."""
    if state.priority_player is not None:
        return state.priority_player
    return state.active_player


def use_hero_power(state: GameState, target: str | None = None) -> None:
    player = state.players[state.active_player]
    power_cost = HERO_POWER_COST if player.hero_power_kind != "structured" else int(player.hero_power_data.get("resource_cost") or HERO_POWER_COST)
    remaining_cost = consume_ritual_mana(player, power_cost)
    player.mana -= remaining_cost
    player.hero_power_used = True
    state.history.append(f"{player.name} uses {player.hero_power_name}.")
    if player.hero_power_kind == "structured":
        if is_friendly_target(state, state.active_player, target):
            for relic in list(player.relics):
                trigger_structured_abilities(state, state.active_player, None, relic, "on_friendly_targeted_by_spell_or_hero_power", target_ref=target)
        resolve_structured_ability(state, state.active_player, None, player.hero_power_data, target_ref=target)
    elif player.hero_power_kind == "ping":
        if target == "hero":
            deal_damage_to_hero(state, 1 - state.active_player, 1, player.hero_power_name)
        else:
            minion = find_minion(state, target or "")
            if minion:
                dealt = deal_damage_to_minion(state, minion, 1)
                state.history.append(f"{player.hero_power_name} deals {dealt} to {minion.card.name}.")
                if minion.current_health <= 0:
                    remove_minion(state, minion)
    elif player.hero_power_kind == "bless":
        minion = find_minion(state, target or "")
        if minion and minion.owner == state.active_player:
            minion.enchant_attack += 1
            minion.enchant_health += 1
            state.history.append(f"{minion.card.name} gains +1/+1.")
    elif player.hero_power_kind == "heal":
        healed = heal_hero(player, 2)
        state.history.append(f"{player.name} heals for {healed}.")
    elif player.hero_power_kind == "armor":
        player.armor += 2
        state.history.append(f"{player.name} gains 2 armor.")


def apply_action(state: GameState, action: dict[str, Any]) -> None:
    """Non-interactive apply: attacks resolve immediately (no response window).
    Used by bot self-play and legacy code."""
    if state.winner is not None:
        return
    kind = action["type"]
    if kind == "play":
        play_card(state, action["hand_index"], action["position"])
    elif kind == "play_relic":
        play_relic(state, action["hand_index"])
    elif kind == "play_spell":
        play_spell(state, action["hand_index"], action.get("target_unit_id") or action.get("target"), ability_index=action.get("ability_index"))
    elif kind == "attack":
        attack_with_minion(state, action["unit_id"], action.get("target_unit_id") or action.get("target"))
    elif kind == "hero_power":
        use_hero_power(state, action.get("target_unit_id") or action.get("target"))
    elif kind == "activate_relic":
        activate_relic(state, action["relic_index"], action.get("target_unit_id") or action.get("target"))
    elif kind == "pass":
        state.history.append(f"{state.players[state.active_player].name} ends the turn.")
        end_turn(state)
    else:
        raise ValueError(f"Unknown action type: {kind}")
    check_winner(state)


def apply_action_interactive(state: GameState, action: dict[str, Any], player_index: int) -> None:
    """Interactive apply: attacks open a response window. Both players get to respond.
    The game loop should use current_priority_player() to determine who acts next."""
    if state.winner is not None:
        return
    kind = action["type"]
    in_response = state.phase.startswith("response")

    if kind == "play":
        play_card(state, action["hand_index"], action["position"])
    elif kind == "play_relic":
        play_relic(state, action["hand_index"])
    elif kind == "play_spell":
        play_spell(state, action["hand_index"], action.get("target_unit_id") or action.get("target"), caster_index=player_index, ability_index=action.get("ability_index"))
        if in_response:
            response_action_played(state, player_index)
    elif kind == "attack":
        # In interactive mode, attack only DECLARES — doesn't resolve yet
        declare_attack(state, action["unit_id"], action.get("target_unit_id") or action.get("target"))
    elif kind == "hero_power":
        use_hero_power(state, action.get("target_unit_id") or action.get("target"))
    elif kind == "activate_relic":
        activate_relic(state, action["relic_index"], action.get("target_unit_id") or action.get("target"))
        if in_response:
            response_action_played(state, player_index)
    elif kind == "pass":
        if in_response:
            pass_response(state, player_index)
        else:
            state.history.append(f"{state.players[state.active_player].name} ends the turn.")
            end_turn(state)
    else:
        raise ValueError(f"Unknown action type: {kind}")
    check_winner(state)


def check_winner(state: GameState) -> None:
    if state.winner is not None:
        return
    if state.players[0].health <= 0 and state.players[1].health <= 0:
        state.winner = 0 if state.active_player == 0 else 1
    elif state.players[0].health <= 0:
        state.winner = 1
    elif state.players[1].health <= 0:
        state.winner = 0


def game_state_view(state: GameState, viewer: int) -> dict[str, Any]:
    you = state.players[viewer]
    opp = state.players[1 - viewer]
    return {
        "turn_number": state.turn_number,
        "active_player": state.players[state.active_player].name,
        "rules_summary": RULES_TEXT,
        "you": {
            "name": you.name,
            "health": you.health,
            "armor": you.armor,
            "mana": you.mana,
            "ritual_mana": you.ritual_mana,
            "max_mana": you.max_mana,
            "hero_power": {"name": you.hero_power_name, "kind": you.hero_power_kind, "used": you.hero_power_used},
            "hero": None if you.hero_card is None else {"name": you.hero_card.name, "text": you.hero_card.text},
            "deck_count": len(you.deck),
            "hand": [
                {
                    "hand_index": index,
                    "id": card.id,
                    "name": card.name,
                    "type": card.card_type,
                    "cost": card.cost,
                    "attack": card.attack,
                    "health": card.health,
                    "keywords": card.keywords,
                    "battlecry": card.battlecry,
                    "deathrattle": card.deathrattle,
                    "spell_kind": card.spell_kind,
                    "speed": card.speed,
                    "text": card.text,
                    "culture": card.culture_slug,
                }
                for index, card in enumerate(you.hand)
            ],
            "board": [minion.summary() for minion in you.board],
            "relics": [{"id": relic.id, "name": relic.name, "text": relic.text} for relic in you.relics],
            "graveyard": [{"name": card.name, "type": card.card_type, "cost": card.cost} for card in you.discard],
        },
        "opponent": {
            "name": opp.name,
            "health": opp.health,
            "armor": opp.armor,
            "mana": opp.mana,
            "ritual_mana": opp.ritual_mana,
            "max_mana": opp.max_mana,
            "hero_power": {"name": opp.hero_power_name, "kind": opp.hero_power_kind, "used": opp.hero_power_used},
            "hero": None if opp.hero_card is None else {"name": opp.hero_card.name, "text": opp.hero_card.text},
            "deck_count": len(opp.deck),
            "hand_count": len(opp.hand),
            "board": [minion.summary() for minion in opp.board],
            "relics": [{"id": relic.id, "name": relic.name, "text": relic.text} for relic in opp.relics],
            "graveyard": [{"name": card.name, "type": card.card_type, "cost": card.cost} for card in opp.discard],
        },
        "history": state.history[-25:],
        "phase": state.phase,
        "pending_attack": _pending_attack_view(state),
    }


def _pending_attack_view(state: GameState) -> dict[str, Any] | None:
    if state.pending_attack is None:
        return None
    attacker = find_minion(state, state.pending_attack["attacker_id"])
    target_id = state.pending_attack["target"]
    target_minion = find_minion(state, target_id or "") if target_id != "hero" else None
    return {
        "attacker": attacker.card.name if attacker else "unknown",
        "attacker_attack": attacker.current_attack if attacker else 0,
        "attacker_health": attacker.current_health if attacker else 0,
        "target": "enemy hero" if target_id == "hero" else (target_minion.card.name if target_minion else "unknown"),
        "target_attack": 0 if target_id == "hero" else (target_minion.current_attack if target_minion else 0),
        "target_health": state.players[1 - state.pending_attack["owner"]].health if target_id == "hero" else (target_minion.current_health if target_minion else 0),
    }
