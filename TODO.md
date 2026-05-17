# Mythic Clash TODO

Last updated: 2026-05-04

## High Priority

- [x] Lock the competitive rules baseline from `docs/competitive-gameplay-foundation.md`.
- [x] Lock the exact implementation target from `docs/exact-rules-v1.md`.
- [x] Lock the extensible card architecture from `docs/card-system-v1.md`.
- [x] Lock the first support-card wave from `docs/support-card-set-v1.md`.
- [x] Lock the culture gameplay family model from `docs/culture-identity-matrix.md`.
- [x] Lock the multiplayer-safe wording and engine constraints from `docs/multiplayer-compatibility.md`.
- [x] Add a proper mulligan step to the engine and self-play script.
- [x] Remove or replace the current hard `turn 30` win rule with a more competitive endgame model.
- [x] Add automated tests for turn flow, combat, deathrattles, reborn, taunt targeting, hero powers, and fatigue.
- [x] Run large-batch self-play and save matchup telemetry so balance work is based on data instead of anecdotes.
- [x] Review the current keyword inference rules so `taunt`, `charge`, `reborn`, and `poisonous` do not overfire from loose text matches.

## Gameplay & Balance

- [ ] Decide the final deck size, copy limits, and sideboard policy for competitive play.
- [ ] Decide whether Mythic Clash should stay fully Hearthstone-like or adopt a small response window / fast-spell layer.
- [x] Add explicit Hero cards and stop inferring deck identity only from selected figures.
- [ ] Assign every culture a primary gameplay family and a secondary leaning.
- [x] Lock the culture-translation rollout rubric before converting all `100` cultures into `v1` packs.
- [ ] Decide the exact name for the special one-per-culture card slot (`Signature Character`, `Icon`, `Paragon`, etc.).
- [ ] Define design limits for signature-character rule bending so they stay memorable but answerable.
- [x] Add Relics as a real card type with board-space and timing rules.
- [ ] Rework generated support spells into a cleaner evergreen base set.
- [ ] Define the first `Neutral Core` support package.
- [ ] Define the first `Domain support` package tied to mythic themes like war, storm, death, sea, and wisdom.
- [ ] Decide whether each culture gets 1 signature support card at launch or only spotlight cultures do.
- [ ] Decide the internal team/player/seat model even if launch remains `1v1` only.
- [ ] Make targeting vocabulary multiplayer-safe before hardcoding more card behaviors.
- [ ] Add a real mulligan compensation model for second player advantage, then measure it.
- [ ] Reduce high-roll blowout patterns from cheap damage spikes and repeated face-race lines.
- [ ] Define a formal burst / lethality budget so most kills are board-led or clearly telegraphed, not from nowhere.
- [ ] Add clearer rarity / role targets so each culture deck has early plays, midgame anchors, and finishers.
- [x] Tighten the culture rollout rubric with a stronger `4` to `6` cost anchor requirement so readable packs do not still end up too soft.
- [x] Define a small benchmark gauntlet for every new translated culture pack so rollout decisions are based on the same matchup checks.
- [ ] Add `4` to `6` lower-profile early-game culture cards per faction so launch decks are not built only from headline mythic names.
- [ ] Decide which keywords are evergreen, which are premium, and which should stay rare.
- [ ] Define a launch card complexity budget so most cards stay single-job and signature cards carry only a limited share of complexity.
- [ ] Add explicit card text templates instead of relying only on broad text-to-effect heuristics.
- [x] Lock how much structural variance between culture packs is healthy so all cultures do not collapse into the same `18 figure / 5 spell / 1 relic` shape.
- [ ] Define pack-level comeback requirements so every culture and family has visible stabilization lines without rubber-band rules.
- [ ] Review whether `Ancient Greek` is slightly overtuned as the pressure gate or whether softer `Oracle` / `Trickster` packs like `Celtic Irish` still need stronger anti-board tools.
- [x] Run a focused Greek-gate retuning pass for the `16` hard Greek-soft cultures from `docs/playtest-bulk-rollout-v1.md`.
- [ ] Decide which `1-3` Greek-gate cultures are acceptable specialists and which still need anti-pressure help.

## Data Pipeline

- [ ] Split raw figure data from derived gameplay card data.
- [x] Create a reproducible export step for normalized cards.
- [x] Add a reusable loader/runtime bridge from `CardSpec` packs into the playable engine layer.
- [ ] Add schema validation for cultures and figures.
- [ ] Add data linting for duplicate IDs, malformed stats, and missing fields.
- [ ] Audit all 2,000 figures for repeated ability text patterns that should become shared mechanics.

## AI & Simulation

- [x] Add transcript logging and structured metrics to self-play runs.
- [x] Add deck matchup batch runners and summary reports.
- [ ] Upgrade `AgenticLLMPlayer` from placeholder to a real planning interface.
- [x] Add a cheaper deterministic benchmark bot so balance checks do not depend only on heuristics.
- [x] Add a faster rollout smoke-test bot so full-culture screening does not depend on the slow benchmark bot.
- [x] Add seed-controlled regression simulations for balance comparisons across patches.

## UX & Product

- [ ] Build the first browser UI shell for hand, board, mana, history, and legal actions.
- [ ] Add a local play/debug interface before full production polish.
- [ ] Add deckbuilder UX around cultures, themes, and hero identity.
- [ ] Add visible priority / response markers, action log, and attack-readiness indicators as core readability features.
- [ ] Surface family/readability tags and short playstyle summaries in the deckbuilder and match intro.
- [ ] Decide whether the first public mode is ladder, sandbox duel, or AI challenge.

## Documentation

- [ ] Keep `README.md` synced with actual project status.
- [ ] Write a concise player-facing rulebook once the competitive baseline is locked.
- [ ] Keep `docs/exact-rules-v1.md` in sync with engine reality once implementation starts.
- [ ] Keep `docs/card-system-v1.md` and `docs/support-card-set-v1.md` synced with future implementation changes.
- [ ] Keep `docs/culture-identity-matrix.md` synced with future hero and signature-card implementation.
- [ ] Keep `docs/multiplayer-compatibility.md` synced with any future targeting or engine-model changes.
- [ ] Sync `docs/knowledge-base-comparison-notes.md` into the main rules docs once the new constraints are accepted.
- [ ] Document the card data schema and card generation rules.
- [ ] Add examples of recommended decks and expected archetypes.
- [ ] Keep translated culture-pack playtest reads, such as `docs/playtest-ancient-greek-v1.md`, synced with the actual data files.
