# Haitian Vodou v1 Playtest Read

Status: second full culture translation pass

This document records what happened when `Haitian Vodou` was translated into the new `v1` card schema as a real playable culture pack.

Related files:

- [data/cards-v1/haitian-vodou-v1.json](../data/cards-v1/haitian-vodou-v1.json)
- [data/decks-v1/haitian-vodou-legba-spirits.json](../data/decks-v1/haitian-vodou-legba-spirits.json)
- [scripts/build-haitian-vodou-v1.py](../scripts/build-haitian-vodou-v1.py)
- [scripts/validate-v1-deck.py](../scripts/validate-v1-deck.py)

## What Was Tested

The pack includes:

- `1` Hero
- `20` translated Figures based on the current Vodou roster
- `4` culture-specific support cards
- `1` Spirit token

The sample mono-culture deck validates under the current `v1` rules:

- `24` main-deck cards
- `18` Figures
- `5` Spells
- `1` Relic
- average cost `2.83`

Mana curve:

- `2` cost: `10`
- `3` cost: `10`
- `4` cost: `3`
- `6` cost: `1`

## What Feels Good

- The culture reads clearly as `Gravebound` first and `Tidebound` second.
- The play pattern is easy to follow:
  - put small bodies into play
  - trade them off
  - get value from death
  - recycle pressure
  - use a little bounce and exhaust to swing tempo
- `Papa Legba`, `Baron Samedi`, `Funeral Drums`, and `Ghede Procession` all point toward the same faction story.
- The faction feels meaningfully different from `Ancient Greek` while still using the same grammar.

## Why This Matters

This was an important test because Vodou could easily have become too broad or too mystical to read fast.

Instead, the translated pack still feels intuitive:

- you can tell what it is trying to do
- you can see where its value comes from
- you can imagine how to counter it

That is exactly the design target we wanted.

## What Needed Tightening

- The raw roster still wanted some curve compression. Many source figures naturally sat in the `4` to `6` cost range.
- The original generated abilities again had to be rewritten almost card by card into cleaner `v1` text.
- Some source themes, especially broader fire-chaos text, had to be pushed down so the faction did not lose its death-and-threshold identity.

## Comparison To Ancient Greek

`Ancient Greek` feels like:

- combat planning
- protection
- tactical removal
- disciplined pressure

`Haitian Vodou` feels like:

- recurring pressure
- death triggers
- attrition value
- small tempo swings through exhaust and bounce

That is a strong sign.

The two cultures feel different in a real gameplay sense, but a player can still understand both without learning a private rules engine for either one.

## Current Character List Verdict

The current Vodou roster translates better than many cultures because it already has:

- multiple natural spirit/death anchors
- clear threshold and underworld flavor
- enough candidates for low-to-mid curve roles

It still is not perfect as a final launch pool by itself.

Like the Greek pass, it would benefit from a few lower-profile support figures over time, but it is already close to a coherent launch shape.

## Conclusion

This test supports the overall direction.

The new rules language is not only working for war-forward cultures.

It is also working for a death-recursion culture without making the game confusing.
