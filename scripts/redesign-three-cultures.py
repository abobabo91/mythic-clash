"""Redesign Norse, Egyptian, Greek with full gameplay depth.

Goals:
- 7-8 spells per deck (up from 4-5) with unique effects
- 2 relics per deck (1 passive, 1 activated)
- Norse aggro viable: burn to face, card draw tied to damage, charge finishers
- Each culture has 2 deck variants (different strategy)
- ~28 cards per pack (more options than deck slots = real deckbuilding)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"

NULL_EFF = {"attack": None, "health": None, "keyword": None, "duration": None, "scope": None, "pool": None, "card_id": None, "extra": {}}

def eff(kind, amount=None, **kw):
    e = {"kind": kind, "amount": amount, **NULL_EFF}
    e.update(kw)
    return e

def abi(id, label, trigger="on_play", target_rule="none", effects=None, timing="slow", limit=None, resource_cost=None):
    return {"id": id, "label": label, "timing": timing, "trigger": trigger, "target_rule": target_rule,
            "resource_cost": resource_cost, "conditions": [], "effects": effects or [], "limit": limit}

def fig(id, name, cost, atk, hp, kw=None, text="", abis=None, rarity="common"):
    return {"id": id, "name": name, "card_type": "figure", "culture_slug": "", "rarity": rarity,
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": cost, "speed": None,
            "subtypes": [], "keywords": kw or [], "unique": rarity == "legendary", "legendary": rarity == "legendary",
            "token": False, "collectible": True, "set_code": "", "flavor_text": "", "attack": atk, "health": hp,
            "abilities": abis or []}

def spl(id, name, cost, speed, text, abis=None, rarity="common"):
    return {"id": id, "name": name, "card_type": "spell", "culture_slug": "", "rarity": rarity,
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": cost, "speed": speed,
            "subtypes": [], "keywords": [], "unique": False, "legendary": False, "token": False,
            "collectible": True, "set_code": "", "flavor_text": "", "attack": None, "health": None,
            "abilities": abis or []}

def rel(id, name, cost, text, abis=None, rarity="rare"):
    return {"id": id, "name": name, "card_type": "relic", "culture_slug": "", "rarity": rarity,
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": cost, "speed": None,
            "subtypes": [], "keywords": [], "unique": False, "legendary": False, "token": False,
            "collectible": True, "set_code": "", "flavor_text": "", "attack": None, "health": None,
            "abilities": abis or []}

def tok(id, name, atk, hp, kw=None, text="", abis=None):
    return {"id": id, "name": name, "card_type": "token", "culture_slug": "", "rarity": "token",
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": 0, "speed": None,
            "subtypes": [], "keywords": kw or [], "unique": False, "legendary": False, "token": True,
            "collectible": False, "set_code": "", "flavor_text": "", "attack": atk, "health": hp,
            "abilities": abis or []}

def hero(id, name, text, abis, traits=None):
    return {"id": id, "name": name, "card_type": "hero", "culture_slug": "", "rarity": "legendary",
            "alignment": "light", "traits": traits or [], "rules_text": text, "cost": None, "speed": None,
            "subtypes": [], "keywords": [], "unique": True, "legendary": True, "token": False,
            "collectible": True, "set_code": "", "flavor_text": "", "attack": None, "health": None,
            "abilities": abis}


# ============================================================
# NORSE-VIKING: Aggro/Burn
# Key fix: hero power hits face, more burn spells, draw tied to face damage
# ============================================================
def build_norse():
    S = "norse-viking"
    return [
        hero(f"{S}-hero-thor", "Thor, Storm Keeper",
             "Hero Power - Thunder Strike (2): Deal 2 damage to the enemy Hero.",
             [abi(f"{S}-hero-1", "Thunder Strike", trigger="manual", target_rule="enemy_hero", timing="slow", resource_cost=2,
                  effects=[eff("deal_damage", 2, scope="enemy_hero")])]),
        # 1-drops (3)
        fig(f"{S}-001", "Ratatoskr", 1, 1, 1, ["stealth"], "Stealth. On play: Draw a card.",
            [abi(f"{S}-001-1", "Gossip", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-002", "Einherjar", 1, 2, 1, [], "On play: Deal 1 damage to the enemy Hero.",
            [abi(f"{S}-002-1", "Battle Cry", effects=[eff("deal_damage", 1, scope="enemy_hero")])]),
        fig(f"{S}-003", "Shield Maiden", 1, 1, 2, [], ""),
        # 2-drops (4)
        fig(f"{S}-004", "Sleipnir", 2, 2, 2, ["rush"], "Rush."),
        fig(f"{S}-005", "Valkyrie Scout", 2, 3, 1, [], "On play: Give a friendly Figure +1 Attack this turn.",
            [abi(f"{S}-005-1", "Inspire", target_rule="friendly_figure", effects=[eff("grant_stats", attack=1, health=0, duration="turn")])]),
        fig(f"{S}-006", "Ulfhednar", 2, 3, 2, ["overwhelm"], "Overwhelm."),
        fig(f"{S}-007", "Berserker", 2, 2, 3, [], ""),
        # 3-drops (4)
        fig(f"{S}-008", "Brynhildr", 3, 3, 3, [], "On play: Draw a card.",
            [abi(f"{S}-008-1", "Shield Maiden Draw", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-009", "Sigurd", 3, 3, 2, ["rush"], "Rush. On play: Deal 1 damage to the enemy Hero.",
            [abi(f"{S}-009-1", "Dragon Slayer", effects=[eff("deal_damage", 1, scope="enemy_hero")])]),
        fig(f"{S}-010", "Skadi", 3, 4, 2, ["rush"], "Rush."),
        fig(f"{S}-011", "Fenrir Pup", 3, 2, 2, ["rush"], "Rush. On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-011-1", "Savage Bite", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])]),
        # 4-drops (3)
        fig(f"{S}-012", "Heimdall", 4, 3, 5, ["guard"], "Guard."),
        fig(f"{S}-013", "Nidhogg", 4, 4, 3, ["overwhelm"], "Overwhelm. On play: Deal 1 to all enemy Figures.",
            [abi(f"{S}-013-1", "Gnaw", target_rule="all_enemy_figures", effects=[eff("deal_damage", 1)])]),
        fig(f"{S}-014", "Tyr", 4, 5, 3, ["charge"], "Charge."),
        # 5-6 drops (3) — finishers
        fig(f"{S}-015", "Fenrir", 5, 6, 4, ["overwhelm", "rush"], "Rush. Overwhelm.", rarity="rare"),
        fig(f"{S}-016", "Thor", 6, 5, 6, ["overwhelm"], "Overwhelm. On play: Deal 2 to all enemy Figures.",
            [abi(f"{S}-016-1", "Lightning Storm", target_rule="all_enemy_figures", effects=[eff("deal_damage", 2)])], rarity="legendary"),
        fig(f"{S}-017", "Odin", 6, 4, 7, [], "On play: Draw 2 cards. Deal 2 damage to the enemy Hero.",
            [abi(f"{S}-017-1", "Allfather", effects=[eff("draw_cards", 2), eff("deal_damage", 2, scope="enemy_hero")])], rarity="legendary"),
        # SPELLS (8) — aggressive, cheap, face-targeting
        spl(f"{S}-spell-battle-rage", "Battle Rage", 1, "fast", "Give a friendly Figure +2 Attack this combat.",
            [abi(f"{S}-sp1", "Battle Rage", trigger="manual", target_rule="friendly_figure", timing="fast",
                 effects=[eff("grant_stats", attack=2, health=0, duration="combat")])]),
        spl(f"{S}-spell-lightning-bolt", "Lightning Bolt", 2, "fast", "Deal 3 damage to any enemy.",
            [abi(f"{S}-sp2", "Lightning Bolt", trigger="manual", target_rule="enemy_character", timing="fast",
                 effects=[eff("deal_damage", 3)])]),
        spl(f"{S}-spell-berserker-cry", "Berserker Cry", 2, "burst", "Give all friendly Figures +1 Attack this turn.",
            [abi(f"{S}-sp3", "Berserker Cry", trigger="manual", timing="burst",
                 effects=[eff("grant_stats", attack=1, health=0, duration="turn", scope="all_friendly_figures")])]),
        spl(f"{S}-spell-rune-sight", "Rune Sight", 1, "burst", "Draw a card.",
            [abi(f"{S}-sp4", "Rune Sight", trigger="manual", timing="burst", effects=[eff("draw_cards", 1)])]),
        spl(f"{S}-spell-ragnarok-axe", "Ragnarok Axe", 3, "fast", "Deal 4 damage to an enemy Figure.",
            [abi(f"{S}-sp5", "Ragnarok Axe", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("deal_damage", 4)])]),
        spl(f"{S}-spell-loki-trick", "Loki's Trick", 1, "fast", "Return a friendly Figure to your hand. It costs 1 less.",
            [abi(f"{S}-sp6", "Loki's Trick", trigger="manual", target_rule="friendly_figure", timing="fast",
                 effects=[eff("return_to_hand", extra={"cost_reduction": 1, "side": "friendly"})])], rarity="rare"),
        spl(f"{S}-spell-valhalla-call", "Valhalla's Call", 3, "burst", "Draw 2 cards. Deal 1 damage to your Hero.",
            [abi(f"{S}-sp7", "Valhalla's Call", trigger="manual", timing="burst",
                 effects=[eff("draw_cards", 2), eff("deal_damage", 1, scope="friendly_hero")])]),
        spl(f"{S}-spell-frost-axe", "Frost Axe", 2, "fast", "Freeze an enemy Figure. Deal 1 damage to it.",
            [abi(f"{S}-sp8", "Frost Axe", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("freeze"), eff("deal_damage", 1)])]),
        # MODAL: Choose one
        spl(f"{S}-spell-odins-choice", "Odin's Choice", 2, "burst",
            "Choose: Deal 2 damage to the enemy Hero OR Draw a card.",
            [abi(f"{S}-sp9a", "Odin's Wrath", trigger="manual", target_rule="enemy_hero", timing="burst",
                 effects=[eff("deal_damage", 2, scope="enemy_hero")]),
             abi(f"{S}-sp9b", "Odin's Wisdom", trigger="manual", timing="burst",
                 effects=[eff("draw_cards", 1)])]),
        # RELICS (2) — 1 passive aggro, 1 activated
        rel(f"{S}-relic-horn", "Horn of Valhalla", 2,
            "The first time each turn a friendly Figure attacks the enemy Hero, deal 1 extra damage.",
            [abi(f"{S}-r1", "Horn of Valhalla", trigger="on_attack_hero", timing="passive",
                 effects=[eff("deal_damage", 1, scope="enemy_hero")], limit="once_each_turn")]),
        rel(f"{S}-relic-mjolnir", "Mjolnir Shard", 3,
            "Activate (1): Deal 2 damage to the enemy Hero. Once per turn.",
            [abi(f"{S}-r2", "Mjolnir Shard", trigger="manual", timing="slow", resource_cost=1,
                 effects=[eff("deal_damage", 2, scope="enemy_hero")], limit="once_each_turn")]),
        # TOKEN
        tok(f"{S}-token-warrior", "Spirit Warrior", 2, 1, ["rush"], "Rush."),
    ]


# ============================================================
# ANCIENT-EGYPTIAN: Control/Value
# More spells, activated relic for board clear, stronger death synergy
# ============================================================
def build_egyptian():
    S = "ancient-egyptian"
    return [
        hero(f"{S}-hero-isis", "Isis, Throne of Magic",
             "Hero Power - Ankh Blessing (2): Restore 2 Health to your Hero or a friendly Figure.",
             [abi(f"{S}-hero-1", "Ankh Blessing", trigger="manual", target_rule="friendly_character", timing="slow", resource_cost=2,
                  effects=[eff("heal", 2)])]),
        # 1-drop (1)
        fig(f"{S}-001", "Scarab Keeper", 1, 1, 2, [], "On play: Gain 1 Ritual Mana.",
            [abi(f"{S}-001-1", "Sacred Scarab", effects=[eff("gain_ritual_mana", 1)])]),
        # 2-drops (4)
        fig(f"{S}-002", "Khnum", 2, 2, 3, [], "On play: Give a friendly Figure +0/+1.",
            [abi(f"{S}-002-1", "Potter's Craft", target_rule="friendly_figure", effects=[eff("grant_stats", attack=0, health=1)])]),
        fig(f"{S}-003", "Bes", 2, 1, 4, ["guard"], "Guard."),
        fig(f"{S}-004", "Serket", 2, 2, 2, ["reborn"], "Reborn."),
        fig(f"{S}-005", "Temple Scribe", 2, 1, 3, [], "On play: Draw a card.",
            [abi(f"{S}-005-1", "Hieroglyphs", effects=[eff("draw_cards", 1)])]),
        # 3-drops (5)
        fig(f"{S}-006", "Ammit", 3, 3, 3, [], "On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-006-1", "Devour", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])]),
        fig(f"{S}-007", "Nephthys", 3, 2, 4, ["guard"], "Guard. Deathrattle: Draw a card.",
            [abi(f"{S}-007-1", "Mourner's Gift", trigger="on_death", effects=[eff("draw_cards", 1)])], rarity="rare"),
        fig(f"{S}-008", "Khepri", 3, 2, 3, ["reborn"], "Reborn. On play: Give a friendly Figure +1/+1.",
            [abi(f"{S}-008-1", "Dawn Renewal", target_rule="friendly_figure", effects=[eff("grant_stats", attack=1, health=1)])], rarity="rare"),
        fig(f"{S}-009", "Mummy Guard", 3, 2, 5, ["guard"], "Guard."),
        fig(f"{S}-010", "Priestess of Isis", 3, 2, 3, [], "On play: Restore 3 Health to your Hero.",
            [abi(f"{S}-010-1", "Sacred Prayer", effects=[eff("heal", 3, scope="friendly_hero")])]),
        # 4-drops (3)
        fig(f"{S}-011", "Bastet", 4, 3, 5, ["lifesteal"], "Lifesteal.", rarity="rare"),
        fig(f"{S}-012", "Sobek", 4, 4, 4, ["rush"], "Rush."),
        fig(f"{S}-013", "Hathor", 4, 2, 5, [], "On play: Heal all friendly Figures for 2 and draw a card.",
            [abi(f"{S}-013-1", "Nurture", effects=[eff("heal", 2, scope="all_friendly_figures"), eff("draw_cards", 1)])], rarity="rare"),
        # 5-drops (3)
        fig(f"{S}-014", "Anubis", 5, 4, 5, [], "On play: Return a Figure (cost 3-) from your discard to your hand.",
            [abi(f"{S}-014-1", "Embalm", effects=[eff("return_from_discard", extra={"max_cost": 3})])], rarity="rare"),
        fig(f"{S}-015", "Horus", 5, 5, 4, ["rush"], "Rush. On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-015-1", "Sky Judgment", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])], rarity="rare"),
        fig(f"{S}-016", "Sekhmet", 5, 4, 5, [], "On play: Deal 2 damage to all enemy Figures.",
            [abi(f"{S}-016-1", "War Goddess", target_rule="all_enemy_figures", effects=[eff("deal_damage", 2)])], rarity="rare"),
        # 6-drops (2)
        fig(f"{S}-017", "Osiris", 6, 4, 8, ["reborn"], "Reborn. Deathrattle: Summon a 2/2 Spirit.",
            [abi(f"{S}-017-1", "Eternal Return", trigger="on_death", effects=[eff("summon_token", card_id=f"{S}-token-spirit")])], rarity="legendary"),
        fig(f"{S}-018", "Ra", 6, 5, 7, [], "On play: Deal 3 damage to an enemy Figure. Restore 3 Health to your Hero.",
            [abi(f"{S}-018-1", "Solar Flare", target_rule="enemy_figure", effects=[eff("deal_damage", 3), eff("heal", 3, scope="friendly_hero")])], rarity="legendary"),
        # SPELLS (8) — control identity
        spl(f"{S}-spell-embalm", "Embalming Rite", 1, "burst", "Give a friendly Figure +0/+2.",
            [abi(f"{S}-sp1", "Embalming Rite", trigger="manual", target_rule="friendly_figure", timing="burst",
                 effects=[eff("grant_stats", attack=0, health=2)])]),
        spl(f"{S}-spell-ankh-shield", "Ankh Shield", 2, "fast", "Give a friendly Figure +0/+3 and Guard this turn.",
            [abi(f"{S}-sp2", "Ankh Shield", trigger="manual", target_rule="friendly_figure", timing="fast",
                 effects=[eff("grant_stats", attack=0, health=3, duration="turn"), eff("grant_keyword", keyword="guard", duration="turn")])]),
        spl(f"{S}-spell-book-dead", "Book of the Dead", 2, "burst", "Draw 2 cards.",
            [abi(f"{S}-sp3", "Book of the Dead", trigger="manual", timing="burst", effects=[eff("draw_cards", 2)])], rarity="rare"),
        spl(f"{S}-spell-plague", "Plague of Locusts", 5, "slow", "Deal 3 damage to all enemy Figures.",
            [abi(f"{S}-sp4", "Plague of Locusts", trigger="manual", target_rule="all_enemy_figures", timing="slow",
                 effects=[eff("deal_damage", 3)])], rarity="rare"),
        spl(f"{S}-spell-mummify", "Mummify", 3, "fast", "Freeze an enemy Figure and deal 2 damage to it.",
            [abi(f"{S}-sp5", "Mummify", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("freeze"), eff("deal_damage", 2)])]),
        spl(f"{S}-spell-solar-lash", "Solar Lash", 3, "fast", "Deal 3 damage to an enemy Figure. Restore 2 Health to your Hero.",
            [abi(f"{S}-sp6", "Solar Lash", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("deal_damage", 3), eff("heal", 2, scope="friendly_hero")])]),
        spl(f"{S}-spell-scarab-swarm", "Scarab Swarm", 3, "slow", "Summon two 1/1 Scarab tokens.",
            [abi(f"{S}-sp7", "Scarab Swarm", trigger="manual", timing="slow",
                 effects=[eff("summon_token", card_id=f"{S}-token-scarab"), eff("summon_token", card_id=f"{S}-token-scarab")])]),
        spl(f"{S}-spell-divine-shield", "Gift of the Nile", 1, "burst", "Give a friendly Figure Ward.",
            [abi(f"{S}-sp8", "Gift of the Nile", trigger="manual", target_rule="friendly_figure", timing="burst",
                 effects=[eff("grant_keyword", keyword="ward")])]),
        # MODAL: Choose one
        spl(f"{S}-spell-judgment-of-maat", "Judgment of Ma'at", 3, "fast",
            "Choose: Deal 3 damage to an enemy Figure OR Restore 4 Health to your Hero.",
            [abi(f"{S}-sp9a", "Destroy the Wicked", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("deal_damage", 3)]),
             abi(f"{S}-sp9b", "Bless the Worthy", trigger="manual", target_rule="friendly_hero", timing="fast",
                 effects=[eff("heal", 4)])]),
        # RELICS (2) — 1 passive value, 1 activated board clear
        rel(f"{S}-relic-canopic", "Canopic Jar", 2,
            "The first time a friendly Figure dies each turn, draw a card.",
            [abi(f"{S}-r1", "Canopic Jar", trigger="on_death", timing="passive",
                 effects=[eff("draw_cards", 1)], limit="once_each_turn")]),
        rel(f"{S}-relic-rod", "Rod of Osiris", 3,
            "Activate (2): Deal 1 damage to all enemy Figures. Once per turn.",
            [abi(f"{S}-r2", "Rod of Osiris", trigger="manual", timing="slow", resource_cost=2,
                 effects=[eff("deal_damage", 1, scope="all_enemy_figures")], limit="once_each_turn")]),
        # TOKENS
        tok(f"{S}-token-spirit", "Spirit of the Dead", 2, 2),
        tok(f"{S}-token-scarab", "Scarab", 1, 1),
    ]


# ============================================================
# ANCIENT-GREEK: Midrange/Spell-Tempo
# More spells, spell synergy relic, flexible game plan
# ============================================================
def build_greek():
    S = "ancient-greek"
    return [
        hero(f"{S}-hero-athena", "Athena, Goddess of Strategy",
             "Hero Power - Owl's Insight (2): Deal 1 damage to an enemy Figure. Draw a card.",
             [abi(f"{S}-hero-1", "Owl's Insight", trigger="manual", target_rule="enemy_figure", timing="slow", resource_cost=2,
                  effects=[eff("deal_damage", 1), eff("draw_cards", 1)])]),
        # 1-drops (3)
        fig(f"{S}-001", "Hermes", 1, 1, 2, [], "On play: Give a friendly Figure +1 Attack this turn.",
            [abi(f"{S}-001-1", "Swift Blessing", target_rule="friendly_figure", effects=[eff("grant_stats", attack=1, health=0, duration="turn")])]),
        fig(f"{S}-002", "Arachne", 1, 1, 1, [], "On play: Draw a card.",
            [abi(f"{S}-002-1", "Weaver", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-003", "Satyr", 1, 2, 1, [], ""),
        # 2-drops (4)
        fig(f"{S}-004", "Dionysus", 2, 2, 3, [], "On play: Draw a card.",
            [abi(f"{S}-004-1", "Revelry", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-005", "Artemis", 2, 3, 2, ["rush"], "Rush."),
        fig(f"{S}-006", "Pan", 2, 2, 2, [], "On play: Give a friendly Figure +1/+1.",
            [abi(f"{S}-006-1", "Wild Growth", target_rule="friendly_figure", effects=[eff("grant_stats", attack=1, health=1)])]),
        fig(f"{S}-007", "Chimera", 2, 3, 2, ["poisonous"], "Poisonous.", rarity="rare"),
        # 3-drops (4)
        fig(f"{S}-008", "Ares", 3, 4, 3, [], "On play: Deal 1 damage to an enemy Figure.",
            [abi(f"{S}-008-1", "War Cry", target_rule="enemy_figure", effects=[eff("deal_damage", 1)])]),
        fig(f"{S}-009", "Medusa", 3, 2, 4, [], "On play: Freeze an enemy Figure.",
            [abi(f"{S}-009-1", "Petrify", target_rule="enemy_figure", effects=[eff("freeze")])], rarity="rare"),
        fig(f"{S}-010", "Hephaestus", 3, 2, 4, [], "On play: Give a friendly Figure +2/+1.",
            [abi(f"{S}-010-1", "Forge", target_rule="friendly_figure", effects=[eff("grant_stats", attack=2, health=1)])], rarity="rare"),
        fig(f"{S}-011", "Pegasus", 3, 3, 2, ["rush"], "Rush. On play: Draw a card.",
            [abi(f"{S}-011-1", "Skyborne", effects=[eff("draw_cards", 1)])], rarity="rare"),
        # 4-drops (3)
        fig(f"{S}-012", "Achilles", 4, 5, 3, ["rush"], "Rush.",
            rarity="rare"),
        fig(f"{S}-013", "Apollo", 4, 3, 5, [], "On play: Deal 2 to an enemy Figure. Restore 2 Health.",
            [abi(f"{S}-013-1", "Solar Arrow", target_rule="enemy_figure",
                 effects=[eff("deal_damage", 2), eff("heal", 2, scope="friendly_hero")])], rarity="rare"),
        fig(f"{S}-014", "Hades", 4, 3, 5, [], "On play: Return a Figure (cost 3-) from your discard to hand.",
            [abi(f"{S}-014-1", "Underworld Gate", effects=[eff("return_from_discard", extra={"max_cost": 3})])], rarity="rare"),
        # 5-6 drops (3)
        fig(f"{S}-015", "Athena", 5, 4, 6, ["guard"], "Guard. On play: Give another Figure +1/+2 and Ward.",
            [abi(f"{S}-015-1", "Aegis", target_rule="other_friendly_figure",
                 effects=[eff("grant_stats", attack=1, health=2), eff("grant_keyword", keyword="ward")])], rarity="legendary"),
        fig(f"{S}-016", "Minotaur", 5, 5, 4, ["charge"], "Charge.", rarity="rare"),
        fig(f"{S}-017", "Zeus", 6, 5, 7, [], "On play: Deal 3 damage to an enemy Figure. Deal 2 to all other enemies.",
            [abi(f"{S}-017-1", "Thunderbolt", target_rule="enemy_figure",
                 effects=[eff("deal_damage", 3, extra={"on_kill_aoe": 2})])], rarity="legendary"),
        # SPELLS (9) — spell-heavy midrange identity
        spl(f"{S}-spell-phalanx", "Phalanx Formation", 2, "fast", "Give a friendly Figure +2/+2 this combat.",
            [abi(f"{S}-sp1", "Phalanx", trigger="manual", target_rule="friendly_figure", timing="fast",
                 effects=[eff("grant_stats", attack=2, health=2, duration="combat")])]),
        spl(f"{S}-spell-olympian-bolt", "Olympian Bolt", 2, "fast", "Deal 3 damage to an enemy Figure.",
            [abi(f"{S}-sp2", "Olympian Bolt", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("deal_damage", 3)])]),
        spl(f"{S}-spell-oracle-vision", "Oracle Vision", 1, "burst", "Draw a card. Gain 1 Ritual Mana.",
            [abi(f"{S}-sp3", "Oracle Vision", trigger="manual", timing="burst",
                 effects=[eff("draw_cards", 1), eff("gain_ritual_mana", 1)])]),
        spl(f"{S}-spell-aegis-ward", "Aegis Ward", 1, "burst", "Give a friendly Figure Ward.",
            [abi(f"{S}-sp4", "Aegis Ward", trigger="manual", target_rule="friendly_figure", timing="burst",
                 effects=[eff("grant_keyword", keyword="ward")])]),
        spl(f"{S}-spell-heroic-charge", "Heroic Charge", 3, "fast", "Give a friendly Figure +3 Attack and Rush this turn.",
            [abi(f"{S}-sp5", "Heroic Charge", trigger="manual", target_rule="friendly_figure", timing="fast",
                 effects=[eff("grant_stats", attack=3, health=0, duration="turn"), eff("grant_keyword", keyword="rush", duration="turn")])], rarity="rare"),
        spl(f"{S}-spell-odyssey", "Odyssey", 2, "fast", "Return an enemy Figure (cost 3-) to its owner's hand.",
            [abi(f"{S}-sp6", "Odyssey", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("return_to_hand", extra={"max_cost": 3})])]),
        spl(f"{S}-spell-hubris", "Hubris", 4, "fast", "Deal 2 damage to an enemy Figure. If it dies, draw 2 cards.",
            [abi(f"{S}-sp7", "Hubris", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("deal_damage", 2, extra={"on_kill_draw": 2})])], rarity="rare"),
        spl(f"{S}-spell-ambrosia", "Ambrosia", 3, "burst", "Restore 4 Health to your Hero. Draw a card.",
            [abi(f"{S}-sp8", "Ambrosia", trigger="manual", timing="burst",
                 effects=[eff("heal", 4, scope="friendly_hero"), eff("draw_cards", 1)])]),
        spl(f"{S}-spell-trojan-horse", "Trojan Horse", 4, "slow", "Summon a 3/3 Warrior with Rush.",
            [abi(f"{S}-sp9", "Trojan Horse", trigger="manual", timing="slow",
                 effects=[eff("summon_token", card_id=f"{S}-token-warrior")])]),
        # MODAL: Choose one
        spl(f"{S}-spell-gift-of-gods", "Gift of the Gods", 2, "fast",
            "Choose: Give a friendly Figure +2/+2 this combat OR Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-sp10a", "Blessing of Ares", trigger="manual", target_rule="friendly_figure", timing="fast",
                 effects=[eff("grant_stats", attack=2, health=2, duration="combat")]),
             abi(f"{S}-sp10b", "Wrath of Zeus", trigger="manual", target_rule="enemy_figure", timing="fast",
                 effects=[eff("deal_damage", 2)])]),
        # RELICS (2)
        rel(f"{S}-relic-aegis", "Aegis of Athena", 2,
            "After you cast a spell, give a random friendly Figure +1/+1.",
            [abi(f"{S}-r1", "Aegis of Athena", trigger="on_spell_cast", timing="passive",
                 effects=[eff("grant_stats", attack=1, health=1, scope="random_friendly_figure")])]),
        rel(f"{S}-relic-tripod", "Oracle's Tripod", 3,
            "Activate (1): Draw a card. Once per turn.",
            [abi(f"{S}-r2", "Oracle's Tripod", trigger="manual", timing="slow", resource_cost=1,
                 effects=[eff("draw_cards", 1)], limit="once_each_turn")]),
        # TOKENS
        tok(f"{S}-token-warrior", "Greek Warrior", 3, 3, ["rush"], "Rush."),
    ]


def finalize(cards, slug, set_code):
    for c in cards:
        c["culture_slug"] = slug
        c["set_code"] = set_code
    return {"culture_slug": slug, "set_code": set_code, "cards": cards}


def deck(hero_id, name, entries, notes=None):
    return {"hero_id": hero_id, "name": name, "notes": notes or [], "cards": entries}


def save(pack, deck_data, slug, deck_filename):
    pack_path = CARDS_DIR / f"{slug}-v1.json"
    pack_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  Pack: {pack_path.name} ({len(pack['cards'])} cards)")

    deck_path = DECKS_DIR / deck_filename
    deck_path.write_text(json.dumps(deck_data, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(e["count"] for e in deck_data["cards"])
    figs = sum(e["count"] for e in deck_data["cards"] if not any(k in e["id"] for k in ["spell", "relic"]))
    spls = sum(e["count"] for e in deck_data["cards"] if "spell" in e["id"])
    rels = sum(e["count"] for e in deck_data["cards"] if "relic" in e["id"])
    print(f"  Deck: {deck_filename} ({total} cards: {figs}fig/{spls}spl/{rels}rel)")


def main():
    S = "norse-viking"
    norse_pack = finalize(build_norse(), S, f"{S}-v1")
    # Deck A: Rush Burn (aggro, max face damage)
    norse_rush = deck(f"{S}-hero-thor", "Thor Rush Burn", [
        {"id": f"{S}-001", "count": 2}, {"id": f"{S}-002", "count": 2}, {"id": f"{S}-003", "count": 1},  # 1-drops: 5
        {"id": f"{S}-004", "count": 2}, {"id": f"{S}-006", "count": 2},  # 2-drops: 4
        {"id": f"{S}-009", "count": 2}, {"id": f"{S}-010", "count": 1},  # 3-drops: 3
        {"id": f"{S}-014", "count": 1},  # 4-drop charge: 1
        {"id": f"{S}-015", "count": 1},  # 5-drop finisher: 1
        {"id": f"{S}-spell-battle-rage", "count": 2},  # spells: 7
        {"id": f"{S}-spell-lightning-bolt", "count": 2},
        {"id": f"{S}-spell-rune-sight", "count": 1},
        {"id": f"{S}-spell-valhalla-call", "count": 1},
        {"id": f"{S}-spell-berserker-cry", "count": 1},
        {"id": f"{S}-spell-odins-choice", "count": 1},  # modal
        {"id": f"{S}-relic-horn", "count": 1}, {"id": f"{S}-relic-mjolnir", "count": 1},  # relics: 2
    ])  # need to recount - remove one fig to fit

    # Deck B: Midrange Storm (slower, more value)
    norse_mid = deck(f"{S}-hero-thor", "Thor Midrange Storm", [
        {"id": f"{S}-001", "count": 2}, {"id": f"{S}-003", "count": 2},  # 1-drops: 4
        {"id": f"{S}-004", "count": 2}, {"id": f"{S}-007", "count": 2},  # 2-drops: 4
        {"id": f"{S}-008", "count": 2}, {"id": f"{S}-011", "count": 1},  # 3-drops: 3
        {"id": f"{S}-012", "count": 1}, {"id": f"{S}-013", "count": 1},  # 4-drops: 2
        {"id": f"{S}-016", "count": 1},  # 6-drop: 1
        {"id": f"{S}-spell-battle-rage", "count": 1},  # spells: 7
        {"id": f"{S}-spell-lightning-bolt", "count": 2},
        {"id": f"{S}-spell-ragnarok-axe", "count": 1},
        {"id": f"{S}-spell-rune-sight", "count": 1},
        {"id": f"{S}-spell-frost-axe", "count": 1},
        {"id": f"{S}-spell-valhalla-call", "count": 1},
        {"id": f"{S}-relic-horn", "count": 1}, {"id": f"{S}-relic-mjolnir", "count": 1},  # relics: 2
    ])  # 14 figs + 8 spells + 2 relics = 24 -- wait let me count
    # 4+4+3+2+1 = 14 figs, 1+2+1+1+1+1 = 7 spells, 2 relics = 23. Need 1 more.
    norse_mid["cards"].append({"id": f"{S}-017", "count": 1})  # Odin
    # 15+7+2 = 24

    print("Norse:")
    save(norse_pack, norse_rush, S, f"{S}-thor-rush-burn.json")
    save(norse_pack, norse_mid, S, f"{S}-thor-midrange-storm.json")

    S = "ancient-egyptian"
    egypt_pack = finalize(build_egyptian(), S, f"{S}-v1")
    # Deck A: Reborn Control
    egypt_ctrl = deck(f"{S}-hero-isis", "Isis Reborn Control", [
        {"id": f"{S}-001", "count": 2},  # 1-drop: 2
        {"id": f"{S}-002", "count": 1}, {"id": f"{S}-004", "count": 2}, {"id": f"{S}-005", "count": 2},  # 2-drops: 5
        {"id": f"{S}-007", "count": 2}, {"id": f"{S}-008", "count": 2},  # 3-drops: 4
        {"id": f"{S}-011", "count": 1}, {"id": f"{S}-012", "count": 1},  # 4-drops: 2
        {"id": f"{S}-016", "count": 1},  # 5-drop: 1
        {"id": f"{S}-017", "count": 1},  # 6-drop: 1
        {"id": f"{S}-spell-embalm", "count": 2},  # spells: 7
        {"id": f"{S}-spell-ankh-shield", "count": 2},
        {"id": f"{S}-spell-book-dead", "count": 1},
        {"id": f"{S}-spell-mummify", "count": 1},
        {"id": f"{S}-spell-divine-shield", "count": 1},
        {"id": f"{S}-relic-canopic", "count": 1}, {"id": f"{S}-relic-rod", "count": 1},  # relics: 2
    ])  # 15+7+2 = 24 -- let me count: 2+5+4+2+1+1 = 15, 2+2+1+1+1 = 7, 2 = 24 ✓

    # Deck B: Token Swarm (wider board, value from deaths)
    egypt_swarm = deck(f"{S}-hero-isis", "Isis Token Swarm", [
        {"id": f"{S}-001", "count": 2},  # 1-drop: 2
        {"id": f"{S}-003", "count": 2}, {"id": f"{S}-004", "count": 2}, {"id": f"{S}-005", "count": 1},  # 2-drops: 5
        {"id": f"{S}-006", "count": 2}, {"id": f"{S}-009", "count": 1}, {"id": f"{S}-010", "count": 1},  # 3-drops: 4
        {"id": f"{S}-013", "count": 1},  # 4-drop: 1
        {"id": f"{S}-014", "count": 1},  # 5-drop: 1
        {"id": f"{S}-spell-embalm", "count": 1},  # spells: 7
        {"id": f"{S}-spell-scarab-swarm", "count": 2},
        {"id": f"{S}-spell-book-dead", "count": 1},
        {"id": f"{S}-spell-solar-lash", "count": 2},
        {"id": f"{S}-spell-divine-shield", "count": 1},
        {"id": f"{S}-relic-canopic", "count": 1}, {"id": f"{S}-relic-rod", "count": 1},  # relics: 2
    ])  # 2+5+4+1+1 = 13 figs, 1+2+1+2+1 = 7 spells, 2 relics = 22. Need 2 more.
    egypt_swarm["cards"].append({"id": f"{S}-015", "count": 1})  # Horus
    egypt_swarm["cards"].append({"id": f"{S}-018", "count": 1})  # Ra
    # 15+7+2 = 24

    print("Egyptian:")
    save(egypt_pack, egypt_ctrl, S, f"{S}-isis-reborn-control.json")
    save(egypt_pack, egypt_swarm, S, f"{S}-isis-token-swarm.json")

    S = "ancient-greek"
    greek_pack = finalize(build_greek(), S, f"{S}-v1")
    # Deck A: Spell Tempo
    greek_tempo = deck(f"{S}-hero-athena", "Athena Spell Tempo", [
        {"id": f"{S}-001", "count": 2}, {"id": f"{S}-002", "count": 2},  # 1-drops: 4
        {"id": f"{S}-004", "count": 2}, {"id": f"{S}-005", "count": 1},  # 2-drops: 3
        {"id": f"{S}-008", "count": 1}, {"id": f"{S}-010", "count": 1}, {"id": f"{S}-011", "count": 1},  # 3-drops: 3
        {"id": f"{S}-012", "count": 1},  # 4-drop: 1
        {"id": f"{S}-016", "count": 1},  # 5-drop charge: 1
        {"id": f"{S}-spell-phalanx", "count": 2},  # spells: 9
        {"id": f"{S}-spell-olympian-bolt", "count": 2},
        {"id": f"{S}-spell-oracle-vision", "count": 2},
        {"id": f"{S}-spell-aegis-ward", "count": 1},
        {"id": f"{S}-spell-odyssey", "count": 1},
        {"id": f"{S}-spell-heroic-charge", "count": 1},
        {"id": f"{S}-relic-aegis", "count": 1}, {"id": f"{S}-relic-tripod", "count": 1},  # relics: 2
    ])  # 4+3+3+1+1 = 12 -- need 1 more fig (min 14)
    # Actually rules say min 14 figures. 12 is too low. Let me add more.
    greek_tempo["cards"].append({"id": f"{S}-006", "count": 1})  # Pan
    greek_tempo["cards"].append({"id": f"{S}-003", "count": 1})  # Satyr
    # 14 figs + 9 spells + 2 relics = 25. One too many. Drop 1 spell.
    # Remove one Oracle Vision
    for e in greek_tempo["cards"]:
        if e["id"] == f"{S}-spell-oracle-vision" and e["count"] == 2:
            e["count"] = 1
            break
    # 14+8+2 = 24 ✓

    # Deck B: Midrange Value
    greek_value = deck(f"{S}-hero-athena", "Athena Midrange Value", [
        {"id": f"{S}-001", "count": 1}, {"id": f"{S}-002", "count": 2},  # 1-drops: 3
        {"id": f"{S}-004", "count": 2}, {"id": f"{S}-006", "count": 1}, {"id": f"{S}-007", "count": 1},  # 2-drops: 4
        {"id": f"{S}-009", "count": 1}, {"id": f"{S}-010", "count": 2}, {"id": f"{S}-011", "count": 1},  # 3-drops: 4
        {"id": f"{S}-013", "count": 1}, {"id": f"{S}-014", "count": 1},  # 4-drops: 2
        {"id": f"{S}-015", "count": 1},  # 5-drop: 1
        {"id": f"{S}-spell-phalanx", "count": 2},  # spells: 6
        {"id": f"{S}-spell-olympian-bolt", "count": 1},
        {"id": f"{S}-spell-ambrosia", "count": 1},
        {"id": f"{S}-spell-hubris", "count": 1},
        {"id": f"{S}-spell-aegis-ward", "count": 1},
        {"id": f"{S}-relic-aegis", "count": 1}, {"id": f"{S}-relic-tripod", "count": 1},  # relics: 2
    ])  # 3+4+4+2+1 = 14 figs, 2+1+1+1+1 = 6 spells, 2 relics = 22. Need 2 more.
    greek_value["cards"].append({"id": f"{S}-017", "count": 1})  # Zeus
    greek_value["cards"].append({"id": f"{S}-spell-oracle-vision", "count": 1})  # Oracle Vision
    # 15+7+2 = 24

    print("Greek:")
    save(greek_pack, greek_tempo, S, f"{S}-athena-spell-tempo.json")
    save(greek_pack, greek_value, S, f"{S}-athena-midrange-value.json")

    # Clean old decks
    for old in DECKS_DIR.glob("norse-viking-thor-storm-rush*"):
        old.unlink()
        print(f"  Removed old: {old.name}")
    for old in DECKS_DIR.glob("ancient-egyptian-isis-control*"):
        old.unlink()
        print(f"  Removed old: {old.name}")
    for old in DECKS_DIR.glob("ancient-greek-athena-midrange*"):
        old.unlink()
        print(f"  Removed old: {old.name}")


if __name__ == "__main__":
    main()
