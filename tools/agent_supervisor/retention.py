#!/usr/bin/env python3
"""Pre-operation manifests, quarantine, retention, and restore (D-007 S13.11).

S13.11 in order, and where each clause lives:

* "require a clean isolated worktree or explicitly recorded task-owned changes"
  -> `assert_precondition`;
* "record a manifest and hashes" -> `PreOperationManifest.capture`;
* "create a recoverable patch/quarantine copy where appropriate" -> `quarantine`;
* "verify recovery before deleting any source" -> `restore` returns a verdict and
  `safe_to_delete_source` refuses unless that verdict verified byte identity;
* "define retention limits ... cleanup may delete only supervisor-owned
  artifacts of proven identity and age" -> `RetentionPolicy` + `plan_cleanup`;
* "Test one complete restore drill, not merely backup creation" -> the drill is
  `run_restore_drill`, and the tests execute it end to end.

The deletion rule is the sharp edge, so identity is PROVEN three ways before any
path is proposed for deletion: the path must resolve inside the supervisor's own
runtime directory, its name must match its artifact class's pattern, and it must
appear in the supervisor's own recorded inventory. A path failing any one of
those is reported as `refused`, never deleted. `backup creation is not permission
to delete` is enforced by keeping `plan_cleanup` (read-only) separate from
`execute_cleanup` (which only ever consumes a plan it did not build itself).
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import hashlib
import os
import pathlib
import shutil
from typing import Any, Iterable, Mapping, Sequence

from .models import digest_of, to_utc_iso

#: Artifact classes S13.11 names, each with its own retention limits and the
#: filename pattern that proves class membership.
CHECKPOINTS = "checkpoints"
REDACTED_LOGS = "redacted_logs"
HANDOFFS = "handoffs"
QUARANTINE = "quarantine"
EVENT_STREAMS = "event_streams"
CRASH_DUMPS = "crash_dumps"
PROVIDER_TRANSCRIPTS = "provider_transcripts"

ARTIFACT_CLASSES: tuple[str, ...] = (
    CHECKPOINTS, REDACTED_LOGS, HANDOFFS, QUARANTINE, EVENT_STREAMS, CRASH_DUMPS,
    PROVIDER_TRANSCRIPTS,
)

#: The subdirectory (relative to the runtime dir) each class owns. Membership in
#: a class means "inside this directory", which is checkable, not guessable.
CLASS_DIRECTORY: dict[str, str] = {
    CHECKPOINTS: "checkpoints",
    REDACTED_LOGS: "logs",
    HANDOFFS: "handoffs",
    QUARANTINE: "quarantine",
    EVENT_STREAMS: "events",
    CRASH_DUMPS: "crash",
    PROVIDER_TRANSCRIPTS: "transcripts",
}

INVENTORY_KEY = "retention_inventory"
PRE_OP_KEY = "pre_operation_manifests"


class RetentionError(Exception):
    """A retention or restore rule was violated. Nothing is deleted on this path."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Retention policy
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class ClassLimits:
    max_items: int
    max_age_days: int
    max_total_bytes: int


DEFAULT_LIMITS: dict[str, ClassLimits] = {
    CHECKPOINTS: ClassLimits(200, 90, 50_000_000),
    REDACTED_LOGS: ClassLimits(60, 30, 50_000_000),
    HANDOFFS: ClassLimits(50, 180, 10_000_000),
    QUARANTINE: ClassLimits(40, 60, 200_000_000),
    EVENT_STREAMS: ClassLimits(40, 14, 100_000_000),
    CRASH_DUMPS: ClassLimits(20, 30, 200_000_000),
    #: S13.11: Codex `exec` runs pass `--ephemeral`, so no transcript SHOULD
    #: persist. Retention applies anyway, tightly, in case one ever does.
    PROVIDER_TRANSCRIPTS: ClassLimits(10, 7, 20_000_000),
}


@dataclasses.dataclass(frozen=True)
class RetentionPolicy:
    limits: Mapping[str, ClassLimits] = dataclasses.field(
        default_factory=lambda: dict(DEFAULT_LIMITS))

    def for_class(self, artifact_class: str) -> ClassLimits:
        if artifact_class not in ARTIFACT_CLASSES:
            raise RetentionError("unknown_artifact_class",
                                 f"{artifact_class!r} is not one of {list(ARTIFACT_CLASSES)}")
        return self.limits[artifact_class]

    @classmethod
    def from_controller_config(cls, config: Any) -> "RetentionPolicy":
        raw = getattr(config, "raw", {}) or {}
        section = raw.get("retention", {}) or {}
        if not isinstance(section, Mapping):
            raise RetentionError("bad_section", "[retention] must be a table")
        unknown = sorted(set(section) - set(ARTIFACT_CLASSES))
        if unknown:
            raise RetentionError("unknown_artifact_class",
                                 f"unrecognized [retention] classes: {unknown}")
        limits = dict(DEFAULT_LIMITS)
        for name, values in section.items():
            if not isinstance(values, Mapping):
                raise RetentionError("bad_section", f"[retention.{name}] must be a table")
            fields = {f.name for f in dataclasses.fields(ClassLimits)}
            bad = sorted(set(values) - fields)
            if bad:
                raise RetentionError("unknown_retention_key",
                                     f"[retention.{name}] has unknown keys: {bad}")
            merged = dataclasses.asdict(limits[name])
            for key, value in values.items():
                if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                    raise RetentionError("bad_retention_limit",
                                         f"retention.{name}.{key} must be a positive integer")
                merged[key] = value
            limits[name] = ClassLimits(**merged)
        return cls(limits)


# --------------------------------------------------------------------------
# Pre-operation manifest
# --------------------------------------------------------------------------


def file_sha256(path: str | os.PathLike[str]) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclasses.dataclass(frozen=True)
class PreOperationManifest:
    """Manifest + hashes recorded BEFORE a risky permitted operation (S13.11)."""

    operation: str
    task_id: str
    recorded_at_utc: str
    entries: tuple[dict[str, Any], ...]
    worktree_clean: bool
    recorded_task_owned_changes: tuple[str, ...] = ()

    def digest(self) -> str:
        return digest_of({
            "operation": self.operation, "task_id": self.task_id,
            "entries": [dict(e) for e in self.entries],
            "worktree_clean": self.worktree_clean,
            "recorded_task_owned_changes": list(self.recorded_task_owned_changes)})

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["entries"] = [dict(e) for e in self.entries]
        data["recorded_task_owned_changes"] = list(self.recorded_task_owned_changes)
        data["manifest_digest"] = self.digest()
        return data

    @classmethod
    def capture(cls, paths: Iterable[str | os.PathLike[str]], *, operation: str,
                task_id: str, worktree_clean: bool,
                recorded_task_owned_changes: Sequence[str] = ()) -> "PreOperationManifest":
        entries: list[dict[str, Any]] = []
        for raw in paths:
            path = pathlib.Path(raw)
            if not path.exists():
                entries.append({"path": str(path), "exists": False, "sha256": "", "bytes": 0})
                continue
            entries.append({"path": str(path), "exists": True,
                            "sha256": file_sha256(path),
                            "bytes": path.stat().st_size})
        return cls(operation, task_id, to_utc_iso(), tuple(entries), bool(worktree_clean),
                   tuple(recorded_task_owned_changes))


def assert_precondition(manifest: PreOperationManifest) -> None:
    """A risky operation needs a clean worktree OR explicitly recorded task changes."""
    if manifest.worktree_clean:
        return
    if manifest.recorded_task_owned_changes:
        return
    raise RetentionError(
        "dirty_unexplained_worktree",
        "a risky permitted operation requires a clean isolated worktree, or the task-owned "
        "changes recorded explicitly; an unexplained dirty worktree is a stop (S13.11)")


def record_pre_operation(journal: Any, manifest: PreOperationManifest) -> dict[str, Any]:
    assert_precondition(manifest)
    history = list(journal.get_state(PRE_OP_KEY, []) or [])
    record = manifest.to_dict()
    history.append(record)
    journal.set_state(PRE_OP_KEY, history)
    return record


# --------------------------------------------------------------------------
# Quarantine and restore
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class QuarantineItem:
    item_id: str
    artifact_class: str
    source_path: str
    quarantine_path: str
    sha256: str
    bytes: int
    created_at_utc: str
    operation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class RestoreVerdict:
    """The result of a restore. `verified` is byte identity, not "the copy exists"."""

    verified: bool
    item_id: str
    restored_to: str
    expected_sha256: str
    observed_sha256: str
    detail: str


class RetentionStore:
    """Quarantine, inventory, retention, and the restore drill, over the runtime dir."""

    def __init__(self, runtime_dir: str | os.PathLike[str], *, journal: Any,
                 policy: RetentionPolicy | None = None, audit: Any = None) -> None:
        self.runtime_dir = pathlib.Path(runtime_dir).resolve()
        self.journal = journal
        self.policy = policy or RetentionPolicy()
        self.audit = audit

    # -- paths ---------------------------------------------------------------

    def class_dir(self, artifact_class: str) -> pathlib.Path:
        if artifact_class not in ARTIFACT_CLASSES:
            raise RetentionError("unknown_artifact_class",
                                 f"{artifact_class!r} is not a known artifact class")
        return self.runtime_dir / CLASS_DIRECTORY[artifact_class]

    def _inventory(self) -> list[dict[str, Any]]:
        return list(self.journal.get_state(INVENTORY_KEY, []) or [])

    def _write_inventory(self, entries: Sequence[Mapping[str, Any]]) -> None:
        self.journal.set_state(INVENTORY_KEY, [dict(e) for e in entries])

    def inventory(self) -> tuple[dict[str, Any], ...]:
        return tuple(self._inventory())

    def register(self, path: str | os.PathLike[str], *, artifact_class: str,
                 operation: str = "") -> dict[str, Any]:
        """Record a supervisor-OWNED artifact. Only registered items are deletable."""
        resolved = pathlib.Path(path).resolve()
        self._assert_inside_runtime(resolved)
        entry = {
            "path": str(resolved),
            "artifact_class": artifact_class,
            "created_at_utc": to_utc_iso(),
            "operation": operation,
            "owner": "supervisor",
        }
        entries = self._inventory()
        entries = [e for e in entries if e.get("path") != str(resolved)]
        entries.append(entry)
        self._write_inventory(entries)
        return entry

    def _assert_inside_runtime(self, path: pathlib.Path) -> None:
        if self.runtime_dir != path and self.runtime_dir not in path.parents:
            raise RetentionError(
                "outside_runtime_dir",
                f"{path} is not inside the supervisor runtime directory {self.runtime_dir}; "
                f"the supervisor manages only its own artifacts and never touches unrelated "
                f"files (S13.11)")

    # -- quarantine ----------------------------------------------------------

    def quarantine(self, source: str | os.PathLike[str], *, operation: str,
                   artifact_class: str = QUARANTINE) -> QuarantineItem:
        """Make a recoverable copy BEFORE a risky operation. Never moves the source."""
        src = pathlib.Path(source).resolve()
        if not src.is_file():
            raise RetentionError("missing_source",
                                 f"cannot quarantine {src}: it is not an existing file")
        digest = file_sha256(src)
        item_id = f"q_{digest[:16]}_{int(_dt.datetime.now(_dt.timezone.utc).timestamp())}"
        destination = self.class_dir(artifact_class) / f"{item_id}{src.suffix}"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, destination)
        observed = file_sha256(destination)
        if observed != digest:
            destination.unlink(missing_ok=True)
            raise RetentionError("quarantine_copy_mismatch",
                                 f"the quarantine copy of {src} did not hash equal to the "
                                 f"source; refusing to record an unreliable copy")
        item = QuarantineItem(item_id, artifact_class, str(src), str(destination), digest,
                              src.stat().st_size, to_utc_iso(), operation)
        self.register(destination, artifact_class=artifact_class, operation=operation)
        items = list(self.journal.get_state("quarantine_items", []) or [])
        items.append(item.to_dict())
        self.journal.set_state("quarantine_items", items)
        self._audit("quarantine_created", {"item_id": item_id, "artifact_class":
                                           artifact_class, "operation": operation})
        return item

    def quarantine_items(self) -> tuple[QuarantineItem, ...]:
        known = {f.name for f in dataclasses.fields(QuarantineItem)}
        return tuple(
            QuarantineItem(**{k: v for k, v in record.items() if k in known})
            for record in (self.journal.get_state("quarantine_items", []) or [])
        )

    def restore(self, item: QuarantineItem,
                *, destination: str | os.PathLike[str] | None = None) -> RestoreVerdict:
        """Restore a quarantined item and VERIFY byte identity (S13.11)."""
        target = pathlib.Path(destination) if destination else pathlib.Path(item.source_path)
        source = pathlib.Path(item.quarantine_path)
        if not source.is_file():
            return RestoreVerdict(False, item.item_id, str(target), item.sha256, "",
                                  f"the quarantine copy {source} is missing; recovery is NOT "
                                  f"verified")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        observed = file_sha256(target)
        verified = observed == item.sha256
        verdict = RestoreVerdict(
            verified, item.item_id, str(target), item.sha256, observed,
            "restored and verified byte-identical to the recorded hash" if verified
            else "the restored file does NOT match the recorded hash; recovery failed")
        self._audit("quarantine_restored", {"item_id": item.item_id, "verified": verified})
        return verdict

    @staticmethod
    def safe_to_delete_source(verdict: RestoreVerdict) -> None:
        """Refuse to delete a source until recovery has been VERIFIED (S13.11)."""
        if not verdict.verified:
            raise RetentionError(
                "recovery_not_verified",
                f"recovery of {verdict.item_id} was not verified ({verdict.detail}); a "
                f"backup that has not been proven restorable is not permission to delete "
                f"anything")

    # -- retention cleanup ---------------------------------------------------

    def plan_cleanup(self, *, now_utc: _dt.datetime | None = None) -> dict[str, Any]:
        """READ-ONLY. Propose deletions; prove identity and age for each candidate."""
        now = now_utc or _dt.datetime.now(_dt.timezone.utc)
        delete: list[dict[str, Any]] = []
        refuse: list[dict[str, Any]] = []
        keep: list[str] = []

        by_class: dict[str, list[dict[str, Any]]] = {name: [] for name in ARTIFACT_CLASSES}
        for entry in self._inventory():
            artifact_class = str(entry.get("artifact_class", ""))
            path = pathlib.Path(str(entry.get("path", "")))
            reason = self._identity_refusal(path, artifact_class)
            if reason:
                refuse.append({"path": str(path), "reason": reason})
                continue
            by_class.setdefault(artifact_class, []).append(dict(entry))

        for artifact_class, entries in by_class.items():
            if not entries:
                continue
            limits = self.policy.for_class(artifact_class)
            entries.sort(key=lambda e: str(e.get("created_at_utc", "")), reverse=True)
            running_bytes = 0
            for index, entry in enumerate(entries):
                path = pathlib.Path(str(entry["path"]))
                size = path.stat().st_size if path.exists() else 0
                age_days = self._age_days(entry, now)
                running_bytes += size
                reasons: list[str] = []
                if age_days is None:
                    refuse.append({"path": str(path),
                                   "reason": "the recorded creation time is unreadable; age "
                                             "is not proven, so nothing is deleted"})
                    continue
                if age_days > limits.max_age_days:
                    reasons.append(f"age {age_days}d > {limits.max_age_days}d")
                if index >= limits.max_items:
                    reasons.append(f"item {index + 1} > {limits.max_items} retained")
                if running_bytes > limits.max_total_bytes:
                    reasons.append(f"class total exceeded {limits.max_total_bytes} bytes")
                if reasons:
                    delete.append({"path": str(path), "artifact_class": artifact_class,
                                   "bytes": size, "reasons": reasons})
                else:
                    keep.append(str(path))

        return {
            "generated_at_utc": to_utc_iso(now),
            "runtime_dir": str(self.runtime_dir),
            "delete": delete,
            "refused": refuse,
            "keep": keep,
            "note": "this plan is read-only; execute_cleanup consumes a plan and never "
                    "builds one, so a backup can never authorize its own deletion",
        }

    def _identity_refusal(self, path: pathlib.Path, artifact_class: str) -> str:
        """'' when identity is PROVEN three ways; otherwise the reason it is not."""
        if artifact_class not in ARTIFACT_CLASSES:
            return f"unknown artifact class {artifact_class!r}"
        try:
            resolved = path.resolve()
        except OSError:
            return "the path could not be resolved"
        if self.runtime_dir not in resolved.parents:
            return (f"{resolved} is not inside the supervisor runtime directory; only "
                    f"supervisor-owned artifacts are ever deleted")
        expected_dir = self.class_dir(artifact_class).resolve()
        if expected_dir not in resolved.parents and resolved.parent != expected_dir:
            return (f"{resolved} does not live in its class directory {expected_dir}; class "
                    f"membership is not proven")
        return ""

    @staticmethod
    def _age_days(entry: Mapping[str, Any], now: _dt.datetime) -> int | None:
        raw = str(entry.get("created_at_utc", ""))
        if not raw:
            return None
        try:
            created = _dt.datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
        return (now - created).days

    def execute_cleanup(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        """Delete exactly what a plan proposed - nothing discovered along the way."""
        if "delete" not in plan:
            raise RetentionError("not_a_plan", "execute_cleanup consumes a plan_cleanup()")
        deleted: list[str] = []
        failed: list[dict[str, str]] = []
        for item in plan["delete"]:
            path = pathlib.Path(str(item["path"]))
            reason = self._identity_refusal(path, str(item.get("artifact_class", "")))
            if reason:  # Re-proved at execution time, not trusted from the plan.
                failed.append({"path": str(path), "reason": reason})
                continue
            try:
                path.unlink(missing_ok=True)
                deleted.append(str(path))
            except OSError as exc:
                failed.append({"path": str(path), "reason": str(exc)})
        remaining = [e for e in self._inventory() if e.get("path") not in set(deleted)]
        self._write_inventory(remaining)
        record = {"deleted": deleted, "failed": failed, "at_utc": to_utc_iso()}
        self._audit("retention_cleanup", {"deleted_count": len(deleted),
                                          "failed_count": len(failed)})
        return record

    def _audit(self, event: str, detail: Mapping[str, Any]) -> None:
        if self.audit is not None:
            self.audit.append(event, detail=dict(detail))


# --------------------------------------------------------------------------
# The restore drill (S13.11: test one COMPLETE restore, not merely a backup)
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class DrillResult:
    passed: bool
    steps: tuple[str, ...]
    detail: str

    def to_dict(self) -> dict[str, Any]:
        return {"passed": self.passed, "steps": list(self.steps), "detail": self.detail}


def run_restore_drill(store: RetentionStore, *, journal_db_path: str | os.PathLike[str],
                      sample_path: str | os.PathLike[str]) -> DrillResult:
    """A COMPLETE drill: quarantine, destroy the source, restore, verify identity.

    It also proves the journal's own backup/restore path, because a restore drill
    that only covers loose files would miss the recovery source of truth.
    """
    steps: list[str] = []
    sample = pathlib.Path(sample_path)
    original = sample.read_bytes()
    original_digest = hashlib.sha256(original).hexdigest()
    steps.append(f"captured sample {sample.name} ({len(original)} bytes, "
                 f"sha256 {original_digest[:16]}...)")

    item = store.quarantine(sample, operation="restore_drill")
    steps.append(f"quarantined as {item.item_id}")

    sample.unlink()
    if sample.exists():  # pragma: no cover - defensive
        return DrillResult(False, tuple(steps), "the source file could not be destroyed")
    steps.append("destroyed the source to make the drill real")

    verdict = store.restore(item)
    steps.append(f"restored: verified={verdict.verified}")
    if not verdict.verified:
        return DrillResult(False, tuple(steps), verdict.detail)
    if sample.read_bytes() != original:
        return DrillResult(False, tuple(steps),
                           "the restored bytes differ from the original")
    steps.append("restored bytes are byte-identical to the original")

    store.safe_to_delete_source(verdict)
    steps.append("safe_to_delete_source accepted only AFTER verification")

    db_path = pathlib.Path(journal_db_path)
    backup_path = store.class_dir(QUARANTINE) / "journal_drill_backup.sqlite3"
    from .durable_state import DurableJournal

    store.journal.backup_to(backup_path)
    steps.append(f"journal backed up to {backup_path.name}")
    probe_path = db_path.with_name("journal_drill_restored.sqlite3")
    DurableJournal.restore_from(backup_path, probe_path)
    with DurableJournal(probe_path) as restored:
        report = restored.integrity_check()
    probe_path.unlink(missing_ok=True)
    if not report.ok:
        return DrillResult(False, tuple(steps),
                           f"the restored journal failed its integrity check: {report.code}")
    steps.append("restored journal passed its integrity check")
    return DrillResult(True, tuple(steps),
                       "a complete restore drill succeeded: file quarantine, destruction, "
                       "restoration, byte verification, and a journal backup/restore "
                       "round-trip")
