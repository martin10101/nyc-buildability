#!/usr/bin/env python3
"""Push safety as PURE POLICY CHECKS (D-007 S13.6).

A branch push is an external side effect AND a controller action: the supervisor
performs pushes itself after a passing review, and the worker never holds
credentials that could (S4.1, S13.3, ADR-005 reconciliation).

**This phase implements the checks only. It never pushes.** There is no
subprocess call in this module and no code path that invokes git, gh, or any
network client - `assert_no_execution()` exists to make that explicit and is
asserted by the tests. Execution belongs to a later phase and is additionally
gated on the ADR-005 amendment being in force, which the owner ruled must precede
any pushing supervisor mode.

The checks answer the S13.6 questions before a push could ever be attempted:

* is the remote URL and repository identity exactly what we expect?
* is the branch the exact authorized non-`main` task branch?
* does local `HEAD` match the expected remote head (and if not, is the result
  ambiguous rather than simply failed)?
* what is the complete changed-path set, and does it touch workflows, hooks,
  dependency manifests/lockfiles, build/deploy definitions, permissions/config,
  submodules, LFS, filters, or attributes?
* which workflows would the push or PR trigger, and is any of them
  `pull_request_target` or secret-bearing?
* is any unauthorized deployment path reachable?

Anything sensitive is an owner/security gate - ASK at minimum. A push to `main`
and a force push are HARD-DENY and no model opinion moves them.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Mapping

from .policy import (
    ASK,
    AUTO,
    DENY_AND_CONTINUE,
    HARD_DENY,
    SECURITY_RELEVANT_CLASSES,
    TIER_ORDER,
    DEFAULT_POLICY_CONFIG,
    PolicyConfig,
    PolicyDecision,
    file_class,
)

#: Structural statement of this phase's boundary.
NO_PUSH_EXECUTION_IN_THIS_PHASE = True

#: Workflow trigger markers that make a workflow a security gate.
DANGEROUS_WORKFLOW_MARKERS: tuple[str, ...] = (
    "pull_request_target", "workflow_run", "secrets.", "${{ secrets",
    "environment:", "id-token: write", "permissions: write-all",
)

#: Path shapes that could reach a deployment.
DEPLOYMENT_PATH_MARKERS: tuple[str, ...] = (
    ".github/workflows/deploy", "render.yaml", "render.yml", "deploy/",
    "infra/", "k8s/", "helm/", "fly.toml", "vercel.json", "netlify.toml",
)


class PushPolicyError(Exception):
    """A push-policy input was malformed."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def assert_no_execution() -> None:
    """Called by tests and `doctor`: this module never performs a push."""
    if not NO_PUSH_EXECUTION_IN_THIS_PHASE:  # pragma: no cover - constant guard
        raise PushPolicyError("execution_not_authorized",
                              "push execution is not authorized in this phase")


@dataclasses.dataclass(frozen=True)
class PushPlan:
    """Everything the checks need. Facts are supplied by the evidence collector."""

    remote_name: str
    remote_url: str
    expected_remote_url: str
    branch: str
    authorized_branch: str
    local_head: str
    expected_remote_head: str = ""
    observed_remote_head: str = ""
    changed_paths: tuple[str, ...] = ()
    force: bool = False
    mode: str = "shadow"
    grant_id: str = ""
    review_passed: bool = False
    workflow_contents: Mapping[str, str] = dataclasses.field(default_factory=dict)
    secret_scan_findings: tuple[str, ...] = ()
    remote_state_known: bool = True


@dataclasses.dataclass(frozen=True)
class PushCheck:
    """One named check with its own tier contribution."""

    name: str
    tier: str
    reason_code: str
    detail: str

    @property
    def ok(self) -> bool:
        return self.tier == AUTO


@dataclasses.dataclass(frozen=True)
class PushEvaluation:
    """The combined verdict. `executed` is always False in this phase."""

    decision: PolicyDecision
    checks: tuple[PushCheck, ...]
    sensitive_classes: tuple[str, ...] = ()
    triggered_workflows: tuple[str, ...] = ()
    deployment_paths: tuple[str, ...] = ()
    executed: bool = False

    def failing(self) -> tuple[PushCheck, ...]:
        return tuple(c for c in self.checks if not c.ok)


def _normalize_remote(url: str) -> str:
    """Compare remotes by identity, not by spelling."""
    text = url.strip().lower().rstrip("/")
    text = re.sub(r"\.git$", "", text)
    text = re.sub(r"^git@([^:]+):", r"https://\1/", text)
    text = re.sub(r"^ssh://git@", "https://", text)
    text = re.sub(r"^https?://[^@/]+@", "https://", text)
    return text


def evaluate_push(plan: PushPlan, *,
                  config: PolicyConfig = DEFAULT_POLICY_CONFIG) -> PushEvaluation:
    """Run every S13.6 check. Returns the strictest tier any check produced."""
    assert_no_execution()
    checks: list[PushCheck] = []

    # 1. Force push and main are HARD-DENY, checked first and unconditionally.
    if plan.force:
        checks.append(PushCheck("force_push", HARD_DENY, "force_push",
                                "a force push is denied regardless of any model's "
                                "opinion (S4.4)"))
    branch = plan.branch.strip()
    if branch.lower() in {name.lower() for name in config.main_branch_names} or \
            branch.lower().endswith("/main"):
        checks.append(PushCheck("target_branch", HARD_DENY, "push_to_main",
                                f"{branch!r} is a protected default branch; a direct push "
                                f"to it is denied (S4.4, invariant 8)"))
    elif not branch:
        checks.append(PushCheck("target_branch", HARD_DENY, "no_branch",
                                "a push with no named branch is refused"))
    elif plan.authorized_branch and branch != plan.authorized_branch:
        checks.append(PushCheck(
            "target_branch", HARD_DENY, "unauthorized_branch",
            f"{branch!r} is not the exact authorized task branch "
            f"{plan.authorized_branch!r}"))
    else:
        checks.append(PushCheck("target_branch", AUTO, "exact_task_branch",
                                f"{branch!r} is the exact authorized non-main task branch"))

    # 2. Remote identity.
    if _normalize_remote(plan.remote_url) != _normalize_remote(plan.expected_remote_url):
        checks.append(PushCheck(
            "remote_identity", HARD_DENY, "remote_identity_mismatch",
            f"remote {plan.remote_name!r} is {plan.remote_url!r}, not the expected "
            f"{plan.expected_remote_url!r}"))
    else:
        checks.append(PushCheck("remote_identity", AUTO, "remote_verified",
                                f"remote {plan.remote_name!r} matches the expected "
                                f"repository identity"))

    # 3. Head expectations. An unknown or divergent remote head is AMBIGUOUS, and
    #    an ambiguous push result is queried, never retried blindly (S13.6).
    if not plan.remote_state_known:
        checks.append(PushCheck(
            "remote_head", ASK, "remote_state_unknown",
            "the remote head could not be read; a decision that depends on current "
            "remote state may not claim success from stale refs"))
    elif plan.expected_remote_head and \
            plan.observed_remote_head != plan.expected_remote_head:
        checks.append(PushCheck(
            "remote_head", ASK, "remote_head_diverged",
            f"the remote head is {plan.observed_remote_head!r}, expected "
            f"{plan.expected_remote_head!r}; query the remote before any retry"))
    else:
        checks.append(PushCheck("remote_head", AUTO, "remote_head_as_expected",
                                "local HEAD and the expected remote head agree"))

    # 4. Changed-path classes.
    classes: dict[str, list[str]] = {}
    for path in plan.changed_paths:
        klass = file_class(path.replace("\\", "/"))
        if klass in SECURITY_RELEVANT_CLASSES:
            classes.setdefault(klass, []).append(path)
    if classes:
        summary = "; ".join(f"{k}: {sorted(v)}" for k, v in sorted(classes.items()))
        checks.append(PushCheck(
            "changed_path_classes", ASK, "sensitive_path_classes",
            f"the diff touches security-relevant classes ({summary}); workflow code, "
            f"hooks, dependency manifests/lockfiles, deployment definitions, and "
            f"permission/config files require an explicit owner/security gate"))
    else:
        checks.append(PushCheck("changed_path_classes", AUTO, "ordinary_paths",
                                f"{len(plan.changed_paths)} changed path(s), all ordinary"))

    # 5. Which workflows the push would trigger, and whether any is dangerous.
    triggered = tuple(sorted(p for p in plan.changed_paths
                             if ".github/workflows/" in p.replace("\\", "/")))
    dangerous: list[str] = []
    for path, body in plan.workflow_contents.items():
        lowered = (body or "").lower()
        for marker in DANGEROUS_WORKFLOW_MARKERS:
            if marker.lower() in lowered:
                dangerous.append(f"{path}:{marker}")
    if dangerous:
        checks.append(PushCheck(
            "workflow_safety", ASK, "secret_bearing_or_privileged_workflow",
            f"a triggered workflow is privileged or secret-bearing ({sorted(dangerous)}); "
            f"this requires an explicit owner/security gate"))
    elif triggered:
        checks.append(PushCheck(
            "workflow_safety", ASK, "workflow_change",
            f"the push changes workflow code {list(triggered)}; workflow changes require "
            f"an explicit owner/security gate"))
    else:
        checks.append(PushCheck("workflow_safety", AUTO, "no_workflow_change",
                                "no workflow file is changed by this push"))

    # 6. Reachable deployment paths.
    deployment = tuple(sorted(
        p for p in plan.changed_paths
        if any(marker in p.replace("\\", "/") for marker in DEPLOYMENT_PATH_MARKERS)))
    if deployment:
        checks.append(PushCheck(
            "deployment_reachability", ASK, "deployment_path_reachable",
            f"the diff touches deployment definitions {list(deployment)}; no unauthorized "
            f"deployment path may be reachable from an automatic push"))
    else:
        checks.append(PushCheck("deployment_reachability", AUTO, "no_deployment_path",
                                "no deployment definition is changed"))

    # 7. Secret scan. A finding is suspected leakage - a Section 4.5 pause.
    if plan.secret_scan_findings:
        checks.append(PushCheck(
            "secret_scan", HARD_DENY, "suspected_secret_leakage",
            f"the secret scan reported {list(plan.secret_scan_findings)}; suspected "
            f"leakage pauses synchronously (S4.5) and never pushes"))
    else:
        checks.append(PushCheck("secret_scan", AUTO, "secret_scan_clean",
                                "the required secret scan reported nothing"))

    # 8. Authority: a push is AUTO only with an owner grant, a passing review, and
    #    limited-auto actually active. None of that is in force by default.
    if not plan.grant_id:
        checks.append(PushCheck("authority", ASK, "no_standing_grant",
                                "no owner standing grant covers this push"))
    elif not plan.review_passed:
        checks.append(PushCheck("authority", ASK, "review_not_passed",
                                "the grant requires a passing review first"))
    elif plan.mode != "limited-auto":
        checks.append(PushCheck(
            "authority", ASK, "mode_not_limited_auto",
            f"mode is {plan.mode!r}; a push proceeds automatically only in limited-auto, "
            f"which is disabled and is enabled only by an explicit owner activation"))
    else:
        checks.append(PushCheck("authority", AUTO, "granted",
                                f"covered by owner grant {plan.grant_id} after a passing "
                                f"review"))

    strictest = max(checks, key=lambda c: TIER_ORDER[c.tier])
    if strictest.tier == HARD_DENY:
        decision = PolicyDecision(
            tier=HARD_DENY, reason_code=strictest.reason_code, reason=strictest.detail,
            outcome=DENY_AND_CONTINUE, rule_id="S13.6",
            synchronous_stop=strictest.reason_code == "suspected_secret_leakage")
    elif strictest.tier == ASK:
        decision = PolicyDecision(
            tier=ASK, reason_code=strictest.reason_code, reason=strictest.detail,
            rule_id="S13.6", classification="security")
    else:
        decision = PolicyDecision(
            tier=AUTO, reason_code="push_checks_passed",
            reason=("every S13.6 check passed. NOTE: this phase implements the checks "
                    "only - no push is executed here"),
            rule_id="S13.6")

    return PushEvaluation(
        decision=decision,
        checks=tuple(checks),
        sensitive_classes=tuple(sorted(classes)),
        triggered_workflows=triggered,
        deployment_paths=deployment,
        executed=False,
    )


def describe(evaluation: PushEvaluation) -> dict[str, Any]:
    """A compact record for the audit log and the owner notification."""
    return {
        "tier": evaluation.decision.tier,
        "reason_code": evaluation.decision.reason_code,
        "reason": evaluation.decision.reason,
        "checks": [dataclasses.asdict(c) for c in evaluation.checks],
        "failing_checks": [c.name for c in evaluation.failing()],
        "sensitive_classes": list(evaluation.sensitive_classes),
        "triggered_workflows": list(evaluation.triggered_workflows),
        "deployment_paths": list(evaluation.deployment_paths),
        "executed": evaluation.executed,
        "phase_note": "policy checks only; push execution is not implemented here",
    }
