# Evals

Test material for the `code-style-review` skill, in the layout the
`skill-creator` skill expects.

- `evals.json`: three task prompts with verifiable expectations. The first
  asks for a report only. The second asks for fixes on files that are
  entirely new. The third reviews a Java diff, to check that Javadoc and
  block comments count as docstrings and that the type annotation rule
  stays silent.
- `files/`: the inputs. `style-sample.diff` plants one violation of each
  rule across three Python files. It keeps one unchanged context line with
  a ticket key, to check that the skill ignores lines the change did not
  add. `retry_new.py` and `test_retry_new.py` carry the same violations
  as whole files for the fix eval. `java-sample.diff` plants the same
  violations in Java.
- `trigger-evals.json`: twenty queries. Ten should trigger and ten are
  near misses, for the description optimization loop.

Run with the `skill-creator` skill. All names, keys, and modules in these
files are fictional.
