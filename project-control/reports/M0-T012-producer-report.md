# M0-T012 Producer Report — CI hygiene: pin all GitHub Actions to reviewed immutable commit SHAs

- **Task:** M0-T012
- **Producer:** backend-engineer
- **Date:** 2026-07-17
- **Worktree:** `.claude/worktrees/M0-T012` (branch `task/M0-T012-sha-pinning`, based on main @ 2678509)
- **Status requested:** `awaiting_gate`
- **Files changed:** `.github/workflows/ci.yml`, `.github/workflows/generate-lockfile.yml` (plus this report)
- **secret-scan.yml:** NOT touched (read-only reference, per packet).

## 1. Scope discrepancy disclosure (packet inventory vs. repository reality)

The task packet inventories **9** tag-pinned refs in `ci.yml` (`checkout@v4 x4`). The actual file on the task branch contains **10** (`checkout@v4 x5` — the M2-T001 `web-e2e` job contributed a fifth `actions/checkout@v4` at line 58 that the packet inventory missed). `generate-lockfile.yml` has 2 as stated. **Total pinned: 12 refs, not 11.** S1 requires zero remaining `@vN` tag refs in the two files, so all 12 were pinned. No other deviation from the packet.

Pre-edit inventory (command + output):

```
$ grep -n "uses:.*@v" .github/workflows/ci.yml .github/workflows/generate-lockfile.yml
ci.yml:29:      - uses: actions/checkout@v4
ci.yml:30:      - uses: actions/setup-node@v4
ci.yml:58:      - uses: actions/checkout@v4
ci.yml:59:      - uses: actions/setup-node@v4
ci.yml:64:      - uses: actions/setup-python@v5
ci.yml:90:        uses: actions/upload-artifact@v4
ci.yml:106:     - uses: actions/checkout@v4
ci.yml:107:     - uses: actions/setup-python@v5
ci.yml:125:     - uses: actions/checkout@v4
ci.yml:139:     - uses: actions/checkout@v4
generate-lockfile.yml:19:      - uses: actions/checkout@v4
generate-lockfile.yml:20:      - uses: actions/setup-node@v4
```

(10 in ci.yml + 2 in generate-lockfile.yml = 12.)

## 2. Tag → SHA resolution (live, 2026-07-17; never from model memory)

### 2.1 Latest release in the SAME major line (S3 — no major bumps)

Commands (per action, `--paginate` over all releases, filtered to the in-use major line):

```
$ gh api "repos/actions/checkout/releases?per_page=100" --paginate --jq '.[].tag_name' | grep '^v4' | sort -rV | head -1
v4.3.1
$ gh api "repos/actions/setup-node/releases?per_page=100" --paginate --jq '.[].tag_name' | grep '^v4' | sort -rV | head -1
v4.4.0
$ gh api "repos/actions/setup-python/releases?per_page=100" --paginate --jq '.[].tag_name' | grep '^v5' | sort -rV | head -1
v5.6.0
$ gh api "repos/actions/upload-artifact/releases?per_page=100" --paginate --jq '.[].tag_name' | grep '^v4' | sort -rV | head -1
v4.6.2
```

The unsorted (creation-date-ordered) listing produced the same four leaders (`v4.3.1`, `v4.4.0`, `v5.6.0`, `v4.6.2`), so creation order and semver order agree.

### 2.2 Tag ref → commit SHA (S2 — annotated-tag dereference handling)

All four tag refs resolved with `object.type == "commit"` (lightweight tags), so **no annotated-tag dereference step was required**; the returned `object.sha` IS the commit SHA in each case. Verbatim outputs:

```
$ gh api repos/actions/checkout/git/ref/tags/v4.3.1
{"ref":"refs/tags/v4.3.1","node_id":"MDM6UmVmMTk3ODE0NjI5OnJlZnMvdGFncy92NC4zLjE=","url":"https://api.github.com/repos/actions/checkout/git/refs/tags/v4.3.1","object":{"sha":"34e114876b0b11c390a56381ad16ebd13914f8d5","type":"commit","url":"https://api.github.com/repos/actions/checkout/git/commits/34e114876b0b11c390a56381ad16ebd13914f8d5"}}

$ gh api repos/actions/setup-node/git/ref/tags/v4.4.0
{"ref":"refs/tags/v4.4.0","node_id":"MDM6UmVmMTg5NDc2OTA0OnJlZnMvdGFncy92NC40LjA=","url":"https://api.github.com/repos/actions/setup-node/git/refs/tags/v4.4.0","object":{"sha":"49933ea5288caeca8642d1e84afbd3f7d6820020","type":"commit","url":"https://api.github.com/repos/actions/setup-node/git/commits/49933ea5288caeca8642d1e84afbd3f7d6820020"}}

$ gh api repos/actions/setup-python/git/ref/tags/v5.6.0
{"ref":"refs/tags/v5.6.0","node_id":"MDM6UmVmMTkyNjI1NTI1OnJlZnMvdGFncy92NS42LjA=","url":"https://api.github.com/repos/actions/setup-python/git/refs/tags/v5.6.0","object":{"sha":"a26af69be951a213d495a4c3e4e4022e16d87065","type":"commit","url":"https://api.github.com/repos/actions/setup-python/git/commits/a26af69be951a213d495a4c3e4e4022e16d87065"}}

$ gh api repos/actions/upload-artifact/git/ref/tags/v4.6.2
{"ref":"refs/tags/v4.6.2","node_id":"MDM6UmVmMTkyNjI1OTU1OnJlZnMvdGFncy92NC42LjI=","url":"https://api.github.com/repos/actions/upload-artifact/git/refs/tags/v4.6.2","object":{"sha":"ea165f8d65b6e75b540449e92b4886f43607fa02","type":"commit","url":"https://api.github.com/repos/actions/upload-artifact/git/commits/ea165f8d65b6e75b540449e92b4886f43607fa02"}}
```

### 2.3 Second-source cross-check via `git ls-remote` (independent transport)

```
$ git ls-remote https://github.com/actions/checkout refs/tags/v4.3.1
34e114876b0b11c390a56381ad16ebd13914f8d5    refs/tags/v4.3.1
$ git ls-remote https://github.com/actions/setup-node refs/tags/v4.4.0
49933ea5288caeca8642d1e84afbd3f7d6820020    refs/tags/v4.4.0
$ git ls-remote https://github.com/actions/setup-python refs/tags/v5.6.0
a26af69be951a213d495a4c3e4e4022e16d87065    refs/tags/v5.6.0
$ git ls-remote https://github.com/actions/upload-artifact refs/tags/v4.6.2
ea165f8d65b6e75b540449e92b4886f43607fa02    refs/tags/v4.6.2
```

All four match the API resolution exactly. (Same verification transport the orchestrator used for the secret-scan.yml pin on 2026-07-15.)

### 2.4 Method validation against the existing secret-scan.yml pin

secret-scan.yml pins `actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2`. The version does NOT match my pin (v4.3.1 is now the latest v4.x), so a direct SHA comparison is not applicable; instead I validated the resolution METHOD by resolving v4.2.2 the same way:

```
$ gh api repos/actions/checkout/git/ref/tags/v4.2.2 --jq '.object'
{"sha":"11bd71901bbe5b1630ceea73d27597364c9af683","type":"commit","url":"https://api.github.com/repos/actions/checkout/git/commits/11bd71901bbe5b1630ceea73d27597364c9af683"}
```

Result equals the orchestrator-verified pin in secret-scan.yml byte-for-byte — the resolution method reproduces a known-good pin.

### 2.5 Final mapping table

| Action | In-use tag | Latest release, same major | Commit SHA | Refs pinned |
|---|---|---|---|---|
| actions/checkout | v4 | v4.3.1 | `34e114876b0b11c390a56381ad16ebd13914f8d5` | 6 (ci.yml x5, generate-lockfile.yml x1) |
| actions/setup-node | v4 | v4.4.0 | `49933ea5288caeca8642d1e84afbd3f7d6820020` | 3 (ci.yml x2, generate-lockfile.yml x1) |
| actions/setup-python | v5 | v5.6.0 | `a26af69be951a213d495a4c3e4e4022e16d87065` | 2 (ci.yml x2) |
| actions/upload-artifact | v4 | v4.6.2 | `ea165f8d65b6e75b540449e92b4886f43607fa02` | 1 (ci.yml x1) |

## 3. Self-check evidence (G2)

### 3.1 S4 — diff shows ONLY `uses:` line substitutions

`git -C <worktree> diff` output: every hunk in both files is a one-line `-`/`+` pair on a `uses:` line; no other line, whitespace, comment, or structural change anywhere. Full diff (12 substitutions):

- ci.yml @26: checkout, setup-node (web job)
- ci.yml @55: checkout, setup-node, setup-python (web-e2e job)
- ci.yml @87: upload-artifact (web-e2e job)
- ci.yml @103: checkout, setup-python (api job)
- ci.yml @122: checkout (contracts job)
- ci.yml @136: checkout (control-plane job)
- generate-lockfile.yml @16: checkout, setup-node (lockfile job)

Representative hunk (all hunks have this exact shape):

```diff
-      - uses: actions/checkout@v4
+      - uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
```

The complete verbatim diff is reproducible with `git -C .claude/worktrees/M0-T012 diff` and will be preserved in the branch commit; the G3 reviewer should re-run it from the worktree.

### 3.2 S1 — zero remaining `@vN` tag refs

```
$ grep -cE "uses:.*@v[0-9]" .github/workflows/ci.yml .github/workflows/generate-lockfile.yml
.github/workflows/ci.yml:0
.github/workflows/generate-lockfile.yml:0
```

(The pinned lines contain `@<40-hex-sha> # vX.Y.Z`; the pattern `uses:.*@v[0-9]` matches only tag refs, and there are zero.)

### 3.3 YAML parses; job structure intact

```
$ python -c "import yaml; d1=yaml.safe_load(open('.github/workflows/ci.yml')); d2=yaml.safe_load(open('.github/workflows/generate-lockfile.yml')); print('ci.yml jobs:', sorted(d1['jobs'])); print('generate-lockfile.yml jobs:', sorted(d2['jobs']))"
ci.yml jobs: ['api', 'contracts', 'control-plane', 'web', 'web-e2e']
generate-lockfile.yml jobs: ['lockfile']
```

### 3.4 S6 — identical action+version pairs use identical SHAs everywhere

```
$ grep -hoE "uses: actions/[a-z-]+@[0-9a-f]{40} # v[0-9.]+" ci.yml generate-lockfile.yml | sort | uniq -c
      6 uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4.3.1
      3 uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
      2 uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5.6.0
      1 uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2
```

Exactly 4 distinct pinned strings covering all 12 refs — no mixed pins of the same action.

## 4. Acceptance-scenario status

| Scenario | Status | Evidence |
|---|---|---|
| S1 zero `@vN` refs, all pins `<40-hex> # vX.Y.Z` | PASS (producer) | §3.2, §3.4 |
| S2 SHA proven equal to official tag target, dereference handled | PASS (producer) | §2.2 (all lightweight, `type:"commit"`), §2.3 ls-remote cross-check, §2.4 method validation |
| S3 same major line, no major bumps | PASS (producer) | §2.1 (v4→v4.3.1, v4→v4.4.0, v5→v5.6.0, v4→v4.6.2) |
| S4 diff only on `uses:` lines; YAML parses | PASS (producer) | §3.1, §3.3 |
| S5 full CI green on branch (all 6 jobs) | **PENDING — orchestrator-executed** after commit/push; producer cannot run branch CI (no git push per ADR-005) |
| S6 identical action+version → identical SHA | PASS (producer) | §3.4 |

## 5. Assumptions, limitations, risks

- **Assumption:** "latest release in the same major line" = highest-semver published release tag under that major on 2026-07-17 (`sort -rV` over the full `--paginate` release list). Pre-releases: none present in the filtered lists.
- **Disclosure:** packet ref count (11) is stale; actual is 12 (§1). No scope expansion beyond the two allowed files.
- **Limitation:** S5 (branch CI green, all 6 jobs including secret-scan) is deliberately not claimed — it runs only after the orchestrator commits and pushes the branch. A wrong SHA would brick CI; the four §2.3 ls-remote cross-checks are the pre-push mitigation.
- **Security/provenance impact:** positive only — closes the G5 M0-T005-R1 / M2-T001 F1 debt; workflows now immune to tag-rewrite supply-chain attacks; no secrets, permissions, or triggers touched.
- **Local disk:** KB-scale text edits only; no installs, no datasets; well within the low-storage budget.

## 6. Recommended next steps

1. Orchestrator: commit worktree changes, push `task/M0-T012-sha-pinning`, capture the S5 CI run URL + job results into this report's directory.
2. security-reviewer: G3 walkthrough — independently re-resolve the four tags (commands in §2) and re-run the §3 checks from the worktree.
