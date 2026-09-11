"""M4-T009 provenance/surfacing half of the R1-R12 residential FAR acceptance
pack: AS-5 (source-digest binding) and AS-6 (qualifying alternative surfaced).

Split out of ``test_r1_r12_residential_far.py`` (which carries AS-1/2/3/4/7/8/9)
so neither module crosses the modularity warn threshold; together they are the
complete AS-1..AS-9 evidence.

AS-5 - SOURCE-DIGEST BINDING, MATCHING *and* MISMATCHED CONTENT.
    Each rule is bound to its expected committed snapshot digest through the
    EXISTING engine-supported representation - not a new field:

      * every rule's ``citations[].snapshot_id`` resolves to a committed
        ``*.snapshot.json`` that records ``content_digest_sha256``;
      * ``SnapshotStore.load`` fails closed (``SnapshotError``) if a snapshot's
        stored digest != ``sha256(verbatim_excerpt)`` (tamper-evidence at load);
      * ``RuleResult.export`` fails closed (``ProvenanceError``) unless every
        cited snapshot's provenance carries ``content_digest_sha256`` (PRD s19).

    MATCHING is asserted non-tautologically: the digest the engine resolves for a
    rule equals BOTH the committed snapshot file's stored digest AND an
    independent recomputation ``sha256`` of that committed file's excerpt (three
    independent derivations must agree). MISMATCHED content is asserted three
    ways: (a) content altered without updating the stored digest -> load refuses
    it; (b) a silent re-capture (content changed + digest recomputed) yields a
    DIFFERENT digest than the family was authored against, so the drift is
    detectable; (c) stripping the citation provenance makes ``export`` fail
    closed. A rule-FILE-recorded digest field (so a rule could carry its own
    expected digest for LOAD-time checking) would need an additive property on
    ``rule_definition.schema.json`` ``citations[]`` (currently
    ``additionalProperties: false``) or a string-valued parameter (parameter
    ``value`` objects are constrained to numbers) - both out of this task's
    allowed paths and NOT made here. See the M4-T009 producer report.

AS-6 - SECOND COLUMN SURFACED FOR EVERY DISTRICT, NEVER APPLIED.
    For every applicable district the qualifying (second-column) alternative is
    surfaced through the exception SELECTED BY ITS ID (never by scanning
    concatenated exception text), whose effect is ``conditional_alternative`` and
    whose citation resolves to the on-disk snapshot digest (tying AS-6 to AS-5).
    The district -> qualifying-value association is byte-checked against the
    snapshot (loaded, never restated), and where the two columns differ the higher
    value is never applied. Negative (metamorphic) cases prove those assertions are
    load-bearing: deleting the qualifying exception, and deleting or misassigning a
    district entry, each make an assertion fail. R8 is the discriminator - its
    wide-street standard alternative repeats 7.20, which is ALSO R8's qualifying
    value, so a naive text search for "7.20" still passes after the qualifying
    surfacing is deleted; only the by-id selection catches it.
"""

from __future__ import annotations

import hashlib
import json
from decimal import Decimal
from pathlib import Path

import pytest

from app.rules import RuleRegistry
from app.rules import coverage as cov
from app.rules.models import ProvenanceError
from app.rules.snapshots import SnapshotError, SnapshotStore

# test file: <root>/services/api/tests/rules/test_r1_r12_residential_far_provenance.py
_ENGINE_DIR = Path(__file__).resolve().parents[2] / "app" / "rules"
_REPO_ROOT = Path(__file__).resolve().parents[4]
_RULESET_DIR = _ENGINE_DIR / "rulesets"
_DOCS_SNAPSHOT_DIR = _REPO_ROOT / "docs" / "research" / "zr-snapshots" / "v1"

_EFFECTIVE_FROM = "2024-12-05"

_FLAT_RULES = {
    "r1-r2-r3-residential-far": "r1_r2_r3_residential_far.rule.json",
    "r2x-r4-residential-far": "r2x_r4_residential_far.rule.json",
    "r5-residential-far": "r5_residential_far.rule.json",
    "r6-r12-residential-far": "r6_r12_residential_far.rule.json",
}
_CONDITIONAL_RULE = "r6-r7-r8-wide-street-conditional-far"
_CONDITIONAL_FILE = "r6_r7_r8_wide_street_conditional_far.rule.json"
_ALL_FAR_RULES = {**_FLAT_RULES, _CONDITIONAL_RULE: _CONDITIONAL_FILE}

# The four ZR 23-22 districts footnote 1 conditions on wide-street proximity.
_CONDITIONAL_DISTRICTS = ("R6", "R7-1", "R7-2", "R8")


# --------------------------------------------------------------------------
# Fixtures / snapshot helpers - everything is loaded from the committed source.
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def registry() -> RuleRegistry:
    """Registry over the production rulesets, resolving citations against the
    CANONICAL docs snapshot source (a superset of the packaged bundle)."""
    return RuleRegistry(_RULESET_DIR, snapshots=SnapshotStore(_DOCS_SNAPSHOT_DIR)).load()


def _rule_doc(rule_id: str) -> dict:
    return json.loads((_RULESET_DIR / _ALL_FAR_RULES[rule_id]).read_text("utf-8"))


def _snapshot_raw(snapshot_id: str) -> dict:
    return json.loads((_DOCS_SNAPSHOT_DIR / f"{snapshot_id}.snapshot.json").read_text("utf-8"))


def _row_values(row: dict) -> tuple[str, str]:
    """(standard, qualifying) value STRINGS for a table row, tolerating the two
    column-naming schemes (23-21 vs 23-22)."""
    if "standard_zoning_lots" in row:
        return row["standard_zoning_lots"], row["qualifying_residential_sites"]
    return row["standard_residences"], row["qualifying_affordable_or_senior_housing"]


def _district_rows(snapshot_id: str) -> dict[str, list[dict]]:
    """Map each district -> the list of table rows it appears in. A flat district
    appears in exactly one row; a wide-street-conditional district appears twice."""
    out: dict[str, list[dict]] = {}
    for row in _snapshot_raw(snapshot_id)["table"]["rows"]:
        std, qual = _row_values(row)
        for district in row["districts"]:
            out.setdefault(district, []).append({"standard": std, "qualifying": qual})
    return out


def _rule_snapshot_id(rule_id: str) -> str:
    """Every rule in this family cites exactly one snapshot; return its id."""
    ids = {c["snapshot_id"] for c in _rule_doc(rule_id)["citations"]}
    assert len(ids) == 1, f"{rule_id} cites more than one snapshot: {ids}"
    return ids.pop()


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _write_snapshot_dir(tmp_path: Path, mutate) -> Path:
    """Copy every committed docs snapshot into a fresh temp dir, applying
    ``mutate(raw_dict)`` to each before writing, so a scenario can tamper one
    snapshot while every other rule's citation still resolves."""
    out = tmp_path / "snaps"
    out.mkdir()
    for src in sorted(_DOCS_SNAPSHOT_DIR.glob("*.snapshot.json")):
        raw = json.loads(src.read_text("utf-8"))
        mutate(raw)
        (out / src.name).write_text(json.dumps(raw), encoding="utf-8")
    return out


def _qualifying_conditional_text(trace: dict) -> str:
    """Concatenated description text of every conditional-alternative exception in
    the evaluation output (this is where a qualifying second-column value is
    surfaced, per the r5 pilot pattern)."""
    return " || ".join(
        e["description"]
        for e in trace["exceptions_applied"]
        if e["effect"] == "conditional_alternative"
    )


# --------------------------------------------------------------------------
# AS-5 - MATCHING content: every rule binds its expected committed digest.
# --------------------------------------------------------------------------

def test_as5_citations_resolve_on_disk_with_expected_dates() -> None:
    """Every rule's citation resolves to a snapshot file that exists on disk and
    whose committed digest is self-consistent (== sha256 of its own excerpt), with
    the section number and 2024-12-05 amendment date matching the snapshot."""
    store = SnapshotStore(_DOCS_SNAPSHOT_DIR).load()
    for rule_id in _ALL_FAR_RULES:
        for citation in _rule_doc(rule_id)["citations"]:
            snap = store.get(citation["snapshot_id"])  # SnapshotError if missing on disk
            raw = _snapshot_raw(citation["snapshot_id"])
            assert citation["section"] == snap.section_number
            assert citation["last_amended"] == _EFFECTIVE_FROM
            assert snap.content_digest_sha256 == _sha256(snap.verbatim_excerpt)
            assert raw["content_digest_sha256"] == snap.content_digest_sha256
            assert raw["source"]["last_amended_machine_readable"].startswith(_EFFECTIVE_FROM)


def test_as5_matching_every_rule_binds_committed_snapshot_digest(registry) -> None:
    """MATCHING: for every rule, the digest the engine resolves into the exported
    trace equals BOTH the committed snapshot file's stored digest AND an independent
    recomputation of ``sha256(verbatim_excerpt)`` - three independent derivations
    that must agree, so this is not a store-checks-itself tautology. ``export()``
    itself fails closed (ProvenanceError) if any citation lacks a resolvable
    digest."""
    store = SnapshotStore(_DOCS_SNAPSHOT_DIR).load()
    for rule_id in _ALL_FAR_RULES:
        doc = _rule_doc(rule_id)
        district = doc["applicability"]["values"][0]
        result = registry.evaluate(rule_id, {"zoning_district": district, "lot_area_sq_ft": 1_000})
        trace = result.export()
        assert len(trace["citations"]) == len(doc["citations"]) == 1, (
            f"{rule_id} must carry exactly one citation"
        )
        citation = trace["citations"][0]
        committed = _snapshot_raw(citation["snapshot_id"])
        snap = store.get(citation["snapshot_id"])
        resolved = citation["provenance"]["content_digest_sha256"]
        assert resolved == snap.content_digest_sha256
        assert resolved == committed["content_digest_sha256"], (
            f"{rule_id}: resolved digest {resolved} != committed file digest "
            f"{committed['content_digest_sha256']}"
        )
        assert resolved == _sha256(committed["verbatim_excerpt"]), (
            f"{rule_id}: committed digest is not the sha256 of its verbatim excerpt"
        )


# --------------------------------------------------------------------------
# AS-5 - MISMATCHED content: the binding fails closed / detects drift.
# --------------------------------------------------------------------------

def test_as5_tampered_excerpt_without_digest_update_fails_closed(tmp_path) -> None:
    """MISMATCHED (a): if a committed snapshot's content is altered but its stored
    digest is left unchanged, ``SnapshotStore.load`` refuses it - so the family can
    never silently bind to drifted source content."""
    def mutate(raw: dict) -> None:
        if raw["snapshot_id"] == "zr-23-21":
            raw["verbatim_excerpt"] = raw["verbatim_excerpt"] + " TAMPERED"
            # stored content_digest_sha256 deliberately left as-is -> now a mismatch

    bad_dir = _write_snapshot_dir(tmp_path, mutate)
    with pytest.raises(SnapshotError):
        SnapshotStore(bad_dir).load()
    # and a whole registry cannot be built over the drifted source either.
    with pytest.raises(SnapshotError):
        RuleRegistry(_RULESET_DIR, snapshots=SnapshotStore(bad_dir)).load()


def test_as5_silent_recapture_drift_is_detectable(tmp_path) -> None:
    """MISMATCHED (b): a snapshot re-captured with DIFFERENT content and a correctly
    recomputed digest loads (it is internally consistent), but its digest differs
    from the digest the family was authored against - so a check comparing the
    resolved digest to the committed expected digest detects the drift, and it is
    not a self-comparison. The rule evaluated over the drifted store carries the
    DRIFTED digest, never the committed one."""
    committed_digest = _snapshot_raw("zr-23-22")["content_digest_sha256"]

    def mutate(raw: dict) -> None:
        if raw["snapshot_id"] == "zr-23-22":
            new_excerpt = raw["verbatim_excerpt"] + "\n\n[re-captured with altered content]"
            raw["verbatim_excerpt"] = new_excerpt
            raw["content_digest_sha256"] = _sha256(new_excerpt)  # internally consistent

    drift_dir = _write_snapshot_dir(tmp_path, mutate)
    store = SnapshotStore(drift_dir).load()  # loads: consistent, no SnapshotError
    drifted = store.get("zr-23-22").content_digest_sha256
    assert drifted != committed_digest, "drift must change the digest"

    registry = RuleRegistry(_RULESET_DIR, snapshots=SnapshotStore(drift_dir)).load()
    for rule_id in ("r6-r12-residential-far", _CONDITIONAL_RULE):
        district = _rule_doc(rule_id)["applicability"]["values"][0]
        trace = registry.evaluate(
            rule_id, {"zoning_district": district, "lot_area_sq_ft": 1_000}
        ).export()
        resolved = trace["citations"][0]["provenance"]["content_digest_sha256"]
        assert resolved == drifted
        assert resolved != committed_digest


def test_as5_export_fails_closed_without_resolvable_digest(registry) -> None:
    """MISMATCHED (c): a material value can never be exported without a resolvable
    citation digest (PRD s19); stripping the provenance makes ``export`` raise."""
    result = registry.evaluate(
        "r1-r2-r3-residential-far", {"zoning_district": "R2", "lot_area_sq_ft": 1_000}
    )
    result.trace.citations[0]["provenance"] = {}
    with pytest.raises(ProvenanceError):
        result.export()


# --------------------------------------------------------------------------
# AS-6 - SECOND COLUMN SURFACED FOR EVERY DISTRICT, NEVER APPLIED.
#
# Strengthened (M4-T009 rework 2026-09-11): the qualifying alternative is selected
# BY ITS EXCEPTION ID, its effect and citation are verified, and the applicable
# district -> qualifying-value association is byte-checked against the snapshot.
# Negative (metamorphic) cases prove those assertions are load-bearing. The R8
# case is the discriminator (wide-street standard alternative repeats 7.20, which
# is also R8's qualifying value).
# --------------------------------------------------------------------------

# The qualifying (second-column) exception id differs by source table: ZR 23-21
# (R1-R5) surfaces "qualifying residential sites"; ZR 23-22 (R6-R12) surfaces
# "qualifying affordable / senior housing".
_QUALIFYING_EXCEPTION_ID = {
    "r1-r2-r3-residential-far": "qualifying_residential_site",
    "r2x-r4-residential-far": "qualifying_residential_site",
    "r5-residential-far": "qualifying_residential_site",
    "r6-r12-residential-far": "qualifying_housing",
    _CONDITIONAL_RULE: "qualifying_housing",
}
# R8's wide-street (footnote-1) standard alternative; its higher value (7.20)
# equals R8's qualifying value, which is exactly why by-id selection is required.
_WIDE_STREET_EXCEPTION_ID = "wide_street_far_alternative"


def _param_value(doc: dict, name: str) -> dict:
    for param in doc["parameters"]:
        if param["name"] == name:
            return param["value"]
    raise KeyError(f"{doc['rule_id']} has no parameter {name!r}")


def _rule_qualifying_value(doc: dict, district: str) -> Decimal:
    """The qualifying FAR the RULE associates with ``district`` (raises KeyError if
    the district entry was removed from the qualifying_far_by_district map)."""
    return Decimal(str(_param_value(doc, "qualifying_far_by_district")[district]))


def _governing_row(rule_id: str, district: str) -> dict:
    """The district's governing table row. A flat district has one row; a
    wide-street-conditional district has two, and the qualifying_far_by_district
    parameter records the LOWER (non-wide-street) row's qualifying value."""
    rows = _district_rows(_rule_snapshot_id(rule_id))[district]
    return min(rows, key=lambda r: Decimal(r["standard"]))


def _expected_standard(rule_id: str, district: str) -> Decimal:
    return Decimal(_governing_row(rule_id, district)["standard"])


def _expected_qualifying(rule_id: str, district: str) -> Decimal:
    return Decimal(_governing_row(rule_id, district)["qualifying"])


def _assert_district_qualifying_association(rule_id: str, doc: dict, district: str) -> None:
    """AS-6 association: the qualifying value the RULE records for ``district`` equals
    the qualifying value in the snapshot row that governs it (loaded from source,
    never restated). Raises KeyError if the district entry is missing, AssertionError
    if it is misassigned."""
    recorded = _rule_qualifying_value(doc, district)  # KeyError if deleted
    expected = _expected_qualifying(rule_id, district)
    assert recorded == expected, (
        f"{rule_id}:{district} qualifying_far_by_district value {recorded} != "
        f"snapshot qualifying value {expected}"
    )


def _rule_exception(doc: dict, exc_id: str) -> dict:
    matches = [e for e in doc["exceptions"] if e["id"] == exc_id]
    assert len(matches) == 1, (
        f"{doc['rule_id']}: expected exactly one {exc_id!r} exception, got {len(matches)}"
    )
    return matches[0]


def _applied_by_id(trace: dict, exc_id: str) -> list:
    """The applied-exception entries in the evaluation output with this id."""
    return [e for e in trace["exceptions_applied"] if e["id"] == exc_id]


def _assert_exception_citation_resolves(registry, rule_id: str, exc: dict) -> None:
    """AS-6 citation: the qualifying exception's citation_ref is a declared citation
    of the rule, and that citation resolves in the evaluation output to a snapshot
    whose provenance digest equals the on-disk snapshot digest (AS-5 chain)."""
    doc = _rule_doc(rule_id)
    ref = exc["citation_ref"]
    assert ref in {c["snapshot_id"] for c in doc["citations"]}, (
        f"{rule_id}: qualifying exception citation_ref {ref!r} is not a declared citation"
    )
    district = doc["applicability"]["values"][0]
    trace = registry.evaluate(
        rule_id, {"zoning_district": district, "lot_area_sq_ft": 1_000}
    ).export()
    resolved = {c["snapshot_id"]: c["provenance"]["content_digest_sha256"] for c in trace["citations"]}
    assert resolved[ref] == _snapshot_raw(ref)["content_digest_sha256"]


def _write_ruleset_dir(tmp_path: Path, target_file: str, mutate) -> Path:
    """Copy every production rule file into a fresh temp dir, applying
    ``mutate(raw_dict)`` to ``target_file`` only, so a scenario can break one rule
    while the rest of the registry still loads."""
    out = tmp_path / "rulesets"
    out.mkdir()
    for src in sorted(_RULESET_DIR.glob("*.rule.json")):
        raw = json.loads(src.read_text("utf-8"))
        if src.name == target_file:
            mutate(raw)
        (out / src.name).write_text(json.dumps(raw), encoding="utf-8")
    return out


def _registry_over(ruleset_dir: Path) -> RuleRegistry:
    return RuleRegistry(ruleset_dir, snapshots=SnapshotStore(_DOCS_SNAPSHOT_DIR)).load()


# ---- AS-6 positive: by-id selection, effect, citation, association ----------

@pytest.mark.parametrize("rule_id", list(_FLAT_RULES))
def test_as6_flat_rules_surface_qualifying_by_id_effect_citation_association(registry, rule_id) -> None:
    """For each flat rule and EACH applicable district: the qualifying second-column
    alternative is surfaced through the exception SELECTED BY ID (not a text scan),
    with effect ``conditional_alternative`` and a resolvable citation; the district's
    qualifying value is byte-associated to the snapshot and appears in the surfaced
    exception; and the higher value is never applied (max stays the standard)."""
    doc = _rule_doc(rule_id)
    exc_id = _QUALIFYING_EXCEPTION_ID[rule_id]
    rule_exc = _rule_exception(doc, exc_id)
    assert rule_exc["effect"] == "conditional_alternative"
    _assert_exception_citation_resolves(registry, rule_id, rule_exc)

    for district in doc["applicability"]["values"]:
        _assert_district_qualifying_association(rule_id, doc, district)
        standard = _expected_standard(rule_id, district)
        qualifying = _expected_qualifying(rule_id, district)
        result = registry.evaluate(
            rule_id, {"zoning_district": district, "lot_area_sq_ft": 10_000}
        )
        trace = result.export()
        assert result.coverage_status == cov.COVERAGE_CONDITIONAL, (
            f"{rule_id}:{district} should be conditional with the eligibility input absent"
        )
        applied = _applied_by_id(trace, exc_id)
        assert len(applied) == 1, (
            f"{rule_id}:{district} must surface exactly one {exc_id!r} conditional alternative"
        )
        assert applied[0]["effect"] == "conditional_alternative"
        assert f"{qualifying:.2f}" in applied[0]["description"], (
            f"{rule_id}:{district} qualifying value {qualifying:.2f} not surfaced by {exc_id!r}"
        )
        max_far = Decimal(str(trace["outputs"]["max_residential_far"]))
        assert max_far == standard
        if standard != qualifying:
            # the higher second-column value is surfaced, never applied.
            assert max_far != qualifying


def test_as6_conditional_rule_surfaces_qualifying_by_id_never_applied(registry) -> None:
    """The four wide-street-conditional districts surface their qualifying
    alternative through the ``qualifying_housing`` exception SELECTED BY ID, while
    the returned value stays the conservative standard. R8 is the discriminator: its
    wide-street standard alternative repeats 7.20, which is also its qualifying
    value, so both exceptions must be present and distinct."""
    doc = _rule_doc(_CONDITIONAL_RULE)
    exc_id = _QUALIFYING_EXCEPTION_ID[_CONDITIONAL_RULE]
    rule_exc = _rule_exception(doc, exc_id)
    assert rule_exc["effect"] == "conditional_alternative"
    _assert_exception_citation_resolves(registry, _CONDITIONAL_RULE, rule_exc)

    for district in _CONDITIONAL_DISTRICTS:
        _assert_district_qualifying_association(_CONDITIONAL_RULE, doc, district)
        conservative = _expected_standard(_CONDITIONAL_RULE, district)
        qualifying = _expected_qualifying(_CONDITIONAL_RULE, district)
        trace = registry.evaluate(
            _CONDITIONAL_RULE, {"zoning_district": district, "lot_area_sq_ft": 10_000}
        ).export()
        qualifying_applied = _applied_by_id(trace, exc_id)
        assert len(qualifying_applied) == 1, (
            f"{district} must surface exactly one {exc_id!r} conditional alternative"
        )
        assert qualifying_applied[0]["effect"] == "conditional_alternative"
        assert f"{qualifying:.2f}" in qualifying_applied[0]["description"], (
            f"{district} qualifying value {qualifying:.2f} not surfaced by {exc_id!r}"
        )
        # the wide-street standard alternative is a DISTINCT, separately-surfaced
        # exception (for R8 it repeats 7.20) - the two are never conflated.
        assert _applied_by_id(trace, _WIDE_STREET_EXCEPTION_ID), (
            f"{district}: the wide-street standard alternative must be surfaced separately"
        )
        max_far = Decimal(str(trace["outputs"]["max_residential_far"]))
        assert max_far == conservative
        assert max_far != qualifying


# ---- AS-6 negative (metamorphic): the assertions above are load-bearing -----

def test_as6_negative_deleting_qualifying_exception_removes_flat_surfacing(tmp_path) -> None:
    """Deleting the qualifying exception from a flat rule removes the by-id surfacing
    the positive test asserts, so that assertion is load-bearing."""
    def mutate(raw: dict) -> None:
        raw["exceptions"] = [e for e in raw["exceptions"] if e["id"] != "qualifying_housing"]

    bad_dir = _write_ruleset_dir(tmp_path, "r6_r12_residential_far.rule.json", mutate)
    trace = _registry_over(bad_dir).evaluate(
        "r6-r12-residential-far", {"zoning_district": "R8A", "lot_area_sq_ft": 10_000}
    ).export()
    assert _applied_by_id(trace, "qualifying_housing") == []


def test_as6_negative_deleting_qualifying_exception_on_r8_is_not_masked_by_wide_street_720(tmp_path) -> None:
    """R8 DISCRIMINATOR: delete the qualifying_housing exception from the wide-street
    rule and evaluate R8. The qualifying surfacing is gone - but a NAIVE text search
    for "7.20" STILL passes, because R8's wide-street standard alternative repeats
    7.20. Selecting the exception BY ID is what catches the deletion; a text scan
    would have accepted a rule that silently dropped the qualifying second column."""
    def mutate(raw: dict) -> None:
        raw["exceptions"] = [e for e in raw["exceptions"] if e["id"] != "qualifying_housing"]

    bad_dir = _write_ruleset_dir(tmp_path, _CONDITIONAL_FILE, mutate)
    trace = _registry_over(bad_dir).evaluate(
        _CONDITIONAL_RULE, {"zoning_district": "R8", "lot_area_sq_ft": 10_000}
    ).export()
    # by-id selection catches the deletion ...
    assert _applied_by_id(trace, "qualifying_housing") == []
    # ... even though a naive concatenated-text search still finds 7.20 (wide street):
    assert "7.20" in _qualifying_conditional_text(trace)
    assert _applied_by_id(trace, _WIDE_STREET_EXCEPTION_ID)


@pytest.mark.parametrize(
    "rule_id,district",
    [("r6-r12-residential-far", "R8A"), (_CONDITIONAL_RULE, "R8")],
)
def test_as6_negative_deleting_district_entry_breaks_association(rule_id, district) -> None:
    """Deleting a district entry (including R8) from qualifying_far_by_district breaks
    the district -> value association the positive test asserts."""
    doc = _rule_doc(rule_id)
    del _param_value(doc, "qualifying_far_by_district")[district]
    with pytest.raises(KeyError):
        _rule_qualifying_value(doc, district)
    with pytest.raises(KeyError):
        _assert_district_qualifying_association(rule_id, doc, district)


@pytest.mark.parametrize(
    "rule_id,district",
    [("r6-r12-residential-far", "R8A"), (_CONDITIONAL_RULE, "R8")],
)
def test_as6_negative_misassigning_district_entry_is_detected(rule_id, district) -> None:
    """Misassigning a district's qualifying value (here R8's 7.20 corrupted) makes the
    byte-association to the snapshot fail."""
    doc = _rule_doc(rule_id)
    good = _expected_qualifying(rule_id, district)
    _param_value(doc, "qualifying_far_by_district")[district] = float(good) + 1.0
    with pytest.raises(AssertionError):
        _assert_district_qualifying_association(rule_id, doc, district)
