#!/usr/bin/env python3
"""Protocol tests: envelope validation, JSONL framing, sequencing (D-007 S8.5, S15).

Covers the "parsing and processes" S15 family at Phase-1 depth: fragmented
JSONL, CRLF, BOM, split multibyte characters, blank lines, interleaved stderr
noise, malformed and truncated JSON, duplicate/reordered/conflicting message
ids, digest mismatch, version mismatch, bounded buffers, and early pipe closure.

Stdlib `unittest` only. No network, no subprocess, no credentials.
"""
from __future__ import annotations

import json
import pathlib
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from tools.agent_supervisor import PROTOCOL_VERSION, SCHEMA_VERSION  # noqa: E402
from tools.agent_supervisor import protocol as pr  # noqa: E402
from tools.agent_supervisor.models import digest_of  # noqa: E402


def envelope(sequence: int = 1, payload: object | None = None,
             message_id: str | None = None, producer: str = "claude"):
    return pr.build_envelope(
        payload={"unit": "one"} if payload is None else payload,
        payload_type="claude_checkpoint",
        run_id="run-1", task_id="M0-T036", sequence=sequence,
        producer=producer, producer_version="2.1.220",
        correlation_id="corr-1", message_id=message_id)


def line(env) -> str:
    return pr.serialize_envelope(env)


class EnvelopeValidationTests(unittest.TestCase):
    def test_valid_envelope_round_trips(self) -> None:
        env = envelope()
        parsed = pr.validate_envelope(json.loads(line(env)))
        self.assertEqual(parsed.message_id, env.message_id)
        self.assertEqual(parsed.payload_digest, digest_of({"unit": "one"}))
        self.assertEqual(parsed.protocol_version, PROTOCOL_VERSION)
        self.assertEqual(parsed.schema_version, SCHEMA_VERSION)

    def test_every_named_field_is_required(self) -> None:
        base = envelope().to_dict()
        for field in ("protocol_version", "schema_version", "message_id", "correlation_id",
                      "sequence", "run_id", "task_id", "payload_type", "created_at_utc",
                      "producer", "producer_version", "payload_digest", "payload"):
            broken = dict(base)
            broken.pop(field)
            with self.assertRaises(pr.ProtocolError) as ctx:
                pr.validate_envelope(broken)
            self.assertEqual(ctx.exception.code, "bad_envelope_shape", field)

    def test_unknown_field_is_rejected(self) -> None:
        data = envelope().to_dict()
        data["extra"] = 1
        with self.assertRaises(pr.ProtocolError) as ctx:
            pr.validate_envelope(data)
        self.assertEqual(ctx.exception.code, "bad_envelope_shape")

    def test_payload_digest_mismatch_is_refused(self) -> None:
        data = envelope().to_dict()
        data["payload"] = {"unit": "tampered"}
        with self.assertRaises(pr.ProtocolError) as ctx:
            pr.validate_envelope(data)
        self.assertEqual(ctx.exception.code, "payload_digest_mismatch")

    def test_protocol_version_mismatch_fails_closed(self) -> None:
        data = envelope().to_dict()
        data["protocol_version"] = "9.9.9"
        with self.assertRaises(pr.ProtocolError) as ctx:
            pr.validate_envelope(data)
        self.assertEqual(ctx.exception.code, "protocol_version_mismatch")

    def test_unknown_payload_type_is_refused(self) -> None:
        data = envelope().to_dict()
        data["payload_type"] = "arbitrary_instruction"
        with self.assertRaises(pr.ProtocolError) as ctx:
            pr.validate_envelope(data)
        self.assertEqual(ctx.exception.code, "unknown_payload_type")

    def test_oversized_envelope_is_refused(self) -> None:
        env = envelope(payload={"blob": "x" * 5000})
        with self.assertRaises(pr.ProtocolError) as ctx:
            pr.validate_envelope(env.to_dict(), max_bytes=1000)
        self.assertEqual(ctx.exception.code, "envelope_too_large")

    def test_bad_sequence_values_are_refused(self) -> None:
        for bad in (0, -1, True):
            with self.assertRaises(pr.ProtocolError):
                pr.build_envelope(payload={}, payload_type="claude_checkpoint",
                                  run_id="r", task_id="t", sequence=bad,  # type: ignore[arg-type]
                                  producer="p", producer_version="v", correlation_id="c")


class FramingTests(unittest.TestCase):
    def read_all(self, reader: pr.EnvelopeReader, chunks) -> list:
        out = []
        for chunk in chunks:
            out.extend(reader.feed(chunk))
        out.extend(reader.close())
        return out

    def test_fragmented_arbitrary_byte_chunks(self) -> None:
        payload = line(envelope(1)) + line(envelope(2)) + line(envelope(3))
        raw = payload.encode("utf-8")
        reader = pr.EnvelopeReader()
        chunks = [raw[i:i + 7] for i in range(0, len(raw), 7)]
        envelopes = self.read_all(reader, chunks)
        self.assertEqual(len(envelopes), 3)
        self.assertEqual([e.sequence for e in envelopes], [1, 2, 3])

    def test_crlf_line_endings(self) -> None:
        raw = (line(envelope(1)).rstrip("\n") + "\r\n").encode("utf-8")
        reader = pr.EnvelopeReader()
        self.assertEqual(len(self.read_all(reader, [raw])), 1)

    def test_leading_bom_is_tolerated(self) -> None:
        raw = "﻿".encode("utf-8") + line(envelope(1)).encode("utf-8")
        reader = pr.EnvelopeReader()
        self.assertEqual(len(self.read_all(reader, [raw])), 1)

    def test_split_multibyte_character(self) -> None:
        env = envelope(1, payload={"note": "café — naïve"})
        raw = line(env).encode("utf-8")
        # Split at every possible byte boundary, including mid-character.
        reader = pr.EnvelopeReader()
        envelopes = self.read_all(reader, [raw[:1] for _ in range(0)] +
                                  [bytes([b]) for b in raw])
        self.assertEqual(len(envelopes), 1)
        self.assertEqual(envelopes[0].payload["note"], "café — naïve")

    def test_blank_lines_and_interleaved_stderr_noise(self) -> None:
        raw = (
            "\n"
            "Warning: something wrote to the same stream\n"
            + line(envelope(1))
            + "\n"
            + "[info] another banner line\n"
            + line(envelope(2))
        ).encode("utf-8")
        reader = pr.EnvelopeReader()
        envelopes = self.read_all(reader, [raw])
        self.assertEqual(len(envelopes), 2)
        self.assertEqual(reader.stats.noise_lines, 2)
        self.assertEqual(reader.stats.blank_lines, 2)

    def test_strict_stream_refuses_noise(self) -> None:
        reader = pr.EnvelopeReader(strict_noise=True)
        with self.assertRaises(pr.ProtocolError) as ctx:
            list(reader.feed(b"not json at all\n"))
        self.assertEqual(ctx.exception.code, "unexpected_non_json")

    def test_malformed_json_object_is_never_treated_as_success(self) -> None:
        reader = pr.EnvelopeReader()
        with self.assertRaises(pr.ProtocolError) as ctx:
            list(reader.feed(b'{"protocol_version": "1.0.0", broken}\n'))
        self.assertEqual(ctx.exception.code, "malformed_json")

    def test_truncated_final_object_is_refused_at_close(self) -> None:
        raw = line(envelope(1)) + '{"protocol_version": "1.0.0", "sch'
        reader = pr.EnvelopeReader()
        got = list(reader.feed(raw.encode("utf-8")))
        self.assertEqual(len(got), 1)
        with self.assertRaises(pr.ProtocolError) as ctx:
            list(reader.close())
        self.assertEqual(ctx.exception.code, "malformed_json")

    def test_final_line_without_newline_is_delivered_on_close(self) -> None:
        raw = line(envelope(1)).rstrip("\n")
        reader = pr.EnvelopeReader()
        self.assertEqual(list(reader.feed(raw.encode("utf-8"))), [])
        self.assertEqual(len(list(reader.close())), 1)

    def test_buffers_are_bounded(self) -> None:
        reader = pr.EnvelopeReader(max_line_bytes=256)
        with self.assertRaises(pr.ProtocolError) as ctx:
            list(reader.feed(b'{"x": "' + b"y" * 1000))
        self.assertEqual(ctx.exception.code, "line_too_large")

    def test_noise_retention_is_capped(self) -> None:
        reader = pr.EnvelopeReader(max_noise_lines=3)
        list(reader.feed(b"noise\n" * 50))
        self.assertEqual(len(reader.noise), 3)
        self.assertEqual(reader.stats.noise_lines, 50)


class SequenceTests(unittest.TestCase):
    def test_in_order_messages_are_accepted(self) -> None:
        tracker = pr.SequenceTracker()
        for i in (1, 2, 3):
            self.assertEqual(tracker.accept(envelope(i)).verdict, pr.ACCEPTED)

    def test_exact_duplicate_is_idempotent_not_reprocessed(self) -> None:
        tracker = pr.SequenceTracker()
        env = envelope(1)
        self.assertEqual(tracker.accept(env).verdict, pr.ACCEPTED)
        self.assertEqual(tracker.accept(env).verdict, pr.DUPLICATE)
        # The duplicate did not advance the expected sequence.
        self.assertEqual(tracker.expected_sequence("claude"), 2)

    def test_conflicting_reuse_of_a_message_id_is_refused(self) -> None:
        tracker = pr.SequenceTracker()
        first = envelope(1, payload={"unit": "one"}, message_id="msg_same")
        second = envelope(2, payload={"unit": "different"}, message_id="msg_same")
        tracker.accept(first)
        with self.assertRaises(pr.ProtocolError) as ctx:
            tracker.accept(second)
        self.assertEqual(ctx.exception.code, "conflicting_message_id")

    def test_sequence_gap_is_refused(self) -> None:
        tracker = pr.SequenceTracker()
        tracker.accept(envelope(1))
        with self.assertRaises(pr.ProtocolError) as ctx:
            tracker.accept(envelope(3))
        self.assertEqual(ctx.exception.code, "sequence_gap")

    def test_reordering_is_refused(self) -> None:
        tracker = pr.SequenceTracker()
        tracker.accept(envelope(1))
        tracker.accept(envelope(2))
        with self.assertRaises(pr.ProtocolError) as ctx:
            tracker.accept(envelope(1, message_id="msg_replayed"))
        self.assertEqual(ctx.exception.code, "sequence_reorder")

    def test_producers_are_sequenced_independently(self) -> None:
        tracker = pr.SequenceTracker()
        tracker.accept(envelope(1, producer="claude"))
        tracker.accept(envelope(1, producer="codex"))
        self.assertEqual(tracker.expected_sequence("claude"), 2)
        self.assertEqual(tracker.expected_sequence("codex"), 2)


class CapabilityHandshakeTests(unittest.TestCase):
    def manifest(self, **over) -> pr.CapabilityManifest:
        executables = {
            "claude": {"version": "2.1.220", "output_modes": ["stream-json"]},
            "codex": {"version": "0.146.0"},
        }
        executables.update(over)
        return pr.CapabilityManifest(executables=executables)

    def test_identical_capabilities_have_no_differences(self) -> None:
        self.assertEqual(self.manifest().differences(self.manifest()), ())

    def test_a_cli_upgrade_is_detected(self) -> None:
        accepted = self.manifest()
        observed = self.manifest(claude={"version": "2.2.0",
                                         "output_modes": ["stream-json"]})
        diffs = accepted.differences(observed)
        self.assertTrue(any("claude.version" in d for d in diffs), diffs)

    def test_a_missing_or_new_executable_is_detected(self) -> None:
        accepted = self.manifest()
        observed = pr.CapabilityManifest(executables={"claude": accepted.executables["claude"],
                                                      "surprise": {"version": "1"}})
        diffs = accepted.differences(observed)
        self.assertTrue(any("codex: missing" in d for d in diffs), diffs)
        self.assertTrue(any("surprise: unexpected" in d for d in diffs), diffs)

    def test_digest_is_stable_and_changes_with_content(self) -> None:
        self.assertEqual(self.manifest().digest(), self.manifest().digest())
        self.assertNotEqual(self.manifest().digest(),
                            self.manifest(codex={"version": "0.147.0"}).digest())


if __name__ == "__main__":
    unittest.main(verbosity=2)
