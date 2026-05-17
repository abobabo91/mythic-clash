"""Deep game-by-game analysis of LLM-vs-LLM tournament results."""
import json
import sys
from pathlib import Path
from collections import Counter

def main():
    jsonl_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("outputs/llm-tournament.jsonl")
    lines = jsonl_path.read_text(encoding="utf-8").strip().splitlines()
    games = [json.loads(line) for line in lines]

    out = []

    def p(s=""):
        out.append(s)

    p(f"{'='*80}")
    p(f"DEEP GAME-BY-GAME ANALYSIS — {len(games)} LLM-vs-LLM games")
    p(f"{'='*80}")
    p()

    for i, g in enumerate(games):
        slug_a = g["slug_a"]
        slug_b = g["slug_b"]
        wi = g.get("winner_index")
        turns = g["turns"]
        hp_a = g["health_a"]
        hp_b = g["health_b"]
        history = g.get("history", [])
        logs_a = g.get("llm_logs_a", [])
        logs_b = g.get("llm_logs_b", [])

        winner_hp = hp_a if wi == 0 else hp_b
        loser_hp = hp_b if wi == 0 else hp_a
        margin = "BLOWOUT" if winner_hp >= 25 else ("CLOSE" if winner_hp <= 10 else "NORMAL")
        winner_slug = slug_a if wi == 0 else slug_b
        loser_slug = slug_b if wi == 0 else slug_a

        # Cards played count
        plays_a = sum(1 for e in history if "Player A plays" in e or "Player A casts" in e)
        plays_b = sum(1 for e in history if "Player B plays" in e or "Player B casts" in e)
        deaths = sum(1 for e in history if e.endswith(" dies."))
        fatigue_events = sum(1 for e in history if "fatigue" in e.lower())

        # Hero power uses
        hp_uses_a = sum(1 for l in logs_a if "hero_power" in l.get("action_id", ""))
        hp_uses_b = sum(1 for l in logs_b if "hero_power" in l.get("action_id", ""))

        # Passes
        passes_a = sum(1 for l in logs_a if l.get("action_id") == "pass")
        passes_b = sum(1 for l in logs_b if l.get("action_id") == "pass")

        # First real play turn
        def first_real_play(logs):
            for l in logs:
                aid = l.get("action_id", "")
                if aid != "pass" and "hero_power" not in aid:
                    return l.get("turn", 99)
            return 99
        fp_a = first_real_play(logs_a)
        fp_b = first_real_play(logs_b)

        # Cards played (names)
        def extract_cards(player_label):
            cards = []
            for e in history:
                if f"{player_label} plays " in e:
                    card = e.split(f"{player_label} plays ", 1)[1].rstrip(".").split(" and draws")[0].split(" from ")[0]
                    cards.append(card)
                elif f"{player_label} casts " in e:
                    card = e.split(f"{player_label} casts ", 1)[1].rstrip(".").split(" and draws")[0]
                    cards.append(card)
            return cards

        cards_a = extract_cards("Player A")
        cards_b = extract_cards("Player B")

        # Key reasoning
        winner_logs = logs_a if wi == 0 else logs_b
        loser_logs = logs_b if wi == 0 else logs_a

        def get_first_reasoning(logs):
            for l in logs:
                if l.get("action_id", "") not in ("pass",):
                    return l.get("reasoning", "")[:200]
            return ""

        def get_last_reasoning(logs):
            for l in reversed(logs):
                r = l.get("reasoning", "")
                if r:
                    return f"T{l.get('turn','?')}: {r[:200]}"
            return ""

        # Death cause
        death_cause = ""
        for e in reversed(history[-8:]):
            e_lower = e.lower()
            if "fatigue" in e_lower or ("deals" in e_lower and "player" in e_lower) or ("attacks" in e_lower and "hero" in e_lower):
                death_cause = e[:120]
                break

        winner_fp = fp_a if wi == 0 else fp_b
        loser_fp = fp_b if wi == 0 else fp_a
        tempo_gap = loser_fp - winner_fp

        coins_a = sum(1 for c in cards_a if c == "The Coin")
        coins_b = sum(1 for c in cards_b if c == "The Coin")

        relics_a = sum(1 for c in cards_a if "relic" in c.lower())
        relics_b = sum(1 for c in cards_b if "relic" in c.lower())

        unique_a = len(set(c for c in cards_a if c != "The Coin"))
        unique_b = len(set(c for c in cards_b if c != "The Coin"))

        w_plays = plays_a if wi == 0 else plays_b
        l_plays = plays_b if wi == 0 else plays_a
        w_passes = passes_a if wi == 0 else passes_b
        l_passes = passes_b if wi == 0 else passes_a
        w_hp_uses = hp_uses_a if wi == 0 else hp_uses_b
        l_hp_uses = hp_uses_b if wi == 0 else hp_uses_a
        w_coins = coins_a if wi == 0 else coins_b
        l_coins = coins_b if wi == 0 else coins_a
        w_relics = relics_a if wi == 0 else relics_b
        l_relics = relics_b if wi == 0 else relics_a
        w_unique = unique_a if wi == 0 else unique_b
        l_unique = unique_b if wi == 0 else unique_a

        p(f"G{i+1:02d} [{margin:>7s}] {winner_slug} ({winner_hp}hp) beat {loser_slug} ({loser_hp}hp) T{turns}")
        p(f"    Plays: W={w_plays} L={l_plays} | Deaths:{deaths} | Fatigue:{fatigue_events}")
        p(f"    First play: W=T{winner_fp} L=T{loser_fp} (gap={tempo_gap:+d}) | Passes: W={w_passes} L={l_passes}")
        p(f"    Hero power: W={w_hp_uses} L={l_hp_uses} | Coins: W={w_coins} L={l_coins} | Relics: W={w_relics} L={l_relics}")
        p(f"    Unique cards: W={w_unique} L={l_unique}")
        p(f"    Kill: {death_cause}")
        p(f"    W early: {get_first_reasoning(winner_logs)}")
        p(f"    L early: {get_first_reasoning(loser_logs)}")
        p(f"    W final: {get_last_reasoning(winner_logs)}")
        p()

    # === AGGREGATE PATTERNS ===
    p(f"{'='*80}")
    p("AGGREGATE PATTERN ANALYSIS")
    p(f"{'='*80}")
    p()

    blowouts = [g for g in games if (g["health_a"] if g.get("winner_index") == 0 else g["health_b"]) >= 25]
    normals = [g for g in games if 10 < (g["health_a"] if g.get("winner_index") == 0 else g["health_b"]) < 25]
    close_games = [g for g in games if (g["health_a"] if g.get("winner_index") == 0 else g["health_b"]) <= 10]

    p(f"Distribution: {len(blowouts)} blowouts, {len(normals)} normal, {len(close_games)} close")
    p()

    # Tempo analysis
    def avg_first_play_turn(game_list, is_winner):
        fps = []
        for g in game_list:
            wi = g.get("winner_index")
            key = "llm_logs_a" if (wi == 0) == is_winner else "llm_logs_b"
            logs = g.get(key, [])
            for l in logs:
                aid = l.get("action_id", "")
                if aid != "pass" and "hero_power" not in aid:
                    fps.append(l.get("turn", 99))
                    break
        return sum(fps) / len(fps) if fps else 0

    p("--- TEMPO: Avg first-play turn ---")
    p(f"  Blowout winners: T{avg_first_play_turn(blowouts, True):.1f}")
    p(f"  Blowout losers:  T{avg_first_play_turn(blowouts, False):.1f}")
    p(f"  Normal winners:  T{avg_first_play_turn(normals, True):.1f}")
    p(f"  Normal losers:   T{avg_first_play_turn(normals, False):.1f}")
    p(f"  Close winners:   T{avg_first_play_turn(close_games, True):.1f}")
    p(f"  Close losers:    T{avg_first_play_turn(close_games, False):.1f}")
    p()

    # Pass rate
    def avg_passes(game_list, is_winner):
        total = 0
        for g in game_list:
            wi = g.get("winner_index")
            key = "llm_logs_a" if (wi == 0) == is_winner else "llm_logs_b"
            logs = g.get(key, [])
            total += sum(1 for l in logs if l.get("action_id") == "pass")
        return total / len(game_list) if game_list else 0

    p("--- PASS RATE (avg per game) ---")
    p(f"  Blowout winners: {avg_passes(blowouts, True):.1f}")
    p(f"  Blowout losers:  {avg_passes(blowouts, False):.1f}")
    p(f"  Normal winners:  {avg_passes(normals, True):.1f}")
    p(f"  Normal losers:   {avg_passes(normals, False):.1f}")
    p(f"  Close winners:   {avg_passes(close_games, True):.1f}")
    p(f"  Close losers:    {avg_passes(close_games, False):.1f}")
    p()

    # Fatigue
    def avg_fatigue(game_list):
        return sum(sum(1 for e in g.get("history", []) if "fatigue" in e.lower()) for g in game_list) / len(game_list) if game_list else 0

    p("--- FATIGUE (avg events per game) ---")
    p(f"  Blowouts: {avg_fatigue(blowouts):.1f}")
    p(f"  Normal:   {avg_fatigue(normals):.1f}")
    p(f"  Close:    {avg_fatigue(close_games):.1f}")
    p()

    # Death cause
    kill_by_type = Counter()
    for g in games:
        for e in reversed(g.get("history", [])[-8:]):
            el = e.lower()
            if "fatigue" in el:
                kill_by_type["fatigue"] += 1
                break
            elif "deals" in el and "player" in el:
                kill_by_type["spell/ability"] += 1
                break
            elif "attacks" in el and "hero" in el:
                kill_by_type["minion_attack"] += 1
                break
        else:
            kill_by_type["unknown"] += 1

    p("--- CAUSE OF DEATH ---")
    for cause, count in sorted(kill_by_type.items(), key=lambda x: -x[1]):
        p(f"  {cause}: {count} ({count*100//len(games)}%)")
    p()

    # Hero power
    def avg_hp_uses(game_list, is_winner):
        total = 0
        for g in game_list:
            wi = g.get("winner_index")
            key = "llm_logs_a" if (wi == 0) == is_winner else "llm_logs_b"
            total += sum(1 for l in g.get(key, []) if "hero_power" in l.get("action_id", ""))
        return total / len(game_list) if game_list else 0

    p("--- HERO POWER USAGE (avg per game) ---")
    p(f"  Winners: {avg_hp_uses(games, True):.1f}")
    p(f"  Losers:  {avg_hp_uses(games, False):.1f}")
    p()

    # Cards played
    def avg_cards_played(game_list, is_winner):
        total = 0
        for g in game_list:
            wi = g.get("winner_index")
            label = "Player A" if (wi == 0) == is_winner else "Player B"
            total += sum(1 for e in g.get("history", []) if f"{label} plays" in e or f"{label} casts" in e)
        return total / len(game_list) if game_list else 0

    p("--- CARDS PLAYED (avg per game) ---")
    p(f"  Winners: {avg_cards_played(games, True):.1f}")
    p(f"  Losers:  {avg_cards_played(games, False):.1f}")
    p()

    # Board at end
    def avg_board(game_list, is_winner):
        total = 0
        for g in game_list:
            wi = g.get("winner_index")
            total += g["board_a"] if (wi == 0) == is_winner else g["board_b"]
        return total / len(game_list) if game_list else 0

    p("--- FINAL BOARD SIZE ---")
    p(f"  Winners: {avg_board(games, True):.1f}")
    p(f"  Losers:  {avg_board(games, False):.1f}")
    p()

    # Turn 1-3 analysis: what happens early?
    p("--- EARLY GAME (T1-T3) ACTIONS ---")
    early_plays = 0
    early_passes = 0
    early_coins = 0
    early_hero_power = 0
    for g in games:
        for key in ["llm_logs_a", "llm_logs_b"]:
            for l in g.get(key, []):
                t = l.get("turn", 99)
                if t > 3:
                    break
                aid = l.get("action_id", "")
                if aid == "pass":
                    early_passes += 1
                elif "hero_power" in aid:
                    early_hero_power += 1
                else:
                    # Check if it's coin
                    r = l.get("reasoning", "").lower()
                    early_plays += 1

    total_early = early_plays + early_passes + early_hero_power
    p(f"  Plays: {early_plays} ({early_plays*100//total_early}%)")
    p(f"  Passes: {early_passes} ({early_passes*100//total_early}%)")
    p(f"  Hero powers: {early_hero_power} ({early_hero_power*100//total_early}%)")
    p()

    # Mana curve — track what turn cards are played
    p("--- MANA CURVE: plays per turn ---")
    plays_per_turn = Counter()
    for g in games:
        for key in ["llm_logs_a", "llm_logs_b"]:
            for l in g.get(key, []):
                aid = l.get("action_id", "")
                if aid.startswith("play:") or aid.startswith("spell:") or aid.startswith("relic:"):
                    plays_per_turn[l.get("turn", 0)] += 1

    for t in range(1, 21):
        count = plays_per_turn.get(t, 0)
        bar = "#" * (count // 4)
        p(f"  T{t:>2d}: {count:>4d} {bar}")
    p()

    # Blowout root causes
    p("--- BLOWOUT ROOT CAUSE ANALYSIS ---")
    tempo_caused = 0
    card_advantage = 0
    fatigue_kill = 0
    for g in blowouts:
        wi = g.get("winner_index")
        w_logs = g.get(f"llm_logs_{'a' if wi==0 else 'b'}", [])
        l_logs = g.get(f"llm_logs_{'b' if wi==0 else 'a'}", [])

        # Check if tempo gap
        def fp(logs):
            for l in logs:
                aid = l.get("action_id", "")
                if aid != "pass" and "hero_power" not in aid:
                    return l.get("turn", 99)
            return 99

        w_fp = fp(w_logs)
        l_fp = fp(l_logs)

        if w_fp < l_fp:
            tempo_caused += 1

        # Card advantage
        w_cards = sum(1 for l in w_logs if l.get("action_id", "").startswith("play") or l.get("action_id", "").startswith("spell"))
        l_cards = sum(1 for l in l_logs if l.get("action_id", "").startswith("play") or l.get("action_id", "").startswith("spell"))
        if w_cards > l_cards + 3:
            card_advantage += 1

        # Fatigue kill
        h = g.get("history", [])
        if any("fatigue" in e.lower() for e in h[-5:]):
            fatigue_kill += 1

    p(f"  Out of {len(blowouts)} blowouts:")
    p(f"    Tempo advantage (winner played first): {tempo_caused}")
    p(f"    Card advantage (winner played 3+ more): {card_advantage}")
    p(f"    Fatigue kill: {fatigue_kill}")
    p()

    # Relic impact
    p("--- RELIC ANALYSIS ---")
    relic_games = 0
    relic_winner_advantage = 0
    for g in games:
        wi = g.get("winner_index")
        h = g.get("history", [])
        w_relics = sum(1 for e in h if f"Player {'A' if wi==0 else 'B'} plays relic" in e.lower())
        l_relics = sum(1 for e in h if f"Player {'B' if wi==0 else 'A'} plays relic" in e.lower())
        if w_relics > 0 or l_relics > 0:
            relic_games += 1
        if w_relics > l_relics:
            relic_winner_advantage += 1

    p(f"  Games with relics: {relic_games}/{len(games)}")
    p(f"  Winner played more relics: {relic_winner_advantage}")
    p()

    # Keyword frequency in played cards
    p("--- KEYWORD USAGE (from game events) ---")
    kw_counter = Counter()
    for g in games:
        for e in g.get("history", []):
            el = e.lower()
            for kw in ["divine shield", "taunt", "guard", "rush", "charge", "poisonous", "lifesteal", "reborn", "stealth", "ward"]:
                if kw in el:
                    kw_counter[kw] += 1

    for kw, count in sorted(kw_counter.items(), key=lambda x: -x[1]):
        p(f"  {kw}: {count}")
    p()

    result = "\n".join(out)
    Path("outputs/game-analysis.txt").write_text(result, encoding="utf-8")
    print(result)


if __name__ == "__main__":
    main()
