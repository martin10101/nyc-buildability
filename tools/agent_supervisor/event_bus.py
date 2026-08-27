"""Durable hook-event bus: dedup + ordering + restart-safe replay (D-024
Amendment 3 unit D, M0-T105; R155/R173).

The accepted telemetry subsystem is REUSED end-to-end, never rebuilt:
`telemetry_hooks.ingest_hook_event` (M0-T089) types each hook payload,
`telemetry_journal.TelemetryJournal` (M0-T088) persists it (sanitize-first,
atomic temp-rename, bounded, rotated), and `telemetry_hooks.SubagentRegistry`
tracks open/close identity. This module adds ONLY the bus semantics unit D
introduces:

* **dedup** -- an idempotency key (event + session + task + explicit event id
  when present, plus a full-payload content digest) is computed at publish and
  stored ON the record; a replayed or double-fired hook is a counted no-op;
* **ordering** -- a monotonic ``bus_sequence`` stamped on each stored record
  preserves arrival order across restarts and journal rotation;
* **restart-safe replay** -- a new bus over the same store rebuilds the dedup
  set, the sequence counter, and the subagent registry from disk (rotated
  generations included) without re-emitting any effect or double-counting a
  dedup-keyed event;
* **session masking** -- raw session/task UUIDs never reach the durable store:
  UUID-shaped identity values are replaced by a stable digest reference before
  the (already sanitize-first) journal write, so correlation survives replay
  while the raw UUID does not.

Hooks write EXTERNAL state only (R155 / D-024 s5.1 item 5): nothing here
blocks a hook, injects model context, or messages a worker.

Supervisor-freeze qualifying evidence: D-024-R155 + D-024-R173.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
from collections import OrderedDict
from typing import Any, Mapping

from .event_stream import ingest_stream_event, parse_stream_json_line, stream_idempotency_key
from .telemetry_hooks import SubagentRegistry, ingest_hook_event
from .telemetry_journal import DEFAULT_MAX_BYTES, DEFAULT_MAX_GENERATIONS, TelemetryJournal
from .telemetry_records import TelemetryRecord, TelemetryRecordError


class EventBusError(Exception):
    """A durable event-bus operation failed (fail visible, never invent)."""


#: Full-string UUID shape (the raw session/task identity form the durable
#: store must never carry -- masked to a stable digest reference instead).
_UUID_RE = re.compile(
    r"(?i)^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")

#: Bounded in-memory dedup window default (keys, not bytes).
DEFAULT_MAX_SEEN_KEYS = 4096


def mask_session_value(value: str) -> str:
    """Stable digest reference for a raw session/task UUID.

    The digest keeps replay/registry correlation working (same input, same
    reference) while the raw UUID never touches disk.
    """
    digest = hashlib.sha256(value.encode("utf-8", "replace")).hexdigest()[:12]
    return f"[SESSION sha256={digest}]"


def _mask_uuids(node: Any) -> Any:
    """Recursively digest-mask every UUID-shaped string (values AND dict
    keys) so no raw UUID reaches the durable store at any nesting depth —
    the round-1 converged finding (G4-L2 / G5-LOW-1 / G3-A4): the top-level
    mask alone let a UUID inside a list/dict attribute value slip through."""
    if isinstance(node, str):
        return mask_session_value(node) if _UUID_RE.match(node) else node
    if isinstance(node, dict):
        return {_mask_uuids(key) if isinstance(key, str) else key:
                _mask_uuids(value) for key, value in node.items()}
    if isinstance(node, (list, tuple)):
        masked = [_mask_uuids(item) for item in node]
        return masked if isinstance(node, list) else tuple(masked)
    return node


def idempotency_key(event_name: Any, payload: Any) -> str:
    """Deterministic dedup key: event + session + task + explicit event id,
    plus a canonical-content digest as the discriminator of last resort.

    Two deliveries of the SAME event with the SAME payload (a double-fired or
    replayed hook) share a key; any payload difference (sequence ids,
    timestamps the runtime stamps per firing) yields a distinct key.
    """
    name = event_name if isinstance(event_name, str) else f"<{type(event_name).__name__}>"
    identity: dict[str, Any] = {"event": name}
    if isinstance(payload, Mapping):
        for field in ("session_id", "task_id", "prompt_id", "hook_event_id", "uuid"):
            value = payload.get(field)
            if isinstance(value, str) and value:
                identity[field] = value
        canonical = json.dumps(dict(payload), sort_keys=True, ensure_ascii=False,
                               default=repr)
    else:
        canonical = repr(payload)
    identity["content_sha256"] = hashlib.sha256(
        canonical.encode("utf-8", "replace")).hexdigest()
    blob = json.dumps(identity, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


@dataclasses.dataclass(frozen=True)
class ReplayResult:
    """Pure state rebuild from the durable store -- no effect re-emission.

    ``store_duplicates`` counts stored records sharing an idempotency key
    (possible only if two writers raced the same store; surfaced, never
    silently collapsed). ``skipped_lines`` are torn/malformed journal lines
    (counted by the journal read path, never guessed into records).
    """

    stored_records: tuple[dict[str, Any], ...]
    registry: SubagentRegistry
    seen_keys: tuple[str, ...]
    last_sequence: int
    skipped_lines: int
    store_duplicates: int
    unparseable_records: int


def replay_store(path: str | os.PathLike[str], *,
                 max_bytes: int = DEFAULT_MAX_BYTES,
                 max_generations: int = DEFAULT_MAX_GENERATIONS,
                 include_rotated: bool = True,
                 registry_max_entries: int = 512) -> ReplayResult:
    """Rebuild bus state (dedup set, sequence, registry) from the store.

    Reading is the ONLY action: no record is re-appended, no hook re-fires,
    no message is sent. A restart therefore reconstructs the pre-restart
    state without double-counting any dedup-keyed event (scenario S6).
    """
    journal = TelemetryJournal(path, max_bytes=max_bytes,
                               max_generations=max_generations)
    result = journal.read_all(include_rotated=include_rotated)
    registry = SubagentRegistry(max_entries=registry_max_entries)
    seen: "OrderedDict[str, None]" = OrderedDict()
    duplicates = 0
    unparseable = 0
    last_sequence = 0
    for stored in result.records:
        attributes = stored.get("attributes")
        attributes = attributes if isinstance(attributes, dict) else {}
        key = attributes.get("idempotency_key")
        if isinstance(key, str) and key:
            if key in seen:
                duplicates += 1
            else:
                seen[key] = None
        sequence = attributes.get("bus_sequence")
        if isinstance(sequence, int) and not isinstance(sequence, bool):
            last_sequence = max(last_sequence, sequence)
        try:
            registry.observe(TelemetryRecord.from_dict(stored))
        except TelemetryRecordError:
            # A stored record that no longer parses is surfaced as a count;
            # replay never guesses it into registry state.
            unparseable += 1
    return ReplayResult(
        stored_records=result.records, registry=registry,
        seen_keys=tuple(seen), last_sequence=last_sequence,
        skipped_lines=result.skipped_lines, store_duplicates=duplicates,
        unparseable_records=unparseable)


class DurableEventBus:
    """Durable, deduplicated, ordered event store over the telemetry journal.

    Construction replays the existing store (bounded by the journal's own
    rotation caps) so publish-time dedup survives a process restart: an event
    re-delivered after a crash is recognized by its stored idempotency key
    and recorded exactly once (scenarios S2/S6).
    """

    def __init__(self, path: str | os.PathLike[str], *,
                 max_seen_keys: int = DEFAULT_MAX_SEEN_KEYS,
                 max_bytes: int = DEFAULT_MAX_BYTES,
                 max_generations: int = DEFAULT_MAX_GENERATIONS,
                 registry_max_entries: int = 512,
                 never_send: tuple[str, ...] = (),
                 fsync: bool = True,
                 warm_rotated: bool = True) -> None:
        if max_seen_keys < 1:
            raise ValueError("max_seen_keys must be >= 1")
        self._journal = TelemetryJournal(
            path, max_bytes=max_bytes, max_generations=max_generations,
            fsync=fsync, never_send=never_send)
        self._max_seen_keys = max_seen_keys
        replay = replay_store(
            path, max_bytes=max_bytes, max_generations=max_generations,
            include_rotated=warm_rotated,
            registry_max_entries=registry_max_entries)
        self._seen: "OrderedDict[str, None]" = OrderedDict(
            (key, None) for key in replay.seen_keys[-max_seen_keys:])
        self._sequence = replay.last_sequence
        self._registry = replay.registry
        self.duplicates_ignored = 0
        self.published = 0

    @property
    def registry(self) -> SubagentRegistry:
        return self._registry

    @property
    def path(self) -> Any:
        return self._journal.path

    def _remember(self, key: str) -> None:
        self._seen[key] = None
        while len(self._seen) > self._max_seen_keys:
            self._seen.popitem(last=False)

    def _store(self, record: TelemetryRecord, key: str) -> TelemetryRecord:
        """Stamp bus metadata, mask raw UUIDs, append, then track identity.

        The key is remembered only AFTER a successful append: a failed write
        (for example a bounds violation) leaves the event unrecorded and
        re-publishable -- fail closed toward durability, never toward silent
        loss behind a remembered key.
        """
        self._sequence += 1
        attributes = _mask_uuids(dict(record.attributes))
        attributes["idempotency_key"] = key
        attributes["bus_sequence"] = self._sequence
        stored_record = dataclasses.replace(
            record,
            session_id=_mask_uuids(record.session_id),
            task_id=_mask_uuids(record.task_id),
            attributes=attributes)
        try:
            self._journal.append(stored_record)
        except Exception:
            self._sequence -= 1
            raise
        self._remember(key)
        self._registry.observe(stored_record)
        self.published += 1
        return stored_record

    def publish(self, event_name: Any, payload: Any, *,
                now_utc_iso: str | None = None) -> TelemetryRecord | None:
        """Record one hook event; a duplicate delivery is a counted no-op.

        Unknown event names flow through `ingest_hook_event` unchanged and
        are recorded honestly (``known: false``) -- never dropped, never
        guessed, never a crash (scenario S7).
        """
        key = idempotency_key(event_name, payload)
        if key in self._seen:
            self.duplicates_ignored += 1
            return None
        record = ingest_hook_event(event_name, payload, now_utc_iso=now_utc_iso)
        return self._store(record, key)

    def publish_stream_event(self, event: Mapping[str, Any], *,
                             now_utc_iso: str | None = None
                             ) -> TelemetryRecord | None:
        """Record one parsed stream-JSON subagent event (dedup-keyed)."""
        key = stream_idempotency_key(event)
        if key in self._seen:
            self.duplicates_ignored += 1
            return None
        record = ingest_stream_event(event, now_utc_iso=now_utc_iso)
        return self._store(record, key)

    def publish_stream_line(self, line: str, *,
                            now_utc_iso: str | None = None
                            ) -> TelemetryRecord | None:
        """Parse one stream-JSON line and record it; blank lines are no-ops.

        A malformed line raises the typed `event_stream.StreamEventError`
        (scenario S3) -- the caller keeps the statusLine sidecar primary
        (R154) and never mistakes a parse failure for an empty stream.
        """
        event = parse_stream_json_line(line)
        if event is None:
            return None
        return self.publish_stream_event(event, now_utc_iso=now_utc_iso)

    def publish_typed(self, record: TelemetryRecord) -> TelemetryRecord | None:
        """Record one already-typed TelemetryRecord, dedup-keyed on its
        content (record_type + identity + canonical attribute AND
        measurement digest — round-1 G3-C1 fix: two status snapshots that
        advance only their measurements are DISTINCT records, never a
        false-dedup; ingestion timestamps stay excluded so a true replay of
        the same observation still collapses).

        Additive unit-E consumption seam (M0-T106; D-024-R174): goal
        check-in/status records produced by other modules persist through
        the SAME durable store, dedup, and replay semantics as hook and
        stream records — no second persistence path. Existing publish paths
        are unchanged.
        """
        key = idempotency_key(
            f"typed:{record.record_type}",
            {"session_id": record.session_id, "task_id": record.task_id,
             "attributes": dict(record.attributes),
             "measurements": {name: m.to_dict() for name, m
                              in record.measurements.items()}})
        if key in self._seen:
            self.duplicates_ignored += 1
            return None
        return self._store(record, key)

    def replay(self, *, include_rotated: bool = True) -> ReplayResult:
        """Fresh pure rebuild from disk (state inspection; no side effects)."""
        return replay_store(
            self._journal.path, max_bytes=self._journal.max_bytes,
            max_generations=self._journal.max_generations,
            include_rotated=include_rotated)
