---
name: jira-leadership-report
description: "Generates a concise, executive-ready Jira report for the Strategic DevOps Squad covering Key Wins, Current Challenges, and Next Priorities over a 2-3 week window."
tools: ["mcp-atlassian/*"]
user-invocable: true
disable-model-invocation: false
---

# Jira Leadership Report

Generate a high-level, outcome-focused report for leadership summarizing recent accomplishments, active risks/blockers, and upcoming strategic work.

## Inputs & Defaults

- **Board URL:** `https://jira.jtiweb.co.uk/secure/RapidBoard.jspa?rapidView=666` (RapidView ID: `666`)
- **Squad Components:** `"Strategic Devops Squad"`, `"Strategic DevOps Squad"`
- **Time Window:** Last 14 days (default)
- **Max Items:** 5–10 high-impact items per section

---

## Data Collection (JQL Rules)

Execute queries against Jira via Atlassian MCP tools using these exact JQL patterns:

1. **Key Wins (Resolved / Delivered):**

```jql
component in ("Strategic Devops Squad", "Strategic DevOps Squad") AND statusCategory = Done AND resolved >= -14d ORDER BY priority DESC, resolved DESC
```

2. **Current Challenges (Active Sprint / In Progress / Blocked):**

```jql
component in ("Strategic Devops Squad", "Strategic DevOps Squad") AND statusCategory != Done AND (status in ("Blocked", "In Progress", "In Review") OR priority in (Critical, Highest, High)) ORDER BY priority DESC
```

3. **Next Priorities (Next Sprint / Backlog):**

```jql
component in ("Strategic Devops Squad", "Strategic DevOps Squad") AND statusCategory = ToDo ORDER BY priority DESC, Rank ASC
```

## Filtering & Synthesis Rules

1. **Impact Filter**: Include only work with high reliability, security, automation, platform migration, or cost/efficiency impact. Omit routine minor tasks.
2. **No Jira Issue Keys**: **NEVER** include Jira keys (e.g., `DESP-1234`, `JTISUPP-9876`, `DAH-189`) in the final output text.
3. **De-duplication**: Merge related tickets (e.g., multiple sub-tasks or terraform modules for one service) into a single strategic statement.
4. **Leadership Phrasing**: Focus on outcomes and business value instead of low-level implementation noise.

## Output Template

Use **exactly** this Markdown format:

**Key wins**:

- [Domain/Area] Outcome delivered → Business or technical impact achieved.
- [Domain/Area] Automation or infrastructure shipped → Risk reduction or speed improvement.

**Current challenges**:

- [Domain/Area] Active blocker or delivery risk → Operational impact and current mitigation step.
- [Domain/Area] Technical dependency or incident response → Resource or timeline constraint.

**Next priorities**:

- [Domain/Area] Upcoming high-value objective → Intended strategic value for the next sprint.
- [Domain/Area] Planned migration or platform upgrade → Target outcome.

## Quality Checks Before Responding

- [ ] Exactly 3 sections are present (**Key wins, Current challenges, Next priorities**).
- [ ] No Jira ticket IDs are present in the text.
- [ ] Every bullet follows the outcome-driven [Domain] format.
- [ ] Items per section do not exceed 10.
- [ ] Stated assumptions in 1 sentence if data was fallback-driven (e.g., "Note: Next priorities are derived from backlog ranking as no future sprint was configured.").
