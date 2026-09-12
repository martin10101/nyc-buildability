"""M4-T010 acceptance pack: rule-citation content-digest binding.

The rule-definition contract gains an OPTIONAL ``citations[].content_digest_sha256``
(64-char lowercase hex), and ``dsl._check_refs`` verifies it fail-closed AT LOAD
against the resolved snapshot's stored digest. Absence of the field is legal
(every pre-existing rule loads unchanged); a recorded digest that disagrees with
the snapshot on disk refuses to load — transcription provenance is bound at the
rule file, which is the representation M4-T009 AS-5 requires and its producer
report §4.4 routed here.

Anti-tautology discipline (M5-T004 lesson): every expected digest is LOADED from
the committed snapshot (or independently recomputed as sha256(verbatim_excerpt)),
never restated as a literal; the S3 mismatch assertion matches the mismatch
message specifically so a mere schema-shape rejection cannot satisfy it.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest

from app.rules.dsl import DSLError, build_rule_definition
from app.rules.snapshots import SnapshotError, SnapshotStore

# test file: <root>/services/api/tests/rules/test_rule_citation_digest.py
_ENGINE_DIR = Path(__file__).resolve().parents[2] / "app" / "rules"
_REPO_ROOT = Path(__file__).resolve().parents[4]
_RULESET_DIR = _ENGINE_DIR / "rulesets"
_DOCS_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"

# The committed ruleset inventory as of this packet (S1 back-compat floor).
_KNOWN_RULE_FILES = 11


@pytest.fixture(scope="module")
def store() -> SnapshotStore:
    """Canonical docs snapshot source — a superset of the packaged bundle."""
    return SnapshotStore(_DOCS_SNAPSHOT_DIR).load()


def _base_doc() -> dict:
    """CONSTRUCTED variant base (clearly labeled, packet rule): the committed
    R5 pilot document, deep-copied so mutations never touch the file."""
    path = _RULESET_DIR / "r5_residential_far.rule.json"
    return copy.deepcopy(json.loads(path.read_text("utf-8")))


def _snapshot_digest(store: SnapshotStore, snapshot_id: str) -> str:
    """The snapshot's STORED digest, cross-checked against an independent
    recomputation so the expected value is derived, never restated."""
    snap = store.get(snapshot_id)
    recomputed = hashlib.sha256(snap.verbatim_excerpt.encode("utf-8")).hexdigest()
    assert snap.content_digest_sha256 == recomputed, (
        f"{snapshot_id}: stored digest is not sha256(verbatim_excerpt); "
        "the v1 snapshot convention is broken and this pack cannot proceed"
    )
    return snap.content_digest_sha256


# --------------------------------------------------------------------------
# S1 — additive backward compatibility: every committed rule loads unchanged.
# --------------------------------------------------------------------------

def test_s1_every_committed_rule_still_validates_and_loads(store):
    files = sorted(_RULESET_DIR.glob("*.rule.json"))
    assert len(files) >= _KNOWN_RULE_FILES, (
        f"ruleset inventory shrank below the {_KNOWN_RULE_FILES} files committed "
        f"when this contract change landed: {[f.name for f in files]}"
    )
    for path in files:
        document = json.loads(path.read_text("utf-8"))
        definition = build_rule_definition(document, store)
        assert definition.rule_id == document["rule_id"]


# --------------------------------------------------------------------------
# S2 — a matching recorded digest loads (the red/green anchor of this unit:
# under the pre-change schema this field was rejected wholesale).
# --------------------------------------------------------------------------

def test_s2_matching_recorded_digest_loads(store):
    doc = _base_doc()
    cited = doc["citations"][0]["snapshot_id"]
    doc["citations"][0]["content_digest_sha256"] = _snapshot_digest(store, cited)
    definition = build_rule_definition(doc, store)
    assert definition.rule_id == doc["rule_id"]


# --------------------------------------------------------------------------
# S3 — a mismatched recorded digest fails closed AT LOAD, with the mismatch
# named. The match= is deliberately specific: a schema-shape rejection says
# "rule schema violation at ..." and cannot satisfy this assertion.
# --------------------------------------------------------------------------

def test_s3_mismatched_recorded_digest_fails_closed_at_load(store):
    doc = _base_doc()
    cited = doc["citations"][0]["snapshot_id"]
    good = _snapshot_digest(store, cited)
    flipped = ("0" if good[0] != "0" else "1") + good[1:]
    assert flipped != good
    doc["citations"][0]["content_digest_sha256"] = flipped
    with pytest.raises(
        DSLError,
        match=r"records content_digest_sha256 .* but the snapshot on disk stores",
    ) as excinfo:
        build_rule_definition(doc, store)
    message = str(excinfo.value)
    assert doc["rule_id"] in message
    assert cited in message


# --------------------------------------------------------------------------
# S4 — malformed digests are rejected by the schema pattern before any
# snapshot comparison runs.
# --------------------------------------------------------------------------

@pytest.mark.parametrize(
    "bad",
    [
        "A" * 64,          # uppercase hex
        "a" * 63,          # too short
        "a" * 65,          # too long
        "z" * 64,          # non-hex
    ],
    ids=["uppercase", "63-chars", "65-chars", "non-hex"],
)
def test_s4_malformed_digest_is_a_schema_violation(store, bad):
    doc = _base_doc()
    doc["citations"][0]["content_digest_sha256"] = bad
    with pytest.raises(DSLError, match=r"rule schema violation at citations/0"):
        build_rule_definition(doc, store)


# --------------------------------------------------------------------------
# S5 — a missing snapshot still fails through the EXISTING resolution path
# first; the digest check introduces no new resolution behavior.
# --------------------------------------------------------------------------

def test_s5_missing_snapshot_still_raises_snapshot_error_first(store):
    doc = _base_doc()
    doc["citations"][0]["snapshot_id"] = "zr-does-not-exist"
    doc["citations"][0]["content_digest_sha256"] = "a" * 64
    with pytest.raises(SnapshotError):
        build_rule_definition(doc, store)
