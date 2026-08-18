#!/usr/bin/env python3
"""Closed-schema session/task memory digest (M0-T067 Unit D, D-013-R044).

The digest is the ONLY input shape the memory graph accepts. The schema is
CLOSED: the allowed field set is exact (an unknown field refuses), every
required field is typed and format-checked, the `agent` value must come from
the repository-derived allowlist (`.claude/agents/*.md` stems + orchestrator),
`outcome` from a fixed enum reconciled with the gate/lifecycle vocabulary, and
`digest_id` must equal the content-derived id (sha256 over the canonical
document without the id itself) — a hand-invented or drifted id refuses.

All validation is fail-closed (`DigestSchemaError` with a machine-readable
code, D-013-R013). Nullable-by-design fields (`source_manifest_fingerprint`,
per-file `content_digest`) accept null but are never fabricated (R051).
Advisory tags are carried as a SEPARATE list — they are leaves, never
structural links (R045); their per-tag validity is judged at promotion so an
invalid tag can be discarded without quarantining the digest (R048).
"""
from __future__ import annotations

import hashlib
import pathlib
import re
import sys

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.context_pack_io import canon_json_bytes  # noqa: E402

DIGEST_SCHEMA_VERSION = "1.0.0"

#: Reconciled with project conventions: gate verdicts + key lifecycle states.
OUTCOME_ENUM = ("PASS", "FAIL", "BLOCKED", "ACCEPTED", "SUBMITTED", "INFO")

MAX_NOTE_CHARS = 2000
MAX_EVIDENCE_REF_CHARS = 300
MAX_ADVISORY_TAG_CHARS = 64

_RX_TASK = re.compile(r"^M\d+-T\d+$")
_RX_REQUIREMENT = re.compile(r"^D-\d{3}-R\d+$")
_RX_SHA40 = re.compile(r"^[0-9a-f]{40}$")
_RX_SHA64 = re.compile(r"^[0-9a-f]{64}$")

#: field name -> (required, type-or-tuple). None-able fields are listed below.
_FIELDS: dict[str, tuple[bool, type | tuple[type, ...]]] = {
    "schema_version": (True, str),
    "digest_id": (True, str),
    "task_id": (True, str),
    "requirement_ids": (True, list),
    "files": (True, list),
    "agent": (True, str),
    "outcome": (True, str),
    "repo_sha": (True, str),
    "source_manifest_fingerprint": (True, (str, type(None))),
    "branch": (True, str),
    "task_index_digest": (True, str),
    "directive_index_digest": (True, str),
    "resolver_version": (True, str),
    "map_version": (True, str),
    "map_digest": (True, str),
    "evidence_refs": (True, list),
    "unresolved_links": (True, list),
    "advisory_tags": (True, list),
    "note": (False, str),
}


class DigestSchemaError(Exception):
    """Fail-closed digest validation error with a machine-readable code."""

    def __init__(self, code: str, detail: str):
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")

    def doc(self) -> dict:
        return {"error": {"code": self.code, "detail": self.detail}}


def agent_allowlist(repo_root: str) -> list[str]:
    """Deterministic allowlist from existing repo facts: .claude/agents stems
    plus the orchestrator (which has no agent file by design)."""
    agents_dir = pathlib.Path(repo_root) / ".claude" / "agents"
    names = {"orchestrator"}
    if agents_dir.is_dir():
        names.update(p.stem for p in agents_dir.glob("*.md"))
    return sorted(names)


def compute_digest_id(doc: dict) -> str:
    """Stable content-derived id: sha256 over the canonical document with the
    digest_id field removed (so the id can be embedded without circularity)."""
    body = {k: v for k, v in doc.items() if k != "digest_id"}
    return hashlib.sha256(canon_json_bytes(body)).hexdigest()


def _require(cond: bool, code: str, detail: str) -> None:
    if not cond:
        raise DigestSchemaError(code, detail)


def _check_files(files: list) -> None:
    for i, f in enumerate(files):
        _require(isinstance(f, dict), "bad_file_entry", f"files[{i}] not an object")
        extra = set(f) - {"path", "content_digest"}
        _require(not extra, "bad_file_entry",
                 f"files[{i}] unknown keys {sorted(extra)}")
        _require(isinstance(f.get("path"), str) and bool(f.get("path")),
                 "bad_file_entry", f"files[{i}].path must be a non-empty string")
        cd = f.get("content_digest")
        _require(cd is None or bool(isinstance(cd, str) and _RX_SHA64.match(cd)),
                 "bad_file_entry",
                 f"files[{i}].content_digest must be null or 64-hex")


def _check_unresolved(links: list) -> None:
    for i, u in enumerate(links):
        _require(isinstance(u, dict), "bad_unresolved_entry", f"unresolved_links[{i}] not an object")
        extra = set(u) - {"kind", "value", "reason"}
        _require(not extra, "bad_unresolved_entry",
                 f"unresolved_links[{i}] unknown keys {sorted(extra)}")
        for k in ("kind", "value", "reason"):
            _require(isinstance(u.get(k), str) and bool(u.get(k)),
                     "bad_unresolved_entry",
                     f"unresolved_links[{i}].{k} must be a non-empty string")


def validate_digest(doc: object, repo_root: str) -> dict:
    """Validate the CLOSED schema; return the doc on success, refuse otherwise."""
    _require(isinstance(doc, dict), "digest_not_object", "digest must be a JSON object")
    assert isinstance(doc, dict)
    unknown = set(doc) - set(_FIELDS)
    _require(not unknown, "closed_schema_violation",
             f"unknown fields {sorted(unknown)} (the digest schema is CLOSED)")
    for name, (required, typ) in _FIELDS.items():
        if name not in doc:
            _require(not required, "missing_required_field", f"missing {name!r}")
            continue
        _require(isinstance(doc[name], typ), "wrong_type",
                 f"{name!r} must be {typ}")
    _require(doc["schema_version"] == DIGEST_SCHEMA_VERSION,
             "unknown_schema_version",
             f"{doc['schema_version']!r} != {DIGEST_SCHEMA_VERSION!r}")
    _require(bool(_RX_TASK.match(doc["task_id"])), "bad_task_id_format",
             f"{doc['task_id']!r}")
    for rid in doc["requirement_ids"]:
        _require(isinstance(rid, str) and bool(_RX_REQUIREMENT.match(rid)),
                 "bad_requirement_id_format", f"{rid!r}")
    _check_files(doc["files"])
    allow = agent_allowlist(repo_root)
    _require(doc["agent"] in allow, "agent_not_in_allowlist",
             f"{doc['agent']!r} not in the repo-derived allowlist ({len(allow)} agents)")
    _require(doc["outcome"] in OUTCOME_ENUM, "outcome_not_in_enum",
             f"{doc['outcome']!r} not in {list(OUTCOME_ENUM)}")
    _require(bool(_RX_SHA40.match(doc["repo_sha"])), "bad_repo_sha",
             f"{doc['repo_sha']!r} must be 40-hex")
    _require(bool(doc["branch"]), "wrong_type", "branch must be non-empty")
    for name in ("task_index_digest", "directive_index_digest"):
        _require(bool(_RX_SHA64.match(doc[name])), "bad_index_digest",
                 f"{name} must be 64-hex")
    _require(bool(_RX_SHA64.match(doc["map_digest"])), "bad_index_digest",
             "map_digest must be 64-hex")
    for i, ref in enumerate(doc["evidence_refs"]):
        _require(isinstance(ref, str) and 0 < len(ref) <= MAX_EVIDENCE_REF_CHARS,
                 "evidence_ref_invalid",
                 f"evidence_refs[{i}] must be a string of 1..{MAX_EVIDENCE_REF_CHARS} chars")
    _check_unresolved(doc["unresolved_links"])
    if "note" in doc:
        _require(len(doc["note"]) <= MAX_NOTE_CHARS, "note_too_long",
                 f"note exceeds {MAX_NOTE_CHARS} chars (no transcripts in digests)")
    expect = compute_digest_id(doc)
    _require(doc["digest_id"] == expect, "digest_id_mismatch",
             f"digest_id {doc['digest_id'][:16]}... != content-derived {expect[:16]}...")
    return doc


def judge_advisory_tag(tag: object) -> str | None:
    """None when the tag is valid; a machine-readable reason otherwise.
    Judged at promotion so an invalid tag is discarded SEPARATELY (R048)."""
    if not isinstance(tag, str):
        return "advisory_tag_not_string"
    if not tag or len(tag) > MAX_ADVISORY_TAG_CHARS:
        return "advisory_tag_bad_length"
    if any(ord(c) < 32 for c in tag):
        return "advisory_tag_control_chars"
    return None
