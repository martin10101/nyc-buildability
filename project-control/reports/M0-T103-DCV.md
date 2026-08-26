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
