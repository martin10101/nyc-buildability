# D-024 Amendment 14 — shell-routing compatibility reconciliation: separate bounded task (M0-T120) before the M0-T119 recertification completes (owner instruction 2026-08-29)

Captured: 2026-08-29 UTC by the orchestrator (Fable 5), verbatim from the owner's interactive
message. Base identity at capture: branch `control/D-024-fable-codex-loop`, HEAD
`85cbcc42e704b523546b6c37d632cdb3204d7eaa` (local == origin; clean tree after reverting an
uncommitted activation-package draft, see timing disclosure). Amends: `source-001.md` (owner
directive v4). Requirement IDs assigned: D-024-R289..D-024-R297.

**Timing disclosure (honest reconciliation):** at the moment this directive arrived,
M0-T118 was ALREADY accepted (DCV 5/5 PASS; accept commit `5251c73`) — R289 was therefore
already satisfied — but M0-T119 had ALREADY been claimed (G0 + claim commit `85cbcc4`,
~35 minutes earlier) and its certification runs had started (golden pack 41/41, affected
packs 499/1, whole suite in flight). Nothing of M0-T119 was submitted, gated, or certified.
On receipt of this directive the orchestrator HALTED M0-T119 work, reverted the uncommitted
activation-package draft, declared the pre-directive certification runs VOID for
certification purposes (the certified identity will change when M0-T120 lands), and placed
M0-T119 on hold per R297. The single M0-T119 recertification will re-run in full at the ONE
final identity that includes M0-T120 (R296).

**Reconciliation finding (R290, durable evidence):** ledger-wide search
(`project-control/tasks/`, `project-control/directives/`) for
bashFirst / bash-first / shell-first / 88041 / shell-routing / native-tool-routing returns
ZERO task or requirement addressing the original shell-first ASK behavior. The three
ASK-held commands from the first live run (`M0-T113-activation-evidence.md` item 4: two
PowerShell + one Bash read-only discovery proposals instead of native file tools) remain
unresolved as WORKER-ROUTING behavior — M0-T115 fixed only the deny→ask-row bookkeeping
seam. The owner's earlier direction (pre-Amendment-12 startup prompt items 3–9: separate
compatibility task, empirical routing proof, native-tool preference, drift detection,
Windows-specific shapes) was never instantiated as a ledger task. CONFIRMED MISSING → R291
creates M0-T120.

Forward trace: paragraph 1 sentence 1 ("Finish M0-T118 through DCV and acceptance.") →
R289; sentence 2 ("Before claiming M0-T119, reconcile the campaign against my earlier
direction concerning Claude Code Auto-mode bashFirst and GitHub issue #88041.") → R290;
paragraph 2 (the missing-task observation) → context verified under R290; paragraph 3
sentence 1 ("If durable evidence confirms this work is missing, create a separate bounded
task before M0-T119.") → R291; sentence 2 ("Empirically prove how installed Claude Code
2.1.251 routes routine discovery and edits under the controller's exact live launch
configuration.") → R292; sentence 3 ("Preserve the command broker and all owner gates; do
not broadly allow Python, PowerShell, sed, heredocs, redirections, compound commands, or
arbitrary scripts.") → R293; paragraph 4 sentence 1 ("Prefer native Read/Grep/Glob/Edit/
Write for repository discovery and editing, with required validation commands explicitly
classified and brokered.") → R294; sentence 2 ("Add a pre-dispatch drift tooth so changed
shell-routing behavior cannot silently enter a certified run.") → R295; paragraph 5
sentence 1 ("Keep this task separate, then include its final identity in the single
M0-T119 recertification.") → R296; sentence 2 ("Do not begin T119 until this
reconciliation is resolved") → R297.

Anchors: #finish-t118 (¶1 s1), #reconcile-bashfirst (¶1 s2 + ¶2), #create-separate-task
(¶3 s1), #empirical-routing-proof (¶3 s2), #broker-preserved (¶3 s3),
#native-tools-preference (¶4 s1), #pre-dispatch-drift-tooth (¶4 s2), #single-recert (¶5
s1), #t119-hold (¶5 s2).

---VERBATIM-BEGIN---
Finish M0-T118 through DCV and acceptance. Before claiming M0-T119, reconcile the campaign against my earlier direction concerning Claude Code Auto-mode bashFirst and GitHub issue #88041.
I do not see a separate accepted compatibility task proving that the original shell-first ASK behavior has been addressed. T117 controls updates and T118 recaptures fixtures; neither appears to resolve shell-first worker routing.
If durable evidence confirms this work is missing, create a separate bounded task before M0-T119. Empirically prove how installed Claude Code 2.1.251 routes routine discovery and edits under the controller’s exact live launch configuration. Preserve the command broker and all owner gates; do not broadly allow Python, PowerShell, sed, heredocs, redirections, compound commands, or arbitrary scripts.
Prefer native Read/Grep/Glob/Edit/Write for repository discovery and editing, with required validation commands explicitly classified and brokered. Add a pre-dispatch drift tooth so changed shell-routing behavior cannot silently enter a certified run.
Keep this task separate, then include its final identity in the single M0-T119 recertification. Do not begin T119 until this reconciliation is resolved
---VERBATIM-END---
