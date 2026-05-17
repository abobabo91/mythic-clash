# Testing Stack v1

Last updated: 2026-05-04

Mythic Clash now uses a two-tier AI testing stack instead of relying on one bot for every job.

## Why

The stronger `benchmark` bot makes better decisions, but it is too slow for full-culture rollout.

It deep-copies the game state for every legal action and scores simulated outcomes. That is useful for high-trust checks, but not for `100`-culture throughput.

## Tiers

### 1. Smoke tier

Use:

- `scripts/run-v1-smoke-gauntlet.py`
- `RolloutPlayer`

Purpose:

- broad rollout screening
- quick deck sanity checks
- cheap matchup sweeps
- early detection of obviously broken or nonfunctional packs

Properties:

- much faster than the benchmark bot
- uses immediate action scoring, not full per-action simulation
- good enough for "does this pack basically work?"
- not strong enough to trust for final balance calls by itself

Recommended use:

- every newly translated culture
- batch rollout waves
- first pass after tuning a deck list

### 2. Benchmark tier

Use:

- `scripts/run-v1-benchmark-gauntlet.py --player-kind benchmark`
- `BenchmarkPlayer`

Purpose:

- stronger matchup validation
- final checks on suspicious or promising packs
- verifying whether a smoke result still holds under a better controller

Properties:

- much slower
- state-copy and simulation heavy
- better at avoiding obvious throwaways and bad sequencing
- still not "true AI", but strong enough for higher-confidence balance reads

Recommended use:

- spotlight cultures
- packs that looked too strong or too weak in smoke tests
- pre-rollout gates before mass conversion

### 3. Transcript tier

Use:

- `scripts/run-self-play.py --output ...`

Purpose:

- inspect weird lines
- confirm a loss came from deck weakness instead of bot stupidity
- spot no-op plays, trapped mana, or hidden engine bugs

Recommended use:

- only when a result looks suspicious
- only for a few seeds, not as a bulk method

## Current Recommendation

Use this order:

1. deck validation
2. smoke gauntlet
3. benchmark gauntlet only if the smoke result matters
4. transcript review only if the benchmark still looks odd

This should let us scale culture testing without waiting hours for every rollout batch.
