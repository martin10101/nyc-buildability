# D-024 Amendment 46 — Codex review-schema repair package (owner authorization, 2026-09-02)

- **Directive:** D-024 (fable-codex-loop campaign)
- **Kind:** amendment (append-only; amends source-001.md; follows source-045-amendment.md)
- **Issued by:** owner (interactive session, 2026-09-02, one message following the read-only
  differential trace of `canary-b5-02r2`'s `review_unavailable` stop, which the session returned
  ending `CODEX_REVIEW_UNAVAILABLE_TRACE_READY`)
- **Context:** canary-b5-02r2 (owner-typed run of `run_m0t142_fable_switch_and_canary.ps1`,
  2026-09-02 22:34–22:37Z) produced a PASS Fable-5 worker leg and a failed Codex review leg:
  the reviewer child spawned and exited 1 with empty stderr and an empty
  `--output-last-message` file (`no_decision` → `review_unavailable` → WAIT_FOR_OWNER; audit
  seq 48 in runtime dir `9aca7075…`). The session's read-only differential trace identified
  `tools/agent_supervisor/schemas/review_verdict.schema.json`'s constraint keywords as the sole
  differing child input versus the last durable Codex review success. The owner then ran a
  diagnostic probe that captured the provider error verbatim (evidence directory below).
- **Base identity at capture:** worktree `C:\Users\MLFLL\Downloads\nyc-zoning\ctl24`,
  branch `candidate/D-024-mrl-option-b`, HEAD `56848d985c2bb342f959e2dc7383245e6bd2ee22`,
  tree clean, `origin/main` `d8b3899f61efa6620e18a26541ced96020f5bef9`. Frozen corrected
  candidate `f8f0f0c8` INSTALLED live; model pin `claude-fable-5` in force. Next unused task
  ID: M0-T143.

## Verbatim owner directive (corrective-package authorization)

> OWNER AUTHORIZATION: implement one bounded corrective task for the now-proven Codex
> review-schema failure.
>
> The owner-run diagnostic conclusively returned:
>
> * exit 1
> * `invalid_json_schema`
> * status 400
> * parameter `text.format.schema`
> * exact error: `In context=('properties', 'evidence_ref_ids'), 'uniqueItems' is not permitted.`
>
> Evidence directory:
>
> `C:\Users\MLFLL\AppData\Local\NYCBuildabilitySupervisor\ctl24-activation\codex-schema-probe-20260902-191655532`
>
> Do not continue investigating authentication, model availability, executable identity,
> budgets, Fable, or repository state. Those are proven healthy. Do not reopen accepted tasks.
> If governance requires a new task, create exactly one bounded follow-up.
>
> Implement one package containing:
>
> 1. Flatten the provider-facing `review_verdict.schema.json` to the known-safe strict
>    Structured Outputs subset. Remove every nonessential constraint keyword together,
>    including:
>
>    * `uniqueItems`
>    * `minLength`
>    * `maxLength`
>    * `minItems`
>    * `maxItems`
>
>    Do not perform a serial one-keyword-at-a-time repair. Retain only the structural provider
>    contract needed for constrained output: object/property types, enum, required fields,
>    array item type, and `additionalProperties: false`.
>
> 2. Preserve every removed guarantee inside `ReviewVerdict.from_provider` or its
>    controller-owned validator:
>
>    * exact object shape
>    * correct field types
>    * bounded rationale length
>    * bounded evidence-reference count
>    * unique evidence-reference IDs
>    * controller-issued evidence IDs only
>    * valid verdict enum
>    * no extra keys
>
> 3. Add mutation tests proving overlong strings, too many/few IDs, duplicate IDs, fabricated
>    IDs, wrong types, bad enum, and extra fields are rejected controller-side.
>
> 4. Add a provider-schema inspection test that rejects unsupported/nonstructural keywords
>    before a Codex process can be spawned. Apply the same projection/inspection principle to
>    every provider-facing schema so this sibling defect cannot recur elsewhere.
>
> 5. Repair reviewer failure observability. For every nonzero Codex exit:
>
>    * preserve a bounded, redacted stdout JSONL tail as well as stderr
>    * parse and record the first structured `error`/`turn.failed` code and message
>    * record the child return code
>    * never store the full prompt, credentials, or unbounded output
>    * never reduce a known provider error to only `no_decision`
>
> 6. Keep the exact worker model pinned to original Fable 5:
>
>    * `claude-fable-5`
>    * no `fable` alias
>    * no `claude-fable-5-1`
>    * no Fable fallback
>
> 7. Correct the canary reporting:
>
>    * Claude authentication and the Fable WorkerResult from `canary-b5-02r2` are already PASS.
>    * Codex review is the only failed/unavailable leg.
>    * Item 8 is already PASS.
>    * Item 10 is NOT_RUN.
>
> 8. Prefer the canonical supported recovery path that retries Codex review from the preserved,
>    validated `canary-b5-02r2` checkpoint and evidence packet without launching Fable again.
>    If the controller has no safe supported review-resume path, state that explicitly and use
>    one successor full canary only; do not invent a bypass.
>
> 9. Run focused tests during implementation and one complete affected-suite verification at
>    the frozen candidate. Use the owner’s captured JSONL error as a regression fixture. No
>    live provider call during implementation.
>
> 10. Obtain independent review, update the immutable installer binding, and produce exactly
>     one owner-run PowerShell command. That command must transactionally install and verify
>     the candidate, confirm `claude-fable-5` remains selected, execute the canonical
>     Codex-review recovery or single successor canary, run item 10, and print the consolidated
>     ten-item result.
>
> Do not execute the owner script, push, merge, or start unrelated work.
>
> End with exactly `CODEX_SCHEMA_REPAIR_READY`.
