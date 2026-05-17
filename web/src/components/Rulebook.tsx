import "./Rulebook.css";

interface Props {
  open: boolean;
  onClose: () => void;
}

export function Rulebook({ open, onClose }: Props) {
  if (!open) return null;

  return (
    <div className="rulebook-overlay" onClick={onClose}>
      <div className="rulebook-panel" onClick={e => e.stopPropagation()}>
        <button className="rulebook-close" onClick={onClose}>x</button>
        <div className="rulebook-content">
          <h1>Mythic Clash</h1>
          <p className="subtitle">Rules & How to Play</p>

          <section>
            <h2>Goal</h2>
            <p>Reduce the opposing hero from <strong>30 Health</strong> to 0. If your deck runs out, you take escalating <em>fatigue damage</em> each draw (1, 2, 3...).</p>
          </section>

          <section>
            <h2>Setup</h2>
            <ul>
              <li>Each player picks a <strong>culture</strong> with unique heroes, figures, spells, and relics.</li>
              <li>Player 1 draws <strong>4 cards</strong>.</li>
              <li>Player 2 draws <strong>5 cards</strong>, gets <strong>The Coin</strong> (free +1 mana), and starts with <strong>1 Ritual Mana</strong>.</li>
              <li>Each player may <strong>mulligan</strong> (redraw any cards once).</li>
            </ul>
          </section>

          <section>
            <h2>Turn Flow</h2>
            <ol>
              <li><strong>Start of turn</strong> — Gain +1 max mana (up to 10), refill mana, draw 1 card, ready your figures.</li>
              <li><strong>Main phase</strong> — Play cards, attack, use hero power, activate relics, cast spells. Do actions in any order.</li>
              <li><strong>End turn</strong> — Unused mana converts to <strong>Ritual Mana</strong> (max 2). Pass to opponent.</li>
            </ol>
          </section>

          <section>
            <h2>Card Types</h2>
            <div className="card-types">
              <div className="ct">
                <div className="ct-icon">&#9876;</div>
                <h3>Figures</h3>
                <p>Creatures with Attack and Health. They fight on the board. New figures enter <strong>sleeping</strong> (can't attack this turn) unless they have Rush or Charge.</p>
              </div>
              <div className="ct">
                <div className="ct-icon">&#10022;</div>
                <h3>Spells</h3>
                <p>One-time effects: damage, heals, buffs, draws. Each spell has a <strong>speed</strong>:</p>
                <ul>
                  <li><strong>Slow</strong> — Your turn only, main phase.</li>
                  <li><strong>Fast</strong> — Also usable in response windows.</li>
                  <li><strong>Burst</strong> — Resolves instantly, no response allowed.</li>
                </ul>
              </div>
              <div className="ct">
                <div className="ct-icon">&#9830;</div>
                <h3>Relics</h3>
                <p>Permanent artifacts. Some have <strong>passive</strong> effects (trigger automatically), others have <strong>activated</strong> abilities (cost mana to use, once per turn).</p>
              </div>
            </div>
          </section>

          <section>
            <h2>Combat</h2>
            <ul>
              <li>Click a ready figure, then click a target (enemy figure or hero).</li>
              <li>Combat damage is <strong>simultaneous</strong> — both attacker and defender deal their Attack to each other.</li>
              <li>Figures with <strong>Guard</strong> must be attacked before other targets.</li>
              <li>Damage <strong>persists</strong> — figures don't heal between turns unless healed by a card.</li>
            </ul>
          </section>

          <section>
            <h2>Response Windows</h2>
            <p>When a figure declares an attack, the <strong>defending player</strong> gets a chance to respond before combat resolves:</p>
            <ul>
              <li>Play <strong>Fast</strong> or <strong>Burst</strong> spells to change the outcome.</li>
              <li>Buff your defender, damage the attacker, freeze, heal, etc.</li>
              <li>Players alternate responses until both pass, then combat resolves.</li>
            </ul>
          </section>

          <section>
            <h2>Mana & Ritual Mana</h2>
            <ul>
              <li>You gain +1 mana crystal each turn, up to <strong>10</strong>.</li>
              <li>Unspent mana converts to <strong>Ritual Mana</strong> (max 2) at end of turn.</li>
              <li>Ritual Mana can only be spent on <strong>spells</strong> and <strong>hero power</strong>.</li>
              <li>Holding mana open threatens responses — even if you don't have a trick, the opponent doesn't know that.</li>
            </ul>
          </section>

          <section>
            <h2>Keywords</h2>
            <div className="keywords-grid">
              <div><strong>Guard</strong> — Enemies must attack this first.</div>
              <div><strong>Rush</strong> — Can attack figures (not heroes) immediately.</div>
              <div><strong>Charge</strong> — Can attack anything immediately.</div>
              <div><strong>Divine Shield</strong> — Ignores the first damage taken.</div>
              <div><strong>Poisonous</strong> — Any damage dealt to a figure destroys it.</div>
              <div><strong>Reborn</strong> — First death returns this at 1 Health.</div>
              <div><strong>Lifesteal</strong> — Damage dealt also heals your hero.</div>
              <div><strong>Overwhelm</strong> — Excess damage to a figure spills to the enemy hero.</div>
              <div><strong>Stealth</strong> — Can't be targeted until it attacks.</div>
              <div><strong>Freeze</strong> — Target skips its next ready phase.</div>
            </div>
          </section>

          <section>
            <h2>Survival Mechanics</h2>
            <ul>
              <li><strong>Survival Instinct</strong> (15 HP or less) — Draw 1 extra card each turn. At 5 HP or less, draw 2 extra.</li>
              <li><strong>Last Stand</strong> (10 HP or less) — Your figures enter play <strong>Ready</strong> (no sleeping). Play a Guard and it blocks immediately.</li>
            </ul>
          </section>

          <section>
            <h2>Tips</h2>
            <ul>
              <li><strong>Trade or Face?</strong> — Sometimes clearing their board is best, sometimes racing to kill their hero is better. Assess who dies first at current damage rates.</li>
              <li><strong>Hold mana</strong> — Banking 2 mana threatens a combat trick. Your opponent might not attack into open mana.</li>
              <li><strong>Don't overextend</strong> — If your opponent might have AoE (board clear), keep some figures in hand as backup.</li>
              <li><strong>Count lethal</strong> — Always check if your board + spells can kill the enemy hero this turn.</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
