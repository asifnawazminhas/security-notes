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

        [NetExec](../active-directory/netexec.md)

SUPPORTED PATH STYLES
=====================

The resolver understands paths such as:

    active-directory/netexec.md
    docs/active-directory/netexec.md
    ../active-directory/netexec.md
    ./kerberos.md
    web/xss.md
    docs/web/xss.md

SAFETY RULES
============

- Only scans Markdown files under docs/.
- Only considers fenced blocks containing exactly ONE .md path.
- Supports ```text```, ```txt```, and untyped ``` blocks.
- Also supports equivalent ~~~ fenced blocks.
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
- Prevents resolved paths from escaping docs/.
- Supports --dry-run.
- Supports --verbose.
- Supports --context-check.

RECOMMENDED WORKFLOW
====================

First:

    python3 scripts/fix-internal-doc-links.py \
        --dry-run \
        --verbose \
        --context-check

After reviewing:

    python3 scripts/fix-internal-doc-links.py --context-check

Then:

    python3 scripts/fix-internal-doc-links.py \
        --dry-run \
        --context-check

Finally:

    git diff --check
    git diff --stat
    git diff -- docs/
    mkdocs build
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


# Nearby prose containing one of these patterns can indicate that
# a standalone .md path is intended as navigation rather than as
# an example of a filesystem/documentation structure.
#
# These patterns deliberately focus on language that indicates
# another document should be opened/read/reviewed.
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
    r"\bbelongs in\b",
    r"\bcovered in\b",
    r"\bis covered in\b",
    r"\bwill be covered in\b",
    r"\bshould cover\b",
    r"\balso review\b",
    r"\bcomplement\b",
]


# ============================================================
# REGULAR EXPRESSIONS
# ============================================================

# Matches paths such as:
#
# active-directory/netexec.md
# docs/active-directory/netexec.md
# ../active-directory/netexec.md
# ./kerberos.md
# web/xss.md
#
# Spaces are deliberately excluded because documentation paths in
# this repository should not require them.
MD_PATH_RE = re.compile(
    r"^(?P<path>"
    r"(?:\.\.?/)*"
    r"[A-Za-z0-9_.-]+"
    r"(?:/[A-Za-z0-9_.-]+)*"
    r"\.md"
    r")$"
)


# First H1 in a target Markdown document.
H1_RE = re.compile(
    r"^#[ \t]+(?P<title>.+?)[ \t]*#*[ \t]*$"
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
    context: str = ""


# ============================================================
# HEADING / LABEL HELPERS
# ============================================================

def clean_heading(text: str) -> str:
    """
    Remove common Markdown formatting from an H1 heading so it can
    safely be used as the label of an internal Markdown link.
    """

    text = text.strip()

    # Remove trailing MkDocs attr_list attributes.
    #
    # Example:
    #
    # # BloodHound { #bloodhound }
    #
    # becomes:
    #
    # BloodHound
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
            -> NetExec

        active-directory.md
            -> Active Directory

        pass-the-hash.md
            -> Pass The Hash

        ntlm-relay.md
            -> NTLM Relay
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
    Prefer the target page's H1 heading.

    Fall back to a readable version of the filename.
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
    Resolve an internal Markdown path safely.

    Supported forms include:

        active-directory/netexec.md
        docs/active-directory/netexec.md
        ../active-directory/netexec.md
        ./kerberos.md
        web/xss.md
        docs/web/xss.md

    Resolution rules:

    1. Paths beginning with "docs/" are interpreted relative to
       the documentation root without accidentally producing:

           docs/docs/...

    2. Paths beginning with "./" or "../" are interpreted relative
       to the current Markdown document.

    3. Other paths are first interpreted relative to docs/.

    4. Other paths are also tested relative to the current source
       document as a fallback.

    5. The resolved target must:

       - exist;
       - be a file;
       - have a .md extension;
       - remain inside docs/.
    """

    docs_root = docs_root.resolve()

    source_dir = source_file.parent.resolve()

    raw_path = raw_path.strip()

    # Normalise Windows-style separators in case they ever appear
    # in Markdown documentation.
    normalised = raw_path.replace(
        "\\",
        "/",
    )

    candidates: list[Path] = []

    # --------------------------------------------------------
    # CASE 1
    #
    # docs/web/xss.md
    #
    # docs_root already points to:
    #
    # /workspaces/security-notes/docs
    #
    # Therefore remove the leading docs/ before joining.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CASE 2
    #
    # ./xss.md
    # ../active-directory/netexec.md
    #
    # These paths explicitly indicate that they are relative to
    # the current source document.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # CASE 3
    #
    # active-directory/netexec.md
    # web/xss.md
    # cheatsheets/impacket.md
    #
    # First interpret these as docs-root-relative because that
    # convention is common throughout this repository.
    #
    # Then try source-relative as a fallback.
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_candidates: list[Path] = []

    seen: set[Path] = set()

    for candidate in candidates:

        if candidate in seen:
            continue

        seen.add(
            candidate
        )

        unique_candidates.append(
            candidate
        )

    # --------------------------------------------------------
    # VALIDATE CANDIDATES
    # --------------------------------------------------------

    for candidate in unique_candidates:

        # Prevent references from escaping docs/.
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
    Calculate the correct relative Markdown path from the source
    document to the target document.

    Example:

        source:
            docs/cheatsheets/netexec.md

        target:
            docs/active-directory/netexec.md

        result:
            ../active-directory/netexec.md
    """

    relative = os.path.relpath(
        target_file,
        start=source_file.parent,
    )

    # Markdown URLs should use forward slashes even when the
    # script is run on Windows.
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
    Retrieve nearby prose immediately before a candidate code block.

    Blank lines are tolerated.

    We collect a small number of preceding prose lines to determine
    whether the path appears to be intended as navigation.
    """

    collected: list[str] = []

    index = (
        block_start_index - 1
    )

    while (
        index >= 0
        and len(collected) < max_lines
    ):

        line = lines[index].strip()

        if not line:

            index -= 1
            continue

        # Stop at another fenced block.
        if (
            line.startswith("```")
            or line.startswith("~~~")
        ):

            break

        # Headings provide structural context but should not by
        # themselves trigger conversion.
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
    Determine whether nearby prose suggests that the standalone
    Markdown path is intended as a documentation/navigation link.
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
# FENCE DETECTION
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
        ```txt

        ~~~
        ~~~text
        ~~~txt

    Other languages are deliberately ignored.
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
    Process a complete Markdown document.
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

        search_index = (
            index + 1
        )

        # ----------------------------------------------------
        # FIND CLOSING FENCE
        # ----------------------------------------------------

        while search_index < len(lines):

            if (
                lines[search_index].strip()
                == fence_marker
            ):

                closing_index = (
                    search_index
                )

                break

            search_index += 1

        # Malformed/unclosed block.
        if closing_index is None:

            output.append(
                lines[index]
            )

            index += 1

            continue

        block_lines = lines[
            index + 1:
            closing_index
        ]

        # ----------------------------------------------------
        # ONLY SINGLE-LINE BLOCKS ARE CANDIDATES
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # MUST BE A STANDALONE .md PATH
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # GET NEARBY PROSE
        # ----------------------------------------------------

        context = get_previous_prose(
            lines=lines,
            block_start_index=index,
        )

        # ----------------------------------------------------
        # OPTIONAL CONSERVATIVE CONTEXT CHECK
        # ----------------------------------------------------

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
                    context=context,
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

        # ----------------------------------------------------
        # RESOLVE TARGET
        # ----------------------------------------------------

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
                    context=context,
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

        # ----------------------------------------------------
        # GENERATE LINK
        # ----------------------------------------------------

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

        # Preserve CRLF if the source uses it.
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
            False,
        )

    updated, changes, skipped = process_content(
        content=original,
        source_file=path,
        docs_root=docs_root,
        require_context=require_context,
    )

    # --------------------------------------------------------
    # PRINT CONVERSIONS
    # --------------------------------------------------------

    if changes:

        print()

        print(
            f"[+] {path}"
        )

        if verbose:

            for change in changes:

                print(
                    f"    Path        : "
                    f"{change.raw_path}"
                )

                print(
                    f"    Target      : "
                    f"{change.target_file}"
                )

                print(
                    f"    Label       : "
                    f"{change.label}"
                )

                print(
                    f"    Relative    : "
                    f"{change.relative_link}"
                )

                print(
                    f"    Context     : "
                    f"{change.context}"
                )

                print(
                    f"    Replace     : "
                    f"{change.replacement}"
                )

                print()

        else:

            print(
                f"    Internal links to convert: "
                f"{len(changes)}"
            )

    # --------------------------------------------------------
    # PRINT SKIPPED CANDIDATES IN VERBOSE MODE
    # --------------------------------------------------------

    if verbose and skipped:

        if not changes:

            print()

            print(
                f"[-] {path}"
            )

        for item in skipped:

            print(
                f"    SKIP Path   : "
                f"{item.raw_path}"
            )

            print(
                f"    SKIP Reason : "
                f"{item.reason}"
            )

            if item.context:

                print(
                    f"    SKIP Context: "
                    f"{item.context}"
                )

            print()

    # --------------------------------------------------------
    # DRY RUN
    # --------------------------------------------------------

    if dry_run:

        return (
            len(changes),
            len(skipped),
            False,
        )

    # --------------------------------------------------------
    # WRITE
    # --------------------------------------------------------

    if (
        changes
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
                len(changes),
                len(skipped),
                False,
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
            "Require nearby prose indicating that the "
            "standalone .md path is intended as a "
            "documentation/navigation reference."
        ),
    )

    args = parser.parse_args()

    docs_root = Path(
        args.root
    )

    # --------------------------------------------------------
    # VALIDATE DOCS ROOT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # COUNTERS
    # --------------------------------------------------------

    total_changes = 0

    total_skipped = 0

    matched_files = 0

    modified_files = 0

    # --------------------------------------------------------
    # PROCESS FILES
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

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
        f"{matched_files}"
    )

    print(
        f"Links to convert       : "
        f"{total_changes}"
    )

    print(
        f"Candidates skipped     : "
        f"{total_skipped}"
    )

    # --------------------------------------------------------
    # DRY-RUN MESSAGE
    # --------------------------------------------------------

    if args.dry_run:

        print()

        print(
            "[*] DRY RUN ONLY - no files were modified."
        )

        if total_changes:

            print()

            print(
                "[*] Review the proposed conversions above."
            )

            print()

            print(
                "[*] Recommended conservative review:"
            )

            print()

            print(
                "    python3 scripts/"
                "fix-internal-doc-links.py "
                "--dry-run --verbose --context-check"
            )

            print()

            print(
                "[*] If the results look correct, apply with:"
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
                "[*] No safe internal documentation links "
                "were identified."
            )

    # --------------------------------------------------------
    # WRITE-MODE MESSAGE
    # --------------------------------------------------------

    else:

        print(
            f"Files modified         : "
            f"{modified_files}"
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
                "[*] Validate MkDocs:"
            )

            print()

            print(
                "    mkdocs build"
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
