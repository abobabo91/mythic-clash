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
    effect_scale,
    minion_attack,
    minion_cost,
    minion_health,
    spell_cost,
)


ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR = ROOT / "data" / "figures"


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
    summoned_turn: int = 0

    @property
    def current_attack(self) -> int:
        return max(0, self.attack + self.enchant_attack)

    @property
    def current_health(self) -> int:
        return self.health + self.enchant_health - self.damage_taken

    @property
    def taunt(self) -> bool:
        return "taunt" in self.card.keywords

    @property
    def rush(self) -> bool:
        return "rush" in self.card.keywords

    @property
    def charge(self) -> bool:
        return "charge" in self.card.keywords

    @property
    def lifesteal(self) -> bool:
        return "lifesteal" in self.card.keywords

    @property
    def poisonous(self) -> bool:
        return "poisonous" in self.card.keywords

    def can_attack(self) -> bool:
        return self.current_attack > 0 and not self.sleeping and self.attacks_this_turn == 0

    def summary(self) -> dict[str, Any]:
        return {
            "unit_id": self.unit_id,
            "name": self.card.name,
            "culture": self.card.culture_slug,
            "attack": self.current_attack,
            "health": self.current_health,
            "max_health": self.health + self.enchant_health,
            "sleeping": self.sleeping,
            "can_attack": self.can_attack(),
            "keywords": self.card.keywords,
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
    discard: list[CardTemplate] = field(default_factory=list)
    hero_power_used: bool = False
    hero_power_kind: str = "ping"
    hero_power_name: str = "Heroic Spark"

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


def derive_keywords(figure: dict[str, Any], attack: int, health: int) -> list[str]:
    text = f"{figure['ability']['name']} {figure['ability']['description']} {' '.join(figure['domains'])}".lower()
    domains = set(figure["domains"])
    keywords: list[str] = []

    if "shield" in text or "ward" in text or "barrier" in text:
        keywords.append("divine_shield")
    if "guardian" in text or "protection" in domains or "mountain" in domains or ("earth" in domains and health >= 9):
        keywords.append("taunt")
    if "drain" in text or "heal self" in text or "healing" in domains:
        keywords.append("lifesteal")
    if "serpent" in domains or "plague" in domains or "poison" in text:
        keywords.append("poisonous")
    if "rebirth" in text or "revive" in text or "resurrection" in text or ("death" in domains and health >= 6):
        keywords.append("reborn")
    if "wind" in domains or "speed" in text or (attack >= 8 and "hero" in figure["type"]):
        keywords.append("rush")
    if "lightning" in text or "charge" in text or ("wind" in domains and attack >= 7):
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


def create_game(
    deck_a: list[CardTemplate],
    deck_b: list[CardTemplate],
    player_a: str = "Player A",
    player_b: str = "Player B",
    seed: int | None = None,
) -> GameState:
    power_a = choose_hero_power(deck_a)
    power_b = choose_hero_power(deck_b)
    players = [
        PlayerState(name=player_a, deck=shuffle_deck(deck_a, seed), hero_power_kind=power_a[0], hero_power_name=power_a[1]),
        PlayerState(name=player_b, deck=shuffle_deck(deck_b, None if seed is None else seed + 1), hero_power_kind=power_b[0], hero_power_name=power_b[1]),
    ]
    state = GameState(players=players, rng=random.Random(seed))
    for _ in range(STARTING_HAND_FIRST):
        draw_card(state, 0)
    for _ in range(STARTING_HAND_SECOND):
        draw_card(state, 1)
    players[1].hand.append(ALL_CARDS["spell-the-coin"])
    start_turn(state, 0)
    return state


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
    draw_card(state, player_index)
    if state.winner is not None:
        return
    for minion in player.board:
        minion.sleeping = False
        minion.attacks_this_turn = 0
    state.history.append(
        f"Turn {state.turn_number}: {player.name} starts with {player.health} health, {player.armor} armor, and {player.mana} mana."
    )


def end_turn(state: GameState) -> None:
    next_player = 1 - state.active_player
    if next_player == 0:
        state.turn_number += 1
    if state.turn_number > MAX_TURNS:
        resolve_timeout_winner(state)
        return
    start_turn(state, next_player)


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
    state.next_unit_id += 1
    position = len(player.board) if position is None else max(0, min(position, len(player.board)))
    player.board.insert(position, minion)
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
        state.history.append(f"{minion.card.name} dies.")
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
    minion.damage_taken += amount
    if poisonous and amount > 0:
        minion.damage_taken = minion.max_health + minion.enchant_health
    return amount


def heal_hero(player: PlayerState, amount: int) -> int:
    before = player.health
    player.health = min(HERO_HEALTH, player.health + amount)
    return player.health - before


def heal_minion(minion: MinionState, amount: int) -> int:
    before = minion.damage_taken
    minion.damage_taken = max(0, minion.damage_taken - amount)
    return before - minion.damage_taken


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


def legal_actions(state: GameState, player_index: int | None = None) -> list[dict[str, Any]]:
    if state.winner is not None:
        return []
    player_index = state.active_player if player_index is None else player_index
    player = state.players[player_index]
    enemy = state.players[1 - player_index]
    actions: list[dict[str, Any]] = []
    enemy_taunts = [minion for minion in enemy.board if minion.taunt]

    for hand_index, card in enumerate(player.hand):
        if card.cost > player.mana:
            continue
        if card.card_type == "minion":
            if len(player.board) >= MAX_BOARD_SIZE:
                continue
            for position in range(len(player.board) + 1):
                actions.append({"id": f"play:{hand_index}:{position}", "type": "play", "hand_index": hand_index, "position": position, "label": f"Play {card.name} at position {position}"})
        else:
            if card.spell_kind in {"draw", "random_missiles", "summon_pair", "coin", "aoe_enemy"}:
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

    for minion in player.board:
        if not minion.can_attack():
            continue
        valid_targets = enemy_taunts or enemy.board
        for target in valid_targets:
            actions.append({"id": f"attack:{minion.unit_id}:{target.unit_id}", "type": "attack", "unit_id": minion.unit_id, "target_unit_id": target.unit_id, "label": f"Attack {target.card.name} with {minion.card.name}"})
        rush_locked = minion.rush and minion.summoned_turn == state.turn_number
        if not enemy_taunts and not rush_locked:
            actions.append({"id": f"attack:{minion.unit_id}:hero", "type": "attack", "unit_id": minion.unit_id, "target": "hero", "label": f"Attack enemy hero with {minion.card.name}"})

    if not player.hero_power_used and player.mana >= HERO_POWER_COST:
        if player.hero_power_kind == "ping":
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

    actions.append({"id": "pass", "type": "pass", "label": "End turn"})
    return actions


def play_card(state: GameState, hand_index: int, position: int) -> None:
    player = state.players[state.active_player]
    card = player.hand.pop(hand_index)
    player.mana -= card.cost
    minion = summon_minion(state, state.active_player, card, position=position, sleeping=not ("charge" in card.keywords or "rush" in card.keywords))
    if minion:
        state.history.append(f"{player.name} plays {card.name}.")
        if card.battlecry:
            resolve_minion_effect(state, state.active_player, minion, card.battlecry, card.value)


def play_spell(state: GameState, hand_index: int, target: str | None = None) -> None:
    player = state.players[state.active_player]
    card = player.hand.pop(hand_index)
    player.mana -= card.cost
    state.history.append(f"{player.name} casts {card.name}.")
    resolve_spell(state, state.active_player, card, target=target)


def attack_with_minion(state: GameState, attacker_id: str, target: str | None) -> None:
    attacker = find_minion(state, attacker_id)
    if attacker is None or attacker.owner != state.active_player or not attacker.can_attack():
        return
    enemy_index = 1 - attacker.owner
    attacker.attacks_this_turn += 1
    attacker.sleeping = False
    if target == "hero":
        deal_damage_to_hero(state, enemy_index, attacker.current_attack, attacker.card.name)
        if attacker.lifesteal:
            healed = heal_hero(state.players[attacker.owner], attacker.current_attack)
            state.history.append(f"{attacker.card.name} lifesteals for {healed}.")
        return

    defender = find_minion(state, target or "")
    if defender is None:
        return
    dealt = deal_damage_to_minion(state, defender, attacker.current_attack, poisonous=attacker.poisonous)
    returned = deal_damage_to_minion(state, attacker, defender.current_attack, poisonous=defender.poisonous)
    state.history.append(f"{attacker.card.name} and {defender.card.name} trade {dealt} and {returned}.")
    if attacker.lifesteal and dealt > 0:
        healed = heal_hero(state.players[attacker.owner], dealt)
        state.history.append(f"{attacker.card.name} lifesteals for {healed}.")
    if defender.lifesteal and returned > 0:
        healed = heal_hero(state.players[defender.owner], returned)
        state.history.append(f"{defender.card.name} lifesteals for {healed}.")
    if defender.current_health <= 0:
        remove_minion(state, defender)
    if attacker.current_health <= 0:
        remove_minion(state, attacker)


def use_hero_power(state: GameState, target: str | None = None) -> None:
    player = state.players[state.active_player]
    player.mana -= HERO_POWER_COST
    player.hero_power_used = True
    state.history.append(f"{player.name} uses {player.hero_power_name}.")
    if player.hero_power_kind == "ping":
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
    if state.winner is not None:
        return
    kind = action["type"]
    if kind == "play":
        play_card(state, action["hand_index"], action["position"])
    elif kind == "play_spell":
        play_spell(state, action["hand_index"], action.get("target_unit_id") or action.get("target"))
    elif kind == "attack":
        attack_with_minion(state, action["unit_id"], action.get("target_unit_id") or action.get("target"))
    elif kind == "hero_power":
        use_hero_power(state, action.get("target_unit_id") or action.get("target"))
    elif kind == "pass":
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
            "max_mana": you.max_mana,
            "hero_power": {"name": you.hero_power_name, "kind": you.hero_power_kind, "used": you.hero_power_used},
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
                    "text": card.text,
                    "culture": card.culture_slug,
                }
                for index, card in enumerate(you.hand)
            ],
            "board": [minion.summary() for minion in you.board],
        },
        "opponent": {
            "name": opp.name,
            "health": opp.health,
            "armor": opp.armor,
            "mana": opp.mana,
            "max_mana": opp.max_mana,
            "hero_power": {"name": opp.hero_power_name, "kind": opp.hero_power_kind, "used": opp.hero_power_used},
            "deck_count": len(opp.deck),
            "hand_count": len(opp.hand),
            "board": [minion.summary() for minion in opp.board],
        },
        "history": state.history[-15:],
    }
