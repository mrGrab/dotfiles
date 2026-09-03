# GitLab API Reference

## Required Environment Variables

- `GITLAB_ACCESS_TOKEN` PAT with minimal read scopes
- Python runtime tools:
  - `uv` for execution
  - `click` for CLI parsing
  - `python-gitlab` for API interaction

## CLI Commands

- Preflight:
  - `uv run scripts/gitlab_cli.py preflight`
- Variable search:
  - `uv run scripts/gitlab_cli.py search-variable --term <KEY>`

## Core Endpoints

- Auth preflight:
  - `GET /api/v4/user`
- Pipelines:
  - `GET /api/v4/projects/:project_id/pipelines/:pipeline_id`
  - `GET /api/v4/projects/:project_id/pipelines/:pipeline_id/jobs`
- Jobs:
  - `GET /api/v4/projects/:project_id/jobs/:job_id`
  - `GET /api/v4/projects/:project_id/jobs/:job_id/trace`
- Runners:
  - `GET /api/v4/runners/:runner_id`
- Variables:
  - Group: `GET /api/v4/groups/:group_id/variables`
  - Project: `GET /api/v4/projects/:project_id/variables`
  - Pipeline/runtime: `GET /api/v4/projects/:project_id/pipelines/:pipeline_id/variables`

## Variable Collision and Precedence

Use this practical order for diagnostics:

1. Pipeline/runtime variables
2. Project variables
3. Group variables
4. Instance variables

If two variables have the same key:

- Prefer exact `environment_scope` match over wildcard.
- If both are wildcard, report ambiguity and inspect job context.

## Failed Job Triage Checklist

1. Confirm pipeline source (`push`, `merge_request_event`, `schedule`, `web`).
2. Confirm job status, `allow_failure`, and stage gating.
3. Inspect trace for deterministic errors first (missing vars, missing artifacts, auth failures, image pull failures).
4. Inspect runner health and tags mismatch.
5. Validate cache/artifact paths and expiration behavior.
6. Recommend the smallest change that addresses root cause.

## Notes on Secret Safety

- Default to redacting values in outputs.
- Only print variable values when user explicitly asks.
- Never log token material.
