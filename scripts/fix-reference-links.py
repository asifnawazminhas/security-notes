#!/usr/bin/env python3

"""
Convert standalone URL-only ```text``` blocks in Markdown files
into normal clickable Markdown links.

Example input:

    ## BloodHound.py

    ```text
    https://github.com/dirkjanm/BloodHound.py
    ```

Example output:

    ## BloodHound.py

    [BloodHound.py](https://github.com/dirkjanm/BloodHound.py)

Safety:
- Only scans .md files.
- Only converts fenced "text" blocks.
- The text block must contain exactly one HTTP/HTTPS URL.
- Uses the nearest preceding Markdown heading as the link label.
- Does not touch bash, PowerShell, YAML, Python, etc. code blocks.
- Does not touch multi-line text blocks.
- Supports --dry-run so changes can be reviewed first.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


URL_RE = re.compile(
    r"^https?://[^\s<>]+$"
)


TEXT_URL_BLOCK_RE = re.compile(
    r"(?P<indent>^[ \t]*)```text[ \t]*\r?\n"
    r"(?P<url>https?://[^\s<>]+)[ \t]*\r?\n"
    r"(?P=indent)```[ \t]*$",
    re.MULTILINE,
)


HEADING_RE = re.compile(
    r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$"
)


def clean_heading(text: str) -> str:
    """
    Convert a Markdown heading into a clean link label.
    """

    text = text.strip()

    # Remove inline code.
    text = re.sub(
        r"`([^`]+)`",
        r"\1",
        text,
    )

    # Remove bold.
    text = re.sub(
        r"\*\*([^*]+)\*\*",
        r"\1",
        text,
    )

    text = re.sub(
        r"__([^_]+)__",
        r"\1",
        text,
    )

    # Remove simple emphasis.
    text = re.sub(
        r"\*([^*]+)\*",
        r"\1",
        text,
    )

    text = re.sub(
        r"_([^_]+)_",
        r"\1",
        text,
    )

    # Remove MkDocs heading attributes such as:
    # { #custom-id }
    text = re.sub(
        r"\s*\{[^{}]*\}\s*$",
        "",
        text,
    )

    return text.strip()


def escape_markdown_label(label: str) -> str:
    """
    Escape characters that could break a Markdown link label.
    """

    label = label.replace(
        "\\",
        "\\\\",
    )

    label = label.replace(
        "[",
        "\\[",
    )

    label = label.replace(
        "]",
        "\\]",
    )

    return label


def find_previous_heading(
    content: str,
    position: int,
) -> str | None:
    """
    Find the nearest Markdown heading before a position.

    Headings located inside fenced code blocks are ignored.
    """

    before = content[:position]

    lines = before.splitlines()

    in_fence = False
    fence_marker = None

    headings: list[str] = []

    for line in lines:

        stripped = line.lstrip()

        if stripped.startswith("```"):

            marker = "```"

            if not in_fence:
                in_fence = True
                fence_marker = marker

            elif fence_marker == marker:
                in_fence = False
                fence_marker = None

            continue

        if stripped.startswith("~~~"):

            marker = "~~~"

            if not in_fence:
                in_fence = True
                fence_marker = marker

            elif fence_marker == marker:
                in_fence = False
                fence_marker = None

            continue

        if in_fence:
            continue

        match = HEADING_RE.match(line)

        if match:

            heading = clean_heading(
                match.group(2)
            )

            if heading:
                headings.append(
                    heading
                )

    if not headings:
        return None

    return headings[-1]


def make_link(
    label: str,
    url: str,
) -> str:
    """
    Create a Markdown link.
    """

    label = escape_markdown_label(
        label
    )

    return f"[{label}]({url})"


def process_content(
    content: str,
) -> tuple[str, list[dict[str, str]]]:
    """
    Convert safe standalone URL text blocks.

    Returns:
        updated content
        list of changes
    """

    changes: list[dict[str, str]] = []

    def replace(
        match: re.Match[str],
    ) -> str:

        url = match.group(
            "url"
        ).strip()

        if not URL_RE.fullmatch(url):
            return match.group(0)

        heading = find_previous_heading(
            content,
            match.start(),
        )

        # Conservative behaviour:
        # if no heading exists, do not convert.
        if not heading:
            return match.group(0)

        markdown_link = make_link(
            heading,
            url,
        )

        indent = match.group(
            "indent"
        )

        changes.append(
            {
                "heading": heading,
                "url": url,
                "replacement": markdown_link,
            }
        )

        return (
            indent
            + markdown_link
        )

    updated_content = (
        TEXT_URL_BLOCK_RE.sub(
            replace,
            content,
        )
    )

    return (
        updated_content,
        changes,
    )


def process_file(
    path: Path,
    dry_run: bool,
) -> tuple[int, bool]:
    """
    Process one Markdown file.

    Returns:
        number of detected changes
        whether the file was modified
    """

    try:

        original = path.read_text(
            encoding="utf-8"
        )

    except UnicodeDecodeError:

        print(
            f"[!] Skipping non-UTF-8 file: {path}",
            file=sys.stderr,
        )

        return 0, False

    updated, changes = process_content(
        original
    )

    if not changes:
        return 0, False

    print()
    print(
        f"[+] {path}"
    )

    for change in changes:

        print(
            f"    Heading : {change['heading']}"
        )

        print(
            f"    URL     : {change['url']}"
        )

        print(
            f"    Replace : {change['replacement']}"
        )

        print()

    if dry_run:
        return len(changes), False

    if updated != original:

        path.write_text(
            updated,
            encoding="utf-8",
        )

        return len(changes), True

    return len(changes), False


def collect_markdown_files(
    root: Path,
) -> list[Path]:
    """
    Recursively collect Markdown files.
    """

    return sorted(
        path
        for path in root.rglob("*.md")
        if path.is_file()
    )


def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Convert standalone URL-only "
            "text code blocks into "
            "clickable Markdown links."
        )
    )

    parser.add_argument(
        "root",
        nargs="?",
        default="docs",
        help=(
            "Directory containing Markdown files "
            "(default: docs)"
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Show proposed changes without "
            "modifying any files."
        ),
    )

    args = parser.parse_args()

    root = Path(
        args.root
    )

    if not root.exists():

        print(
            f"[!] Path does not exist: {root}",
            file=sys.stderr,
        )

        return 1

    if not root.is_dir():

        print(
            f"[!] Path is not a directory: {root}",
            file=sys.stderr,
        )

        return 1

    files = collect_markdown_files(
        root
    )

    if not files:

        print(
            f"[!] No Markdown files found under: {root}"
        )

        return 0

    mode = (
        "DRY RUN"
        if args.dry_run
        else "WRITE"
    )

    print(
        "=" * 70
    )

    print(
        " Markdown Reference Link Converter"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Mode  : {mode}"
    )

    print(
        f"Root  : {root}"
    )

    print(
        f"Files : {len(files)}"
    )

    total_changes = 0
    modified_files = 0
    matched_files = 0

    for path in files:

        count, modified = process_file(
            path,
            args.dry_run,
        )

        if count:

            matched_files += 1
            total_changes += count

        if modified:
            modified_files += 1

    print()
    print(
        "=" * 70
    )

    print(
        " Summary"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Markdown files scanned : {len(files)}"
    )

    print(
        f"Files with matches     : {matched_files}"
    )

    print(
        f"Links to convert       : {total_changes}"
    )

    if args.dry_run:

        print()
        print(
            "[*] Dry run only - no files were modified."
        )

        if total_changes:

            print(
                "[*] Review the proposed changes above."
            )

            print(
                "[*] Run again without --dry-run "
                "to apply them."
            )

    else:

        print(
            f"Files modified         : {modified_files}"
        )

        if total_changes:

            print()
            print(
                "[+] Conversion completed."
            )

            print()
            print(
                "[*] Review with:"
            )

            print(
                "    git diff -- docs/"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
