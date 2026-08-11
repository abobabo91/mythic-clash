# Mythic Clash

Browser-based mythological card game. 100 cultures × 20 mythological figures = **2,000 figures** with v1 card packs and legal sample decks. Headless duel engine for testing + rules + web UI (React + Vite). README has phase progress (Phase 4 in progress: competitive tuning + explicit card export + expanded support cards; Phase 5 partial: local play vs bot/LLM works, deckbuilder and polish do not; Phase 6 = card artwork).

## Critical rules

- **Card data is the foundation.** `data/cards-v1/` (100 culture packs), `data/decks-v1/` (legal sample decks), `data/cultures.json`, `data/card-specs-v1.json` — these are the schema-of-truth. NEVER edit a card's stat lines without running the engine self-tests AND a tournament dry-run; small balance changes ripple across decks.
- **The headless duel engine** (`game/engine.py`, `game/rules.py`, `game/players.py`) is the test bed. If a rule change passes manual playtests but breaks the engine self-tests, the rule change is wrong — fix it, don't bypass the engine.
- **NEVER hardcode card data into engine logic.** Engine reads from `data/`; cards reference engine effects by name. Decoupling lets us tune cards without code changes.
- **Wave-based culture builds.** Cultures roll out in waves (`build-wave-N-v1.py` scripts). Don't dump 100 cultures in one merge — wave structure preserves reviewability and balance tuning.

## Stack & run

- Python engine + React/Vite web UI + Python server
- Engine + game logic: `game/` (Python)
- Web UI: `web/` (React + Vite + TypeScript + ESLint)
- HTTP server: `server/app.py`
- Build a new culture pack: `python scripts/build-<culture>-v1.py`
- Analyze figures: `python scripts/analyze-figures.py`
- Tournament analysis: `python scripts/analyze-tournament-deep.py`
- Web UI dev: `cd web && npm install && npm run dev`

## Where things live

- Card schema + translation logic: `game/card_schema.py`, `game/card_translation.py`
- Engine: `game/engine.py` (battle resolution), `game/rules.py` (turn-by-turn logic), `game/players.py` (AI/bot players)
- Server: `server/app.py`
- Web UI source: `web/src/`
- Web build output: `web/dist/`
- Culture packs (THE data): `data/cards-v1/<culture>/`
- Sample decks: `data/decks-v1/<culture>/`
- Cultures list: `data/cultures.json`
- Card-system compatibility: `data/card-system-compatibility.{json,md}`
- Per-culture figures stats: `data/figures-culture-summary.csv`, `data/figures-statistics.md`
- Build scripts: `scripts/build-<culture>-v1.py`
- Analysis scripts: `scripts/analyze-*.py`
- Benchmarks (engine perf, balance): `data/benchmarks/`
- Tests: `tests/`
- Open backlog: `TODO.md`
- Researched competitive-format rationale: `docs/competitive-gameplay-foundation.md`

## Common workflows

**To add a new culture's card pack:**
1. Write `scripts/build-<culture>-v1.py` following the pattern of existing wave-build scripts
2. Output goes to `data/cards-v1/<culture>/`
3. Generate a legal sample deck for `data/decks-v1/<culture>/`
4. Run `python scripts/analyze-figures.py` to verify the new figures fit the statistical envelope
5. Run a tournament dry-run with the new deck to check balance

**To change a game rule:**
1. Update `game/rules.py` (and `game/engine.py` if it touches battle resolution)
2. Run the engine self-tests in `tests/`
3. Run `scripts/analyze-tournament-deep.py` to check the rule's effect on tournament balance
4. Update `docs/competitive-gameplay-foundation.md` if the change affects the format

## Gotchas

- **100 cultures × 20 figures = a LOT of data files.** A naive `git status` can be slow when modifying scripts that touch every culture. Use targeted scripts and verify with the analysis tools.
- **Competitive tuning** is the active phase. Don't ship rule changes that haven't been tournament-tested — the data overhead of having 100 cultures × decks is exactly what enables proper testing.
- Card artwork is **Phase 6** (not started). Don't reference artwork that doesn't exist when building UI components.
- The API/WebSocket URLs in `web/src/App.tsx` are hardcoded to `localhost:8000`, and `server/app.py` never mounts `StaticFiles` — the server does not serve the built UI. Run the Vite dev server alongside it.
