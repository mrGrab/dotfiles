---
name: improve-codebase-architecture
description: Find opportunities to deepen modules in a codebase. Show the options in a visual HTML report. Then use the grilling skill to explore the option the user selects.
disable-model-invocation: true
---

# Improve Codebase Architecture

Find architecture problems and suggest **deepening opportunities**. These are changes that turn shallow modules into deep modules. The goals are to improve testability and make the codebase easier for AI to navigate.

Use the project's domain model and the shared design vocabulary:

- Call the Skill tool with `codebase-design`. Use its architecture terms: **module**, **interface**, **depth**, **seam**, **adapter**, **leverage**, and **locality**. Follow its principles: the deletion test, "the interface is the test surface", and "one adapter = hypothetical seam, two = real".
- Use these terms as written in every suggestion. Do not replace them with "component", "service", "API", or "boundary".
- Use `CONTEXT.md` for domain terms and names for seams. Use ADRs in `docs/adr/` to learn about decisions. Do not suggest decisions that an ADR has already settled unless there is a strong reason to review them again.

## Process

### 1. Explore

**Set the scope before you scan.** A deepened module helps with future changes. Give more attention to parts of the codebase that change often. Decide where to look before you explore:

- If the user names a module, area, or problem, focus on it. Do not infer another scope.
- Otherwise, inspect enough commit history with `git log --oneline` to find files and areas that change often. Start with those areas. If the changes do not point to clear areas, review a wider scope.

Read the domain glossary in `CONTEXT.md` and any relevant ADRs before you explore the code.

Then use a sub-agent to explore the codebase. Explore the code and note where it is hard to understand:

- Does one concept require you to read many small modules?
- Are any modules **shallow**, with an interface almost as complex as the implementation?
- Were pure functions extracted only to make testing possible, while bugs in their use remain hard to find? This can indicate poor **locality**.
- Do tightly coupled modules leak across their seams?
- Is any code untested or hard to test through its current interface?

For each module that may be shallow, apply the **deletion test**: If you delete it, does the complexity become more concentrated, or does it only move elsewhere? If complexity becomes more concentrated, this may be an opportunity to deepen a module.

### 2. Show options in an HTML report

Write a complete HTML file to the operating system's temporary directory. Do not add the report to the repository. Find the temporary directory from `$TMPDIR`. If it is not set, use `/tmp` on Linux or macOS, or `%TEMP%` on Windows. Name the file `<tmpdir>/architecture-review-<timestamp>.html` so each run has a new file.

Open the report for the user. Use `xdg-open <path>` on Linux, `open <path>` on macOS, or `start <path>` on Windows. Tell the user the absolute path.

Use **Tailwind via CDN** for layout and styling. Use **Mermaid via CDN** for diagrams that show calls, dependencies, or sequences. You can also use custom CSS, HTML, or SVG for diagrams such as mass diagrams, cross-sections, or collapse views. Use different diagram types when they fit. Each option must include a before-and-after visual.

For each option, include a card with:

- **Files**: The files and modules involved.
- **Problem**: Why the current architecture causes difficulty.
- **Solution**: What would change. Use plain English.
- **Benefits**: Explain the effect on locality, leverage, and tests.
- **Before and after diagrams**: Put them side by side. Show the shallow structure and the deeper module.
- **Recommendation strength**: Show one badge: `Strong`, `Worth exploring`, or `Speculative`.

End the report with a **Top recommendation** section. Name the option to do first and explain why.

Use domain terms from `CONTEXT.md` and architecture terms from `codebase-design`. For example, if `CONTEXT.md` names the concept "Order", say "the Order intake module". Do not use a code name such as "FooBarHandler" or call it an "Order service".

If an option conflicts with an ADR, include it only when the problem is serious enough to review that decision again. Clearly identify the conflict in the card. For example: _"Conflicts with ADR-0007, but consider reviewing it because..."_. Do not list every possible change that an ADR rules out.

See [HTML-REPORT.md](HTML-REPORT.md) for the HTML template, diagram examples, and style rules.

Do not suggest interfaces at this stage. After you write and open the report, ask the user: "Which of these would you like to explore?"

### 3. Explore the selected option

When the user chooses an option, call the Skill tool with `grilling`. Use it to discuss the decisions, constraints, and dependencies. Define the deepened module, what belongs behind its seam, and which tests will remain.

As the decisions become clear, make needed updates during the discussion. Call the Skill tool with `domain-modeling` to update the domain model:

- **The new module name is a concept not in `CONTEXT.md`:** Add the term to `CONTEXT.md`. Create the file only if needed.
- **A domain term is unclear:** Clarify it in `CONTEXT.md` during the discussion.
- **The user rejects an option for an important reason:** Offer to record the reason in an ADR only if a future architecture review needs it to avoid suggesting the same option. Ask: _"Would you like me to record this in an ADR so future architecture reviews do not suggest this option again?"_ Do not offer for temporary or obvious reasons.
- **The user wants to explore other interfaces for the deepened module:** Call the Skill tool with `codebase-design` and use its parallel "design it twice" process.
