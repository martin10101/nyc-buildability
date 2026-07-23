#!/usr/bin/env python3
"""Validate project-control/product-map.json (M0-T022, owner dashboard).

Stdlib-only. This is the control-plane integrity gate for the ONE new metadata
file the owner dashboard adds. It enforces the invariants a JSON Schema cannot:

  1. Structural shape (required keys, types, weight ranges, unique system ids).
  2. eng_weight and launch_weight each sum to exactly 100 across systems.
  3. Every ledger task (project-control/tasks/*.json) maps to EXACTLY ONE system
     (no orphan, no double-count) under the canonical membership rule below.
  4. Every referenced id resolves: tasks_include/tasks_exclude and task_overrides
     keys are real ledger tasks; system.milestones exist in master_plan;
     journey.systems and readiness_cap.on_task resolve.

Canonical membership rule (mirrored by the TypeScript engine in
apps/web/src/lib/dashboard so both compute identical numbers):

    membership(system) = ({ tasks whose milestone_id is in system.milestones }
                          - system.tasks_exclude) | system.tasks_include

Usage:
    python tools/validate_product_map.py            # human report, exit 0/1
    python tools/validate_product_map.py --check     # same, quiet on success
    python tools/validate_product_map.py --json      # machine-readable report

Exit code 0 = valid, 1 = one or more errors.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PC = ROOT / "project-control"
PRODUCT_MAP = PC / "product-map.json"
SCHEMA = PC / "product-map.schema.json"
TASKS_DIR = PC / "tasks"
MASTER_PLAN = PC / "master_plan.json"
BLOCKERS_DIR = PC / "blockers"

TASK_ID = __import__("re").compile(r"^M\d+-T\d{3}(-R\d+)?$")
MILESTONE_ID = __import__("re").compile(r"^M\d+$")


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def load_product_map(path: Path = PRODUCT_MAP) -> dict:
    return _load(path)


def load_ledger_tasks(tasks_dir: Path = TASKS_DIR) -> dict:
    """Return {task_id: milestone_id} for every task file in the ledger."""
    out = {}
    for p in sorted(tasks_dir.glob("*.json")):
        try:
            t = _load(p)
        except (ValueError, OSError):
            continue
        tid = t.get("task_id") or p.stem
        ms = t.get("milestone_id") or (tid.split("-", 1)[0] if "-" in tid else "")
        out[tid] = ms
    return out


def resolve_membership(pm: dict, task_milestones: dict) -> dict:
    """Return {system_id: set(task_ids)} under the canonical membership rule."""
    membership = {}
    for s in pm.get("systems", []):
        sid = s.get("id")
        ms = set(s.get("milestones") or [])
        include = set(s.get("tasks_include") or [])
        exclude = set(s.get("tasks_exclude") or [])
        from_ms = {t for t, m in task_milestones.items() if m in ms}
        # Unknown includes are kept so a dangling include is caught by the
        # reference-existence check rather than being silently dropped here.
        membership[sid] = (from_ms - exclude) | include
    return membership


def _known_blockers(blockers_dir: Path = BLOCKERS_DIR) -> set:
    out = set()
    if not blockers_dir.exists():
        return out
    for p in blockers_dir.glob("*.json"):
        try:
            b = _load(p)
        except (ValueError, OSError):
            continue
        if b.get("blocker_id"):
            out.add(b["blocker_id"])
    return out


def validate(pm: dict, task_milestones: dict, milestones: set,
             blockers: set | None = None) -> list:
    """Return a list of human-readable error strings ([] means valid)."""
    errors: list = []
    blockers = blockers if blockers is not None else set()

    systems = pm.get("systems")
    if not isinstance(systems, list) or not systems:
        errors.append("systems: must be a non-empty array")
        return errors

    # ---- structural per-system checks + weight accumulation ----
    ids: list = []
    eng_total = 0.0
    launch_total = 0.0
    required = ("id", "name", "owner_purpose", "owner_why",
                "eng_weight", "launch_weight", "planned_count")
    for i, s in enumerate(systems):
        where = f"systems[{i}]"
        if not isinstance(s, dict):
            errors.append(f"{where}: must be an object")
            continue
        for k in required:
            if k not in s:
                errors.append(f"{where}: missing required field '{k}'")
        sid = s.get("id", f"<index {i}>")
        ids.append(s.get("id"))
        for wk in ("eng_weight", "launch_weight"):
            v = s.get(wk)
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                errors.append(f"{where} ({sid}): {wk} must be a number")
            elif not (0 <= v <= 100):
                errors.append(f"{where} ({sid}): {wk}={v} out of range 0..100")
        pc = s.get("planned_count")
        if not isinstance(pc, int) or isinstance(pc, bool) or pc < 0:
            errors.append(f"{where} ({sid}): planned_count must be an integer >= 0")
        if isinstance(s.get("eng_weight"), (int, float)) and not isinstance(s.get("eng_weight"), bool):
            eng_total += s["eng_weight"]
        if isinstance(s.get("launch_weight"), (int, float)) and not isinstance(s.get("launch_weight"), bool):
            launch_total += s["launch_weight"]
        # referenced milestones must exist
        for m in (s.get("milestones") or []):
            if not MILESTONE_ID.match(str(m)):
                errors.append(f"{where} ({sid}): malformed milestone id {m!r}")
            elif milestones and m not in milestones:
                errors.append(f"{where} ({sid}): milestone {m} not in master_plan")
        # include/exclude ids must be real tasks
        for key in ("tasks_include", "tasks_exclude"):
            for t in (s.get(key) or []):
                if not TASK_ID.match(str(t)):
                    errors.append(f"{where} ({sid}): {key} has malformed task id {t!r}")
                elif t not in task_milestones:
                    errors.append(f"{where} ({sid}): {key} references unknown task {t}")
        cap = s.get("readiness_cap")
        if cap is not None:
            ot = cap.get("on_task")
            if ot and ot not in task_milestones:
                errors.append(f"{where} ({sid}): readiness_cap.on_task references unknown task {ot}")

    # ---- unique system ids ----
    seen = set()
    for sid in ids:
        if sid in seen:
            errors.append(f"systems: duplicate system id {sid!r}")
        seen.add(sid)
    valid_ids = {i for i in ids if i}

    # ---- weight sums (integer weights => exact; tolerate float noise) ----
    if abs(eng_total - 100.0) > 1e-9:
        errors.append(f"eng_weight across systems must sum to 100, got {eng_total:g}")
    if abs(launch_total - 100.0) > 1e-9:
        errors.append(f"launch_weight across systems must sum to 100, got {launch_total:g}")

    # ---- every ledger task maps to EXACTLY ONE system ----
    membership = resolve_membership(pm, task_milestones)
    counts = {t: 0 for t in task_milestones}
    for sid, tasks in membership.items():
        for t in tasks:
            if t in counts:
                counts[t] += 1
    orphans = sorted(t for t, c in counts.items() if c == 0)
    doubles = sorted(t for t, c in counts.items() if c > 1)
    if orphans:
        errors.append(f"{len(orphans)} ledger task(s) map to NO system: {', '.join(orphans)}")
    if doubles:
        detail = []
        for t in doubles:
            owners = [sid for sid, ts in membership.items() if t in ts]
            detail.append(f"{t} -> {owners}")
        errors.append(f"{len(doubles)} ledger task(s) map to MULTIPLE systems: {'; '.join(detail)}")

    # ---- journey references ----
    for j in pm.get("architect_journey", []):
        for sref in (j.get("systems") or []):
            if sref not in valid_ids:
                errors.append(f"architect_journey step {j.get('step')}: unknown system {sref!r}")

    # ---- task_overrides keys must be real tasks ----
    for tid in (pm.get("task_overrides") or {}):
        if tid not in task_milestones:
            errors.append(f"task_overrides: references unknown task {tid}")

    # ---- blocker_labels keys should be real blockers (warn-as-error only if known set provided) ----
    if blockers:
        for bid in (pm.get("blocker_labels") or {}):
            if bid not in blockers:
                errors.append(f"blocker_labels: references unknown blocker {bid}")

    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate project-control/product-map.json")
    ap.add_argument("--check", action="store_true", help="quiet on success")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    a = ap.parse_args(argv)

    if not PRODUCT_MAP.exists():
        print(f"product-map.json not found at {PRODUCT_MAP}", file=sys.stderr)
        return 1
    try:
        pm = load_product_map()
    except ValueError as e:
        print(f"product-map.json is not valid JSON: {e}", file=sys.stderr)
        return 1
    if not SCHEMA.exists():
        print(f"product-map.schema.json not found at {SCHEMA}", file=sys.stderr)
        return 1
    try:
        _load(SCHEMA)
    except ValueError as e:
        print(f"product-map.schema.json is not valid JSON: {e}", file=sys.stderr)
        return 1

    task_milestones = load_ledger_tasks()
    milestones = set()
    if MASTER_PLAN.exists():
        try:
            mp = _load(MASTER_PLAN)
            milestones = {m.get("id") for m in mp.get("milestones", []) if m.get("id")}
        except ValueError:
            pass

    errors = validate(pm, task_milestones, milestones, _known_blockers())

    if a.json:
        print(json.dumps({"valid": not errors, "error_count": len(errors),
                          "errors": errors, "task_count": len(task_milestones),
                          "system_count": len(pm.get("systems", []))}, indent=2))
        return 0 if not errors else 1

    if errors:
        print(f"product-map.json INVALID ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    if not a.check:
        print(f"product-map.json OK: {len(pm.get('systems', []))} systems, "
              f"{len(task_milestones)} ledger tasks, all mapped exactly once; "
              f"eng_weight and launch_weight each sum to 100.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
