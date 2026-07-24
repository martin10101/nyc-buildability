# M3-T001 — Producer report (evidence for G0–G5)

**Task:** M3-T001 — Legal-source authority hierarchy, corpus scope, coverage matrix, and internal
legal-source manifest contract. **Directive:** D-002 (regime v1.0; `D-002:ALL`). **Producer:**
official-source-researcher (this tab). **Branch:** `task/M3-T001-legal-source-authority`. **Frozen base:**
`cc142081336f2dac0854a947694fec33559dcc8a` (post-D-002-consolidation main). **Role:** producer — this
report is evidence for an **independent** gate; the producer does not self-accept.

> Producer-discipline attestation (D-002 R036–R039, R051–R060): only this task's allowed paths and this one
> report path were modified; no runtime code, no canonical contract, no shared hotspot, no other task's
> files, no control CLI. The new `legal_source_manifest.schema.json` is an interface *addition*, not a
> change to a frozen shared contract; no interface-change request was required.

---

## 1. Deliverables produced (G0 inputs/outputs satisfied)

| Output | Path | Acceptance |
|---|---|---|
| Source authority policy | `docs/SOURCE_AUTHORITY_POLICY.md` | AS-1, AS-8, NC-3 |
| Legal-corpus coverage matrix | `docs/LEGAL_CORPUS_COVERAGE_MATRIX.md` | AS-2, AS-3, AS-4, AS-9, NC-1 |
| Document evidence policy | `docs/DOCUMENT_EVIDENCE_POLICY.md` | AS-12 |
| Construction-code release scope (DRAFT) | `docs/CONSTRUCTION_CODE_RELEASE_SCOPE.md` | AS-10 (B-011) |
| Source access registry (additive) | `docs/SOURCE_ACCESS_REGISTRY.md` §9–§10 | AS-5, AS-6, NC-3 |
| Legal-source manifest schema | `packages/contracts/schemas/v1/legal_source_manifest.schema.json` | AS-11 |
| Manifest fixtures (2 positive, 8 negative) | `packages/contracts/schemas/v1/fixtures/legal_source_manifest/{positive,negative}/` | AS-11 |
| Self-check harness | `packages/contracts/schemas/v1/fixtures/legal_source_manifest/check_m3_t001.py` | AS-4, AS-11, AS-12, NC-2 |
| Architect benchmark analysis | `project-control/reports/M3-T001-architect-benchmark-analysis.md` | AS-7, NC-1, NC-2 |
| This producer report | `project-control/reports/M3-T001-producer-report.md` | G0–G5 evidence |

**Acceptance-scenario → evidence map** (full AS-1…AS-12, NC-1…NC-3): §5.

---

## 2. G2 — producer self-check (executable, reproducible)

### 2.1 Manifest schema + fixtures + doc invariants (single harness)

Command (repo root = worktree root):

```
python packages/contracts/schemas/v1/fixtures/legal_source_manifest/check_m3_t001.py
```

Output (authoritative final run):

```
schema sha256: 9b153e907999e2938fe4ad77e2b4e0daaac7541a20bcd9278064748e89f44210

[PASS] AS-11a schema meta-validates (Draft 2020-12)
[PASS] AS-11d deterministic $id + x-contract-version constants - $id_ok=True version_ok=True sha256=9b153e90...f44210
[PASS] AS-11b positive validates: upcodes_reference_only.json
[PASS] AS-11b positive validates: zr_portal_html.json
[PASS] AS-11c negative rejected: bad_raw_hash_format.json - rejected on: ... does not match '^sha256:...'
[PASS] AS-11c negative rejected: bad_status_enum.json - rejected on: 'verified' is not one of [...]
[PASS] AS-11c negative rejected: missing_corpus_version.json - rejected on: 'corpus_version' is a required property
[PASS] AS-11c negative rejected: missing_provenance.json - rejected on: 'provenance' is a required property
[PASS] AS-11c negative rejected: missing_provenance_source_id.json - rejected on: 'source_id' is a required property
[PASS] AS-11c negative rejected: missing_raw_sha256.json - rejected on: 'raw_sha256' is a required property
[PASS] AS-11c negative rejected: provenance_tier_out_of_range.json - rejected on: 8 is greater than the maximum of 7
[PASS] AS-11c negative rejected: unknown_top_level_field.json - rejected on: Additional properties are not allowed ('unexpected_field')
[PASS] AS-11 fixtures summary - 2 positive / 8 negative
[PASS] AS-12 prohibited claims only appear as prohibitions
[PASS] AS-4 no aggregate complete/compliant/buildable guarantee
[PASS] NC-2 no PDF committed anywhere in tree
[PASS] NC-2 no inferred BBL/address in benchmark analysis

============================================================
TOTAL: 17 checks, 0 failed
(exit 0)
```

(Console renders the separator em-dash as `-` above; the schema SHA-256 is printed on every run so
byte-identity across reruns is visible — AS-11d.)

This one harness proves AS-11a (schema meta-validates), AS-11b (positives validate), AS-11c (negatives
each rejected on the isolated missing/invalid field), AS-11d (deterministic `$id` + `x-contract-version`;
schema SHA-256 printed for byte-identity across reruns), AS-4 (no aggregate complete/compliant/buildable
guarantee), AS-12 (prohibited claims only appear as prohibitions), and NC-2 (no PDF committed; no inferred
BBL/address in the benchmark analysis).

### 2.2 Registry additive-only proof (existing accepted rows byte-unchanged, AS-5)

The pre-existing `docs/SOURCE_ACCESS_REGISTRY.md` content is preserved byte-for-byte; only new sections
§9–§10 were appended (CRLF-consistent).

```
$ git diff --numstat HEAD -- docs/SOURCE_ACCESS_REGISTRY.md
121     0       docs/SOURCE_ACCESS_REGISTRY.md          # 121 added, 0 removed

$ git diff HEAD -- docs/SOURCE_ACCESS_REGISTRY.md | grep -c '^-[^-]'
0                                                       # zero deletion/modification lines

$ git diff HEAD -- docs/SOURCE_ACCESS_REGISTRY.md | grep '^@@'
@@ -201,3 +201,124 @@ ...                               # single hunk appended at EOF
```

The change is purely additive (single append hunk at end of file; 0 existing lines removed or modified),
so every existing accepted registry row is byte-unchanged (AS-5). (Pre-append the working-tree prefix was
also verified SHA-256-identical before/after the append.)

### 2.3 No typegen / schema-bundle impact (contract §Generated artifacts)

`legal_source_manifest.schema.json` is **not** in the `SCHEMA_FILES` allowlist of
`packages/contracts/scripts/generate_ts_types.py` or `services/api/scripts/sync_contract_schemas.py`, so it
is not a TypeScript typegen target and not part of the runtime schema bundle. Adding it changes no generated
artifact.

```
$ grep -c legal_source_manifest packages/contracts/scripts/generate_ts_types.py
0
$ grep -c legal_source_manifest services/api/scripts/sync_contract_schemas.py
0
```

Both generators use explicit `SCHEMA_FILES` allowlists (property_profile / source_fact / common /
coverage_status / rule_evaluation / scenario); `legal_source_manifest.schema.json` is in neither, so it is
not TypeScript-generated and not part of the runtime `_contract_schemas` bundle.

### 2.4 No new runtime dependency

The harness imports only the standard library plus the already-installed `jsonschema` (4.26.0). No
`requests`/`httpx`/UpCodes-SDK/scraping/AI framework is added. The docs describe M3-T005 channels but this
task ingests nothing and adds no connector.

---

## 3. G1 posture — source-identity honesty (for the data-contract-verifier gate)

- The six new DOB channels (§9) are recorded **"to verify at G1"** and, where identity/endpoint/access/
  terms/download URL is unresolved, explicitly **BLOCKED at G1 — not verified** (AS-6). No channel is
  presented as verified on faith; no live re-research was performed in this producer tab.
- ZoLa reaffirmed **presentation-only**; UpCodes recorded **reference-only** (tier 5), with dated
  API-availability note, subscription/pricing recorded as *not a fact to assert / not procured*, and
  "the program does not require it" (NC-3).
- The construction-code **edition + effective date are not guessed**; they are marked "to verify at G1"
  and read from the official source at M3-T005 (CLAUDE.md principle 3).

## 4. G3/G4/G5 posture (for the independent reviewers)

- **G3 (code-reviewer):** deliverables are documentation + one additive JSON Schema + fixtures + a stdlib
  harness. No runtime code paths. Internal consistency (single status vocabulary, single provenance-tier
  set, single prohibited-claims list) is enforced by cross-references and the harness.
- **G4 (control-plane / CI):** the harness is deterministic and runnable in CI; no control files were
  touched except this report and the benchmark analysis (both under the task's own report scope).
- **G5 (security-reviewer):** untrusted-document posture is stated in `DOCUMENT_EVIDENCE_POLICY.md` §5
  (capture-time vs parser-level controls; no PDF JS/attachment execution; prompt-injection isolation). No
  secrets, tokens, or credentials appear. The client PDF is **not committed** (NC-2). No paid service is
  introduced.

## 5. Acceptance-scenario → evidence map

| ID | Where satisfied |
|---|---|
| AS-1 | SOURCE_AUTHORITY_POLICY.md §1–§2 (7 tiers; "tier number is a provenance class, not a conflict winner") |
| AS-2 | LEGAL_CORPUS_COVERAGE_MATRIX.md §3 (every replan domain, exactly one status) |
| AS-3 | LEGAL_CORPUS_COVERAGE_MATRIX.md §3 (six actionable columns; every non-implemented row has task/blocker/continuing limitation + next action + reviewer) |
| AS-4 | LEGAL_CORPUS_COVERAGE_MATRIX.md §4 + harness AS-4 check |
| AS-5 | SOURCE_ACCESS_REGISTRY.md §9 (all six channels) + §10 (ZoLa/UpCodes); §2.2 byte-identity proof |
| AS-6 | SOURCE_ACCESS_REGISTRY.md §9 "BLOCKED at G1" dispositions; manifest `status: blocked_at_g1` |
| AS-7 | M3-T001-architect-benchmark-analysis.md (SHA + observations + 6 discrepancies; no conclusion; no identity) |
| AS-8 | SOURCE_AUTHORITY_POLICY.md §3 (precedence factors; amendment-becomes-law; project-specific control; unresolved→conflict/PRR; AI proposes only) |
| AS-9 | LEGAL_CORPUS_COVERAGE_MATRIX.md §2 (single vocabulary → runtime mapping; not_applicable only after resolution; unknown never not_applicable/false) |
| AS-10 | CONSTRUCTION_CODE_RELEASE_SCOPE.md (DRAFT; edition/as-of; claims; in-scope; channels; exclusions+blocked claims; B-011 gate) |
| AS-11 | legal_source_manifest.schema.json + fixtures + harness (a–e) |
| AS-12 | DOCUMENT_EVIDENCE_POLICY.md §1/§2/§4/§7 + harness AS-12 check |
| NC-1 | absence discipline in coverage matrix §3 note + benchmark analysis (no "confirmed absent") |
| NC-2 | harness NC-2 checks (no PDF; no inferred identity) |
| NC-3 | SOURCE_AUTHORITY_POLICY.md §2 rule 1 + registry §10 (UpCodes/ZoLa never controlling; no runtime dependency) |

## 6. Limitations / handoff

- The coverage matrix's "future task (unassigned)" rows carry explicit continuing limitations; they are
  **orchestrator** next-actions, not silently covered.
- B-011 (construction-code release scope) is a **owner decision**; the scope doc is a DRAFT with no
  authority until approved.
- Next dependency unlocked on acceptance: **M3-T002** (immutable capture) needs accepted M3-T001.
