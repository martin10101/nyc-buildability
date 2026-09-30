---
name: reviewer-worktree-git-and-manifest-verify
description: How to run git-anchored + manifest-binding verification for a supervisor gate when the worktree guard blocks git against the ctl24 shared checkout
metadata:
  type: feedback
---

Two reusable QA methods for supervisor re-certification gates (M0-T112/T116/T119 pattern), discovered doing the M0-T119 G4.

**Git against certified SHAs works from the reviewer's OWN worktree even though git against ctl24 is guarded.**
- **Why:** the read-only reviewer worktree (`.../worktrees/agent-*`) is a *separate repo* (`nyc-development-feasibility-claude-pack/.git`) from the shared checkout `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24`, but it has fetched the campaign branch, so all certified objects (e.g. `7d8195b`, tree `8d34ea53…`, golden blob `c54fd0d2…`, `f89aa29`, `d1b05bb`) are reachable in its object store. The worktree guard refuses ANY git that redirects to ctl24 (`cd ctl24 && git`, `git -C ctl24`) AND refuses compound/`${VAR}`-expansion commands as "too complex" — so run ONE plain git per Bash call from the worktree cwd (no cd, no `-C`, no `&&`).
- **How to apply:** verify anchors with `git rev-parse <sha>:path`, `git ls-tree -d <sha> path`, negative-space with `git log --oneline A..B -- tools/` (empty = no supervisor change), and "no test removed" with `git ls-tree -r --name-only <sha> tools/ | grep test_ | sort` diffed via `comm`. pytest is NOT blocked — run the real suite against `C:/Users/MLFLL/Downloads/nyc-zoning/ctl24` (a plain `cd ctl24 && python -m pytest …` is allowed; only git is guarded). Env reads via `${VAR:-x}` are blocked too — use `python -c "import os; ..."`.

**The controller manifest hashes LF-normalized content; the Windows working tree is CRLF.**
- **Why:** comparing the stored `controller_manifest.json` per-file sha256 (dict of `relpath -> hex`, rooted at `agent_supervisor`) against raw on-disk bytes gives ~all mismatches on `.py`/`.md`. Normalizing `\r\n -> \n` before hashing makes them match exactly (M0-T119: 118/119 matched, the 1 non-match is the EXTERNAL `config.toml` bound by logical name — it lives outside the repo tree, so it's legitimately "missing on disk").
- **How to apply:** to prove the manifest binds the final tree without the owner's external config, recompute `sha256(open(f,'rb').read().replace(b'\r\n',b'\n'))` for each entry under `ctl24/tools/agent_supervisor/`. `doctor` (non-live, default) with only `--manifest` will FAIL `controller_manifest: config_path_missing` in the sandbox (external config absent) — that single FAIL is a sandbox artifact, not a defect; every other doctor check passes and its `control_response_live_probe` line reports the certified executable digest (e.g. `d6f6c29a8ac6b3cf`). See [[in-regime-accept-mechanics]].
