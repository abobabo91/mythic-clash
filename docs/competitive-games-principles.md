# Designing competitive games that stay fun

Working principles for competitive game design, distilled from sports psychology, HCI, game-studies research, and designer commentary. Compiled to inform this game and format-agnostic on purpose: it says what makes *any* competitive game stay fun, without assuming cards.

Read alongside:
- [`competitive-gameplay-foundation.md`](competitive-gameplay-foundation.md) — the same question answered for the specific card-game format, from what Magic / Hearthstone / Runeterra / Snap actually do.
- [`knowledge-base-comparison-notes.md`](knowledge-base-comparison-notes.md) — where Mythic Clash's current design meets or misses the principles below.

## The one-sentence rule

A competitive game stays fun when it keeps both players and spectators in a state of **informed uncertainty** — they know enough to care, plan, and feel responsible for the outcome, while still not knowing exactly what happens next.

## What makes competition feel good

Three pillars carry most of the literature:

1. **Sense of competence and autonomy.** Players need the contest to communicate "your choices mattered" rather than "the system did this to you." This is self-determination-theory work applied to games: enjoyable competition preserves meaningful choice and avoids humiliating loss conditions. Practical consequence: small decisions need to ripple visibly through the game state.

2. **Challenge–skill fit (flow).** The match should feel winnable enough to keep attention high but difficult enough that improvement keeps mattering over hundreds of plays. Too easy → boredom; too hard → resignation. Onboarding should put the player on the *learnable* side of this gradient, not protect them from it.

3. **Suspense + surprise.** Audience studies (notably a minute-by-minute tennis viewership study) show both significantly raise engagement. Outcome uncertainty alone is not enough — the game also needs **interpretable resolution moments** where uncertainty is about to break either way.

## The levers you actually control

### Legibility is an excitement multiplier

When players can answer "How am I doing?" and "What can I do next?" without reconstructing the state from memory, attention flows into strategy and tension. Visible status, recognition over recall, and minimal cognitive bookkeeping are usability principles that double as fun principles. Tabletop usability research (NN/g, Board Game Geek discussions) consistently flags this as a top-tier excitement killer when violated.

This does NOT mean every game should be fully open-information. Hidden information from *other players* creates good tension. Hiding *the player's own actionable state* is just friction.

### Productive hiddenness vs trackable hidden info

The community calls the bad version **"trackable hidden information"** — the game pretends something is unknown when a player with a notebook could reconstruct it. Players hate this; it converts strategy into clerical work. Make hidden information either genuinely uncertain or stop hiding it.

### Downtime is the #1 reported fun killer

Three fixes recur across designer forums:
- Give players meaningful **reactions** on opponents' turns
- Allow **indirect participation** (piggybacking, discussion, side bets)
- Design turns so they can be **pre-planned** rather than flooded with new information at decision time

Or sidestep the whole problem with simultaneous resolution where it fits.

### Skill–luck balance across time horizons

Single matches can be unpredictable while better players still win over enough repeated play. Poker is the textbook example: persistent performance differences rule out pure chance, but per-hand variance keeps each round alive. The design lever: keep variance *bounded and reasoned-about*, not unbounded.

### Pacing via resource systems

Mana curves (and analogs in other genres) are powerful because they:
- Naturally create pacing — different card costs matter at different game phases
- Function as a soft catch-up — both players always have draws that are situationally optimal/suboptimal
- Make later turns feel different from earlier ones without changing the rules

When the resource system is misunderstood by new players, it produces "non-games" (e.g. mana screw in Magic). Worth designing in safety valves.

### Micro-climaxes are the unit of suspense

Suspense doesn't fill a match evenly — it spikes at decision/resolution moments and decays between them. Examples:
- **Darts:** the checkout (player can finish from current score → public, legible, narratively charged)
- **Tennis:** break point, tiebreak
- **Card games:** the all-in, the lethal setup, the key topdeck window
- **Fighting games:** punish window, knockdown, corner escape

Even real-time games benefit from states that *feel like turns* — implicit decision points where the state is about to flip. The Street Fighter "frame advantage" concept is exactly this: real-time on the surface, turn-like at the advantage-state level.

**Practical:** if your game has long flat stretches between micro-climaxes, you don't have a balance problem, you have a pacing problem.

## Easy to learn, hard to master (carefully)

The cliché is right but commonly misapplied. Three things to keep straight:

- **Skill floor ≠ skill ceiling.** Lower the floor with teaching, defaults, and onboarding. Don't lower the ceiling — that just makes the game thinner. Fighting games (Modern controls in SF6, Fantasy Strike's design philosophy) demonstrate that simplified inputs preserve depth if the strategic layer is intact.
- **Emergence beats bulk complexity.** Simple rule sets that interact richly (chess, Go) sustain mastery longer than complex rule piles. Designer columns at *Magic* call this **lenticular design**: the same card looks simple to a novice and layered to an expert.
- **"Hard to learn" is usually a rulebook problem, not a depth problem.** Many games that newcomers bounce off aren't strategically deep — they have too many exceptions, subsystems, or icons. Logical rules > numerous rules.

## Bad practices that recur

- **Analysis paralysis + low interactivity.** One slow player + no off-turn engagement = the room drains.
- **Trackable hidden info.** Make players take notes to recover what the game is hiding. Felt fake.
- **Early hopelessness.** Runaway leaders, runaway losers, player elimination — all kill suspense. Soft comebacks (boosts to trailing players, more variance late, comeback lines) beat punishing the leader.
- **Catch-up that feels like theft.** If the leader is *visibly* robbed rather than challenged, players resent it even when scores stay close. Boost the loser, don't taze the winner.
- **Execution barriers that gate the actual contest.** Demanding inputs can be part of identity (fighting-game community defends this), but only when they're core to the genre. Otherwise they just stop players reaching the read-and-counter layer.
- **Spectator opacity.** If interested watchers can't follow what matters, the game can't grow. MOBA-spectatorship research calls this "assumed-knowledge debt."
- **Reliability & service failures.** In computer games, bugs / latency / broken matchmaking dominate sentiment even when the underlying design is good.

## Where the principles cash out in card games specifically

Card games stack pre-game strategy (deck construction), in-game tactics (sequencing, bluffing, matchup knowledge), and bounded variance (hand draws) in a way that produces unusual depth-per-rule-count. The same stacking turns hostile when:
- Iconography is unreadable
- Timing windows are ambiguous
- Hidden information is trackable (counted-out decks, fixed mana sequences)
- Resource pacing has no safety valve

This is the principle layer that informs the mythic-clash competitive format. See `mythic-clash/docs/competitive-gameplay-foundation.md` for the specific application — culture-pack balance, card-system compatibility, deck-archetype space, and what we tune for in tournament dry-runs.

## When in doubt

Run a tournament dry-run with the change in place. The data overhead of having 100 cultures × decks exists precisely so balance changes can be measured rather than guessed. The principles above explain *why* a specific change is likely to help or hurt; the dry-run tells you *whether* it actually did.
