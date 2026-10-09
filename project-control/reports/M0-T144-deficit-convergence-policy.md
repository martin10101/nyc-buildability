# M0-T144 producer report — deficit-convergence policy installation

- **Task:** M0-T144 (governance; D-024 Amendment 51 part B, R761–R766)
- **Producer:** orchestrator (content is owner-dictated verbatim; captured at
  `source-051-amendment.md`)
- **Content commit:** `6aafd5e40afcbca16c9755ce6722e5b251b3518e` — ONE commit touching exactly
  the two owner-named paths (`A .claude/skills/deficit-convergence/SKILL.md`, `M CLAUDE.md`),
  62 insertions, 0 deletions.
- **Date:** 2026-09-04 (UTC)

## 1. Changed files (R761/R763/R764)

| Path | Change |
|---|---|
| `CLAUDE.md` | ONE insertion: permanent principle **18** carrying the owner's mandatory trigger verbatim: "For repeated failures, commissioning failures, external CLI/provider incompatibilities, or conflicting evidence, load /deficit-convergence before editing. Do not use live reruns as serial discovery. Produce either verified closure or one consolidated blocker report." (diff: `1 file changed, 1 insertion(+)`) |
| `.claude/skills/deficit-convergence/SKILL.md` | New narrowly-triggered skill: frontmatter description with the narrow trigger + explicit "Do NOT invoke for an ordinary isolated failure with an already-proven cause" + "Manually invocable as /deficit-convergence"; body carries the owner's **20 rules verbatim** (numbered 1–20 exactly once), the non-applicability statement, the no-repo-wide-audit prohibition, the authority-unchanged clause, and the two terminal outcomes (`VERIFIED_CLOSED` or one consolidated blocker report). |

## 2. Validation results (R765)

1. **Frontmatter:** parses (single `description:` key, 668 chars); matches the repo's skill
   format (fence + description, directory name = skill name).
2. **Rule integrity:** the numbered rules extracted from the body are exactly `1..20`, each once.
3. **Carve-outs present:** the ordinary-isolated-failure non-applicability statement (SKILL.md
   line 8, wrapped) and the repo-wide-audit prohibition both verified by grep.
4. **Live discovery:** the running Claude Code harness discovered the new skill immediately
   after the write and lists it as invocable (`/deficit-convergence`) alongside the 22 existing
   project skills (23 skill directories total) — discovery validated against the real loader,
   not a simulation.
5. **CLAUDE.md diff bounded:** `git diff -U0` shows exactly one inserted line (principle 18);
   nothing else changed.
6. **Registry validator:** `python tools/validate_directive_compliance.py --check` exit 0 at
   the content commit (run in the wave).

## 3. Prohibition compliance (R762)

No runtime controller code, no test files, no model selection, no GitHub configuration, and no
accepted-evidence file changed (the content commit's name-status is exactly the two paths). No
provider was launched (no new run dir under the controller runtime `mrl\`); no stabilization or
regression campaign started.

## 4. Producer self-checks (G2)

1. Scope: content commit = exactly the two allowed policy paths; this report is the third
   allowed path. PASS.
2. Verbatim fidelity: trigger text and the 20 rules match `source-051-amendment.md` word for
   word (the skill renders `$LASTEXITCODE` in code backticks; rule text otherwise byte-equal).
   PASS (independent review to confirm).
3. Narrow trigger: the skill's description and body both bound its applicability and prohibit
   repo-wide audits. PASS.
4. One commit: single content commit `6aafd5e4`. PASS.

No independent review has occurred at the time of this section; the wave's G3 + DCV records
follow separately.
