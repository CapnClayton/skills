#!/usr/bin/env python3
"""Convert house-style ticket markdown to Atlassian Document Format (ADF).

acli accepts only plain text or ADF for descriptions and comments, so the
markdown the jira-ticket skill drafts must be converted before
`acli jira workitem create --from-json` or `--description-file`.

Supported subset (everything the skill's ticket shapes use):
  - paragraphs (blank-line separated)
  - `**bold**`, `` `code` ``, `[text](url)`, bare http(s) URLs
  - `* ` / `- ` bullet lists and `1. ` ordered lists, nested by indentation
  - `# ` .. `### ` headings
  - fenced code blocks (```)

Usage:
  md_to_adf.py ticket.md > ticket.adf.json
  md_to_adf.py ticket.md --wrap-create --project PROJ --type Task \
      --summary "[Backend] ..." --parent PROJ-12 --assignee <account id> \
      --field customfield_10007=1234 --field customfield_10004=1 \
      --label needs-decision > create.json
  cat ticket.md | md_to_adf.py - > ticket.adf.json

`--field` sets any custom field by raw id (see references/project-config.md
for the ids of the site). The value is parsed as JSON when it is valid
JSON (numbers, true/false, objects), otherwise it is passed as a string.
"""
import argparse
import json
import re
import sys

INLINE_RE = re.compile(
    r"(\*\*(?P<bold>.+?)\*\*)"
    r"|(`(?P<code>[^`]+)`)"
    r"|(\[(?P<ltext>[^\]]+)\]\((?P<lurl>[^)\s]+)\))"
    r"|(?P<url>https?://[^\s)\]>,]+(?<![.,;:]))"
)
BULLET_RE = re.compile(r"^(?P<indent>\s*)[*-]\s+(?P<text>.*)$")
ORDERED_RE = re.compile(r"^(?P<indent>\s*)\d+[.)]\s+(?P<text>.*)$")
HEADING_RE = re.compile(r"^(?P<level>#{1,6})\s+(?P<text>.*)$")
SECTION_RE = re.compile(r"^\*\*[^*]+\*\*$")


def inline(text):
    """Split one line of text into ADF text nodes with marks."""
    nodes = []
    pos = 0
    for m in INLINE_RE.finditer(text):
        if m.start() > pos:
            nodes.append({"type": "text", "text": text[pos:m.start()]})
        if m.group("bold") is not None:
            nodes.append({"type": "text", "text": m.group("bold"),
                          "marks": [{"type": "strong"}]})
        elif m.group("code") is not None:
            nodes.append({"type": "text", "text": m.group("code"),
                          "marks": [{"type": "code"}]})
        elif m.group("ltext") is not None:
            nodes.append({"type": "text", "text": m.group("ltext"),
                          "marks": [{"type": "link",
                                     "attrs": {"href": m.group("lurl")}}]})
        elif m.group("url") is not None:
            nodes.append({"type": "text", "text": m.group("url"),
                          "marks": [{"type": "link",
                                     "attrs": {"href": m.group("url")}}]})
        pos = m.end()
    if pos < len(text):
        nodes.append({"type": "text", "text": text[pos:]})
    return nodes or [{"type": "text", "text": ""}]


def paragraph(text):
    return {"type": "paragraph", "content": inline(text)}


def convert(markdown):
    lines = markdown.replace("\r\n", "\n").split("\n")
    doc = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if line.strip().startswith("```"):
            lang = line.strip()[3:].strip()
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            node = {"type": "codeBlock",
                    "content": [{"type": "text", "text": "\n".join(buf)}]}
            if lang:
                node["attrs"] = {"language": lang}
            doc.append(node)
            continue

        hm = HEADING_RE.match(line)
        if hm:
            doc.append({"type": "heading",
                        "attrs": {"level": len(hm.group("level"))},
                        "content": inline(hm.group("text").strip())})
            i += 1
            continue

        if BULLET_RE.match(line) or ORDERED_RE.match(line):
            block, i = parse_list(lines, i)
            doc.append(block)
            continue

        # A bold-only line is a section header in the house style; keep it
        # as its own paragraph even when the next line is not blank.
        if SECTION_RE.match(line.strip()):
            doc.append(paragraph(line.strip()))
            i += 1
            continue

        # paragraph: gather until blank line or a block starter
        buf = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not (
            BULLET_RE.match(lines[i]) or ORDERED_RE.match(lines[i])
            or HEADING_RE.match(lines[i]) or lines[i].strip().startswith("```")
            or SECTION_RE.match(lines[i].strip())
        ):
            buf.append(lines[i].strip())
            i += 1
        doc.append(paragraph(" ".join(buf)))

    return {"type": "doc", "version": 1, "content": doc}


def parse_list(lines, i):
    """Parse a (possibly nested) list starting at lines[i].

    Returns (list_node, next_index). Nesting is by indentation: any deeper
    indent than the current list opens a child list under the last item.
    Continuation lines (indented, no marker) append to the item's paragraph.
    """
    first = BULLET_RE.match(lines[i]) or ORDERED_RE.match(lines[i])
    base_indent = len(first.group("indent").expandtabs(4))
    ordered = ORDERED_RE.match(lines[i]) is not None and not BULLET_RE.match(lines[i])
    items = []  # each: {"raw": str, "children": [list nodes]}
    n = len(lines)

    def build():
        content = []
        for it in items:
            li = {"type": "listItem", "content": [paragraph(it["raw"])]}
            li["content"].extend(it["children"])
            content.append(li)
        return {"type": "orderedList" if ordered else "bulletList",
                "content": content}

    while i < n:
        line = lines[i]
        if not line.strip():
            # A blank line ends the list unless the next non-blank line is a
            # list item at this depth or deeper.
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n and (BULLET_RE.match(lines[j]) or ORDERED_RE.match(lines[j])):
                nm = BULLET_RE.match(lines[j]) or ORDERED_RE.match(lines[j])
                if len(nm.group("indent").expandtabs(4)) >= base_indent:
                    i = j
                    continue
            return build(), i
        m = BULLET_RE.match(line) or ORDERED_RE.match(line)
        if m:
            indent = len(m.group("indent").expandtabs(4))
            if indent < base_indent:
                return build(), i
            if indent > base_indent:
                child, i = parse_list(lines, i)
                if not items:
                    items.append({"raw": "", "children": []})
                items[-1]["children"].append(child)
                continue
            items.append({"raw": m.group("text").strip(), "children": []})
            i += 1
            continue
        # continuation line of the previous item (indented, no marker)
        if items and len(line) - len(line.lstrip()) > base_indent:
            items[-1]["raw"] += " " + line.strip()
            i += 1
            continue
        return build(), i
    return build(), i


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="markdown file, or - for stdin")
    ap.add_argument("--wrap-create", action="store_true",
                    help="emit a full acli `workitem create --from-json` body")
    ap.add_argument("--project", help="project key, e.g. PROJ")
    ap.add_argument("--type", default="Task")
    ap.add_argument("--summary")
    ap.add_argument("--parent", help="parent key or id, e.g. PROJ-12")
    ap.add_argument("--assignee", help="account id (not @me; acli create does not resolve it)")
    ap.add_argument("--field", action="append", default=[], metavar="ID=VALUE",
                    help="custom field by raw id, e.g. customfield_10007=1234; repeatable")
    ap.add_argument("--label", action="append", default=[])
    args = ap.parse_args()

    src = sys.stdin.read() if args.file == "-" else open(args.file, encoding="utf-8").read()
    adf = convert(src)

    if not args.wrap_create:
        json.dump(adf, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return

    if not args.summary or not args.project:
        ap.error("--summary and --project are required with --wrap-create")
    body = {
        "projectKey": args.project,
        "type": args.type,
        "summary": args.summary,
        "description": adf,
    }
    if args.assignee:
        # acli's --from-json does not resolve the "@me" alias; Jira then silently falls
        # back to the project's default assignee (the project lead). Require the account id.
        if args.assignee == "@me":
            sys.exit(
                "--assignee @me is not resolved by `acli jira workitem create --from-json`; "
                "pass the account id from references/project-config.md instead"
            )
        body["assignee"] = args.assignee
    if args.label:
        body["labels"] = args.label
    if args.parent:
        body["parentIssueId"] = args.parent
    extra = {}
    for spec in args.field:
        if "=" not in spec:
            ap.error(f"--field expects ID=VALUE, got {spec!r}")
        key, raw = spec.split("=", 1)
        try:
            extra[key] = json.loads(raw)
        except json.JSONDecodeError:
            extra[key] = raw
    if extra:
        body["additionalAttributes"] = extra
    json.dump(body, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
