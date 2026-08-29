#!/usr/bin/env python3

"""
Add new-tab attributes to external Markdown links in MkDocs documentation.

Example:

    [BloodHound.py](https://github.com/dirkjanm/BloodHound.py)

becomes:

    [BloodHound.py](https://github.com/dirkjanm/BloodHound.py){ target="_blank" rel="noopener noreferrer" }

The script is deliberately conservative.

Safety:
- Only scans .md files.
- Only modifies Markdown links using http:// or https://.
- Does not modify internal relative links.
- Does not modify images.
- Does not modify links inside fenced code blocks.
- Does not modify links already using target="_blank".
- Preserves existing MkDocs attr_list attributes where possible.
- Supports --dry-run.
- Supports --verbose.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

NEW_TAB_ATTRIBUTES = 'target="_blank" rel="noopener noreferrer"'


# Match normal Markdown links:
#
# [Label](https://example.com)
#
# Deliberately excludes images:
#
# ![Image](https://example.com/image.png)
#
EXTERNAL_LINK_RE = re.compile(
    r'(?<!!)'
    r'\[(?P<label>[^\]\n]+)\]'
    r'\('
    r'(?P<url>https?://[^)\s]+)'
    r'\)'
    r'(?P<attrs>\{[^}\n]*\})?',
    re.IGNORECASE,
)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

def is_fence_line(line: str) -> tuple[bool, str | None]:
    """
    Determine whether a line starts a Markdown fenced code block.

    Returns:
        (is_fence, marker)
    """

    stripped = line.lstrip()

    if stripped.startswith("```"):
        return True, "```"

    if stripped.startswith("~~~"):
        return True, "~~~"

    return False, None


def has_target_blank(attrs: str | None) -> bool:
    """
    Determine whether existing attributes already contain
    target="_blank" or target='_blank'.
    """

    if not attrs:
        return False

    return bool(
        re.search(
            r"""target\s*=\s*["']_blank["']""",
            attrs,
            flags=re.IGNORECASE,
        )
    )


def has_rel_noopener(attrs: str | None) -> bool:
    """
    Determine whether rel already contains noopener.
    """

    if not attrs:
        return False

    match = re.search(
        r"""rel\s*=\s*["']([^"']*)["']""",
        attrs,
        flags=re.IGNORECASE,
    )

    if not match:
        return False

    values = {
        value.casefold()
        for value in match.group(1).split()
    }

    return "noopener" in values


def has_rel_noreferrer(attrs: str | None) -> bool:
    """
    Determine whether rel already contains noreferrer.
    """

    if not attrs:
        return False

    match = re.search(
        r"""rel\s*=\s*["']([^"']*)["']""",
        attrs,
        flags=re.IGNORECASE,
    )

    if not match:
        return False

    values = {
        value.casefold()
        for value in match.group(1).split()
    }

    return "noreferrer" in values


def update_existing_attrs(attrs: str) -> str:
    """
    Add target/rel values to an existing MkDocs attr_list block
    without discarding existing classes, IDs, or attributes.

    Example:

        { .external }

    becomes:

        { .external target="_blank" rel="noopener noreferrer" }
    """

    inner = attrs[1:-1].strip()

    # Add target if missing.
    if not has_target_blank(attrs):

        target_match = re.search(
            r"""target\s*=\s*["'][^"']*["']""",
            inner,
            flags=re.IGNORECASE,
        )

        if target_match:

            inner = (
                inner[:target_match.start()]
                + 'target="_blank"'
                + inner[target_match.end():]
            )

        else:

            if inner:
                inner += " "

            inner += 'target="_blank"'

    # Handle rel attribute.
    rel_match = re.search(
        r"""rel\s*=\s*["']([^"']*)["']""",
        inner,
        flags=re.IGNORECASE,
    )

    if rel_match:

        existing_values = rel_match.group(1).split()

        lower_values = {
            value.casefold()
            for value in existing_values
        }

        if "noopener" not in lower_values:
            existing_values.append("noopener")

        if "noreferrer" not in lower_values:
            existing_values.append("noreferrer")

        new_rel = (
            'rel="'
            + " ".join(existing_values)
            + '"'
        )

        inner = (
            inner[:rel_match.start()]
            + new_rel
            + inner[rel_match.end():]
        )

    else:

        if inner:
            inner += " "

        inner += 'rel="noopener noreferrer"'

    return "{ " + inner.strip() + " }"


def build_replacement(
    label: str,
    url: str,
    attrs: str | None,
) -> str:
    """
    Build the updated Markdown link.
    """

    base_link = f"[{label}]({url})"

    if attrs:

        updated_attrs = update_existing_attrs(
            attrs
        )

        return (
            base_link
            + updated_attrs
        )

    return (
        base_link
        + "{ "
        + NEW_TAB_ATTRIBUTES
        + " }"
    )


# ------------------------------------------------------------
# Line processing
# ------------------------------------------------------------

def process_line(
    line: str,
) -> tuple[str, list[dict[str, str]]]:
    """
    Process external Markdown links on one non-code line.
    """

    changes: list[dict[str, str]] = []

    def replace(
        match: re.Match[str],
    ) -> str:

        label = match.group("label")
        url = match.group("url")
        attrs = match.group("attrs")

        if (
            has_target_blank(attrs)
            and has_rel_noopener(attrs)
            and has_rel_noreferrer(attrs)
        ):
            return match.group(0)

        replacement = build_replacement(
            label=label,
            url=url,
            attrs=attrs,
        )

        changes.append(
            {
                "label": label,
                "url": url,
                "before": match.group(0),
                "after": replacement,
            }
        )

        return replacement

    updated = EXTERNAL_LINK_RE.sub(
        replace,
        line,
    )

    return updated, changes


# ------------------------------------------------------------
# Content processing
# ------------------------------------------------------------

def process_content(
    content: str,
) -> tuple[str, list[dict[str, str]]]:
    """
    Process a complete Markdown document while ignoring fenced
    code blocks.
    """

    output: list[str] = []
    all_changes: list[dict[str, str]] = []

    in_fence = False
    fence_marker: str | None = None

    for line in content.splitlines(
        keepends=True
    ):

        is_fence, marker = is_fence_line(
            line
        )

        if is_fence:

            if not in_fence:

                in_fence = True
                fence_marker = marker

            elif marker == fence_marker:

                in_fence = False
                fence_marker = None

            output.append(
                line
            )

            continue

        if in_fence:

            output.append(
                line
            )

            continue

        updated_line, changes = process_line(
            line
        )

        output.append(
            updated_line
        )

        all_changes.extend(
            changes
        )

    return (
        "".join(output),
        all_changes,
    )


# ------------------------------------------------------------
# File processing
# ------------------------------------------------------------

def process_file(
    path: Path,
    dry_run: bool,
    verbose: bool,
) -> tuple[int, bool]:
    """
    Process one Markdown file.

    Returns:
        number of changes
        whether file was modified
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

    if verbose:

        for change in changes:

            print(
                f"    Label  : {change['label']}"
            )

            print(
                f"    URL    : {change['url']}"
            )

            print(
                f"    Before : {change['before']}"
            )

            print(
                f"    After  : {change['after']}"
            )

            print()

    else:

        print(
            f"    External links to update: "
            f"{len(changes)}"
        )

    if dry_run:

        return len(changes), False

    if updated != original:

        path.write_text(
            updated,
            encoding="utf-8",
        )

        return len(changes), True

    return len(changes), False


# ------------------------------------------------------------
# File discovery
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Add target=\"_blank\" and secure rel attributes "
            "to external Markdown links."
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
            "Show proposed changes without modifying files."
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Show every link before and after conversion."
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
        "=" * 72
    )

    print(
        " External Markdown Links - New Tab Converter"
    )

    print(
        "=" * 72
    )

    print()

    print(
        f"Mode                  : {mode}"
    )

    print(
        f"Root                  : {root}"
    )

    print(
        f"Markdown files        : {len(files)}"
    )

    print(
        f"Verbose               : "
        f"{'yes' if args.verbose else 'no'}"
    )

    total_changes = 0
    matched_files = 0
    modified_files = 0

    for path in files:

        count, modified = process_file(
            path=path,
            dry_run=args.dry_run,
            verbose=args.verbose,
        )

        if count:

            matched_files += 1
            total_changes += count

        if modified:

            modified_files += 1

    print()
    print(
        "=" * 72
    )

    print(
        " Summary"
    )

    print(
        "=" * 72
    )

    print()

    print(
        f"Markdown files scanned : {len(files)}"
    )

    print(
        f"Files with links       : {matched_files}"
    )

    print(
        f"Links to update        : {total_changes}"
    )

    if args.dry_run:

        print()
        print(
            "[*] DRY RUN ONLY - no files were modified."
        )

        if total_changes:

            print(
                "[*] Review the proposed changes."
            )

            print()
            print(
                "[*] For detailed before/after output:"
            )

            print()
            print(
                "    python3 scripts/"
                "external-links-new-tab.py "
                "--dry-run --verbose"
            )

            print()
            print(
                "[*] To apply the changes:"
            )

            print()
            print(
                "    python3 scripts/"
                "external-links-new-tab.py"
            )

    else:

        print(
            f"Files modified         : {modified_files}"
        )

        if total_changes:

            print()
            print(
                "[+] External links updated."
            )

            print()
            print(
                "[*] Review with:"
            )

            print()
            print(
                "    git diff --stat"
            )

            print()
            print(
                "    git diff --check"
            )

            print()
            print(
                "    git diff -- docs/"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
