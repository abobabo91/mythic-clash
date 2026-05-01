"""
Player controllers for Mythic Clash self-play.
"""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI

from .engine import GameState, game_state_view


class BasePlayer:
    def choose_action(self, state: GameState, player_index: int, legal_actions: list[dict[str, Any]]) -> dict[str, Any]:
        raise NotImplementedError


class HeuristicPlayer(BasePlayer):
    def choose_action(self, state: GameState, player_index: int, legal_actions: list[dict[str, Any]]) -> dict[str, Any]:
        view = game_state_view(state, player_index)
        you = view["you"]
        opponent = view["opponent"]

        attack_actions = [action for action in legal_actions if action["type"] == "attack"]
        spell_actions = [action for action in legal_actions if action["type"] == "play_spell"]
        play_actions = [action for action in legal_actions if action["type"] == "play"]
        power_actions = [action for action in legal_actions if action["type"] == "hero_power"]

        if attack_actions:
            lethal = [action for action in attack_actions if action.get("target") == "hero"]
            total_face = sum(m["attack"] for m in you["board"] if m["can_attack"])
            if lethal and total_face >= opponent["health"] + opponent["armor"]:
                return lethal[0]
            hero_hits = [action for action in attack_actions if action.get("target") == "hero"]
            if hero_hits and len(opponent["board"]) <= 1:
                return hero_hits[0]
            return attack_actions[0]

        if spell_actions:
            priority = {
                "execute_damaged": 0,
                "damage": 1,
                "aoe_enemy": 2,
                "summon_pair": 3,
                "buff": 4,
                "heal": 5,
                "draw": 6,
                "random_missiles": 7,
                "coin": 8,
            }
            hand = {card["hand_index"]: card for card in you["hand"]}
            spell_actions.sort(
                key=lambda action: (
                    priority.get(hand[action["hand_index"]]["spell_kind"], 99),
                    -hand[action["hand_index"]]["cost"],
                )
            )
            return spell_actions[0]

        if play_actions:
            hand = {card["hand_index"]: card for card in you["hand"]}
            play_actions.sort(
                key=lambda action: (
                    -hand[action["hand_index"]]["cost"],
                    -(hand[action["hand_index"]]["attack"] + hand[action["hand_index"]]["health"]),
                    action["position"],
                )
            )
            return play_actions[0]

        if power_actions:
            return power_actions[0]

        return {"id": "pass", "type": "pass", "label": "End turn"}


class PromptLLMPlayer(BasePlayer):
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.2,
        api_key_env: str = "OPENAI_API_KEY",
        reasoning_effort: str | None = None,
    ) -> None:
        api_key = os.environ.get(api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing {api_key_env} for LLM self-play.")
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.reasoning_effort = reasoning_effort

    def build_prompt(self, state: GameState, player_index: int, legal_actions: list[dict[str, Any]]) -> tuple[str, str]:
        view = game_state_view(state, player_index)
        system = (
            "You are a strong digital card game player in a Hearthstone-like duel. "
            "Choose exactly one legal action. "
            "Optimize for mana efficiency, board control, favorable trades, damage racing, and lethal setups. "
            "Respect Taunt, hand size, and the value of initiative. "
            "Return JSON only with keys action_id and short_reason."
        )
        user = json.dumps(
            {
                "rules": view["rules_summary"],
                "state": view,
                "legal_actions": legal_actions,
                "instruction": (
                    "Choose one legal action_id only. "
                    "You always receive the full rules, private hand, public board, and recent history every turn. "
                    "Return JSON: {\"action_id\": \"...\", \"short_reason\": \"...\"}."
                ),
            },
            ensure_ascii=False,
            indent=2,
        )
        return system, user

    def choose_action(self, state: GameState, player_index: int, legal_actions: list[dict[str, Any]]) -> dict[str, Any]:
        system, user = self.build_prompt(state, player_index, legal_actions)
        kwargs: dict[str, Any] = {
            "model": self.model,
            "input": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": self.temperature,
            "text": {"format": {"type": "json_object"}},
        }
        if self.reasoning_effort:
            kwargs["reasoning"] = {"effort": self.reasoning_effort}

        response = self.client.responses.create(**kwargs)
        raw_text = getattr(response, "output_text", None)
        if not raw_text:
            output = getattr(response, "output", [])
            if output:
                raw_text = output[0].content[0].text
        payload = json.loads(raw_text)
        chosen_id = payload["action_id"]
        for action in legal_actions:
            if action["id"] == chosen_id:
                chosen = dict(action)
                chosen["llm_reason"] = payload.get("short_reason", "")
                return chosen
        raise RuntimeError(f"Model chose invalid action_id: {chosen_id}")


class AgenticLLMPlayer(PromptLLMPlayer):
    """
    Placeholder for a future agentic version.

    Right now it uses the exact same per-turn prompt path, but it keeps a
    separate interface ready for future upgrades like planning, memory,
    tool use, or tree search.
    """

    pass
