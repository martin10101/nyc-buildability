---
name: ruff-e501-not-raw-length
description: In G4/G1 lint review, raw line-length > 100 is NOT the same as a ruff E501 failure; ruff exempts unbreakable-token overflow. Scan the whole tree for ground truth.
metadata:
  type: feedback
---

Never infer a ruff E501 failure from raw character length alone. Ruff 0.13.0 at
`line-length=100` (this repo's `services/api/pyproject.toml`, `select=["E","F","I","UP","B"]`)
does NOT flag every line > 100 chars. It exempts lines whose overflow past the limit is an
unbreakable token — i.e. no whitespace after the limit column (a URL/long string/`# type: ignore`
token that starts before col 100 and runs continuously past it). It also tolerates lines where the
code fits within the limit and only trailing whitespace-separated comment chunks (`# noqa`, `# type:
ignore`) overflow.

**Why:** In the M2-T022 first G4 wave (ec4b75dc) I FAILed on B1, asserting a 107-char test line
`detail={..., "url": "https://..."},` "is a multi-chunk line, so ruff's single-word/URL E501
exception does not apply" and would fail `ruff check`. That was WRONG. The delta re-adjudication
(HEAD e40c87c4) found `origin/main services/api/app/main.py:105` (104 chars, `... -> Response:
# type: ignore[no-untyped-def]`, token straddling cols 82→103, no whitespace after col 100) is
ACCEPTED, merged, and ruff-green under CI's `ruff check .` — structurally identical to the line I
flagged. Also `transport.py:171` (114) and `:453` (106) are ruff-green on main. My prior "E501 is
enforced repo-wide, every accepted file conforms" corroboration was based on a scan of only TWO
subdirectories (`app/api` + `tests/api`) and missed these accepted >100 lines elsewhere.

**How to apply:** (1) A raw-length finding is a legitimate style/cleanup note, but do NOT claim it
fails `ruff check`, fails a documented ruff command, or contradicts a producer's "ruff clean"
self-check unless you can ground it. (2) To ground ruff's real behavior without executing ruff
(ADR-005 no-exec discipline): scan the WHOLE `services/api` tree at `origin/main` for lines > 100;
any that exist in CI-green accepted code are living proof of what ruff tolerates — compare the
disputed line's structure (does a single non-ws token straddle the limit with no whitespace after
it?) against them. (3) CI's ruff is `working-directory: services/api` + `ruff check .` (recursive),
pinned via `requirements-tools.lock` (verify the version there matches any captured evidence).
See also [[probe-separator-deleting-normalizations]] for the no-exec probe discipline.
