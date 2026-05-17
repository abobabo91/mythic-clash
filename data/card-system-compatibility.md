# Card System Compatibility

## Summary

- Cultures checked: **100**
- Figures checked: **2000**
- Figures whose **body** already translates cleanly: **2000** (100.0%)
- Figures with at least one inferred keyword in the new model: **785** (39.2%)
- Figures with a **simple ability blueprint** that fits the new grammar without extra redesign: **752** (37.6%)
- Figures that still need manual rules rewriting or broader primitive support: **1248** (62.4%)

## What This Means

- The current figure list is compatible with the new card **body** model.
- The current figure list is **not** yet directly compatible with the full structured ability model at a high rate.
- The main migration pain is not stats, rarity, or culture ownership. It is the current broad freeform ability language.

## Top Unsupported Concept Buckets

- `five_stat_system` appears in **913** figure abilities.
- `alignment_subsystem` appears in **87** figure abilities.
- `hidden_info_subsystem` appears in **40** figure abilities.
- `resource_subsystem` appears in **32** figure abilities.
- `non_launch_status_terms` appears in **20** figure abilities.
- `board_geometry_subsystem` appears in **16** figure abilities.
- `special_ability_subsystem` appears in **12** figure abilities.

## Most Repeated Ability Descriptions

- **54**x: Pull one enemy out of position and lower its speed by 3.
- **46**x: All allied attackers gain +3 power and +1 speed this turn.
- **44**x: Grant one ally +4 defense and create a shield that absorbs 6 damage.
- **40**x: Heal all allies for 3 HP and negate the next fire effect played against them.
- **33**x: Create a 5/5/5/5/5 spirit token with the same alignment as this card.
- **31**x: Phase through danger, avoid the next hit, and gain +2 magic.
- **30**x: Reveal hidden enemies and grant all allies +2 magic.
- **30**x: Double resource growth for 1 turn and heal all allies for 2 HP.
- **29**x: Look at the top 3 cards, draw 1, and give an ally +2 wisdom.
- **26**x: Deal 8 damage to one dark-aligned enemy and grant allied cards +2 power this turn.
- **26**x: Revive one fallen ally at half stats or deal 7 damage to an injured enemy.
- **26**x: Burn the opposing field for 3 damage now and 2 more next turn.
- **25**x: Poison one enemy for 2 turns and steal 2 speed from it.
- **25**x: Strike all enemies for 4 damage and stun the fastest target.
- **25**x: Summon a wild ally token and heal your weakest card for 4 HP.

## Lowest Blueprint-Ready Cultures

| Culture | Figures | Simple Blueprints | Rate |
|---|---:|---:|---:|
| hopi | 20 | 0 | 0.0% |
| taiwanese-aboriginal | 20 | 1 | 5.0% |
| buryat-mongol | 20 | 3 | 15.0% |
| fijian | 20 | 3 | 15.0% |
| kashmiri-shaivism | 20 | 3 | 15.0% |
| tamil-dravidian | 20 | 3 | 15.0% |
| tongan | 20 | 3 | 15.0% |
| yakut-sakha | 20 | 3 | 15.0% |
| yazidi | 20 | 3 | 15.0% |
| iroquois-haudenosaunee | 20 | 4 | 20.0% |
| shaiva-hindu | 20 | 4 | 20.0% |
| toltec | 20 | 4 | 20.0% |
| zoroastrian-persian | 20 | 4 | 20.0% |
| aboriginal-australian | 20 | 5 | 25.0% |
| ancient-greek | 20 | 5 | 25.0% |
| armenian | 20 | 5 | 25.0% |
| assyrian | 20 | 5 | 25.0% |
| haida | 20 | 5 | 25.0% |
| inca-andean | 20 | 5 | 25.0% |
| melanesian-papuan | 20 | 5 | 25.0% |

## Migration Read

The existing dataset already works for:

- figure identity
- cost / attack / health projection
- culture ownership
- rarity and uniqueness decisions
- keyword inference as a starting point

The existing dataset still needs redesign for:

- old five-stat ability language (`power`, `defense`, `speed`, `magic`, `wisdom`)
- broad custom subsystem wording like hidden cards, reserve, resource growth, and alignment-specific checks
- repeated template text that does not create a clean faction role on its own

## Files

- JSON report: `data\card-system-compatibility.json`
- Markdown report: `data\card-system-compatibility.md`
