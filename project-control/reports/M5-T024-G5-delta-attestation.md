# G5 DELTA RE-REVIEW ATTESTATION — M5-T024

> Preservation note: saved VERBATIM by the orchestrator from the same G5 reviewer's agent-return
> channel (transport entity-decoding only). Companion to M5-T024-G5-security-review.md.

**Prior verdict:** G5 PASS at content identity `0002ddb7` (one advisory A1).
**New content identity:** `9ce75316` on candidate/D-024-mrl-option-b (HEAD `b08a0c88` adds only control-plane lifecycle files — confirmed `git diff 9ce75316..b08a0c88 --stat` = state.json + M5-T024.json only).
**Delta reviewed:** `git diff 0002ddb7..9ce75316 --stat` → checklist (111 lines) + producer-report addendum (57 lines) + orchestrator control-plane artifacts (gates, review reports, state, task). I read the full checklist diff and the report addendum, and re-ran my privacy grep against the checklist blob at `9ce75316`.

## VERDICT: G5 PASS STANDS at content identity 9ce75316

### (a) A1 — SATISFIED
The honest-exposure note is now **§5** ("Honest exposure note — READ THIS BEFORE §6"), physically preceding the CORS + API-flag step (now **§6**). Verified in the diff:
- Content moved **verbatim and intact** — the three exposure bullets (no-auth → routes reachable by anyone holding the URL; "the flag is a feature toggle, not an access control"; "Unlisted is not secret"; "Real access control arrives with the auth layer, blocked on B-001") are unchanged; only position/numbering moved.
- Cross-references consistently updated: §0 now "See §5 before turning the internal flag on" (was §6); §6 step 2 back-references it ("You already read the exposure consequence in §5"); §4 CORS pointers now say §6.
- A strict top-to-bottom reader now meets the exposure note **before** the API-flag step. My original advisory is fully resolved; no residual.

### (b) Fresh privacy grep at 9ce75316 — CLEAN
```
$ git show 9ce75316:docs/…CHECKLIST.md | grep -noE 'https?://[a-zA-Z0-9.-]+' | sort -u
135:http://127.0.0.1                 # documented local default only
$ … grep -niE 'onrender|sk-|bearer|-----BEGIN|eyJ|password=|token=|api_key=|#241|robots|sitemap|indexing|marketing'
28: "No public listing, marketing, indexing, or removal of the internal/dev posture"   # negative/exclusionary only
```
The only URL literal remains `http://127.0.0.1` (the genuine code default, `apps/web/src/lib/api.ts:153`). The new RC-1 text adds URL examples of the form `<new-web-service-origin>/property?ruleeval=on` — that is a **placeholder + route path**, no real host; confirmed by the grep finding no additional URL literal. The producer-report addendum introduces no real URL/key/token (read in full). **D-043-R002 intact — no new leakage.**

### (c) No change weakens any of the six PASS items
1. **Secret/URL leakage** — unchanged/PASS (grep above; placeholders only).
2. **Exposure honesty** — **strengthened** (A1); content intact, now read before the flag step. Still does not imply an unlisted URL is access control — it explicitly denies it.
3. **CORS** — unchanged/PASS. §6 step 1 (formerly §5) retains exact-origin / no-wildcard / no-trailing-slash semantics matching `services/api/app/main.py:66-82,104`; §9 step 2 still directs fixing the exact-origin match, never loosening to wildcard.
4. **Secrets policy** — unchanged/PASS. §2 step 3 (Supabase blank per B-001, service-role never in frontend, publishable-only) untouched; the §2 step 1 edit only adds the two-factor-gate explanation.
5. **Scope prohibitions** — unchanged/PASS. No render.yaml change (§8 still "recorded, NOT done here"); no dependency change (docs-only); no PR #241; no public-launch/indexing action (only the negative statement at line 28). The RC-1 rework is confined to the opt-in URL and gate explanation.
6. **Owner boundary (Tier D / Section 20)** — unchanged/PASS. Every dashboard step remains owner-performed; credentials only via dashboard.

### Note (informational, not a G5 defect)
The RC-1 fix adds code-line citations (`apps/web/src/components/property/PropertyLookup.tsx:265`, `apps/web/src/app/property/page.tsx:30`, `rule-evaluation.ts:96-103`). The security-load-bearing fact — the two-factor gate makes internal surfaces unreachable by default (fail-safe) — I independently confirmed at `rule-evaluation.ts:96-103` (`ruleEvaluationSurfaceEnabled` requires env flag AND `?ruleeval=on`); this strengthens the exposure posture. The exact mount-point/UI-reachability accuracy of PropertyLookup.tsx:265 and page.tsx:30 is G1's evidence/technical-accuracy scope, not a G5 security/privacy concern.

**Attestation:** As the independent G5 reviewer, I attest that my G5 PASS verdict stands at content identity **9ce75316**. Advisory A1 is SATISFIED; no new privacy leakage was introduced; none of the six security/privacy PASS items is weakened. No blocking corrections. Recommendation to orchestrator: record G5 = PASS at reviewed_sha 9ce75316.
