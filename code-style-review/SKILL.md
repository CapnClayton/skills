---
name: code-style-review
description: >-
  Reviews a branch, diff, or file against ten rules for comments,
  docstrings, tests, and names. It reports only the lines the change
  added: ticket keys only on TODOs, no tombstone comments, no rationale
  docstrings, no comments in tests, neutral validation comments, no
  mention of tools not in use, type annotations on new functions, metric
  assertions inside behavior tests, one comment per definition, and names
  that say what they hold or do. Use whenever the user asks to review,
  check, lint, tidy, or clean up a branch, diff, or PR for style,
  comments, names, or hygiene, or asks what to fix before a PR, even if
  they do not name a rule.
user-invocable: true
argument-hint: "[base branch, or a file to review]"
---

# Code style review

A linter finds syntax and format errors. These rules find what a linter
does not: comments, docstrings, tests, names, and the words in them. The
review reports only the lines the change added. It does not grade lines
the change did not touch.

The rule list without the procedure is in
[references/rules.md](references/rules.md). Point other review tooling at
that file when a repo must apply the same rules.

## Usage

```
/code-style-review              # diff the current branch against main
/code-style-review develop      # diff against another base
/code-style-review src/retry.py # review one whole file as new
```

Plain requests trigger the skill too: "check my comments before I open the
PR", "anything in this diff you would flag", "clean up the docstrings on
this branch".

## Scope

- **Added lines only.** Run `git diff -U0 <base>...HEAD` and review the
  `+` lines. A comment that was in the file before the change is out of
  scope, even when it breaks a rule. If an earlier pass removed one, put
  it back.
- **Base branch.** Use the argument. Without one, use `main`, then
  `master`. If neither exists, ask.
- **A file argument** means the whole file is new. Review every line.
- **Uncommitted changes** count. Add `git diff -U0` of the working tree
  to the branch diff.
- **Style feedback from the user** applies to the lines the change added,
  not to the whole file. Do not widen it.
- **Docstring** means any documentation comment: a Python docstring,
  Javadoc, JSDoc, or a `/** */` block. Rules 3, 4, and 9 apply to all of
  them. A block comment reports at its first line.

## Rules

Each rule has a detection hint and a fix. Apply all ten to every added
line.

1. **Ticket keys only on TODOs.** A key such as `PROJ-412` belongs in a
   commit message or a PR title. In code, comments, docstrings, docs, and
   config, it is allowed only as `TODO(PROJ-412)` for work that has not
   landed. Detect: `[A-Z][A-Z0-9]+-[0-9]+` outside a TODO. Fix: describe
   the thing the key points to, or delete the reference.
2. **No tombstone comments.** A comment that describes something the
   change removed ("legacy loop removed", "no longer needed", "replaced
   the old X") describes code that is not there. Fix: delete it. The
   reason goes in the commit or the PR.
3. **No rationale docstrings on small helpers.** A new helper whose name
   and body say what it does gets no docstring. A docstring that stays
   says what the function does. It does not say why the team chose it.
   Detect: "because", "we chose", "so that we", "asked for" in a
   docstring. Fix: delete the docstring, or cut it to one line that says
   what.
4. **No comments in tests.** No docstrings, section banners, or inline
   comments in a test file. The test name and its assertions are the
   documentation. Fix: delete the comment. Rename the test if the name
   did not carry the meaning.
5. **Validation comments are neutral.** Write "Reject unknown currency
   codes". Do not write "so a typo cannot silently retry forever". A
   comment states the rule. The story of what goes wrong without the rule
   goes in the PR. Fix: cut the comment to the rule, or delete it when
   the code already reads as the rule.
6. **Name what is used, not what is not.** No "instead of SQLite", "no
   Alembic", "replaces the old client". A mention of an absent tool makes
   the reader ask whether it is in play. Fix: name the tool in use in a
   positive sentence.
7. **New functions declare types.** In a language with optional
   annotations (Python, TypeScript, PHP), every new function annotates
   its parameters and its return value. Tests are exempt. Use the builtin
   generics (`list[int]`, `X | None`), not the legacy typing aliases.
   Fix: add the annotations from the body and the call sites.
8. **Metric assertions live in behavior tests.** A test whose only
   purpose is to check that a counter or a timer was recorded adds a test
   and no coverage. Fix: move the assertion into the test that already
   exercises the path. Delete the standalone test.
9. **One comment per definition.** A comment sits on the class or the
   function. It is not repeated on each field, argument, or call site.
   Fix: keep the one on the definition and delete the copies.
10. **Names say what they hold or do.** A function name is a verb phrase
    for an action (`send_receipt`) or a noun phrase for the value it
    returns (`backoff_seconds`). A boolean reads as a question
    (`is_retryable`, `has_pool`). A variable names the value, not its
    type or its place in the algorithm: no `tmp`, `val`, `data`, `obj`,
    `flag`, `result2`. Use an abbreviation only when the codebase already
    uses it. The name agrees with the body and with any comment on it: a
    `get_x` or `getX` function does not write, a `count` is an integer, a field
    named `cfg` does not hold a pool. One term per concept across the
    change. Detect: a generic name, a single letter outside an index or
    a comprehension, a name that contradicts its comment or body. Fix:
    rename to the thing it holds or does, and update every use.

## Procedure

1. Resolve the base. Collect the diff with `-U0`, so each hunk header
   gives the new line number of each added line.
2. Walk the added lines of each file once. Test all ten rules on each
   line. A docstring or a multi-line comment counts as one unit; report
   its first line.
3. Report findings grouped by file, in line order. One line per finding:

   ```
   payments/retry.py:14  rule 3  docstring explains why ("We chose exponential backoff because...")  -> delete the docstring
   ```

   Quote enough of the line to find it. Name the fix. Do not repeat the
   rule text.
4. When nothing is flagged, say so in one line and stop.
5. Do not change files unless the user asks. "Fix them" or "clean it up"
   is that ask. When you fix, change only the flagged lines. Then diff
   against the base again and confirm that no unflagged line moved. Show
   the changed lines, not the whole file.

## Out of scope

The skill does not judge logic or structure. It does not run a linter or
a formatter. It does not comment on a PR. It reports in chat, and the
user decides what to carry over.
