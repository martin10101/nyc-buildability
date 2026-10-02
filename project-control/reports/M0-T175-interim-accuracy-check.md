# M0-T175 — interim accuracy check of the checklist increment (control-plane-verifier, read-only)

Saved verbatim by the orchestrator (session 08a1e891, claude-opus-5-5) from the reviewer's return. Interim
check of the checklist only, at 0f3a0228; it is not a gate record. Acceptance scenario 2 (the owner's steps
and the lane-1 canary evidence) was not judged. The four citation nits and the two plain-words notes were
applied by the producer in 62cf8cae (rework 2); a delta attestation for that commit follows in the gate
reports.

---

VERDICT: PASS for the M0-T175 checklist increment. Blocking findings: 0.
Head reviewed: 0f3a02280049cf3d9a90a4eeac4755b4c785de43 (worktree clean).

CHECK 1 — commands/flags/keys/paths/defaults (CONFIRMED, all exact). Verified via --help and source at 0f3a0228:
- doctor/verify-controller/start flags all real: start has --mode {shadow,supervised,limited-auto} (cli.py:3289), --config (:3309), --model-selection (:3310), --max-tasks default 1 (:3329), --approve-prompt-digest (:3335); no --lane flag exists (correct). doctor --config/--model-selection default None (cli.py:3249-3251). verify-controller --manifest REQUIRED + --config.
- config default /etc/nyc-supervisor/config.toml (platform_paths.py:41 POSIX_CONFIG_DIR, :67-77 default_config_path; config.py:375-383); manifest default + filename controller_manifest.json (platform_paths.py:80-106, manifest.py:38).
- PROTECTED verdict = root-uid0 + not group/world-writable + protected parent + no symlink, fail-closed (posix_acl.py:77-180: symlink :110, uid :118, mode :126, combine :159; os_acl.py dispatch :493-495). doctor prints "controller-config OS-ACL posture" (cli.py:1456-1459, built :510-533, emitted :1435). "controller verified, including the external config.toml binding." is the real string (cli.py:1733).
- template lines exact: User:18, WorkingDirectory:19, DISABLE_AUTOUPDATER=1 :22, NYC_SUP_CLAUDE_BIN:26, NYC_SUP_GATE_CMD:27, NYC_SUP_START_CMD:28, ExecStart→launch.sh :29, Restart=no :30, no [Install]. launch.sh exits 3/4/5 at :62-64/:67-72/:78-82, gated hand-off :84-88.
- codex-cli 0.157.0 (package-lock.json:16; fixture :62), claude 2.1.287 (fixture :44), --ignore-user-config (codex_reviewer.py:135, reason :17). 70% ceiling MEMORY_PAUSE_FRACTION=0.70 (resource_sampling.py:160, :232, :297; config note :112-118). Caps global=2/per-lane=1 (config.example.toml:137/138; run_budget.py:793). All config keys [codex]/[claude]/[approved_models] at cited lines. No invented or misspelled item.

CHECK 2 — step-5 orchestrator tomllib check (CONFIRMED). Ran the checklist's exact ok-logic (docs/D091_LINUX_COMMISSIONING.md:205-215) against 5 in-memory TOML strings (source swapped file→string only): PASS only for different+both-allowlisted; STOP for equal models, missing reviewer_model key, combiner not on allowlist, and empty combiner. Section/key names match the code it emulates: [review_combiner].model (review_combiner.py:420 key, :434 field, :512-516 required-no-default), [claude].reviewer_model (claude_reviewer.py:370 section, :384), [claude].allowed_models (dual_review.py:251-256 conductor refusal). Identity-independence is by identity not model string (review_combiner.py:572).

CHECK 3 — safety (CONFIRMED). Top note (lines 5-9) + every step header (13/69/91/124) mark root config, codex login, systemd install and start as owner-typed; all orchestrator checks labeled read-only (34/78/108/199) and use only doctor(no --live)/verify-controller/codex --version/systemd-analyze verify/grep/python3 tomllib — no commissioning command assigned to the orchestrator. Combiner stays off until the owner names the model (step 5, 161-191). Failure rule stop/keep-evidence/no-retry present (lines 9 and 230-234). The concrete NYC_SUP_START_CMD is orchestrator-PREPARED but owner-TYPED (145-148) — consistent with authority model.

CHECK 4 — plain words (non-blocking). Numbered steps are plain (command then check). Two dense passages for a non-technical reader: the "Linux paths for these checks" bullets (lines 54-67) and the certification/jargon note (lines 223-225, "void the certification"). Neither blocks; suggest trimming parentheticals if simplified later.

CHECK 5 — scope (CONFIRMED). git diff --stat 86364030..0f3a0228 = the two allowed_paths files + state.json + tasks/M0-T175.json. Producer commits 33e26662 and b055cf20 touched ONLY docs/D091_LINUX_COMMISSIONING.md + reports/M0-T175-producer-report.md; the ledger files changed solely in the orchestrator progress commit 0f3a0228. Producer never touched project-control/** — matches the expected diffstat exactly.

NON-BLOCKING citation nits (accuracy of the fact holds; only the pointer is slightly off):
1. docs/D091_LINUX_COMMISSIONING.md:62-63 cites cli.py:480-489 for "verify-controller without --manifest verifies nothing and fails closed." That range is _check_manifest, the doctor INFORMATIONAL helper (returns ok=True with a "NOTHING was verified" note). The verify-controller command's actual fail-closed path (ok=False, HALT, return 1, reason_code missing_manifest) is cli.py:1696-1710; corroborated by --help (cli.py:3473) and runbook section 6. Fact is true; fix: cite cli.py:1696-1710 for the "fails closed" half.
2. docs/D091_LINUX_COMMISSIONING.md:159 "atomic reservation review_slots.py:28-30" points to module-docstring prose about fail-closed reservation, not the reservation code. Concept is real in that module; optionally cite the reservation function body.
3. project-control/reports/M0-T175-producer-report.md:49 labels manifest.py:54 as CONFIG_LOGICAL_NAME, but line 54 is the "config.toml" entry in COVERED_PATTERNS (CONFIG_LOGICAL_NAME is line 47). Both validly reference the config.toml binding; the checklist itself (line 52) cites 47,54 without the mislabel. Report-only labeling nit.
4. docs/D091_LINUX_COMMISSIONING.md:59 cites platform_paths.py:80-97 for default_activation_dir; the POSIX return is line 98 (function spans 80-98). Trivial boundary; function clearly starts at 80.

Per the task instruction, acceptance scenario 2 (post-owner-steps canary evidence) was NOT judged — owner steps and lane-1 canary evidence are still pending, as the producer report also states.

Files reviewed (absolute):
/root/project/rv-T175/docs/D091_LINUX_COMMISSIONING.md
/root/project/rv-T175/project-control/reports/M0-T175-producer-report.md
/root/project/rv-T175/project-control/tasks/M0-T175.json

END-OF-REPORT
