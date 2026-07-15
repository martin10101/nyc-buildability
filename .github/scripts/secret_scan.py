#!/usr/bin/env python3
"""Repository-local secret scanner (task M0-T005).

Scans git-tracked files plus untracked-but-not-ignored files for likely
credentials and exits nonzero when any finding remains after allowlisting.

Design constraints (docs/SECRETS_POLICY.md, PRD sections 17/25):
- Python standard library only; no network access; deterministic.
- Matched values are MASKED in output (first/last 4 characters only) so the
  scanner itself never re-leaks a credential into CI logs.
- Two allowlist mechanisms, both visible in output:
    1. Path allowlist (basename match) for known high-entropy lookalikes
       such as npm sha512 integrity hashes in package-lock.json.
    2. Inline pragma: a line containing `secretscan:allow <justification>`
       suppresses findings on that line. Reviewers must check the
       justification; unexplained pragmas should fail review.
- This scanner COMPLEMENTS GitHub push protection; it does not replace it.

Exit codes: 0 = clean, 1 = findings, 2 = execution error.
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

# Basename -> justification. Applied to every path whose final component matches.
PATH_ALLOWLIST: dict[str, str] = {
    "package-lock.json": "npm sha512 integrity hashes are high-entropy base64 lookalikes",
    ".env.example": "names-only template; contains no values by policy (docs/SECRETS_POLICY.md)",
}

# Placeholder markers that disqualify a generic-assignment value as a real credential.
PLACEHOLDER_HINTS = (
    "example", "placeholder", "your", "changeme", "change-me", "dummy",
    "sample", "redacted", "fixme", "todo", "<", "{", "$",
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
# Requires quotes, length >= 20, Shannon entropy >= 3.5 bits/char, and no placeholder marker,
# to keep noise near zero (docs/SECRETS_POLICY.md, false-positive strategy).
GENERIC_CLASS = "generic-credential-assignment"
GENERIC_RE = re.compile(
    r"(?i)\b(?:api[_-]?key|apikey|secret|password|passwd|token)\b\s*[:=]\s*['\"](?P<v>[A-Za-z0-9+/=_.-]{20,})['\"]"
)
GENERIC_MIN_ENTROPY = 3.5


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


def list_files(repo_root: str) -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=repo_root, capture_output=True, check=True,
    ).stdout
    return [p.decode("utf-8", "replace") for p in out.split(b"\0") if p]


def main() -> int:
    start = time.monotonic()
    try:
        repo_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, check=True,
        ).stdout.decode().strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"secret-scan: ERROR: not a git repository or git unavailable: {exc}", file=sys.stderr)
        return 2

    findings: list[tuple[str, int, str, str]] = []  # (path, line_no, class, masked)
    pragma_allows: list[tuple[str, int, str]] = []  # (path, line_no, line-tail justification)
    path_allows: list[tuple[str, str]] = []         # (path, justification)
    scanned = 0

    for rel_path in list_files(repo_root):
        basename = rel_path.rsplit("/", 1)[-1]
        if basename in PATH_ALLOWLIST:
            path_allows.append((rel_path, PATH_ALLOWLIST[basename]))
            continue
        full = f"{repo_root}/{rel_path}"
        try:
            with open(full, "rb") as fh:
                raw = fh.read(MAX_FILE_BYTES + 1)
        except OSError:
            continue  # deleted-but-listed or unreadable; nothing to scan
        if len(raw) > MAX_FILE_BYTES or b"\0" in raw[:8192]:
            continue  # oversized or binary
        scanned += 1
        text = raw.decode("utf-8", "replace")
        for line_no, line in enumerate(text.splitlines(), start=1):
            hits: list[tuple[str, str]] = []
            for cls, pattern in PATTERNS:
                for m in pattern.finditer(line):
                    value = m.groupdict().get("v") or m.group(0)
                    hits.append((cls, mask(value)))
            for m in GENERIC_RE.finditer(line):
                value = m.group("v")
                lowered = value.lower()
                if any(h in lowered for h in PLACEHOLDER_HINTS):
                    continue
                if shannon_entropy(value) < GENERIC_MIN_ENTROPY:
                    continue
                hits.append((GENERIC_CLASS, mask(value)))
            if not hits:
                continue
            if PRAGMA in line:
                idx = line.find(PRAGMA)
                justification = line[idx + len(PRAGMA):].strip() or "(NO JUSTIFICATION GIVEN)"
                pragma_allows.append((rel_path, line_no, justification))
                continue
            for cls, masked in hits:
                findings.append((rel_path, line_no, cls, masked))

    elapsed = time.monotonic() - start
    print(f"secret-scan: scanned {scanned} files in {elapsed:.2f}s")
    if path_allows:
        print(f"secret-scan: path allowlist skipped {len(path_allows)} file(s):")
        for path, why in path_allows:
            print(f"  ALLOWLISTED PATH {path} -- {why}")
    if pragma_allows:
        print(f"secret-scan: inline pragma allowed {len(pragma_allows)} line(s):")
        for path, line_no, why in pragma_allows:
            print(f"  ALLOWLISTED LINE {path}:{line_no} -- justification: {why}")

    if findings:
        print(f"secret-scan: FAIL -- {len(findings)} potential credential(s) found:")
        for path, line_no, cls, masked in findings:
            print(f"  {path}:{line_no} [{cls}] {masked}")
        print("secret-scan: remove the credential, rotate it if it was real "
              "(docs/SECRETS_POLICY.md incident procedure), or allowlist a "
              "verified false positive with a justification.")
        return 1

    print("secret-scan: PASS -- no findings")
    return 0


if __name__ == "__main__":
    sys.exit(main())
