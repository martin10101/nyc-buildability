---
name: crlf-lf-digest-review-method
description: How to independently QA a line-ending (CRLF/LF) digest-normalization task at a frozen SHA without editing production or trusting the producer's helper
metadata:
  type: feedback
---

Reviewing a CRLF/LF digest-normalization task (e.g. M0-T156 directive-registry) as read-only G4 QA.

**Rule:** prove the fix and its red/green independently of the producer's own hash helper.

**Why:** if the AS-1 red/green test computes its "expected" value by calling the same production
`sha256_text_artifact` it is testing, a mutation (e.g. over-forgiving normalization that strips
spaces) is self-consistent and the test still passes. M0-T156's AS-1 test was adequate precisely
because it used an INDEPENDENT oracle: `hashlib.sha256(b"line one\nline two\n")` literal LF bytes,
not the helper. Verify the oracle is independent.

**How to apply (worktree-isolated, no git writes, no shared-checkout cd):**
1. Commits are reachable across worktrees (shared object store) — `git cat-file -t <sha>`, `git show`,
   `git diff`, `git log`, `git archive` all work from your own worktree even for another branch's SHA.
   The bash guard refuses `cd <shared-checkout> && git ...` and rejects multi-line `${PIPESTATUS}`
   scripts as "too complex" — run plain single commands from your own worktree dir.
2. AS-3 (recompute digests): pull each artifact via `git show <sha>:<path>` capturing BYTES
   (subprocess, not text), normalize `b.replace(b"\r\n",b"\n").replace(b"\r",b"\n")`, sha256, compare
   to the recorded manifest value AND the CI-reported prefix. Also assert CRLF->norm == LF-norm
   (line-ending independence). Note: git blobs are already LF (`.gitattributes eol=lf`), so raw==norm
   for the stored blob — synthesize a CRLF copy to exercise the CRLF path.
3. AS-2/AS-6 both representations on the REAL registry: `git archive <sha> tools project-control .claude
   CLAUDE.md` -> extract with Python `tarfile` (tar's `-C C:/...` fails: colon = remote host). Run
   `validate --check` on the LF tree (== CI side) AND on a second copy where you convert every
   directive `.md`/`.json` to CRLF. Both must EXIT 0.
4. Red-half without editing production: monkeypatch `directive_registry.normalize_text_artifact_bytes
   = lambda b: b` then call `validate()` on the CRLF tree — expect a flood of c2/c14 mismatches
   (M0-T156: 316). CRITICAL: the validator does `sys.path.insert(0, tools/)` + `import directive_registry`
   (top-level name), so patch that module, NOT `tools.directive_registry` (different object; patch silently
   no-ops and you get 0 errors — a false green).
5. AS-6 guard/reminder suites (`test_directive_reminder/readonly_agent_guard/agent_dispatch_guard`) need
   `.claude/settings.json` + `.claude/hooks/**` — archive `.claude` too or they fail with FileNotFound
   (harness artifact, not a defect). They don't touch normalization code, so CI green + a clean diff
   covers them regardless.
6. Full `test_directive_compliance.py` single-pass can take 30-60+ min locally (registry copytree per
   Fixture test under AV/disk pressure) — run TARGETED classes; from an extracted scratch tree it's fast
   (LineEndingNormalizationTest ran 7.8s for me vs the producer's 239.9s). A local split-run
   (A-L + M-V) is acceptable when tests use isolated tempdir fixtures (no shared state) and CI runs
   single-pass green.

**Security meaning of the normalization (AS-5):** `\r\n`/`\r`/`\n` all collapse to `\n`, so ONLY the
line-ending REPRESENTATION is forgiven; a lone CR inserted mid-line becomes a real `\n` (changes
content -> still caught), and CR/LF choice carries no semantic channel in JSON/Markdown. Sound.
