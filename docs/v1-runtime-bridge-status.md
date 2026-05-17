# v1 Runtime Bridge Status

Last updated: 2026-05-03

This document records the current status of the runtime bridge between the new `CardSpec` culture packs and the playable headless engine.

## What Exists Now

The engine can now:

- load `v1` card packs from `data/cards-v1/`
- load `v1` deck files from `data/decks-v1/`
- preserve explicit Hero cards and Hero Powers
- preserve `Ritual Mana`
- preserve a simple `Relic` row
- use `4 / 5` opening hands
- enforce a `5`-figure board cap
- perform a simple automatic mulligan for self-play
- interpret a focused subset of structured abilities and effects
- run heuristic self-play using translated culture packs

Main code:

- [game/engine.py](/c:/Users/abele/Desktop/github/mythic-clash/game/engine.py:1)
- [scripts/run-self-play.py](/c:/Users/abele/Desktop/github/mythic-clash/scripts/run-self-play.py:1)

## Supported Runtime Pieces

Currently supported well enough for the translated `Ancient Greek` and `Haitian Vodou` packs:

- Figures
- Spells
- Relics
- Hero Powers
- token summoning
- draw
- healing
- direct damage
- simple board-wide damage
- temporary and permanent stat buffs
- keyword grants like `Guard` and `Ward`
- `Reborn`
- simple discard recursion
- bounce to hand
- `Freeze` / `Exhaust` style tempo denial
- targeted destruction
- basic `on_play`, `on_death`, `on_attack_declared`, `on_strike`, and relic passive triggers

## Smoke Test Result

This bridge now runs a real translated-pack duel.

Example command:

```powershell
python scripts\run-self-play.py `
  --pack-a data\cards-v1\ancient-greek-v1.json `
  --deck-a data\decks-v1\ancient-greek-athena-midrange.json `
  --pack-b data\cards-v1\haitian-vodou-v1.json `
  --deck-b data\decks-v1\haitian-vodou-legba-spirits.json `
  --player-a heuristic `
  --player-b heuristic `
  --seed 7 `
  --max-steps 160
```

Observed results from early smoke tests:

- `Ancient Greek` vs `Haitian Vodou` completed successfully across multiple seeds
- `Ancient Greek` vs `Inuit` completed successfully
- `Haitian Vodou` vs `Inuit` completed successfully

This does **not** prove balance.

It does prove that translated packs can now survive a full runtime loop instead of only existing as data files.

## What Is Still Approximate

The bridge is intentionally practical, not complete.

Current limitations include:

- the engine still uses the older simple turn shell in some places
- starting hand and board-cap rules are still closer to the prototype than the full `exact-rules-v1` spec
- some effects are simplified instead of modeled perfectly
- not all effect primitives from `card-system-v1` are implemented yet
- some conditional targeting and timing details are still approximate
- no mulligan yet
- no full `Fast` / `Burst` response windows yet
- relic support exists, but only at the simpler passive-trigger level
- many targeted minion `on_play` effects still use a default target chooser instead of explicit player choice

## What This Means

We have passed an important milestone:

- translated cultures are no longer just documents and JSON
- they can now be loaded into the game loop and played

But we are not done.

The bridge is currently strong enough for:

- faction identity testing
- deck-shape testing
- rough matchup feel
- engine integration work

It is not yet strong enough for:

- serious balance conclusions
- tournament-grade rules validation
- broad automation across all future mechanics

## Best Next Steps

The best follow-up work is:

1. expand effect and condition coverage based on the next translated culture packs
2. bring the core engine shell closer to `exact-rules-v1`
3. add regression tests for Hero Powers, Relics, recursion, temporary buffs, and ritual-mana spending
