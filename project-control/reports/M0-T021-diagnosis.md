# M0-T021 — diagnosis: lock-verifier reproducibility defect (orchestrator-captured evidence)

Captured by the orchestrator for reviewer verification (evidence-capture division of labor, ADR-005 /
owner directive 2026-07-15). Root cause confirmed from clean main `f5ab631`.

## 1. Observed failure (reproduction on the effective-main verifier)
CI job **`api-tooling-lock-verify`** on PR #79 (head `c97e086`, whose `services/api/scripts/**` is
byte-identical to main `f5ab631`) failed at the step `bash scripts/lock_tools.sh --check`:

```
--- services/api/requirements-tools.lock   2026-07-22 04:01:58 +0000
+++ /tmp/tmp.QUpuZfpigc                       2026-07-22 04:02:06 +0000
@@ -10,9 +10,9 @@
-certifi==2026.6.17 \
-    --hash=sha256:024c88eeec92ca068db80f02b8b07c9cef7b9fe261d1d535abfd5abd6f6af432 \
-    --hash=sha256:2227dcbaafe0d2f59279d1762ddddc37783ed4354594f194ffc31d20f41fc3db
+certifi==2026.7.22 \
+    --hash=sha256:62f22742b58a1a33014a2b6b706588a8d7e2a88ae7bd1a6ebe8c992928483775 \
+    --hash=sha256:741e2c3b351ddf169a738da9f2c048608ff7f2c5cc02f1ebc6b118bb090d5d55
      # via
      #   httpcore / httpx
ERROR: requirements-tools.lock is NOT byte-identical to a fresh lock.
##[error]Process completed with exit code 1.
```
`certifi 2026.7.22` was published upstream 2026-07-22 (PyPI). The committed lock still fully satisfies
`requirements-tools.in`; nothing in the repo changed. `api-lock-verify` (production `requirements.txt`)
passed **only** because no production transitive dep released today — it carries the identical latent
defect (see §3).

## 2. Exact verification command (services/api/scripts/lock_tools.sh, --check mode, f5ab631)
```bash
COMPILE=(uv pip compile --universal --python-version 3.12 --generate-hashes --no-header "${IN_FILE}")
TMP="$(mktemp)"                                   # <-- BLANK temp file
"${COMPILE[@]}" --output-file "${TMP}" >/dev/null  # compile into the blank file
diff -u "${OUT_FILE}" "${TMP}"                       # committed lock vs fresh resolve
```

## 3. Root cause (confirmed)
`uv pip compile`, like pip-tools, reads an **existing** `--output-file` and uses its pinned versions as
resolution **preferences** (it will not upgrade them unless `--upgrade` is passed). The verifier defeats
that by pointing `--output-file` at a **freshly `mktemp`'d empty file**: with no existing pins to prefer,
uv resolves every package to the **latest** version available at CI time. So `--check` is really asking
"is anything newer available upstream?", not "does the committed lock reproduce from its inputs?". Any
upstream release of any (even transitive) package flips the check red on **every** unrelated PR — a
repo-wide deadlock. The identical pattern exists in the production mirror
`services/api/scripts/lock_requirements.sh` (`mktemp` → compile-into-blank → diff), so production-lock CI
will break the same way the moment any runtime transitive dep releases.

## 4. Intended fix (for the producer)
Seed the temp output with the committed lock before the identical **non-`--upgrade`** compile, so uv uses
the committed pins as existing-output preferences and the check verifies *reproducibility*:
```bash
TMP="$(mktemp)"
cp "${OUT_FILE}" "${TMP}"     # seed with the committed lock (existing-output preferences)
"${COMPILE[@]}" --output-file "${TMP}" >/dev/null
diff -u "${OUT_FILE}" "${TMP}"
```
This keeps: genuine manifest↔lock drift still fails (recompile changes the seeded file); tampered/missing
hashes still fail (recompile regenerates correct hashes ≠ committed); no `--upgrade`, no re-lock, no
silent updates. `dependency_age_gate.py` and both lock files are untouched. NOTE: the producer must
confirm uv's existing-output-preference behavior empirically in CI (thin-client policy: uv is not run
locally) and, if uv needs an explicit flag to honor preferences, use the minimal non-upgrade mechanism —
never `--upgrade`.
