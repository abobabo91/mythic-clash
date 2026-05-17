"""Build 7 new cultures with diverse archetypes.

Each culture has:
- ~25-30 cards in pack (more than deck slots = deckbuilding choices)
- 7-8 spells including 1 modal card
- 2 relics (1 passive, 1 activated)
- Unique mechanical identity
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"

NULL = {"attack": None, "health": None, "keyword": None, "duration": None, "scope": None, "pool": None, "card_id": None, "extra": {}}
def eff(kind, amount=None, **kw):
    e = {"kind": kind, "amount": amount, **NULL}; e.update(kw); return e
def abi(id, label, trigger="on_play", target_rule="none", effects=None, timing="slow", limit=None, resource_cost=None):
    return {"id": id, "label": label, "timing": timing, "trigger": trigger, "target_rule": target_rule,
            "resource_cost": resource_cost, "conditions": [], "effects": effects or [], "limit": limit}
def fig(id, name, cost, atk, hp, kw=None, text="", abis=None, rarity="common"):
    return {"id": id, "name": name, "card_type": "figure", "culture_slug": "", "rarity": rarity,
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": cost, "speed": None,
            "subtypes": [], "keywords": kw or [], "unique": rarity=="legendary", "legendary": rarity=="legendary",
            "token": False, "collectible": True, "set_code": "", "flavor_text": "", "attack": atk, "health": hp, "abilities": abis or []}
def spl(id, name, cost, speed, text, abis=None, rarity="common"):
    return {"id": id, "name": name, "card_type": "spell", "culture_slug": "", "rarity": rarity,
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": cost, "speed": speed,
            "subtypes": [], "keywords": [], "unique": False, "legendary": False, "token": False,
            "collectible": True, "set_code": "", "flavor_text": "", "attack": None, "health": None, "abilities": abis or []}
def rel(id, name, cost, text, abis=None, rarity="rare"):
    return {"id": id, "name": name, "card_type": "relic", "culture_slug": "", "rarity": rarity,
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": cost, "speed": None,
            "subtypes": [], "keywords": [], "unique": False, "legendary": False, "token": False,
            "collectible": True, "set_code": "", "flavor_text": "", "attack": None, "health": None, "abilities": abis or []}
def tok(id, name, atk, hp, kw=None, text="", abis=None):
    return {"id": id, "name": name, "card_type": "token", "culture_slug": "", "rarity": "token",
            "alignment": "neutral", "traits": [], "rules_text": text, "cost": 0, "speed": None,
            "subtypes": [], "keywords": kw or [], "unique": False, "legendary": False, "token": True,
            "collectible": False, "set_code": "", "flavor_text": "", "attack": atk, "health": hp, "abilities": abis or []}
def hero(id, name, text, abis):
    return {"id": id, "name": name, "card_type": "hero", "culture_slug": "", "rarity": "legendary",
            "alignment": "light", "traits": [], "rules_text": text, "cost": None, "speed": None,
            "subtypes": [], "keywords": [], "unique": True, "legendary": True, "token": False,
            "collectible": True, "set_code": "", "flavor_text": "", "attack": None, "health": None, "abilities": abis}


# ============================================================
# 1. JAPANESE SHINTO — Token/Swarm
# Wide boards, mass buffs, sacrifice for value
# ============================================================
def build_japanese():
    S = "japanese-shinto"
    return [
        hero(f"{S}-hero", "Amaterasu, Sun Goddess",
             "Hero Power (2): Summon a 1/1 Kami Spirit.",
             [abi(f"{S}-h1", "Divine Light", trigger="manual", timing="slow", resource_cost=2,
                  effects=[eff("summon_token", card_id=f"{S}-tok-kami")])]),
        fig(f"{S}-001", "Fox Messenger", 1, 1, 1, [], "On play: Draw a card.",
            [abi(f"{S}-01", "Swift Message", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-002", "Shrine Maiden", 1, 1, 2, [], ""),
        fig(f"{S}-003", "Kitsune", 2, 2, 2, [], "On play: Summon a 1/1 Kami Spirit.",
            [abi(f"{S}-03", "Fox Fire", effects=[eff("summon_token", card_id=f"{S}-tok-kami")])]),
        fig(f"{S}-004", "Tanuki", 2, 2, 3, [], "On play: Give a friendly Figure +1 Health.",
            [abi(f"{S}-04", "Shape Gift", target_rule="friendly_figure", effects=[eff("grant_stats", attack=0, health=1)])]),
        fig(f"{S}-005", "Tengu", 3, 3, 2, ["rush"], "Rush."),
        fig(f"{S}-006", "Oni", 3, 4, 3, [], "On play: Deal 1 damage to an enemy Figure.",
            [abi(f"{S}-06", "Demon Strike", target_rule="enemy_figure", effects=[eff("deal_damage", 1)])]),
        fig(f"{S}-007", "Raijin", 4, 3, 4, [], "On play: Deal 1 damage to all enemy Figures.",
            [abi(f"{S}-07", "Thunder Drum", target_rule="all_enemy_figures", effects=[eff("deal_damage", 1)])]),
        fig(f"{S}-008", "Fujin", 4, 4, 4, ["rush"], "Rush."),
        fig(f"{S}-009", "Susanoo", 5, 5, 5, [], "On play: Summon two 1/1 Kami Spirits.",
            [abi(f"{S}-09", "Storm Summon", effects=[eff("summon_token", card_id=f"{S}-tok-kami"), eff("summon_token", card_id=f"{S}-tok-kami")])], rarity="legendary"),
        fig(f"{S}-010", "Tsukuyomi", 6, 4, 7, [], "On play: Give all friendly Figures +1/+1.",
            [abi(f"{S}-10", "Moon Blessing", effects=[eff("grant_stats", attack=1, health=1, scope="all_friendly_figures")])], rarity="legendary"),
        spl(f"{S}-sp-rally", "Kami Rally", 2, "burst", "Give all friendly Figures +1 Attack this turn.",
            [abi(f"{S}-s1", "Kami Rally", trigger="manual", timing="burst", effects=[eff("grant_stats", attack=1, health=0, duration="turn", scope="all_friendly_figures")])]),
        spl(f"{S}-sp-spirit-wave", "Spirit Wave", 3, "slow", "Summon three 1/1 Kami Spirits.",
            [abi(f"{S}-s2", "Spirit Wave", trigger="manual", timing="slow", effects=[eff("summon_token", card_id=f"{S}-tok-kami"), eff("summon_token", card_id=f"{S}-tok-kami"), eff("summon_token", card_id=f"{S}-tok-kami")])]),
        spl(f"{S}-sp-divine-wind", "Divine Wind", 2, "fast", "Give a friendly Figure +1/+2 this combat.",
            [abi(f"{S}-s3", "Divine Wind", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=1, health=2, duration="combat")])]),
        spl(f"{S}-sp-purify", "Purify", 3, "fast", "Deal 2 damage to an enemy Figure. If it dies, summon a 1/1 Kami.",
            [abi(f"{S}-s4", "Purify", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 2, extra={"on_kill_summon": f"{S}-tok-kami"})])]),
        spl(f"{S}-sp-offering", "Sacred Offering", 1, "burst", "Draw a card.",
            [abi(f"{S}-s5", "Sacred Offering", trigger="manual", timing="burst", effects=[eff("draw_cards", 1)])]),
        spl(f"{S}-sp-modal", "Blessing of the Kami", 2, "fast",
            "Choose: Give all friendly Figures +0/+1 OR Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-s6a", "Strengthen All", trigger="manual", timing="fast", effects=[eff("grant_stats", attack=0, health=1, scope="all_friendly_figures")]),
             abi(f"{S}-s6b", "Kami Strike", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 2)])]),
        rel(f"{S}-rel-torii", "Torii Gate", 2, "After you summon a token, give it +1/+1.",
            [abi(f"{S}-r1", "Torii Gate", trigger="on_summon_token", timing="passive", effects=[eff("grant_stats", attack=1, health=1)])]),
        rel(f"{S}-rel-drum", "Taiko Drum", 3, "Activate (1): Give all friendly Figures +1 Attack this turn. Once per turn.",
            [abi(f"{S}-r2", "Taiko Drum", trigger="manual", timing="slow", resource_cost=1, effects=[eff("grant_stats", attack=1, health=0, duration="turn", scope="all_friendly_figures")], limit="once_each_turn")]),
        tok(f"{S}-tok-kami", "Kami Spirit", 1, 1),
    ]

# ============================================================
# 2. CELTIC IRISH — Trickery/Bounce
# Return to hand for replay value, tempo disruption
# ============================================================
def build_celtic():
    S = "celtic-irish"
    return [
        hero(f"{S}-hero", "Morrigan, Phantom Queen",
             "Hero Power (2): Return a friendly Figure (cost 2-) to your hand. Draw a card.",
             [abi(f"{S}-h1", "Fade", trigger="manual", target_rule="friendly_figure", timing="slow", resource_cost=2,
                  effects=[eff("return_to_hand", extra={"side": "friendly", "max_cost": 2}), eff("draw_cards", 1)])]),
        fig(f"{S}-001", "Will-o-Wisp", 1, 1, 1, [], "On play: Deal 1 damage to an enemy Figure.",
            [abi(f"{S}-01", "Flicker", target_rule="enemy_figure", effects=[eff("deal_damage", 1)])]),
        fig(f"{S}-002", "Leprechaun", 1, 1, 2, [], "On play: Gain 1 Ritual Mana.",
            [abi(f"{S}-02", "Gold Trick", effects=[eff("gain_ritual_mana", 1)])]),
        fig(f"{S}-003", "Selkie", 2, 2, 3, [], "On play: Draw a card.",
            [abi(f"{S}-03", "Sea Story", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-004", "Banshee", 2, 3, 2, [], "On play: Freeze an enemy Figure.",
            [abi(f"{S}-04", "Wail", target_rule="enemy_figure", effects=[eff("freeze")])]),
        fig(f"{S}-005", "Cu Chulainn", 3, 4, 3, ["rush"], "Rush.",  rarity="rare"),
        fig(f"{S}-006", "Brigid", 3, 2, 4, [], "On play: Restore 3 Health to your Hero. Draw a card.",
            [abi(f"{S}-06", "Hearthfire", effects=[eff("heal", 3, scope="friendly_hero"), eff("draw_cards", 1)])], rarity="rare"),
        fig(f"{S}-007", "Dagda", 4, 3, 5, [], "On play: Return an enemy Figure (cost 3-) to its owner's hand.",
            [abi(f"{S}-07", "Cauldron Bounce", target_rule="enemy_figure", effects=[eff("return_to_hand", extra={"max_cost": 3})])], rarity="rare"),
        fig(f"{S}-008", "Lugh", 4, 4, 4, [], "On play: Deal 2 damage to an enemy Figure. Give a friendly Figure +1/+1.",
            [abi(f"{S}-08", "Many Skills", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])], rarity="rare"),
        fig(f"{S}-009", "Nuada", 5, 5, 5, ["guard"], "Guard. On play: Draw a card.",
            [abi(f"{S}-09", "Silver Hand", effects=[eff("draw_cards", 1)])], rarity="legendary"),
        fig(f"{S}-010", "Danu", 6, 4, 7, [], "On play: Return all enemy Figures (cost 2-) to their owner's hand.",
            [abi(f"{S}-10", "Mother's Wrath", effects=[eff("return_to_hand", extra={"max_cost": 2, "scope": "all_enemy"})])], rarity="legendary"),
        spl(f"{S}-sp-trick", "Fairy Trick", 1, "fast", "Return a friendly Figure to your hand. It costs 1 less this turn.",
            [abi(f"{S}-s1", "Fairy Trick", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("return_to_hand", extra={"cost_reduction": 1, "side": "friendly"})])]),
        spl(f"{S}-sp-mist", "Celtic Mist", 2, "fast", "Give a friendly Figure Stealth until your next turn.",
            [abi(f"{S}-s2", "Celtic Mist", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_keyword", keyword="stealth", duration="turn")])]),
        spl(f"{S}-sp-bolt", "Druid's Lightning", 2, "fast", "Deal 3 damage to an enemy Figure.",
            [abi(f"{S}-s3", "Druid's Lightning", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 3)])]),
        spl(f"{S}-sp-cauldron", "Cauldron Brew", 3, "burst", "Draw 2 cards. Gain 1 Ritual Mana.",
            [abi(f"{S}-s4", "Cauldron Brew", trigger="manual", timing="burst", effects=[eff("draw_cards", 2), eff("gain_ritual_mana", 1)])]),
        spl(f"{S}-sp-ward", "Ogham Shield", 1, "burst", "Give a friendly Figure Ward.",
            [abi(f"{S}-s5", "Ogham Shield", trigger="manual", target_rule="friendly_figure", timing="burst", effects=[eff("grant_keyword", keyword="ward")])]),
        spl(f"{S}-sp-modal", "Morrigan's Choice", 3, "fast",
            "Choose: Return an enemy Figure (cost 4-) to hand OR Deal 2 damage to all enemy Figures.",
            [abi(f"{S}-s6a", "Phantom Bounce", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("return_to_hand", extra={"max_cost": 4})]),
             abi(f"{S}-s6b", "Crow Storm", trigger="manual", target_rule="all_enemy_figures", timing="fast", effects=[eff("deal_damage", 2)])]),
        rel(f"{S}-rel-cauldron", "Dagda's Cauldron", 2, "After you return a card to hand, draw a card. Once per turn.",
            [abi(f"{S}-r1", "Dagda's Cauldron", trigger="on_return_to_hand", timing="passive", effects=[eff("draw_cards", 1)], limit="once_each_turn")]),
        rel(f"{S}-rel-stone", "Lia Fail", 3, "Activate (2): Return a friendly Figure (cost 3-) to hand and summon a 2/2 Sidhe. Once per turn.",
            [abi(f"{S}-r2", "Lia Fail", trigger="manual", timing="slow", resource_cost=2, effects=[eff("return_to_hand", extra={"side": "friendly", "max_cost": 3}), eff("summon_token", card_id=f"{S}-tok-sidhe")], limit="once_each_turn")]),
        tok(f"{S}-tok-sidhe", "Sidhe Warrior", 2, 2),
    ]

# ============================================================
# 3. VEDIC HINDU — Ramp/Big
# Mana acceleration, huge late-game, overwhelm
# ============================================================
def build_vedic():
    S = "vedic-hindu"
    return [
        hero(f"{S}-hero", "Vishnu, The Preserver",
             "Hero Power (2): Gain 1 Ritual Mana. Give a friendly Figure +0/+1.",
             [abi(f"{S}-h1", "Preserve", trigger="manual", target_rule="friendly_figure", timing="slow", resource_cost=2,
                  effects=[eff("gain_ritual_mana", 1), eff("grant_stats", attack=0, health=1)])]),
        fig(f"{S}-001", "Devotee", 1, 1, 2, [], "On play: Gain 1 Ritual Mana.",
            [abi(f"{S}-01", "Prayer", effects=[eff("gain_ritual_mana", 1)])]),
        fig(f"{S}-002", "Temple Monkey", 2, 2, 3, [], "On play: Draw a card.",
            [abi(f"{S}-02", "Curiosity", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-003", "Naga", 2, 1, 4, ["guard"], "Guard."),
        fig(f"{S}-004", "Yaksha", 3, 2, 4, [], "On play: Gain 1 Ritual Mana. Draw a card.",
            [abi(f"{S}-04", "Forest Gift", effects=[eff("gain_ritual_mana", 1), eff("draw_cards", 1)])], rarity="rare"),
        fig(f"{S}-005", "Garuda", 3, 3, 3, ["rush"], "Rush."),
        fig(f"{S}-006", "Hanuman", 4, 4, 4, ["rush"], "Rush. On play: Give another friendly Figure +1 Attack.",
            [abi(f"{S}-06", "Valor", target_rule="other_friendly_figure", effects=[eff("grant_stats", attack=1, health=0)])], rarity="rare"),
        fig(f"{S}-007", "Ganesha", 4, 2, 6, ["guard"], "Guard. On play: Draw a card.",
            [abi(f"{S}-07", "Wisdom", effects=[eff("draw_cards", 1)])], rarity="rare"),
        fig(f"{S}-008", "Indra", 5, 5, 5, ["overwhelm"], "Overwhelm. On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-08", "Thunderbolt", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])], rarity="rare"),
        fig(f"{S}-009", "Shiva", 6, 6, 6, ["overwhelm"], "Overwhelm. On play: Deal 2 damage to all enemy Figures.",
            [abi(f"{S}-09", "Dance of Destruction", target_rule="all_enemy_figures", effects=[eff("deal_damage", 2)])], rarity="legendary"),
        fig(f"{S}-010", "Brahma", 7, 5, 8, [], "On play: Draw 2 cards. Restore 5 Health to your Hero.",
            [abi(f"{S}-10", "Creation", effects=[eff("draw_cards", 2), eff("heal", 5, scope="friendly_hero")])], rarity="legendary"),
        spl(f"{S}-sp-mantra", "Sacred Mantra", 1, "burst", "Gain 2 Ritual Mana.",
            [abi(f"{S}-s1", "Sacred Mantra", trigger="manual", timing="burst", effects=[eff("gain_ritual_mana", 2)])]),
        spl(f"{S}-sp-flame", "Agni's Flame", 2, "fast", "Deal 3 damage to any enemy.",
            [abi(f"{S}-s2", "Agni's Flame", trigger="manual", target_rule="enemy_character", timing="fast", effects=[eff("deal_damage", 3)])]),
        spl(f"{S}-sp-shield", "Dharma Shield", 2, "fast", "Give a friendly Figure +0/+3 this combat.",
            [abi(f"{S}-s3", "Dharma Shield", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=0, health=3, duration="combat")])]),
        spl(f"{S}-sp-sight", "Third Eye", 2, "burst", "Draw 2 cards.",
            [abi(f"{S}-s4", "Third Eye", trigger="manual", timing="burst", effects=[eff("draw_cards", 2)])], rarity="rare"),
        spl(f"{S}-sp-smite", "Divine Smite", 4, "slow", "Deal 4 damage to an enemy Figure.",
            [abi(f"{S}-s5", "Divine Smite", trigger="manual", target_rule="enemy_figure", timing="slow", effects=[eff("deal_damage", 4)])]),
        spl(f"{S}-sp-modal", "Trimurti's Will", 3, "fast",
            "Choose: Deal 3 damage to an enemy Figure OR Give a friendly Figure +2/+2.",
            [abi(f"{S}-s6a", "Shiva's Wrath", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 3)]),
             abi(f"{S}-s6b", "Brahma's Gift", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=2, health=2)])]),
        rel(f"{S}-rel-lotus", "Lotus Throne", 2, "At the start of your turn, if you have 2+ Ritual Mana, draw a card.",
            [abi(f"{S}-r1", "Lotus Throne", trigger="on_turn_start", timing="passive", effects=[eff("draw_cards", 1)])]),
        rel(f"{S}-rel-trident", "Shiva's Trident", 3, "Activate (2): Deal 3 damage to an enemy Figure. Once per turn.",
            [abi(f"{S}-r2", "Shiva's Trident", trigger="manual", timing="slow", resource_cost=2, effects=[eff("deal_damage", 3, scope="enemy_figure")], limit="once_each_turn")]),
    ]

# ============================================================
# 4. HAITIAN VODOU — Death/Combo
# Death triggers chain, sacrifice for power
# ============================================================
def build_haitian():
    S = "haitian-vodou"
    return [
        hero(f"{S}-hero", "Baron Samedi",
             "Hero Power (2): Deal 1 damage to a friendly Figure. Draw a card.",
             [abi(f"{S}-h1", "Death Touch", trigger="manual", target_rule="friendly_figure", timing="slow", resource_cost=2,
                  effects=[eff("deal_damage", 1), eff("draw_cards", 1)])]),
        fig(f"{S}-001", "Zombie Servant", 1, 2, 1, [], "Deathrattle: Deal 1 damage to the enemy Hero.",
            [abi(f"{S}-01", "Curse", trigger="on_death", effects=[eff("deal_damage", 1, scope="enemy_hero")])]),
        fig(f"{S}-002", "Houngan", 1, 1, 2, [], "On play: Draw a card.",
            [abi(f"{S}-02", "Spirit Call", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-003", "Erzulie", 2, 2, 3, ["lifesteal"], "Lifesteal."),
        fig(f"{S}-004", "Ti Jean", 2, 3, 1, [], "Deathrattle: Summon a 1/1 Spirit.",
            [abi(f"{S}-04", "Spirit Legacy", trigger="on_death", effects=[eff("summon_token", card_id=f"{S}-tok-spirit")])]),
        fig(f"{S}-005", "Loa Rider", 3, 3, 3, [], "On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-05", "Spirit Bolt", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])]),
        fig(f"{S}-006", "Mambo", 3, 2, 4, [], "Deathrattle: Draw 2 cards.",
            [abi(f"{S}-06", "Knowledge Beyond", trigger="on_death", effects=[eff("draw_cards", 2)])], rarity="rare"),
        fig(f"{S}-007", "Papa Legba", 4, 3, 5, [], "On play: Return a Figure (cost 3-) from your discard to hand.",
            [abi(f"{S}-07", "Crossroads", effects=[eff("return_from_discard", extra={"max_cost": 3})])], rarity="rare"),
        fig(f"{S}-008", "Ogou", 4, 5, 3, ["rush"], "Rush.", rarity="rare"),
        fig(f"{S}-009", "Damballa", 5, 4, 6, [], "On play: Deal 1 damage to all Figures (friendly and enemy).",
            [abi(f"{S}-09", "Serpent Wave", effects=[eff("deal_damage", 1, scope="all_figures")])], rarity="rare"),
        fig(f"{S}-010", "Baron Samedi", 6, 5, 7, [], "On play: Destroy a friendly Figure. Deal its Attack as damage to an enemy Figure.",
            [abi(f"{S}-10", "Death Sacrifice", target_rule="friendly_figure", effects=[eff("destroy", extra={"deal_attack_damage_to_enemy": True})])], rarity="legendary"),
        spl(f"{S}-sp-hex", "Vodou Hex", 2, "fast", "Deal 3 damage to an enemy Figure.",
            [abi(f"{S}-s1", "Vodou Hex", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 3)])]),
        spl(f"{S}-sp-ritual", "Dark Ritual", 1, "burst", "Deal 2 damage to your Hero. Draw 2 cards.",
            [abi(f"{S}-s2", "Dark Ritual", trigger="manual", timing="burst", effects=[eff("deal_damage", 2, scope="friendly_hero"), eff("draw_cards", 2)])]),
        spl(f"{S}-sp-possess", "Possession", 3, "fast", "Freeze an enemy Figure. Deal 2 damage to it.",
            [abi(f"{S}-s3", "Possession", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("freeze"), eff("deal_damage", 2)])]),
        spl(f"{S}-sp-rebirth", "Spirit Rebirth", 2, "burst", "Give a friendly Figure Reborn.",
            [abi(f"{S}-s4", "Spirit Rebirth", trigger="manual", target_rule="friendly_figure", timing="burst", effects=[eff("grant_keyword", keyword="reborn")])]),
        spl(f"{S}-sp-draw", "Ancestor's Whisper", 1, "burst", "Draw a card.",
            [abi(f"{S}-s5", "Ancestor's Whisper", trigger="manual", timing="burst", effects=[eff("draw_cards", 1)])]),
        spl(f"{S}-sp-modal", "Loa's Judgment", 3, "fast",
            "Choose: Deal 4 damage to an enemy Figure OR Restore 4 Health and draw a card.",
            [abi(f"{S}-s6a", "Punish", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 4)]),
             abi(f"{S}-s6b", "Heal", trigger="manual", timing="fast", effects=[eff("heal", 4, scope="friendly_hero"), eff("draw_cards", 1)])]),
        rel(f"{S}-rel-altar", "Vodou Altar", 2, "The first time a friendly Figure dies each turn, deal 2 damage to the enemy Hero.",
            [abi(f"{S}-r1", "Vodou Altar", trigger="on_death", timing="passive", effects=[eff("deal_damage", 2, scope="enemy_hero")], limit="once_each_turn")]),
        rel(f"{S}-rel-drum", "Ritual Drum", 3, "Activate (1): Deal 1 damage to a friendly Figure. Give it +2 Attack. Once per turn.",
            [abi(f"{S}-r2", "Ritual Drum", trigger="manual", target_rule="friendly_figure", timing="slow", resource_cost=1,
                 effects=[eff("deal_damage", 1), eff("grant_stats", attack=2, health=0)], limit="once_each_turn")]),
        tok(f"{S}-tok-spirit", "Restless Spirit", 1, 1),
    ]

# ============================================================
# 5. AZTEC MEXICA — Sacrifice Aggro
# Spend health for power, all-in burst
# ============================================================
def build_aztec():
    S = "aztec-mexica"
    return [
        hero(f"{S}-hero", "Huitzilopochtli, Sun of War",
             "Hero Power (2): Deal 2 damage to an enemy Figure. Deal 1 damage to your Hero.",
             [abi(f"{S}-h1", "Blood Sun", trigger="manual", target_rule="enemy_figure", timing="slow", resource_cost=2,
                  effects=[eff("deal_damage", 2), eff("deal_damage", 1, scope="friendly_hero")])]),
        fig(f"{S}-001", "Eagle Warrior", 1, 2, 1, [], ""),
        fig(f"{S}-002", "Jaguar Scout", 1, 1, 1, ["rush"], "Rush."),
        fig(f"{S}-003", "Blood Priest", 2, 2, 2, [], "On play: Deal 1 damage to your Hero. Draw a card.",
            [abi(f"{S}-03", "Blood Draw", effects=[eff("deal_damage", 1, scope="friendly_hero"), eff("draw_cards", 1)])]),
        fig(f"{S}-004", "Obsidian Knight", 2, 3, 2, ["overwhelm"], "Overwhelm."),
        fig(f"{S}-005", "Serpent Dancer", 3, 4, 2, ["rush"], "Rush."),
        fig(f"{S}-006", "Skull Rack", 3, 2, 4, [], "On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-06", "Skull Throw", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])]),
        fig(f"{S}-007", "Tlaloc Priest", 3, 3, 3, [], "On play: Deal 2 damage to your Hero. Draw 2 cards.",
            [abi(f"{S}-07", "Rain Sacrifice", effects=[eff("deal_damage", 2, scope="friendly_hero"), eff("draw_cards", 2)])], rarity="rare"),
        fig(f"{S}-008", "Tezcatlipoca", 4, 5, 3, ["charge"], "Charge.", rarity="rare"),
        fig(f"{S}-009", "Quetzalcoatl", 5, 4, 5, ["overwhelm"], "Overwhelm. On play: Deal 3 damage to an enemy Figure.",
            [abi(f"{S}-09", "Feathered Serpent", target_rule="enemy_figure", effects=[eff("deal_damage", 3)])], rarity="rare"),
        fig(f"{S}-010", "Mictlantecuhtli", 6, 6, 5, ["overwhelm", "charge"], "Charge. Overwhelm. On play: Deal 3 damage to your Hero.",
            [abi(f"{S}-10", "Death Lord", effects=[eff("deal_damage", 3, scope="friendly_hero")])], rarity="legendary"),
        spl(f"{S}-sp-sacrifice", "Blood Sacrifice", 1, "burst", "Deal 2 damage to your Hero. Deal 3 damage to an enemy Figure.",
            [abi(f"{S}-s1", "Blood Sacrifice", trigger="manual", target_rule="enemy_figure", timing="burst", effects=[eff("deal_damage", 2, scope="friendly_hero"), eff("deal_damage", 3)])]),
        spl(f"{S}-sp-sun-bolt", "Sun Bolt", 2, "fast", "Deal 3 damage to any enemy.",
            [abi(f"{S}-s2", "Sun Bolt", trigger="manual", target_rule="enemy_character", timing="fast", effects=[eff("deal_damage", 3)])]),
        spl(f"{S}-sp-rage", "Warrior's Rage", 1, "fast", "Give a friendly Figure +3 Attack this combat.",
            [abi(f"{S}-s3", "Warrior's Rage", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=3, health=0, duration="combat")])]),
        spl(f"{S}-sp-obsidian", "Obsidian Edge", 2, "burst", "Give a friendly Figure +2 Attack and Overwhelm this turn.",
            [abi(f"{S}-s4", "Obsidian Edge", trigger="manual", target_rule="friendly_figure", timing="burst", effects=[eff("grant_stats", attack=2, health=0, duration="turn"), eff("grant_keyword", keyword="overwhelm", duration="turn")])]),
        spl(f"{S}-sp-draw", "War Chant", 1, "burst", "Draw a card.",
            [abi(f"{S}-s5", "War Chant", trigger="manual", timing="burst", effects=[eff("draw_cards", 1)])]),
        spl(f"{S}-sp-modal", "Sun or Moon", 2, "fast",
            "Choose: Deal 2 damage to the enemy Hero OR Deal 2 damage to your Hero and draw 2 cards.",
            [abi(f"{S}-s6a", "Sun Strike", trigger="manual", target_rule="enemy_hero", timing="fast", effects=[eff("deal_damage", 2, scope="enemy_hero")]),
             abi(f"{S}-s6b", "Moon's Price", trigger="manual", timing="fast", effects=[eff("deal_damage", 2, scope="friendly_hero"), eff("draw_cards", 2)])]),
        rel(f"{S}-rel-altar", "Altar of the Sun", 2, "The first time each turn you take self-damage, give a random friendly Figure +1/+1.",
            [abi(f"{S}-r1", "Altar of the Sun", trigger="on_self_damage", timing="passive", effects=[eff("grant_stats", attack=1, health=1, scope="random_friendly_figure")], limit="once_each_turn")]),
        rel(f"{S}-rel-knife", "Obsidian Knife", 3, "Activate (0): Deal 1 damage to your Hero. Deal 2 damage to an enemy Figure. Once per turn.",
            [abi(f"{S}-r2", "Obsidian Knife", trigger="manual", timing="slow", resource_cost=0,
                 effects=[eff("deal_damage", 1, scope="friendly_hero"), eff("deal_damage", 2)], limit="once_each_turn")]),
    ]

# ============================================================
# 6. CHINESE — Harmony/Balance
# Gains when board is balanced, many modal cards
# ============================================================
def build_chinese():
    S = "ancient-chinese"
    return [
        hero(f"{S}-hero", "Jade Emperor",
             "Hero Power (2): Gain 2 Armor. If you have more Figures than the enemy, draw a card instead.",
             [abi(f"{S}-h1", "Celestial Decree", trigger="manual", timing="slow", resource_cost=2,
                  effects=[eff("gain_armor", 2)])]),
        fig(f"{S}-001", "Scholar", 1, 1, 2, [], "On play: Draw a card.",
            [abi(f"{S}-01", "Study", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-002", "Dragon Whelp", 2, 2, 3, [], ""),
        fig(f"{S}-003", "Jade Warrior", 2, 2, 2, ["rush"], "Rush."),
        fig(f"{S}-004", "Monkey King", 3, 3, 3, [], "On play: Give a friendly Figure +1/+1.",
            [abi(f"{S}-04", "Mischief", target_rule="friendly_figure", effects=[eff("grant_stats", attack=1, health=1)])]),
        fig(f"{S}-005", "Phoenix", 3, 2, 3, ["reborn"], "Reborn."),
        fig(f"{S}-006", "Iron Fan", 3, 3, 2, ["rush"], "Rush. On play: Draw a card.",
            [abi(f"{S}-06", "Wind Fan", effects=[eff("draw_cards", 1)])], rarity="rare"),
        fig(f"{S}-007", "Erlang Shen", 4, 4, 4, ["rush"], "Rush. On play: Deal 1 damage to an enemy Figure.",
            [abi(f"{S}-07", "Third Eye", target_rule="enemy_figure", effects=[eff("deal_damage", 1)])], rarity="rare"),
        fig(f"{S}-008", "Guan Yu", 4, 3, 5, ["guard"], "Guard."),
        fig(f"{S}-009", "Nezha", 5, 5, 4, ["rush"], "Rush. On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-09", "Fire Wheels", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])], rarity="rare"),
        fig(f"{S}-010", "Azure Dragon", 6, 5, 7, [], "On play: Deal 2 damage to all enemy Figures. Draw a card.",
            [abi(f"{S}-10", "Storm Breath", target_rule="all_enemy_figures", effects=[eff("deal_damage", 2), eff("draw_cards", 1)])], rarity="legendary"),
        spl(f"{S}-sp-harmony", "Celestial Harmony", 2, "fast",
            "Choose: Give a friendly Figure +2/+2 this combat OR Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-s1a", "Yang", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=2, health=2, duration="combat")]),
             abi(f"{S}-s1b", "Yin", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 2)])]),
        spl(f"{S}-sp-jade", "Jade Shield", 2, "fast", "Give a friendly Figure +0/+3 and Guard this turn.",
            [abi(f"{S}-s2", "Jade Shield", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=0, health=3, duration="turn"), eff("grant_keyword", keyword="guard", duration="turn")])]),
        spl(f"{S}-sp-bolt", "Dragon Bolt", 3, "fast", "Deal 4 damage to an enemy Figure.",
            [abi(f"{S}-s3", "Dragon Bolt", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 4)])]),
        spl(f"{S}-sp-scroll", "Ancient Scroll", 1, "burst", "Draw a card. Gain 1 Ritual Mana.",
            [abi(f"{S}-s4", "Ancient Scroll", trigger="manual", timing="burst", effects=[eff("draw_cards", 1), eff("gain_ritual_mana", 1)])]),
        spl(f"{S}-sp-balance", "Balance of Five", 3, "burst", "Restore 3 Health. Draw a card. Gain 1 Armor.",
            [abi(f"{S}-s5", "Balance of Five", trigger="manual", timing="burst", effects=[eff("heal", 3, scope="friendly_hero"), eff("draw_cards", 1), eff("gain_armor", 1)])]),
        spl(f"{S}-sp-ward", "Dragon Ward", 1, "burst", "Give a friendly Figure Ward.",
            [abi(f"{S}-s6", "Dragon Ward", trigger="manual", target_rule="friendly_figure", timing="burst", effects=[eff("grant_keyword", keyword="ward")])]),
        rel(f"{S}-rel-scroll", "Scroll of Wisdom", 2, "After you cast a spell, give a random friendly Figure +1/+1.",
            [abi(f"{S}-r1", "Scroll of Wisdom", trigger="on_spell_cast", timing="passive", effects=[eff("grant_stats", attack=1, health=1, scope="random_friendly_figure")])]),
        rel(f"{S}-rel-gong", "Dragon Gong", 3, "Activate (1): Draw a card. Once per turn.",
            [abi(f"{S}-r2", "Dragon Gong", trigger="manual", timing="slow", resource_cost=1, effects=[eff("draw_cards", 1)], limit="once_each_turn")]),
    ]

# ============================================================
# 7. INUIT — Freeze/Stall
# Freeze everything, high health figures, fatigue win
# ============================================================
def build_inuit():
    S = "inuit"
    return [
        hero(f"{S}-hero", "Sedna, Sea Mother",
             "Hero Power (2): Freeze an enemy Figure.",
             [abi(f"{S}-h1", "Icy Grasp", trigger="manual", target_rule="enemy_figure", timing="slow", resource_cost=2,
                  effects=[eff("freeze")])]),
        fig(f"{S}-001", "Snow Hare", 1, 1, 2, [], "On play: Freeze an enemy Figure.",
            [abi(f"{S}-01", "Chill Breath", target_rule="enemy_figure", effects=[eff("freeze")])]),
        fig(f"{S}-002", "Ice Fisher", 2, 1, 4, [], "On play: Draw a card.",
            [abi(f"{S}-02", "Patience", effects=[eff("draw_cards", 1)])]),
        fig(f"{S}-003", "Tundra Guard", 2, 1, 5, ["guard"], "Guard."),
        fig(f"{S}-004", "Polar Bear", 3, 3, 4, [], "On play: Freeze an enemy Figure.",
            [abi(f"{S}-04", "Ice Swipe", target_rule="enemy_figure", effects=[eff("freeze")])]),
        fig(f"{S}-005", "Shaman", 3, 2, 4, [], "On play: Restore 3 Health to your Hero.",
            [abi(f"{S}-05", "Spirit Heal", effects=[eff("heal", 3, scope="friendly_hero")])]),
        fig(f"{S}-006", "Walrus Elder", 4, 2, 6, ["guard", "lifesteal"], "Guard. Lifesteal."),
        fig(f"{S}-007", "Aurora Spirit", 4, 3, 5, [], "On play: Freeze all enemy Figures.",
            [abi(f"{S}-07", "Northern Lights", target_rule="all_enemy_figures", effects=[eff("freeze")])], rarity="rare"),
        fig(f"{S}-008", "Nanook", 5, 4, 6, ["guard"], "Guard. On play: Deal 2 damage to an enemy Figure.",
            [abi(f"{S}-08", "Bear Swipe", target_rule="enemy_figure", effects=[eff("deal_damage", 2)])], rarity="rare"),
        fig(f"{S}-009", "Sedna", 6, 3, 9, ["lifesteal"], "Lifesteal. On play: Freeze all enemy Figures. Restore 3 Health.",
            [abi(f"{S}-09", "Deep Freeze", target_rule="all_enemy_figures", effects=[eff("freeze"), eff("heal", 3, scope="friendly_hero")])], rarity="legendary"),
        spl(f"{S}-sp-frost", "Frost Bolt", 2, "fast", "Deal 2 damage to an enemy Figure. Freeze it.",
            [abi(f"{S}-s1", "Frost Bolt", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("deal_damage", 2), eff("freeze")])]),
        spl(f"{S}-sp-blizzard", "Blizzard", 5, "slow", "Deal 2 damage to all enemy Figures. Freeze them.",
            [abi(f"{S}-s2", "Blizzard", trigger="manual", target_rule="all_enemy_figures", timing="slow", effects=[eff("deal_damage", 2), eff("freeze")])], rarity="rare"),
        spl(f"{S}-sp-igloo", "Igloo Shield", 2, "fast", "Give a friendly Figure +0/+3 and Guard this turn.",
            [abi(f"{S}-s3", "Igloo Shield", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=0, health=3, duration="turn"), eff("grant_keyword", keyword="guard", duration="turn")])]),
        spl(f"{S}-sp-fish", "Ice Fishing", 2, "burst", "Draw 2 cards.",
            [abi(f"{S}-s4", "Ice Fishing", trigger="manual", timing="burst", effects=[eff("draw_cards", 2)])], rarity="rare"),
        spl(f"{S}-sp-heal", "Warm Hearth", 2, "burst", "Restore 4 Health to your Hero. Gain 1 Armor.",
            [abi(f"{S}-s5", "Warm Hearth", trigger="manual", timing="burst", effects=[eff("heal", 4, scope="friendly_hero"), eff("gain_armor", 1)])]),
        spl(f"{S}-sp-modal", "Spirit's Will", 2, "fast",
            "Choose: Freeze an enemy Figure OR Give a friendly Figure +2/+2 this combat.",
            [abi(f"{S}-s6a", "Ice Bind", trigger="manual", target_rule="enemy_figure", timing="fast", effects=[eff("freeze")]),
             abi(f"{S}-s6b", "Spirit Buff", trigger="manual", target_rule="friendly_figure", timing="fast", effects=[eff("grant_stats", attack=2, health=2, duration="combat")])]),
        rel(f"{S}-rel-ice", "Permafrost Seal", 2, "The first time each turn you Freeze an enemy, gain 2 Armor.",
            [abi(f"{S}-r1", "Permafrost Seal", trigger="on_freeze", timing="passive", effects=[eff("gain_armor", 2)], limit="once_each_turn")]),
        rel(f"{S}-rel-lamp", "Seal Oil Lamp", 3, "Activate (1): Draw a card. Once per turn.",
            [abi(f"{S}-r2", "Seal Oil Lamp", trigger="manual", timing="slow", resource_cost=1, effects=[eff("draw_cards", 1)], limit="once_each_turn")]),
    ]


def finalize(cards, slug, set_code):
    for c in cards:
        c["culture_slug"] = slug
        c["set_code"] = set_code
    return {"culture_slug": slug, "set_code": set_code, "cards": cards}

def dk(hero_id, name, entries, notes=None):
    return {"hero_id": hero_id, "name": name, "notes": notes or [], "cards": entries}

def save_pack(pack, slug):
    path = CARDS_DIR / f"{slug}-v1.json"
    path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"  {slug}: {len(pack['cards'])} cards")

def save_deck(deck_data, filename):
    path = DECKS_DIR / filename
    path.write_text(json.dumps(deck_data, indent=2, ensure_ascii=False), encoding="utf-8")
    total = sum(e["count"] for e in deck_data["cards"])
    print(f"    {filename}: {total} cards")

def main():
    cultures = [
        ("japanese-shinto", build_japanese),
        ("celtic-irish", build_celtic),
        ("vedic-hindu", build_vedic),
        ("haitian-vodou", build_haitian),
        ("aztec-mexica", build_aztec),
        ("ancient-chinese", build_chinese),
        ("inuit", build_inuit),
    ]

    for slug, builder in cultures:
        S = slug
        cards = builder()
        pack = finalize(cards, slug, f"{slug}-v1")
        save_pack(pack, slug)

        # Remove old decks
        for old in list(DECKS_DIR.glob(f"{slug}-*.json")):
            old.unlink()

        # Build one deck per culture (24 cards: ~14-15 figures, 7-8 spells, 2 relics)
        # Get card IDs
        figs = [c["id"] for c in cards if c["card_type"] == "figure"]
        spls = [c["id"] for c in cards if c["card_type"] == "spell"]
        rels = [c["id"] for c in cards if c["card_type"] == "relic"]
        hero_id = [c["id"] for c in cards if c["card_type"] == "hero"][0]

        # Auto-build a balanced deck
        entries = []
        fig_count = 0
        spl_count = 0

        # Add 2x cheap figures, 2x mid, 1x expensive
        cheap = [f for f in figs if any(c["cost"] <= 2 for c in cards if c["id"] == f)]
        mid = [f for f in figs if any(2 < c["cost"] <= 4 for c in cards if c["id"] == f)]
        expensive = [f for f in figs if any(c["cost"] >= 5 for c in cards if c["id"] == f)]

        for f in cheap[:4]:
            entries.append({"id": f, "count": 2})
            fig_count += 2
        for f in mid[:3]:
            entries.append({"id": f, "count": 2})
            fig_count += 2
        for f in expensive[:2]:
            entries.append({"id": f, "count": 1})
            fig_count += 1

        # Add spells
        for s in spls[:5]:
            cnt = 2 if spl_count < 6 else 1
            # Cap at what fits
            if fig_count + spl_count + cnt + 2 <= 24:
                entries.append({"id": s, "count": cnt})
                spl_count += cnt
            else:
                entries.append({"id": s, "count": 1})
                spl_count += 1

        # Add remaining spells if space
        for s in spls[5:]:
            if fig_count + spl_count + 2 < 24:
                entries.append({"id": s, "count": 1})
                spl_count += 1

        # Add 2 relics
        for r in rels[:2]:
            entries.append({"id": r, "count": 1})

        total = sum(e["count"] for e in entries)
        # Pad or trim to 24
        while total < 24 and mid:
            # Add another figure
            extra = mid.pop()
            entries.append({"id": extra, "count": 1})
            total += 1
            fig_count += 1
        while total > 24:
            # Remove last entry count
            if entries[-1]["count"] > 1:
                entries[-1]["count"] -= 1
                total -= 1
            else:
                entries.pop()
                total = sum(e["count"] for e in entries)

        deck_name = f"{slug}-{hero_id.split('-')[-1]}-main"
        d = dk(hero_id, deck_name.replace("-", " ").title(), entries)
        save_deck(d, f"{deck_name}.json")

    print("\nDone!")


if __name__ == "__main__":
    main()
