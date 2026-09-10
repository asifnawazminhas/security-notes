#!/usr/bin/env python3

"""
Convert standalone internal Markdown document references displayed inside
fenced text blocks into clickable internal MkDocs links.

The scanner understands ALL Markdown fenced code blocks so that closing
fences belonging to bash, Python, YAML, PowerShell, JSON, and other code
blocks are never mistaken for new opening fences.

Only the following fenced blocks are candidates for link conversion:

    ```
    ```text
    ```txt

and their ~~~ equivalents.

Supported candidate blocks
==========================

Single reference:

    ```text
    docs/web/sql-injection.md
    ```

Multiple references:

    ```text
    docs/web/xss.md
    docs/web/html-injection.md
    ```

Safety rules
============

- Only scans Markdown files under docs/.
- Understands all fenced code blocks for document traversal.
- Only untyped, text, and txt fences are conversion candidates.
- Every non-empty candidate line must be a standalone .md path.
- Every target must physically exist inside docs/.
- Resolved targets must remain inside docs/.
- Multi-reference blocks are atomic.
- If one target in a multi-reference block is missing, the whole block
  remains unchanged.
- Directory trees are not converted.
- Mixed-content blocks are not converted.
- Shell/code/config blocks are never converted.
- Existing Markdown links are not modified.
- Internal links do not receive target="_blank".
- Link labels come from the target page's first H1.
- Filename-derived labels are used as a fallback.
- Relative links are calculated automatically.
- Supports --dry-run.
- Supports --verbose.
- Supports --context-check.

Recommended workflow
====================

Review:

    python3 scripts/fix-internal-doc-links.py \
        --dry-run \
        --verbose \
        --context-check

Apply:

    python3 scripts/fix-internal-doc-links.py \
        --context-check

Verify:

    python3 scripts/fix-internal-doc-links.py \
        --dry-run \
        --context-check

Then:

    git diff --check
    git diff --stat
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

CONVERTIBLE_FENCE_LANGUAGES = {
    "",
    "text",
    "txt",
}


LINK_CONTEXT_PATTERNS = [
    r"\bsee\b",
    r"\bsee also\b",
    r"\bread\b",
    r"\brelated\b",
    r"\brelated notes\b",
    r"\bdetailed notes\b",
    r"\bdetailed explanation\b",
    r"\bdetailed analysis\b",
    r"\bdetailed testing\b",
    r"\bdetailed methodology\b",
    r"\bdetailed technique\b",
    r"\bdetailed discussion\b",
    r"\bfor more information\b",
    r"\bfor more details\b",
    r"\bmore information\b",
    r"\bmore details\b",
    r"\bcontinue\b",
    r"\bvisit\b",
    r"\brefer to\b",
    r"\breference\b",
    r"\breferences\b",
    r"\bcheatsheet\b",
    r"\bcheatsheets\b",
    r"\bdocumentation\b",
    r"\bnotes\b",
    r"\bbelongs in\b",
    r"\bcovered in\b",
    r"\bis covered in\b",
    r"\bwill be covered in\b",
    r"\bshould cover\b",
    r"\balso review\b",
    r"\bcomplement\b",
    r"\bfor complete .+ validation\b",
    r"\bdedicated .+ page\b",
    r"\bwill be added at\b",
    r"\bprovide .+ review guidance\b",
]


# ============================================================
# REGULAR EXPRESSIONS
# ============================================================

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


# Opening Markdown fence.
#
# Supports fences longer than three characters too:
#
# ```
# ```bash
# ````markdown
# ~~~python
#
# The info string is captured but does not determine whether the
# scanner recognises the fence. It only determines whether the block
# is eligible for conversion.
FENCE_START_RE = re.compile(
    r"^[ \t]{0,3}"
    r"(?P<fence>`{3,}|~{3,})"
    r"(?P<info>[^\r\n]*)"
    r"(?:\r?\n)?$"
)


TREE_MARKERS = (
    "├",
    "└",
    "│",
    "─",
    "┬",
    "┴",
    "┼",
    "╭",
    "╮",
    "╰",
    "╯",
    "┌",
    "┐",
    "┘",
)


# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class FenceInfo:
    marker_char: str
    marker_length: int
    language: str
    convertible: bool


@dataclass
class LinkConversion:
    raw_path: str
    target_file: Path
    label: str
    relative_link: str
    replacement: str


@dataclass
class BlockConversion:
    source_file: Path
    context: str
    links: list[LinkConversion]
    multiline: bool


@dataclass
class SkippedBlock:
    source_file: Path
    raw_paths: list[str]
    reason: str
    context: str = ""
    missing_paths: list[str] | None = None


# ============================================================
# LABEL HELPERS
# ============================================================

def clean_heading(text: str) -> str:
    """
    Remove common Markdown formatting from an H1 heading so it can
    safely be used as an internal Markdown link label.
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
    """

    name = path.stem

    if name.casefold() == "index":
        name = path.parent.name

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
        "acls": "ACLs",
        "ace": "ACE",
        "ad": "AD",
        "adcs": "AD CS",
        "adfs": "ADFS",
        "api": "API",
        "asrep": "AS-REP",
        "bloodhound": "BloodHound",
        "bola": "BOLA",
        "cors": "CORS",
        "csrf": "CSRF",
        "css": "CSS",
        "dcom": "DCOM",
        "dns": "DNS",
        "dom": "DOM",
        "gmsa": "gMSA",
        "gpp": "GPP",
        "graphql": "GraphQL",
        "grpc": "gRPC",
        "html": "HTML",
        "http": "HTTP",
        "https": "HTTPS",
        "idor": "IDOR",
        "impacket": "Impacket",
        "javascript": "JavaScript",
        "jwt": "JWT",
        "kerberos": "Kerberos",
        "laps": "LAPS",
        "ldap": "LDAP",
        "llm": "LLM",
        "mdt": "MDT",
        "mfa": "MFA",
        "netexec": "NetExec",
        "nosql": "NoSQL",
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

    return " ".join(output)


# ============================================================
# TARGET PAGE LABEL
# ============================================================

def get_target_h1(
    target: Path,
) -> str | None:
    """
    Read the first H1 heading from a target Markdown document.

    All fenced code blocks are ignored.
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

    lines = content.splitlines(
        keepends=True
    )

    index = 0

    while index < len(lines):

        fence = parse_any_fence_start(
            lines[index]
        )

        if fence is not None:

            closing_index = find_closing_fence(
                lines=lines,
                opening_index=index,
                fence=fence,
            )

            if closing_index is None:
                return None

            index = closing_index + 1
            continue

        match = H1_RE.match(
            lines[index].rstrip("\r\n")
        )

        if match:

            title = clean_heading(
                match.group("title")
            )

            if title:
                return title

        index += 1

    return None


def get_link_label(
    target: Path,
) -> str:
    """
    Prefer the target page's first H1 heading.

    Fall back to a human-readable filename.
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

def candidate_target_paths(
    raw_path: str,
    source_file: Path,
    docs_root: Path,
) -> list[Path]:
    """
    Generate possible resolved paths for an internal Markdown reference.

    docs/foo.md
        -> relative to docs/

    ./foo.md
    ../foo.md
        -> relative to source document

    foo/bar.md
        -> docs-root-relative first
        -> source-relative second
    """

    docs_root = docs_root.resolve()
    source_dir = source_file.parent.resolve()

    raw_path = raw_path.strip()

    normalised = raw_path.replace(
        "\\",
        "/",
    )

    candidates: list[Path] = []

    if normalised.startswith("docs/"):

        without_docs = normalised[
            len("docs/"):
        ]

        candidates.append(
            (
                docs_root
                / Path(without_docs)
            ).resolve()
        )

    elif (
        normalised.startswith("./")
        or normalised.startswith("../")
    ):

        candidates.append(
            (
                source_dir
                / Path(normalised)
            ).resolve()
        )

    else:

        candidates.append(
            (
                docs_root
                / Path(normalised)
            ).resolve()
        )

        candidates.append(
            (
                source_dir
                / Path(normalised)
            ).resolve()
        )

    unique: list[Path] = []
    seen: set[Path] = set()

    for candidate in candidates:

        if candidate in seen:
            continue

        seen.add(candidate)
        unique.append(candidate)

    return unique


def resolve_target(
    raw_path: str,
    source_file: Path,
    docs_root: Path,
) -> Path | None:
    """
    Resolve an internal Markdown path safely.
    """

    docs_root = docs_root.resolve()

    candidates = candidate_target_paths(
        raw_path=raw_path,
        source_file=source_file,
        docs_root=docs_root,
    )

    for candidate in candidates:

        try:

            candidate.relative_to(
                docs_root
            )

        except ValueError:

            continue

        if not candidate.exists():
            continue

        if not candidate.is_file():
            continue

        if candidate.suffix.casefold() != ".md":
            continue

        return candidate

    return None


def make_relative_link(
    source_file: Path,
    target_file: Path,
) -> str:
    """
    Calculate a relative Markdown path from source to target.
    """

    relative = os.path.relpath(
        target_file,
        start=source_file.parent,
    )

    return relative.replace(
        os.sep,
        "/",
    )


# ============================================================
# CONTEXT ANALYSIS
# ============================================================

def get_previous_prose(
    lines: list[str],
    block_start_index: int,
    max_lines: int = 5,
) -> str:
    """
    Retrieve nearby prose immediately before a candidate fenced block.
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

        if is_fence_line(line):

            break

        if line in {
            "---",
            "***",
            "___",
        }:

            index -= 1
            continue

        if line.startswith("#"):

            if collected:
                break

            index -= 1
            continue

        collected.append(line)
        index -= 1

    collected.reverse()

    return " ".join(collected)


def context_looks_navigational(
    context: str,
) -> bool:
    """
    Determine whether nearby prose suggests documentation navigation.
    """

    if not context:
        return False

    for pattern in LINK_CONTEXT_PATTERNS:

        if re.search(
            pattern,
            context,
            flags=re.IGNORECASE,
        ):

            return True

    return False


# ============================================================
# FENCE ANALYSIS
# ============================================================

def parse_any_fence_start(
    line: str,
) -> FenceInfo | None:
    """
    Recognise ANY Markdown fenced-code opening.

    This is the critical traversal function.

    It recognises:

        ```
        ```text
        ```bash
        ```python
        ````markdown
        ~~~
        ~~~yaml

    The language only determines whether the block is eligible for
    conversion. Non-convertible blocks are still skipped correctly.
    """

    raw = line.rstrip("\r\n")

    match = FENCE_START_RE.fullmatch(
        raw
    )

    if not match:
        return None

    marker = match.group("fence")
    info = match.group("info").strip()

    marker_char = marker[0]
    marker_length = len(marker)

    language = ""

    if info:

        # First token of the info string is the language identifier.
        language = info.split(
            None,
            1,
        )[0].casefold()

        # Handle common attribute-like forms conservatively.
        language = language.strip()

    convertible = (
        language
        in CONVERTIBLE_FENCE_LANGUAGES
    )

    return FenceInfo(
        marker_char=marker_char,
        marker_length=marker_length,
        language=language,
        convertible=convertible,
    )


def is_fence_line(
    line: str,
) -> bool:
    """
    Return True when a line looks like a Markdown fence.
    """

    stripped = line.strip()

    return bool(
        re.fullmatch(
            r"`{3,}[^\r\n]*|~{3,}[^\r\n]*",
            stripped,
        )
    )


def is_closing_fence(
    line: str,
    fence: FenceInfo,
) -> bool:
    """
    Determine whether a line closes the supplied fence.

    CommonMark-style behaviour:

    - same marker character;
    - at least as many marker characters as the opening fence;
    - only whitespace after the marker.
    """

    raw = line.rstrip("\r\n")

    pattern = (
        r"^[ \t]{0,3}"
        + re.escape(fence.marker_char)
        + "{"
        + str(fence.marker_length)
        + r",}[ \t]*$"
    )

    return bool(
        re.fullmatch(
            pattern,
            raw,
        )
    )


def find_closing_fence(
    lines: list[str],
    opening_index: int,
    fence: FenceInfo,
) -> int | None:
    """
    Find the closing fence for one already-recognised opening fence.
    """

    index = opening_index + 1

    while index < len(lines):

        if is_closing_fence(
            lines[index],
            fence,
        ):

            return index

        index += 1

    return None


def block_contains_tree_markers(
    block_lines: list[str],
) -> bool:
    """
    Detect obvious directory-tree or diagram content.
    """

    for line in block_lines:

        for marker in TREE_MARKERS:

            if marker in line:
                return True

    return False


def extract_md_paths_from_block(
    block_lines: list[str],
) -> list[str] | None:
    """
    Return standalone .md paths only when every non-empty line is a
    standalone Markdown document path.
    """

    non_empty = [
        line.strip()
        for line in block_lines
        if line.strip()
    ]

    if not non_empty:
        return None

    paths: list[str] = []

    for line in non_empty:

        match = MD_PATH_RE.fullmatch(
            line
        )

        if not match:
            return None

        paths.append(
            match.group("path")
        )

    return paths


# ============================================================
# LINK GENERATION
# ============================================================

def build_link_conversion(
    raw_path: str,
    source_file: Path,
    target_file: Path,
) -> LinkConversion:
    """
    Build one Markdown link conversion.
    """

    label = get_link_label(
        target_file
    )

    relative_link = make_relative_link(
        source_file=source_file,
        target_file=target_file,
    )

    replacement = (
        f"[{escape_markdown_label(label)}]"
        f"({relative_link})"
    )

    return LinkConversion(
        raw_path=raw_path,
        target_file=target_file,
        label=label,
        relative_link=relative_link,
        replacement=replacement,
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
    list[BlockConversion],
    list[SkippedBlock],
]:
    """
    Process one complete Markdown document.

    Important:

    ALL fenced code blocks participate in traversal.

    Only text/txt/untyped fences participate in conversion.
    """

    lines = content.splitlines(
        keepends=True
    )

    output: list[str] = []

    conversions: list[BlockConversion] = []
    skipped: list[SkippedBlock] = []

    index = 0

    while index < len(lines):

        fence = parse_any_fence_start(
            lines[index]
        )

        # Ordinary Markdown/prose.
        if fence is None:

            output.append(
                lines[index]
            )

            index += 1
            continue

        closing_index = find_closing_fence(
            lines=lines,
            opening_index=index,
            fence=fence,
        )

        # Malformed/unclosed fence. Preserve the remainder exactly.
        if closing_index is None:

            output.extend(
                lines[index:]
            )

            break

        # ----------------------------------------------------
        # NON-CONVERTIBLE CODE BLOCK
        #
        # This is the important bug fix.
        #
        # We recognise the whole block and jump past its closing
        # fence instead of later mistaking that closing fence for
        # a new opening fence.
        # ----------------------------------------------------

        if not fence.convertible:

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = closing_index + 1
            continue

        block_lines = lines[
            index + 1:
            closing_index
        ]

        # ----------------------------------------------------
        # DIRECTORY TREE PROTECTION
        # ----------------------------------------------------

        if block_contains_tree_markers(
            block_lines
        ):

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = closing_index + 1
            continue

        # ----------------------------------------------------
        # PATH EXTRACTION
        # ----------------------------------------------------

        raw_paths = extract_md_paths_from_block(
            block_lines
        )

        if raw_paths is None:

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = closing_index + 1
            continue

        # ----------------------------------------------------
        # CONTEXT
        # ----------------------------------------------------

        context = get_previous_prose(
            lines=lines,
            block_start_index=index,
        )

        if (
            require_context
            and not context_looks_navigational(
                context
            )
        ):

            skipped.append(
                SkippedBlock(
                    source_file=source_file,
                    raw_paths=raw_paths,
                    reason=(
                        "nearby prose does not clearly indicate "
                        "a navigational/documentation link"
                    ),
                    context=context,
                )
            )

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = closing_index + 1
            continue

        # ----------------------------------------------------
        # RESOLVE TARGETS ATOMICALLY
        # ----------------------------------------------------

        resolved_targets: list[
            tuple[str, Path]
        ] = []

        missing_paths: list[str] = []

        for raw_path in raw_paths:

            target = resolve_target(
                raw_path=raw_path,
                source_file=source_file,
                docs_root=docs_root,
            )

            if target is None:

                missing_paths.append(
                    raw_path
                )

            else:

                resolved_targets.append(
                    (
                        raw_path,
                        target,
                    )
                )

        if missing_paths:

            if len(raw_paths) == 1:

                reason = (
                    "target Markdown file does not exist "
                    "inside docs/"
                )

            else:

                reason = (
                    "multi-reference block skipped atomically "
                    "because one or more target Markdown files "
                    "do not exist inside docs/"
                )

            skipped.append(
                SkippedBlock(
                    source_file=source_file,
                    raw_paths=raw_paths,
                    reason=reason,
                    context=context,
                    missing_paths=missing_paths,
                )
            )

            output.extend(
                lines[
                    index:
                    closing_index + 1
                ]
            )

            index = closing_index + 1
            continue

        # ----------------------------------------------------
        # BUILD LINKS
        # ----------------------------------------------------

        link_conversions: list[
            LinkConversion
        ] = []

        for raw_path, target in resolved_targets:

            link_conversions.append(
                build_link_conversion(
                    raw_path=raw_path,
                    source_file=source_file,
                    target_file=target,
                )
            )

        # ----------------------------------------------------
        # PRESERVE INDENTATION / NEWLINE STYLE
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # REPLACE FENCED REFERENCE BLOCK
        # ----------------------------------------------------

        for link_index, link in enumerate(
            link_conversions
        ):

            output.append(
                indentation
                + link.replacement
                + newline
            )

            if (
                link_index
                < len(link_conversions) - 1
            ):

                output.append(
                    newline
                )

        conversions.append(
            BlockConversion(
                source_file=source_file,
                context=context,
                links=link_conversions,
                multiline=(
                    len(link_conversions) > 1
                ),
            )
        )

        index = closing_index + 1

    return (
        "".join(output),
        conversions,
        skipped,
    )


# ============================================================
# VERBOSE OUTPUT
# ============================================================

def print_conversion(
    conversion: BlockConversion,
) -> None:
    """
    Print detailed information about one converted block.
    """

    block_type = (
        "MULTI"
        if conversion.multiline
        else "SINGLE"
    )

    print(
        f"    Block Type  : {block_type}"
    )

    if conversion.context:

        print(
            f"    Context     : {conversion.context}"
        )

    for link in conversion.links:

        print(
            f"    Path        : {link.raw_path}"
        )

        print(
            f"    Target      : {link.target_file}"
        )

        print(
            f"    Label       : {link.label}"
        )

        print(
            f"    Relative    : {link.relative_link}"
        )

        print(
            f"    Replace     : {link.replacement}"
        )

        print()


def print_skipped(
    skipped: SkippedBlock,
) -> None:
    """
    Print detailed information about one skipped block.
    """

    block_type = (
        "MULTI"
        if len(skipped.raw_paths) > 1
        else "SINGLE"
    )

    print(
        f"    SKIP Type   : {block_type}"
    )

    print(
        f"    SKIP Reason : {skipped.reason}"
    )

    if skipped.context:

        print(
            f"    SKIP Context: {skipped.context}"
        )

    if len(skipped.raw_paths) == 1:

        print(
            f"    SKIP Path   : "
            f"{skipped.raw_paths[0]}"
        )

    else:

        print(
            "    SKIP Paths  :"
        )

        for raw_path in skipped.raw_paths:

            print(
                f"                  {raw_path}"
            )

    if skipped.missing_paths:

        print(
            "    Missing     :"
        )

        for raw_path in skipped.missing_paths:

            print(
                f"                  {raw_path}"
            )

    print()


# ============================================================
# FILE PROCESSING
# ============================================================

def process_file(
    path: Path,
    docs_root: Path,
    dry_run: bool,
    verbose: bool,
    require_context: bool,
) -> tuple[
    int,
    int,
    int,
    bool,
]:
    """
    Process one Markdown file.

    Returns:

        converted blocks
        converted links
        skipped blocks
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

        return (
            0,
            0,
            0,
            False,
        )

    except OSError as exc:

        print(
            f"[!] Unable to read {path}: {exc}",
            file=sys.stderr,
        )

        return (
            0,
            0,
            0,
            False,
        )

    updated, conversions, skipped = process_content(
        content=original,
        source_file=path,
        docs_root=docs_root,
        require_context=require_context,
    )

    converted_link_count = sum(
        len(conversion.links)
        for conversion in conversions
    )

    if conversions:

        print()

        print(
            f"[+] {path}"
        )

        if verbose:

            for conversion in conversions:

                print_conversion(
                    conversion
                )

        else:

            print(
                f"    Reference blocks to convert : "
                f"{len(conversions)}"
            )

            print(
                f"    Internal links to convert   : "
                f"{converted_link_count}"
            )

    if verbose and skipped:

        if not conversions:

            print()

            print(
                f"[-] {path}"
            )

        for skipped_block in skipped:

            print_skipped(
                skipped_block
            )

    if dry_run:

        return (
            len(conversions),
            converted_link_count,
            len(skipped),
            False,
        )

    if (
        conversions
        and updated != original
    ):

        try:

            path.write_text(
                updated,
                encoding="utf-8",
            )

        except OSError as exc:

            print(
                f"[!] Unable to write {path}: {exc}",
                file=sys.stderr,
            )

            return (
                len(conversions),
                converted_link_count,
                len(skipped),
                False,
            )

        return (
            len(conversions),
            converted_link_count,
            len(skipped),
            True,
        )

    return (
        len(conversions),
        converted_link_count,
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
            "Convert fenced internal .md documentation "
            "references into clickable MkDocs links."
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
            "Show detailed conversions and skipped blocks."
        ),
    )

    parser.add_argument(
        "--context-check",
        action="store_true",
        help=(
            "Require nearby prose indicating that a fenced "
            ".md block is intended as documentation navigation."
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
            f"[!] Path is not a directory: "
            f"{docs_root}",
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
        f"Mode                   : {mode}"
    )

    print(
        f"Documentation root     : {docs_root}"
    )

    print(
        f"Markdown files         : {len(files)}"
    )

    print(
        f"Context check          : "
        f"{'required' if args.context_check else 'not required'}"
    )

    print(
        f"Verbose                : "
        f"{'yes' if args.verbose else 'no'}"
    )

    print(
        "Multi-reference mode   : atomic"
    )

    print(
        "Fence traversal        : all languages"
    )

    print(
        "Convertible fences     : text, txt, untyped"
    )

    total_converted_blocks = 0
    total_converted_links = 0
    total_skipped_blocks = 0
    files_with_conversions = 0
    modified_files = 0

    for path in files:

        (
            converted_blocks,
            converted_links,
            skipped_blocks,
            modified,
        ) = process_file(
            path=path,
            docs_root=docs_root,
            dry_run=args.dry_run,
            verbose=args.verbose,
            require_context=args.context_check,
        )

        if converted_blocks:

            files_with_conversions += 1

        total_converted_blocks += (
            converted_blocks
        )

        total_converted_links += (
            converted_links
        )

        total_skipped_blocks += (
            skipped_blocks
        )

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
        f"Markdown files scanned : "
        f"{len(files)}"
    )

    print(
        f"Files with conversions : "
        f"{files_with_conversions}"
    )

    print(
        f"Blocks to convert      : "
        f"{total_converted_blocks}"
    )

    print(
        f"Links to convert       : "
        f"{total_converted_links}"
    )

    print(
        f"Blocks skipped         : "
        f"{total_skipped_blocks}"
    )

    if args.dry_run:

        print()

        print(
            "[*] DRY RUN ONLY - no files were modified."
        )

        if total_converted_blocks:

            print()

            print(
                "[*] Review the proposed conversions above."
            )

            print()

            print(
                "[*] Recommended apply command:"
            )

            print()

            print(
                "    python3 scripts/"
                "fix-internal-doc-links.py "
                "--context-check"
            )

        else:

            print()

            print(
                "[*] No safe internal documentation "
                "reference blocks were identified."
            )

    else:

        print(
            f"Files modified         : "
            f"{modified_files}"
        )

        if total_converted_blocks:

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
                "[*] Verify remaining raw documentation paths:"
            )

            print()

            print(
                "    grep -RInE "
                "'docs/[A-Za-z0-9_./-]+\\.md' "
                "docs/"
            )

            print()

            print(
                "[*] Then verify idempotence:"
            )

            print()

            print(
                "    python3 scripts/"
                "fix-internal-doc-links.py "
                "--dry-run --context-check"
            )

    return 0


if __name__ == "__main__":

    raise SystemExit(
        main()
    )
