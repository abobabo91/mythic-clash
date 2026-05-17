# Culture Testing Status

Last updated: 2026-05-04

## Coverage Snapshot

- `100 / 100` cultures have been compatibility-checked against the new `CardSpec` translation layer.
- `100 / 100` cultures now have a real `v1` pack in [data/cards-v1](/c:/Users/abele/Desktop/github/mythic-clash/data/cards-v1:1).
- `100 / 100` cultures now have a legal `24`-card sample deck in [data/decks-v1](/c:/Users/abele/Desktop/github/mythic-clash/data/decks-v1:1).
- `100 / 100` cultures now have rollout-tier gameplay testing through the fast smoke gauntlet.
- the remaining gap is no longer translation coverage; it is competitive balance and deeper engine/testing work

## What "Tested" Means Now

There are still different levels of testing in the repo:

- `compatibility-tested`: figure data was checked against the structured card schema
- `rollout-tested`: the culture has a `v1` pack, legal deck, and passed the fast smoke gauntlet
- `spotlight-tested`: the culture also received a curated write-up or extra benchmark attention

All `100` cultures are now at least rollout-tested.

## Spotlight Cultures

These `35` cultures were translated in curated waves before the bulk pass and have wave notes or dedicated playtest docs:

- `ancient-greek`
- `haitian-vodou`
- `inuit`
- `zoroastrian-persian`
- `japanese-shinto`
- `maori`
- `cherokee`
- `muisca-colombian`
- `yanomami`
- `guarani`
- `mapuche`
- `taino-caribbean`
- `candomble-afro-brazilian`
- `apache`
- `navajo-dine`
- `hopi`
- `toltec`
- `haida`
- `olmec`
- `zapotec`
- `inca-andean`
- `iroquois-haudenosaunee`
- `assyrian`
- `ancient-chinese`
- `slavic`
- `ancient-egyptian`
- `norse-viking`
- `roman`
- `celtic-irish`
- `maya`
- `yazidi`
- `taiwanese-aboriginal`
- `georgian-nart`
- `arabian-pre-islamic`
- `thai-buddhist`

Key references:

- [docs/playtest-ancient-greek-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-ancient-greek-v1.md:1)
- [docs/playtest-haitian-vodou-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-haitian-vodou-v1.md:1)
- [docs/playtest-inuit-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-inuit-v1.md:1)
- [docs/playtest-wave-2-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-2-v1.md:1)
- [docs/playtest-wave-3-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-3-v1.md:1)
- [docs/playtest-wave-4-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-4-v1.md:1)
- [docs/playtest-wave-5-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-5-v1.md:1)
- [docs/playtest-wave-6-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-6-v1.md:1)
- [docs/playtest-wave-7-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-7-v1.md:1)
- [docs/playtest-wave-8-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-8-v1.md:1)
- [docs/playtest-wave-9-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-9-v1.md:1)
- [docs/playtest-wave-10-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-10-v1.md:1)
- [docs/playtest-wave-11-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-wave-11-v1.md:1)

## Bulk Rollout Cultures

The remaining `65` cultures were converted in one reproducible bulk pass and then validated plus smoke-tested:

- [docs/playtest-bulk-rollout-v1.md](/c:/Users/abele/Desktop/github/mythic-clash/docs/playtest-bulk-rollout-v1.md:1)
- [data/benchmarks/bulk-rollout-build-summary.json](/c:/Users/abele/Desktop/github/mythic-clash/data/benchmarks/bulk-rollout-build-summary.json:1)
- [data/benchmarks/bulk-rollout-test-report.json](/c:/Users/abele/Desktop/github/mythic-clash/data/benchmarks/bulk-rollout-test-report.json:1)
- [data/benchmarks/bulk-rollout-test-report-with-greek-gate.json](/c:/Users/abele/Desktop/github/mythic-clash/data/benchmarks/bulk-rollout-test-report-with-greek-gate.json:1)

Bulk rollout headline:

- `65 / 65` validated
- `65 / 65` passed rollout smoke
- no remaining validation failures
- no remaining broad-field collapse cultures
- `16` cultures are still hard Greek-soft and should be first in the next pressure-tuning pass

## Main Remaining Risk

The primary blocker is no longer legacy card translation.

The primary blocker now is matchup pressure tuning, especially against `Ancient Greek` as the current benchmark aggression gate.

That means the next project work should focus on:

- retuning the Greek-soft cultures from the bulk report
- checking whether `Ancient Greek` itself is slightly overtuned
- improving benchmark telemetry and regression tooling
- moving deeper into engine fidelity and UI work

## Practical Meaning

Mythic Clash is now in a different phase from where it started:

- the myth dataset is complete
- the `v1` culture card layer is complete across all `100` cultures
- the rollout testing layer is in place and reusable
- the next real work is competitive tuning and engine/product depth, not coverage generation
