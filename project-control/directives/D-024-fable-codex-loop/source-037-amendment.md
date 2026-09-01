# D-024 Amendment 37 — narrow AD-093 defect-lane task for the journey-5 invalid_checkpoint: controller-authoritative git-state checkpoint enrichment (owner instruction 2026-09-01)

Captured: 2026-09-01 UTC by the orchestrator (Fable 5), verbatim, BEFORE acting.
Base identity at capture: HEAD `f10353ab` (campaign seq 68). Amends: `source-001.md`.
Requirement IDs: D-024-R460..D-024-R471.

Reconciliation: authorizes ONE narrow AD-093 defect-lane task (new ledger task M0-T133) to fix the
journey-5 `invalid_checkpoint` (opus worker omitted the four git-state fields
`branch`/`worktree`/`starting_sha`/`current_sha`). The smallest durable correction makes those four
CONTROLLER-AUTHORITATIVE envelope fields the controller populates deterministically before final
checkpoint validation (dispatch context + a fresh read-only git measurement), with exact normalized
match-or-fail-closed when the worker supplied any, preserving the worker's original bytes and auditing
the enrichment. No prompt-only fix, no bare Opus retry, no weakening of any other checkpoint-integrity
requirement. Approved fallback models used immediately (do not wait for Fable). If the correction
cannot be made without weakening fail-closed checkpoint integrity, STOP and report the precise blocker.

Forward trace: para 1 (authorize ONE narrow AD-093 task; use approved fallback models immediately; do
not wait for Fable; optimize fastest safe return) -> R460; "smallest durable correction" + cond 1 (no
prompt-only, no bare Opus retry) -> R461; cond 2 (controller-authoritative envelope fields) -> R462;
cond 3 (populate only those four before final validation from dispatch context + fresh read-only git)
-> R463; cond 4 (worker-supplied -> exact normalized match; mismatch/unreadable/unexpected-branch/
wrong-worktree/ambiguous-SHA fail closed) -> R464; cond 5 (preserve original bytes; audit which fields
added; never present enrichment as worker-authored) -> R465; cond 6 (do not alter semantic completion/
evidence/status/review/advancement/worktree-isolation/effect/budget/owner-gate requirements) -> R466;
cond 7 (removal-sensitive tests, 8 scenarios) -> R467; cond 8 (affected packs first; single final
identity ONE golden + ONE whole suite once; independent gates + DCV parallel; no broad 17-defect
survey; no unrelated cert repeats) -> R468; cond 9 (preserve PAUSED_RECOVERY journal/audit 104/pending
0/worktrees/budgets/owner-touch/model pin/manifest/PR #241) -> R469; cond 10 (after acceptance + ONE
R247 recert, stop and present targeted proof + exact clear-recovery + one parse-validated start with a
fresh unused run id; no additional optional work) -> R470; final para (do not clear recovery/start/
execute commissioning yourself; stop-and-report if fail-closed integrity would weaken) -> R471.
Anchors: #authorization (R460), #smallest-correction (R461), #authoritative-fields (R462),
#populate-before-validation (R463), #match-or-fail-closed (R464), #preserve-and-audit (R465),
#no-other-weakening (R466), #tests (R467), #test-sequence (R468), #preservation (R469),
#present-commands (R470), #stop-if-weakening (R471).

---VERBATIM-BEGIN---
I authorize one narrow AD-093 defect-lane task for the journey-5 `invalid_checkpoint` finding. Use the approved fallback models immediately; do not wait for Fable availability. Optimize for the fastest safe return to commissioning.

Implement the smallest durable correction:

1. Do not make a prompt-only wording fix and do not simply retry Opus.
2. Treat `branch`, `worktree`, `starting_sha`, and `current_sha` as controller-authoritative checkpoint-envelope fields because the controller already knows or can measure them deterministically.
3. Before final checkpoint validation, populate only those four fields from the dispatch context and a fresh read-only git measurement.
4. If the worker supplied any of those fields, require an exact normalized match. Any mismatch, unreadable repository state, unexpected branch, wrong worktree, or ambiguous SHA must still fail closed.
5. Preserve the worker’s original checkpoint bytes as evidence and audit exactly which controller-authoritative fields were added. Never present enrichment as worker-authored data.
6. Do not alter semantic completion, evidence, status, review, advancement, worktree-isolation, effect, budget, or owner-gate requirements.
7. Add focused removal-sensitive tests for:
   - all four fields missing and safely enriched;
   - partially missing fields;
   - supplied fields matching;
   - each supplied field mismatching;
   - unreadable/ambiguous git state;
   - normalized Windows worktree paths;
   - the exact journey-5 Opus checkpoint fixture;
   - no false completion or advancement.
8. Run the directly affected checkpoint/runner/loop/recovery packs first. At the single final identity, run one fast golden pack and one whole supervisor suite only once, followed by the required independent gates and DCV in parallel where allowed. Do not reopen the broad 17-defect survey or repeat unrelated certification runs.
9. Preserve the current PAUSED_RECOVERY journal, audit 104, pending effects 0, worktrees, budgets, owner-touch history, model pin, manifest, and PR #241 throughout implementation.
10. After acceptance and the single required R247 recertification, stop and present:
    - the targeted proof;
    - the exact owner-typed `clear-recovery` command;
    - one parse-validated start command using a fresh unused run ID;
    - no additional optional work.

Do not clear recovery, start the loop, or execute the commissioning commands yourself. If this correction cannot be made without weakening fail-closed checkpoint integrity, stop and report the precise blocker instead.
---VERBATIM-END---
