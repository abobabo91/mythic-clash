"""
Hearthstone-like prototype rules for Mythic Clash.
"""

from __future__ import annotations

HERO_HEALTH = 30
STARTING_HAND_FIRST = 4
STARTING_HAND_SECOND = 5
MAX_MANA = 10
MAX_BOARD_SIZE = 5
MAX_HAND_SIZE = 10
MAX_TURNS = 30
HERO_POWER_COST = 2
SURVIVAL_INSTINCT_THRESHOLD = 15  # extra draw when HP <= this
DESPERATE_DRAW_THRESHOLD = 5  # draw 2 extra (instead of 1) when HP <= this
LAST_STAND_THRESHOLD = 10  # figures enter ready when HP <= this

RULES_TEXT = """
Mythic Clash Tavern Prototype

Goal
- Reduce the opposing hero from 30 Health to 0.
- Drawing from an empty deck deals escalating fatigue damage (1, 2, 3, ...).
- Past turn 30, both players take escalating overtime fatigue each turn.

Core structure
- Each player has a hero, a deck, a hand, and a board.
- Each side can control up to 5 figures.
- Cards cost mana to play.
- Mana increases by 1 each turn, up to 10.
- The second player starts with an extra card, The Coin, and 1 Ritual Mana after mulligan.

Setup
1. First player draws 4 cards.
2. Second player draws 5 cards.
3. Each player gets one mulligan.
4. The second player gains The Coin after mulligan.

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
- Survival Instinct: at 15 or fewer Health, draw an extra card at the start of your turn. At 5 or fewer, draw 2 extra instead.
- Last Stand: at 10 or fewer Health, your Figures enter play Ready (no sleeping).

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
