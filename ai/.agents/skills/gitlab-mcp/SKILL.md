---
name: gitlab-mcp-skill
description: Use this skill when working with GitLab MCP tools for merge requests, issues, repositories, pipelines, work items, variables, dependency proxy, vulnerabilities, webhooks, search, CI catalog, and related GitLab workflows.
---

# gitlab-mcp

The GitLab MCP server provides 268 tools: 266 unique tools across 22 toolsets, plus `execute_graphql` and the `discover_tools` meta-tool.

The tool counts include duplicate entries: `get_branch` and `list_branches` appear in both the `merge_requests` and `branches` toolsets.

For exact parameter details, see the [upstream generated tool documentation](https://github.com/zereight/gitlab-mcp/tree/main/docs/tools/). These files are in the upstream repository, not in this local skill folder. Use this file for the main workflows and key parameter rules.

## Toolsets

| Toolset          | Tools | Enabled by default | How to enable                                        |
| ---------------- | ----: | ------------------ | ---------------------------------------------------- |
| merge_requests   |    45 | yes                | -                                                    |
| issues           |    24 | yes                | -                                                    |
| repositories     |     7 | yes                | -                                                    |
| branches         |    15 | yes                | -                                                    |
| projects         |    11 | yes                | -                                                    |
| labels           |     5 | yes                | -                                                    |
| ci               |     4 | yes                | -                                                    |
| groups           |     1 | yes                | -                                                    |
| users            |     7 | yes                | -                                                    |
| pipelines        |    56 | no                 | `USE_PIPELINE=true` or `GITLAB_TOOLSETS=pipelines`   |
| milestones       |    17 | no                 | `USE_MILESTONE=true` or `GITLAB_TOOLSETS=milestones` |
| wiki             |    10 | no                 | `USE_GITLAB_WIKI=true` or `GITLAB_TOOLSETS=wiki`     |
| releases         |     7 | no                 | `GITLAB_TOOLSETS=releases`                           |
| tags             |     5 | no                 | `GITLAB_TOOLSETS=tags`                               |
| snippets         |     5 | no                 | `GITLAB_TOOLSETS=snippets`                           |
| workitems        |    18 | no                 | `GITLAB_TOOLSETS=workitems`                          |
| webhooks         |     6 | no                 | `GITLAB_TOOLSETS=webhooks`                           |
| search           |     3 | no                 | `GITLAB_TOOLSETS=search`                             |
| variables        |    10 | no                 | `GITLAB_TOOLSETS=variables`                          |
| dependency_proxy |     4 | no                 | `GITLAB_TOOLSETS=dependency_proxy`                   |
| vulnerabilities  |     4 | no                 | `GITLAB_TOOLSETS=vulnerabilities`                    |
| orbit            |     4 | no                 | `GITLAB_TOOLSETS=orbit`                              |

To enable all toolsets, set `GITLAB_TOOLSETS=all`.

To enable individual tools outside their toolset, use `GITLAB_TOOLS`.

Use `discover_tools` to list and enable optional toolsets for the current session. `execute_graphql` is not part of a toolset. To enable it, set `GITLAB_TOOLS=execute_graphql`.

## Key Workflows

### Code Review (see `reference/code-review.md`)

1. Use `list_merge_request_changed_files` to get file paths without diffs.
2. Use `get_merge_request_file_diff` to get diffs. Request 3-5 files in each call.
3. Use `create_merge_request_thread` or `create_draft_note` to add review comments.
4. Use `bulk_publish_draft_notes` to publish all draft comments.

### MR Lifecycle (see reference/merge-requests.md)

Use this order: `create_merge_request` -> review -> `approve_merge_request` -> `merge_merge_request`.

### Issue Management (see reference/issues.md)

Use this order: `create_issue` -> `create_issue_link` -> `create_issue_note` -> `update_issue`.

For a small change to a long issue description, use `update_issue_description_patch`. Do not send the full description again.

### Projects & Namespaces

- Use `get_project` or `list_projects` to inspect projects. Use `update_project` to change project settings.
- Use `list_project_members` or `list_group_members` to find members by name or username.
- Use `list_namespaces`, `get_namespace`, or `verify_namespace` to find the target namespace before you create a project or group.
- Set `verify_namespace.parent_id` to check a nested namespace.
- Set `create_repository.namespace_id` to create a project in a group namespace.

### Branches & Commits

- Branch tools: `create_branch`, `list_branches`, `get_branch`, `delete_branch`.
- Protected branch tools: `list_protected_branches`, `get_protected_branch`, `protect_branch`, `unprotect_branch`, `update_default_branch`.
- Commit tools: `list_commits`, `get_commit`, `get_commit_diff`, `get_file_blame`, `list_commit_statuses`, `create_commit_status`.

### CI

- To check CI configuration, use `validate_ci_lint` or `validate_project_ci_lint`.
- To find CI catalog resources, use `list_ci_catalog_resources` or `get_ci_catalog_resource`.
- For pipeline, job, and deployment workflows, see `reference/pipelines.md`.

### Work Items (see reference/work-items.md)

Use this order: `list_work_items` -> `get_work_item` -> `update_work_item` -> `create_work_item_note`.

### Variables & Dependency Proxy

Enable the toolsets with `GITLAB_TOOLSETS=variables` or `GITLAB_TOOLSETS=dependency_proxy`.

- Variable tools: project and group tools to list, get, create, update, or delete variables. Tool names include `list_*_variables`, `get_*_variable`, `create_*_variable`, `update_*_variable`, and `delete_*_variable`.
- Dependency proxy tools: `get_dependency_proxy_settings`, `update_dependency_proxy_settings`, `list_dependency_proxy_blobs`, `purge_dependency_proxy_cache`.

### Webhooks & Search

- For webhook workflows, see `reference/webhooks.md`.
- For code search, see `reference/search.md`.

### Vulnerability Triage (see `reference/vulnerability-triage.md`)

Enable this toolset with `GITLAB_TOOLSETS=vulnerabilities`. It requires GitLab Ultimate.

Use `list_project_vulnerabilities` and `get_vulnerability` to inspect findings. Use `dismiss_vulnerability` to dismiss a finding with a reason, or `confirm_vulnerability` to confirm it. Do not mark vulnerabilities as resolved directly. GitLab resolves them after a later pipeline no longer reports them.

### File Operations

- To read files, use `get_file_contents` or `get_repository_tree`.
- To write one file, use `create_or_update_file`. To write multiple files in one commit, use `push_files`.

## Parameter Hints

- **project_id**: Use a numeric ID or a URL-encoded path, such as `group%2Fsubgroup%2Fproject`.
- **namespace_id**: For `create_repository`, use the numeric namespace ID. First, use `list_namespaces` or `verify_namespace`.
- **parent_id**: Use this to scope subgroup creation or to check a nested group with `verify_namespace`.
- **MR lookup**: Provide `mergeRequestIid` or `branchName`, but not both.
- **list_issues**: The default scope is issues created by the current user. Use `scope: "all"` to list all issues.
- **list_merge_requests**: If you do not provide `project_id`, the tool returns the user's merge requests across all projects.
- **CI catalog lookup**: Provide one field only: `id` or `full_path`.
- **Emoji reactions**: Merge request, issue, and work item reaction tools use GitLab emoji names, such as `thumbsup`, `rocket`, or `eyes`.
- **Work items**: Status and custom fields require GitLab Premium or Ultimate.
- **execute_graphql**: Escape double quotes in query strings.

## Tools That Need Care

The following tools can change remote data or trigger an action. Check the target and expected result before you use one:

- `approve_deployment`
- `cancel_pipeline`
- `cancel_pipeline_job`
- `delete_branch`
- `delete_deployment`
- `delete_draft_note`
- `delete_environment`
- `delete_group_milestone`
- `delete_group_variable`
- `delete_group_wiki_page`
- `delete_issue`
- `delete_issue_emoji_reaction`
- `delete_issue_link`
- `delete_issue_note_emoji_reaction`
- `delete_label`
- `delete_merge_request_discussion_note`
- `delete_merge_request_emoji_reaction`
- `delete_merge_request_note`
- `delete_merge_request_note_emoji_reaction`
- `delete_milestone`
- `delete_pipeline`
- `delete_pipeline_schedule`
- `delete_pipeline_schedule_variable`
- `delete_pipeline_trigger`
- `delete_project_variable`
- `delete_release`
- `delete_review_app_environments`
- `delete_snippet`
- `delete_tag`
- `delete_webhook`
- `delete_wiki_page`
- `delete_work_item_emoji_reaction`
- `delete_work_item_note_emoji_reaction`
- `erase_pipeline_job`
- `merge_merge_request`
- `protect_branch`
- `purge_dependency_proxy_cache`
- `push_files`
- `stop_environment`
- `stop_stale_environments`
- `unprotect_branch`
- `update_default_branch`

## Other Tools

- **Dynamic discovery**: Use `discover_tools` to list and enable optional toolsets during the session.
- **GraphQL**: Use `execute_graphql` for queries that the REST tools do not support.
- **Tool documentation**: The [upstream `docs/tools/` folder](https://github.com/zereight/gitlab-mcp/tree/main/docs/tools/) contains generated parameter details from `tools/registry.ts`.
- **Remote MCP OAuth**: With `GITLAB_MCP_OAUTH=true`, `POST /register` uses a per-client IP rate limit. See [environment variables](https://github.com/zereight/gitlab-mcp/blob/main/docs/configuration/environment-variables.md#oauth_register_rate_limit_per_hour) for configuration.
- **Zoekt search**: Use `search_code`, `search_project_code`, or `search_group_code`. Advanced search must be enabled.
- **Work items**: Work items use GraphQL. They are an alternative to issues and require GitLab Premium or Ultimate.
