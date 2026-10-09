# M0-T143 — Definitive return report (D-024 Amendment 46, R713)

This artifact is the durable capture of the implementing session's return to the owner. The live
final reply reproduces this content; per D-001 the durable repository record, not the chat
transcript, is the authoritative form. Its last line is exactly the required token.

## Ten-item return (mapping the owner's numbered package)

1. **Schema flattened (R702):** `review_verdict.schema.json` reduced in ONE change to the strict
   Structured-Outputs subset; `uniqueItems`, `minLength`, `maxLength`, `minItems`, `maxItems`
   removed together; structure (types, enum, required, array item type,
   `additionalProperties:false`) retained. Frozen code commit `3f4cee86`.
2. **Guarantees preserved (R703):** every removed guarantee now enforced in
   `ReviewVerdict.from_provider` — exact shape, types, bounded rationale (nonempty..4096),
   bounded ref count (1..64), per-id bounds (nonempty..128), uniqueness, controller-issued IDs
   only, verdict enum, no extra keys.
3. **Mutation tests (R704):** all enumerated mutants rejected controller-side; red observed
   (2 failed at flatten-without-bounds), green after; recorded mutation pair on the uniqueness
   check (disabled → 2 failed → restored → 2 passed).
4. **Pre-spawn inspection (R705):** `assert_codex_output_schema_strict` refuses non-structural
   keywords BEFORE any Codex process (even the `--version` probe) in BOTH reviewers; sweep test
   covers every provider-facing schema (worker_result via the Draft-7 projection;
   review_verdict + codex_decision via the strict inspection).
5. **Failure observability (R706):** every nonzero Codex exit now records the parsed first
   `error`/`turn.failed` code+message, the child return code, and bounded redacted stdout-JSONL
   + stderr tails; typed `provider_rejected_request` / `missing_decision_file`; never a bare
   `no_decision`; never the full prompt, credentials, or unbounded output.
6. **Model pin (R707):** exactly `claude-fable-5`; no `fable` alias, no `claude-fable-5-1`, no
   fallback; the owner script VERIFIES (never edits) the pin and the doctor's model_selection
   row.
7. **Canary reporting corrected (R708):** canary-b5-02r2's Claude auth + Fable WorkerResult are
   PASS; Codex review was the only failed leg; item 8 already PASS; item 10 NOT_RUN — the
   successor readout splits the legs and surfaces the parsed provider error.
8. **Recovery path (R709):** stated explicitly — the controller has NO safe supported
   review-resume path (`CYCLE_ENTRY_STATES` excludes CODEX_REVIEW; no pending prompt exists),
   so the package uses ONE successor full canary `canary-b5-02r3` via the canonical audited
   surfaces (`resume-after-answer` → `start`); no bypass invented.
9. **Tests (R710):** focused suites during implementation; ONE complete affected-suite run at
   the frozen candidate: 3626 passed / 2 skipped / 0 failed — independently reproduced by both
   G4 and G3; the owner's captured JSONL error is the committed regression fixture; no live
   provider call anywhere.
10. **Review, binding, one command (R711):** independent G3 (code-reviewer) PASS + G4
    (qa-engineer) PASS + DCV PASS recorded; `source_binding.json` (+ runbook §4 + ps_test pin)
    rebound to `3f4cee86`; exactly ONE owner-run PowerShell command deployed:

    `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$env:LOCALAPPDATA\NYCBuildabilitySupervisor\ctl24-activation\run_m0t143_codex_schema_repair_and_canary.ps1"`

    (SHA-256 `096ee3ea749ca3b8654561a20aa442b0bac472ad6f1635e430da0116ebfed5de`; transactional
    install+verify of `3f4cee86`, claude-fable-5 confirmation, canonical WAIT_FOR_OWNER exit,
    ONE `canary-b5-02r3`, item 10 harness, consolidated ten-item table + token.)

Prohibitions honored (R712): the owner script was not executed; nothing pushed; nothing merged;
no unrelated work started.

CODEX_SCHEMA_REPAIR_READY
