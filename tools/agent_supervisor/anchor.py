#!/usr/bin/env python3
"""External audit anchoring - Option A mechanism only (D-007 S13.12; ruling D-007-R533).

The owner ruled Option A: a controller-pushed anchor branch. At every checkpoint
the supervisor produces an anchor - the audit chain's head digest, bound to the
controller version and the checkout identity - plus the EXACT `git` argv that
would publish it to a dedicated anchor branch.

**This module is a MECHANISM. It executes nothing.** There is no `subprocess`
import here and no call site that runs a command; `assert_no_execution` asserts
that at import-checking time and a test asserts it structurally. Publishing
requires BOTH of:

  (a) controller-held push credentials existing (the controller pushes, never the
      worker - S13.6 / the ADR-005 reconciliation), and
  (b) an explicit activation the owner performs and that is recorded through
      directive compliance.

`activation_status()` reports which of the two is missing, and
`assert_activated()` refuses with that reason. Until both exist, the honest
description of this build is: the anchor CONTENT and the exact push argv are
produced and stored locally; nothing has ever been pushed. The local sidecar head
anchor from Phase 1 remains the only tamper evidence in force, and it detects
truncation only on the same machine.
"""
from __future__ import annotations

import dataclasses
import re
from typing import Any, Mapping, Sequence

from .models import digest_of, to_utc_iso

#: The dedicated anchor branch. Never a working branch, and never `main`.
ANCHOR_BRANCH = "audit/supervisor-anchors"
ANCHOR_FILE_TEMPLATE = "anchors/{checkout_key}/{sequence:012d}.json"

ACTIVATION_KEY = "audit_anchor_activation"
LAST_ANCHOR_KEY = "audit_anchor_last"

#: Branch names that may never be an anchor target under any configuration.
FORBIDDEN_ANCHOR_BRANCHES: frozenset[str] = frozenset({"main", "master", "HEAD"})


class AnchorError(Exception):
    """An anchoring rule was violated. Nothing is published on this path."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclasses.dataclass(frozen=True)
class AnchorRecord:
    """One checkpoint's anchor: what is being attested, and by which controller."""

    sequence: int
    chain_head_digest: str
    controller_version: str
    checkout_key: str
    run_id: str
    task_id: str
    checkpoint_id: str
    records_covered: int
    created_at_utc: str

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    def digest(self) -> str:
        return digest_of(self.to_dict())

    def content_bytes(self) -> bytes:
        """The EXACT bytes of the anchor file. Deterministic; LF-terminated."""
        from .models import canonical_json

        payload = self.to_dict()
        payload["anchor_digest"] = self.digest()
        return canonical_json(payload) + b"\n"

    def file_path(self) -> str:
        return ANCHOR_FILE_TEMPLATE.format(checkout_key=self.checkout_key[:32],
                                           sequence=self.sequence)

    def commit_message(self) -> str:
        return (f"audit-anchor: {self.checkout_key[:12]} seq {self.sequence} "
                f"head {self.chain_head_digest[:16]}")


def build_anchor(
    *,
    audit_log: Any,
    checkout_key: str,
    run_id: str,
    task_id: str,
    checkpoint_id: str,
) -> AnchorRecord:
    """Produce the anchor for the audit chain's CURRENT head. Reads only."""
    from . import CONTROLLER_VERSION

    verification = audit_log.verify_chain()
    if not verification.ok:
        raise AnchorError(
            "chain_not_verifiable",
            f"refusing to anchor a chain that does not verify ({verification.code}: "
            f"{verification.message}); an anchor over a broken chain would attest to "
            f"nothing")
    return AnchorRecord(
        sequence=int(audit_log.head_sequence),
        chain_head_digest=str(audit_log.head_digest),
        controller_version=CONTROLLER_VERSION,
        checkout_key=checkout_key,
        run_id=run_id,
        task_id=task_id,
        checkpoint_id=checkpoint_id,
        records_covered=int(verification.records_checked),
        created_at_utc=to_utc_iso(),
    )


# --------------------------------------------------------------------------
# The exact argv (produced, never run)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class PublishPlan:
    """Everything a future activated controller would need. Nothing executed."""

    branch: str
    remote: str
    file_path: str
    content_sha256: str
    commit_message: str
    argv: tuple[tuple[str, ...], ...]

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["argv"] = [list(a) for a in self.argv]
        data["plan_digest"] = digest_of(data)
        return data


_SAFE_REMOTE = re.compile(r"^[A-Za-z0-9._@:/\-]+$")


def build_publish_plan(anchor: AnchorRecord, *, remote: str = "origin",
                       branch: str = ANCHOR_BRANCH) -> PublishPlan:
    """The exact argv sequence that WOULD publish this anchor. Runs nothing."""
    if branch in FORBIDDEN_ANCHOR_BRANCHES:
        raise AnchorError("forbidden_anchor_branch",
                          f"{branch!r} may never be an anchor target; the anchor branch is a "
                          f"dedicated branch and pushing to main is a hard deny (invariant 8)")
    if not _SAFE_REMOTE.match(remote):
        raise AnchorError("unsafe_remote",
                          f"remote {remote!r} contains characters that are not accepted in a "
                          f"remote name or URL")
    from .models import sha256_hex

    content_digest = sha256_hex(anchor.content_bytes())
    argv = (
        ("git", "--no-pager", "hash-object", "-w", "--stdin"),
        ("git", "--no-pager", "update-index", "--add", "--cacheinfo",
         "100644", "<blob-sha>", anchor.file_path()),
        ("git", "--no-pager", "write-tree"),
        ("git", "--no-pager", "commit-tree", "<tree-sha>", "-p", f"refs/heads/{branch}",
         "-m", anchor.commit_message()),
        ("git", "--no-pager", "update-ref", f"refs/heads/{branch}", "<commit-sha>"),
        ("git", "--no-pager", "push", remote, f"refs/heads/{branch}:refs/heads/{branch}"),
    )
    return PublishPlan(branch, remote, anchor.file_path(), content_digest,
                       anchor.commit_message(), argv)


#: Names whose PRESENCE as a module attribute would mean this module can run
#: something. This is a deny list, in the same spirit as
#: `process.HARD_DENY_ARGUMENTS`: the literals appear here, and only here, so a
#: source-level scan for real execution syntax elsewhere stays meaningful.
EXECUTION_SURFACE_NAMES: tuple[str, ...] = ("subprocess", "Popen", "run", "os", "socket")


def assert_no_execution() -> None:
    """Structural assertion: this module never runs a command (mirrors push_policy)."""
    import sys

    module = sys.modules[__name__]
    for forbidden in EXECUTION_SURFACE_NAMES:
        if hasattr(module, forbidden):
            raise AnchorError(
                "execution_surface_present",
                f"anchor.py exposes {forbidden!r}; Option A is a MECHANISM in this build and "
                f"must have no execution surface at all")


# --------------------------------------------------------------------------
# Activation (both conditions, or nothing)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ActivationStatus:
    active: bool
    credentials_present: bool
    owner_activated: bool
    reason: str
    activation_reference: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


def activation_status(journal: Any, *,
                      credentials_present: bool = False) -> ActivationStatus:
    """Report whether Option A may publish. Both conditions or nothing."""
    record = journal.get_state(ACTIVATION_KEY)
    owner_activated = (isinstance(record, Mapping)
                       and bool(record.get("owner_activated", False))
                       and bool(record.get("directive_reference", "")))
    reference = str(record.get("directive_reference", "")) if isinstance(record, Mapping) \
        else ""
    missing: list[str] = []
    if not credentials_present:
        missing.append("controller-held push credentials do not exist")
    if not owner_activated:
        missing.append("the owner has not performed the explicit activation, recorded "
                       "through directive compliance")
    if missing:
        return ActivationStatus(
            False, credentials_present, owner_activated,
            "Option A anchoring is NOT active: " + "; ".join(missing)
            + ". The anchor content and the exact push argv are produced and stored "
              "locally; nothing has been or will be pushed until both conditions hold",
            reference)
    return ActivationStatus(True, True, True,
                            f"Option A anchoring is active under {reference}", reference)


def assert_activated(status: ActivationStatus) -> None:
    if not status.active:
        raise AnchorError("anchoring_not_activated", status.reason)


def record_anchor(journal: Any, anchor: AnchorRecord, plan: PublishPlan, *,
                  audit: Any = None) -> dict[str, Any]:
    """Store the produced anchor and its plan locally. Publishes nothing."""
    record = {
        "anchor": anchor.to_dict(),
        "anchor_digest": anchor.digest(),
        "publish_plan": plan.to_dict(),
        "published": False,
        "published_reason": "Option A execution is gated on controller credentials AND an "
                            "explicit owner activation; neither is assumed here",
        "recorded_at_utc": to_utc_iso(),
    }
    journal.set_state(LAST_ANCHOR_KEY, record)
    if audit is not None:
        audit.append("audit_anchor_produced",
                     detail={"anchor_digest": record["anchor_digest"],
                             "chain_head_digest": anchor.chain_head_digest,
                             "sequence": anchor.sequence, "published": False})
    return record


def last_anchor(journal: Any) -> dict[str, Any] | None:
    data = journal.get_state(LAST_ANCHOR_KEY)
    return data if isinstance(data, Mapping) else None


def anchor_at_checkpoint(
    *,
    journal: Any,
    audit_log: Any,
    checkout_key: str,
    run_id: str,
    task_id: str,
    checkpoint_id: str,
    remote: str = "origin",
    credentials_present: bool = False,
) -> dict[str, Any]:
    """The per-checkpoint entry point: build, plan, record. Never publishes."""
    anchor = build_anchor(audit_log=audit_log, checkout_key=checkout_key, run_id=run_id,
                          task_id=task_id, checkpoint_id=checkpoint_id)
    plan = build_publish_plan(anchor, remote=remote)
    record = record_anchor(journal, anchor, plan, audit=audit_log)
    record["activation"] = activation_status(
        journal, credentials_present=credentials_present).to_dict()
    return record


def verify_anchor_against_chain(anchor: Mapping[str, Any], audit_log: Any) -> tuple[bool, str]:
    """Check a stored anchor still describes the chain (truncation/rollback detector)."""
    recorded_sequence = int(anchor.get("sequence", -1))
    recorded_digest = str(anchor.get("chain_head_digest", ""))
    current_sequence = int(audit_log.head_sequence)
    if current_sequence < recorded_sequence:
        return False, (f"the audit chain head is at sequence {current_sequence} but an anchor "
                       f"attests to {recorded_sequence}; the log was truncated or rolled back")
    if current_sequence == recorded_sequence and audit_log.head_digest != recorded_digest:
        return False, (f"sequence {recorded_sequence} now has digest "
                       f"{str(audit_log.head_digest)[:16]}..., not the anchored "
                       f"{recorded_digest[:16]}...; the log was rewritten")
    return True, (f"the chain is consistent with the anchor at sequence {recorded_sequence} "
                  f"(head is now {current_sequence})")


def anchor_history_note(anchors: Sequence[Mapping[str, Any]]) -> str:
    """A plain sentence for the owner-facing docs about what anchoring proves today."""
    return (
        f"{len(anchors)} anchor(s) produced locally, 0 published. A locally stored anchor "
        f"detects a rewritten or truncated audit log ON THIS MACHINE. It becomes independent "
        f"tamper evidence only once Option A is activated and the anchors are pushed to "
        f"{ANCHOR_BRANCH}, which requires controller credentials and an explicit owner act."
    )
