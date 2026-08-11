# Session Handoff — NYC Buildability (current-only)

**Authoritative state:** the `project-control/` ledger + git + CI. On resume, read it live —
`python tools/project_control.py status` and `python tools/current_state.py` — and reconcile against
the remote: **origin/main may have advanced, so do not trust any SHA here as still-current.** This
file is orientation only. Rules/gates/workflow routes live in `CLAUDE.md`. Old blocks via
`git log -p docs/SESSION_HANDOFF.md`. Keep CURRENT-ONLY: the `context-budget` CI check fails > ~4000 tok.

## SESSION 18 — steps 1-2 DONE (#219+#220 merged to main); M0-T056 + R595 go-live remain

Refreshed **2026-08-11 (session 18; `claude-opus-4-8`)**. **Accepted = 84.** #220 (session 15 control)
is **MERGED to main** (merge `0d42953`). Integration branch is now **`control/session16-codex-golive`**
off `origin/main` (worktree `.claude/worktrees/session15-acc`; open a PR when you push). Owner go-live
authorization = **D-011 amendment-004** (R030/R031/R032): build+accept M0-T056, then activate R595 + add
the accept allowlist — STRICTLY SEQUENCED after the now-DONE follow-ups + #220→main. The ledger wins.

### Done this session (all on main now)
- **M0-T062 ACCEPTED (83)** — follow-ups (a)+(b): drained inert `M0-T056` from `_EMPTY_IDENTITY_GRANDFATHERED`
  (it gained 7 tracked `tools/agent_supervisor` allowed_paths → resolves non-empty → c17 guards it live) +
  O1 `path_free_justification` fail-closed regression tests. Governance/orchestrator-produced; G0/G2/G3 +
  control-plane-verifier DCV (empty D-001 set). `validate --check` exit 0.
- **M0-T047 ACCEPTED (84)** — nanoid **3.3.17** remediation (GHSA-2v37-7h3g-55p8), D-009. Landed byte-identical
  to #219 onto #220; G0/G2/G3(code)/G5(security) + D-009/D-010 DCV. **Selective-citation fix:** the resolver
  REQUIRES citing the two M0-T047-scoped nanoid age-gate HOLDS **D-010-R233** (age-eligible on/after
  2026-08-10T10:39:22Z) + **D-010-R246** (don't bypass the age gate) — both classification `hold` (NOT
  deferrable) → verified PASS directly; D-009 applicable subset empty (empty row). Age genuinely satisfied
  (nanoid 3.3.17 uploaded 2026-08-03T10:39:22Z, 8.50d; NO waiver); fresh #220 web-dependency-security PASS.
- **PR #219 MERGED → main** (nanoid fix; merge `75cc81b`, remote branch deleted). **PR #220 MERGED → main**
  (merge `0d42953`; all 8 required checks green on head 98aeb64; merge-tree dry-run was clean).

### NEXT — runway (ordered; D-011 amendment-004). Steps 1-2 DONE.
3. **M0-T056** (R595 production actuation) — **AUTHORIZED**: build + full gate wave (G0/G2/G3/G5 + DCV) + accept.
   Packet is `ready`, in-regime D-010:ALL, allowed_paths = 7 `tools/agent_supervisor/*` + report. Adds a 2nd
   spawner (`turnover_adapters.py make_subprocess_command_runner`) + removes the human. Fold in the two carried
   G5 residuals below. **NOTE:** derive_applicable may flag OTHER applicable D-010 rows (like M0-T047 did) —
   run `evaluate_task_refs` first and cite whatever it requires (selective-citation guard fails closed).
4. **Activate R595 + add the accept allowlist** — **AUTHORIZED** — supervisor live end-to-end. ONLY after
   M0-T056 accepted. Verify `default_mode` flips off shadow + the live proof host satisfies the C1 Job-Object
   gate (P8: POSIX/Render hard-refuses `start` → the live proof likely runs on the owner's Windows host w/
   elevated config ACL; **STOP + hand the owner the exact command** at that step — genuine owner touchpoint).

### Carried M0-T056 pre-actuation residuals (2 non-blocking G5 advisories)
- **(M0-T059)** if M0-T056 adds a concurrent recorder settling the same pid, use an atomic read-modify-write in
  `clear_child_record`/`recorded_start_token_for` (two `get_state` reads today; benign single-threaded).
- **(M0-T060)** optionally also gate the achieved `job_object` branch on `ContainmentReport.verified_in_job`.

### Accept mechanics (proven session 17-18; reuse)
- **Reviewed content commit FIRST** (code+producer-report), stamp `--sha <R>` on gates; keep gate/DCV/accept
  evidence UNCOMMITTED until after `accept` (HEAD stays R; material identity = allowed_paths manifest, stable
  across control-plane commits). Fill DCV `reviewed_manifest_sha256` from the G3/G5 gate `content_manifest_sha256`.
- **Empty-set cited directive** still needs a `task_verifications` row (verifier=directive-compliance-verifier or
  control-plane-verifier ≠ producer). Non-empty applicable requirements each need a `{id,state:PASS,evidence,note}`.
- **Producers auto-isolate off origin/main** (now current). Reviewers run read-only IN `session15-acc` at HEAD;
  their shell cwd may be the PRIMARY checkout → give ABSOLUTE worktree paths + `git -C <worktree>`.
- CI `control-plane` runs `validate_directive_compliance.py --check` + `test_directive_compliance.py`;
  `supervisor-bridge` runs the FULL `pytest tools/test_agent_supervisor_*.py` (36 modules; freeze list is a subset).
  `project-control/**` LF; stage exact paths; commit+push after each accept. Reviewer/orchestrator `claude-opus-4-8` xhigh; producers UNNAMED.

### Still in force
deployment/G6/Graphify/expansion holds; `default_mode=shadow` until R595 flips; a failed gate / reproduced defect
/ unresolvable contradiction STOPS and returns to the owner. Codex model-fallback RESOLVED (non-sticky).
