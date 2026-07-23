"""Context hook for the Owner Directive Compliance System (directive D-001).

Reads ONLY the active directive registry (project-control/directives/index.json and
the referenced manifests) and injects a small, advisory, non-blocking reminder:

- SessionStart (source startup/resume/compact): a bounded "active directive pointer"
  (directive IDs + short titles + registry path + the substance line). This is what
  restores the short pointer after a context compaction.
- UserPromptSubmit: ONLY the one-line substance reminder, so the full list is not
  repeated on every prompt.

Design guarantees (D-001-R050/R051/R112..R115, correction 6):
- NON-BLOCKING: always exit 0 with hookSpecificOutput.additionalContext; NEVER emits a
  permissionDecision and NEVER exits 2, so it cannot block a prompt or override the two
  PreToolUse guards (agent_dispatch_guard / readonly_agent_guard are untouched).
- BOUNDED: output is hard-capped; the per-prompt injection is tiny.
- NEVER raw source: only validated directive IDs, sanitized short titles, and fixed
  pointer/imperative text are emitted — registry text is treated as inert DATA, so it
  cannot become a prompt-injection or command-execution surface. Nothing is executed.
- FAIL-CLOSED & VISIBLE: a corrupt/invalid registry yields a visible warning, never
  silence. Zero active directives yields no injection (clean). Any internal error is
  caught and downgraded to a short warning with exit 0 (a hook failure never breaks a
  session).
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = ROOT / "project-control" / "directives"

DIRECTIVE_ID_RE = re.compile(r"^D-\d{3}$")
_TITLE_OK = re.compile(r"[^A-Za-z0-9 ,.\-()/:+]")

PER_PROMPT_CAP = 400
SESSION_CAP = 1400
MAX_INDEX_BYTES = 262144  # 256 KiB; a directive index is tiny — larger is anomalous

SUBSTANCE = ("If this prompt changes repository work, invoke /directive-compliance and "
             "capture/bind it before acting.")


def _registry_dir() -> Path:
    env = os.environ.get("CLAUDE_DIRECTIVE_REGISTRY")
    return Path(env) if env else DEFAULT_REGISTRY


def _sanitize_title(s: str, limit: int = 60) -> str:
    s = _TITLE_OK.sub("", str(s or ""))[:limit].strip()
    return s or "(untitled)"


def _cap(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _load_active():
    """Return (active_list, warning). active_list = [(id, title)]. warning is a string
    when the registry is present-but-corrupt (fail-closed, visible), else None. A
    missing registry is not a warning (zero active directives)."""
    reg = _registry_dir()
    idx = reg / "index.json"
    if not idx.exists():
        return [], None
    try:
        raw = idx.read_bytes()
    except OSError as e:
        return [], f"directive registry index.json is unreadable ({e})"
    if len(raw) > MAX_INDEX_BYTES:
        return [], (f"directive registry index.json is unexpectedly large "
                    f"({len(raw)} bytes > {MAX_INDEX_BYTES}); refusing to parse")
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (ValueError, UnicodeError) as e:
        return [], f"directive registry index.json is unreadable/corrupt ({e})"
    if not isinstance(data, dict) or not isinstance(data.get("directives"), list):
        return [], "directive registry index.json has an unexpected shape"
    active = []
    for entry in data["directives"]:
        if not isinstance(entry, dict):
            return [], "directive registry index has a malformed entry"
        if entry.get("status") != "active":
            continue
        did = entry.get("directive_id")
        if not (isinstance(did, str) and DIRECTIVE_ID_RE.match(did)):
            return [], f"directive registry has a malformed directive id {did!r}"
        active.append((did, _sanitize_title(entry.get("title"))))
    return active, None


def _emit(event: str, text: str):
    sys.stdout.write(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": event or "UserPromptSubmit",
            "additionalContext": text,
        }
    }))


def main() -> int:
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
        if not isinstance(payload, dict):
            payload = {}
        event = payload.get("hook_event_name") or payload.get("hookEventName") or "UserPromptSubmit"
        active, warning = _load_active()

        if warning:
            _emit(event, _cap(
                "WARNING (directive-compliance): " + warning
                + ". Run `python tools/validate_directive_compliance.py --check`. " + SUBSTANCE,
                SESSION_CAP))
            return 0

        if not active:
            # Zero active directives: clean, no injection.
            return 0

        if str(event) == "UserPromptSubmit":
            # Per-prompt: tiny, just the imperative (do not repeat the full list).
            _emit(event, _cap(SUBSTANCE, PER_PROMPT_CAP))
            return 0

        # SessionStart (startup/resume/compact) or any other: the short active pointer.
        ids = ", ".join(f"{did} ({title})" for did, title in active[:8])
        text = (f"Active owner directives ({len(active)}): {ids}. "
                f"Registry: project-control/directives/ (validate with "
                f"tools/validate_directive_compliance.py). " + SUBSTANCE)
        _emit(event, _cap(text, SESSION_CAP))
        return 0
    except Exception as e:  # pragma: no cover - a hook must never break the session
        try:
            _emit("UserPromptSubmit",
                  _cap(f"WARNING (directive-compliance reminder failed: {e}). " + SUBSTANCE,
                       PER_PROMPT_CAP))
        except Exception:
            pass
        return 0


if __name__ == "__main__":
    sys.exit(main())
