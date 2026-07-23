#!/usr/bin/env python3
"""Shared, read-only directive resolver for the Owner Directive Compliance System
(directive D-001, correction 1). Stdlib-only. NO write operations.

ONE interpretation, shared by BOTH consumers so they can never diverge:
  - tools/project_control.py     -> enforces claim/submit/accept lifecycle checks;
  - tools/validate_directive_compliance.py -> validates registry integrity.

Two-lane principle (D-001-R118): this module RESOLVES and VALIDATES references. It
never accepts a task, records a gate, or writes any file. All work-blocking decisions
still flow through project_control.py, blockers, holds and gates. A reference that is
nonexistent, malformed, withdrawn, superseded, or hash-invalid FAILS CLOSED.

Registry layout (project-control/directives/):
  index.json
  schema/v1/*.schema.json
  D-<nnn>-<slug>/{source-001.md, source-00N-amendment.md, manifest.json,
                 requirements.json, verification.json}
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTIVES_DIR = ROOT / "project-control" / "directives"

DIRECTIVE_ID_RE = re.compile(r"^D-\d{3}$")
REQUIREMENT_ID_RE = re.compile(r"^D-\d{3}-R\d{3}$")

# A reference is honored ONLY when its directive is in one of these states.
ACTIVE_STATES = frozenset({"active"})
# States that explicitly must fail closed when cited (distinct message).
DEAD_STATES = frozenset({"superseded", "withdrawn", "retired", "proposed"})

# Verification states that count as "resolved and satisfied at a given identity".
SATISFIED_STATE = "PASS"
UNRESOLVED_VERIFICATION_STATES = frozenset(
    {"pending", "FAIL", "BLOCKED", "UNVERIFIABLE"})


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Directive:
    """One directive's loaded records plus any integrity errors found on load."""

    def __init__(self, directive_id: str, dir_path: Path):
        self.directive_id = directive_id
        self.dir_path = dir_path
        self.manifest: dict = {}
        self.requirements: dict = {}
        self.verification: dict = {}
        self.index_entry: dict = {}
        self.errors: list[str] = []       # integrity problems (validator surfaces these)
        self.loaded = False

    @property
    def status(self) -> str:
        # Prefer the manifest lifecycle_state/status; fall back to the index entry.
        return (self.manifest.get("lifecycle_state")
                or self.manifest.get("status")
                or self.index_entry.get("status") or "")

    @property
    def is_active(self) -> bool:
        return self.status in ACTIVE_STATES and not self.errors

    def requirement_ids(self) -> set:
        return {r.get("id") for r in self.requirements.get("requirements", [])
                if r.get("id")}

    def requirement(self, req_id: str):
        for r in self.requirements.get("requirements", []):
            if r.get("id") == req_id:
                return r
        return None


class DirectiveRegistry:
    """Loads and resolves the directive registry. Read-only; fail-closed."""

    def __init__(self, directives_dir: Path = DIRECTIVES_DIR):
        self.dir = Path(directives_dir)
        self.index: dict = {}
        self.directives: dict[str, Directive] = {}
        self.errors: list[str] = []          # registry-level integrity errors
        self.exists = self.dir.exists()

    # ---- loading -------------------------------------------------------

    def load(self) -> "DirectiveRegistry":
        """Load the registry. Never raises on integrity problems: it records them in
        self.errors / directive.errors so the validator can report every one, and so
        resolve_* can fail closed. Only a hard filesystem/JSON parse error on the
        index is fatal (also recorded, leaving the registry empty)."""
        if not self.exists:
            return self
        idx = self.dir / "index.json"
        if not idx.exists():
            self.errors.append("index.json missing")
            return self
        try:
            self.index = _load_json(idx)
        except (ValueError, OSError) as e:
            self.errors.append(f"index.json unreadable/invalid JSON: {e}")
            return self
        if self.index.get("schema") != "directive_index/v1":
            self.errors.append(
                f"index.json schema is {self.index.get('schema')!r}, expected 'directive_index/v1'")
        seen = set()
        for entry in self.index.get("directives", []):
            did = entry.get("directive_id")
            if not did or not DIRECTIVE_ID_RE.match(did):
                self.errors.append(f"index entry has malformed directive_id {did!r}")
                continue
            if did in seen:
                self.errors.append(f"index lists directive {did} more than once")
                continue
            seen.add(did)
            manifest_rel = entry.get("manifest") or ""
            dpath = self.dir / manifest_rel
            d = Directive(did, dpath.parent)
            d.index_entry = entry
            self._load_directive(d, dpath)
            self.directives[did] = d
        return self

    def _load_directive(self, d: Directive, manifest_path: Path):
        if not manifest_path.exists():
            d.errors.append(f"{d.directive_id}: manifest not found at {manifest_path.name}")
            return
        try:
            d.manifest = _load_json(manifest_path)
        except (ValueError, OSError) as e:
            d.errors.append(f"{d.directive_id}: manifest unreadable/invalid JSON: {e}")
            return
        d.loaded = True
        # Verify source-file hashes (append-only integrity, correction 3 / D-001-R107).
        for src in d.manifest.get("sources", []):
            fpath = d.dir_path / src.get("file", "")
            declared = src.get("content_digest_sha256")
            if not fpath.exists():
                d.errors.append(f"{d.directive_id}: source file {src.get('file')!r} missing")
                continue
            actual = sha256_file(fpath)
            if actual != declared:
                d.errors.append(
                    f"{d.directive_id}: source {src.get('file')!r} digest mismatch "
                    f"(manifest {declared}, actual {actual}) -- silent rewrite of an "
                    f"active source is prohibited")
        # Load requirements + verification.
        rfile = d.dir_path / (d.manifest.get("requirements_file") or "requirements.json")
        vfile = d.dir_path / (d.manifest.get("verification_file") or "verification.json")
        if rfile.exists():
            try:
                d.requirements = _load_json(rfile)
            except (ValueError, OSError) as e:
                d.errors.append(f"{d.directive_id}: requirements.json invalid: {e}")
        else:
            d.errors.append(f"{d.directive_id}: requirements.json missing")
        if vfile.exists():
            try:
                d.verification = _load_json(vfile)
            except (ValueError, OSError) as e:
                d.errors.append(f"{d.directive_id}: verification.json invalid: {e}")
        else:
            d.errors.append(f"{d.directive_id}: verification.json missing")

    # ---- accessors -----------------------------------------------------

    def active_directives(self) -> list[Directive]:
        return [d for d in self.directives.values() if d.is_active]

    def get(self, directive_id: str):
        return self.directives.get(directive_id)

    # ---- applicability (D-001-R102/R103, correction 2) -----------------

    @staticmethod
    def _applicability_matches(applic: dict, task: dict) -> tuple[bool, str | None]:
        """Conjunction semantics: for every NON-EMPTY dimension the task must match;
        an empty dimension is a wildcard. Returns (matches, unresolved_reason).
        A malformed applicability object is UNRESOLVED (fail closed), never a silent
        match/non-match."""
        if not isinstance(applic, dict):
            return False, "applicability is missing or not an object"
        dims = ("task_ids", "task_types", "milestones", "paths", "lifecycle_events")
        for k in ("task_ids", "task_types", "milestones", "paths"):
            v = applic.get(k, [])
            if not isinstance(v, list):
                return False, f"applicability.{k} is not a list"
        tids = applic.get("task_ids") or []
        ttypes = applic.get("task_types") or []
        miles = applic.get("milestones") or []
        paths = applic.get("paths") or []
        if tids and task.get("task_id") not in tids:
            return False, None
        if ttypes and task.get("task_type") not in ttypes:
            return False, None
        if miles and task.get("milestone_id") not in miles:
            return False, None
        if paths:
            allowed = task.get("allowed_paths") or []
            if not any(_path_intersects(p, allowed) for p in paths):
                return False, None
        # Entirely-empty applicability is a legitimate "applies to everything" wildcard.
        return True, None

    def derive_applicable(self, task: dict) -> tuple[set, list[str]]:
        """Return (applicable_requirement_ids, unresolved_reasons) across ALL active
        directives. Unresolved reasons (malformed applicability, conflicting active
        directives) mean controlled work must BLOCK (D-001-R104), never silently choose."""
        applicable: set = set()
        unresolved: list[str] = []
        active = self.active_directives()
        # Conflict signal: a task citing/covered by a directive that is itself
        # superseded_by an active directive is ambiguous -> unresolved.
        for d in active:
            reqs = d.requirements.get("requirements", [])
            if not isinstance(reqs, list):
                unresolved.append(f"{d.directive_id}: requirements list malformed")
                continue
            for r in reqs:
                applic = r.get("applicability")
                matches, reason = self._applicability_matches(applic, task)
                if reason:
                    unresolved.append(f"{r.get('id')}: {reason}")
                    continue
                if matches:
                    applicable.add(r.get("id"))
        # Cross-directive conflict: two active directives both scope the same task_id
        # while one supersedes the other -> unresolved (must be owner-decided).
        for d in active:
            sup = d.manifest.get("superseded_by")
            if sup and sup in self.directives and self.directives[sup].is_active:
                if task.get("task_id") in (d.manifest.get("scope", {}).get("task_ids") or []):
                    unresolved.append(
                        f"{d.directive_id} is superseded_by active {sup}; scope for "
                        f"{task.get('task_id')} is ambiguous")
        return applicable, unresolved

    def covers_governance(self, task: dict) -> bool:
        """True iff the task cites an ACTIVE governance-scoped directive that actually
        covers it (task_id in scope.task_ids OR task_type in scope.task_types). Used by
        the CLI governance-path guard (s19 / D-001-R118): a task whose allowed_paths
        touch governance/control-plane files must cite such a directive."""
        tid = task.get("task_id")
        ttype = task.get("task_type")
        cited = {r.get("directive_id") for r in (task.get("directive_refs") or [])
                 if isinstance(r, dict)}
        for d in self.active_directives():
            if d.directive_id not in cited:
                continue
            scope = d.manifest.get("scope", {}) or {}
            if "governance" not in (scope.get("task_types") or []):
                continue
            if tid in (scope.get("task_ids") or []) or ttype in (scope.get("task_types") or []):
                return True
        return False

    # ---- reference evaluation (used by project_control.py) -------------

    def evaluate_task_refs(self, task: dict) -> dict:
        """Evaluate a task's directive_refs against the derived applicable set.

        directive_refs is a list of {"directive_id": "D-001",
        "requirement_ids": ["D-001-R001", ...] | "ALL"}.

        Returns a dict:
          ok: bool
          applicable_ids: sorted list
          cited_ids: sorted list
          missing_ids: applicable but not cited (selective-citation failure)
          invalid_refs: [reason strings]  (nonexistent/dead/hash-invalid/malformed)
          unresolved: [reason strings]     (block + require blocker/owner decision)
          reasons: [human-readable failure strings]  (empty iff ok)
        """
        applicable, unresolved = self.derive_applicable(task)
        cited: set = set()
        invalid: list[str] = []
        refs = task.get("directive_refs") or []
        if not isinstance(refs, list):
            invalid.append("directive_refs is not a list")
            refs = []
        for ref in refs:
            if not isinstance(ref, dict):
                invalid.append(f"directive_refs entry is not an object: {ref!r}")
                continue
            did = ref.get("directive_id")
            if not did or not DIRECTIVE_ID_RE.match(str(did)):
                invalid.append(f"malformed directive id in ref: {did!r}")
                continue
            d = self.directives.get(did)
            if d is None:
                invalid.append(f"cited directive {did} does not exist (fail closed)")
                continue
            if d.errors:
                invalid.append(
                    f"cited directive {did} has integrity errors "
                    f"(e.g. {d.errors[0]}); fail closed")
                continue
            if not d.is_active:
                invalid.append(
                    f"cited directive {did} is {d.status or 'unknown'!r}, not active "
                    f"(fail closed)")
                continue
            req_ids = ref.get("requirement_ids")
            if req_ids == "ALL":
                # Expand to the directive's requirements that are applicable to this task.
                for rid in d.requirement_ids():
                    if rid in applicable:
                        cited.add(rid)
            elif isinstance(req_ids, list):
                for rid in req_ids:
                    if not REQUIREMENT_ID_RE.match(str(rid)):
                        invalid.append(f"{did}: malformed requirement id {rid!r}")
                        continue
                    if d.requirement(rid) is None:
                        invalid.append(f"{did}: cited requirement {rid} does not exist")
                        continue
                    cited.add(rid)
            else:
                invalid.append(
                    f"{did}: requirement_ids must be a list or the string 'ALL', "
                    f"got {req_ids!r}")
        missing = sorted(applicable - cited)
        reasons: list[str] = []
        if invalid:
            reasons.extend(invalid)
        if unresolved:
            reasons.extend(
                f"unresolved scope (block + owner/blocker decision required): {u}"
                for u in unresolved)
        if missing:
            reasons.append(
                "selective citation: applicable requirement(s) not covered by "
                f"directive_refs: {', '.join(missing)}")
        if applicable and not refs:
            reasons.append(
                "task is in-regime with applicable requirements but cites no directive_refs")
        return {
            "ok": not reasons,
            "applicable_ids": sorted(applicable),
            "cited_ids": sorted(cited),
            "missing_ids": missing,
            "invalid_refs": invalid,
            "unresolved": unresolved,
            "reasons": reasons,
        }

    # ---- final-verification state (used by project_control.accept) -----

    def unresolved_requirements(self, directive_id: str, reviewed_manifest_sha256: str | None) -> list[str]:
        """Return reasons a directive is NOT fully verified at the given content
        identity. Empty list == every requirement PASS at that identity. Reads
        verification.json (the durable clean-context review record). This is used as
        EVIDENCE by accept(); acceptance authority still lives in accept()."""
        d = self.directives.get(directive_id)
        if d is None:
            return [f"directive {directive_id} not found"]
        if d.errors:
            return [f"directive {directive_id} integrity error: {d.errors[0]}"]
        v = d.verification
        if not v:
            return [f"{directive_id}: no verification.json"]
        producer = (v.get("producer") or d.requirements.get("producer") or "").strip()
        verifier = (v.get("verifier") or "").strip()
        reasons: list[str] = []
        if not verifier:
            reasons.append(f"{directive_id}: no independent verifier recorded")
        elif producer and verifier == producer:
            reasons.append(
                f"{directive_id}: verifier {verifier!r} equals producer "
                f"{producer!r}; independent verification required")
        vsha = v.get("reviewed_manifest_sha256")
        if reviewed_manifest_sha256 is not None and vsha != reviewed_manifest_sha256:
            reasons.append(
                f"{directive_id}: verification is stale -- recorded at content "
                f"identity {vsha}, current is {reviewed_manifest_sha256}")
        req_ids = d.requirement_ids()
        ver_states = {r.get("id"): r.get("state") for r in v.get("requirements", [])}
        missing_rows = sorted(req_ids - set(ver_states))
        if missing_rows:
            reasons.append(
                f"{directive_id}: verification missing rows for {', '.join(missing_rows)}")
        for rid in sorted(req_ids):
            st = ver_states.get(rid)
            if st == "NOT_APPLICABLE":
                row = next((r for r in v.get("requirements", []) if r.get("id") == rid), {})
                if not row.get("not_applicable_justification") or not row.get("not_applicable_approved_by"):
                    reasons.append(f"{rid}: NOT_APPLICABLE without justification + independent approver")
                continue
            if st != SATISFIED_STATE:
                reasons.append(f"{rid}: verification state {st!r} (not PASS)")
        return reasons


def _path_intersects(scope_path: str, allowed_paths: list) -> bool:
    """True if any allowed path is under (or equal to) scope_path, or vice-versa.
    Directory scopes end with '/'; both prefixes are checked so a file scope and a
    directory allowed-path still intersect sensibly."""
    sp = scope_path.rstrip("/")
    for a in allowed_paths:
        ap = str(a).rstrip("/")
        if ap == sp or ap.startswith(sp + "/") or sp.startswith(ap + "/"):
            return True
    return False


def content_manifest(paths: list, root: Path = ROOT, exclude_prefixes: tuple = ()) -> str:
    """Path-scoped content identity (D-001-R110, correction 5). Deterministic SHA-256
    over the sorted (relpath, file-content-hash) of every existing file under `paths`
    (files or directory trees). Because it hashes CONTENT, not a commit, it is stable
    across merge/rebase/squash when the relevant contents are identical, and it changes
    whenever any relevant file's content changes. Nonexistent paths are skipped.

    Any file whose repo-relative posix path starts with one of `exclude_prefixes` is
    omitted. The CLI passes the volatile control-plane prefix so the identity guards the
    reviewable code/doc work product and does not churn on lifecycle bookkeeping (task
    status, gate/report records, verification.json) — registry integrity is separately
    enforced by tools/validate_directive_compliance.py."""
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for p in sorted(str(x) for x in paths):
        base = (root / p)
        if base.is_file():
            files = [base]
        elif base.is_dir():
            files = [f for f in sorted(base.rglob("*")) if f.is_file()]
        else:
            continue
        for f in files:
            try:
                rel = f.resolve().relative_to(root.resolve()).as_posix()
            except ValueError:
                rel = f.as_posix()
            if rel in seen or any(rel.startswith(pre) for pre in exclude_prefixes):
                continue
            seen.add(rel)
            entries.append((rel, sha256_file(f)))
    entries.sort()
    h = hashlib.sha256()
    for rel, digest in entries:
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(digest.encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def load_registry(directives_dir: Path = DIRECTIVES_DIR) -> DirectiveRegistry:
    return DirectiveRegistry(directives_dir).load()


if __name__ == "__main__":  # pragma: no cover - manual inspection helper
    import sys
    reg = load_registry()
    out = {
        "exists": reg.exists,
        "registry_errors": reg.errors,
        "directives": {
            did: {"status": d.status, "active": d.is_active,
                  "requirements": len(d.requirement_ids()), "errors": d.errors}
            for did, d in reg.directives.items()
        },
    }
    print(json.dumps(out, indent=2))
    sys.exit(0 if not reg.errors and all(not d.errors for d in reg.directives.values()) else 1)
