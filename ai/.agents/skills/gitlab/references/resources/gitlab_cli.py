#!/usr/bin/env python3
"""GitLab self-hosted operations CLI."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import click
import gitlab
import gitlab.exceptions

try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.table import Table

    _console: Console | None = Console()
    HAS_RICH = True
except ImportError:
    _console = None
    HAS_RICH = False

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ENV_FAMILIES: list[frozenset[str]] = [
    frozenset({"eph", "dev", "qa"}),
    frozenset({"test", "stage"}),
    frozenset({"stg", "prod", "prd"}),
]

VARIABLE_PRECEDENCE: tuple[str, ...] = ("pipeline", "project", "group", "instance")


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------


@dataclass
class Settings:
    base_url: str
    token: str
    ssl_verify: bool = True
    timeout: int = 30


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class GitLabClient:
    """Thin, extensible wrapper around python-gitlab.

    All API calls live here. Commands only hold CLI concerns.
    """

    def __init__(self, settings: Settings) -> None:
        self._gl = gitlab.Gitlab(
            url=settings.base_url,
            private_token=settings.token,
            ssl_verify=settings.ssl_verify,
            timeout=settings.timeout,
        )
        try:
            self._gl.auth()
        except gitlab.GitlabAuthenticationError as exc:
            raise click.ClickException(f"Authentication failed: {exc}") from exc
        except gitlab.GitlabConnectionError as exc:
            raise click.ClickException(f"Connection failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------

    def current_user(self) -> dict[str, Any]:
        u = self._gl.user
        return {"id": u.id, "username": u.username, "name": u.name}

    # ------------------------------------------------------------------
    # Pipelines & jobs
    # ------------------------------------------------------------------

    def pipeline_info(self, project_id: int, pipeline_id: int) -> dict[str, Any]:
        p = self._gl.projects.get(project_id).pipelines.get(pipeline_id)
        return {
            "id": p.id,
            "status": p.status,
            "ref": p.ref,
            "sha": p.sha,
            "source": p.source,
            "web_url": p.web_url,
        }

    def failed_jobs(self, project_id: int, pipeline_id: int) -> list[Any]:
        pipeline = self._gl.projects.get(project_id).pipelines.get(pipeline_id)
        return [j for j in pipeline.jobs.list(get_all=True) if j.status == "failed"]

    def job_trace(self, project_id: int, job_id: int) -> list[str]:
        try:
            raw = self._gl.projects.get(project_id).jobs.get(job_id).trace()
            return raw.splitlines() if isinstance(raw, str) else []
        except gitlab.GitlabGetError:
            return ["trace unavailable"]

    def runner_info(self, runner_id: int) -> dict[str, Any]:
        try:
            r = self._gl.runners.get(runner_id)
            return {
                "id": r.id,
                "description": getattr(r, "description", None),
                "online": getattr(r, "online", None),
                "active": getattr(r, "active", None),
                "paused": getattr(r, "paused", None),
                "status": getattr(r, "status", None),
            }
        except gitlab.GitlabGetError:
            return {"id": runner_id, "error": "runner details unavailable"}

    # ------------------------------------------------------------------
    # Variables
    # ------------------------------------------------------------------

    def search_variables(
        self,
        term: str,
        search_groups: bool,
        search_projects: bool,
        visibility: str,
    ) -> list[dict[str, Any]]:
        """Substring search in key OR value across all accessible groups/projects."""
        hits: list[dict[str, Any]] = []

        def _scan(entity: Any, entity_type: str) -> None:
            entity_name = getattr(entity, "name", "N/A")

            try:
                variables = entity.variables.list(all=True, iterator=True)
            except gitlab.exceptions.GitlabListError:
                _log(
                    f"Skipping {entity_type} '{entity_name}': no access or no variables"
                )
                return

            for var in variables:
                if (var.key and term in var.key) or (var.value and term in var.value):
                    hits.append(
                        {
                            "entity_type": entity_type,
                            "entity_id": entity.id,
                            "entity_name": entity_name,
                            "web_url": getattr(entity, "web_url", None),
                            "key": var.key,
                            "value": var.value,
                            "environment_scope": getattr(var, "environment_scope", "*"),
                        }
                    )

        if search_groups:
            for group in self._gl.groups.list(
                all=True, visibility=visibility, archived=False, iterator=True
            ):
                _scan(group, "Group")

        if search_projects:
            for project in self._gl.projects.list(
                all=True, visibility=visibility, archived=False, iterator=True
            ):
                _scan(project, "Project")

        return hits


# ---------------------------------------------------------------------------
# Pure helpers
# ---------------------------------------------------------------------------


def _normalize_env(name: str | None) -> str | None:
    if not name:
        return None
    lowered = name.strip().lower()
    for family in ENV_FAMILIES:
        if lowered in family:
            return sorted(family)[0]
    return lowered


def _env_matches(scope: str | None, requested_env: str | None) -> bool:
    if not requested_env:
        return True
    if (scope or "*").strip() == "*":
        return True
    return _normalize_env(scope) == _normalize_env(requested_env)


def _filter_vars(
    variables: list[dict[str, Any]], key: str, environment: str | None
) -> list[dict[str, Any]]:
    return [
        v
        for v in variables
        if v.get("key") == key and _env_matches(v.get("environment_scope"), environment)
    ]


def _format_var(var: dict[str, Any], scope: str, show_values: bool) -> dict[str, Any]:
    return {
        "scope": scope,
        "key": var.get("key"),
        "environment_scope": var.get("environment_scope", "*"),
        "masked": bool(var.get("masked", False)),
        "protected": bool(var.get("protected", False)),
        "value": var.get("value", "") if show_values else "<redacted>",
    }


def _log(message: str) -> None:
    if HAS_RICH and _console is not None:
        _console.log(message)
    else:
        click.echo(message, err=True)


def _emit(data: Any, output_format: str) -> None:
    """Render data as JSON or Rich pretty table depending on --output."""
    if output_format == "json" or not HAS_RICH or _console is None:
        click.echo(json.dumps(data, indent=2, sort_keys=True, default=str))
        return

    if isinstance(data, list):
        if not data:
            _console.print("[dim]No results.[/dim]")
            return
        table = Table(show_header=True, header_style="bold cyan")
        for col in data[0]:
            table.add_column(str(col))
        for row in data:
            table.add_row(
                *[
                    json.dumps(v, default=str)
                    if isinstance(v, (dict, list))
                    else str(v)
                    for v in row.values()
                ]
            )
        _console.print(table)

    elif isinstance(data, dict):
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold")
        table.add_column("Value")
        for k, v in data.items():
            table.add_row(
                str(k),
                json.dumps(v, default=str) if isinstance(v, (dict, list)) else str(v),
            )
        _console.print(table)

    else:
        _console.print(str(data))


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


@click.group()
@click.option(
    "--base-url",
    envvar="GITLAB_BASE_URL",
    default="https://gitlab.jtides.com",
    show_default=True,
    help="Self-hosted GitLab base URL",
)
@click.option("--token", envvar="GITLAB_ACCESS_TOKEN", required=True, help="GitLab PAT")
@click.option(
    "--no-ssl-verify",
    is_flag=True,
    default=False,
    help="Disable SSL certificate verification",
)
@click.option(
    "--timeout", type=int, default=30, show_default=True, help="HTTP timeout in seconds"
)
@click.option(
    "--output",
    type=click.Choice(["json", "pretty"]),
    default="json",
    show_default=True,
    envvar="GITLAB_CLI_OUTPUT",
    help="Output format (pretty requires rich)",
)
@click.pass_context
def cli(
    ctx: click.Context,
    base_url: str,
    token: str,
    no_ssl_verify: bool,
    timeout: int,
    output: str,
) -> None:
    """Interact with a self-hosted GitLab instance for CI/CD troubleshooting and variable lookup."""
    ctx.ensure_object(dict)
    ctx.obj["settings"] = Settings(
        base_url=base_url.rstrip("/"),
        token=token,
        ssl_verify=not no_ssl_verify,
        timeout=timeout,
    )
    ctx.obj["output"] = output


def _client(ctx: click.Context) -> GitLabClient:
    return GitLabClient(ctx.obj["settings"])


def _fmt(ctx: click.Context) -> str:
    return ctx.obj["output"]


# ------------------------------------------------------------------
# preflight
# ------------------------------------------------------------------


@cli.command()
@click.pass_context
def preflight(ctx: click.Context) -> None:
    """Validate API access and return authenticated user info."""
    _emit(_client(ctx).current_user(), _fmt(ctx))


# ------------------------------------------------------------------
# troubleshoot
# ------------------------------------------------------------------


@cli.command()
@click.option("--project-id", type=int, required=True)
@click.option("--pipeline-id", type=int, required=True)
@click.option(
    "--include-traces",
    is_flag=True,
    default=False,
    help="Append job trace lines to each failed job",
)
@click.option(
    "--trace-lines",
    type=int,
    default=20,
    show_default=True,
    help="Number of trace lines when --include-traces is set",
)
@click.pass_context
def troubleshoot(
    ctx: click.Context,
    project_id: int,
    pipeline_id: int,
    include_traces: bool,
    trace_lines: int,
) -> None:
    """Summarize failed jobs, runner health, and next checks for a pipeline."""
    client = _client(ctx)
    failed = client.failed_jobs(project_id, pipeline_id)

    seen: set[int] = set()
    runner_health: list[dict[str, Any]] = []
    for job in failed:
        runner_id = (getattr(job, "runner", None) or {}).get("id")
        if runner_id and runner_id not in seen:
            seen.add(runner_id)
            runner_health.append(client.runner_info(runner_id))

    failed_summaries: list[dict[str, Any]] = []
    for job in failed:
        entry: dict[str, Any] = {
            "id": job.id,
            "name": job.name,
            "stage": job.stage,
            "status": job.status,
            "allow_failure": getattr(job, "allow_failure", None),
            "runner_id": (getattr(job, "runner", None) or {}).get("id"),
            "web_url": getattr(job, "web_url", None),
        }
        if include_traces:
            entry["trace_head"] = client.job_trace(project_id, job.id)[:trace_lines]
        failed_summaries.append(entry)

    _emit(
        {
            "pipeline": client.pipeline_info(project_id, pipeline_id),
            "failed_jobs": failed_summaries,
            "runner_health": runner_health,
            "next_checks": [
                "Inspect failed traces for auth, artifact, cache, and image pull errors",
                "Validate runner tags and job tag routing",
                "Validate rules and needs/dependency graph for skipped prerequisites",
            ],
        },
        _fmt(ctx),
    )


# ------------------------------------------------------------------
# list-variables
# ------------------------------------------------------------------


@cli.command("list-variables")
@click.option("--project-id", type=int)
@click.option("--group-id", type=int)
@click.option(
    "--environment", type=str, help="Filter by environment scope (uses family matching)"
)
@click.option(
    "--show-values", is_flag=True, default=False, help="Print variable values in output"
)
@click.pass_context
def list_variables(
    ctx: click.Context,
    project_id: int | None,
    group_id: int | None,
    environment: str | None,
    show_values: bool,
) -> None:
    """List all CI/CD variables for a project or group, optionally filtered by environment."""
    client = _client(ctx)
    rows: list[dict[str, Any]] = []

    if group_id is not None:
        for var in client.group_variables(group_id):
            if _env_matches(var.get("environment_scope"), environment):
                rows.append(_format_var(var, "group", show_values))

    if project_id is not None:
        for var in client.project_variables(project_id):
            if _env_matches(var.get("environment_scope"), environment):
                rows.append(_format_var(var, "project", show_values))

    _emit(rows, _fmt(ctx))


# ------------------------------------------------------------------
# job-trace
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# search-variable
# ------------------------------------------------------------------


@cli.command("search-variable")
@click.option(
    "--term", required=True, help="Substring to match against variable keys and values"
)
@click.option(
    "--no-groups", is_flag=True, default=False, help="Skip group variable search"
)
@click.option(
    "--no-projects", is_flag=True, default=False, help="Skip project variable search"
)
@click.option(
    "--visibility",
    type=click.Choice(["internal", "private", "public"]),
    default="internal",
    show_default=True,
    help="Visibility filter for groups and projects",
)
@click.pass_context
def search_variable(
    ctx: click.Context,
    term: str,
    no_groups: bool,
    no_projects: bool,
    visibility: str,
) -> None:
    """Search all groups and projects for variables whose key or value contains TERM."""
    client = _client(ctx)
    fmt = _fmt(ctx)

    _log(
        f"Searching for '{term}' in {'groups ' if not no_groups else ''}{'projects' if not no_projects else ''}..."
    )

    hits = client.search_variables(
        term=term,
        search_groups=not no_groups,
        search_projects=not no_projects,
        visibility=visibility,
    )

    if fmt == "pretty" and HAS_RICH and _console is not None:
        from rich.table import Table as RTable

        table = RTable(show_header=True, header_style="bold cyan")
        for col in (
            "entity_type",
            "entity_id",
            "entity_name",
            "key",
            "value",
            "environment_scope",
            "web_url",
        ):
            table.add_column(col)
        for h in hits:
            table.add_row(
                h["entity_type"],
                str(h["entity_id"]),
                h["entity_name"],
                h["key"],
                h["value"],
                h["environment_scope"],
                h.get("web_url") or "",
            )
        _console.print(table)
    else:
        _emit(hits, fmt)


# ------------------------------------------------------------------
# job-trace
# ------------------------------------------------------------------


@cli.command("job-trace")
@click.option("--project-id", type=int, required=True)
@click.option("--job-id", type=int, required=True)
@click.option(
    "--lines", type=int, default=50, show_default=True, help="Max lines to print"
)
@click.pass_context
def job_trace(ctx: click.Context, project_id: int, job_id: int, lines: int) -> None:
    """Print the trace (log) of a specific job."""
    trace = _client(ctx).job_trace(project_id, job_id)[:lines]
    if HAS_RICH and _console is not None and _fmt(ctx) == "pretty":
        _console.print(
            Syntax("\n".join(trace), "bash", theme="monokai", line_numbers=True)
        )
    else:
        click.echo("\n".join(trace))


if __name__ == "__main__":
    cli()
