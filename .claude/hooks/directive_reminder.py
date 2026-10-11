"""Context hook for the Owner Directive Compliance System (directive D-001) and the
research-and-verification workflow (directive D-093).

Reads ONLY the active directive registry (project-control/directives/index.json and
the referenced manifests) and injects a small, advisory, non-blocking reminder:

- SessionStart (sources startup/resume/clear/compact, and an absent source): FIRST one
  bounded research-and-verification line (D-093) naming the always-loaded rule and its
  sha256 digest, the procedure, the evidence-records folder, and the handoff's sanitized
  first line, then the existing bounded "active directive pointer" (directive IDs + short
  titles + registry path + the substance line). The research line is emitted even when there
  are zero active directives, and restores the research pointer after a context compaction.
- UserPromptSubmit: UNCHANGED — ONLY the one-line substance reminder, so the full list is
  not repeated on every prompt and the research line is not re-injected per prompt.

Design guarantees (D-001-R050/R051/R112..R115, correction 6; D-093):
- NON-BLOCKING: always exit 0 with hookSpecificOutput.additionalContext; NEVER emits a
  permissionDecision and NEVER exits 2, so it cannot block a prompt or override the two
  PreToolUse guards (agent_dispatch_guard / readonly_agent_guard are untouched).
- BOUNDED: output is hard-capped; the per-prompt injection is tiny; the research line is
  itself capped (< RESEARCH_CAP, handoff first line <= HANDOFF_CAP) and the existing
  directive part keeps its own SESSION_CAP / PER_PROMPT_CAP.
- NEVER raw source: only validated directive IDs, sanitized short titles, the research
  rule's sha256 digest, the SANITIZED handoff first line, and fixed pointer/imperative text
  are emitted — registry and handoff text are treated as inert DATA, so they cannot become a
  prompt-injection or command-execution surface. Nothing is executed.
- FAIL-VISIBLE (advisory, NOT fail-closed): a corrupt/invalid registry yields a visible
  warning, never silence; a missing research rule file yields a visible WARNING line (still
  exit 0) — the research rule is not loaded, and the session sees that — but the hook is
  advisory and always exits 0, so it never blocks a prompt. Mechanical fail-closed
  enforcement of the directive regime and the research workflow lives in the CLI
  (tools/project_control.py), the validators (tools/validate_directive_compliance.py,
  tools/research_record_check.py), blockers, gates, and CI — never in this hook
  (D-001-R134, amendment 3). Any internal error is caught and downgraded to a short warning
  with exit 0 (a hook failure never breaks a session).
"""
import hashlib
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

# D-093 research-and-verification pointer bounds and repository-relative paths.
RESEARCH_CAP = 600
HANDOFF_CAP = 140
RESEARCH_RULE_REL = ".claude/rules/research-and-verification.md"
RESEARCH_PROCEDURE_REL = "docs/RESEARCH_AND_VERIFICATION.md"
RESEARCH_RECORDS_REL = "docs/research/evidence-records/"
HANDOFF_REL = "docs/SESSION_HANDOFF.md"

SUBSTANCE = ("If this prompt changes repository work, invoke /directive-compliance and "
             "capture/bind it before acting.")


def _registry_dir() -> Path:
    env = os.environ.get("CLAUDE_DIRECTIVE_REGISTRY")
    return Path(env) if env else DEFAULT_REGISTRY


def _research_root() -> Path:
    """The repository root used to find the research rule and handoff. Overridable by
    CLAUDE_RESEARCH_ROOT for tests, mirroring CLAUDE_DIRECTIVE_REGISTRY."""
    env = os.environ.get("CLAUDE_RESEARCH_ROOT")
    return Path(env) if env else ROOT


def _sanitize_title(s: str, limit: int = 60) -> str:
    s = _TITLE_OK.sub("", str(s or ""))[:limit].strip()
    return s or "(untitled)"


def _research_line() -> str:
    """Build the bounded SessionStart research-and-verification pointer (D-093).

    Treats all repository text as inert data: the rule is referenced by its sha256 digest
    (never its body) and the handoff first line is sanitized with the title allow-list and
    capped. A missing rule file yields a visible WARNING instead (the research rule is not
    loaded); a missing handoff says '(handoff missing)'."""
    root = _research_root()
    rule = root / RESEARCH_RULE_REL
    try:
        raw = rule.read_bytes()
    except OSError:
        raw = None
    if raw is None:
        return (f"WARNING (research-and-verification): {RESEARCH_RULE_REL} is missing; "
                f"the research rule is not loaded.")
    digest = hashlib.sha256(raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()[:12]
    handoff = root / HANDOFF_REL
    try:
        text = handoff.read_text(encoding="utf-8", errors="replace")
    except OSError:
        text = None
    if text is None:
        first = "(handoff missing)"
    else:
        lines = text.splitlines()
        first = _sanitize_title(lines[0], HANDOFF_CAP) if lines else "(handoff missing)"
    line = (f"Research and verification (D-093): rule {RESEARCH_RULE_REL} [sha256 {digest}], "
            f"procedure {RESEARCH_PROCEDURE_REL}, evidence records {RESEARCH_RECORDS_REL}. "
            f'Current state: {HANDOFF_REL} ("{first}"). '
            f"On resume or after compaction, re-read the handoff before acting.")
    return _cap(line, RESEARCH_CAP)


def _cap(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)].rstrip() + "..."


def _load_active():
    """Return (active_list, warning). active_list = [(id, title)]. warning is a string
    when the registry is present-but-corrupt (fail-visible: surfaced as an advisory
    warning, exit 0 — never blocking), else None. A missing registry is not a warning
    (zero active directives)."""
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

        if str(event) == "UserPromptSubmit":
            # UserPromptSubmit output is UNCHANGED (no research line, no full list).
            if warning:
                _emit(event, _cap(
                    "WARNING (directive-compliance): " + warning
                    + ". Run `python tools/validate_directive_compliance.py --check`. " + SUBSTANCE,
                    SESSION_CAP))
                return 0
            if not active:
                return 0  # Zero active directives: clean, no injection.
            # Per-prompt: tiny, just the imperative (do not repeat the full list).
            _emit(event, _cap(SUBSTANCE, PER_PROMPT_CAP))
            return 0

        # SessionStart (startup/resume/clear/compact, absent source) or any other non-prompt
        # event: the research-and-verification line FIRST (always, even with zero directives),
        # then the existing directive text (which keeps its own SESSION_CAP).
        research = _research_line()
        if warning:
            directive = _cap(
                "WARNING (directive-compliance): " + warning
                + ". Run `python tools/validate_directive_compliance.py --check`. " + SUBSTANCE,
                SESSION_CAP)
        elif not active:
            directive = ""
        else:
            ids = ", ".join(f"{did} ({title})" for did, title in active[:8])
            directive = _cap(
                (f"Active owner directives ({len(active)}): {ids}. "
                 f"Registry: project-control/directives/ (validate with "
                 f"tools/validate_directive_compliance.py). " + SUBSTANCE), SESSION_CAP)
        _emit(event, research if not directive else research + "\n" + directive)
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
