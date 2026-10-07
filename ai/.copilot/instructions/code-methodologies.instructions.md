---
name: "Code Methodologies"
description: "Software design principles and engineering rules for all codebases."
applyTo: "**"
---

# Global Code Methodologies

When you write, change, or review code, follow these principles in this order:

1. **KISS (Keep It Simple):** Choose the simplest solution that works. Avoid early abstractions, complex inheritance, and unnecessary complexity.
2. **YAGNI (You Aren't Gonna Need It):** Do not add unrequested features, speculative options, or wrappers for possible future needs.
3. **Pragmatic SOLID:** Prefer composition over inheritance. Apply SOLID principles only when they directly improve maintainability or testing.
4. **DRY (Don't Repeat Yourself):** Remove duplication when doing so improves the design. Keep some duplication rather than add the wrong abstraction.

## Core Engineering Guardrails

- **Standard library first:** Prefer standard library modules over third-party dependencies.
- **Fail fast and be idempotent:** Automation, scripts, and API handlers must stop on errors and show clear messages. Repeated runs must be safe.
- **Self-documenting code:** Use clear names and explicit types. Add comments and docstrings only to explain non-obvious logic or important requirements.
