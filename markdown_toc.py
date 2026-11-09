#!/usr/bin/env python3
"""Generate a table of contents from a Markdown file's headings.

Reads Markdown from a file (or stdin) and prints a GitHub-flavoured
table of contents: indented bullet links with anchor slugs that match
GitHub's own heading anchors, so the TOC links work when pasted back
into a README.

Features:
  * ATX headings only (# through ######).
  * Headings inside fenced code blocks are ignored.
  * Duplicate headings get GitHub-style -1, -2 suffixes.
  * --min-level / --max-level to include only a heading range.
  * --indent sets spaces per level (default 2).

Usage:
    python3 markdown_toc.py README.md
    cat notes.md | python3 markdown_toc.py
    python3 markdown_toc.py --min-level 2 --max-level 3 docs.md

Stdlib only. No network, no files written.
"""

import argparse
import re
import sys

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def slugify(text, seen):
    """GitHub-style anchor slug for a heading, with dedup suffixes."""
    text = re.sub(r"<[^>]+>", "", text)          # strip inline HTML tags
    # GitHub's slugger: lowercase, drop punctuation, spaces become hyphens.
    # Repeated hyphens are kept (e.g. "FAQ & Troubleshooting!" -> "faq--troubleshooting").
    slug = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE).strip().lower()
    slug = slug.replace(" ", "-")
    if not slug:
        slug = "section"
    if slug in seen:
        seen[slug] += 1
        slug = f"{slug}-{seen[slug]}"
    else:
        seen[slug] = 0
    return slug


def extract_toc(lines, min_level=1, max_level=6, indent=2):
    """Return TOC lines for the headings found in *lines*."""
    toc = []
    seen = {}
    in_fence = False
    for line in lines:
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING_RE.match(line.rstrip("\n"))
        if not match:
            continue
        level = len(match.group(1))
        if level < min_level or level > max_level:
            continue
        title = match.group(2).strip()
        if not title:
            continue
        anchor = slugify(title, seen)
        pad = " " * (indent * (level - min_level))
        toc.append(f"{pad}- [{title}](#{anchor})")
    return toc


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a GitHub-flavoured table of contents "
                    "from a Markdown file's headings.")
    parser.add_argument("file", nargs="?",
                        help="Markdown file to read (default: stdin)")
    parser.add_argument("--min-level", type=int, default=1, choices=range(1, 7),
                        help="shallowest heading level to include (default: 1)")
    parser.add_argument("--max-level", type=int, default=6, choices=range(1, 7),
                        help="deepest heading level to include (default: 6)")
    parser.add_argument("--indent", type=int, default=2,
                        help="spaces per nesting level (default: 2)")
    args = parser.parse_args(argv)

    if args.min_level > args.max_level:
        parser.error("--min-level cannot be greater than --max-level")

    if args.file:
        try:
            with open(args.file, encoding="utf-8") as handle:
                lines = handle.readlines()
        except FileNotFoundError:
            print(f"error: no such file: {args.file}", file=sys.stderr)
            return 1
        except OSError as exc:
            print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
            return 1
    else:
        lines = sys.stdin.readlines()
        if not lines:
            print("error: no input — pass a file or pipe Markdown to stdin",
                  file=sys.stderr)
            return 2

    toc = extract_toc(lines, args.min_level, args.max_level, args.indent)
    if not toc:
        print("error: no headings found in the given range",
              file=sys.stderr)
        return 1
    print("\n".join(toc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
