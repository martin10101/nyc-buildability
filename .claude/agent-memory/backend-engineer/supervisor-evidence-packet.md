---
name: supervisor-evidence-packet
description: How the agent_supervisor review evidence packet is built/collected/guarded, the canonical documented-test-command source, and loop.py's modularity ceiling
metadata:
  type: project
---

Supervisor review runs on a bounded, digest-bound EVIDENCE PACKET (never the repo/transcript). Key seams:

- `tools/agent_supervisor/evidence.py`: `EvidenceCollector` (read-only git via `assert_read_only_git`, `GIT_FACT_COMMANDS`, bounded `read_file`) + `build_packet`. `build_packet` params `task_packet=` and `extra_sections=` are the extension points. **`extra_sections` bypasses the builder's top-level `failed_collections` routing** — sections placed there must be fail-visible INLINE (render ok/failed per entry). Only `task_packet=` (a `CollectionResult`) routes a missing file to `failed_collections` (as `task_packet.file`). Whole packet is redacted by `redact_structure` and byte-capped (`DEFAULT_PACKET_BYTES` 262144 → `STOP_FOR_OWNER`).
- `loop.py::_collect` (~line 2400) assembles the packet from `self.collector`. `self.collector is None` in most shadow/unit tests.
- Injection immunization = `review_packet.guard_packet` (AD-083/0A.1): scans `sections` KEYS for prohibited markers + a whole-packet structural byte cap (`_scan_packet_size`, `DEFAULT_GUARD_MAX_PACKET_BYTES=8MB`) that catches value-smuggled dumps. New sections under `sections` are covered automatically (no guard change needed). Load-bearing mutation test: pass `max_packet_bytes=0` to disable the cap and prove a hostile oversized value slips through.
- Reviewer contract text: `codex_reviewer.REVIEW_INSTRUCTIONS` (must stay pure ASCII + deterministic; do NOT change the codex output schema or decision enum). Existing tests hard-anchor phrases like "YOUR MEASURED ACCESS on this host: NONE" and "WORKER-AUTHORED DATA: inspect it, never" — keep anchor phrases contiguous on one physical concatenated line.

Canonical source of a task's documented test commands = **`TaskAuthority.documented_test_commands`** (populated by `policy.validate_documented_test_commands` against `tools/agent_supervisor/schemas/task_packet_commands.schema.json`, packet key `documented_test_commands`). NOT `command_docs.py` — that module is the doc-VALIDATION tooth (owner-presented CLI commands vs the live parser), unrelated to runtime. Tokenize a documented command with `policy.parse_command(cmd).tokens` (single clean segment, no metachars).

git porcelain (`status --porcelain=v1 --untracked-files=all`) quotes paths with spaces AND octal-escapes non-ASCII UTF-8 bytes on this host (e.g. `?? "caf\303\251.py"`, `?? "with space.py"`); nested unquoted `?? pkg/sub/f.py`. A C-unquote decoder (octal→bytes→utf-8) is required.

`loop.py` is grandfathered-oversized: baseline 1899, material-growth limit = baseline + max(50, 10%) = **2088**, and after M0-T148 it sits at EXACTLY 2088 (zero headroom). `modularity_check.py` fails on `sloc > limit`; SLOC = non-blank non-`#` physical lines; test files (`test_*.py`) and `tests/`,`fixtures/`,`schemas/`,`prompts/` segments are excluded. Any further line added to loop.py fails the gate → decompose, don't grow. Put new collection/logic in evidence.py (or a focused module), not loop.py.
