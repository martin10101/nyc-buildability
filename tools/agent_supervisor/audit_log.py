#!/usr/bin/env python3
"""Append-only audit log with the MANDATORY local hash chain (D-007 S13.12).

S13.12 is explicit: "a plain append-only file is not sufficient for an
unattended autonomous controller". Each event therefore carries

    sequence      strictly increasing, contiguous from 1
    prev_digest   the previous event's digest (genesis links to GENESIS_DIGEST)
    digest        SHA-256 over the event's own canonical JSON, minus `digest`

which makes tampering, reordering, duplication, and truncation detectable:

    tampering    -> a record's recomputed digest no longer matches
    reordering   -> sequence is non-contiguous, or prev_digest does not match
    duplication  -> sequence repeats
    truncation   -> the sidecar head anchor names a sequence/digest the file
                    no longer contains

Truncation deserves a note. A hash chain alone cannot detect that its own TAIL
was removed - the shortened file is internally consistent. Detection needs an
anchor held outside the file. Phase 1 writes a sidecar head file next to the
log (`<log>.head.json`) recording the last sequence and digest, and
`verify_chain()` fails closed when the log falls short of it.

EXTERNAL anchoring (the owner ruled Option A at dispatch: the controller pushes
the chain head to a dedicated `supervisor-audit-anchor` branch) is NOT
implemented here - it needs controller-held push credentials and the ADR-005
amendment to be in force, so it lands in Phase 3. The sidecar head is a strictly
weaker, same-machine anchor and is documented as such. See README.md.

No private transcripts or raw source contents ever enter the log (S13.12); every
record passes through `redaction` first and carries the resulting count.
"""
from __future__ import annotations

import dataclasses
import json
import os
import pathlib
from typing import Any, Iterator

from . import CONTROLLER_VERSION
from .models import AuditRecord, canonical_json, digest_of, to_utc_iso
from .redaction import redact_structure

#: prev_digest of the first record in a chain.
GENESIS_DIGEST = "0" * 64

#: Fields that are never part of a record's own digest.
_DIGEST_EXCLUDED = ("digest",)


class AuditChainError(Exception):
    """The audit chain failed verification. Recovery must halt, not repair.

    S13.12: "Missing, reordered, duplicated, truncated, or digest-invalid audit
    events halt recovery rather than being silently repaired."
    """

    def __init__(self, code: str, message: str, sequence: int | None = None) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.sequence = sequence


@dataclasses.dataclass(frozen=True)
class ChainVerification:
    """Result of verifying a chain. `ok` False always carries a code."""

    ok: bool
    records_checked: int
    head_sequence: int
    head_digest: str
    code: str = ""
    message: str = ""
    failed_sequence: int | None = None


def compute_record_digest(record: dict[str, Any]) -> str:
    """Digest of an audit record, excluding the `digest` field itself."""
    payload = {k: v for k, v in record.items() if k not in _DIGEST_EXCLUDED}
    return digest_of(payload)


class AuditLog:
    """Append-only, hash-chained JSONL audit log.

    The log is opened in append mode and flushed + fsynced on every write: an
    unattended controller must not lose its last events to a power cut. The head
    anchor is rewritten (replace-write) after each append.
    """

    def __init__(self, path: str | os.PathLike[str], *, fsync: bool = True) -> None:
        self.path = pathlib.Path(path)
        self.head_path = self.path.with_suffix(self.path.suffix + ".head.json")
        self._fsync = fsync
        self.path.parent.mkdir(parents=True, exist_ok=True)
        #: Set when the existing log could not be read. The log then REFUSES new
        #: appends (never append onto a chain you cannot verify) while still
        #: allowing `verify_chain()` to report the damage, so `doctor` and
        #: recovery can diagnose a broken log instead of crashing on open.
        self.load_error: AuditChainError | None = None
        try:
            self._sequence, self._prev_digest = self._load_head_from_log()
        except AuditChainError as exc:
            self.load_error = exc
            self._sequence, self._prev_digest = -1, ""

    # -- state ---------------------------------------------------------------

    @property
    def head_sequence(self) -> int:
        return self._sequence

    @property
    def head_digest(self) -> str:
        return self._prev_digest

    def _load_head_from_log(self) -> tuple[int, str]:
        """Read the log's own tail to resume the chain (no trust in the sidecar)."""
        if not self.path.exists():
            return 0, GENESIS_DIGEST
        last: dict[str, Any] | None = None
        for record in self._iter_raw():
            last = record
        if last is None:
            return 0, GENESIS_DIGEST
        return int(last["sequence"]), str(last["digest"])

    def _iter_raw(self) -> Iterator[dict[str, Any]]:
        """Yield parsed records. Tolerates a BOM and CRLF; refuses malformed JSON."""
        with self.path.open("r", encoding="utf-8-sig", newline="") as handle:
            for lineno, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AuditChainError(
                        "malformed_record",
                        f"line {lineno} is not valid JSON: {exc}",
                    ) from exc

    # -- writing -------------------------------------------------------------

    def append(
        self,
        event_type: str,
        *,
        run_id: str = "",
        checkpoint_id: str = "",
        state_from: str = "",
        state_to: str = "",
        executable_identity: dict[str, Any] | None = None,
        input_digest: str = "",
        output_digest: str = "",
        decision: str = "",
        policy_result: str = "",
        error_category: str = "",
        detail: dict[str, Any] | None = None,
        never_send: tuple[str, ...] = (),
    ) -> AuditRecord:
        """Append one event, redacting first and chaining to the current head."""
        if self.load_error is not None:
            raise AuditChainError(
                "append_to_damaged_chain",
                f"refusing to append to an unreadable audit log ({self.load_error.code}: "
                f"{self.load_error.message}); a damaged chain is never silently extended")
        redacted = redact_structure(
            {
                "executable_identity": executable_identity or {},
                "detail": detail or {},
            },
            extra_literals=never_send,
        )
        body = redacted.value

        record = AuditRecord(
            sequence=self._sequence + 1,
            timestamp_utc=to_utc_iso(),
            event_type=event_type,
            run_id=run_id,
            controller_version=CONTROLLER_VERSION,
            prev_digest=self._prev_digest,
            checkpoint_id=checkpoint_id,
            state_from=state_from,
            state_to=state_to,
            executable_identity=body["executable_identity"],
            input_digest=input_digest,
            output_digest=output_digest,
            decision=decision,
            policy_result=policy_result,
            error_category=error_category,
            redaction_count=redacted.count,
            detail=body["detail"],
        )
        as_dict = record.to_dict()
        as_dict["digest"] = compute_record_digest(as_dict)

        line = canonical_json(as_dict).decode("utf-8") + "\n"
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            handle.write(line)
            handle.flush()
            if self._fsync:
                os.fsync(handle.fileno())

        self._sequence = as_dict["sequence"]
        self._prev_digest = as_dict["digest"]
        self._write_head()
        return AuditRecord.from_dict(as_dict)

    def _write_head(self) -> None:
        """Replace-write the sidecar head anchor (truncation detection)."""
        payload = {
            "sequence": self._sequence,
            "digest": self._prev_digest,
            "updated_at_utc": to_utc_iso(),
            "controller_version": CONTROLLER_VERSION,
        }
        tmp = self.head_path.with_suffix(self.head_path.suffix + ".tmp")
        tmp.write_bytes(canonical_json(payload) + b"\n")
        os.replace(tmp, self.head_path)

    # -- verification --------------------------------------------------------

    def read_all(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        return list(self._iter_raw())

    def verify_chain(self) -> ChainVerification:
        """Verify the whole chain. Never repairs; reports the first failure."""
        try:
            records = self.read_all()
        except AuditChainError as exc:
            return ChainVerification(False, 0, 0, "", exc.code, exc.message, exc.sequence)

        prev = GENESIS_DIGEST
        expected_seq = 1
        seen: set[int] = set()

        for record in records:
            seq = record.get("sequence")
            if not isinstance(seq, int):
                return ChainVerification(False, len(seen), expected_seq - 1, prev,
                                         "bad_sequence_type",
                                         f"sequence must be an int, got {seq!r}")
            if seq in seen:
                return ChainVerification(False, len(seen), expected_seq - 1, prev,
                                         "duplicate_sequence",
                                         f"sequence {seq} appears more than once", seq)
            if seq != expected_seq:
                return ChainVerification(False, len(seen), expected_seq - 1, prev,
                                         "sequence_gap_or_reorder",
                                         f"expected sequence {expected_seq}, found {seq}",
                                         seq)
            if record.get("prev_digest") != prev:
                return ChainVerification(False, len(seen), expected_seq - 1, prev,
                                         "prev_digest_mismatch",
                                         f"record {seq} does not link to the previous record",
                                         seq)
            recomputed = compute_record_digest(record)
            if record.get("digest") != recomputed:
                return ChainVerification(False, len(seen), expected_seq - 1, prev,
                                         "digest_mismatch",
                                         f"record {seq} content does not match its digest",
                                         seq)
            seen.add(seq)
            prev = str(record["digest"])
            expected_seq += 1

        head_seq = expected_seq - 1

        # Truncation: the chain is internally consistent but shorter than the
        # anchor says it should be.
        anchor = self._read_head_anchor()
        if anchor is not None:
            if head_seq < int(anchor["sequence"]):
                return ChainVerification(
                    False, len(seen), head_seq, prev, "truncated",
                    f"head anchor records sequence {anchor['sequence']} but the log "
                    f"ends at {head_seq}", head_seq)
            if head_seq == int(anchor["sequence"]) and prev != anchor["digest"]:
                return ChainVerification(
                    False, len(seen), head_seq, prev, "head_digest_mismatch",
                    "log head digest does not match the head anchor", head_seq)

        return ChainVerification(True, len(seen), head_seq, prev)

    def _read_head_anchor(self) -> dict[str, Any] | None:
        if not self.head_path.exists():
            return None
        try:
            data = json.loads(self.head_path.read_text(encoding="utf-8-sig"))
        except json.JSONDecodeError:
            return None
        if not isinstance(data, dict) or "sequence" not in data or "digest" not in data:
            return None
        return data

    def require_valid(self) -> ChainVerification:
        """Verify and raise `AuditChainError` on failure (startup / recovery use)."""
        verification = self.verify_chain()
        if not verification.ok:
            raise AuditChainError(verification.code, verification.message,
                                  verification.failed_sequence)
        return verification
