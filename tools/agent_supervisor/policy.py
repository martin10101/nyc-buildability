#!/usr/bin/env python3
"""The deterministic four-tier policy engine (D-007 S4, S3, S13.12).

This module is the heart of the supervisor. Every proposed action, tool call and
candidate forwarded prompt is classified into EXACTLY ONE tier by deterministic
local code:

    HARD_DENY   never, regardless of any model's opinion (S4.4), resolving to
                DENY_AND_CONTINUE or DENY_AND_HALT
    AUTO        proceed and log (S4.1), including owner-created standing grants
    NOTIFY      proceed, tell the owner asynchronously, exactly once (S4.2)
    ASK         queue the question, do not stall the world (S4.3)

Non-negotiable properties implemented here:

* **A model recommendation may only STRICTEN.** `apply_model_recommendation()`
  takes the stricter of (deterministic tier, recommended tier) and records an
  ignored recommendation when a model tries to loosen one (S4, S13.12 inv. 4).
* **Claude's stated reason is never an input to classification.** It is carried
  on the action for the audit record and is treated as untrusted data (S8.3).
  `evaluate()` does not read it. Instructions found in model output, repository
  text, PR comments, or test output never move an action to a looser tier.
* **Standing grants are owner-created, exact-shape, task-scoped, expiring.**
  `owner_grant()` refuses construction by anything but the owner, refuses a bare
  executable allowlist, and requires a declared post-verification (S4.1).
* **Unclassifiable means ASK, never AUTO.** The final fallthrough is ASK.

Also here, because they are deterministic policy rather than adapter behaviour:

* `resolve_model()` - S3 per-provider model selection with own-provider allowlist
  enforcement, ordered fallback (a NOTIFY event) and exhausted-chain ASK. It
  lives in the policy engine, not in an adapter, because S3.2 rule 7 says model
  selection never widens authority: both adapters must obey ONE implementation.
* `check_independence()` - the five-clause dependency-independence check recorded
  in the Phase 0 return, which gates parallel continuation under S4.3(a).
* `NotifyOnceLedger` - the S4.2 "notify exactly once" ledger.

Nothing in this module executes anything. It parses, classifies, and explains.
"""
from __future__ import annotations

import dataclasses
import fnmatch
import os
import pathlib
import posixpath
import re
import shlex
from typing import Any, Callable, Mapping, Sequence

from .models import digest_of, to_utc_iso
from .process import EFFORT_ARGUMENT_PREFIXES, HARD_DENY_ARGUMENTS

#: Bumped whenever a rule changes. Bound into every approval digest (S13.5) so a
#: policy change invalidates approvals that were granted under the old rules.
POLICY_VERSION = "1.0.0"

# --------------------------------------------------------------------------
# Tiers and outcomes
# --------------------------------------------------------------------------

AUTO = "AUTO"
NOTIFY = "NOTIFY"
ASK = "ASK"
HARD_DENY = "HARD_DENY"

TIERS: tuple[str, ...] = (AUTO, NOTIFY, ASK, HARD_DENY)

#: Strictness ordering. `max()` over this is the only legal way to combine a
#: deterministic tier with a model recommendation.
TIER_ORDER: dict[str, int] = {AUTO: 0, NOTIFY: 1, ASK: 2, HARD_DENY: 3}

DENY_AND_CONTINUE = "DENY_AND_CONTINUE"
DENY_AND_HALT = "DENY_AND_HALT"

#: S4.3 classes that categorically block dependent continuation.
BLOCKING_ASK_CLASSES: frozenset[str] = frozenset(
    {"architecture", "dependency", "scope", "security"})

ASK_CLASSES: frozenset[str] = frozenset(
    {"architecture", "dependency", "scope", "security", "owner_gate", "legal",
     "credential", "payment", "evidence_conflict", "destructive", "unclassified"})

#: S4.5 - the SHORT synchronous-stop list. Everything else must be AUTO, NOTIFY
#: or a queued ASK. This tuple is the whole list; nothing may be added to it by
#: configuration.
SYNCHRONOUS_STOP_CONDITIONS: tuple[str, ...] = (
    "owner_emergency_stop",
    "owner_manual_pause",
    "unsafe_or_drifted_recovery",
    "suspected_secret_leakage",
    "controller_integrity_failure",
    "unexplained_concurrent_writer",
    "provider_auth_or_org_change",
    "deny_and_halt",
    "circuit_breaker_hard_threshold",
    "blocking_ask_with_no_independent_unit",
)


class PolicyError(Exception):
    """A policy input was malformed. Fail closed; never default to permissive."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


class GrantError(PolicyError):
    """A standing grant was refused. Models may never create or widen a grant."""


@dataclasses.dataclass(frozen=True)
class PolicyDecision:
    """One deterministic classification. Always carries WHY."""

    tier: str
    reason_code: str
    reason: str
    outcome: str = ""              # DENY_AND_CONTINUE / DENY_AND_HALT when HARD_DENY
    rule_id: str = ""
    classification: str = ""       # S4.3 class when ASK
    advisory_eligible: bool = False
    matched_grant: str = ""
    synchronous_stop: bool = False
    policy_version: str = POLICY_VERSION
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @property
    def blocks_dependent_work(self) -> bool:
        return self.tier == ASK and self.classification in BLOCKING_ASK_CLASSES

    def stricter_of(self, other: "PolicyDecision") -> "PolicyDecision":
        return other if TIER_ORDER[other.tier] > TIER_ORDER[self.tier] else self


def _deny(outcome: str, rule_id: str, reason_code: str, reason: str) -> PolicyDecision:
    return PolicyDecision(
        tier=HARD_DENY, reason_code=reason_code, reason=reason, outcome=outcome,
        rule_id=rule_id, synchronous_stop=(outcome == DENY_AND_HALT))


def _ask(rule_id: str, reason_code: str, reason: str, classification: str,
         advisory_eligible: bool = False) -> PolicyDecision:
    if classification not in ASK_CLASSES:
        raise PolicyError("unknown_ask_class", f"{classification!r} is not an ASK class")
    return PolicyDecision(tier=ASK, reason_code=reason_code, reason=reason,
                          rule_id=rule_id, classification=classification,
                          advisory_eligible=advisory_eligible)


def _auto(rule_id: str, reason_code: str, reason: str, *, grant: str = "",
          advisory_eligible: bool = False) -> PolicyDecision:
    return PolicyDecision(tier=AUTO, reason_code=reason_code, reason=reason,
                          rule_id=rule_id, matched_grant=grant,
                          advisory_eligible=advisory_eligible)


# --------------------------------------------------------------------------
# Path handling (S13.5 canonicalization, S4.1 allowed_paths)
# --------------------------------------------------------------------------


def _glob_to_regex(pattern: str) -> re.Pattern[str]:
    """Translate a posix-style path glob into a regex.

    `**` crosses directory separators, `*` and `?` do not. Patterns are matched
    against the repository-relative posix path.
    """
    out = ["(?s)\\A"]
    index = 0
    length = len(pattern)
    while index < length:
        char = pattern[index]
        if char == "*":
            if pattern.startswith("**", index):
                index += 2
                if pattern.startswith("/", index):
                    index += 1
                    out.append("(?:.*/)?")
                else:
                    out.append(".*")
                continue
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        elif char == "[":
            close = pattern.find("]", index)
            if close == -1:
                out.append(re.escape(char))
            else:
                out.append(pattern[index:close + 1])
                index = close
        else:
            out.append(re.escape(char))
        index += 1
    out.append("\\Z")
    return re.compile("".join(out))


def path_matches(relative_posix: str, pattern: str) -> bool:
    """True when a repository-relative posix path matches an allowed-path glob.

    A bare directory pattern (`tools/agent_supervisor`) matches the directory and
    everything under it, which is how the task packets are written.
    """
    pattern = pattern.strip()
    if not pattern:
        return False
    if _glob_to_regex(pattern).match(relative_posix):
        return True
    if not pattern.endswith("/") and "*" not in pattern:
        return _glob_to_regex(pattern.rstrip("/") + "/**").match(relative_posix) is not None
    return False


def clean_allowed_path_entry(entry: str) -> str:
    """Strip the human annotation task packets attach to an allowed path.

    Packets are written for humans: `tools/agent_supervisor/** (create; per D-007
    Section 6 layout)`. The authority object stores the pattern only, so an
    annotation can never widen or narrow a match by accident.
    """
    text = entry.strip()
    cut = text.find(" (")
    if cut != -1:
        text = text[:cut]
    return text.strip().rstrip(",").strip()


@dataclasses.dataclass(frozen=True)
class ResolvedTarget:
    """One canonicalized target path plus the reason it may be unusable."""

    raw: str
    canonical: str
    relative_posix: str
    inside_root: bool
    escape_reason: str = ""
    file_identity: str = ""


def _norm(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))


#: Windows reserved DEVICE names. A path component equal to one of these (with or
#: without an extension) is not a file at all - `os.path.realpath` maps it to
#: `\\.\nul` and friends, and `os.path.relpath` then RAISES rather than returning
#: a path. Found by the Phase 4 path-normalization fuzzer with the input
#: `.env;/nul`, which crashed `resolve_target` instead of denying it.
WINDOWS_RESERVED_DEVICE_NAMES: frozenset[str] = frozenset({
    "con", "prn", "aux", "nul",
    *(f"com{n}" for n in range(1, 10)),
    *(f"lpt{n}" for n in range(1, 10)),
})


def _names_a_reserved_device(text: str) -> bool:
    """True when any path component is a Windows reserved device name."""
    for part in re.split(r"[\\/]+", text):
        stem = part.split(".", 1)[0].strip().lower()
        if stem in WINDOWS_RESERVED_DEVICE_NAMES:
            return True
    return False


def file_identity(path: str | os.PathLike[str]) -> str:
    """A stable identity string for an existing file (S13.5 file identity).

    Uses the filesystem's own identifiers (device + inode on POSIX; volume serial
    + file index on Windows, which CPython exposes through `st_dev`/`st_ino`)
    plus size and mtime. Hard links, replacement races, and case-only renames
    change this string even when the path does not.
    """
    try:
        stat = os.stat(path)
    except OSError:
        return "absent"
    return f"dev={stat.st_dev};ino={stat.st_ino};size={stat.st_size};mtime={stat.st_mtime_ns}"


def resolve_target(raw: str, root: str | os.PathLike[str]) -> ResolvedTarget:
    """Canonicalize a proposed target path and detect every escape shape.

    Defends: `..` traversal, absolute paths outside the root, symlink/junction
    escapes (via `os.path.realpath`, which resolves reparse points on Windows),
    unresolved shell/environment variables, NTFS alternate data streams, and
    device paths. Paths with spaces are ordinary and are NOT rejected.
    """
    text = str(raw)
    if not text.strip():
        return ResolvedTarget(text, "", "", False, "empty_path")
    if "\x00" in text:
        return ResolvedTarget(text, "", "", False, "nul_byte")
    if re.search(r"\$\{|\$[A-Za-z_]|%[A-Za-z_][A-Za-z0-9_]*%|(?:^|[/\\])~(?:[/\\]|$)", text):
        # An unexpanded variable means the true target is unknown at policy time.
        return ResolvedTarget(text, "", "", False, "unresolved_variable")

    # A reserved DEVICE name is refused before any resolution is attempted: it
    # never denotes a file, and letting it reach `realpath`/`relpath` makes them
    # raise. Checked on every platform so a POSIX CI run enforces the same rule a
    # Windows host does.
    if _names_a_reserved_device(text):
        return ResolvedTarget(text, "", "", False, "device_path")

    try:
        root_real = os.path.realpath(str(root))
        candidate = text if os.path.isabs(text) else os.path.join(root_real, text)
        real = os.path.realpath(candidate)
    except (OSError, ValueError):
        # Canonicalization itself failed: the true target cannot be established,
        # so it is refused rather than guessed.
        return ResolvedTarget(text, "", "", False, "unresolvable_path")

    # Alternate data stream / device path shapes on Windows.
    tail = os.path.basename(real)
    if os.name == "nt" and tail.count(":") >= 1:
        return ResolvedTarget(text, real, "", False, "alternate_data_stream")
    if text.startswith("\\\\.\\") or text.startswith("\\\\?\\GLOBALROOT") \
            or real.startswith("\\\\.\\") or real.startswith("\\\\?\\GLOBALROOT"):
        return ResolvedTarget(text, real, "", False, "device_path")

    inside = _norm(real) == _norm(root_real) or _norm(real).startswith(
        _norm(root_real) + os.sep)
    relative = ""
    escape = ""
    if inside:
        try:
            relative = pathlib.PurePath(os.path.relpath(real, root_real)).as_posix()
        except ValueError:
            # Different mounts/devices: not a relative path at all.
            return ResolvedTarget(text, real, "", False, "device_path")
        if relative == ".":
            relative = ""
    else:
        # Distinguish a plain out-of-tree path from a link that pretends to be
        # in-tree: the lexical path stays inside but the real path does not.
        lexical = os.path.normpath(candidate)
        lexical_inside = _norm(lexical) == _norm(root_real) or _norm(lexical).startswith(
            _norm(root_real) + os.sep)
        escape = "symlink_or_junction_escape" if lexical_inside else "outside_root"
    return ResolvedTarget(text, real, relative, inside, escape,
                          file_identity(real) if inside else "")


# --------------------------------------------------------------------------
# File classes (S4.1 security-relevant exclusions, S13.6 push classes)
# --------------------------------------------------------------------------

FILE_CLASS_PATTERNS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("workflow", (".github/workflows/**", ".github/**", ".gitlab-ci.yml",
                  "azure-pipelines.yml", "Jenkinsfile")),
    ("hook", (".git/hooks/**", ".claude/hooks/**", ".husky/**",
              ".pre-commit-config.yaml")),
    ("permission_settings", (".claude/settings.json", ".claude/settings.local.json",
                             ".claude/settings*.json", ".claude/rules/**",
                             ".claude/agents/**", ".claude/skills/**",
                             ".codex/config.toml", ".vscode/settings.json")),
    ("secret_bearing", (".env", ".env.*", "*.pem", "*.key", "*.pfx", "*.p12",
                        "id_rsa*", "id_ed25519*", "*.credentials.json",
                        "credentials.json", ".git-credentials", ".netrc",
                        ".npmrc", "*secrets*.json", "*secrets*.yml",
                        "*secrets*.yaml")),
    ("lockfile", ("package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
                  "Pipfile.lock", "Cargo.lock", "go.sum", "composer.lock",
                  "requirements.lock", "**/package-lock.json", "**/yarn.lock",
                  "**/pnpm-lock.yaml", "**/poetry.lock", "**/Cargo.lock")),
    ("dependency_manifest", ("package.json", "pyproject.toml", "requirements*.txt",
                             "Pipfile", "Cargo.toml", "go.mod", "Gemfile",
                             "composer.json", "**/package.json",
                             "**/requirements*.txt", "**/pyproject.toml")),
    ("deploy_definition", ("render.yaml", "render.yml", "Dockerfile", "Dockerfile.*",
                           "docker-compose*.yml", "docker-compose*.yaml",
                           "vercel.json", "netlify.toml", "fly.toml", "*.tf",
                           "k8s/**", "deploy/**", "infra/**", "helm/**")),
    ("launcher_script", ("*.ps1", "*.bat", "*.cmd", "*.sh", "scripts/**")),
    ("submodule_config", (".gitmodules",)),
    ("attributes_filter", (".gitattributes",)),
)

#: Everything in this set is excluded from baseline AUTO (S4.1) and requires an
#: owner gate on a push (S13.6).
SECURITY_RELEVANT_CLASSES: frozenset[str] = frozenset({
    "workflow", "hook", "permission_settings", "secret_bearing", "lockfile",
    "dependency_manifest", "deploy_definition", "launcher_script",
    "submodule_config", "attributes_filter",
})

ORDINARY = "ordinary"


def file_class(relative_posix: str) -> str:
    """Classify a repository-relative path. Most-sensitive class wins.

    Only a leading `./` is removed. `str.lstrip("./")` would eat the leading dot
    of `.env`, `.gitmodules`, and `.github/...` and quietly reclassify every
    security-relevant dotfile as ordinary - a bug this function was written with
    and its tests caught.
    """
    text = relative_posix.strip().replace("\\", "/")
    while text.startswith("./"):
        text = text[2:]
    text = text.lstrip("/")
    if not text:
        return ORDINARY
    base = posixpath.basename(text)
    for name, patterns in FILE_CLASS_PATTERNS:
        for pattern in patterns:
            if path_matches(text, pattern):
                return name
            if "/" not in pattern and fnmatch.fnmatch(base, pattern):
                return name
    return ORDINARY


#: Absolute-ish credential store shapes. Reading, printing, copying, uploading or
#: logging any of these is a HARD-DENY / DENY_AND_HALT (S4.4).
CREDENTIAL_PATH_MARKERS: tuple[str, ...] = (
    ".ssh/", ".aws/credentials", ".aws/config", ".gnupg/", ".config/gh/",
    ".codex/auth.json", ".claude/.credentials.json", ".docker/config.json",
    "keychain", "login.keychain", "credentials.sqlite", ".git-credentials",
    ".netrc", "_netrc", ".azure/", ".kube/config",
)

#: Commands whose whole purpose is to dump the environment or an auth store.
CREDENTIAL_COMMAND_SHAPES: tuple[tuple[str, ...], ...] = (
    ("printenv",), ("env",), ("set",), ("gh", "auth", "token"),
    ("git", "credential", "fill"), ("cmdkey",), ("security", "find-generic-password"),
)


def _looks_like_credential_path(text: str) -> bool:
    lowered = text.replace("\\", "/").lower()
    if any(marker in lowered for marker in CREDENTIAL_PATH_MARKERS):
        return True
    return file_class(lowered.lstrip("/")) == "secret_bearing"


# --------------------------------------------------------------------------
# Command shapes (inspection only - nothing here executes)
# --------------------------------------------------------------------------

#: Read-only git subcommands the supervisor enumerates for AUTO (S4.1). Anything
#: not on this list is not a read-only git command as far as policy is concerned.
READ_ONLY_GIT_SUBCOMMANDS: frozenset[str] = frozenset({
    "status", "diff", "rev-parse", "log", "show", "ls-files", "ls-tree",
    "cat-file", "merge-base", "describe", "name-rev", "rev-list", "shortlog",
    "blame", "count-objects", "for-each-ref", "symbolic-ref", "check-ignore",
    "diff-tree", "whatchanged", "grep", "verify-commit",
})

#: Git global options that change where or how git runs. Refused during
#: evidence collection and never AUTO (S13.6: no aliases, pagers, external diff).
UNSAFE_GIT_GLOBAL_OPTIONS: tuple[str, ...] = (
    "-c", "--exec-path", "--git-dir", "--work-tree", "--namespace", "-C",
    "--upload-pack", "--receive-pack", "-P", "--paginate",
)

#: Subcommand-level flags that turn a read-only git command into something that
#: runs external code or writes a file.
UNSAFE_GIT_SUBCOMMAND_FLAGS: tuple[str, ...] = (
    "--ext-diff", "--textconv", "--exec", "--output", "-o",
)

DESTRUCTIVE_GIT_SHAPES: tuple[tuple[str, ...], ...] = (
    ("git", "reset", "--hard"),
    ("git", "clean"),
    ("git", "checkout", "--"),
    ("git", "restore"),
)

#: Delete verbs across the shells that exist on this platform.
DELETE_VERBS: frozenset[str] = frozenset({
    "rm", "del", "erase", "rmdir", "rd", "unlink", "remove-item", "ri",
    "shred", "srm",
})

RECURSIVE_DELETE_FLAGS: frozenset[str] = frozenset({
    "-r", "-rf", "-fr", "-rrf", "--recursive", "/s", "-force", "-recurse",
    "-recurse:$true", "/q",
})

SHELL_METACHARACTERS: tuple[str, ...] = ("|", ">", "<", "&", ";", "\n", "\r")
SUBSTITUTION_MARKERS: tuple[str, ...] = ("$(", "`", "${", "$env:", "%(",
                                         "iex ", "invoke-expression", "eval ",
                                         "| sh", "| bash", "|sh", "|bash",
                                         "-encodedcommand", "-enc ")

#: Command shapes that disable a control. Any of these is DENY_AND_HALT (S4.4).
CONTROL_DISABLING_MARKERS: tuple[str, ...] = (
    "--no-verify", "core.hookspath", "--disable-hooks", "--no-hooks",
    "secret_scanning", "branch_protection", "skipsecretscan",
    "gitleaks.enabled=false",
)


@dataclasses.dataclass(frozen=True)
class CommandShape:
    """The inspected shape of a proposed command. NEVER executed by this module."""

    raw: str
    tokens: tuple[str, ...]
    segments: tuple[tuple[str, ...], ...]
    has_substitution: bool
    has_metacharacter: bool
    parse_error: str = ""

    @property
    def program(self) -> str:
        return self.tokens[0] if self.tokens else ""


def _strip_quotes(token: str) -> str:
    if len(token) >= 2 and token[0] == token[-1] and token[0] in "\"'":
        return token[1:-1]
    return token


def _split_segments(tokens: Sequence[str]) -> tuple[tuple[str, ...], ...]:
    segments: list[tuple[str, ...]] = []
    current: list[str] = []
    for token in tokens:
        if token in ("&&", "||", ";", "|", "&"):
            if current:
                segments.append(tuple(current))
            current = []
            continue
        current.append(token)
    if current:
        segments.append(tuple(current))
    return tuple(segments)


def parse_command(raw: str | Sequence[str]) -> CommandShape:
    """Tokenize a proposed command for INSPECTION.

    A command arriving as a string (the Claude `Bash` tool's shape) is exactly
    the shape shell interpolation needs, so it is tokenized here only to classify
    it. The supervisor never re-serializes it into a shell.
    """
    if isinstance(raw, (list, tuple)):
        tokens = tuple(str(item) for item in raw)
        text = " ".join(tokens)
        substitution = any(marker in text.lower() for marker in SUBSTITUTION_MARKERS)
        meta = any(ch in token for token in tokens for ch in SHELL_METACHARACTERS)
        return CommandShape(text, tokens, _split_segments(tokens), substitution, meta)

    text = str(raw)
    lowered = text.lower()
    substitution = any(marker in lowered for marker in SUBSTITUTION_MARKERS)
    meta = any(ch in text for ch in SHELL_METACHARACTERS)
    try:
        tokens = tuple(_strip_quotes(t) for t in shlex.split(text, posix=False))
        error = ""
    except ValueError as exc:
        tokens = ()
        error = str(exc)
    return CommandShape(text, tokens, _split_segments(tokens), substitution, meta, error)


def _program_name(token: str) -> str:
    """Basename of argv[0] without an executable suffix, lowercased."""
    base = posixpath.basename(str(token).replace("\\", "/")).lower()
    for suffix in (".exe", ".cmd", ".bat", ".com", ".ps1"):
        if base.endswith(suffix):
            return base[: -len(suffix)]
    return base


def _is_destructive_segment(segment: Sequence[str]) -> str:
    """Return a reason code when a command segment destroys things, else ''."""
    if not segment:
        return ""
    program = _program_name(segment[0])
    rest = list(segment[1:])
    lowered_rest = [t.lower() for t in rest]

    if program == "git":
        for shape in DESTRUCTIVE_GIT_SHAPES:
            wanted = list(shape[1:])
            if lowered_rest[:len(wanted)] == wanted:
                return f"destructive_git:{'_'.join(w.strip('-') or 'discard' for w in wanted)}"

    if program in DELETE_VERBS:
        recursive_flags = {f.lower() for f in RECURSIVE_DELETE_FLAGS}
        recursive = any(flag in recursive_flags for flag in lowered_rest)
        targets = [t for t in rest if not t.startswith("-") and not t.startswith("/")]
        wildcard = any("*" in t or "?" in t for t in targets)
        if recursive or wildcard:
            return "recursive_or_wildcard_delete"
        return "delete_command"
    return ""


DANGEROUS_DELETE_TARGETS: tuple[str, ...] = (
    ".", "..", "./", "../", "/", "\\", "*", "**", "~", "~/",
)


def _dangerous_delete_target(target: str, *, root: str, worktree: str) -> str:
    """Reason code when a delete target is a root, home, parent, or wildcard."""
    text = str(target).strip().strip('"').strip("'")
    if text in DANGEROUS_DELETE_TARGETS:
        return "delete_targets_root_or_wildcard"
    if re.fullmatch(r"[A-Za-z]:[\\/]?", text):
        return "delete_targets_drive_root"
    if re.search(r"\$\{|\$[A-Za-z_]|%[A-Za-z_][A-Za-z0-9_]*%", text):
        return "delete_targets_unresolved_variable"
    if text.startswith("~"):
        return "delete_targets_home_directory"
    if "*" in text or "?" in text:
        return "delete_targets_wildcard"
    resolved = resolve_target(text, root)
    if resolved.escape_reason in ("symlink_or_junction_escape", "outside_root"):
        return f"delete_target_{resolved.escape_reason}"
    for boundary in (root, worktree):
        if boundary and _norm(resolved.canonical) == _norm(os.path.realpath(boundary)):
            return "delete_targets_repository_or_worktree_root"
    home = os.path.expanduser("~")
    if _norm(resolved.canonical) == _norm(home):
        return "delete_targets_home_directory"
    return ""


# --------------------------------------------------------------------------
# Prompt-injection neutralization (S8.3, S13.2)
# --------------------------------------------------------------------------

INJECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("override_instruction", re.compile(
        r"(?i)\b(ignore|disregard|forget|override)\b[^.\n]{0,40}\b"
        r"(previous|prior|above|earlier|all)\b[^.\n]{0,25}\b"
        r"(instruction|rule|policy|direction)")),
    ("role_reassignment", re.compile(
        r"(?i)\byou are now\b|\bact as (?:the )?(?:owner|administrator|supervisor)\b|"
        r"\bnew system prompt\b")),
    ("approval_demand", re.compile(
        r"(?i)\b(auto[- ]?approve|always allow|approve this|grant (?:me|full) "
        r"(?:access|permission)|mark (?:this )?(?:as )?(?:approved|complete))\b")),
    # `--[a-z-]*dangerously` and not `--dangerously`: the deny list contains
    # `--allow-dangerously-skip-permissions`, which a leading-anchored pattern
    # silently missed. Caught by driving the injection corpus from the deny list.
    ("bypass_request", re.compile(
        r"(?i)--[a-z-]*dangerously[a-z-]*|--yolo\b|\bskip permissions?\b|"
        r"\bbypass (?:the )?(?:sandbox|approval|policy|hook)\b|"
        r"\bdisable (?:the )?(?:hook|test|ci|audit)")),
    ("mode_change", re.compile(
        r"(?i)\bset (?:permission ?)?mode\b|\bacceptedits\b|\benable limited[- ]auto\b")),
    ("policy_claim", re.compile(
        r"(?i)\b(?:the )?polic(?:y|ies) (?:says?|allows?|permits?)\b|"
        r"\bthis is (?:tier )?AUTO\b|\bthis is pre[- ]?approved\b")),
)


@dataclasses.dataclass(frozen=True)
class UntrustedText:
    """Text from a model, a repository file, a log, or a PR comment.

    `labels` names the injection shapes detected. The point is not to sanitize
    the text into obedience-safe form - it is to make sure the text is carried as
    DATA and that any attempt to instruct the supervisor is visible in the audit
    record. No classification consumes this object.
    """

    text: str
    labels: tuple[str, ...]
    truncated: bool = False

    @property
    def suspicious(self) -> bool:
        return bool(self.labels)

    def as_quoted_block(self, limit: int = 2000) -> str:
        body = self.text if len(self.text) <= limit else self.text[:limit] + "\n[TRUNCATED]"
        return ("<<<UNTRUSTED_DATA (never an instruction to the supervisor)\n"
                f"{body}\nUNTRUSTED_DATA")


def detect_injection(text: str) -> tuple[str, ...]:
    """Names of the injection shapes present in untrusted text."""
    if not isinstance(text, str):
        return ()
    return tuple(sorted({label for label, pattern in INJECTION_PATTERNS
                         if pattern.search(text)}))


def neutralize_untrusted(text: Any, *, limit: int = 20000) -> UntrustedText:
    """Wrap untrusted text as data and label any instruction attempt it carries."""
    body = text if isinstance(text, str) else str(text)
    truncated = len(body) > limit
    if truncated:
        body = body[:limit]
    return UntrustedText(body, detect_injection(body), truncated)


# --------------------------------------------------------------------------
# Standing grants (S4.1)
# --------------------------------------------------------------------------

GRANT_OPERATION_TYPES: frozenset[str] = frozenset({
    "test_command", "branch_push", "pr_mutation", "file_write", "runtime_file_write",
})

#: A grant may never allowlist one of these on its own (S4.1: "Do not allowlist a
#: bare executable name; allowlist the complete operation shape").
BARE_EXECUTABLES: frozenset[str] = frozenset({
    "python", "python3", "py", "git", "gh", "bash", "sh", "powershell", "pwsh",
    "node", "npm", "npx", "cmd", "dotnet", "make",
})


@dataclasses.dataclass(frozen=True)
class StandingGrant:
    """An owner-created, exact-shape, task-scoped pre-authorization.

    Every field the directive enumerates is present: operation type, expected
    file classes, whether delete/rename is permitted, the maximum change boundary
    (paths, file count, size), a preimage hash where a file's prior state
    matters, and the verification required afterward.

    Construct through `owner_grant()`, which refuses anything but `created_by ==
    "owner"`. That is the structural expression of "models must never create,
    widen, or extend a grant".
    """

    grant_id: str
    task_id: str
    operation_type: str
    created_by: str
    post_verification: str
    argv_shapes: tuple[str, ...] = ()
    path_scope: tuple[str, ...] = ()
    file_classes: tuple[str, ...] = (ORDINARY,)
    delete_permitted: bool = False
    rename_permitted: bool = False
    max_file_count: int = 0
    max_change_bytes: int = 0
    preimage_sha256: str = ""
    branch: str = ""
    requires_passing_review: bool = False
    requires_mode: str = ""
    expires_with_task: bool = True

    def digest(self) -> str:
        return digest_of(dataclasses.asdict(self))

    def is_active(self, *, task_id: str, task_status: str = "in_progress") -> bool:
        """A grant expires with its task. Nothing extends it."""
        if self.task_id != task_id:
            return False
        if self.expires_with_task and task_status not in ("in_progress", "awaiting_gate",
                                                          "claimed"):
            return False
        return True


def owner_grant(**fields: Any) -> StandingGrant:
    """Build an owner grant, refusing every shape the directive forbids."""
    known = {f.name for f in dataclasses.fields(StandingGrant)}
    unknown = sorted(set(fields) - known)
    if unknown:
        raise GrantError("unknown_grant_field", f"unrecognized grant fields: {unknown}")

    created_by = str(fields.get("created_by", ""))
    if created_by != "owner":
        raise GrantError(
            "model_created_grant",
            "standing grants are owner-created; a grant with created_by="
            f"{created_by!r} is refused. Models must never create, widen, or extend "
            "a grant (S4.1)")
    operation = str(fields.get("operation_type", ""))
    if operation not in GRANT_OPERATION_TYPES:
        raise GrantError("unknown_operation_type",
                         f"{operation!r} is not one of {sorted(GRANT_OPERATION_TYPES)}")
    if not str(fields.get("post_verification", "")).strip():
        raise GrantError("missing_post_verification",
                         "a grant must state the verification required afterward (S4.1)")
    if not str(fields.get("grant_id", "")).strip() or not str(fields.get("task_id", "")).strip():
        raise GrantError("missing_identity", "a grant needs a grant_id and a task_id")

    shapes = tuple(fields.get("argv_shapes", ()) or ())
    for shape in shapes:
        parts = shape.split()
        if len(parts) < 2:
            raise GrantError(
                "bare_executable_grant",
                f"grant shape {shape!r} allowlists a bare executable; allowlist the "
                f"complete operation shape (S4.1)")
        if _program_name(parts[0]) in BARE_EXECUTABLES and all(
                part.strip("*") == "" for part in parts[1:]):
            raise GrantError(
                "bare_executable_grant",
                f"grant shape {shape!r} is a bare executable with unconstrained "
                f"arguments; that is never a complete operation shape (S4.1)")
    if operation == "branch_push":
        branch = str(fields.get("branch", ""))
        if not branch:
            raise GrantError("missing_branch", "a push grant must name its exact branch")
        if branch.lower() in ("main", "master", "head"):
            raise GrantError("main_branch_grant",
                             "no grant may authorize a push to main; S4.4 hard-denies it")
    return StandingGrant(**fields)


def assert_not_widened(original: StandingGrant, candidate: StandingGrant) -> None:
    """Refuse any change that makes an existing grant broader (S4.1)."""
    if original.grant_id != candidate.grant_id:
        raise GrantError("grant_identity_changed", "a grant id may not be reassigned")
    widenings: list[str] = []
    if set(candidate.argv_shapes) - set(original.argv_shapes):
        widenings.append("argv_shapes")
    if set(candidate.path_scope) - set(original.path_scope):
        widenings.append("path_scope")
    if set(candidate.file_classes) - set(original.file_classes):
        widenings.append("file_classes")
    if candidate.delete_permitted and not original.delete_permitted:
        widenings.append("delete_permitted")
    if candidate.rename_permitted and not original.rename_permitted:
        widenings.append("rename_permitted")
    if candidate.max_file_count > original.max_file_count:
        widenings.append("max_file_count")
    if candidate.max_change_bytes > original.max_change_bytes:
        widenings.append("max_change_bytes")
    if candidate.branch != original.branch:
        widenings.append("branch")
    if candidate.expires_with_task is False and original.expires_with_task:
        widenings.append("expires_with_task")
    if widenings:
        raise GrantError("grant_widened",
                         f"grant {original.grant_id} would be widened in {widenings}")


def _shape_matches(shape: str, tokens: Sequence[str]) -> bool:
    """Token-by-token glob match of a grant shape against a concrete argv."""
    parts = shape.split()
    if len(parts) != len(tokens):
        return False
    for index, (pattern, token) in enumerate(zip(parts, tokens)):
        if index == 0:
            candidate = _program_name(token)
            pattern = _program_name(pattern)
        else:
            candidate = str(token).replace("\\", "/")
            pattern = pattern.replace("\\", "/")
        if not fnmatch.fnmatch(candidate, pattern):
            return False
    return True


# --------------------------------------------------------------------------
# Task authority and policy configuration
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class TaskAuthority:
    """The authority the current controlled task actually confers.

    The supervisor NEVER derives authority from a model's description of the
    task; this object is built from the task packet on disk.
    """

    task_id: str
    stage: str
    repo_root: str
    worktree: str
    branch: str
    allowed_paths: tuple[str, ...] = ()
    forbidden_paths: tuple[str, ...] = ()
    documented_test_commands: tuple[str, ...] = ()
    grants: tuple[StandingGrant, ...] = ()
    runtime_dir: str = ""
    push_branch: str = ""
    status: str = "in_progress"
    active: bool = True

    @classmethod
    def from_packet(
        cls,
        packet: Mapping[str, Any],
        *,
        repo_root: str,
        worktree: str,
        branch: str,
        stage: str = "",
        grants: Sequence[StandingGrant] = (),
        documented_test_commands: Sequence[str] = (),
        runtime_dir: str = "",
        push_branch: str = "",
    ) -> "TaskAuthority":
        allowed = tuple(clean_allowed_path_entry(entry)
                        for entry in packet.get("allowed_paths", []) or ())
        forbidden = tuple(clean_allowed_path_entry(entry)
                          for entry in packet.get("forbidden_paths", []) or ())
        status = str(packet.get("status", "in_progress"))
        return cls(
            task_id=str(packet.get("task_id", "")),
            stage=stage or status,
            repo_root=repo_root,
            worktree=worktree,
            branch=branch,
            allowed_paths=tuple(p for p in allowed if p),
            forbidden_paths=tuple(p for p in forbidden if p),
            documented_test_commands=tuple(documented_test_commands),
            grants=tuple(grants),
            runtime_dir=runtime_dir,
            push_branch=push_branch,
            status=status,
            active=status in ("in_progress", "claimed", "awaiting_gate"),
        )

    def active_grants(self) -> tuple[StandingGrant, ...]:
        return tuple(g for g in self.grants
                     if g.is_active(task_id=self.task_id, task_status=self.status))


@dataclasses.dataclass(frozen=True)
class PolicyConfig:
    """Deterministic bounds read from the immutable controller config `[policy]`."""

    max_changed_files_per_checkpoint: int = 20
    max_change_bytes_per_checkpoint: int = 262_144
    max_single_file_bytes: int = 131_072
    main_branch_names: tuple[str, ...] = ("main", "master")
    allow_remote_reads: bool = False
    advisory_eligible_categories: tuple[str, ...] = (
        "read_only_inspection", "in_scope_file_edit", "documented_test_command")

    @classmethod
    def from_controller_config(cls, config: Any) -> "PolicyConfig":
        """Read `[policy]` out of the immutable config, failing closed."""
        raw = getattr(config, "raw", {}) or {}
        section = raw.get("policy", {}) or {}
        if not isinstance(section, Mapping):
            raise PolicyError("bad_policy_section", "[policy] must be a table")
        known = {f.name for f in dataclasses.fields(cls)}
        unknown = sorted(set(section) - known)
        if unknown:
            raise PolicyError("unknown_policy_key",
                              f"unrecognized [policy] keys: {unknown}")
        values: dict[str, Any] = {}
        for key, value in section.items():
            if key in ("main_branch_names", "advisory_eligible_categories"):
                if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                    raise PolicyError("bad_policy_value",
                                      f"[policy].{key} must be a list of strings")
                values[key] = tuple(value)
            elif key == "allow_remote_reads":
                if not isinstance(value, bool):
                    raise PolicyError("bad_policy_value",
                                      "[policy].allow_remote_reads must be a boolean")
                values[key] = value
            else:
                if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                    raise PolicyError("bad_policy_value",
                                      f"[policy].{key} must be a positive integer")
                values[key] = value
        return cls(**values)


DEFAULT_POLICY_CONFIG = PolicyConfig()


# --------------------------------------------------------------------------
# Proposed actions
# --------------------------------------------------------------------------

ACTION_KINDS: frozenset[str] = frozenset({
    "read", "command", "git_command", "file_write", "file_delete", "file_rename",
    "runtime_file_write", "push", "pr_mutation", "external_write",
    "forwarded_prompt", "session_resume", "handoff_generation", "subagent",
    "network", "unknown",
})

# --------------------------------------------------------------------------
# Trust zones (S13.2) - added in Phase 4
# --------------------------------------------------------------------------
#
# S13.2 names three zones, and S13.12 turns two of them into invariants:
# invariant 10 "no reviewer write access" and invariant 11 "no worker access to
# the active controller". Invariant 11 was already enforced by the S13.1
# controller-mutation rule below. Invariant 10 was NOT expressible before,
# because a `ProposedAction` carried no origin - the Phase 4 adversarial matrix
# is what surfaced that. `origin_zone` defaults to WORKER, so every action built
# before this existed classifies exactly as it did.

ZONE_CONTROLLER = "CONTROLLER"
ZONE_WORKER = "WORKER"
ZONE_REVIEWER = "REVIEWER"

TRUST_ZONES: tuple[str, ...] = (ZONE_CONTROLLER, ZONE_WORKER, ZONE_REVIEWER)

#: The ONLY action kinds a REVIEWER may ever propose. The reviewer reads
#: evidence; it does not write, and it does not execute worker-modified code to
#: review it (S13.2).
REVIEWER_PERMITTED_KINDS: frozenset[str] = frozenset({"read"})

#: Kinds that mutate something, anywhere.
MUTATING_KINDS: frozenset[str] = frozenset({
    "file_write", "file_delete", "file_rename", "runtime_file_write", "push",
    "pr_mutation", "external_write",
})


@dataclasses.dataclass(frozen=True)
class ProposedAction:
    """One thing somebody wants to do. The unit of classification.

    `stated_reason` is Claude's own words. It is recorded and NEVER read by
    `evaluate()`.
    """

    kind: str
    tool_name: str = ""
    tool_input: Mapping[str, Any] = dataclasses.field(default_factory=dict)
    argv: tuple[str, ...] = ()
    command_text: str = ""
    target_paths: tuple[str, ...] = ()
    change_bytes: int = 0
    change_file_count: int = 1
    branch: str = ""
    effect_type: str = ""
    event_type: str = ""
    owner_gate: str = ""
    category: str = ""
    request_id: str = ""
    stated_reason: str = ""
    #: Which S13.2 trust zone proposed this. Defaults to WORKER, which is what
    #: every pre-Phase-4 call site meant.
    origin_zone: str = ZONE_WORKER

    def __post_init__(self) -> None:
        if self.kind not in ACTION_KINDS:
            raise PolicyError("unknown_action_kind",
                              f"{self.kind!r} is not one of {sorted(ACTION_KINDS)}")
        if self.origin_zone not in TRUST_ZONES:
            raise PolicyError("unknown_trust_zone",
                              f"{self.origin_zone!r} is not one of {list(TRUST_ZONES)}; an "
                              f"unrecognized origin is never treated as trusted")

    def command_shape(self) -> CommandShape:
        if self.argv:
            return parse_command(list(self.argv))
        return parse_command(self.command_text)


#: Owner gates that can only ever queue (S4.3), and are simultaneously barred
#: from every automatic path (S5.2, S13.12 invariant 9).
OWNER_GATES: frozenset[str] = frozenset({
    "merge", "task_acceptance", "hold_release", "production_deploy", "g6_legal",
    "legal_publication", "credential", "payment", "milestone_change",
    "dependency_addition", "policy_exception", "permission_config_change",
})


# --------------------------------------------------------------------------
# HARD-DENY rules (S4.4)
# --------------------------------------------------------------------------

#: ONE deny list, not two. These are re-exported from `process.py` rather than
#: restated, so the argv validator and the policy engine can never drift apart -
#: and so the flag names appear as literals in exactly one place in the package.
BYPASS_FLAG_MARKERS: tuple[str, ...] = tuple(sorted(HARD_DENY_ARGUMENTS))

EFFORT_FLAG_MARKERS: tuple[str, ...] = tuple(EFFORT_ARGUMENT_PREFIXES)

#: Paths that ARE the controller. Mutating any of them halts (S13.1).
CONTROLLER_PATHS: tuple[str, ...] = ("tools/agent_supervisor/**",
                                     "tools/agent_supervisor")


def _hard_deny(action: ProposedAction, authority: TaskAuthority,
               config: PolicyConfig) -> PolicyDecision | None:
    """Apply S4.4 in a fixed order. Returns None when nothing hard-denies."""
    shape = action.command_shape()
    joined = " ".join(action.argv) if action.argv else action.command_text
    lowered = f"{joined} {action.tool_name}".lower()

    # 0. Trust-zone containment (S13.2, S13.12 invariants 10 and 11).
    #
    # The reviewer is read-only, full stop. A reviewer-originated mutation is not
    # a policy question to weigh - it is evidence that the confinement layer
    # failed, which is exactly the B-015 class of defect, so it halts rather than
    # merely being refused.
    if action.origin_zone == ZONE_REVIEWER and action.kind not in REVIEWER_PERMITTED_KINDS:
        if action.kind in MUTATING_KINDS:
            return _deny(
                DENY_AND_HALT, "S13.2/reviewer_readonly", "reviewer_write_attempt",
                f"a {action.kind!r} was proposed from the REVIEWER zone. The reviewer never "
                f"gets write permissions; a write reaching this point means confinement "
                f"failed, which is a synchronous stop, not a denial to log and continue")
        return _deny(
            DENY_AND_HALT, "S13.2/reviewer_readonly", "reviewer_execution_attempt",
            f"a {action.kind!r} was proposed from the REVIEWER zone. The reviewer inspects "
            f"the worker diff from a read-only view and must NOT execute worker-modified "
            f"code to review it")
    # 1. Permission/sandbox/hook-trust bypass, and effort flags.
    for flag in BYPASS_FLAG_MARKERS:
        if flag in lowered:
            return _deny(DENY_AND_HALT, "S4.4/bypass", "bypass_flag",
                         f"{flag} is a permission/sandbox/hook-trust bypass; denied "
                         f"unconditionally and treated as evidence of an unsafe attempt")
    for flag in EFFORT_FLAG_MARKERS:
        if re.search(rf"{re.escape(flag)}(\s|=|$)", lowered):
            return _deny(DENY_AND_CONTINUE, "S4.4/effort", "effort_flag",
                         f"{flag} is permanently prohibited in every configuration file, "
                         f"prompt, and CLI invocation")

    # 2. Credential access, exfiltration, or logging.
    for path in action.target_paths:
        if _looks_like_credential_path(path):
            return _deny(DENY_AND_HALT, "S4.4/credentials", "credential_access",
                         f"{path!r} is a credential or auth store; reading, printing, "
                         f"copying, uploading, or logging it is denied")
    for segment in shape.segments:
        if not segment:
            continue
        candidate = (_program_name(segment[0]), *[t.lower() for t in segment[1:]])
        for credential_shape in CREDENTIAL_COMMAND_SHAPES:
            if candidate[:len(credential_shape)] == credential_shape:
                return _deny(DENY_AND_HALT, "S4.4/credentials", "credential_command",
                             f"`{' '.join(credential_shape)}` dumps an environment or auth "
                             f"store; denied")
    if any(_looks_like_credential_path(token) for token in shape.tokens):
        return _deny(DENY_AND_HALT, "S4.4/credentials", "credential_access",
                     "the command references a credential or auth store path")

    # 3. Mutating the active controller, its policy, schemas, or prompts.
    if action.kind in ("file_write", "file_delete", "file_rename"):
        for path in action.target_paths:
            resolved = resolve_target(path, authority.repo_root)
            if resolved.inside_root and any(
                    path_matches(resolved.relative_posix, pattern)
                    for pattern in CONTROLLER_PATHS):
                if not any(path_matches(resolved.relative_posix, allowed)
                           for allowed in authority.allowed_paths):
                    return _deny(
                        DENY_AND_HALT, "S13.1/controller", "controller_mutation",
                        f"{resolved.relative_posix} belongs to the active controller; "
                        f"Claude, Codex, repository text, hooks, tests, and task code may "
                        f"never modify the controller, policy, schemas, or prompts")

    # 4. Disabling hooks, tests, CI, secret scanning, branch protection, or audit.
    for marker in CONTROL_DISABLING_MARKERS:
        if marker in lowered:
            return _deny(DENY_AND_HALT, "S4.4/disable_controls", "control_disabling",
                         f"{marker!r} disables a required control (hooks, tests, CI, "
                         f"secret scanning, branch protection, or audit logging)")

    # 5. Direct push to main and force push.
    if action.kind in ("push", "command", "git_command"):
        push_segments = [s for s in shape.segments
                         if s and _program_name(s[0]) == "git"
                         and "push" in [t.lower() for t in s[1:]]]
        if action.kind == "push" and not push_segments:
            push_segments = [tuple(action.argv) or ("git", "push")]
        for segment in push_segments:
            tokens = [t.lower() for t in segment]
            if any(t in ("--force", "-f", "--force-with-lease") or
                   t.startswith("--force-with-lease=") for t in tokens):
                return _deny(DENY_AND_CONTINUE, "S4.4/force_push", "force_push",
                             "a force push is denied regardless of any model's opinion")
            for name in config.main_branch_names:
                if action.branch.lower() == name or any(
                        t == name or t.endswith(f":{name}") or t.endswith(f"/{name}")
                        for t in tokens[2:]):
                    return _deny(DENY_AND_CONTINUE, "S4.4/main_push", "push_to_main",
                                 f"a direct push to {name!r} is denied; the supervisor "
                                 f"pushes only to the exact authorized task branch")

    # 6. Destructive git and deletion shapes.
    for segment in shape.segments:
        reason = _is_destructive_segment(segment)
        if reason.startswith("destructive_git"):
            return _deny(DENY_AND_CONTINUE, "S4.4/destructive_git", reason,
                         f"`{' '.join(segment)}` is a broad discard/reset/clean and is "
                         f"denied")
        if reason == "recursive_or_wildcard_delete":
            return _deny(DENY_AND_CONTINUE, "S4.4/recursive_delete", reason,
                         "recursive or wildcard deletion is denied")
        if reason == "delete_command":
            for token in segment[1:]:
                if token.startswith("-") or token.startswith("/"):
                    continue
                danger = _dangerous_delete_target(
                    token, root=authority.repo_root, worktree=authority.worktree)
                if danger:
                    return _deny(DENY_AND_CONTINUE, "S4.4/delete_target", danger,
                                 f"deletion target {token!r} is refused: {danger}")

    if action.kind == "file_delete":
        for path in action.target_paths:
            danger = _dangerous_delete_target(
                path, root=authority.repo_root, worktree=authority.worktree)
            if danger:
                return _deny(DENY_AND_CONTINUE, "S4.4/delete_target", danger,
                             f"deletion target {path!r} is refused: {danger}")

    # 7. Command substitution or dynamic evaluation concealing a destructive op.
    if shape.has_substitution:
        conceals = any(_is_destructive_segment(segment) for segment in shape.segments)
        marker_hit = any(m in shape.raw.lower() for m in
                         ("iex ", "invoke-expression", "eval ", "-encodedcommand", "-enc "))
        if conceals or marker_hit:
            return _deny(DENY_AND_CONTINUE, "S4.4/substitution", "concealed_execution",
                         "shell command substitution or dynamic evaluation is denied; the "
                         "true operation cannot be determined before it runs")

    # 8. Path escapes on any mutating action.
    if action.kind in ("file_write", "file_delete", "file_rename"):
        for path in action.target_paths:
            resolved = resolve_target(path, authority.worktree or authority.repo_root)
            if resolved.escape_reason in ("symlink_or_junction_escape", "device_path",
                                          "alternate_data_stream", "unresolved_variable",
                                          "nul_byte", "empty_path",
                                          "unresolvable_path"):
                return _deny(DENY_AND_CONTINUE, "S13.5/canonicalization",
                             resolved.escape_reason,
                             f"{path!r} is refused: {resolved.escape_reason}")

    # 9. Protected paths outside the packet.
    if action.kind in ("file_write", "file_delete", "file_rename"):
        for path in action.target_paths:
            resolved = resolve_target(path, authority.repo_root)
            if not resolved.inside_root:
                continue
            if any(path_matches(resolved.relative_posix, pattern)
                   for pattern in authority.forbidden_paths):
                allowed = any(path_matches(resolved.relative_posix, pattern)
                              for pattern in authority.allowed_paths)
                if not allowed:
                    return _deny(DENY_AND_CONTINUE, "S4.4/protected_path",
                                 "protected_path_mutation",
                                 f"{resolved.relative_posix} is a protected owner/control/"
                                 f"security path outside the current task packet")

    # 10. No mutation without an active authorized task and stage (inv. 1).
    if action.kind in ("file_write", "file_delete", "file_rename", "push",
                       "pr_mutation", "external_write") and not authority.active:
        return _deny(DENY_AND_CONTINUE, "S13.12/inv1", "no_active_task",
                     f"task {authority.task_id!r} is not active (status "
                     f"{authority.status!r}); no mutation is permitted")
    return None


# --------------------------------------------------------------------------
# AUTO rules (S4.1)
# --------------------------------------------------------------------------


def _grant_match(action: ProposedAction, authority: TaskAuthority,
                 mode: str, review_passed: bool) -> tuple[StandingGrant | None, str]:
    """Find the standing grant covering this exact operation shape, if any."""
    shape = action.command_shape()
    for grant in authority.active_grants():
        if grant.operation_type == "test_command" and action.kind == "command":
            if shape.has_substitution or shape.has_metacharacter:
                continue
            if any(_shape_matches(pattern, shape.tokens) for pattern in grant.argv_shapes):
                return grant, ""
        elif grant.operation_type == "branch_push" and action.kind == "push":
            if action.branch != grant.branch:
                continue
            if grant.requires_passing_review and not review_passed:
                return None, "grant_requires_passing_review"
            if grant.requires_mode and mode != grant.requires_mode:
                return None, f"grant_requires_mode:{grant.requires_mode}"
            return grant, ""
        elif grant.operation_type in ("file_write", "runtime_file_write") and \
                action.kind in ("file_write", "runtime_file_write"):
            if action.change_file_count > max(grant.max_file_count, 0):
                continue
            if grant.max_change_bytes and action.change_bytes > grant.max_change_bytes:
                continue
            ok = bool(action.target_paths)
            for path in action.target_paths:
                resolved = resolve_target(path, authority.repo_root)
                if not resolved.inside_root:
                    ok = False
                    break
                if not any(path_matches(resolved.relative_posix, p)
                           for p in grant.path_scope):
                    ok = False
                    break
                if file_class(resolved.relative_posix) not in grant.file_classes:
                    ok = False
                    break
            if ok:
                return grant, ""
    return None, ""


def _auto_read(action: ProposedAction, authority: TaskAuthority) -> PolicyDecision | None:
    """Repository and project-control status reads (S4.1)."""
    for path in action.target_paths:
        resolved = resolve_target(path, authority.repo_root)
        if not resolved.inside_root:
            return _ask("S4.3/out_of_tree_read", "read_outside_repository",
                        f"{path!r} resolves outside the repository", "scope")
    return _auto("S4.1/status_read", "repository_status_read",
                 "repository and project-control status read",
                 advisory_eligible=True)


def _auto_git(action: ProposedAction, authority: TaskAuthority) -> PolicyDecision | None:
    """Enumerated read-only git commands (S4.1)."""
    shape = action.command_shape()
    if not shape.segments or len(shape.segments) != 1 or shape.has_substitution:
        return None
    segment = shape.segments[0]
    if _program_name(segment[0]) != "git":
        return None
    rest = list(segment[1:])
    for option in rest:
        if option in UNSAFE_GIT_GLOBAL_OPTIONS:
            return _ask("S13.6/git_options", "unsafe_git_global_option",
                        f"git option {option!r} changes where or how git runs and is "
                        f"never AUTO (no aliases, pagers, external diff, or textconv)",
                        "security")
    subcommand = next((t for t in rest if not t.startswith("-")), "")
    if subcommand not in READ_ONLY_GIT_SUBCOMMANDS:
        return None
    for flag in rest:
        if flag in UNSAFE_GIT_SUBCOMMAND_FLAGS:
            return _ask("S13.6/git_flags", "unsafe_git_subcommand_flag",
                        f"{flag!r} can run external code or write a file during an "
                        f"otherwise read-only git command", "security")
    return _auto("S4.1/read_only_git", "read_only_git_command",
                 f"`git {subcommand}` is on the enumerated read-only list",
                 advisory_eligible=True)


def _auto_test_command(action: ProposedAction,
                       authority: TaskAuthority) -> PolicyDecision | None:
    """Test commands documented by the task packet (S4.1)."""
    shape = action.command_shape()
    if not shape.tokens or shape.has_substitution or shape.has_metacharacter:
        return None
    for documented in authority.documented_test_commands:
        if _shape_matches(documented, shape.tokens):
            return _auto("S4.1/documented_test", "documented_test_command",
                         f"matches the packet-documented test command {documented!r}",
                         advisory_eligible=True)
    return None


def _auto_file_write(action: ProposedAction, authority: TaskAuthority,
                     config: PolicyConfig) -> PolicyDecision:
    """File create/modify inside allowed_paths and the isolated worktree (S4.1).

    Deletes, renames, oversized changes, and security-relevant file classes are
    never baseline-AUTO.
    """
    if action.change_file_count > config.max_changed_files_per_checkpoint:
        return _ask("S4.1/change_size", "change_size_bound_exceeded",
                    f"{action.change_file_count} files exceeds the per-checkpoint bound "
                    f"of {config.max_changed_files_per_checkpoint}", "scope")
    if action.change_bytes > config.max_change_bytes_per_checkpoint:
        return _ask("S4.1/change_size", "change_size_bound_exceeded",
                    f"{action.change_bytes} bytes exceeds the per-checkpoint bound of "
                    f"{config.max_change_bytes_per_checkpoint}", "scope")

    worktree = authority.worktree or authority.repo_root
    if not action.target_paths:
        return _ask("S4.1/no_target", "no_target_path",
                    "a file write with no target path cannot be bounded", "unclassified")
    for path in action.target_paths:
        in_worktree = resolve_target(path, worktree)
        if not in_worktree.inside_root:
            return _ask("S4.1/worktree", "outside_task_worktree",
                        f"{path!r} does not resolve inside the isolated task worktree",
                        "scope")
        resolved = resolve_target(path, authority.repo_root)
        relative = resolved.relative_posix or in_worktree.relative_posix
        if not any(path_matches(relative, pattern) for pattern in authority.allowed_paths):
            return _ask("S4.1/allowed_paths", "outside_allowed_paths",
                        f"{relative} is outside the task packet's allowed_paths",
                        "scope")
        klass = file_class(relative)
        if klass in SECURITY_RELEVANT_CLASSES:
            return _ask("S4.1/file_class", f"security_relevant_class:{klass}",
                        f"{relative} is a {klass}; that class is never baseline-AUTO and "
                        f"needs a standing grant or a stricter tier", "security")
        if action.change_bytes > config.max_single_file_bytes:
            return _ask("S4.1/change_size", "single_file_bound_exceeded",
                        f"{relative} would change {action.change_bytes} bytes, over the "
                        f"single-file bound of {config.max_single_file_bytes}", "scope")
    return _auto("S4.1/in_scope_edit", "in_scope_file_write",
                 "create/modify inside allowed_paths and the isolated worktree, "
                 "ordinary file class, within the change-size bound",
                 advisory_eligible=True)


def _auto_runtime_file(action: ProposedAction,
                       authority: TaskAuthority) -> PolicyDecision:
    """Creating known supervisor runtime files in the approved runtime directory."""
    if not authority.runtime_dir:
        return _ask("S4.1/runtime_dir", "no_runtime_directory",
                    "no approved runtime directory is configured", "unclassified")
    for path in action.target_paths:
        resolved = resolve_target(path, authority.runtime_dir)
        if not resolved.inside_root:
            return _ask("S4.1/runtime_dir", "outside_runtime_directory",
                        f"{path!r} is not inside the approved runtime directory", "scope")
    return _auto("S4.1/runtime_file", "supervisor_runtime_file",
                 "known supervisor runtime file in the approved runtime directory")


# --------------------------------------------------------------------------
# The classifier
# --------------------------------------------------------------------------


def evaluate(
    action: ProposedAction,
    *,
    authority: TaskAuthority,
    mode: str = "shadow",
    config: PolicyConfig = DEFAULT_POLICY_CONFIG,
    review_passed: bool = False,
) -> PolicyDecision:
    """Classify one proposed action into exactly one tier.

    Deterministic and total: every input path ends in a decision, and the final
    fallthrough is ASK, never AUTO. `action.stated_reason` is deliberately not
    consulted anywhere in this function.
    """
    denial = _hard_deny(action, authority, config)
    if denial is not None:
        return denial

    # Owner gates can only ever queue (S4.3, S5.2, inv. 9).
    if action.owner_gate:
        if action.owner_gate not in OWNER_GATES:
            return _ask("S4.3/owner_gate", "unknown_owner_gate",
                        f"{action.owner_gate!r} is not a recognized owner gate; queuing",
                        "owner_gate")
        classification = {
            "g6_legal": "legal", "legal_publication": "legal",
            "credential": "credential", "payment": "payment",
            "dependency_addition": "dependency", "policy_exception": "security",
            "permission_config_change": "security",
        }.get(action.owner_gate, "owner_gate")
        return _ask("S4.3/owner_gate", f"owner_gate:{action.owner_gate}",
                    f"{action.owner_gate} is an owner-authority item: it queues for the "
                    f"owner and is simultaneously barred from every automatic path",
                    classification)

    grant, grant_block = _grant_match(action, authority, mode, review_passed)
    if grant is not None:
        return _auto("S4.1/standing_grant", "standing_grant",
                     f"covered by owner grant {grant.grant_id} "
                     f"({grant.operation_type}); post-verification required: "
                     f"{grant.post_verification}", grant=grant.grant_id)

    if action.kind == "read":
        return _auto_read(action, authority)

    if action.kind in ("command", "git_command"):
        for rule in (_auto_git, _auto_test_command):
            decision = rule(action, authority)
            if decision is not None:
                return decision
        return _ask("S4.3/unclassified_command", "undocumented_command",
                    "the command is not an enumerated read-only git command and is not a "
                    "packet-documented test command", "unclassified")

    if action.kind == "file_write":
        return _auto_file_write(action, authority, config)

    if action.kind == "runtime_file_write":
        return _auto_runtime_file(action, authority)

    if action.kind == "file_delete":
        return _ask("S4.3/deletion", "deletion_of_existing_file",
                    "deletion of a pre-existing file is an owner-authority item",
                    "destructive")

    if action.kind == "file_rename":
        return _ask("S4.3/rename", "rename_not_baseline_auto",
                    "renames are never baseline-AUTO and need a standing grant or an "
                    "owner answer", "scope")

    if action.kind == "push":
        if grant_block:
            return _ask("S4.1/push_grant", grant_block,
                        f"a push to {action.branch!r} is not covered right now: "
                        f"{grant_block}", "scope")
        return _ask("S4.1/push", "push_without_grant",
                    f"a push to {action.branch!r} needs an owner standing grant and "
                    f"limited-auto; at least one is missing", "scope")

    if action.kind == "pr_mutation":
        return _ask("S4.1/pr", "pr_mutation_without_grant",
                    "creating or updating the task PR is a controller action that needs a "
                    "standing grant and limited-auto", "scope")

    if action.kind == "external_write":
        return _ask("S13.7/unmodeled", "external_write",
                    f"external write {action.effect_type!r} is ASK-gated unless it is "
                    f"explicitly modeled in policy with an action id", "security")

    if action.kind == "subagent":
        return _ask("S8.4/background_agent", "background_agent_request",
                    "a background/subagent request cannot reach the broker independently "
                    "and is not auto-approved", "security")

    if action.kind == "network":
        return _ask("S13.3/network", "network_access",
                    "network is denied by default; an explicit allowance is an owner "
                    "decision", "security")

    if action.kind == "session_resume":
        return _auto("S4.1/session_resume", "resume_exact_session",
                     "resuming the exact recorded session")

    if action.kind == "handoff_generation":
        return _auto("S4.1/handoff", "generate_session_handoff",
                     "generating a session handoff")

    if action.kind == "forwarded_prompt":
        return _auto("S4.1/forward", "forwarded_prompt",
                     "forwarding a prompt that itself carries the task id, authorized "
                     "stage, permitted paths, requested action, stop conditions, and the "
                     "demand for a structured checkpoint")

    return _ask("S4.3/fallthrough", "unclassified_request",
                f"the policy cannot confidently classify a {action.kind!r} request "
                f"({action.tool_name!r}); unclassifiable means ASK, never AUTO",
                "unclassified")


def apply_model_recommendation(
    decision: PolicyDecision,
    recommended_tier: str,
    *,
    source: str,
) -> PolicyDecision:
    """Combine a model's recommendation with the deterministic decision.

    A recommendation may only STRICTEN. A looser recommendation is recorded as
    ignored and changes nothing (S4, S13.12 invariant 4).
    """
    if recommended_tier not in TIER_ORDER:
        raise PolicyError("unknown_tier", f"{recommended_tier!r} is not a tier")
    if TIER_ORDER[recommended_tier] > TIER_ORDER[decision.tier]:
        outcome = decision.outcome
        if recommended_tier == HARD_DENY and not outcome:
            outcome = DENY_AND_CONTINUE
        return dataclasses.replace(
            decision,
            tier=recommended_tier,
            outcome=outcome,
            synchronous_stop=decision.synchronous_stop or outcome == DENY_AND_HALT,
            notes=decision.notes + (f"strictened_by:{source}:{recommended_tier}",))
    if recommended_tier != decision.tier:
        return dataclasses.replace(
            decision,
            notes=decision.notes + (
                f"recommendation_ignored:{source}:{recommended_tier}:"
                f"a model recommendation may only stricten",))
    return decision


# --------------------------------------------------------------------------
# NOTIFY (S4.2) - proceed, tell the owner asynchronously, exactly once
# --------------------------------------------------------------------------

NOTIFY_EVENTS: frozenset[str] = frozenset({
    "task_pr_created", "task_pr_updated", "first_push_new_task_branch",
    "usage_limit_wait_entered", "scheduled_resume_succeeded",
    "session_rotation_completed", "safe_checkpoint_auto_recovery",
    "model_fallback_engaged", "schema_retry_succeeded",
    "circuit_breaker_warning",
})


def classify_event(event_type: str) -> PolicyDecision:
    """Classify a supervisor EVENT (not an action) into NOTIFY, stop, or ASK."""
    if event_type in NOTIFY_EVENTS:
        return PolicyDecision(tier=NOTIFY, reason_code=f"notify:{event_type}",
                              reason="low-risk, reversible, in-scope: proceed and notify "
                                     "asynchronously; the loop never blocks",
                              rule_id="S4.2")
    if event_type in SYNCHRONOUS_STOP_CONDITIONS:
        return PolicyDecision(
            tier=ASK, reason_code=f"synchronous_stop:{event_type}",
            reason="a Section 4.5 condition: pause and wait for the owner",
            rule_id="S4.5", classification="security", synchronous_stop=True)
    return _ask("S4.3/unknown_event", f"unclassified_event:{event_type}",
                f"{event_type!r} is not an enumerated NOTIFY event", "unclassified")


def requires_synchronous_stop(condition: str) -> bool:
    """True only for the short S4.5 list. Nothing else pauses the world."""
    return condition in SYNCHRONOUS_STOP_CONDITIONS


class NotifyOnceLedger:
    """Durable "notify exactly once" ledger (S4.2, S15 tier-policy family).

    Keys live in the journal's state table, so a restart cannot re-notify an
    event that already went out.
    """

    PREFIX = "notify_once/"

    def __init__(self, journal: Any) -> None:
        self._journal = journal

    @staticmethod
    def key_for(event_type: str, subject: str) -> str:
        return digest_of({"event_type": event_type, "subject": subject})

    def should_notify(self, event_type: str, subject: str = "") -> bool:
        """True the first time only; records the event durably."""
        if event_type not in NOTIFY_EVENTS:
            raise PolicyError("not_a_notify_event",
                              f"{event_type!r} is not an S4.2 NOTIFY event")
        key = self.PREFIX + self.key_for(event_type, subject)
        if self._journal.get_state(key) is not None:
            return False
        self._journal.set_state(key, {"event_type": event_type, "subject": subject,
                                      "notified_at_utc": to_utc_iso()})
        return True

    def notified(self, event_type: str, subject: str = "") -> bool:
        return self._journal.get_state(
            self.PREFIX + self.key_for(event_type, subject)) is not None


# --------------------------------------------------------------------------
# ASK batching (S4.3 rule 4: batch, don't drip)
# --------------------------------------------------------------------------


def batch_ask_questions(asks: Sequence[Any]) -> str:
    """Combine every open question into ONE owner message (S4.3 rule 4)."""
    items = list(asks)
    if not items:
        return ""
    lines = [f"{len(items)} question(s) are waiting for you:"]
    for index, ask in enumerate(items, start=1):
        if isinstance(ask, Mapping):
            question = ask.get("question", "")
            ask_id = ask.get("ask_id", "")
            classification = ask.get("classification", "")
        else:
            question = getattr(ask, "question", str(ask))
            ask_id = getattr(ask, "ask_id", "")
            classification = getattr(ask, "classification", "")
        lines.append(f"  {index}. [{ask_id}] ({classification}) {question}")
    lines.append("Answer locally with `approve-once`/`deny`, or through the authenticated "
                 "remote surface. Nothing that depends on these answers is proceeding.")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# The five-clause dependency-independence check (S4.3(a), Phase 0 return)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class WorkUnit:
    """A candidate unit of in-scope work that might continue past a queued ASK."""

    unit_id: str
    task_id: str
    target_paths: tuple[str, ...] = ()
    interfaces: tuple[str, ...] = ()
    assumption_attestation: str = ""
    assumes_answer_to: tuple[str, ...] = ()

    def digest(self) -> str:
        return digest_of(dataclasses.asdict(self))


@dataclasses.dataclass(frozen=True)
class AskItem:
    """A queued owner question plus the closure of what any answer could touch."""

    ask_id: str
    question: str
    classification: str
    affected_path_closure: tuple[str, ...] = ()
    named_interfaces: tuple[str, ...] = ()

    def digest(self) -> str:
        return digest_of(dataclasses.asdict(self))


@dataclasses.dataclass(frozen=True)
class ClauseResult:
    clause: str
    passed: bool
    detail: str


@dataclasses.dataclass(frozen=True)
class IndependenceResult:
    """The recorded check. `independent` is True only when ALL five clauses pass."""

    independent: bool
    unit_id: str
    ask_id: str
    clauses: tuple[ClauseResult, ...]
    record_digest: str = ""

    def failed_clauses(self) -> tuple[str, ...]:
        return tuple(c.clause for c in self.clauses if not c.passed)


def check_independence(
    unit: WorkUnit,
    ask: AskItem,
    *,
    journal: Any = None,
    edges_checked: Sequence[str] = (),
) -> IndependenceResult:
    """The five recorded clauses. Failing ANY clause means the unit is dependent.

    1. Path disjointness      unit paths INTERSECT ask closure == empty
    2. Interface disjointness no interface the unit touches is named by the ask
    3. Class gate             the ask is not architecture/dependency/scope/security
    4. Assumption check       no unit step depends on a particular answer, and the
                              attestation naming that is present
    5. Durability             the inputs and conclusion are journaled digest-bound
                              BEFORE the unit continues

    A missing journal fails clause 5: the check is not merely computed, it is
    recorded, because S4.3(a) requires "a recorded dependency check".
    """
    clauses: list[ClauseResult] = []

    unit_paths = {p.replace("\\", "/").strip("/") for p in unit.target_paths}
    closure = {p.replace("\\", "/").strip("/") for p in ask.affected_path_closure}
    overlap = sorted(
        p for p in unit_paths
        if p in closure or any(path_matches(p, pattern) for pattern in closure)
        or any(path_matches(c, p) for c in closure))
    clauses.append(ClauseResult(
        "path_disjointness", not overlap,
        "no shared paths" if not overlap else f"shared paths: {overlap}"))

    interface_overlap = sorted(set(unit.interfaces) & set(ask.named_interfaces))
    clauses.append(ClauseResult(
        "interface_disjointness", not interface_overlap,
        f"edges checked in source: {list(edges_checked)}" if not interface_overlap
        else f"shared interfaces: {interface_overlap}"))

    class_ok = ask.classification not in BLOCKING_ASK_CLASSES
    clauses.append(ClauseResult(
        "class_gate", class_ok,
        f"ask class {ask.classification!r}"
        + ("" if class_ok else " blocks dependent continuation categorically")))

    assumption_ok = (ask.ask_id not in unit.assumes_answer_to
                     and bool(unit.assumption_attestation.strip()))
    clauses.append(ClauseResult(
        "assumption_check", assumption_ok,
        unit.assumption_attestation.strip()
        or "no attestation recorded; an unattested unit is treated as dependent"))

    record = {
        "unit_id": unit.unit_id, "unit_digest": unit.digest(),
        "ask_id": ask.ask_id, "ask_digest": ask.digest(),
        "unit_paths": sorted(unit_paths), "ask_closure": sorted(closure),
        "edges_checked": list(edges_checked), "ask_class": ask.classification,
        "clauses": [dataclasses.asdict(c) for c in clauses],
        "recorded_at_utc": to_utc_iso(),
    }
    record_digest = ""
    if journal is None:
        clauses.append(ClauseResult(
            "durability", False,
            "no journal supplied; the check must be recorded before the unit continues"))
    else:
        record["conclusion_independent"] = all(c.passed for c in clauses)
        record_digest = digest_of(record)
        try:
            journal.set_state(f"independence/{unit.unit_id}/{ask.ask_id}",
                              {**record, "record_digest": record_digest})
        except Exception as exc:  # pragma: no cover - defensive
            record_digest = ""
            clauses.append(ClauseResult("durability", False,
                                        f"journal write failed: {exc}"))
        else:
            clauses.append(ClauseResult(
                "durability", True,
                f"journaled digest-bound as {record_digest[:16]}..."))

    independent = all(c.passed for c in clauses)
    return IndependenceResult(independent, unit.unit_id, ask.ask_id,
                              tuple(clauses), record_digest)


# --------------------------------------------------------------------------
# Model selection (S3) - deterministic, shared by both adapters
# --------------------------------------------------------------------------

#: S3.3 - purposes for which the cheaper advisory model is NEVER acceptable.
ADVISORY_FORBIDDEN_PURPOSES: frozenset[str] = frozenset({
    "security_sensitive_approval",
    "external_write_approval",
    "ambiguous_effect_recovery",
    "scope_or_authority_interpretation",
    "handoff_verification",
    "checkpoint_review",
})

ADVISORY_ALLOWED_PURPOSES: frozenset[str] = frozenset({
    "routine_tool_approval", "triage", "summarization",
})


@dataclasses.dataclass(frozen=True)
class ModelResolution:
    """Which model will run, why, and what tier the choice itself carries."""

    provider: str
    model: str
    tier: str
    reason_code: str
    reason: str
    attempted: tuple[str, ...] = ()
    fallback_engaged: bool = False
    selection_digest: str = ""

    @property
    def usable(self) -> bool:
        return bool(self.model) and self.tier in (AUTO, NOTIFY)


def assert_advisory_allowed(purpose: str) -> None:
    """Refuse `advisory_model` for anything S3.3 reserves to `review_model`."""
    if purpose in ADVISORY_FORBIDDEN_PURPOSES:
        raise PolicyError(
            "advisory_model_forbidden",
            f"the cheaper advisory model may never be used for {purpose!r}; S3.3 reserves "
            f"that to review_model (or its engaged approved fallback) or to deterministic "
            f"verification")
    if purpose not in ADVISORY_ALLOWED_PURPOSES:
        raise PolicyError("unknown_advisory_purpose",
                          f"{purpose!r} is not an enumerated advisory purpose; refusing")


def resolve_model(
    provider: str,
    *,
    config: Any,
    selection: Any,
    availability: Callable[[str], bool] | None = None,
    role: str = "primary",
    purpose: str = "checkpoint_review",
) -> ModelResolution:
    """Resolve the model to use for one provider and role (S3.2 rules 3 and 4).

    * A model outside its OWN provider's `allowed_models` is refused in every
      role, even if the provider defaults to or suggests it.
    * The chain is the primary, then that provider's own `fallback_models`, in
      order - never the other provider's list.
    * Engaging a fallback is a NOTIFY event.
    * An exhausted chain queues an ASK and holds - never a silent substitution.
    """
    if provider not in ("codex", "claude"):
        raise PolicyError("unknown_provider", f"{provider!r} is not a provider")
    allowed = tuple(config.allowlist(provider))
    chosen = selection.selection(provider)
    digest = selection.digest()
    probe = availability or (lambda _model: True)

    if role == "advisory":
        assert_advisory_allowed(purpose)
        candidate = chosen.advisory_model or chosen.primary
        if not candidate:
            return ModelResolution(provider, "", ASK, "no_advisory_model",
                                   "no advisory model is configured and no primary exists",
                                   selection_digest=digest)
        if candidate not in allowed:
            return ModelResolution(
                provider, "", ASK, "model_not_allowlisted",
                f"{candidate!r} is not in {provider}.allowed_models and must never be used "
                f"in any role", (candidate,), selection_digest=digest)
        if not probe(candidate):
            return ModelResolution(
                provider, "", ASK, "advisory_model_unavailable",
                f"advisory model {candidate!r} is unavailable; advisory calls do not fall "
                f"back silently", (candidate,), selection_digest=digest)
        return ModelResolution(provider, candidate, AUTO, "advisory_model_selected",
                               f"advisory model {candidate!r} for purpose {purpose!r}",
                               (candidate,), selection_digest=digest)

    if role != "primary":
        raise PolicyError("unknown_role", f"{role!r} is not a model role")

    chain = list(chosen.chain())
    if not chain:
        if not allowed:
            return ModelResolution(
                provider, "", AUTO, "account_default",
                f"{provider}.allowed_models is empty: only the account/CLI default may be "
                f"used and no explicit selection is permitted", selection_digest=digest)
        return ModelResolution(
            provider, "", ASK, "no_selection",
            f"no {provider} model is selected but the allowlist is non-empty; queue an ASK "
            f"rather than choosing for the owner", selection_digest=digest)

    attempted: list[str] = []
    for index, candidate in enumerate(chain):
        attempted.append(candidate)
        if candidate not in allowed:
            return ModelResolution(
                provider, "", ASK, "model_not_allowlisted",
                f"{candidate!r} is not in {provider}.allowed_models and must never be used "
                f"in any role, even as a fallback", tuple(attempted),
                selection_digest=digest)
        if probe(candidate):
            if index == 0:
                return ModelResolution(provider, candidate, AUTO, "primary_model",
                                       f"configured {provider} model {candidate!r}",
                                       tuple(attempted), selection_digest=digest)
            return ModelResolution(
                provider, candidate, NOTIFY, "fallback_engaged",
                f"the {provider} primary was unavailable; engaged approved fallback "
                f"{candidate!r} (position {index} in the chain). Engaging a fallback is a "
                f"NOTIFY event", tuple(attempted), True, digest)
    return ModelResolution(
        provider, "", ASK, "chain_exhausted",
        f"every {provider} model in the owner-approved chain is unavailable "
        f"({attempted}); queue an ASK and hold - never silently substitute",
        tuple(attempted), selection_digest=digest)
