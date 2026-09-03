# Examples

## 1) Failed Pipeline Investigation

Goal: identify why pipeline `92841` failed in project `134`.

```bash
export GITLAB_BASE_URL="https://gitlab.jtides.com"
uv run scripts/gitlab_cli.py troubleshoot --project-id 134 --pipeline-id 92841
```

Expected result:

- Pipeline state summary
- Failed job IDs and names
- Runner health hints
- Actionable next checks

## 2) Search Variable or Value

Goal: find `DES_TEAM_NAME`.

```bash

uv run scripts/gitlab_cli.py search-variable --term DES_TEAM_NAME
```

## 3) Quick API Preflight

```bash
uv run scripts/gitlab_cli.py preflight
```

Expected result: authenticated user JSON returned by GitLab.
