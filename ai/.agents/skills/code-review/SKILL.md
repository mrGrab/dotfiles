---
name: code-review
description: Review a codebase, selected files, pipelines, formatting, or changes since a point the user names. Check the requested scope against repository standards and any related requirements. Use sub-agents to check standards and requirements in parallel when available, then combine their findings in one report. Use this skill when the user asks for a project, codebase, pipeline, formatting, branch, pull request, or change review.
---

Review the scope that the user requests. This can be the current codebase, selected files or directories, pipeline configuration, formatting, or changes since a named point.

- **Standards**: Does the code follow the repository's documented coding standards?
- **Spec**: Does the code meet the requirements in the related issue or specification?

When sub-agents are available, use separate agents to check standards and requirements at the same time. Then combine their findings in one report. If sub-agents are not available, do both checks yourself.

For a repository-wide or current-state review, review the files in scope as they exist now. For a change review, compare the changes with the point the user names. Review non-code files, such as pipeline and formatter configuration, when they are in scope. If the user asks for a pipeline or formatting review, run relevant existing validation tools when available. Do not change files during a review.

## Process

### 1. Set the review scope

Use the scope that the user names. If the user requests a review of a codebase or project without naming a smaller scope, review the current repository. If the scope is unclear, ask what files, directories, or systems to include.

For a review of changes, use the point the user names. It can be a commit SHA, branch name, tag, `main`, `HEAD~5`, or another Git reference. If the user does not name a point, ask for one.

For a change review, use `git diff <fixed-point>...HEAD` to compare from the merge-base. Also get the commit list with `git log <fixed-point>..HEAD --oneline`. Check the reference with `git rev-parse <fixed-point>`. If the reference is invalid or the diff is empty, stop. Do not start the sub-agents.

For a current-state review, inspect the files in scope. Do not require a fixed point or a non-empty diff.

### 2. Identify the requirements

Find a related issue or specification when the review asks whether the work meets specific requirements. For change reviews, search for issue references in commit messages, such as `#123`, `Closes #45`, or GitLab `!67`. Use `docs/agents/issue-tracker.md` if it exists and describes how to access the issue tracker. Also check paths provided by the user and relevant files under `docs/`, `specs/`, or `.scratch/`.

If the requirements are not available, ask the user for them when needed. If the user says there are no requirements, skip the **Spec** check and report "no spec available". For a general codebase, pipeline, or formatting review, do not require a specification. Check the requested quality and standards directly.

### 3. Identify the standards sources

Find the repository files that apply to the review scope. These can include coding standards, `CONTRIBUTING.md`, pipeline rules, formatter configuration, lint rules, and instructions for specific directories or file types.

The **Standards** check must also use the following set of Fowler code smells from _Refactoring_, chapter 3. Use this set even if the repository has no coding standards. Follow these two rules:

- **Repository standards take priority.** Follow a documented repository standard. If it allows something that a code smell would flag, do not report the smell.
- **Treat smells as suggestions.** Label each smell as a possible problem, such as "possible Feature Envy". Do not report a smell as a hard violation. Do not report issues that a tool already checks.

For each smell, the text describes the problem and a possible fix. Compare the code in scope with these descriptions:

- **Mysterious Name**: A function, variable, or type has a name that does not explain what it does or contains. Possible fix: choose a clear name. If no clear name is possible, the design may be unclear.
- **Duplicated Code**: The same logic appears in more than one part of the code in scope. Possible fix: move the shared logic to one place and use it in both places.
- **Feature Envy**: A method uses another object's data more than its own data. Possible fix: move the method to the object that owns the data.
- **Data Clumps**: The same fields or parameters often appear together. Possible fix: put them in one type and pass that type.
- **Primitive Obsession**: A primitive type or string represents a domain idea that may need its own type. Possible fix: make a small type for that idea.
- **Repeated Switches**: The same `switch` statement or `if` chain for the same type appears more than once in the code in scope. Possible fix: use polymorphism or one shared map.
- **Shotgun Surgery**: One logical change causes edits in many files. Possible fix: put the related changes in one module.
- **Divergent Change**: One file or module changes for several unrelated reasons. Possible fix: split it so each part changes for one reason.
- **Speculative Generality**: The change adds abstractions, parameters, or hooks that the specification does not need. Possible fix: remove them and use direct code until there is a real need.
- **Message Chains**: Code uses a long sequence such as `a.b().c().d()` to reach data. Possible fix: hide the sequence behind a method on the first object.
- **Middle Man**: A class or function mainly passes a call to another part of the code. Possible fix: remove it and call the actual target.
- **Refused Bequest**: A subclass or implementer ignores or changes most of what it inherits. Possible fix: replace inheritance with composition.

### 4. Review the standards and requirements

When sub-agents are available, start the **Standards** and **Spec** agents in parallel. Give the **Standards** agent these details:

- The review scope. For a change review, include the full diff command and commit list. For a current-state review, include the files or areas to inspect.
- The paths to the coding standard files from step 3.
- The full list of code smells from step 3. The sub-agent cannot see that list unless you include it.
- This instruction: "For each relevant file or code section, report (a) each place where the code breaks a documented standard, with the standard file and rule; and (b) each code smell, with its name and the related code. For a change review, report findings introduced by the change. For a current-state review, report findings in the requested scope. Separate rule violations from possible smells. A violation of a documented standard can be a hard issue. A code smell is always a judgement call. A documented repository standard takes priority over the smell list. Do not report issues that a tool checks. Use fewer than 400 words."

Give the **Spec** agent these details:

- The review scope. For a change review, include the diff command and commit list. For a current-state review, include the files or areas to inspect.
- The related requirements or specification, if available.
- This instruction: "Report (a) requirements that are missing or only partly complete; (b) changes that the specification did not ask for; and (c) requirements that appear complete but may be implemented incorrectly. Quote the relevant specification text for each finding. Use fewer than 400 words."

For a change review without requirements, do not start the **Spec** agent. State "no spec available" in the report. For a general quality review that does not ask for a specification check, do not start this agent. If sub-agents are not available, review the standards and requirements directly.

### 5. Aggregate

Combine all findings in one report. For each finding, identify whether it relates to **Standards** or **Spec**. Keep the findings distinct and do not hide one category with the other. Make only small edits to agent findings for clarity.

End with one line that gives the number of findings and the most serious issue in each category, if there is one.

## Why two axes

A change can pass one check and fail the other:

- Code can follow every standard but do the wrong thing. In this case, **Standards pass** and **Spec fail**.
- Code can meet the issue requirements but break repository standards. In this case, **Spec pass** and **Standards fail**.

Label findings by category so that one check does not hide the results of the other.
