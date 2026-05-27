"""
Player controllers for Mythic Clash self-play.
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from typing import Any

from .engine import GameState, MinionState, PlayerState, apply_action, apply_action_interactive, game_state_view, legal_actions
from .rules import RULES_TEXT


class BasePlayer:
    def choose_action(self, state: GameState, player_index: int, legal_actions: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError


class ScoredPlayer(BasePlayer):
    def __init__(self, *, pass_penalty: float = 3.0) -> None:
        self.pass_penalty = pass_penalty

    def choose_action(self, state: GameState, player_index: int, legal_actions: list[dict[str, Any]]) -> dict[str, Any]:
        if len(legal_actions) == 1:
            return legal_actions[0]

        scored_actions: list[tuple[float, tuple[int, int, int], dict[str, Any]]] = []
        for action in legal_actions:
            score = self.score_action(state, player_index, legal_actions, action)
            tie_break = self.action_tie_break(state, player_index, action)
            scored_actions.append((score, tie_break, action))

        scored_actions.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return scored_actions[0][2]

    def score_action(
        self,
        state: GameState,
        player_index: int,
        legal_actions_now: list[dict[str, Any]],
        action: dict[str, Any],
    ) -> float:
        before_score = self.evaluate_state(state, player_index)
        before_player = state.players[player_index]
        before_enemy = state.players[1 - player_index]
        simulated = deepcopy(state)
        simulated_before_player = simulated.players[player_index]
        mana_before = simulated_before_player.mana + simulated_before_player.ritual_mana
        if simulated.phase.startswith("response"):
            apply_action_interactive(simulated, dict(action), player_index)
        else:
            apply_action(simulated, dict(action))

        if simulated.winner == player_index:
            return 1_000_000.0
        if simulated.winner is not None and simulated.winner != player_index:
            return -1_000_000.0

        after_score = self.evaluate_state(simulated, player_index)
        score = after_score
        after_player = simulated.players[player_index]
        after_enemy = simulated.players[1 - player_index]
        mana_after = after_player.mana + after_player.ritual_mana
        spent_mana = max(0, mana_before - mana_after)
        state_delta = after_score - before_score
        score += spent_mana * 0.4

        cards_spent = max(0, len(before_player.hand) - len(after_player.hand))
        own_board_delta = len(after_player.board) - len(before_player.board)
        enemy_board_delta = len(before_enemy.board) - len(after_enemy.board)
        own_life_delta = (after_player.health + after_player.armor) - (before_player.health + before_player.armor)
        enemy_life_delta = (before_enemy.health + before_enemy.armor) - (after_enemy.health + after_enemy.armor)
        relic_delta = len(after_player.relics) - len(before_player.relics)
        if (
            cards_spent > 0
            and own_board_delta <= 0
            and enemy_board_delta <= 0
            and own_life_delta <= 0
            and enemy_life_delta <= 0
            and relic_delta <= 0
            and state_delta < 0.5
        ):
            score -= 6.0 * cards_spent

        if action["type"] == "pass" and any(candidate["type"] != "pass" for candidate in legal_actions_now):
            score -= self.pass_penalty
        elif simulated.active_player == player_index and simulated.winner is None:
            followups = legal_actions(simulated, player_index)
            non_pass_followups = [candidate for candidate in followups if candidate["type"] != "pass"]
            score += min(len(non_pass_followups), 6) * 0.1
            if non_pass_followups:
                best_followup_gain = max(self.estimate_followup_gain(simulated, player_index, candidate) for candidate in non_pass_followups)
                score += max(0.0, min(best_followup_gain, 12.0)) * 0.35
                if cards_spent > 0 and own_board_delta <= 0 and enemy_board_delta <= 0 and own_life_delta <= 0 and enemy_life_delta <= 0 and relic_delta <= 0 and best_followup_gain <= 0.5:
                    score -= 2.5

        return score

    def estimate_followup_gain(self, state: GameState, player_index: int, action: dict[str, Any]) -> float:
        simulated = deepcopy(state)
        before_score = self.evaluate_state(state, player_index)
        if simulated.phase.startswith("response"):
            apply_action_interactive(simulated, dict(action), player_index)
        else:
            apply_action(simulated, dict(action))
        if simulated.winner == player_index:
            return 100.0
        if simulated.winner is not None and simulated.winner != player_index:
            return -100.0
        return self.evaluate_state(simulated, player_index) - before_score

    def evaluate_state(self, state: GameState, player_index: int) -> float:
        from .rules import SURVIVAL_INSTINCT_THRESHOLD, LAST_STAND_THRESHOLD
        you = state.players[player_index]
        opponent = state.players[1 - player_index]

        if you.health <= 0:
            return -100_000.0
        if opponent.health <= 0:
            return 100_000.0

        score = 0.0
        # Health matters more when low (survival instinct awareness)
        if you.health <= LAST_STAND_THRESHOLD:
            score += you.health * 2.5  # desperate: every HP is critical
        elif you.health <= SURVIVAL_INSTINCT_THRESHOLD:
            score += you.health * 1.4
        else:
            score += you.health * 0.8
        score += you.armor * 0.5

        # Opponent health: penalize pushing them below SI threshold (they get extra draws)
        if opponent.health > SURVIVAL_INSTINCT_THRESHOLD:
            score -= opponent.health * 0.95
        elif opponent.health > LAST_STAND_THRESHOLD:
            score -= opponent.health * 0.8  # they already have SI, less marginal value
        else:
            score -= opponent.health * 1.3  # they're in last stand, finish them fast
        score -= opponent.armor * 0.35

        score += self.evaluate_player_board(you)
        score -= self.evaluate_player_board(opponent)
        score += (len(you.hand) - len(opponent.hand)) * 0.42
        score += (len(you.relics) - len(opponent.relics)) * 0.65
        score -= you.fatigue * 0.12
        score += opponent.fatigue * 0.12

        # Board attack totals and racing awareness
        own_attack = sum(max(0, m.current_attack) for m in you.board if m.can_attack())
        own_total_attack = sum(max(0, m.current_attack) for m in you.board)
        enemy_attack = sum(max(0, m.current_attack) for m in opponent.board)
        enemy_taunts = [m for m in opponent.board if m.taunt]
        taunt_hp = sum(m.current_health for m in enemy_taunts)

        score += own_total_attack * 0.22
        score -= enemy_attack * 0.34

        # Lethal awareness
        if own_attack >= opponent.effective_life:
            score += 18.0
        elif own_total_attack >= opponent.effective_life and taunt_hp == 0:
            score += 12.0  # lethal next turn if no new taunts
        if enemy_attack >= you.effective_life:
            score -= 24.0

        # Racing: if we're ahead on clock, value face damage more
        own_clock = (opponent.effective_life / max(1, own_total_attack)) if own_total_attack > 0 else 99
        enemy_clock = (you.effective_life / max(1, enemy_attack)) if enemy_attack > 0 else 99
        if own_clock < enemy_clock:
            score += 3.0  # we kill them first — aggressor bonus

        # Frozen/disabled figures are weaker
        frozen_own = sum(1 for m in you.board if m.skip_ready_once or m.cant_attack_turns > 0)
        frozen_enemy = sum(1 for m in opponent.board if m.skip_ready_once or m.cant_attack_turns > 0)
        score -= frozen_own * 2.0
        score += frozen_enemy * 2.0

        # Opponent's open mana = potential tricks (caution)
        opp_mana = opponent.mana + opponent.ritual_mana
        if opp_mana >= 2 and len(opponent.hand) > 0:
            score -= 0.5  # slight penalty for opponent having response options

        return score

    def evaluate_player_board(self, player: PlayerState) -> float:
        return sum(self.evaluate_minion(minion) for minion in player.board)

    def evaluate_minion(self, minion: MinionState) -> float:
        score = minion.current_attack * 1.45 + minion.current_health * 1.1
        keywords = minion.runtime_keywords
        if "guard" in keywords or "taunt" in keywords:
            score += 1.7 + minion.current_health * 0.12
        if "divine_shield" in keywords or "ward" in keywords:
            score += 2.2
        if "reborn" in keywords and minion.reborn_available:
            score += 2.0
        if "lifesteal" in keywords:
            score += 1.1 + minion.current_attack * 0.3
        if "poisonous" in keywords:
            score += 2.3
        if "stealth" in keywords:
            score += 0.9
        if "overwhelm" in keywords:
            score += 1.5 + minion.current_attack * 0.2
        if "charge" in keywords:
            score += 1.0
        if minion.skip_ready_once or minion.cant_attack_turns > 0:
            score -= 2.5  # frozen/disabled figures can't attack next turn
        if minion.can_attack():
            score += 0.9 + minion.current_attack * 0.35
        if minion.sleeping and ("rush" in keywords or "charge" in keywords):
            score += 0.4
        return score

    def action_tie_break(self, state: GameState, player_index: int, action: dict[str, Any]) -> tuple[int, int, int]:
        type_priority = {
            "attack": 6,
            "play_spell": 5,
            "activate_relic": 5,
            "play": 4,
            "hero_power": 3,
            "play_relic": 2,
            "pass": 1,
        }
        hand_value = 0
        if "hand_index" in action:
            card = state.players[player_index].hand[action["hand_index"]]
            hand_value = card.cost
            if card.card_type == "minion":
                hand_value += card.attack + card.health
        # Prefer face attacks when racing (ahead on clock or opponent is low)
        target_bonus = 0
        if action.get("target") == "hero":
            opponent = state.players[1 - player_index]
            if opponent.health <= 15:
                target_bonus = 3  # push for lethal when opponent is low
            else:
                target_bonus = 1
        return (type_priority.get(action["type"], 0), hand_value, target_bonus)


class HeuristicPlayer(ScoredPlayer):
    pass


class RolloutPlayer(ScoredPlayer):
    def __init__(self) -> None:
        super().__init__(pass_penalty=2.0)

    def choose_action(self, state: GameState, player_index: int, legal_actions: list[dict[str, Any]]) -> dict[str, Any]:
        if len(legal_actions) == 1:
            return legal_actions[0]

        scored_actions: list[tuple[float, tuple[int, int, int], dict[str, Any]]] = []
        for action in legal_actions:
            scored_actions.append((self.immediate_score(state, player_index, legal_actions, action), self.action_tie_break(state, player_index, action), action))
        scored_actions.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return scored_actions[0][2]

    def immediate_score(
        self,
        state: GameState,
        player_index: int,
        legal_actions_now: list[dict[str, Any]],
        action: dict[str, Any],
    ) -> float:
        player = state.players[player_index]
        enemy = state.players[1 - player_index]
        score = 0.0
        in_response = state.phase.startswith("response")

        if action["type"] == "pass":
            if in_response:
                # During response, passing is often correct — low penalty
                return -0.2
            has_real_option = any(candidate["type"] != "pass" for candidate in legal_actions_now)
            return -self.pass_penalty if has_real_option else 0.0

        # During response windows, score spells based on combat impact
        if in_response and action["type"] == "play_spell" and state.pending_attack:
            return self.score_response_spell(state, player_index, action)

        if action["type"] == "attack":
            attacker = self.find_minion(state, action.get("unit_id"))
            if attacker is None:
                return -50.0
            if action.get("target") == "hero":
                if enemy.effective_life <= attacker.current_attack:
                    return 100_000.0
                pressure = attacker.current_attack * 2.0
                if self.board_ahead(player, enemy):
                    pressure += 1.5
                return pressure
            defender = self.find_minion(state, action.get("target_unit_id"))
            if defender is None:
                return -25.0
            return self.score_attack(attacker, defender)

        if action["type"] == "play":
            card = player.hand[action["hand_index"]]
            return self.score_hand_card_play(state, player_index, card)

        if action["type"] == "play_relic":
            card = player.hand[action["hand_index"]]
            return 2.2 + (card.cost * 0.25) + len(player.board) * 0.15 - len(player.relics) * 0.4

        if action["type"] == "play_spell":
            card = player.hand[action["hand_index"]]
            return self.score_manual_card_use(state, player_index, card, action)

        if action["type"] == "hero_power":
            return self.score_hero_power(state, player_index, action)

        if action["type"] == "activate_relic":
            relic = player.relics[action["relic_index"]] if action["relic_index"] < len(player.relics) else None
            if relic is None:
                return -10.0
            return self.score_manual_card_use(state, player_index, relic, action)

        return score

    def score_response_spell(self, state: GameState, player_index: int, action: dict[str, Any]) -> float:
        """Score a spell played during a response window based on combat impact."""
        pending = state.pending_attack
        if not pending:
            return 0.0

        player = state.players[player_index]
        card = player.hand[action["hand_index"]]
        attacker = self.find_minion(state, pending["attacker_id"])
        target_id = pending["target"]
        defender = self.find_minion(state, target_id) if target_id != "hero" else None
        am_defender = player_index != pending["owner"]

        score = 0.0
        # Evaluate based on ability effects
        for ability in card.extra.get("abilities", []):
            for effect in ability.get("effects", []):
                kind = effect.get("kind")
                amount = int(effect.get("amount") or 0)

                if kind == "grant_stats" and am_defender and defender:
                    atk_boost = int(effect.get("attack") or 0)
                    hp_boost = int(effect.get("health") or 0)
                    target_uid = action.get("target_unit_id")
                    if target_uid == defender.unit_id:
                        # Buffing our defender in combat
                        new_hp = defender.current_health + hp_boost
                        new_atk = defender.current_attack + atk_boost
                        survives_after = new_hp > (attacker.current_attack if attacker else 0)
                        would_die_without = defender.current_health <= (attacker.current_attack if attacker else 0)
                        if would_die_without and survives_after:
                            score += self.evaluate_minion(defender) * 1.5 + 3.0  # Saving a figure is huge
                        elif survives_after:
                            score += hp_boost * 0.5 + atk_boost * 0.8
                        else:
                            score -= 1.0  # Wasting a buff on a figure that still dies

                if kind == "deal_damage" and am_defender and attacker:
                    target_uid = action.get("target_unit_id")
                    if target_uid == attacker.unit_id:
                        if amount >= attacker.current_health:
                            score += self.evaluate_minion(attacker) * 1.2  # Killing the attacker
                        else:
                            score += amount * 0.5

                if kind == "heal" and am_defender and defender:
                    target_uid = action.get("target_unit_id")
                    if target_uid == defender.unit_id:
                        would_die = defender.current_health <= (attacker.current_attack if attacker else 0)
                        healed_hp = min(amount, defender.card.health - defender.current_health + defender.enchant_health)
                        survives_after = (defender.current_health + healed_hp) > (attacker.current_attack if attacker else 0)
                        if would_die and survives_after:
                            score += self.evaluate_minion(defender) * 1.2 + 2.0
                        elif not would_die:
                            score += healed_hp * 0.3

                if kind == "freeze" and not am_defender and attacker:
                    # Attacker freezing the defender — not useful in response
                    pass

                if kind == "draw_cards":
                    score += amount * 0.8  # Drawing during response is OK but not amazing

        # Burst spells that draw or heal are generally positive during response
        # (they resolve immediately with no counter-response opportunity)
        if score <= 0 and card.speed == "burst":
            # Burst utility during response is slightly positive — free value
            for ability in card.extra.get("abilities", []):
                for effect in ability.get("effects", []):
                    if effect.get("kind") == "draw_cards":
                        score = max(score, 0.6 * int(effect.get("amount") or 1))
                    elif effect.get("kind") == "heal":
                        amt = int(effect.get("amount") or 0)
                        if player.health < 20:
                            score = max(score, 0.3 * amt)
                    elif effect.get("kind") == "gain_armor":
                        score = max(score, 0.3 * int(effect.get("amount") or 0))

        # If no meaningful impact from a Fast spell, slightly negative (wasting a response opportunity)
        if score <= 0:
            score = -0.5 if card.speed == "fast" else -0.3
        return score

    def find_minion(self, state: GameState, unit_id: str | None) -> MinionState | None:
        if not unit_id:
            return None
        for player in state.players:
            for minion in player.board:
                if minion.unit_id == unit_id:
                    return minion
        return None

    def board_ahead(self, player: PlayerState, enemy: PlayerState) -> bool:
        own = sum(minion.current_attack + minion.current_health for minion in player.board)
        opp = sum(minion.current_attack + minion.current_health for minion in enemy.board)
        return own >= opp

    def score_attack(self, attacker: MinionState, defender: MinionState) -> float:
        attacker_value = self.evaluate_minion(attacker)
        defender_value = self.evaluate_minion(defender)
        score = 0.2
        kills_defender = "poisonous" in attacker.runtime_keywords or attacker.current_attack >= defender.current_health
        defender_kills = "poisonous" in defender.runtime_keywords or defender.current_attack >= attacker.current_health

        if kills_defender:
            score += defender_value * 0.85
        else:
            score += min(attacker.current_attack, defender.current_health) * 0.35

        if defender_kills:
            score -= attacker_value * 0.7
        else:
            score += 1.2
            if attacker.current_attack > 0:
                remaining_health = attacker.current_health - defender.current_attack
                score += max(0.0, remaining_health) * 0.08

        if "guard" in defender.runtime_keywords or "taunt" in defender.runtime_keywords:
            score += 0.6
        if attacker.current_attack >= defender.current_attack and not defender_kills:
            score += 0.4
        return score

    def score_hand_card_play(self, state: GameState, player_index: int, card: Any) -> float:
        player = state.players[player_index]
        enemy = state.players[1 - player_index]
        score = (card.cost or 0) * 0.25
        if getattr(card, "card_type", "") == "minion":
            score += (card.attack or 0) * 1.2 + (card.health or 0) * 0.95
            score += self.keyword_score(getattr(card, "keywords", []), attack=card.attack or 0, health=card.health or 0)
            if len(player.board) < len(enemy.board):
                score += 0.5
            for ability in getattr(card, "extra", {}).get("abilities", []):
                if ability.get("trigger") == "on_play":
                    score += self.score_ability_effects(state, player_index, ability, None)
            return score
        return score

    def score_manual_card_use(self, state: GameState, player_index: int, card: Any, action: dict[str, Any]) -> float:
        score = (card.cost or 0) * 0.15
        ability = None
        for candidate in getattr(card, "extra", {}).get("abilities", []):
            if candidate.get("trigger") == "manual":
                ability = candidate
                break
        if ability is None:
            return score
        return score + self.score_ability_effects(state, player_index, ability, action)

    def score_hero_power(self, state: GameState, player_index: int, action: dict[str, Any]) -> float:
        player = state.players[player_index]
        ability = getattr(player, "hero_power_data", None)
        if not ability:
            return 0.5
        return 0.4 + self.score_ability_effects(state, player_index, ability, action)

    def score_ability_effects(self, state: GameState, player_index: int, ability: dict[str, Any], action: dict[str, Any] | None) -> float:
        player = state.players[player_index]
        enemy = state.players[1 - player_index]
        target = self.find_minion(state, action.get("target_unit_id")) if action else None
        target_side = None
        if target is not None:
            target_side = "friendly" if target.owner == player_index else "enemy"
        if action and action.get("target") == "hero":
            target_side = "enemy_hero"
        if action and action.get("target") == "friendly_hero":
            target_side = "friendly_hero"

        score = 0.0
        for effect in ability.get("effects", []):
            kind = effect.get("kind")
            amount = int(effect.get("amount") or 0)
            extra = effect.get("extra", {})

            if kind == "deal_damage":
                if ability.get("target_rule") == "all_enemy_figures":
                    if not enemy.board:
                        score -= 3.0
                    for minion in enemy.board:
                        score += min(amount, minion.current_health) * 0.7
                        if amount >= minion.current_health:
                            score += self.evaluate_minion(minion) * 0.45
                elif effect.get("scope") == "enemy_hero" or target_side == "enemy_hero":
                    if enemy.effective_life <= amount:
                        score += 100_000.0
                    score += amount * 1.7
                elif target is not None and target_side == "enemy":
                    score += min(amount, target.current_health) * 0.8
                    if amount >= target.current_health or extra.get("if_target_is_damaged"):
                        score += self.evaluate_minion(target) * 0.65
                else:
                    score += amount * 0.2
                continue

            if kind == "heal":
                if ability.get("target_rule") == "all_friendly_figures":
                    missing = sum(max(0, minion.max_health - minion.current_health) for minion in player.board)
                    score += missing * 0.55 if missing > 0 else -3.0
                elif effect.get("scope") == "friendly_hero" or target_side == "friendly_hero":
                    missing = max(0, 30 - player.health)
                    score += min(amount, missing) * 0.6 if missing > 0 else -1.5
                elif target is not None and target_side == "friendly":
                    missing = max(0, target.max_health - target.current_health)
                    score += min(amount, missing) * 0.75 if missing > 0 else -2.0
                continue

            if kind == "draw_cards":
                score += max(1, amount) * 1.35
                continue

            if kind == "summon_token":
                if len(player.board) >= 5:
                    score -= 2.5
                    continue
                token_card = state.card_registry.get(effect.get("card_id"))
                if token_card is not None:
                    score += (token_card.attack or 0) * 1.0 + (token_card.health or 0) * 0.9
                    score += self.keyword_score(getattr(token_card, "keywords", []), attack=token_card.attack or 0, health=token_card.health or 0)
                else:
                    score += 2.0
                continue

            if kind == "grant_stats":
                attack = int(effect.get("attack") or 0)
                health = int(effect.get("health") or 0)
                if target is not None and target_side == "friendly":
                    score += attack * 1.1 + health * 0.9
                    if target.can_attack():
                        score += attack * 0.8
                else:
                    score += attack * 0.2 + health * 0.2
                continue

            if kind == "grant_keyword":
                keyword = effect.get("keyword") or ""
                if target is not None and target_side == "friendly":
                    score += self.keyword_score([keyword], attack=target.current_attack, health=target.current_health)
                    if keyword == "stealth" and target.can_attack():
                        score += target.current_attack * 0.5
                else:
                    score += 0.3
                continue

            if kind == "freeze":
                if target is not None and target_side == "enemy":
                    score += 1.2 + target.current_attack * 0.6
                continue

            if kind == "return_to_hand":
                if target is not None and target_side == "enemy":
                    max_cost = extra.get("max_cost")
                    if max_cost is None or (target.card.cost or 0) <= max_cost:
                        score += self.evaluate_minion(target) * 0.7
                continue

            if kind == "destroy":
                if target is not None and target_side == "enemy":
                    score += self.evaluate_minion(target) * 0.95
                continue

            if kind == "gain_ritual_mana":
                score += max(1, amount) * 0.6
                continue

            if kind == "discover_from_pool":
                score += 1.3
                continue

            if kind == "return_from_discard":
                score += 1.5
                continue

        return score

    def keyword_score(self, keywords: list[str], *, attack: int, health: int) -> float:
        score = 0.0
        runtime = {"ward": "divine_shield"}.get
        normalized = [runtime(keyword, keyword) for keyword in keywords]
        if "guard" in normalized or "taunt" in normalized:
            score += 1.5 + health * 0.1
        if "divine_shield" in normalized:
            score += 2.2
        if "rush" in normalized or "charge" in normalized:
            score += 1.4 + attack * 0.25
        if "stealth" in normalized:
            score += 0.8 + attack * 0.15
        if "poisonous" in normalized:
            score += 2.0
        if "lifesteal" in normalized:
            score += 1.0
        if "reborn" in normalized:
            score += 1.8
        return score


class BenchmarkPlayer(ScoredPlayer):
    def __init__(self) -> None:
        super().__init__(pass_penalty=4.0)


THINKING_LLM_SYSTEM = """\
You are playing Mythic Clash, a 1v1 card game. Play to win.

## Rules
""" + RULES_TEXT + """

## Additional rules
- Spell speeds: Slow (main phase only), Fast (also in response windows), Burst (resolves immediately, no response).
- Response windows: When a figure declares an attack, the defending player may play Fast/Burst spells before combat resolves. Players alternate responses until both pass, then combat resolves.
- Overwhelm: excess combat damage to a figure spills onto the enemy hero.
- Freeze: frozen figures skip their next ready phase.
- Ward/Divine Shield: absorbs the first damage instance.
- Activated relics: cost mana to use, typically once per turn.
- Unused mana converts to Ritual Mana (max 2), usable for spells and hero power only.

## Things you can do
- Play figures from hand to build board presence.
- Attack with ready figures — you can attack enemy figures (trading) OR attack the enemy hero directly (going face).
- Cast spells: removal, buffs, heals, card draw, board clears.
- Use your hero power (2 mana, once per turn, Slow speed).
- Activate relics for repeatable effects.
- Hold mana open to bank Ritual Mana or to threaten Fast spell responses.
- During response windows: cast Fast/Burst spells to change combat outcomes (buff defenders, damage attackers, freeze, heal).
- Pass to end your turn — any unspent mana becomes Ritual Mana.

## Things to consider
- You can check for lethal: can your board + spells kill the enemy hero this turn?
- You can trade (attack their figures) to control the board, or go face (attack their hero) to race for damage.
- You can hold mana open to represent a combat trick even if you don't have one — the opponent can see your mana but not your hand.
- You can sequence attacks in any order — sending a weaker figure first may bait out the opponent's combat trick.
- You can play around the opponent's possible spells by checking their mana and hand size.
- You can choose not to play all your figures at once if the opponent might have AoE (board clear effects).
- You can assess whether you're the aggressor (pushing damage) or defender (stabilizing) and play accordingly.
- You can count how many turns until you or the opponent dies at current damage rates.

Think step by step about the game state, then choose the best action.

Your response MUST end with a JSON block on its own line:
```json
{"action_id": "...", "plan": "...", "reasoning": "..."}
```

Where:
- action_id: the exact id of the legal action you choose
- plan: your 1-2 sentence plan for the next few turns
- reasoning: why you chose this specific action over alternatives
"""


MODEL_PRESETS: dict[str, dict[str, Any]] = {
    # Anthropic
    "sonnet": {"provider": "anthropic", "model": "claude-sonnet-4-20250514", "thinking": True, "budget": 5000},
    "haiku": {"provider": "anthropic", "model": "claude-haiku-4-5-20251001", "thinking": True, "budget": 4000},
    "opus": {"provider": "anthropic", "model": "claude-opus-4-20250514", "thinking": True, "budget": 6000},
    # OpenAI
    "gpt-4o": {"provider": "openai", "model": "gpt-4o", "thinking": False},
    "gpt-4o-mini": {"provider": "openai", "model": "gpt-4o-mini", "thinking": False},
    "o4-mini": {"provider": "openai", "model": "o4-mini", "thinking": False},
    # Gemini
    "gemini-lite": {"provider": "gemini", "model": "gemini-3.1-flash-lite", "thinking": False},
    "gemini-flash": {"provider": "gemini", "model": "gemini-3.1-flash-lite", "thinking": False},
    "gemini-pro": {"provider": "gemini", "model": "gemini-3.1-pro-preview", "thinking": True, "budget": 5000},
}

DEFAULT_MODEL = "gemini-lite"


class ThinkingLLMPlayer(BasePlayer):
    """LLM player that supports Anthropic, OpenAI, and Gemini models."""

    def __init__(
        self,
        model: str | None = None,
        budget_tokens: int | None = None,
        api_key_env: str | None = None,
    ) -> None:
        model = model or DEFAULT_MODEL
        preset = MODEL_PRESETS.get(model)
        if preset:
            self.provider = preset["provider"]
            self.model_id = preset["model"]
            self.use_thinking = preset.get("thinking", False)
            self.budget_tokens = budget_tokens or preset.get("budget", 5000)
        else:
            self.model_id = model
            if "claude" in model:
                self.provider = "anthropic"
                self.use_thinking = True
            elif "gemini" in model:
                self.provider = "gemini"
                self.use_thinking = "flash" in model or "pro" in model
            else:
                self.provider = "openai"
                self.use_thinking = False
            self.budget_tokens = budget_tokens or 5000

        self.anthropic_client = None
        self.openai_client = None
        self.gemini_client = None

        if self.provider == "anthropic":
            import anthropic
            key_env = api_key_env or "ANTHROPIC_API_KEY"
            api_key = os.environ.get(key_env)
            if not api_key:
                raise RuntimeError(f"Missing {key_env} for Anthropic LLM self-play.")
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)
        elif self.provider == "gemini":
            from google import genai
            key_env = api_key_env or "GEMINI_API_KEY"
            api_key = os.environ.get(key_env)
            if not api_key:
                raise RuntimeError(f"Missing {key_env} for Gemini LLM self-play.")
            self.gemini_client = genai.Client(api_key=api_key)
        else:
            from openai import OpenAI
            key_env = api_key_env or "OPENAI_API_KEY"
            api_key = os.environ.get(key_env)
            if not api_key:
                raise RuntimeError(f"Missing {key_env} for OpenAI LLM self-play.")
            self.openai_client = OpenAI(api_key=api_key)

        self.turn_log: list[dict[str, Any]] = []

    def build_user_prompt(self, state: GameState, player_index: int, actions: list[dict[str, Any]]) -> str:
        view = game_state_view(state, player_index)
        you = view["you"]
        opp = view["opponent"]

        lines = []
        lines.append(f"=== TURN {view['turn_number']} ===")

        # Response window context
        pending = view.get("pending_attack")
        phase = view.get("phase", "main")
        if pending and phase.startswith("response"):
            lines.append("")
            lines.append("*** COMBAT RESPONSE WINDOW ***")
            lines.append(f"  {pending['attacker']} ({pending['attacker_attack']}/{pending['attacker_health']}) is attacking your {pending['target']} ({pending['target_attack']}/{pending['target_health']})")
            lines.append(f"  You may play Fast or Burst spells before combat resolves.")
            lines.append(f"  If you pass, combat proceeds.")
        lines.append("")

        # Your status
        lines.append(f"YOUR HERO: {you['hero']['name'] if you['hero'] else 'Unknown'}")
        lines.append(f"  Health: {you['health']}  Armor: {you['armor']}  Mana: {you['mana']}/{you['max_mana']}  Ritual Mana: {you['ritual_mana']}")
        hp = you["hero_power"]
        lines.append(f"  Hero Power: {hp['name']} ({'USED' if hp['used'] else 'available'})")
        lines.append(f"  Deck: {you['deck_count']} cards remaining")
        lines.append("")

        # Your hand
        lines.append(f"YOUR HAND ({len(you['hand'])} cards):")
        for card in you["hand"]:
            kw = ", ".join(card["keywords"]) if card["keywords"] else ""
            if card["type"] == "minion":
                lines.append(f"  [{card['hand_index']}] {card['name']} - {card['cost']} mana {card['attack']}/{card['health']}{' [' + kw + ']' if kw else ''} | {card['text']}")
            else:
                lines.append(f"  [{card['hand_index']}] {card['name']} ({card['type']}) - {card['cost']} mana | {card['text']}")
        lines.append("")

        # Your board
        lines.append(f"YOUR BOARD ({len(you['board'])}/5 figures):")
        if you["board"]:
            for m in you["board"]:
                kw = ", ".join(m["keywords"]) if m["keywords"] else ""
                status = []
                if m["sleeping"]:
                    status.append("sleeping")
                if m["can_attack"]:
                    status.append("ready")
                if m["divine_shield"]:
                    status.append("shielded")
                if m["reborn_available"]:
                    status.append("reborn")
                lines.append(f"  {m['unit_id']}: {m['name']} {m['attack']}/{m['health']}{' [' + kw + ']' if kw else ''} ({', '.join(status)})")
        else:
            lines.append("  (empty)")
        if you["relics"]:
            lines.append(f"  Relics: {', '.join(r['name'] + ' - ' + r['text'] for r in you['relics'])}")
        lines.append("")

        # Enemy status
        lines.append(f"ENEMY HERO: {opp['hero']['name'] if opp['hero'] else 'Unknown'}")
        lines.append(f"  Health: {opp['health']}  Armor: {opp['armor']}  Mana: {opp['mana']}/{opp['max_mana']}")
        hp = opp["hero_power"]
        lines.append(f"  Hero Power: {hp['name']} ({'USED' if hp['used'] else 'available'})")
        lines.append(f"  Hand: {opp['hand_count']} cards  Deck: {opp['deck_count']} cards")
        lines.append("")

        # Enemy board
        lines.append(f"ENEMY BOARD ({len(opp['board'])}/5 figures):")
        if opp["board"]:
            for m in opp["board"]:
                kw = ", ".join(m["keywords"]) if m["keywords"] else ""
                tags = []
                if m["divine_shield"]:
                    tags.append("shielded")
                if m["reborn_available"]:
                    tags.append("reborn")
                lines.append(f"  {m['unit_id']}: {m['name']} {m['attack']}/{m['health']}{' [' + kw + ']' if kw else ''}{' (' + ', '.join(tags) + ')' if tags else ''}")
        else:
            lines.append("  (empty)")
        if opp["relics"]:
            lines.append(f"  Relics: {', '.join(r['name'] + ' - ' + r['text'] for r in opp['relics'])}")

        # Opponent threat assessment
        opp_mana = opp["mana"] + opp.get("ritual_mana", 0)
        opp_hero = opp['hero']['name'] if opp['hero'] else ''
        if opp_mana >= 2 and opp['hand_count'] > 0:
            lines.append(f"  WARNING: Enemy has {opp_mana} mana and {opp['hand_count']} cards — may have Fast spells!")
        lines.append("")

        # Graveyards
        your_dead = you.get("graveyard", [])
        opp_dead = opp.get("graveyard", [])
        if your_dead:
            names = [f"{c['name']}({c['cost']})" for c in your_dead]
            lines.append(f"YOUR GRAVEYARD: {', '.join(names)}")
        if opp_dead:
            names = [f"{c['name']}({c['cost']})" for c in opp_dead]
            lines.append(f"ENEMY GRAVEYARD: {', '.join(names)}")
        if your_dead or opp_dead:
            lines.append("")

        # Recent history
        lines.append("RECENT EVENTS:")
        for event in view["history"]:
            lines.append(f"  {event}")
        lines.append("")

        # Legal actions
        lines.append(f"LEGAL ACTIONS ({len(actions)}):")
        for action in actions:
            lines.append(f'  id="{action["id"]}"  {action["label"]}')
        lines.append("")

        if pending and phase.startswith("response"):
            lines.append("You are in a RESPONSE WINDOW. Decide: use a Fast/Burst spell to change the combat outcome, or pass to let combat resolve.")
            lines.append("Consider: Can you save your figure? Can you buff it to win the trade? Can you kill the attacker before damage?")
        else:
            lines.append("Think step by step:")
            lines.append("1. CHECK LETHAL: Can your board + spells kill the enemy hero this turn?")
            lines.append("2. ASSESS ROLE: Am I the aggressor (racing) or defender (trading to stabilize)?")
            lines.append("3. PLAY AROUND: Does the enemy have mana open? What tricks could they have?")
            lines.append("4. SEQUENCE: If attacking, send WEAKEST figure first to bait their combat trick.")
            lines.append("5. HOLD MANA? Keep 2+ mana open if you have Fast spells — bluff or respond.")
            lines.append("6. OVEREXTEND? Don't play everything if the enemy might have AoE.")
        lines.append('End your response with: ```json\\n{"action_id": "...", "plan": "...", "reasoning": "..."}\\n```')

        return "\n".join(lines)

    def choose_action(self, state: GameState, player_index: int, actions: list[dict[str, Any]]) -> dict[str, Any]:
        if len(actions) == 1:
            chosen = dict(actions[0])
            chosen["llm_reason"] = "only legal action"
            chosen["llm_thinking"] = ""
            chosen["llm_plan"] = ""
            return chosen

        user_prompt = self.build_user_prompt(state, player_index, actions)

        if self.provider == "anthropic":
            thinking_text, response_text = self._call_anthropic(user_prompt)
        elif self.provider == "gemini":
            thinking_text, response_text = self._call_gemini(user_prompt)
        else:
            thinking_text, response_text = self._call_openai(user_prompt)

        # Parse JSON from response
        payload = self._extract_json(response_text)
        chosen_id = payload.get("action_id", "")

        for action in actions:
            if action["id"] == chosen_id:
                chosen = dict(action)
                chosen["llm_reason"] = payload.get("reasoning", "")
                chosen["llm_thinking"] = thinking_text
                chosen["llm_plan"] = payload.get("plan", "")
                self.turn_log.append({
                    "turn": state.turn_number,
                    "player": player_index,
                    "action_id": chosen_id,
                    "reasoning": payload.get("reasoning", ""),
                    "plan": payload.get("plan", ""),
                    "thinking": thinking_text,
                    "response": response_text,
                })
                return chosen

        # Fallback: if the model picked a bad ID, try fuzzy match
        for action in actions:
            if chosen_id in action["id"] or action["id"] in chosen_id:
                chosen = dict(action)
                chosen["llm_reason"] = f"(fuzzy match) {payload.get('reasoning', '')}"
                chosen["llm_thinking"] = thinking_text
                chosen["llm_plan"] = payload.get("plan", "")
                return chosen

        # Last resort: pass
        for action in actions:
            if action["type"] == "pass":
                chosen = dict(action)
                chosen["llm_reason"] = f"(fallback - model chose invalid id: {chosen_id})"
                chosen["llm_thinking"] = thinking_text
                chosen["llm_plan"] = ""
                return chosen

        return dict(actions[-1])

    def _call_anthropic(self, user_prompt: str) -> tuple[str, str]:
        kwargs: dict[str, Any] = {
            "model": self.model_id,
            "max_tokens": 8000,
            "messages": [{"role": "user", "content": user_prompt}],
            "system": THINKING_LLM_SYSTEM,
        }
        if self.use_thinking:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": self.budget_tokens}

        response = self.anthropic_client.messages.create(**kwargs)

        thinking_text = ""
        response_text = ""
        for block in response.content:
            if block.type == "thinking":
                thinking_text = block.thinking
            elif block.type == "text":
                response_text = block.text
        return thinking_text, response_text

    def _call_openai(self, user_prompt: str) -> tuple[str, str]:
        response = self.openai_client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": THINKING_LLM_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=4000,
        )
        text = response.choices[0].message.content or ""
        return "", text

    def _call_gemini(self, user_prompt: str) -> tuple[str, str]:
        import time as _time
        from google.genai import types

        config_kwargs: dict[str, Any] = {
            "max_output_tokens": 4000,
            "system_instruction": THINKING_LLM_SYSTEM,
        }
        if self.use_thinking:
            config_kwargs["thinking_config"] = types.ThinkingConfig(
                thinking_budget=self.budget_tokens,
            )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.gemini_client.models.generate_content(
                    model=self.model_id,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(**config_kwargs),
                )
                break
            except Exception as e:
                err_str = str(e).lower()
                if self.use_thinking and attempt == 0 and "thinking" in err_str:
                    config_kwargs.pop("thinking_config", None)
                    self.use_thinking = False
                    continue
                if ("rate" in err_str or "429" in err_str or "quota" in err_str or "resource" in err_str) and attempt < max_retries - 1:
                    _time.sleep(5 * (attempt + 1))
                    continue
                raise

        thinking_text = ""
        response_text = ""
        if response.candidates and response.candidates[0].content:
            for part in response.candidates[0].content.parts:
                if getattr(part, "thought", False):
                    thinking_text += part.text or ""
                else:
                    response_text += part.text or ""

        return thinking_text, response_text

    def _extract_json(self, text: str) -> dict[str, Any]:
        import re
        # Try to find JSON in ```json ... ``` block
        match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try to find any JSON object
        match = re.search(r"\{[^{}]*\"action_id\"[^{}]*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {}


# Keep old names for backwards compatibility with scripts
class PromptLLMPlayer(ThinkingLLMPlayer):
    pass


class AgenticLLMPlayer(ThinkingLLMPlayer):
    pass
