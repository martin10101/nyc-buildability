# D-010 source-029 — Product-efficiency directive: reduce control-plane overhead + code verbosity without reducing quality/testing/safety (owner, 2026-08-09)

Captured verbatim from the owner's message (2026-08-09). Standing operating-policy that **applies to
all future work in this program**, not just this session. Sequenced by the owner as a side project:
do NOT interrupt the current M0-T054/M2-T015 work; apply the lean rules prospectively; M2-T016 is the
first product task under the leaner process. The owner subsequently instructed "do the lean process
implementation" — authorizing Phase 1 (policy-only) now while producer work is paused. Frozen base SHA
`14abf8e` (origin/main at capture). Full parking + managed order: `docs/OWNER_EFFICIENCY_DIRECTIVE_PLAN.md`.

## Verbatim owner text

> OWNER PRODUCT-EFFICIENCY DIRECTIVE — REDUCE CONTROL-PLANE OVERHEAD AND CODE VERBOSITY WITHOUT REDUCING QUALITY, TESTING OR SAFETY
>
> GOAL
>
> Improve the speed and maintainability of NYC Buildability by reducing duplicated control-plane work, unnecessary handoff narration and repetitive code.
>
> This is not authorization to weaken verification, remove required evidence, reduce adversarial testing, bypass safety boundaries or redesign the supervisor.
>
> The guiding rule is:
>
> CUT DUPLICATED EXPLANATION AND MANUAL BOOKKEEPING — NOT VERIFICATION, TESTING, PROVENANCE OR SAFETY.
>
> SEQUENCING
>
> Do not interrupt or broaden any currently executing M0-T054 turnover work, protected-config procedure, M2-T015 completion work or required acceptance lifecycle.
>
> Capture this directive durably at the next already-required lawful control-plane seam. Do not create an immediate standalone PR merely to repeat this message if it can lawfully join the next existing control-plane PR.
>
> Apply the lean operating rules prospectively after M2-T015 acceptance. Use M2-T016 as the first full product task operating under the leaner process.
>
> Do not begin a repository-wide refactor.
>
> Do not turn this directive into a multi-day supervisor-improvement project.
>
> PART A — CONTROL-PLANE AND HANDOFF EFFICIENCY
>
> 1. ESTABLISH ONE CANONICAL ROUTINE EXECUTION RECORD
>
> Inspect the current overlap between: task JSON; state JSON; runtime journal/ledger; SESSION_HANDOFF; producer report; directive verification; PR description; gate evidence. Identify which routine facts are currently written manually in more than one location, including: task status; progress percentage; latest safe commit; completed unit; test result; review verdict; current blocker; next action. Choose the smallest existing machine-readable record that can remain the canonical source for ordinary unit progress. Prefer an existing journal/event record rather than inventing another database, service or parallel source of truth. Other status views and reports should be generated or projected from that canonical evidence wherever safely possible. Do not delete, rewrite or invalidate existing historical evidence. This change is prospective.
>
> 2. MINIMAL UNIT-COMPLETION EVENT
>
> For each completed product unit, record one small structured event containing only what is necessary: task ID; unit/checkpoint ID; branch; exact commit SHA; tests executed and result; Codex/reviewer verdict; blocker, if any; next authorized unit/action; evidence links or digests. Do not manually rewrite that same information into several narrative files after every unit.
>
> 3. HANDOFFS ONLY AT REAL SEAMS
>
> Create or materially refresh a handoff only when one of these occurs: an actual main-orchestrator or worker context rotation; a model turnover; a stop requiring an owner decision; a material failure/recovery incident; task submission or acceptance; another demonstrated event where a successor cannot continue safely from the canonical records. Do not produce a full historical handoff after every normal unit or supervisor cycle. A routine handoff should normally contain only: 1. active task and current status; 2. active branch and latest safe SHA; 3. completed units; 4. current unfinished unit; 5. current blockers/owner decisions; 6. exact next action; 7. links to authoritative evidence. Historical detail remains available through Git and the durable journal. Do not repeatedly paste old session histories into the current handoff. Keep an ordinary handoff within approximately 2,000 tokens unless material evidence genuinely cannot fit. If critical evidence cannot fit, link to the authoritative repository record rather than silently omitting it.
>
> 4. FEWER CONTROL-ONLY PULL REQUESTS
>
> For an ordinary product task: product work continues through intentional commits on its task branch; routine machine-readable evidence accumulates during execution; routine control-plane updates are batched into one meaningful seam PR; a second control PR is acceptable for final acceptance if required by the existing lifecycle. Separate immediate control PRs remain appropriate for: new owner decisions that must be durable before action; security incidents; protected-config changes; material recovery events; legal or policy decisions; any existing rule that genuinely requires pre-action durability. Do not combine unrelated product code and privileged controller changes merely to reduce PR count. Target one or two routine control-plane PRs per ordinary product task, excluding legitimate owner/security/recovery events.
>
> 5. PRODUCER REPORTS AND PR DESCRIPTIONS
>
> Generate objective sections from authoritative evidence where possible: commits; changed files; test commands/results; gate verdicts; requirement coverage; evidence paths. Reserve manually authored narrative for actual engineering judgment: architectural decisions; unresolved risk; compatibility decisions; material limitations; deployment holds; professional/legal boundaries. Do not have Claude manually restate machine-verifiable facts in multiple places.
>
> 6. CONTROL-PLANE TIME BUDGET
>
> Routine control-plane administration should normally consume no more than approximately 15–20% of execution effort. This is an efficiency target, not permission to skip required evidence. If routine bookkeeping exceeds that range without a security incident, owner decision, protected change or failed gate, report the duplicated work and return attention to the product. Do not create another supervisor feature solely to calculate this percentage.
>
> 7. SAFER PACKETS WITH FEWER FALSE BLOCKS
>
> Do not weaken path or scope enforcement. At packet creation, inspect the relevant dependency/generator impact so naturally necessary files are included in the bounded allowed paths from the beginning, including: generated artifacts; their source generator; their focused tests; directly required wiring files. Keep paths exact and bounded. Do not use broad wildcards simply to avoid scope decisions.
>
> PART B — CONCISE, MAINTAINABLE CODE
>
> 1. PRESERVE BEHAVIOR AND SAFETY
>
> Do not simplify away: deterministic calculations; typed failures; fail-closed behavior; immutable provenance; per-fact evidence lineage; correction-history integrity; material-evidence promotion gates; qualified-human approval boundaries; adversarial document handling; tax-lot-as-cross-check-only doctrine; B-001 deployment honesty; existing five-borough scope; normal tests and gates. Line-count reduction is not itself an acceptance criterion.
>
> 2. CENTRALIZE ARCHITECTURAL DOCTRINE
>
> Keep the complete explanation of project doctrine in the relevant architecture/security documentation. Inside implementation files: module documentation should concisely state purpose, authority boundary and unusual security assumptions; function documentation should explain inputs, outputs and non-obvious invariants; comments should explain why a surprising decision exists; comments should not repeatedly restate visible code or reproduce the entire project philosophy. Reference the canonical architecture document where appropriate instead of duplicating several paragraphs in every module. Do not remove comments that preserve an important security rationale or explain a demonstrated past defect.
>
> 3. SHARED TYPED VALIDATION RESULTS
>
> Where current modules repeatedly create their own versions of: accepted result; refused result; immutable verdict; typed error payload; malformed-input refusal; fail-closed serialization; identify whether a small existing shared result abstraction can serve them safely. Prefer a minimal common set of typed result patterns over bespoke near-identical dataclasses in every validator. Do not create an elaborate framework or internal programming language. Extract shared behavior only where repetition is real and the common semantics are genuinely identical.
>
> 4. TABLE-DRIVEN SURVEY RULES
>
> Where appropriate, define grounded relationships in one canonical rule table or registry: survey fact type; accepted normalized-value shape; supported units; required deterministic validations; geometry/location requirement; professional-confirmation requirement; material/non-material classification. Validators should consume the same grounded rules rather than independently reproducing overlapping conditional logic. The table must remain closed, typed, deterministic and covered by tests. Unknown combinations must still fail closed.
>
> 5. SHORT TYPED ERRORS WITH STRUCTURED DETAILS
>
> Prefer: stable typed error/rejection code; concise human-readable message; structured metadata containing submitted value, expected rule and failed condition. Do not place a full architecture essay inside every runtime error string. Long explanations belong in documentation or the UI's explanatory layer. Preserve enough detail for debugging, evidence review and professional use.
>
> 6. PARAMETERIZED ADVERSARIAL TESTS
>
> Do not reduce adversarial coverage. Where many tests repeat the same setup and assertion shape, use parameterized fixture tables containing: case name; input; expected result; expected typed error; material invariant being proved. Preserve each existing malicious, malformed, ambiguous, tampered and unresolved case. Do not combine tests when doing so would hide which security invariant failed.
>
> 7. GENERATED CONTRACT TYPES
>
> Continue using deterministic generation for contract-derived TypeScript/Python types where appropriate. Do not maintain parallel hand-written representations when they can safely be generated from the authoritative schema. Generation must remain deterministic, drift-checked and covered by normal CI.
>
> 8. FILE AND FUNCTION DESIGN
>
> Use cohesive modules with small public interfaces. Do not split files merely to satisfy an arbitrary line limit. Do not allow a module to become a mixture of unrelated parsing, validation, persistence and business-rule authority. Prefer straightforward functions and data tables over excessive wrapper classes and layers. Avoid adding a new abstraction until it removes demonstrated repetition or protects a material invariant.
>
> 9. PDF PARSER KEEP-VERSUS-REPLACE ASSESSMENT
>
> After M2-T015 acceptance, perform only a bounded assessment of the custom PDF lexer/container/object/xref/content implementation. Compare: security and malformed-document handling; deterministic behavior; dependency/advisory exposure; supported PDF features; maintenance burden; sandbox compatibility; test coverage; whether a mature pinned library can provide equivalent behavior. Do not replace the parser merely to reduce line count. Do not begin a broad parser rewrite under this directive. If the custom implementation protects unique project requirements, retain it and identify only focused simplifications. If a mature library is demonstrably safer and materially smaller, create a separate clearly scoped product task with migration and regression evidence.
>
> PART C — IMPLEMENTATION METHOD
>
> PHASE 1 — POLICY-ONLY, AFTER M2-T015 ACCEPTANCE
>
> Make the smallest prospective operating-policy changes necessary to establish: one routine execution source of truth; minimal unit events; seam-only handoffs; batched control-plane PRs; generated objective reporting; concise-code expectations; parameterized-test expectations. Do not modify the supervisor core merely to write these policies. Do not rewrite existing product modules during Phase 1.
>
> PHASE 2 — PROVE THE LEAN PROCESS ON M2-T016
>
> Run M2-T016 using the new operating rules. Measure and return: product units/commits completed; number of handoff rewrites; number of routine control PRs; approximate control-plane versus product effort; duplicated records eliminated; whether any required evidence became harder to locate; whether any gate/reviewer lost necessary context. If evidence quality or recoverability deteriorates, stop and correct the lean policy. Do not weaken the required evidence to meet an efficiency target.
>
> PHASE 3 — AUTOMATE ONLY A DEMONSTRATED BOTTLENECK
>
> Only if M2-T016 still demonstrates material duplicated manual bookkeeping may you implement one small bounded helper that projects existing canonical events into required status/report views. Requirements for any helper: no new database or service; no supervisor redesign; deterministic output; idempotent regeneration; drift test; no deletion of authoritative evidence; no silent overwriting of owner-authored judgment; independent Codex review; normal CI coverage. Any broader automation requires a separate owner decision.
>
> PART D — REVIEW REQUIREMENTS
>
> Codex must independently review the proposed efficiency changes for: accidental loss of evidence; weakened fail-closed behavior; hidden incompatibility with directive compliance; unclear authority/source-of-truth ownership; excessive new abstraction; tests removed or made less diagnostic; product work being delayed by process optimization. The correct verdict is REVISE if efficiency is achieved by deleting required evidence, combining materially different safety cases or weakening gates.
>
> PART E — PROHIBITIONS
>
> Do not: interrupt the current M0-T054/M2-T015 sequence; reopen accepted supervisor defects without new qualifying evidence; alter protected config or ACLs under this directive; authorize LIMITED-AUTO; change supervised-auto activation; weaken command/path/credential protections; rewrite Git history; delete existing evidence; perform a repository-wide style cleanup; create a multi-week refactor; count deleted lines as product progress; delay the architect/browser MVP for cosmetic neatness; replace functioning security-sensitive code without comparative evidence.
>
> RETURN
>
> At the appropriate post-M2-T015 seam, return: 1. the map of currently duplicated control-plane facts; 2. the selected canonical routine execution record; 3. the lean handoff format; 4. the exact future handoff triggers; 5. the routine control-PR batching rule; 6. the concise-code and parameterized-test guidance adopted; 7. the exact files changed for Phase 1; 8. proof that no safety, evidence, gate or provenance requirement was removed; 9. the M2-T016 before/after efficiency measurements; 10. any narrowly justified follow-up helper task.
>
> Then continue product development autonomously.
>
> The supervisor exists to accelerate the NYC Buildability product. Process optimization is successful only when it produces more reliable product delivery with less duplicated work.
>
> this new update should apply to all future work in this program not just for this season after this is done you can continue reg program build

## Capture annotations (orchestrator, non-authoritative)

- Standing operating-policy; applies to all future work. Guiding rule: cut duplicated explanation +
  manual bookkeeping, NOT verification/testing/provenance/safety. Line-count reduction is never an
  acceptance criterion.
- Owner follow-up "do the lean process implementation" authorizes **Phase 1 (policy-only) now** while
  producer work is paused; it does not authorize rewriting product/supervisor code, a repo-wide
  refactor, retroactive application, or interrupting the M0-T054/M2-T015 sequence.
- Phase 2 (prove on M2-T016) and Phase 3 (bounded projector helper, only if still needed) remain
  gated as written. Part B.9 PDF assessment stays post-M2-T015-acceptance, comparison-only.
- Independent review (Part D) via the code-reviewer/security-reviewer/control-plane-verifier at the
  Phase-1 gate seam; REVISE if efficiency deletes evidence, merges safety cases, or weakens gates.
