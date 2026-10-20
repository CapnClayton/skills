# Project configuration

Fill this in once per Jira site. Values in angle brackets are placeholders.
Custom field ids differ per site, so never guess them; discover them with
the steps below and record them here.

Site: `<https://your-site.atlassian.net>`
Cloud id: `<uuid from getAccessibleAtlassianResources>`
Default assignee account id: `<accountId from atlassianUserInfo>`

## Project

| Thing                                | Value                                              |
|--------------------------------------|----------------------------------------------------|
| Project key                          | `<PROJ>`                                           |
| Board id                             | `<board id>`                                       |
| Sprint field                         | `<customfield_NNNNN>` (numeric sprint id)          |
| Internal-improvements / hygiene epic | `<PROJ-NN>`                                        |
| Scope tags used in summaries         | `[Backend]`, `[Frontend]`                          |
| Issue type ids                       | Task `<id>`, Story `<id>`, Bug `<id>`, Epic `<id>` |
| Transition ids                       | In Progress `<id>`, In Review `<id>`, Done `<id>`  |
| Default priority                     | `<lowest severity name>`                           |

Note here any rule the hygiene epic sets on what may be pulled into the
active sprint without triage (for example, "under two days of effort").

## Discovering the values

- Cloud id: `getAccessibleAtlassianResources` once per session.
- Field ids: `getJiraIssueTypeMetaWithFields` for the project and Task
  type, or read any existing ticket with `view: "evidence"` and note the
  `customFields` ids.
- Transition ids: `getTransitionsForJiraIssue` on any open ticket.
- Active sprint: JQL `project = <PROJ> AND sprint in openSprints()`.
- Future sprints: `listJiraBoardSprints {boardId, state: "future"}`. JQL
  cannot see a sprint that has no issues yet.

## Create

Use `createJiraIssue` with a markdown description. Set everything in one
call so the ticket lands ready to work:

```
project: <PROJ>
issueType: Task
summary: "[Backend] ..."
description: <markdown>
additional_fields:
  parent: {key: "<PROJ-NN>"}
  <sprint field>: <sprint id>
  assignee: {accountId: "<account id>"}
```

## Edit

Some Task screens reject a custom field by its display name ("not found in
the project's issue type metadata"). Pass the raw id in `fields` instead.
The edit response does not echo the value; confirm with a JQL search that
requests the field.

## Links

Create dependencies with `createIssueLink` (type Blocks). A "Blocked by"
sentence in the description is for the reader; the link is for the board.

## After create

Branch name equals the ticket key. Commit and PR titles start with the
ticket key.
