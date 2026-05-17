# Culture Rollout Rubric v1

Status: locked translation standard before large-scale culture conversion

This document defines how cultures should be updated into the `v1` Mythic Clash card model.

The goal is simple:

- stop relying on taste alone
- make culture translation repeatable
- keep flavor strong without making gameplay unreadable

This is the document we should follow before converting the full `100` cultures.

## Purpose

The culture rollout process must solve four things at once:

1. preserve the cultural feel
2. produce readable gameplay
3. create decks that curve and function
4. stay consistent enough that `100` cultures can be updated without chaos

This rubric is the bridge between the earlier family-model docs and the practical card-pack files.

## Core Rule

Every culture update must aim for:

- different plan
- same grammar

That means cultures may differ by:

- pressure pattern
- keyword bias
- healing level
- recursion level
- relic reliance
- spell density
- card draw level
- top-end finish pattern

They should not usually differ by:

- private resources
- private timing systems
- private board rules
- custom zones
- hidden faction-only win conditions

## Translation Steps

Each culture must be updated in this order.

## 1. Identity Lock

Before writing cards, define:

- primary gameplay family
- secondary leaning
- signature character
- 3 to 5 play-pattern promises
- 2 to 4 de-emphasized themes

This part must be short and explicit.

Example promise lines:

- wins through tactical board pressure
- stalls one enemy piece, then attacks hard
- uses deaths as value, not pure burn

If this identity cannot be summarized simply, the culture is not ready to convert.

## 2. Roster Triage

Sort the `20` source figures into these buckets:

- `core fit`
- `secondary fit`
- `signature fit`
- `salvageable with rewrite`
- `de-emphasized`

Definitions:

- `core fit`: already supports the primary family well
- `secondary fit`: supports the secondary leaning without muddying the main read
- `signature fit`: memorable card that can hold the limited rule-bending slot
- `salvageable with rewrite`: lore is useful but the current ability text is wrong
- `de-emphasized`: important mythically, but too off-plan for the main culture shell

Every culture should still keep the `20` source figures in the pack.

But only some of them should define the gameplay center.

## 3. Ability Rewrite

Rewrite source abilities into `v1` structured grammar.

Priority order:

1. keep the gameplay role
2. keep the mythic fantasy
3. keep the exact original wording only if it already fits

This is important.

We are not trying to preserve the old generator text.

We are trying to preserve:

- the card's role
- the culture's read
- the faction promise

### Rewrite Rules

- remove five-stat language
- remove alignment-dependent narrow text unless it is very central
- replace position/row language with clean target or tempo language
- replace broad status soup with supported evergreen effects
- convert overlong spectacle text into one or two focused effects

### Preferred v1 effect families

Use these first whenever possible:

- damage
- heal
- draw
- summon token
- grant stats
- grant keyword
- ready
- exhaust
- freeze
- destroy damaged unit
- return to hand
- return from discard
- gain ritual mana

Do not invent a culture-only primitive unless the signature slot truly needs it.

## 3.5 Launch Constraint Check

Before moving from rewrite to curve work, every culture should be checked against the launch competitive constraints.

### Telegraphed lethality check

Ask:

- does this culture usually threaten lethal through board, relic, or known setup?
- is too much of its closing power hiding in generic hand burst?

If the answer is "yes, too much is hidden in hand," revise it.

### Generation and discover check

Ask:

- are generated cards coming from explicit narrow buckets?
- would an opponent broadly understand the range after seeing the effect?

Do not approve:

- full-pool discover as a common pattern
- long nested generation chains
- hidden information debt as identity

### Complexity budget check

Ask:

- do most cards still have one clear job?
- is the culture's depth coming from sequencing and role pressure more than from text volume?

Default expectation:

- most non-signature cards should have one main effect and at most one rider
- signature characters may be deeper, but must still be answerable

### Comeback visibility check

Ask:

- what does this culture do when behind on board?
- what punishes enemy overextension?
- how does it stabilize without hard rubber-band rules?

If the answer is unclear, the pack is not ready.

## 4. Curve and Role Assignment

Every culture must produce a deckable gameplay curve, not just a lore roster.

### Mandatory role coverage

Every culture should contain enough material for:

- early stabilization or pressure
- midgame anchors
- at least one clean closer
- at least some interaction
- at least one weakness

### Minimum practical shape inside the `20` figures

Recommended target:

- `4` to `6` cards that can reasonably serve as early plays
- `6` to `8` midgame stabilizers or pressure cards
- `3` to `5` strong finishers or swing cards
- `2` to `4` interaction-focused figures

These categories overlap.

They are role checks, not hard slots.

### Midgame anchor rule

Do not approve a culture pack if its readable plan exists only in the low curve.

Every rollout-ready culture should have at least:

- `1` real `4` or `5` cost stabilizer or pressure anchor
- `1` visible board swing card in the `4` to `6` cost range
- `1` realistic way to convert tempo or survival into closing pressure

This is the main protection against packs that validate cleanly but still feel too soft once benchmark decks start landing larger threats.

## 5. Support Layer

Every translated culture pack should add:

- `1` Hero
- `3` culture-specific Spells
- `1` culture-specific Relic

That gives us:

- clear identity expression
- enough non-figure support to test real gameplay
- a manageable standard for scale

Do not exceed this in rollout `v1` unless there is a strong reason.

More support variety can come later.

Support cards should also obey two launch rules:

- they should reinforce the family read, not replace it with generic burst
- they should create visible tactical choices more often than surprise-from-hand finishes

## Pack Construction Rubric

Each culture pack should currently contain:

- `1` Hero
- `20` Figures
- `3` Spells
- `1` Relic
- optional tokens if needed

That gives us:

- `24` collectible non-hero cards

This should stay the standard launch translation shape.

## Structural Variance Policy

We do want variety.

We do **not** want random pack structures.

### What should stay consistent

- `20` source figures stay represented
- `3` spells and `1` relic is the default support shape
- every sample deck should still validate under the global deck rules

### What may vary by family

- cheap-figure density
- average curve
- draw access
- removal density
- relic centrality
- top-end count

### Healthy family-level variance targets

`Vanguard`

- usually more `3` and `4` cost figures
- lower spell reliance
- stronger combat buffs

`Tempest`

- usually slightly higher spell density in sample deck
- more reach
- fewer sticky midgame bodies

`Sanctuary`

- more healing
- more guard/ward effects
- steadier midgame

`Gravebound`

- more recursion
- more expendable low bodies
- more death-payoff shape

`Tidebound`

- more exhaust, freeze, and bounce
- tempo-first interaction
- attack follow-through

`Oracle`

- more draw, selection, and setup
- lower raw stat pressure

`Wildhost`

- more token or board-presence density
- more combat snowball patterns

`Trickster`

- more temporary disruption
- less raw body efficiency

This gives us controlled variety instead of flattening everyone into the same exact deck in different costumes.

## Low-End Identity Policy

This is one of the most important decisions in the whole rollout.

### Rule

Do not solve every weak curve by turning iconic myth figures into generic low drops.

### Allowed compression

We may compress some famous figures downward when:

- the gameplay role is still believable
- the card still reads like that character
- the culture needs one or two iconic early anchors

### Not allowed

Do not mass-compress so far that:

- too many legendary names look like filler two-drops
- cultures lose mythic stature
- every deck curve works but feels fake

### Recommended long-term answer

Use a hybrid model:

- keep some compressed iconic cards
- eventually add `4` to `6` lower-profile support figures per culture

Examples:

- hunters
- scouts
- priests
- attendants
- guardians
- local warriors
- temple or civic defenders

That is the healthiest path for both flavor and gameplay.

## Signature Character Policy

Each culture gets one primary signature character slot.

### Signature rules

- strong
- memorable
- slightly more rule-bending
- not the strongest raw-rate card by default
- must still be answerable

### Signature should do one of these

- convert the culture's main plan into a spike
- bend a normal rule slightly
- create a memorable once-per-turn or on-play twist

### Signature should not do these

- create a private minigame
- introduce a faction-only subsystem
- invalidate common counterplay
- require matchup-specific trivia to understand
- become the main source of hidden burst lethality for the whole culture

## Testing Standard

No culture should be considered rollout-ready until it passes all of these.

## Required tests

1. identity review
2. legal deck validation
3. one sample deck build
4. one short written playtest read
5. at least one runtime duel
6. one explicit launch-constraint review covering lethality, generation, complexity, and comeback lines
7. one explicit check that the sample deck contains real `4` to `6` cost anchors instead of only a compressed low curve

## Better standard for stronger confidence

Use this when possible:

1. legal deck validation
2. runtime duel against at least two already translated cultures
3. quick review of whether the deck curve looks fake or natural
4. quick review of whether the support cards really reinforce the family
5. quick review of whether opening turns differ meaningfully from already translated cultures
6. quick review of whether the deck still has visible outs when behind
7. quick review of whether the deck can still contest the game once benchmark opponents reach their first major midgame threat turn

## Rollout Labels

Every culture should be tagged with one of these statuses:

- `assigned`
- `translated`
- `deck_validated`
- `runtime_tested`
- `needs_revision`

This keeps the rollout honest.

## Revision Triggers

A culture should stop and be revised before mass rollout if any of these happen:

- it only becomes playable by extreme curve distortion
- its sample deck feels too much like another culture already translated
- its signature character carries too much of the identity alone
- too many off-plan myths remain equally loud
- the support cards are doing all the identity work while the figures feel generic
- too much of its kill pattern is hidden in generic burst from hand
- its generation or discover effects create too much memory debt
- its ordinary cards are too text-dense to read as a clean culture shell

## Batch Rollout Order

Do not convert `100` cultures alphabetically.

Use staged rollout waves:

### Wave 1

- `6` to `8` cultures from very different families

Goal:

- prove the rubric generalizes

### Wave 2

- `12` to `20` more cultures

Goal:

- test repeatability
- identify family-level drift

### Wave 3

- remaining cultures

Goal:

- mass application after the method is already stable

## Practical Decision

We should now use this rubric for the next culture batch.

If the next `3` to `5` cultures still feel strong under this rubric, then we can begin scaled conversion with much more confidence.
