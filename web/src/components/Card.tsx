import { CardInfo, MinionInfo } from "../types";
import "./Card.css";

interface HandCardProps {
  card: CardInfo;
  playable: boolean;
  selected: boolean;
  onClick: () => void;
}

export function HandCard({ card, playable, selected, onClick }: HandCardProps) {
  const typeClass = card.card_type === "spell" ? "spell" : card.card_type === "relic" ? "relic" : "minion";

  // Pick an icon for the art placeholder based on type
  const artIcon = card.card_type === "spell" ? "\u2727" : card.card_type === "relic" ? "\u2666" : "\u2694";

  return (
    <div
      className={`hand-card ${typeClass} ${playable ? "playable" : ""} ${selected ? "selected" : ""}`}
      onClick={playable ? onClick : undefined}
      title={card.text}
    >
      <div className="card-cost">{card.cost}</div>
      <div className="card-art">{artIcon}</div>
      <div className="card-name">{card.name}</div>
      {card.card_type === "spell" && (
        <div className="card-speed">{card.speed}</div>
      )}
      {card.keywords.length > 0 && (
        <div className="card-keywords">{card.keywords.join(" ")}</div>
      )}
      <div className="card-text">{card.text}</div>
      {card.card_type === "minion" && (
        <div className="card-stats">
          <span className="atk">{card.attack}</span>
          <span className="sep">/</span>
          <span className="hp">{card.health}</span>
        </div>
      )}
    </div>
  );
}

interface BoardMinionProps {
  minion: MinionInfo;
  friendly: boolean;
  canAttack: boolean;
  selected: boolean;
  targetable: boolean;
  onClick: () => void;
}

export function BoardMinion({ minion, friendly, canAttack, selected, targetable, onClick }: BoardMinionProps) {
  const kw = minion.keywords;
  return (
    <div
      className={`board-minion ${friendly ? "friendly" : "enemy"} ${canAttack ? "can-attack" : ""} ${selected ? "selected" : ""} ${targetable ? "targetable" : ""} ${minion.sleeping ? "sleeping" : ""} ${kw.includes("guard") || kw.includes("taunt") ? "has-guard" : ""}`}
      onClick={onClick}
      title={minion.text}
    >
      <div className="card-name">{minion.name}</div>
      <div className="card-stats">
        <span className="atk">{minion.attack}</span>
        <span className="sep">/</span>
        <span className={`hp ${minion.health < minion.max_health ? "damaged" : ""}`}>{minion.health}</span>
      </div>
      {kw.length > 0 && <div className="card-keywords">{kw.map(k => k[0].toUpperCase()).join("")}</div>}
      {minion.divine_shield && <div className="shield-badge">W</div>}
      {minion.reborn && <div className="reborn-badge">R</div>}
    </div>
  );
}
