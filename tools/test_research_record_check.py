#!/usr/bin/env python3
"""Tests for tools/research_record_check.py (owner directive D-093).

Stdlib-only (unittest); runnable as `python3 tools/test_research_record_check.py` so the
control-plane CI job can execute it; non-zero exit on any failure. Every record is built in a
temporary repo root with a tiny code file — the committed NB-*.json records are never read.
"""
from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import research_record_check as rrc  # noqa: E402

CHECKER = HERE / "research_record_check.py"
OUTPUT = "dwelling_units.legal_limit"


def complete_record(code_rel: str, code_sha: str) -> dict:
    """A fully valid record: matching code identity, a current independent agent review, and a
    named professional review for the current revision. Only condition 6 (C1) blocks Verified."""
    return {
        "schema": "research_record/v1",
        "record_id": "NB-90",
        "title": "Special density dwelling-unit limit",
        "revision": 2,
        "last_changed": "2026-10-11",
        "question": {
            "text": "What is the legal dwelling-unit limit?",
            "property": {"address": "215-16 Northern Blvd", "borough": "Queens",
                         "block": 1, "lot": 2},
            "lot_scope": "zoning_lot",
            "site_scope": "whole_site",
            "time_scope": "current_law",
        },
        "evidence": [{
            "id": "E1", "kind": "law_text", "authority": "NYC Zoning Resolution",
            "title": "ZR 23-22", "url": "https://zoningresolution.planning.nyc.gov/node/1",
            "reference": "node/1", "page": None, "document_date": "2026-03-26",
            "retrieved": "2026-10-10", "excerpt": "the quoted provision words",
            "saved_copy": None, "sha256": None,
        }],
        "meaning_and_applicability": {
            "provisions_read": ["ZR 23-22", "ZR 12-10"],
            "exceptions_considered": [],
            "reading": "The provision applies because ...",
            "applies": "yes",
        },
        "measurement_basis": {
            "quantities": [{"name": "lot_area", "value": 10000, "units": "sqft",
                            "basis": "survey", "scope": "existing whole site"}],
            "double_count_risk": "none identified",
        },
        "conclusion": {
            "research_status": "answered_from_primary_source",
            "observed_facts": ["the source states X"],
            "interpretation": "",
            "conflicts": [], "conditions": [], "settled_by": [],
        },
        "searches": [],
        "implementation": {
            "affected_outputs": [OUTPUT],
            "code_paths": [code_rel],
            "code_identity": {code_rel: code_sha},
            "worked_example": {"inputs": {"lot_area": 10000}, "expected": 12,
                               "basis": "independently worked", "prepared_by": "backend-engineer"},
            "regression_cases": [],
            "dependency_assessment": [],
        },
        "review": {
            "producer": "backend-engineer",
            "agent_reviews": [{
                "reviewer": "code-reviewer", "date": "2026-10-11", "reviewed_revision": 2,
                "reviewed_code_identity": {code_rel: code_sha}, "verdict": "agrees",
                "findings": [], "report": None,
            }],
            "professional_review": {
                "reviewer_name": "Jane Doe RA", "role": "Registered Architect",
                "date": "2026-10-11", "reviewed_revision": 2, "decision": "concurs",
                "comments": "reviewed and concurs",
            },
        },
        "freshness": {
            "checked_on": "2026-10-11", "method": "live_fetch", "snapshot_date": None,
            "limitation": "live fetch on the date shown",
        },
        "promotion": {"requested_label": None},
    }


class Base(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="rrc-"))
        (self.root / "app").mkdir(parents=True)
        self.code_rel = "app/limits.py"
        self.code_file = self.root / self.code_rel
        self.code_file.write_text("LEGAL_LIMIT = 42\n", encoding="utf-8")
        self.code_sha = rrc._sha256_lf(self.code_file)
        self.records_dir = self.root / "docs" / "research" / "evidence-records"
        self.records_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    def record(self) -> dict:
        return complete_record(self.code_rel, self.code_sha)

    def write(self, record: dict) -> Path:
        slug = record.get("record_id", "REC")
        path = self.records_dir / f"{slug}-case.json"
        path.write_text(json.dumps(record), encoding="utf-8")
        return path

    def run_check(self):
        return subprocess.run(
            [sys.executable, str(CHECKER), "--check", "--records-dir", str(self.records_dir)],
            capture_output=True, text=True)

    def path_for(self, record: dict) -> Path:
        return self.records_dir / f"{record.get('record_id', 'REC')}-case.json"


class CompleteRecord(Base):
    def test_complete_record_has_no_structural_errors(self):
        rec = self.record()
        self.assertEqual(rrc.validate_record(rec, self.path_for(rec), self.root), [])

    def test_check_passes_and_prints_disclaimer(self):
        self.write(self.record())
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("not a professional verification", r.stdout)

    def test_complete_record_promotion_blocked_only_by_c1(self):
        # MUTATION TARGET 1 (C1 refusal): evidence prerequisites are all met, yet the Verified
        # label is still refused — by exactly one reason, the open owner question C1.
        rec = self.record()
        refusals = rrc.promotion_refusals(OUTPUT, [(self.path_for(rec), rec)], self.root)
        self.assertEqual(refusals, [rrc.C1_REFUSAL])

    def test_derive_reports_current_and_code_current(self):
        rec = self.record()
        d = rrc.derive(rec, self.root)
        self.assertTrue(d["code_current"])
        self.assertEqual(d["review_state"], "current")


class PromotionRefusals(Base):
    def test_without_professional_review_refuses_prof_and_c1(self):
        rec = self.record()
        rec["review"]["professional_review"] = None
        refusals = rrc.promotion_refusals(OUTPUT, [(self.path_for(rec), rec)], self.root)
        self.assertTrue(any("professional review" in r for r in refusals), refusals)
        self.assertIn(rrc.C1_REFUSAL, refusals)

    def test_output_with_no_record_is_refused(self):
        rec = self.record()
        refusals = rrc.promotion_refusals("not.covered", [(self.path_for(rec), rec)], self.root)
        self.assertTrue(any("no evidence record covers" in r for r in refusals), refusals)

    def test_non_verified_known_label_never_refused(self):
        rec = self.record()
        for label in ("Conditional", "Provisional", "Illustrative", "Pending verification",
                      "Unresolved"):
            self.assertEqual(
                rrc.promotion_refusals(OUTPUT, [(self.path_for(rec), rec)], self.root, label),
                [], label)

    def test_unknown_label_is_refused(self):
        rec = self.record()
        refusals = rrc.promotion_refusals(OUTPUT, [(self.path_for(rec), rec)], self.root, "Golden")
        self.assertTrue(any("not a known report label" in r for r in refusals), refusals)

    def test_searched_not_found_refuses_promotion(self):
        rec = self.record()
        rec["conclusion"]["research_status"] = "searched_not_found"
        rec["searches"] = [{
            "source": "ACRIS", "query": "deed 215-16", "result": "not_found",
            "missing_item": "the recorded deed", "affected_outputs": [OUTPUT],
            "next_step": "order a title search",
        }]
        # structurally valid even though it is a dead end
        self.assertEqual(rrc.validate_record(rec, self.path_for(rec), self.root), [])
        refusals = rrc.promotion_refusals(OUTPUT, [(self.path_for(rec), rec)], self.root)
        self.assertTrue(any("searched_not_found" in r for r in refusals), refusals)


class Staleness(Base):
    def test_stale_record_refuses_promotion_but_check_still_passes(self):
        # MUTATION TARGET 2 (staleness): the linked code changes AFTER the review.
        rec = self.record()
        self.write(rec)
        self.code_file.write_text("LEGAL_LIMIT = 99  # changed after review\n", encoding="utf-8")
        d = rrc.derive(rec, self.root)
        self.assertFalse(d["code_current"])
        self.assertEqual(d["review_state"], "stale")
        refusals = rrc.promotion_refusals(OUTPUT, [(self.path_for(rec), rec)], self.root)
        self.assertTrue(any("stale" in r.lower() for r in refusals), refusals)
        # drift is REPORTED, not failed: nothing requests Verified, so --check still exits 0.
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("code_current=False", r.stdout)
        self.assertIn("NOTE", r.stdout)


class StructuralErrors(Base):
    def assertKeyError(self, rec, needle):
        errs = rrc.validate_record(rec, self.path_for(rec), self.root)
        self.assertTrue(any(needle in e for e in errs), f"{needle!r} not in {errs}")

    def test_missing_measurement_basis(self):
        rec = self.record()
        del rec["measurement_basis"]
        self.assertKeyError(rec, "measurement_basis")

    def test_empty_evidence_list(self):
        rec = self.record()
        rec["evidence"] = []
        self.assertKeyError(rec, "evidence")

    def test_incomplete_record_is_refused_promotion(self):
        rec = self.record()
        del rec["measurement_basis"]
        refusals = rrc.promotion_refusals(OUTPUT, [(self.path_for(rec), rec)], self.root)
        self.assertTrue(any("not structurally valid" in r for r in refusals), refusals)

    def test_conflicting_evidence_needs_conflicts(self):
        rec = self.record()
        rec["conclusion"]["research_status"] = "conflicting_evidence"
        rec["conclusion"]["conflicts"] = []
        self.assertKeyError(rec, "conflicting_evidence")

    def test_interpretation_awaiting_review_needs_interpretation(self):
        rec = self.record()
        rec["conclusion"]["research_status"] = "interpretation_awaiting_review"
        rec["conclusion"]["interpretation"] = ""
        self.assertKeyError(rec, "interpretation_awaiting_review")

    def test_searched_not_found_needs_matching_search(self):
        rec = self.record()
        rec["conclusion"]["research_status"] = "searched_not_found"
        rec["searches"] = []
        self.assertKeyError(rec, "searched_not_found")

    def test_access_blocked_needs_matching_search(self):
        rec = self.record()
        rec["conclusion"]["research_status"] = "access_blocked"
        rec["searches"] = [{
            "source": "ACRIS", "query": "x", "result": "found",
            "missing_item": "", "affected_outputs": [], "next_step": "",
        }]
        self.assertKeyError(rec, "access_blocked")

    def test_property_as_string_is_valid_and_empty_is_not(self):
        # [ORCH] the committed records name the property as one string (README); empty is refused.
        rec = self.record()
        rec["question"]["property"] = "215-16 Northern Boulevard, Queens (borough 4, block 7334, lot 70)"
        self.assertEqual(rrc.validate_record(rec, self.path_for(rec), self.root), [])
        rec["question"]["property"] = "  "
        self.assertKeyError(rec, "question.property")

    def test_reviewer_equals_producer(self):
        # MUTATION TARGET 3 (reviewer==producer): an agent review by the producer is invalid.
        rec = self.record()
        rec["review"]["agent_reviews"][0]["reviewer"] = rec["review"]["producer"]
        self.assertKeyError(rec, "must not equal the record producer")

    def test_saved_copy_sha_mismatch(self):
        snap = self.root / "evidence" / "snap.html"
        snap.parent.mkdir(parents=True)
        snap.write_text("<html>captured source</html>\n", encoding="utf-8")
        rec = self.record()
        rec["evidence"][0]["saved_copy"] = "evidence/snap.html"
        rec["evidence"][0]["sha256"] = "0" * 64  # deliberately wrong
        self.assertKeyError(rec, "sha256 does not match")

    def test_code_path_with_dotdot(self):
        rec = self.record()
        rec["implementation"]["code_paths"] = ["../outside.py"]
        rec["implementation"]["code_identity"] = {"../outside.py": "a" * 64}
        self.assertKeyError(rec, "must not contain '..'")

    def test_code_identity_keys_mismatch(self):
        rec = self.record()
        rec["implementation"]["code_identity"] = {"app/other.py": self.code_sha}
        self.assertKeyError(rec, "code_identity' keys must equal")

    def test_unknown_vocabulary_value(self):
        rec = self.record()
        rec["conclusion"]["research_status"] = "totally_made_up"
        self.assertKeyError(rec, "is not a known status")

    def test_filename_must_start_with_record_id(self):
        rec = self.record()
        wrong = self.records_dir / "WRONG-name.json"
        errs = rrc.validate_record(rec, wrong, self.root)
        self.assertTrue(any("must start with record_id" in e for e in errs), errs)


class CheckExitCodes(Base):
    def test_verified_request_exits_1(self):
        rec = self.record()
        rec["promotion"]["requested_label"] = "Verified"
        self.write(rec)
        r = self.run_check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn(rrc.C1_REFUSAL, r.stdout)

    def test_conditional_request_exits_0(self):
        rec = self.record()
        rec["promotion"]["requested_label"] = "Conditional"
        self.write(rec)
        r = self.run_check()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_empty_records_dir_exits_1(self):
        r = self.run_check()  # records_dir exists but holds no *.json
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("no *.json", r.stdout)

    def test_invalid_json_exits_2(self):
        (self.records_dir / "NB-bad.json").write_text("{ not valid json", encoding="utf-8")
        r = self.run_check()
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)

    def test_structural_error_exits_1(self):
        rec = self.record()
        del rec["measurement_basis"]
        self.write(rec)
        r = self.run_check()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("FAIL", r.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
