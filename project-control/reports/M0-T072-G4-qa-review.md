# M0-T072 G4 QA review — condensed verdict record (round 1)

CONDENSED transcription by the orchestrator (report-preservation rule): this
captures the reviewer's verdict and every blocking correction; the full verbatim
return is preserved in the session task-notification record. NOT labeled verbatim. Reviewer: independent qa-engineer subagent, read-only, at
frozen HEAD `ec8bc58`. Blocking corrections C1/C2 and the disclosed defects are
addressed in the round-1 rework at `be3a599` (see M0-T072-rework-evidence.md).

---

## G4 QA verdict — M0-T072 — **PASS with required corrections** (record as PASS; C1–C4 blocking for acceptance)

Worktree `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t072`, HEAD `ec8bc58` (branch tip `98267d3` = later CLI-written gate records only). All nine acceptance scenarios independently reproduce as the producer claims; no claim in `project-control/reports/M0-T072-before-after-evidence.md` was falsified except the suite-count line (F3). Adversarial probing found one **new** defect in the same family the task exists to close (F1) plus a second silent-pass-on-bad-input (F2).

**C1 / F1 — MEDIUM-HIGH — a self-consistent manifest can attest to its own (empty) coverage and still report "controller verified".** `manifest_is_stale` recomputes `manifest_digest` over `{"files", "controller_version"}` only; `patterns` is outside the integrity digest, and `verify_manifest` takes its coverage patterns from the manifest under test. A manifest with `patterns: []` binding only `config.toml` passes the production check with all package files unverified. AS-8 only mutates `files`, so the suite cannot see this. Fix: fold `patterns` into the staleness digest, and/or assert the manifest's patterns equal COVERED_PATTERNS for production verification.

**C2 / F2 — MEDIUM — `record-manifest --config` will bind `model_selection.toml` (or any file) under the logical name `config.toml` and report success.** The S3.1 exclusion is checked on the logical name only, never on the supplied source path. A mistyped path in runbook §5 produces a manifest that never binds the real config and makes every authenticated model change invalidate the controller. Fix: refuse when `pathlib.Path(args.config).name in EXCLUDED_NAMES`.

**C3 / F3 — MEDIUM — the suite-baseline number in the evidence file is the pre-suite count.** "1813 passed, 2 skipped" was measured WITHOUT the 27 new regression tests (the battery ran against a checkout lacking the new module). Re-capture on the delivered tree before using it as the M0-T039 re-established baseline.

**C4 / F4 — LOW-MEDIUM — AS-9's placeholder test is fitted to the artifact, and one live placeholder survives.** `test_no_unresolved_executable_placeholders` checks six hand-picked prefixes; the runbook's `<the stamp created in step 3>` at line 156 (rollback fence) is precisely shaped to miss it. Either reuse the `$backup` variable or scan for a generic `<[^>]+>` inside fences.

Advisory F5-F10: config binding is normalized-content not byte (runbook prints two digests for one file); `start` exits 0 on missing `--manifest`; raw tracebacks on malformed `files`; `require_verified` still has zero production callers; `doctor` without `--manifest` returns ok/exit 0; G0-readiness + evidence-map outside allowed_paths.

Runbook↔source surface check: all 8 subcommands and 19 flags exist; no caret continuation anywhere. Recommendation: record **PASS**; C1/C2 blocking (silent-PASS-on-bad-input in the exact defect family this task closes), C3/C4 blocking evidence/doc corrections.

*(Full verbatim detail is in the orchestrator's task transcript; this preservation captures the reviewer's verdict, every blocking correction C1-C4, and the advisory findings F5-F10 for the acceptance record.)*
