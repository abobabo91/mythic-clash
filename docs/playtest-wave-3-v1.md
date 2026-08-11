# Wave 3 v1 Playtest Read

Status: third controlled rollout check under the stricter rubric

This wave translated three more cultures into real `v1` packs and ran them through the current benchmark gauntlet.

Cultures covered here:

- `Cherokee`
- `Muisca Colombian`
- `Yanomami`

Related files:

- [scripts/build-wave-3-v1.py](../scripts/build-wave-3-v1.py)
- [data/cards-v1/cherokee-v1.json](../data/cards-v1/cherokee-v1.json)
- [data/decks-v1/cherokee-selu-harvest-storm.json](../data/decks-v1/cherokee-selu-harvest-storm.json)
- [data/cards-v1/muisca-colombian-v1.json](../data/cards-v1/muisca-colombian-v1.json)
- [data/decks-v1/muisca-colombian-bochica-golden-bastion.json](../data/decks-v1/muisca-colombian-bochica-golden-bastion.json)
- [data/cards-v1/yanomami-v1.json](../data/cards-v1/yanomami-v1.json)
- [data/decks-v1/yanomami-omama-spirit-renewal.json](../data/decks-v1/yanomami-omama-spirit-renewal.json)

## Structural Result

All three decks validate as legal `24`-card lists:

- `18` Figures
- `5` Spells
- `1` Relic

Validation summaries:

- `Cherokee`: average cost `3.25`
- `Muisca Colombian`: average cost `3.42`
- `Yanomami`: average cost `3.46`

This wave also proved the batch builder path is holding up:

- `3` new Heroes
- `60` translated source Figures
- `9` support Spells
- `3` Relics
- tokens where needed

## Benchmark Result

Current benchmark gauntlet used here:

- `Ancient Greek` as the primary strength check
- `Haitian Vodou` as the secondary recursion/value check

### Seed `31`

- `Cherokee` vs `Ancient Greek`: Greek won on turn `12`
- `Cherokee` vs `Haitian Vodou`: Cherokee won on turn `17`
- `Muisca Colombian` vs `Ancient Greek`: Muisca won on turn `17`
- `Muisca Colombian` vs `Haitian Vodou`: Muisca won on turn `16`
- `Yanomami` vs `Ancient Greek`: Greek won on turn `12` after the retune
- `Yanomami` vs `Haitian Vodou`: Yanomami won on turn `11` after the retune

### Seed `47`

- `Cherokee` vs `Ancient Greek`: Greek won on turn `13`
- `Cherokee` vs `Haitian Vodou`: Cherokee won on turn `16`
- `Muisca Colombian` vs `Ancient Greek`: Muisca won on turn `13`
- `Muisca Colombian` vs `Haitian Vodou`: Muisca won on turn `15`
- `Yanomami` vs `Ancient Greek`: Greek won on turn `15` after the retune
- `Yanomami` vs `Haitian Vodou`: Yanomami won on turn `16` after the retune

## Important Retune

Wave 3 produced one clear stop-and-think signal.

The first Yanomami version was too explosive because the same `Forest Spirit` token was being created by:

- `Shamanic Gathering`
- `Omama`'s Hero Power
- several figure effects

At `2/2`, that body pushed the deck too far toward snowball openings.

So before locking the wave result, the token was reduced to `1/2`.

That was the right correction:

- Yanomami stopped running over `Ancient Greek`
- it still kept its intended pressure into `Haitian Vodou`
- the culture read stayed intact

This is exactly the kind of correction the rollout gate is supposed to catch.

## Culture Reads

### Cherokee

Cherokee reads well.

It feels like:

- `Wildhost` first
- `Tempest` second

In play that means:

- healing and board glue
- small spirit/token reinforcement
- visible thunder damage to close games

The important thing is that it is understandable on sight.

The main weakness is also clear:

- it can grind and stabilize well enough
- but it still struggles to punch through the best Greek top-end boards

That is not a rules problem. It is a power-band problem.

### Muisca Colombian

Muisca is the cleanest success of the wave.

It feels like:

- `Sanctuary` first
- `Oracle` second

In play it has:

- visible healing
- bounded draw smoothing
- guard and restoration layers
- controlled light-based finish pressure

Most importantly, it wins through stable board turns, not weird loopholes.

This is very close to the kind of faction readability we want at scale.

### Yanomami

Yanomami now reads correctly after the retune.

It feels like:

- `Wildhost` first
- `Gravebound` second

In play it has:

- spirit swarming
- recursive glue
- healing padding
- steady board-led pressure

After the token reduction, it still beats slower grind decks, but it no longer looks like an unfair early rollout outlier.

## Most Useful Design Finding

Wave 3 is the strongest evidence yet that the rollout process itself is improving.

Why:

- the families stayed readable
- the benchmark gauntlet exposed a real balance problem
- the balance problem was fixed with a small, meaningful rules change
- the corrected pack still kept its intended identity

That is exactly the workflow we wanted:

- translate
- test
- stop when something looks wrong
- fix the right thing
- retest before scaling

## Bottom Line

This wave is a success, but not a mass-rollout green light yet.

What is now clearly true:

- `Cherokee` is readable and useful, but still softer into `Ancient Greek`
- `Muisca Colombian` is a strong rollout-ready template
- `Yanomami` needed a retune, and the retuned version now looks healthy

So the current answer is:

- keep using the benchmarked wave rollout model
- do not convert all `100` cultures yet
- continue with the next small batch under the same gate

The best next cultures are now the remaining strong candidates from this lane:

- `Guarani`
- `Mapuche`

Those give us another good check on whether this family/benchmark method continues to hold without forcing a rough-file stress test too early.
