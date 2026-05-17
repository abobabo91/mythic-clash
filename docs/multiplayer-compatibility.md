# Mythic Clash Multiplayer Compatibility

Status: locked

This document does **not** make multiplayer the launch format.

It answers a narrower and more useful question:

- how do we keep Mythic Clash `1v1`-first while preserving the option to add meaningful `2v2` and larger team modes later?

Short answer:

- yes, we can add it later meaningfully
- but only if we protect the rules and card model from hardcoded `1v1` assumptions now

## Recommendation

Build and balance Mythic Clash around:

- `1v1` first

But architect the rules around:

- players
- teams
- target scopes
- board ownership

This gives us the best of both worlds:

- clean launch focus
- real expansion room later

## What Kind Of Multiplayer We Should Support Later

There are two main paths.

## 1. Shared-team battlefield

Both teammates partially share:

- board space
- resources
- or major combat zones

Pros:

- very social
- very combo-heavy
- strong team identity

Cons:

- much harder to balance
- much harder to read
- much easier to break with support cards and relics

## 2. Parallel teammates

Each player has their own:

- Hero
- deck
- hand
- mana
- Figure row
- Relic row

But they are on the same team.

Pros:

- easiest to understand
- easiest to implement from a `1v1` base
- easiest to extend to `2v2` and larger team formats
- preserves card and board readability

Cons:

- slightly less “shared battle table” feeling

## Final recommendation

Later multiplayer should use:

- `parallel teammates`

That is the correct future direction for Mythic Clash.

## The Multiplayer-Safe Rules Principle

The current game should continue to behave like a `1v1` game.

But card text and engine concepts should be written in a way that can later distinguish:

- `self`
- `friendly`
- `ally`
- `enemy`
- `enemy team`
- `all opposing players`

That is the key future-proofing move.

## Launch vs Future Mode Split

## Launch

Balanced and supported:

- `1v1`

## Future

Possible after the core game stabilizes:

- `2v2`
- free-for-all variants if desired later
- larger team variants if the UI and pacing support them

Do **not** attempt to balance launch around all of them at once.

## How A Clean `2v2` Would Likely Work Later

Recommended model:

- two players per team
- each player has their own hero, hand, deck, mana, and board
- each player takes their own turn
- effects can target friendly units, ally units, enemy units, enemy heroes, or all enemies depending on wording
- the team loses when both heroes on that team are defeated

Recommended seat order:

- Team A Player 1
- Team B Player 1
- Team A Player 2
- Team B Player 2

This keeps tempo distributed and prevents one team from dumping two full consecutive turns too easily.

## Why Not Shared Mana Or Shared Board

Those ideas are tempting, but they create many problems:

- support relics scale too hard
- aggro decks become explosive too quickly
- combo turns get much longer
- board states become harder to read

Parallel boards avoid most of that.

## What The Engine Must Avoid Hardcoding Now

To keep multiplayer possible later, the engine should avoid assumptions like:

- there are exactly two players forever
- there is exactly one enemy hero
- there is exactly one enemy board
- “friendly” always means only your own cards
- “all enemies” always means one opposing player

Even if the launch implementation uses 2 players only, the internal language should not trap us there.

## Multiplayer-Safe Target Vocabulary

The card system should expand its target rules to support team-aware language.

Recommended vocabulary additions:

- `ally_figure`
- `ally_hero`
- `ally_character`
- `friendly_team_figure`
- `friendly_team_character`
- `enemy_team_figure`
- `enemy_team_character`
- `enemy_team_hero`
- `all_enemy_figures`
- `all_enemy_heroes`
- `all_enemy_characters`
- `all_friendly_team_figures`
- `all_friendly_team_characters`

Important distinction:

- `friendly` should usually mean “you control”
- `ally` should usually mean “your teammate controls”

That is much clearer than overloading one word later.

## Board Ownership Vocabulary

The rules model should clearly distinguish:

- `controller`
- `owner`
- `team`
- `seat`

These concepts make future modes easier:

- `owner`: whose deck the card started in
- `controller`: who currently controls it
- `team`: which side that player belongs to
- `seat`: their position in turn order

## Future-Proofing Card Text

Current cards should prefer wording like:

- `friendly Figure`
- `friendly Hero`
- `enemy Figure`
- `enemy Hero`
- `all enemy Figures`

and avoid vague wording like:

- `your side`
- `their side`

unless the engine defines those explicitly.

That way, later multiplayer cards can cleanly say:

- `an ally Figure`
- `both friendly Heroes`
- `all enemy Figures`

without rewriting the whole language model.

## Card Types That Need Extra Care For Multiplayer

## 1. Healing and protection

These scale very hard in team games.

Risk:

- one support deck keeps two heroes alive too efficiently

Guideline:

- most launch healing should target your own Hero or a friendly Figure only
- ally-targeted healing can be introduced later in a controlled way

## 2. Draw and resource acceleration

Risk:

- team decks funnel value too efficiently

Guideline:

- avoid “both players draw” style effects at launch
- avoid relics that broadly refund costs to the whole team

## 3. Aura relics

Risk:

- one relic unintentionally buffs two whole boards

Guideline:

- launch relics should affect only cards you control unless explicitly marked otherwise

## 4. Summon and token engines

Risk:

- swarm scaling becomes much stronger in team formats

Guideline:

- keep token generation board-local by default

## 5. Burn and reach

Risk:

- direct damage that is fair in `1v1` becomes too flexible in `2v2`

Guideline:

- be careful with cards that can freely target any enemy hero
- team formats may need separate deckbuilding or balance rules later

## What Rules We Should Prepare Now

We should prepare the rules architecture now for:

- teams as a concept
- player seat order
- team win conditions
- board-local vs team-wide targeting
- ally-specific targeting

We should **not** prepare full multiplayer balance now for:

- shared mana
- giant team boards
- many ally combo loops
- special multiplayer-only card pools

## Multiplayer-Safe Design Rules For New Cards

When designing cards now, follow these rules:

### 1. Default to self-board effects

Most support cards should help:

- your Hero
- your Figures
- your Relics

not “everyone friendly on the team”

### 2. Make team-wide effects rare later

Team-wide buffs and heals should be premium and tightly costed if introduced later.

### 3. Keep attack logic board-local

In future `2v2`, a Figure should usually attack from:

- its controller’s board

and target:

- a legal enemy Figure or Hero

without needing a shared formation board at first.

### 4. Avoid cards that become exponentially stronger with more players

Examples to be careful with:

- “draw for every friendly card played this turn”
- “allies everywhere gain +1/+1 whenever anything dies”
- “your team’s spells cost 1 less”

### 5. Keep signature characters mostly self-contained

Signature Characters should mainly scale with:

- their own board
- their own controller

not with the entire team by default

That keeps them memorable without becoming multiplayer abuse cases.

## Good Future Multiplayer Hooks

If we later want explicit team-play cards, these are good directions:

- protect an ally Hero
- move one ally Figure
- let an ally draw 1
- grant one ally Figure Guard this combat
- let an ally use your support relic once

These are readable and social without exploding complexity.

## Bad Future Multiplayer Hooks

These are much riskier:

- both teammates fully share mana
- both teammates share one giant hand
- free spell-copying across the whole team
- passive relics that affect all friendly boards all the time
- alternate team-only win conditions

## Suggested Future Mode Roadmap

If multiplayer is ever added, the order should be:

1. make the engine team-aware internally
2. test `2v2` with no multiplayer-exclusive cards
3. add only a very small number of ally-aware support cards if needed
4. evaluate pacing, readability, and degenerate combos
5. only then consider larger `XvX` modes

## Exact Recommendation For Today

Today, Mythic Clash should do this:

- keep `1v1` as the official launch format
- keep deck balance focused on `1v1`
- make card wording and target scopes multiplayer-safe
- make the engine model capable of teams later

That is enough to preserve the option meaningfully.

## Bottom Line

Yes, `2v2` and even larger `XvX` formats can be added later in a meaningful way.

But the healthy version is:

- `1v1` first
- parallel teammates later
- multiplayer-safe wording now
- multiplayer balance later

That gives Mythic Clash expansion room without sacrificing launch clarity.

