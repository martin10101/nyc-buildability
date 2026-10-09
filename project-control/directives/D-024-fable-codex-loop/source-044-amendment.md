# D-024 Amendment 44 — Claude Code JSON-Schema Draft-7 compatibility hotfix + canary continuation correction (owner directive, 2026-09-02)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-043-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-02)
- **Channel:** Claude Code interactive prompt (verbatim below)
- **Context:** The owner ran the Amendment-43 corrected canary script
  (`%LOCALAPPDATA%\NYCBuildabilitySupervisor\ctl24-activation\run_m0t136_canaries.ps1`).
  canary-b5-01 PASSED (controller audit record sequence 17, 2026-09-02T18:24:58.305Z:
  `launch_manifest_refused` naming `clean_status`, exit 11, no provider contact, no
  `one_shot_unit.json` under `mrl\canary-b5-01`). canary-b5-02 then launched ONE fresh
  `claude -p` child which exited 1 BEFORE provider contact (audit records 22–26,
  2026-09-02T18:25:00–02Z; `mrl\canary-b5-02\one_shot_unit.json`: `session_id` empty,
  `observed_models` [], `processes_total` 1, stderr
  `Error: --json-schema is not a valid JSON Schema: no schema with key or ref
  "https://json-schema.org/draft/2020-12/schema"`). The controller entered a synchronous
  stop (`no_valid_checkpoint`) and the durable journal now reports PAUSED_RECOVERY
  (observed read-only this session: no emergency stop, no manual pause, 0 surviving
  children, 0 pending effects, audit chain ok head 26). This amendment captures the
  owner's bounded correction: one JSON-Schema Draft-7 compatibility hotfix at the Claude
  CLI boundary plus the corrected canary continuation.
- **Base identity at capture:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`,
  branch `candidate/D-024-mrl-option-b` (local only, no upstream), HEAD `c3903878`
  (M0-T140 G0/claim commit), working tree clean, frozen production candidate
  `1489879e1f6787a9d53ed74db4524b24039e03a2` installed live at 2026-09-02T17:13Z
  (backup/install/verify evidence in `ctl24-activation`). The next unused task ID is
  M0-T141. `origin/main` not consulted (candidate branch is local-only; R520/R521).

## Verbatim owner directive

> Implement one bounded Claude Code JSON-Schema compatibility hotfix and carry it through focused independent acceptance in this session. Do not start another broad audit or tranche.
>
> Confirmed root cause:
>
> Claude Code 2.1.252 locally rejects the provider-facing WorkerResult schema because it declares:
>
> `"$schema": "https://json-schema.org/draft/2020-12/schema"`
>
> The child exits 1 before provider contact. Anthropic's current structured-output documentation requires Draft 7, and anthropics/claude-code issue #80402 reproduces this exact error and documents Draft 7 or removal of the top-level declaration as the workaround.
>
> Required repair:
>
> 1. Preserve the canonical internal WorkerResult contract and controller-side validation.
> 2. At the Claude CLI boundary, generate a deep-copied provider schema explicitly compatible with Draft 7.
> 3. Prefer the explicit Draft-7 declaration:
>    `http://json-schema.org/draft-07/schema#`
> 4. Verify every keyword used by WorkerResult is Draft-7 compatible. Fail closed instead of silently translating any unsupported newer-draft keyword.
> 5. Pass only the compatible copy to Claude's `--json-schema`; never mutate the canonical in-memory schema.
> 6. Add focused tests proving:
>
>    * canonical schema remains unchanged;
>    * provider schema declares Draft 7;
>    * the serialized CLI argument contains no Draft 2020-12 declaration;
>    * unknown/newer-only keywords refuse;
>    * the same exact error would return with the guard removed.
> 7. Preserve the existing failed run as evidence: provider-contact count was zero.
> 8. Correct the temporary canary continuation: reuse the existing b5-01 PASS, do not rerun it, remove the obsolete park/pending-approval assumption, canonically recover the current state, and use one correlated successor run for exactly one actual b5-02 provider call.
> 9. M0-T140 must remain properly claimed and authorized. Do not reopen accepted tasks or interpret R603–R605.
> 10. Create the next available bounded hotfix task. Limit production changes to the schema-at-CLI-boundary path and necessary focused tests.
> 11. Run focused tests, mutation proof, modularity, and governance checks.
> 12. Use separate foreground G3, G4, and DCV reviewers. Producer and verifier identities must differ. Resolve review findings within this bounded scope without returning to the owner after every step.
> 13. Freeze the corrected controller candidate and update its immutable source binding.
> 14. Do not push, merge, or make any provider call during implementation or verification.
>
> After acceptance, generate and parser-validate one external owner-run PowerShell script that performs, fail-fast:
>
> * verified backup;
> * immutable hotfix installation;
> * manifest recording and source verification;
> * normal doctor;
> * canonical recovery;
> * exactly one resumed b5-02 provider canary;
> * remaining evidence checks and the ten-row result.
>
> On an installation/doctor failure, use the bound transactional rollback. Do not automatically rollback merely because a canary reports a product defect; preserve its evidence and stop.
>
> Return only:
>
> * `SCHEMA_COMPATIBILITY_HOTFIX_READY` or `SCHEMA_COMPATIBILITY_HOTFIX_BLOCKED`;
> * accepted hotfix task and candidate SHA;
> * focused test/review results;
> * external script path and SHA-256;
> * exactly one PowerShell execution command.
>
> Do not execute the owner-run script yourself.

## Decomposition

Requirements D-024-R664 through D-024-R683 (see `requirements.json`), amendment_sequence 44.
Forward trace: opening scope/sequencing sentence pair → R664; the confirmed-root-cause
paragraph block → R665; "Required repair" items 1–7 → R666–R672 in order; item 8 (canary
continuation correction) → R673; item 9 → R674; item 10 → R675; item 11 → R676; item 12 →
R677; item 13 → R678; item 14 → R679; the post-acceptance owner-run-script paragraph and
fail-fast list → R680; the rollback/no-auto-rollback paragraph → R681; the return-items
list → R682; the closing prohibition ("Do not execute the owner-run script yourself") →
R683. No source sentence is left unmapped; no requirement is invented beyond the source
text. Bindings: hotfix-task rows (R664–R672, R675–R678, R682) → M0-T141; canary-continuation
rows (R673, R680, R681, R683) → M0-T140; cross-cutting holds (R674, R679) → both. R603–R605
remain owner-only and uninterpreted (Amendment 41); nothing here reopens M0-T136/T138/T139.
