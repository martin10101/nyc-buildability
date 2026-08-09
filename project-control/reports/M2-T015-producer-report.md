# M2-T015 producer report

Task: **M2-T015 — Secure survey ingestion, extraction, and deterministic verification (Packet B)**
Producer: supervised worker (Claude, `tools/agent_supervisor --mode supervised`), worktree `wt-m2t015`,
branch `task/M2-T015-survey-ingestion`. This report is the AOS §6 return packet, one section per unit.
Unit 1 (survey-evidence contract + fixtures) is committed at `cabe128` with its evidence in that
commit's message (orchestrator-verified `python .github/scripts/validate_contracts.py` → exit 0).

**Currency:** this report is current **through unit 3l + the G3/G5-gate rework of 2026-08-09**.
Section "Units 3a–3l — the deterministic ingestion/extraction pipeline" (below) consolidates the
implementation delivery; section "Rework 2026-08-09 — gate corrections 1–3" records the three
concrete corrections the 4-reviewer wave required (lint parity under pinned ruff 0.13.0, the named
synthetic fixture pack + matrix, and this report update). The reviewers found the pipeline
logic/security/contract SOUND (G1 PASS, G5 PASS, G3 ruled the logic correct); the rework changed **no
pipeline behavior** and left every existing passing assertion byte-for-byte intact.

---

## Unit 2 — architecture + threat model + isolation-terminology reconciliation (2026-08-08)

**Status requested:** `awaiting_gate` — file artifacts complete in the worktree; the commit and the
validator re-run must be executed/captured by the orchestrator (producer sandbox is read-only for
git-write and python; denials recorded verbatim in §U2.6 below, per the standing evidence-capture
division of labor and the unit-1 precedent).

### U2.1 Scope-authorization resolution (requested action, item 1)

The forwarded action said to obtain orchestrator authorization **if** the schema path were outside
this unit's allowed paths. It is not: `packages/contracts/schemas/v1/survey_evidence.schema.json`
appears verbatim in the forwarded packet's PERMITTED PATHS and in the task file
(`project-control/tasks/M2-T015.json`, `allowed_paths`: "packages/contracts/schemas/v1/
survey_evidence.schema.json + its generated artifacts via the M2-T010 tooling"). **No scope
expansion was needed; no out-of-scope path was touched.**

### U2.2 Files changed (this unit)

| File | Change |
| --- | --- |
| `docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md` | NEW (unit-2 artifact, previously untracked) — canonical pipeline, parser isolation boundary §5, digest discipline, storage design, state machine. |
| `docs/UPLOAD_THREAT_MODEL.md` | NEW (unit-2 artifact, previously untracked) — threat catalog T01–T11, control matrix, residual risks for G5. |
| `packages/contracts/schemas/v1/survey_evidence.schema.json` | One description string reworded (`extraction_run_id`); no key, type, `$ref`, enum, or constraint changed. |
| `docs/SURVEY_EVIDENCE_CONTRACT.md` | One table cell reworded (§3 identity table, `extraction_run_id` row) to match. |
| `project-control/reports/M2-T015-producer-report.md` | NEW — this report. |

### U2.3 Contracts/schema changed — and why no version bump

The `survey_evidence.schema.json` change edits **only the human-readable `description`** of the
optional `extraction_run_id` property. No structural keyword changes: property set, `required`,
types, `$ref` targets, patterns, enums, and `additionalProperties: false` are all byte-identical
(see the exact diff in §U2.6, command 4). Validation semantics are provably unchanged — every
fixture verdict is identical. This contract was **created by unit 1 of this same task and has not
yet passed any gate or been accepted**; refining its prose before first acceptance is in-task
authoring, not a change to a published contract, so no version bump is required. (Post-acceptance,
the additive-change + version-bump rule of `.claude/rules/backend-api.md` applies.)

**Before (schema, line 141):**

> "OPTIONAL identifier of the extraction run (one **sandboxed processing job** over one document); …"

**After (schema, line 141):**

> "OPTIONAL identifier of the extraction run (one **isolated processing job** over one document -
> a job that runs only inside the verified, fail-closed parser isolation boundary of
> docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md section 5, kernel-enforced and proven by a
> capability probe; a plain child process is never that boundary, and when the boundary cannot be
> verified parsing is disabled with a typed isolation_unavailable outcome, so no run - and
> therefore no run id - can ever come from unisolated parsing); …" (traceability tail unchanged)

**Before (contract doc, §3 table):** "One sandboxed processing job; shared by all facts it produced …"

**After (contract doc, §3 table):** "One isolated processing job over one document, run only inside
the verified, fail-closed parser isolation boundary (`docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md`
§5) — never a plain, merely-separated child process; when the boundary cannot be verified, parsing
is disabled (typed `isolation_unavailable`) and no run id is ever minted. Shared by all facts the
run produced …"

### U2.4 Terminology reconciliation — every sandbox/isolation reference, with meaning

Post-edit, every match of `sandbox`/`isolat` (case-insensitive) across the four artifacts and the
survey_evidence fixture directories falls into exactly one of five consistent meanings; none
conflicts with another (full raw match lists: §U2.6, commands 2–3):

| # | Meaning | Occurrences | Consistency statement |
| --- | --- | --- | --- |
| 1 | **The §5 parser isolation boundary** — kernel-enforced filesystem allowlist (Landlock) + network denial (seccomp), proven by a fail-closed capability probe; the only condition under which untrusted bytes are decoded. | Architecture §§2 (S2/S4 rows), 5, 12; Threat model §§1–5 (T06, control inventory, residual risk 3, fixture notes); Contract doc §3 row; Schema `extraction_run_id` description. | All sites describe the SAME boundary with the same two kernel-enforced properties and the same verification requirement; the schema and contract doc now cite architecture §5 rather than asserting their own model. |
| 2 | **`isolation_unavailable`** — the typed fail-closed outcome when the boundary cannot be verified: parsing disabled, documents rest in `uploaded`, blocker surfaced, S2–S8 do not run, **no unisolated fallback**, and (schema/contract doc) therefore no `extraction_run_id` is ever minted. | Architecture §§2, 5; Threat model T06, §5.3, fixture notes; Contract doc §3 row; Schema description. | Identical behavior at every site; the reworded schema/contract text PRESERVES this behavior and adds the contract-side corollary (no run id without a verified boundary). |
| 3 | **Negative sandbox statements** — a plain child process is *not* the boundary and is deliberately never called a sandbox; process separation is defense-in-depth only and never enables parsing. | Architecture §5 (line 111); Threat model §5.3 (line 108); restated in word form ("a plain child process is never that boundary") in the schema description and contract-doc row. | These are the two intentional remaining uses of the word "sandbox(ed)" in the docs — both NEGATIVE, i.e., they forbid exactly the claim the old wording made. No artifact any longer describes any runtime process as "sandboxed". |
| 4 | **Tenant isolation** — confidentiality separation between tenants (RLS / storage policy), a different axis from parser isolation, always qualified by "tenant". | Threat model A1, §5.1; Architecture §7 (storage/RLS). | Never used for the parser boundary; unambiguous in context. |
| 5 | **Format-admission "sandboxing" feasibility** — `fixtures/invalid/survey_evidence/unapproved_extraction_method.json` paraphrases `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md` row 7's rationale for DEFERRING native DWG ("proprietary, licensing/sandboxing/testability unproven"): whether a third-party toolchain could feasibly be confined **at all** is an admission criterion for a format. | One fixture `_expected_failure` narrative. | This is a faithful paraphrase of an out-of-scope input document (M2-T014 output; not in this unit's permitted paths), describes toolchain-confinement feasibility, and makes no claim that any runtime process is a sandbox. Left unchanged deliberately; if the orchestrator wants the format policy's own vocabulary migrated, that is an M2-T014-owned follow-up, not a unit-2 edit. |

`packages/contracts/generated/survey_evidence.ts` (also a permitted path) **does not exist yet** —
the M2-T010 generation tooling has not been run for this contract — so there is no generated
artifact to reconcile; when it is first generated it will inherit the corrected description.

### U2.5 Fail-closed behavior preservation (requested action, item 4)

The `isolation_unavailable` / parsing-disabled semantics are untouched: architecture §5
("There is **no fallback to unisolated parsing**", worker refuses jobs, typed outcome, blocker
surfaced) and threat model §5.3 (availability loss, never silent unisolated parsing) are exactly as
authored; the reworded schema/contract text *strengthens* the linkage by stating that no
`extraction_run_id` can exist unless the verified boundary admitted the job.

### U2.6 Commands run — exact output

All commands below ran in `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m2t015` on 2026-08-08. The
producer sandbox auto-permits only enumerated read-only git commands; every other execution
attempt is recorded verbatim under "denied" below.

**(1) Status / SHA / branch at unit start (before edits; the two docs were untracked unit-2 output):**

```
> git status; git log --oneline -3; git rev-parse HEAD; git branch --show-current
On branch task/M2-T015-survey-ingestion
Your branch is up to date with 'origin/task/M2-T015-survey-ingestion'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md
	docs/UPLOAD_THREAT_MODEL.md

nothing added to commit but untracked files present (use "git add" to track)
cabe128 M2-T015 unit 1 (supervised-auto): survey-evidence contract + fixtures
d2b6e87 Merge pull request #189 from martin10101/control/supervised-auto-activation-capture
88117e5 D-010: source-023 captured (owner SUPERVISED-AUTO activation decision 2026-08-08; R214-R235)
cabe12866b7257fd9e046b8e90d1bdc1500206c4
task/M2-T015-survey-ingestion
```

**(2) Post-edit terminology search — `sandbox` (case-insensitive, includes untracked):**

```
> git grep -n -i --untracked -e sandbox -- docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md docs/UPLOAD_THREAT_MODEL.md docs/SURVEY_EVIDENCE_CONTRACT.md packages/contracts/schemas/v1/survey_evidence.schema.json packages/contracts/fixtures/valid/survey_evidence packages/contracts/fixtures/invalid/survey_evidence
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:111:process is **not** that boundary and is never described as sandboxed; process separation is
docs/UPLOAD_THREAT_MODEL.md:108:   defense-in-depth only and is not called a sandbox and never enables parsing by itself.
packages/contracts/fixtures/invalid/survey_evidence/unapproved_extraction_method.json:2:  "_expected_failure": "M2-T015: extraction_method 'native_dwg_parse' is not in the CLOSED extraction-path enum. docs/SURVEY_DOCUMENT_FORMAT_POLICY.md row 7 DEFERS native DWG parsing (proprietary format, licensing/sandboxing unproven); an unapproved or improvised extraction path can never be recorded as the provenance of a survey fact.",
```

Three matches, all accounted for in §U2.4 (meanings 3, 3, 5). Zero positive "sandboxed process/job"
claims remain in any artifact.

**(3) Post-edit terminology search — `isolat` (case-insensitive, includes untracked):** 33 matches;
every match is meaning 1, 2, or 4 of §U2.4. Raw output (abridged only by nothing — this is the
complete match list):

```
> git grep -n -i --untracked -e isolat -- docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md docs/UPLOAD_THREAT_MODEL.md docs/SURVEY_EVIDENCE_CONTRACT.md packages/contracts/schemas/v1/survey_evidence.schema.json packages/contracts/fixtures/valid/survey_evidence packages/contracts/fixtures/invalid/survey_evidence
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:46:| S2 | **Security screen** (async, isolated) | Render worker — isolated parser process (§5) | ...
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:48:| S4 | **Extraction** (isolated) | Isolated parser process | Per-format extraction (§3) inside the parser isolation boundary and resource-limit model (§5). ...
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:55:Stages S2–S4 decode untrusted bytes and run **only** inside the §5 parser isolation boundary.
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:57:refused with a typed `isolation_unavailable` outcome — documents rest in `uploaded`, an
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:58:operational blocker is surfaced, and S2–S8 do not run (§5). There is no unisolated fallback.
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:107:## 5. Parser isolation boundary and resource-limit model
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:109:All parsing/decoding of untrusted bytes runs in a **dedicated isolated parser process** on the
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:110:worker, behind an isolation boundary with two **kernel-enforced** properties. A plain child
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:116:1. **Filesystem isolation.** The parser process cannot read any filesystem path outside an
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:129:process applies the full isolation policy, then attempts (a) reading a canary path outside the
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:130:allowlist and (b) an outbound connection. If either attempt succeeds — or the isolation
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:132:the worker refuses to claim extraction jobs, each refusal is a typed `isolation_unavailable`
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:136:There is **no fallback to unisolated parsing**.
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:142:substrate and the probe evidence is recorded, or (b) an isolated worker/container boundary — a
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:146:of extraction availability, never silent unisolated parsing. Verifying or provisioning the
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:149:**Defense-in-depth on the isolated process** (required in addition to, never instead of, the
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:265:  evidence storage, added by migration with tested RLS; tenant isolation scopes documents to the
docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md:354:| Security screen, extraction, reconstruction, checks | Render worker — isolated parser processes per §5; parsing stays disabled until the §5 boundary is verified on the substrate |
docs/SURVEY_EVIDENCE_CONTRACT.md:69:| Extraction run | `extraction_run_id` (optional) | One isolated processing job over one document, run only inside the verified, fail-closed parser isolation boundary (`docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md` §5) — never a plain, merely-separated child process; when the boundary cannot be verified, parsing is disabled (typed `isolation_unavailable`) and no run id is ever minted. Shared by all facts the run produced (analogous to the retrieval-event segment of `source_fact.observation_id`). |
docs/UPLOAD_THREAT_MODEL.md:6:**Companions:** `docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md` (pipeline, parser isolation
docs/UPLOAD_THREAT_MODEL.md:15:In scope: the upload endpoint, security screening, isolated extraction, deterministic
docs/UPLOAD_THREAT_MODEL.md:23:  their *confidentiality* (tenant isolation) and their *integrity* (immutability, digests).
docs/UPLOAD_THREAT_MODEL.md:31:  the isolated parser process holds none, and the §5-referenced filesystem allowlist makes
docs/UPLOAD_THREAT_MODEL.md:36:Trust boundaries: client → API upload gate; API → job queue → worker; worker parent → isolated
docs/UPLOAD_THREAT_MODEL.md:62:| T06 | **Parser exploitation** | ... | Parser isolation boundary (architecture §5): kernel-enforced filesystem allowlisting ... **parsing is disabled** (typed `isolation_unavailable`, documents rest in `uploaded`, blocker surfaced), never run behind a plain child process; defense-in-depth on the isolated process: ... | SB-S6 (regression backstop SB-S9) |
docs/UPLOAD_THREAT_MODEL.md:74:| Structural validation; active-content screen; page/pixel/bomb bounds | Worker security screen (S2), inside the §5 isolation boundary | Architecture §2, §5 |
docs/UPLOAD_THREAT_MODEL.md:76:| Parser isolation boundary: kernel-enforced FS allowlist + network denial, fail-closed capability probe (parsing disabled when unproven); rlimits, timeouts, no-secrets process, structured output | Worker parent ↔ isolated parser process (S2–S4) | Architecture §5 |
docs/UPLOAD_THREAT_MODEL.md:88:   and its deny-overwrite policy (T05/T10 hardening), tenant-isolation RLS, retention/quota
docs/UPLOAD_THREAT_MODEL.md:98:3. **Parser isolation depends on kernel features not yet verified on Render.** The §5 boundary
docs/UPLOAD_THREAT_MODEL.md:103:   running substrate, and until it does — or until an isolated worker/container boundary (a
docs/UPLOAD_THREAT_MODEL.md:107:   unisolated parsing. A plain child process (no secrets, rlimits, structured output) is
docs/UPLOAD_THREAT_MODEL.md:130:- Isolation-boundary fixtures (SB-S6) exercise the capability probe both ways: policy applied
docs/UPLOAD_THREAT_MODEL.md:132:  unsupported kernel → typed `isolation_unavailable`, no byte decoded.
packages/contracts/schemas/v1/survey_evidence.schema.json:141:      "description": "OPTIONAL identifier of the extraction run (one isolated processing job over one document - a job that runs only inside the verified, fail-closed parser isolation boundary of docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md section 5, kernel-enforced and proven by a capability probe; a plain child process is never that boundary, and when the boundary cannot be verified parsing is disabled with a typed isolation_unavailable outcome, so no run - and therefore no run id - can ever come from unisolated parsing); all facts produced by the same run share it, so a whole extraction can be traced, reviewed, or superseded together (analogous to the retrieval-event segment of source_fact.observation_id). A re-extraction of the same document mints a NEW run id and NEW evidence records; it never mutates existing ones."
```

(Three long table rows above — architecture 46, threat model 62, and the two doc rows marked "..." —
are elided mid-cell for line length ONLY in this report; the reviewer reproduces the full lines with
the same command at the committed SHA. No match line is omitted.)

**(4) Exact working-tree diff of the two tracked-file edits:**

```
> git diff
diff --git a/docs/SURVEY_EVIDENCE_CONTRACT.md b/docs/SURVEY_EVIDENCE_CONTRACT.md
index 74a8e1e..63d947b 100644
--- a/docs/SURVEY_EVIDENCE_CONTRACT.md
+++ b/docs/SURVEY_EVIDENCE_CONTRACT.md
@@ -66,7 +66,7 @@ Three permanent rules shape every field:
-| Extraction run | `extraction_run_id` (optional) | One sandboxed processing job; shared by all facts it produced (analogous to the retrieval-event segment of `source_fact.observation_id`). |
+| Extraction run | `extraction_run_id` (optional) | One isolated processing job over one document, run only inside the verified, fail-closed parser isolation boundary (`docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md` §5) — never a plain, merely-separated child process; when the boundary cannot be verified, parsing is disabled (typed `isolation_unavailable`) and no run id is ever minted. Shared by all facts the run produced (analogous to the retrieval-event segment of `source_fact.observation_id`). |
diff --git a/packages/contracts/schemas/v1/survey_evidence.schema.json b/packages/contracts/schemas/v1/survey_evidence.schema.json
index d1a370b..9127a97 100644
--- a/packages/contracts/schemas/v1/survey_evidence.schema.json
+++ b/packages/contracts/schemas/v1/survey_evidence.schema.json
@@ -138,7 +138,7 @@
-      "description": "OPTIONAL identifier of the extraction run (one sandboxed processing job over one document); all facts produced by the same run share it, so a whole extraction can be traced, reviewed, or superseded together (analogous to the retrieval-event segment of source_fact.observation_id). A re-extraction of the same document mints a NEW run id and NEW evidence records; it never mutates existing ones."
+      "description": "OPTIONAL identifier of the extraction run (one isolated processing job over one document - a job that runs only inside the verified, fail-closed parser isolation boundary of docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md section 5, kernel-enforced and proven by a capability probe; a plain child process is never that boundary, and when the boundary cannot be verified parsing is disabled with a typed isolation_unavailable outcome, so no run - and therefore no run id - can ever come from unisolated parsing); all facts produced by the same run share it, so a whole extraction can be traced, reviewed, or superseded together (analogous to the retrieval-event segment of source_fact.observation_id). A re-extraction of the same document mints a NEW run id and NEW evidence records; it never mutates existing ones."
```

(Context lines omitted here for length; the hunks contain no other +/- lines. `git diff` also
printed the standard Windows `warning: LF will be replaced by CRLF` notice for both files —
autocrlf display noise, not a content change; unit-1 files committed identically from this
environment.)

**Denied in the producer sandbox (verbatim policy responses; ASK-tier, never AUTO):**

```
> bash: cd ... && python .github/scripts/validate_contracts.py
the command is not an enumerated read-only git command and is not a packet-documented test command

> powershell: python .github/scripts/validate_contracts.py
the policy cannot confidently classify a 'unknown' request ('PowerShell'); unclassifiable means ASK, never AUTO

> powershell: git add docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md docs/UPLOAD_THREAT_MODEL.md docs/SURVEY_EVIDENCE_CONTRACT.md packages/contracts/schemas/v1/survey_evidence.schema.json; git status --short
the policy cannot confidently classify a 'unknown' request ('PowerShell'); unclassifiable means ASK, never AUTO
```

### U2.7 Tests / acceptance checks

| Check | Result | Evidence |
| --- | --- | --- |
| SB-S8 contract validation: `python .github/scripts/validate_contracts.py` (validates all 10 schemas incl. `survey_evidence` + every valid/invalid fixture in both directions) | **NOT RUN — producer sandbox denial (above)**; orchestrator capture requested, exactly as in unit 1 ("Checked 10 schema file(s); 0 failure(s)." exit 0 at `cabe128`) | Expected to pass: the schema diff is description-text-only (command 4), which the validator does not evaluate for instance verdicts; every keyword byte-identical. This is an EXPECTATION, not a claim of a passing run. |
| Terminology consistency sweep | PASS (producer self-check) | §U2.6 commands 2–3: zero positive "sandbox" claims; all isolation references map to §U2.4 meanings 1/2/4. |
| Fail-closed behavior preserved | PASS (producer self-check) | §U2.5; architecture §5 / threat model §5.3 passages untouched by this unit's edits (command 4 shows the only two modified lines). |

### U2.8 Assumptions and defaults

1. Unit-1 contract prose may be corrected pre-acceptance without a version bump (§U2.3 reasoning).
2. The fixture's format-policy paraphrase (meaning 5) is intentionally out of this unit's edit set.
3. ASCII-only text used inside the JSON schema description ("section 5", hyphens) matching the
   contract's existing house style; typographic §/— retained in the markdown docs, matching theirs.

### U2.9 Known limitations / open items for the orchestrator

1. **Commit + push (orchestrator/supervisor action):** stage exactly
   `docs/SURVEY_DOCUMENT_INGESTION_ARCHITECTURE.md`, `docs/UPLOAD_THREAT_MODEL.md`,
   `docs/SURVEY_EVIDENCE_CONTRACT.md`, `packages/contracts/schemas/v1/survey_evidence.schema.json`,
   `project-control/reports/M2-T015-producer-report.md` on `task/M2-T015-survey-ingestion`; record
   the resulting SHA so the independent security reviewer inspects committed content.
2. **Validator capture (orchestrator action):** run `python .github/scripts/validate_contracts.py`
   at that SHA and record the banner + exit code (unit-1 pattern).
3. `packages/contracts/generated/survey_evidence.ts` does not exist yet (M2-T010 tooling not yet run
   for this contract) — future unit, not a defect of this one.
4. `docs/SURVEY_FIXTURE_MATRIX.md` is a later-unit output; not part of this unit.
5. Follow-up candidate (M2-T014 scope, NOT this task): `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md`
   still uses "sandboxable/sandboxed" as admission-criterion vocabulary; if the owner wants the
   whole corpus migrated to boundary-verified vocabulary, that is a separate directive-bound edit.

### U2.10 Security / provenance impact

Positive: the contract no longer implies a "sandbox" guarantee the runtime does not make. The
enforceable claim (kernel-enforced, probe-verified, fail-closed §5 boundary) and the explicitly
non-sandbox child process are now distinguished in every artifact the G5 reviewer will read, and
the no-boundary → no-parse → no-run-id chain is stated in the contract itself. No new risks; no
new dependencies.

### U2.11 Recommended next tasks

Orchestrator: execute §U2.9 items 1–2, then dispatch `security-reviewer` (G5) against the recorded
SHA with this report, the two docs, the contract doc, and the schema as the review set.

---

## Units 3a–3l — the deterministic ingestion/extraction pipeline (through 2026-08-08)

This section is the AOS §6 summary of the implementation delivery under
`services/api/app/documents/**` and `services/api/tests/documents/**`. The reviewers found this body
of work SOUND (G1 data-contract PASS, G5 security PASS, G3 ruled the logic correct); the details
below are the honest map of what ships live vs what is deferred.

### U3.1 What was built (module-by-module)

| Area | Module(s) | What it does |
| --- | --- | --- |
| S1 upload gate | `gate.py`, `limits.py`, `errors.py` | Content sniffing + extension agreement (typed `ExtensionMismatchError`), streaming byte cap (`UploadTooLargeError` at `MAX_UPLOAD_BYTES+1`), known-answer `sha256:` digest over exact bytes, safe temp-path construction. Metadata-only typed errors (no document bytes in any payload). |
| Isolation boundary | `isolation.py` | Fail-closed capability probe (`require_isolation`) → `ParsingPermitted` / `ParsingDisabled`; the only condition under which untrusted bytes are decoded. |
| Format routing | `extraction/routing.py` | CLOSED per-format matrix (`route_format`), single isolation-gated pipeline entry (`begin_extraction_job`), wrong-address routing (`wrong_address_routing`). No parser lives here — it only selects and hands out a decoder inside a proven-boundary authorization. |
| PDF reader | `extraction/pdf_lexer.py`, `pdf_xref.py`, `pdf_objects.py`, `pdf_content.py`, `pdf_container.py` | Strict-subset PDF reader: real xref, objects, content operators; embedded-text runs, vector segments/rects. Every refusal is a typed VALUE, never an exception. |
| Vector/embedded decoder | `extraction/vector_pdf_decoder.py` | First concrete `DecoderSeam`: decodes a digitally-authored PDF into ordered `DecodedPage` primitives; a curve (or any out-of-subset construct) is a `pdf_decode_refusal` value; one bad page fails the whole decode. Pure function of its bytes. |
| Fact taxonomy + typing | `taxonomy.py`, `units.py`, `models.py` | Canonical `fact_type` vocabulary; deterministic normalized-value + stated-unit typing (`units.py`) that NEVER coerces/infers/converts a unit (typed `UnresolvedNormalizedValue` refusal-as-value). |
| Deterministic checks | `checks/` (`boundary.py`, `area.py`, `metadata.py`) | The screening checks (`scale_consistency`, `address_bbl_match`, boundary/area/metadata) as typed `CheckPassed`/`CheckFailed`/`CheckUnevaluable` values. |
| Correction history | `correction_history.py` | Append-only correction-history integrity validation (deterministic, no AI judgment). |
| Geometry/location validation | `geometry_validation.py` | Deterministic cross-field `location` validation (closed coordinate-space/kind vocabularies, fail-closed on smuggled keys). |
| Tax-lot cross-check | `crosscheck.py` | Read-only, non-promotable `tax_lot_bbl_crosscheck` (SB-S4): context-only, `overrides_survey = False`, never mutates a survey value. |
| Promotion + state | `promotion.py`, `state.py` | Per-fact promotion (confidence never substitutes for a resolved validator) and the promotion-gated state machine (`promotion_gated_transition`); wrong-address/needs-review edges. |
| Pipeline composition | `extraction/survey_pipeline.py` | `run_survey_extraction`: upload → route → isolate → decode → assemble facts → deterministic checks → per-fact promotion → gated transition, returning a typed `ExtractionCompleted` / `ExtractionNotStarted` / `DecoderUnavailable` outcome. |

### U3.2 SB-S1..S9 coverage (summary; full map in `docs/M2-T015-SB-COVERAGE-MATRIX.md`)

- **SB-S1** digitally-authored path → `auto_extracted` through the H5 gate (clean scale+BBL doc).
- **SB-S2** closed format routing; unsupported → typed rejection; raster → `DecoderUnavailable`.
- **SB-S3** deterministic checks; failures/decode-refusals/empty extractions route to `needs_review`, recorded, never silent.
- **SB-S4** MapPLUTO/tax-lot BBL cross-check wired context-only (unit 3l); divergence routes to review and never mutates a survey value; facts byte-for-byte identical across none/match/divergent references. (AREA cross-check deferred — follows boundary/area reconstruction.)
- **SB-S5** fail-closed AI/confidence boundary; confidence promotes nothing.
- **SB-S6** isolation boundary fail-closed; with the boundary unproven no byte is decoded (spy decoder proves `decode` is never called).
- **SB-S7** wrong-address document → `needs_review` with the typed wrong-address routing value.
- **SB-S8** every assembled `survey_evidence` record validates against the canonical v1 schema.
- **SB-S9** the whole pack is a permanent CI regression backstop.

### U3.3 Honest deferrals (unchanged by the rework)

1. **Boundary/area reconstruction** is NOT performed by units 3k/3l — assembly is deliberately narrow (exact canonical `1:N` scale + 10-digit BBL). Distance/bearing/area normalization and free-text address labeling are a later deterministic-association unit; no boundary polygon or lot-area fact is fabricated. The tax-lot AREA cross-check follows that reconstruction and is therefore not wired yet (the mechanism is unit-tested in `test_crosscheck.py`).
2. **OCR / raster extraction** is deferred: raster formats (scanned PDF, TIFF, PNG, JPEG) route but carry `decoder=None` → `DecoderUnavailable`. Rotated-page normalization is likewise a later unit.
3. **B-001 durable private storage** is deferred; store-only DWG acceptance and durable evidence storage wait on it. Native DWG / DXF are typed deferrals with the vector-PDF-export alternative.
4. **Isolation application vs presence:** `require_isolation` proves the boundary is PRESENT; applying the Landlock ruleset + seccomp filter before the first untrusted byte is the deployed isolated-parser path's duty (architecture §5, B-001/deployment-gated). CI runs on Linux where the real path exists (R274).

---

## Rework 2026-08-09 — gate corrections 1–3

The 4-reviewer wave accepted the pipeline logic/security/contract but required three concrete
closures. None changed pipeline behavior; the excluded-from-edit modules (routing, survey_pipeline,
vector_pdf_decoder, crosscheck, checks/, promotion, state, models) are byte-for-byte unchanged in
behavior.

### R.1 Correction 1 — `ruff check .` exit 0 under pinned ruff 0.13.0

CI's `api` job runs `cd services/api && ruff check .` with ruff **0.13.0** (pinned in
`requirements-tools.lock`; `pyproject.toml select = [E,F,I,UP,B]`, line-length 100). After the
orchestrator's auto-fix, 16 findings remained; all fixed **without any `# noqa`**:

- **15 × E501** — three module-docstring first lines (`units.py`, `geometry_validation.py`,
  `correction_history.py`) reworded (`application-level` → `app-level`, meaning preserved); and long
  tuple/call lines in `test_correction_history.py` (205, 263, 342), `test_gate.py` (183, 198), and
  `test_geometry_validation.py` (246, 248, 249, 251, 255, 266, 276) wrapped across lines — **pure
  formatting; no test value or behavior changed**.
- **1 × UP047** — `units.py::_match_unit` converted to PEP 695 type-parameter syntax; the now-unused
  module-level `_UnitT = TypeVar(...)` and the `from typing import TypeVar` import were removed
  (ruff confirmed no new F401). Ruff 0.13.0 additionally raised **UP049** (PEP 695 params must not be
  private), so the parameter is named `UnitT` (no leading underscore). The migration is semantically
  identical to the old bounded `TypeVar` (both a generic function bounded by `enum.Enum`).

Result: `python -m ruff check .` → **All checks passed!** (exit 0) over the whole `services/api` tree.

**Runtime note (honest limitation):** the project targets Python 3.12 (`requires-python >=3.12`,
ruff `target-version = "py312"`) and **CI's `api` job runs Python 3.12** (verified in
`.github/workflows/ci.yml`: every `setup-python` pin is `python-version: "3.12"`). PEP 695 function
type-parameter syntax requires 3.12+. The producer sandbox on this session has only a working Python
**3.11.9** (the local 3.12/3.13 install is a gutted directory with no `python.exe`), which cannot
*parse* PEP 695 syntax. Because ruff parses independently of the runtime, `ruff check .` verifies at
exit 0 locally on the pinned 0.13.0. For pytest, I proved the suite green on 3.11 with the
semantically-identical bounded-`TypeVar` form of `_match_unit`, then re-applied the PEP 695 form
(the shipped state) for ruff/CI parity; on CI (3.12) both `ruff check .` exit 0 and the full pytest
run hold simultaneously. This is a producer-sandbox limitation, not a code defect — the orchestrator
should capture the authoritative 3.12 pytest banner in CI.

### R.2 Correction 2 — the named synthetic fixture pack + matrix

Delivered the objective FIXTURES clause: a committed **all-synthetic** fixture pack with MANIFEST
digests, following the `mappluto_geometry/build_fixture_pack.py` pattern, plus the fixture matrix doc.

- **Location:** `services/api/tests/documents/fixtures/survey_documents/` — `build_fixture_pack.py`
  (deterministic generator), 14 committed fixture files, and `MANIFEST.json`.
- **All-synthetic + provenance:** surveys have no live official source, so every fixture is
  deterministically synthesized (no real client survey, no captured official response, no private
  document). Each MANIFEST entry carries `classification: synthetic`, `category`, `format`,
  `builder`, honest `extraction_status`, `byte_size`, `purpose`, `supported_scenarios`, and a
  `sha256:<hex>` over the exact committed bytes.
- **Builders mirror the suite:** PDF fixtures use the exact `_assemble_pdf` / `_one_page_pdf` byte
  assemblers from `test_survey_pipeline.py` / `test_vector_pdf_decoder.py`; raster fixtures are
  structural PNG stubs (signature + IHDR + IEND with valid CRC32, no zlib → byte-identical on every
  host); malicious fixtures reuse the T01/T02 threat vectors from `test_gate.py`.
- **All 12 objective categories covered** (fixture → status):
  digital PDFs `SVY01` (live), vector PDFs `SVY02` (live), clean scans `SVY03` (deferred→OCR/raster),
  poor scans `SVY04` (deferred→OCR/raster), rotated pages `SVY05` (deferred→rotation-normalization),
  mixed units `SVY06` (deferred→distance/unit-normalization), decimal ambiguities `SVY07`
  (deferred→distance/bearing-normalization), conflicting dimensions `SVY08` (live: scale_consistency
  fail→needs_review), incomplete boundaries `SVY09` (deferred→boundary-reconstruction), multi-page
  `SVY10` (live), wrong-address `SVY11` (live: address_bbl_match fail→needs_review),
  malicious/oversized `SVY12`+`SVY13`+`SVY14` (live: S1 gate reject + streaming cap).
- **Matrix doc:** `docs/SURVEY_FIXTURE_MATRIX.md` maps each of the 12 categories → fixture id(s) →
  deterministic check(s)/scenario(s) → extraction_status (live vs deferred), honest about every
  deferral. It is a DIFFERENT document from `docs/M2-T015-SB-COVERAGE-MATRIX.md`; both are kept.
- **MANIFEST-integrity + representativeness test:** `tests/documents/test_survey_fixture_pack.py`
  (14 tests) asserts every committed fixture's bytes match its recorded `sha256`/`byte_size`; the
  pack round-trips byte-identically through `build_fixture_pack.py` (fixtures AND MANIFEST); all 12
  categories are present; and the live/deferred/malicious fixtures decode/route through the real
  pipeline / S1 gate exactly as documented (ties the matrix to executable behavior, not prose).

### R.3 Correction 3 — this report

Brought current through unit 3l + the rework (was Unit 2 only): the intro currency note, the
"Units 3a–3l" consolidation (U3.1–U3.3), and this rework section.

### R.4 Self-verify — verbatim command output (2026-08-09)

From `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015/services/api`:

```
> python -m ruff --version
ruff 0.13.0

> python -m ruff check .
All checks passed!
```

Full-suite pytest on the shipped (PEP 695) code cannot run on this sandbox's Python 3.11 (it cannot
parse PEP 695). The suite was proven green on 3.11 with the semantically-identical bounded-`TypeVar`
form of `_match_unit`, immediately before re-applying the shipped PEP 695 form:

```
> python -m pytest tests/documents/ -q        # units.py temporarily in bounded-TypeVar form (3.11-parseable)
939 passed, 1 skipped in 1.46s
```

(939 = the prior 925 + the 14 new `test_survey_fixture_pack.py` tests. The bounded-`TypeVar` and
PEP 695 forms are the same generic function bounded by `enum.Enum`; ruff's UP047 treats them as the
identical upgrade. The orchestrator captures the authoritative 3.12 pytest banner in CI, where the
shipped PEP 695 code parses and both ruff exit 0 and the full run hold together.)

Contract validator from the worktree root (ran clean in this session):

```
> python .github/scripts/validate_contracts.py
meta-schema engines : stdlib-structural + jsonschema 4.26.0
instance engines    : stdlib mini-validator + jsonschema 4.26.0 (cross-checked)
... (10 schemas + all valid/invalid fixtures OK) ...
Checked 10 schema file(s); 0 failure(s).
```

(The rework touched no `packages/contracts/**` file, so this is unchanged from the contract's prior
green state; captured here for completeness. Exit 0.)

### R.5 Files changed/created in the rework (exact paths + one-line purpose)

| File | Change | Purpose |
| --- | --- | --- |
| `services/api/app/documents/units.py` | edited | docstring first line ≤100; `_match_unit` → PEP 695 `[UnitT: enum.Enum]`; removed unused `TypeVar` import + module-level alias (UP047/UP049/E501). No behavior change. |
| `services/api/app/documents/geometry_validation.py` | edited | docstring first line reworded ≤100 (E501). No behavior change. |
| `services/api/app/documents/correction_history.py` | edited | docstring first line reworded ≤100 (E501). No behavior change. |
| `services/api/tests/documents/test_correction_history.py` | edited | wrapped 3 long lines (205, 263, 342); no test values changed. |
| `services/api/tests/documents/test_gate.py` | edited | wrapped 2 long lines (183, 198); no test values changed. |
| `services/api/tests/documents/test_geometry_validation.py` | edited | wrapped 7 long parametrize tuples; no test values changed. |
| `services/api/tests/documents/fixtures/survey_documents/build_fixture_pack.py` | NEW | deterministic all-synthetic fixture-pack builder (12 categories, 14 fixtures). |
| `services/api/tests/documents/fixtures/survey_documents/SVY01..SVY14 (14 files)` | NEW | committed synthetic fixtures (PDF/PNG/binary), one+ per objective category. |
| `services/api/tests/documents/fixtures/survey_documents/MANIFEST.json` | NEW | per-fixture digests, classification, category, extraction_status, scenarios. |
| `services/api/tests/documents/test_survey_fixture_pack.py` | NEW | MANIFEST-integrity + deterministic round-trip + representativeness tests (14 tests). |
| `docs/SURVEY_FIXTURE_MATRIX.md` | NEW | 12-category → fixture → check/scenario → extraction_status matrix (honest deferrals). |
| `project-control/reports/M2-T015-producer-report.md` | edited | this rework update (Corrections 1–3). |

### R.6 Assumptions / limitations of the rework

1. **PEP 695 was orchestrator-directed** as the UP047 fix; it is the only way to satisfy UP047 under
   `target-version = py312` without a prohibited `# noqa`. UP049 forced the non-private name `UnitT`.
   Consequence: `units.py` (and anything importing it — the whole pipeline) now requires Python 3.12+
   to *import*; this is consistent with `requires-python >=3.12` and CI's 3.12, but it is the first
   3.12-only syntax in this package (the code was previously de-facto 3.11-parseable). Flagged for
   visibility.
2. **Pytest on the shipped code was not run locally** (Python 3.11-only sandbox cannot parse PEP 695);
   green was proven on the semantically-identical bounded-`TypeVar` form (R.4). Authoritative 3.12
   pytest is an orchestrator/CI capture.
3. **Oversize fixture is a small sentinel**, not a >50 MiB file (thin-client storage policy); the cap
   boundary (`UploadTooLargeError` at `MAX_UPLOAD_BYTES+1`) is proven in-memory in the integrity test.
4. **Contract validator** (`python .github/scripts/validate_contracts.py`) — the rework touched no
   contract/schema/fixture under `packages/contracts/**` (all edits are in `services/api/app/documents`,
   `services/api/tests/documents`, and `docs/`). Ran clean in this session: "Checked 10 schema
   file(s); 0 failure(s)." exit 0 (R.4). No contract verdict changed.
5. No self-acceptance: this is producer evidence only; an independent gate re-runs `ruff check .`
   (0.13.0) and pytest on 3.12 to confirm exit 0 / green.

**Report path:** `project-control/reports/M2-T015-producer-report.md`
