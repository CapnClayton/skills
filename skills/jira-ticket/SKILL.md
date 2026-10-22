---
name: jira-ticket
description: >-
  Creates Jira tickets in a fixed style: a scoped summary, then
  bolded Acceptance Criteria, Description, and Technical Notes sections, each
  with one job and a specified order. Use this whenever the user asks to write,
  draft, create, file, or ticket work in Jira, break an epic, spec, or tech
  brief into tickets, turn code-review findings, dependency bumps, or other
  hygiene items into tickets, or tighten up an existing ticket's description,
  even if they do not say "Jira" or name a section. All ticket prose follows
  ASD-STE100 Simplified Technical English.
---

# Jira tickets

A ticket is read top-down by a reviewer who wants to know, in order: how
will we know it is done, why are we doing it, and where exactly does the
change go. The three sections map to those three questions. Keep each
section doing only its own job so the reader never has to hunt.

Project-specific values (project key, epic keys, custom field ids,
transition ids) live in [references/project-config.md](references/project-config.md).
Read it before any create or edit call. If it still holds placeholders, ask
the user for the values or discover them with the Jira tools, then fill it
in so the next session does not have to.

The Atlassian MCP is the first choice for every Jira read and write. When
it fails to connect, times out, or errors twice on one call, switch to
`acli` (the Atlassian CLI) without asking and follow
[references/acli-fallback.md](references/acli-fallback.md). It maps every
MCP call to an acli command and covers the two differences that matter:
acli takes ADF, not markdown (convert with `scripts/md_to_adf.py`), and
custom fields only go in at create time.

## Summary (title)

- Prefix with the team's scope tag, for example `[Backend]` or `[Frontend]`,
  when the project uses one. The config file records which tags exist.
- When an epic spans milestones, add `M1:` / `M2:` after the prefix, then
  optionally the service name: `[Backend] M1: Inventory: expire reservations ...`.
- Hygiene tickets end with the repo: `... in billing-worker`.
- Name the outcome, not the activity. "Remove unused direct dependencies
  from X" beats "Dependency cleanup".
- Never put a priority marker (P0, P1, Sev) in the summary. Priority is a
  field, and a marker in the title goes stale when the field changes.

## Pick the shape

**Feature ticket** (child of a product epic, usually from a spec or tech
brief):

```
**Acceptance Criteria**
* ...

**Description**
<intent sentence + spec link>
**Blocked by** ... (linked).
<context paragraphs with bolded lead-ins>

**Technical Notes**
Repo: <name>.
* `path/File.java`: ...
```

**Hygiene ticket** (dependency bump, dead code, flag cleanup, under the
team's internal-improvements epic):

```
<one short intro paragraph: what and why>

**Acceptance Criteria**
* ...

**Technical Notes**
* ...
```

Acceptance comes first on feature tickets because the reviewer evaluates
the ticket top-down and wants the testable outcome before the reasoning.
Hygiene tickets are short enough that a one-paragraph intro replaces the
Description section; do not add an empty or padded Description.

## Acceptance Criteria

Each bullet is a check a reviewer or QA could run without reading the code.
Write observable behavior with concrete inputs and outputs:

- Good: "The sweeper releases a reservation created with `ttl_seconds=60`
  within one sweep interval after `expires_at`, and the SKU's `available`
  count rises by the reserved quantity."
- Good: "POST without `ttl_seconds` applies the tenant default."
- Weak: "Expired reservations are handled correctly."

Include the non-code deliverables that gate "done": wiki or runbook
sections, a metric that must increment with named tags, the version bump,
"CI passes" or "the integration tests pass". Include what must *not*
change ("The three existing fields are unchanged", "The sweeper never
releases a reservation confirmed before `expires_at`"). Six to eight
bullets is typical for a feature ticket, two to four for hygiene.

Do not put implementation here. If a bullet names a file or a method, it
belongs in Technical Notes.

## Description

Lead with one sentence of intent, then the spec link with the section that
applies: `Spec: <url> (sections 2 and 4, M1 row "expiry, sweeper")`.

Then, as needed, short paragraphs each opened with a bolded lead-in so
they scan as a list of concerns:

- `**Blocked by** PROJ-402, the schema change (linked).` Name the key in
  the sentence so a reader of the Description alone knows what to wait
  on. Always also create the real Jira Blocks link; text alone is not a
  dependency the board can see.
- `**Clock.**`, `**Idempotency.**`, `**Capacity caveat.**`,
  `**Known loss.**`: one paragraph each for a constraint, accepted
  limitation, or cross-cutting rule the implementer must respect.
- A plain paragraph for data shape (CSV columns, event fields) when the
  AC references them.

If the spec contradicts itself (two sizes for the same column, two names
for one field), say so here and ask. Do not pick one silently; a draft that
quietly resolved a conflict is the kind of thing a reviewer rejects, and
the conflict is usually a real open question.

Keep it to what the implementer needs. No narrative about how the ticket
was produced, no mention of the assistant or the session.

## Technical Notes

Start with `Repo: <name>.` on its own line. One repo per ticket; if the
work spans repos, that is two tickets.

Then one bullet per file, path first, then the specific change:

```
* `service/ReservationService.java` `create`: default `ttlSeconds` from
  `TenantLimits`; reject above the maximum with 400 `ttl_too_long`; set
  `expiresAt`.
* `job/ReservationSweeper.java` (new): the sweep loop.
```

Use a numbered sub-list when the change is an algorithm with ordered steps
(claim, update, commit, publish). Use a `Guards:` sub-list for edge cases
the implementer must handle (publish after commit, clock source, null
legacy rows).

Also put here, as bullets:

- Reuse directives: "The serializer and topic config are reused
  unchanged." This prevents reinvention.
- Metrics: name, type, tags, and what is deliberately excluded ("No
  tenant tag").
- Docs to touch, by page name or path.
- Branch or PR state: an existing PR link, or "a working commit exists on
  branch X; rename to this ticket's key before opening the PR".
- Review hints for hygiene tickets: "Review the HTTP client first. It
  moves from 2.4 to 2.6." and what to leave alone and why ("Leave
  `config-core` in place; the analyzer flags it but it is loaded
  reflectively").

## Atomicity and dependencies

One ticket is one independently mergeable PR in one repo. Split by repo and
by deployable step; ask before folding small tickets together. Order
dependencies with real Blocks links so the board shows them. Keep
behavioral fixes out of a hygiene ticket; note them as "tracked separately"
and file them on their own.

## Fields and workflow

Issue type is Task, even for bug-shaped fixes, unless the config file says
otherwise. Hygiene and hardening go under the internal-improvements epic;
feature work reuses the existing product epic. Use the project's lowest
default priority unless told otherwise.

Show the draft in chat before creating anything in Jira. The exception: a
findings report already shown in chat counts as the draft when the user
says "create tickets for items N and M". For hygiene tickets the usual
request is create, add to current sprint, assign to the user, move to In
Progress, then In Review, all in one go.

Two worked examples, one of each shape, are in
[references/examples.md](references/examples.md). Read them when drafting
a ticket type you have not written in this session.

## Prose style

Write every sentence in the ticket in ASD-STE100 Simplified Technical
English. A ticket is read by people who did not attend the design
conversation, often months later, and sometimes in a second language. STE
removes the ambiguity that a reviewer would otherwise have to ask about.

- **Short sentences.** At most 20 words in an instruction, 25 in a
  description. One idea per sentence. Split rather than join with "and",
  "which", or a semicolon.
- **Active voice, named agent.** Say who does the action. "The sweeper
  releases the row", not "the row is released". "`ReservationService`
  rejects the request", not "the request gets rejected".
- **Instructions start with the verb.** In Technical Notes: "Clamp
  `end_date` to the job start time", not "`end_date` should be clamped".
- **One term per concept.** Pick "reservation" and never switch to "hold"
  or "lock" for style. Pick "release" and do not drift to "free" or
  "expire" when you mean the same action.
- **One meaning per word.** "Close" is either the state transition or the
  UI action, never both in one ticket.
- **Define abbreviations at first use**, abbreviation first and the
  expansion in parentheses: "a TTL (time to live)", "the SKU (stock
  keeping unit)". After that, use the abbreviation alone. Skip only the
  ones every engineer reads without thinking: API, CI, PR, URL, JSON,
  HTTP, SQL, SDK.
- **No gerunds as nouns or adjectives.** "The sweep claims 500 rows", not
  "the sweeping of rows". "Expired reservations", not "expiring
  reservations" when you mean ones already past `expires_at`.
- **No idioms, hedges, or figurative language.** No "should just work",
  "a bit flaky", "nuke the cache". Say what happens.
- **Articles and demonstratives.** "the row", "this reservation", so the
  reader knows which one.
- **Paragraphs of six sentences or fewer, one topic each.** The bolded
  lead-ins in Description exist for this.

Before you show the draft, reread each sentence and apply the rules above.
A sentence that resists them usually hides two ideas or a missing agent.

Markdown renders through the Atlassian MCP; use `*` bullets and backticks
for identifiers. acli does not render markdown: when on the acli
fallback, draft the same markdown, then convert it with
`scripts/md_to_adf.py` before the call. Ticket keys do not belong in code
or docs content, only in commit and PR titles and `TODO(KEY)` markers.
