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
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIRECTIVES_DIR = ROOT / "project-control" / "directives"
MIGRATION_MANIFEST_PATH = DIRECTIVES_DIR / "migration_manifest.json"

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


def _within(child: Path, parent: Path) -> bool:
    """True iff `child` resolves to a path inside `parent` (path-containment guard,
    defense-in-depth). A '../' or absolute registry-internal path value therefore
    cannot point outside the directives tree; callers fail closed on False."""
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except (ValueError, OSError):
        return False


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
            if not _within(dpath, self.dir):
                self.errors.append(f"index entry {did} manifest path escapes the registry: {manifest_rel!r}")
                continue
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
            if not _within(fpath, d.dir_path):
                d.errors.append(f"{d.directive_id}: source path {src.get('file')!r} escapes the directive dir")
                continue
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

    # ---- per-task verification (D-001 amendment 3, Section 2) ----------

    def task_unresolved_requirements(self, directive_id: str, task_id: str,
                                     applicable_ids, reviewed_manifest_sha256: str | None) -> list[str]:
        """Reasons a SPECIFIC (directive, task) pair is NOT fully verified at the given
        content identity. Empty list == every requirement APPLICABLE TO THIS TASK is
        PASS at that identity, by an independent verifier, in a well-formed row.

        This is the multi-task replacement for unresolved_requirements(): one directive
        may govern several tasks, each with its own allowed paths, content identity,
        evidence, and reviewer. Only the requirements applicable to *this* task are
        evaluated for *this* task's acceptance ('ALL' means all-applicable-to-this-task).

        Supports verification.json schema directive_verification/v2 (task_verifications[])
        and falls back to the v1 single-task shape for legacy/other directives. Missing,
        duplicate, extra, cross-task, or stale rows FAIL CLOSED."""
        d = self.directives.get(directive_id)
        if d is None:
            return [f"directive {directive_id} not found"]
        if d.errors:
            return [f"directive {directive_id} integrity error: {d.errors[0]}"]
        v = d.verification
        if not v:
            return [f"{directive_id}: no verification.json"]
        applicable = set(applicable_ids or [])
        schema = v.get("schema")
        if schema == "directive_verification/v2":
            return self._v2_task_unresolved(d, v, directive_id, task_id, applicable,
                                            reviewed_manifest_sha256)
        # v1 back-compat: a single flat requirements[] shape scoped to one task. Evaluate
        # ONLY the requirements applicable to this task (owner correction: not every
        # requirement belonging to the directive).
        return self._v1_task_unresolved(d, v, directive_id, applicable,
                                         reviewed_manifest_sha256)

    def _v2_task_unresolved(self, d, v, directive_id, task_id, applicable,
                            reviewed_manifest_sha256):
        rows_all = v.get("task_verifications")
        if not isinstance(rows_all, list):
            return [f"{directive_id}: v2 verification missing task_verifications[] (fail closed)"]
        matches = [tv for tv in rows_all if isinstance(tv, dict)
                   and tv.get("task_id") == task_id
                   and tv.get("directive_id", directive_id) == directive_id]
        if not matches:
            return [f"{directive_id}/{task_id}: no task_verification row (fail closed)"]
        if len(matches) > 1:
            return [f"{directive_id}/{task_id}: duplicate task_verification rows "
                    f"({len(matches)}) (fail closed)"]
        tv = matches[0]
        reasons: list[str] = []
        producer = (tv.get("producer") or v.get("producer")
                    or d.requirements.get("producer") or "").strip()
        verifier = (tv.get("verifier") or "").strip()
        if not verifier:
            reasons.append(f"{directive_id}/{task_id}: no independent verifier recorded")
        elif producer and verifier == producer:
            reasons.append(f"{directive_id}/{task_id}: verifier {verifier!r} equals producer "
                           f"{producer!r}; independent verification required")
        vsha = tv.get("reviewed_manifest_sha256")
        if reviewed_manifest_sha256 is not None and vsha != reviewed_manifest_sha256:
            reasons.append(f"{directive_id}/{task_id}: verification is stale -- recorded at "
                           f"content identity {vsha}, current is {reviewed_manifest_sha256}")
        rows = {}
        for r in tv.get("requirements", []):
            rid = r.get("id")
            if rid in rows:
                reasons.append(f"{directive_id}/{task_id}: duplicate verification row {rid}")
            rows[rid] = r
        # cross-task / extra rows: a verification row for a requirement NOT applicable to
        # this task is contamination -> fail closed.
        extra = sorted(set(rows) - applicable)
        if extra:
            reasons.append(f"{directive_id}/{task_id}: verification has non-applicable "
                           f"(extra/cross-task) rows: {', '.join(extra)}")
        # the row's declared applicable set (if present) must equal the derived set.
        declared = tv.get("applicable_requirement_ids")
        if declared is not None and set(declared) != applicable:
            reasons.append(f"{directive_id}/{task_id}: recorded applicable_requirement_ids do "
                           f"not equal the derived applicable set (fail closed)")
        missing = sorted(applicable - set(rows))
        if missing:
            reasons.append(f"{directive_id}/{task_id}: verification missing rows for "
                           f"{', '.join(missing)}")
        for rid in sorted(applicable):
            r = rows.get(rid)
            if r is None:
                continue  # already reported missing
            st = r.get("state")
            if st == "NOT_APPLICABLE":
                if not r.get("not_applicable_justification") or not r.get("not_applicable_approved_by"):
                    reasons.append(f"{rid}: NOT_APPLICABLE without justification + independent approver")
                continue
            if st != SATISFIED_STATE:
                reasons.append(f"{rid}: verification state {st!r} (not PASS)")
        return reasons

    def _v1_task_unresolved(self, d, v, directive_id, applicable, reviewed_manifest_sha256):
        producer = (v.get("producer") or d.requirements.get("producer") or "").strip()
        verifier = (v.get("verifier") or "").strip()
        reasons: list[str] = []
        if not verifier:
            reasons.append(f"{directive_id}: no independent verifier recorded")
        elif producer and verifier == producer:
            reasons.append(f"{directive_id}: verifier {verifier!r} equals producer "
                           f"{producer!r}; independent verification required")
        vsha = v.get("reviewed_manifest_sha256")
        if reviewed_manifest_sha256 is not None and vsha != reviewed_manifest_sha256:
            reasons.append(f"{directive_id}: verification is stale -- recorded at content "
                           f"identity {vsha}, current is {reviewed_manifest_sha256}")
        ver_states = {r.get("id"): r for r in v.get("requirements", [])}
        missing_rows = sorted(applicable - set(ver_states))
        if missing_rows:
            reasons.append(f"{directive_id}: verification missing rows for {', '.join(missing_rows)}")
        for rid in sorted(applicable):
            row = ver_states.get(rid)
            if row is None:
                continue
            st = row.get("state")
            if st == "NOT_APPLICABLE":
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
    """LEGACY, NON-AUTHORITATIVE working-tree content identity. Superseded by
    frozen_git_identity()/git_tree_manifest() (D-001 amendment 3, Section 3): the
    AUTHORITATIVE reviewed identity is derived from canonical tracked GIT content at a
    reviewed commit, NOT from raw working-tree bytes (a LF-vs-CRLF checkout would change
    this hash even when the canonical git content is identical). The CLI no longer calls
    this for submit/gate/accept; it is retained only for legacy order-independence tests.

    Deterministic SHA-256 over the sorted (relpath, file-content-hash) of every existing
    file under `paths` (files or directory trees). Because it hashes CONTENT, not a commit,
    it is stable across merge/rebase/squash when the relevant contents are identical, and it
    changes whenever any relevant file's content changes. Nonexistent paths are skipped.

    Any file whose repo-relative posix path starts with one of `exclude_prefixes` is
    omitted. The CLI passes the volatile control-plane prefix so the identity guards the
    reviewable code/doc work product and does not churn on lifecycle bookkeeping (task
    status, gate/report records, verification.json) — registry integrity is separately
    enforced by tools/validate_directive_compliance.py."""
    entries: list[tuple[str, str]] = []
    seen: set[str] = set()
    for p in sorted(str(x) for x in paths):
        base = (root / p)
        if not _within(base, root):
            continue  # a '../'/absolute allowed_path can never pull in files outside root
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


# ==========================================================================
# Git-canonical content identity (D-001 amendment 3, Section 3).
#
# The AUTHORITATIVE reviewed content identity is derived from CANONICAL TRACKED
# GIT CONTENT at a specific reviewed commit -- NOT from raw working-tree bytes.
# Each entry is (repo-relative path, file mode, git object type, git object id).
# Because the identity is the git blob/object id (content-addressed canonical
# stored content), it is:
#   * cross-platform: a LF-vs-CRLF checkout difference cannot change it when the
#     canonical git content is identical (checkout eol conversion touches the
#     working tree, never the stored blob);
#   * byte-exact for binary content (blob id hashes the exact stored bytes);
#   * mode-sensitive (100644 file / 100755 exec / 120000 symlink / 160000
#     submodule-gitlink are distinct);
#   * stable across merge, rebase, and squash (identical blobs -> identical ids
#     regardless of commit graph);
#   * invalidated by any relevant content or file-mode change.
# Submission, independent gates, and acceptance all consume this ONE shared
# implementation (D-001-R152). Relevant untracked/dirty files fail CLOSED
# (D-001-R149) rather than being silently omitted.
# ==========================================================================

SHA40_RE = re.compile(r"^[0-9a-f]{40}$")


def _run_git(root: Path, args: list) -> tuple:
    """Run `git -C root <args>` capturing bytes. Returns (stdout_bytes, error_or_None).
    A non-zero exit or an unavailable git binary is a fail-closed error, never a
    silent empty result."""
    try:
        proc = subprocess.run(["git", "-C", str(root), *args],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (OSError, ValueError) as e:
        return None, f"git unavailable: {e}"
    if proc.returncode != 0:
        msg = proc.stderr.decode("utf-8", "replace").strip() or f"git exited {proc.returncode}"
        return None, msg
    return proc.stdout, None


def git_work_tree_root(root: Path) -> tuple:
    """Return (repo_top_or_None, error). Fails closed when `root` is not inside a git
    work tree."""
    out, err = _run_git(root, ["rev-parse", "--show-toplevel"])
    if err is not None:
        return None, f"not a git work tree: {err}"
    return out.decode("utf-8").strip(), None


def resolve_commit(root: Path, sha: str | None) -> tuple:
    """Validate that `sha` (or HEAD when falsy) resolves to a commit object. Returns
    (full_40hex_sha, error). Peels tags to commits."""
    rev = f"{sha}^{{commit}}" if sha else "HEAD^{commit}"
    out, err = _run_git(root, ["rev-parse", "--verify", "--quiet", rev])
    if err is not None or not out.strip():
        return None, (f"cannot resolve reviewed commit {sha or 'HEAD'!r} to a commit object "
                      f"(fail closed)")
    full = out.decode("utf-8").strip()
    if not SHA40_RE.match(full):
        return None, f"resolved commit {full!r} is not a 40-hex sha (fail closed)"
    return full, None


def git_tree_manifest(root: Path, commit: str, paths: list,
                      exclude_prefixes: tuple = ()) -> tuple:
    """Deterministic SHA-256 over sorted (relpath, mode, type, object-id) for every
    tracked object at `commit` under `paths` (files or directory trees; `-r` expands
    directories, gitlinks appear as type 'commit'). Returns (identity_hex, entries,
    error)."""
    entries: list = []
    seen: set = set()
    for p in paths:
        pp = str(p).strip().rstrip("/")
        if not pp:
            continue
        out, err = _run_git(root, ["ls-tree", "-r", "-z", "--full-tree", commit, "--", pp])
        if err is not None:
            return None, None, f"git ls-tree failed for {pp!r}: {err}"
        for rec in out.split(b"\x00"):
            if not rec:
                continue
            meta, sep, path_b = rec.partition(b"\t")
            if not sep:
                return None, None, f"unparseable ls-tree record: {rec!r}"
            try:
                mode, gtype, obj = meta.decode("utf-8").split()
            except ValueError:
                return None, None, f"unparseable ls-tree meta: {meta!r}"
            rel = path_b.decode("utf-8")
            if rel in seen or any(rel.startswith(pre) for pre in exclude_prefixes):
                continue
            seen.add(rel)
            entries.append((rel, mode, gtype, obj))
    entries.sort()
    h = hashlib.sha256()
    for rel, mode, gtype, obj in entries:
        h.update(rel.encode("utf-8")); h.update(b"\0")
        h.update(mode.encode("ascii")); h.update(b"\0")
        h.update(gtype.encode("ascii")); h.update(b"\0")
        h.update(obj.encode("ascii")); h.update(b"\n")
    return h.hexdigest(), entries, None


def relevant_working_tree_dirty(root: Path, paths: list,
                                exclude_prefixes: tuple = ()) -> tuple:
    """Return (dirty_entries, error). dirty_entries is a list of (xy_status, path) for
    any tracked file under `paths` that is modified/staged/deleted OR any untracked file
    under `paths`, excluding exclude_prefixes. A non-empty list is the fail-closed signal
    that the working tree does not match committed content for the relevant scope."""
    args = ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--"]
    args += [str(p) for p in paths if str(p).strip()]
    out, err = _run_git(root, args)
    if err is not None:
        return None, f"git status failed: {err}"
    dirty: list = []
    tokens = out.split(b"\x00")
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if not tok:
            i += 1
            continue
        xy = tok[:2].decode("utf-8", "replace")
        path = tok[3:].decode("utf-8", "replace")
        # rename/copy records carry the origin path in the following NUL field.
        if xy[:1] in ("R", "C"):
            i += 1
        if not any(path.startswith(pre) for pre in exclude_prefixes):
            dirty.append((xy, path))
        i += 1
    return dirty, None


def frozen_git_identity(paths: list, reviewed_sha: str | None = None,
                        root: Path = ROOT, exclude_prefixes: tuple = (),
                        require_clean: bool = True) -> tuple:
    """The authoritative git-canonical reviewed content identity for a task's paths.
    Returns (identity_hex, resolved_commit_sha, error). Fails closed (error != None) when:
      * `root` is not a git work tree / git is unavailable;
      * reviewed_sha (or HEAD) does not resolve to a commit;
      * require_clean and a relevant tracked file is dirty or a relevant file is untracked.
    An empty relevant set (all paths under exclude_prefixes or absent at the commit)
    yields the deterministic empty-set hash, not an error -- untracked/dirty relevant
    files are caught by the cleanliness guard above, so an empty set means there is
    genuinely no reviewable tracked content in scope."""
    top, err = git_work_tree_root(root)
    if err is not None:
        return None, None, f"content identity requires a git work tree: {err}"
    commit, err = resolve_commit(root, reviewed_sha)
    if err is not None:
        return None, None, err
    if require_clean:
        dirty, derr = relevant_working_tree_dirty(root, paths, exclude_prefixes)
        if derr is not None:
            return None, None, derr
        if dirty:
            preview = "; ".join(f"[{xy.strip() or '??'}] {p}" for xy, p in dirty[:8])
            return None, None, (
                "relevant files are dirty or untracked (fail closed; commit or remove them "
                "so the reviewed identity binds committed content): " + preview)
    identity, entries, err = git_tree_manifest(root, commit, paths, exclude_prefixes)
    if err is not None:
        return None, None, err
    return identity, commit, None


# ==========================================================================
# Material packet digest + immutable migration manifest (D-001 amendment 3,
# Section 1). A legacy task is grandfathered ONLY if it is in the frozen
# migration manifest AND its material packet digest is unchanged since baseline.
# ==========================================================================

# Material packet fields (owner amendment 3, Section 1). EXCLUDES lifecycle
# bookkeeping (status, progress, timestamps, reports, gate records, roster,
# worktree, progress_log). A material amendment/replan changes this digest and
# invalidates grandfathering; a pure lifecycle transition does not.
MATERIAL_FIELDS = ("objective", "inputs", "outputs", "dependencies",
                   "allowed_paths", "forbidden_paths", "acceptance_scenarios",
                   "required_gates", "risks", "blockers")


def material_digest(task: dict) -> str:
    """Deterministic SHA-256 over the task's MATERIAL packet fields only."""
    material = {k: task.get(k) for k in MATERIAL_FIELDS}
    canon = json.dumps(material, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


class MigrationManifest:
    """The immutable, owner-frozen list of pre-regime task IDs (bound to a baseline
    commit) plus each packet's material digest at that baseline. Membership decides
    whether a not-in-regime task may be grandfathered; a task ID absent here can NEVER
    become grandfathered by merely omitting the regime stamp. The list must not silently
    grow: its content is hashed and that hash is recorded in the governing directive's
    manifest, so any change is caught by tools/validate_directive_compliance.py and
    requires an owner-issued amendment. Missing/corrupt -> fail closed."""

    def __init__(self, path: Path = MIGRATION_MANIFEST_PATH):
        self.path = Path(path)
        self.data: dict = {}
        self.errors: list[str] = []
        self.exists = self.path.exists()
        self.entries: dict = {}

    def load(self) -> "MigrationManifest":
        if not self.exists:
            self.errors.append("migration_manifest.json missing")
            return self
        try:
            self.data = _load_json(self.path)
        except (ValueError, OSError) as e:
            self.errors.append(f"migration_manifest.json unreadable/invalid JSON: {e}")
            return self
        if self.data.get("schema") != "directive_migration/v1":
            self.errors.append(
                f"migration schema {self.data.get('schema')!r} != 'directive_migration/v1'")
        seen = set()
        for t in self.data.get("tasks", []):
            tid = t.get("task_id")
            dig = t.get("material_digest")
            if not tid or not dig:
                self.errors.append(f"migration entry malformed (needs task_id + material_digest): {t!r}")
                continue
            if tid in seen:
                self.errors.append(f"migration manifest lists {tid} more than once")
                continue
            seen.add(tid)
            self.entries[tid] = t
        return self

    @property
    def baseline_sha(self) -> str:
        return self.data.get("frozen_baseline_sha", "")

    @property
    def content_sha256(self) -> str:
        try:
            return sha256_file(self.path)
        except OSError:
            return ""

    def contains(self, task_id: str) -> bool:
        return task_id in self.entries and not self.errors

    def digest_for(self, task_id: str):
        e = self.entries.get(task_id)
        return e.get("material_digest") if e else None


def load_migration_manifest(path: Path = MIGRATION_MANIFEST_PATH) -> MigrationManifest:
    return MigrationManifest(path).load()


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
