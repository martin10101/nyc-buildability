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
      directive_reminder) — the policy may never arrive by replacing the file

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
    hooks_blob = json.dumps(settings.get("hooks", {}))
    for hook in PRESERVED_HOOKS:
        if hook not in hooks_blob:
            errors.append(f"p7 pre-existing hook registration {hook!r} disappeared")

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
