#!/usr/bin/env python3
"""M0-T069 Unit F tests: promotion benchmark (corpus, cases, honest report).

Runnable as ``python tools/test_context_benchmark.py`` or under pytest.
The full 5-shape report is exercised once by the orchestrator to produce the
committed benchmark evidence; these tests keep CI-viable runtime by running
one full shape end-to-end plus report-structure checks over two shapes.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)
sys.path.insert(0, _ROOT)

from tools import context_benchmark as cb  # noqa: E402


class AS1ShapeAndCases(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.shape = cb.run_shape("cross_module_change", samples=1)
        cls.rows = {r["case"]: r for r in cls.shape["rows"]}

    def test_all_r056_cases_present(self) -> None:
        self.assertEqual(
            set(self.rows),
            {"cold_build", "warm_no_change", "one_file_change",
             "dependency_change", "rename", "delete",
             "corrupt_cache_recovery", "interrupted_write_recovery",
             "concurrent_writer", "parser_version_change"})

    def test_parser_version_case_is_distinct_and_documented(self) -> None:
        # M0-T075 (D-018-R043): the parser-version bump must force a FULL
        # rebuild through the real global-invalidator path, byte-identical.
        row = self.rows["parser_version_change"]
        self.assertTrue(row["parser_version_full_rebuild"])
        self.assertTrue(row["byte_identical"])
        self.assertIn("parser_probe", row["rebuild_reason"])

    def test_every_case_byte_identical_to_clean_full(self) -> None:
        for case, row in self.rows.items():
            self.assertTrue(row["byte_identical"], case)

    def test_warm_no_change_reparses_zero(self) -> None:
        self.assertTrue(self.rows["warm_no_change"]["zero_reparse"])
        self.assertEqual(self.rows["warm_no_change"]["files_parsed"], 0)

    def test_local_and_dependency_changes_stay_incremental(self) -> None:
        self.assertTrue(self.rows["one_file_change"]["no_full_rebuild"])
        self.assertTrue(self.rows["dependency_change"]["no_full_rebuild"])

    def test_rename_delete_leave_no_stale_nodes(self) -> None:
        self.assertFalse(self.rows["rename"]["stale_nodes"])
        self.assertFalse(self.rows["delete"]["stale_nodes"])

    def test_recovery_and_concurrency(self) -> None:
        self.assertTrue(self.rows["interrupted_write_recovery"]["orphan_quarantined"])
        self.assertTrue(self.rows["concurrent_writer"]["lock_refused"])

    def test_corpus_manifest_and_baseline_recorded(self) -> None:
        self.assertEqual(len(self.shape["corpus_manifest_digest"]), 64)
        self.assertTrue(self.shape["baseline_export_digest"])
        self.assertTrue(self.shape["census_reconciles"])


class AS3AS4ReportHonesty(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # Two shapes only for runtime; the committed report runs all five.
        saved = dict(cb.SHAPES)
        cb.SHAPES = {k: saved[k] for k in
                     ("single_file_bug", "control_plane_only")}
        try:
            cls.report = cb.build_report(samples=2)
        finally:
            cb.SHAPES = saved

    def test_method_statement_and_order(self) -> None:
        self.assertIn("SAME snapshot", self.report["method"])
        self.assertIn("confound", self.report["method"])
        self.assertTrue(self.report["correctness_first"])

    def test_promotion_evidence_r059_all_true(self) -> None:
        for key, val in self.report["promotion_evidence_R059"].items():
            self.assertTrue(val, key)

    def test_timings_carry_samples_median_p95_and_label(self) -> None:
        mr = self.report["measured_runtime"]
        self.assertIn("never byte-identity content", mr["label"])
        stats = mr["per_shape"]["single_file_bug"]["warm_no_change"]
        self.assertEqual(stats["samples"], 2)
        self.assertIsNotNone(stats["median"])
        self.assertIsNotNone(stats["p95"])

    def test_provider_savings_unmeasured_and_no_combined_number(self) -> None:
        eff = self.report["efficiency"]
        self.assertIn("UNMEASURED", eff["provider_token_savings"])
        self.assertNotIn("savings_percent", str(self.report))
        self.assertNotIn("token_savings_total", str(self.report))

    def test_thresholds_proposed_with_rationale_decision_pending(self) -> None:
        tp = self.report["threshold_proposal"]
        self.assertTrue(tp["proposed_before_owner_decision"])
        for t in tp["thresholds"]:
            self.assertTrue(t["rationale"])
        self.assertIn("PENDING owner/control-plane decision",
                      self.report["promotion_decision"])

    def test_markdown_renders_from_report(self) -> None:
        md = cb.render_md(self.report)
        self.assertIn("## Promotion evidence", md)
        self.assertIn("PENDING owner/control-plane decision", md)
        self.assertIn("single_file_bug", md)

    def test_control_plane_only_change_is_non_eligible(self) -> None:
        rows = [r for r in self.report["correctness"]
                if r["shape"] == "control_plane_only"]
        cases = {r["case"] for r in rows}
        self.assertIn("non_eligible_change", cases)
        non = [r for r in rows if r["case"] == "non_eligible_change"][0]
        self.assertTrue(non["byte_identical"])


class P95Correction(unittest.TestCase):
    def test_p95_nearest_rank(self) -> None:
        # M0-T075 (D-018-R045): nearest-rank p95, not the old median-at-small-n.
        s = cb._stats([1.0, 2.0, 3.0])
        self.assertEqual(s["p95"], 3.0)   # was 2.0 (median) before the fix
        self.assertEqual(s["median"], 2.0)
        s20 = cb._stats([float(i) for i in range(1, 21)])
        self.assertEqual(s20["p95"], 19.0)  # ceil(0.95*20)-1 = rank 18 -> 19.0
        self.assertEqual(cb._stats([])["p95"], None)


class EvidencePredicates(unittest.TestCase):
    def test_lock_orphan_parser_folded_into_evidence(self) -> None:
        # M0-T075 (D-018-R044): actual refusal/quarantine + the parser case
        # are PASS predicates; absence of the case fails the predicate.
        saved = dict(cb.SHAPES)
        cb.SHAPES = {"single_file_bug": saved["single_file_bug"]}
        try:
            report = cb.build_report(samples=1)
        finally:
            cb.SHAPES = saved
        ev = report["promotion_evidence_R059"]
        self.assertTrue(ev["lock_refusal_enforced"])
        self.assertTrue(ev["orphan_temp_quarantined"])
        self.assertTrue(ev["parser_version_change_documented_full_rebuild"])


class E2ESingleShape(unittest.TestCase):
    def test_e2e_regime_shape_end_to_end(self) -> None:
        # Bounded CI-viable slice of the e2e corpus: the in-regime shape
        # proves requirement texts, excerpts, determinism, split refusal,
        # and enforceable insufficiency through the ACTUAL compiler.
        row = cb._e2e_shape("single_file_bug")
        self.assertEqual(row["exit_cold"], 0)
        self.assertTrue(row["cold_warm_byte_identical"])
        self.assertTrue(row["within_budget"])
        self.assertTrue(row["sufficient"])
        self.assertTrue(row["provenance_complete"])
        self.assertTrue(row["requirement_ids_present"])
        self.assertTrue(row["requirements_group_present"])
        self.assertTrue(row["source_excerpt_present"])
        self.assertTrue(row["graph_or_source_evidence_resolved"])
        self.assertEqual(row["tiny_budget_split_exit"], 2)
        self.assertEqual(row["reviewer_insufficiency_exit"], 3)


class DeterministicCorpus(unittest.TestCase):
    def test_corpus_manifest_digest_deterministic(self) -> None:
        digests = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as root:
                cb.build_corpus_shape("schema_change", root)
                digests.append(cb.corpus_manifest_digest(root))
        self.assertEqual(digests[0], digests[1])


class D019FrozenBaseline(unittest.TestCase):
    """M0-T076 / D-019-R035/R036: the e2e baseline comparison is a frozen,
    state-invariant required-evidence comparison, not a source-id count."""

    def test_no_worse_compares_required_evidence_not_counts(self) -> None:
        base = {"exit_cold": 0, "sufficient": True, "provenance_complete": True,
                "graph_or_source_evidence_resolved": True,
                "source_excerpt_present": True, "memory_status_honest": True,
                "within_budget": True, "requirement_ids_present": True,
                "requirements_group_present": True}
        ok, regs = cb._fingerprint_no_worse(base, dict(base))
        self.assertTrue(ok)
        self.assertEqual(regs, [])
        # a real regression is caught: sufficiency lost, or exit regressed
        worse = dict(base, sufficient=False)
        ok2, regs2 = cb._fingerprint_no_worse(base, worse)
        self.assertFalse(ok2)
        self.assertTrue(any("sufficient" in r for r in regs2))
        ok3, _ = cb._fingerprint_no_worse(base, dict(base, exit_cold=3))
        self.assertFalse(ok3)
        # relevance identity: a changed requirement signal is a regression
        ok4, regs4 = cb._fingerprint_no_worse(base, dict(base, requirement_ids_present=False))
        self.assertFalse(ok4)

    def test_capture_and_compare_roundtrip_no_worse(self) -> None:
        baseline = cb.capture_e2e_baseline()
        self.assertEqual(baseline["schema"], cb.E2E_BASELINE_SCHEMA)
        self.assertEqual(set(baseline["shapes"]), set(cb.SHAPES))
        with tempfile.TemporaryDirectory() as d:
            bpath = os.path.join(d, "baseline.json")
            with open(bpath, "wb") as fh:
                fh.write(cb.canon_json_bytes(baseline))
            report = cb.build_e2e_report(bpath)
            bc = report["baseline_comparison"]
            self.assertEqual(bc["status"], "compared")
            self.assertTrue(bc["no_worse_than_baseline"])
            self.assertIn("required-evidence", bc["comparison_basis"])

    def test_committed_baseline_is_valid_schema(self) -> None:
        import json as _json
        path = os.path.join(_ROOT, "project-control", "reports",
                            "M0-T076-baseline-g0.json")
        with open(path, encoding="utf-8") as fh:
            base = _json.load(fh)
        self.assertEqual(base["schema"], cb.E2E_BASELINE_SCHEMA)
        self.assertEqual(set(base["shapes"]), set(cb.SHAPES))
        self.assertIn("UNMEASURED", base["provider_token_savings"])


if __name__ == "__main__":
    unittest.main()
