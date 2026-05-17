# Culture Rollout Gate

Last updated: 2026-05-03

This document answers one specific question:

Should we update all `100` cultures into the new `v1` model right now?

Current answer:

- **not yet**

The overall direction is working.

The current mass-rollout method is not clean enough yet.

## Why We Should Pause Before All 100

Three translated cultures now exist and survive runtime testing:

- `Ancient Greek`
- `Haitian Vodou`
- `Inuit`

That is a strong proof that the design direction works.

It is **not** yet proof that the current update method is ready to be stamped across all cultures without introducing avoidable problems.

## What Is Working

- cultures can be made readable and distinct without private subsystems
- the shared rules grammar is holding up
- runtime self-play works well enough for rough faction-feel testing
- primary / secondary family assignment is helping a lot

So the big-picture plan is good.

## What Still Needs To Change Before Full Rollout

## 1. The culture-update method is still too artisanal

Right now, each translated culture still needs a lot of judgment calls:

- which figures get compressed into lower costs
- which themes get de-emphasized
- which effects get rewritten into which v1 primitives
- which support cards best express the culture

That is fine for `3` cultures.

It is dangerous for `100`.

Before mass rollout, we need a more explicit translation rubric.

## 2. The current translated decks are a little too structurally similar

The three sample decks all currently land at:

- `18` Figures
- `5` Spells
- `1` Relic

That is valid and useful for testing.

But if all `100` cultures land in nearly the same structure with the same low-curve compression style, we risk making the game readable at the cost of flattening faction personality.

We need to decide:

- how much structural variance is healthy
- which families should naturally prefer `2` relics, heavier top-end, or more spell density
- how much family-level curve identity should differ

## 3. Low-end role support is still partly fake-compressed

The translated packs work because several famous myth characters were pushed down into clear `2` and `3` cost gameplay roles.

That is fine as a stopgap.

But if we mass-apply that blindly, we may get:

- too many legendary or iconic figures acting like generic low drops
- cultures that play smoothly but feel less mythically believable

Before full rollout, we should decide whether to:

- keep doing that
- add `4` to `6` lower-profile support figures per culture
- or use a hybrid approach

## 4. Runtime testing is useful, but still approximate

The current bridge is good enough for rough matchup feel.

It is not yet precise enough to certify all culture updates as final gameplay.

Important current limitation:

- many targeted minion `on_play` abilities still use a default target chooser instead of explicit player choice

That means the tests are good for:

- readability
- curve sanity
- broad pressure profile

but weaker for:

- exact power evaluation
- subtle tactical card quality

## 5. More than half the source dataset still wants manual rules rewriting

From the compatibility report:

- only `752 / 2000` figures currently fit a simple ability blueprint cleanly
- `1248 / 2000` still need manual redesign or broader primitive support

So a mass conversion today would not be:

- one clean automated pass

It would be:

- a very large partially manual rewrite process

That is exactly where we should standardize the method first.

## What I Think We Should Lock Before Updating All 100

## A. A translation rubric

Each culture translation should explicitly define:

- primary family
- secondary leaning
- signature character
- 3 to 5 core play-pattern promises
- de-emphasized themes
- allowed rule-bending space

## B. A pack-construction rubric

Each culture pack should follow a consistent but not identical structure.

Example questions to lock:

- how many cheap figures should each family usually have
- which families are allowed `2` relics more often
- which families get stronger card draw
- which families should lean more top-heavy

## C. A low-end identity policy

We need one clear answer to this:

How do we make curves work without making cultures feel fake?

The likely answer is:

- keep some compressed iconic cards
- but eventually add a small number of lower-profile support figures per culture

## D. A runtime test policy

Before updating all `100`, we should decide what counts as “tested enough.”

For example:

- legal deck validation
- at least one runtime duel
- at least one deck-shape review
- one short written playtest read

## Recommended Next Move

Do **not** update all `100` cultures yet.

Instead:

1. use [docs/culture-rollout-rubric-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/culture-rollout-rubric-v1.md:1) as the working translation standard
2. use [docs/culture-translation-checklist.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/culture-translation-checklist.md:1) for each pack
3. translate and test `3` to `5` more cultures from different families
4. if those still feel good, then batch-convert the rest much more confidently

## Practical Decision

Current recommendation:

- **stop before the full 100-culture rollout**

Reason:

- the direction is right
- the scaling method still needs one more design pass

That is a good place to pause, because fixing the method now will save a lot of cleanup later.
