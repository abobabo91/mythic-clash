import { useState, useCallback } from "react";
import { GameState, ActionInfo, MinionInfo } from "../types";
import { HandCard, BoardMinion } from "./Card";
import "./GameBoard.css";

interface Props {
  state: GameState;
  actions: ActionInfo[];
  onAction: (actionId: string) => void;
  hint: string | null;
  onHint: () => void;
  hasActions: boolean;
}

/** No rotation — flat hand layout */
function fanStyle(_index: number, _total: number): React.CSSProperties {
  return {};
}

const SLOT_COUNT = 7;

export function GameBoard({ state, actions, onAction, hint, onHint, hasActions }: Props) {
  const [selectedCard, setSelectedCard] = useState<number | null>(null);
  const [selectedAttacker, setSelectedAttacker] = useState<string | null>(null);

  const isMyTurn = actions.length > 0;
  const you = state.you;
  const opp = state.opponent;

  // Build action lookup maps
  const playActions = actions.filter(a => a.type === "play" || a.type === "play_spell" || a.type === "play_relic");
  const attackActions = actions.filter(a => a.type === "attack");
  const heroPowerActions = actions.filter(a => a.type === "hero_power");
  const relicActions = actions.filter(a => a.type === "activate_relic");
  const passAction = actions.find(a => a.type === "pass");

  const playableHandIndices = new Set(playActions.map(a => a.hand_index).filter(i => i !== undefined));
  const attackerIds = new Set(attackActions.map(a => a.unit_id));

  const getTargetsForAttacker = useCallback((unitId: string) => {
    return attackActions.filter(a => a.unit_id === unitId).map(a => a.target!);
  }, [attackActions]);

  const handleHandClick = (index: number) => {
    setSelectedAttacker(null);
    if (selectedCard === index) {
      const action = playActions.find(a => a.hand_index === index);
      if (action) {
        onAction(action.id);
        setSelectedCard(null);
      }
    } else {
      setSelectedCard(index);
    }
  };

  const handleBoardClick = (minion: MinionInfo, friendly: boolean) => {
    if (selectedAttacker) {
      const targets = getTargetsForAttacker(selectedAttacker);
      if (targets.includes(minion.unit_id)) {
        const action = attackActions.find(a => a.unit_id === selectedAttacker && a.target === minion.unit_id);
        if (action) {
          onAction(action.id);
          setSelectedAttacker(null);
          setSelectedCard(null);
          return;
        }
      }
    }

    if (friendly && attackerIds.has(minion.unit_id)) {
      setSelectedCard(null);
      setSelectedAttacker(selectedAttacker === minion.unit_id ? null : minion.unit_id);
    }
  };

  const handleHeroClick = (isEnemy: boolean) => {
    if (isEnemy && selectedAttacker) {
      const action = attackActions.find(a => a.unit_id === selectedAttacker && a.target === "hero");
      if (action) {
        onAction(action.id);
        setSelectedAttacker(null);
        setSelectedCard(null);
      }
    }
  };

  const targets = selectedAttacker ? getTargetsForAttacker(selectedAttacker) : [];

  return (
    <div className="game-board">

      {/* ── Opponent Hero Row ── */}
      <div className="opponent-area">
        <div
          className={`hero-portrait enemy ${targets.includes("hero") ? "targetable" : ""}`}
          onClick={() => handleHeroClick(true)}
        >
          <div className="hero-name">{opp.hero_name}</div>
          <div className="hero-hp">
            {opp.armor > 0 && <span className="armor">{opp.armor}</span>}
            <span className="hp">{opp.health}</span>
          </div>
          <div className="hero-mana">{opp.mana}/{opp.max_mana}{opp.ritual_mana > 0 ? ` +${opp.ritual_mana}R` : ""}</div>
          <div className="hero-info">{opp.hand_size} cards | {opp.deck_size} deck</div>
        </div>
        {opp.relics.map((r, i) => (
          <div key={i} className="relic-slot enemy" title={r.text}>
            <div className="relic-name">{r.name}</div>
          </div>
        ))}
      </div>

      {/* ── Opponent Board ── */}
      <div className="opponent-board">
        <div className="board-slots">
          {Array.from({ length: SLOT_COUNT }).map((_, i) => (
            <div key={i} className="board-slot" />
          ))}
        </div>
        {opp.board.map(m => (
          <BoardMinion
            key={m.unit_id}
            minion={m}
            friendly={false}
            canAttack={false}
            selected={false}
            targetable={targets.includes(m.unit_id)}
            onClick={() => handleBoardClick(m, false)}
          />
        ))}
        {opp.board.length === 0 && <div className="empty-board">No minions</div>}
      </div>

      {/* ── Center Divider ── */}
      <div className="center-divider">
        <div className="turn-badge">
          Turn {state.turn} &middot; {state.phase}
          {state.winner !== null && (
            <span className="winner-text"> &middot; {state.winner === 0 ? "Victory!" : "Defeat"}</span>
          )}
        </div>

        <div className="action-group">
          {hasActions && (
            <button className="hint-btn" onClick={onHint} title="Ask the bot what it would do">
              ? Hint
            </button>
          )}
          {heroPowerActions.length > 0 && (
            <button onClick={() => onAction(heroPowerActions[0].id)} title={you.hero_power_text}>
              Hero Power
            </button>
          )}
          {relicActions.map(a => (
            <button key={a.id} onClick={() => onAction(a.id)}>
              {a.label}
            </button>
          ))}
        </div>

        {passAction && (
          <button
            className="end-turn-btn"
            onClick={() => {
              onAction(passAction.id);
              setSelectedCard(null);
              setSelectedAttacker(null);
            }}
          >
            End Turn
          </button>
        )}

        {hint && (
          <div className="hint-popup">
            Bot suggests: <strong>{hint}</strong>
          </div>
        )}
      </div>

      {/* ── Your Board ── */}
      <div className="your-board">
        <div className="board-slots">
          {Array.from({ length: SLOT_COUNT }).map((_, i) => (
            <div key={i} className="board-slot" />
          ))}
        </div>
        {you.board.map(m => (
          <BoardMinion
            key={m.unit_id}
            minion={m}
            friendly={true}
            canAttack={attackerIds.has(m.unit_id)}
            selected={selectedAttacker === m.unit_id}
            targetable={false}
            onClick={() => handleBoardClick(m, true)}
          />
        ))}
        {you.board.length === 0 && <div className="empty-board">No minions</div>}
      </div>

      {/* ── Your Hero Row ── */}
      <div className="your-area">
        <div className="hero-portrait friendly">
          <div className="hero-name">{you.hero_name}</div>
          <div className="hero-hp">
            {you.armor > 0 && <span className="armor">{you.armor}</span>}
            <span className="hp">{you.health}</span>
          </div>
          <div className="hero-mana">{you.mana}/{you.max_mana}{you.ritual_mana > 0 ? ` +${you.ritual_mana}R` : ""}</div>
          <div className="hero-info">{you.hand.length} hand | {you.deck_size} deck</div>
        </div>
        {you.relics.map((r, i) => (
          <div key={i} className={`relic-slot friendly ${r.activated_available ? "activatable" : ""}`} title={r.text}>
            <div className="relic-name">{r.name}</div>
          </div>
        ))}
      </div>

      {/* ── Your Hand ── */}
      <div className="hand-row">
        {you.hand.map((card, i) => (
          <div key={`${card.id}-${i}`} style={fanStyle(i, you.hand.length)}>
            <HandCard
              card={card}
              playable={playableHandIndices.has(i)}
              selected={selectedCard === i}
              onClick={() => handleHandClick(i)}
            />
          </div>
        ))}
      </div>

      {/* ── Event Log (minimal overlay) ── */}
      <div className="event-log">
        {state.history.slice(-5).map((e, i) => (
          <div key={i} className="log-entry">{e}</div>
        ))}
      </div>
    </div>
  );
}
