# Survey / Official-Document Ingestion Architecture (canonical)

**Status:** Canonical architecture for the secure survey / official-document ingestion,
extraction, and deterministic-verification pipeline. Produced by task **M2-T015** (owner directive
2026-07-20 section 3, survey workstream Packet B), architecture unit.
**Companions:** `docs/SURVEY_DOCUMENT_FORMAT_POLICY.md` (M2-T014 supported-format decisions —
HARD input; on any format question the policy wins); `docs/SURVEY_EVIDENCE_CONTRACT.md` +
`packages/contracts/schemas/v1/survey_evidence.schema.json` (per-fact provenance contract, M2-T015
unit 1; on any field/enum question the schema wins); `docs/UPLOAD_THREAT_MODEL.md` (threat model +
control matrix for the G5 reviewer, produced with this document).
**Implementation home:** `services/api/app/documents/**` (later M2-T015 unit). Where this document
names limits or tolerances they are **initial bounds**: named constants in the implementation,
confirmed with the G0 disk/execution budget, each proven by a fixture, and changed only through
review — never tuned silently and never set by AI.

## 1. Doctrine (non-negotiable)

1. **Extraction doctrine.** The pipeline is never "OCR reads the survey". Each format routes to
   the best available extraction path per the format policy: vector/CAD object extraction where
   the open PDF container preserves vector content; embedded PDF text extraction for born-digital
   text layers; OCR **only** for scanned text (advisory, never authoritative); line/symbol
   detection for scanned geometry (advisory); AI-assisted classification only where bounded and
   schema-constrained; deterministic geometry reconstruction and validation **always** (§8–§9).
2. **Fail-closed.** No language-model output becomes canonical geometry or a material
   buildability input because the model expressed high confidence. A material value that cannot
   be independently validated surfaces as a visible `unresolved` validation result and routes the
   document to `needs_review` — never a silent pass, never a silent drop (SB-S3, SB-S5).
3. **Division of authority.** AI retrieves, classifies, drafts, and explains. Deterministic code
   calculates, normalizes, reconstructs, and validates. Qualified humans approve. The backend
   state machine (§4) is the only writer of document state; AI may not skip states or declare
   compliance.
4. **Provenance per fact.** Every extracted fact is one `survey_evidence` record carrying the
   original document digest, page, location, verbatim original value, normalized value + units,
   extraction method, confidence, validation results, correction history, and
   professional-confirmation state. Document-level provenance (filename, uploader, upload time,
   declared class, server-sniffed MIME, size, storage location, conversion lineage) lives on the
   document ingestion record, joined by digest.
5. **Cloud-only processing.** All parsing, rendering, OCR, and AI calls run on Render workers or
   CI runners — never on the owner's PC (`docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md`).

## 2. Pipeline stages

| # | Stage | Where | What happens |
|---|---|---|---|
| S1 | **Upload gate** (synchronous) | API | Stream-enforced size cap; server-side content sniffing (declared MIME recorded, never trusted); extension–content cross-check; SHA-256 digest computed on the exact received bytes; original stored immutably (§6–§7); document record created in `uploaded` with target BBL (upload *intent*), declared class, and metadata. Gate failure → typed rejection (§4). |
| S2 | **Security screen** (async, isolated) | Render worker — isolated parser process (§5) | Structural validation as exactly the sniffed format; page/pixel counts against limits; decompression-bomb bounds; dangerous-content screen (PDF JavaScript, launch/open actions, embedded files, external references — never executed, flagged). Failure → `rejected`, typed reason. |
| S3 | **Format routing** | Worker | Route to the designated extraction path(s) per the format policy decision matrix (§3). Unapproved format → typed rejection/deferral with the policy's stated alternative — never improvised parsing (SB-S2). |
| S4 | **Extraction** (isolated) | Isolated parser process | Per-format extraction (§3) inside the parser isolation boundary and resource-limit model (§5). Output: structured detections only. |
| S5 | **Deterministic normalization** | Worker | Deterministic code normalizes detected values and units. Ambiguity (mixed units, decimal ambiguity) is never guessed — it becomes a failing/unresolved `units_consistency` result. |
| S6 | **Deterministic geometry reconstruction** | Worker | Candidate boundary geometry rebuilt deterministically from extracted primitives (§8). |
| S7 | **Deterministic verification** | Worker | The eleven checks of §9 run; every outcome is recorded on the affected facts as typed `validation_results`. |
| S8 | **Evidence emission + state transition** | Worker → API | One `survey_evidence` record per fact, validating against the canonical schema (SB-S8). State machine advances to `auto_extracted` or `needs_review` (§4). |
| S9 | **Review + professional confirmation** | Humans (Packet C UI, M2-T016) | Qualified review, corrections (append-only), per-fact confirmation, document-level confirmation or rejection. |

Stages S2–S4 decode untrusted bytes and run **only** inside the §5 parser isolation boundary.
While that boundary is unavailable or unverified on the worker substrate, extraction jobs are
refused with a typed `isolation_unavailable` outcome — documents rest in `uploaded`, an
operational blocker is surfaced, and S2–S8 do not run (§5). There is no unisolated fallback.

## 3. Per-format extraction paths (exactly per the format policy)

`extraction_method` values below are the closed enum of the survey_evidence contract; no other
path exists, and a new path is added additively only after the format policy approves it.

| Format (policy row) | Verdict | Pipeline handling | Permitted `extraction_method` values |
|---|---|---|---|
| Born-digital PDF (1) | SUPPORTED | Parse text layer; inspect vector content where present; render pages for review display. | `embedded_text_extraction`; `vector_object_extraction` (where vector content exists); `ai_assisted_classification`; `deterministic_geometry_reconstruction` |
| Vector PDF (2) | SUPPORTED | **Primary CAD interchange target.** Vector object extraction from the open PDF container (paths, lines, text runs); page geometry is PDF user space, never auto-trusted as georeferenced. | `vector_object_extraction`; `embedded_text_extraction`; `ai_assisted_classification`; `deterministic_geometry_reconstruction` |
| Scanned PDF (3) | SUPPORTED (raster-only) | Flagged `raster_only=true`. OCR for text — **advisory only**. Line/symbol detection for geometry — **advisory only**. No vector content exists to extract. | `ocr_text`; `line_symbol_detection`; `ai_assisted_classification`; `deterministic_geometry_reconstruction` (from advisory primitives — see advisory-lineage rule below) |
| TIFF (4) | SUPPORTED (raster) | As row 3; each frame of a multi-frame TIFF is one page; lossless display derivative may be generated (original kept). | as row 3 |
| PNG / JPEG (5) | SUPPORTED (raster) | As row 3; JPEG lossiness recorded as a document-level data-quality caveat. | as row 3 |
| DXF (6) | CONVERT / DEFER-initial | **Not parsed.** No validated conversion stage exists yet, so a DXF upload is refused with a typed `format_deferred` response steering the user to export a **vector PDF**. A future DXF→vector-PDF conversion stage must pass its own G1 before any DXF is accepted. |  — (none) |
| Native DWG (7) | DEFER | **Not parsed, nothing derived.** The policy permits store-only acceptance at most; because B-001 defers durable private storage, store-only DWG acceptance is also deferred — a DWG upload is refused with typed guidance to export a vector PDF. Any DWG-parsing library is a licensing/payment STOP condition (owner decision). |  — (none) |
| Anything else | not in the matrix | Typed rejection naming the supported formats. Never improvised parsing (SB-S2). |  — |

**Advisory-lineage rule.** OCR and line/symbol detections are advisory. Deterministic
reconstruction and checks may run on them (the arithmetic is deterministic even when the inputs
are advisory), but a material fact whose lineage is advisory-only always routes the document to
`needs_review`, and the fact itself is born `unconfirmed` like every other fact. Only the clean
digitally-authored path (SB-S1) can reach `auto_extracted`.

## 4. Document state machine

States: `uploaded` → `processing` → `auto_extracted` | `needs_review` → `professionally_confirmed`,
with `rejected` reachable from screening and review. The backend state machine is the only
transition authority; every transition is recorded with timestamp and actor; no state is skippable.

| From | To | Trigger | Authority |
|---|---|---|---|
| (upload request) | `uploaded` | S1 gate passed; original stored immutably; digest recorded | API (deterministic) |
| (upload request) | typed API error, no record | Stream size cap tripped before bytes were durably stored | API |
| `uploaded` | `processing` | Worker claims the extraction job | State machine |
| `uploaded`/`processing` | `rejected` | Security screen or structural validation failure (S2), unapproved format (S3), or integrity failure (§6) — always with a typed reason | State machine (deterministic result) |
| `processing` | `auto_extracted` | Extraction completed; every executed check on every material fact is `pass`; no material advisory-only lineage | State machine |
| `processing` | `needs_review` | Extraction completed with any `fail`/`unresolved` on a material fact, any material advisory-only or AI-classified value, or any tax-lot divergence — the fail-closed routing | State machine |
| `auto_extracted` | `needs_review` | Later divergence (e.g. cross-check against newly accepted tax-lot geometry), a submitted correction, or a reviewer pulling it in | State machine / human request |
| `auto_extracted`/`needs_review` | `processing` | Re-extraction: a new run with a new `extraction_run_id`; existing evidence records are never mutated | State machine (orchestrated job) |
| `auto_extracted`/`needs_review` | `professionally_confirmed` | Qualified professional confirms the document after per-fact review | **Qualified human only** |
| `needs_review` | `rejected` | Professional rejects the document (not a survey, wrong property per SB-S7, unusable) | **Qualified human only** |
| `professionally_confirmed` | `needs_review` | A post-confirmation contradiction is discovered — reopening is visible and audited, never silent | State machine + human |

`rejected` is terminal; a corrected upload is a new document with its own digest identity.
Document state is distinct from per-fact `professional_confirmation` (contract §4.7): a
`professionally_confirmed` document asserts review completed; each material fact still carries its
own confirmation state. AI cannot trigger, veto, or propose any transition.

## 5. Parser isolation boundary and resource-limit model

All parsing/decoding of untrusted bytes runs in a **dedicated isolated parser process** on the
worker, behind an isolation boundary with two **kernel-enforced** properties. A plain child
process is **not** that boundary and is never described as sandboxed; process separation is
defense-in-depth only and never suffices to enable parsing.

**Required boundary properties (both mandatory, kernel-enforced):**

1. **Filesystem isolation.** The parser process cannot read any filesystem path outside an
   explicit allowlist: its own job-scoped temp directory (read/write) plus the read-only
   interpreter and pinned parser-library paths required to execute. Enforced with the Landlock
   LSM (unprivileged, self-applied by the parser process before the first untrusted byte is
   read). Secrets files, other jobs' directories, and every unrelated path are outside the
   allowlist and unreadable by kernel decision, not by convention.
2. **Network denial.** The parser process cannot create sockets or make outbound connections.
   Enforced with a seccomp-BPF filter (installed with `no_new_privs` before parsing begins)
   denying socket-creation and connection syscalls; the structured-output pipe to the parent is
   inherited and needs no socket. Where the running kernel's Landlock ABI provides network
   rules, they are applied as an additional layer.

**Fail-closed enforcement verification.** Worker startup runs a capability probe: a probe
process applies the full isolation policy, then attempts (a) reading a canary path outside the
allowlist and (b) an outbound connection. If either attempt succeeds — or the isolation
syscalls are unavailable or unsupported on the running kernel — the boundary is UNAVAILABLE:
the worker refuses to claim extraction jobs, each refusal is a typed `isolation_unavailable`
outcome, documents rest in `uploaded` (no state is skipped, nothing silently degrades), and an
operational blocker is surfaced. Every parser process additionally self-verifies its applied
policy before reading untrusted bytes and aborts with a typed failure if verification fails.
There is **no fallback to unisolated parsing**.

**Honest substrate statement.** Render's managed containers do not document a guarantee that
Landlock and seccomp are available to tenant workloads, and neither property has been verified
on the actual substrate yet. Therefore **parsing (S2–S4, and with it S5–S8) remains disabled**
until either (a) the startup capability probe proves both properties on the running Render
substrate and the probe evidence is recorded, or (b) an isolated worker/container boundary — a
dedicated parsing container/jail with no network egress and a minimal read-only filesystem —
is available. Until one of those holds, no code path decodes untrusted document bytes.
(Recorded as a residual risk in `docs/UPLOAD_THREAT_MODEL.md` §5.3: the failure mode is loss
of extraction availability, never silent unisolated parsing. Verifying or provisioning the
boundary is deployment-side work under its own gates — nothing is provisioned by this design.)

**Defense-in-depth on the isolated process** (required in addition to, never instead of, the
kernel-enforced boundary):

- **Separate process, no secrets.** Separate OS process (never in the API/worker parent);
  minimal environment with **no secrets** (the process never holds credentials —
  `ANTHROPIC_API_KEY` etc. stay in the parent per `docs/SECRETS_POLICY.md`); working directory
  = the job-scoped temp dir; argv-only spawn, no shell.
- **Parser-level resolution off.** Parser libraries are configured with external-reference /
  external-entity resolution disabled; an outbound attempt is therefore both configured away
  and kernel-denied, and any denied attempt is logged as a typed anomaly.
- **No execution of content.** PDF JavaScript, actions, and embedded files are never executed or
  extracted — only detected and flagged (S2). No macro/script execution anywhere.
- **Resource ceilings** (POSIX rlimits on the Linux worker + parent-enforced timeouts and output
  caps on every platform): CPU time, address space/RSS, file size, open descriptors; process-group
  kill on timeout.
- **Bounded decode.** Image decoders get explicit pixel caps *before* allocation; PDF parsers get
  object-count/recursion caps; streams decode incrementally with ratio + absolute-size aborts.
- **Structured output only.** The process returns structured JSON on stdout (size-capped); the
  parent validates it against an internal schema. Timeout, crash, non-JSON, or oversized output →
  typed parse failure (→ `rejected` or `needs_review` per stage), never a retry-until-it-works
  loop and never a partial silent ingest.

| Limit (named constant) | Initial bound |
|---|---|
| `MAX_UPLOAD_BYTES` | 50 MiB (stream-enforced at S1) |
| `MAX_PAGES` | 60 |
| `MAX_DECODED_PIXELS_PER_PAGE` | 50,000,000 px (pre-allocation guard) |
| `MAX_DECOMPRESSION_RATIO` | 100:1 per stream |
| `MAX_DECODED_STREAM_BYTES` | 512 MiB absolute per stream |
| `PARSE_TIMEOUT_SECONDS` / `PAGE_TIMEOUT_SECONDS` | 120 / 30 |
| `MAX_CHILD_RSS_BYTES` | 1 GiB |
| `MAX_JOB_TEMP_BYTES` | 500 MiB |
| `MAX_CHILD_STDOUT_BYTES` | 32 MiB |
| `MAX_AI_CALLS_PER_RUN` / `MAX_AI_INPUT_CHARS` | 20 / 20,000 (per call) |
| `JOB_TEMP_TTL_SECONDS` (orphaned-dir scavenge threshold) | 3,600 |
| `JOB_DIR_GRACE_SECONDS` (marker-write grace window) | 300 |
| `SCAVENGE_INTERVAL_SECONDS` (periodic sweep cadence) | 600 |
| `MAX_SCAVENGE_DELETIONS_PER_SWEEP` (per-sweep bound) | 100 |

Each limit has a failing fixture (SB-S6). Parser dependencies are exact-pinned, advisory-free,
age-gated, and G5-provenance-reviewed per `docs/DEPENDENCY_SECURITY_POLICY.md`; heavy native
dependencies are disk-budgeted at G0 and may be Render/CI-only.

**Temp discipline.** One job-scoped temp directory per extraction job, created as a direct
child of a single configured root (`JOB_TEMP_ROOT`) with a system-generated name; bounded by
`MAX_JOB_TEMP_BYTES`; deleted in a `finally` path on success *and* failure; cleanup is tested
(SB-S6). Document bytes never appear in logs.

**Deterministic abandoned-job cleanup.** `finally` cleanup cannot run after a SIGKILL, an OOM
kill, a worker-process crash, or a host crash, so residue removal never depends on it alone:

1. **Ownership marker.** Before any document byte is written into a job directory, the worker
   writes and fsyncs an `OWNER.json` marker inside it: worker instance id, worker pid **plus
   process start time** (so pid reuse can never fake liveness), the `extraction_run_id`, and
   the creation timestamp.
2. **Deterministic liveness rule.** A job directory is *live* iff its marker names this worker
   instance and a process with that exact pid AND start time still exists, or the directory is
   younger than `JOB_DIR_GRACE_SECONDS` (covering the instant before the marker lands).
   Anything else — dead pid, foreign or stale instance id, missing or unparseable marker past
   the grace window — is *orphaned*.
3. **Bounded scavenging.** A scavenger sweep runs at worker startup (before the worker claims
   any job) and every `SCAVENGE_INTERVAL_SECONDS` thereafter. It enumerates only the direct
   children of `JOB_TEMP_ROOT`; an orphaned directory is deleted once it is older than
   `JOB_TEMP_TTL_SECONDS`. Each sweep deletes at most `MAX_SCAVENGE_DELETIONS_PER_SWEEP`
   directories — the remainder waits for the next sweep, so a pathological state cannot wedge
   startup or starve job processing.
4. **Safe path validation.** A candidate is deleted only when ALL of the following hold: it is
   a direct child of the configured root; its resolved real path stays inside the root; it is a
   real directory, not a symlink; and its name matches the system-generated job-directory
   pattern. Recursive deletion never follows symlinks. A candidate failing any condition is
   **never deleted** — it is recorded as a typed anomaly and surfaced, because an unexpected
   path under the temp root is itself a security signal.
5. **Audit record.** Every deletion and every refusal writes an audit record: relative path,
   marker contents (or their absence), the deterministic reason (owner dead / stale instance /
   marker missing past grace / TTL expired / validation refusal), timestamps, and bytes
   reclaimed. Paths and metadata only — document bytes never appear in logs or audit records.
6. **Host-crash coverage.** A directory orphaned by an instance or host loss is collected by
   the next worker instance's startup sweep over the same root; where the substrate's instance
   disk is ephemeral, instance replacement destroys the residue with the disk. Either way no
   residue outlives `JOB_TEMP_TTL_SECONDS` plus one sweep on any surviving disk.
7. **Executable acceptance coverage (SB-S6).** Fixtures prove: a dead-owner directory is
   collected after TTL with its audit record; a live directory is never touched; a symlinked or
   out-of-root candidate is refused with a typed anomaly and never followed; a marker-less
   directory is collected only after the grace window; post-conditions assert zero residue.

## 6. Immutable originals and digest discipline

- The **exact original uploaded bytes** are stored write-once and are immutable forever. The
  module exposes no update or overwrite operation for originals.
- `document_digest` = `sha256:<64 hex>` of those exact bytes, computed server-side at S1 —
  raw-bytes semantics per the contract (`$defs/raw_bytes_digest_sha256`), deliberately not
  canonical-JSON digest semantics. Every evidence record of the document carries it.
- The digest is **re-verified** before every parse and every (future) serve; a mismatch is a
  typed integrity failure that halts processing and surfaces a blocker — never auto-repair.
- If extraction ever runs on a converted derivative (e.g. the future validated DXF→vector-PDF
  stage), `document_digest` still digests the ORIGINAL upload; the derivative gets its own digest
  and the conversion records tool + version on the document record (format policy provenance
  rule). Original + converted artifacts are both kept.
- Corrections never touch originals or `original_value`; re-extraction mints new evidence records
  under a new `extraction_run_id`.

## 7. Storage design — honest about the B-001 hold

**Designed now, provisioned later.** B-001 (Supabase management access token) blocks all
production storage provisioning. Nothing below exists in any environment yet: **no bucket, no
credentials, no migration, no deployment.** The pipeline is built against a storage abstraction so
that contracts, parsing, validation, fixtures, and CI-reviewable flows proceed now, and the
production binding is added when B-001 clears.

Design (deferred):

- **Supabase Storage, private bucket** (working name `survey-documents`); public access disabled.
  Content-addressed layout: `originals/<sha256>` (write-once), `derivatives/<original-sha256>/<derivation-id>/…`
  with tool+version lineage. Storage policies deny overwrite/delete of originals to the worker
  role (immutability enforced by policy *and* by the module's API surface).
- **Postgres**: `documents` ingestion-record table (document-level provenance of contract §2) and
  evidence storage, added by migration with tested RLS; tenant isolation scopes documents to the
  uploading organization.
- **Serving**: short-TTL signed URLs for reviewer display only, `Content-Disposition: attachment`
  + `X-Content-Type-Options: nosniff`; originals are never served inline or publicly.
- **Retention and quotas** per `docs/LOW_STORAGE_CLOUD_DEVELOPMENT_POLICY.md` (max file size,
  per-org storage caps, retention limits — enforced values set with provisioning).
- **Credentials**, when provisioning is unblocked, follow `docs/SECRETS_POLICY.md`: names added to
  the section-2 inventory in the same change, values in Render env vars (`sync: false`) /
  GitHub environment secrets only, never in Git. Provisioning itself requires the owner action
  recorded in B-001.

Active now (no credentials required): the storage abstraction interface; a bounded, temp-dir-backed
test implementation used by CI only; synthetic fixture packs (small, in-repo per the low-storage
policy); digest discipline (§6) — the digest, not a storage id, is the content identity, which is
exactly why the contract's `document_ref` is optional while B-001 is open.

## 8. Deterministic geometry reconstruction (always)

Reconstruction is deterministic code — never AI, never curve-fitting-by-model:

1. **Primitive collection**: vector segments/curves and text runs (vector path), or advisory
   detected lines/symbols and OCR dimension texts (raster path), each already an evidence record
   with page-space coordinates (contract §4.2 — page space is never survey/world space).
2. **Dimension association**: dimension/bearing texts are associated to segments by deterministic
   geometric rules (proximity/orientation with fixed tolerances). AI may *propose* an association
   as a bounded classification; the association becomes usable only when deterministic validation
   confirms it (§10).
3. **Boundary assembly**: candidate closed traverses assembled from primitives; stated bearings
   and distances take precedence over measured page geometry, with the discrepancy recorded.
4. **Derived facts** (computed closure, calculated area, assembled polygon) are emitted as
   evidence records with `extraction_method: deterministic_geometry_reconstruction`, carrying the
   run lineage. All tolerances are named constants, recorded with the check results
   (`expected_value`/`observed_value`) so every outcome is reproducible from the record.

## 9. Deterministic verification checks

Exactly the contract's closed `check_id` enum. Every executed check writes a typed
`validation_results` entry — `pass`, `fail` (ran, found a contradiction), or `unresolved` (could
not independently validate — the fail-closed condition); `fail`/`unresolved` always carry a stated
reason. Failures are visible unresolved conditions, never silent acceptance (SB-S3).

| `check_id` | Deterministic question |
|---|---|
| `address_bbl_match` | Does the document's detected address/BBL text match the target property's official address/BBL? Mismatch → `fail` and the document is flagged, never silently ingested into that property's evidence (SB-S7). Unreadable/absent → `unresolved`. |
| `units_consistency` | Are all detected units resolvable and mutually consistent? Mixed units and decimal ambiguity → `fail`/`unresolved`, never a guessed unit. |
| `scale_consistency` | Is the stated scale consistent with measurable relationships on the page (vector coordinate spacing vs dimension labels; bar scale where detected)? |
| `north_orientation` | Is the detected north-arrow orientation consistent with stated bearings? |
| `boundary_closure` | Does the reconstructed traverse close within tolerance? Gap recorded as `observed_value`. |
| `area_vs_stated` | Does the calculated polygon area match the stated lot area within tolerance? Both values recorded. |
| `segment_sum` | Do chained segment dimensions sum to stated overall dimensions? |
| `contradictory_dimensions` | Do multiple statements about the same edge/quantity conflict? |
| `geometry_validity` | Is the assembled geometry valid (simple, non-self-intersecting, non-degenerate)? |
| `elevation_consistency` | Where elevations are present: datum stated, values internally consistent. Absent elevations → check not run (no fabricated pass). |
| `tax_lot_geometry_comparison` | How does the reconstructed boundary compare with accepted MapPLUTO tax-lot geometry (consumed read-only via the `mappluto_geometry_arcgis` domain models)? Divergence is recorded as a **typed comparison result** with metrics. |

**MapPLUTO cross-check rule (SB-S4).** The tax-lot comparison is a cross-check ONLY. It never
silently overrides a licensed survey; no code path replaces a survey value with the tax-lot value.
Divergence routes the document to `needs_review`, where evidentiary weight is judged by a
qualified professional (document-class taxonomy, research doc §9).

## 10. Fail-closed AI boundary

**Where AI is permitted** — bounded, schema-constrained classification of already-extracted
content: labeling detected text runs (is this the scale statement? the address block?), symbol
classification, `fact_type` candidates, and document-class *suggestion* for the human reviewer.
Calls are bounded (`MAX_AI_CALLS_PER_RUN`, `MAX_AI_INPUT_CHARS`), constrained to closed
enums/JSON schemas, validated on return (invalid → retry-bounded → typed failure), and produce
evidence records with `extraction_method: ai_assisted_classification` and true model confidence.

**Where AI is forbidden** — computing or reconstructing geometry, normalizing values, setting or
waiving tolerances, executing or scoring checks, transitioning document state, writing
corrections, confirming facts, or overriding any deterministic result.

**Fail-closed promotion rule (SB-S5).** An AI-classified value becomes usable only when
deterministic validation independently confirms it; otherwise its checks record `unresolved` with
a stated reason, the fact stays `unconfirmed`, and the document routes to `needs_review`.
Confidence — however high — promotes nothing. The contract makes this impossible to hide (contract
§6), and the state machine makes it impossible to act on.

**Prompt-injection posture** (controls detailed in `docs/UPLOAD_THREAT_MODEL.md` T09): document
content is untrusted data, never instructions; classifier calls have no tool access and no
side-effect capability; output is schema-constrained; and even a fully successful injection can
only produce a wrong classification candidate that then fails independent validation visibly.

## 11. Execution environments

| Concern | Environment |
|---|---|
| Upload gate + state machine | FastAPI on Render |
| Security screen, extraction, reconstruction, checks | Render worker — isolated parser processes per §5; parsing stays disabled until the §5 boundary is verified on the substrate |
| Tests + fixtures (synthetic only; bounded sizes) | GitHub Actions CI; logic runs identically with the temp-dir storage fake |
| Owner PC | Thin client only — no parsing, no datasets, no document stores (low-storage policy) |

Fixture pack, matrix, and MANIFEST digest discipline are specified in
`docs/SURVEY_FIXTURE_MATRIX.md` (implementation unit; `build_fixture_pack.py` pattern). No private
client document ever becomes a repository fixture without recorded owner authorization and
redaction evidence (task packet forbidden-paths rule).
