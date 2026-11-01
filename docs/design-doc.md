# AI-Native Cozy Mystery Prototype

## 1. Project Goal

This is a small experimental game-design and learning project.

The goal is not to immediately build a complete game. The goal is to create a very small playable prototype that demonstrates:

* Gameplay and systems thinking
* Player psychology and agency
* Experimental game design
* Prototyping, playtesting and iteration
* Interactive narrative
* AI-native gameplay exploration
* Turning an abstract AI capability into tangible player value

The first prototype should remain extremely small.

The core experience should work without AI before AI is introduced.

---

## 2. Core Concept

### Working Pitch

The player wakes up in a cosy, remote inn.

Everything initially appears normal and welcoming, although a few small details feel strangely inconsistent.

The player has a limited number of turns to explore the inn, interact with its occupants and investigate clues.

Their initial objective is simple:

Leave the inn.

Eventually, the player finds a way out.

But at midnight, the world resets.

They wake up in the same room again.

The inn, its objects and its occupants have returned to their original state.

Only the player remembers what happened.

The player's question gradually changes from:

"How do I leave?"

to:

"Why can't I leave this place?"

and eventually:

"What rules are governing this reset?"

---

## 3. Intended Player Fantasy

The player should feel like they are genuinely investigating a mystery rather than following a designer-authored sequence of puzzle solutions.

The core fantasy is:

I can follow my own curiosity, decide what to investigate, connect evidence to people and places, form my own hypotheses, and use future loops to test whether I am right.

AI itself should not be the player fantasy.

Ideally, the player does not think:

"This AI is clever."

They think:

"Wait… I think I figured out how this world works."

---

## 4. Tone

Cozy Mystery

Not horror.

The world should feel:

* Warm
* Curious
* Slightly strange
* Occasionally funny
* Inviting rather than threatening

There may be a very light friendship, affection or romance element, but this is not a core system.

Tone principle:

Curious, not frightening.

Strange events should make the player want to investigate rather than run away.

---

## 5. Core Gameplay Loop

Current proposed loop:

Explore → Find Evidence → Connect Evidence → Observe Reaction / World Change → Form Hypothesis → Reset → Try Again

The player can:

1. Choose where to explore.
2. Discover evidence.
3. Interact with NPCs.
4. Present evidence to characters or locations.
5. Observe NPC reactions or changes in world state.
6. Decide which investigation path to follow.
7. Form hypotheses within a limited number of turns.
8. Experience the reset.
9. Use knowledge from previous loops to investigate differently.

---

## 6. Interaction Philosophy

Free-text input is not the primary interaction for the MVP.

Reasons:

* High cognitive load
* Players may not want to type complete questions
* Localization becomes difficult
* Mystery solving can turn into "learning how to prompt the AI"

The primary interaction should instead be:

Evidence × Character / Location

Example:

The player discovers a Blue Ribbon.

They can choose:

Present Blue Ribbon → Mira

Mira's response can depend on:

* What Mira knows
* What the player has previously done
* Current world state
* Evidence already discovered

Evidence becomes the player's main language for investigating the world.

---

## 7. Evidence Design

Evidence should not directly explain its own meaning.

The current direction is:

Partially ambiguous evidence, with occasional multiple plausible interpretations.

Example:

"A torn piece of blue fabric with a faint smell of smoke."

Rather than:

"This belongs to Mira and proves she was at the scene."

The meaning of evidence may evolve depending on:

* When it is discovered
* Where it is discovered
* Who it is presented to
* What the player has already done

Core principle:

Evidence creates questions, not answers.

A good clue should:

Narrow possibilities while opening new questions.

---

## 8. Player Experience Principles

### 1. Follow Your Curiosity

The player chooses which clues to pursue rather than following a fixed investigation checklist.

### 2. Evidence Creates Questions, Not Answers

The game provides information.

Interpretation belongs to the player.

### 3. Actions Change the Investigation, Not Simply Succeed or Fail

An incorrect hypothesis or an early confrontation should not simply punish the player.

Actions may:

* Change NPC behaviour
* Change schedules
* Cause information to be withheld
* Trigger another world event

Consequences should create new investigation opportunities rather than dead ends.

### 4. Discovery Should Be Inferred, Not Stumbled Upon

Important events may be missable.

However, the game should provide enough subtle hints for an attentive player to predict that something might happen.

The desired reaction is:

"I knew I should check here!"

Not:

"Apparently I was supposed to randomly visit this place on Turn 4."

### 5. Curious, Not Frightening

Mystery should create curiosity rather than relying on horror.

---

## 9. Living World

The MVP uses a lightly living world.

NPCs follow simple schedules or agendas.

For example:

* Morning → Lobby
* Afternoon → Garden
* Evening → Dining Room
* Midnight → Secret meeting

Player actions can modify parts of those schedules.

For example:

Present Evidence to Mira
→ Mira changes her plan
→ She appears somewhere unusual at midnight
→ The player may discover a new event.

Hidden events can be missed, but they should be hinted at.

More dynamic NPC decision-making can be explored later.

---

## 10. Reset Rules

The basic MVP rule is:

When time expires, the location, NPCs, objects and world state return to their initial state.

The player retains:

* Their own knowledge
* A lightweight Investigation Journal

The Journal records confirmed factual discoveries only.

For example:

✓ Mira lied about being in the Library.
✓ The Innkeeper leaves the lobby before midnight.

It does not perform deductions for the player:

✗ Therefore Mira met the Innkeeper.
✗ Mira caused the reset.

Connections and hypotheses remain the player's responsibility.

If playtesting shows that the Journal makes the mystery too easy, its support can be reduced or removed.

---

## 11. Memory Anomaly

One important MVP reveal is that the player initially believes:

I am the only person who remembers previous loops.

However, something the player does eventually triggers an anomaly.

After the next reset, one NPC appears to remember a fragment of the previous loop.

For example:

Previous loop:

"You haven't tried the pie."

After reset:

"Morning…"
pause
"You still haven't tried the pie."

The desired player reaction is:

"Wait… they remember?"

This should not simply be:

Loop 3 → Memory unlocked.

It should be triggered by a previous player action and world state.

Current direction:

Player Action → NPC interacts with a particular location/object/state at the moment of reset → a fragment of memory survives.

The player's understanding can then progress through:

They remember.

↓

Why do they remember?

↓

Can I reproduce it?

↓

Can I exploit this rule to escape?

---

## 12. Opening Experience

The opening gives the player a few hints that:

"Something about this place isn't right."

It does not immediately explain the time loop.

The first loop should be very short, approximately 2–4 minutes.

Possible structure:

**Turn 1**

The player wakes up and explores their room.

They discover an unusual clue, potentially written in their own handwriting:

Leave before midnight.

**Turn 2**

The player explores the inn or speaks to an NPC.

Another subtle inconsistency appears.

**Turn 3**

The player discovers a way to leave.

They successfully "escape."

**Midnight**

Something impossible happens.

**Reset**

The player wakes up in the same bed.

An NPC repeats exactly the same opening line.

The player's understanding changes:

"Wait… I wasn't simply trapped inside the inn."

The first reset simultaneously creates two questions:

* What just happened?
* Why didn't escaping work?

---

## 13. MVP Setting

Remote Inn

Reasons:

* Naturally invites exploration
* A small NPC cast makes sense
* A small number of locations makes sense
* "Why can't I leave?" is immediately understandable
* Supports a Cozy Mystery tone
* Requires little worldbuilding
* Can later expand beyond the inn

The first playable prototype may contain only:

* 3 locations
* 2 NPCs
* 1 reset
* 1 memory anomaly
* 1 underlying hidden rule

The goal is not to create a complete game.

The first major test is:

After experiencing the first reset, does the player naturally want to try again to understand what is happening?

---

## 14. Replay Philosophy

The first version will test:

Player knowledge + lightweight factual Journal

When a new loop begins:

The world resets.

Confirmed factual knowledge may remain available.

However, the player must still:

* Recognise patterns
* Connect evidence
* Form hypotheses
* Decide what to test next

If this makes the mystery too easy, Journal support can be reduced.

---

## 15. Future Exploration — NOT MVP

The following are future notes only and should not be added to the first prototype.

### Persistent NPC Memory

Selected NPCs may retain limited memories across loops after specific triggers.

### Player-Controlled Persistence

The player may eventually learn how to deliberately allow:

* An object
* An NPC memory
* A world state

to survive a reset.

### Larger Reset

The player initially believes:

"I am trapped in the inn."

Later:

"Maybe the inn isn't the real problem."

Eventually:

"Is the entire day or world resetting?"

### More Dynamic NPCs

The system could evolve from:

NPC follows a designer-authored schedule

toward:

NPC acts according to goals + knowledge + relationships + world state.

This could later become an important AI-native gameplay system.

---

## 16. AI Design Question

AI should not simply:

* Generate dialogue
* Generate random stories
* Generate more narrative branches

The player-facing question should be:

What limitations of traditional branching narratives prevent the player from genuinely investigating, forming their own hypotheses and testing those hypotheses against responsive characters and systems?

Potential AI value currently worth exploring:

* NPCs understand evidence and context presented by the player.
* NPC responses reflect their knowledge, memory and current world state.
* The game can understand or challenge the player's own theory.
* NPC behaviour may eventually emerge from goals + knowledge + state rather than entirely fixed branches.

However:

AI must not arbitrarily change the truth of the mystery.

The designer should retain control of:

* Ground truth
* World rules
* Character knowledge
* Constraints
* Valid state changes

AI makes the world respond more naturally and contextually to player investigation.

AI integration is a later experiment, not a requirement for the first MVP.

---

## 17. Development Phases

### Phase 1 — Player Experience & Design Hypothesis

Status: Essentially complete

Defined:

* Player fantasy
* Cozy Mystery tone
* Investigation loop
* Evidence interaction
* Reset concept
* Replay philosophy
* Lightly living world
* Memory anomaly
* Design principles
* MVP scope philosophy

### Phase 2 — Design the Actual Mystery

Status: Complete. Decisions are recorded in `CLAUDE.md`.

Defined:

* 3 locations
* 2 NPCs
* NPC roles and motivations
* Core mystery truth
* Why the inn resets
* First-loop clues
* Evidence set
* NPC schedules
* Memory trigger
* First 2–3 loops
* Plausible player hypotheses
* Minimum ending / reveal

Keep it extremely small.

### Phase 3 — Build a Rule-Based Prototype

Do not use AI yet.

Implement:

* Location navigation
* Turns / time
* Evidence inventory
* Present Evidence interaction
* NPC state
* Simple schedules
* Reset
* Journal
* Memory anomaly trigger

Goal:

Prove that the core experience is fun.

### Phase 4 — AI Experiment

Only introduce AI once the core prototype works.

Compare:

Rule-based version

vs

AI-enhanced version

Explore whether AI genuinely improves:

* Player agency
* NPC responsiveness
* Hypothesis testing
* Emergent investigation
* Replay experience

### Phase 5 — Playtest & Case Study

Run a small number of exploratory playtests.

Observe:

* What is the player's first hypothesis?
* Does the first reset make them want to continue?
* Do they understand the clues?
* Do discoveries feel earned?
* Does the Journal make the mystery too easy?
* Does the memory anomaly land?
* Does AI genuinely improve the experience?

Document:

Hypothesis → Prototype → Playtest → Findings → Iteration → AI trade-offs

The result becomes a design case study.
