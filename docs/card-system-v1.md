# Mythic Clash Card System v1

Status: locked

This document answers two linked questions:

1. What should Mythic Clash cards actually look like as a game system?
2. How do we keep the rules open enough that future cards and mechanics are easier to add?

The key design choice is:

- cards should be built from reusable rules primitives
- not from one-off hardcoded exceptions whenever possible

That keeps the game extensible without making the launch set unreadable.

## Design Goals

The card system should:

- be simple to read on the front end
- be structured enough to serialize cleanly
- support future mechanics without rewriting the engine each set
- let Mythic Clash stay mostly board-first
- support Figures, Spells, Relics, Heroes, and Tokens under one shared vocabulary

## The Main Principle

Every card should be expressible as:

- metadata
- stats, if relevant
- keywords
- one or more abilities

Every ability should be expressible as:

- timing
- trigger or activation condition
- optional target rules
- one or more effect primitives

This is the main "open rules" decision. It is much better than building cards around:

- hardcoded spell kinds only
- one-off named battlecries
- dozens of special-case booleans

## Shared Card Model

Every card should support the following fields, even if some are unused by a given type.

### Required fields

- `id`
- `name`
- `card_type`
- `culture_slug`
- `rarity`
- `alignment`
- `traits`
- `rules_text`

### Optional universal fields

- `cost`
- `speed`
- `subtypes`
- `keywords`
- `unique`
- `legendary`
- `token`
- `set_code`
- `art_prompt`
- `flavor_text`

### Stats fields

Used by Figures and some summoned tokens:

- `attack`
- `health`

### Ability fields

Each card may contain an `abilities` array.

Each ability contains:

- `id`
- `label`
- `timing`
- `trigger`
- `target_rule`
- `conditions`
- `effects`
- `limit`

## Card Types

## Hero

Hero cards need:

- `id`
- `name`
- `card_type: hero`
- `culture_slug`
- `hero_power`
- optional `passive_ability`

Recommended hero model:

- shared baseline of 30 Health
- hero-specific card stores identity, power, and optional passive hook

### Why this is extensible

It lets future sets add:

- passive heroes
- alternate hero powers
- hero-specific relic interactions

without changing the whole game model.

## Figure

Figure cards need:

- `cost`
- `attack`
- `health`
- `keywords`
- `abilities`

Figures should be the most common type in the game.

## Spell

Spell cards need:

- `cost`
- `speed`
- `abilities`

Recommended speeds:

- `slow`
- `fast`
- `burst`

Do not create extra spell speeds early unless they solve a real gameplay need.

## Relic

Relic cards need:

- `cost`
- optional `durability` only if the design later wants it
- `abilities`

Relics should stay persistent, low-clutter, and build-around oriented.

Important rule:

- avoid needing a separate Relic durability system at launch

If the game later wants fragile relics, that can be added as a supported optional field.

## Token

Token cards should use the same model as normal cards but carry:

- `token: true`
- `collectible: false`

This is important because it means tokens can:

- be summoned
- copied
- buffed
- referenced by effects

without needing a second object model.

## Ability Architecture

Abilities should not be free-form text in the engine.

They should be built from structured primitives.

## Timing values

Recommended base timing vocabulary:

- `passive`
- `slow`
- `fast`
- `burst`
- `activated`

## Trigger values

Recommended base trigger vocabulary:

- `on_play`
- `on_summon`
- `on_attack_declared`
- `on_strike`
- `on_damage_dealt`
- `on_damage_taken`
- `on_death`
- `on_turn_start`
- `on_turn_end`
- `on_friendly_play`
- `on_enemy_play`
- `on_relic_play`
- `on_heal`
- `on_draw`
- `manual`

This list is intentionally broad enough that future mechanics can hook into known events.

## Target rules

Targeting should be standardized.

Recommended target rule vocabulary:

- `none`
- `self`
- `friendly_figure`
- `friendly_hero`
- `friendly_character`
- `ally_figure`
- `ally_hero`
- `ally_character`
- `enemy_figure`
- `enemy_hero`
- `enemy_character`
- `enemy_team_figure`
- `enemy_team_hero`
- `enemy_team_character`
- `any_figure`
- `any_character`
- `adjacent_friendly_figure`
- `damaged_enemy_figure`
- `random_enemy_figure`
- `empty_friendly_slot`
- `friendly_relic`
- `enemy_relic`
- `all_enemy_figures`
- `all_enemy_heroes`
- `all_enemy_characters`
- `all_friendly_team_figures`
- `all_friendly_team_characters`

This should be a data field, not rephrased from scratch every time.

## Conditions

Conditions are what make the system extensible without becoming chaotic.

Recommended base condition primitives:

- `if_you_control_trait`
- `if_target_is_damaged`
- `if_you_have_empty_board_slot`
- `if_this_survived_damage`
- `if_you_cast_spell_this_turn`
- `if_enemy_has_guard`
- `if_you_have_relic`
- `if_card_drawn_this_turn`
- `if_primary_culture_matches`
- `if_secondary_culture_present`
- `if_health_below`
- `if_turn_number_at_least`

## Effect primitives

These are the most important long-term system decision.

Every new card should try to use these primitives before introducing new rule code.

Recommended v1 effect primitive library:

- `deal_damage`
- `heal`
- `draw_cards`
- `summon_token`
- `grant_stats`
- `set_stats`
- `grant_keyword`
- `remove_keyword`
- `silence`
- `destroy`
- `return_to_hand`
- `ready`
- `exhaust`
- `freeze`
- `gain_armor`
- `gain_ritual_mana`
- `reduce_cost`
- `discover_from_pool`
- `create_in_hand`
- `copy_card`
- `replace_relic`
- `move_position`
- `buff_adjacent`
- `trigger_again`
- `set_guard_ignore`
- `set_cant_attack`
- `set_cant_be_targeted`

This list is enough to build a very large number of clean launch cards.

## Delayed and persistent effects

To keep the game open for future designs, every effect should optionally support:

- `duration: until_end_of_turn`
- `duration: until_your_next_turn`
- `duration: permanent`
- `duration: while_in_play`
- `duration: this_combat`

This avoids hardcoding temporary behavior per card.

## Traits, Domains, and Subtypes

Mythic Clash already has mythology domains in the figure data. That is a strength and should become a first-class card-system layer.

Recommended card classification layers:

- `culture_slug`
- `domains`
- `subtypes`
- `alignment`

Examples of subtypes:

- god
- goddess
- hero
- spirit
- monster
- beast
- oracle
- warrior
- priest
- trickster
- guardian

Why this matters:

- domains let support cards scale across many cultures
- subtypes let future synergies exist without locking everything to exact names

## Keyword Policy

Keywords should only be promoted when they:

- appear often enough
- are short enough
- create strategic meaning
- are easier to teach as a keyword than as repeated rules text

Recommended keyword buckets:

### Evergreen

- Guard
- Ward
- Rush
- Lifesteal
- Reborn
- Overwhelm
- Stealth

### Premium

- Charge
- Poisonous
- Freeze

### Future reserved space

- Scout
- Echo
- Rally
- Spellshield
- Ambush

Reserved space means:

- the rules model is allowed to support them later
- but they should not be common at launch

## Open Rules Without Becoming Bloated

There is a big difference between:

- extensible

and:

- vague

To keep the game open and still disciplined:

### Good extensibility

- shared triggers
- shared target rules
- shared effect primitives
- consistent keyword behavior
- tags and domains as reusable hooks

### Bad extensibility

- "this card works differently because flavor"
- too many one-off timing exceptions
- custom resource systems on individual cards
- cards that invent private minigames

## Text Templating Rules

Rules text should always mirror the underlying structured ability.

Use a small number of sentence templates.

Examples:

- `Battlecry: Deal 2 damage to an enemy Figure.`
- `Fast: Give a friendly Figure +2/+2 this combat.`
- `At the end of your turn, if you played a Spell, draw a card.`
- `Deathrite: Summon a 1/1 Spirit token.`

This makes future additions much easier because the UI, parser, and player all see the same shape.

## Recommended Naming Of Ability Buckets

Instead of only `battlecry` and `deathrattle`, Mythic Clash should use its own broad ability buckets.

Recommended named buckets:

- `Battlecry`
- `Deathrite`
- `Invocation`
- `Passive`
- `Strike`
- `Lasting`
- `Hero Power`

This gives the game flavor while staying structurally clean.

## Multiplayer-safe language

Even though launch should stay `1v1`, the card system should reserve these meanings:

- `friendly`: controlled by you
- `ally`: controlled by your teammate
- `enemy`: controlled by an opposing player
- `team`: all players on one side of a multiplayer match

That keeps future `2v2` and larger team modes much easier to add later without rewriting the whole text and target model.

## Support Card Architecture

Support cards should not all be "generic spells."

Mythic Clash should deliberately support three support layers:

- `Neutral Core`
- `Domain Support`
- `Signature Culture Support`

That means the rules model must support:

- culture-locked cards
- domain-locked cards
- neutral cards

This is very important for future scaling.

## Recommended Pools For Discover / Create Effects

Random generation should always use explicit pools.

Recommended pool types:

- `neutral_core_spell`
- `war_domain_card`
- `death_domain_card`
- `friendly_culture_figure`
- `secondary_culture_card`
- `token_spirit`

Do not use:

- `random_card_from_entire_game`

as a normal pattern.

## Future-Proofing Decisions We Should Make Now

To keep the game open later, the engine and card model should be built now with these assumptions:

- a card can have multiple abilities
- a card can gain abilities temporarily
- a card can reference traits, domains, and cultures
- a card can create another card into hand
- a card can create a token on board
- a relic can have activated abilities
- a hero can have passive text in future sets
- future card types can reuse the same ability framework

## Things We Should Not Prematurely Support

Do not over-open the rules in these directions at launch:

- nested trigger chains that never end
- alternate win conditions
- hidden trap zones
- full reaction permission to all cards
- many separate resource types
- permanent aura layers with many ordering exceptions

That kind of openness is expensive and often makes future content harder, not easier.

## Recommended Implementation Data Shape

Example pseudo-JSON for a Spell:

```json
{
  "id": "core-sunfire-burst",
  "name": "Sunfire Burst",
  "card_type": "spell",
  "culture_slug": "neutral",
  "rarity": "rare",
  "alignment": "light",
  "cost": 5,
  "speed": "slow",
  "traits": ["sun", "fire"],
  "rules_text": "Deal 2 damage to all enemy Figures.",
  "abilities": [
    {
      "id": "sunfire-burst-1",
      "label": "Sunfire Burst",
      "timing": "slow",
      "trigger": "on_play",
      "target_rule": "enemy_figure",
      "effects": [
        {
          "kind": "deal_damage",
          "amount": 2,
          "scope": "all_valid_targets"
        }
      ]
    }
  ]
}
```

Example pseudo-JSON for a Relic:

```json
{
  "id": "war-banner-of-ares",
  "name": "Banner of Ares",
  "card_type": "relic",
  "culture_slug": "ancient-greek",
  "rarity": "rare",
  "alignment": "neutral",
  "cost": 2,
  "traits": ["war"],
  "rules_text": "Your attacking Figures have +1 Attack.",
  "abilities": [
    {
      "id": "banner-of-ares-1",
      "label": "War Banner",
      "timing": "passive",
      "trigger": "on_attack_declared",
      "target_rule": "friendly_figure",
      "conditions": [
        {
          "kind": "attacker_is_friendly"
        }
      ],
      "effects": [
        {
          "kind": "grant_stats",
          "attack": 1,
          "health": 0,
          "duration": "this_combat"
        }
      ]
    }
  ]
}
```

## Bottom Line

If we design cards first, we should not design them as isolated cool text boxes.

We should design:

- a reusable card grammar
- a reusable rules primitive library
- a reusable support-card structure

That is what will keep Mythic Clash open for future growth without collapsing into rules spaghetti.
