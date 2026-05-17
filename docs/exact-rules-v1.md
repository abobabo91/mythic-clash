# Mythic Clash Exact Rules v1

Status: locked

This document turns the design recommendations into a concrete game specification.

It is intentionally opinionated. The point is to stop debating the whole game at once and give the project a real rules target.

## Core Identity

Mythic Clash is a 1v1 digital mythic card battler.

The game should be:

- board-first
- readable in under a minute
- tactically interactive
- low on hidden randomness
- deep in sequencing, trading, and matchup adaptation

It should feel closer to:

- Hearthstone in readability
- Runeterra in limited interaction
- Magic in tournament structure

It should not feel like:

- a full-stack rules labyrinth
- a solitaire combo race
- a random-effect circus

## Final v1 Decision Summary

These are the decisions this document locks in.

- 30 Health heroes
- 24-card main deck
- 6-card sideboard for competitive play
- 1 hero per deck
- 1 primary culture plus up to 1 secondary culture
- up to 10 mana
- up to 2 banked `Ritual Mana` for spells and hero powers only
- max 5 figures per side
- 4-card starting hand for first player
- 5-card starting hand plus `The Coin` for second player
- one mulligan
- persistent unit damage
- figures attack once per turn
- limited response windows with `Slow`, `Fast`, and `Burst` timing
- fatigue instead of hard turn-limit victory

## Competitive Integrity Constraints

These are launch constraints, not optional style notes.

They exist to keep Mythic Clash easy to enter, hard to master, and readable under pressure.

### 1. Telegraphed lethality

Mythic Clash should usually kill through visible pressure.

That means:

- most lethal turns should come from board presence, a visible Relic, or a known signature threat
- direct hand-burst should usually finish pressure that already exists, not replace it
- large face-damage swings should be expensive, setup-gated, or clearly telegraphed

Do not normalize:

- cheap face-burst chains from low board states
- repeated zero-cost or near-zero-cost damage compression
- "safe life totals are fake" finishing patterns as a normal metagame expectation

### 2. Restricted generation and discover

Mythic Clash may use generation and `discover`, but only in disciplined forms.

Launch rules:

- generated cards should usually come from explicit and narrow buckets
- `discover` should point to a visible domain, culture, or rules-defined mini-pool
- long "created by created by created by" chains are not a normal launch pattern
- full-pool random generation should stay rare and deliberate, not routine

The goal is uncertainty without memory-tax opacity.

### 3. Launch complexity budget

Most launch cards should be legible on first read.

Default expectation:

- one primary job per card
- one main timing expectation per card
- at most one meaningful rider on most non-signature cards

Allowed exceptions:

- signature characters
- a few build-around Relics
- a few late-game finishers

Not allowed:

- routine text-wall cards
- many conditional branches on ordinary early and midgame cards
- cultures whose identity only works if every card is individually complex

### 4. Visible comeback lines

The game should avoid both hopelessness and rubber-band theft.

Every competitive culture or family should therefore have access to:

- at least one stabilizing line when behind
- at least one way to punish overextension
- at least one path to convert survival into renewed pressure

These tools should create outs, not erase earned advantage.

## Required Digital Clarity

Mythic Clash is a digital card game, so readability rules are part of the game design itself.

The shipped game should clearly show:

- whose priority it is
- when a response window is open
- what Figures can still attack
- current mana and `Ritual Mana`
- active Relics and passive sources
- a clean public action log, including generated or discovered cards when they become public

If those things are unclear, the rules will feel harder than they really are.

## Card Types

Mythic Clash v1 uses four real card types and one token class.

### 1. Hero

Each deck has exactly one Hero.

A Hero defines:

- your primary culture
- your hero power
- your deck identity

Heroes start in play and are not shuffled into the deck.

Hero baseline:

- 30 Health
- 0 Armor
- one hero power

### 2. Figure

Figures are the main board units.

They have:

- cost
- attack
- health
- traits / domains
- optional keywords
- optional text abilities

Figures are the main source of:

- board pressure
- trading
- tempo
- most match-winning threats

### 3. Spell

Spells are one-shot effects.

Every spell has one of three timings:

- `Slow`
- `Fast`
- `Burst`

Spells provide:

- removal
- combat tricks
- healing
- draw / filtering
- token generation
- finishers

### 4. Relic

Relics are persistent non-figure permanents.

They occupy a separate support row and do not count against the 5-figure board cap.

Relics may have:

- passive effects
- triggered effects
- activated abilities

Relics are important because they let cultures express identity without forcing every deck to be just creatures plus burn spells.

### 5. Token

Tokens are generated by other cards and are not legal deckbuilding cards unless a rule explicitly says otherwise.

## Deck Construction

## Main Deck

Each ladder or tournament deck contains:

- exactly 24 main-deck cards
- exactly 1 Hero

The Hero is not counted among the 24 main-deck cards.

## Sideboard

Competitive sideboard:

- up to 6 cards

Ladder:

- no sideboard used during the match

## Culture Rules

Each deck chooses:

- 1 primary culture
- optionally 1 secondary culture

The Hero must belong to the primary culture.

Main deck composition rules:

- at least 12 cards from the primary culture
- up to 6 cards from the secondary culture
- up to 6 neutral / core cards

If no secondary culture is chosen:

- the freed slots may be filled by more primary culture cards or neutral / core cards

## Type Composition Rules

To keep the game board-centric, every main deck must contain:

- at least 14 Figures
- at most 8 Spells
- at most 2 Relics

This is one of the most important anti-degeneracy rules in the whole format.

It prevents:

- spell-only decks
- low-board face-race piles
- relic prison shells that skip combat

## Copy Limits

- a deck may include up to 2 copies of a card by name
- `Legendary` figures and unique named relics are limited to 1 copy
- generated tokens do not affect copy limits

## Legal Card Groups

At launch, a deck may use legal cards from:

- its primary culture
- its secondary culture, if chosen
- neutral core cards
- domain support cards tied to the chosen cultures

## Setup

1. Randomly determine the first player.
2. First player draws 4 cards.
3. Second player draws 5 cards.
4. Each player may mulligan any number of cards once.
5. Replacements are drawn from the deck after the returned cards are shuffled back.
6. The second player adds `The Coin` to hand after the mulligan is complete.
7. Heroes begin at 30 Health and 0 Armor.
8. Both players begin with 0 mana and 0 Ritual Mana.

## Mulligan Rules

Mulligan goals are part of the skill test.

The mulligan happens only once.

Players may keep any number of cards and redraw the rest.

There is no additional free redraw after that.

## Resource System

## Mana

- each player starts with 0 maximum mana
- at the start of your turn, gain 1 maximum mana
- maximum mana cannot exceed 10
- at the start of your turn, refill current mana to maximum

## Ritual Mana

Unused regular mana at the end of your turn converts into `Ritual Mana`.

Ritual Mana rules:

- maximum stored Ritual Mana is 2
- Ritual Mana can only be used on Spells and Hero Powers
- Ritual Mana is spent before regular mana when paying for a Spell

This system gives the game planning depth without becoming a reaction-heavy stack game.

## Hand Size, Drawing, and Fatigue

- maximum hand size is 10
- if you would draw a card while at 10 cards, that card is burned
- if you would draw from an empty deck, you take fatigue damage instead
- fatigue starts at 1 and increases by 1 each failed draw

## Board Structure

Each player has:

- a Hero zone
- a Figure row
- a Relic row

Board limits:

- maximum 5 Figures in play
- maximum 2 Relics in play

Figure order is preserved from left to right.

This matters for:

- adjacency effects
- summon placement
- sequencing

But adjacency should stay rare at launch.

## Turn Structure

Each turn has six parts.

### 1. Start Phase

Resolve in this order:

1. gain 1 max mana
2. refill current mana
3. draw 1 card
4. ready your Figures
5. resolve start-of-turn effects

### 2. Main Phase

The active player may:

- play Figures
- play `Slow` spells
- play `Burst` spells
- play Relics
- use the Hero Power

The active player may take as many legal actions as they want while they have priority and enough resources.

### 3. Attack Phase

The active player may attack with ready Figures one at a time.

For each attack:

1. choose one ready attacker
2. choose its target
3. open a response window
4. resolve combat

After one attack resolves, the active player may:

- declare another attack
- return to main-phase actions if legal
- end the turn

### 4. Response Window

A response window opens:

- after an attack is declared
- after a `Fast` spell is played

During a response window:

- the non-active player gets priority first
- then the active player may respond
- players alternate adding one `Fast` or `Burst` action at a time
- when both players pass in sequence, the stack resolves

To keep the game readable:

- only `Fast` and `Burst` effects may be used here
- Figures and Relics cannot be played during response windows
- Hero Powers are normally `Slow` unless a card explicitly says otherwise

### 5. Combat Resolution

Once both players pass in a combat window:

- all queued `Fast` effects resolve last-in, first-out
- `Burst` effects resolve immediately when played and do not wait
- if the attacker and defender are still legal, combat damage resolves

### 6. End Phase

At end of turn:

- resolve end-of-turn effects
- convert unused mana into Ritual Mana up to the cap
- clear temporary end-of-turn effects

## Timing Rules

Mythic Clash v1 uses only three speed bands.

### Slow

`Slow` cards may be played:

- only on your own turn
- only when no response window is open
- only outside active combat resolution

Typical `Slow` cards:

- unit summons
- large draw spells
- board clears
- long-term setup cards

### Fast

`Fast` cards may be played:

- during your turn
- during response windows
- during combat windows

Typical `Fast` cards:

- combat tricks
- spot removal
- protection
- interruptive tempo plays

### Burst

`Burst` cards:

- resolve immediately
- do not create a response opportunity by themselves
- still require you to have priority

Typical `Burst` cards:

- small buffs
- card filtering
- self-contained setup effects

## Combat Rules

## Basic Combat

Each ready Figure may attack once each turn.

A Figure can attack only if:

- it is in play
- it is ready
- it has attack greater than 0
- it has not attacked this turn

Figures normally enter play exhausted.

Exceptions:

- `Rush`
- `Charge`
- other effects that explicitly ready them

## Legal Targets

An attacking Figure may target:

- an enemy Figure
- the enemy Hero

If the defending player controls any `Guard` Figures, attackers must target a `Guard` Figure first unless a card explicitly ignores `Guard`.

## Damage

- combat damage is simultaneous
- damage to Figures persists until healed or removed
- if a Figure's health is reduced to 0 or less, it dies

## Hero Damage

Heroes do not attack in v1.

Heroes may lose Health from:

- direct spell damage
- unblocked Figure attacks
- triggered effects
- fatigue

## Keywords

Mythic Clash v1 evergreen keywords:

- `Guard`: enemy attacks must target this first
- `Ward`: ignore the first source of damage or destruction that would affect this figure
- `Rush`: may attack Figures the turn it enters play
- `Lifesteal`: damage dealt by this Figure also heals your Hero
- `Reborn`: the first time this dies, return it with 1 Health exhausted
- `Overwhelm`: excess combat damage against a Figure hits the enemy Hero
- `Stealth`: cannot be targeted by enemy attacks or targeted enemy effects until it deals damage or uses an activated attack-related effect

Premium launch keywords:

- `Charge`: may attack Figures or the Hero immediately
- `Poisonous`: any combat damage dealt by this Figure to another Figure is lethal
- `Freeze`: a frozen Figure does not ready during its controller's next start phase

## Hero Powers

Hero Powers are:

- once per turn
- cost 2 mana unless the Hero says otherwise
- `Slow` by default

Launch hero power template library:

- `War Spark`: deal 1 damage to any enemy
- `Sacred Blessing`: give a friendly Figure +1/+1 this turn or permanently if the template is balanced that way
- `Living Water`: restore 2 Health to your Hero or a friendly Figure
- `Stone Resolve`: gain 2 Armor

Not every Hero needs a unique power at launch.

It is acceptable for Heroes to map to a small shared power library first.

## Relic Rules

Relics are where a lot of strategic identity can live without making every Figure text box huge.

Relic rules:

- max 2 per player in play
- Relics do not attack
- Relics do not take combat damage
- if a Relic slot is full, you cannot play another Relic unless a card says replace or destroy

Relics should mostly do one of these jobs:

- support a tribe or domain
- bank value over time
- create build-around identity
- offer a narrow activated utility tool

Relics should not:

- repeatedly create free cards with no constraint
- fully lock out combat
- create excessive hidden information

## Match Structure

## Ladder

Ladder uses:

- best-of-one
- no sideboarding during the match
- same exact rules engine as tournament play

## Tournament

Tournament uses:

- best-of-three
- 24-card main deck
- up to 6-card sideboard

After game 1:

- each player may swap any number of cards between main deck and sideboard
- the main deck must still be exactly 24 cards

After each game in a match:

- the loser of the previous game chooses to play first or second

This is a clean, skillful adaptation rule and is worth keeping.

## Concessions and Timers

Players may concede at any time.

Recommended digital timer target:

- 75 seconds base turn time
- plus a small reserve bank that refills slowly

The timer should be visible.

The goal is:

- enough time for meaningful planning
- not enough time for abuse

Required companion UX:

- visible timer
- visible priority marker
- visible response-window marker
- clear attack-readiness indicator
- clean action log

## Exact Content The Game Still Needs

This is the practical design gap between "engine prototype" and "competitive game."

## 1. We absolutely need general support cards

Yes.

The game cannot rely only on mythological figures plus a few generated spells.

Without a real support layer:

- decks become repetitive
- figures must carry too many design jobs at once
- the game becomes over-dependent on raw stat lines
- faction identity gets flattened into "big creature with text"

Mythic Clash needs a `Neutral Core` package.

## Neutral Core package

Needed at launch:

- early curve filler cards
- narrow removal
- healing / stabilization
- card draw / filtering
- anti-wide tools
- anti-big-threat tools
- relic interaction
- token generation
- one or two clean finishers

Recommended size:

- 24 to 36 neutral support cards

## 2. We need faction-specific non-creature cards

Yes, but not in the most expensive possible way.

The project should not start by hand-authoring 8 unique support cards for all 100 cultures. That would explode production cost and balancing overhead.

Instead, use a three-layer support model.

### Layer A: Neutral Core cards

Usable by everyone.

Purpose:

- keep decks functional
- cover baseline gameplay needs

### Layer B: Domain support cards

These are not tied to one exact culture, but to mythic themes already present in the data.

Examples of domain groups:

- War
- Storm
- Sun
- Moon
- Death
- Underworld
- Sea
- Sky
- Trickery
- Wisdom
- Fertility
- Beasts

Recommended structure:

- 2 to 4 support cards per domain group
- mix of Spells and Relics

Why this is strong:

- scalable across 100 cultures
- preserves myth flavor
- gives decks real support identities
- avoids the production nightmare of 100 tiny bespoke spell suites

### Layer C: Signature culture cards

These are truly culture-specific extra cards.

Recommended at first:

- 1 signature Relic or Spell per culture, not a whole package

Purpose:

- preserve distinctive flavor
- create a headline deckbuilding reason to visit a culture

This should come after Core and Domain support exist.

## 3. We need Heroes as a real card layer

Right now the prototype effectively infers hero powers from deck themes.

That is fine for testing, but not for a real game.

We need:

- explicit Hero cards
- clear hero power assignment
- deckbuilding legality anchored to those Heroes

Minimum viable hero layer:

- 1 Hero per culture
- Hero uses one of the shared power templates
- Hero has a culture, a title, and maybe one passive hook at most

## 4. We need better card-role coverage

Each legal competitive culture pairing must be able to build:

- an early game
- a midgame
- a finisher plan
- interaction
- stabilization
- a reason to pick that pairing over another

If a culture has 20 fun figures but no clean removal or no tempo tools, it may still be unplayable competitively.

## 5. We need explicit card text templates

The current heuristic figure conversion is a good prototype seam, but it is not enough for competitive integrity.

We need explicit templates for:

- summon effects
- healing
- buffs
- conditional removal
- random restricted generation
- death triggers
- relic activation

## Recommended Launch Card Ecosystem

Minimum viable competitive launch target:

- 100 Heroes
- 2,000 Figures
- 24 to 36 Neutral Core support cards
- 24 to 48 Domain support cards
- optional first-wave signature cards for spotlight cultures

That means the real missing content is not "more creatures."

It is:

- Heroes
- a neutral core
- domain support
- exact templating

## Exact Recommendation On Extra Non-Creature Cards

Yes, Mythic Clash should add extra faction-specific non-creature cards.

But the best rollout is:

1. Neutral Core first
2. Domain support second
3. Signature culture support third

That gives the game:

- enough general structure to function
- enough thematic support to feel mythic
- enough control on scope to stay buildable

## What To Build Next

If we follow this ruleset, the next concrete implementation tasks are:

1. Add explicit Hero cards and deck legality rules.
2. Add mulligan to the engine.
3. Replace hard turn-limit win logic with fatigue.
4. Reduce board cap from 7 to 5.
5. Add `Slow` / `Fast` / `Burst` timing support.
6. Add Relics as a supported card type.
7. Build the first Neutral Core support set.
8. Build the first Domain support set.
9. Convert figure heuristics into explicit card templates where possible.

## Companion Docs

- `docs/card-system-v1.md` defines the extensible card architecture.
- `docs/support-card-set-v1.md` defines the first real support-card wave.
- `docs/culture-identity-matrix.md` defines readable culture gameplay families and signature-character rules.
- `docs/multiplayer-compatibility.md` defines how to preserve future `2v2` and `XvX` options without destabilizing `1v1`.
