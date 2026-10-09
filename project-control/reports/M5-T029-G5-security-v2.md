# M5-T029 — G5 security review v2

- **Verdict: PASS**
- Reviewer: independent `security-reviewer`
- Producer: `frontend-engineer`
- SHA: `1e93d0ccb0e6a3b49a5f761c530b717d3bbf8bf0`
- Tree: `c691e3a0dd3b4349950fc11d3c40cce544ca42b7`
- Content identity: `0a423de2dbe8da714bc719662396ca12e4320edcf30d0c6be4217bc114485bc2`
- Worktree: `/workspace/scratch/cfa2464c5c7f/nycdf-ui-review-v2`

Application source matched the frozen commit. Only orchestrator-owned submission records were dirty. This review made no implementation, control, dependency or git mutations.

## Reproduced closure and checks

**G5-F1 is closed.** Independent, in-memory execution of the actual `ArchitectEntry` confirmed that mismatched and missing evaluation BBLs announce identity failure and withheld results. Matching evaluations retain their normal draft announcement; typed failures retain their failure announcement. Mismatched property profiles are also withheld with an identity announcement.

Actual-source rendering additionally confirmed that hostile missing-source identifiers remain escaped text, with an explicit unavailable-source explanation and usable Close control.

Independent replacement tests passed:

```text
./node_modules/.bin/vitest run \
  src/lib/__tests__/map-context.test.ts \
  src/components/architect/__tests__/entry.test.tsx \
  src/components/architect/__tests__/workspace.test.tsx \
  src/components/address/__tests__/lot-outline-map.test.tsx \
  src/components/survey-review/__tests__/survey-review.test.tsx
```

**5 files / 51 tests passed.**

Independent `PYTHONDONTWRITEBYTECODE=1 python tools/modularity_check.py --check` passed: **434 files, zero failures, 18 unchanged legacy warnings.**

## Trust boundaries

The delta preserves fixed external origins, bounded requests/responses, cancellation, omitted credentials/referrers, authoritative BBL resolution, safe official links and React-escaped source records. The slash-label correction remains bounded display text. MapLibre HTML attribution remains constant.

Fact filtering, disclosures, printing and compact survey presentation add no authorization, network or persistence behavior. Existing survey capabilities, blockers and server-enforced mutations remain. The forbidden-path diff against `ef7ee891a70af4752187d6161deadbd55cbdb96a` is empty. Prior passing security checks remain applicable to byte-identical code.

## Requirement conclusions

These are G5-scoped conclusions; visual acceptance and overall directive acceptance remain separate.

| Requirement | Verdict | Conclusion |
|---|---|---|
| D-061-R001 | PASS | Presentation introduces no authorization authority. |
| D-061-R002 | PASS | Identity rejection now agrees between visible results and announcements; facts and limitations remain accessible. |
| D-061-R003 | PASS | Records remain escaped, links validated and missing evidence explicit. |
| D-061-R004 | PASS | One-box requests remain bounded and encoded. |
| D-061-R005 | PASS | Fixed sources, bounded geometry, constant HTML attribution and failure handling remain. |
| D-061-R006 | PASS | Unavailable capabilities remain honest; printing and survey presentation claim no new persistence. |
| D-061-R007 | PASS for G5 | Independent security checks pass; remaining CI/UI gates are still required. |
| D-061-R009 | PASS | Backend, contracts, credentials, dependencies and deployment configuration remain unchanged. |
| D-061-R010 | PASS | Resolver authority, candidate isolation, cancellation and recovery remain. |
| D-061-R013 | PASS through review | Captured main remains `d8b3899f61efa6620e18a26541ced96020f5bef9`; PR 241 remains unmerged. |

## CI scope and conclusion

Orchestrator-captured current-SHA checks passed: secret-scan run `34899412837`, dependency-security job `104161481140`, modularity job `104161481485`, and web job `104161480938`.

Evidence: `/workspace/scratch/cfa2464c5c7f/ui-browser-evidence/1e93d0cc-ci-status.json` and adjacent modularity/web logs.

The latest browser result is **98/99**, with one visible City Planning attribution assertion requiring correction. This G5 PASS does not waive that outstanding UI gate.

**No open G5 defects at the reviewed SHA.** A narrow reattestation is appropriate for the forthcoming attribution-copy correction. This report makes no whole-system security, legal-accuracy or live-deployment claim.
