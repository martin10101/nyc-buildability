# G3 Delta Re-attestation — M0-T149 (frozen candidate v2 = 45b0572c)

- **Reviewed identity:** frozen candidate **45b0572c** on `task/M0-T149-command-profile` (merged at 7804bc03). Delta vs my reviewed **ed04c4bb** inspected via `git diff ed04c4bb 45b0572c`. Working tree confirmed byte-identical to 45b0572c for the four source files (`git diff --stat 45b0572c -- <files>` empty), so all results below are at the v2 identity.
- **Commands run at v2:** `python -m pytest tools/test_agent_supervisor_policy.py tools/test_agent_supervisor_reviewer.py -q` → **247 passed, 1 skipped** (= producer's 122+1 / 125 split); `ruff check` on the four files → **All checks passed!**; `python tools/modularity_check.py --check` → **selected 357 files; failures 0; warnings 13**. My classifier probes were blocked by the read-only guard's mutation-substring heuristic; behavior is instead confirmed via the passing red/green tests read from source.

## C1 disposition — SATISFIED

**F1 (blocking) — CLOSED.** `_MUTATING_CHECKER_TOKENS` now includes `--add-noqa` (policy.py:983-987). `ruff check --add-noqa` and `python -m ruff check --add-noqa` are refused `mutating_checker_token:--add-noqa`, asserted red/green (`test_the_add_noqa_source_writer_is_refused`) and proven never-executed at the enforcement point (`test_the_add_noqa_source_writer_is_refused_never_executed`: `ok:false`, `non_mutating_profile_refused`, `self.ran == []`).

**F2 — CLOSED.** `--output-file`, `-o`, and `clean` added to the set with an accurate rationale comment noting the internal consistency with git's `-o` (`UNSAFE_GIT_SUBCOMMAND_FLAGS`). Tested (`test_a_report_file_writing_ruff_arg_is_refused`, `test_ruff_clean_is_refused`). The new `test_the_mutating_checker_token_set_covers_every_known_writer` machine-checks the full 8-token set, so the in-source completeness claim is now test-pinned rather than asserted.

**F5 — CLOSED (root-cause fix).** `_refuse_interpreter_target` no longer skips unknown dash tokens: `-c`/fused `-c<code>` → `inline_python_code`; `-m` and fused `-m<module>` both route through the shared `_refuse_python_module` → the one closed module allowlist; any other flag → `unrecognized_interpreter_flag:<token>` (previously a bypass vector where `-mpip`/unknown flags could shuttle the parser past the target check). Tested for `-W`, corrected `-u`, and fused `-mpip`/`-mcompileall`/`-mpydoc`/`-mwebbrowser`/`-cprint(1)`.

**Regression safety — verified.** `test_a_fused_allowlisted_module_still_admits` (`-mpytest`, `-mruff check .` admit) and `test_previously_admitted_real_shapes_still_admit` (all real documented shapes admit `""`) guard the tightening. I re-derived that every `documented_test_commands` shape across `project-control/tasks/*.json` (python `-m pytest/ruff/unittest`, `python tools/*.py …`, bare `pytest -q`/`ruff check .`) still admits; no new admit path is introduced (the interpreter branch is strictly tighter). The M0-T148 annotation is reworded to the accurate enumerated-shape claim, and F3's report/modularity-claim (13 warnings + policy.py cohesion justification) is corrected. POLICY_VERSION correctly stays 1.1.0 (1.0.0 never shipped; net rule change is still 1.0.0→1.1.0).

## New findings

**LOW / informational (non-blocking) — policy.py:983-987.** The ruff argument gate remains an exact-token denylist, so the fused short-option-with-value spelling `ruff check -o<file>` (e.g. `-oreport.txt`, token `!= "-o"`) is not matched and would be admitted. Esoteric (no orchestrator-authored packet uses fused short-value ruff flags), low impact (writes a report file), and the inherent limit of a token denylist — noted for the record, not a blocking item. All realistic/documented mutating spellings are now covered.

C1 is satisfied and no blocking items remain. The delta is a clean, well-tested tightening.

VERDICT: PASS

---

*Orchestrator preservation note: saved VERBATIM from the code-reviewer agent-return channel (2026-09-07 delta re-attestation; HTML entities decoded, content unaltered).*
