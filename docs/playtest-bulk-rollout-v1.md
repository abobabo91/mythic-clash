# Bulk Rollout v1

Last updated: 2026-05-04

This report covers the remaining `65` cultures that were converted after the first `35` spotlight cultures were already translated in curated waves.

Primary automation:

- [scripts/run-v1-bulk-rollout.py](/c:/Users/abele/Desktop/github/mythic-clash/scripts/run-v1-bulk-rollout.py:1)
- [data/benchmarks/bulk-rollout-build-summary.json](/c:/Users/abele/Desktop/github/mythic-clash/data/benchmarks/bulk-rollout-build-summary.json:1)
- [data/benchmarks/bulk-rollout-test-report.json](/c:/Users/abele/Desktop/github/mythic-clash/data/benchmarks/bulk-rollout-test-report.json:1)
- [data/benchmarks/bulk-rollout-test-report-with-greek-gate.json](/c:/Users/abele/Desktop/github/mythic-clash/data/benchmarks/bulk-rollout-test-report-with-greek-gate.json:1)

## Coverage

- `65 / 65` bulk cultures exported to real `v1` packs
- `65 / 65` bulk cultures validated as legal `24`-card decks
- `65 / 65` bulk cultures passed the rollout smoke gauntlet
- `65 / 65` bulk cultures also received a both-seat `Ancient Greek` gate check

The only direct deck retune needed during the bulk pass was `Etruscan`, which improved from a failing `1-5` smoke shell to a healthy `4-2` shell after shifting out of clunky recursion and into a smoother low-end midrange plan.

## Broad-field smoke results

Across `Ancient Greek`, `Haitian Vodou`, and `Inuit` with the fast rollout bot:

- `12` cultures finished `6-0`
- `25` cultures finished `5-1`
- `18` cultures finished `4-2`
- `6` cultures finished `3-3`
- `4` cultures finished `2-4`

This is strong enough to say the bulk rollout produced playable, readable factions instead of broken exports or unusable shells.

## Greek gate results

The both-seat `Ancient Greek` gate is still the harder competitive signal.

- `2` cultures finished `4-0`
- `3` cultures finished `3-1`
- `15` cultures finished `2-2`
- `29` cultures finished `1-3`
- `16` cultures finished `0-4`

That means the rollout is complete, but the pressure-balance phase is not.

## Strongest Greek-gate performers

These were the clear standouts from the bulk group:

- `hittite` at `4-0`
- `sumerian` at `4-0`
- `lao` at `3-1`
- `yoruba` at `3-1`
- `zulu` at `3-1`

These are good candidates for future benchmark or showcase decks once deeper tuning starts.

## Hard Greek-soft cultures

These finished `0-4` in the both-seat `Ancient Greek` gate and should be first in the next pressure-tuning pass:

- `akkadian`
- `aztec-mexica`
- `baltic-lithuanian`
- `burmese-nat`
- `celtic-welsh`
- `fijian`
- `igbo`
- `indian-buddhist`
- `kazakh`
- `korean`
- `mandaean`
- `melanesian-papuan`
- `samoan`
- `scythian`
- `shaiva-hindu`
- `tibetan-bon`

These are not broken in the general field. They are mostly too draw-sensitive or too soft into fast visible pressure.

## Practical meaning

The culture-update project is no longer blocked on translation coverage.

What is now true:

- all `100` cultures have a `v1` pack
- all `100` cultures have a Hero and support-card shell
- all `100` cultures have a legal sample deck
- all `100` cultures have at least rollout-tier gameplay testing

What is still not true:

- all `100` cultures are pressure-balanced against the main Greek gate
- all `100` cultures have manual written playtest notes
- all `100` cultures have benchmark-tier deep matchup testing

So the next phase should focus much less on data generation and much more on:

- Greek-gate balance passes
- richer benchmark telemetry
- deeper engine fidelity
- UI and playtesting tooling
