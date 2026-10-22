# skills
* I do not condone the use of generative AI.
* I do not support "AI Art"
* Datacenter sprawl is accelerating the destruction our environment

Unfortunately, I have to step into this space professionally so at
minimum I can try and make the best of it. Here are generic skills
that may help others navigate this [sloppy](https://www.youtube.com/watch?v=UXWmgX-V02k) era.

## Installing

Two routes.

**As a plugin.** Register this repo as a marketplace once, then install
the plugin. Skills are then invoked with the plugin prefix, for example
`/skills:jira-ticket`.

```
/plugin marketplace add CapnClayton/skills
/plugin install skills@capnclayton
```

**As plain skills.** Copy a directory from `skills/` into
`~/.claude/skills/` (user-level) or into `.claude/skills/` inside a
project. Claude Code picks it up on the next session, and the skill keeps
its short name, for example `/jira-ticket`.

Each skill is self-contained: a `SKILL.md` with the instructions, optional
`references/` the skill reads on demand, optional `scripts/` it runs, and
optional `evals/` for testing it with the `skill-creator` skill.

## Skills

| Skill                       | Purpose                                                                                                                                                                               | Notes                                                                                           |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| [code-style-review](skills/code-style-review/) | Reviews a branch, diff, or file against ten rules for comments, docstrings, tests, and names. It reports only the lines the change added. It fixes on request. | `references/rules.md` is the plain rule list for other review tooling. Ships with evals. |
| [jira-ticket](skills/jira-ticket/) | Drafts and files Jira tickets in a fixed shape: scoped summary, then Acceptance Criteria, Description, and Technical Notes, each with one job. Prose in Simplified Technical English. | Fill in `references/project-config.md` with your project's ids before filing. Falls back to the `acli` CLI when the Atlassian MCP is down; `scripts/md_to_adf.py` converts the draft to ADF for it. Ships with evals. |
