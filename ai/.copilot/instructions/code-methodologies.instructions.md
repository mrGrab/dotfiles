---
name: "Code Methodologies"
description: "Core software design principles and engineering standards applied across all codebases."
applyTo: "**"
---

# Global Code Methodologies

When generating, refactoring, or reviewing code, apply these proven approaches in exact order of priority:

1. **KISS (Keep It Simple, Stupid):** Prefer the simplest working solution. Avoid premature abstractions, complex inheritance hierarchies, and overengineering.
2. **YAGNI (You Aren't Gonna Need It):** Never implement unrequested features, speculative configuration options, or "future-proofing" wrapper logic.
3. **Pragmatic SOLID:** Use composition over inheritance. Apply SOLID principles only where they directly reduce maintenance overhead or improve testability.
4. **DRY (Don't Repeat Yourself):** Eliminate duplication when it adds clear structural value, but favor slight duplication over the wrong abstraction.

## Core Engineering Guardrails

- **Standard Library First:** Prefer standard library modules before pulling in third-party dependencies.
- **Fail-Fast & Idempotent:** Automation, scripts, and API handlers must fail immediately with clear error messages and be safe to re-run.
- **Self-Documenting Code:** Write clear variable/function names and explicit types. Reserve docstrings and comments strictly for non-obvious logic or business contracts.
