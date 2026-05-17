"""
Automated tests for the Mythic Clash engine.

Covers: turn flow, combat, deathrattles, reborn, taunt targeting,
hero powers, fatigue, keywords, relics, and overtime.
"""

import pytest

from game.engine import (
    CardTemplate,
    GameState,
    MinionState,
    PlayerState,
    apply_action,
    attack_with_minion,
    check_winner,
    create_game,
    deal_damage_to_hero,
    deal_damage_to_minion,
    destroy_relic,
    draw_card,
    end_turn,
    find_minion,
    game_state_view,
    heal_hero,
    heal_minion,
    legal_actions,
    play_card,
    play_relic,
    remove_minion,
    start_turn,
    summon_minion,
    use_hero_power,
    validate_deck,
)
from game.rules import HERO_HEALTH, MAX_BOARD_SIZE, MAX_MANA, MAX_TURNS


def make_minion(name="Test Minion", cost=2, attack=2, health=3, keywords=None, culture="test", rarity="common", **extra_fields):
    kw = keywords or []
    return CardTemplate(
        id=f"test-{name.lower().replace(' ', '-')}",
        name=name,
        culture_slug=culture,
        source="test",
        card_type="minion",
        cost=cost,
        rarity=rarity,
        alignment="neutral",
        text="",
        attack=attack,
        health=health,
        keywords=list(kw),
        **extra_fields,
    )


def make_spell(name="Test Spell", cost=2, spell_kind="damage", value=3):
    return CardTemplate(
        id=f"test-{name.lower().replace(' ', '-')}",
        name=name,
        culture_slug="test",
        source="test",
        card_type="spell",
        cost=cost,
        rarity="common",
        alignment="neutral",
        text="",
        spell_kind=spell_kind,
        value=value,
    )


def make_relic(name="Test Relic", cost=3, abilities=None):
    return CardTemplate(
        id=f"test-{name.lower().replace(' ', '-')}",
        name=name,
        culture_slug="test",
        source="test",
        card_type="relic",
        cost=cost,
        rarity="rare",
        alignment="neutral",
        text="",
        extra={"abilities": abilities or []},
    )


def make_game(deck_a=None, deck_b=None, seed=1):
    if deck_a is None:
        deck_a = [make_minion(f"A{i}", cost=i % 5 + 1) for i in range(18)]
    if deck_b is None:
        deck_b = [make_minion(f"B{i}", cost=i % 5 + 1) for i in range(18)]
    return create_game(deck_a, deck_b, seed=seed)


# --- Turn Flow ---

class TestTurnFlow:
    def test_first_player_starts_turn_1(self):
        state = make_game()
        assert state.turn_number == 1
        assert state.active_player == 0

    def test_mana_increments_each_turn(self):
        state = make_game()
        assert state.players[0].mana == 1
        assert state.players[0].max_mana == 1
        apply_action(state, {"type": "pass"})
        assert state.players[1].mana == 1
        apply_action(state, {"type": "pass"})
        assert state.players[0].mana == 2
        assert state.players[0].max_mana == 2

    def test_mana_caps_at_max(self):
        state = make_game()
        state.players[0].max_mana = MAX_MANA - 1
        state.players[0].mana = 0
        apply_action(state, {"type": "pass"})
        apply_action(state, {"type": "pass"})
        assert state.players[0].max_mana == MAX_MANA
        assert state.players[0].mana == MAX_MANA

    def test_draw_on_turn_start(self):
        state = make_game()
        hand_before = len(state.players[1].hand)
        apply_action(state, {"type": "pass"})
        assert len(state.players[1].hand) == hand_before + 1

    def test_second_player_gets_coin(self):
        state = make_game()
        coins = [c for c in state.players[1].hand if c.spell_kind == "coin"]
        assert len(coins) == 1


# --- Combat ---

class TestCombat:
    def test_minion_attacks_minion(self):
        state = make_game()
        attacker_card = make_minion("Attacker", attack=3, health=4)
        defender_card = make_minion("Defender", attack=2, health=5)
        attacker = summon_minion(state, 0, attacker_card)
        defender = summon_minion(state, 1, defender_card)
        attacker.sleeping = False
        attack_with_minion(state, attacker.unit_id, defender.unit_id)
        assert attacker.damage_taken == 2
        assert defender.damage_taken == 3

    def test_minion_kills_minion(self):
        state = make_game()
        attacker_card = make_minion("Attacker", attack=5, health=4)
        defender_card = make_minion("Defender", attack=2, health=3)
        attacker = summon_minion(state, 0, attacker_card)
        defender = summon_minion(state, 1, defender_card)
        attacker.sleeping = False
        attack_with_minion(state, attacker.unit_id, defender.unit_id)
        assert defender not in state.players[1].board
        assert attacker.damage_taken == 2

    def test_attack_hero(self):
        state = make_game()
        card = make_minion("Attacker", attack=4, health=3)
        attacker = summon_minion(state, 0, card)
        attacker.sleeping = False
        attack_with_minion(state, attacker.unit_id, "hero")
        assert state.players[1].health == HERO_HEALTH - 4

    def test_mutual_kill(self):
        state = make_game()
        a_card = make_minion("A", attack=3, health=3)
        b_card = make_minion("B", attack=3, health=3)
        a = summon_minion(state, 0, a_card)
        b = summon_minion(state, 1, b_card)
        a.sleeping = False
        attack_with_minion(state, a.unit_id, b.unit_id)
        assert a not in state.players[0].board
        assert b not in state.players[1].board


# --- Keywords ---

class TestKeywords:
    def test_taunt_forces_targeting(self):
        state = make_game()
        taunt_card = make_minion("Taunter", attack=1, health=5, keywords=["taunt"])
        normal_card = make_minion("Normal", attack=3, health=3)
        summon_minion(state, 1, taunt_card)
        summon_minion(state, 1, normal_card)
        attacker_card = make_minion("Attacker", attack=2, health=2)
        attacker = summon_minion(state, 0, attacker_card)
        attacker.sleeping = False
        actions = legal_actions(state)
        attack_actions = [a for a in actions if a["type"] == "attack" and a.get("unit_id") == attacker.unit_id]
        target_ids = {a.get("target_unit_id") for a in attack_actions if a.get("target_unit_id")}
        taunter = [m for m in state.players[1].board if m.card.name == "Taunter"][0]
        assert taunter.unit_id in target_ids
        assert all(a.get("target") != "hero" for a in attack_actions)

    def test_divine_shield_absorbs_first_hit(self):
        state = make_game()
        shielded_card = make_minion("Shielded", attack=2, health=3, keywords=["divine_shield"])
        attacker_card = make_minion("Attacker", attack=4, health=4)
        shielded = summon_minion(state, 1, shielded_card)
        attacker = summon_minion(state, 0, attacker_card)
        attacker.sleeping = False
        attack_with_minion(state, attacker.unit_id, shielded.unit_id)
        assert shielded.damage_taken == 0
        assert not shielded.divine_shield
        assert attacker.damage_taken == 2

    def test_charge_can_attack_immediately(self):
        state = make_game()
        charge_card = make_minion("Charger", attack=3, health=2, keywords=["charge"])
        # play_card sets sleeping based on keywords; summon_minion uses the sleeping param
        minion = summon_minion(state, 0, charge_card, sleeping=False)
        assert not minion.sleeping
        assert minion.can_attack()

    def test_rush_can_attack_minions_not_hero(self):
        state = make_game()
        rush_card = make_minion("Rusher", attack=3, health=2, keywords=["rush"])
        minion = summon_minion(state, 0, rush_card, sleeping=False)
        assert not minion.sleeping
        target_card = make_minion("Target", attack=1, health=1)
        summon_minion(state, 1, target_card)
        actions = legal_actions(state)
        rush_attacks = [a for a in actions if a["type"] == "attack" and a.get("unit_id") == minion.unit_id]
        has_hero_target = any(a.get("target") == "hero" for a in rush_attacks)
        has_minion_target = any(a.get("target_unit_id") for a in rush_attacks)
        assert has_minion_target
        assert not has_hero_target

    def test_lifesteal_heals_hero(self):
        state = make_game()
        state.players[0].health = 20
        ls_card = make_minion("Lifestealer", attack=4, health=3, keywords=["lifesteal"])
        attacker = summon_minion(state, 0, ls_card)
        attacker.sleeping = False
        attack_with_minion(state, attacker.unit_id, "hero")
        assert state.players[0].health == 24

    def test_poisonous_kills_regardless_of_health(self):
        state = make_game()
        poison_card = make_minion("Poison", attack=1, health=1, keywords=["poisonous"])
        big_card = make_minion("Big", attack=1, health=20)
        poison = summon_minion(state, 0, poison_card)
        big = summon_minion(state, 1, big_card)
        poison.sleeping = False
        attack_with_minion(state, poison.unit_id, big.unit_id)
        assert big not in state.players[1].board

    def test_reborn_returns_with_1_health(self):
        state = make_game()
        reborn_card = make_minion("Reborner", attack=2, health=4, keywords=["reborn"])
        killer_card = make_minion("Killer", attack=10, health=10)
        reborn = summon_minion(state, 0, reborn_card)
        killer = summon_minion(state, 1, killer_card)
        reborn.sleeping = False
        attack_with_minion(state, reborn.unit_id, killer.unit_id)
        reborns = [m for m in state.players[0].board if m.card.name == "Reborner"]
        assert len(reborns) == 1
        assert reborns[0].current_health == 1
        assert not reborns[0].reborn_available


# --- Deathrattle ---

class TestDeathrattle:
    def test_deathrattle_damage(self):
        state = make_game()
        dr_card = make_minion("Deathdealer", attack=1, health=1, deathrattle="damage_enemy")
        dr_card.value = 3
        killer_card = make_minion("Killer", attack=5, health=5)
        dr = summon_minion(state, 0, dr_card)
        killer = summon_minion(state, 1, killer_card)
        dr.sleeping = False
        health_before = state.players[1].health
        attack_with_minion(state, dr.unit_id, killer.unit_id)
        assert dr not in state.players[0].board
        assert state.players[1].health < health_before or killer.damage_taken > 1

    def test_deathrattle_summon(self):
        state = make_game()
        dr_card = make_minion("Summoner", attack=1, health=1, deathrattle="summon_token")
        dr_card.value = 2
        killer_card = make_minion("Killer", attack=5, health=5)
        dr = summon_minion(state, 0, dr_card)
        killer = summon_minion(state, 1, killer_card)
        dr.sleeping = False
        board_before = len(state.players[0].board)
        attack_with_minion(state, dr.unit_id, killer.unit_id)
        assert len(state.players[0].board) >= board_before


# --- Hero Powers ---

class TestHeroPower:
    def test_ping_hero_power(self):
        state = make_game()
        state.players[0].hero_power_kind = "ping"
        state.players[0].hero_power_name = "War Spark"
        state.players[0].mana = 2
        use_hero_power(state, "hero")
        assert state.players[1].health == HERO_HEALTH - 1
        assert state.players[0].hero_power_used

    def test_heal_hero_power(self):
        state = make_game()
        state.players[0].hero_power_kind = "heal"
        state.players[0].hero_power_name = "Living Water"
        state.players[0].health = 25
        state.players[0].mana = 2
        use_hero_power(state)
        assert state.players[0].health == 27

    def test_armor_hero_power(self):
        state = make_game()
        state.players[0].hero_power_kind = "armor"
        state.players[0].hero_power_name = "Stone Resolve"
        state.players[0].mana = 2
        use_hero_power(state)
        assert state.players[0].armor == 2

    def test_bless_hero_power(self):
        state = make_game()
        card = make_minion("Target", attack=2, health=3)
        minion = summon_minion(state, 0, card)
        state.players[0].hero_power_kind = "bless"
        state.players[0].hero_power_name = "Sacred Blessing"
        state.players[0].mana = 2
        use_hero_power(state, minion.unit_id)
        assert minion.current_attack == 3
        assert minion.current_health == 4

    def test_hero_power_once_per_turn(self):
        state = make_game()
        state.players[0].hero_power_kind = "armor"
        state.players[0].hero_power_name = "Stone Resolve"
        state.players[0].mana = 4
        use_hero_power(state)
        assert state.players[0].hero_power_used
        actions = legal_actions(state)
        hp_actions = [a for a in actions if a["type"] == "hero_power"]
        assert len(hp_actions) == 0


# --- Fatigue ---

class TestFatigue:
    def test_empty_deck_fatigue(self):
        state = make_game()
        state.players[0].deck = []
        state.players[0].fatigue = 1
        health_before = state.players[0].health
        draw_card(state, 0)
        assert state.players[0].health == health_before - 1
        assert state.players[0].fatigue == 2

    def test_fatigue_escalates(self):
        state = make_game()
        state.players[0].deck = []
        state.players[0].fatigue = 3
        health_before = state.players[0].health
        draw_card(state, 0)
        assert state.players[0].health == health_before - 3
        assert state.players[0].fatigue == 4

    def test_fatigue_can_kill(self):
        state = make_game()
        state.players[0].deck = []
        state.players[0].health = 1
        state.players[0].fatigue = 5
        draw_card(state, 0)
        assert state.players[0].health <= 0
        assert state.winner == 1

    def test_overtime_fatigue_past_max_turns(self):
        state = make_game()
        state.turn_number = MAX_TURNS
        state.players[0].health = 30
        state.players[1].health = 30
        # P0 passes, ending their turn. P1's turn starts.
        state.active_player = 0
        apply_action(state, {"type": "pass"})
        # P1 passes, ending their turn. Turn increments past MAX_TURNS.
        apply_action(state, {"type": "pass"})
        assert state.turn_number > MAX_TURNS
        assert state.players[0].health < 30 or state.players[1].health < 30


# --- Relics ---

class TestRelics:
    def test_play_relic(self):
        state = make_game()
        relic = make_relic("Holy Relic", cost=1)
        state.players[0].hand.append(relic)
        state.players[0].mana = 3
        hand_idx = len(state.players[0].hand) - 1
        play_relic(state, hand_idx)
        assert len(state.players[0].relics) == 1
        assert state.players[0].relics[0].name == "Holy Relic"

    def test_max_two_relics(self):
        state = make_game()
        state.players[0].relics = [make_relic("R1"), make_relic("R2")]
        relic3 = make_relic("R3", cost=1)
        state.players[0].hand.append(relic3)
        state.players[0].mana = 5
        actions = legal_actions(state)
        relic_actions = [a for a in actions if a["type"] == "play_relic"]
        assert len(relic_actions) == 0

    def test_destroy_relic(self):
        state = make_game()
        relic = make_relic("Fragile Relic")
        state.players[0].relics.append(relic)
        destroy_relic(state, 0, relic)
        assert len(state.players[0].relics) == 0
        assert relic in state.players[0].discard


# --- Board Limits ---

class TestBoardLimits:
    def test_board_cap(self):
        state = make_game()
        for i in range(MAX_BOARD_SIZE):
            summon_minion(state, 0, make_minion(f"M{i}"))
        result = summon_minion(state, 0, make_minion("Extra"))
        assert result is None
        assert len(state.players[0].board) == MAX_BOARD_SIZE


# --- Healing ---

class TestHealing:
    def test_heal_hero_caps_at_max(self):
        state = make_game()
        state.players[0].health = 28
        healed = heal_hero(state.players[0], 10)
        assert state.players[0].health == HERO_HEALTH
        assert healed == 2

    def test_heal_minion(self):
        state = make_game()
        card = make_minion("Wounded", attack=2, health=5)
        minion = summon_minion(state, 0, card)
        minion.damage_taken = 3
        healed = heal_minion(minion, 2)
        assert minion.damage_taken == 1
        assert healed == 2


# --- Win Conditions ---

class TestWinConditions:
    def test_hero_death_wins_opponent(self):
        state = make_game()
        state.players[0].health = 0
        check_winner(state)
        assert state.winner == 1

    def test_both_die_active_player_loses(self):
        state = make_game()
        state.active_player = 0
        state.players[0].health = 0
        state.players[1].health = 0
        check_winner(state)
        assert state.winner == 0

    def test_armor_absorbs_damage(self):
        state = make_game()
        state.players[0].armor = 5
        dealt = deal_damage_to_hero(state, 0, 3)
        assert state.players[0].armor == 2
        assert state.players[0].health == HERO_HEALTH
        assert dealt == 3


# --- Game State View ---

class TestGameStateView:
    def test_view_has_hero(self):
        state = make_game()
        view = game_state_view(state, 0)
        assert view["you"]["hero"] is not None
        assert "name" in view["you"]["hero"]

    def test_view_hides_opponent_hand(self):
        state = make_game()
        view = game_state_view(state, 0)
        assert "hand" not in view["opponent"]
        assert "hand_count" in view["opponent"]

    def test_view_includes_graveyard(self):
        state = make_game()
        state.players[0].discard.append(make_minion("Dead Guy", cost=3))
        view = game_state_view(state, 0)
        assert len(view["you"]["graveyard"]) == 1
        assert view["you"]["graveyard"][0]["name"] == "Dead Guy"


# --- Deck Validation ---

class TestDeckValidation:
    def test_legal_deck_passes(self):
        deck = [make_minion(f"Fig{i}", cost=i % 5 + 1) for i in range(18)]
        deck += [make_spell(f"Spell{i}") for i in range(4)]
        deck += [make_relic(f"Relic{i}") for i in range(2)]
        errors = validate_deck(deck)
        assert errors == []

    def test_too_few_figures(self):
        deck = [make_minion(f"Fig{i}") for i in range(10)]
        deck += [make_spell(f"Spell{i}") for i in range(14)]
        errors = validate_deck(deck)
        assert any("Figures" in e for e in errors)

    def test_too_many_spells(self):
        deck = [make_minion(f"Fig{i}") for i in range(14)]
        deck += [make_spell(f"Spell{i}") for i in range(10)]
        errors = validate_deck(deck)
        assert any("Spells" in e for e in errors)

    def test_too_many_copies(self):
        same = make_minion("Duplicate", cost=2)
        deck = [same] * 3 + [make_minion(f"Fig{i}") for i in range(21)]
        errors = validate_deck(deck)
        assert any("Duplicate" in e for e in errors)

    def test_legendary_copy_limit(self):
        legend = make_minion("Legend", cost=5, rarity="legendary")
        deck = [legend] * 2 + [make_minion(f"Fig{i}") for i in range(22)]
        errors = validate_deck(deck)
        assert any("Legend" in e for e in errors)

    def test_wrong_size(self):
        deck = [make_minion(f"Fig{i}") for i in range(20)]
        errors = validate_deck(deck)
        assert any("20 cards" in e for e in errors)
