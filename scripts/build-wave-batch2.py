"""Build batch 2: 10 new cultures with unique archetypes.

Slavic=Enrage, Roman=Legion, Persian=Dual, Hawaiian=Tide, Aboriginal=Transform,
Yoruba=Chain, Mongol=Cavalry, Babylonian=Prophecy, Maori=Debuff, Sikh=Armor
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
CARDS_DIR = ROOT / "data" / "cards-v1"
DECKS_DIR = ROOT / "data" / "decks-v1"

N = {"attack": None, "health": None, "keyword": None, "duration": None, "scope": None, "pool": None, "card_id": None, "extra": {}}
def E(kind, amount=None, **kw):
    e = {"kind": kind, "amount": amount, **N}; e.update(kw); return e
def A(id, label, trigger="on_play", target_rule="none", effects=None, timing="slow", limit=None, resource_cost=None):
    return {"id": id, "label": label, "timing": timing, "trigger": trigger, "target_rule": target_rule, "resource_cost": resource_cost, "conditions": [], "effects": effects or [], "limit": limit}
def F(id, n, c, a, h, kw=None, t="", ab=None, r="common"):
    return {"id":id,"name":n,"card_type":"figure","culture_slug":"","rarity":r,"alignment":"neutral","traits":[],"rules_text":t,"cost":c,"speed":None,"subtypes":[],"keywords":kw or [],"unique":r=="legendary","legendary":r=="legendary","token":False,"collectible":True,"set_code":"","flavor_text":"","attack":a,"health":h,"abilities":ab or []}
def S(id, n, c, spd, t, ab=None, r="common"):
    return {"id":id,"name":n,"card_type":"spell","culture_slug":"","rarity":r,"alignment":"neutral","traits":[],"rules_text":t,"cost":c,"speed":spd,"subtypes":[],"keywords":[],"unique":False,"legendary":False,"token":False,"collectible":True,"set_code":"","flavor_text":"","attack":None,"health":None,"abilities":ab or []}
def R(id, n, c, t, ab=None, r="rare"):
    return {"id":id,"name":n,"card_type":"relic","culture_slug":"","rarity":r,"alignment":"neutral","traits":[],"rules_text":t,"cost":c,"speed":None,"subtypes":[],"keywords":[],"unique":False,"legendary":False,"token":False,"collectible":True,"set_code":"","flavor_text":"","attack":None,"health":None,"abilities":ab or []}
def T(id, n, a, h, kw=None, t="", ab=None):
    return {"id":id,"name":n,"card_type":"token","culture_slug":"","rarity":"token","alignment":"neutral","traits":[],"rules_text":t,"cost":0,"speed":None,"subtypes":[],"keywords":kw or[],"unique":False,"legendary":False,"token":True,"collectible":False,"set_code":"","flavor_text":"","attack":a,"health":h,"abilities":ab or[]}
def H(id, n, t, ab):
    return {"id":id,"name":n,"card_type":"hero","culture_slug":"","rarity":"legendary","alignment":"light","traits":[],"rules_text":t,"cost":None,"speed":None,"subtypes":[],"keywords":[],"unique":True,"legendary":True,"token":False,"collectible":True,"set_code":"","flavor_text":"","attack":None,"health":None,"abilities":ab}

# ================================================================
# SLAVIC — Berserker/Enrage: figures get stronger when damaged
# ================================================================
def build_slavic():
    P = "slavic"
    return [
        H(f"{P}-hero", "Perun, Thunder Lord", "Hero Power (2): Deal 1 damage to a friendly Figure. Give it +2 Attack.",
          [A(f"{P}-h1","War Blessing",trigger="manual",target_rule="friendly_figure",timing="slow",resource_cost=2,effects=[E("deal_damage",1),E("grant_stats",attack=2,health=0)])]),
        F(f"{P}-01","Leshy",1,1,2,[],"On play: Draw a card.",[A(f"{P}-a01","Forest Lore",effects=[E("draw_cards",1)])]),
        F(f"{P}-02","Bogatyr",2,2,3,[],"Has +2 Attack while damaged.",[A(f"{P}-a02","Rage",trigger="passive",timing="passive",effects=[E("grant_stats",attack=2,health=0,extra={"condition":"while_damaged"})])]),
        F(f"{P}-03","Kikimora",2,3,2,["rush"],"Rush."),
        F(f"{P}-04","Domovoi",2,1,4,["guard"],"Guard."),
        F(f"{P}-05","Vila",3,3,3,[],"On play: Deal 1 damage to a friendly Figure. Give it +2/+1.",[A(f"{P}-a05","Spite Gift",target_rule="friendly_figure",effects=[E("deal_damage",1),E("grant_stats",attack=2,health=1)])],r="rare"),
        F(f"{P}-06","Zmey",3,4,3,[],"On play: Deal 2 damage to an enemy Figure.",[A(f"{P}-a06","Fire Breath",target_rule="enemy_figure",effects=[E("deal_damage",2)])]),
        F(f"{P}-07","Rusalka",3,2,4,["lifesteal"],"Lifesteal."),
        F(f"{P}-08","Veles",4,4,4,[],"On play: Deal 1 damage to ALL Figures.",[A(f"{P}-a08","Underworld Pulse",effects=[E("deal_damage",1,scope="all_figures")])],r="rare"),
        F(f"{P}-09","Svarog",5,5,5,["overwhelm"],"Overwhelm. On play: Deal 2 damage to an enemy Figure.",[A(f"{P}-a09","Forge Fire",target_rule="enemy_figure",effects=[E("deal_damage",2)])],r="rare"),
        F(f"{P}-10","Perun",6,6,6,["overwhelm"],"Overwhelm. On play: Deal 1 damage to all Figures.",[A(f"{P}-a10","Thunder",effects=[E("deal_damage",1,scope="all_figures")])],r="legendary"),
        S(f"{P}-s1","Battle Fury",1,"fast","Give a friendly Figure +2 Attack this combat.",[A(f"{P}-sa1","Battle Fury",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=2,health=0,duration="combat")])]),
        S(f"{P}-s2","Lightning Strike",2,"fast","Deal 3 damage to any enemy.",[A(f"{P}-sa2","Lightning Strike",trigger="manual",target_rule="enemy_character",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s3","War Cry",2,"burst","Deal 1 damage to all friendly Figures. Give them +1 Attack.",[A(f"{P}-sa3","War Cry",trigger="manual",timing="burst",effects=[E("deal_damage",1,scope="all_friendly_figures"),E("grant_stats",attack=1,health=0,scope="all_friendly_figures")])]),
        S(f"{P}-s4","Slavic Mead",1,"burst","Draw a card.",[A(f"{P}-sa4","Slavic Mead",trigger="manual",timing="burst",effects=[E("draw_cards",1)])]),
        S(f"{P}-s5","Fire of Svarog",4,"slow","Deal 3 damage to all enemy Figures.",[A(f"{P}-sa5","Fire of Svarog",trigger="manual",target_rule="all_enemy_figures",timing="slow",effects=[E("deal_damage",3)])],r="rare"),
        S(f"{P}-s6","Perun's Choice",2,"fast","Choose: Deal 2 damage to a friendly Figure and give it +3/+1 OR Deal 3 damage to an enemy Figure.",
          [A(f"{P}-sa6a","Enrage",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("deal_damage",2),E("grant_stats",attack=3,health=1)]),
           A(f"{P}-sa6b","Smite",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        R(f"{P}-r1","Oak of Perun",2,"The first time each turn a friendly Figure takes damage, give it +1 Attack.",[A(f"{P}-ra1","Oak of Perun",trigger="on_friendly_damaged",timing="passive",effects=[E("grant_stats",attack=1,health=0)],limit="once_each_turn")]),
        R(f"{P}-r2","Forge Anvil",3,"Activate (1): Deal 1 damage to a friendly Figure. Draw a card. Once per turn.",[A(f"{P}-ra2","Forge Anvil",trigger="manual",timing="slow",resource_cost=1,effects=[E("deal_damage",1),E("draw_cards",1)],limit="once_each_turn")]),
    ]

# ================================================================
# ROMAN — Legion/Wide Buff: many cheap figures, buff them all
# ================================================================
def build_roman():
    P = "roman"
    return [
        H(f"{P}-hero","Mars, God of War","Hero Power (2): Give all friendly Figures +1 Attack this turn.",
          [A(f"{P}-h1","Legion March",trigger="manual",timing="slow",resource_cost=2,effects=[E("grant_stats",attack=1,health=0,duration="turn",scope="all_friendly_figures")])]),
        F(f"{P}-01","Legionary",1,1,2,[],""),
        F(f"{P}-02","Velite",1,2,1,["rush"],"Rush."),
        F(f"{P}-03","Centurion",2,2,3,[],"On play: Give another friendly Figure +1/+1.",[A(f"{P}-a03","Rally",target_rule="other_friendly_figure",effects=[E("grant_stats",attack=1,health=1)])]),
        F(f"{P}-04","Shield Bearer",2,1,4,["guard"],"Guard."),
        F(f"{P}-05","Lictor",3,3,2,["rush"],"Rush. On play: Draw a card.",[A(f"{P}-a05","Scout",effects=[E("draw_cards",1)])]),
        F(f"{P}-06","Tribune",3,2,4,[],"On play: Give all friendly Figures +0/+1.",[A(f"{P}-a06","Fortify",effects=[E("grant_stats",attack=0,health=1,scope="all_friendly_figures")])],r="rare"),
        F(f"{P}-07","Gladiator",3,4,3,["rush"],"Rush."),
        F(f"{P}-08","Praetorian",4,3,5,["guard"],"Guard. On play: Give adjacent Figures +1/+1.",[A(f"{P}-a08","Shield Wall",effects=[E("grant_stats",attack=1,health=1,scope="all_friendly_figures")])],r="rare"),
        F(f"{P}-09","Jupiter",5,4,6,[],"On play: Deal 2 damage to all enemy Figures.",[A(f"{P}-a09","Thunderbolt",target_rule="all_enemy_figures",effects=[E("deal_damage",2)])],r="rare"),
        F(f"{P}-10","Augustus",6,5,7,[],"On play: Give all friendly Figures +2/+2.",[A(f"{P}-a10","Imperial Decree",effects=[E("grant_stats",attack=2,health=2,scope="all_friendly_figures")])],r="legendary"),
        S(f"{P}-s1","Testudo",2,"fast","Give a friendly Figure +0/+3 and Guard this turn.",[A(f"{P}-sa1","Testudo",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=0,health=3,duration="turn"),E("grant_keyword",keyword="guard",duration="turn")])]),
        S(f"{P}-s2","Pilum Throw",2,"fast","Deal 3 damage to an enemy Figure.",[A(f"{P}-sa2","Pilum Throw",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s3","Triumph",3,"burst","Give all friendly Figures +1/+1.",[A(f"{P}-sa3","Triumph",trigger="manual",timing="burst",effects=[E("grant_stats",attack=1,health=1,scope="all_friendly_figures")])],r="rare"),
        S(f"{P}-s4","Roman Roads",1,"burst","Draw a card. Gain 1 Ritual Mana.",[A(f"{P}-sa4","Roman Roads",trigger="manual",timing="burst",effects=[E("draw_cards",1),E("gain_ritual_mana",1)])]),
        S(f"{P}-s5","Decimation",4,"slow","Deal 2 damage to ALL Figures.",[A(f"{P}-sa5","Decimation",trigger="manual",timing="slow",effects=[E("deal_damage",2,scope="all_figures")])]),
        S(f"{P}-s6","Mars's Choice",2,"fast","Choose: Give all friendly Figures +1 Attack this turn OR Deal 2 damage to an enemy Figure.",
          [A(f"{P}-sa6a","Charge!",trigger="manual",timing="fast",effects=[E("grant_stats",attack=1,health=0,duration="turn",scope="all_friendly_figures")]),
           A(f"{P}-sa6b","Strike",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",2)])]),
        R(f"{P}-r1","Eagle Standard",2,"After you play a Figure, give all friendly Figures +0/+1. Once per turn.",[A(f"{P}-ra1","Eagle Standard",trigger="on_friendly_play",timing="passive",effects=[E("grant_stats",attack=0,health=1,scope="all_friendly_figures")],limit="once_each_turn")]),
        R(f"{P}-r2","War Drum",3,"Activate (1): Give all friendly Figures +1 Attack this turn. Once per turn.",[A(f"{P}-ra2","War Drum",trigger="manual",timing="slow",resource_cost=1,effects=[E("grant_stats",attack=1,health=0,duration="turn",scope="all_friendly_figures")],limit="once_each_turn")]),
        T(f"{P}-tok","Recruit",1,1),
    ]

# ================================================================
# ZOROASTRIAN PERSIAN — Dual Nature: Light/Dark modal on every spell
# ================================================================
def build_persian():
    P = "zoroastrian-persian"
    return [
        H(f"{P}-hero","Ahura Mazda, Lord of Wisdom","Hero Power (2): Choose: Deal 1 damage to an enemy Figure OR Restore 2 Health to your Hero.",
          [A(f"{P}-h1a","Smite",trigger="manual",target_rule="enemy_figure",timing="slow",resource_cost=2,effects=[E("deal_damage",1)]),
           A(f"{P}-h1b","Heal",trigger="manual",target_rule="friendly_hero",timing="slow",resource_cost=2,effects=[E("heal",2)])]),
        F(f"{P}-01","Fire Keeper",1,1,2,[],"On play: Draw a card.",[A(f"{P}-a01","Tend Flame",effects=[E("draw_cards",1)])]),
        F(f"{P}-02","Yazata",2,2,3,[],"On play: Give a friendly Figure +1/+1.",[A(f"{P}-a02","Blessing",target_rule="friendly_figure",effects=[E("grant_stats",attack=1,health=1)])]),
        F(f"{P}-03","Fravashi",2,1,4,["guard"],"Guard."),
        F(f"{P}-04","Atar",3,3,3,[],"On play: Deal 2 damage to an enemy Figure.",[A(f"{P}-a04","Sacred Fire",target_rule="enemy_figure",effects=[E("deal_damage",2)])]),
        F(f"{P}-05","Mithra",3,2,4,["lifesteal"],"Lifesteal."),
        F(f"{P}-06","Sraosha",4,4,4,["rush"],"Rush. On play: Draw a card.",[A(f"{P}-a06","Vigilance",effects=[E("draw_cards",1)])],r="rare"),
        F(f"{P}-07","Verethragna",4,5,3,["rush"],"Rush.",[],r="rare"),
        F(f"{P}-08","Angra Mainyu",5,4,5,[],"On play: Deal 2 damage to all enemy Figures.",[A(f"{P}-a08","Dark Wave",target_rule="all_enemy_figures",effects=[E("deal_damage",2)])],r="rare"),
        F(f"{P}-09","Saoshyant",6,5,7,[],"On play: Restore 5 Health. Draw 2 cards.",[A(f"{P}-a09","Final Judgment",effects=[E("heal",5,scope="friendly_hero"),E("draw_cards",2)])],r="legendary"),
        S(f"{P}-s1","Light or Dark",2,"fast","Choose: Give a friendly Figure +2/+2 this combat OR Deal 2 damage to an enemy Figure.",
          [A(f"{P}-sa1a","Light",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=2,health=2,duration="combat")]),
           A(f"{P}-sa1b","Dark",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",2)])]),
        S(f"{P}-s2","Fire and Ice",3,"fast","Choose: Deal 3 damage to an enemy Figure OR Freeze an enemy Figure and deal 1 damage.",
          [A(f"{P}-sa2a","Fire",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)]),
           A(f"{P}-sa2b","Ice",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("freeze"),E("deal_damage",1)])]),
        S(f"{P}-s3","Truth or Lie",1,"burst","Choose: Draw a card OR Gain 2 Ritual Mana.",
          [A(f"{P}-sa3a","Truth",trigger="manual",timing="burst",effects=[E("draw_cards",1)]),
           A(f"{P}-sa3b","Lie",trigger="manual",timing="burst",effects=[E("gain_ritual_mana",2)])]),
        S(f"{P}-s4","Creation or Destruction",4,"slow","Choose: Restore 4 Health and draw 2 cards OR Deal 3 damage to all enemy Figures.",
          [A(f"{P}-sa4a","Creation",trigger="manual",timing="slow",effects=[E("heal",4,scope="friendly_hero"),E("draw_cards",2)]),
           A(f"{P}-sa4b","Destruction",trigger="manual",target_rule="all_enemy_figures",timing="slow",effects=[E("deal_damage",3)])],r="rare"),
        S(f"{P}-s5","Sacred Flame",2,"fast","Deal 3 damage to any enemy.",[A(f"{P}-sa5","Sacred Flame",trigger="manual",target_rule="enemy_character",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s6","Asha's Ward",1,"burst","Give a friendly Figure Ward.",[A(f"{P}-sa6","Asha's Ward",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_keyword",keyword="ward")])]),
        R(f"{P}-r1","Eternal Flame",2,"After you cast a spell, give a random friendly Figure +1/+1.",[A(f"{P}-ra1","Eternal Flame",trigger="on_spell_cast",timing="passive",effects=[E("grant_stats",attack=1,health=1,scope="random_friendly_figure")])]),
        R(f"{P}-r2","Faravahar",3,"Activate (1): Draw a card. Once per turn.",[A(f"{P}-ra2","Faravahar",trigger="manual",timing="slow",resource_cost=1,effects=[E("draw_cards",1)],limit="once_each_turn")]),
    ]

# ================================================================
# HAWAIIAN POLYNESIAN — Tide/Tempo: bounce + replay for value
# ================================================================
def build_hawaiian():
    P = "hawaiian-polynesian"
    return [
        H(f"{P}-hero","Maui, Trickster Hero","Hero Power (2): Return a friendly Figure (cost 2-) to hand. It costs 1 less.",
          [A(f"{P}-h1","Fishhook",trigger="manual",target_rule="friendly_figure",timing="slow",resource_cost=2,effects=[E("return_to_hand",extra={"side":"friendly","max_cost":2,"cost_reduction":1})])]),
        F(f"{P}-01","Reef Runner",1,1,2,[],"On play: Draw a card.",[A(f"{P}-a01","Tide Gift",effects=[E("draw_cards",1)])]),
        F(f"{P}-02","Tiki Guard",2,1,4,["guard"],"Guard."),
        F(f"{P}-03","Wave Dancer",2,2,2,[],"On play: Deal 1 damage to an enemy Figure. Draw a card.",[A(f"{P}-a03","Splash",target_rule="enemy_figure",effects=[E("deal_damage",1),E("draw_cards",1)])],r="rare"),
        F(f"{P}-04","Hina",3,2,4,[],"On play: Restore 3 Health to your Hero.",[A(f"{P}-a04","Moon Heal",effects=[E("heal",3,scope="friendly_hero")])]),
        F(f"{P}-05","Ku",3,4,3,["rush"],"Rush."),
        F(f"{P}-06","Pele",4,3,4,[],"On play: Deal 3 damage to an enemy Figure.",[A(f"{P}-a06","Lava Bolt",target_rule="enemy_figure",effects=[E("deal_damage",3)])],r="rare"),
        F(f"{P}-07","Kanaloa",4,3,5,[],"On play: Return an enemy Figure (cost 3-) to its owner's hand.",[A(f"{P}-a07","Deep Bounce",target_rule="enemy_figure",effects=[E("return_to_hand",extra={"max_cost":3})])],r="rare"),
        F(f"{P}-08","Lono",5,4,6,["guard"],"Guard. On play: Draw 2 cards.",[A(f"{P}-a08","Harvest",effects=[E("draw_cards",2)])],r="rare"),
        F(f"{P}-09","Maui",6,5,6,[],"On play: Return all enemy Figures (cost 3-) to hand.",[A(f"{P}-a09","Great Trick",effects=[E("return_to_hand",extra={"max_cost":3,"scope":"all_enemy"})])],r="legendary"),
        S(f"{P}-s1","Tidal Return",2,"fast","Return an enemy Figure (cost 3-) to its owner's hand.",[A(f"{P}-sa1","Tidal Return",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("return_to_hand",extra={"max_cost":3})])]),
        S(f"{P}-s2","Ocean Surge",2,"fast","Give a friendly Figure +2/+2 this combat.",[A(f"{P}-sa2","Ocean Surge",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=2,health=2,duration="combat")])]),
        S(f"{P}-s3","Island Song",1,"burst","Draw a card. Gain 1 Ritual Mana.",[A(f"{P}-sa3","Island Song",trigger="manual",timing="burst",effects=[E("draw_cards",1),E("gain_ritual_mana",1)])]),
        S(f"{P}-s4","Volcano Burst",4,"slow","Deal 3 damage to all enemy Figures.",[A(f"{P}-sa4","Volcano Burst",trigger="manual",target_rule="all_enemy_figures",timing="slow",effects=[E("deal_damage",3)])],r="rare"),
        S(f"{P}-s5","Maui's Choice",2,"fast","Choose: Return a friendly Figure to hand (costs 1 less) OR Deal 2 damage to an enemy Figure.",
          [A(f"{P}-sa5a","Replay",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("return_to_hand",extra={"side":"friendly","cost_reduction":1})]),
           A(f"{P}-sa5b","Strike",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",2)])]),
        S(f"{P}-s6","Coral Shield",1,"burst","Give a friendly Figure Ward.",[A(f"{P}-sa6","Coral Shield",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_keyword",keyword="ward")])]),
        R(f"{P}-r1","Fishhook Relic",2,"After you return a card to hand, draw a card. Once per turn.",[A(f"{P}-ra1","Fishhook Relic",trigger="on_return_to_hand",timing="passive",effects=[E("draw_cards",1)],limit="once_each_turn")]),
        R(f"{P}-r2","Tiki Totem",3,"Activate (1): Give a friendly Figure +1/+1. Once per turn.",[A(f"{P}-ra2","Tiki Totem",trigger="manual",target_rule="friendly_figure",timing="slow",resource_cost=1,effects=[E("grant_stats",attack=1,health=1)],limit="once_each_turn")]),
    ]

# ================================================================
# ABORIGINAL AUSTRALIAN — Dreamtime/Transform: figures upgrade
# ================================================================
def build_aboriginal():
    P = "aboriginal-australian"
    return [
        H(f"{P}-hero","Rainbow Serpent","Hero Power (2): Give a friendly Figure +1/+1.",
          [A(f"{P}-h1","Dreamtime Blessing",trigger="manual",target_rule="friendly_figure",timing="slow",resource_cost=2,effects=[E("grant_stats",attack=1,health=1)])]),
        F(f"{P}-01","Bush Spirit",1,1,2,[],"On play: Draw a card.",[A(f"{P}-a01","Whisper",effects=[E("draw_cards",1)])]),
        F(f"{P}-02","Wombat Guardian",2,1,4,["guard"],"Guard."),
        F(f"{P}-03","Emu Runner",2,3,2,["rush"],"Rush."),
        F(f"{P}-04","Bunyip",3,3,4,[],"On play: Give a friendly Figure +1/+1.",[A(f"{P}-a04","Grow",target_rule="friendly_figure",effects=[E("grant_stats",attack=1,health=1)])]),
        F(f"{P}-05","Tiddalik",3,2,5,["guard"],"Guard. On play: Draw a card.",[A(f"{P}-a05","Deep Drink",effects=[E("draw_cards",1)])],r="rare"),
        F(f"{P}-06","Baiame",4,3,5,[],"On play: Give all friendly Figures +1/+1.",[A(f"{P}-a06","Creator",effects=[E("grant_stats",attack=1,health=1,scope="all_friendly_figures")])],r="rare"),
        F(f"{P}-07","Yowie",4,4,4,["rush"],"Rush."),
        F(f"{P}-08","Mimi Spirit",5,4,6,[],"On play: Give a friendly Figure +2/+2 and Ward.",[A(f"{P}-a08","Dream Shield",target_rule="friendly_figure",effects=[E("grant_stats",attack=2,health=2),E("grant_keyword",keyword="ward")])],r="rare"),
        F(f"{P}-09","Rainbow Serpent",6,5,8,[],"On play: Give all friendly Figures +2/+2.",[A(f"{P}-a09","Dreamtime",effects=[E("grant_stats",attack=2,health=2,scope="all_friendly_figures")])],r="legendary"),
        S(f"{P}-s1","Dreamtime Shift",2,"fast","Give a friendly Figure +2/+2 this combat.",[A(f"{P}-sa1","Dreamtime Shift",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=2,health=2,duration="combat")])]),
        S(f"{P}-s2","Dust Storm",3,"fast","Deal 2 damage to all enemy Figures.",[A(f"{P}-sa2","Dust Storm",trigger="manual",target_rule="all_enemy_figures",timing="fast",effects=[E("deal_damage",2)])],r="rare"),
        S(f"{P}-s3","Song Line",1,"burst","Draw a card. Gain 1 Ritual Mana.",[A(f"{P}-sa3","Song Line",trigger="manual",timing="burst",effects=[E("draw_cards",1),E("gain_ritual_mana",1)])]),
        S(f"{P}-s4","Ancestor's Gift",2,"burst","Give a friendly Figure +1/+2.",[A(f"{P}-sa4","Ancestor's Gift",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_stats",attack=1,health=2)])]),
        S(f"{P}-s5","Serpent's Choice",3,"fast","Choose: Give a friendly Figure +3/+3 OR Deal 3 damage to an enemy Figure.",
          [A(f"{P}-sa5a","Empower",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=3,health=3)]),
           A(f"{P}-sa5b","Strike",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s6","Ochre Shield",1,"burst","Give a friendly Figure Ward.",[A(f"{P}-sa6","Ochre Shield",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_keyword",keyword="ward")])]),
        R(f"{P}-r1","Songline Map",2,"After you play a Figure, give it +1/+1. Once per turn.",[A(f"{P}-ra1","Songline Map",trigger="on_friendly_play",timing="passive",effects=[E("grant_stats",attack=1,health=1)],limit="once_each_turn")]),
        R(f"{P}-r2","Dreaming Stone",3,"Activate (2): Give a friendly Figure +2/+2. Once per turn.",[A(f"{P}-ra2","Dreaming Stone",trigger="manual",target_rule="friendly_figure",timing="slow",resource_cost=2,effects=[E("grant_stats",attack=2,health=2)],limit="once_each_turn")]),
    ]

# ================================================================
# YORUBA — Spirit Chain: on-play effects chain off each other
# ================================================================
def build_yoruba():
    P = "yoruba"
    return [
        H(f"{P}-hero","Ogun, Iron Lord","Hero Power (2): Deal 1 damage to an enemy Figure. If it dies, draw a card.",
          [A(f"{P}-h1","Iron Strike",trigger="manual",target_rule="enemy_figure",timing="slow",resource_cost=2,effects=[E("deal_damage",1,extra={"on_kill_draw":1})])]),
        F(f"{P}-01","Ibeji Twin",1,1,1,[],"On play: Draw a card.",[A(f"{P}-a01","Twin Bond",effects=[E("draw_cards",1)])]),
        F(f"{P}-02","Eshu",2,2,2,[],"On play: Give another friendly Figure +1 Attack and draw a card.",[A(f"{P}-a02","Crossroads",target_rule="other_friendly_figure",effects=[E("grant_stats",attack=1,health=0),E("draw_cards",1)])],r="rare"),
        F(f"{P}-03","Oya",2,3,2,["rush"],"Rush."),
        F(f"{P}-04","Obatala",3,2,4,["guard"],"Guard. On play: Give a friendly Figure +0/+2.",[A(f"{P}-a04","White Shield",target_rule="friendly_figure",effects=[E("grant_stats",attack=0,health=2)])]),
        F(f"{P}-05","Yemoja",3,2,4,["lifesteal"],"Lifesteal. On play: Restore 2 Health.",[A(f"{P}-a05","River Heal",effects=[E("heal",2,scope="friendly_hero")])]),
        F(f"{P}-06","Shango",4,4,3,[],"On play: Deal 3 damage to an enemy Figure.",[A(f"{P}-a06","Thunder Axe",target_rule="enemy_figure",effects=[E("deal_damage",3)])],r="rare"),
        F(f"{P}-07","Ogun",4,4,4,["rush"],"Rush.",r="rare"),
        F(f"{P}-08","Osun",5,3,6,[],"On play: Give all friendly Figures +1/+1. Draw a card.",[A(f"{P}-a08","River Blessing",effects=[E("grant_stats",attack=1,health=1,scope="all_friendly_figures"),E("draw_cards",1)])],r="rare"),
        F(f"{P}-09","Olorun",6,5,7,[],"On play: Deal 2 damage to all enemy Figures. Restore 3 Health.",[A(f"{P}-a09","Supreme Light",target_rule="all_enemy_figures",effects=[E("deal_damage",2),E("heal",3,scope="friendly_hero")])],r="legendary"),
        S(f"{P}-s1","Spirit Bolt",2,"fast","Deal 3 damage to an enemy Figure.",[A(f"{P}-sa1","Spirit Bolt",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s2","Ancestor Dance",2,"fast","Give a friendly Figure +2/+1 this combat.",[A(f"{P}-sa2","Ancestor Dance",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=2,health=1,duration="combat")])]),
        S(f"{P}-s3","Divination",1,"burst","Draw a card.",[A(f"{P}-sa3","Divination",trigger="manual",timing="burst",effects=[E("draw_cards",1)])]),
        S(f"{P}-s4","Ogun's Forge",3,"burst","Give a friendly Figure +2/+2.",[A(f"{P}-sa4","Ogun's Forge",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_stats",attack=2,health=2)])]),
        S(f"{P}-s5","Ifa's Choice",3,"fast","Choose: Deal 4 damage to an enemy Figure OR Restore 4 Health and draw a card.",
          [A(f"{P}-sa5a","Punish",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",4)]),
           A(f"{P}-sa5b","Bless",trigger="manual",timing="fast",effects=[E("heal",4,scope="friendly_hero"),E("draw_cards",1)])]),
        S(f"{P}-s6","Iron Ward",1,"burst","Give a friendly Figure Ward.",[A(f"{P}-sa6","Iron Ward",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_keyword",keyword="ward")])]),
        R(f"{P}-r1","Shrine of Ogun",2,"After you play a Figure, give a random friendly Figure +1/+1.",[A(f"{P}-ra1","Shrine of Ogun",trigger="on_friendly_play",timing="passive",effects=[E("grant_stats",attack=1,health=1,scope="random_friendly_figure")])]),
        R(f"{P}-r2","Talking Drum",3,"Activate (1): Draw a card. Once per turn.",[A(f"{P}-ra2","Talking Drum",trigger="manual",timing="slow",resource_cost=1,effects=[E("draw_cards",1)],limit="once_each_turn")]),
    ]

# ================================================================
# MONGOLIAN — Cavalry/Rush: everything rushes, hit-and-run
# ================================================================
def build_mongol():
    P = "mongolian-shamanist"
    return [
        H(f"{P}-hero","Genghis Khan, World Conqueror","Hero Power (2): Give a friendly Figure Rush and +1 Attack this turn.",
          [A(f"{P}-h1","Cavalry Charge",trigger="manual",target_rule="friendly_figure",timing="slow",resource_cost=2,effects=[E("grant_keyword",keyword="rush",duration="turn"),E("grant_stats",attack=1,health=0,duration="turn")])]),
        F(f"{P}-01","Horse Archer",1,2,1,["rush"],"Rush."),
        F(f"{P}-02","Scout Rider",2,2,2,["rush"],"Rush. On play: Draw a card.",[A(f"{P}-a02","Scout",effects=[E("draw_cards",1)])]),
        F(f"{P}-03","Steppe Guard",2,1,4,["guard"],"Guard."),
        F(f"{P}-04","Khan's Rider",3,3,2,["rush"],"Rush. On play: Deal 1 damage to an enemy Figure.",[A(f"{P}-a04","Arrow",target_rule="enemy_figure",effects=[E("deal_damage",1)])]),
        F(f"{P}-05","Tumen Captain",3,3,3,["rush"],"Rush."),
        F(f"{P}-06","War Shaman",3,2,4,[],"On play: Give a friendly Figure +2/+1.",[A(f"{P}-a06","War Blessing",target_rule="friendly_figure",effects=[E("grant_stats",attack=2,health=1)])],r="rare"),
        F(f"{P}-07","Mangudai",4,4,3,["rush","overwhelm"],"Rush. Overwhelm.",r="rare"),
        F(f"{P}-08","Subotai",5,5,4,["rush"],"Rush. On play: Deal 2 damage to an enemy Figure.",[A(f"{P}-a08","Flanking Strike",target_rule="enemy_figure",effects=[E("deal_damage",2)])],r="rare"),
        F(f"{P}-09","Genghis Khan",6,6,5,["rush","overwhelm"],"Rush. Overwhelm. On play: Give all friendly Figures +1 Attack.",[A(f"{P}-a09","Conquer",effects=[E("grant_stats",attack=1,health=0,scope="all_friendly_figures")])],r="legendary"),
        S(f"{P}-s1","Mounted Strike",1,"fast","Give a friendly Figure +2 Attack this combat.",[A(f"{P}-sa1","Mounted Strike",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=2,health=0,duration="combat")])]),
        S(f"{P}-s2","Arrow Rain",2,"fast","Deal 2 damage to an enemy Figure.",[A(f"{P}-sa2","Arrow Rain",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",2)])]),
        S(f"{P}-s3","Kumis",1,"burst","Draw a card.",[A(f"{P}-sa3","Kumis",trigger="manual",timing="burst",effects=[E("draw_cards",1)])]),
        S(f"{P}-s4","Stampede",3,"slow","Deal 1 damage to all enemy Figures. Give all friendly Figures +1 Attack this turn.",[A(f"{P}-sa4","Stampede",trigger="manual",target_rule="all_enemy_figures",timing="slow",effects=[E("deal_damage",1),E("grant_stats",attack=1,health=0,duration="turn",scope="all_friendly_figures")])]),
        S(f"{P}-s5","Khan's Command",2,"fast","Choose: Give a friendly Figure Rush and +2 Attack this turn OR Deal 3 damage to an enemy Figure.",
          [A(f"{P}-sa5a","Charge",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_keyword",keyword="rush",duration="turn"),E("grant_stats",attack=2,health=0,duration="turn")]),
           A(f"{P}-sa5b","Arrow",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s6","Yurt Shield",2,"fast","Give a friendly Figure +0/+3 this combat.",[A(f"{P}-sa6","Yurt Shield",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=0,health=3,duration="combat")])]),
        R(f"{P}-r1","War Banner",2,"Your Rush Figures have +1 Attack.",[A(f"{P}-ra1","War Banner",trigger="passive",timing="passive",effects=[E("grant_stats",attack=1,health=0,scope="friendly_rush_figures")])]),
        R(f"{P}-r2","Shaman Tent",3,"Activate (1): Draw a card. Once per turn.",[A(f"{P}-ra2","Shaman Tent",trigger="manual",timing="slow",resource_cost=1,effects=[E("draw_cards",1)],limit="once_each_turn")]),
    ]

# ================================================================
# BABYLONIAN — Prophecy/Scry: plan ahead, conditional payoffs
# ================================================================
def build_babylonian():
    P = "babylonian"
    return [
        H(f"{P}-hero","Marduk, Supreme God","Hero Power (2): Draw a card. Gain 1 Ritual Mana.",
          [A(f"{P}-h1","Divine Sight",trigger="manual",timing="slow",resource_cost=2,effects=[E("draw_cards",1),E("gain_ritual_mana",1)])]),
        F(f"{P}-01","Scribe",1,1,2,[],"On play: Draw a card.",[A(f"{P}-a01","Record",effects=[E("draw_cards",1)])]),
        F(f"{P}-02","Ziggurat Guard",2,1,4,["guard"],"Guard."),
        F(f"{P}-03","Astrologer",2,2,2,[],"On play: Draw a card. Gain 1 Ritual Mana.",[A(f"{P}-a03","Star Chart",effects=[E("draw_cards",1),E("gain_ritual_mana",1)])],r="rare"),
        F(f"{P}-04","Lamassu",3,2,5,["guard"],"Guard."),
        F(f"{P}-05","Enkidu",3,3,3,["rush"],"Rush."),
        F(f"{P}-06","Ishtar",4,3,5,[],"On play: Draw 2 cards.",[A(f"{P}-a06","Star Gate",effects=[E("draw_cards",2)])],r="rare"),
        F(f"{P}-07","Gilgamesh",4,5,4,["rush"],"Rush. On play: Deal 1 damage to an enemy Figure.",[A(f"{P}-a07","Heroic Strike",target_rule="enemy_figure",effects=[E("deal_damage",1)])],r="rare"),
        F(f"{P}-08","Tiamat",5,4,6,[],"On play: Deal 2 damage to all enemy Figures.",[A(f"{P}-a08","Chaos Wave",target_rule="all_enemy_figures",effects=[E("deal_damage",2)])],r="rare"),
        F(f"{P}-09","Marduk",6,5,7,[],"On play: Deal 3 damage to an enemy Figure. Draw 2 cards.",[A(f"{P}-a09","Supreme Decree",target_rule="enemy_figure",effects=[E("deal_damage",3),E("draw_cards",2)])],r="legendary"),
        S(f"{P}-s1","Tablet of Fate",1,"burst","Draw 2 cards.",[A(f"{P}-sa1","Tablet of Fate",trigger="manual",timing="burst",effects=[E("draw_cards",2)])],r="rare"),
        S(f"{P}-s2","Starfire",2,"fast","Deal 3 damage to an enemy Figure.",[A(f"{P}-sa2","Starfire",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s3","Divine Shield",2,"fast","Give a friendly Figure +0/+3 and Guard this turn.",[A(f"{P}-sa3","Divine Shield",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=0,health=3,duration="turn"),E("grant_keyword",keyword="guard",duration="turn")])]),
        S(f"{P}-s4","Prophecy",1,"burst","Draw a card. Gain 1 Ritual Mana.",[A(f"{P}-sa4","Prophecy",trigger="manual",timing="burst",effects=[E("draw_cards",1),E("gain_ritual_mana",1)])]),
        S(f"{P}-s5","Marduk's Choice",3,"fast","Choose: Deal 4 damage to an enemy Figure OR Draw 2 cards and gain 2 Ritual Mana.",
          [A(f"{P}-sa5a","Smite",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",4)]),
           A(f"{P}-sa5b","Foresight",trigger="manual",timing="fast",effects=[E("draw_cards",2),E("gain_ritual_mana",2)])]),
        S(f"{P}-s6","Ward of Ishtar",1,"burst","Give a friendly Figure Ward.",[A(f"{P}-sa6","Ward of Ishtar",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_keyword",keyword="ward")])]),
        R(f"{P}-r1","Star Chart",2,"At the start of your turn, if you have 2+ Ritual Mana, draw a card.",[A(f"{P}-ra1","Star Chart",trigger="on_turn_start",timing="passive",effects=[E("draw_cards",1)])]),
        R(f"{P}-r2","Tablet Press",3,"Activate (1): Draw a card. Once per turn.",[A(f"{P}-ra2","Tablet Press",trigger="manual",timing="slow",resource_cost=1,effects=[E("draw_cards",1)],limit="once_each_turn")]),
    ]

# ================================================================
# MAORI — Haka/Intimidate: debuff enemies, weaken their stats
# ================================================================
def build_maori():
    P = "maori"
    return [
        H(f"{P}-hero","Tu, God of War","Hero Power (2): Give an enemy Figure -1 Attack (permanent).",
          [A(f"{P}-h1","War Face",trigger="manual",target_rule="enemy_figure",timing="slow",resource_cost=2,effects=[E("grant_stats",attack=-1,health=0)])]),
        F(f"{P}-01","War Dancer",1,1,2,[],"On play: Give an enemy Figure -1 Attack.",[A(f"{P}-a01","Intimidate",target_rule="enemy_figure",effects=[E("grant_stats",attack=-1,health=0)])]),
        F(f"{P}-02","Patu Guard",2,1,4,["guard"],"Guard."),
        F(f"{P}-03","Taiaha Warrior",2,3,2,["rush"],"Rush."),
        F(f"{P}-04","Tohunga",3,2,4,[],"On play: Give an enemy Figure -2 Attack.",[A(f"{P}-a04","Weaken",target_rule="enemy_figure",effects=[E("grant_stats",attack=-2,health=0)])],r="rare"),
        F(f"{P}-05","Taniwha",3,3,4,[],"On play: Draw a card.",[A(f"{P}-a05","Deep Sight",effects=[E("draw_cards",1)])]),
        F(f"{P}-06","Maui",4,4,4,["rush"],"Rush. On play: Give an enemy Figure -1 Attack.",[A(f"{P}-a06","Trickster",target_rule="enemy_figure",effects=[E("grant_stats",attack=-1,health=0)])],r="rare"),
        F(f"{P}-07","Rongo",4,3,5,[],"On play: Give all enemy Figures -1 Attack.",[A(f"{P}-a07","Peace Curse",effects=[E("grant_stats",attack=-1,health=0,scope="all_enemy_figures")])],r="rare"),
        F(f"{P}-08","Whiro",5,5,5,[],"On play: Deal 2 damage to an enemy Figure. Give it -2 Attack.",[A(f"{P}-a08","Dark Curse",target_rule="enemy_figure",effects=[E("deal_damage",2),E("grant_stats",attack=-2,health=0)])],r="rare"),
        F(f"{P}-09","Tu",6,6,6,[],"On play: Give all enemy Figures -2 Attack.",[A(f"{P}-a09","Haka",effects=[E("grant_stats",attack=-2,health=0,scope="all_enemy_figures")])],r="legendary"),
        S(f"{P}-s1","Haka Cry",2,"fast","Give an enemy Figure -2 Attack this turn.",[A(f"{P}-sa1","Haka Cry",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("grant_stats",attack=-2,health=0,duration="turn")])]),
        S(f"{P}-s2","Taiaha Strike",2,"fast","Deal 3 damage to an enemy Figure.",[A(f"{P}-sa2","Taiaha Strike",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s3","War Dance",1,"burst","Draw a card.",[A(f"{P}-sa3","War Dance",trigger="manual",timing="burst",effects=[E("draw_cards",1)])]),
        S(f"{P}-s4","Greenstone Shield",2,"fast","Give a friendly Figure +1/+3 this combat.",[A(f"{P}-sa4","Greenstone Shield",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=1,health=3,duration="combat")])]),
        S(f"{P}-s5","Tu's Choice",3,"fast","Choose: Give all enemy Figures -1 Attack OR Deal 3 damage to an enemy Figure.",
          [A(f"{P}-sa5a","Weaken All",trigger="manual",timing="fast",effects=[E("grant_stats",attack=-1,health=0,scope="all_enemy_figures")]),
           A(f"{P}-sa5b","Strike",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s6","Mana Shield",1,"burst","Give a friendly Figure Ward.",[A(f"{P}-sa6","Mana Shield",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_keyword",keyword="ward")])]),
        R(f"{P}-r1","War Mask",2,"After you play a Figure, give a random enemy Figure -1 Attack. Once per turn.",[A(f"{P}-ra1","War Mask",trigger="on_friendly_play",timing="passive",effects=[E("grant_stats",attack=-1,health=0,scope="random_enemy_figure")],limit="once_each_turn")]),
        R(f"{P}-r2","Jade Mere",3,"Activate (1): Give an enemy Figure -2 Attack. Once per turn.",[A(f"{P}-ra2","Jade Mere",trigger="manual",target_rule="enemy_figure",timing="slow",resource_cost=1,effects=[E("grant_stats",attack=-2,health=0)],limit="once_each_turn")]),
    ]

# ================================================================
# SIKH — Unyielding/Armor: armor-based defense, can't be burst
# ================================================================
def build_sikh():
    P = "sikh"
    return [
        H(f"{P}-hero","Guru Gobind Singh","Hero Power (2): Gain 3 Armor.",
          [A(f"{P}-h1","Iron Will",trigger="manual",timing="slow",resource_cost=2,effects=[E("gain_armor",3)])]),
        F(f"{P}-01","Khalsa Scout",1,1,2,[],"On play: Gain 1 Armor.",[A(f"{P}-a01","Iron Spirit",effects=[E("gain_armor",1)])]),
        F(f"{P}-02","Nihangs Guard",2,1,4,["guard"],"Guard."),
        F(f"{P}-03","Akali Warrior",2,3,2,["rush"],"Rush."),
        F(f"{P}-04","Granthi",3,2,4,[],"On play: Gain 3 Armor. Draw a card.",[A(f"{P}-a04","Prayer",effects=[E("gain_armor",3),E("draw_cards",1)])],r="rare"),
        F(f"{P}-05","Singh Sentinel",3,3,4,["guard"],"Guard."),
        F(f"{P}-06","Baba Deep Singh",4,4,4,["rush"],"Rush. On play: Gain 2 Armor.",[A(f"{P}-a06","Unyielding",effects=[E("gain_armor",2)])],r="rare"),
        F(f"{P}-07","Hari Singh Nalwa",4,5,3,["overwhelm"],"Overwhelm. On play: Deal 2 damage to an enemy Figure.",[A(f"{P}-a07","Lion Strike",target_rule="enemy_figure",effects=[E("deal_damage",2)])],r="rare"),
        F(f"{P}-08","Banda Singh",5,4,6,["guard"],"Guard. On play: Gain 5 Armor.",[A(f"{P}-a08","Fortress",effects=[E("gain_armor",5)])],r="rare"),
        F(f"{P}-09","Guru Gobind Singh",6,5,7,[],"On play: Gain 5 Armor. Give all friendly Figures +1/+1.",[A(f"{P}-a09","Khalsa",effects=[E("gain_armor",5),E("grant_stats",attack=1,health=1,scope="all_friendly_figures")])],r="legendary"),
        S(f"{P}-s1","Iron Resolve",2,"burst","Gain 4 Armor.",[A(f"{P}-sa1","Iron Resolve",trigger="manual",timing="burst",effects=[E("gain_armor",4)])]),
        S(f"{P}-s2","Kirpan Strike",2,"fast","Deal 3 damage to an enemy Figure.",[A(f"{P}-sa2","Kirpan Strike",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3)])]),
        S(f"{P}-s3","Langar",1,"burst","Draw a card. Gain 1 Armor.",[A(f"{P}-sa3","Langar",trigger="manual",timing="burst",effects=[E("draw_cards",1),E("gain_armor",1)])]),
        S(f"{P}-s4","Shield of Faith",2,"fast","Give a friendly Figure +0/+3 and Guard this turn.",[A(f"{P}-sa4","Shield of Faith",trigger="manual",target_rule="friendly_figure",timing="fast",effects=[E("grant_stats",attack=0,health=3,duration="turn"),E("grant_keyword",keyword="guard",duration="turn")])]),
        S(f"{P}-s5","Khalsa's Choice",3,"fast","Choose: Gain 5 Armor OR Deal 3 damage to an enemy Figure and gain 2 Armor.",
          [A(f"{P}-sa5a","Defend",trigger="manual",timing="fast",effects=[E("gain_armor",5)]),
           A(f"{P}-sa5b","Strike",trigger="manual",target_rule="enemy_figure",timing="fast",effects=[E("deal_damage",3),E("gain_armor",2)])]),
        S(f"{P}-s6","Waheguru",1,"burst","Give a friendly Figure Ward.",[A(f"{P}-sa6","Waheguru",trigger="manual",target_rule="friendly_figure",timing="burst",effects=[E("grant_keyword",keyword="ward")])]),
        R(f"{P}-r1","Golden Temple",2,"At the start of your turn, gain 2 Armor.",[A(f"{P}-ra1","Golden Temple",trigger="on_turn_start",timing="passive",effects=[E("gain_armor",2)])]),
        R(f"{P}-r2","Chakram",3,"Activate (0): Spend 3 Armor to deal 3 damage to an enemy Figure. Once per turn.",[A(f"{P}-ra2","Chakram",trigger="manual",target_rule="enemy_figure",timing="slow",resource_cost=0,effects=[E("deal_damage",3)],limit="once_each_turn")]),
    ]


def finalize(cards, slug):
    for c in cards:
        c["culture_slug"] = slug; c["set_code"] = f"{slug}-v1"
    return {"culture_slug": slug, "set_code": f"{slug}-v1", "cards": cards}

def auto_deck(cards, hero_id, name):
    """Auto-build a 24-card deck from the pack."""
    figs = [c for c in cards if c["card_type"] == "figure"]
    spls = [c for c in cards if c["card_type"] == "spell"]
    rels = [c for c in cards if c["card_type"] == "relic"]

    figs.sort(key=lambda c: c["cost"])
    entries = []
    fig_count = 0

    # Add 2x cheap figs, 2x mid, 1x expensive
    cheap = [f for f in figs if f["cost"] <= 2]
    mid = [f for f in figs if 3 <= f["cost"] <= 4]
    exp = [f for f in figs if f["cost"] >= 5]

    for f in cheap[:4]:
        entries.append({"id": f["id"], "count": 2}); fig_count += 2
    for f in mid[:3]:
        entries.append({"id": f["id"], "count": 2}); fig_count += 2
    for f in exp[:2]:
        entries.append({"id": f["id"], "count": 1}); fig_count += 1

    # Spells: add first 5 at count 1, first 2 at count 2
    spl_count = 0
    for j, s in enumerate(spls[:6]):
        cnt = 2 if j < 2 else 1
        if fig_count + spl_count + cnt + 2 <= 24:
            entries.append({"id": s["id"], "count": cnt}); spl_count += cnt
        elif fig_count + spl_count + 1 + 2 <= 24:
            entries.append({"id": s["id"], "count": 1}); spl_count += 1

    # Relics: 2
    for r in rels[:2]:
        entries.append({"id": r["id"], "count": 1})

    total = sum(e["count"] for e in entries)
    # Pad to 24
    idx = 0
    while total < 24 and idx < len(spls):
        found = False
        for e in entries:
            if e["id"] == spls[idx]["id"]:
                found = True; break
        if not found:
            entries.append({"id": spls[idx]["id"], "count": 1}); total += 1
        idx += 1
    while total < 24 and mid:
        extra = mid.pop()
        found = any(e["id"] == extra["id"] for e in entries)
        if not found:
            entries.append({"id": extra["id"], "count": 1}); total += 1
    # Trim if over
    while total > 24:
        for e in reversed(entries):
            if e["count"] > 1:
                e["count"] -= 1; total -= 1; break
        else:
            entries.pop(); total = sum(e["count"] for e in entries)

    return {"hero_id": hero_id, "name": name, "notes": [], "cards": entries}


def main():
    builders = [
        ("slavic", build_slavic, "Perun Berserker"),
        ("roman", build_roman, "Mars Legion"),
        ("zoroastrian-persian", build_persian, "Ahura Mazda Dual"),
        ("hawaiian-polynesian", build_hawaiian, "Maui Tide"),
        ("aboriginal-australian", build_aboriginal, "Rainbow Serpent Dream"),
        ("yoruba", build_yoruba, "Ogun Spirits"),
        ("mongolian-shamanist", build_mongol, "Genghis Cavalry"),
        ("babylonian", build_babylonian, "Marduk Prophecy"),
        ("maori", build_maori, "Tu Haka"),
        ("sikh", build_sikh, "Guru Gobind Armor"),
    ]

    for slug, builder, deck_name in builders:
        cards = builder()
        pack = finalize(cards, slug)

        # Save pack
        pack_path = CARDS_DIR / f"{slug}-v1.json"
        pack_path.write_text(json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8")

        # Remove old decks
        for old in list(DECKS_DIR.glob(f"{slug}-*.json")):
            old.unlink()

        # Build and save deck
        hero_id = [c["id"] for c in cards if c["card_type"] == "hero"][0]
        deck = auto_deck(cards, hero_id, deck_name)
        total = sum(e["count"] for e in deck["cards"])
        deck_filename = f"{slug}-{deck_name.lower().replace(' ', '-')}.json"
        deck_path = DECKS_DIR / deck_filename
        deck_path.write_text(json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8")

        figs = sum(e["count"] for e in deck["cards"] if not any(k in e["id"] for k in ["spell","relic","rel-","tok"]))
        spls = sum(e["count"] for e in deck["cards"] if "spell" in e["id"] or e["id"].endswith(("-s1","-s2","-s3","-s4","-s5","-s6")))
        print(f"  {slug}: {len(cards)} pack, {total} deck ({figs}f/{total-figs-2}s/2r)")

    print("\nDone!")

if __name__ == "__main__":
    main()
