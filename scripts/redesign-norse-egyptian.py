"""Redesign Norse-Viking and Ancient-Egyptian as distinct archetypes.

Norse = Aggro/Tempo: cheap figures, overwhelm, charge, cheap Fast combat tricks
Egyptian = Control/Value: sticky figures, reborn, death triggers, heals, card advantage
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# No external deps needed — we build raw JSON dicts

CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"

NULL_EFFECT = {"attack": None, "health": None, "keyword": None, "duration": None, "scope": None, "pool": None, "card_id": None, "extra": {}}

def effect(kind, amount=None, **kwargs):
    e = {"kind": kind, "amount": amount, **NULL_EFFECT}
    e.update(kwargs)
    return e

def ability(id, label, trigger="on_play", target_rule="none", effects=None, timing="slow", limit=None, resource_cost=None):
    return {
        "id": id, "label": label, "timing": timing, "trigger": trigger,
        "target_rule": target_rule, "resource_cost": resource_cost,
        "conditions": [], "effects": effects or [], "limit": limit,
    }

def figure(id, name, cost, attack, health, keywords=None, rules_text="", abilities=None, rarity="common", traits=None, subtypes=None):
    return {
        "id": id, "name": name, "card_type": "figure", "culture_slug": "", # filled later
        "rarity": rarity, "alignment": "neutral", "traits": traits or [],
        "rules_text": rules_text, "cost": cost, "speed": None,
        "subtypes": subtypes or [], "keywords": keywords or [],
        "unique": rarity == "legendary", "legendary": rarity == "legendary",
        "token": False, "collectible": True, "set_code": "",
        "flavor_text": "", "attack": attack, "health": health,
        "abilities": abilities or [],
    }

def spell(id, name, cost, speed, rules_text, abilities=None, rarity="common", traits=None):
    return {
        "id": id, "name": name, "card_type": "spell", "culture_slug": "",
        "rarity": rarity, "alignment": "neutral", "traits": traits or [],
        "rules_text": rules_text, "cost": cost, "speed": speed,
        "subtypes": [], "keywords": [],
        "unique": False, "legendary": False, "token": False, "collectible": True,
        "set_code": "", "flavor_text": "", "attack": None, "health": None,
        "abilities": abilities or [],
    }

def relic(id, name, cost, rules_text, abilities=None, rarity="rare", traits=None):
    return {
        "id": id, "name": name, "card_type": "relic", "culture_slug": "",
        "rarity": rarity, "alignment": "neutral", "traits": traits or [],
        "rules_text": rules_text, "cost": cost, "speed": None,
        "subtypes": [], "keywords": [],
        "unique": False, "legendary": False, "token": False, "collectible": True,
        "set_code": "", "flavor_text": "", "attack": None, "health": None,
        "abilities": abilities or [],
    }

def token(id, name, attack, health, keywords=None, rules_text="", abilities=None):
    return {
        "id": id, "name": name, "card_type": "token", "culture_slug": "",
        "rarity": "token", "alignment": "neutral", "traits": [],
        "rules_text": rules_text, "cost": 0, "speed": None,
        "subtypes": [], "keywords": keywords or [],
        "unique": False, "legendary": False, "token": True, "collectible": False,
        "set_code": "", "flavor_text": "", "attack": attack, "health": health,
        "abilities": abilities or [],
    }

def hero(id, name, rules_text, abilities, traits=None):
    return {
        "id": id, "name": name, "card_type": "hero", "culture_slug": "",
        "rarity": "legendary", "alignment": "light", "traits": traits or [],
        "rules_text": rules_text, "cost": None, "speed": None,
        "subtypes": [], "keywords": [],
        "unique": True, "legendary": True, "token": False, "collectible": True,
        "set_code": "", "flavor_text": "", "attack": None, "health": None,
        "abilities": abilities,
    }

# ============================================================
# NORSE-VIKING: Aggro/Tempo
# Identity: Cheap rush, overwhelm, face damage, combat tricks
# Win condition: race the opponent down before running out of cards
# ============================================================

def build_norse():
    S = "norse-viking"
    cards = [
        hero(f"{S}-hero-thor", "Thor, Storm Keeper",
             "Hero Power - Thunder Strike (2): Deal 1 damage to any enemy.",
             [ability(f"{S}-hero-1", "Thunder Strike", trigger="manual", target_rule="enemy_character", timing="slow", resource_cost=2,
                      effects=[effect("deal_damage", 1)])],
             traits=["thunder", "storms", "war"]),

        # 1-drops (2)
        figure(f"{S}-001", "Ratatoskr", 1, 1, 1, ["stealth"],
               "Stealth. On play: Draw a card.",
               [ability(f"{S}-001-1", "Gossip", effects=[effect("draw_cards", 1)])],
               rarity="common"),
        figure(f"{S}-002", "Einherjar", 1, 2, 1, [],
               "On play: Deal 1 damage to the enemy Hero.",
               [ability(f"{S}-002-1", "Battle Cry", target_rule="none",
                        effects=[effect("deal_damage", 1, scope="enemy_hero")])],
               rarity="common"),

        # 2-drops (4) — aggressive stats
        figure(f"{S}-003", "Sleipnir", 2, 2, 2, ["rush"],
               "Rush.",
               rarity="common"),
        figure(f"{S}-004", "Valkyrie Scout", 2, 3, 1, [],
               "On play: Give a friendly Figure +1 Attack this turn.",
               [ability(f"{S}-004-1", "Inspire", target_rule="friendly_figure",
                        effects=[effect("grant_stats", attack=1, health=0, duration="turn")])],
               rarity="common"),
        figure(f"{S}-005", "Berserker", 2, 2, 3, [],
               "Has +2 Attack while damaged.",
               [ability(f"{S}-005-1", "Rage", trigger="passive", timing="passive",
                        effects=[effect("grant_stats", attack=2, health=0, extra={"condition": "while_damaged"})])],
               rarity="uncommon"),
        figure(f"{S}-006", "Ulfhednar", 2, 3, 2, ["overwhelm"],
               "Overwhelm.",
               rarity="common"),

        # 3-drops (4)
        figure(f"{S}-007", "Brynhildr", 3, 3, 3, [],
               "On play: Draw a card.",
               [ability(f"{S}-007-1", "Shield Maiden", effects=[effect("draw_cards", 1)])],
               rarity="common"),
        figure(f"{S}-008", "Sigurd", 3, 3, 2, ["rush"],
               "Rush. On play: Give another friendly Figure +1 Attack.",
               [ability(f"{S}-008-1", "Dragon Slayer", target_rule="other_friendly_figure",
                        effects=[effect("grant_stats", attack=1, health=0)])],
               rarity="rare"),
        figure(f"{S}-009", "Skadi", 3, 4, 2, ["rush"],
               "Rush.",
               rarity="common"),
        figure(f"{S}-010", "Fenrir Pup", 3, 2, 2, ["rush"],
               "Rush. On play: Deal 2 damage to an enemy Figure.",
               [ability(f"{S}-010-1", "Savage Bite", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 2)])],
               rarity="rare"),

        # 4-drops (3)
        figure(f"{S}-011", "Heimdall", 4, 3, 5, ["guard"],
               "Guard.",
               rarity="common"),
        figure(f"{S}-012", "Nidhogg", 4, 4, 3, ["overwhelm"],
               "Overwhelm. On play: Deal 1 damage to all enemy Figures.",
               [ability(f"{S}-012-1", "Gnaw", target_rule="all_enemy_figures",
                        effects=[effect("deal_damage", 1)])],
               rarity="rare"),
        figure(f"{S}-013", "Tyr", 4, 5, 3, ["rush"],
               "Rush.",
               rarity="rare"),

        # 5-drops (2)
        figure(f"{S}-014", "Fenrir", 5, 6, 4, ["overwhelm", "rush"],
               "Rush. Overwhelm.",
               rarity="rare"),
        figure(f"{S}-015", "Surtur", 5, 5, 5, [],
               "On play: Deal 3 damage to an enemy Figure.",
               [ability(f"{S}-015-1", "Flame Blade", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 3)])],
               rarity="rare"),

        # 6-drops (2) — finishers
        figure(f"{S}-016", "Thor", 6, 5, 6, ["overwhelm"],
               "Overwhelm. On play: Deal 2 damage to all enemy Figures.",
               [ability(f"{S}-016-1", "Lightning Storm", target_rule="all_enemy_figures",
                        effects=[effect("deal_damage", 2)])],
               rarity="legendary"),
        figure(f"{S}-017", "Odin", 6, 4, 7, [],
               "On play: Draw 2 cards.",
               [ability(f"{S}-017-1", "Allfather's Wisdom", effects=[effect("draw_cards", 2)])],
               rarity="legendary"),

        # SPELLS — distinct Norse identity: aggressive, cheap, combat tricks
        spell(f"{S}-spell-battle-rage", "Battle Rage", 1, "fast",
              "Give a friendly Figure +2 Attack this combat.",
              [ability(f"{S}-spell-1", "Battle Rage", trigger="manual", target_rule="friendly_figure", timing="fast",
                       effects=[effect("grant_stats", attack=2, health=0, duration="combat")])],
              rarity="common"),
        spell(f"{S}-spell-thunder-strike", "Lightning Bolt", 2, "fast",
              "Deal 3 damage to any enemy.",
              [ability(f"{S}-spell-2", "Lightning Bolt", trigger="manual", target_rule="enemy_character", timing="fast",
                       effects=[effect("deal_damage", 3)])],
              rarity="common"),
        spell(f"{S}-spell-berserker-cry", "Berserker Cry", 2, "burst",
              "Give all friendly Figures +1 Attack this turn.",
              [ability(f"{S}-spell-3", "Berserker Cry", trigger="manual", target_rule="none", timing="burst",
                       effects=[effect("grant_stats", attack=1, health=0, duration="turn", scope="all_friendly_figures")])],
              rarity="uncommon"),
        spell(f"{S}-spell-rune-sight", "Rune Sight", 2, "burst",
              "Draw a card.",
              [ability(f"{S}-spell-4", "Rune Sight", trigger="manual", target_rule="none", timing="burst",
                       effects=[effect("draw_cards", 1)])],
              rarity="common"),
        spell(f"{S}-spell-ragnarok-axe", "Ragnarok Axe", 4, "fast",
              "Deal 4 damage to an enemy Figure. If it dies, deal 2 damage to the enemy Hero.",
              [ability(f"{S}-spell-5", "Ragnarok Axe", trigger="manual", target_rule="enemy_figure", timing="fast",
                       effects=[effect("deal_damage", 4, extra={"on_kill_hero_damage": 2})])],
              rarity="rare"),

        # RELICS — aggressive identity
        relic(f"{S}-relic-mjolnir-shard", "Mjolnir Shard", 2,
              "Your Figures with Overwhelm have +1 Attack.",
              [ability(f"{S}-relic-1", "Mjolnir Shard", trigger="passive", timing="passive",
                       effects=[effect("grant_stats", attack=1, health=0, scope="friendly_overwhelm_figures")])],
              rarity="rare"),
        relic(f"{S}-relic-horn-of-valhalla", "Horn of Valhalla", 3,
              "The first time each turn a friendly Figure attacks the enemy Hero, deal 1 extra damage.",
              [ability(f"{S}-relic-2", "Horn of Valhalla", trigger="on_attack_hero", timing="passive",
                       effects=[effect("deal_damage", 1, scope="enemy_hero")])],
              rarity="rare"),

        # TOKEN
        token(f"{S}-token-spirit-warrior", "Spirit Warrior", 2, 1, ["rush"],
              "Rush."),
    ]
    return cards


# ============================================================
# ANCIENT-EGYPTIAN: Control/Value
# Identity: Sticky minions, reborn, death triggers, heals, card draw
# Win condition: outvalue the opponent, never run out of resources
# ============================================================

def build_egyptian():
    S = "ancient-egyptian"
    cards = [
        hero(f"{S}-hero-isis", "Isis, Throne of Magic",
             "Hero Power - Ankh Blessing (2): Restore 2 Health to your Hero or a friendly Figure.",
             [ability(f"{S}-hero-1", "Ankh Blessing", trigger="manual", target_rule="friendly_character", timing="slow", resource_cost=2,
                      effects=[effect("heal", 2)])],
             traits=["sun", "death", "healing", "magic"]),

        # 1-drops (1)
        figure(f"{S}-001", "Scarab Keeper", 1, 1, 2, [],
               "On play: Gain 1 Ritual Mana.",
               [ability(f"{S}-001-1", "Sacred Scarab", effects=[effect("gain_ritual_mana", 1)])],
               rarity="common"),

        # 2-drops (4) — sticky and defensive
        figure(f"{S}-002", "Khnum", 2, 2, 3, [],
               "On play: Give a friendly Figure +1 Health.",
               [ability(f"{S}-002-1", "Potter's Craft", target_rule="friendly_figure",
                        effects=[effect("grant_stats", attack=0, health=1)])],
               rarity="common"),
        figure(f"{S}-003", "Bes", 2, 1, 4, ["guard"],
               "Guard.",
               rarity="common"),
        figure(f"{S}-004", "Serket", 2, 2, 2, ["reborn"],
               "Reborn.",
               rarity="uncommon"),
        figure(f"{S}-005", "Temple Scribe", 2, 1, 3, [],
               "On play: Draw a card.",
               [ability(f"{S}-005-1", "Hieroglyphs", effects=[effect("draw_cards", 1)])],
               rarity="common"),

        # 3-drops (4) — value engines
        figure(f"{S}-006", "Ammit", 3, 3, 3, [],
               "On play: Deal 2 damage to an enemy Figure.",
               [ability(f"{S}-006-1", "Devour", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 2)])],
               rarity="common"),
        figure(f"{S}-007", "Nephthys", 3, 2, 4, ["guard"],
               "Guard. Deathrattle: Draw a card.",
               [ability(f"{S}-007-1", "Mourner's Gift", trigger="on_death",
                        effects=[effect("draw_cards", 1)])],
               rarity="rare"),
        figure(f"{S}-008", "Khepri", 3, 2, 3, ["reborn"],
               "Reborn. On play: Give a friendly Figure +1/+1.",
               [ability(f"{S}-008-1", "Dawn Renewal", target_rule="friendly_figure",
                        effects=[effect("grant_stats", attack=1, health=1)])],
               rarity="rare"),
        figure(f"{S}-009", "Mummy Guard", 3, 2, 5, ["guard"],
               "Guard.",
               rarity="common"),

        # 4-drops (3) — midrange anchors
        figure(f"{S}-010", "Bastet", 4, 3, 5, ["lifesteal"],
               "Lifesteal.",
               rarity="rare"),
        figure(f"{S}-011", "Sobek", 4, 4, 4, ["rush"],
               "Rush.",
               rarity="common"),
        figure(f"{S}-012", "Hathor", 4, 2, 5, [],
               "On play: Heal all friendly Figures for 2 and draw a card.",
               [ability(f"{S}-012-1", "Nurture", effects=[
                   effect("heal", 2, scope="all_friendly_figures"),
                   effect("draw_cards", 1),
               ])],
               rarity="rare"),

        # 5-drops (3) — value bombs
        figure(f"{S}-013", "Anubis", 5, 4, 5, [],
               "On play: Return a friendly Figure that costs 3 or less from your discard to your hand.",
               [ability(f"{S}-013-1", "Embalm", effects=[effect("return_from_discard", extra={"max_cost": 3})])],
               rarity="rare"),
        figure(f"{S}-014", "Horus", 5, 5, 4, ["rush"],
               "Rush. On play: Deal 2 damage to an enemy Figure.",
               [ability(f"{S}-014-1", "Sky Judgment", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 2)])],
               rarity="rare"),
        figure(f"{S}-015", "Sekhmet", 5, 4, 5, [],
               "On play: Deal 2 damage to all enemy Figures.",
               [ability(f"{S}-015-1", "War Goddess", target_rule="all_enemy_figures",
                        effects=[effect("deal_damage", 2)])],
               rarity="rare"),

        # 6-drops (2) — finishers
        figure(f"{S}-016", "Osiris", 6, 4, 8, ["reborn"],
               "Reborn. Deathrattle: Summon a 2/2 Spirit of the Dead.",
               [ability(f"{S}-016-1", "Eternal Return", trigger="on_death",
                        effects=[effect("summon_token", card_id=f"{S}-token-spirit")])],
               rarity="legendary"),
        figure(f"{S}-017", "Ra", 6, 5, 7, [],
               "On play: Deal 3 damage to an enemy Figure and restore 3 Health to your Hero.",
               [ability(f"{S}-017-1", "Solar Flare", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 3), effect("heal", 3, scope="friendly_hero")])],
               rarity="legendary"),

        # SPELLS — control identity: cheap heals, expensive removal, card draw
        spell(f"{S}-spell-embalming-rite", "Embalming Rite", 1, "burst",
              "Give a friendly Figure +0/+2.",
              [ability(f"{S}-spell-1", "Embalming Rite", trigger="manual", target_rule="friendly_figure", timing="burst",
                       effects=[effect("grant_stats", attack=0, health=2)])],
              rarity="common"),
        spell(f"{S}-spell-book-of-dead", "Book of the Dead", 2, "burst",
              "Draw 2 cards.",
              [ability(f"{S}-spell-2", "Book of the Dead", trigger="manual", target_rule="none", timing="burst",
                       effects=[effect("draw_cards", 2)])],
              rarity="rare"),
        spell(f"{S}-spell-ankh-shield", "Ankh Shield", 2, "fast",
              "Give a friendly Figure +0/+3 and Guard this turn.",
              [ability(f"{S}-spell-3", "Ankh Shield", trigger="manual", target_rule="friendly_figure", timing="fast",
                       effects=[effect("grant_stats", attack=0, health=3, duration="turn"),
                                effect("grant_keyword", keyword="guard", duration="turn")])],
              rarity="uncommon"),
        spell(f"{S}-spell-plague-of-locusts", "Plague of Locusts", 5, "slow",
              "Deal 3 damage to all enemy Figures.",
              [ability(f"{S}-spell-4", "Plague of Locusts", trigger="manual", target_rule="all_enemy_figures", timing="slow",
                       effects=[effect("deal_damage", 3)])],
              rarity="rare"),
        spell(f"{S}-spell-mummify", "Mummify", 3, "fast",
              "Freeze an enemy Figure and deal 2 damage to it.",
              [ability(f"{S}-spell-5", "Mummify", trigger="manual", target_rule="enemy_figure", timing="fast",
                       effects=[effect("freeze"), effect("deal_damage", 2)])],
              rarity="uncommon"),

        # RELICS — value/grind identity
        relic(f"{S}-relic-book-of-thoth", "Book of Thoth", 2,
              "At the end of your turn, if you played two or more cards this turn, draw a card.",
              [ability(f"{S}-relic-1", "Book of Thoth", trigger="on_turn_end", timing="passive",
                       effects=[effect("draw_cards", 1)])],
              rarity="rare"),
        relic(f"{S}-relic-canopic-jar", "Canopic Jar", 3,
              "The first time a friendly Figure dies each turn, restore 2 Health to your Hero.",
              [ability(f"{S}-relic-2", "Canopic Jar", trigger="on_death", timing="passive",
                       effects=[effect("heal", 2, scope="friendly_hero")],
                       limit="once_each_turn")],
              rarity="rare"),

        # TOKENS
        token(f"{S}-token-spirit", "Spirit of the Dead", 2, 2, [],
              ""),
    ]
    return cards


# ============================================================
# ANCIENT-GREEK: Midrange/Tempo
# Identity: Flexible, combat tricks, spell synergy, adaptable
# Win condition: win the board through efficient trades + tricks, then convert to face
# ============================================================

def build_greek():
    S = "ancient-greek"
    cards = [
        hero(f"{S}-hero-athena", "Athena, Goddess of Strategy",
             "Hero Power - Owl's Insight (2): Deal 1 damage to an enemy Figure. If it dies, draw a card.",
             [ability(f"{S}-hero-1", "Owl's Insight", trigger="manual", target_rule="enemy_figure", timing="slow", resource_cost=2,
                      effects=[effect("deal_damage", 1, extra={"on_kill_draw": 1})])],
             traits=["wisdom", "war", "strategy"]),

        # 1-drops (2)
        figure(f"{S}-001", "Hermes", 1, 1, 2, [],
               "On play: Give a friendly Figure +1 Attack this turn.",
               [ability(f"{S}-001-1", "Swift Blessing", target_rule="friendly_figure",
                        effects=[effect("grant_stats", attack=1, health=0, duration="turn")])],
               rarity="common"),
        figure(f"{S}-002", "Arachne", 1, 1, 1, [],
               "On play: Draw a card.",
               [ability(f"{S}-002-1", "Weaver", effects=[effect("draw_cards", 1)])],
               rarity="common"),

        # 2-drops (4) — efficient, flexible
        figure(f"{S}-003", "Dionysus", 2, 2, 3, [],
               "On play: Draw a card.",
               [ability(f"{S}-003-1", "Revelry", effects=[effect("draw_cards", 1)])],
               rarity="common"),
        figure(f"{S}-004", "Artemis", 2, 3, 2, ["rush"],
               "Rush.",
               rarity="common"),
        figure(f"{S}-005", "Pan", 2, 2, 2, [],
               "On play: Give a friendly Figure +1/+1.",
               [ability(f"{S}-005-1", "Wild Growth", target_rule="friendly_figure",
                        effects=[effect("grant_stats", attack=1, health=1)])],
               rarity="uncommon"),
        figure(f"{S}-006", "Chimera", 2, 3, 2, ["poisonous"],
               "Poisonous.",
               rarity="rare"),

        # 3-drops (4) — strong midrange
        figure(f"{S}-007", "Ares", 3, 4, 3, [],
               "On play: Deal 1 damage to an enemy Figure.",
               [ability(f"{S}-007-1", "War Cry", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 1)])],
               rarity="common"),
        figure(f"{S}-008", "Medusa", 3, 2, 4, [],
               "On play: Freeze an enemy Figure.",
               [ability(f"{S}-008-1", "Petrify", target_rule="enemy_figure",
                        effects=[effect("freeze")])],
               rarity="rare"),
        figure(f"{S}-009", "Hephaestus", 3, 2, 4, [],
               "On play: Give a friendly Figure +2/+1.",
               [ability(f"{S}-009-1", "Forge", target_rule="friendly_figure",
                        effects=[effect("grant_stats", attack=2, health=1)])],
               rarity="rare"),
        figure(f"{S}-010", "Pegasus", 3, 3, 2, ["rush"],
               "Rush. On play: Draw a card.",
               [ability(f"{S}-010-1", "Skyborne", effects=[effect("draw_cards", 1)])],
               rarity="rare"),

        # 4-drops (3)
        figure(f"{S}-011", "Achilles", 4, 5, 3, ["rush"],
               "Rush. On play: Deal 2 damage to an enemy Figure.",
               [ability(f"{S}-011-1", "Spear Throw", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 2)])],
               rarity="rare"),
        figure(f"{S}-012", "Apollo", 4, 3, 5, [],
               "On play: Deal 2 damage to an enemy Figure. Restore 2 Health to your Hero.",
               [ability(f"{S}-012-1", "Solar Arrow", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 2), effect("heal", 2, scope="friendly_hero")])],
               rarity="rare"),
        figure(f"{S}-013", "Hades", 4, 3, 5, [],
               "On play: Return a friendly Figure that costs 3 or less from your discard to your hand.",
               [ability(f"{S}-013-1", "Underworld Gate", effects=[effect("return_from_discard", extra={"max_cost": 3})])],
               rarity="rare"),

        # 5-drop (1)
        figure(f"{S}-014", "Athena", 5, 4, 6, ["guard"],
               "Guard. On play: Give another friendly Figure +1/+2 and Ward.",
               [ability(f"{S}-014-1", "Aegis Blessing", target_rule="other_friendly_figure",
                        effects=[effect("grant_stats", attack=1, health=2),
                                 effect("grant_keyword", keyword="ward")])],
               rarity="legendary"),

        # 6-drops (2) — finishers
        figure(f"{S}-015", "Zeus", 6, 5, 7, [],
               "On play: Deal 3 damage to an enemy Figure. If it dies, deal 2 damage to all other enemy Figures.",
               [ability(f"{S}-015-1", "Thunderbolt", target_rule="enemy_figure",
                        effects=[effect("deal_damage", 3, extra={"on_kill_aoe": 2})])],
               rarity="legendary"),
        figure(f"{S}-016", "Minotaur", 5, 5, 4, ["charge"],
               "Charge.",
               rarity="rare"),

        # SPELLS — midrange identity: cheap tricks, flexible, spell-matters
        spell(f"{S}-spell-phalanx", "Phalanx Formation", 2, "fast",
              "Give a friendly Figure +2/+2 this combat.",
              [ability(f"{S}-spell-1", "Phalanx Formation", trigger="manual", target_rule="friendly_figure", timing="fast",
                       effects=[effect("grant_stats", attack=2, health=2, duration="combat")])],
              rarity="common"),
        spell(f"{S}-spell-olympian-bolt", "Olympian Bolt", 2, "fast",
              "Deal 3 damage to an enemy Figure.",
              [ability(f"{S}-spell-2", "Olympian Bolt", trigger="manual", target_rule="enemy_figure", timing="fast",
                       effects=[effect("deal_damage", 3)])],
              rarity="common"),
        spell(f"{S}-spell-oracle-vision", "Oracle Vision", 1, "burst",
              "Draw a card. Gain 1 Ritual Mana.",
              [ability(f"{S}-spell-3", "Oracle Vision", trigger="manual", target_rule="none", timing="burst",
                       effects=[effect("draw_cards", 1), effect("gain_ritual_mana", 1)])],
              rarity="uncommon"),
        spell(f"{S}-spell-heroic-charge", "Heroic Charge", 3, "fast",
              "Give a friendly Figure +3 Attack and Rush this turn.",
              [ability(f"{S}-spell-4", "Heroic Charge", trigger="manual", target_rule="friendly_figure", timing="fast",
                       effects=[effect("grant_stats", attack=3, health=0, duration="turn"),
                                effect("grant_keyword", keyword="rush", duration="turn")])],
              rarity="rare"),
        spell(f"{S}-spell-aegis-ward", "Aegis Ward", 1, "burst",
              "Give a friendly Figure Ward.",
              [ability(f"{S}-spell-5", "Aegis Ward", trigger="manual", target_rule="friendly_figure", timing="burst",
                       effects=[effect("grant_keyword", keyword="ward")])],
              rarity="uncommon"),

        # RELICS — spell synergy
        relic(f"{S}-relic-aegis-of-athena", "Aegis of Athena", 2,
              "After you cast a spell, give a random friendly Figure +1/+1.",
              [ability(f"{S}-relic-1", "Aegis of Athena", trigger="on_spell_cast", timing="passive",
                       effects=[effect("grant_stats", attack=1, health=1, scope="random_friendly_figure")])],
              rarity="rare"),
        relic(f"{S}-relic-oracle-tripod", "Oracle's Tripod", 3,
              "At the start of your turn, if you have 2 or more Ritual Mana, draw a card.",
              [ability(f"{S}-relic-2", "Oracle's Tripod", trigger="on_turn_start", timing="passive",
                       effects=[effect("draw_cards", 1)])],
              rarity="rare"),
    ]
    return cards


def finalize_pack(cards, culture_slug, set_code):
    for c in cards:
        c["culture_slug"] = culture_slug
        c["set_code"] = set_code
    return {"culture_slug": culture_slug, "set_code": set_code, "cards": cards}


def build_deck(culture_slug, hero_id, name, card_entries, notes=None):
    return {
        "hero_id": hero_id,
        "name": name,
        "notes": notes or [],
        "cards": card_entries,
    }


def main():
    # Norse
    norse_cards = build_norse()
    norse_pack = finalize_pack(norse_cards, "norse-viking", "norse-viking-v1")

    norse_deck = build_deck("norse-viking", "norse-viking-hero-thor", "Thor Storm Rush", [
        # 1-drops (2x2=4)
        {"id": "norse-viking-001", "count": 2},  # Ratatoskr
        {"id": "norse-viking-002", "count": 2},  # Einherjar
        # 2-drops (3x2=6)
        {"id": "norse-viking-003", "count": 2},  # Sleipnir
        {"id": "norse-viking-004", "count": 2},  # Valkyrie Scout
        {"id": "norse-viking-006", "count": 2},  # Ulfhednar
        # 3-drops (2x2=4)
        {"id": "norse-viking-008", "count": 2},  # Sigurd
        {"id": "norse-viking-009", "count": 1},  # Skadi
        {"id": "norse-viking-010", "count": 1},  # Fenrir Pup
        # 5-drop (1)
        {"id": "norse-viking-014", "count": 1},  # Fenrir (finisher)
        # Spells (4)
        {"id": "norse-viking-spell-battle-rage", "count": 2},  # 1-cost combat trick
        {"id": "norse-viking-spell-thunder-strike", "count": 2},  # 2-cost removal
        # Relic (1)
        {"id": "norse-viking-relic-horn-of-valhalla", "count": 1},
    ], notes=["Aggressive Norse rush deck. Cheap figures, combat tricks, face damage. Win by T10 or lose."])

    # Verify: 2+2+2+2+2+2+2+1+1+1+2+2+1 = 22... need 24
    # Let me recount: 4+6+4+1+4+1 = 20. Need 4 more.
    norse_deck["cards"].append({"id": "norse-viking-007", "count": 2})  # Brynhildr (draw)
    norse_deck["cards"].append({"id": "norse-viking-012", "count": 1})  # Nidhogg
    norse_deck["cards"].append({"id": "norse-viking-016", "count": 1})  # Thor (finisher)

    # Egyptian
    egyptian_cards = build_egyptian()
    egyptian_pack = finalize_pack(egyptian_cards, "ancient-egyptian", "ancient-egyptian-v1")

    egyptian_deck = build_deck("ancient-egyptian", "ancient-egyptian-hero-isis", "Isis Control", [
        # 1-drop (2)
        {"id": "ancient-egyptian-001", "count": 2},  # Scarab Keeper
        # 2-drops (2x3=6)
        {"id": "ancient-egyptian-002", "count": 2},  # Khnum
        {"id": "ancient-egyptian-004", "count": 2},  # Serket (reborn)
        {"id": "ancient-egyptian-005", "count": 2},  # Temple Scribe
        # 3-drops (2x2=4)
        {"id": "ancient-egyptian-007", "count": 2},  # Nephthys (guard + deathrattle draw)
        {"id": "ancient-egyptian-008", "count": 2},  # Khepri (reborn + buff)
        # 4-drops (2x1+1=3)
        {"id": "ancient-egyptian-010", "count": 1},  # Bastet (lifesteal)
        {"id": "ancient-egyptian-012", "count": 1},  # Hathor (heal + draw)
        {"id": "ancient-egyptian-011", "count": 1},  # Sobek (rush)
        # 5-drops (2)
        {"id": "ancient-egyptian-013", "count": 1},  # Anubis (return from discard)
        {"id": "ancient-egyptian-015", "count": 1},  # Sekhmet (AoE)
        # 6-drop (1)
        {"id": "ancient-egyptian-016", "count": 1},  # Osiris (reborn + deathrattle)
        # Spells (5)
        {"id": "ancient-egyptian-spell-embalming-rite", "count": 2},  # 1-cost +0/+2
        {"id": "ancient-egyptian-spell-ankh-shield", "count": 2},  # 2-cost combat trick
        {"id": "ancient-egyptian-spell-book-of-dead", "count": 1},  # 2-cost draw 2
        # Relic (1)
        {"id": "ancient-egyptian-relic-canopic-jar", "count": 1},
    ], notes=["Egyptian control deck. Sticky figures, reborn, death value, heals. Outlast and outvalue."])
    # Count: 2+6+4+3+2+1+5+1 = 24 ✓

    # Also fix Norse deck: swap Nidhogg for Rune Sight draw spell for sustain
    norse_deck["cards"] = [e for e in norse_deck["cards"] if e["id"] != "norse-viking-012"]
    norse_deck["cards"].append({"id": "norse-viking-spell-rune-sight", "count": 1})  # Draw 1

    # Greek
    greek_cards = build_greek()
    greek_pack = finalize_pack(greek_cards, "ancient-greek", "ancient-greek-v1")

    greek_deck = build_deck("ancient-greek", "ancient-greek-hero-athena", "Athena Midrange", [
        # 1-drops (2x2=4)
        {"id": "ancient-greek-001", "count": 2},  # Hermes
        {"id": "ancient-greek-002", "count": 2},  # Arachne
        # 2-drops (2x2=4)
        {"id": "ancient-greek-003", "count": 2},  # Dionysus (draw)
        {"id": "ancient-greek-004", "count": 2},  # Artemis (rush)
        # 3-drops (2x2+1=5)
        {"id": "ancient-greek-007", "count": 2},  # Ares
        {"id": "ancient-greek-009", "count": 2},  # Hephaestus (buff)
        {"id": "ancient-greek-010", "count": 1},  # Pegasus (rush + draw)
        # 4-drops (2)
        {"id": "ancient-greek-011", "count": 1},  # Achilles (rush + removal)
        {"id": "ancient-greek-012", "count": 1},  # Apollo (removal + heal)
        # 5-drop (1)
        {"id": "ancient-greek-016", "count": 1},  # Minotaur (charge)
        # Spells (6) — high spell count is the Greek identity
        {"id": "ancient-greek-spell-phalanx", "count": 2},      # 2-cost Fast +2/+2
        {"id": "ancient-greek-spell-olympian-bolt", "count": 2}, # 2-cost Fast deal 3
        {"id": "ancient-greek-spell-oracle-vision", "count": 1}, # 1-cost Burst draw + ritual
        {"id": "ancient-greek-spell-aegis-ward", "count": 1},    # 1-cost Burst ward
        # Relic (1)
        {"id": "ancient-greek-relic-aegis-of-athena", "count": 1},
    ], notes=["Greek midrange/tempo. Flexible cards, combat tricks, spell synergy. Adapts to any matchup."])
    # Count: 4+4+5+2+1+6+1 = 23... need 1 more
    greek_deck["cards"].append({"id": "ancient-greek-006", "count": 1})  # Chimera (poisonous)
    # Now 24

    # Verify deck sizes
    norse_total = sum(e["count"] for e in norse_deck["cards"])
    egyptian_total = sum(e["count"] for e in egyptian_deck["cards"])
    greek_total = sum(e["count"] for e in greek_deck["cards"])
    print(f"Norse deck: {norse_total} cards")
    print(f"Egyptian deck: {egyptian_total} cards")
    print(f"Greek deck: {greek_total} cards")

    # Save packs
    for pack, slug in [(norse_pack, "norse-viking"), (egyptian_pack, "ancient-egyptian"), (greek_pack, "ancient-greek")]:
        path = CARDS_DIR / f"{slug}-v1.json"
        path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved {path}")

    # Save decks
    for deck, filename in [
        (norse_deck, "norse-viking-thor-storm-rush.json"),
        (egyptian_deck, "ancient-egyptian-isis-control.json"),
        (greek_deck, "ancient-greek-athena-midrange.json"),
    ]:
        path = DECKS_DIR / filename
        path.write_text(json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
