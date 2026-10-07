---
name: grilling
description: Ask the user questions to test a plan, decision, or idea before they act. Map each choice and the decisions that follow from it. Use this skill when the user asks to "grill me," "stress-test this," "poke holes in this," "war-game this decision," or requests detailed questions instead of a quick answer.
---

Ask the user questions until you both understand the subject. Map the decisions as a **design tree**. Each decision can lead to more decisions.

## Rounds

Work through the tree in **rounds**. The **frontier** is the set of decisions that you can ask about now. Their required earlier decisions are settled. Ask all questions on the current frontier in one round. Keep question numbers in order for the full session. Do not start again at 1 in a later round. Give a recommended answer for each question:

```
❓ **Q1** - **<Question title>**:

<Question text. Explain why the decision matters. Use more than one paragraph if needed.>

- **A.** <option>
- **B.** <option>
- **C.** <option>

➡️ **Recommended: B** — <Brief reason to choose B over A or C, or what can go wrong with another choice.>

---

❓ **Q2** - **<Question Title>**:

<question body>

- **A.** <option>
- **B.** <option>

➡️ **Recommended: A** — <Brief reason.>
```

The user's answers can change the tree. A settled decision can make more questions ready. After each round, work out the new frontier and ask those questions in the next round. If one question depends on an answer to another open question, ask it in a later round.

**Changes to earlier answers:** If an answer conflicts with a decision that was settled earlier, point out the conflict. Ask again about that decision and any decisions that depend on it. Do not keep using the old answer without telling the user.

## Finding facts

You must find facts. Do not ask the user to find them. If a question needs a fact from the environment, such as a file or tool result, get the fact yourself. Use a sub-agent if available. Otherwise, use your tools. Do not delay all questions while you look for one fact. Ask the questions that do not depend on that fact. Ask the other questions after you find it. The user makes the decisions. Ask the user and wait for their answer.

## Scope control

This process can cover every decision, but the user can stop at any time. If the user asks to stop, finish, or move on, stop asking questions. Summarize the decisions that are settled. State which parts you did not explore.

## Done

The session is done when there are no more questions on the frontier. You have reviewed each branch, and you have not left any assumptions unstated. Before you finish, summarize the settled decisions in a short plan or specification. Do not act on the plan until the user confirms that you both understand it.
