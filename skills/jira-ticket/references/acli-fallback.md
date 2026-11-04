# acli fallback for the Atlassian MCP

The Atlassian MCP is the first choice. Fall back to `acli` (the Atlassian
CLI) when the MCP server fails to connect, times out, or returns an error
twice for the same call. Do not ask before falling back; say in the reply
that acli was used. Do not retry the MCP in the same turn after switching.

Project key, board id, custom field ids, and the hygiene epic are in
[project-config.md](project-config.md). Everything there except the MCP
call shapes applies unchanged. `<PROJ>`, `<board id>`, `<sprint field>`
and `<PROJ-NN>` below are those values.

## Preflight

```
acli jira auth status
```

If it reports `unauthorized`, stop and ask the user to run
`acli jira auth login --web` in their own shell (in Claude Code, typing
`! acli jira auth login --web` runs it in the session). Do not try to log
in or read credential stores yourself.

## Two rules that differ from the MCP

1. **Descriptions and comments are plain text or ADF, never markdown.**
   acli does not render markdown. Write the draft as markdown as usual,
   then convert it with the skill's script before any create, edit, or
   comment:

   ```
   python3 <skill dir>/scripts/md_to_adf.py ticket.md > ticket.adf.json
   ```

   The script handles the full house style: bold section lines, `*`
   bullets, numbered sub-lists, backtick code, links, bare URLs. Keep the
   markdown file in the scratchpad.

2. **Custom fields only go in at create time.** The sprint field, story
   points, and any other custom field are set through the
   `additionalAttributes` block of `--from-json`. `workitem edit` has no
   custom-field flag, so set them on create. To change them later, wait
   for the MCP or do it in the Jira UI, and say so.

## Command map

| Skill step                 | MCP                        | acli                                                                                                              |
|----------------------------|----------------------------|-------------------------------------------------------------------------------------------------------------------|
| Find active sprint         | `getJiraBoardSprintData`   | `acli jira board list-sprints --id <board id> --state active --json`                                              |
| Find future sprints        | `listJiraBoardSprints`     | `acli jira board list-sprints --id <board id> --state future --json`                                              |
| JQL search                 | `searchJiraIssuesUsingJql` | `acli jira workitem search --jql "..." --json` (search allows only its default fields; custom fields need `view`) |
| Read a ticket              | `getJiraIssue`             | `acli jira workitem view <PROJ>-123 --fields '*all' --json`                                                       |
| Create                     | `createJiraIssue`          | `acli jira workitem create --from-json create.json --json`                                                        |
| Edit summary / description | `editJiraIssue`            | `acli jira workitem edit --key <PROJ>-123 --summary "..." --description-file ticket.adf.json --yes`               |
| Edit labels                | `editJiraIssue`            | `acli jira workitem edit --key <PROJ>-123 --labels needs-decision --yes` (or `--remove-labels`)                   |
| Assign                     | `editJiraIssue`            | `acli jira workitem assign --key <PROJ>-123 --assignee @me --yes`                                                 |
| Transition                 | `transitionJiraIssue`      | `acli jira workitem transition --key <PROJ>-123 --status "In Progress" --yes`                                     |
| Comment                    | `addCommentToJiraIssue`    | `acli jira workitem comment create --key <PROJ>-123 --body-file comment.adf.json`                                 |
| Blocks link                | `createIssueLink`          | `acli jira workitem link create --out <PROJ>-401 --in <PROJ>-402 --type Blocks --yes`                             |
| Link types                 | n/a                        | `acli jira workitem link type`                                                                                    |

Transitions take the target status name, not the transition id. Links
take the outward description: `--out A --in B --type Blocks` means
"A blocks B". Always pass `--yes` on write commands so they do not block
on a prompt. Always pass `--json` on reads so the output is parseable.

## Create, end to end

Write the draft to the scratchpad as `ticket.md`, show it in chat as
usual, then after approval:

```
python3 <skill dir>/scripts/md_to_adf.py ticket.md \
  --wrap-create \
  --project <PROJ> \
  --summary "[Backend] ..." \
  --parent <PROJ-NN> \
  --assignee <account id> \
  --field <sprint field>=<sprint id> \
  --label needs-decision \        # only when a decision is open
  > create.json
acli jira workitem create --from-json create.json --json
```

`--field` is repeatable and takes the raw custom field id, so story
points or any other site-specific field go in the same way.
`--wrap-create` emits the body acli expects: `projectKey`, `type`,
`summary`, ADF `description`, `assignee`, `labels`, `parentIssueId`, and
`additionalAttributes` with the custom fields. Read the key from the JSON
response.

**Assignee.** acli's `--from-json` does not resolve the `@me` alias (only
the `--assignee` flag on `workitem assign` does). Pass the account id from
[project-config.md](project-config.md), instead. Confirm the assignee with the view below
after every create, and fix a wrong one with 
`acli jira workitem assign --key <PROJ>-123 --assignee @me --yes`.

If `parentIssueId` rejects the key, look up the numeric id with
`acli jira workitem view <PROJ-NN> --fields id --json` and pass that.

## Hygiene flow (create, sprint, assign, In Progress, In Review)

Sprint and assignee go in the create call above. Then:

```
acli jira workitem transition --key <PROJ>-123 --status "In Progress" --yes
acli jira workitem transition --key <PROJ>-123 --status "In Review" --yes
```

## Confirming a write

acli write responses do not always echo the field. Confirm with a view:

```
acli jira workitem view <PROJ>-123 --fields summary,status,assignee,parent,<sprint field> --json
```
