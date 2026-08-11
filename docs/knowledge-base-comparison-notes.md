# Mythic Clash vs Competitive Games Knowledge Base

Status: design comparison against [`competitive-games-principles.md`](competitive-games-principles.md)

This note compares the broader competitive-game design research against the current Mythic Clash direction.

The goal is not to restate what we already believe.

The goal is to find the changes that would genuinely improve Mythic Clash before mass culture rollout and before deeper engine work.

## Where Mythic Clash Already Aligns Well

The current design is already strong on a few important axes:

- shared grammar across factions instead of private faction mini-games
- readable board structure with a hard `5`-figure cap
- automatic mana rather than land-style resource variance
- limited interaction windows with `Slow`, `Fast`, and `Burst`
- fatigue instead of an arbitrary fixed late-game winner
- small keyword set and clear card-type structure
- culture identity built around "different plan, same grammar"

Those are all good signs.

The knowledge-base file does **not** suggest that Mythic Clash should become more complicated.

It suggests that Mythic Clash should become more disciplined about:

- how tension peaks are created
- how much hidden information debt is allowed
- how often losing players can still see a line back in
- how much cognitive burden each card is allowed to carry

## Real Improvements Worth Adopting

## 1. Add a formal "telegraphed lethality" rule to card and set design

The research repeatedly favors informed uncertainty over fake safety or surprise lethals from nowhere.

Mythic Clash already says it should avoid one-turn blowouts, but that principle should become a harder design rule:

- most lethal setups should be visible on board, through a relic, or through a known signature threat
- direct hand-burst should usually finish games the board already pressured
- large face-damage swings should be expensive, setup-gated, or strongly telegraphed

Why this matters:

- it creates better micro-climaxes
- it makes counting lethal a skill test
- it avoids "I was dead from 18 and could not reasonably play around it" losses

This is especially important before expanding the support-card pool.

## 2. Tighten the policy on generated and discovered cards

The current docs already dislike huge random pools, but the knowledge-base file makes the reason sharper:

- hidden-but-trackable information becomes memory tax
- spectator readability collapses when outcomes depend on large unknown generation trees

Mythic Clash should adopt a stricter content rule:

- `discover` and generation effects should use explicit, narrow, mostly public pools
- players should usually know the bucket, not guess from the whole game
- launch sets should avoid long "created by created by created by" chains

This keeps uncertainty interesting without making the game feel clerical.

## 3. Add a card complexity budget, not just an extensible grammar

The open card grammar is good for implementation.

It is not enough by itself for onboarding.

The research points toward lenticular design:

- cards should be usable at first read
- deeper value should come from sequencing, timing, matchup context, and combinations
- not from text-wall exceptions

Mythic Clash should define a launch complexity budget such as:

- most cards should have one clear job and one main timing
- only a small minority should use multi-step or highly conditional text
- signature characters may be the deepest cards in a culture, but still need to be answerable

This is especially important because the current culture translations can drift toward rewrite-heavy complexity if we are not careful.

## 4. Make "visible comeback lines" a real pack-design requirement

The knowledge-base file is very strong on one point:

- hopelessness is poison
- hard rubber-banding is also bad

The healthy middle is soft comeback space.

For Mythic Clash, that should become a pack-level rule:

- every culture should have at least one stabilizing tool
- every gameplay family should have some way to contest an early snowball
- neutral core should include cheap defensive interaction that is narrow but real

Examples of healthy comeback tools:

- efficient answers to overcommitted boards
- freeze, exhaust, bounce, or guard effects that buy one turn
- healing that matters only if paired with board recovery
- relic or hero-power lines that help a behind player stabilize without deleting earned advantage

This is not about punishing the leader.

It is about making sure the trailing player still sees skillful outs.

## 5. Treat pacing and readability as first-class product rules, not later polish

The knowledge-base file pushes hard on downtime, action clarity, and spectator readability.

Mythic Clash already mentions visible timers and action logs, but they should be treated as required infrastructure:

- visible timer
- visible priority / response indicator
- clean action log
- clear display of `Ritual Mana`
- clear display of what can still attack
- clear display of relic state and passive sources

This matters because Mythic Clash is building limited interaction windows.

If players cannot immediately tell who can act and why, the game will feel harder than it actually is.

## 6. Protect against solved openers and culture-pack convergence

The current translations are promising, but they also show a real risk:

- packs can converge into similar midrange shells
- famous myth figures get curve-compressed into the same cost bands
- early turns can become repetitive if we rely only on headline characters

The knowledge-base file correctly treats solved openings as a long-term fun killer.

That means Mythic Clash should keep pushing on:

- lower-profile early cards
- family-specific early play patterns
- meaningful mulligan differences between cultures
- distinct reasons to spend or bank mana on turns `2` to `4`

If the first three turns start feeling identical across cultures, the family model will lose a lot of its value.

## 7. Surface faction readability to the player, not only to designers

The culture-family model is good internally.

The research suggests we should also expose that readability outward.

Mythic Clash should plan for:

- deckbuilder tags like `Vanguard`, `Sanctuary`, or `Oracle`
- short culture playstyle blurbs
- match-intro or hover summaries that tell players what a culture usually does

That supports the exact goal we defined earlier:

- different factions should feel different
- but players should still broadly understand what they are facing

This is a real design improvement, not just UI flavor, because it lowers the knowledge tax without flattening mastery.

## Most Important Conclusion

The biggest improvements suggested by the knowledge-base file are **not**:

- more keywords
- more hidden information
- more reactive complexity
- more faction-exclusive mechanics

The biggest improvements are:

- clearer threat telegraphing
- tighter information discipline
- stronger comeback visibility
- stronger pacing/readability infrastructure
- stricter complexity budgeting

That is a very healthy result.

It means the current direction is broadly right, but it still needs more constraint before scale.

## Recommended Immediate Actions

Before converting all `100` cultures, Mythic Clash should:

1. define a launch card complexity budget
2. define a stricter discover / generation policy
3. define pack-level comeback requirements
4. define a burst / lethality budgeting rule for support-card design
5. treat timers, priority markers, and action log as required UX, not optional polish

If we do those things first, the later culture rollout and engine work will rest on a much stronger competitive foundation.
