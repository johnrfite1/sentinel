#!/usr/bin/env python3
"""Extract one exact ATX-heading section from a Markdown document.

The anchor must occur exactly once outside CommonMark backtick and tilde fenced
code blocks.  The section ends at the next outside-fence ATX heading whose
depth is the same as or shallower than the anchor's depth.
"""

import re
import sys


ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})(?:[ \t]+|$)(?!#)")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


def section_label(anchor):
    text = re.sub(r"^#{1,6}[ \t]+", "", anchor)
    number = re.match(r"([0-9]+(?:\.[0-9]+)*)\b", text)
    return "§" + number.group(1) if number else repr(anchor)


def outside_fence_headings(lines):
    """Yield (line index, depth) for ATX headings outside fenced code."""
    fence_char = None
    fence_length = 0

    for index, raw_line in enumerate(lines):
        line = raw_line.rstrip("\r\n")
        if fence_char is not None:
            close = re.match(
                r"^ {0,3}(" + re.escape(fence_char) + r"{%d,})[ \t]*$" % fence_length,
                line,
            )
            if close:
                fence_char = None
                fence_length = 0
            continue

        opening = FENCE_OPEN.match(line)
        if opening:
            marker = opening.group(1)
            fence_char = marker[0]
            fence_length = len(marker)
            continue

        heading = ATX_HEADING.match(line)
        if heading:
            yield index, len(heading.group(1))


def extract(text, anchor):
    anchor_heading = ATX_HEADING.match(anchor)
    label = section_label(anchor)
    if anchor_heading is None:
        # The public callers pass maintained exact ATX headings. Keep malformed
        # invocations distinct from a document that lacks a valid anchor.
        raise ValueError("markdown section %s: invalid exact ATX anchor" % label)

    lines = text.splitlines(keepends=True)
    headings = list(outside_fence_headings(lines))
    anchors = [
        (index, depth)
        for index, depth in headings
        if lines[index].rstrip("\r\n") == anchor
    ]

    if not anchors:
        raise ValueError(
            "markdown section %s: could not isolate section; anchor not found" % label
        )
    if len(anchors) != 1:
        raise ValueError(
            "markdown section %s: ambiguous section; %d headings claim the exact anchor"
            % (label, len(anchors))
        )

    start, depth = anchors[0]
    end = len(lines)
    for index, candidate_depth in headings:
        if index > start and candidate_depth <= depth:
            end = index
            break
    return "".join(lines[start + 1:end])


def main(argv):
    if len(argv) != 3:
        print("usage: extract-markdown-section.py FILE EXACT_ANCHOR", file=sys.stderr)
        return 2

    path, anchor = argv[1:]
    try:
        with open(path, encoding="utf-8", newline="") as handle:
            text = handle.read()
        sys.stdout.write(extract(text, anchor))
    except (OSError, UnicodeError) as error:
        print("markdown section %s: cannot read document: %s" %
              (section_label(anchor), error), file=sys.stderr)
        return 2
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
