#!/usr/bin/env python3

"""
Safely convert standalone URL-only ```text``` blocks in Markdown
reference sections into normal clickable Markdown links.

The script is deliberately conservative.

Example:

    # References

    ## BloodHound.py

    ```text
    https://github.com/dirkjanm/BloodHound.py
    ```

becomes:

    # References

    ## BloodHound.py

    [BloodHound.py](https://github.com/dirkjanm/BloodHound.py)


Another supported structure:

    # References

    ## Tools

    ```text
    https://github.com/fortra/impacket
    ```

In this case the generic heading "Tools" is NOT used as the link label.
Instead, a label is derived from the URL:

    [fortra/impacket](https://github.com/fortra/impacket)


SAFETY RULES

- Only scans .md files.
- Only examines fenced ```text``` blocks.
- The block must contain exactly one HTTP/HTTPS URL.
- By default, the URL must be inside a reference-oriented section.
- Commands containing URLs are not modified.
- Multi-line text blocks are not modified.
- bash, PowerShell, YAML, Python, etc. blocks are not modified.
- Generic headings are not blindly used as link labels.
- Example/test URLs such as target.example are skipped by default.
- --dry-run makes no changes.
- --verbose shows skipped blocks and reasons.
- --all-reference-urls can be used later if broader matching is desired.
- Existing Markdown links are unaffected.

Recommended first run:

    python3 scripts/fix-reference-links.py --dry-run --verbose

Apply only after reviewing the output:

    python3 scripts/fix-reference-links.py

Then review:

    git diff --stat
    git diff -- docs/
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


# ============================================================
# REGULAR EXPRESSIONS
# ============================================================

URL_RE = re.compile(
    r"^https?://[^\s<>]+$",
    re.IGNORECASE,
)

TEXT_URL_BLOCK_RE = re.compile(
    r"(?P<indent>^[ \t]*)```text[ \t]*\r?\n"
    r"(?P<url>https?://[^\s<>]+)[ \t]*\r?\n"
    r"(?P=indent)```[ \t]*$",
    re.MULTILINE | re.IGNORECASE,
)

HEADING_RE = re.compile(
    r"^(?P<hashes>#{1,6})[ \t]+(?P<title>.+?)[ \t]*#*[ \t]*$"
)


# ============================================================
# REFERENCE SECTION NAMES
# ============================================================

REFERENCE_SECTION_NAMES = {
    "reference",
    "references",
    "resource",
    "resources",
    "sources",
    "source",
    "further reading",
    "additional reading",
    "recommended reading",
    "documentation",
    "official documentation",
    "official references",
    "official resources",
    "external references",
    "external resources",
    "useful references",
    "useful resources",
    "links",
    "useful links",
}


# ============================================================
# GENERIC HEADINGS
# ============================================================

GENERIC_LINK_HEADINGS = {
    "reference",
    "references",
    "resource",
    "resources",
    "source",
    "sources",
    "tools",
    "tool",
    "documentation",
    "official documentation",
    "official references",
    "official resources",
    "external references",
    "external resources",
    "further reading",
    "additional reading",
    "recommended reading",
    "useful links",
    "links",
    "github",
    "website",
    "websites",
    "testing",
    "extension testing",
    "extensions",
    "installation",
    "usage",
    "examples",
    "example",
    "notes",
    "related",
    "related tools",
    "related resources",
}


# ============================================================
# TEST / PLACEHOLDER DOMAINS
# ============================================================

PLACEHOLDER_DOMAINS = {
    "example.com",
    "example.org",
    "example.net",
    "example.local",
    "target.example",
    "test.example",
    "localhost",
}


# ============================================================
# KNOWN SITE LABELS
# ============================================================

KNOWN_HOST_LABELS = {
    "attack.mitre.org": "MITRE ATT&CK",
    "bloodhound.specterops.io": "BloodHound Documentation",
    "cheatsheetseries.owasp.org": "OWASP Cheat Sheet Series",
    "github.com": "GitHub",
    "learn.microsoft.com": "Microsoft Learn",
    "neo4j.com": "Neo4j",
    "portswigger.net": "PortSwigger",
    "www.netexec.wiki": "NetExec Wiki",
    "netexec.wiki": "NetExec Wiki",
}


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Heading:
    level: int
    title: str
    start: int


@dataclass
class Change:
    heading: str
    url: str
    label: str
    replacement: str
    reason: str


@dataclass
class Skipped:
    heading: str
    url: str
    reason: str


# ============================================================
# TEXT HELPERS
# ============================================================

def clean_heading(text: str) -> str:
    """
    Clean Markdown formatting from a heading.
    """

    text = text.strip()

    text = re.sub(
        r"\s*\{[^{}]*\}\s*$",
        "",
        text,
    )

    text = re.sub(
        r"`([^`]+)`",
        r"\1",
        text,
    )

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

    return text.strip()


def normalise_heading(text: str) -> str:
    """
    Normalise heading text for comparisons.
    """

    text = clean_heading(text)

    text = text.casefold()

    text = re.sub(
        r"[^a-z0-9]+",
        " ",
        text,
    )

    return " ".join(
        text.split()
    )


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


def make_link(label: str, url: str) -> str:
    """
    Create a Markdown link.
    """

    return (
        f"[{escape_markdown_label(label)}]"
        f"({url})"
    )


# ============================================================
# HEADING PARSING
# ============================================================

def parse_headings(content: str) -> list[Heading]:
    """
    Parse Markdown headings while ignoring fenced code blocks.
    """

    headings: list[Heading] = []

    in_fence = False
    fence_marker: str | None = None

    offset = 0

    for line in content.splitlines(keepends=True):

        stripped = line.lstrip()

        if stripped.startswith("```"):

            if not in_fence:
                in_fence = True
                fence_marker = "```"

            elif fence_marker == "```":
                in_fence = False
                fence_marker = None

            offset += len(line)
            continue

        if stripped.startswith("~~~"):

            if not in_fence:
                in_fence = True
                fence_marker = "~~~"

            elif fence_marker == "~~~":
                in_fence = False
                fence_marker = None

            offset += len(line)
            continue

        if not in_fence:

            match = HEADING_RE.match(
                line.rstrip("\r\n")
            )

            if match:

                title = clean_heading(
                    match.group("title")
                )

                if title:

                    headings.append(
                        Heading(
                            level=len(
                                match.group("hashes")
                            ),
                            title=title,
                            start=offset,
                        )
                    )

        offset += len(line)

    return headings


def headings_before_position(
    headings: list[Heading],
    position: int,
) -> list[Heading]:
    """
    Return all headings occurring before a position.
    """

    return [
        heading
        for heading in headings
        if heading.start < position
    ]


def current_heading(
    headings: list[Heading],
    position: int,
) -> Heading | None:
    """
    Return the nearest preceding heading.
    """

    previous = headings_before_position(
        headings,
        position,
    )

    if not previous:
        return None

    return previous[-1]


def heading_ancestors(
    headings: list[Heading],
    position: int,
) -> list[Heading]:
    """
    Build the active Markdown heading hierarchy at a position.

    Example:

        # References
        ## Official Documentation
        ### Microsoft

    returns all active ancestors.
    """

    previous = headings_before_position(
        headings,
        position,
    )

    stack: list[Heading] = []

    for heading in previous:

        while (
            stack
            and stack[-1].level >= heading.level
        ):
            stack.pop()

        stack.append(
            heading
        )

    return stack


# ============================================================
# REFERENCE SECTION DETECTION
# ============================================================

def is_reference_heading(title: str) -> bool:
    """
    Determine whether a heading identifies a reference section.
    """

    normalised = normalise_heading(
        title
    )

    if normalised in REFERENCE_SECTION_NAMES:
        return True

    if normalised.endswith(
        " references"
    ):
        return True

    if normalised.endswith(
        " resources"
    ):
        return True

    if normalised.endswith(
        " documentation"
    ):
        return True

    return False


def is_inside_reference_section(
    headings: list[Heading],
    position: int,
) -> bool:
    """
    Determine whether a URL block is inside a reference section.
    """

    ancestors = heading_ancestors(
        headings,
        position,
    )

    return any(
        is_reference_heading(
            heading.title
        )
        for heading in ancestors
    )


# ============================================================
# URL HELPERS
# ============================================================

def hostname_from_url(url: str) -> str:
    """
    Extract a normalised hostname.
    """

    parsed = urlparse(
        url
    )

    host = (
        parsed.hostname
        or ""
    ).casefold()

    if host.startswith("www."):
        host_without_www = host[4:]

        if host_without_www in KNOWN_HOST_LABELS:
            return host_without_www

    return host


def is_placeholder_url(url: str) -> bool:
    """
    Skip example/test URLs that are likely part of documentation
    rather than real external references.
    """

    host = hostname_from_url(
        url
    )

    if host in PLACEHOLDER_DOMAINS:
        return True

    if host.endswith(
        ".example"
    ):
        return True

    if host.endswith(
        ".example.com"
    ):
        return True

    if host.endswith(
        ".example.org"
    ):
        return True

    if host.endswith(
        ".example.net"
    ):
        return True

    if host.endswith(
        ".example.local"
    ):
        return True

    return False


def clean_url_segment(segment: str) -> str:
    """
    Convert a URL path segment into a readable label.
    """

    segment = unquote(
        segment
    )

    segment = re.sub(
        r"\.(html?|md|php|aspx?)$",
        "",
        segment,
        flags=re.IGNORECASE,
    )

    segment = segment.replace(
        "_",
        " ",
    )

    segment = segment.replace(
        "-",
        " ",
    )

    segment = " ".join(
        segment.split()
    )

    return segment.strip()


def github_label(url: str) -> str | None:
    """
    Derive owner/repository label for GitHub URLs.
    """

    parsed = urlparse(
        url
    )

    parts = [
        unquote(part)
        for part in parsed.path.split("/")
        if part
    ]

    if len(parts) >= 2:

        owner = parts[0]
        repository = parts[1]

        return (
            f"{owner}/{repository}"
        )

    return None


def derive_label_from_url(url: str) -> str:
    """
    Derive a sensible fallback label from a URL.
    """

    parsed = urlparse(
        url
    )

    host = hostname_from_url(
        url
    )

    if host == "github.com":

        label = github_label(
            url
        )

        if label:
            return label

    path_parts = [
        part
        for part in parsed.path.split("/")
        if part
    ]

    if path_parts:

        final_segment = clean_url_segment(
            path_parts[-1]
        )

        if final_segment:

            if host in KNOWN_HOST_LABELS:

                site_name = KNOWN_HOST_LABELS[
                    host
                ]

                return (
                    f"{site_name} - "
                    f"{final_segment}"
                )

            return final_segment

    if host in KNOWN_HOST_LABELS:
        return KNOWN_HOST_LABELS[
            host
        ]

    if host:
        return host

    return url


# ============================================================
# LINK LABEL SELECTION
# ============================================================

def heading_is_generic(title: str) -> bool:
    """
    Determine whether a heading is too generic to use as a
    reference link label.
    """

    normalised = normalise_heading(
        title
    )

    if normalised in GENERIC_LINK_HEADINGS:
        return True

    if is_reference_heading(
        title
    ):
        return True

    return False


def select_link_label(
    heading: Heading | None,
    url: str,
) -> tuple[str, str]:
    """
    Select the best link label.

    Returns:
        label
        reason
    """

    if heading is not None:

        if not heading_is_generic(
            heading.title
        ):

            return (
                heading.title,
                "specific preceding heading",
            )

    return (
        derive_label_from_url(
            url
        ),
        "label derived from URL",
    )


# ============================================================
# CONTENT PROCESSING
# ============================================================

def process_content(
    content: str,
    allow_all_reference_urls: bool = False,
) -> tuple[
    str,
    list[Change],
    list[Skipped],
]:
    """
    Convert safe standalone URL text blocks.
    """

    headings = parse_headings(
        content
    )

    changes: list[Change] = []
    skipped: list[Skipped] = []

    def replace(
        match: re.Match[str],
    ) -> str:

        url = match.group(
            "url"
        ).strip()

        heading = current_heading(
            headings,
            match.start(),
        )

        heading_name = (
            heading.title
            if heading
            else "(none)"
        )

        if not URL_RE.fullmatch(
            url
        ):

            skipped.append(
                Skipped(
                    heading=heading_name,
                    url=url,
                    reason="not a valid standalone HTTP/HTTPS URL",
                )
            )

            return match.group(0)

        if is_placeholder_url(
            url
        ):

            skipped.append(
                Skipped(
                    heading=heading_name,
                    url=url,
                    reason="placeholder/example URL",
                )
            )

            return match.group(0)

        inside_references = (
            is_inside_reference_section(
                headings,
                match.start(),
            )
        )

        if (
            not inside_references
            and not allow_all_reference_urls
        ):

            skipped.append(
                Skipped(
                    heading=heading_name,
                    url=url,
                    reason="not inside a reference-oriented section",
                )
            )

            return match.group(0)

        label, label_reason = (
            select_link_label(
                heading,
                url,
            )
        )

        if not label:

            skipped.append(
                Skipped(
                    heading=heading_name,
                    url=url,
                    reason="could not derive a safe link label",
                )
            )

            return match.group(0)

        markdown_link = make_link(
            label,
            url,
        )

        indent = match.group(
            "indent"
        )

        changes.append(
            Change(
                heading=heading_name,
                url=url,
                label=label,
                replacement=markdown_link,
                reason=label_reason,
            )
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
        skipped,
    )


# ============================================================
# FILE PROCESSING
# ============================================================

def process_file(
    path: Path,
    dry_run: bool,
    verbose: bool,
    allow_all_reference_urls: bool,
) -> tuple[int, int, bool]:
    """
    Process one Markdown file.

    Returns:
        number of changes
        number of skipped blocks
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

        return 0, 0, False

    updated, changes, skipped = (
        process_content(
            original,
            allow_all_reference_urls=(
                allow_all_reference_urls
            ),
        )
    )

    if changes:

        print()
        print(
            f"[+] {path}"
        )

        for change in changes:

            print(
                f"    Heading : {change.heading}"
            )

            print(
                f"    URL     : {change.url}"
            )

            print(
                f"    Label   : {change.label}"
            )

            print(
                f"    Reason  : {change.reason}"
            )

            print(
                f"    Replace : {change.replacement}"
            )

            print()

    if verbose and skipped:

        if not changes:

            print()
            print(
                f"[-] {path}"
            )

        for item in skipped:

            print(
                f"    SKIP Heading : {item.heading}"
            )

            print(
                f"    SKIP URL     : {item.url}"
            )

            print(
                f"    SKIP Reason  : {item.reason}"
            )

            print()

    if dry_run:

        return (
            len(changes),
            len(skipped),
            False,
        )

    if (
        changes
        and updated != original
    ):

        path.write_text(
            updated,
            encoding="utf-8",
        )

        return (
            len(changes),
            len(skipped),
            True,
        )

    return (
        len(changes),
        len(skipped),
        False,
    )


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


# ============================================================
# COMMAND LINE
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Safely convert standalone URL-only "
            "text blocks in Markdown reference "
            "sections into clickable links."
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
            "modifying files."
        ),
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help=(
            "Also show URL blocks that were skipped "
            "and the reason they were skipped."
        ),
    )

    parser.add_argument(
        "--all-reference-urls",
        action="store_true",
        help=(
            "Allow URL-only text blocks outside explicit "
            "reference sections. This is broader and should "
            "only be used after reviewing a dry run."
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
        " Safe Markdown Reference Link Converter"
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
        "Reference sections   : required"
        if not args.all_reference_urls
        else
        "Reference sections   : not required"
    )

    print(
        f"Verbose skips         : "
        f"{'yes' if args.verbose else 'no'}"
    )

    total_changes = 0
    total_skipped = 0
    matched_files = 0
    modified_files = 0

    for path in files:

        changes, skipped, modified = (
            process_file(
                path=path,
                dry_run=args.dry_run,
                verbose=args.verbose,
                allow_all_reference_urls=(
                    args.all_reference_urls
                ),
            )
        )

        if changes:

            matched_files += 1

        total_changes += changes
        total_skipped += skipped

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
        f"Files with conversions : {matched_files}"
    )

    print(
        f"Links to convert       : {total_changes}"
    )

    print(
        f"URL blocks skipped     : {total_skipped}"
    )

    if args.dry_run:

        print()
        print(
            "[*] DRY RUN ONLY - no files were modified."
        )

        if total_changes:

            print(
                "[*] Review the proposed Replace lines."
            )

            print(
                "[*] If they look correct, run:"
            )

            print()

            print(
                "    python3 scripts/fix-reference-links.py"
            )

        else:

            print(
                "[*] No safe conversions were identified."
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
                "[*] Review all modifications before committing:"
            )

            print()

            print(
                "    git diff --stat"
            )

            print()

            print(
                "    git diff -- docs/"
            )

            print()

            print(
                "    git status"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
