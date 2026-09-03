---
name: gitlab
description: Automate interactions with GitLab instances.
allowed_tools:
  - scripts/gitlab_cli.py
---

# GitLab Ops
Automate gitlab interactions like troubleshooting, variable inspection, and pipeline analysis. Focus on read-only API access and actionable insights. Designed for DevOps engineers, SREs.

## Quick Start

1. Confirm required inputs:
   - `GITLAB_ACCESS_TOKEN` (PAT)
   - Target identifiers: `project_id`, `group_id`, `pipeline_id`, `job_id`, `environment`
2. Install runtime dependencies:
   - `uv add click python-gitlab`
3. Run API preflight first:
   - `uv run scripts/gitlab_cli.py preflight`

## Guardrails

- Never request elevated tokens when read-only scopes are enough.

## Workflows

### 1) Search Variable or Value

1. Accept one target key.
3. Return precedence view for the target environment.
4. If multiple matches exist, explain effective winner and why.

## Output Format

1. `Findings`: concise facts from API evidence.
2. `Likely Cause`: highest-confidence cause.
3. `Next Checks`: exact API/UI checks with IDs.
4. `Fix Plan`: smallest safe change and rollback note.

## Advanced References

- See [REFERENCE.md](REFERENCE.md) for endpoint map and precedence logic.
- See [EXAMPLES.md](EXAMPLES.md) for end-to-end scenarios.
