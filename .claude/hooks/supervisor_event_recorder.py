"""Supervisor hook-event recorder (D-024 Amendment 3 unit D, M0-T105;
R155/R173).

A thin COMMAND hook (never HTTP): reads ONE hook payload as JSON from stdin
and appends it to the durable event store via the supervisor event bus
(`tools/agent_supervisor/event_bus.py` -- dedup + sanitize-first atomic
persistence + bounded rotation). It records; it never decides.

NOT REGISTERED: wiring this into `.claude/settings.json` is a SEPARATE
reviewed change (settings.json is forbidden_paths for M0-T105); committing
this script activates nothing.

Design guarantees (R155 / scenario S9/S11):
- EXTERNAL STATE ONLY: writes one JSONL record under the bounded store path
  (default ``.claude/telemetry/hook_events.jsonl`` -- the gitignored runtime
  location established by the M0-T099 statusLine sidecar; M0-T100 ignore
  entry). Nothing else on disk is touched; the repository is read-only to
  this script.
- NEVER BLOCKS: always exits 0 and prints NOTHING to stdout -- no
  permissionDecision, no additionalContext, no worker message. A recorder
  cannot gate, delay, or steer a session.
- FAIL CLOSED, SESSION-SAFE: any error (oversized stdin, malformed JSON,
  unwritable store, import failure) records nothing and still exits 0 -- a
  broken recorder must never break the session it observes.
- BOUNDED: stdin is read to a hard byte cap; the store is bounded and
  rotated by the journal; dedup state is bounded by the bus.
- NO SECRETS: embeds no tokens; everything persisted passes the accepted
  sanitize-first pipeline (paths [HOME]-masked, prompts withheld, secrets
  redacted, raw session UUIDs digest-masked by the bus).

``NYCB_EVENT_STORE_PATH`` overrides the store path (tests point it at a
temp directory; production leaves it unset).
"""
import json
import os
import sys
from pathlib import Path

#: A single hook payload larger than this is anomalous input, not data.
MAX_STDIN_BYTES = 1_048_576

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_STORE = _REPO_ROOT / ".claude" / "telemetry" / "hook_events.jsonl"


def _store_path():
    override = os.environ.get("NYCB_EVENT_STORE_PATH")
    return Path(override) if override else _DEFAULT_STORE


def _main():
    # BYTES first, then an explicit UTF-8 decode: Claude Code emits hook
    # payloads as UTF-8, while sys.stdin.read() would use the Windows locale
    # (cp1252) and mojibake or drop non-ASCII events — the measured M0-T104
    # lesson (G4 round-1 M1 fix). utf-8-sig tolerates a BOM; "replace" keeps
    # a damaged byte visible instead of losing the whole event.
    raw_bytes = sys.stdin.buffer.read(MAX_STDIN_BYTES + 1)
    if len(raw_bytes) > MAX_STDIN_BYTES:
        return 0  # oversized payload: record nothing (fail closed)
    payload = json.loads(raw_bytes.decode("utf-8-sig", "replace"))
    if not isinstance(payload, dict):
        return 0
    event_name = payload.get("hook_event_name")
    if not isinstance(event_name, str) or not event_name:
        return 0  # never guess an event name
    sys.path.insert(0, str(_REPO_ROOT))
    from tools.agent_supervisor.event_bus import DurableEventBus

    # fsync off: recorders run on live lifecycle events and must stay fast;
    # the journal read path tolerates (skips + counts) a torn final line by
    # design -- same stance as the accepted statusLine refresh path.
    # warm_rotated off: only the ACTIVE journal generation warms the dedup
    # set, so a duplicate delivered after a rotation boundary is re-recorded
    # (the safe direction -- never data loss, never false-dedup) and later
    # surfaced by replay as store_duplicates; the trade buys bounded
    # per-invocation latency (G3-A3/G4-L1 round-1 disclosure).
    bus = DurableEventBus(_store_path(), fsync=False, warm_rotated=False)
    bus.publish(event_name, payload)
    return 0


if __name__ == "__main__":
    try:
        code = _main()
    except Exception:
        code = 0  # a recorder failure must never break the session (S9)
    raise SystemExit(code)
