# G1 DELTA RE-REVIEW ATTESTATION — M5-T024 (RC-1)

> Preservation note: saved VERBATIM by the orchestrator from the same G1 reviewer's agent-return
> channel (transport entity-decoding only). Companion to M5-T024-G1-evidence-review.md.

## RC-1: DISCHARGED

**G1 PASS stands at content identity `9ce75316`.** No residuals, no new findings.

## Identity / scope verification (reproduced)
- `git diff 9ce75316..HEAD --stat` → only `project-control/state.json` + `project-control/tasks/M5-T024.json` (control-plane lifecycle). Deliverable content at HEAD `b08a0c88` == `9ce75316`.
- `git diff 0002ddb7..9ce75316 --stat` → `docs/RENDER_INTERNAL_WEB_DEPLOY_CHECKLIST.md` (+111 lines) and `project-control/reports/M5-T024-producer-report.md` addendum (in scope), plus orchestrator-recorded gate/review control-plane artifacts (`gates/M5-T024-G1.json`, `gates/M5-T024-G5.json`, the two review reports). No production source, no forbidden path, `render.yaml` untouched.

## (a) RC-1 fully discharged — owner can execute §9 in printed order; opt-in explanation is code-accurate everywhere

Reproduced against source (all citations verified in the first pass and re-confirmed):
- **§2 step 1 (checklist lines 122-131)** now states the flag alone surfaces nothing and describes the two-factor gate: env flag AND per-request `?ruleeval=on` → the single `ruleEvalEnabled` boolean gating **both** the address front door (`<AddressResolutionScreen />`) **and** the draft rule-eval surface, with the only mount point named. Citations `rule-evaluation.ts:96-103`, `page.tsx:30`, `PropertyLookup.tsx:265` are all accurate (I re-checked: `ruleEvaluationSurfaceEnabled` = env flag AND `?ruleeval` true-token at 96-103; `page.tsx:30` computes it; `PropertyLookup.tsx:265` is the sole mount). It explicitly says plain `/property` shows only the numeric BBL form (no address field) and that to use the address flow you open `/property?ruleeval=on`.
- **§9 (lines 252-294)** — the dead end is gone. A "read before step 2" preamble (lines 257-265) introduces `<new-web-service-origin>/property?ruleeval=on`, states that plain `/property` with no address field is EXPECTED not a broken deploy, and cites the full gate chain. **Step 1** loads the plain URL (BBL lookup works on its own). **Step 2** (lines 270-277) navigates to the `?ruleeval=on` URL where the address front door is mounted, then enters a real address — with an absent-field recovery note ("if the address field is absent, you are on plain `/property` — re-open with `?ruleeval=on`") and the CORS-mismatch recovery note preserved. **Step 3** (lines 278-284) rides the *same* `?ruleeval=on` request for the rule-eval surface, correctly noting the same two-factor gate mounts both surfaces. Following the printed order, every step is now reachable.

The opt-in explanation is code-accurate in both places it appears (§2 step 1 and §9) and matches the two-factor gate in `rule-evaluation.ts:96-103`.

## (b) Renumbering left no stale cross-reference
I enumerated every `§N` reference in the file and checked each against the swapped map (exposure note → §5 "READ THIS BEFORE §6"; CORS + API-flag → §6):
- All CORS references point to §6: line 166 ("CORS entry in §6"), 168-169 ("before §6"/"§6 rationale"), 273 ("CORS allowlist from §6 step 1"), 276 ("re-check … in §6"), 279 ("both services (§2, §6)").
- All exposure references point to §5: line 32 ("See §5 before turning the internal flag on"), 173/176 (§5 heading + "in §6"), 214 ("You already read the exposure consequence in §5").
- Remaining `§1`-lookalikes at lines 220/320/323/326 are `§1.3` / "research file §1" external-doc references, not in-file section pointers — correct.

No stale `§5`/`§6` (or any other) internal cross-reference remains.

## (c) Nothing else material changed
- No new external/factual claims were introduced — only the verified code citations (`page.tsx:30`, `PropertyLookup.tsx:265`, `rule-evaluation.ts:96-103/54-77`), all confirmed accurate. The §5/§6 exposure and CORS content is byte-preserved (only position + numbering moved; matches the producer's renumbering map).
- **Privacy still clean** (re-run independently): the only http(s) literal in the reworked checklist is `http://127.0.0.1:8000` (line 135, documented local default); zero `onrender.com` / real hosts; zero keys/tokens/secrets. D-043-R002 intact.
- Prior PASS findings for S1/S3/S4 and directive prohibitions R002/R004 are unaffected by this delta.

## Advisory carry-over (unchanged, out of scope)
A-1 (`page.tsx:22` stale docstring) and A-2 (`.env.example` reference to a non-existent DEPLOYMENT §0.1) remain open in forbidden-path files — future non-M5-T024 cleanup, not blocking. A-3 (api.ts "147-154" off by ~1) is immaterial.

## Attestation
RC-1 is **DISCHARGED**. No new required corrections. **G1 = PASS at content identity `9ce75316`** (live HEAD `b08a0c88` differs only by control-plane lifecycle files). Recommend the orchestrator record the delta re-review as clearing the sole BLOCKING condition; M5-T024 has no outstanding G1 blockers.
