#!/usr/bin/env python3

"""
Convert standalone internal Markdown document paths displayed in fenced
text/code blocks into clickable internal MkDocs links.

Example:

    Current file:
        docs/cheatsheets/netexec.md

    Markdown:

        For the detailed explanation of NetExec, see:

        ```text
        active-directory/netexec.md
        ```

    Becomes:

        For the detailed explanation of NetExec, see:

        [NetExec](../active-directory/netexec.md)

The script is deliberately conservative.

SAFETY RULES
============

- Only scans Markdown files under docs/.
- Only considers fenced blocks containing exactly ONE .md path.
- Supports ```text``` and untyped ``` blocks.
- The referenced target must actually exist under docs/.
- Does not modify multi-line code blocks.
- Does not modify directory trees.
- Does not modify shell commands.
- Does not modify YAML examples.
- Does not modify arbitrary .md strings inside prose.
- Does not modify existing Markdown links.
- Does not add target="_blank" to internal links.
- Derives the link label from the target page's first H1 heading.
- Falls back to a readable filename-derived label.
- Calculates the relative link from the current document automatically.
- Supports --dry-run.
- Supports --verbose.
- Supports --context-check to require link-oriented prose before the block.

Recommended first run:

    python3 scripts/fix-internal-doc-links.py --dry-run --verbose

Nothing is modified during a dry run.

After reviewing:

    python3 scripts/fix-internal-doc-links.py

Then:

    git diff --check
    git diff --stat
    git diff -- docs/
"""


from __future__ import annotations

import argparse
import os
import re
import sys

from dataclasses import dataclass
from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

DEFAULT_DOCS_ROOT = "docs"


# Words/phrases that strongly suggest that a nearby standalone
# Markdown path is intended to be navigational.
LINK_CONTEXT_PATTERNS = [
    r"\bsee\b",
    r"\bsee also\b",
    r"\bread\b",
    r"\brelated\b",
    r"\brelated notes\b",
    r"\bdetailed notes\b",
    r"\bdetailed explanation\b",
    r"\bfor more information\b",
    r"\bfor more details\b",
    r"\bmore information\b",
    r"\bmore details\b",
    r"\bcontinue\b",
    r"\bvisit\b",
    r"\brefer to\b",
    r"\breference\b",
    r"\bcheatsheet\b",
    r"\bdocumentation\b",
    r"\bnotes\b",
]


# ============================================================
# REGULAR EXPRESSIONS
# ============================================================

# A path such as:
#
# active-directory/netexec.md
# ../active-directory/netexec.md
# ./kerberos.md
# cheatsheets/bloodhound.md
#
# Spaces are deliberately not supported because our documentation
# paths should not need them.
MD_PATH_RE = re.compile(
    r"^(?P<path>"
    r"(?:\.\.?/)*"
    r"[A-Za-z0-9_.-]+"
    r"(?:/[A-Za-z0-9_.-]+)*"
    r"\.md"
    r")$"
)


H1_RE = re.compile(
    r"^#[ \t]+(?P<title>.+?)[ \t]*#*[ \t]*$"
)


MARKDOWN_LINK_RE = re.compile(
    r"\[[^\]]+\]\([^)]+\.md(?:#[^)]+)?\)"
)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class Candidate:
    source_file: Path
    raw_path: str
    target_file: Path
    label: str
    relative_link: str
    replacement: str
    context: str


@dataclass
class Skipped:
    source_file: Path
    raw_path: str
    reason: str


# ============================================================
# GENERAL HELPERS
# ============================================================

def clean_heading(text: str) -> str:
    """
    Clean basic Markdown formatting from a heading.
    """

    text = text.strip()

    # Remove MkDocs heading attributes.
    text = re.sub(
        r"\s*\{[^{}]*\}\s*$",
        "",
        text,
    )

    # Inline code.
    text = re.sub(
        r"`([^`]+)`",
        r"\1",
        text,
    )

    # Bold.
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

    # Simple emphasis.
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


def humanise_filename(path: Path) -> str:
    """
    Turn a Markdown filename into a readable fallback label.

    Examples:

        netexec.md
            -> Netexec

        active-directory.md
            -> Active Directory

        pass-the-hash.md
            -> Pass The Hash
    """

    name = path.stem

    name = name.replace(
        "_",
        " ",
    )

    name = name.replace(
        "-",
        " ",
    )

    words = name.split()

    special_names = {
        "acl": "ACL",
        "ace": "ACE",
        "ad": "AD",
        "adcs": "AD CS",
        "api": "API",
        "asrep": "AS-REP",
        "bloodhound": "BloodHound",
        "csrf": "CSRF",
        "css": "CSS",
        "dcom": "DCOM",
        "dns": "DNS",
        "gmsa": "gMSA",
        "gpp": "GPP",
        "grpc": "gRPC",
        "html": "HTML",
        "http": "HTTP",
        "idor": "IDOR",
        "impacket": "Impacket",
        "jwt": "JWT",
        "kerberos": "Kerberos",
        "laps": "LAPS",
        "ldap": "LDAP",
        "llm": "LLM",
        "mfa": "MFA",
        "netexec": "NetExec",
        "ntds": "NTDS",
        "ntlm": "NTLM",
        "oauth": "OAuth",
        "oidc": "OIDC",
        "powershell": "PowerShell",
        "rbcd": "RBCD",
        "rpc": "RPC",
        "s4u": "S4U",
        "saml": "SAML",
        "sccm": "SCCM",
        "scom": "SCOM",
        "smb": "SMB",
        "sql": "SQL",
        "ssrf": "SSRF",
        "ssti": "SSTI",
        "svg": "SVG",
        "url": "URL",
        "wmi": "WMI",
        "winrm": "WinRM",
        "wsus": "WSUS",
        "xss": "XSS",
        "xxe": "XXE",
    }

    output: list[str] = []

    for word in words:

        lower = word.casefold()

        if lower in special_names:
            output.append(
                special_names[lower]
            )

        else:
            output.append(
                word.capitalize()
            )

    return " ".join(
        output
    )


# ============================================================
# TARGET PAGE LABEL
# ============================================================

def get_target_h1(
    target: Path,
) -> str | None:
    """
    Read the first H1 heading from the target Markdown document.

    Fenced code blocks are ignored.
    """

    try:

        content = target.read_text(
            encoding="utf-8"
        )

    except (
        UnicodeDecodeError,
        OSError,
    ):

        return None

    in_fence = False
    fence_marker: str | None = None

    for line in content.splitlines():

        stripped = line.lstrip()

        if stripped.startswith("```"):

            if not in_fence:

                in_fence = True
                fence_marker = "```"

            elif fence_marker == "```":

                in_fence = False
                fence_marker = None

            continue

        if stripped.startswith("~~~"):

            if not in_fence:

                in_fence = True
                fence_marker = "~~~"

            elif fence_marker == "~~~":

                in_fence = False
                fence_marker = None

            continue

        if in_fence:
            continue

        match = H1_RE.match(
            line
        )

        if match:

            title = clean_heading(
                match.group("title")
            )

            if title:
                return title

    return None


def get_link_label(
    target: Path,
) -> str:
    """
    Prefer the target page H1.

    Fall back to the filename if necessary.
    """

    heading = get_target_h1(
        target
    )

    if heading:
        return heading

    return humanise_filename(
        target
    )


# ============================================================
# PATH RESOLUTION
# ============================================================

def resolve_target(
    raw_path: str,
    source_file: Path,
    docs_root: Path,
) -> Path | None:
    """
    Resolve a Markdown path safely.

    We support two common styles:

        active-directory/netexec.md

    which is interpreted relative to docs/

    and:

        ../active-directory/netexec.md

    which is interpreted relative to the current Markdown file.

    The resulting file MUST exist inside docs/.
    """

    docs_root = docs_root.resolve()

    source_dir = source_file.parent.resolve()

    candidates: list[Path] = []

    raw = Path(
        raw_path
    )

    # If the path explicitly begins with ./ or ../,
    # treat it as source-relative first.
    if (
        raw_path.startswith("./")
        or raw_path.startswith("../")
    ):

        candidates.append(
            (source_dir / raw).resolve()
        )

        candidates.append(
            (docs_root / raw).resolve()
        )

    else:

        # Most paths used in these notes are docs-root-relative.
        candidates.append(
            (docs_root / raw).resolve()
        )

        # Also try relative to the current document.
        candidates.append(
            (source_dir / raw).resolve()
        )

    for candidate in candidates:

        try:

            candidate.relative_to(
                docs_root
            )

        except ValueError:

            # Target escaped docs/.
            continue

        if (
            candidate.exists()
            and candidate.is_file()
            and candidate.suffix.casefold() == ".md"
        ):

            return candidate

    return None


def make_relative_link(
    source_file: Path,
    target_file: Path,
) -> str:
    """
    Calculate the correct relative Markdown path from the source
    document to the target document.
    """

    relative = os.path.relpath(
        target_file,
        start=source_file.parent,
    )

    # Markdown URLs should use forward slashes.
    relative = relative.replace(
        os.sep,
        "/",
    )

    return relative


# ============================================================
# CONTEXT ANALYSIS
# ============================================================

def get_previous_prose(
    lines: list[str],
    block_start_index: int,
    max_lines: int = 4,
) -> str:
    """
    Retrieve nearby prose before a candidate code block.

    Blank lines are tolerated.

    We stop when encountering another fenced block or heading after
    collecting useful prose.
    """

    collected: list[str] = []

    index = block_start_index - 1

    while (
        index >= 0
        and len(collected) < max_lines
    ):

        line = lines[index].strip()

        if not line:

            index -= 1
            continue

        if (
            line.startswith("```")
            or line.startswith("~~~")
        ):
            break

        if line.startswith("#"):

            if collected:
                break

            index -= 1
            continue

        collected.append(
            line
        )

        index -= 1

    collected.reverse()

    return " ".join(
        collected
    )


def context_looks_navigational(
    context: str,
) -> bool:
    """
    Determine whether nearby prose suggests the path is intended
    as a documentation link.
    """

    if not context:
        return False

    lowered = context.casefold()

    for pattern in LINK_CONTEXT_PATTERNS:

        if re.search(
            pattern,
            lowered,
            flags=re.IGNORECASE,
        ):

            return True

    return False


# ============================================================
# BLOCK DETECTION
# ============================================================

def parse_fence_start(
    line: str,
) -> tuple[str, str] | None:
    """
    Parse a supported fenced block opening.

    Supported:

        ```
        ```text
        ``` text
        ~~~
        ~~~text

    Other language blocks are ignored.
    """

    stripped = line.strip()

    match = re.fullmatch(
        r"(?P<fence>```|~~~)"
        r"[ \t]*"
        r"(?P<lang>[A-Za-z0-9_-]*)"
        r"[ \t]*",
        stripped,
    )

    if not match:
        return None

    fence = match.group(
        "fence"
    )

    language = match.group(
        "lang"
    ).casefold()

    if language not in {
        "",
        "text",
        "txt",
    }:

        return None

    return (
        fence,
        language,
    )


# ============================================================
# CONTENT PROCESSING
# ============================================================

def process_content(
    content: str,
    source_file: Path,
    docs_root: Path,
    require_context: bool,
) -> tuple[
    str,
    list[Candidate],
    list[Skipped],
]:
    """
    Process a Markdown document.
    """

    lines = content.splitlines(
        keepends=True
    )

    output: list[str] = []

    changes: list[Candidate] = []
    skipped: list[Skipped] = []

    index = 0

    while index < len(lines):

        opening = parse_fence_start(
            lines[index]
        )

        if opening is None:

            output.append(
                lines[index]
            )

            index += 1
            continue

        fence_marker, _language = opening

        closing_index: int | None = None

        search_index = index + 1

        while search_index < len(lines):

            if (
                lines[search_index].strip()
                == fence_marker
            ):

                closing_index = search_index
                break

            search_index += 1

        if closing_index is None:

            # Malformed/unclosed block. Leave untouched.
            output.append(
                lines[index]
            )

            index += 1
            continue

        block_lines = lines[
            index + 1:
            closing_index
        ]

        # Only blocks containing exactly one non-empty line
        # are candidates.
        non_empty = [
            line.strip()
            for line in block_lines
            if line.strip()
        ]

        if len(non_empty) != 1:

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = (
                closing_index + 1
            )

            continue

        raw_path = non_empty[0]

        path_match = MD_PATH_RE.fullmatch(
            raw_path
        )

        if not path_match:

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = (
                closing_index + 1
            )

            continue

        raw_path = path_match.group(
            "path"
        )

        context = get_previous_prose(
            lines,
            index,
        )

        if (
            require_context
            and not context_looks_navigational(
                context
            )
        ):

            skipped.append(
                Skipped(
                    source_file=source_file,
                    raw_path=raw_path,
                    reason=(
                        "nearby prose does not clearly indicate "
                        "a navigational/documentation link"
                    ),
                )
            )

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = (
                closing_index + 1
            )

            continue

        target = resolve_target(
            raw_path=raw_path,
            source_file=source_file,
            docs_root=docs_root,
        )

        if target is None:

            skipped.append(
                Skipped(
                    source_file=source_file,
                    raw_path=raw_path,
                    reason=(
                        "target Markdown file does not exist "
                        "inside docs/"
                    ),
                )
            )

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = (
                closing_index + 1
            )

            continue

        label = get_link_label(
            target
        )

        relative_link = make_relative_link(
            source_file=source_file,
            target_file=target,
        )

        replacement = (
            f"[{escape_markdown_label(label)}]"
            f"({relative_link})"
        )

        # Preserve indentation from the opening fence.
        indentation = (
            lines[index][
                :len(lines[index])
                - len(lines[index].lstrip())
            ]
        )

        newline = (
            "\r\n"
            if lines[index].endswith("\r\n")
            else "\n"
        )

        output.append(
            indentation
            + replacement
            + newline
        )

        changes.append(
            Candidate(
                source_file=source_file,
                raw_path=raw_path,
                target_file=target,
                label=label,
                relative_link=relative_link,
                replacement=replacement,
                context=context,
            )
        )

        index = (
            closing_index + 1
        )

    return (
        "".join(output),
        changes,
        skipped,
    )


# ============================================================
# FILE PROCESSING
# ============================================================

def process_file(
    path: Path,
    docs_root: Path,
    dry_run: bool,
    verbose: bool,
    require_context: bool,
) -> tuple[int, int, bool]:
    """
    Process one Markdown file.

    Returns:

        number of conversions
        number of skipped candidates
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

        return (
            0,
            0,
            False,
        )

    updated, changes, skipped = process_content(
        content=original,
        source_file=path,
        docs_root=docs_root,
        require_context=require_context,
    )

    if changes:

        print()
        print(
            f"[+] {path}"
        )

        if verbose:

            for change in changes:

                print(
                    f"    Path        : {change.raw_path}"
                )

                print(
                    f"    Target      : {change.target_file}"
                )

                print(
                    f"    Label       : {change.label}"
                )

                print(
                    f"    Relative    : {change.relative_link}"
                )

                print(
                    f"    Context     : {change.context}"
                )

                print(
                    f"    Replace     : {change.replacement}"
                )

                print()

        else:

            print(
                f"    Internal links to convert: "
                f"{len(changes)}"
            )

    if verbose and skipped:

        if not changes:

            print()
            print(
                f"[-] {path}"
            )

        for item in skipped:

            print(
                f"    SKIP Path   : {item.raw_path}"
            )

            print(
                f"    SKIP Reason : {item.reason}"
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


# ============================================================
# FILE DISCOVERY
# ============================================================

def collect_markdown_files(
    docs_root: Path,
) -> list[Path]:
    """
    Recursively collect Markdown files under docs/.
    """

    return sorted(
        path
        for path in docs_root.rglob("*.md")
        if path.is_file()
    )


# ============================================================
# MAIN
# ============================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            "Convert standalone internal .md path code blocks "
            "into clickable MkDocs links."
        )
    )

    parser.add_argument(
        "root",
        nargs="?",
        default=DEFAULT_DOCS_ROOT,
        help=(
            "MkDocs documentation directory "
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
            "Show detailed conversions and skipped candidates."
        ),
    )

    parser.add_argument(
        "--context-check",
        action="store_true",
        help=(
            "Require nearby prose such as 'see', "
            "'detailed notes', 'related', or 'documentation' "
            "before converting a standalone .md path."
        ),
    )

    args = parser.parse_args()

    docs_root = Path(
        args.root
    )

    if not docs_root.exists():

        print(
            f"[!] Documentation directory does not exist: "
            f"{docs_root}",
            file=sys.stderr,
        )

        return 1

    if not docs_root.is_dir():

        print(
            f"[!] Path is not a directory: {docs_root}",
            file=sys.stderr,
        )

        return 1

    docs_root = docs_root.resolve()

    files = collect_markdown_files(
        docs_root
    )

    if not files:

        print(
            f"[!] No Markdown files found under: "
            f"{docs_root}"
        )

        return 0

    mode = (
        "DRY RUN"
        if args.dry_run
        else "WRITE"
    )

    print(
        "=" * 74
    )

    print(
        " Internal MkDocs Link Converter"
    )

    print(
        "=" * 74
    )

    print()

    print(
        f"Mode                  : {mode}"
    )

    print(
        f"Documentation root    : {docs_root}"
    )

    print(
        f"Markdown files        : {len(files)}"
    )

    print(
        f"Context check         : "
        f"{'required' if args.context_check else 'not required'}"
    )

    print(
        f"Verbose               : "
        f"{'yes' if args.verbose else 'no'}"
    )

    total_changes = 0
    total_skipped = 0
    matched_files = 0
    modified_files = 0

    for path in files:

        changes, skipped, modified = process_file(
            path=path,
            docs_root=docs_root,
            dry_run=args.dry_run,
            verbose=args.verbose,
            require_context=args.context_check,
        )

        if changes:

            matched_files += 1

        total_changes += changes
        total_skipped += skipped

        if modified:
            modified_files += 1

    print()
    print(
        "=" * 74
    )

    print(
        " Summary"
    )

    print(
        "=" * 74
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
        f"Candidates skipped     : {total_skipped}"
    )

    if args.dry_run:

        print()
        print(
            "[*] DRY RUN ONLY - no files were modified."
        )

        if total_changes:

            print()
            print(
                "[*] Review the proposed conversions."
            )

            print()
            print(
                "[*] Recommended detailed review:"
            )

            print()
            print(
                "    python3 scripts/fix-internal-doc-links.py "
                "--dry-run --verbose --context-check"
            )

            print()
            print(
                "[*] If the conservative results look correct:"
            )

            print()
            print(
                "    python3 scripts/fix-internal-doc-links.py "
                "--context-check"
            )

        else:

            print()
            print(
                "[*] No safe internal document links "
                "were identified."
            )

    else:

        print(
            f"Files modified         : {modified_files}"
        )

        if total_changes:

            print()
            print(
                "[+] Internal documentation links updated."
            )

            print()
            print(
                "[*] Review before committing:"
            )

            print()
            print(
                "    git diff --check"
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
                "[*] Then validate MkDocs:"
            )

            print()
            print(
                "    mkdocs build"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
