# M5-T029 — G5 security review

- **Result: FAIL — one medium integrity/accessibility defect**
- Reviewer: independent `security-reviewer`
- Producer: `frontend-engineer`
- Reviewed SHA: `50995365dedba7694f8462c5db3fd4dcf235690f`
- Tree: `13827e2aea66270500aa635646b5eef82ad0b97f`
- Baseline: `ef7ee891a70af4752187d6161deadbd55cbdb96a`
- Worktree: `/workspace/scratch/cfa2464c5c7f/nycdf-ui-review`
- Review was read-only. No implementation, control, dependency or git mutations were performed. The supplied dependency symlink was used for tests.

This is a security and integrity review of the frontend change. It does not certify production authorization, tenant isolation, backend security, legal accuracy, or deployment readiness.

## Defect G5-F1 — mismatched analysis still receives a success announcement

**Severity: medium.**  
**Location:** `apps/web/src/components/architect/ArchitectEntry.tsx`, line 137.

The visible workspace correctly withholds an evaluation when its BBL differs from the selected property. However, `rule-eval-announcer` receives `analysis.evaluation` before that identity guard. It therefore announces a successful classification of the rejected document.

**Reproduction independently executed:**

1. Load the actual `ArchitectEntry` and fixture modules in memory using the installed TypeScript transpiler.
2. Supply `baseProfile()` through the property hook.
3. Supply `draftApplicableDoc()` through the analysis hook, changing its `evaluated_input.bbl` to `5000010001`.
4. Select the profile’s BBL and `view=evidence`.
5. Render the actual component using `react-dom/server`.

**Observed:**

- The identity-mismatch alert is present.
- The evaluation is withheld from the visible calculation view.
- The live region nevertheless contains:

> Draft rule evaluation loaded: an unreviewed draft determination that requires professional review.

Other rejected evaluation classifications can also produce property-specific success announcements. This gives assistive-technology users an inconsistent account of whether the analysis belongs to their property.

**Required correction:** Guard the success announcement using the same BBL identity condition as the visible results. Announce the identity failure, or suppress success classification, for mismatched or missing BBLs. Add regression assertions for both cases while retaining valid evaluation and typed failure announcements. The canonical evaluation client need not change.

## Independent checks

Executed from `apps/web`:

```text
./node_modules/.bin/vitest run \
  src/lib/__tests__/address-search.test.ts \
  src/lib/__tests__/map-context.test.ts \
  src/lib/__tests__/provenance-link.test.ts \
  src/lib/__tests__/bbl.test.ts \
  src/components/architect/__tests__/autocomplete.test.tsx \
  src/components/architect/__tests__/entry.test.tsx \
  src/components/architect/__tests__/workspace.test.tsx \
  src/components/address/__tests__/lot-outline-map.test.tsx \
  src/components/survey-review/__tests__/survey-review.test.tsx
```

**Result: 9 files passed; 69 tests passed.**

Additional read-only, in-memory execution of actual source modules verified:

- GeoSearch and NYZD requests use `credentials: "omit"` and `referrerPolicy: "no-referrer"`.
- Address query text containing `&street=evil` stays within the single encoded `text` parameter.
- Address suggestion control characters are rejected.
- Hostile legal-link forms, custom ports, query parameters and unsupported fragments are rejected.
- NYZD responses exceeding 1,500,000 bytes are withheld.
- Active cancellation returns an aborted outcome even when the injected transport never resolves.
- Captured source strings containing `<img onerror>`, `<script>` and `javascript:` remain escaped text and create no executable element or link.

These additional checks passed. They also reproduced G5-F1 without writing files.

## Security findings outside G5-F1

No additional blocking security defect was found in the reviewed change.

- **External requests:** New data clients use fixed HTTPS origins. Address input is limited, debounced and encoded. Both clients impose response limits, deadlines and cancellation. NYZD adds feature, coordinate, ring and request-envelope validation. No server-side arbitrary-fetch capability was introduced.
- **Untrusted content:** New evidence and calculation surfaces render records as React text. Legal links are reconstructed from a strict official-origin/path allowlist; dataset links use the existing validated token helper.
- **Map HTML:** MapLibre attribution contains module constants. Reflected attribution remains React-escaped text. Source-returned URLs are not passed into attribution HTML.
- **Property identity:** Canonical BBL validation, authoritative resolver selection and visible wrong-property withholding are present. G5-F1 is the remaining inconsistency.
- **Session data:** The added storage contains browser-session address presentation context. It does not control API identity, authorize review actions, or persist survey decisions. Storage failure remains recoverable.
- **Survey interfaces:** The existing runtime flag, digest validation, HTTP client, server-authorized mutations and typed refusals remain. Property filtering is presentation filtering, not a claimed authorization boundary.
- **Scope:** The captured changed-path inventory contains frontend code/tests and orchestrator-owned task records. Backend services, contracts, database, credentials, dependencies and deployment configuration are unchanged.
- **Modularity:** Network clients, request hooks, session context, URL policy and presentation remain separate. The reviewed CI modularity log reports **431 selected files, zero failures, 18 existing warnings**. No new oversized security-sensitive module was introduced.

## Directive verification

These conclusions cover the G5 aspects of each requirement. Overall visual fidelity and final directive acceptance remain with the designated reviewers.

| Requirement | G5 conclusion at reviewed SHA | Evidence |
|---|---|---|
| D-061-R001 | PASS within security scope | Route adapters and shared shell add presentation without new authorization authority. Visual acceptance belongs to G3. |
| D-061-R002 | **FAIL** | G5-F1 gives a success announcement for an identity-rejected analysis. Visible facts, conflicts and review records otherwise remain accessible. |
| D-061-R003 | PASS within security scope | Actual source/trace records remain available as escaped text; safe official links and explicit missing evidence are present. |
| D-061-R004 | PASS within security scope | One-box entry sends encoded, bounded text to the fixed official suggestion endpoint. |
| D-061-R005 | PASS within security scope | Fixed raster sources, constant attribution, bounded optional geometry and honest failures; no new legal geometry calculation. Source-semantic verification remains G1. |
| D-061-R006 | PASS within security scope | Planned capabilities are unavailable; printing does not claim server persistence; survey authorization remains server-controlled. |
| D-061-R007 | **FAIL / not yet satisfied** | Focused security tests pass, but G5-F1 requires correction and this gate cannot pass at the reviewed SHA. Final browser/CI gates remain separate. |
| D-061-R009 | PASS | Captured diff inventory shows no forbidden backend, contract, credential, dependency or configuration change. |
| D-061-R010 | PASS within security scope | Five-borough candidate validation, manual/BBL recovery, cancellation and existing authoritative resolution remain. Candidate PAD BBL is not adopted. |
| D-061-R013 | PASS through captured review state | Orchestrator’s GitHub evidence records main at `d8b3899f61efa6620e18a26541ced96020f5bef9`; PR 241 remains open and unmerged. Delivery must preserve this. |

## Captured evidence inspected

- `/workspace/scratch/cfa2464c5c7f/ui-browser-evidence/50995365-scope.txt`
- `/workspace/scratch/cfa2464c5c7f/ui-browser-evidence/50995365-remote-state.txt`
- `/workspace/scratch/cfa2464c5c7f/ui-browser-evidence/50995365-web.log`
- `/workspace/scratch/cfa2464c5c7f/ui-browser-evidence/50995365-modularity.log`

The remote-state capture records secret-scan run `34896822696` successful and completed dependency-security, web and modularity jobs successful. Browser and supervisor jobs were still pending in that capture. No deployed state was independently verified.

## Conclusion

**G5 FAIL at `50995365dedba7694f8462c5db3fd4dcf235690f`.** Correct G5-F1, freeze the resulting SHA, and perform a targeted independent recheck. The successful security checks above can be retained where the verified source remains unchanged.

```json
{
  "schema_version": "1.0",
  "decision": "REVISE",
  "reviewed_task_id": "M5-T029",
  "reviewed_checkpoint_id": "M5-T029-frozen-submission-50995365dedba7694f8462c5db3fd4dcf235690f",
  "verified_repo_head": "50995365dedba7694f8462c5db3fd4dcf235690f",
  "verified_origin_main": "d8b3899f61efa6620e18a26541ced96020f5bef9",
  "model_used": "",
  "verified_facts": [
    {
      "fact": "Independent focused security regression: 9 files and 69 tests passed."
    },
    {
      "fact": "Read-only actual-source execution verified request privacy options, query encoding, hostile-link rejection, oversized-response rejection, active cancellation and escaped source HTML."
    },
    {
      "fact": "Actual ArchitectEntry rendering reproduced a success live-region announcement for an identity-rejected evaluation."
    }
  ],
  "unverified_claims": [
    {
      "claim": "Final browser/CI and deployment readiness",
      "why": "Other gates and live deployment are outside this completed source review; captured CI still had pending jobs."
    },
    {
      "claim": "Whole-system authorization and tenant isolation",
      "why": "This is a frontend delta review; backend authorization and production configuration were not changed or retested."
    }
  ],
  "blocking_findings": [
    {
      "finding": "G5-F1: ArchitectEntry.tsx line 137 announces the raw evaluation's success classification even when its BBL fails the visible result identity guard."
    }
  ],
  "reason_codes": [
    "FRONTEND_IDENTITY_ANNOUNCEMENT_MISMATCH"
  ],
  "next_claude_prompt": "Correct the presentation-only evaluation announcement identity guard, add mismatched/missing-BBL announcement regressions, freeze the resulting SHA, and request targeted independent G5 recheck. Preserve canonical clients and all existing failure announcements.",
  "owner_question": "",
  "rotation_reason": "",
  "evidence_refs": [
    {
      "path": "apps/web/src/components/architect/ArchitectEntry.tsx"
    },
    {
      "path": "apps/web/src/components/architect/__tests__/entry.test.tsx"
    },
    {
      "path": "apps/web/src/lib/address-search.ts"
    },
    {
      "path": "apps/web/src/lib/architect/zoning-context.ts"
    },
    {
      "path": "apps/web/src/lib/architect/source-links.ts"
    }
  ]
}
```

