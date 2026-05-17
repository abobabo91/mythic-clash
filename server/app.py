"""FastAPI WebSocket server for Mythic Clash."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from game.engine import (
    create_v1_game,
    legal_actions,
    apply_action_interactive,
    current_priority_player,
    game_state_view,
)
from game.players import RolloutPlayer

app = FastAPI(title="Mythic Clash")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA = ROOT / "data"


def list_cultures() -> list[dict[str, str]]:
    cultures = []
    for p in sorted((DATA / "cards-v1").glob("*-v1.json")):
        slug = p.stem.replace("-v1", "")
        if "neutral" in slug or "domain" in slug:
            continue
        pack = json.loads(p.read_text(encoding="utf-8"))
        hero = next((c for c in pack["cards"] if c["card_type"] == "hero"), None)
        cultures.append({
            "slug": slug,
            "name": slug.replace("-", " ").title(),
            "hero": hero["name"] if hero else slug,
        })
    return cultures


@app.get("/api/cultures")
def get_cultures():
    return list_cultures()


def state_to_client(state, player_index: int) -> dict[str, Any]:
    """Build the game state view for a specific player."""
    you = state.players[player_index]
    opp = state.players[1 - player_index]

    def minion_dict(m):
        return {
            "unit_id": m.unit_id,
            "name": m.card.name,
            "attack": m.current_attack,
            "health": m.current_health,
            "max_health": m.max_health + m.enchant_health,
            "cost": m.card.cost,
            "keywords": list(m.runtime_keywords),
            "can_attack": m.can_attack(),
            "sleeping": m.sleeping,
            "divine_shield": m.divine_shield,
            "reborn": m.reborn_available,
            "text": m.card.text,
        }

    def card_dict(c):
        return {
            "id": c.id,
            "name": c.name,
            "cost": c.cost,
            "card_type": c.card_type,
            "attack": getattr(c, "attack", 0),
            "health": getattr(c, "health", 0),
            "keywords": getattr(c, "keywords", []),
            "text": c.text,
            "speed": getattr(c, "speed", ""),
        }

    def relic_dict(r):
        return {
            "name": r.card.name,
            "text": r.card.text,
            "activated_available": r.activated_available,
        }

    return {
        "turn": state.turn_number,
        "phase": state.phase,
        "active_player": state.active_player,
        "priority": current_priority_player(state),
        "winner": state.winner,
        "you": {
            "health": you.health,
            "armor": you.armor,
            "mana": you.mana,
            "max_mana": you.max_mana,
            "ritual_mana": you.ritual_mana,
            "hand": [card_dict(c) for c in you.hand],
            "board": [minion_dict(m) for m in you.board],
            "relics": [relic_dict(r) for r in you.relics],
            "deck_size": len(you.deck),
            "hero_name": you.name,
            "hero_power_used": you.hero_power_used,
            "hero_power_text": you.hero_power_name or "",
        },
        "opponent": {
            "health": opp.health,
            "armor": opp.armor,
            "mana": opp.mana,
            "max_mana": opp.max_mana,
            "ritual_mana": opp.ritual_mana,
            "hand_size": len(opp.hand),
            "board": [minion_dict(m) for m in opp.board],
            "relics": [relic_dict(r) for r in opp.relics],
            "deck_size": len(opp.deck),
            "hero_name": opp.name,
            "hero_power_used": opp.hero_power_used,
        },
        "history": state.history[-10:],
    }


def actions_to_client(actions: list[dict]) -> list[dict]:
    """Simplify action dicts for the client."""
    out = []
    for a in actions:
        out.append({
            "id": a["id"],
            "label": a["label"],
            "type": a["type"],
            "hand_index": a.get("hand_index"),
            "unit_id": a.get("unit_id"),
            "target": a.get("target"),
        })
    return out


# Store active games so hint endpoint can access them
active_games: dict[str, dict] = {}


@app.websocket("/ws/game")
async def game_ws(ws: WebSocket):
    await ws.accept()

    try:
        # Wait for game config
        config = await ws.receive_json()
        slug_a = config["culture_a"]
        slug_b = config["culture_b"]
        opponent_type = config.get("opponent", "bot")  # "bot" or "llm"
        player_side = config.get("side", 0)  # 0 = player A, 1 = player B
        seed = config.get("seed", 42)

        pack_a = str(DATA / f"cards-v1/{slug_a}-v1.json")
        pack_b = str(DATA / f"cards-v1/{slug_b}-v1.json")
        deck_a = str(sorted((DATA / "decks-v1").glob(f"{slug_a}-*.json"))[0])
        deck_b = str(sorted((DATA / "decks-v1").glob(f"{slug_b}-*.json"))[0])

        state = create_v1_game(pack_a, deck_a, pack_b, deck_b, seed=seed)
        bot = RolloutPlayer()
        human_player = player_side
        ai_player = 1 - player_side

        # Send initial state
        await ws.send_json({
            "type": "state",
            "state": state_to_client(state, human_player),
            "actions": [],
        })

        while state.winner is None:
            priority = current_priority_player(state)
            actions = legal_actions(state, priority)

            if not actions:
                break

            if priority == human_player:
                # Send state + legal actions to human
                await ws.send_json({
                    "type": "state",
                    "state": state_to_client(state, human_player),
                    "actions": actions_to_client(actions),
                })

                # Wait for human choice (or hint request)
                while True:
                    msg = await ws.receive_json()

                    if msg.get("type") == "hint":
                        # Use the heuristic bot to suggest best action
                        hint_bot = RolloutPlayer()
                        suggested = hint_bot.choose_action(state, human_player, actions)
                        await ws.send_json({
                            "type": "hint",
                            "action_id": suggested.get("id", ""),
                            "label": suggested.get("label", ""),
                            "reason": f"The bot recommends: {suggested.get('label', 'pass')}",
                        })
                        continue  # wait for actual action

                    action_id = msg.get("action_id")
                    break

                chosen = next((a for a in actions if a["id"] == action_id), None)
                if not chosen:
                    chosen = next((a for a in actions if a["type"] == "pass"), actions[-1])
            else:
                # AI plays
                chosen = bot.choose_action(state, ai_player, actions)

            apply_action_interactive(state, chosen, priority)

            # Send updated state after each action
            await ws.send_json({
                "type": "state",
                "state": state_to_client(state, human_player),
                "actions": [],
                "last_action": {
                    "player": priority,
                    "action": chosen.get("label", chosen.get("id", "")),
                },
            })

        # Game over
        winner = "you" if state.winner == human_player else "opponent"
        await ws.send_json({
            "type": "game_over",
            "winner": winner,
            "state": state_to_client(state, human_player),
        })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await ws.send_json({"type": "error", "message": str(e)})
        except:
            pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
