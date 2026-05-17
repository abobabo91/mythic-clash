import { useState, useEffect, useRef, useCallback } from "react";
import { GameBoard } from "./components/GameBoard";
import { Rulebook } from "./components/Rulebook";
import { GameState, ActionInfo, ServerMessage, CultureInfo } from "./types";

const WS_URL = "ws://localhost:8000/ws/game";
const API_URL = "http://localhost:8000/api";

function App() {
  const [screen, setScreen] = useState<"lobby" | "playing">("lobby");
  const [cultures, setCultures] = useState<CultureInfo[]>([]);
  const [myCulture, setMyCulture] = useState("");
  const [oppCulture, setOppCulture] = useState("");
  const [opponent, setOpponent] = useState<"bot" | "llm">("bot");
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [actions, setActions] = useState<ActionInfo[]>([]);
  const [gameOver, setGameOver] = useState<string | null>(null);
  const [showRules, setShowRules] = useState(false);
  const [hint, setHint] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/cultures`)
      .then(r => r.json())
      .then(data => {
        setCultures(data);
        if (data.length > 0) {
          setMyCulture(data[0].slug);
          setOppCulture(data[Math.min(1, data.length - 1)].slug);
        }
      })
      .catch(() => {});
  }, []);

  const startGame = useCallback(() => {
    const ws = new WebSocket(WS_URL);
    wsRef.current = ws;

    ws.onopen = () => {
      ws.send(JSON.stringify({
        culture_a: myCulture,
        culture_b: oppCulture,
        opponent,
        side: 0,
        seed: Math.floor(Math.random() * 10000),
      }));
      setScreen("playing");
      setGameOver(null);
      setHint(null);
    };

    ws.onmessage = (event) => {
      const msg: ServerMessage = JSON.parse(event.data);
      if (msg.type === "state") {
        if (msg.state) setGameState(msg.state);
        setActions(msg.actions || []);
        setHint(null);
      } else if (msg.type === "game_over") {
        if (msg.state) setGameState(msg.state);
        setActions([]);
        setGameOver(msg.winner === "you" ? "Victory!" : "Defeat");
      } else if (msg.type === "hint") {
        const hintMsg = msg as any;
        setHint(`${hintMsg.label}`);
      } else if (msg.type === "error") {
        console.error("Server error:", msg.message);
      }
    };

    ws.onclose = () => {
      wsRef.current = null;
    };
  }, [myCulture, oppCulture, opponent]);

  const sendAction = useCallback((actionId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action_id: actionId }));
      setActions([]);
      setHint(null);
    }
  }, []);

  const requestHint = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "hint" }));
    }
  }, []);

  const backToLobby = () => {
    wsRef.current?.close();
    wsRef.current = null;
    setScreen("lobby");
    setGameState(null);
    setActions([]);
    setGameOver(null);
    setHint(null);
  };

  if (screen === "lobby") {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "100vh", gap: 20 }}>
        <h1 style={{ fontSize: 32, color: "var(--accent)", letterSpacing: 3, fontFamily: "inherit", textShadow: "0 0 20px var(--accent-glow)" }}>MYTHIC CLASH</h1>
        <p style={{ color: "var(--text-dim)", fontSize: 12, letterSpacing: 2, textTransform: "uppercase" }}>Choose your culture and opponent</p>

        <div style={{ display: "flex", gap: 32, alignItems: "flex-start", marginTop: 20 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, alignItems: "center" }}>
            <label style={{ fontSize: 11, color: "var(--text-dim)", letterSpacing: 1, textTransform: "uppercase" }}>Your Culture</label>
            <select value={myCulture} onChange={e => setMyCulture(e.target.value)} style={{ width: 240 }}>
              {cultures.map(c => (
                <option key={c.slug} value={c.slug}>{c.name}</option>
              ))}
            </select>
            {myCulture && (
              <div style={{ fontSize: 11, color: "var(--accent)", textShadow: "0 0 6px var(--accent-glow)" }}>
                {cultures.find(c => c.slug === myCulture)?.hero}
              </div>
            )}
          </div>

          <div style={{ fontSize: 18, color: "var(--text-dim)", paddingTop: 28, letterSpacing: 4 }}>VS</div>

          <div style={{ display: "flex", flexDirection: "column", gap: 8, alignItems: "center" }}>
            <label style={{ fontSize: 11, color: "var(--text-dim)", letterSpacing: 1, textTransform: "uppercase" }}>Opponent Culture</label>
            <select value={oppCulture} onChange={e => setOppCulture(e.target.value)} style={{ width: 240 }}>
              {cultures.map(c => (
                <option key={c.slug} value={c.slug}>{c.name}</option>
              ))}
            </select>
            {oppCulture && (
              <div style={{ fontSize: 11, color: "var(--accent)", textShadow: "0 0 6px var(--accent-glow)" }}>
                {cultures.find(c => c.slug === oppCulture)?.hero}
              </div>
            )}
          </div>
        </div>

        <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
          <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, cursor: "pointer", color: "var(--text-dim)" }}>
            <input type="radio" name="opp" checked={opponent === "bot"} onChange={() => setOpponent("bot")} />
            Heuristic Bot
          </label>
          <label style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, cursor: "pointer", color: "var(--text-dim)" }}>
            <input type="radio" name="opp" checked={opponent === "llm"} onChange={() => setOpponent("llm")} />
            LLM (Gemini)
          </label>
        </div>

        <div style={{ display: "flex", gap: 12, marginTop: 20 }}>
          <button className="primary" onClick={startGame} style={{ padding: "12px 36px", fontSize: 15, letterSpacing: 2 }}>
            Start Game
          </button>
          <button onClick={() => setShowRules(true)} style={{ padding: "12px 24px", fontSize: 13 }}>
            Rules
          </button>
        </div>

        <Rulebook open={showRules} onClose={() => setShowRules(false)} />
      </div>
    );
  }

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      {gameState && (
        <GameBoard
          state={gameState}
          actions={actions}
          onAction={sendAction}
          hint={hint}
          onHint={requestHint}
          hasActions={actions.length > 0}
        />
      )}
      {gameOver && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.8)",
          display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 16,
          backdropFilter: "blur(4px)",
        }}>
          <div style={{
            fontSize: 40, fontWeight: "bold", letterSpacing: 4,
            color: gameOver === "Victory!" ? "var(--green)" : "var(--health)",
            textShadow: gameOver === "Victory!" ? "0 0 20px var(--green-glow)" : "0 0 20px var(--health-glow)",
          }}>
            {gameOver}
          </div>
          <div style={{ color: "var(--text-dim)", fontSize: 13, letterSpacing: 1 }}>
            {gameState && `Turn ${gameState.turn}  |  ${gameState.you.health} HP vs ${gameState.opponent.health} HP`}
          </div>
          <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
            <button className="primary" onClick={backToLobby} style={{ padding: "10px 28px", fontSize: 14 }}>
              Back to Lobby
            </button>
          </div>
        </div>
      )}
      {!gameState && (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "100%", color: "var(--text-dim)" }}>
          Connecting...
        </div>
      )}

      {/* Floating buttons */}
      {screen === "playing" && (
        <div style={{ position: "fixed", top: 10, right: 10, display: "flex", gap: 8, zIndex: 50 }}>
          <button onClick={() => setShowRules(true)} style={{ fontSize: 11, padding: "5px 10px", opacity: 0.6 }}>
            Rules
          </button>
        </div>
      )}
      <Rulebook open={showRules} onClose={() => setShowRules(false)} />
    </div>
  );
}

export default App;
