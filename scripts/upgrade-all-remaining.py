"""Upgrade all 60 remaining cultures using the batch 4 pattern."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

DATA = Path("data/cards-v1")
DECKS = Path("data/decks-v1")

DONE = {
    "norse-viking", "ancient-egyptian", "ancient-greek",
    "japanese-shinto", "celtic-irish", "vedic-hindu", "haitian-vodou",
    "aztec-mexica", "ancient-chinese", "inuit",
    "slavic", "roman", "zoroastrian-persian", "hawaiian-polynesian",
    "aboriginal-australian", "yoruba", "mongolian-shamanist",
    "babylonian", "maori", "sikh",
    "finnish-karelian", "maya", "zulu", "korean", "inca-andean",
    "sumerian", "filipino-tagalog", "igbo", "lakota-sioux", "berber-amazigh",
    "ainu", "akan", "akkadian", "algonquian-ojibwe", "apache",
    "arabian-pre-islamic", "armenian", "assyrian", "balinese-hindu-buddhist", "baltic-lithuanian",
}

# Find all remaining cultures
ALL = sorted(
    p.stem.replace("-v1", "")
    for p in DATA.glob("*-v1.json")
    if "neutral" not in p.stem and "domain" not in p.stem
)
REMAINING = [c for c in ALL if c not in DONE]


def eff(kind, amount=None, attack=None, health=None, keyword=None, scope=None):
    return {
        "kind": kind, "amount": amount, "attack": attack, "health": health,
        "keyword": keyword, "duration": None, "scope": scope,
        "pool": None, "card_id": None, "extra": {},
    }


def ab(aid, label, trigger, target, effects, timing="slow", cost=None):
    return {
        "id": aid, "label": label, "timing": timing, "trigger": trigger,
        "target_rule": target, "resource_cost": cost, "conditions": [],
        "effects": effects, "limit": None,
    }


CARD_DEFAULTS = {
    "alignment": "", "collectible": True, "flavor_text": "", "legendary": False,
    "set_code": "v1", "subtypes": [], "token": False, "traits": [], "unique": False,
}


def make_spell(sid, name, cost, speed, text, target, effects):
    timing = speed
    card = dict(CARD_DEFAULTS)
    card.update({
        "id": sid, "name": name, "card_type": "spell", "cost": cost,
        "speed": speed, "rarity": "common", "rules_text": text,
        "culture_slug": sid.split("-s")[0] if "-s" in sid else sid.rsplit("-", 1)[0],
        "keywords": [], "attack": 0, "health": 0,
        "abilities": [ab(f"{sid}-ab0", name, "on_play", target, effects, timing)],
    })
    return card


def make_relic(sid, name, cost, text, trigger, target, effects, rcost=None):
    card = dict(CARD_DEFAULTS)
    card.update({
        "id": sid, "name": name, "card_type": "relic", "cost": cost,
        "speed": "", "rarity": "rare", "rules_text": text,
        "culture_slug": sid.split("-r")[0] if "-r" in sid else sid.rsplit("-", 1)[0],
        "keywords": [], "attack": 0, "health": 0,
        "abilities": [ab(f"{sid}-ab0", name, trigger, target, effects, cost=rcost)],
    })
    return card


def upgrade_figures(pack):
    figs = [c for c in pack["cards"] if c["card_type"] == "figure"]
    for i, f in enumerate(figs):
        cost = f.get("cost", 3)
        kw = f.get("keywords", [])
        if kw and f.get("rules_text", ""):
            continue
        fid = f["id"]
        ab_draw = ab(f"{fid}-ab0", "Draw", "on_play", "none", [eff("draw_cards", 1)])
        ab_buff = ab(f"{fid}-ab0", "Buff", "on_play", "friendly_figure", [eff("buff", attack=1, health=1)])
        ab_dmg2 = ab(f"{fid}-ab0", "Damage", "on_play", "enemy_figure", [eff("deal_damage", 2)])
        ab_aoe = ab(f"{fid}-ab0", "AoE", "on_play", "all_enemy_figures",
                    [eff("deal_damage", 2, scope="all_enemy_figures")])

        if cost >= 6:
            f["rules_text"] = "On play: Deal 2 damage to all enemy Figures. Draw a card."
            f["abilities"] = [ab_aoe, ab(f"{fid}-ab1", "Draw", "on_play", "none", [eff("draw_cards", 1)])]
        elif cost == 5 and i % 3 == 0:
            f["keywords"] = ["rush", "overwhelm"]; f["rules_text"] = "Rush. Overwhelm."
        elif cost == 5 and i % 3 == 1:
            f["keywords"] = ["guard", "reborn"]; f["rules_text"] = "Guard. Reborn."
        elif cost == 5:
            f["rules_text"] = "On play: Deal 2 damage to an enemy Figure. Draw a card."
            f["abilities"] = [ab_dmg2, ab(f"{fid}-ab1", "Draw", "on_play", "none", [eff("draw_cards", 1)])]
        elif cost == 4 and i % 3 == 0:
            f["keywords"] = ["rush"]; f["rules_text"] = "Rush. On play: Draw a card."
            f["abilities"] = [ab_draw]
        elif cost == 4 and i % 3 == 1:
            f["keywords"] = ["guard"]; f["rules_text"] = "Guard. On play: Give a friendly Figure +1/+1."
            f["abilities"] = [ab_buff]
        elif cost == 4:
            f["keywords"] = ["poisonous"]; f["rules_text"] = "Poisonous."
        elif cost == 3 and i % 2 == 0:
            f["rules_text"] = "On play: Draw a card."; f["abilities"] = [ab_draw]
        elif cost == 3:
            f["keywords"] = ["guard"]; f["rules_text"] = "Guard."
        elif cost <= 2 and i % 3 == 0:
            f["rules_text"] = "On play: Draw a card."; f["abilities"] = [ab_draw]
        elif cost <= 2 and i % 3 == 1:
            f["keywords"] = ["stealth"]; f["rules_text"] = "Stealth."
        elif cost <= 2:
            f["keywords"] = ["rush"]; f["rules_text"] = "Rush."


def build_deck(slug, pack):
    hero = next((c for c in pack["cards"] if c["card_type"] == "hero"), None)
    figures = [c for c in pack["cards"] if c["card_type"] == "figure"]
    spells = [c for c in pack["cards"] if c["card_type"] == "spell"]
    relics = [c for c in pack["cards"] if c["card_type"] == "relic"]
    by_cost = {}
    for f in figures:
        by_cost.setdefault(f.get("cost", 3), []).append(f)

    picked, picked_ids = [], set()
    for f in sorted([f for f in figures if "guard" in f.get("keywords", [])], key=lambda x: x.get("cost", 99)):
        if len([p for p in picked if "guard" in p.get("keywords", [])]) >= 2:
            break
        if f["id"] not in picked_ids:
            picked.append(f); picked_ids.add(f["id"])
    for f in sorted([f for f in figures if any(k in f.get("keywords", []) for k in ("rush", "charge"))],
                    key=lambda x: x.get("cost", 99)):
        if len([p for p in picked if any(k in p.get("keywords", []) for k in ("rush", "charge"))]) >= 2:
            break
        if f["id"] not in picked_ids:
            picked.append(f); picked_ids.add(f["id"])

    target = {2: 2, 3: 2, 4: 3, 5: 2, 6: 1}
    for cost in sorted(target):
        avail = [f for f in by_cost.get(cost, []) if f["id"] not in picked_ids]
        need = target[cost] - len([p for p in picked if p.get("cost") == cost])
        for f in avail[:max(0, need)]:
            picked.append(f); picked_ids.add(f["id"])

    remain = sorted([f for f in figures if f["id"] not in picked_ids], key=lambda x: x.get("cost", 99))
    while len(picked) < 14 and remain:
        picked.append(remain.pop(0))

    deck_cards = [{"id": f["id"], "count": 1} for f in picked[:14]]
    spell_ids = set()
    for s in spells:
        if s["id"] not in spell_ids and len(spell_ids) < 8:
            deck_cards.append({"id": s["id"], "count": 1})
            spell_ids.add(s["id"])
    for r in relics[:2]:
        deck_cards.append({"id": r["id"], "count": 1})

    deck = {"name": f"{slug} deck", "hero_id": hero["id"] if hero else "", "cards": deck_cards}
    dp = sorted(DECKS.glob(f"{slug}-*.json"))
    if dp:
        dp[0].write_text(json.dumps(deck, indent=2, ensure_ascii=False), encoding="utf-8")
    return sum(e["count"] for e in deck_cards)


def gen_names(slug):
    """Generate thematic spell/relic names from culture slug."""
    parts = slug.replace("-", " ").split()
    base = parts[0].title()
    return (
        f"{base} Strike", f"{base} Ward", f"{base} Cry", f"{base} Draw",
        f"{base} Wrath", f"{base} Sight", f"{base} Choice",
        f"{base} Totem", f"{base} Shrine",
    )


def upgrade_culture(slug):
    pack = json.loads((DATA / f"{slug}-v1.json").read_text(encoding="utf-8"))
    pack["cards"] = [c for c in pack["cards"] if c["card_type"] not in ("spell", "relic")]
    upgrade_figures(pack)

    s1, s2, s3, s4, s5, s6, s7, r1, r2 = gen_names(slug)
    s = slug

    pack["cards"] += [
        make_spell(f"{s}-s1", s1, 3, "fast", "Deal 3 damage to an enemy character.",
                   "enemy_character", [eff("deal_damage", 3)]),
        make_spell(f"{s}-s1b", s1, 3, "fast", "Deal 3 damage to an enemy character.",
                   "enemy_character", [eff("deal_damage", 3)]),
        make_spell(f"{s}-s2", s2, 2, "fast", "Give a friendly Figure +0/+3 and Ward.",
                   "friendly_figure", [eff("buff", attack=0, health=3), eff("grant_keyword", keyword="divine_shield")]),
        make_spell(f"{s}-s3", s3, 2, "burst", "Give a friendly Figure +2 Attack this turn.",
                   "friendly_figure", [eff("buff_temp", attack=2)]),
        make_spell(f"{s}-s4", s4, 2, "burst", "Draw 2 cards.", "none", [eff("draw_cards", 2)]),
        make_spell(f"{s}-s5", s5, 5, "slow", "Deal 2 damage to all enemy Figures.",
                   "none", [eff("deal_damage_all_enemies", 2, scope="all_enemy_figures")]),
        make_spell(f"{s}-s6", s6, 1, "burst", "Draw a card.", "none", [eff("draw_cards", 1)]),
        make_spell(f"{s}-s7", s7, 3, "fast", "Choose: Deal 4 damage to an enemy Figure OR Heal your Hero for 4.",
                   "enemy_figure", [eff("deal_damage", 4)]),
        make_relic(f"{s}-r1", r1, 3, "Activated (2 mana): Deal 2 damage to the enemy Hero.",
                   "manual", "none", [eff("deal_damage_hero", 2)], rcost=2),
        make_relic(f"{s}-r2", r2, 2, "After you cast a spell, draw a card.",
                   "on_spell_cast", "none", [eff("draw_cards", 1)]),
    ]

    (DATA / f"{slug}-v1.json").write_text(
        json.dumps(pack, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    total = build_deck(slug, pack)
    return total


if __name__ == "__main__":
    print(f"Upgrading {len(REMAINING)} remaining cultures...")
    ok = 0
    fail = 0
    for slug in REMAINING:
        try:
            total = upgrade_culture(slug)
            print(f"  {slug}: {total} cards")
            ok += 1
        except Exception as e:
            print(f"  {slug}: UPGRADE FAIL - {type(e).__name__}: {str(e)[:80]}")
            fail += 1

    print(f"\nUpgraded: {ok}, Failed: {fail}")

    # Verify with bot games
    print("\nVerifying with bot mirror games...")
    from game.engine import create_v1_game, legal_actions, apply_action_interactive, current_priority_player
    from game.players import RolloutPlayer

    pass_count = 0
    fail_count = 0
    for slug in REMAINING:
        pp = f"data/cards-v1/{slug}-v1.json"
        dps = sorted(DECKS.glob(f"{slug}-*.json"))
        if not dps:
            print(f"  {slug}: NO DECK")
            fail_count += 1
            continue
        dp = str(dps[0])
        try:
            state = create_v1_game(pp, dp, pp, dp, seed=42)
            bots = [RolloutPlayer(), RolloutPlayer()]
            for _ in range(200):
                if state.winner is not None:
                    break
                p = current_priority_player(state)
                acts = legal_actions(state, p)
                if not acts:
                    break
                c = bots[p].choose_action(state, p, acts)
                apply_action_interactive(state, c, p)
            whp = state.players[state.winner].health if state.winner is not None else 0
            pass_count += 1
        except Exception as e:
            print(f"  {slug}: GAME FAIL - {type(e).__name__}: {str(e)[:80]}")
            fail_count += 1

    print(f"\nBot verification: {pass_count} pass, {fail_count} fail")
    print(f"Total cultures done: {len(DONE) + ok}")
