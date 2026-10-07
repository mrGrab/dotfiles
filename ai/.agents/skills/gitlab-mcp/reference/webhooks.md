# Webhook Operations

> **Optional toolset**: Enable with `GITLAB_TOOLSETS=webhooks`.

## List, create, update, or delete hooks

Use `list_webhooks` with either `project_id` or `group_id`.

Use `create_webhook` and `update_webhook` to manage a hook. For a group hook, use `group_id` instead of `project_id`.

`delete_webhook` removes a hook. Check the target before you use it. The operation is blocked in permission mode `modify`.

## Review recent events

GitLab provides webhook events from the last seven days. Use `list_webhook_events` to find an event. Set `summary: true` to get a short result. Then use `get_webhook_event` with the event ID to get full details.
