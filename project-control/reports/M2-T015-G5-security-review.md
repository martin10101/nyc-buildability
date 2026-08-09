# Gate Report

- **Gate ID:** G5 (Security & privacy)
- **Task ID:** M2-T015 (Secure survey/official-document ingestion — untrusted uploads + parsing, Packet B)
- **Reviewer:** security-reviewer (independent, read-only)
- **Producer:** backend-engineer / supervised-auto (orchestrator-captured units 3i–3l)
- **Result:** **PASS**
- **Clean environment/worktree used:** Yes — worktree `C:/Users/MLFLL/Downloads/nyc-zoning/wt-m2t015` at frozen SHA `897e7df6c29753008a14fbb4c1457752e19ed2e0` (verified `git rev-parse HEAD`).

> Saved verbatim by the orchestrator (report-preservation; transport entity-decoding only). Reviewed at
> `897e7df`; the subsequent behavior-preserving ruff-0.13.0 lint fix carries a reviewer delta-attestation.

## Acceptance criteria reviewed
Primary G5 scenario **SB-S6** (isolation boundary + resource bounds fail-closed), plus the security-bearing aspects of SB-S1 (isolated decode), SB-S4 (read-only tax-lot cross-check), SB-S5 (fail-closed AI boundary), SB-S7 (wrong-address flag-not-ingest), and SB-S8 (schema-validated provenance). Threat model `docs/UPLOAD_THREAT_MODEL.md` T01–T11 traced to enforcement points.

## Directive/requirement verification
The task file (`project-control/tasks/M2-T015.json`) carries no `directive_refs` array [orchestrator note: it does — this G5 report scopes to the security control matrix; per-`D-<nnn>-R<nnn>` re-derivation is the separate `directive-compliance-verifier` pass]. This G5 report verifies the security control matrix.

## Steps independently executed
1. `cd services/api && python -m pytest tests/documents/ -q` → **925 passed, 1 skipped** (reproduced; matches claimed evidence).
2. Ran the real gate on this host: `require_isolation()` → `os_name: Windows`, `permitted: False`, `reject_code: isolation_unavailable`, `failed_capability: os`. Fail-closed confirmed on the review substrate.
3. Grepped the whole `app/documents/` tree for third-party imports → none (stdlib-only: `zlib`, `hashlib`, `re`, `secrets`, `ntpath`, `os`, `platform`, `ctypes`, `math`). PDF path uses no external parser.
4. Grepped for `eval/exec/subprocess/Popen/os.system/socket/urllib/requests/httpx/pickle/__import__` → none. Grepped for `os.environ/getenv/BYPASS/FORCE_/ENABLE/disable_isolation` → only docstring/reject-code text, no real reads.
5. Grepped for any logging/print → **none** in the module (document bytes cannot be logged).
6. Read every file named in the packet plus the backing tests (`test_isolation.py`, `test_survey_pipeline.py::TestIsolationFailClosed`, `test_pdf_container.py`, `test_gate.py`).

## Expected versus actual

**Isolation fail-closed — exact reachability argument (verified).** A decoder is reachable through exactly one path. `run_survey_extraction` (survey_pipeline.py:647) calls `begin_extraction_job(format_identity)`, whose first statement (routing.py:393) is `capability = require_isolation()`; on `ParsingDisabled` it returns `IsolationUnavailable` before `route_format` is ever called (routing.py:394–395), so no decoder is selected and `run_survey_extraction` returns `ExtractionNotStarted` without touching `entry.decoder` (survey_pipeline.py:648–649). A concrete decoder is handed out ONLY inside `ExtractionJobAuthorized`, constructed only on the `ParsingPermitted` branch. `require_isolation()` (isolation.py:318) takes zero parameters, reads no env/config, and has no override — the signature itself is the proof (`test_gate_takes_no_override_parameter`). Verdict is `ParsingPermitted` only when Linux + Landlock (active LSM + queryable ABI) + seccomp are all affirmatively probed; every error/unknown/partial path returns `ParsingDisabled` (guarded probes + `_derive_verdict`). The spy-decoder test (`test_isolation_unavailable_never_decodes`) subclasses `VectorPdfDecoder`, records calls, and asserts `calls == []` when isolation is disabled — proving no byte is decoded. This matches doctrine.

**No bypass path found.** `begin_extraction_job` has a single parameter (format identity); no flag, env var, or ambient state can reach routing/decoding without a proven boundary. `test_module_reads_no_environment_and_spawns_no_process` asserts the isolation module imports no `os`, references no `subprocess`/`os.environ`/`getenv`.

**Input validation (S1, gate.py + limits.py).** Server-side magic-byte sniff over ≤512 bytes against a fixed signature table (PDF/PNG/TIFF-LE/TIFF-BE/JPEG); declared MIME/extension never selects handling — `check_extension_matches` rejects extension↔content mismatch (`ExtensionMismatchError`) and unsupported extensions (`UnsupportedExtensionError`); unknown magic is never guessed. Polyglot/structural-mismatch defense (T01) is layered: S1 sniff keys routing to one type, and the strict-subset reader then requires the file to parse cleanly as exactly that type. Covered by `test_extension_content_mismatch_raises_typed_error`, `test_unknown_or_empty_magic_is_unrecognized_never_guessed`.

**Resource bounds / DoS (verified per-item, fail-closed).** Streaming cap reads at most cap+1 bytes, one chunk resident, raises `UploadTooLargeError` at the first over-cap byte (`test_over_cap_stops_reading_immediately_without_buffering_whole_stream`). PDF reader bounds: `MAX_PDF_OBJECTS=4096`, `MAX_PAGE_COUNT=512`, `MAX_DECODED_STREAM_BYTES=8 MiB` (single-shot `zlib.decompressobj().decompress(data, max_length)` + `unconsumed_tail`/`eof` abort → decompression-bomb safe), `_MAX_RESOLVE_HOPS=32`, page-tree and reference **cycle detection** via visited-set, `MAX_NESTING_DEPTH=32` (below CPython recursion limit — no `RecursionError`), `MAX_COLLECTION_ITEMS=8192`, `MAX_TOKEN_BYTES/MAX_NUMBER_BYTES`, content-stream `MAX_CONTENT_OPERATORS/MAX_PRIMITIVES/MAX_Q_DEPTH`. Every refusal is a frozen typed value, never an exception (`decode` returns `(refusal,)`). Encryption/xref-streams/hybrid/`/Prev`/`/DecodeParms`/filter-arrays all refused by name. Proven by `test_flate_output_bound_is_refused`, `test_page_count_bound_is_refused`, `test_reference_cycle_is_refused`, `test_page_tree_cycle_is_refused`, `test_corrupt_flate_stream_is_refused`.

**Path traversal / storage-key injection (T07).** Temp names are `secrets.token_hex` only; `validate_temp_upload_path` refuses nul-byte, reserved device names, `..`/`.`, drive/UNC, absolute, embedded separators, then realpath-containment as a direct child. Storage keys are validated `sha256:<64 hex>` bodies used verbatim as filenames — no client filename ever reaches a path. Symlink escape refused (`test_symlink_resolving_outside_the_root_fails_realpath_containment`).

**Immutable originals + digest re-verify (T10).** `TempDirStorage.put_original` refuses overwrite (`ImmutableOriginalViolationError`) before checking bytes, and refuses digest mismatch; `get_original` re-hashes on every read → `DigestMismatchError`, never auto-repair.

**No-AI authority / fail-closed AI boundary (SB-S5).** The implemented pipeline invokes no LLM — classification is exact-pattern deterministic (`1:N` scale, 10-digit BBL); unclassifiable/instruction-shaped text is left unassembled, never coerced (`test_unclassifiable_runs_are_never_coerced_into_facts`). `promotion.evaluate_promotion` records `confidence`/`extraction_method` verbatim and branches on neither — promotion requires resolved typed deterministic validations only. `state.ActorKind` is a closed two-member enum with no AI member; `transition` accepts no confidence/score channel; the H5 gate weighs only an `isinstance(PromotionAllowed)` check. Structurally sound.

**Tax-lot cross-check is read-only (SB-S4).** `crosscheck.py` imports no state/storage/session/db machinery; `TaxLotReference` is frozen with class-level `promotable=False`/`overrides_survey=False`; `_tax_lot_crosscheck` reads the assembled BBL fact and can only pull routing toward `needs_review`, never mutate a fact or promote (`test_crosscheck_is_context_only_never_promotable_never_a_survey_check`).

**Log redaction / PII.** `errors.py` payloads are metadata-only by construction; no logging anywhere in the module; refusal `detail`/`found` strings are length-capped and byte-escaped, never raw attacker bytes.

## Evidence paths
- Isolation gate: `services/api/app/documents/isolation.py`; single entry `services/api/app/documents/extraction/routing.py` (`begin_extraction_job`, lines 376–403); pipeline `services/api/app/documents/extraction/survey_pipeline.py` (lines 647–726).
- Readers: `services/api/app/documents/extraction/{pdf_lexer,pdf_objects,pdf_xref,pdf_container,pdf_content,vector_pdf_decoder}.py`.
- S1 gate/limits: `services/api/app/documents/{gate,limits,errors,storage,state,promotion,crosscheck}.py`.
- Tests: `services/api/tests/documents/{test_isolation,test_survey_pipeline,test_pdf_container,test_gate}.py`.
- Threat model: `docs/UPLOAD_THREAT_MODEL.md`.

## Human-style walkthrough findings
Fed the real `require_isolation()` on the Windows review host: parsing is disabled (`isolation_unavailable`), so no untrusted byte would be decoded here — the intended production posture until the substrate proves the boundary. The synthetic PDF fixtures exercise the full route→isolate→decode→assemble→check→promote→transition path under a stubbed-permitted seam, and every failure class (decode refusal, empty extraction, failed check, BBL mismatch, tax-lot divergence) routes to `needs_review` rather than promoting.

## Regression/security/provenance findings
No critical, high, or medium defects. One low/defense-in-depth item and one informational item below. Dependency check: **PASS** — PDF path is stdlib-only, no new parser dependency added, so no G5 package-provenance obligation is triggered by this task.

**Deployment-gated (presence vs application), honestly disclosed:** The Landlock/seccomp boundary is a *capability presence probe* only. Actual application (Landlock ruleset, seccomp-BPF filter under `no_new_privs`, canary self-verify) and the `MAX_CHILD_RSS_BYTES`/timeout/temp-scavenger worker limits are B-001-gated and deliberately absent (documented in `limits.py` docstring and threat model §5.3). Because the probe fails closed when the boundary is unproven, this deferral does not weaken the current posture — it defers *extraction availability*, never enabling unisolated parsing.

## Defects
None blocking.

- **LOW / hardening (L1) — aggregate decoded-byte budget not enforced in the pure reader.** The reader bounds each *individual* decoded stream to 8 MiB but not the *aggregate* across a `/Contents` array (up to `MAX_COLLECTION_ITEMS=8192` streams/page, joined in `pdf_container._page_content`) or across pages (up to `MAX_PAGE_COUNT=512`, accumulated in `_walk_page_tree`). A highly-compressible PDF within the 50 MiB S1 cap could therefore expand to many GiB resident in the parsing process. **Not currently exploitable:** the decode path is unreachable until the isolation boundary is proven (verified fail-closed on this host), and the threat model names `MAX_CHILD_RSS_BYTES` + per-document timeout as the aggregate backstop — explicitly deferred to the worker-side unit. **Remediation:** when the worker limits land, also add an in-reader running aggregate-decoded-byte budget so the pure reader is self-bounding even if ever invoked outside the RSS-limited boundary (defense-in-depth). File refs: `pdf_container.py` `_page_content` (lines 235–263), `_walk_page_tree` (lines 135–203).
- **INFORMATIONAL (I1)** — `TempDirStorage` exists-then-write is not concurrency-safe; already disclosed in `storage.py` docstring as CI/local-only, with production requiring a single conditional put when B-001 resolves. No action for this gate.

## Required rework
None. L1 is a follow-up to fold into the B-001 worker-limits unit; it does not block G5.

## Reviewer conclusion
**PASS.** The untrusted-upload ingestion pipeline enforces its security doctrine structurally: decode is reachable through exactly one isolation-gated entry point with no override/env/config/flag bypass (signature-proven and spy-decoder-proven), fails closed to typed `isolation_unavailable` with zero bytes decoded when the boundary is unproven (reproduced on the review host), and every input-validation and per-item resource bound refuses closed as a typed value. Originals are immutable and digest-re-verified, storage keys and temp paths are injection-proof, the state machine and promotion gate admit no AI authority, the tax-lot cross-check is read-only and non-promotable, no secrets/PII/document bytes are logged, and the PDF path adds no dependency. The single low-severity item (aggregate decoded-byte budget) is a documented, non-live, defense-in-depth follow-up bounded by the honestly-deferred worker RSS backstop. Evidence reproduced: **925 passed / 1 skipped**.

---

## G5 Delta-Attestation — at merged main HEAD `1b3af35` (post-rework): PASS holds

Same independent security-reviewer. **G5 PASS (from `897e7df`) STANDS at `1b3af35`.**
- The 12 security-seam files (`isolation.py`, `limits.py`, `storage.py`, `extraction/{routing,vector_pdf_decoder,pdf_container,pdf_lexer,pdf_xref}.py`, `crosscheck.py`, `state.py`, `errors.py`, `taxonomy.py`) are **byte-identical** (`git diff 897e7df 1b3af35` empty) — every behavioral verdict carries forward.
- The 7 changed files are lint-only, each hunk verified runtime-inert (UP007 `X|Y`, B905 `strict=False` default, B009 attr-access in already-guarded branches, F401 unused import, E501 docstrings, UP047 PEP 695 same generic). No control flow / bounds / verdict / security change.
- Independent runtime check at HEAD (Python 3.11): `require_isolation()` → `permitted=False, reject_code=isolation_unavailable` — fail-closed reproduces.
- New malicious/oversized fixtures (`SVY12` exe-renamed-as-pdf, `SVY13` html-renamed-as-tiff, `SVY14` oversize) are **additive coverage** of the already-verified S1 controls (magic-byte sniff, extension-mismatch, streaming cap) — no new decode surface, no gap.
- Captured CI evidence (`M2-T015-CI-evidence.md`) verified: api job 3.12 SUCCESS, ruff clean, 939 documents (+14 security-fixture tests), 2025 full api. Local pytest not runnable (PEP 695 needs 3.12) → evidence-capture division of labor.
- Prior L1 (aggregate decoded-byte budget, B-001 worker-side backstop) unchanged, non-blocking.
- Non-security note: PEP 695 requires Python ≥3.12 at import (consistent with `requires-python>=3.12` + CI/prod 3.12) — a deployment/tooling-contract item, not a security defect.

**Verdict: G5 PASS at `1b3af35`.**
