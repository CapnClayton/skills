# Code style rules

Ten rules for comments, docstrings, tests, and names. They apply to the
lines a change added. They do not apply to lines that were in a touched
file before the change. The `code-style-review` skill applies them. This
file is the plain list for other tooling that reads a rules file.
"Docstring" means any documentation comment: a Python docstring, Javadoc,
JSDoc, or a `/** */` block.

1. A ticket key (`PROJ-412`) appears in code, comments, docstrings, docs,
   or config only as `TODO(PROJ-412)` for work that has not landed. In all
   other places it belongs in the commit message or the PR title.
2. No comment describes something the change removed. The reason for a
   removal goes in the commit or the PR.
3. A small new helper gets no docstring. A docstring that stays says what
   the function does. It does not say why the team chose that approach.
4. A test file carries no docstrings, section banners, or inline comments.
   The test name and its assertions are the documentation.
5. A validation comment states the rule in neutral words. It does not
   tell the story of what goes wrong without the check.
6. A comment or a doc names the tool in use. It does not mention a tool
   that is not in use. It does not frame a choice as "instead of" or "no
   longer" something else.
7. Every new function in a language with optional type annotations
   declares its parameter types and its return type. Tests are exempt.
   Use the builtin generics, not the legacy typing aliases.
8. No test exists only to check that a metric was recorded. A metric
   assertion goes in the behavior test that already exercises the path.
9. One comment per definition. A comment sits on the class or the
   function. It is not repeated on each field, argument, or call site.
10. A name says what it holds or does. A function name is a verb phrase
    for an action or a noun phrase for the value it returns. A boolean
    reads as a question. A variable names the value, not its type or its
    place in the algorithm. An abbreviation is allowed only when the
    codebase already uses it. The name agrees with the body and with any
    comment on it. One term per concept across the change.
