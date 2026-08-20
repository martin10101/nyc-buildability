#!/usr/bin/env python3
"""Deterministic, read-only validator for the repository MCP default-deny policy
(owner directive D-020, task M0-T077). Stdlib-only. Fail-closed: ANY missing,
weakened, malformed, or unparseable invariant is an error.

The policy lives in the checked-in project settings (.claude/settings.json) and
must guarantee that fresh ordinary Claude Code sessions opened from this
repository (and its clean worktrees) load NO unrelated external MCP server:

  p1  settings file exists and parses as a JSON object
  p2  disableClaudeAiConnectors is exactly true      (claude.ai account connectors
      are never auto-fetched or connected)
  p3  allowedMcpServers is exactly []                (default-deny allowlist: no MCP
      server of any scope may load; an ABSENT key means "all allowed" and is a
      policy failure, not a default)
  p4  deniedMcpServers contains at least the five audited local identifiers
      (pencil, supabase, mysql, sequential-thinking, playwright) as
      {"serverName": ...} entries (deny > allow; survives a future allowlist edit)
  p5  disabledMcpjsonServers contains at least the four audited .mcp.json
      identifiers (supabase, mysql, sequential-thinking, playwright)
  p6  enableAllProjectMcpServers is exactly false
  p8  permissions.deny contains "mcp__*" (deny-first tool rule: per the official
      settings precedence, a deny at any level cannot be allowed by another level,
      so MCP tool use stays blocked even if a broader allowlist appears in a user
      or local settings source)
  p7  the pre-existing settings the merge was required to preserve still exist:
      $schema, model, fallbackModel, effortLevel, env, and the three control-plane
      hook registrations (agent_dispatch_guard, readonly_agent_guard,
      directive_reminder) — each hook must be an actual registration (its script
      referenced by a registered entry's "command"), not merely a substring
      anywhere in the hooks blob — the policy may never arrive by replacing the
      file (G3 F-3)
  p9  whole-file shape assertion: Claude Code DISCARDS the entire settings file —
      silently voiding the whole policy — when any key carries a schema-invalid
      shape, even though the file still parses as JSON (G3 F-2 + re-review probes
      59-63 demonstrated eight such shapes). Instead of enumerating discard shapes,
      EVERY key present must be a known key matching its expected shape, including
      list element types and the env/permissions/hooks sub-structures; anything
      unrecognized or mistyped fails CLOSED. Adding a genuinely new setting to the
      checked-in file therefore requires extending KNOWN_KEY_SHAPES in the same
      reviewed change — intended visibility, mirroring the connector procedure
  p10 CI-wiring twin check (G4 MAJOR-2): the required control-plane workflow must
      still run BOTH policy steps (this validator and its test suite). Removing
      one step is caught by the survivor; removing both removes every executor of
      this file and is catchable only by diff review — disclosed, not hidden

A future task that is explicitly authorized to use ONE connector edits the policy
inside its own reviewed task (see docs/MCP_DEFAULT_DENY_POLICY.md); this validator
then fails until its expectations are amended in that same reviewed change, which
is exactly the intended visibility.

Usage:
  python tools/validate_mcp_policy.py            # human report, exit 0/1
  python tools/validate_mcp_policy.py --check    # quiet on success
  python tools/validate_mcp_policy.py --settings PATH   # test override
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SETTINGS = ROOT / ".claude" / "settings.json"

#: Exact audited identifiers (project-control/reports/M0-T077-mcp-audit.md).
DENIED_SERVER_NAMES = (
    "pencil",
    "supabase",
    "mysql",
    "sequential-thinking",
    "playwright",
)
DISABLED_MCPJSON_NAMES = (
    "supabase",
    "mysql",
    "sequential-thinking",
    "playwright",
)
#: Pre-existing keys the D-020 merge was required to preserve (p7).
PRESERVED_KEYS = ("$schema", "model", "fallbackModel", "effortLevel", "env", "hooks")
PRESERVED_HOOKS = (
    "agent_dispatch_guard.py",
    "readonly_agent_guard.py",
    "directive_reminder.py",
)
#: permissions.defaultMode values PROVEN accepted by the consumer (G3 re-review
#: probes 55-58 verified all four against the live CLI); anything else makes Claude
#: Code discard the whole settings file. Deliberately conservative: a value missing
#: here fails VISIBLY (fail closed), never silently.
VALID_DEFAULT_MODES = ("default", "acceptEdits", "plan", "bypassPermissions")


def _is_str_list(v: object) -> bool:
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


def _is_str_dict(v: object) -> bool:
    return (isinstance(v, dict)
            and all(isinstance(k, str) and isinstance(x, str) for k, x in v.items()))


def _is_mcp_matcher_list(v: object) -> bool:
    """allowedMcpServers/deniedMcpServers: entries carry exactly one matcher —
    serverName (str), serverUrl (str), or serverCommand (list of str)."""
    if not isinstance(v, list):
        return False
    for entry in v:
        if not isinstance(entry, dict) or len(entry) != 1:
            return False
        ((key, val),) = entry.items()
        if key in ("serverName", "serverUrl"):
            if not isinstance(val, str):
                return False
        elif key == "serverCommand":
            if not _is_str_list(val):
                return False
        else:
            return False
    return True


def _is_hooks_shape(v: object) -> bool:
    """hooks: {event: [{matcher?: str, hooks: [{type: str, command: str}, ...]}]}"""
    if not isinstance(v, dict):
        return False
    for event, entries in v.items():
        if not isinstance(event, str) or not isinstance(entries, list):
            return False
        for entry in entries:
            if not isinstance(entry, dict):
                return False
            if "matcher" in entry and not isinstance(entry["matcher"], str):
                return False
            inner = entry.get("hooks")
            if not isinstance(inner, list):
                return False
            for hook in inner:
                if not isinstance(hook, dict):
                    return False
                if not isinstance(hook.get("type"), str):
                    return False
                if not isinstance(hook.get("command"), str):
                    return False
    return True


#: Known permission sub-keys and their required shapes (p9).
PERMISSION_KEY_SHAPES = {
    "deny": (_is_str_list, "list of rule strings"),
    "allow": (_is_str_list, "list of rule strings"),
    "ask": (_is_str_list, "list of rule strings"),
    "additionalDirectories": (_is_str_list, "list of path strings"),
    "defaultMode": (lambda v: v in VALID_DEFAULT_MODES,
                    f"one of {VALID_DEFAULT_MODES}"),
}

#: Every key the checked-in settings file is allowed to carry, with its required
#: shape (p9). A key added to the file later must be added here in the SAME
#: reviewed change, or the validator fails closed.
KNOWN_KEY_SHAPES = {
    "$schema": (lambda v: isinstance(v, str), "string"),
    "model": (lambda v: isinstance(v, str), "string"),
    "fallbackModel": (_is_str_list, "list of model-id strings"),
    "effortLevel": (lambda v: isinstance(v, str), "string"),
    "disableClaudeAiConnectors": (lambda v: isinstance(v, bool), "boolean"),
    "allowedMcpServers": (_is_mcp_matcher_list, "list of matcher objects"),
    "deniedMcpServers": (_is_mcp_matcher_list, "list of matcher objects"),
    "disabledMcpjsonServers": (_is_str_list, "list of server-name strings"),
    "enableAllProjectMcpServers": (lambda v: isinstance(v, bool), "boolean"),
    "permissions": (lambda v: isinstance(v, dict), "object"),
    "env": (_is_str_dict, "object of string values"),
    "hooks": (_is_hooks_shape, "hooks registration structure"),
}


def _registered_hook_commands(hooks: object):
    """Yield every "command" string of an actual hook registration.

    Shape: hooks -> {event: [{matcher?, hooks: [{type, command}, ...]}, ...]}.
    Anything malformed is simply not yielded — the caller then reports the
    expected hook as missing (fail closed)."""
    if not isinstance(hooks, dict):
        return
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            for hook in entry.get("hooks") or []:
                if isinstance(hook, dict) and isinstance(hook.get("command"), str):
                    yield hook["command"]


def validate(settings_path: Path) -> list[str]:
    """Return the list of policy errors (empty = policy intact)."""
    errors: list[str] = []
    if not settings_path.is_file():
        return [f"p1 settings file missing: {settings_path}"]
    try:
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [f"p1 settings file unreadable/unparseable: {exc}"]
    if not isinstance(settings, dict):
        return ["p1 settings root is not a JSON object"]

    if settings.get("disableClaudeAiConnectors") is not True:
        errors.append("p2 disableClaudeAiConnectors must be exactly true "
                      f"(found: {settings.get('disableClaudeAiConnectors')!r})")

    allowed = settings.get("allowedMcpServers")
    if allowed != []:
        errors.append("p3 allowedMcpServers must be present and exactly [] "
                      f"(found: {allowed!r}; an absent key means ALL servers allowed)")

    denied = settings.get("deniedMcpServers")
    denied_names = set()
    if isinstance(denied, list):
        for entry in denied:
            if isinstance(entry, dict) and isinstance(entry.get("serverName"), str):
                denied_names.add(entry["serverName"])
    for name in DENIED_SERVER_NAMES:
        if name not in denied_names:
            errors.append(f"p4 deniedMcpServers is missing the audited identifier "
                          f"{{'serverName': '{name}'}}")

    disabled = settings.get("disabledMcpjsonServers")
    disabled_names = {n for n in disabled if isinstance(n, str)} if isinstance(disabled, list) else set()
    for name in DISABLED_MCPJSON_NAMES:
        if name not in disabled_names:
            errors.append(f"p5 disabledMcpjsonServers is missing the audited "
                          f"identifier '{name}'")

    if settings.get("enableAllProjectMcpServers") is not False:
        errors.append("p6 enableAllProjectMcpServers must be exactly false "
                      f"(found: {settings.get('enableAllProjectMcpServers')!r})")

    permissions = settings.get("permissions")
    deny_rules = permissions.get("deny") if isinstance(permissions, dict) else None
    if not (isinstance(deny_rules, list) and "mcp__*" in deny_rules):
        errors.append("p8 permissions.deny must contain the un-overridable "
                      "deny-first tool rule 'mcp__*' "
                      f"(found: {deny_rules!r})")

    for key in PRESERVED_KEYS:
        if key not in settings:
            errors.append(f"p7 pre-existing setting {key!r} disappeared "
                          "(the policy must merge, never replace)")
    # Each guard script must be referenced BY FULL PATH inside a registered hook
    # command (hooks -> event -> entry -> hooks[] -> command), not merely appear as
    # a substring somewhere in the hooks blob (G3 F-3 decoy). Honest residual: a
    # string-level check cannot prove invocation semantics — a command crafted to
    # contain the exact path still satisfies it; the behavioral guarantee comes
    # from the hook test suites the same CI job runs.
    commands = list(_registered_hook_commands(settings.get("hooks")))
    for hook in PRESERVED_HOOKS:
        if not any(f".claude/hooks/{hook}" in cmd for cmd in commands):
            errors.append(f"p7 pre-existing hook registration {hook!r} disappeared "
                          "(no registered hook command references "
                          f".claude/hooks/{hook})")

    # p9 whole-file shape assertion (fail closed): any unknown or mistyped key can
    # make Claude Code silently discard the ENTIRE settings file.
    for key, value in settings.items():
        spec = KNOWN_KEY_SHAPES.get(key)
        if spec is None:
            errors.append(f"p9 unknown settings key {key!r} (fail closed: an "
                          "unrecognized or mistyped key is the consumer-discard "
                          "vector; extend KNOWN_KEY_SHAPES in the same reviewed "
                          "change that adds a key)")
            continue
        check, expected = spec
        if not check(value):
            errors.append(f"p9 settings key {key!r} must be {expected}; a "
                          "schema-invalid shape makes Claude Code discard the "
                          "ENTIRE settings file")
    if isinstance(permissions, dict):
        for key, value in permissions.items():
            spec = PERMISSION_KEY_SHAPES.get(key)
            if spec is None:
                errors.append(f"p9 unknown permissions sub-key {key!r} (fail closed)")
                continue
            check, expected = spec
            if not check(value):
                errors.append(f"p9 permissions.{key} must be {expected}; a "
                              "schema-invalid shape makes Claude Code discard the "
                              "ENTIRE settings file")

    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    try:
        ci_text = ci_path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"p10 cannot read {ci_path.name}: {exc} (fail closed)")
    else:
        for step in ("python3 tools/validate_mcp_policy.py --check",
                     "python3 tools/test_mcp_policy.py"):
            if step not in ci_text:
                errors.append(f"p10 required control-plane CI step missing: {step!r}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="quiet on success")
    parser.add_argument("--settings", type=Path, default=DEFAULT_SETTINGS,
                        help="settings file to validate (tests only)")
    args = parser.parse_args(argv)
    errors = validate(args.settings)
    if errors:
        print(f"MCP default-deny policy INVALID ({len(errors)} error(s)):")
        for err in errors:
            print(f"  - {err}")
        return 1
    if not args.check:
        print("MCP default-deny policy intact: claude.ai connectors disabled, "
              "empty allowlist, audited identifiers denied, .mcp.json servers "
              "rejected, auto-approval off, pre-existing settings preserved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
