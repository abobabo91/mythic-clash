# Inuit v1 Playtest Read

Status: third full culture translation pass

This document records what happened when `Inuit` was translated into the new `v1` card schema as a real playable culture pack.

Related files:

- [data/cards-v1/inuit-v1.json](/c:/Users/abele/Desktop/github/mythic-clash/data/cards-v1/inuit-v1.json:1)
- [data/decks-v1/inuit-sedna-tidehunt.json](/c:/Users/abele/Desktop/github/mythic-clash/data/decks-v1/inuit-sedna-tidehunt.json:1)
- [scripts/build-inuit-v1.py](/c:/Users/abele/Desktop/github/mythic-clash/scripts/build-inuit-v1.py:1)
- [scripts/validate-v1-deck.py](/c:/Users/abele/Desktop/github/mythic-clash/scripts/validate-v1-deck.py:1)

## What Was Tested

The pack includes:

- `1` Hero
- `20` translated Figures based on the current Inuit roster
- `4` culture-specific support cards

The sample mono-culture deck validates under the current `v1` rules:

- `24` main-deck cards
- `18` Figures
- `5` Spells
- `1` Relic
- average cost `2.79`

Mana curve:

- `2` cost: `9`
- `3` cost: `13`
- `5` cost: `2`

## What Feels Good

- The culture reads clearly as `Tidebound` first and `Vanguard` second.
- The core loop is very readable:
  - stall or bounce one enemy piece
  - land a strong attack
  - keep pressure moving
- `Sedna`, `Iceflow Ambush`, `Kiviuq`, and `Harpoon Rack` all reinforce the same faction idea.
- The faction feels different from both `Ancient Greek` and `Haitian Vodou` without needing a strange private subsystem.

## Matchup Feel

`Inuit` feels like:

- tempo denial
- clean attack windows
- bounce and exhaust pressure
- efficient hunting bodies

That is a good sign because it is not just:

- Greek with water flavor

and not:

- Vodou without recursion

It has its own clear tactical read.

## What Needed Tightening

- The raw roster again skewed expensive and had to be compressed into more `2` and `3` cost roles.
- Several original abilities referenced movement, speed, or broader stat tricks that were better translated into cleaner exhaust, bounce, and combat-pressure effects.
- The final pack needed to stay disciplined and not turn every sea/ice myth reference into a new subsystem.

## Cross-Culture Result

This was the first translation pass after the runtime bridge and the tighter `v1` shell changes.

That matters because Inuit did not only validate as JSON.

It also entered real self-play against:

- `Ancient Greek`
- `Haitian Vodou`

and completed matches successfully.

## Current Character List Verdict

The current Inuit roster is a strong fit for the new model.

It already has:

- a clean signature anchor in `Sedna`
- several natural tempo-control figures
- enough hunting/combat figures to support the secondary Vanguard edge

It still benefits from curve shaping, but it is one of the more naturally readable source cultures.

## Conclusion

This translation strengthens the bigger design claim.

The new Mythic Clash direction can now support at least three clearly different cultures that still feel understandable:

- `Ancient Greek`
- `Haitian Vodou`
- `Inuit`
