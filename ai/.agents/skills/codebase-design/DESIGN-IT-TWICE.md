# Design It Twice

Use this process when the user wants to compare interface designs for a module that may be deepened. It follows Ousterhout's "Design It Twice" principle: the first design is unlikely to be the best.

Use the terms in [SKILL.md](SKILL.md): **module**, **interface**, **seam**, **adapter**, and **leverage**.

## Process

### 1. Describe the problem

Before you start the sub-agents, explain the problem for the chosen module to the user. Include:

- The constraints that each proposed interface must meet.
- The dependencies the module needs and their categories. See [DEEPENING.md](DEEPENING.md).
- A short code sketch to make the constraints clear. The sketch is an example, not a design proposal.

Show this explanation to the user. Then continue to Step 2 without waiting for a reply. The user can read and consider the problem while the sub-agents work.

### 2. Start sub-agents

Start at least three sub-agents at the same time. Each must design a **very different** interface for the deepened module.

Give each sub-agent a separate technical brief. Include file paths, dependencies between modules, the dependency category from [DEEPENING.md](DEEPENING.md), and what belongs behind the seam. These briefs provide technical detail beyond the problem explanation in Step 1. Give each sub-agent a different design goal:

- Agent 1: "Keep the interface small: use no more than three entry points. Get the most leverage from each one."
- Agent 2: "Make the interface flexible: support many use cases and extensions."
- Agent 3: "Design for the most common caller: make the usual case simple."
- Agent 4, if needed: "Use ports and adapters for dependencies that cross the seam."

Include terms from [SKILL.md](SKILL.md) and `GLOSSARY.md` in each brief. This helps the sub-agents use the same architecture terms and project domain terms.

Ask each sub-agent to provide:

1. The interface: types, methods, parameters, rules, required operation order, and errors.
2. An example of how callers use the interface.
3. The behaviour that the implementation hides behind the seam.
4. The dependency plan and adapters. See [DEEPENING.md](DEEPENING.md).
5. The trade-offs, including where the design provides strong or limited leverage.

### 3. Show and compare the designs

Show each design separately so the user can consider it. Then compare the designs in prose. Compare their **depth** (leverage at the interface), **locality** (where changes stay), and **seam placement**.

After the comparison, recommend the strongest design and explain why. If parts of different designs work well together, propose a combined design. Give a clear recommendation, not just a list of options.
