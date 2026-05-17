# Wave 2 v1 Playtest Read

Status: second multi-culture rollout check under the stricter rubric

This document records the next translation wave after the rules and rollout rubric were tightened around:

- telegraphed lethality
- restricted generation / discover
- visible comeback lines
- launch card complexity budget

Cultures covered here:

- `Zoroastrian Persian`
- `Japanese Shinto`
- `Maori`

Related files:

- [scripts/build-wave-2-v1.py](/c:/Users/abele/Desktop/github/mythic-clash/scripts/build-wave-2-v1.py:1)
- [data/cards-v1/zoroastrian-persian-v1.json](/c:/Users/abele/Desktop/github/mythic-clash/data/cards-v1/zoroastrian-persian-v1.json:1)
- [data/decks-v1/zoroastrian-persian-ahura-bastion.json](/c:/Users/abele/Desktop/github/mythic-clash/data/decks-v1/zoroastrian-persian-ahura-bastion.json:1)
- [data/cards-v1/japanese-shinto-v1.json](/c:/Users/abele/Desktop/github/mythic-clash/data/cards-v1/japanese-shinto-v1.json:1)
- [data/decks-v1/japanese-shinto-amaterasu-tempo.json](/c:/Users/abele/Desktop/github/mythic-clash/data/decks-v1/japanese-shinto-amaterasu-tempo.json:1)
- [data/cards-v1/maori-v1.json](/c:/Users/abele/Desktop/github/mythic-clash/data/cards-v1/maori-v1.json:1)
- [data/decks-v1/maori-maui-tidal-growth.json](/c:/Users/abele/Desktop/github/mythic-clash/data/decks-v1/maori-maui-tidal-growth.json:1)

## Structural Result

All three new sample decks validate as legal `24`-card lists:

- `18` Figures
- `5` Spells
- `1` Relic

Validation summaries:

- `Zoroastrian Persian`: average cost `2.79`
- `Japanese Shinto`: average cost `3.38` after the retune
- `Maori`: average cost `3.42` after the retune

That matters because the stricter rubric still translated cleanly into:

- a Hero
- `20` represented source Figures
- `3` Spells
- `1` Relic
- optional tokens where needed

So the new method is structurally working.

## Runtime Result

### Initial bridge result

I ran six bridge matches on seed `31`:

- `Zoroastrian Persian` vs `Ancient Greek`: Greek won on turn `20`
- `Zoroastrian Persian` vs `Haitian Vodou`: Zoroastrian Persian won on turn `16`
- `Japanese Shinto` vs `Ancient Greek`: Greek won on turn `10`
- `Japanese Shinto` vs `Inuit`: Inuit won on turn `10`
- `Maori` vs `Ancient Greek`: Greek won on turn `10`
- `Maori` vs `Haitian Vodou`: Vodou won on turn `15`

That gave the first good warning:

- identity readability was holding
- pack strength was not

So I retuned `Japanese Shinto` and `Maori` to carry more real `4` to `5` cost anchors and more visible closing pressure.

### Retuned bridge result

I rebuilt the wave, revalidated the decks, and reran the key benchmark matchups.

Seed `31`:

- `Zoroastrian Persian` vs `Ancient Greek`: Greek won on turn `20`
- `Zoroastrian Persian` vs `Haitian Vodou`: Zoroastrian Persian won on turn `16`
- `Japanese Shinto` vs `Ancient Greek`: Greek won on turn `12`
- `Japanese Shinto` vs `Inuit`: Japanese Shinto won on turn `11`
- `Maori` vs `Ancient Greek`: Greek won on turn `11`
- `Maori` vs `Haitian Vodou`: Maori won on turn `16`

Extra seed `47` on the two previously softer packs:

- `Japanese Shinto` vs `Ancient Greek`: Greek won on turn `15`
- `Japanese Shinto` vs `Inuit`: Japanese Shinto won on turn `12`
- `Maori` vs `Ancient Greek`: Maori won on turn `8`
- `Maori` vs `Haitian Vodou`: Maori won on turn `9`

That is a real improvement, not just decklist cosmetics.

## Culture Reads

### Zoroastrian Persian

This is the cleanest success of the wave.

It reads the way we wanted:

- `Sanctuary` first
- `Vanguard` second

In play it feels like:

- durable healing and warding
- board correction
- slow but readable stabilization
- righteous pressure once it turns the corner

Most importantly, it does not win by hidden burst.

It survives, cleans up, then closes through visible board presence and fatigue pressure.

### Japanese Shinto

The retuned identity reads correctly and now has a real playable shell.

The culture does feel like:

- `Tempest` first
- `Tidebound` second

You can see:

- freeze windows
- elemental tempo
- token-based follow-through
- a small purification layer

The important change is that it now converts those tools into wins against `Inuit` instead of only spending cards cleanly and falling behind anyway.

The remaining issue is matchup ceiling.

Against `Ancient Greek`, the deck still feels a little too honest:

- it can answer some things
- it can pressure some things
- but it still struggles to overpower the best benchmark midgame threats once Greek turns the corner

### Maori

Maori now reads correctly and closes games much better than the first pass.

The culture does feel like:

- `Tidebound` first
- `Wildhost` second

You can see:

- bounce and exhaust
- small token support
- growth and recovery
- sea-led tempo pressure

The retuned list now does a much better job turning those tools into visible pressure.

That shows up clearly in the retest:

- it now beats `Haitian Vodou` on both tested seeds
- it can produce a fast board-led kill against `Ancient Greek`

The remaining caution is consistency.

Maori looks much healthier now, but some of its best wins still come from drawing its stronger tempo-to-pressure curve in the right order.

## Most Useful Design Finding

This wave gives a much better answer to the rollout question than the first pass did.

The answer is:

- the translation rubric is good enough to keep using
- the midgame-anchor retune rule was the right correction
- the game is still **not** yet ready for a blind all-`100` rollout

Why:

- identity readability is holding up
- structural translation is holding up
- but balance and pack-shape tuning are not stable enough yet

The biggest remaining issue is not faction confusion.

It is benchmark spread.

More specifically:

- the softer cultures are no longer just collapsing
- but `Ancient Greek` still looks like the pack other cultures must clear to prove the rollout is safe

## What This Suggests We Should Change

Before the full rollout, we should keep the stronger rubric and tighten one more thing:

### 1. Benchmark testing requirement

Every rollout-ready culture should be checked not only for identity and legality, but also for how it performs into at least one strong benchmark pack.

Right now that benchmark is clearly `Ancient Greek`.

If a new culture loses while still feeling readable, that is not enough.

We now need to ask:

- does it have a real midgame anchor
- can it convert stabilization into pressure
- can it fight through a proven top-end board deck without only relying on high-rolls

### 2. Low-end identity without over-compression

The wave also confirms a continuing tension:

- we need enough `2` and `3` cost cards to make decks functional
- but too much compression flattens cultures into similar low-curve shells

So the right answer is still:

- keep using some compression now
- but plan to add more lower-profile culture cards later

## Bottom Line

This wave was worth doing.

It proves the stricter rubric generalizes across three more families, and the retune improved the two softer decks in a meaningful way:

- `Sanctuary`
- `Tempest`
- `Wildhost`-adjacent play

The updated stop signal is more precise now:

- do not mass-convert all `100` cultures yet
- keep translating small batches under the stronger rubric
- treat `Ancient Greek` as the current benchmark pack until something else consistently proves stronger

The right next step is to translate the next small batch under this standard and keep checking whether new cultures feel both:

- readable on sight
- sturdy enough to survive contact with the current benchmark packs
