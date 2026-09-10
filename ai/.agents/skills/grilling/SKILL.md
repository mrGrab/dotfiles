---
name: grilling
description: Interview the user relentlessly to stress-test a plan, decision, or idea before they act on it, mapping every choice and its downstream consequences. Use when the user asks to "grill me," "stress-test this," "poke holes in this," "war-game this decision," or wants rigorous Socratic questioning instead of a quick answer.
---

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

## Rounds

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled — questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round, numbered continuously across the whole session (don't restart numbering each round), with your recommended answer:

```
❓ **Q1** - **<Question Title>**:

<question body — context and why this decision matters, can be multiple paragraphs>

- **A.** <option>
- **B.** <option>
- **C.** <option>

➡️ **Recommended: B** — <one-line rationale: why B over A/C, or what breaks if you pick wrong>

---

❓ **Q2** - **<Question Title>**:

<question body>

- **A.** <option>
- **B.** <option>

➡️ **Recommended: A** — <rationale>
```

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

**Revisions:** if an answer contradicts something previously marked settled, flag the conflict explicitly and re-open that branch (and anything downstream of it) rather than silently carrying the contradiction forward.

## Finding facts

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), go get it yourself — dispatch a sub-agent if you have that capability, otherwise use your available tools directly inline. Either way, don't block the whole round on it: a running lookup is an unsettled prerequisite, so only questions downstream of it wait; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait for their answer.

## Scope control

This process is exhaustive by design, but the user can end it early — if they say to stop, wrap up, or move on, close out immediately: summarize what's settled and flag which branches were left unexplored, rather than continuing to press.

## Done

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Summarize the settled decisions as a short plan/spec before considering the exercise complete. Do not act on it until the user confirms you have reached a shared understanding.
