# Mythic Clash

A browser-based mythological card game featuring figures from 100 cultures across the world.

## Project Status

- `100 / 100` cultures now have `v1` exported packs in [data/cards-v1](/c:/Users/abele/Desktop/github/mythic-clash/data/cards-v1:1)
- `100 / 100` cultures now have legal sample decks in [data/decks-v1](/c:/Users/abele/Desktop/github/mythic-clash/data/decks-v1:1)
- `100 / 100` cultures now have rollout-tier gameplay testing
- `35` cultures also have curated spotlight playtest notes
- the main remaining work is competitive tuning, deeper engine fidelity, and the UI

## Project Phases

- [x] Phase 1 — Cultures dataset (100 cultures)
- [x] Phase 2 — Mythological figures dataset (20 per culture = 2,000 figures)
- [x] Phase 3 — Headless duel prototype & rules
- [~] Phase 4 — Competitive tuning, explicit card export, and expanded support cards
- [ ] Phase 5 — Playable UI
- [ ] Phase 6 — Card artwork

## Planning Docs

- `TODO.md` — current implementation backlog
- `docs/competitive-gameplay-foundation.md` — researched gameplay recommendation for a competitive Mythic Clash format
- `docs/exact-rules-v1.md` — exact target ruleset and missing card-system requirements
- `docs/card-system-v1.md` — extensible card architecture and rules primitives
- `docs/support-card-set-v1.md` — first-wave neutral and domain support card designs
- `docs/culture-identity-matrix.md` — readable culture gameplay families and signature-character framework
- `docs/multiplayer-compatibility.md` — future-proofing for later `2v2` and `XvX` modes
- `docs/culture-dataset-assessment.md` — assessment of how well the current figure pool fits that framework
- `docs/culture-assignment-batch-1.md` — first concrete culture-to-family assignment pass
- `docs/culture-assignment-batch-2.md` — second concrete culture-to-family assignment pass
- `docs/culture-assignment-batch-3.md` — third concrete culture-to-family assignment pass
- `docs/culture-testing-status.md` — current all-cultures rollout status
- `docs/playtest-bulk-rollout-v1.md` — bulk rollout results for the remaining 65 cultures

## Data

- `data/cultures.json` — 100 cultures with region, period, mythology type, themes
- `data/figures/` — 100 culture files, 20 mythological figures each
- `game/` — derives playable card templates, deck lists, and a duel engine from the figure data
- `data/cards-v1/` — explicit exported `v1` card packs for all 100 cultures
- `data/decks-v1/` — legal sample decks for all 100 cultures
- `data/benchmarks/` — smoke-test and benchmark summaries, including the bulk rollout reports

## Cultures Coverage

| Region | Count |
|--------|-------|
| Europe | 13 |
| Africa | 10 |
| Middle East | 10 |
| South Asia | 10 |
| East Asia | 7 |
| Southeast Asia | 7 |
| Central Asia | 6 |
| Oceania | 8 |
| Americas | 22 |
| Caucasus | 3 |
| Caribbean | 4 |
