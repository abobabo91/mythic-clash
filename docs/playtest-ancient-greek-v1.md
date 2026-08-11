# Ancient Greek v1 Playtest Read

Status: first full culture translation pass

This document records what happened when `Ancient Greek` was translated into the new `v1` card schema as a real playable culture pack instead of a loose concept.

Related files:

- [data/cards-v1/ancient-greek-v1.json](../data/cards-v1/ancient-greek-v1.json)
- [data/decks-v1/ancient-greek-athena-midrange.json](../data/decks-v1/ancient-greek-athena-midrange.json)
- [scripts/build-ancient-greek-v1.py](../scripts/build-ancient-greek-v1.py)
- [scripts/validate-v1-deck.py](../scripts/validate-v1-deck.py)

## What Was Tested

The pack includes:

- `1` Hero
- `20` translated Figures based on the current Greek roster
- `4` culture-specific non-figure support cards

The sample mono-culture deck validates under the current `v1` rules:

- `24` main-deck cards
- `18` Figures
- `5` Spells
- `1` Relic
- average cost `3.08`

Mana curve:

- `2` cost: `8`
- `3` cost: `9`
- `4` cost: `5`
- `5` cost: `1`
- `6` cost: `1`

## What Feels Good

- The culture reads clearly as `Vanguard` first and `Oracle` second.
- The core loop is easy to understand: develop a board, protect or ready one key figure, and convert that into favorable trades.
- `Athena Parthenos`, `Athena, Battlefield Sage`, `Phalanx Formation`, and `Aegis of Athena` all pull in the same direction, which makes the culture identity feel intentional rather than scattered.
- The deck has recognizable tactical jobs:
  - cheap tempo pieces
  - combat buffs
  - precision removal
  - a few high-end mythic finishers
- Matchup reads are intuitive. An opponent can quickly tell that this culture is trying to win through board control, combat edges, and selective protection rather than through a private subsystem.

## What Needed Rework

- The original raw Greek ability texts did not carry over directly. They had to be rewritten into the new grammar almost card by card.
- The schema needed one real upgrade during translation: activated abilities needed an explicit `resource_cost`, mainly for Hero Powers.
- Several figures had to be retuned down into `2` and `3` cost roles to make the deck curve feel usable.

This last point matters a lot.

If we preserve the current generated stat-to-cost output too literally, the deck becomes too midrange-heavy and the opening turns feel thin. The translated deck works because some cards were deliberately pushed into clearer early-game jobs.

## Current Character List Verdict

The current named-character list is good enough to build a coherent faction identity.

It is not yet ideal as the entire launch card pool for that culture by itself.

Why:

- myth rosters naturally skew toward famous midgame and lategame characters
- competitive decks still want cleaner low-end plays
- a board-first game with a `14`-Figure minimum is much healthier when cultures have a few true setup figures instead of only famous headline characters

So the answer is:

- yes, the current roster can be translated meaningfully
- no, we should not assume the current named roster alone is the final best shape

## Recommendation

For launch-quality culture packs, we should probably add `4` to `6` lower-profile culture cards per faction over time, such as:

- soldiers
- hunters
- priests
- attendants
- scouts
- civic or temple defenders

That keeps the mythic stars as the face cards while making the gameplay curve smoother and more intuitive.

## Conclusion

This test passed the important part.

The new rules language can support a culture pack that feels readable, competitive, and distinct without becoming hard to parse.

The main remaining pressure is not faction identity.

It is curve support and card-role coverage across the existing character rosters.
