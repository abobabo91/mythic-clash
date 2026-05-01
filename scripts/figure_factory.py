"""
Shared helpers for generating balanced figure datasets.
"""

from __future__ import annotations

import json
import os

OUT = "data/figures"
os.makedirs(OUT, exist_ok=True)

STAT_KEYS = ["power", "defense", "speed", "magic", "wisdom"]

TYPE_BASE = {
    "god": {"power": 7, "defense": 7, "speed": 6, "magic": 8, "wisdom": 8},
    "goddess": {"power": 6, "defense": 7, "speed": 6, "magic": 8, "wisdom": 9},
    "hero": {"power": 8, "defense": 7, "speed": 8, "magic": 5, "wisdom": 6},
    "heroine": {"power": 7, "defense": 7, "speed": 8, "magic": 6, "wisdom": 7},
    "spirit": {"power": 4, "defense": 5, "speed": 7, "magic": 8, "wisdom": 7},
    "creature": {"power": 7, "defense": 7, "speed": 7, "magic": 6, "wisdom": 5},
    "monster": {"power": 8, "defense": 6, "speed": 7, "magic": 7, "wisdom": 4},
    "demon": {"power": 8, "defense": 6, "speed": 6, "magic": 8, "wisdom": 4},
    "ancestor": {"power": 5, "defense": 6, "speed": 5, "magic": 7, "wisdom": 8},
    "guardian": {"power": 7, "defense": 8, "speed": 5, "magic": 6, "wisdom": 6},
}

RARITY_BONUS = {
    "common": 0,
    "uncommon": 2,
    "rare": 4,
    "legendary": 7,
}

DOMAIN_PRIORITY = {
    "sun": ["power", "magic", "wisdom"],
    "moon": ["magic", "wisdom", "speed"],
    "light": ["magic", "wisdom", "power"],
    "darkness": ["magic", "power", "defense"],
    "death": ["magic", "power", "wisdom"],
    "underworld": ["magic", "defense", "power"],
    "war": ["power", "defense", "speed"],
    "storm": ["power", "magic", "speed"],
    "thunder": ["power", "magic", "speed"],
    "fire": ["power", "magic", "speed"],
    "water": ["magic", "speed", "wisdom"],
    "sea": ["magic", "speed", "defense"],
    "rain": ["magic", "wisdom", "speed"],
    "wind": ["speed", "magic", "power"],
    "sky": ["magic", "wisdom", "speed"],
    "earth": ["defense", "wisdom", "power"],
    "mountain": ["defense", "power", "wisdom"],
    "forest": ["speed", "wisdom", "magic"],
    "animal": ["speed", "power", "defense"],
    "serpent": ["speed", "magic", "power"],
    "dragon": ["power", "magic", "defense"],
    "fertility": ["wisdom", "magic", "defense"],
    "wisdom": ["wisdom", "magic", "defense"],
    "trickster": ["speed", "magic", "wisdom"],
    "healing": ["wisdom", "magic", "defense"],
    "love": ["magic", "speed", "wisdom"],
    "creation": ["magic", "wisdom", "defense"],
    "destruction": ["power", "magic", "defense"],
    "justice": ["wisdom", "power", "defense"],
    "ancestor": ["wisdom", "defense", "magic"],
    "spirit": ["magic", "wisdom", "speed"],
    "agriculture": ["wisdom", "defense", "magic"],
    "corn": ["wisdom", "defense", "magic"],
    "rice": ["wisdom", "defense", "magic"],
    "iron": ["power", "defense", "wisdom"],
    "hunting": ["speed", "power", "wisdom"],
}

ABILITY_NAMES = {
    "sun": "Solar Ascendance",
    "moon": "Moonlit Veil",
    "light": "Radiant Aegis",
    "darkness": "Shadow Eclipse",
    "death": "Grave Call",
    "underworld": "Chthonic Gate",
    "war": "Battle Surge",
    "storm": "Storm Crown",
    "thunder": "Thunder Spear",
    "fire": "Ember Wrath",
    "water": "Tidal Ward",
    "sea": "Ocean's Claim",
    "rain": "Monsoon Blessing",
    "wind": "Sky-Rider Rush",
    "sky": "Vault of Heaven",
    "earth": "Stoneheart Guard",
    "mountain": "Peak Resolve",
    "forest": "Wildwood Pact",
    "animal": "Primal Charge",
    "serpent": "Coiled Fate",
    "dragon": "Dragon's Breath",
    "fertility": "Harvest Plenty",
    "wisdom": "Ancient Counsel",
    "trickster": "Clever Reversal",
    "healing": "Restoring Rite",
    "love": "Binding Charm",
    "creation": "World-Seed",
    "destruction": "Ruinous Blow",
    "justice": "Judgment Oath",
    "ancestor": "Elder Memory",
    "spirit": "Otherworld Touch",
    "agriculture": "Field Blessing",
    "corn": "Golden Grain",
    "rice": "Abundant Harvest",
    "iron": "Forged Will",
    "hunting": "Hunter's Mark",
}

ABILITY_TEXT = {
    "sun": "Deal 8 damage to one dark-aligned enemy and grant allied cards +2 power this turn.",
    "moon": "Give one allied card stealth for 2 turns and restore 4 HP.",
    "light": "Remove one negative effect from all allies and raise their wisdom by 2.",
    "darkness": "Reduce all enemy stats by 2 for 1 turn and drain 3 life from the weakest foe.",
    "death": "Revive one fallen ally at half stats or deal 7 damage to an injured enemy.",
    "underworld": "Banish one enemy card for 1 turn and weaken it by 2 defense on return.",
    "war": "All allied attackers gain +3 power and +1 speed this turn.",
    "storm": "Strike all enemies for 4 damage and stun the fastest target.",
    "thunder": "Deal 9 damage to one target and chain 3 damage to another enemy.",
    "fire": "Burn the opposing field for 3 damage now and 2 more next turn.",
    "water": "Heal all allies for 3 HP and negate the next fire effect played against them.",
    "sea": "Pull one enemy out of position and lower its speed by 3.",
    "rain": "Restore 5 HP across your field and reduce enemy fire power by 2.",
    "wind": "Move freely, dodge the next attack, and gain +3 speed this turn.",
    "sky": "Reveal hidden enemies and grant all allies +2 magic.",
    "earth": "Grant one ally +4 defense and create a shield that absorbs 6 damage.",
    "mountain": "This card becomes immovable for 2 turns and gains +3 defense.",
    "forest": "Summon a wild ally token and heal your weakest card for 4 HP.",
    "animal": "Rush a target for 7 damage, then retreat without taking counter damage.",
    "serpent": "Poison one enemy for 2 turns and steal 2 speed from it.",
    "dragon": "Deal 10 damage to one enemy and frighten adjacent foes.",
    "fertility": "Double resource growth for 1 turn and heal all allies for 2 HP.",
    "wisdom": "Look at the top 3 cards, draw 1, and give an ally +2 wisdom.",
    "trickster": "Swap the highest and lowest stats of one enemy for 2 turns.",
    "healing": "Restore one ally to full HP and remove one curse from it.",
    "love": "Charm one enemy for 1 turn or create a protective bond between 2 allies.",
    "creation": "Create a 5/5/5/5/5 spirit token with the same alignment as this card.",
    "destruction": "Deal 8 damage and lower the target's defense by 3 permanently.",
    "justice": "Expose one enemy card; if it has higher power than wisdom, stun it for 1 turn.",
    "ancestor": "Call on the elders to block the next attack against any ally.",
    "spirit": "Phase through danger, avoid the next hit, and gain +2 magic.",
    "agriculture": "Gain 3 resource tokens and grant all earth allies +1 defense.",
    "corn": "Feed the field: all allied cards recover 3 HP and +1 wisdom.",
    "rice": "Generate 3 resource tokens and cleanse one allied debuff.",
    "iron": "Gain +3 power and +2 defense until the end of the turn.",
    "hunting": "Mark a target; all damage dealt to it this turn is increased by 2.",
}

DARK_DOMAINS = {
    "darkness",
    "death",
    "underworld",
    "chaos",
    "night",
    "curse",
    "demon",
    "monster",
    "plague",
    "revenge",
}

LIGHT_DOMAINS = {
    "sun",
    "light",
    "healing",
    "fertility",
    "wisdom",
    "creation",
    "justice",
    "harvest",
    "mercy",
}


def infer_alignment(domains, ftype):
    domain_set = set(domains)
    if domain_set & DARK_DOMAINS:
        return "dark"
    if domain_set & LIGHT_DOMAINS:
        return "light"
    if ftype in {"demon", "monster"}:
        return "dark"
    return "neutral"


def statline(ftype, domains, rarity, alignment):
    stats = dict(TYPE_BASE.get(ftype, TYPE_BASE["spirit"]))
    priorities = []
    for domain in domains:
        priorities.extend(DOMAIN_PRIORITY.get(domain, []))

    if not priorities:
        priorities = ["power", "magic", "wisdom", "defense", "speed"]

    if alignment == "light":
        priorities = ["wisdom", "magic"] + priorities
    elif alignment == "dark":
        priorities = ["power", "magic"] + priorities

    seen = []
    for key in priorities + ["power", "defense", "speed", "magic", "wisdom"]:
        if key not in seen:
            seen.append(key)

    points = RARITY_BONUS[rarity]
    idx = 0
    while points > 0:
        key = seen[idx % len(seen)]
        if stats[key] < 10:
            stats[key] += 1
            points -= 1
        idx += 1

    def shift(up_key, down_key):
        if stats[up_key] < 10 and stats[down_key] > 3:
            stats[up_key] += 1
            stats[down_key] -= 1

    for domain in domains:
        if domain in {"war", "fire", "storm", "thunder", "dragon"}:
            shift("power", "wisdom")
        elif domain in {"wisdom", "ancestor", "justice"}:
            shift("wisdom", "speed")
        elif domain in {"wind", "trickster", "animal", "hunting"}:
            shift("speed", "defense")
        elif domain in {"earth", "mountain", "protection"}:
            shift("defense", "speed")
        elif domain in {"sea", "water", "moon", "spirit"}:
            shift("magic", "power")

    return stats


def ability_for(domains):
    for domain in domains:
        if domain in ABILITY_NAMES:
            return ABILITY_NAMES[domain], ABILITY_TEXT[domain]
    return "Mythic Presence", "Grant one allied card +2 to all stats until end of turn."


def describe(name, ftype, domains, culture_name, note=None):
    if note:
        return note
    domain_text = ", ".join(domains[:-1]) + f", and {domains[-1]}" if len(domains) > 1 else domains[0]
    article = "an" if ftype[:1].lower() in {"a", "e", "i", "o", "u"} else "a"
    return f"{name} is {article} {ftype} from {culture_name} tradition associated with {domain_text}."


def build_figure(culture_name, name, ftype, domains, rarity, note=None, alignment=None):
    alignment = alignment or infer_alignment(domains, ftype)
    stats = statline(ftype, domains, rarity, alignment)
    ability_name, ability_desc = ability_for(domains)
    return {
        "name": name,
        "type": ftype,
        "domains": domains,
        "stats": stats,
        "rarity": rarity,
        "alignment": alignment,
        "ability": {"name": ability_name, "description": ability_desc},
        "description": describe(name, ftype, domains, culture_name, note),
    }


def E(name, ftype, domains, rarity, note=None, alignment=None):
    return (name, ftype, domains, rarity, note, alignment)


def L(name, ftype, domains, note=None, alignment=None):
    return E(name, ftype, domains, "legendary", note, alignment)


def R(name, ftype, domains, note=None, alignment=None):
    return E(name, ftype, domains, "rare", note, alignment)


def U(name, ftype, domains, note=None, alignment=None):
    return E(name, ftype, domains, "uncommon", note, alignment)


def C(name, ftype, domains, note=None, alignment=None):
    return E(name, ftype, domains, "common", note, alignment)


def save(slug, culture_name, entries):
    figures = [build_figure(culture_name, *entry) for entry in entries]
    for i, figure in enumerate(figures, 1):
        figure["id"] = f"{slug}-{i:03d}"
        figure["culture_slug"] = slug
    with open(f"{OUT}/{slug}.json", "w", encoding="utf-8") as fh:
        json.dump(
            {"culture_slug": slug, "count": len(figures), "figures": figures},
            fh,
            indent=2,
            ensure_ascii=False,
        )
    print(f"  {slug}: {len(figures)} figures")
