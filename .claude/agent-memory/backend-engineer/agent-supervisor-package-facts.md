---
name: agent-supervisor-package-facts
description: Stable facts for tools/agent_supervisor work — manifest is dynamic (new files safe), evidence packet size, digest round-trip scheme, unittest convention
metadata:
  type: reference
---

Facts about `tools/agent_supervisor/` (verified M0-T042, 2026-08-07) useful for future supervisor changes.

- **Manifest is generated dynamically, not frozen.** `manifest.py` uses `rglob("*")` over `COVERED_PATTERNS`
  (`*.py`, `schemas/*.json`, `prompts/*.md`, `README.md`, `config*.toml`, `launchers/*`) and verifies against a
  manifest generated in the same run. There is NO committed file-list fixture. Adding new `.py` modules and editing
  `README.md`/`__init__.py` docstrings is manifest-safe — no test enumerates an expected file set.
- **Tests are stdlib `unittest`, no pytest.** Run the whole suite: `python -m unittest discover -s tools -p
  "test_agent_supervisor_*.py"` from the orch root (Py 3.11, Windows). As of M0-T042: 1212 run / 0 fail / 2 skip,
  ~73s. Fake-CLI tests write a decision file and emit a `--json` usage event; never invoke a real `codex`/`claude`.
- **A minimal `ev.build_packet(run_id,task_id,checkpoint_id,checkpoint)` packet is ~650 bytes (~163 est. tokens at
  bytes/4).** Budget-refusal tests must use a SMALL `model_context_window` (e.g. 100 → 20-token/80-byte ceiling) to
  actually trip `within_ceiling=False`; a window of 1000 (200-token ceiling) does NOT refuse such a packet.
- **Record digest scheme (models.digest_of over canonical_json):** `digest_of` is SHA-256 over sorted-key,
  no-whitespace, non-ASCII-preserved JSON — deterministic over dicts. For a sealed record, compute the digest over
  the body with `redaction_labels` as a LIST and WITHOUT the `record_digest` key; a `to_dict()` that converts the
  lone tuple field to a list keeps the in-memory and JSON-round-trip digests identical.
- **`process.run` signature:** `run(argv, *, cwd=, env=, timeout=, input_text=, container=, use_job_object=)`.
  `redaction.redact_structure(obj)` returns `RedactionResult(.value/.count/.labels)`; masks by sensitive KEY and by
  value patterns. `models.USAGE_UNKNOWN == "unknown"` (missing usage is unknown, never 0).
