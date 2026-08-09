"""M0-T054 post-apply doctor proof (R314). Unelevated, read-only. Durable evidence.

Run from the repo root with the repo on PYTHONPATH:
    PYTHONPATH=<repo> python project-control/reports/M0-T054-protected-config/doctor_proof.py

Verifies every condition the owner enumerated (R314) and prints one PASS/FAIL verdict.
Exit 0 only if ALL checks pass.

SHA note (owner decision "A", 2026-08-09): the elevated apply delivered the
authorized content with CRLF line endings (git autocrlf converted the staged file,
which lives under project-control/reports/** and lacked the eol=lf pin that
directives/** has). The applied content is byte-identical to the intended change
except \\n vs \\r\\n: stripping CR yields exactly the pre-registered LF SHA
9560f901e40e64cc320698c6cea9d5996e9e8495fb3ed22c6e681a6ebf1581e5. The owner
ACCEPTED the applied CRLF form as correct, so the recorded expected SHA is the
applied value below. Both are asserted here for transparency.
"""
from __future__ import annotations
import hashlib, json, sys
from pathlib import Path

CONFIG = Path(r"C:\Program Files\SupervisorConfig\config.toml")
STAGED = Path(r"C:\Users\MLFLL\Downloads\nyc-zoning\nyc-development-feasibility-claude-pack\project-control\reports\M0-T054-protected-config\config.staged.toml")
MODEL_SELECTION = Path(r"C:\SupervisorController\model_selection.toml")
EXPECTED_APPLIED_SHA = "6aef12a9f60a6a64d7af77de3c071289c35dfe60977239e901df8d642c3fffde"  # accepted CRLF form (owner decision A)
PREREGISTERED_LF_SHA = "9560f901e40e64cc320698c6cea9d5996e9e8495fb3ed22c6e681a6ebf1581e5"  # LF form (CR-stripped)

results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))


live = CONFIG.read_bytes()
staged = STAGED.read_bytes()
check("content matches staged file", live == staged, f"live {len(live)}B vs staged {len(staged)}B")

live_sha = hashlib.sha256(live).hexdigest()
check("SHA-256 == recorded applied value", live_sha == EXPECTED_APPLIED_SHA,
      f"live {live_sha[:16]}.. expected {EXPECTED_APPLIED_SHA[:16]}..")
check("content == authorized change (CR-stripped == pre-registered LF SHA)",
      hashlib.sha256(live.replace(b"\r\n", b"\n")).hexdigest() == PREREGISTERED_LF_SHA,
      "line-ending-only difference confirmed")

from tools.agent_supervisor import os_acl
verdict = os_acl.evaluate_controller_config_acl(str(CONFIG)).to_dict()
check("protected FILE ACL = PROTECTED", verdict.get("file", {}).get("protected") is True,
      verdict.get("file", {}).get("state"))
parent = verdict.get("parent") or {}
check("protected PARENT ACL = PROTECTED", parent.get("protected") is True, parent.get("state"))
aces = verdict.get("file", {}).get("evidence", {}).get("aces", [])
principals = {a.get("principal", ""): tuple(a.get("rights", [])) for a in aces}
three_ok = (
    any(p.endswith("Administrators") and set(r) == {"F"} for p, r in principals.items())
    and any(p.endswith("SYSTEM") and set(r) == {"F"} for p, r in principals.items())
    and any(p.endswith("MLFLL") and set(r) == {"RX"} for p, r in principals.items())
    and len(aces) == 3
)
check("intended three-principal DACL (Admins:F, SYSTEM:F, MLFLL:RX)", three_ok,
      json.dumps([(a.get("principal"), a.get("rights")) for a in aces]))

check("config readable (unelevated)", True, "read succeeded")

try:
    with open(MODEL_SELECTION, "a", encoding="utf-8"):
        writable = True
except Exception:
    writable = False
check("model_selection.toml writable by ordinary account", writable is True, str(MODEL_SELECTION))

from tools.agent_supervisor import config as C
import tempfile, os
cfg = C.load_controller_config(str(CONFIG))
sel_text = (
    '[codex]\nreview_model = "gpt-5.6-sol"\nadvisory_model = ""\n'
    'fallback_models = ["gpt-5.6-terra"]\n\n[claude]\nmodel = "claude-opus-4-8"\nfallback_models = []\n'
)
tmp = Path(tempfile.gettempdir()) / "ms.opus.proof.toml"
tmp.write_text(sel_text, encoding="utf-8")
res = C.validate_selection(cfg, C.load_model_selection(str(tmp)))
os.unlink(tmp)
check("explicit claude-opus-4-8 selection accepted (live config)", res.ok, "; ".join(res.errors))

check("controller.default_mode == shadow", cfg.raw.get("controller", {}).get("default_mode") == "shadow",
      str(cfg.raw.get("controller", {})))
check("codex.allowed_models unchanged", tuple(cfg.codex_allowed_models) == ("gpt-5.6-sol", "gpt-5.6-terra"),
      str(cfg.codex_allowed_models))
check("claude.allowed_models == [claude-opus-4-8] only", tuple(cfg.claude_allowed_models) == ("claude-opus-4-8",),
      str(cfg.claude_allowed_models))

allok = all(ok for _, ok, _ in results)
print("=== M0-T054 protected-config doctor proof (R314), owner decision A ===")
for name, ok, detail in results:
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  ({detail})" if detail else ""))
print("=== VERDICT:", "ALL PASS" if allok else "FAILURE — STOP", "===")
sys.exit(0 if allok else 1)
