# M0-T159 — G3 re-review of the REQUIRED CORRECTIONS (code-reviewer "cr-m0b", fresh reviewer, read-only)

> Transmission history: pinned at fa7e5fae, delivered as three SendMessage parts (1/3..3/3) ending with
> END-OF-REPORT; no truncation. Joined verbatim by the orchestrator (transport wrapper tags removed only).
> Scope: the reports-only correction commit cdd62c5c (cherry-pick of 651271b6) answering the first G3's
> PASS-with-required-corrections (M0-T159-G3.md, F1-F7). Verdict PASS (corrections); every correction
> closed with its facts verified; advisories A1-A5 are citation-level and do not change any owner action.
> This record re-stamps G3 at the re-frozen content identity; the original M0-T159-G3.md stays as history.

---

M0-T159 G3 re-review of REQUIRED CORRECTIONS (fresh reviewer, read-only). PART 1/3.

PIN: HEAD at start = fa7e5fae (matches expected). Correction commit cdd62c5c touches ONLY the two report files (git show --stat confirms); tools/ is byte-identical at a3f24ff3 (no code/fixture/test moved).

F1 — CLOSED, facts TRUE. Recert §1 and §5.0 name the candidate: commit a3f24ff3, commit_tree 82432361…, subtree 9c0b14ea…. I re-derived both with git: commit_tree = 82432361540c3c2a11c55ffa3d6d485426cd45f7, subtree = 9c0b14eaa56ce32d241c77f789266035b584380c, and git ls-tree -r counts 204 subtree files — all match. The 147-file / 55dc71350b… STOP is present at §5.4. The wrong-source guard is load-bearing and exactly right: cfc3d22c subtree = 11d43515… (differs), diff a3f24ff3..cfc3d22c = 4 files +1280/-8 (cli.py, evidence.py, gate_wave.py, policy.py — the uncertified M0-T149/T152 changes), parent 33662211 — every value in §5.0/§5.3 verified. STOP-on-11d43515 correctly blocks installing the integrated ledger commit.

F2 — CLOSED, facts TRUE. Recert §5.1–§5.10 map 1:1 to CONTROLLER_UPDATE_RUNBOOK §§2,3,4,5,5a,6,7,8,9; commands match verbatim, including the §4 source_worktree_exists removal (runbook:117 == recert:162). Verified in update_controller_from_candidate.ps1: install does `git worktree add --detach $binding.commit_sha` at :649 (so install RE-CREATES wt-controller-src at the bound commit — the mechanism §5.6 relies on); backup_stale refusal at :640; source_worktree_exists at :646. All as described.

F3 — CLOSED, facts TRUE. I read all three launchers: C:\SupervisorController{,2,3}\autostart-launch.ps1 each set $WorkDir = …\wt-controller-src and Start-Process … -WorkingDirectory $WorkDir, legacy explicit-flag form (no --launch-manifest), per-lane --checkout. So the runbook §5a allowance "remove the source worktree after §§6-8" WOULD strand all three lanes — and §5.5 correctly overrides it with DO NOT remove. This is a real safety improvement over the base runbook. The §5.6 propagation (robocopy /MIR + Assert-SameTree, then §5.7 verify-controller from all four dirs) is correctly ordered AFTER the source is installed+verified, and §5.1's lanes-stopped precondition protects the /MIR. wt-controller-src is currently detached at a5886dab (verified), matching the report.

Part 2 next.

---

M0-T159 G3 corrections — PART 2/3.

F4 — CLOSED, facts TRUE. Recert §5.11 drafts a FRESH launch manifest per lane using the exact MRL_LAUNCH_RUNBOOK §1 command (only --worktree/--task-packet substituted, everything else literal — matches runbook:23-38), checks it binds 2.1.281 / 946eb509…bfff1, then `start --repin-cli-identity` as the LAST act. The mechanism is stated precisely and is correct in code: claude_version_mismatch is raised on the launch-MANIFEST pin (mrl_one_shot.py:252, after verify_chain_now at :249), while --repin-cli-identity cures the JOURNAL pin provider_cli_drift (recovery_probes.py:367; cli_identity_repinned written at :388). So BOTH the fresh draft and the repin are genuinely needed, exactly as §5.11 says. This satisfies runbook §13 step 4 ("Only then repin… never repin first"). The chain value 2.1.281/946eb509 is producer-measured and correctly gated by a STOP if the check line prints anything else.

F5 — CLOSED. Producer report discloses the two previously-omitted fixture diffs: capability probe_meta.claude_binaries 3→1 (npm claude/claude.cmd shims removed; benign, removes a PATH-shadow) and routing assistant_events 2→1 / 3→2 (stream granularity only). Plus F6 (2.1.281 --help flag-presence record: all MRL-path flags present incl. --restricted/dontAsk/--json-schema; legacy --max-turns and --permission-prompt-tool no longer own help lines but still accepted live, proven by the routing capture) and F7 (fixtures sit inside the manifest root but match none of its covered patterns — recert §1 line 17, §3 line 45).

Your specific question — the source_binding.json re-pin to a3f24ff3: DESCRIBED CORRECTLY. §5.0 says "today it pins a5886dab / 65036d3f… / 850841ab…"; I verified HEAD's tools/controller_update/source_binding.json pins exactly commit_sha a5886dab, commit_tree_sha 65036d3f51cd46dc47e1c359a8dacb486b03eaf1, subtree_tree_sha 850841ab…. The report frames the re-pin to a3f24ff3 as an orchestrator reviewed-commit step BEFORE §5.2, and keeps it DISTINCT from the §5.11 journal --repin-cli-identity (two different repins — no conflation). It is not falsely claimed done: HEAD still pins a5886dab and a3f24ff3 is not an ancestor of HEAD, consistent with "not yet re-pinned". Its checks are true: a3f24ff3 exists on origin/task/M0-T159-cli-2-1-281-admission and all 12 required_modules exist at it (git-verified).

Part 3 (danger check, advisories, verdict) next.

---

M0-T159 G3 corrections — PART 3/3.

DANGER CHECK (§5 typed as written): SAFE. The only destructive commands are (a) `git worktree remove --force wt-controller-src` in §5.3 — run only after the installer's own source_worktree_exists refusal, and the very next install re-creates it at a3f24ff3 (ps1:649); and (b) `robocopy /MIR` into ...2/...3 in §5.6 — run only after §5.1 (all lanes stopped, no lock) and §5.5 (source installed+verified), from the verified tree, with a rollback note. Every risky transition is fail-closed with an explicit STOP; the CLI repin is genuinely last; the first launch is a supervised one-cycle canary with an audit watch-list and a stop+blocker rule (§5.12). Unsubstituted <LANE_WORKTREE>/<LANE_PACKET_ID> fail closed at draft. Nothing here can harm the live system if typed in order.

ADVISORY (none blocking):
- A1 recert:122 cites update_controller_from_candidate.ps1:620-643 for "backup_evidence_missing / backup_stale". backup_stale is correctly at :640; backup_evidence_missing's literal is at :468, reached from the install block via Read-BackupEvidence at :624. Line-cite imprecision only; owner sees a typed REFUSED code regardless.
- A2 recert §5.11/§5.12 cite recovery_probes.py:358-384 for the repin; cli_identity_repinned is at :388 (just past the range). provider_cli_drift at :367 is in-range. Substance correct.
- A3 The source_binding re-pin is a §5.0 bullet ("Re-pin BEFORE step 5.2"), not a numbered step. It sits before §5.1 so order is clear, but numbering it (e.g. §5.0.1) would stop a top-to-bottom typist skipping it.
- A4 The §5.11 lane-1 block lists `clear-recovery` unconditionally; prose (recert:333) conditions it on PAUSED_RECOVERY. Harmless (clear-recovery refuses outside that state), but a `# only if PAUSED_RECOVERY` comment in the block would remove ambiguity.
- A5 (already flagged by the producer as an orchestrator discovery item) MRL_LAUNCH_RUNBOOK:71-75/90 conflates claude_version_mismatch with the repin; the report handles it correctly (does both draft+repin) and logs it — good.

PRESERVATION: cdd62c5c is documentation-only (git-confirmed: 2 report files), tools/ byte-identical at a3f24ff3; the byte-untouched lane-journal claim rests on producer attestation plus the reports-only correction, which is consistent.

All five required corrections F1-F5 (with F4/F5 folded, plus F6/F7) are closed and every fact they rely on is verified TRUE. The runbook is complete, correctly ordered (repin LAST), and safe to hand the owner as typed commands. Advisories are cosmetic/citation-level and do not affect owner actions.

M0-T159 G3 VERDICT (corrections): PASS

END-OF-REPORT
