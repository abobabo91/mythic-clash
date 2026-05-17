"""Upgrade batch 3: 10 cultures with unique mechanics."""
import json
from pathlib import Path

DATA = Path("data/cards-v1")


def load_pack(slug):
    return json.loads((DATA / f"{slug}-v1.json").read_text(encoding="utf-8"))


def save_pack(slug, pack):
    (DATA / f"{slug}-v1.json").write_text(
        json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def spell(sid, name, cost, speed, text, target="none", effects=None):
    return {
        "id": sid, "name": name, "card_type": "spell", "cost": cost,
        "speed": speed, "rarity": "common", "rules_text": text,
        "extra": {"abilities": [{"trigger": "on_play", "target_rule": target, "effects": effects or []}]},
    }


def relic(sid, name, cost, text, ability):
    return {
        "id": sid, "name": name, "card_type": "relic", "cost": cost,
        "rarity": "rare", "rules_text": text, "extra": {"abilities": [ability]},
    }


def uf(card, kw=None, text="", atk=0, hp=0, abilities=None):
    """Upgrade a figure in-place."""
    if kw is not None:
        card["keywords"] = kw
    if text:
        card["rules_text"] = text
    if atk:
        card["attack"] = max(1, card.get("attack", 1) + atk)
    if hp:
        card["health"] = max(1, card.get("health", 1) + hp)
    if abilities is not None:
        card.setdefault("extra", {})["abilities"] = abilities


def on_play(target, effects):
    return [{"trigger": "on_play", "target_rule": target, "effects": effects}]


def dmg(n):
    return {"kind": "deal_damage", "amount": n}


def draw(n=1):
    return {"kind": "draw_cards", "amount": n}


def buff(a, h):
    return {"kind": "buff", "attack": a, "health": h}


def freeze():
    return {"kind": "freeze"}


def ward():
    return {"kind": "grant_keyword", "keyword": "divine_shield"}


def armor(n):
    return {"kind": "gain_armor", "amount": n}


def ritual(n=1):
    return {"kind": "gain_ritual_mana", "amount": n}


# ============================================================
CULTURES = {}

# --- FINNISH-KARELIAN: Spell Mastery ---
def build_finnish():
    pack = load_pack("finnish-karelian")
    cards = [c for c in pack["cards"] if c["card_type"] not in ("spell", "relic")]
    by_name = {c["name"]: c for c in cards if c["card_type"] == "figure"}

    uf(by_name["Väinämöinen"], text="On play: Draw 2 cards.", abilities=on_play("none", [draw(2)]))
    uf(by_name["Ukko"], text="On play: Deal 3 damage to all enemy Figures.", abilities=on_play("all_enemy_figures", [dmg(3)]))
    uf(by_name["Louhi"], kw=["guard"], text="Guard. On play: Freeze an enemy Figure.", abilities=on_play("enemy_figure", [freeze()]))
    uf(by_name["Ilmarinen"], text="On play: Give a friendly Figure +2/+2.", abilities=on_play("friendly_figure", [buff(2, 2)]))
    uf(by_name["Lemminkäinen"], kw=["rush", "overwhelm"], text="Rush. Overwhelm.", atk=1)
    uf(by_name["Ahti"], kw=["lifesteal"], text="Lifesteal. On play: Draw a card.", abilities=on_play("none", [draw()]))
    uf(by_name["Mielikki"], kw=["guard"], text="Guard. On play: Heal your Hero for 3.", abilities=on_play("none", [{"kind": "heal_hero", "amount": 3}]))
    uf(by_name["Tursas"], kw=["rush"], text="Rush. On play: Deal 2 damage to an enemy Figure.", abilities=on_play("enemy_figure", [dmg(2)]))
    uf(by_name["Kokko the Eagle"], kw=["charge"], text="Charge.", atk=1, hp=-1)
    uf(by_name["Kuutar"], text="On play: Draw a card.", abilities=on_play("none", [draw()]))

    cards += [
        spell("fk-s1", "Rune Storm", 3, "fast", "Deal 3 damage to an enemy character.", "enemy_character", [dmg(3)]),
        spell("fk-s1b", "Rune Storm", 3, "fast", "Deal 3 damage to an enemy character.", "enemy_character", [dmg(3)]),
        spell("fk-s2", "Kantele Song", 2, "burst", "Draw 2 cards.", "none", [draw(2)]),
        spell("fk-s2b", "Kantele Song", 2, "burst", "Draw 2 cards.", "none", [draw(2)]),
        spell("fk-s3", "Ice Ward", 2, "fast", "Give a friendly Figure +0/+3 and Ward.", "friendly_figure", [buff(0, 3), ward()]),
        spell("fk-s4", "Kalevala Bolt", 1, "fast", "Deal 2 damage to an enemy Figure.", "enemy_figure", [dmg(2)]),
        spell("fk-s5", "Frost Bind", 2, "fast", "Freeze an enemy Figure. Draw a card.", "enemy_figure", [freeze(), draw()]),
        spell("fk-s6", "Sampo's Gift", 3, "burst", "Choose: Deal 2 damage to all enemies OR Give all friendly Figures +1/+1.", "none", [{"kind": "deal_damage_all_enemies", "amount": 2}]),
        relic("fk-r1", "The Sampo", 3, "Activated (2 mana): Draw a card and deal 1 damage to the enemy Hero.",
              {"trigger": "activated", "cost": 2, "target_rule": "none", "effects": [draw(), {"kind": "deal_damage_hero", "amount": 1}]}),
        relic("fk-r2", "Väinämöinen's Kantele", 2, "After you cast a spell, give a random friendly Figure +1 Health.",
              {"trigger": "on_spell_cast", "target_rule": "random_friendly_figure", "effects": [buff(0, 1)]}),
    ]
    pack["cards"] = cards
    save_pack("finnish-karelian", pack)


# --- MAYA: Prophecy/Calendar ---
def build_maya():
    pack = load_pack("maya")
    cards = [c for c in pack["cards"] if c["card_type"] not in ("spell", "relic")]
    by_name = {c["name"]: c for c in cards if c["card_type"] == "figure"}

    uf(by_name["Itzamna"], text="On play: Deal 2 damage to all enemy Figures. Draw a card.",
       abilities=on_play("all_enemy_figures", [dmg(2)]) + on_play("none", [draw()]))
    uf(by_name["Kukulkan"], kw=["charge", "overwhelm"], text="Charge. Overwhelm.", atk=1)
    uf(by_name["Ix Chel"], kw=["lifesteal"], text="Lifesteal. On play: Heal all friendly Figures for 2.",
       abilities=on_play("all_friendly_figures", [{"kind": "heal", "amount": 2}]))
    uf(by_name["Hunahpu"], kw=["rush"], text="Rush. On play: Give another friendly Figure +2 Attack.",
       abilities=on_play("friendly_figure", [buff(2, 0)]))
    uf(by_name["Zipacna"], kw=["guard", "reborn"], text="Guard. Reborn.")
    uf(by_name["Bacab"], kw=["guard"], text="Guard. On play: Gain 2 Armor.", abilities=on_play("none", [armor(2)]))
    uf(by_name["Vucub Caquix"], kw=["poisonous"], text="Poisonous. On play: Deal 1 damage to an enemy Figure.",
       abilities=on_play("enemy_figure", [dmg(1)]))
    uf(by_name["Xmucane"], text="On play: Draw a card.", abilities=on_play("none", [draw()]))
    uf(by_name["Gucumatz"], kw=["stealth"], text="Stealth. On play: Draw a card.", abilities=on_play("none", [draw()]))
    uf(by_name.get("Xpiyacoc", by_name.get("Ixtab", {})), text="On play: Give a friendly Figure +1/+1.",
       abilities=on_play("friendly_figure", [buff(1, 1)]))

    cards += [
        spell("maya-s1", "Sun Strike", 3, "fast", "Deal 3 damage to an enemy character.", "enemy_character", [dmg(3)]),
        spell("maya-s1b", "Sun Strike", 3, "fast", "Deal 3 damage to an enemy character.", "enemy_character", [dmg(3)]),
        spell("maya-s2", "Blood Rite", 1, "burst", "Deal 2 damage to your Hero. Draw 2 cards.", "none",
              [{"kind": "damage_own_hero", "amount": 2}, draw(2)]),
        spell("maya-s2b", "Blood Rite", 1, "burst", "Deal 2 damage to your Hero. Draw 2 cards.", "none",
              [{"kind": "damage_own_hero", "amount": 2}, draw(2)]),
        spell("maya-s3", "Jade Shield", 2, "fast", "Give a friendly Figure +0/+3 and Guard.", "friendly_figure",
              [buff(0, 3), {"kind": "grant_keyword", "keyword": "guard"}]),
        spell("maya-s4", "Calendar of Doom", 5, "slow", "Deal 3 damage to all enemy Figures.", "none",
              [{"kind": "deal_damage_all_enemies", "amount": 3}]),
        spell("maya-s5", "Stargazer's Vision", 1, "burst", "Draw a card.", "none", [draw()]),
        spell("maya-s6", "Serpent's Choice", 3, "fast", "Choose: Deal 4 damage to an enemy Figure OR Give a friendly Figure +3 Attack.",
              "enemy_figure", [dmg(4)]),
        relic("maya-r1", "Jade Codex", 3, "Activated (2 mana): Draw a card.",
              {"trigger": "activated", "cost": 2, "target_rule": "none", "effects": [draw()]}),
        relic("maya-r2", "Obsidian Mirror", 2, "After you play a Figure, deal 1 damage to all enemy Figures.",
              {"trigger": "on_figure_play", "target_rule": "all_enemy_figures", "effects": [dmg(1)]}),
    ]
    pack["cards"] = cards
    save_pack("maya", pack)


def build_generic(slug, spell_names, relic_names, figure_upgrades):
    """Build a culture with standard spell/relic templates + custom figure upgrades."""
    pack = load_pack(slug)
    cards = [c for c in pack["cards"] if c["card_type"] not in ("spell", "relic")]
    by_name = {c["name"]: c for c in cards if c["card_type"] == "figure"}

    # Apply figure upgrades
    for name, kwargs in figure_upgrades.items():
        if name in by_name:
            uf(by_name[name], **kwargs)
        else:
            # Try partial match
            for fn in by_name:
                if name.lower() in fn.lower():
                    uf(by_name[fn], **kwargs)
                    break

    sn = spell_names
    rn = relic_names
    s = slug

    cards += [
        spell(f"{s}-s1", sn[0], 3, "fast", "Deal 3 damage to an enemy character.", "enemy_character", [dmg(3)]),
        spell(f"{s}-s1b", sn[0], 3, "fast", "Deal 3 damage to an enemy character.", "enemy_character", [dmg(3)]),
        spell(f"{s}-s2", sn[1], 2, "fast", "Give a friendly Figure +0/+3 and Ward.", "friendly_figure", [buff(0, 3), ward()]),
        spell(f"{s}-s3", sn[2], 2, "burst", "Give a friendly Figure +2 Attack this turn.", "friendly_figure", [{"kind": "buff_temp", "attack": 2}]),
        spell(f"{s}-s4", sn[3], 2, "burst", "Draw 2 cards.", "none", [draw(2)]),
        spell(f"{s}-s5", sn[4], 5, "slow", "Deal 2 damage to all enemy Figures.", "none", [{"kind": "deal_damage_all_enemies", "amount": 2}]),
        spell(f"{s}-s6", sn[5], 1, "burst", "Draw a card.", "none", [draw()]),
        spell(f"{s}-s7", sn[6], 3, "fast", "Choose: Deal 4 damage to an enemy Figure OR Heal your Hero for 4.", "enemy_figure", [dmg(4)]),
        relic(f"{s}-r1", rn[0], 3, "Activated (2 mana): Deal 2 damage to the enemy Hero.",
              {"trigger": "activated", "cost": 2, "target_rule": "none", "effects": [{"kind": "deal_damage_hero", "amount": 2}]}),
        relic(f"{s}-r2", rn[1], 2, "After you cast a spell, draw a card.",
              {"trigger": "on_spell_cast", "target_rule": "none", "effects": [draw()]}),
    ]
    pack["cards"] = cards
    save_pack(slug, pack)


# --- ZULU: Formation/Aura ---
def build_zulu():
    build_generic("zulu",
        ["Assegai Strike", "Shield Wall", "War Cry", "Battle Drum", "Impi Charge", "Sangoma Vision", "Warrior's Choice"],
        ["War Shield", "Sangoma Drum"],
        {
            "Unkulunkulu": {"kw": ["guard", "overwhelm"], "text": "Guard. Overwhelm. On play: Give all friendly Figures +1 Attack.", "abilities": on_play("all_friendly_figures", [buff(1, 0)])},
            "Inkosazana": {"text": "On play: Draw 2 cards. Heal your Hero for 3.", "abilities": on_play("none", [draw(2), {"kind": "heal_hero", "amount": 3}])},
            "Inkanyamba": {"kw": ["rush", "overwhelm"], "text": "Rush. Overwhelm."},
            "Tokoloshe": {"kw": ["stealth"], "text": "Stealth. On play: Deal 2 damage to an enemy Figure.", "abilities": on_play("enemy_figure", [dmg(2)])},
            "Mamlambo": {"kw": ["guard"], "text": "Guard. On play: Give a friendly Figure +1/+2.", "abilities": on_play("friendly_figure", [buff(1, 2)])},
            "Thikoloshe": {"kw": ["rush"], "text": "Rush. On play: Draw a card.", "abilities": on_play("none", [draw()])},
            "Sangoma Snake": {"text": "On play: Draw a card.", "abilities": on_play("none", [draw()])},
            "Lightning Bird": {"kw": ["charge"], "text": "Charge.", "atk": 1, "hp": -1},
            "Ndlovu": {"kw": ["guard", "reborn"], "text": "Guard. Reborn."},
            "Amadlozi": {"text": "On play: Give a friendly Figure +1 Health.", "abilities": on_play("friendly_figure", [buff(0, 1)])},
        })


# --- KOREAN: Spirit/Haunt ---
def build_korean():
    build_generic("korean",
        ["Spirit Bolt", "Ancestor's Blessing", "Ghost Wail", "Mudang Vision", "Haetae's Judgment", "Spirit Sight", "Spirit's Choice"],
        ["Spirit Mirror", "Dokkaebi Lantern"],
        {
            "Dangun Wanggeom": {"text": "On play: Deal 3 damage to an enemy Figure. Draw a card.", "abilities": on_play("enemy_figure", [dmg(3)]) + on_play("none", [draw()])},
            "Hwanung": {"kw": ["reborn"], "text": "Reborn. On play: Give a friendly Figure +1/+1.", "abilities": on_play("friendly_figure", [buff(1, 1)])} if "Hwanung" in "" else {},
            # Apply to figures by position since we don't know all names
        })
    # Patch Korean figures by index
    pack = load_pack("korean")
    figs = [c for c in pack["cards"] if c["card_type"] == "figure"]
    for i, f in enumerate(figs):
        cost = f.get("cost", 3)
        if cost >= 6 and "abilities" not in f.get("extra", {}):
            uf(f, kw=["reborn"], text="Reborn. On play: Return a friendly Figure from discard to hand.", abilities=on_play("none", [{"kind": "return_from_discard"}]))
        elif cost == 5 and i % 2 == 0 and "abilities" not in f.get("extra", {}):
            uf(f, kw=["rush"], text="Rush. On play: Deal 2 damage to an enemy Figure.", abilities=on_play("enemy_figure", [dmg(2)]))
        elif cost == 5 and "abilities" not in f.get("extra", {}):
            uf(f, kw=["guard", "reborn"], text="Guard. Reborn.")
        elif cost == 4 and i % 2 == 0 and "abilities" not in f.get("extra", {}):
            uf(f, kw=["rush"], text="Rush. On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost == 4 and "abilities" not in f.get("extra", {}):
            uf(f, kw=["guard"], text="Guard. On play: Freeze an enemy Figure.", abilities=on_play("enemy_figure", [freeze()]))
        elif cost == 3 and "abilities" not in f.get("extra", {}):
            uf(f, text="On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost <= 2 and i % 2 == 0 and "abilities" not in f.get("extra", {}):
            uf(f, kw=["stealth"], text="Stealth. On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost <= 2 and "abilities" not in f.get("extra", {}):
            uf(f, text="On play: Give a friendly Figure +1 Health.", abilities=on_play("friendly_figure", [buff(0, 1)]))
    save_pack("korean", pack)


# --- INCA: Ramp/Big ---
def build_inca():
    build_generic("inca-andean",
        ["Sun Strike", "Terrace Wall", "Inti's Fire", "Quipu Draw", "Mountain Fury", "Sun Reading", "Condor's Choice"],
        ["Sun Disc", "Quipu Record"],
        {
            "Viracocha": {"text": "On play: Draw 2 cards. Gain 1 Ritual Mana.", "abilities": on_play("none", [draw(2), ritual()])},
            "Inti": {"kw": ["charge", "overwhelm"], "text": "Charge. Overwhelm.", "atk": 1},
            "Mama Ocllo": {"text": "On play: Draw a card. Give a friendly Figure +1/+1.", "abilities": on_play("none", [draw()]) + on_play("friendly_figure", [buff(1, 1)])},
            "Pariacaca": {"kw": ["rush"], "text": "Rush. On play: Deal 3 damage to an enemy Figure.", "abilities": on_play("enemy_figure", [dmg(3)])},
            "Catequil": {"kw": ["rush"], "text": "Rush. On play: Gain 1 Ritual Mana.", "abilities": on_play("none", [ritual()])},
            "Supay": {"kw": ["guard", "lifesteal"], "text": "Guard. Lifesteal."},
            "Ayar Cachi": {"kw": ["rush"], "text": "Rush.", "atk": 1},
            "Mama Quilla": {"text": "On play: Heal your Hero for 3. Draw a card.", "abilities": on_play("none", [{"kind": "heal_hero", "amount": 3}, draw()])},
        })


# --- SUMERIAN: Law/Order ---
def build_sumerian():
    build_generic("sumerian",
        ["Decree of An", "Tablet Ward", "Law of Ur", "Scribe's Draw", "Flood Judgment", "Star Reading", "King's Choice"],
        ["Tablet of Law", "Ziggurat Altar"],
        {})
    # Patch figures
    pack = load_pack("sumerian")
    figs = [c for c in pack["cards"] if c["card_type"] == "figure"]
    for i, f in enumerate(figs):
        cost = f.get("cost", 3)
        if cost >= 6:
            uf(f, text="On play: Deal 2 damage to all enemy Figures. Draw a card.", abilities=on_play("all_enemy_figures", [dmg(2)]) + on_play("none", [draw()]))
        elif cost == 5 and i % 3 == 0:
            uf(f, kw=["rush", "overwhelm"], text="Rush. Overwhelm.")
        elif cost == 5 and i % 3 == 1:
            uf(f, kw=["guard", "reborn"], text="Guard. Reborn.")
        elif cost == 5:
            uf(f, text="On play: Return an enemy Figure to its owner's hand.", abilities=on_play("enemy_figure", [{"kind": "bounce"}]))
        elif cost == 4 and i % 2 == 0:
            uf(f, kw=["rush"], text="Rush. On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost == 4:
            uf(f, kw=["guard"], text="Guard. On play: Give a friendly Figure +1/+1.", abilities=on_play("friendly_figure", [buff(1, 1)]))
        elif cost == 3 and i % 2 == 0:
            uf(f, text="On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost == 3:
            uf(f, kw=["guard"], text="Guard.")
        elif cost <= 2 and i % 2 == 0:
            uf(f, text="On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost <= 2:
            uf(f, kw=["rush"], text="Rush.")
    save_pack("sumerian", pack)


# For the remaining 4, use the same pattern
def build_remaining(slug, spell_names, relic_names):
    build_generic(slug, spell_names, relic_names, {})
    pack = load_pack(slug)
    figs = [c for c in pack["cards"] if c["card_type"] == "figure"]
    for i, f in enumerate(figs):
        cost = f.get("cost", 3)
        if cost >= 6:
            uf(f, text="On play: Deal 2 damage to all enemy Figures. Draw a card.", abilities=on_play("all_enemy_figures", [dmg(2)]) + on_play("none", [draw()]))
        elif cost == 5 and i % 3 == 0:
            uf(f, kw=["rush", "overwhelm"], text="Rush. Overwhelm.")
        elif cost == 5 and i % 3 == 1:
            uf(f, kw=["guard", "reborn"], text="Guard. Reborn.")
        elif cost == 5:
            uf(f, text="On play: Return an enemy Figure to its owner's hand.", abilities=on_play("enemy_figure", [{"kind": "bounce"}]))
        elif cost == 4 and i % 2 == 0:
            uf(f, kw=["rush"], text="Rush. On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost == 4:
            uf(f, kw=["guard"], text="Guard. On play: Freeze an enemy Figure.", abilities=on_play("enemy_figure", [freeze()]))
        elif cost == 3 and i % 2 == 0:
            uf(f, text="On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost == 3:
            uf(f, kw=["guard"], text="Guard.")
        elif cost <= 2 and i % 3 == 0:
            uf(f, text="On play: Draw a card.", abilities=on_play("none", [draw()]))
        elif cost <= 2 and i % 3 == 1:
            uf(f, kw=["stealth"], text="Stealth.")
        elif cost <= 2:
            uf(f, kw=["rush"], text="Rush.")
    save_pack(slug, pack)


# ============================================================
# BUILD ALL
# ============================================================
if __name__ == "__main__":
    build_finnish()
    print("finnish-karelian: done")

    build_maya()
    print("maya: done")

    build_zulu()
    print("zulu: done")

    build_korean()
    print("korean: done")

    build_inca()
    print("inca-andean: done")

    build_sumerian()
    print("sumerian: done")

    build_remaining("filipino-tagalog",
        ["Aswang Strike", "Diwata Shield", "Tikbalang Shift", "Babaylan Draw", "Bagyo Storm", "Ancestor Sight", "Diwata's Choice"],
        ["Agimat Charm", "Babaylan Staff"])
    print("filipino-tagalog: done")

    build_remaining("igbo",
        ["Chi Strike", "Ofo Ward", "Ancestor Call", "Dibia Draw", "Amadioha's Wrath", "Oracle Sight", "Ala's Choice"],
        ["Ofo Staff", "Ikenga Shrine"])
    print("igbo: done")

    build_remaining("lakota-sioux",
        ["Thunder Arrow", "Vision Shield", "Spirit Walk", "Medicine Draw", "Storm Fury", "Vision Sight", "Eagle's Choice"],
        ["Sacred Pipe", "Medicine Wheel"])
    print("lakota-sioux: done")

    build_remaining("berber-amazigh",
        ["Desert Strike", "Sand Shield", "Nomad Rush", "Scout's Report", "Sandstorm", "Star Sight", "Wanderer's Choice"],
        ["Silver Amulet", "Caravan Horn"])
    print("berber-amazigh: done")

    print("\nAll 10 batch 3 cultures upgraded!")
