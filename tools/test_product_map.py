#!/usr/bin/env python3
"""Unit tests for tools/validate_product_map.py and the real product-map.json.

Stdlib-only (unittest); runnable as `python3 tools/test_product_map.py` so the
control-plane CI job can execute it exactly like test_project_control.py.
Positive test validates the REAL committed product-map.json against the REAL
ledger; negative tests use synthetic in-memory fixtures so they never touch the
committed files.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import validate_product_map as vpm  # noqa: E402


def _min_pm():
    """A minimal, valid two-system product map over a synthetic 2-task ledger."""
    return {
        "version": 1,
        "progress_model": {"engineering_completion": "x", "launch_readiness": "y"},
        "owner_status_vocabulary": {"accepted": "ACCEPTED"},
        "systems": [
            {"id": "sys_a", "name": "A", "owner_purpose": "p", "owner_why": "w",
             "eng_weight": 60, "launch_weight": 70, "planned_count": 1,
             "milestones": ["M0"]},
            {"id": "sys_b", "name": "B", "owner_purpose": "p", "owner_why": "w",
             "eng_weight": 40, "launch_weight": 30, "planned_count": 1,
             "milestones": ["M1"]},
        ],
        "architect_journey": [{"step": 0, "label": "s", "systems": ["sys_a"]}],
    }


SYNTH_TASKS = {"M0-T001": "M0", "M1-T001": "M1"}
SYNTH_MS = {"M0", "M1"}


class RealProductMap(unittest.TestCase):
    def test_real_product_map_is_valid(self):
        pm = vpm.load_product_map()
        tasks = vpm.load_ledger_tasks()
        milestones = set()
        if vpm.MASTER_PLAN.exists():
            import json
            mp = json.loads(vpm.MASTER_PLAN.read_text(encoding="utf-8-sig"))
            milestones = {m.get("id") for m in mp.get("milestones", []) if m.get("id")}
        errors = vpm.validate(pm, tasks, milestones, vpm._known_blockers())
        self.assertEqual(errors, [], f"real product-map.json should be valid; got: {errors}")

    def test_every_real_task_maps_exactly_once(self):
        pm = vpm.load_product_map()
        tasks = vpm.load_ledger_tasks()
        membership = vpm.resolve_membership(pm, tasks)
        counts = {t: 0 for t in tasks}
        for ts in membership.values():
            for t in ts:
                if t in counts:
                    counts[t] += 1
        self.assertTrue(all(c == 1 for c in counts.values()),
                        f"tasks not mapped exactly once: "
                        f"{[t for t, c in counts.items() if c != 1]}")

    def test_weight_totals_are_100(self):
        pm = vpm.load_product_map()
        self.assertEqual(sum(s["eng_weight"] for s in pm["systems"]), 100)
        self.assertEqual(sum(s["launch_weight"] for s in pm["systems"]), 100)


class NegativeCases(unittest.TestCase):
    def test_valid_synthetic_passes(self):
        self.assertEqual(vpm.validate(_min_pm(), SYNTH_TASKS, SYNTH_MS), [])

    def test_eng_weight_not_100_fails(self):
        pm = _min_pm()
        pm["systems"][0]["eng_weight"] = 59  # totals 99
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("eng_weight" in e and "100" in e for e in errs), errs)

    def test_launch_weight_not_100_fails(self):
        pm = _min_pm()
        pm["systems"][1]["launch_weight"] = 31  # totals 101
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("launch_weight" in e and "100" in e for e in errs), errs)

    def test_orphan_task_fails(self):
        # A ledger task no system covers (belongs to milestone M2, unmapped).
        tasks = dict(SYNTH_TASKS, **{"M2-T009": "M2"})
        errs = vpm.validate(_min_pm(), tasks, SYNTH_MS | {"M2"})
        self.assertTrue(any("NO system" in e for e in errs), errs)

    def test_double_mapped_task_fails(self):
        pm = _min_pm()
        pm["systems"][1]["tasks_include"] = ["M0-T001"]  # also in sys_a via M0
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("MULTIPLE systems" in e for e in errs), errs)

    def test_dangling_include_fails(self):
        pm = _min_pm()
        pm["systems"][0]["tasks_include"] = ["M9-T999"]
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("unknown task M9-T999" in e for e in errs), errs)

    def test_unknown_milestone_fails(self):
        pm = _min_pm()
        pm["systems"][0]["milestones"] = ["M0", "M8"]
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("M8 not in master_plan" in e for e in errs), errs)

    def test_journey_unknown_system_fails(self):
        pm = _min_pm()
        pm["architect_journey"][0]["systems"] = ["sys_ghost"]
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("unknown system 'sys_ghost'" in e for e in errs), errs)

    def test_duplicate_system_id_fails(self):
        pm = _min_pm()
        pm["systems"][1]["id"] = "sys_a"
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("duplicate system id" in e for e in errs), errs)

    def test_task_override_unknown_fails(self):
        pm = _min_pm()
        pm["task_overrides"] = {"M9-T999": {"owner_title": "x", "owner_description": "y"}}
        errs = vpm.validate(pm, SYNTH_TASKS, SYNTH_MS)
        self.assertTrue(any("task_overrides" in e and "M9-T999" in e for e in errs), errs)


if __name__ == "__main__":
    unittest.main(verbosity=2)
