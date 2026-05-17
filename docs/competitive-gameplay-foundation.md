# Mythic Clash Competitive Gameplay Foundation

Status: locked

Research date: 2026-05-03

This document is a synthesis of official rules and official support material from major card games, plus design recommendations for Mythic Clash. The recommendations below are not copied from one game. They are an inference from what the strongest competitive card games consistently do well.

## Executive Recommendation

Mythic Clash should become a digital-first board battler with:

- one visible mana system
- one hero per player
- one readable board
- tight but meaningful interaction windows
- low hidden complexity
- a small evergreen keyword set
- tournament structure that rewards adaptation

The best target is not "be as complex as Magic" and not "be as explosive as Yu-Gi-Oh." The best target is:

- as readable as Hearthstone
- as adaptive as Runeterra
- as structurally disciplined as Magic tournament play
- as fast to re-queue as Marvel Snap

That gives Mythic Clash the best chance of becoming "easy to learn, hard to master."

## What The Big Games Teach

### Hearthstone

Official Hearthstone positioning still describes the game as "deceptively simple" and says it is easy to get into while offering depth over time. Blizzard also explicitly defends Standard as a fresher, more balanced competitive format, and recent balance notes say they target the speed and prevalence of single-turn blowouts.

What to borrow:

- visible mana that increases automatically
- clean battlefield readability
- limited evergreen keywords
- a rotating core competitive format
- aggressive post-launch balance changes

What not to borrow too far:

- too much direct-face burst from hand
- too many "created by" chains
- too much Charge density

### Magic: The Gathering

Magic's official rules structure shows why it stays competitive for decades:

- deep deck construction rules
- mulligans
- play/draw decisions
- best-of-three match structure
- sideboarding
- precise rules language

What to borrow:

- match structure, not stack complexity
- sideboard adaptation in tournament play
- exact card templating
- explicit timing and targeting vocabulary

What not to borrow:

- a giant universal stack for every casual action
- broad instant-speed permission on too many cards

### Pokemon TCG

Pokemon's official rules show the strength of turn discipline:

- a clear turn skeleton
- one energy attachment per turn
- one active battler plus a capped bench
- redundant win conditions
- opening rules that protect game starts

What to borrow:

- strong setup rules
- mulligan clarity
- simple board caps
- first-turn restrictions when necessary for fairness

What not to borrow:

- a resource system that is too dependent on drawing a separate energy class unless Mythic is designed around it from day one

### Yu-Gi-Oh!

Yu-Gi-Oh! proves that combo depth and sideboarding can sustain a competitive audience, but the official rulebook also shows how quickly complexity grows when the board, timing model, and card text all expand at once.

What to borrow:

- side deck logic for tournament adaptation
- archetype identity
- combo expression for advanced players

What not to borrow:

- huge opening-turn combo trees
- too many summon sub-rules
- too much text density per card
- many simultaneous exception systems

### Legends of Runeterra

Runeterra's official support materials are especially valuable for Mythic Clash because they show a strong middle ground between no interaction and full stack complexity:

- alternating action priority
- banked spell mana
- attack token rhythm
- burst / fast / slow timing bands

What to borrow:

- a very small response model
- banked mana for spells only
- attack windows that create tactical back-and-forth

What not to borrow fully:

- too many timing bands if the rest of the game is still stabilizing

### Marvel Snap

Marvel Snap's official help pages show the value of extremely legible competition:

- clear stakes
- short matches
- simple card presentation
- visible initiative
- retreat systems that reduce feel-bad losses

What to borrow:

- very short decision loops
- visible priority / reveal order
- concession systems that respect player time

What not to borrow literally:

- lane scoring as the main win condition, because Mythic Clash already wants creature combat and hero life totals

## The Core Design Principles Mythic Clash Should Follow

### 1. Simple resource system, deep spending decisions

Players should understand their resources in seconds.

Good:

- gain 1 max mana per turn
- refill mana automatically
- optional banked spell-only mana

Bad:

- separate land/energy draw dependency
- too many discounts
- free actions that bypass mana too often

### 2. Board matters more than hand burst

The most skill-testing and spectatable games reward:

- trading
- sequencing
- timing pressure
- reading removal
- planning around board space

Mythic Clash should be a board-first game. Burn, combo, and inevitability decks can exist, but the main game should still happen on the board.

### 3. Interaction should exist, but in controlled windows

Players need the feeling that they can fight back. But full open-ended instant-speed interaction would make Mythic Clash much harder to parse.

Recommendation:

- no full Magic-style stack
- no responses to everything
- yes to a few defined response windows

### 4. Keywords must stay compact

The evergreen keyword list should stay small enough that a new player can learn it in one session.

Target:

- 8 to 12 evergreen keywords max

### 5. Deckbuilding should create identity before raw greed

The strongest competitive formats do not let every deck take every best card forever.

Mythic Clash should constrain deckbuilding through:

- hero identity
- culture pairing limits
- rarity and uniqueness rules
- rotation / curated format rules

### 6. Competitive structure needs adaptation

For serious play, one-and-done games are not enough. Best-of-three with a sideboard is still the cleanest competitive structure for a board-based card game.

## Competitive Fun Tradeoffs By Rule Family

This section is intentionally blunt. Every rule family creates both upside and risk. "Easy to learn, hard to master" comes from choosing the right tradeoffs, not from maximizing complexity.

### Resource systems

Automatic mana growth

Pros:

- easy to understand
- low setup friction
- fewer non-games from resource screw
- easier to balance early, mid, and late game curves

Cons:

- can make ramp and curve play feel samey if card design is weak
- lowers variance, which means overpowered decks surface faster

Separate resource cards like lands / energy

Pros:

- strong deckbuilding tension
- deep consistency math
- more room for macro-resource strategy

Cons:

- more mulligan dependency
- more "I lost because my deck didn’t function" games
- much harder for new players

Verdict for Mythic Clash:

- do not use a separate resource card class
- use automatic mana growth

### Banked mana

No banked mana

Pros:

- cleaner and faster
- easier for new players to spend efficiently

Cons:

- curve misses feel harsher
- reactive and spell-heavy decks get less texture

Spell-only banked mana

Pros:

- rewards planning
- creates comeback elasticity
- improves control and trick-based decks without opening the whole game up

Cons:

- increases hidden future threat range
- can make cheap reactive cards too efficient if pushed

Verdict for Mythic Clash:

- bank a small amount only
- cap it tightly

### Deck size

Small decks

Pros:

- archetype identity shows up more often
- lower collection burden
- players get to "do their thing" more consistently

Cons:

- repetitive play patterns
- combo consistency can get dangerous quickly
- weaker players get punished harder by strong decklists

Large decks

Pros:

- more variance
- more deckbuilding tension
- lower consistency for degenerate combos

Cons:

- weaker thematic cohesion
- more dead draws
- harder for new players to build functional lists

Verdict for Mythic Clash:

- stay in the medium zone
- do not go tiny unless the whole format is built around very short games

### Copy limits

High copy limits

Pros:

- more consistency
- easier deckbuilding
- clearer archetype identity

Cons:

- more repetitive games
- stronger auto-includes
- combo decks become more reliable

Low copy limits

Pros:

- more card variety
- more mythic uniqueness
- fewer repetitive mirror patterns

Cons:

- weaker players may struggle to build smooth curves
- variance rises if draw/filter tools are weak

Verdict for Mythic Clash:

- keep unique mythic legends at 1 copy
- keep most constructed staples at 2 copies
- do not go to 3 or 4 copies by default

### Board size

Large boards

Pros:

- more combo space
- more token play
- more spectacle

Cons:

- harder combat math
- weaker mobile readability
- higher stall potential

Tight boards

Pros:

- more meaningful slot pressure
- easier threat assessment
- stronger sequencing decisions

Cons:

- go-wide archetypes need careful support
- players may feel constrained if every deck floods units

Verdict for Mythic Clash:

- keep the board tight

### Interaction windows

No interaction on opponent turn

Pros:

- very easy to parse
- fast turns
- good for onboarding

Cons:

- low bluffing depth
- fewer comeback lines
- can feel solitaire when proactive decks are strong

Open instant-speed interaction

Pros:

- huge skill ceiling
- rich bluffing and response play
- strong tournament depth

Cons:

- much steeper learning curve
- long turns
- rules disputes become more common
- harder spectator readability

Defined response windows

Pros:

- preserves counterplay
- more readable than full stack games
- enough depth for combat tricks and key answers

Cons:

- still needs careful UI and rules text
- can frustrate players if windows are inconsistent

Verdict for Mythic Clash:

- use defined response windows
- do not use fully open instant-speed interaction

### Damage model

Damage clears at end of turn

Pros:

- simpler for casual players
- lower punishment for small trading mistakes

Cons:

- less meaningful incremental combat
- reduces board-control skill expression

Persistent damage

Pros:

- rewards efficient trades
- improves removal-light gameplay
- creates more tactical pressure

Cons:

- makes pings and cheap damage much stronger
- can snowball early board edges

Verdict for Mythic Clash:

- keep persistent damage
- balance cheap ping effects carefully

### Hero damage from hand

Low direct face reach

Pros:

- board stays important
- games feel more interactive
- less surprise lethality

Cons:

- pure control mirrors can drag
- slower games need clearer finishers

High direct face reach

Pros:

- dramatic finishes
- rewards counting lethal
- can prevent board stalls

Cons:

- creates non-interactive hand kills
- compresses strategic variety
- makes healing or armor almost mandatory

Verdict for Mythic Clash:

- keep direct hero damage meaningful but limited

### Random generation

Wide-pool random generation

Pros:

- exciting moments
- high novelty
- strong casual appeal

Cons:

- weak strategic planning
- hidden outcome range
- skill gets blurred by pool size

Restricted or discover-style generation

Pros:

- still exciting
- easier to plan around
- supports skillful adaptation

Cons:

- still creates variance
- can become repetitive if the buckets are too small

Verdict for Mythic Clash:

- only use bounded randomness

### Sideboards

No sideboard

Pros:

- easier deck submission
- lower complexity
- faster tournaments

Cons:

- polarized matchups hit harder
- less room for adaptation
- lower depth in serious competition

Small sideboard

Pros:

- meaningful adaptation
- preserves archetype identity
- lower burden than large sideboards

Cons:

- adds tournament-only complexity
- requires stronger card catalog organization

Verdict for Mythic Clash:

- use a small sideboard for competitive best-of-three

### Rotation

No rotation

Pros:

- player collection stays relevant forever
- eternal sandbox appeal

Cons:

- card pool complexity compounds
- new-player entry gets worse
- old staples crowd out new design space

Curated rotation

Pros:

- healthier metagames
- clearer onboarding
- better design freedom

Cons:

- players can resent losing ranked legality
- requires format communication discipline

Verdict for Mythic Clash:

- support both Standard and Eternal eventually

### Timers

Loose or no timers

Pros:

- less stress for new players

Cons:

- stalls tournaments
- enables rope abuse
- hurts spectator experience

Tight, visible timers

Pros:

- improves pace
- supports serious competition
- creates real-time pressure skill

Cons:

- can punish mobile players or complex turns

Verdict for Mythic Clash:

- use visible, reasonable timers
- do not let thinking time become a hidden resource exploit

## What Makes These Games Fun At A Competitive Level

Competitive card games are most fun when players feel that:

- they had real choices on most turns
- the better sequence often wins
- they can improve by study and practice
- matches reward matchup knowledge
- losses teach something clear
- wins feel earned rather than random

The strongest recurring fun generators are:

- strong mulligan decisions
- meaningful mana curve tension
- trade vs face decisions
- reading removal and bluffing around it
- sideboarding
- playing around known ranges
- planning two turns ahead
- pivoting roles between aggressor and defender
- visible comeback lines

The strongest recurring "not fun" generators are:

- non-games
- hidden random pools
- infinite value with no pressure
- giant text walls
- first-player snowballing
- one-turn lethals from nowhere
- matchup polarization that makes sideboarding irrelevant

## Common Competitive Card Game Failure Modes

### Non-games

These are games where one player never really got to play.

Causes:

- bad opening consistency
- too much first-player advantage
- overpowered early tempo snowball
- hard counters that shut off a deck before choices matter

Why they are deadly:

- they make players feel powerless
- they reduce learning value
- they hurt tournament credibility

### Solved openers

If the first three turns are always the same for top decks, the game may look deep while actually becoming stale.

Symptoms:

- same mulligan priorities every match
- same opening sequences every mirror
- too many universal staples

### Excessive matchup polarization

If one deck is 70-30 or 80-20 into too many others, queue luck matters too much.

Symptoms:

- ladder frustration
- tournaments decided more by pairings than play
- sideboards becoming mandatory just to survive

### Value without commitment

When cards create too many free cards, too much free mana, or too much free damage, players stop making real tradeoffs.

Symptoms:

- every deck "just gets more stuff"
- late game turns feel bloated
- card advantage stops being a meaningful metric

### Too much generated information debt

If players cannot track what could have been randomly created, high-level play becomes memory tax rather than strategy.

Symptoms:

- post-game confusion
- hard-to-follow streams
- hidden pools matter more than board state

### One-turn blowouts

These are exactly the kind of play patterns recent Hearthstone balance notes still target.

Symptoms:

- safe life totals are fake
- the board feels optional
- players feel punished for not holding up every answer at all times

### Board stalls

If defending is too easy and finishers are too weak, games bog down.

Symptoms:

- both sides fill the board and stop attacking
- life totals stop moving
- only topdecked sweepers matter

### Rules text ambiguity

If players cannot predict outcomes from reading the card, the game loses competitive trust.

Symptoms:

- "why did that happen?" moments
- judge-call style disputes
- players memorizing exceptions instead of learning systems

### Spectator unreadability

A competitive game also has to be watchable.

Symptoms:

- too many objects on screen
- hidden combat math
- too many simultaneous triggers
- unclear priority windows

### Balance by novelty instead of structure

If each set tries to be exciting by breaking baseline assumptions, the long-term game loses integrity.

Symptoms:

- rules bloat
- permanent power creep
- emergency bans and rewrites too often

## Easy To Get In, Hard To Master Checklist

### Easy to get in means:

- a player understands the win condition immediately
- a player can read the board at a glance
- a player knows what their mana does
- a player can identify legal actions easily
- common keywords are few and intuitive
- first games are not lost to invisible rules

### Hard to master means:

- mulligans matter
- sequencing matters
- combat math matters
- role assessment matters
- matchup knowledge matters
- sideboarding matters
- bluffing and resource banking matter
- deckbuilding has tradeoffs, not just "play all the best cards"

### Warning sign

Many games accidentally become:

- easy to start and shallow to master

or:

- hard to enter and hard to master for the wrong reasons

The sweet spot is not "more mechanics." The sweet spot is "more meaningful decisions per mechanic."

## What Rules Mythic Clash Should Add

- Add a real mulligan system.
- Add a small amount of spell-only banked mana.
- Add a strict response model with only a few timing bands.
- Add a competitive best-of-three format with a small sideboard.
- Add exact card templating standards before card complexity expands.
- Add visible turn timers and a clean action log.
- Add stronger first-player / second-player balance testing.
- Add a curated evergreen core set for competitive play.
- Add archetype support through hero and culture identity.
- Add more narrow answers than universal answers.
- Add more skill-testing combat choices than hand-only burst kills.
- Add telemetry-driven balance review early.

## What Rules Mythic Clash Should Not Add

- Do not add land-style resource cards.
- Do not add fully open instant-speed responses to everything.
- Do not add too many evergreen keywords at launch.
- Do not add many zero-cost cards.
- Do not add cheap Charge cards freely.
- Do not add full-pool random generation as a regular pattern.
- Do not add giant hand-disruption packages early.
- Do not add too many free card creation loops.
- Do not add too many exception-based subtypes before the baseline game is stable.
- Do not add a large board cap just because digital UI can technically fit it.
- Do not add tournament formats before the core rules are stable enough to support them.
- Do not let card text be looser than engine behavior.

## Recommended Mythic Clash Rule Set

## Game Identity

Mythic Clash should be:

- a 1v1 digital mythic battler
- hero-vs-hero
- board-centric
- medium-speed
- low-randomness relative to party card games

Target match length:

- best-of-one ladder game: 8 to 12 minutes
- best-of-three tournament match: 20 to 35 minutes

## Win Condition

Recommended:

- each hero starts at 30 Health
- if a hero reaches 0, that player loses
- if a player must draw from an empty deck, they take escalating fatigue damage instead
- remove the current fixed turn-30 winner rule for serious play

Why:

- fatigue is a cleaner long-game pressure system than a hard arbitrary cutoff
- control mirrors can still end naturally
- tournament clocks should handle match length, not an early in-game sudden ending

## Deck Construction

Recommended competitive deck rules:

- 24-card main deck
- 1 hero
- up to 6-card sideboard for tournament best-of-three
- max 2 copies of non-legendary support cards
- max 1 copy of unique legendary mythic figures
- each deck chooses up to 2 cultures plus neutral support cards

Why 24 cards:

- smaller than Hearthstone's 30 keeps mythic identity cards visible more often
- larger than the current 18 reduces repetitive draw patterns and high consistency blowouts
- still fast enough for a digital game

Why 2 cultures:

- creates deck identity
- prevents "best cards from everywhere" piles
- preserves the mythology theme instead of flattening it

## Opening Hand and Mulligan

Recommended:

- first player draws 4 cards
- second player draws 5 cards
- full once-only mulligan of any number of cards
- second player receives a compensation card similar to `The Coin`

If balance testing shows the second player is still weak:

- either improve the compensation card
- or give the second player one banked ritual mana on turn 1

Do not:

- stack multiple second-player bonuses without data

## Resource System

Recommended:

- start at 1 max mana
- gain 1 max mana each turn, up to 10
- refill to full each turn
- up to 2 unused mana becomes `Ritual Mana`
- Ritual Mana can only be spent on spells or activated hero powers

Why this hybrid system is strong:

- Hearthstone-style clarity keeps the game approachable
- Runeterra-style banked spell mana rewards planning
- control and reactive decks get flexibility without requiring full instant-speed complexity

## Board Structure

Recommended:

- max 5 units per side
- left-to-right order is preserved
- adjacency matters only for a small number of cards

Why reduce from 7 to 5:

- better readability on desktop and mobile
- easier combat math
- less board stall
- each unit slot becomes strategically meaningful

## Turn Structure

Recommended turn flow:

1. Start of turn:
   draw 1 card
   gain 1 max mana
   refill mana
   convert saved Ritual Mana if relevant
   ready units
   resolve start-of-turn effects
2. Main phase:
   play units
   play slow spells
   use hero power
   declare attacks
3. Response window:
   defender may use fast spells / combat tricks
   attacker may answer if they also have a legal fast-speed response
4. Combat resolves
5. Post-combat main phase:
   play remaining cards if legal
6. End step:
   resolve end-of-turn effects
   discard to hand limit if needed

This is more interactive than Hearthstone, but much lighter than Magic.

## Timing Model

Recommended timing bands:

- Unit / Relic / Slow Spell: own turn, main phase only
- Fast Spell: can be used in clearly marked response windows
- Burst Spell: resolves immediately on your action, no response

Do not add more than 3 timing speeds at launch.

This is one of the most important design choices in the whole project. It creates skill without making every casual turn take forever.

## Combat

Recommended:

- units attack enemy units or the enemy hero
- damage to units persists until healed
- combat damage is simultaneous
- defenders with `Guard` must be targeted first
- attacker chooses attack order
- no random target selection in core combat

Recommended keyword rename:

- consider renaming `Taunt` to `Guard` or `Protector` for Mythic Clash flavor
- consider renaming `Divine Shield` to `Ward`

## Card Types

Recommended launch card types:

- Hero: deck-defining leader, starts in play
- Figure: your main unit card type
- Spell: one-shot effects
- Relic: persistent support card with an ongoing effect or activated ability

Why add Relics:

- they fit mythology well
- they let decks express identity without overloading units
- they create slower strategic axes besides minion combat

## Hero Powers

Hero powers should stay simple.

Recommended power level:

- 2 mana
- once per turn
- one line of text

Good hero power jobs:

- stabilize curve
- express deck identity
- prevent dead turns

Bad hero power jobs:

- become the whole deck
- generate endless free value
- create repetitive non-games

## Keywords

Recommended evergreen launch set:

- Guard
- Rush
- Ward
- Lifesteal
- Reborn
- Overwhelm
- Stealth
- Spellshield or Hexproof-like protection, but only if needed

Recommended premium / limited-use keywords:

- Charge
- Poisonous
- Freeze / Stun

Important balance note:

- `Charge` should be rare
- `Poisonous` should be rare
- `Guard` should be common enough to matter, but not so common that every game stalls

## Randomness Policy

Mythic Clash should use bounded randomness only.

Acceptable randomness:

- draw order
- small random missile spreads
- discover / choose-1-of-3 from a tight bucket
- summon from a restricted tribe, domain, or culture bucket

Bad randomness:

- full-pool random generation
- board wipes from weak setup
- random win/loss swings from giant outcomes
- repeated cost reduction into swing turns with no counterplay

Rule of thumb:

- if the likely outcome range is too wide to plan around, it is bad for high-level play

## Removal and Reach

Recommended removal structure:

- cheap damage spells should be narrow
- premium removal should cost tempo
- hard removal should be conditional
- board clears should be expensive and telegraphed

Direct face damage should exist, but not dominate.

If games are routinely decided by:

- hand burn from 20
- charge chains
- repeated zero-cost loops

then the format is moving away from skillful board play.

## Card Text Standards

Mythic Clash needs strict templating.

Every card should clearly express:

- who it targets
- when it can be used
- what zone it affects
- whether the effect is immediate, delayed, or persistent
- whether the effect is random and what its pool is

This is one of Magic's biggest long-term lessons: strong templating is invisible when it works, but critical for competitive trust.

## Ladder vs Tournament Structure

Recommended:

- Ladder: best-of-one
- Tournament / gauntlet: best-of-three with sideboard

Tournament sideboarding rule:

- after game 1, players may swap any number of cards with their 6-card sideboard
- the main deck must return to legal size before each next game

Why:

- ladder stays fast and accessible
- tournament play rewards adaptation and matchup depth

## Rotation and Format Policy

Recommended long-term structure:

- `Standard`: curated modern format, official ranked format
- `Eternal`: all released cards

Also recommended:

- a curated evergreen `Core` package that is refreshed on a regular cadence

This follows a proven pattern from Hearthstone and Magic:

- keep ranked entry manageable
- keep design space healthy
- preserve older cards somewhere

## What Mythic Clash Should Avoid

Do not build the final game around:

- giant combo turns from empty boards
- too many zero-cost cards
- large-scale hand disruption
- universal instant-speed interaction
- text walls as baseline card design
- too many evergreen keywords
- too many summon / transform exceptions
- over-frequent random generation from unrestricted pools

## Recommended Development Order

1. Finalize the competitive rules baseline.
2. Add mulligan, timing, and sideboard support in the engine.
3. Build automated gameplay tests.
4. Run self-play at scale and collect matchup data.
5. Normalize figure-to-card conversion rules.
6. Build the browser UI only after the rules stop shifting every day.

## Bottom Line

The best version of Mythic Clash is not the most complicated version.

The best version is the one where:

- a new player can understand a turn in under a minute
- a strong player can gain edge through sequencing, matchup reads, and sideboarding
- most games are decided on visible information
- the board matters
- randomness spices games instead of rewriting them
- the rules engine is strict enough that players trust it

That points to a competitive Mythic Clash built around:

- simple mana
- compact board states
- low but real interaction
- sideboarded best-of-three competitive play
- careful control of burst damage and high-roll randomness

## Sources

- Hearthstone homepage: https://hearthstone.blizzard.com/en-us
- Hearthstone Standard announcement: https://hearthstone.blizzard.com/en-us/news/19995505
- Hearthstone Core Set announcement: https://hearthstone.blizzard.com/en-us/news/23620129
- Hearthstone 32.2.4 balance notes: https://hearthstone.blizzard.com/en-us/news/24204920/32-2-4-patch-notes/
- Magic rules portal: https://magic.wizards.com/en/rules
- Magic Tournament Rules (effective March 11, 2024): https://media.wizards.com/ContentResources/WPN/MTG_MTR_2024_Mar11_1.pdf
- Pokemon TCG rulebook: https://assets.pokemon.com/assets/cms2/pdf/trading-card-game/rulebook/swsh5_rulebook_en.pdf
- Yu-Gi-Oh! official rulebook v9.01: https://www.yugioh-card.com/ygo_cms/ygo/all/uploads/Rulebook_v9_en.pdf
- Legends of Runeterra Round FAQ: https://support-legendsofruneterra.riotgames.com/hc/en-us/articles/360035562034-Round-FAQ
- Legends of Runeterra Mana FAQ: https://support-legendsofruneterra.riotgames.com/hc/en-us/articles/360035562074-Let-s-Talk-About-Mana
- Legends of Runeterra Card Types: https://support-legendsofruneterra.riotgames.com/hc/en-us/articles/360035562134-Card-Types-and-How-They-Work
- Marvel Snap gameplay help: https://marvelsnap.helpshift.com/hc/en/3-marvel-snap/section/18-gameplay-1768314133/
- Marvel Snap snapping rules: https://marvelsnap.helpshift.com/hc/en/3-marvel-snap/faq/28-what-is-snapping/?p=ios
- Marvel Snap retreat rules: https://marvelsnap.helpshift.com/hc/en/3-marvel-snap/faq/29-what-does-retreating-do/?p=all
- Marvel Snap ranked rules: https://marvelsnap.helpshift.com/hc/en/3-marvel-snap/faq/30-how-do-ranks-work/?p=all
