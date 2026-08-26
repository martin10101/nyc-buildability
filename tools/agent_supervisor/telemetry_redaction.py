"""Telemetry-specific sanitization on top of the secret redaction pass
(D-024 Phase B, M0-T088; 16.1 "redaction of credentials, prompts, repository
secrets, and terminal escape sequences").

`redaction.py` (D-007 S13.9) removes credential-shaped content. Telemetry
persisted to journals/sidecars needs three further hygiene passes:

* **terminal escapes** -- status/usage payloads can carry ANSI/VT sequences;
  stored records must be plain text (16.1);
* **user paths** -- home-directory prefixes are masked because the repository
  is PUBLIC (M0-T086 G5-S1 adjudication: probe_meta and telemetry must not
  commit fresh absolute install paths);
* **prompts / free text** -- the journal stores summaries and references, not
  full prompts or transcripts (D-024 s5.3): prompt-like keys are withheld as
  digest references and any long free text is bounded to an excerpt + digest.

`sanitize_structure` composes all passes and is the single entry point the
telemetry journal/sidecar write path uses. `redact_probe_meta` is the wiring
point for `capability_probe` (G5-S1).

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

from .redaction import SENSITIVE_KEY_PATTERN, RedactionResult, redact_text

#: CSI (colors/cursor), OSC (titles/hyperlinks), and single-char ESC sequences,
#: plus stray control characters other than tab/newline.
_TERMINAL_ESCAPES = re.compile(
    r"\x1b\[[0-?]*[ -/]*[@-~]"          # CSI ... final byte
    r"|\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)"  # OSC ... BEL or ST
    r"|\x1b[@-Z\\-_]"                    # single-char escapes (incl. bare ST)
    r"|[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]"  # other C0 controls + DEL
)

#: Dict keys whose string values are prompt/transcript-like and therefore
#: never stored verbatim (D-024 s5.3: summaries and references, not prompts).
PROMPT_KEY_PATTERN = re.compile(
    r"(?i)(^|_)(prompt|prompts|instruction|instructions|assignment[_-]?text"
    r"|transcript[_-]?text|message[_-]?text|conversation)($|_)"
)

#: Free-text ceiling for any persisted string; longer text is excerpted.
MAX_TEXT_CHARS = 512
_EXCERPT_CHARS = 128

#: Home-directory prefixes for the platforms this controller runs on. The
#: replacement keeps the path's tail useful while dropping the identifying
#: prefix. Both slash directions are matched on every platform (paths cross
#: machines inside evidence records).
_HOME_PREFIXES = re.compile(
    r"(?i)(?:[A-Z]:[\\/]Users[\\/]|/(?:home|Users)/)[^\\/\s\"',;:\]\[]+"
)
_HOME_MASK = "[HOME]"


def strip_terminal_escapes(text: str) -> tuple[str, int]:
    """Remove terminal escape sequences/control chars; return (clean, count)."""
    return _TERMINAL_ESCAPES.subn("", text)


def redact_user_paths(text: str) -> tuple[str, int]:
    """Mask home-directory prefixes: ``C:\\Users\\name`` / ``/home/name`` ->
    ``[HOME]`` (drive-letter case-insensitive; the username segment is
    consumed by the mask)."""
    return _HOME_PREFIXES.subn(_HOME_MASK, text)


def _digest_marker(original: str, kind: str) -> str:
    digest = hashlib.sha256(original.encode("utf-8", "replace")).hexdigest()
    return f"[{kind} sha256={digest} chars={len(original)}]"


def withhold_prompt(text: str) -> str:
    """Replace prompt-like text with a verifiable reference, never the content."""
    return _digest_marker(text, "PROMPT-WITHHELD")


def withhold_prompt_value(value: Any) -> str:
    """Withhold ANY prompt-like value - scalar or nested structure - wholesale.

    M0-T088 G4-Adv2 carried fix: a prompt-like key holding a LIST or DICT of
    message strings (a conversation, a transcript slice) must not survive as
    per-string excerpts; the whole subtree collapses to one digest reference
    over its canonical JSON (D-024 s5.3/R044: summaries and references, never
    prompt content).
    """
    if isinstance(value, str):
        return withhold_prompt(value)
    canonical = json.dumps(value, sort_keys=True, ensure_ascii=False,
                           default=repr)
    return _digest_marker(canonical, "PROMPT-WITHHELD")


def bound_text(text: str, max_chars: int = MAX_TEXT_CHARS) -> str:
    """Bound free text to an excerpt plus a digest reference (D-024 s5.3)."""
    if len(text) <= max_chars:
        return text
    return text[:_EXCERPT_CHARS] + _digest_marker(text, "TRUNCATED")


def sanitize_text(
    text: str,
    extra_literals: Iterable[str] | None = None,
    *,
    max_chars: int = MAX_TEXT_CHARS,
) -> RedactionResult:
    """Escape-strip, path-mask, secret-redact, then bound one string.

    Secret redaction runs AFTER escape stripping so a credential fragmented by
    escape sequences still matches, and BEFORE bounding so truncation can never
    cut a secret in half and leak the head.
    """
    out, count = strip_terminal_escapes(text)
    labels: set[str] = set()
    if count:
        labels.add("terminal_escape")
    out, n = redact_user_paths(out)
    if n:
        count += n
        labels.add("user_path")
    secret = redact_text(out, extra_literals)
    out = secret.value
    count += secret.count
    labels.update(secret.labels)
    bounded = bound_text(out, max_chars)
    if bounded is not out:
        count += 1
        labels.add("bounded_text")
    return RedactionResult(value=bounded, count=count, labels=tuple(sorted(labels)))


def sanitize_structure(
    obj: Any,
    extra_literals: Iterable[str] | None = None,
) -> RedactionResult:
    """Recursively sanitize a JSON-shaped structure for telemetry persistence.

    Key-driven rules run first (they see the ORIGINAL value): sensitive keys
    are masked exactly as `redaction.redact_structure` masks them; prompt-like
    keys become digest references. Everything else gets the string pipeline.
    """
    literals = tuple(extra_literals or ())
    count = 0
    labels: set[str] = set()

    def walk(node: Any) -> Any:
        nonlocal count, labels
        if isinstance(node, str):
            result = sanitize_text(node, literals)
            count += result.count
            labels.update(result.labels)
            return result.value
        if isinstance(node, dict):
            out: dict[Any, Any] = {}
            for key, value in node.items():
                if isinstance(key, str) and SENSITIVE_KEY_PATTERN.search(key):
                    if value in (None, "", [], {}):
                        out[key] = value
                    else:
                        out[key] = "[REDACTED:sensitive_key]"
                        count += 1
                        labels.add("sensitive_key")
                elif (isinstance(key, str) and PROMPT_KEY_PATTERN.search(key)
                        and value not in (None, "", [], {}, ())):
                    # scalar OR nested list/dict: withheld wholesale (G4-Adv2)
                    out[key] = withhold_prompt_value(value)
                    count += 1
                    labels.add("prompt_withheld")
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


def redact_probe_meta(meta: dict[str, Any]) -> dict[str, Any]:
    """Sanitize a capability-probe ``probe_meta`` block (G5-S1 wiring).

    probe_meta legitimately varies between runs (timestamps, resolved binary
    paths) but must not publish home-directory prefixes in a PUBLIC repo.
    """
    result = sanitize_structure(meta)
    value = result.value
    if not isinstance(value, dict):  # sanitize preserves the input shape
        raise TypeError("probe_meta must be a dict")
    return value
