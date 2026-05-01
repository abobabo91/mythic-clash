# Mythic Clash Tavern Prototype

This version pivots the game toward a Hearthstone-like digital card battler.

The goal is:

- low entry: one hero, one mana system, one board
- high ceiling: curve discipline, trading, sequencing, pressure, hand management, and lethal counting
- LLM-playable: every decision can be made from a compact state snapshot plus a list of legal actions

## Core structure

### Win condition

- Both heroes start at `30 Health`
- some effects can add `Armor`
- reduce the enemy hero to `0`
- if the game reaches `turn 30`, higher `Health + Armor` wins

### Deck model

- prototype deck size: `18 cards`
- mostly mythological figure minions
- plus a small package of generated support spells
- second player receives `The Coin`

### Turn flow

1. gain one maximum mana crystal, up to `10`
2. refill current mana to max
3. draw one card
4. unsleep surviving minions
5. take actions until you pass

### Board model

- one shared board per player
- max `7` minions per side
- minion order is preserved
- board order does not drive many effects yet, but the engine keeps it because positional play is valuable in digital card games

## Why this is closer to best practice

This follows the strongest parts of modern competitive digital card games:

- one clean resource system
- visible board combat
- persistent minion damage
- tight board limits
- second-player compensation
- small, readable keyword set
- bounded randomness instead of pure chaos

## Borrowed conventions

The prototype borrows these Hearthstone-like conventions:

- mana ramps by `1` each turn
- the second player gets `The Coin`
- board space is capped
- minions attack once per turn
- `Taunt`, `Divine Shield`, `Charge`, `Rush`, `Lifesteal`, `Poisonous`, and `Reborn` are compact, high-signal keywords

## Card types

### Minions

Most existing mythological figures are normalized into minions with:

- `Attack`
- `Health`
- `Cost`
- `Keywords`
- optional `Battlecry`
- optional `Deathrattle`

### Spells

The prototype also injects a few generated support spells such as:

- direct damage
- healing
- buff
- draw
- summon pair
- execute damaged minion
- small random missile effect

That gives the game more tactical range without requiring us to hand-author 2,000 unique spell cards yet.

## Keywords

- `Taunt`: enemies must attack this before other targets
- `Divine Shield`: ignores the first damage instance
- `Charge`: can attack immediately, including heroes
- `Rush`: can attack minions immediately
- `Lifesteal`: damage dealt also heals your hero
- `Poisonous`: any non-zero damage it deals to a minion destroys that minion
- `Reborn`: first death returns the minion with `1 Health`

## Hero powers

Each deck gets a simple hero power inferred from its mythic themes:

- aggressive decks tend to get a `1 damage` ping
- supportive/light decks tend to get a `+1/+1` blessing
- restorative decks tend to get a `heal 2`
- slower decks tend to get `gain 2 armor`

This is intentionally simple. The hero power should shape tempo decisions without dominating the deck identity.

## Randomness philosophy

Some luck is good. Competitive best practice is not “remove randomness,” but “bound it.”

Good randomness:

- small random missile effects
- topdeck variance
- match-to-match draw order
- second-player compensation via The Coin

Bad randomness:

- huge board wipes from tiny mana
- random effects that decide the whole game from a massive pool
- card text that makes planning impossible

So this prototype uses controlled randomness that still leaves room for skill:

- you usually know the likely outcomes
- the range is small enough that good sequencing still matters
- random effects tend to be tactical nudges, not total game rewrites

## How current figure data maps into cards

Your figure data already has:

- rarity
- alignment
- five stats
- domain tags
- ability text

The prototype projects those into:

- minion cost
- attack
- health
- keyword set
- battlecry
- deathrattle

This lets the dataset become playable immediately while preserving the mythology flavor.

## LLM self-play model

The default AI path is intentionally stateless per turn:

- the prompt always contains the rules
- the prompt always contains the current board
- the prompt always contains the player’s hand
- the prompt always contains recent game history
- the prompt always contains the legal actions

The model returns one JSON action.

That means:

- no ML training pipeline is needed
- no hidden search tree is required
- the AI is interpretable from its turn-by-turn reasons

## Agentic placeholder

There is also a placeholder `AgenticLLMPlayer`.

Right now it uses the same one-turn prompt loop, but it gives us a stable seam for future upgrades like:

- short-term memory
- matchup notes
- tool-using search
- multi-step planning

## Recommended next tuning steps

1. Reduce automatic `Taunt` frequency if too many games stall.
2. Tune spell density so the format does not become “all burn, no board.”
3. Add a few adjacency or positioning effects once the base system is stable.
4. Run many self-play logs and look for:
   early non-games
   repeated dominant curves
   too much face-race
   too little comeback space
