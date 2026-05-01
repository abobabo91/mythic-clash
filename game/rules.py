"""
Hearthstone-like prototype rules for Mythic Clash.
"""

from __future__ import annotations

HERO_HEALTH = 30
STARTING_HAND_FIRST = 3
STARTING_HAND_SECOND = 4
MAX_MANA = 10
MAX_BOARD_SIZE = 7
MAX_HAND_SIZE = 10
MAX_TURNS = 30
HERO_POWER_COST = 2

RULES_TEXT = """
Mythic Clash Tavern Prototype

Goal
- Reduce the opposing hero from 30 Health to 0.
- If the game reaches turn 30, the player with more total effective life wins.

Core structure
- Each player has a hero, a deck, a hand, and a board.
- Each side can control up to 7 minions.
- Cards cost mana to play.
- Mana increases by 1 each turn, up to 10.
- The second player starts with an extra card and The Coin.

Turn flow
1. Start of turn:
- Refill mana and gain 1 max mana crystal.
- Draw 1 card.
- Ready minions that have survived since last turn.
2. Main phase:
- Play cards from hand.
- Attack with ready minions.
- Use your hero power once.
- End turn.

Combat
- Minions deal attack damage equal to their Attack.
- Damage persists until healed.
- Minion combat is simultaneous unless Divine Shield prevents damage.
- Minions with Taunt must be attacked before non-Taunt targets.
- Charge can attack heroes or minions immediately.
- Rush can attack minions immediately but not heroes.

Keywords in this prototype
- Taunt: enemies must attack this first.
- Divine Shield: ignore the first damage instance.
- Charge: can attack immediately.
- Rush: can attack minions immediately.
- Lifesteal: damage dealt also heals your hero.
- Poisonous: any damage dealt to a minion destroys it.
- Reborn: the first time this dies, return it with 1 Health.

Competitive design goals
- Low entry: one board, one resource, no reaction stack.
- High ceiling: curve discipline, tempo, trading, hand management, lethal counting, and sequencing.
- Controlled randomness: small, bounded random effects are allowed when they create adaptation rather than coin-flip outcomes.
""".strip()


RARITY_MANA_BONUS = {
    "common": 0,
    "uncommon": 0,
    "rare": 0,
    "legendary": 1,
}


def minion_attack(power: int, speed: int) -> int:
    return max(1, round((power * 0.75 + speed * 0.25) / 1.6))


def minion_health(defense: int, wisdom: int) -> int:
    return max(1, round((defense * 0.8 + wisdom * 0.2)))


def minion_cost(total_stats: int, rarity: str) -> int:
    base = max(1, round(total_stats / 8.5))
    return max(1, min(MAX_MANA, base + RARITY_MANA_BONUS.get(rarity, 0)))


def spell_cost(base: int) -> int:
    return max(0, min(MAX_MANA, base))


def effect_scale(power: int, magic: int, wisdom: int) -> int:
    return max(1, round((power * 0.25 + magic * 0.5 + wisdom * 0.25) / 2.2))
