# Evals

Test material for the `jira-ticket` skill, in the layout the
`skill-creator` skill expects.

- `evals.json`: three task prompts with verifiable expectations. Each
  prompt asks for a draft in chat, so a run needs no Jira access.
- `files/`: the inputs those prompts reference. The brief contains a
  deliberate contradiction (a 900 vs 1800 second default TTL) to check that
  the skill surfaces conflicts instead of resolving them silently. The
  findings file contains a behavior bug to check that it stays out of the
  hygiene ticket.
- `trigger-evals.json`: twenty queries, half should trigger and half are
  near-misses, for the description optimization loop.

Run with the `skill-creator` skill: it spawns each prompt with and
without the skill, grades the expectations, and opens a review viewer.
All names, keys, repos, and services in these files are fictional.
