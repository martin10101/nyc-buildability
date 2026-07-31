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
import os
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

# ==========================================================================
# ACCEPTANCE-ORDERING LIFECYCLE CLASSIFICATION  (the STATED RULE)
#
# Owner directive D-004, Message F item 2(a) == requirement D-004-R629:
#   "rows whose sole unmet obligations are acceptance-ordering lifecycle acts
#    (accept, post-accept cleanup, checkpoint, stop-after) must NOT gate
#    accept() - evaluated, not deleted; verified at the first post-accept
#    opportunity instead."
# Classification authority D-004-R632: the per-row classification belongs to
# the INDEPENDENT VERIFIER, not to the producer and not to this module.
# Append-only invariant D-004-R627: no requirement row's applicability is ever
# edited; this mechanism reads rows, it never rewrites them.
#
# AUDIT THIS RULE, NOT THE BEHAVIOR.  A requirement row may be treated as an
# acceptance-ordering lifecycle act -- recorded EVALUATED-AND-DEFERRED instead
# of gating accept() -- if and ONLY IF ALL FIVE conditions below hold TOGETHER.
# They are CONJUNCTIVE: failing any one leaves the row gating acceptance
# exactly as it does today.  Every input is either the requirement row's OWN
# recorded semantics or an independent verifier's per-row attestation.  There
# is no special-cased task id, no flag, and no environment override.
#
#   (1) ACT CLASS.  The verification row carries a `lifecycle_classification`
#       object whose `act_class` is drawn from ACCEPTANCE_ORDERING_ACT_CLASSES
#       -- the owner's CLOSED four-item enumeration, transcribed from R629
#       ("accept, post-accept cleanup, checkpoint, stop-after").  No other
#       value is accepted and this code never extends the enumeration.
#
#   (2) INDEPENDENT ATTESTATION.  That object records a non-empty
#       `classified_by` that is NOT the producer of the verification record,
#       plus a non-empty `justification`.  Per R632 the sufficient judgment is
#       the independent verifier's; this module supplies NECESSARY conditions
#       only and deliberately refuses to supply the sufficient one.
#
#   (3) LIFECYCLE BINDING (row semantics).  The requirement row's own
#       `applicability.lifecycle_events` is non-empty and is a SUBSET of
#       ACCEPTANCE_ORDERING_LIFECYCLE_EVENTS.  This is the mechanical reading
#       of R629's word "SOLE": a row that also binds an obligation at
#       claim/progress/submit/gate carries a duty that WAS satisfiable before
#       acceptance, so it keeps gating.
#
#   (4) ELIGIBLE CLASSIFICATION (row semantics).  The row's own
#       `classification` is in LIFECYCLE_ELIGIBLE_CLASSIFICATIONS -- an
#       ALLOWLIST, not a denylist.  An acceptance-ordering ACT is something the
#       executor DOES ("obligation") or an ordering constraint on when it may
#       stop ("sequencing").  Every other classification the schema permits --
#       prohibition, hold, decision, authorization, dependency, harness,
#       evidence, external_fact, return -- is a BAR on acceptance or an
#       evidentiary/return duty, not an act performed AT acceptance.  Deferring
#       a prohibition/hold/authorization bound to acceptance would waive the
#       very bar that says "do not accept yet"; those are excluded
#       structurally so that NO attestation, however well-formed, can reach
#       them.
#
#   (5) NO NEGATIVE FINDING.  The verification row's `state` is neither FAIL
#       nor BLOCKED.  A row the verifier actively failed or found blocked is a
#       substantive negative finding and keeps gating however it is classified.
#
# WHY (3) ADMITS ONLY "accept": the registry's ACTUAL lifecycle-event
# vocabulary is {claim, progress, submit, gate, accept}.  "accept" is the only
# token denoting an act at or after acceptance; claim/progress/submit/gate are
# all strictly earlier.  All four of the owner's act classes are recorded with
# the "accept" token by the capture convention, and WHICH of the four a given
# row is remains the verifier's call under (1)+(2).  Tokens absent from the
# vocabulary ("checkpoint", "post_accept", ...) are deliberately NOT added:
# defining semantics for an unused token would widen the rule on speculation,
# and a rule one notch too permissive silently lowers the acceptance bar for
# every future task.
#
# KNOWN LIMIT, STATED ON PURPOSE: conditions (3) and (4) cannot separate an
# ordering constraint that is an act ("stop AFTER acceptance") from one that is
# a bar ("stop BEFORE acceptance") -- both are `sequencing` rows bound to
# "accept".  That discrimination is exactly the semantic judgment R632 assigns
# to the independent verifier, and it is why (1)+(2) are mandatory rather than
# advisory.
#
# WHAT DEFERRAL MEANS: the row is EVALUATED -- never deleted, waived, or
# silently passed.  accept() records every deferral on the task packet and the
# obligation is verified at the FIRST post-accept opportunity the control plane
# offers: project_control.checkpoint() REFUSES to record a checkpoint while any
# registered deferral is still unverified.
# ==========================================================================

# The owner's closed enumeration of acceptance-ordering acts (D-004-R629).
ACCEPTANCE_ORDERING_ACT_CLASSES = frozenset({
    "accept",                # "accept"
    "post_accept_cleanup",   # "post-accept cleanup"
    "checkpoint",            # "checkpoint"
    "stop_after",            # "stop-after"
})

# Lifecycle-event tokens that denote an act AT OR AFTER acceptance. Derived from
# the registry's real vocabulary {claim, progress, submit, gate, accept}.
ACCEPTANCE_ORDERING_LIFECYCLE_EVENTS = frozenset({"accept"})

# Requirement classifications that can describe an ACT (allowlist, see (4)).
LIFECYCLE_ELIGIBLE_CLASSIFICATIONS = frozenset({"obligation", "sequencing"})

# The per-row attestation key an independent verifier writes into a verification
# row. `additionalProperties: true` in directive_verification.schema.json admits
# it without any schema change.
LIFECYCLE_CLASSIFICATION_KEY = "lifecycle_classification"

# Verifier verdicts that can NEVER be deferred, however classified (see (5)).
NEGATIVE_VERIFICATION_STATES = frozenset({"FAIL", "BLOCKED"})


def acceptance_ordering_deferral(requirement_row, verification_row,
                                 producer: str = "") -> tuple:
    """Apply the five CONJUNCTIVE conditions stated in the section header above.

    Returns (deferral, refusals):
      * (None, [])         no lifecycle_classification is claimed -> the row
                           gates acceptance exactly as before (the default);
      * (None, [reason..]) a claim WAS made and is REFUSED -> the reasons are
                           surfaced alongside the row's ordinary "not PASS"
                           reason, so a refused claim is loud, never silent;
      * (deferral, [])     all five conditions hold -> the caller records the
                           deferral and does not gate on this row.

    Fails closed on every malformed shape and never raises. The producer
    argument is the identity that PRODUCED the verification record; an
    attestation by that identity is refused (condition 2)."""
    if not isinstance(verification_row, dict):
        return None, []
    claim = verification_row.get(LIFECYCLE_CLASSIFICATION_KEY)
    if claim is None:
        return None, []
    rid = verification_row.get("id") or "<unknown requirement>"
    if not isinstance(claim, dict):
        return None, [f"{rid}: {LIFECYCLE_CLASSIFICATION_KEY} is not an object "
                      f"(fail closed; the row keeps gating acceptance)"]
    refusals: list[str] = []

    # (1) act class from the owner's closed enumeration.
    act = claim.get("act_class")
    act = act.strip() if isinstance(act, str) else ""
    if act not in ACCEPTANCE_ORDERING_ACT_CLASSES:
        refusals.append(
            f"{rid}: lifecycle act_class {claim.get('act_class')!r} is not one of the "
            f"owner-enumerated acceptance-ordering acts "
            f"{sorted(ACCEPTANCE_ORDERING_ACT_CLASSES)}")

    # (2) independent attestation.
    by = claim.get("classified_by")
    by = by.strip() if isinstance(by, str) else ""
    if not by:
        refusals.append(f"{rid}: lifecycle classification records no classified_by; "
                        f"an independent verifier must own the classification")
    elif producer and by == producer:
        refusals.append(f"{rid}: lifecycle classification by {by!r} equals the verification "
                        f"producer {producer!r}; the classification is the INDEPENDENT "
                        f"verifier's, not the producer's")
    just = claim.get("justification")
    just = just.strip() if isinstance(just, str) else ""
    if not just:
        refusals.append(f"{rid}: lifecycle classification records no justification; "
                        f"an unreasoned classification is refused")

    # (3)+(4) the requirement row's OWN recorded semantics.
    events: list = []
    if not isinstance(requirement_row, dict):
        refusals.append(f"{rid}: no requirement row found in requirements.json; the row's "
                        f"own lifecycle semantics cannot be read (fail closed)")
    else:
        cls = requirement_row.get("classification")
        cls = cls.strip() if isinstance(cls, str) else ""
        if cls not in LIFECYCLE_ELIGIBLE_CLASSIFICATIONS:
            refusals.append(
                f"{rid}: requirement classification {requirement_row.get('classification')!r} "
                f"cannot describe an acceptance-ordering ACT (eligible: "
                f"{sorted(LIFECYCLE_ELIGIBLE_CLASSIFICATIONS)}); a bar on acceptance or an "
                f"evidentiary/return duty is never deferred")
        applic = requirement_row.get("applicability")
        raw_events = applic.get("lifecycle_events") if isinstance(applic, dict) else None
        if (not isinstance(raw_events, list) or not raw_events
                or not all(isinstance(e, str) for e in raw_events)):
            refusals.append(f"{rid}: applicability.lifecycle_events is missing, empty or "
                            f"malformed; the row's lifecycle binding cannot be read "
                            f"(fail closed)")
        else:
            events = [e.strip() for e in raw_events]
            outside = sorted(set(events) - ACCEPTANCE_ORDERING_LIFECYCLE_EVENTS)
            if outside:
                refusals.append(
                    f"{rid}: lifecycle_events {sorted(set(events))} bind obligations outside "
                    f"acceptance ordering ({', '.join(outside)}), so this row's unmet "
                    f"obligations are not SOLELY acceptance-ordering acts")

    # (5) a negative verifier finding is never deferrable.
    state = verification_row.get("state")
    if state in NEGATIVE_VERIFICATION_STATES:
        refusals.append(f"{rid}: verification state {state!r} is a substantive negative "
                        f"finding; it keeps gating acceptance however it is classified")

    if refusals:
        return None, refusals
    return {
        "requirement_id": rid,
        "act_class": act,
        "classified_by": by,
        "classified_at": claim.get("classified_at") or "",
        "justification": just,
        "row_classification": requirement_row.get("classification"),
        "row_lifecycle_events": sorted(set(events)),
        "verification_state": state,
    }, []


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

    def task_verification_result(self, directive_id: str, task_id: str, applicable_ids,
                                 reviewed_manifest_sha256: str | None,
                                 reviewed_sha: str | None = None) -> dict:
        """Structured per-(directive, task) verification state.

        Returns {"reasons": [...], "deferrals": [...]}:
          * reasons   -- why this pair is NOT fully verified at the given content
                         identity (empty == every applicable requirement is PASS at
                         that identity, by an independent verifier, in a well-formed
                         row, OR is a properly attested acceptance-ordering lifecycle
                         act);
          * deferrals -- the acceptance-ordering lifecycle acts that were EVALUATED
                         and deferred rather than gating (see the module-level
                         "ACCEPTANCE-ORDERING LIFECYCLE CLASSIFICATION" rule). The
                         caller MUST record these; they are never waived.

        One directive may govern several tasks, each with its own allowed paths,
        content identity, evidence, and reviewer, so only the requirements applicable
        to *this* task are evaluated for *this* task's acceptance ('ALL' means
        all-applicable-to-this-task).

        Supports verification.json schema directive_verification/v2 (task_verifications[])
        and falls back to the v1 single-task shape for legacy/other directives. Missing,
        duplicate, extra, cross-task, or stale rows FAIL CLOSED. When `reviewed_sha` is
        supplied, the record's reviewed commit must match it (D-004-R630: reviewed_sha is
        ACTUALLY compared); a record that omits it therefore fails closed too."""
        d = self.directives.get(directive_id)
        if d is None:
            return {"reasons": [f"directive {directive_id} not found"], "deferrals": []}
        if d.errors:
            return {"reasons": [f"directive {directive_id} integrity error: {d.errors[0]}"],
                    "deferrals": []}
        v = d.verification
        if not v:
            return {"reasons": [f"{directive_id}: no verification.json"], "deferrals": []}
        applicable = set(applicable_ids or [])
        schema = v.get("schema")
        if schema == "directive_verification/v2":
            reasons, deferrals = self._v2_task_unresolved(
                d, v, directive_id, task_id, applicable, reviewed_manifest_sha256,
                reviewed_sha)
        else:
            # v1 back-compat: a single flat requirements[] shape scoped to one task.
            # Evaluate ONLY the requirements applicable to this task (owner correction:
            # not every requirement belonging to the directive).
            reasons, deferrals = self._v1_task_unresolved(
                d, v, directive_id, applicable, reviewed_manifest_sha256, reviewed_sha)
        return {"reasons": reasons, "deferrals": deferrals}

    def task_unresolved_requirements(self, directive_id: str, task_id: str,
                                     applicable_ids, reviewed_manifest_sha256: str | None,
                                     reviewed_sha: str | None = None) -> list[str]:
        """Reasons a SPECIFIC (directive, task) pair is NOT fully verified at the given
        content identity. Thin projection of task_verification_result()["reasons"];
        callers that must RECORD the deferred acceptance-ordering rows (accept()) use
        task_verification_result() instead."""
        return self.task_verification_result(
            directive_id, task_id, applicable_ids, reviewed_manifest_sha256,
            reviewed_sha)["reasons"]

    def requirement_verification_state(self, directive_id: str, task_id: str,
                                       requirement_id: str) -> tuple:
        """(state, row) for ONE requirement row of ONE task, or (None, None) when no
        such row exists. Used to confirm a deferred acceptance-ordering act at the
        first post-accept opportunity; read-only, never raises."""
        d = self.directives.get(directive_id)
        if d is None or d.errors or not d.verification:
            return None, None
        v = d.verification
        rows = []
        if v.get("schema") == "directive_verification/v2":
            for tv in (v.get("task_verifications") or []):
                if (isinstance(tv, dict) and tv.get("task_id") == task_id
                        and tv.get("directive_id", directive_id) == directive_id):
                    rows.extend(r for r in (tv.get("requirements") or [])
                                if isinstance(r, dict))
        else:
            rows.extend(r for r in (v.get("requirements") or []) if isinstance(r, dict))
        for r in rows:
            if r.get("id") == requirement_id:
                return r.get("state"), r
        return None, None

    def _v2_task_unresolved(self, d, v, directive_id, task_id, applicable,
                            reviewed_manifest_sha256, reviewed_sha=None):
        rows_all = v.get("task_verifications")
        if not isinstance(rows_all, list):
            return ([f"{directive_id}: v2 verification missing task_verifications[] "
                     f"(fail closed)"], [])
        matches = [tv for tv in rows_all if isinstance(tv, dict)
                   and tv.get("task_id") == task_id
                   and tv.get("directive_id", directive_id) == directive_id]
        if not matches:
            return ([f"{directive_id}/{task_id}: no task_verification row (fail closed)"], [])
        if len(matches) > 1:
            return ([f"{directive_id}/{task_id}: duplicate task_verification rows "
                     f"({len(matches)}) (fail closed)"], [])
        tv = matches[0]
        reasons: list[str] = []
        deferrals: list[dict] = []
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
        # reviewed_sha is ACTUALLY compared (D-004-R630 / Message F item 2(b)); a record
        # that omits it therefore fails closed, exactly as a mismatching one does.
        rsha = tv.get("reviewed_sha")
        if reviewed_sha is not None and rsha != reviewed_sha:
            reasons.append(f"{directive_id}/{task_id}: verification reviewed_sha is stale -- "
                           f"recorded at commit {rsha}, current reviewed commit is "
                           f"{reviewed_sha} (fail closed)")
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
                deferral, refusals = acceptance_ordering_deferral(
                    d.requirement(rid), r, producer)
                if deferral is not None:
                    deferral["directive_id"] = directive_id
                    deferral["task_id"] = task_id
                    deferrals.append(deferral)
                    continue
                reasons.extend(refusals)
                reasons.append(f"{rid}: verification state {st!r} (not PASS)")
        return reasons, deferrals

    def _v1_task_unresolved(self, d, v, directive_id, applicable, reviewed_manifest_sha256,
                            reviewed_sha=None):
        producer = (v.get("producer") or d.requirements.get("producer") or "").strip()
        verifier = (v.get("verifier") or "").strip()
        reasons: list[str] = []
        deferrals: list[dict] = []
        if not verifier:
            reasons.append(f"{directive_id}: no independent verifier recorded")
        elif producer and verifier == producer:
            reasons.append(f"{directive_id}: verifier {verifier!r} equals producer "
                           f"{producer!r}; independent verification required")
        vsha = v.get("reviewed_manifest_sha256")
        if reviewed_manifest_sha256 is not None and vsha != reviewed_manifest_sha256:
            reasons.append(f"{directive_id}: verification is stale -- recorded at content "
                           f"identity {vsha}, current is {reviewed_manifest_sha256}")
        rsha = v.get("reviewed_sha")
        if reviewed_sha is not None and rsha != reviewed_sha:
            reasons.append(f"{directive_id}: verification reviewed_sha is stale -- recorded "
                           f"at commit {rsha}, current reviewed commit is {reviewed_sha} "
                           f"(fail closed)")
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
                deferral, refusals = acceptance_ordering_deferral(
                    d.requirement(rid), row, producer)
                if deferral is not None:
                    deferral["directive_id"] = directive_id
                    deferral["task_id"] = None
                    deferrals.append(deferral)
                    continue
                reasons.extend(refusals)
                reasons.append(f"{rid}: verification state {st!r} (not PASS)")
        return reasons, deferrals


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
    A non-zero exit, a timeout, or an unavailable git binary is a fail-closed error, never
    a silent empty result. GIT_LITERAL_PATHSPECS=1 forces every pathspec to be matched
    literally so pathspec magic (e.g. ':(exclude)') in task allowed_paths cannot alter the
    file set (defense-in-depth; G5 hardening). A bounded timeout prevents a wedged git from
    hanging the CLI."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            env={**os.environ, "GIT_LITERAL_PATHSPECS": "1"}, timeout=60)
    except subprocess.TimeoutExpired:
        return None, "git command timed out (fail closed)"
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
    # --end-of-options guarantees `rev` is parsed as a revision, never as a git option,
    # even if an operator passes a value beginning with '-' (G5 hardening).
    out, err = _run_git(root, ["rev-parse", "--verify", "--quiet", "--end-of-options", rev])
    if err is not None or not out.strip():
        return None, (f"cannot resolve reviewed commit {sha or 'HEAD'!r} to a commit object "
                      f"(fail closed)")
    full = out.decode("utf-8").strip()
    if not SHA40_RE.match(full):
        return None, f"resolved commit {full!r} is not a 40-hex sha (fail closed)"
    return full, None


def _hash_manifest_entries(entries: list) -> str:
    """The ONE canonical encoding of a content-identity manifest: sorted 4-field
    records, NUL-separated within a record and newline-terminated. Shared by the
    raw-blob manifest and the control-plane material manifest so an identity built
    from both components is a single, order-independent hash."""
    entries = sorted(entries)
    h = hashlib.sha256()
    for rel, mode, gtype, value in entries:
        h.update(rel.encode("utf-8")); h.update(b"\0")
        h.update(mode.encode("ascii")); h.update(b"\0")
        h.update(gtype.encode("ascii")); h.update(b"\0")
        h.update(value.encode("ascii")); h.update(b"\n")
    return h.hexdigest()


def _ls_tree_entries(root: Path, commit: str, paths: list) -> tuple:
    """(entries, error) of (relpath, mode, gtype, object-id) for every tracked object at
    `commit` under `paths`; `-r` expands directories and gitlinks appear as type
    'commit'. No filtering: callers apply their own prefix policy."""
    entries: list = []
    seen: set = set()
    for p in paths:
        pp = str(p).strip().rstrip("/")
        if not pp:
            continue
        out, err = _run_git(root, ["ls-tree", "-r", "-z", "--full-tree", commit, "--", pp])
        if err is not None:
            return None, f"git ls-tree failed for {pp!r}: {err}"
        for rec in out.split(b"\x00"):
            if not rec:
                continue
            meta, sep, path_b = rec.partition(b"\t")
            if not sep:
                return None, f"unparseable ls-tree record: {rec!r}"
            try:
                mode, gtype, obj = meta.decode("utf-8").split()
            except ValueError:
                return None, f"unparseable ls-tree meta: {meta!r}"
            rel = path_b.decode("utf-8")
            if rel in seen:
                continue
            seen.add(rel)
            entries.append((rel, mode, gtype, obj))
    return entries, None


def git_tree_manifest(root: Path, commit: str, paths: list,
                      exclude_prefixes: tuple = ()) -> tuple:
    """Deterministic SHA-256 over sorted (relpath, mode, type, object-id) for every
    tracked object at `commit` under `paths` (files or directory trees; `-r` expands
    directories, gitlinks appear as type 'commit'). Returns (identity_hex, entries,
    error)."""
    all_entries, err = _ls_tree_entries(root, commit, paths)
    if err is not None:
        return None, None, err
    entries = [e for e in all_entries
               if not any(e[0].startswith(pre) for pre in exclude_prefixes)]
    entries.sort()
    return _hash_manifest_entries(entries), entries, None


# ==========================================================================
# CONTROL-PLANE MATERIAL IDENTITY  (owner directive D-004-R630, Message F
# item 2(b): "governance-shaped tasks (allowed_paths entirely under
# project-control/) get real staleness/dirt guards").
#
# THE PROBLEM.  The raw-blob manifest above deliberately EXCLUDES the
# control-plane tree, because the control plane rewrites its own records: every
# submit/gate/accept mutates the task packet it is operating on. For a task
# whose allowed_paths lie entirely inside that tree the excluded set is
# everything, so the identity degenerates to the deterministic empty-set hash
# and the dirt guard sees nothing -- both guards compare a constant with itself.
#
# THE RESOLUTION -- MATERIAL CONTENT vs LIFECYCLE BOOKKEEPING.  The exclusion is
# not removed (that would be unworkable, see below); it is replaced, for the
# excluded tree, by a MATERIAL identity that measures exactly the content a
# reviewer reviewed:
#
#   * a task packet (project-control/tasks/<id>.json) contributes
#     material_digest(packet) -- the owner's OWN material/lifecycle boundary
#     from D-001 amendment 3 Section 1, which already excludes status, progress,
#     timestamps, reports, gate records, roster, worktree and progress_log;
#   * EVERY other control-plane file contributes its canonical git blob id,
#     exactly like ordinary work product: reports, directive sources,
#     requirements, verification records, config.
#
# WHY THE EXCLUSION CANNOT SIMPLY BE DROPPED.  A task packet's raw blob id
# changes on every lifecycle transition, and the control plane performs such
# transitions BETWEEN the moment an identity is stamped and the moment it is
# checked: submit() stamps the identity and then writes status/progress to the
# packet; gate() writes progress_percent after stamping its own record; accept()
# then recomputes and compares. A raw-blob control-plane identity is therefore
# stale by construction the instant it is recorded, and no task could ever be
# accepted. The material digest is the only boundary that is BOTH non-vacuous
# and stable across the submit -> gate -> accept window.
#
# CONSEQUENCE, STATED PLAINLY: a purely lifecycle-bookkeeping edit to a task
# packet (status / progress_percent / updated_at / progress_log / reports) does
# NOT move the identity, by design. A material packet amendment does, and so
# does any change to any other file in scope. The guard is real, not literal.
# ==========================================================================

# The one lifecycle-owned file class inside the control-plane tree: task packets,
# whose non-material fields the control plane rewrites on every transition.
TASK_PACKET_PREFIX = "project-control/tasks/"
TASK_PACKET_SUFFIX = ".json"
# Marker distinguishing a material-digest entry from a git object id in a manifest
# entry, so the two can never collide in the hashed encoding.
MATERIAL_ENTRY_PREFIX = "material:"


def is_task_packet_path(rel: str) -> bool:
    """True for a control-plane task packet, whose non-material fields are rewritten
    by the control plane itself and therefore never bind a reviewed identity."""
    return str(rel).startswith(TASK_PACKET_PREFIX) and str(rel).endswith(TASK_PACKET_SUFFIX)


def _packet_material_at_commit(root: Path, commit: str, rel: str, obj: str) -> tuple:
    """(material_digest_hex, error) for a task packet stored at object id `obj`."""
    out, err = _run_git(root, ["cat-file", "blob", obj])
    if err is not None:
        return None, f"cannot read {rel} at {commit[:12]}: {err}"
    try:
        packet = json.loads(out.decode("utf-8-sig"))
    except (ValueError, UnicodeDecodeError) as e:
        return None, f"task packet {rel} at {commit[:12]} is not valid JSON: {e}"
    if not isinstance(packet, dict):
        return None, f"task packet {rel} at {commit[:12]} is not a JSON object"
    return material_digest(packet), None


def control_plane_entries(root: Path, commit: str, paths: list,
                          include_prefixes: tuple = ()) -> tuple:
    """(entries, error) for the tracked control-plane objects at `commit` under `paths`
    that fall inside `include_prefixes` -- i.e. exactly the objects the raw-blob
    manifest excludes. Task packets contribute their MATERIAL digest; everything else
    contributes its git object id. See the section header for why."""
    if not include_prefixes:
        return [], None
    all_entries, err = _ls_tree_entries(root, commit, paths)
    if err is not None:
        return None, err
    out: list = []
    for rel, mode, gtype, obj in all_entries:
        if not any(rel.startswith(pre) for pre in include_prefixes):
            continue
        if gtype == "blob" and is_task_packet_path(rel):
            dig, derr = _packet_material_at_commit(root, commit, rel, obj)
            if derr is not None:
                return None, derr
            out.append((rel, mode, gtype, MATERIAL_ENTRY_PREFIX + dig))
        else:
            out.append((rel, mode, gtype, obj))
    out.sort()
    return out, None


def _status_records(root: Path, paths: list) -> tuple:
    """(records, error) of (xy_status, path) for every modified/staged/deleted tracked
    file and every untracked file under `paths`. No prefix filtering."""
    args = ["status", "--porcelain=v1", "-z", "--untracked-files=all", "--"]
    args += [str(p) for p in paths if str(p).strip()]
    out, err = _run_git(root, args)
    if err is not None:
        return None, f"git status failed: {err}"
    records: list = []
    tokens = out.split(b"\x00")
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if not tok:
            i += 1
            continue
        xy = tok[:2].decode("utf-8", "replace")
        path = tok[3:].decode("utf-8", "replace")
        # rename/copy records carry the origin path in the following NUL field. Porcelain
        # v1 reports the R/C in the index (X) column; check both columns defensively.
        if xy[:1] in ("R", "C") or xy[1:2] in ("R", "C"):
            i += 1
        records.append((xy, path))
        i += 1
    return records, None


def relevant_working_tree_dirty(root: Path, paths: list,
                                exclude_prefixes: tuple = ()) -> tuple:
    """Return (dirty_entries, error). dirty_entries is a list of (xy_status, path) for
    any tracked file under `paths` that is modified/staged/deleted OR any untracked file
    under `paths`, excluding exclude_prefixes. A non-empty list is the fail-closed signal
    that the working tree does not match committed content for the relevant scope."""
    records, err = _status_records(root, paths)
    if err is not None:
        return None, err
    return [(xy, path) for xy, path in records
            if not any(path.startswith(pre) for pre in exclude_prefixes)], None


def control_plane_material_dirty(root: Path, paths: list,
                                 include_prefixes: tuple = ()) -> tuple:
    """Return (dirty_entries, error) for CONTROL-PLANE files under `paths` (those the
    raw-blob dirt guard drops via its exclusion tuple). A file is dirty unless it is a
    tracked, modified task packet whose working-tree MATERIAL digest still equals its
    HEAD material digest -- i.e. unless the only change is lifecycle bookkeeping.
    Untracked, deleted, renamed/copied and unreadable files are ALWAYS dirty.

    An EMPTY path list means an empty scope, not the whole repository: `git status --`
    with no pathspec reports every file, so a task that declares no allowed_paths would
    otherwise be judged against control-plane records it does not own."""
    if not include_prefixes:
        return [], None
    if not [p for p in paths if str(p).strip()]:
        return [], None
    records, err = _status_records(root, paths)
    if err is not None:
        return None, err
    dirty: list = []
    for xy, path in records:
        if not any(path.startswith(pre) for pre in include_prefixes):
            continue
        if _is_lifecycle_only_packet_change(root, xy, path):
            continue
        dirty.append((xy, path))
    return dirty, None


def _is_lifecycle_only_packet_change(root: Path, xy: str, path: str) -> bool:
    """True ONLY for a tracked task packet whose working-tree material digest equals its
    HEAD material digest. Every other shape -- non-packet file, untracked ('?'), deleted
    ('D'), renamed/copied ('R'/'C'), unreadable, unparseable, or materially changed --
    returns False so the caller treats it as dirt (fail closed)."""
    if not is_task_packet_path(path):
        return False
    if any(c in xy for c in ("?", "!", "D", "R", "C", "U")):
        return False
    out, err = _run_git(root, ["cat-file", "blob", f"HEAD:{path}"])
    if err is not None:
        return False
    try:
        head_packet = json.loads(out.decode("utf-8-sig"))
        work_packet = json.loads((Path(root) / path).read_text(encoding="utf-8-sig"))
    except (ValueError, OSError, UnicodeDecodeError):
        return False
    if not isinstance(head_packet, dict) or not isinstance(work_packet, dict):
        return False
    return material_digest(head_packet) == material_digest(work_packet)


def frozen_git_identity(paths: list, reviewed_sha: str | None = None,
                        root: Path = ROOT, exclude_prefixes: tuple = (),
                        require_clean: bool = True,
                        control_plane_prefixes: tuple = ()) -> tuple:
    """The authoritative git-canonical reviewed content identity for a task's paths.
    Returns (identity_hex, resolved_commit_sha, error). Fails closed (error != None) when:
      * `root` is not a git work tree / git is unavailable;
      * reviewed_sha (or HEAD) does not resolve to a commit;
      * require_clean and a relevant tracked file is dirty or a relevant file is untracked;
      * require_clean and a control-plane file in scope carries a MATERIAL (non-lifecycle)
        working-tree change (D-004-R630).

    The identity has TWO components hashed as one manifest: the raw-blob entries for
    paths outside `exclude_prefixes`, plus the MATERIAL entries for paths inside
    `control_plane_prefixes` (see the CONTROL-PLANE MATERIAL IDENTITY section). When
    `control_plane_prefixes` is empty, or no path in scope falls inside it, the value is
    byte-identical to the raw-blob identity, so existing identities are unchanged.
    An empty relevant set yields the deterministic empty-set hash -- which for a
    governance-shaped task is no longer possible unless its allowed_paths genuinely
    contain no tracked content at all."""
    top, err = git_work_tree_root(root)
    if err is not None:
        return None, None, f"content identity requires a git work tree: {err}"
    commit, err = resolve_commit(root, reviewed_sha)
    if err is not None:
        return None, None, err
    if require_clean:
        # The cleanliness check compares the working tree to HEAD, so a clean LIVE stamp is
        # only meaningful when the reviewed commit IS HEAD. If an explicit reviewed_sha
        # resolves to a non-HEAD commit, the "clean" guard would validate the wrong tree, so
        # fail closed (N2). reviewed_sha=None (-> HEAD) and submit/gate passing the current
        # HEAD both satisfy this.
        head, herr = resolve_commit(root, None)
        if herr is not None:
            return None, None, herr
        if commit != head:
            return None, None, (
                f"reviewed sha {commit[:12]} is not HEAD {head[:12]}; a clean live content-"
                f"identity stamp must be taken at HEAD (fail closed)")
        dirty, derr = relevant_working_tree_dirty(root, paths, exclude_prefixes)
        if derr is not None:
            return None, None, derr
        cp_dirty, cderr = control_plane_material_dirty(root, paths, control_plane_prefixes)
        if cderr is not None:
            return None, None, cderr
        dirty = list(dirty) + list(cp_dirty)
        if dirty:
            preview = "; ".join(f"[{xy.strip() or '??'}] {p}" for xy, p in dirty[:8])
            return None, None, (
                "relevant files are dirty or untracked (fail closed; commit or remove them "
                "so the reviewed identity binds committed content): " + preview)
    identity, entries, err = git_tree_manifest(root, commit, paths, exclude_prefixes)
    if err is not None:
        return None, None, err
    cp_entries, cperr = control_plane_entries(root, commit, paths, control_plane_prefixes)
    if cperr is not None:
        return None, None, cperr
    if cp_entries:
        identity = _hash_manifest_entries(list(entries) + list(cp_entries))
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
