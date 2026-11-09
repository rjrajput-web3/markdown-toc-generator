# markdown-toc-generator

Generate a table of contents from a Markdown file's headings — with
anchor slugs that match GitHub's own, so the links work when you paste
the TOC back into a README.

Stdlib only. No dependencies, no network, writes nothing to disk.

## What it does

- Reads ATX headings (`#` through `######`) from a file or stdin.
- Ignores headings inside fenced code blocks.
- Builds GitHub-style anchors: lowercase, punctuation dropped,
  spaces become hyphens — including GitHub's repeated-hyphen behaviour
  (`FAQ & Troubleshooting!` → `#faq--troubleshooting`).
- Duplicate headings get `-1`, `-2` suffixes, exactly like GitHub.
- `--min-level` / `--max-level` include only a heading range;
  `--indent` sets spaces per nesting level (default 2).

## Usage

```bash
python3 markdown_toc.py README.md
cat notes.md | python3 markdown_toc.py
python3 markdown_toc.py --min-level 2 --max-level 3 docs.md
```

## Example

Input (`demo.md`):

```markdown
# My Project

## Getting Started

### Installation

## Usage

## Usage
```

```bash
$ python3 markdown_toc.py demo.md
```

Output:

```markdown
- [My Project](#my-project)
  - [Getting Started](#getting-started)
    - [Installation](#installation)
  - [Usage](#usage)
  - [Usage](#usage-1)
```

With `--min-level 2 --max-level 3`, the same file gives:

```markdown
- [Getting Started](#getting-started)
  - [Installation](#installation)
- [Usage](#usage)
- [Usage](#usage-1)
```

Headings inside fenced code blocks are skipped:

```bash
$ printf '# Guide\n\n```\n# Not a heading\n```\n\n## Real Heading\n' | python3 markdown_toc.py
- [Guide](#guide)
  - [Real Heading](#real-heading)
```

## Exit codes

| Code | Meaning |
| ---- | ------- |
| 0 | TOC printed |
| 1 | File not found / unreadable, or no headings in range |
| 2 | Empty stdin, or `--min-level` greater than `--max-level` |

## Requirements

Python 3.8+. No third-party packages.
