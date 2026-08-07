#!/usr/bin/env python3
"""Versioned cross-CLI protocol: envelopes, framing, sequencing (D-007 S8.5).

Codex and Claude never talk to each other. Every logical message crosses the
supervisor as a schema-validated UTF-8 JSON/JSONL envelope carrying

    protocol_version schema_version message_id correlation_id sequence
    run_id task_id payload_type created_at_utc producer producer_version
    payload_digest payload

Three pieces live here:

`build_envelope` / `validate_envelope`
    Construction and strict inbound validation, including recomputing
    `payload_digest` - a payload that does not match its digest is refused
    before anything acts on it.

`EnvelopeReader`
    Incremental JSONL framing built on an incremental UTF-8 decoder, so it
    tolerates fragmented reads, split multibyte characters, CRLF line endings,
    a UTF-8 BOM, blank lines, and interleaved non-JSON stderr noise. Buffers are
    BOUNDED: an over-long line fails closed rather than growing without limit.

`SequenceTracker`
    Idempotent message-id handling plus refusal of gaps, reordering, and
    conflicting reuse of a message id.

Phase 1 scope note: the startup capability handshake against resolved
executables (S8.5) is represented by `CapabilityManifest` here as a data
structure with a comparison function; the live probe that populates it from
`claude --version` / `codex --version` belongs to Phase 2's adapters.
"""
from __future__ import annotations

import codecs
import dataclasses
import json
import uuid
from typing import Any, Iterator, Mapping

from . import PROTOCOL_VERSION, SCHEMA_VERSION
from .models import ProtocolEnvelope, RecordError, digest_of, to_utc_iso

#: Refuse any single JSONL line larger than this (bounded buffers, S8.5).
DEFAULT_MAX_LINE_BYTES = 1_048_576

#: Refuse an envelope whose serialized form exceeds this (packet-size bound, S10).
DEFAULT_MAX_ENVELOPE_BYTES = 4_194_304

#: How many non-JSON noise lines to retain for diagnostics before dropping them.
DEFAULT_MAX_NOISE_LINES = 100

PAYLOAD_TYPES = (
    "claude_checkpoint",
    "codex_decision",
    "evidence_packet",
    "forwarded_prompt",
    "handoff",
    "capability_handshake",
    "owner_answer",
)


class ProtocolError(Exception):
    """An envelope or stream violated the protocol. Always fail closed."""

    def __init__(self, code: str, message: str, message_id: str | None = None) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
        self.message_id = message_id


# --------------------------------------------------------------------------
# Envelope construction and validation
# --------------------------------------------------------------------------


def new_message_id() -> str:
    return f"msg_{uuid.uuid4().hex}"


def build_envelope(
    *,
    payload: Any,
    payload_type: str,
    run_id: str,
    task_id: str,
    sequence: int,
    producer: str,
    producer_version: str,
    correlation_id: str,
    message_id: str | None = None,
    created_at_utc: str | None = None,
) -> ProtocolEnvelope:
    """Build a valid envelope, computing `payload_digest` from the payload."""
    if payload_type not in PAYLOAD_TYPES:
        raise ProtocolError("unknown_payload_type",
                            f"{payload_type!r} not in {list(PAYLOAD_TYPES)}")
    if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
        raise ProtocolError("bad_sequence", "sequence must be an integer >= 1")

    return ProtocolEnvelope(
        protocol_version=PROTOCOL_VERSION,
        schema_version=SCHEMA_VERSION,
        message_id=message_id or new_message_id(),
        correlation_id=correlation_id,
        sequence=sequence,
        run_id=run_id,
        task_id=task_id,
        payload_type=payload_type,
        created_at_utc=created_at_utc or to_utc_iso(),
        producer=producer,
        producer_version=producer_version,
        payload_digest=digest_of(payload),
        payload=payload,
    )


def serialize_envelope(envelope: ProtocolEnvelope) -> str:
    """One JSONL line, newline-terminated."""
    return json.dumps(envelope.to_dict(), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False) + "\n"


def validate_envelope(
    data: Mapping[str, Any],
    *,
    max_bytes: int = DEFAULT_MAX_ENVELOPE_BYTES,
    expect_protocol_version: str = PROTOCOL_VERSION,
) -> ProtocolEnvelope:
    """Validate identity, framing, schema, size, and digest before acting (S8.5)."""
    try:
        envelope = ProtocolEnvelope.from_dict(data)
    except RecordError as exc:
        raise ProtocolError("bad_envelope_shape", exc.message) from exc

    if envelope.protocol_version != expect_protocol_version:
        raise ProtocolError(
            "protocol_version_mismatch",
            f"expected protocol_version {expect_protocol_version!r}, got "
            f"{envelope.protocol_version!r}; the supervisor fails closed when installed "
            f"behavior no longer matches the accepted capability manifest",
            envelope.message_id)
    if envelope.schema_version != SCHEMA_VERSION:
        raise ProtocolError("schema_version_mismatch",
                            f"expected schema_version {SCHEMA_VERSION!r}, got "
                            f"{envelope.schema_version!r}", envelope.message_id)
    if envelope.payload_type not in PAYLOAD_TYPES:
        raise ProtocolError("unknown_payload_type",
                            f"{envelope.payload_type!r} not in {list(PAYLOAD_TYPES)}",
                            envelope.message_id)
    if not isinstance(envelope.sequence, int) or isinstance(envelope.sequence, bool) \
            or envelope.sequence < 1:
        raise ProtocolError("bad_sequence", "sequence must be an integer >= 1",
                            envelope.message_id)
    if not envelope.message_id or not envelope.run_id:
        raise ProtocolError("missing_identity", "message_id and run_id are required",
                            envelope.message_id)

    size = len(json.dumps(data, ensure_ascii=False).encode("utf-8"))
    if size > max_bytes:
        raise ProtocolError("envelope_too_large",
                            f"envelope is {size} bytes, limit is {max_bytes}",
                            envelope.message_id)

    recomputed = digest_of(envelope.payload)
    if recomputed != envelope.payload_digest:
        raise ProtocolError(
            "payload_digest_mismatch",
            "payload does not match payload_digest; the message is corrupt or was "
            "modified in transit", envelope.message_id)

    return envelope


# --------------------------------------------------------------------------
# Incremental JSONL framing
# --------------------------------------------------------------------------


@dataclasses.dataclass
class ReaderStats:
    lines_seen: int = 0
    envelopes_yielded: int = 0
    blank_lines: int = 0
    noise_lines: int = 0
    bytes_consumed: int = 0


class EnvelopeReader:
    """Incremental, bounded JSONL reader tolerant of real subprocess streams.

    Feed it whatever chunks arrive (`bytes` or `str`); it yields validated
    envelopes as complete lines become available. Anything that is not JSON at
    all is treated as interleaved noise (stderr bleed) and counted, not raised -
    a subprocess writing a banner must not crash the supervisor. Anything that
    IS JSON but is not a valid envelope raises `ProtocolError`, because that is
    a protocol violation rather than noise.
    """

    def __init__(
        self,
        *,
        max_line_bytes: int = DEFAULT_MAX_LINE_BYTES,
        max_envelope_bytes: int = DEFAULT_MAX_ENVELOPE_BYTES,
        max_noise_lines: int = DEFAULT_MAX_NOISE_LINES,
        strict_noise: bool = False,
    ) -> None:
        self.max_line_bytes = max_line_bytes
        self.max_envelope_bytes = max_envelope_bytes
        self.max_noise_lines = max_noise_lines
        self.strict_noise = strict_noise
        self.stats = ReaderStats()
        self.noise: list[str] = []
        self._decoder = codecs.getincrementaldecoder("utf-8")(errors="strict")
        self._buffer = ""
        self._seen_first_line = False

    def feed(self, chunk: bytes | str) -> Iterator[ProtocolEnvelope]:
        """Consume a chunk; yield every envelope that completed."""
        if isinstance(chunk, bytes):
            self.stats.bytes_consumed += len(chunk)
            text = self._decoder.decode(chunk)
        else:
            self.stats.bytes_consumed += len(chunk.encode("utf-8"))
            text = chunk
        self._buffer += text

        while True:
            index = self._buffer.find("\n")
            if index < 0:
                break
            line = self._buffer[:index]
            self._buffer = self._buffer[index + 1:]
            yield from self._handle_line(line)

        if len(self._buffer.encode("utf-8")) > self.max_line_bytes:
            overflow = len(self._buffer.encode("utf-8"))
            self._buffer = ""
            raise ProtocolError(
                "line_too_large",
                f"unterminated line exceeded the {self.max_line_bytes}-byte bound "
                f"({overflow} bytes buffered); buffer discarded and the stream fails closed")

    def close(self) -> Iterator[ProtocolEnvelope]:
        """Flush a final line that arrived without a trailing newline (early pipe close)."""
        tail = self._decoder.decode(b"", True)
        self._buffer += tail
        remainder, self._buffer = self._buffer, ""
        if remainder.strip():
            yield from self._handle_line(remainder)

    def _handle_line(self, line: str) -> Iterator[ProtocolEnvelope]:
        self.stats.lines_seen += 1

        if not self._seen_first_line:
            line = line.lstrip("﻿")  # BOM, only meaningful on the first line
            self._seen_first_line = True
        line = line.rstrip("\r")          # CRLF tolerance
        stripped = line.strip()

        if not stripped:
            self.stats.blank_lines += 1
            return
        if not stripped.startswith("{"):
            self._note_noise(stripped)
            return
        try:
            data = json.loads(stripped)
        except json.JSONDecodeError as exc:
            # It opened as an object but does not parse. A truncated or malformed
            # object is a protocol violation, never "success" and never noise -
            # this is the exact shape a cut-off final message arrives in.
            raise ProtocolError("malformed_json",
                                f"line {self.stats.lines_seen} opens as a JSON object but is "
                                f"not valid JSON (truncated or malformed): {exc}") from exc
        if not isinstance(data, Mapping):
            self._note_noise(stripped)
            return

        envelope = validate_envelope(data, max_bytes=self.max_envelope_bytes)
        self.stats.envelopes_yielded += 1
        yield envelope

    def _note_noise(self, line: str) -> None:
        self.stats.noise_lines += 1
        if self.strict_noise:
            raise ProtocolError("unexpected_non_json",
                                f"non-JSON line on a strict stream: {line[:120]!r}")
        if len(self.noise) < self.max_noise_lines:
            self.noise.append(line[:500])


# --------------------------------------------------------------------------
# Sequencing and idempotency
# --------------------------------------------------------------------------

ACCEPTED = "accepted"
DUPLICATE = "duplicate"


@dataclasses.dataclass(frozen=True)
class AcceptResult:
    """`verdict` is ACCEPTED (process it) or DUPLICATE (already processed; skip)."""

    verdict: str
    envelope: ProtocolEnvelope


class SequenceTracker:
    """Enforce per-producer ordering and idempotent message ids (S8.5).

    * A message id seen before WITH THE SAME envelope digest is a benign retry:
      reported as DUPLICATE so the caller skips re-processing it.
    * A message id seen before with DIFFERENT content is conflicting reuse and is
      refused.
    * A sequence that skips ahead is a gap; one that goes backwards is a
      reordering. Both are refused - the supervisor never guesses what it missed.
    """

    def __init__(self, *, first_sequence: int = 1) -> None:
        self._first_sequence = first_sequence
        self._expected: dict[str, int] = {}
        self._seen: dict[str, str] = {}

    @property
    def seen_message_ids(self) -> frozenset[str]:
        return frozenset(self._seen)

    def expected_sequence(self, producer: str) -> int:
        return self._expected.get(producer, self._first_sequence)

    def accept(self, envelope: ProtocolEnvelope) -> AcceptResult:
        envelope_digest = envelope.digest()
        previous = self._seen.get(envelope.message_id)
        if previous is not None:
            if previous == envelope_digest:
                return AcceptResult(DUPLICATE, envelope)
            raise ProtocolError(
                "conflicting_message_id",
                f"message_id {envelope.message_id!r} was already seen with different "
                f"content; conflicting reuse is refused", envelope.message_id)

        expected = self.expected_sequence(envelope.producer)
        if envelope.sequence != expected:
            code = "sequence_gap" if envelope.sequence > expected else "sequence_reorder"
            raise ProtocolError(
                code,
                f"producer {envelope.producer!r} expected sequence {expected}, got "
                f"{envelope.sequence}", envelope.message_id)

        self._seen[envelope.message_id] = envelope_digest
        self._expected[envelope.producer] = expected + 1
        return AcceptResult(ACCEPTED, envelope)


# --------------------------------------------------------------------------
# Capability handshake (data structure; live probe is Phase 2)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class CapabilityManifest:
    """Accepted executable/protocol capabilities (S8.5, S13.4).

    Phase 1 provides the record and the comparison. Populating it from live
    `--version`/`--help` probes is Phase 2, where the adapters exist.
    """

    executables: dict[str, dict[str, Any]]
    protocol_version: str = PROTOCOL_VERSION
    schema_version: str = SCHEMA_VERSION

    def digest(self) -> str:
        return digest_of(dataclasses.asdict(self))

    def differences(self, observed: "CapabilityManifest") -> tuple[str, ...]:
        """Named differences between accepted and observed capabilities."""
        diffs: list[str] = []
        if observed.protocol_version != self.protocol_version:
            diffs.append(f"protocol_version {self.protocol_version} -> "
                         f"{observed.protocol_version}")
        if observed.schema_version != self.schema_version:
            diffs.append(f"schema_version {self.schema_version} -> {observed.schema_version}")
        for name, accepted in self.executables.items():
            if name not in observed.executables:
                diffs.append(f"{name}: missing from observed capabilities")
                continue
            seen = observed.executables[name]
            for key, value in accepted.items():
                if seen.get(key) != value:
                    diffs.append(f"{name}.{key}: {value!r} -> {seen.get(key)!r}")
        for name in observed.executables:
            if name not in self.executables:
                diffs.append(f"{name}: unexpected new executable in observed capabilities")
        return tuple(diffs)
