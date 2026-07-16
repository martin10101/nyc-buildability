#!/usr/bin/env python3
"""Repository-local secret scanner (task M0-T005, hardened in M0-T005-R1).

Scans git-tracked files plus untracked-but-not-ignored files for likely
credentials and exits nonzero when any finding remains after allowlisting.

Design constraints (docs/SECRETS_POLICY.md, PRD sections 17/25):
- Python standard library only; no network access; deterministic.
- Matched values are MASKED in output (first/last 4 characters only) so the
  scanner itself never re-leaks a credential into CI logs.
- All dynamic output (paths, justifications, masked values) is stripped of
  control characters before printing so a hostile filename or value cannot
  forge GitHub workflow commands (::notice / ::add-mask / ...) in the CI log.
- Two allowlist mechanisms, both visible in output:
    1. Exact-relative-path allowlist for known high-entropy lookalikes
       (npm sha512 integrity hashes in apps/web/package-lock.json).
       Policy-approved .env.example templates are NOT skipped: they are
       scanned with every pattern class PLUS a stricter names-only content
       check (any non-empty assignment value fails). Any .env.example at a
       non-approved path is scanned exactly like a normal file.
    2. Inline pragma: a line containing `secretscan:allow <justification>`
       suppresses findings on that line and prints a visible ALLOWLISTED
       LINE notice. A pragma with an EMPTY justification does NOT suppress:
       the finding is reported and the scan fails (docs/SECRETS_POLICY.md
       section 5).
- UTF-16 files (the default output encoding of Windows PowerShell 5.1 `>`
  redirection) are detected via BOM and decoded, not skipped as binary.
- Oversized (> MAX_FILE_BYTES) and binary skips print a visible notice.
- This scanner COMPLEMENTS GitHub push protection; it does not replace it.

Exit codes: 0 = clean, 1 = findings, 2 = execution error (git unavailable,
not a repository, or `git ls-files` failure).
"""

from __future__ import annotations

import math
import re
import subprocess
import sys
import time
from collections import Counter

MAX_FILE_BYTES = 2_000_000  # skip larger files (repo stores no large text; low-storage policy)
PRAGMA = "secretscan:allow"

# Exact repo-relative path -> justification. The file is skipped entirely.
# (M0-T005-R1: basename matching removed -- a decoy file with an allowlisted
# basename elsewhere in the tree is now scanned like any other file.)
PATH_ALLOWLIST: dict[str, str] = {
    "apps/web/package-lock.json": "npm sha512 integrity hashes are high-entropy base64 lookalikes",
}

# Exact repo-relative paths of the two policy-approved .env.example templates
# (docs/SECRETS_POLICY.md section 2). These are NOT skipped: every pattern
# class runs on them AND any non-empty assignment value is itself a finding
# (templates are names-and-comments only by policy section 3.1).
ENV_TEMPLATE_PATHS: dict[str, str] = {
    "services/api/.env.example": "policy-approved template (exact path); content-scanned: any non-empty value fails",
    "apps/web/.env.example": "policy-approved template (exact path); content-scanned: any non-empty value fails",
}
ENV_TEMPLATE_CLASS = "env-template-nonempty-value"
ENV_ASSIGN_RE = re.compile(r"^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*(?P<v>\S.*)$")

# Placeholder markers that disqualify a candidate value as a real credential.
# "..." = truncated documentation example (real base64/hex/URI values never
# contain a literal ellipsis); "user:pass" = the canonical URI doc example.
PLACEHOLDER_HINTS = (
    "example", "placeholder", "your", "changeme", "change-me", "dummy",
    "sample", "redacted", "fixme", "todo", "<", "{", "$", "...", "user:pass",
)

# (class name, compiled pattern). Value to mask = whole match unless a group named 'v' exists.
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # Render API keys / tokens (observed prefix; G5 report pattern class).
    ("render-api-key", re.compile(r"\brnd_[A-Za-z0-9]{16,}")),
    # Supabase personal access tokens.
    ("supabase-access-token", re.compile(r"\bsbp_[A-Fa-f0-9]{40}\b")),
    # JSON Web Tokens: base64url JSON header starting {"alg"... plus two dot-separated segments.
    # Supabase anon AND service-role keys are JWTs; neither belongs in git (env-scoped config).
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    # service_role assignment carrying an actual value (bare names in schemas/YAML keys do not match).
    ("service-role-assignment", re.compile(r"(?i)service_role[A-Za-z0-9_]*\s*[:=]\s*['\"]?(?P<v>[A-Za-z0-9._+/=-]{20,})")),
    # PEM private key blocks (RSA/EC/OPENSSH/PKCS8/none).
    ("pem-private-key", re.compile(r"-----BEGIN[A-Z ]*PRIVATE KEY-----")),
    # AWS access key IDs.
    ("aws-access-key-id", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    # GitHub tokens: classic (ghp_), OAuth (gho_), app (ghs_/ghu_/ghr_), fine-grained (github_pat_).
    ("github-token", re.compile(r"\b(?:ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    # Slack tokens (bot/app/user/legacy).
    ("slack-token", re.compile(r"\bxox[abeprs]-[A-Za-z0-9-]{10,}\b")),
]

# Generic credential assignment: keyword = 'quoted-high-entropy-value'.
# M0-T005-R1 (G3 defect D1): an optional identifier prefix is allowed before
# the keyword so compound names (AUTH_TOKEN=, DB_PASSWORD=, allowed_token=)
# match; `\b` alone can never fire between `_` and the keyword.
# Requires quotes, length >= 20, Shannon entropy >= 3.5 bits/char, and no
# placeholder marker, to keep noise near zero.
GENERIC_CLASS = "generic-credential-assignment"
GENERIC_RE = re.compile(
    r"(?i)\b[A-Za-z0-9_-]*(?:api[_-]?key|apikey|secret|password|passwd|token)\b"
    r"\s*[:=]\s*['\"](?P<v>[A-Za-z0-9+/=_.-]{20,})['\"]"
)
GENERIC_MIN_ENTROPY = 3.5

# Inventory-name class (M0-T005-R1, G3 defect D2 / G5 required rework item 2):
# the exact secret names enumerated in docs/SECRETS_POLICY.md section 2
# carrying ANY non-placeholder value are always a violation -- deterministic,
# no entropy gate. Assignment forms matched: NAME=value (env style, value
# immediately after '='), NAME: value (YAML style), optionally quoted.
# Names-only mentions (docs, tables, templates with empty values) do not match.
INVENTORY_CLASS = "inventory-secret-name-assignment"
INVENTORY_NAMES = (
    r"SUPABASE_SERVICE_ROLE_KEY|SUPABASE_DB_URL|SUPABASE_DB_PASSWORD|"
    r"SUPABASE_ACCESS_TOKEN|GEOCLIENT_SUBSCRIPTION_KEY|ANTHROPIC_API_KEY|"
    r"VERCEL_TOKEN|RENDER_DEPLOY_HOOK_URL_[A-Z0-9_]*|SENTRY_DSN|"
    r"NEXT_PUBLIC_SUPABASE_ANON_KEY"
)
INVENTORY_RE = re.compile(
    r"\b(?:" + INVENTORY_NAMES + r")\b(?:\s*:\s*|=)['\"]?(?P<v>[^'\"`\s#]{8,})"
)

# Postgres URI with embedded password (M0-T005-R1, G3 defect D2 / G5 item 3).
# The masked value is the password portion only.
POSTGRES_CLASS = "postgres-uri-with-password"
POSTGRES_RE = re.compile(r"\bpostgres(?:ql)?://[^:/\s@]+:(?P<v>[^@\s]+)@")


# ---------------------------------------------------------------------------
# Shared output-sanitization helper. Kept textually identical in
# .github/scripts/secret_scan.py and .github/scripts/validate_contracts.py:
# both are standalone stdlib scripts and the task scope forbids adding a
# shared module (M0-T005 G5 finding F1 + M0-T009 G5 finding F2).
# ---------------------------------------------------------------------------
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")


def sanitize_for_log(text: str) -> str:
    """Replace control characters (newline, CR, ESC, NUL, ...) with '?' so a
    hostile filename or value can never start a new log line and forge a
    GitHub workflow command (::notice / ::add-mask / ::error ...)."""
    return _CONTROL_CHARS_RE.sub("?", str(text))


def emit(message: str, *, err: bool = False) -> None:
    """Print one sanitized line to stdout (or stderr)."""
    print(sanitize_for_log(message), file=sys.stderr if err else sys.stdout)


# ---------------------------------------------------------------------------


def shannon_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    total = len(value)
    return -sum((c / total) * math.log2(c / total) for c in counts.values())


def mask(value: str) -> str:
    """Show first/last 4 chars only; never echo a full candidate credential."""
    if len(value) <= 12:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


def is_placeholder(text: str) -> bool:
    lowered = text.lower()
    return any(h in lowered for h in PLACEHOLDER_HINTS)


def list_files(repo_root: str) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root, capture_output=True, check=True,
    ).stdout
    return [p.decode("utf-8", "replace") for p in out.split(b"\0") if p]


def scan_line(line: str, env_template: bool) -> list[tuple[str, str]]:
    """Return (class, masked_value) hits for one line of text."""
    hits: list[tuple[str, str]] = []
    for cls, pattern in PATTERNS:
        for m in pattern.finditer(line):
            value = m.groupdict().get("v") or m.group(0)
            hits.append((cls, mask(value)))
    for m in INVENTORY_RE.finditer(line):
        value = m.group("v")
        if is_placeholder(value):
            continue
        hits.append((INVENTORY_CLASS, mask(value)))
    for m in POSTGRES_RE.finditer(line):
        # Placeholder gate runs on the full match so doc examples such as
        # a literal user/pass pair or a truncated URI are not findings.
        if is_placeholder(m.group(0)):
            continue
        hits.append((POSTGRES_CLASS, mask(m.group("v"))))
    for m in GENERIC_RE.finditer(line):
        value = m.group("v")
        if is_placeholder(value):
            continue
        if shannon_entropy(value) < GENERIC_MIN_ENTROPY:
            continue
        hits.append((GENERIC_CLASS, mask(value)))
    if env_template:
        m = ENV_ASSIGN_RE.match(line)
        if m:
            value = m.group("v").strip()
            if value:
                hits.append((ENV_TEMPLATE_CLASS, mask(value)))
    return hits


def main() -> int:
    start = time.monotonic()
    try:
        repo_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, check=True,
        ).stdout.decode().strip()
    except (subprocess.CalledProcessError, OSError) as exc:
        emit(f"secret-scan: ERROR: not a git repository or git unavailable: {exc}", err=True)
        return 2

    try:
        all_files = list_files(repo_root)
    except (subprocess.CalledProcessError, OSError) as exc:
        emit(f"secret-scan: ERROR: git ls-files failed: {exc}", err=True)
        return 2

    findings: list[tuple[str, int, str, str]] = []   # (path, line_no, class, masked)
    pragma_allows: list[tuple[str, int, str]] = []   # (path, line_no, justification)
    empty_pragmas: list[tuple[str, int]] = []        # (path, line_no) -- NOT suppressed
    path_allows: list[tuple[str, str]] = []          # (path, justification/notice)
    skipped: list[tuple[str, str]] = []              # (path, reason) -- visible skip notices
    scanned = 0

    for rel_path in all_files:
        if rel_path in PATH_ALLOWLIST:
            path_allows.append((rel_path, PATH_ALLOWLIST[rel_path]))
            continue
        env_template = rel_path in ENV_TEMPLATE_PATHS
        if env_template:
            path_allows.append((rel_path, ENV_TEMPLATE_PATHS[rel_path]))
        full = f"{repo_root}/{rel_path}"
        try:
            with open(full, "rb") as fh:
                raw = fh.read(MAX_FILE_BYTES + 1)
        except OSError:
            continue  # deleted-but-listed or unreadable; nothing to scan
        if len(raw) > MAX_FILE_BYTES:
            skipped.append((rel_path, f"oversized (> {MAX_FILE_BYTES} bytes)"))
            continue
        if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
            # UTF-16 BOM (LE = Windows PowerShell 5.1 `>` redirection default).
            # Must be checked BEFORE the null-byte binary heuristic, which
            # UTF-16's interleaved NUL bytes would otherwise trip (G3 D6).
            text = raw.decode("utf-16", "replace")
        elif b"\0" in raw[:8192]:
            skipped.append((rel_path, "binary (NUL byte in first 8KB)"))
            continue
        else:
            text = raw.decode("utf-8", "replace")
        scanned += 1
        for line_no, line in enumerate(text.splitlines(), start=1):
            hits = scan_line(line, env_template)
            if not hits:
                continue
            if PRAGMA in line:
                idx = line.find(PRAGMA)
                justification = line[idx + len(PRAGMA):].strip()
                if justification:
                    pragma_allows.append((rel_path, line_no, justification))
                    continue
                # Empty justification: the pragma does NOT suppress (G3 D4);
                # fall through so the hits are reported as findings.
                empty_pragmas.append((rel_path, line_no))
            for cls, masked in hits:
                findings.append((rel_path, line_no, cls, masked))

    elapsed = time.monotonic() - start
    emit(f"secret-scan: scanned {scanned} files in {elapsed:.2f}s")
    if path_allows:
        emit(f"secret-scan: exact-path allowlist/template rules applied to {len(path_allows)} file(s):")
        for path, why in path_allows:
            emit(f"  ALLOWLISTED PATH {path} -- {why}")
    if pragma_allows:
        emit(f"secret-scan: inline pragma allowed {len(pragma_allows)} line(s):")
        for path, line_no, why in pragma_allows:
            emit(f"  ALLOWLISTED LINE {path}:{line_no} -- justification: {why}")
    if empty_pragmas:
        emit(f"secret-scan: {len(empty_pragmas)} pragma(s) with EMPTY justification -- NOT suppressed:")
        for path, line_no in empty_pragmas:
            emit(f"  EMPTY PRAGMA {path}:{line_no} -- add a written justification or remove the line")
    if skipped:
        emit(f"secret-scan: skipped {len(skipped)} file(s) without content scan:")
        for path, why in skipped:
            emit(f"  SKIPPED {path} -- {why}")

    if findings:
        emit(f"secret-scan: FAIL -- {len(findings)} potential credential(s) found:")
        for path, line_no, cls, masked in findings:
            emit(f"  {path}:{line_no} [{cls}] {masked}")
        emit("secret-scan: remove the credential, rotate it if it was real "
             "(docs/SECRETS_POLICY.md incident procedure), or allowlist a "
             "verified false positive with a justification.")
        return 1

    emit("secret-scan: PASS -- no findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
