#!/usr/bin/env python3
"""Deterministic, read-only validator for the Owner Directive Compliance registry
(directive D-001). Stdlib-only. Shares tools/directive_registry.py with
tools/project_control.py so the CLI and the validator can never diverge (correction 1).

Exit 0 = valid, 1 = one or more errors. Read-only: writes nothing.

Checks (D-001-R048 c1..c16 plus correction-specific integrity):
  c1  schemas + unique IDs                 c9  baseline/head SHA presence
  c2  source hashes                        c10 stale verification after source/head change
  c3  append-only amendment history        c11 no unsupported NOT_APPLICABLE
  c4  source-anchor coverage               c12 no acceptance with unresolved items
  c5  valid task/PR references             c13 no narrative 'complete' replacing atomic statuses
  c6  applicable-task requirement refs     c14 no silent requirement disappearance via supersession
  c7  producer/verifier separation         c15 no retroactive mutation of accepted packets
  c8  evidence-path existence              c16 safe handling of multiple simultaneous directives
  + manifest/requirement required keys, applicability presence, directive-state vocabulary,
    locked-requirement-id append-only, requirements<->verification id-set equality.

Usage:
  python tools/validate_directive_compliance.py            # human report, exit 0/1
  python tools/validate_directive_compliance.py --check    # quiet on success
  python tools/validate_directive_compliance.py --json     # machine-readable
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import directive_registry as dr  # noqa: E402  (shared resolver)

ROOT = Path(__file__).resolve().parents[1]
PC = ROOT / "project-control"
DIRECTIVES_DIR = PC / "directives"
TASKS_DIR = PC / "tasks"

DIRECTIVE_STATES = {"proposed", "active", "superseded", "withdrawn", "retired"}
REQUIREMENT_STATUSES = {"pending", "implemented", "PASS", "FAIL", "BLOCKED",
                        "UNVERIFIABLE", "NOT_APPLICABLE"}
VERIFICATION_STATES = {"pending", "PASS", "FAIL", "BLOCKED", "UNVERIFIABLE", "NOT_APPLICABLE"}
UNRESOLVED_VERIFICATION = {"pending", "FAIL", "BLOCKED", "UNVERIFIABLE"}
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")

MANIFEST_REQUIRED = ("schema", "directive_id", "version", "status", "captured_at",
                     "frozen_baseline_sha", "sources", "affected_tasks", "affected_prs",
                     "scope", "owner_approval", "lifecycle_state", "requirements_file",
                     "verification_file", "amendments", "audit_log")
REQUIREMENT_REQUIRED = ("id", "text", "source_ref", "classification", "applicability",
                        "dependencies", "required_harness", "required_evidence",
                        "producer", "independent_verifier", "status", "status_reason",
                        "evidence_paths", "reviewed_sha", "maps_to")


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _ledger_task_ids(tasks_dir: Path) -> set:
    out = set()
    if not tasks_dir.exists():
        return out
    for p in tasks_dir.glob("*.json"):
        try:
            out.add(_load_json(p).get("task_id") or p.stem)
        except (ValueError, OSError):
            continue
    return out


def _ledger_task_status(tasks_dir: Path, task_id: str) -> str | None:
    p = tasks_dir / f"{task_id}.json"
    if not p.exists():
        return None
    try:
        return _load_json(p).get("status")
    except (ValueError, OSError):
        return None


def _validate_v1_verification(w, m, v, req_ids, req_producer, completion_claimed):
    """v1 single-task verification cross-checks (c7/c8/c10/c11/c12/c13/c14)."""
    errors = []
    ver_rows = {vr.get("id"): vr for vr in v.get("requirements", [])}
    rset, vset = req_ids, set(ver_rows)
    if rset - vset:
        errors.append(f"c14 {w} verification.json missing rows for {', '.join(sorted(rset - vset))}")
    if vset - rset:
        errors.append(f"c14 {w} verification.json has rows with no requirement: {', '.join(sorted(vset - rset))}")
    producer = (v.get("producer") or req_producer or "").strip()
    verifier = (v.get("verifier") or "").strip()
    if verifier and producer and verifier == producer:
        errors.append(f"c7 {w} verifier {verifier!r} equals producer {producer!r}")
    for vid, vr in ver_rows.items():
        if vr.get("state") not in VERIFICATION_STATES:
            errors.append(f"c1 {w} verification row {vid} state {vr.get('state')!r} invalid")
        if vr.get("state") == "NOT_APPLICABLE":
            if not vr.get("not_applicable_justification") or not vr.get("not_applicable_approved_by"):
                errors.append(f"c11 {w} {vid} NOT_APPLICABLE without justification + independent approver")
        if vr.get("state") == "PASS" and not (vr.get("evidence") or []):
            errors.append(f"c8 {w} {vid} verification PASS without evidence")
    vsha = v.get("reviewed_manifest_sha256")
    msha = m.get("final_reviewed_manifest_sha256")
    if vsha is not None and msha is not None and vsha != msha:
        errors.append(f"c10 {w} verification content-identity {vsha} != manifest final identity {msha} (stale)")
    unresolved_rows = [vid for vid, vr in ver_rows.items() if vr.get("state") in UNRESOLVED_VERIFICATION]
    if completion_claimed and unresolved_rows:
        errors.append(f"c12/c13 {w} completion claimed while {len(unresolved_rows)} verification row(s) unresolved")
    return errors


def _validate_v2_verification(w, did, m, v, req_ids, req_producer, completion_claimed, tasks_dir):
    """v2 multi-task verification cross-checks (D-001 amendment 3, Section 2). Each
    task_verifications[] entry is checked in isolation: cross-directive contamination,
    duplicate task rows, per-task producer/verifier separation, applicable-id validity and
    subset-ness, no extra/cross-task requirement rows, PASS-needs-evidence, justified
    NOT_APPLICABLE, and content-identity format. Missing/duplicate/extra/cross-task rows
    are integrity errors here and fail closed at accept()."""
    errors = []
    tvs = v.get("task_verifications")
    if not isinstance(tvs, list):
        return [f"c1 {w} v2 verification missing task_verifications[] array"]
    seen_tasks = set()
    total_unresolved = 0
    covered = set()
    for tv in tvs:
        tid = tv.get("task_id")
        tw = f"{w} {tid}"
        if tv.get("directive_id") != did:
            errors.append(f"c16 {tw} task_verification directive_id {tv.get('directive_id')!r} != {did} (cross-directive contamination)")
        if not dr.re.match(r"^M\d+-T\d{3}(-R\d+)?$", str(tid or "")):
            errors.append(f"c5 {tw} task_verification has malformed task_id")
            continue
        if tid in seen_tasks:
            errors.append(f"c16 {tw} duplicate task_verification for the same task (fail closed)")
        seen_tasks.add(tid)
        covered.add(tid)
        producer = (tv.get("producer") or v.get("producer") or req_producer or "").strip()
        verifier = (tv.get("verifier") or "").strip()
        if verifier and producer and verifier == producer:
            errors.append(f"c7 {tw} verifier {verifier!r} equals producer {producer!r} (per-task separation)")
        applic = tv.get("applicable_requirement_ids") or []
        for rid in applic:
            if not dr.REQUIREMENT_ID_RE.match(str(rid)):
                errors.append(f"c1 {tw} malformed applicable requirement id {rid!r}")
            elif rid not in req_ids:
                errors.append(f"c6 {tw} applicable id {rid} is not a requirement of {did}")
        applic_set = set(applic)
        rows = {}
        for r in tv.get("requirements", []):
            rid = r.get("id")
            if rid in rows:
                errors.append(f"c16 {tw} duplicate verification row {rid}")
            rows[rid] = r
        extra = sorted(set(rows) - applic_set)
        if extra:
            errors.append(f"c16 {tw} verification rows outside this task's applicable set (extra/cross-task): {', '.join(extra)}")
        missing = sorted(applic_set - set(rows))
        if missing:
            errors.append(f"c14 {tw} verification missing rows for applicable requirement(s): {', '.join(missing)}")
        for rid, r in rows.items():
            st = r.get("state")
            if st not in VERIFICATION_STATES:
                errors.append(f"c1 {tw} verification row {rid} state {st!r} invalid")
            if st == "NOT_APPLICABLE" and (not r.get("not_applicable_justification") or not r.get("not_applicable_approved_by")):
                errors.append(f"c11 {tw} {rid} NOT_APPLICABLE without justification + independent approver")
            if st == "PASS" and not (r.get("evidence") or []):
                errors.append(f"c8 {tw} {rid} verification PASS without evidence")
            if st in UNRESOLVED_VERIFICATION:
                total_unresolved += 1
        vsha = tv.get("reviewed_manifest_sha256")
        if vsha is not None and not SHA64.match(str(vsha)):
            errors.append(f"c10 {tw} reviewed_manifest_sha256 present but not a 64-hex sha")
        rsha = tv.get("reviewed_sha")
        if rsha is not None and not SHA40.match(str(rsha)):
            errors.append(f"c9 {tw} reviewed_sha present but not a 40-hex sha")
    for t in m.get("affected_tasks", []):
        tp = tasks_dir / f"{t}.json"
        if not tp.exists():
            continue
        try:
            task = _load_json(tp)
        except (ValueError, OSError):
            continue
        if task.get("directive_regime_version") and t not in covered:
            errors.append(f"c14 {w} in-regime affected task {t} has no task_verification row")
    msha = m.get("final_reviewed_manifest_sha256")
    primary = (m.get("affected_tasks") or [None])[0]
    if msha is not None and primary is not None:
        ptv = next((x for x in tvs if x.get("task_id") == primary), None)
        if ptv is not None and ptv.get("reviewed_manifest_sha256") not in (None, msha):
            errors.append(f"c10 {w} manifest final identity {msha} != primary task {primary} verification identity {ptv.get('reviewed_manifest_sha256')} (stale)")
    if completion_claimed and total_unresolved:
        errors.append(f"c12/c13 {w} completion claimed while {total_unresolved} verification row(s) unresolved")
    return errors


def _validate_migration_manifest(registry_root: Path, active_directives) -> list:
    """Integrity of the immutable migration manifest (D-001 amendment 3, Section 1):
    schema, 40-hex baseline sha, well-formed unique task entries with 64-hex material
    digests, and the append-only content lock -- the manifest's content hash MUST equal
    the migration_manifest_sha256 recorded in a governing active directive's manifest, so
    the legacy list cannot silently grow without an owner amendment."""
    errors = []
    mm_path = registry_root / "migration_manifest.json"
    if not mm_path.exists():
        return ["mig migration_manifest.json missing (regime enforcement needs the frozen baseline list)"]
    try:
        mm = _load_json(mm_path)
    except (ValueError, OSError) as e:
        return [f"mig migration_manifest.json unreadable/invalid JSON: {e}"]
    if mm.get("schema") != "directive_migration/v1":
        errors.append(f"mig schema {mm.get('schema')!r} != 'directive_migration/v1'")
    if not SHA40.match(str(mm.get("frozen_baseline_sha", ""))):
        errors.append("mig frozen_baseline_sha missing or not a 40-hex sha")
    seen = set()
    for t in mm.get("tasks", []):
        tid = t.get("task_id")
        dig = t.get("material_digest")
        if not dr.re.match(r"^M\d+-T\d{3}(-R\d+)?$", str(tid or "")):
            errors.append(f"mig task_id {tid!r} malformed")
            continue
        if not SHA64.match(str(dig or "")):
            errors.append(f"mig {tid} material_digest missing or not a 64-hex sha")
        if tid in seen:
            errors.append(f"mig {tid} listed more than once")
        seen.add(tid)
    recorded = None
    for d in active_directives:
        rec = d.manifest.get("migration_manifest_sha256")
        if rec:
            recorded = rec
            actual = hashlib.sha256(mm_path.read_bytes()).hexdigest()
            if actual != recorded:
                errors.append(f"mig content hash {actual[:12]}.. != {d.directive_id} "
                              f"manifest.migration_manifest_sha256 {str(recorded)[:12]}.. "
                              f"(the frozen legacy list changed without an owner amendment)")
    if recorded is None:
        errors.append("mig no active directive records migration_manifest_sha256 "
                      "(the frozen legacy list would be unprotected)")
    return errors


def validate(registry_root: Path = DIRECTIVES_DIR, tasks_dir: Path = TASKS_DIR) -> list:
    """Return a list of human-readable error strings ([] == valid)."""
    errors: list = []
    reg = dr.DirectiveRegistry(registry_root).load()

    if not reg.exists:
        return [f"directives registry not found at {registry_root}"]
    # c1 index schema
    if reg.index.get("schema") != "directive_index/v1":
        errors.append(f"c1 index.json schema {reg.index.get('schema')!r} != 'directive_index/v1'")
    # registry-level errors (index parse, dup ids)
    for e in reg.errors:
        errors.append(f"c1/registry: {e}")

    ledger = _ledger_task_ids(tasks_dir)
    schema_dir = registry_root / "schema" / "v1"
    for name in ("directive_index", "directive_manifest", "directive_requirements",
                 "directive_verification"):
        if not (schema_dir / f"{name}.schema.json").exists():
            errors.append(f"c1 versioned schema missing: schema/v1/{name}.schema.json")
    # v2 multi-task verification schema (D-001 amendment 3, Section 2).
    if not (registry_root / "schema" / "v2" / "directive_verification.schema.json").exists():
        errors.append("c1 versioned schema missing: schema/v2/directive_verification.schema.json")
    # Immutable migration manifest integrity + append-only content lock (Section 1).
    errors.extend(_validate_migration_manifest(registry_root, reg.active_directives()))

    # c16: multiple directives are handled independently; iterate each.
    active_ids = [d.directive_id for d in reg.active_directives()]
    for did, d in sorted(reg.directives.items()):
        w = f"[{did}]"
        # c2 source hashes + structural load errors surfaced by the resolver
        for e in d.errors:
            errors.append(f"c2 {w} {e}")
        if not d.loaded:
            continue
        m = d.manifest

        # ---- manifest required keys (D-001-R020) ----
        for k in MANIFEST_REQUIRED:
            if k not in m:
                errors.append(f"{w} manifest missing required key '{k}'")
        # c9 baseline/head SHA presence
        if not SHA40.match(str(m.get("frozen_baseline_sha", ""))):
            errors.append(f"c9 {w} frozen_baseline_sha missing or not a 40-hex sha")
        if "final_reviewed_sha" not in m:
            errors.append(f"c9 {w} manifest missing 'final_reviewed_sha' key (may be null)")
        frs = m.get("final_reviewed_sha")
        if frs is not None and not SHA40.match(str(frs)):
            errors.append(f"c9 {w} final_reviewed_sha set but not a 40-hex sha: {frs!r}")

        # c1 status vocabulary (directive states, D-001-R105)
        if m.get("status") not in DIRECTIVE_STATES:
            errors.append(f"c1 {w} manifest status {m.get('status')!r} not in {sorted(DIRECTIVE_STATES)}")
        if m.get("lifecycle_state") not in DIRECTIVE_STATES:
            errors.append(f"c1 {w} lifecycle_state {m.get('lifecycle_state')!r} not in {sorted(DIRECTIVE_STATES)}")
        if "state" not in (m.get("owner_approval") or {}):
            errors.append(f"{w} owner_approval.state missing")

        # ---- c3 append-only amendment history ----
        srcs = m.get("sources", [])
        seqs = [s.get("sequence") for s in srcs]
        if seqs != list(range(1, len(srcs) + 1)):
            errors.append(f"c3 {w} source sequences {seqs} are not contiguous 1..N")
        if srcs and srcs[0].get("kind") != "original":
            errors.append(f"c3 {w} first source must be kind 'original'")
        for s in srcs[1:]:
            if s.get("kind") != "amendment":
                errors.append(f"c3 {w} source {s.get('file')!r} after the original must be an amendment")
            if not s.get("amends"):
                errors.append(f"c3 {w} amendment {s.get('file')!r} missing 'amends' pointer")
        amend_files = {s.get("file") for s in srcs if s.get("kind") == "amendment"}
        if set(m.get("amendments", [])) != amend_files:
            errors.append(f"c3 {w} manifest.amendments {m.get('amendments')} != amendment source files {sorted(amend_files)}")

        reqs = d.requirements.get("requirements", [])
        req_ids = [r.get("id") for r in reqs]
        # c1 unique requirement ids
        if len(req_ids) != len(set(req_ids)):
            errors.append(f"c1 {w} duplicate requirement id(s)")
        src_files = {s.get("file") for s in srcs}

        for r in reqs:
            rid = r.get("id")
            rw = f"{w} {rid}"
            for k in REQUIREMENT_REQUIRED:
                if k not in r:
                    errors.append(f"{rw} missing required key '{k}'")
            if not dr.REQUIREMENT_ID_RE.match(str(rid or "")):
                errors.append(f"c1 {rw} malformed requirement id")
            # applicability presence (D-001-R102)
            applic = r.get("applicability")
            if not isinstance(applic, dict):
                errors.append(f"{rw} applicability missing/not an object")
            else:
                for ak in ("task_ids", "task_types", "milestones", "paths",
                           "lifecycle_events", "effective_date"):
                    if ak not in applic:
                        errors.append(f"{rw} applicability missing '{ak}'")
            # c4 source-anchor coverage
            sref = str(r.get("source_ref") or "")
            anchor_file = sref.split("#", 1)[0].strip()
            if not anchor_file:
                errors.append(f"c4 {rw} source_ref has no source file")
            elif anchor_file not in src_files:
                errors.append(f"c4 {rw} source_ref {sref!r} names {anchor_file!r} which is not a registered source")
            if "#" not in sref:
                errors.append(f"c4 {rw} source_ref {sref!r} has no anchor")
            # c1 classification / status vocab
            if r.get("classification") not in {
                    "obligation", "prohibition", "hold", "sequencing", "dependency",
                    "decision", "harness", "evidence", "external_fact", "return", "authorization"}:
                errors.append(f"c1 {rw} unknown classification {r.get('classification')!r}")
            if r.get("status") not in REQUIREMENT_STATUSES:
                errors.append(f"c1 {rw} status {r.get('status')!r} not in {sorted(REQUIREMENT_STATUSES)}")
            # c5 maps_to.tasks valid ids
            for t in (r.get("maps_to", {}).get("tasks") or []):
                if not dr.re.match(r"^M\d+-T\d{3}(-R\d+)?$", str(t)):
                    errors.append(f"c5 {rw} maps_to.task {t!r} is not a valid task id")
            # c8 evidence-path existence (only when the producer claims progress)
            if r.get("status") in ("implemented", "PASS"):
                ev = r.get("evidence_paths") or []
                if not ev:
                    errors.append(f"c8 {rw} status {r.get('status')} but no evidence_paths")
                for ep in ev:
                    if not (ROOT / ep).exists():
                        errors.append(f"c8 {rw} evidence path does not exist: {ep}")
            # c11 no unsupported NOT_APPLICABLE
            if r.get("status") == "NOT_APPLICABLE" and not r.get("not_applicable_justification"):
                errors.append(f"c11 {rw} NOT_APPLICABLE without not_applicable_justification")

        # ---- c14 no silent disappearance via supersession (append-only ids) ----
        locked = m.get("locked_requirement_ids")
        if locked is None:
            errors.append(f"c14 {w} manifest missing locked_requirement_ids (append-only baseline)")
        else:
            missing = sorted(set(locked) - set(req_ids))
            if missing:
                errors.append(f"c14 {w} locked requirement id(s) deleted from requirements.json: {', '.join(missing)}")
            declared = m.get("requirements_id_digest_sha256")
            actual = hashlib.sha256("\n".join(sorted(req_ids)).encode()).hexdigest()
            if declared and declared != actual:
                errors.append(f"c14 {w} requirements_id_digest mismatch: manifest {declared[:12]}.. actual {actual[:12]}.. (added/removed/renumbered id without amendment)")
        # c14 requirements BODY integrity: the frozen content-manifest excludes the
        # control-plane tree, so the reviewed matrix body (each row's text/evidence/
        # classification) is protected here instead. Any edit to requirements.json after
        # activation changes this digest -> a visible, CI-caught failure.
        rfile_path = d.dir_path / (m.get("requirements_file") or "requirements.json")
        declared_body = m.get("requirements_content_digest_sha256")
        if not declared_body:
            errors.append(f"c14 {w} manifest missing requirements_content_digest_sha256 "
                          f"(the reviewed requirement bodies would be unprotected)")
        elif rfile_path.exists():
            actual_body = hashlib.sha256(rfile_path.read_bytes()).hexdigest()
            if actual_body != declared_body:
                errors.append(f"c14 {w} requirements.json content digest mismatch "
                              f"(manifest {declared_body[:12]}.. actual {actual_body[:12]}..): "
                              f"a requirement body was edited without a recorded amendment")

        # ---- c7/c10/c11/c12/c13 verification cross-checks (schema-aware) ----
        v = d.verification
        completion_claimed = bool(m.get("complete") or m.get("all_addressed")
                                  or str(m.get("owner_approval", {}).get("state", "")).lower() in ("complete", "accepted"))
        if m.get("complete") is not None or m.get("all_addressed") is not None:
            errors.append(f"c13 {w} manifest carries a narrative completion flag; per-requirement atomic states are the only completion signal")
        req_producer = (d.requirements.get("producer") or "").strip()
        if v.get("schema") == "directive_verification/v2":
            errors.extend(_validate_v2_verification(
                w, did, m, v, set(req_ids), req_producer, completion_claimed, tasks_dir))
        else:
            errors.extend(_validate_v1_verification(
                w, m, v, set(req_ids), req_producer, completion_claimed))

        # ---- c5 affected task/PR references ----
        for t in m.get("affected_tasks", []):
            if not dr.re.match(r"^M\d+-T\d{3}(-R\d+)?$", str(t)):
                errors.append(f"c5 {w} affected_task {t!r} malformed")
            elif ledger and t not in ledger:
                errors.append(f"c5 {w} affected_task {t} not found in ledger")
        for pr in m.get("affected_prs", []):
            if not isinstance(pr, (int, str)):
                errors.append(f"c5 {w} affected_pr {pr!r} not an int/str")

        # ---- c15 no retroactive mutation of accepted packets ----
        # A directive may legitimately scope a task that later reaches its own terminal
        # `accepted` state (the bootstrap case: D-001 scopes M0-T023, which is accepted
        # only at its own completion). That is NOT a retroactive mutation. What c15
        # guards is a directive RETROACTIVELY binding an already-accepted task that never
        # consented — an accepted task in scope whose packet does not cite this directive.
        # (Mere presence is fine; the CLI's terminal-state guards enforce immutability.)
        for t in (m.get("scope", {}).get("task_ids") or []):
            if _ledger_task_status(tasks_dir, t) != "accepted":
                continue
            tp = tasks_dir / f"{t}.json"
            cites = False
            if tp.exists():
                try:
                    trefs = _load_json(tp).get("directive_refs") or []
                    cites = any(isinstance(r, dict) and r.get("directive_id") == did
                                for r in trefs)
                except (ValueError, OSError):
                    cites = False
            if not cites:
                errors.append(f"c15 {w} scope includes accepted task {t} that does not cite "
                              f"{did}; a directive may not retroactively bind an "
                              f"already-accepted task")

        # ---- c6 applicable-task requirement references ----
        # For each in-regime affected task that exists, the task must cite the directive
        # and cover its applicable requirements (no selective citation).
        for t in m.get("affected_tasks", []):
            tp = tasks_dir / f"{t}.json"
            if not tp.exists():
                continue
            try:
                task = _load_json(tp)
            except (ValueError, OSError):
                continue
            if not task.get("directive_regime_version"):
                continue  # grandfathered / not in-regime -> not required to cite
            ev = reg.evaluate_task_refs(task)
            if not ev["ok"]:
                errors.append(f"c6 {w} in-regime task {t} fails reference coverage: {'; '.join(ev['reasons'][:2])}")

    return errors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Validate the Owner Directive Compliance registry (D-001).")
    ap.add_argument("--check", action="store_true", help="quiet on success")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--registry", default=str(DIRECTIVES_DIR), help="registry root (default project-control/directives)")
    ap.add_argument("--tasks", default=str(TASKS_DIR), help="ledger tasks dir")
    a = ap.parse_args(argv)

    errors = validate(Path(a.registry), Path(a.tasks))
    if a.json:
        print(json.dumps({"valid": not errors, "error_count": len(errors), "errors": errors}, indent=2))
        return 0 if not errors else 1
    if errors:
        print(f"directive registry INVALID ({len(errors)} error(s)):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    if not a.check:
        reg = dr.load_registry(Path(a.registry))
        print(f"directive registry OK: {len(reg.directives)} directive(s), "
              f"{len(reg.active_directives())} active; source hashes, ID append-only, "
              f"and producer/verifier separation verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
