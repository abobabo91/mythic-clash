# Mythic Clash

A Hearthstone-like duel card game built from world mythology: **100 cultures × 20 mythological figures = 2,000 figures**, translated into playable card packs, plus a headless Python duel engine, bot and LLM self-play, and a local browser UI.

**Status: unfinished, actively open.** The data layer and the engine are done and tested; the game is playable locally against a bot or an LLM. What is *not* done is the competitive balance pass, the evergreen support-card set, the deckbuilder, artwork, and anything resembling deployment. See [What's not finished](#whats-not-finished) — it is the most useful section of this README.

---

## What works today

| Piece | State |
|---|---|
| Culture dataset | 100 cultures with region, period, mythology type, themes — `data/cultures.json` |
| Figure dataset | 2,000 figures, 20 per culture — `data/figures/` |
| Card packs | 102 `v1` packs — 100 cultures + `neutral-core-v1` + `domain-support-v1` — `data/cards-v1/` |
| Sample decks | 117 legal decks — `data/decks-v1/` |
| Duel engine | ~2,200 lines, headless, deterministic under a seed — `game/engine.py` |
| Tests | 45 tests, all passing (`python -m pytest tests/`) |
| Bots | Heuristic, rollout, and a cheap benchmark/smoke bot — `game/players.py` |
| LLM self-play | Anthropic / OpenAI / Gemini players, keys read from env vars only |
| Benchmarks | 189 smoke-test and matchup reports — `data/benchmarks/` |
| Web UI | React + Vite lobby → pick two cultures → play vs bot or LLM over a WebSocket |
| Server | FastAPI: `GET /api/cultures`, `WS /ws/game` — `server/app.py` |

Rollout coverage: all 100 cultures have a `v1` pack, a legal sample deck, and rollout-tier gameplay testing. 35 of them ("spotlight cultures") also have curated playtest write-ups — see [docs/culture-testing-status.md](docs/culture-testing-status.md).

## What's not finished

This is a side project in the middle of its balance phase, not a shippable game. The full backlog lives in [TODO.md](TODO.md) (last swept 2026-05-04); these are the things most likely to bite you:

**Gameplay design decisions still open**
- Final deck size, copy limits, and sideboard policy for competitive play are undecided.
- The one-per-culture special card slot has no agreed name (`Signature Character` / `Icon` / `Paragon`) and no design limits on how far it may bend the rules.
- No formal burst / lethality budget, so some matchups still end in high-roll blowouts from cheap damage spikes rather than board play.
- No pack-level comeback requirements, and no explicit rarity/role targets guaranteeing each deck has early plays, midgame anchors, and finishers.
- Several cultures still lack `4`–`6` lower-profile early-game cards, so launch decks lean on headline mythic names.
- `Ancient Greek` acts as the de-facto pressure gate; which of the Greek-soft cultures are acceptable specialists vs. genuinely under-tooled is not decided.

**Card system**
- Generated support spells have not been reworked into a clean evergreen base set; the `Neutral Core` and `Domain support` packages are first-wave drafts.
- Card behaviour still leans on broad text-to-effect heuristics instead of explicit card-text templates.
- No schema validation or data linting for cultures/figures (duplicate IDs, malformed stats, missing fields go undetected).
- Raw figure data and derived gameplay card data are not cleanly separated.

**Engine & AI**
- `AgenticLLMPlayer` is a placeholder — it is literally `class AgenticLLMPlayer(ThinkingLLMPlayer): pass`. Only `ThinkingLLMPlayer` / `PromptLLMPlayer` do real work.
- `MODEL_PRESETS` in `game/players.py` pins model IDs that have since moved on; refresh them before trusting an LLM benchmark run.
- Second-player compensation has no real mulligan model and has not been measured.

**UI & product**
- No deckbuilder. The lobby picks a culture; you play its prebuilt sample deck.
- No card artwork at all (Phase 6, not started) — cards render as text.
- No online multiplayer. `WS /ws/game` runs one human against a local bot or LLM; the 2v2 / XvX vocabulary in [docs/multiplayer-compatibility.md](docs/multiplayer-compatibility.md) is design-only.
- Priority/response markers, action log, and attack-readiness indicators are not surfaced as first-class readability features.

**Plumbing**
- No `requirements.txt` / `pyproject.toml`, no Dockerfile, no CI. Install deps by hand (below).
- The API and WebSocket URLs are hardcoded to `localhost:8000` in `web/src/App.tsx`, so the UI cannot be deployed as-is.
- `server/app.py` imports `StaticFiles` but never mounts it — the server does not serve the built web UI, so you need the Vite dev server running alongside it.
- No `LICENSE` file yet. Pick one before accepting contributions.

## Run it

Python 3.11+ and Node 18+.

```bash
# engine tests — no third-party deps beyond pytest
python -m pytest tests/

# server
pip install fastapi uvicorn
python server/app.py            # http://localhost:8000

# web UI, in a second shell
cd web && npm install && npm run dev
```

LLM self-play is optional and lazily imported — install only the provider you want and export its key:

```bash
pip install anthropic          # ANTHROPIC_API_KEY
pip install openai             # OPENAI_API_KEY
pip install google-genai       # GEMINI_API_KEY
```

No key is ever read from a file or committed; every provider path reads `os.environ` and raises if the variable is missing.

## Repo layout

```
data/cultures.json      100 cultures: region, period, mythology type, themes
data/figures/           100 files × 20 figures
data/cards-v1/          exported v1 card packs (+ neutral core, domain support)
data/decks-v1/          legal sample decks
data/benchmarks/        smoke tests, matchup reports, rollout summaries
game/                   card schema, figure→card translation, engine, rules, players
server/app.py           FastAPI: culture list + game WebSocket
web/                    React + Vite UI
scripts/                41 build / analysis / validation scripts
tests/                  engine tests
docs/                   design, rules, rollout and playtest notes
```

## Phases

- [x] Phase 1 — Cultures dataset (100 cultures)
- [x] Phase 2 — Figures dataset (2,000 figures)
- [x] Phase 3 — Headless duel prototype & rules
- [~] Phase 4 — Competitive tuning, explicit card export, expanded support cards
- [~] Phase 5 — Playable UI (local play vs bot/LLM works; deckbuilder and polish do not)
- [ ] Phase 6 — Card artwork

## Key docs

- [TODO.md](TODO.md) — the real backlog
- [docs/exact-rules-v1.md](docs/exact-rules-v1.md) — target ruleset
- [docs/card-system-v1.md](docs/card-system-v1.md) — card architecture and rules primitives
- [docs/competitive-gameplay-foundation.md](docs/competitive-gameplay-foundation.md) — why the format is shaped this way
- [docs/culture-identity-matrix.md](docs/culture-identity-matrix.md) — culture gameplay families and signature-character framework
- [docs/culture-testing-status.md](docs/culture-testing-status.md) — per-culture rollout and testing status
- [docs/playtest-bulk-rollout-v1.md](docs/playtest-bulk-rollout-v1.md) — bulk rollout results
- [docs/multiplayer-compatibility.md](docs/multiplayer-compatibility.md) — future 2v2 / XvX constraints

## Cultures coverage

| Region | Count |
|--------|-------|
| Americas | 22 |
| Europe | 13 |
| Africa | 10 |
| Middle East | 10 |
| South Asia | 10 |
| Oceania | 8 |
| East Asia | 7 |
| Southeast Asia | 7 |
| Central Asia | 6 |
| Caribbean | 4 |
| Caucasus | 3 |
