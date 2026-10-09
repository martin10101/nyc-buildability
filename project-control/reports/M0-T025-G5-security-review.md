# G5 Security/Privacy Review — M0-T025 (path containment for manifest requirements_file/verification_file, LOW-1)

**Task:** M0-T025 — add path-containment validation for the directive manifest's `requirements_file` / `verification_file` references (LOW-1 hardening).
**Reviewer:** security-reviewer (independent; read-only; not the producer).
**Reviewed identity:** candidate commit `20f7651c` (`task/M0-T025-path-containment`), merged at `56db6a17`. Blob identity verified: `tools/directive_registry.py` (`e1168304`), `tools/validate_directive_compliance.py` (`d649b6fe`), `tools/test_directive_compliance.py` (`940ad7dd`), and `project-control/reports/M0-T025-producer-report.md` (`805ddc84`) are **byte-identical** across `20f7651c`, `56db6a17`, current HEAD `75f060d8`, and the working tree — so working-tree review equals frozen-candidate review.
**Scope of diff:** exactly 4 files (3 tools + 1 producer report); no product/runtime code, no `.claude/**`, no registry sources. Confirmed via `git show --stat 20f7651c`.

## Assessment against the required checks

### 1. Traversal-defense completeness of `resolve_contained_ref` — PASS
The guard applies, in order: (a) type/emptiness (`not isinstance(ref, str) or not ref.strip()`), (b) `p.is_absolute() or p.drive or p.root`, (c) `".." in p.parts`, (d) final `_within(base_dir / p, base_dir)` which `resolve()`-normalizes and rejects anything not `relative_to` the resolved base.

I exercised every input class named in the task directly against the shipped function on this Windows host (`WindowsPath` flavor):

| Class | Example | Result |
|---|---|---|
| POSIX rooted | `/rooted/x.json`, `/x.json` | REJECTED (via `root`) |
| Windows drive-abs | `C:\foo\x.json`, `C:/foo/x.json` | REJECTED (via `is_absolute`/`drive`) |
| Drive-RELATIVE | `C:x.json` | REJECTED (via `drive`) |
| Bare-root | `\x.json` | REJECTED (via `root`) |
| UNC | `\\server\share\x.json`, `//server/share/x.json` | REJECTED (via `drive`/`is_absolute`) |
| `..` (lead/mid/tail) | `../x.json`, `a/../../x.json`, `a/..` | REJECTED (via `parts`) |
| non-string/empty/ws | `None`, `42`, `""`, `"   "` | REJECTED (via type/strip) |
| legit relative | `requirements.json`, `sub/requirements.json`, `a//b/x.json`, `.`, `.../x.json` | ACCEPTED and confirmed **inside** base_dir |

No input class resolved outside the directive directory yet passed. Cross-platform reasoning for the CI/Linux (`PosixPath`) flavor: the union `is_absolute() or drive or root` covers POSIX rootedness (`/...` → `is_absolute` True), and Windows-shaped values that POSIX does not recognize as separators degrade to inert single-component relative names that stay contained (they then fail closed as "missing"), never an escape; a relative path lacking both `..` and rootedness cannot textually climb above base_dir, and the only residual vector (symlink) is caught by the final `resolve()` containment check. The real 30-directive registry validating clean on this host (below) plus the captured CI run corroborate the POSIX flavor.

**Read-before-reject:** confirmed. The cheap textual rejections (type, absolute/drive/root, `..`) return before any filesystem access. Only the residual class reaches `_within`, which calls `resolve()` — a realpath/symlink stat, **not** a content open/read. Actual content reads (`_load_json` / `read_bytes`) occur only for a fully-contained, existing path. No rejected/escaping reference is ever opened or read. The producer's claim holds.

### 2. Fail-closed behavior, no warning downgrade — PASS
A rejected reference appends to `d.errors` and leaves the record unloaded. The consumption chain is uniformly hard-fail: `Directive.is_active` returns `False` when `self.errors` is non-empty (line 447); `evaluate_task_refs` emits `"…has integrity errors …; fail closed"` and `ok=False` (lines 685-689); `project_control.py` blocks at `claim`, `submit`, `accept`, and `new-task` on `not ev["ok"]` (lines 486-490, 502-505, 549-551, 814-817). The standalone validator routes containment failures into the same `errors` list and `main()` returns exit 1 for `--check`, default, and `--json` (lines 582-586, 581). There is no `warnings`-style channel these can be diverted to. Fail-closed cannot be downgraded.

### 3. Information exposure — PASS
Rejection messages interpolate only `{ref!r}` — the offending `requirements_file`/`verification_file` value, which is checked-in, orchestrator-authored registry data, never secrets or user/product data. Messages go to `d.errors`/stderr. The diff adds **no** new import, logging, network, subprocess, `open()`, or dependency (`git show … | grep` for added I/O lines → none; `subprocess` in `directive_registry.py` is pre-existing git tooling, untouched by this diff).

### 4. Regression risk to the compliance regime (DoS on acceptance) — PASS
The guard **accepts** nested relative refs (proven directly: `sub/requirements.json` accepted; unit `test_guard_accepts_plain_and_nested_relative_refs`) and the missing-key default `"requirements.json"`. I reproduced the counter-evidence: `python tools/validate_directive_compliance.py --check` → **exit 0** on the real 30-directive registry. No legitimate existing layout is rejected; the change is additive narrowing only. No lock-out of the registry.

### 5. LOW-1 trusted-input caveat preserved as defense-in-depth — PASS
`resolve_contained_ref`'s docstring states the references are "trusted, checked-in registry data, but they must still name a file within the directive's own directory," and `_within` is documented "defense-in-depth." The change is framed and implemented as hardening of trusted input, not as sanitization of attacker-controlled input, matching the LOW-1 required disposition (items 1-3) exactly.

## Findings

- **INFO / LOW (non-blocking):** the rejection message for drive-relative (`C:x.json`) and bare-root (`\x.json`) forms reads "absolute file reference … is rejected." These are technically drive-relative / rooted-but-not-absolute, so the wording is slightly imprecise. Cosmetic only — the rejection itself is correct and fail-closed; no security impact.
- **INFO:** a traversal `requirements_file` produces two error lines (loader-side + validator c2/c14-side). Producer-acknowledged, intentional (each consumer fails closed independently); harmless.
- **INFO:** the final `_within` uses `resolve()` then a later `.exists()`/read — a theoretical TOCTOU window. Out of scope by design: LOW-1 scopes these as trusted, checked-in, non-concurrent-adversary data; not a defect.

No HIGH, no MEDIUM, no BLOCKING findings.

## Commands run (read-only, this host: Python 3.11.9, Windows)
- `git rev-parse` blob-identity check across `20f7651c` / `56db6a17` / HEAD / worktree → all four files identical.
- `python tools/validate_directive_compliance.py --check` → **exit 0** (real 30-directive registry clean through the new guard).
- `python -m pytest tools/test_directive_compliance.py -k "PathContainment" -q` → **6 passed, 120 deselected in 421.29s, exit 0**.
- `python -m ruff check tools/directive_registry.py tools/validate_directive_compliance.py tools/test_directive_compliance.py` → **"All checks passed!", exit 0**.
- Direct adversarial probe of `resolve_contained_ref` over 20 input classes (table above) → every escaping/malformed class REJECTED, every legitimate class contained; **no escapes**.
- `git show 20f7651c` diff/scope + added-I/O grep → 4 files, no new import/network/subprocess/open/logging.

Note: I did not run the full ~27-minute suite (per instruction); the orchestrator-captured full-suite run at `20f7651c` (`M0-T025-orchestrator-evidence.md`) is the authoritative full-suite/G4 evidence and is not this G5 gate's responsibility.

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the security-reviewer agent-return channel (2026-09-07 gate wave; transport framing line removed, content unaltered). Reviewed identity 20f7651c; recorded at gate time by the orchestrator.*
