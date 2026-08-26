# M0-T103 directive-compliance verification — round 1 (VERBATIM save)

Reviewer: independent read-only `directive-compliance-verifier` (unnamed spawn), dispatched at
HEAD `702fe4a` (deliverable identity `e0a867b`, manifest `6092f93e…`); the repository advanced
mid-review through the G3-forced correction cycle to identity `a4cfdaa` (manifest `0b04e3b1…`),
so the verifier — correctly, fail-closed — returned **BLOCKED** rather than stamping a superseded
identity, independently reproduced the frozen-identity defect (G3 round-1 BLOCKING-1) from the
git object, and recommended re-dispatch at `a4cfdaa`. Round 2 at the corrected identity follows
in this file. Returned 2026-08-26 UTC; saved verbatim below (transport entity-decoding only).

---

I have everything needed to conclude. Let me make the frozen-identity defect airtight — confirmed: in the frozen blob at **e0a867b** (=702fe4a), line 166 `@pytest.mark.skipif(...)` decorates the `post()` fixture at lines 168-169 (pytest ignores marks on fixtures), leaving `test_live_reprobe_claude_version_matches_fixture` at line 173 **unguarded** — it fails on any claude-absent runner. This is exactly the G3 round-1 BLOCKING-1 (commit 6eb65b9), independently reproduced from the git object.

---

DCV: BLOCKED

(Full 29-row BLOCKED matrix as returned — every row BLOCKED "stale identity" except D-024-R185
recorded VIOLATED at the frozen identity with the reproduced skipif evidence; see the agent
transcript payload. Key rows preserved verbatim:)

- D-024-R185: state VIOLATED — evidence: "frozen blob e0a867b L166 skipif decorates post() fixture(L168); live test L173 UNGUARDED", "G3 round-1 (6eb65b9) FAIL reproduced claude-absent failure via stripped PATH", "fixed only at a4cfdaa" — note: "At the assigned frozen identity the project test suite is NOT green on a claude-absent runner (existing-suite-green clause fails); the frozen deliverable failed its own G3."
- All other 28 rows: state BLOCKED with substance-sound notes ("cannot certify at stale/superseded identity"; identity-independent evidence recorded as carrying).

FINDINGS

BLOCKING-1 (root cause of the BLOCKED verdict) — Assigned frozen identity is stale/superseded. I was dispatched to verify HEAD `702fe4a` / deliverable `e0a867b` / content_manifest `6092f93e…`. During the review the repository advanced: current HEAD is `30cd297` and `git rev-parse HEAD` at my first command returned 702fe4a, so the move happened mid-review. The reflog shows a full rework cycle after 702fe4a (6eb65b9 → 87a1c3c → **a4cfdaa** → d832c4c → e911fd3 → 7c7d2ee → 96d8623 → 30cd297). The current task report `project-control/reports/M0-T103.json` at HEAD now records `reviewed_sha=a4cfdaa49188e546173fd32b467dcf643bec5fc4` and `content_manifest_sha256=0b04e3b1…`, and the M0-T103 task is `awaiting_gate` at that corrected identity. A DCV stamped at the assigned identity is (a) non-acceptable — reviewed_sha e0a867b != live HEAD 30cd297 and material identity 6092f93e != current 0b04e3b1, so `accept()` would refuse it (in-regime accept requires reviewed_sha == accept-time HEAD and matching material identity); and (b) not honest — that identity failed its own G3. **The DCV must be re-dispatched against a4cfdaa (HEAD 30cd297, content_manifest 0b04e3b1).**

BLOCKING-2 (independent finding at the frozen identity, R185 VIOLATED) — I reproduced the G3 round-1 BLOCKING-1 directly from the frozen git object `e0a867b:tools/test_agent_supervisor_capability_probe.py`: line 166 `@pytest.mark.skipif(shutil.which("claude") is None, …)` sits above the `post()` fixture (lines 168-169), not above `test_live_reprobe_claude_version_matches_fixture` (line 173). pytest ignores marks on fixtures, so the live drift-tooth test is unguarded and fails on any claude-absent runner (the supervisor-bridge CI context). Therefore R185's "existing project suite remains green" clause is not satisfied at the assigned frozen identity. My own live pytest passed 18/18 only because this machine has claude present. This was corrected at a4cfdaa (skipif moved onto the test, mirroring the codex sibling).

ADVISORY (to accelerate the re-run at a4cfdaa) — the following are identity-independent or carry across the rework, and looked sound:
- Live machine corroborates the upgrade: `claude --version` = `2.1.246 (Claude Code)`; native binary sha256 `9f07f1ecaf26231fc2fac489e7c5214140d38fd14764938a2c8c46f31931d204`, size 250948768 — both exactly match the report and the post-update fixture. `claude doctor` = native 2.1.246, commit 1ba9d2211ae1, config method native, auto-update success->2.1.246 (2026-08-26), 1 warning (leftover npm shim) — matches report §3.
- Resolver cross-check (`directive_registry.evaluate_task_refs` on `project-control/tasks/M0-T103.json`): 29 applicable IDs, `ok=True`, `missing_ids=[]`, `invalid_refs=[]`, `unresolved=[]` — the applicable set is complete and correctly cited via `D-024:ALL`, and matches the verification-row's 29 IDs exactly.
- `python tools/validate_directive_compliance.py --check` -> EXIT=0.
- Rework delta e0a867b->a4cfdaa is minimal and on-point: the fixture `capability_probe_live_2026-08-26_m0t103_post_update.json` is **byte-unchanged** (so the binary-identity/masking evidence carries); the test file moved the skipif onto the test and generalized the masking tooth (account-agnostic path fragments + non-empty binaries + whole-fixture/probe_meta scan, addressing R183/ADVISORY-2); report §5 records the correction. Current working tree passes 18/18 with claude present, and the producer/G3 recorded 16 passed + 2 clean SKIPs with a stripped PATH (claude-absent).

Note on process: the three regime suites (`test_directive_compliance.py`, `test_project_control.py`, `test_directive_reminder.py`) were slow; `test_directive_compliance.py` alone exceeded 5 minutes, so I launched them in the background and did not block the verdict on them (they test the compliance machinery, not M0-T103; the validator `--check` already passed EXIT=0). They are not load-bearing for this BLOCKED disposition.

Recommendation to the orchestrator: do not record this DCV against 702fe4a. Re-dispatch the M0-T103 DCV at the current corrected identity **a4cfdaa** (HEAD 30cd297, content_manifest 0b04e3b1, report reviewed_sha a4cfdaa). At that identity the 29 requirements appear substantively satisfiable on the evidence I could inspect (fixture unchanged, guard fixed, masking generalized, live binary/doctor corroborated, resolver/validator clean), but they must be re-verified and stamped there so reviewed_sha == accept-time HEAD.


---

# M0-T103 DCV — round 2 at the corrected identity (VERBATIM save; same verifier, context intact)

Requested via SendMessage per the round-1 recommendation. Saved verbatim below; the fenced JSON is
the canonical payload merged into the D-024 `verification.json` M0-T103 row at accept time
(reviewed_sha restamped to accept-time HEAD per the verifier's own recommendation and D-004-R630).

---

All checks pass. Final integrity sweep confirms: the entire c6a495f..HEAD range touches only M0-T103 deliverables + its own control-plane records (no forbidden path, no other task file); **zero merges** in range (PR #241 untouched, no prohibited merge/accept/deploy); and both pre-update 2.1.220 fixtures are retained alongside the new post-update fixture (R181). I have reproduced primary evidence for all 29 requirements at the corrected identity a4cfdaa.

DCV: PASS

```json
{
  "reviewed_sha": "a4cfdaa49188e546173fd32b467dcf643bec5fc4",
  "content_manifest_sha256": "0b04e3b14e09f0395590714f53f98acd3bb3e622908c02086a64ae1532d489a0",
  "requirements": [
    {"id":"D-024-R140","state":"PASS","evidence":["producer=orchestrator/Fable; independent G3/G4/G5+DCV verify","diff c6a495f..HEAD: no activation/deploy/credential/protected write","npm-uninstall left to owner (report s2)"],"note":"Producer/reviewer roles and owner-final-authority boundary preserved."},
    {"id":"D-024-R145","state":"PASS","evidence":["report s1 pre-update capture + clean pushed tree (c6a495f==origin, porcelain empty)","s1 no-disruption determination","s2 official updater only"],"note":"Upgrade performed under exactly the authorized preconditions."},
    {"id":"D-024-R146","state":"PASS","evidence":["report s9: no bypass flags (canaries --strict-mcp-config only), no MCP/SDK/dep/PR","no forbidden path in diff; 0 merges in range","model resolved claude-fable-5 = existing approved policy"],"note":"No prohibited authorization exercised."},
    {"id":"D-024-R147","state":"PASS","evidence":["report s1 official stable 2.1.246 (M0-T102 changelog snapshot)","live claude update confirmed current release = 2.1.246"],"note":"Execution-time official baseline confirmed."},
    {"id":"D-024-R148","state":"PASS","evidence":["re-ran live: claude --version=2.1.246, native sha256 9f07f1ec..., size 250948768","fixture pins 2.1.220(pre)/2.1.246(post) as historical","live updater confirmed current release"],"note":"Live binary + current release re-probed at execution time, matching fixture."},
    {"id":"D-024-R149","state":"PASS","evidence":["post-update installed-version fixture (2.1.246, masked)","real canaries: probe + model + hook-chain (report s4)","guard fixed: reproduced 18 present / 16+2 absent"],"note":"Installed-version fixture + real canary present for the probed surface."},
    {"id":"D-024-R152","state":"PASS","evidence":["report s8: /goal live fixtures remain unit E","no /goal adoption in diff"],"note":"No premature adoption; honest deferral."},
    {"id":"D-024-R153","state":"PASS","evidence":["report s3/s6 daemon auto-restart onto 2.1.246 observed","no second process-management system activated (shadow-only)"],"note":"Native background observed, not prematurely adopted."},
    {"id":"D-024-R154","state":"PASS","evidence":["report s4 agents --json observed outside Fable context","no worker-facing token quotas in any deliverable/diff"],"note":"Passive-observation boundary honored."},
    {"id":"D-024-R155","state":"PASS","evidence":["report s4 canary3 PreToolUse hook-chain ran on 2.1.246 (G3/G4-verified; not re-run per -p prohibition)","readonly-guard PreToolUse chain independently live in my own session"],"note":"Hooks fire/guard proven; deeper hook matrix honestly deferred to unit D."},
    {"id":"D-024-R156","state":"PASS","evidence":["report s8 worktree canaries remain unit C","existing writer-lease isolation retained"],"note":"Native worktree eval deferred; logical isolation retained."},
    {"id":"D-024-R157","state":"PASS","evidence":["report s8: no workflow adoption; unchanged plan"],"note":"No dynamic-workflow adoption."},
    {"id":"D-024-R158","state":"PASS","evidence":["report s8 skills surface untouched (unit G)"],"note":"No skills/command adoption."},
    {"id":"D-024-R159","state":"PASS","evidence":["report s8 UserPromptExpansion fixtures remain unit G"],"note":"Honest pending; no collision with built-in /loop claimed."},
    {"id":"D-024-R160","state":"PASS","evidence":["report s3/s6 running processes keep binary; no resume misuse"],"note":"Session semantics observed; safe-seam turnover preserved."},
    {"id":"D-024-R161","state":"PASS","evidence":["independent G3/G4/G5+DCV at frozen identity a4cfdaa","no native review claimed as gate substitute"],"note":"Native reviews not substituted for independent acceptance."},
    {"id":"D-024-R162","state":"PASS","evidence":["report s8 accepted statusLine telemetry integration RETAINED; handler tests green","live 2.1.246 statusLine payload deferred to next fresh interactive session (M0-T091 pattern)"],"note":"Retention obligation met; live-payload is an honest bounded deferral with a concrete discharge path."},
    {"id":"D-024-R163","state":"PASS","evidence":["report s9 no messaging/Remote Control enabled","doctor lists Remote Control but task did not enable/require it"],"note":"Not adopted; loop correctness independent of it."},
    {"id":"D-024-R166","state":"PASS","evidence":["report s9 no top-level-loop mechanism adopted","diff adopts none of /loop,/batch,SDK,MCP,resume,autocompact as authority"],"note":"Campaign authority remains Codex/ledger/git/owner gates."},
    {"id":"D-024-R167","state":"PASS","evidence":["report s1-3 all 6 steps: 2.1.220 sha af5bf1f1 -> 2.1.246 sha 9f07f1ec","clean+pushed c6a495f==origin; disruption determination; s2 official updater only","post identity live-verified: doctor native 2.1.246 commit 1ba9d2211ae1"],"note":"Full pre/post procedure recorded; post-state independently live-verified."},
    {"id":"D-024-R168","state":"PASS","evidence":["disposable child canaries on new binary; Gate0/MCP-deny/hooks + accepted suites re-run","BLOCKING-1 harness regression RECORDED (report s5) + fixed; rollback claude install 2.1.220 documented","no runtime backend activated (shadow-only)"],"note":"Post-update checklist met; regression recorded not silenced; statusLine/skills live behaviors honestly deferred."},
    {"id":"D-024-R171","state":"PASS","evidence":["pre fixtures (2.1.220) + post fixture (2.1.246) both present + masked","dual-version pair test pins both; post-fixture no-leak verified independently"],"note":"Unit B installed+upgraded masked probes delivered."},
    {"id":"D-024-R180","state":"PASS","evidence":["test diff: drift tooth repointed to post fixture (single active target), not layered","pre-update fixtures retained for shape/history; rollback preserved for rollout (report s7)"],"note":"Replace-not-layer honored with one active backend + recorded rollback window."},
    {"id":"D-024-R181","state":"PASS","evidence":["3 fixtures present incl. both pre-update (0 deletions)","report s5: nothing deleted"],"note":"No accepted code deleted on a docs-equivalence claim."},
    {"id":"D-024-R182","state":"PASS","evidence":["deterministic probe fixtures + 3 bounded real canaries (report s4)","suite ~3s; no token-burn threshold test"],"note":"Testing method matches the mandate."},
    {"id":"D-024-R183","state":"PASS","evidence":["fixture leak-scan clean (no MLFLL/Users/secret); generalized masking tooth (whole-fixture, drive-rooted/Users) G4-killed 5 mutants","win32-x64 + exact 2.1.246 confirmed; strict MCP default-deny effective (canary2)"],"note":"Platform+installed-version+MCP+no-leak proofs delivered; bg/goal/UPE/subagent behaviors deferred to units C-G."},
    {"id":"D-024-R184","state":"PASS","evidence":["report s4/s6 no routine polling into Fable ctx; no token quotas","session integrity observed and honestly recorded"],"note":"Worker-protection slice met; full concurrency/rotation matrix owed to later units."},
    {"id":"D-024-R185","state":"PASS","evidence":["suite green on upgraded machine: reproduced 18 present / 16 passed +2 skips absent; producer 228 passed","independent G3/G4/G5+DCV at same frozen identity a4cfdaa (control-plane-only to HEAD)","G4 5 mutant kills on masking tooth; drift tooth fired RED on real upgrade then re-baselined"],"note":"Suite-green + same-identity independent review + mutation teeth satisfied; no GitHub external effect performed this task."},
    {"id":"D-024-R188","state":"PASS","evidence":["single cohesive writer task (unit B) after accepted M0-T102","verification rows + campaign record current; validator EXIT=0","no token ceilings in prompts"],"note":"Campaign execution rules honored."}
  ],
  "d030": null
}
```

FINDINGS

Verdict: DCV PASS — all 29 applicable requirements independently verified SATISFIED at the corrected identity a4cfdaa (content_manifest 0b04e3b1...). The round-1 BLOCKING-1/BLOCKING-2 conditions are fully discharged.

What was reproduced from primary evidence (not producer claims): identity control-plane-only to HEAD with material identity recomputed EXACTLY (0b04e3b1...); BLOCKING-1 fix confirmed in the deliverable with both contexts reproduced (18 present / 16+2 absent); R183 masking generalized + non-vacuous (independent leak scan clean, 5 [HOME] masks); live binary/doctor corroboration (2.1.246, sha 9f07f1ec..., commit 1ba9d2211ae1); resolver 29/29 ok; validator EXIT=0; prohibitions clean (no forbidden path, zero merges, PR #241 untouched, shadow-only); R181 all three fixtures retained.

ADVISORY (transparency, non-blocking): (1) the two claude -p canaries were not re-executed by the verifier (API-call prohibition) — corroborated by G3 round-2 and G4, and no row hinges solely on them; (2) the live 2.1.246 statusLine payload deferral is an honest bounded deferral with a concrete next-session discharge path (M0-T091 pattern) — PASS on affected rows; (3) no modularity concern (test-harness-only change).

Recommendation: record this DCV PASS; stamp the verification row at accept-time HEAD (control-plane-only interval, identical material identity, per D-004-R630).
