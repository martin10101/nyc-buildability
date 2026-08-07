#!/usr/bin/env python3
"""Never-send / secret redaction (D-007 S13.9).

Everything the supervisor persists or transmits passes through here FIRST.
Redaction is pattern-based and deliberately over-eager: a false positive costs a
masked string, a false negative costs a leaked credential.

Two entry points:

    redact_text(text)       -> RedactionResult for a single string
    redact_structure(obj)   -> RedactionResult for arbitrary JSON-shaped data

Both report a `count` because D-007 S13.12 requires every audit record to carry
a redaction count, and S13.9 escalates redaction *uncertainty* to an ASK (which
Phase 2's policy engine consumes; this module only reports the count and the
labels it matched).

Phase 1 scope note: the "never-send list" is the built-in pattern set plus
caller-supplied extra literals. The tracked, owner-editable never-send file and
the ASK escalation path are Phase 2/3.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Iterable, Pattern

#: Replacement marker. Includes the label so an operator can tell *what class* of
#: secret was removed without learning its value.
_MASK = "[REDACTED:{label}]"

#: Key names whose VALUE is always masked regardless of the value's shape.
#: Matched case-insensitively against dict keys.
SENSITIVE_KEY_PATTERN = re.compile(
    r"(?i)(^|_)(secret|token|password|passwd|api[_-]?key|apikey|auth|authorization"
    r"|credential|cookie|session[_-]?key|private[_-]?key|access[_-]?key)($|_)"
)

#: (label, compiled pattern) pairs applied to every string.
#: Ordered most-specific first so a broad pattern never eats a specific one.
_PATTERNS: list[tuple[str, Pattern[str]]] = [
    ("anthropic_key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{8,}")),
    ("openai_key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_\-]{20,}")),
    ("github_pat", re.compile(r"gh[pousr]_[A-Za-z0-9]{16,}")),
    ("github_fine_grained_pat", re.compile(r"github_pat_[A-Za-z0-9_]{20,}")),
    ("aws_access_key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"xox[baprs]-[A-Za-z0-9\-]{10,}")),
    ("google_api_key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("bearer_token", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{12,}")),
    ("basic_auth_url", re.compile(r"[a-zA-Z][a-zA-Z0-9+.\-]*://[^\s/:@]+:[^\s/@]+@")),
    ("private_key_block",
     re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
                re.DOTALL)),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\b")),
    # `KEY=value` / `KEY: value` assignments for sensitive-looking names.
    ("assigned_secret",
     re.compile(r"(?i)\b(?:[A-Z0-9_]*(?:SECRET|TOKEN|PASSWORD|PASSWD|API_?KEY|CREDENTIAL)"
                r"[A-Z0-9_]*)\s*[=:]\s*(?:\"[^\"\n]+\"|'[^'\n]+'|[^\s\"',;]+)")),
]


@dataclasses.dataclass(frozen=True)
class RedactionResult:
    """Outcome of a redaction pass.

    `count` is the number of individual substitutions made; `labels` is the
    sorted set of pattern labels that fired (safe to log - names, never values).
    """

    value: Any
    count: int
    labels: tuple[str, ...]

    @property
    def redacted(self) -> bool:
        return self.count > 0


def _mask(label: str) -> str:
    return _MASK.format(label=label)


def redact_text(
    text: str,
    extra_literals: Iterable[str] | None = None,
) -> RedactionResult:
    """Redact a single string.

    `extra_literals` are exact strings the caller knows must never be persisted
    (for example a value read from the environment). They are masked verbatim,
    before the pattern pass, so a literal that does not match any pattern is
    still removed.
    """
    if not isinstance(text, str):
        raise TypeError(f"redact_text expects str, got {type(text).__name__}")

    count = 0
    labels: set[str] = set()
    out = text

    for literal in extra_literals or ():
        if literal and literal in out:
            occurrences = out.count(literal)
            out = out.replace(literal, _mask("never_send"))
            count += occurrences
            labels.add("never_send")

    for label, pattern in _PATTERNS:
        out, n = pattern.subn(_mask(label), out)
        if n:
            count += n
            labels.add(label)

    return RedactionResult(value=out, count=count, labels=tuple(sorted(labels)))


def redact_structure(
    obj: Any,
    extra_literals: Iterable[str] | None = None,
) -> RedactionResult:
    """Recursively redact a JSON-shaped structure.

    Dict values are masked wholesale when their KEY looks sensitive, because a
    value under `api_key` is a secret even when it does not match any pattern.
    Dict keys themselves are left intact (they are structure, not payload).
    """
    literals = tuple(extra_literals or ())
    count = 0
    labels: set[str] = set()

    def walk(node: Any) -> Any:
        nonlocal count, labels
        if isinstance(node, str):
            result = redact_text(node, literals)
            count += result.count
            labels.update(result.labels)
            return result.value
        if isinstance(node, dict):
            out: dict[Any, Any] = {}
            for key, value in node.items():
                if isinstance(key, str) and SENSITIVE_KEY_PATTERN.search(key):
                    # Preserve the shape (None/empty stay as-is: nothing leaked).
                    if value in (None, "", [], {}):
                        out[key] = value
                    else:
                        out[key] = _mask("sensitive_key")
                        count += 1
                        labels.add("sensitive_key")
                else:
                    out[key] = walk(value)
            return out
        if isinstance(node, list):
            return [walk(item) for item in node]
        if isinstance(node, tuple):
            return tuple(walk(item) for item in node)
        return node

    value = walk(obj)
    return RedactionResult(value=value, count=count, labels=tuple(sorted(labels)))
