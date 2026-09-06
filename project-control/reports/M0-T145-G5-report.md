# M0-T145 G5 reports (verbatim reviewer returns, both rounds)

Saved VERBATIM by the orchestrator from the security-reviewer agent-return channel (2026-09-06;
transport entity-decoding only: `&lt;`→`<`, `&gt;`→`>`, `&amp;`→`&`; the harness's
instruction-shape neutralization notice on round 1 is transport metadata, not reviewer content).
ROUND 1 reviewed SHA 0671edd5 → PASS, later SUPERSEDED by the reviewer itself (that commit
carried the G3 regression its battery did not probe); ROUND 2 (delta re-attestation) reviewed
SHA bac01a56 → **PASS** (authoritative).

Round-1 report highlights (full text preserved in the session record; superseded verdict):
- 16-case parent-vs-child differential (glued-assignment, provider-prefixed, nested, discard,
  data-position cases): zero deny→allow observed IN THAT BATTERY; five intended tightenings.
- ReDoS analysis: single character-class `+`, no catastrophic backtracking; ms-scale on
  200k–500k adversarial inputs.
- Hook wiring confirmed live in `.claude/settings.json` (Bash|PowerShell|Write|Edit|MultiEdit|
  NotebookEdit).
- Findings: L1 pre-existing drive-qualified variable-write residual (`${C:report.txt} = 'x'`) —
  out of scope, compensating-control-covered, TRACKED as documented-residual follow-up;
  L2 informational (debrace false-positives are strictly deny-direction); L3 cosmetic
  (duplicate §6 numbering in the producer report — accepted as-is).

---

## ROUND 2 (delta re-attestation, reviewed bac01a56) — PASS (authoritative)

# Gate Report — G5 delta-attestation

- **Gate ID:** G5 (independent security review, delta re-attestation)
- **Task ID:** M0-T145
- **Reviewer:** security-reviewer (independent; read-only)
- **Reviewed content identity:** `bac01a561e20398d3606bd770703f8311a89e029` (confirmed on-disk HEAD), delta over the previously-reviewed `0671edd5`; parent baseline `29f9ee7b`.
- **Result: PASS**
- **Clean worktree used:** `C:\Users\MLFLL\Downloads\nyc-zoning\wt-m0t145`

## Context

My prior G5 PASS was against `0671edd5`, whose debrace was **global**. Independent G3 correctly found that a global debrace deletes `{`/`}`, which double as `_SEGMENT_CHARS` separators, so brace-glued **command-position** forms (no assignment) were newly ALLOWED. My original 16-case differential exercised glued *assignment* forms but not glued *command-position* forms, so it did not surface this vector — the G3 finding is a genuine additional regression class, not a contradiction of my earlier rows. The rework scopes the debrace to assignment position:
`_PS_BRACED_VAR = re.compile(r"\$\{([A-Za-z0-9_:.\-]+)\}(?=\s*=(?!=))")`.

## Steps independently executed at `bac01a56`

1. `python tools/test_readonly_agent_guard_powershell.py` → **exit 0, ALL CHECKS PASSED** — includes the six new `M0-T145 brace-glued deny` rows and the third mutant tooth `mutant drops assignment lookahead -> ${x}powershell -enc glues past` (proves the lookahead is load-bearing).
2. `python -m pytest tools/test_readonly_agent_guard_powershell.py -q` → **exit 0, 1 passed**.
3. `python tools/test_readonly_agent_guard.py` (general/Bash) → **exit 0, ALL CHECKS PASSED**.
4. Three-way differential — parent `29f9ee7b` vs regressed `0671edd5` (loaded from git objects) vs reworked disk — over 18 cases including the six glued command forms.
5. ReDoS probe of the lookahead variant.

## Expected versus actual (three-way differential)

| Case | PAR | OLD (0671edd5) | NEW (bac01a56) | new-vs-parent |
|---|---|---|---|---|
| `${x}powershell -enc` (glued cmd) | DENY | allow (regr) | **DENY** | same |
| `${x}git push` | DENY | allow (regr) | **DENY** | same |
| `${a-b}pwsh -enc` | DENY | allow (regr) | **DENY** | same |
| `${x}start powershell -enc` | DENY | allow (regr) | **DENY** | same |
| `${x}cmd /c whoami` | DENY | allow (regr) | **DENY** | same |
| `${a}${b}git push` | DENY | allow (regr) | **DENY** | same |
| `${x} = powershell -enc` | allow | DENY | DENY | stricter (fix) |
| `${x}=powershell -enc` (glued asg) | allow | DENY | DENY | stricter (fix) |
| `${a}=${b}=powershell -enc` (chain) | allow | DENY | DENY | stricter (fix) |
| `${a-b} = powershell -enc` | allow | DENY | DENY | stricter (fix) |
| `${C:report.txt} = powershell -enc` | allow | DENY | DENY | stricter (fix) |
| `${x}==powershell` (comparison) | allow | allow | allow | same (parity via `(?!=)`) |
| `${x} == powershell` | allow | allow | allow | same |
| `gci > ${null}` (discard) | allow | allow | allow | same |
| `gci > ${null:x}` | DENY | allow (regr) | **DENY** | same |
| `${x} = Get-Content README.md` | allow | allow | allow | same |
| `${env:PATH} -split ';'` | allow | allow | allow | same |
| `${${x}} = powershell -enc` (nested residual) | allow | allow | allow | same |

**LAUNDER (new deny→allow vs parent): NONE.**

Findings:
- **(1) Glued command-position regression fixed.** All six forms: parent DENY, `0671edd5` ALLOW (I independently reproduced the G3 regression from git objects), `bac01a56` DENY. Non-assignment braces retain their separator role, so the glued command token still splits into command position and is caught. Confirmed.
- **(2) Assignment fix intact.** All five assignment-fronted shell forms remain allow→DENY. The lookahead `(?=\s*=(?!=))` fires exactly where downstream `_ASSIGN_LAYER` (single-`=`, not `==`) can strip, so the two stay consistent. `> ${null}` is no longer rewritten and stays ALLOWED directly via the `\$\{null\}` branch of `_PS_REDIRECT_TARGET_OK`; `${x}==powershell` stays parent-parity ALLOW because `(?!=)` excludes the comparison operator. Confirmed as the coordinator described.
- **Bonus regression also fixed (disclosure):** `gci > ${null:x}` — the global debrace at `0671edd5` rewrote `${null:x}`→`$null:x`, which `_PS_REDIRECT_TARGET_OK`'s `\$null\b` then wrongly accepted as a discard (ALLOW). This was a *second* regression sub-class in `0671edd5`. My original review reported this row as DENY, which I now attribute to a content-identity race on disk during my review (the identity was moving); the authoritative git-object comparison shows `0671edd5` ALLOWED it. At `bac01a56` it is correctly DENY (parity with parent), because the redirect target keeps its braces and `\$\{null\}` requires exactly `${null}`. This strengthens, not weakens, the PASS: the rework restores parent behavior here too.
- **(3) ReDoS:** the lookahead adds only a bounded `\s*=` with a fixed-width negative lookahead — no nested quantifier over alternation, no catastrophic backtracking. Timings: name-noclose 200k → 1.4 ms; close-no-`=` 100k → 0.7 ms; 200k trailing spaces before EOF → 0.6 ms; 100k `${a}` prefixes → 3.1 ms; assign-tail → 1.0 ms. Non-issue.
- **(4) Both suites green** at `bac01a56` (exit 0), Bash pack unchanged (PowerShell-scoped by construction).

Structural argument (why no laundering is possible): at `bac01a56` a brace is rewritten only when immediately followed by `\s*=(?!=)`, so the rewrite output is always followed by `=` (an assignment), never by a command token — it can therefore only reveal an assignment RHS (tightening), never glue a command into a variable name. Every non-assignment brace is byte-for-byte parent behavior. The empirical LAUNDER=NONE across all 18 cases (incl. the six glued forms) confirms this.

## Regression/security/provenance findings

- No Critical/High/Medium. The rework removes the `0671edd5` regression class(es) and preserves the intended fix.
- **L1 (pre-existing, acknowledged/tracked):** drive-qualified variable write with a non-shell RHS (`${C:report.txt} = 'x'`) — unchanged, out of scope, compensating-control-covered; coordinator will track as a documented-residual follow-up.
- **L2 (informational, unchanged):** any theoretical new false-positive from debracing is strictly fail-closed (deny-direction only).
- **L3 (cosmetic):** duplicate `## 6.` numbering in the producer report — accepted as-is to avoid moving the reviewed identity.
- **Process note (self-disclosure):** my original G5 battery had a coverage gap (no glued command-position forms) and a reliability gap on the `${null:x}` row due to the moving content identity. The independent G3 gate caught the real regression — producer≠verifier and multiple independent gates worked as designed. This delta re-attestation is performed against fixed git objects to eliminate the disk-race.

## Reviewer conclusion

**PASS at `bac01a56`.** The assignment-scoped lookahead cleanly closes the M0-T109 residual (assignment-fronted braced nested shells DENY) while restoring parent behavior for every non-assignment brace — the six glued command-position forms and `gci > ${null:x}` are all back to parent DENY, with zero deny→allow laundering across the three-way differential, no ReDoS, both suites green (including the six new glued-deny rows and the load-bearing lookahead-removal mutant), and the Bash pack byte-identical. The docstring and test corrections are honest and accurate.

Verdict to orchestrator: **PASS** at content identity `bac01a561e20398d3606bd770703f8311a89e029`. My earlier `0671edd5` PASS is **superseded** by this delta (that commit carried the G3 regression).
