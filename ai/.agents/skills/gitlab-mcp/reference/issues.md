# Issue Management

## Find issues

- Use `get_issue` to inspect one issue.
- Use `list_issues` to search project issues. Its default scope is issues created by the current user. Set `scope: "all"` to include all issues.
- Use `my_issues` to find issues assigned to the current user across projects.

## Create or update issues

Use `create_issue` to make an issue. Use `update_issue` to change its fields or state.

For a small edit to a long description, use `update_issue_description_patch` instead of sending the full description. Set `patch_type` to `search_replace` or `unified_diff`. Use `dry_run: true` to preview the edit. The tool fails if the patch does not match, matches multiple places without permission, or makes no change.

## Link issues

Use `create_issue_link` to connect issues. Use `list_issue_links` or `get_issue_link` to inspect links. Use `delete_issue_link` to remove a link.

## Notes and discussions

Use `create_issue_note` to add a note or reply to a discussion. Use `list_issue_discussions` to read discussion threads and `update_issue_note` to edit a note. Use `create_note` when one workflow must add a note to either an issue or a merge request.

## Reactions

Use the issue and issue-note emoji reaction tools to list, add, or remove reactions. GitLab emoji names include `thumbsup`, `rocket`, and `eyes`.

## Delete

`delete_issue` permanently removes an issue. Check the project and issue before using it.
