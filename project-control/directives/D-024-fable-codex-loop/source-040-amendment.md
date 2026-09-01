# D-024 Amendment 40 — Tranche-B producer authorization + subagent model-selection policy (owner directive, 2026-09-01)

**Kind:** amendment (append-only) · **Amends:** source-001.md · **Sequence:** 40
**Recorded_at:** 2026-09-01T22:30:00+00:00 · **Actor:** orchestrator (Tranche-B producer session)
**Base identity at capture:** frozen origin/main `d8b3899f61efa6620e18a26541ced96020f5bef9`;
clean base `6f5d12a6203c2c89390a982657fa8d66a91a0c3d` (= `origin/control/D-024-fable-codex-loop`);
new local candidate branch `candidate/D-024-mrl-option-b` created from that exact base; archive/evidence
branch `stabilization/D-024-mrl` preserved unchanged at `76c4edff3175f0d185c136e52e1329e3a5cf8199`
(M0-T134 formally accepted there; accepted code tree `5e89175d`); no upstream; nothing pushed.
**Session:** session_01Bc5Kqa74kPZ4h6nJaXM63k.

This amendment (a) confirms the formal acceptance of M0-T134 (MRL Tranche A), (b) authorizes ONE bounded
Tranche-B producer workflow whose Cluster B0 is the clean reapplication onto the clean base, (c) rejects
the previously suggested one-line reapply command as an inadequate continuity procedure, (d) authorizes
deletion (after Tranche-A acceptance) of the stale `claude_runner.py` modularity file-exception entry
ONLY, (e) adds concise defect-convergence guidance through the existing reliability architecture, and
(f) sets the standing model-selection policy (main session Fable 5.1 at effort high; fallback
claude-opus-4-8 at effort xhigh; owner-commanded thematic switching of subagent selections only). It
supersedes no prior requirement; it adds R515 onward. Where it authorizes Tranche B it lifts, for this
one bounded workflow only, the Amendment-39 stop-after-Tranche-A instruction (R513); every other hold
(no push, no PR, no merge, no remote branch, no protected-branch change, PR #241 untouched, no live loop,
no Tranche C) remains.

---

## Verbatim owner authorization

> M0-T134 is formally accepted. Proceed as the Tranche-B producer under the authorization below. This is one bounded Tranche-B workflow; the clean reapplication is Cluster B0, not a separate initiative.
>
> Do not execute the previously suggested one-line "git switch ... && git checkout ..." command. It is not an adequate continuity procedure because it copies only tools content, uses a directory-level schemas path, and does not reconstruct the canonical project-control state on the clean base.
>
> Authorization boundaries:
>
> - Local branch creation, authorized local edits, tests, governance records, and logical local commits are permitted.
> - No push, remote integration-branch creation, branch-protection change, PR creation/update, merge, task auto-acceptance, production deployment, or real Codex-loop launch.
> - PR #241 and all remote refs remain untouched.
> - Do not begin Tranche C.
> - Do not run live provider canaries until the offline implementation and canary package are complete. Prepare the exact owner-run PowerShell commands and stop for owner execution.
> - You may use foreground subagents within scope for parallel read-only tracing, variant analysis, isolated non-overlapping implementation, test analysis, and independent self-review. The primary session is the sole integrator and committer. No background agents or subagent Git operations.
>
> Apply defect convergence: survey and cluster the complete Tranche-B failure surface before implementation. Resolve related producers, consumers, schemas, CLI wiring, policies, tests, documentation, and Windows behavior together. Do not stop after each ordinary defect. Use focused tests while editing, affected tests when a cluster closes, and final regression once on the frozen candidate.
>
> CLUSTER B0 — clean base and canonical continuity
>
> 1. Verify "stabilization/D-024-mrl" is clean at acceptance commit "76c4edff", with no upstream and no remote effects.
> 2. Preserve that branch unchanged as the evidence/archive branch.
> 3. Verify the proposed local branch name does not already exist before creating anything.
> 4. Create a new local candidate integration branch from exact base "6f5d12a6203c2c89390a982657fa8d66a91a0c3d". This is local only and is not yet the protected remote Option-B branch.
> 5. Reapply exactly the approved 19-file Tranche-A tools delta. Use explicit individual file paths; do not checkout an entire directory.
> 6. Independently compare every reapplied production/schema/test blob with the accepted code tree at "5e89175d". All 19 must be byte-identical.
> 7. Do not copy the abandoned branch ancestry or blindly copy "project-control/".
>
> Before writing governance, perform a reference-closure inventory from the accepted state. Identify every canonical semantic record required so the clean branch truthfully contains:
>
> - the applicable owner directives and exact requirement rows;
> - the accepted M0-T134 task state;
> - its evidence map;
> - G0/G2/G3/G4/DCV records;
> - its verification row and reviewed identity;
> - every task/report/directive reference required by validators;
> - the correct current project-control status and continuation point.
>
> Reconstruct that minimum complete semantic state through canonical project-control tooling and cleanly formatted targeted edits. Do not import abandoned M0-T133 renewal state, noisy reserialization churn, stale current-work pointers, or obsolete handoff claims. No dangling reference to evidence that exists only on the archive branch is permitted.
>
> Run every project-control, directive, task, manifest, evidence, MCP, and campaign-continuity validator. The clean branch must independently report M0-T134 accepted and have one coherent next state. If reproducing accepted governance on a rewritten clean SHA requires a canonical cross-SHA provenance record, create that record explicitly rather than pretending the old reviewed SHA is the new SHA.
>
> Resolve the stale modularity exception during B0:
>
> - Capture this owner clarification canonically: the earlier byte-identical restoration was the Tranche-A anti-renewal requirement; after formal Tranche-A acceptance, deletion of only the stale "tools/agent_supervisor/claude_runner.py" file-exception entry is authorized.
> - Do not renew, extend, narrow, replace, or regenerate an exception or baseline.
> - Keep "tools/modularity_baseline.json" unchanged.
> - Before deletion, independently prove the expected baseline material-growth limit and current SLOC.
> - Delete only that file-exception entry.
> - Prove the unpiped modularity gate remains green without it.
> - Preserve the inert baseline-regeneration record unless canonical policy requires otherwise.
>
> Add the previously approved concise defect-convergence guidance through the existing reliability architecture—not a new large skill:
>
> - short always-loaded instruction in root "CLAUDE.md";
> - extend the existing "/engineering-reliability" routing/standard only as necessary;
> - require failure-surface inventory, change-impact analysis, variant analysis, root-cause clustering, bounded repair, progressive verification, and frozen-candidate regression;
> - keep the addition concise and avoid duplicating existing debugging rules.
>
> After B0, freeze a clean candidate SHA and run:
>
> - all 77 Tranche-A focused cases;
> - the full affected supervisor suite;
> - unpiped modularity;
> - applicable lint;
> - all project-control/directive/continuity validators.
>
> Any failure must be consolidated and resolved before Tranche B behavior is added.
>
> TRANCHE-B IMPLEMENTATION CLUSTERS
>
> B1 — Versioned launch manifest and live repository binding
>
> Build one canonical "start --launch-manifest <absolute-path>" entrance. The manifest supplies expected values but is never accepted as proof. Immediately before dispatch, independently verify the actual repository root, normalized origin, task ID, task-packet digest, worktree, branch, HEAD, tree, clean starting status, allowed paths, settings/profile identity, and authorized mode. Any expected-versus-observed mismatch must refuse before provider launch.
>
> B2 — Complete executable and runtime identity
>
> Resolve, hash, and bind the complete Claude and Codex dispatch chains: wrapper → runtime executable → actual package/entrypoint. Use streaming full SHA-256 immediately before every spawn, with no size/mtime hash cache. Verify updater disablement in the actual child environment. Verify runtime-reported model and version. Test same-size/restored-mtime replacement, wrapper retargeting, entrypoint replacement, updater re-enablement, and model/version mismatch.
>
> B3 — Restricted permissions with bounded subagents
>
> Do not permanently forbid Agent/subagent use. Build a controller-governed bounded-subagent contract:
>
> - configurable per-run concurrent-agent and total-agent limits;
> - initial delegation depth of one;
> - foreground agents only;
> - inherited repository identity, task, allowed paths, and tool restrictions;
> - controller-issued parent/child identities and global accounting;
> - parallel read-only analysis permitted;
> - single-writer integration or isolated non-overlapping worktrees;
> - no subagent commit, push, PR, merge, or acceptance;
> - complete descendant termination;
> - explicit denial of MCP and all tools outside the inventory.
>
> The restricted profile must combine the actual Claude CLI mechanisms correctly: restricted operation, "dontAsk", explicit tools inventory, exact approvals/denials, strict MCP denial, and accounted managed policy. Do not assume that "--tools" alone grants permission. Capability support must be proven by the later real Windows canary.
>
> B4 — One-shot wiring, budgets, and containment
>
> Wire the accepted Tranche-A WorkerResult, ReviewVerdict, remote observation, gate recorder, transport, and executable-identity primitives into the actual CLI/loop path. One task uses one fresh Claude process, one prompt, one schema-bound result, stdin closes, no resume, no second message, no background fallback. Apply total run accounting across the primary worker and subagents. Enforce process and turn limits. Cancellation or timeout must terminate and prove zero remaining descendants.
>
> B5 — PowerShell launch path and canary package
>
> Replace or prominently obsolete the stale main-based runbook so there is exactly one operator launch path. Build real PowerShell tests that preserve raw "$LASTEXITCODE" and cannot be made green through piping or "Tee-Object". Prepare one exact owner-run canary package that tests:
>
> - clean-base manifest launch;
> - live repository mismatch refusal;
> - Claude/Codex child authentication;
> - runtime model/version identity;
> - updater disablement;
> - restricted tool denial;
> - one successful one-shot result;
> - bounded subagent fan-out and over-limit denial;
> - full process-tree cleanup;
> - bad-command raw exit-code preservation.
>
> Do not execute the live provider canaries yourself in this authorization.
>
> Testing and evidence:
>
> - Every positive contract needs a paired negative or mutation test.
> - Gate results must come from the raw gate recorder.
> - No hand-authored success claims.
> - Do not run the entire suite after every edit.
> - When all B clusters are complete, freeze one candidate SHA and run the complete affected and repository verification once.
> - Any later code change invalidates that final verification.
> - Regenerate "docs/SESSION_HANDOFF.md" only at the final frozen B candidate, not during intermediate work.
>
> Finish with exactly one of:
>
> "TRANCHE_B_OFFLINE_COMPLETE_CANARIES_READY"
>
> or
>
> "CONSOLIDATED_BLOCKED"
>
> Report the archive identity, clean-base identity, complete governance continuity mapping, exact commits, changed files, root-cause clusters, tests and raw return codes, mutation results, modularity-without-exception result, protected-file comparisons, final Git status, and the single owner-run PowerShell canary package. Report every blocker together. Do not push, launch the real loop, or begin Tranche C.
>
> Awesome one other thing to add. Since every single model selection that cortex can select has values like ultra-high medium Max. I wanna be able to just tell codex, hey, switch all the subagents to ultra or Max, or whatever the case is, and it should do a thematically, and the main should always stay on fable 5.1 that just came out and it should be on high nutmegs, just high. Fable,5.1 high, that should be the standard. And when it falls back, it should fall back to opus four point eight x high, but again the main will stay. This will be the two selections, but if for the sub agents, I should be able to tell it, go this way or that way

---

## Capture notes (orchestrator; not owner text)

- The final paragraph is a voice-transcribed owner addendum. It is captured verbatim above. The
  orchestrator reads "cortex"/"codex" as the Claude Code session/agent system being commanded, "ultra"
  as the extra-high effort level (`xhigh`), and "high nutmegs, just high" as effort level `high`.
  Any reading that materially changes scope is recorded as an unresolved question row (R-class
  `question`) rather than silently interpreted; the exact model identifier for "Fable 5.1" is an
  external time-sensitive fact that must be verified, never guessed (permanent principle 3).
- "Previously suggested one-line command" refers to the `git switch -c ... && git checkout ad770ad4 --
  ...` line in the M0-T134 acceptance return; it is rejected by this amendment.

## Source anchors (forward trace)

- #accept-and-role — M0-T134 formally accepted; proceed as Tranche-B producer; one bounded workflow; B0 = clean reapplication.
- #reject-one-liner — do not execute the one-line reapply command; inadequate continuity procedure.
- #boundaries — permitted local actions; prohibited remote/acceptance/deployment/live-loop actions; PR #241 + remote refs untouched; no Tranche C; no live canaries before package complete; subagent rules (foreground, in scope, primary session sole integrator/committer, no background agents, no subagent Git).
- #defect-convergence — survey/cluster failure surface before implementation; resolve related surfaces together; progressive verification cadence.
- #b0-steps — the seven numbered clean-base steps.
- #b0-reference-closure — reference-closure inventory items; reconstruction rules; exclusions; no dangling archive-only references.
- #b0-validators — run every validator; independent M0-T134 accepted report; one coherent next state; explicit cross-SHA provenance record.
- #b0-modularity — stale exception resolution: owner clarification capture; deletion-only authorization; no renew/extend/narrow/replace/regenerate; baseline unchanged; prove limit + SLOC before deletion; prove gate green unpiped; preserve inert regeneration record.
- #b0-guidance — concise defect-convergence guidance via CLAUDE.md + /engineering-reliability; required elements; concise, non-duplicating.
- #b0-freeze — freeze clean candidate SHA; five verification items; consolidate failures before Tranche B behavior.
- #b1-launch-manifest — one canonical start --launch-manifest entrance; expected vs observed verification list; refuse before provider launch.
- #b2-executable-identity — full dispatch-chain hashing; streaming SHA-256 before every spawn; no cache; updater disablement in child env; runtime model/version; five named test classes.
- #b3-bounded-subagents — no permanent Agent prohibition; bounded-subagent contract items; restricted profile composition; --tools alone does not grant permission; capability proven by later real Windows canary.
- #b4-one-shot-wiring — wire Tranche-A primitives into the CLI/loop path; one-process/one-prompt/one-result semantics; total run accounting; process/turn limits; termination with zero-descendant proof.
- #b5-launch-path-canary — single operator launch path (obsolete stale main-based runbook); real PowerShell tests preserving raw $LASTEXITCODE; the ten-item owner-run canary package; no live canary execution in this authorization.
- #testing-evidence — paired negative/mutation tests; raw gate recorder results; no hand-authored success claims; no full-suite-per-edit; single final frozen verification; later change invalidates; handoff regenerated only at final frozen B candidate.
- #return — terminal token; required report items; report every blocker together; no push/live loop/Tranche C.
- #model-selection — main session Fable 5.1 effort high as the standard; fallback claude-opus-4-8 effort xhigh; owner-commanded thematic switch of subagent selections (effort/model) without touching the main pin.
