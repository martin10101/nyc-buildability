# M5-T043 — producer report

Wide-street wiring module hardening + extraction (DB-028 a–e, h). One concise evidence pass.

**Resubmission note (reviewability).** The prior pass referenced code only by file:line and git
blob digest and did not embed the changed source, so the reviewers could not read the implementation
from the report. This pass EMBEDS the actual new-side hunks in bounded per-file sections (§3.1–§3.6)
so the aggregate diff cap cannot hide any file's change and no source is displaced by report prose,
assertions, or digest identifiers. Each hunk is the verbatim worktree text the worker read; line
anchors point to the rest of each file.

**Worker vs supervisor / authority.** §3 embeds the NEW side verbatim from this worktree. The
authoritative VERBATIM OLD-side `git diff` hunks and the committed blob digests (§5) are bound by the
supervisor/orchestrator at the frozen head — git is orchestrator-only (ADR-005), and a producer runs
only its documented test commands. §4 records the WORKER's own runs of the five documented commands
in this worktree; the supervisor reproduces them at the frozen head. Commits, pushes, gates, and
acceptance are the orchestrator's; nothing here claims completion or green CI.

**Working-tree state.** These changes are UNSTAGED working-tree modifications (git porcelain ` M`,
plus the new file `named_street_override_status.py`); the orchestrator stages and commits them. They
are not staged by the producer.

**No implementation defect** is asserted or fixed here beyond the DB-028 items the packet scopes; no
speculative source change was made. AS-6/AS-8 stay PENDING until the orchestrator supplies CI on the
committed changes (§6). No root-level lint finding was repaired and no supervisor tooling was edited.

## 1. Scope and boundaries

In scope, all inside the packet `allowed_paths`:

- **(a) Extraction + compatibility facade.** `MatchedNamedStreetOverride`,
  `NamedStreetOverrideStatus`, `_fully_resolved_typed_inputs`, and
  `build_named_street_override_status` moved from `wide_street_wiring.py` into the new
  `services/api/app/rules/named_street_override_status.py`. `wide_street_wiring.py` now imports the
  three public symbols from that submodule (`:94-98`) and keeps them in `__all__` (`:112,113,115`) as
  a compatibility facade — every pre-existing import path (`integration.py`,
  `api/v1/rule_evaluation.py`, `spatial/wide_street_live_provider.py`, and the three suites) resolves
  to the SAME objects; no consumer edited.
- **(b) Accuracy.** Module docstring (`wide_street_wiring.py:48-61`), the `NamedStreetOverrideStatus`
  docstring (moved), and the branch-4 `named_pending` reason (`determine_wide_street_far`, the
  `if named_pending:` branch, `:414-434`) now state the ZR 12-10 matcher IS consulted but could not
  resolve the candidate segment. No "not implemented" / "out-of-scope" / "follow-up" phrasing
  survives either rules module (grep-clean, AS-4).
- **(c) Guard hardening (tighten-only).** `_elevated_exceptions_checked` (`:222-254`) and the
  `named_pending` derivation (`:324`) now require `override_table_implemented=True` on the safe path,
  replacing the old `may_touch AND NOT implemented` boolean pair. A hand-built
  `may_touch=False / implemented=False` status (a shape `build_named_street_override_status` never
  emits) no longer clears the attestation. Attestation only became stricter; the builder's own
  outputs are unaffected (behavior-preserving for every producing path).
- **(d) Empty-decisions nit.** `_elevated_exceptions_checked` returns `bool(decisions) and all(...)`
  (`:252-254`) so the no-policy-decisions professional-review branch reports
  `exceptions_checked=False`, never the vacuous `all(()) -> True`.
- **(e) Provider fail-safe test.** `test_db028e_...` forces the provider's existing
  matcher-load-failure branch via a raising `load_default_matcher` + `cache_clear`, asserting the
  UNRESOLVED status (never a cleared one) and the typed fail-safe log. Provider source is out of
  scope and unchanged (the branch already existed, M5-T040).
- **(h) Web fallback wording.** `CalculationEvidence.tsx:44` defensive null-FAR fallback reads
  `"Not calculated"` (matching `DevelopmentLimits`) instead of a professional-review phrase, so no
  non-review `determination_state` can render a professional-review phrase.

Preserved (byte-equivalent behavior, per PRESERVATION input): the wiring truth table and provenance
fields for every path `build_named_street_override_status` produces; contract v1.1.0 and all
schema/TS/`integration.py`/`response.py` files untouched; DRAFT/not-verified vocabulary unchanged
(D-045-R009); fail-closed direction preserved (D-051). No `services/api/app/connectors/**` touched
(M5-T044 disjointness).

## 2. Acceptance evidence (AS-1 … AS-8)

- **AS-1 (a):** `test_db028a_named_street_status_extracted_with_compatibility_facade` (§3.3) asserts
  facade `is` submodule identity and `__all__` membership on both modules; consumer suites green
  untouched (§4 cmd 2, 4).
- **AS-2 (c):** `test_db028c_hand_built_not_implemented_status_never_clears_guard` (§3.3) — the
  `OVERRIDE_NOT_IMPLEMENTED` hand-built status yields `exceptions_checked=False`,
  `named_street_override_pending=True`, professional review.
- **AS-3 (d):** `test_db028d_no_policy_decisions_reports_exceptions_checked_false` (§3.3) — empty
  decisions + `OVERRIDE_CLEAR` → `exceptions_checked=False`, professional review.
- **AS-4 (b):** grep of both rules modules for `not implemented` / `out-of-scope` / `follow-up`
  returns no matches; docstrings and branch-4 reason describe consulted-but-unresolved (§3.1, §3.2).
- **AS-5 (e):** `test_db028e_named_street_matcher_load_failure_fails_safe_unresolved` (§3.4) — raising
  loader → `override_table_implemented=False`, `segment_may_touch=True`, `matched_override is None`,
  note "could not be loaded", `event=named_override_matcher_unavailable` + `error_type=RuntimeError`
  logged.
- **AS-6 (h, CI-proved):** `report-view.test.tsx` new case (§3.6) renders `"Wide-street conditional
  FAR (dimensionless ratio): Not calculated"` and asserts NEITHER "withheld — professional review
  required" NOR "Professional review required" for the non-review within-100ft state. **Web test
  proves only in CI on the pushed head — PENDING orchestrator CI** (§6).
- **AS-7:** ruff clean; the three documented pytest suites green; modularity exit 0 (failures 0) with
  `wide_street_wiring.py` improved (dropped off the warn list after the extraction); contract files
  byte-untouched. §4.
- **AS-8:** CI green on the pushed head — **PENDING**, orchestrator captures (§6).

## 3. Reviewable implementation hunks (new-side, embedded; bounded per file)

The verbatim OLD-side `git diff` and the committed blob digests are bound by the supervisor at the
frozen head (§5). Each section below embeds the NEW-side worktree source and, for in-place edits,
states the old→new change; where the exact prior bytes are not reconstructable without git, the
change is described from the code's own committed comment and the named M5-T040 finding, and the
verbatim old side is deferred to the supervisor's diff (never guessed).

### 3.1 `services/api/app/rules/named_street_override_status.py` — NEW file (extraction target; DB-028a)

The extracted submodule. Bodies are byte-moved from `wide_street_wiring.py` (their prior location);
only the module wrapper (module docstring + imports + `__all__`) is genuinely new. Public interface
and the independent typed-input re-check, verbatim (anchors: imports `:28-44`; classes `:47-96`;
`_fully_resolved_typed_inputs` `:99-124`; `build_named_street_override_status` `:127-251`):

```python
# :28-44 — module imports + public surface
from __future__ import annotations
from collections.abc import Sequence
from dataclasses import dataclass
from app.rules.named_street_override import (
    MatchStatus, NamedStreetOverrideMatcher, OverrideQuery, _normalize_cd,
)
__all__ = [
    "MatchedNamedStreetOverride",
    "NamedStreetOverrideStatus",
    "build_named_street_override_status",
]

# :61-65 — MatchedNamedStreetOverride fields (distinct override provenance)
    provision_id: str | None
    snapshot_sha256: str | None
    section_anchor: str | None
    matched_row_verbatim: str | None
    reason: str

# :93-96 — NamedStreetOverrideStatus fields (the attestation the FAR determination consumes)
    override_table_implemented: bool
    segment_may_touch_named_override: bool
    note: str | None
    matched_override: MatchedNamedStreetOverride | None = None

# :113-124 — independent typed-input re-check (fail-closed; not the matcher's coercing short-circuit)
    for field in (
        query.borough, query.street_name, query.cross_street_from, query.cross_street_to,
    ):
        if not isinstance(field, str) or not field.strip():
            return False
    cd = query.community_district
    if isinstance(cd, bool) or not isinstance(cd, (int, str)):
        return False
    return _normalize_cd(cd) is not None
```

Builder outcome structure, verbatim (`build_named_street_override_status`, the three attesting
shapes — this is the truth table the PRESERVATION input requires byte-equivalent):

```python
# empty candidate list -> unresolved (fail-closed)   (:167-177)
    if not segment_queries:
        return NamedStreetOverrideStatus(
            override_table_implemented=False, segment_may_touch_named_override=True, note=... )
# any MATCHED_OVERRIDE -> professional review, carries provenance   (:199-214)
            return NamedStreetOverrideStatus(
                override_table_implemented=True, segment_may_touch_named_override=True,
                note=..., matched_override=MatchedNamedStreetOverride(...) )
# any unresolved segment -> unresolved (fail-closed)   (:229-240)
    if unresolved:
        return NamedStreetOverrideStatus(
            override_table_implemented=False, segment_may_touch_named_override=True, note=... )
# every segment NOT_MATCHED with fully-resolved inputs -> table applied, clear   (:242-251)
    return NamedStreetOverrideStatus(
        override_table_implemented=True, segment_may_touch_named_override=False, note=... )
```

### 3.2 `services/api/app/rules/wide_street_wiring.py` — facade + guard (c) + empty-decisions (d) + wording (b)

Compatibility facade (proves every prior import path still resolves — DB-028a), verbatim:

```python
# :94-98 — re-export the moved symbols from the submodule
from app.rules.named_street_override_status import (
    MatchedNamedStreetOverride, NamedStreetOverrideStatus, build_named_street_override_status,
)
# :112,113,115 — kept in __all__ so `from app.rules.wide_street_wiring import ...` is unchanged
    "MatchedNamedStreetOverride",
    "NamedStreetOverrideStatus",
    "build_named_street_override_status",
```

Guard hardening (c) + empty-decisions (d) — `_elevated_exceptions_checked`, NEW verbatim (`:222-254`):

```python
def _elevated_exceptions_checked(
    decisions: Sequence[PolicyDecision],
    named_street_override: NamedStreetOverrideStatus,
) -> bool:
    if named_street_override.matched_override is not None:
        return False
    # DB-028(c): the safe attestation path REQUIRES override_table_implemented=True; a
    # hand-built may_touch=False/implemented=False status can no longer clear the criterion
    # (attestation only tightens; build_named_street_override_status never emits that shape).
    if not named_street_override.override_table_implemented:
        return False
    # DB-028(d): empty decisions are explicitly False, never the vacuous all(()) -> True.
    return bool(decisions) and all(
        d.decision_state in (DECISION_WIDE, DECISION_NARROW) for d in decisions
    )
```

Old→new for §3.2:
- (c) guard: the two `if ... return False` early-outs on `matched_override` and
  `override_table_implemented` REPLACE the prior `may_touch AND NOT implemented` boolean pair (the
  guard's own committed comment states this; M5-T040 G3 A3). The safe path now keys on
  `override_table_implemented`, so the inconsistent hand-built `may_touch=False/implemented=False`
  status no longer clears — tighten-only; every shape the builder emits is unaffected.
- (d) empty-decisions: the final return is `bool(decisions) and all(...)`. The prior form was the
  bare `all(d.decision_state in (DECISION_WIDE, DECISION_NARROW) for d in decisions)` (the `all(...)`
  clause is preserved verbatim); the added `bool(decisions) and` prefix makes the empty set return
  False instead of the vacuous True (M5-T040 G3 A4).

Named-pending derivation (c), NEW verbatim (`:324`): `named_pending = not
named_street_override.override_table_implemented`. Per the committed comment at `:318-323` the prior
derivation was the `may_touch AND NOT implemented` pair; the safe (not-pending) path now REQUIRES
`override_table_implemented=True`. Verbatim old bytes: supervisor diff (§5).

Wording (b), NEW verbatim (branch-4 reason, `:421-430`):

```python
    reason=(
        "a candidate segment may fall under the ZR 12-10 named-street override / "
        "C5-3/C6-4/C6-6 alternate-width table (Broadway W94-97 CD7; Allen St "
        "Rivington-Delancey CD3): the named-street override matcher was consulted but "
        "could not resolve the candidate segment (missing community district or "
        "cross-street bounds, or an indeterminate locator), so the override exception is "
        "unresolved; exceptions_checked cannot be asserted and the wide-street FAR is "
        "withheld - professional review required"
    ),
```

The module docstring `:48-61` likewise states the ZR 12-10 table "IS consulted here" and a candidate
"could not resolve" fails safe. Per M5-T040 G3 A1/A2 the prior docstring/reason used "not
implemented" phrasing; grep of both rules modules for `not implemented` / `out-of-scope` /
`follow-up` is now clean (AS-4). Verbatim old bytes: supervisor diff (§5).

### 3.3 `services/api/tests/rules/test_wide_street_wiring.py` — fixtures + regression tests (DB-028 a,c,d)

Fixtures, NEW verbatim (`:107-124`):

```python
OVERRIDE_CLEAR = NamedStreetOverrideStatus(
    override_table_implemented=True, segment_may_touch_named_override=False,
    note="every candidate segment resolved NOT_MATCHED with fully-resolved inputs",
)
# DB-028(c): hand-built inconsistent status build_named_street_override_status never emits;
# the hardened guard must NOT let it clear the elevated exceptions_checked criterion.
OVERRIDE_NOT_IMPLEMENTED = NamedStreetOverrideStatus(
    override_table_implemented=False, segment_may_touch_named_override=False,
    note="hand-built inconsistent status: override table not applied, no touch flagged",
)
```

`OVERRIDE_CLEAR` fixture correction (reviewer aid): it now models
`override_table_implemented=True, segment_may_touch_named_override=False` — the genuinely-resolved
shape the builder emits for the all-clear path. Under the prior boolean-pair guard an
`implemented=False` fixture cleared only because `may_touch=False`; the hardened guard keys on
`implemented`, so the fixture now models the real cleared status. Consumer behavior for that path is
preserved (§4 cmd 2 green).

Regression tests, NEW verbatim (`:481-534`):

```python
def test_db028a_named_street_status_extracted_with_compatibility_facade() -> None:
    from app.rules import named_street_override_status as submodule
    from app.rules import wide_street_wiring as facade
    for name in ("MatchedNamedStreetOverride", "NamedStreetOverrideStatus",
                 "build_named_street_override_status"):
        assert getattr(facade, name) is getattr(submodule, name)
        assert name in facade.__all__
        assert name in submodule.__all__

def test_db028c_hand_built_not_implemented_status_never_clears_guard() -> None:
    result = determine_wide_street_far(
        [_wide_decision()], lot=_make_lot(), wide_segments=[_within_segment()],
        ec5_preconditions=EC5_CHECKED, named_street_override=OVERRIDE_NOT_IMPLEMENTED,
        correlation_id=CID,
    )
    assert result.exceptions_checked is False
    assert result.named_street_override_pending is True
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW

def test_db028d_no_policy_decisions_reports_exceptions_checked_false() -> None:
    result = determine_wide_street_far(
        [], lot=_make_lot(), wide_segments=[], ec5_preconditions=EC5_CHECKED,
        named_street_override=OVERRIDE_CLEAR, correlation_id=CID,
    )
    assert result.determination_state == DETERMINATION_PROFESSIONAL_REVIEW
    assert result.exceptions_checked is False
```

### 3.4 `services/api/tests/spatial/test_wide_street_live_provider.py` — provider fail-safe test (DB-028e)

NEW verbatim (`:568-602`); the provider source itself is out of scope and unchanged — this test
forces the pre-existing matcher-load-failure branch:

```python
def test_db028e_named_street_matcher_load_failure_fails_safe_unresolved(monkeypatch, caplog) -> None:
    provider._named_street_matcher.cache_clear()
    def _raising_loader() -> None:
        raise RuntimeError("named-street snapshot store unavailable")
    monkeypatch.setattr(provider, "load_default_matcher", _raising_loader)
    seg_result = SimpleNamespace(
        segments=[SimpleNamespace(borough="Manhattan", street_name="Broadway")]
    )
    try:
        with caplog.at_level(logging.WARNING, logger="app.spatial.wide_street_live_provider"):
            status = provider._named_street_override_status(seg_result, CID)
    finally:
        provider._named_street_matcher.cache_clear()
    assert status.override_table_implemented is False
    assert status.segment_may_touch_named_override is True
    assert status.matched_override is None
    assert "could not be loaded" in (status.note or "")
    lines = _fail_safe_lines(caplog)
    assert any("event=named_override_matcher_unavailable" in line for line in lines)
    assert any("error_type=RuntimeError" in line for line in lines)
```

### 3.5 `apps/web/src/components/architect/CalculationEvidence.tsx` — web fallback wording (DB-028h)

NEW verbatim (`:44`, the defensive null-FAR fallback branch):

```tsx
<p className="section-note">{wideValueLabel} (dimensionless ratio): {wideReview ? "withheld — professional review required" : (evaluation.wide_street.governing_max_residential_far ?? "Not calculated")}. Floor area is derived as FAR × zoning-lot area (sq ft).</p>
```

Only the `??` fallback is changed: a CONFIRMED (non-review) determination whose FAR is nonetheless
absent now reads `"Not calculated"` (matching `DevelopmentLimits`) instead of a professional-review
phrase, so no non-review `determination_state` can render "professional review required". The review
case (`wideReview`) still reads "withheld — professional review required" — unchanged. Per M5-T040
HJ A1 the prior fallback borrowed the professional-review phrase; verbatim old bytes: supervisor diff
(§5).

### 3.6 `apps/web/src/components/architect/__tests__/report-view.test.tsx` — web assertion (DB-028h)

NEW verbatim (`:169-182`):

```tsx
it("renders the defensive null-FAR fallback as 'Not calculated', never a professional-review phrase, for a non-review determination (DB-028h)", () => {
    const profile = baseProfile();
    const doc = wideStreetDoc(profile.identity.bbl); // within_100ft_of_wide_street (a non-review state)
    doc.wide_street!.governing_max_residential_far = null;
    render(<ReportView profile={profile} scenario={null} evaluation={doc} label="Test property" />);
    const provenance = screen.getByTestId("wide-street-provenance");
    expect(provenance).toHaveTextContent("Wide-street conditional FAR (dimensionless ratio): Not calculated");
    expect(provenance).not.toHaveTextContent("withheld — professional review required");
    expect(provenance).not.toHaveTextContent("Professional review required");
});
```

## 4. Commands run — worker run in this worktree (documented_test_commands; cwd explicit)

Commands 1–4 ran from `services/api` (`cd services/api` first — worker confirmed cwd
`/c/Users/MLFLL/Downloads/nyc-zoning/wt-m5t043/services/api`); command 5 ran from the repo root
(`cd ../..` — confirmed cwd `/c/Users/MLFLL/Downloads/nyc-zoning/wt-m5t043`). Each documented command
was run verbatim and alone — nothing chained onto it. Exit status read from each tool's own
result line.

| # | cwd | command | actual outcome |
|---|-----|---------|--------|
| 1 | `services/api` | `python -m ruff check .` | `All checks passed!` (exit 0) |
| 2 | `services/api` | `python -m pytest tests/rules/test_wide_street_wiring.py tests/rules/test_named_street_override.py -q` | `101 passed in 0.78s` |
| 3 | `services/api` | `python -m pytest tests/spatial/test_wide_street_live_provider.py -q` | `39 passed in 0.32s` |
| 4 | `services/api` | `python -m pytest tests/api tests/rules/test_rules_integration.py -q` | `475 passed in 18.80s` |
| 5 | repo root | `python tools/modularity_check.py --check` | `selected 444 files; failures 0; warnings 21` — `wide_street_wiring.py` NOT among the 21 warns (extraction dropped it off) |

The 21 modularity warns are pre-existing and out of scope (unchanged by this task): they name
`scenario_analysis.py`, several `connectors/*`, `rules/integration.py`, `rules/named_street_override.py`
(the pre-existing matcher, a DIFFERENT file from the new `named_street_override_status.py`, which is
under threshold), `scenario/breakeven.py`, `surveyReview/types.ts`, and ten `tools/agent_supervisor/*`
files. No root-level lint finding was repaired and no `tools/agent_supervisor/*` (supervisor tooling)
file was edited — both are out of scope per the packet.

Supervisor reproduction of these five commands (with cwd) and the authoritative blob digests are
captured at the frozen head by the orchestrator/supervisor, not asserted here.

## 5. Evidence digest manifest (supplementary; supervisor binds authoritative)

The reviewable source is embedded in §3; this manifest is supplementary provenance, NOT a substitute
for the code. The supervisor binds the authoritative new-side blob SHAs and the verbatim old→new
`git diff` at the frozen head (LF-normalized; git is orchestrator-only, ADR-005).

| DB-028 evidence | file | §3 | worker-read new-side blob (advisory) |
|---|---|---|---|
| extraction target + facade bodies | `services/api/app/rules/named_street_override_status.py` | §3.1 | `2a9a02bb` |
| facade re-export + guard(c) + named_pending(c) + empty-decisions(d) + wording(b) | `services/api/app/rules/wide_street_wiring.py` | §3.2 | `4cb7021d` |
| regression tests db028a/c/d + fixtures | `services/api/tests/rules/test_wide_street_wiring.py` | §3.3 | `d7a52816` |
| provider fail-safe test db028e | `services/api/tests/spatial/test_wide_street_live_provider.py` | §3.4 | `70ac3cf7` |
| web fallback wording (h) | `apps/web/src/components/architect/CalculationEvidence.tsx` | §3.5 | `b0c47f33` |
| web fallback assertion (h) | `apps/web/src/components/architect/__tests__/report-view.test.tsx` | §3.6 | `f6a19fd9` |

## 6. Pending — web / push / CI (explicit)

- The vitest web suite (`report-view.test.tsx`, AS-6/AS-8) is **NOT run locally** (thin client; web
  behavior proves ONLY in CI on the pushed head — CODING_RULES). Local review of the render logic
  (`CalculationEvidence.tsx:41-44`; the non-review fixture and phrase-free `reason` /
  `fallback_direction_note`) is a pre-check, not verification.
- Push and CI capture are the orchestrator's (ADR-005). AS-6 and AS-8 stay PENDING until the
  orchestrator supplies CI results for the committed changes. Do not read this report as green CI.

## 7. Discovery routing (D-069)

No out-of-scope defects found; no implementation defect is established by the visible packet. The
modularity warn list (21) is pre-existing and out of scope (unchanged by this task);
`wide_street_wiring.py` improved off it.
