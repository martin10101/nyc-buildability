"""Atomic telemetry sidecar + bounded, rotated JSONL journal (D-024 Phase B,
M0-T088; s5.3: "the telemetry journal must be bounded, rotated, redacted, and
compactable").

Two persistence surfaces, both sanitize-first (everything passes
`telemetry_redaction.sanitize_structure` BEFORE touching disk):

* :class:`TelemetrySidecar` -- one small JSON document holding the latest
  snapshot (the status-line/subagent feeds overwrite it on every refresh).
  Writes are atomic: unique temp file + ``os.replace``, so an interrupted
  writer leaves either the previous complete document (killed before rename)
  or the new complete document (killed after rename) - never a torn file.
  Overlapping refreshes each rename their own temp file; the last rename wins.

* :class:`TelemetryJournal` -- append-only JSONL history with a byte bound and
  numbered-generation rotation (``.1`` newest ... ``.N`` oldest, older dropped).
  This is runtime telemetry, not the tamper-evident audit log: `audit_log.py`
  keeps the hash chain; this journal favors bounded disk use and tolerant
  read-back (a torn final line - a crash mid-append - is skipped and counted,
  never invented into a record).

Nothing here writes into model context or composes prompts (s5.3/R044).

Supervisor-freeze qualifying evidence: D-024-R100.
"""
from __future__ import annotations

import dataclasses
import itertools
import json
import os
import pathlib
import threading
import time
from typing import Any

from .telemetry_records import TelemetryRecord
from .telemetry_redaction import sanitize_structure

#: A sidecar is a "compact external record" (s5.3); refuse to write a snapshot
#: this large rather than let a bug grow it without bound.
MAX_SIDECAR_BYTES = 256 * 1024

#: Journal rotation defaults: rotate the active file when an append would push
#: it past `max_bytes`; keep at most `max_generations` rotated files.
DEFAULT_MAX_BYTES = 4 * 1024 * 1024
DEFAULT_MAX_GENERATIONS = 3

_tmp_counter = itertools.count()


class TelemetryBoundsError(Exception):
    """A payload exceeded the configured telemetry bounds (fail, don't grow)."""


def _atomic_write_bytes(path: pathlib.Path, payload: bytes) -> None:
    """Write via unique temp file + ``os.replace`` (atomic on POSIX and NTFS).

    The temp name embeds pid + a process-local counter so overlapping writers
    never share a temp file. On Windows, ``os.replace`` can transiently fail
    with ``PermissionError`` while a reader holds the destination open; a short
    bounded retry absorbs that without hiding real failures.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(
        f"{path.name}.{os.getpid()}.{next(_tmp_counter)}.tmp")
    with tmp.open("wb") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    try:
        for attempt in range(8):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if attempt == 7:
                    raise
                time.sleep(0.01 * (attempt + 1))
    finally:
        if tmp.exists():  # only on failure; success renamed it away
            try:
                tmp.unlink()
            except OSError:
                pass


def _to_sanitized_dict(record: TelemetryRecord | dict[str, Any],
                       never_send: tuple[str, ...]) -> dict[str, Any]:
    raw = record.to_dict() if isinstance(record, TelemetryRecord) else dict(record)
    result = sanitize_structure(raw, extra_literals=never_send)
    out = result.value
    # Surface the write-path redaction count on the stored record itself so a
    # reader can see that sanitization ran (audit-log parity, D-007 S13.12).
    out["redaction_count"] = int(out.get("redaction_count", 0)) + result.count
    return out


class TelemetrySidecar:
    """Latest-snapshot document with atomic replace-write semantics."""

    def __init__(self, path: str | os.PathLike[str], *,
                 max_bytes: int = MAX_SIDECAR_BYTES,
                 never_send: tuple[str, ...] = ()) -> None:
        self.path = pathlib.Path(path)
        self.max_bytes = max_bytes
        self.never_send = never_send
        # In-process overlap guard: concurrent refresh ticks through one
        # sidecar serialize their renames (Windows denies os.replace to a
        # destination mid-replace by another thread). Cross-process overlap is
        # absorbed by the bounded retry in _atomic_write_bytes.
        self._lock = threading.Lock()

    def update(self, record: TelemetryRecord | dict[str, Any]) -> dict[str, Any]:
        """Sanitize and atomically replace the snapshot; returns what was stored."""
        stored = _to_sanitized_dict(record, self.never_send)
        payload = (json.dumps(stored, ensure_ascii=False, sort_keys=True)
                   + "\n").encode("utf-8")
        if len(payload) > self.max_bytes:
            raise TelemetryBoundsError(
                f"sidecar payload is {len(payload)} bytes; bound is "
                f"{self.max_bytes} (a sidecar stores a compact snapshot, "
                f"never transcripts - D-024 s5.3)")
        with self._lock:
            _atomic_write_bytes(self.path, payload)
        return stored

    def read(self) -> dict[str, Any] | None:
        """The last complete snapshot, or ``None`` when absent/unreadable.

        A sidecar is disposable state: an unparseable file (impossible via the
        atomic writer, possible via external interference) reads as "no
        snapshot" - callers treat that as unknown, never as zero usage.
        """
        try:
            data = json.loads(self.path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError):
            return None
        return data if isinstance(data, dict) else None


@dataclasses.dataclass(frozen=True)
class JournalReadResult:
    """Read-back outcome: parsed records plus the torn/malformed line count."""

    records: tuple[dict[str, Any], ...]
    skipped_lines: int


class TelemetryJournal:
    """Bounded, rotated, redact-first JSONL journal."""

    def __init__(self, path: str | os.PathLike[str], *,
                 max_bytes: int = DEFAULT_MAX_BYTES,
                 max_generations: int = DEFAULT_MAX_GENERATIONS,
                 fsync: bool = True,
                 never_send: tuple[str, ...] = ()) -> None:
        if max_bytes <= 0 or max_generations < 1:
            raise ValueError("max_bytes must be > 0 and max_generations >= 1")
        self.path = pathlib.Path(path)
        self.max_bytes = max_bytes
        self.max_generations = max_generations
        self._fsync = fsync
        self.never_send = never_send
        self._lock = threading.Lock()

    def _generation_path(self, n: int) -> pathlib.Path:
        return self.path.with_name(f"{self.path.name}.{n}")

    def _rotate(self) -> None:
        """path -> .1 -> .2 ... dropping anything past max_generations."""
        oldest = self._generation_path(self.max_generations)
        if oldest.exists():
            oldest.unlink()
        for n in range(self.max_generations - 1, 0, -1):
            src = self._generation_path(n)
            if src.exists():
                os.replace(src, self._generation_path(n + 1))
        if self.path.exists():
            os.replace(self.path, self._generation_path(1))

    def append(self, record: TelemetryRecord | dict[str, Any]) -> dict[str, Any]:
        """Sanitize, bound, rotate if needed, then append one JSONL line."""
        stored = _to_sanitized_dict(record, self.never_send)
        line = (json.dumps(stored, ensure_ascii=False, sort_keys=True)
                + "\n").encode("utf-8")
        if len(line) > self.max_bytes:
            raise TelemetryBoundsError(
                f"journal record is {len(line)} bytes; a single record may not "
                f"exceed the journal bound {self.max_bytes} (store summaries "
                f"and references, not transcripts - D-024 s5.3)")
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            try:
                current = self.path.stat().st_size
            except OSError:
                current = 0
            if current and current + len(line) > self.max_bytes:
                self._rotate()
            with self.path.open("ab") as handle:
                handle.write(line)
                handle.flush()
                if self._fsync:
                    os.fsync(handle.fileno())
        return stored

    def read_all(self, *, include_rotated: bool = False) -> JournalReadResult:
        """Parse the journal (oldest first). Torn lines are skipped, counted,
        and never guessed into records (fail to unknown, not to invention)."""
        paths: list[pathlib.Path] = []
        if include_rotated:
            for n in range(self.max_generations, 0, -1):
                gen = self._generation_path(n)
                if gen.exists():
                    paths.append(gen)
        if self.path.exists():
            paths.append(self.path)
        records: list[dict[str, Any]] = []
        skipped = 0
        for path in paths:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for line in handle:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        parsed = json.loads(line)
                    except json.JSONDecodeError:
                        skipped += 1
                        continue
                    if isinstance(parsed, dict):
                        records.append(parsed)
                    else:
                        skipped += 1
        return JournalReadResult(records=tuple(records), skipped_lines=skipped)
