#!/usr/bin/env python3
"""Transactional durable journal and runtime location (D-007 S6, S7, S13.7).

Runtime state, transcripts, locks, handoffs, and logs live OUTSIDE the
repository, keyed by a hash of the CANONICAL FULL CHECKOUT PATH (never the
basename), so two checkouts of the same repository can never share state:

    Windows : %LOCALAPPDATA%\\NYCBuildabilitySupervisor\\<sha256-of-checkout-path>\\
    POSIX   : $XDG_STATE_HOME (or ~/.local/state)/NYCBuildabilitySupervisor/<sha256>/

The POSIX branch is a documented deviation from S6's Windows-only wording: the
directive targets Windows, but the repository's CI runs on Linux and the tests
must execute there. Production remains the Windows path.

The journal itself is standard-library SQLite configured for durability
(`journal_mode=WAL`, `synchronous=FULL`), with transactional schema versioning,
a startup integrity check, before/after external-effect records, and a tested
backup/restore path.

Recovery discipline (S6/S7): an unreadable, rolled-back, partially migrated, or
integrity-failing journal is REJECTED, never guessed at. `IntegrityReport` names
the exact failure so the operator sees why the controller refused to continue.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import pathlib
import shutil
import sqlite3
from typing import Any, Iterable

from .models import (
    EFFECT_CONFIRMED,
    EFFECT_FAILED,
    EFFECT_PENDING,
    EffectRecord,
    QueuedAsk,
    TransitionRecord,
    canonical_json,
    to_utc_iso,
)

#: Bump ONLY together with a migration in `_MIGRATIONS`.
JOURNAL_SCHEMA_VERSION = 1

APP_DIR_NAME = "NYCBuildabilitySupervisor"
DB_FILENAME = "supervisor_journal.sqlite3"

#: Folder names that indicate a cloud-synced or network location. S6 requires the
#: authoritative database to live on a local filesystem.
CLOUD_SYNC_MARKERS = ("onedrive", "dropbox", "google drive", "googledrive", "icloud", "box sync")


class JournalError(Exception):
    """The journal is unusable. Recovery must stop rather than guess."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# Runtime location
# --------------------------------------------------------------------------


def canonical_checkout_path(checkout: str | os.PathLike[str]) -> str:
    """Absolute, resolved, case-normalized checkout path (the hashing input)."""
    return os.path.normcase(str(pathlib.Path(checkout).resolve()))


def checkout_key(checkout: str | os.PathLike[str]) -> str:
    """SHA-256 of the canonical full checkout path (S6: never the basename)."""
    return hashlib.sha256(canonical_checkout_path(checkout).encode("utf-8")).hexdigest()


def runtime_base_dir() -> pathlib.Path:
    """The per-user application directory holding every checkout's runtime state."""
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            raise JournalError("no_localappdata",
                               "LOCALAPPDATA is not set; cannot locate the runtime directory")
        return pathlib.Path(local) / APP_DIR_NAME
    state_home = os.environ.get("XDG_STATE_HOME")
    base = pathlib.Path(state_home) if state_home else pathlib.Path.home() / ".local" / "state"
    return base / APP_DIR_NAME


def runtime_dir_for(
    checkout: str | os.PathLike[str],
    *,
    base: str | os.PathLike[str] | None = None,
) -> pathlib.Path:
    """Runtime directory for one checkout. Refuses any location inside the checkout.

    `base` exists for tests, which point it at a temp directory. Production never
    passes it; the default resolves to %LOCALAPPDATA% (or the POSIX equivalent).
    """
    base_dir = pathlib.Path(base) if base is not None else runtime_base_dir()
    target = (base_dir / checkout_key(checkout)).resolve()
    checkout_resolved = pathlib.Path(checkout).resolve()
    if target == checkout_resolved or checkout_resolved in target.parents:
        raise JournalError(
            "runtime_dir_inside_repo",
            f"runtime directory {target} is inside the checkout {checkout_resolved}; "
            f"supervisor runtime state must never live in the repository")
    return target


def looks_cloud_synced(path: str | os.PathLike[str]) -> bool:
    """True when the path appears to sit in a cloud-synced folder (S6 warning)."""
    lowered = str(path).lower()
    return any(marker in lowered for marker in CLOUD_SYNC_MARKERS)


# --------------------------------------------------------------------------
# Schema
# --------------------------------------------------------------------------

_MIGRATIONS: dict[int, tuple[str, ...]] = {
    1: (
        """
        CREATE TABLE IF NOT EXISTS schema_meta (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS state_kv (
            key             TEXT PRIMARY KEY,
            value           TEXT NOT NULL,
            updated_at_utc  TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS transitions (
            sequence         INTEGER PRIMARY KEY,
            state_from       TEXT NOT NULL,
            state_to         TEXT NOT NULL,
            trigger          TEXT NOT NULL,
            run_id           TEXT NOT NULL,
            committed_at_utc TEXT NOT NULL,
            detail           TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS effects (
            action_id            TEXT PRIMARY KEY,
            effect_type          TEXT NOT NULL,
            target               TEXT NOT NULL,
            expected_prior_state TEXT NOT NULL,
            request_digest       TEXT NOT NULL,
            status               TEXT NOT NULL,
            created_at_utc       TEXT NOT NULL,
            completed_at_utc     TEXT NOT NULL DEFAULT '',
            resulting_state      TEXT NOT NULL DEFAULT '',
            reconciliation       TEXT NOT NULL DEFAULT ''
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS outbox (
            message_id     TEXT PRIMARY KEY,
            envelope       TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            sent_at_utc    TEXT NOT NULL DEFAULT ''
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS inbox (
            message_id      TEXT PRIMARY KEY,
            envelope_digest TEXT NOT NULL,
            received_at_utc TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS queued_asks (
            ask_id          TEXT PRIMARY KEY,
            run_id          TEXT NOT NULL,
            task_id         TEXT NOT NULL,
            question        TEXT NOT NULL,
            request_digest  TEXT NOT NULL,
            created_at_utc  TEXT NOT NULL,
            classification  TEXT NOT NULL DEFAULT 'unclassified',
            answered_at_utc TEXT NOT NULL DEFAULT '',
            answer          TEXT NOT NULL DEFAULT ''
        )
        """,
    ),
}

_REQUIRED_TABLES = (
    "schema_meta", "state_kv", "transitions", "effects", "outbox", "inbox", "queued_asks",
)


@dataclasses.dataclass(frozen=True)
class IntegrityReport:
    ok: bool
    schema_version: int
    checks: tuple[str, ...] = ()
    code: str = ""
    message: str = ""


# --------------------------------------------------------------------------
# Journal
# --------------------------------------------------------------------------


class DurableJournal:
    """Transactional SQLite journal. Open it, check integrity, then use it."""

    def __init__(self, db_path: str | os.PathLike[str]) -> None:
        self.db_path = pathlib.Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None

    # -- lifecycle -----------------------------------------------------------

    def open(self) -> "DurableJournal":
        try:
            conn = sqlite3.connect(str(self.db_path), isolation_level=None, timeout=30.0)
            conn.row_factory = sqlite3.Row
            # Adopt the connection BEFORE the first statement so a failure below is
            # still closed by `close()` and never leaks an open file handle.
            self._conn = conn
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=FULL")
            conn.execute("PRAGMA foreign_keys=ON")
            self._migrate()
        except sqlite3.DatabaseError as exc:
            # A corrupt or non-database file must surface as a journal failure, not
            # as a raw driver error: recovery rejects an unreadable journal (S6).
            self.close()
            raise JournalError("unreadable_database",
                               f"journal at {self.db_path} could not be opened: {exc}") from exc
        return self

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> "DurableJournal":
        return self.open()

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            raise JournalError("not_open", "journal is not open")
        return self._conn

    # -- schema --------------------------------------------------------------

    def _migrate(self) -> None:
        """Apply migrations inside ONE transaction, guarded by a progress flag."""
        conn = self.conn
        conn.execute("""CREATE TABLE IF NOT EXISTS schema_meta (
                            key TEXT PRIMARY KEY, value TEXT NOT NULL)""")
        current = int(self._meta_get("schema_version", "0"))
        if self._meta_get("migration_in_progress", "") == "1":
            raise JournalError(
                "partial_migration",
                "a previous schema migration did not complete; the journal is partially "
                "migrated and must not be used")
        if current > JOURNAL_SCHEMA_VERSION:
            raise JournalError(
                "downgraded_schema",
                f"journal schema version {current} is newer than this controller's "
                f"{JOURNAL_SCHEMA_VERSION}; refusing to downgrade")
        if current == JOURNAL_SCHEMA_VERSION:
            return

        conn.execute("BEGIN IMMEDIATE")
        try:
            self._meta_set_locked("migration_in_progress", "1")
            for version in range(current + 1, JOURNAL_SCHEMA_VERSION + 1):
                for statement in _MIGRATIONS[version]:
                    conn.execute(statement)
            self._meta_set_locked("schema_version", str(JOURNAL_SCHEMA_VERSION))
            self._meta_set_locked("high_water_sequence",
                                  self._meta_get("high_water_sequence", "0"))
            self._meta_set_locked("migration_in_progress", "0")
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise

    def _meta_get(self, key: str, default: str = "") -> str:
        row = self.conn.execute("SELECT value FROM schema_meta WHERE key = ?",
                                (key,)).fetchone()
        return row["value"] if row else default

    def _meta_set_locked(self, key: str, value: str) -> None:
        self.conn.execute(
            "INSERT INTO schema_meta(key, value) VALUES(?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value", (key, value))

    def _meta_set(self, key: str, value: str) -> None:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self._meta_set_locked(key, value)
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    # -- integrity -----------------------------------------------------------

    def integrity_check(self) -> IntegrityReport:
        """Startup integrity check (S6). Fails closed with a named reason."""
        checks: list[str] = []
        try:
            row = self.conn.execute("PRAGMA integrity_check").fetchone()
        except sqlite3.DatabaseError as exc:
            return IntegrityReport(False, -1, tuple(checks), "unreadable_database", str(exc))
        result = row[0] if row else "unknown"
        if result != "ok":
            return IntegrityReport(False, -1, tuple(checks), "sqlite_integrity_failed",
                                   f"PRAGMA integrity_check returned {result!r}")
        checks.append("sqlite_integrity=ok")

        version = int(self._meta_get("schema_version", "0"))
        if version != JOURNAL_SCHEMA_VERSION:
            return IntegrityReport(False, version, tuple(checks), "schema_version_mismatch",
                                   f"journal schema {version}, controller expects "
                                   f"{JOURNAL_SCHEMA_VERSION}")
        checks.append(f"schema_version={version}")

        if self._meta_get("migration_in_progress", "0") == "1":
            return IntegrityReport(False, version, tuple(checks), "partial_migration",
                                   "migration_in_progress flag is set")

        present = {
            row["name"] for row in
            self.conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
        missing = sorted(set(_REQUIRED_TABLES) - present)
        if missing:
            return IntegrityReport(False, version, tuple(checks), "missing_tables",
                                   f"journal is missing tables: {missing}")
        checks.append(f"tables={len(_REQUIRED_TABLES)}")

        high_water = int(self._meta_get("high_water_sequence", "0"))
        row = self.conn.execute("SELECT MAX(sequence) AS m FROM transitions").fetchone()
        observed = int(row["m"] or 0)
        if observed < high_water:
            return IntegrityReport(
                False, version, tuple(checks), "rolled_back",
                f"transitions end at sequence {observed} but the recorded high-water mark is "
                f"{high_water}; the journal was rolled back and must not be trusted")
        checks.append(f"transitions={observed}")
        return IntegrityReport(True, version, tuple(checks))

    def require_healthy(self) -> IntegrityReport:
        report = self.integrity_check()
        if not report.ok:
            raise JournalError(report.code, report.message)
        return report

    # -- key/value durable record (S7 field set) -----------------------------

    def set_state(self, key: str, value: Any) -> None:
        payload = canonical_json(value).decode("utf-8")
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "INSERT INTO state_kv(key, value, updated_at_utc) VALUES(?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
                "updated_at_utc = excluded.updated_at_utc",
                (key, payload, to_utc_iso()))
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def get_state(self, key: str, default: Any = None) -> Any:
        row = self.conn.execute("SELECT value FROM state_kv WHERE key = ?", (key,)).fetchone()
        if row is None:
            return default
        return json.loads(row["value"])

    def all_state(self) -> dict[str, Any]:
        return {
            row["key"]: json.loads(row["value"])
            for row in self.conn.execute("SELECT key, value FROM state_kv ORDER BY key")
        }

    # -- transitions ---------------------------------------------------------

    def next_transition_sequence(self) -> int:
        row = self.conn.execute("SELECT MAX(sequence) AS m FROM transitions").fetchone()
        return int(row["m"] or 0) + 1

    def record_transition(
        self,
        *,
        state_from: str,
        state_to: str,
        trigger: str,
        run_id: str,
        detail: dict[str, Any] | None = None,
        state_updates: dict[str, Any] | None = None,
    ) -> TransitionRecord:
        """Commit a transition and any state updates in ONE transaction.

        S7 requires the commit to happen and be durably flushed BEFORE the next
        side effect, which is why this returns only after COMMIT.
        """
        sequence = self.next_transition_sequence()
        record = TransitionRecord(
            sequence=sequence,
            state_from=state_from,
            state_to=state_to,
            trigger=trigger,
            run_id=run_id,
            committed_at_utc=to_utc_iso(),
            detail=detail or {},
        )
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "INSERT INTO transitions(sequence, state_from, state_to, trigger, run_id, "
                "committed_at_utc, detail) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (record.sequence, record.state_from, record.state_to, record.trigger,
                 record.run_id, record.committed_at_utc,
                 canonical_json(record.detail).decode("utf-8")))
            self._meta_set_locked("high_water_sequence", str(sequence))
            for key, value in (state_updates or {}).items():
                self.conn.execute(
                    "INSERT INTO state_kv(key, value, updated_at_utc) VALUES(?, ?, ?) "
                    "ON CONFLICT(key) DO UPDATE SET value = excluded.value, "
                    "updated_at_utc = excluded.updated_at_utc",
                    (key, canonical_json(value).decode("utf-8"), record.committed_at_utc))
            self.conn.execute("COMMIT")
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        return record

    def last_transition(self) -> TransitionRecord | None:
        row = self.conn.execute(
            "SELECT * FROM transitions ORDER BY sequence DESC LIMIT 1").fetchone()
        if row is None:
            return None
        return TransitionRecord(
            sequence=row["sequence"], state_from=row["state_from"], state_to=row["state_to"],
            trigger=row["trigger"], run_id=row["run_id"],
            committed_at_utc=row["committed_at_utc"], detail=json.loads(row["detail"]))

    def transitions(self) -> list[TransitionRecord]:
        return [
            TransitionRecord(
                sequence=row["sequence"], state_from=row["state_from"],
                state_to=row["state_to"], trigger=row["trigger"], run_id=row["run_id"],
                committed_at_utc=row["committed_at_utc"], detail=json.loads(row["detail"]))
            for row in self.conn.execute("SELECT * FROM transitions ORDER BY sequence")
        ]

    # -- external effects (S6 before/after, S13.7 exactly-once) --------------

    def record_before_effect(
        self,
        *,
        action_id: str,
        effect_type: str,
        target: str,
        expected_prior_state: str,
        request_digest: str,
    ) -> EffectRecord:
        """Journal an effect BEFORE performing it. Duplicate action ids are refused."""
        record = EffectRecord(
            action_id=action_id, effect_type=effect_type, target=target,
            expected_prior_state=expected_prior_state, request_digest=request_digest,
            status=EFFECT_PENDING, created_at_utc=to_utc_iso())
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "INSERT INTO effects(action_id, effect_type, target, expected_prior_state, "
                "request_digest, status, created_at_utc) VALUES(?, ?, ?, ?, ?, ?, ?)",
                (record.action_id, record.effect_type, record.target,
                 record.expected_prior_state, record.request_digest, record.status,
                 record.created_at_utc))
            self.conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            self.conn.execute("ROLLBACK")
            raise JournalError(
                "duplicate_action_id",
                f"action_id {action_id!r} already exists; an idempotency key is never "
                f"reused") from exc
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        return record

    def record_after_effect(
        self,
        action_id: str,
        *,
        resulting_state: str,
        status: str = EFFECT_CONFIRMED,
        reconciliation: str = "",
    ) -> EffectRecord:
        """Journal the VERIFIED result of an effect (S6: only after verification)."""
        if status not in (EFFECT_CONFIRMED, EFFECT_FAILED):
            raise JournalError("bad_effect_status", f"unexpected status {status!r}")
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            cursor = self.conn.execute(
                "UPDATE effects SET status = ?, resulting_state = ?, completed_at_utc = ?, "
                "reconciliation = ? WHERE action_id = ? AND status = ?",
                (status, resulting_state, to_utc_iso(), reconciliation, action_id,
                 EFFECT_PENDING))
            if cursor.rowcount != 1:
                self.conn.execute("ROLLBACK")
                raise JournalError(
                    "no_pending_effect",
                    f"no PENDING effect with action_id {action_id!r}; refusing to invent an "
                    f"after-effect record")
            self.conn.execute("COMMIT")
        except JournalError:
            raise
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
        return self.get_effect(action_id)  # type: ignore[return-value]

    def get_effect(self, action_id: str) -> EffectRecord | None:
        row = self.conn.execute("SELECT * FROM effects WHERE action_id = ?",
                                (action_id,)).fetchone()
        return self._effect_from_row(row) if row else None

    def pending_effects(self) -> list[EffectRecord]:
        """Effects with no verified after-effect: S11.5 AMBIGUOUS_EFFECT candidates."""
        return [
            self._effect_from_row(row) for row in
            self.conn.execute("SELECT * FROM effects WHERE status = ? ORDER BY created_at_utc",
                              (EFFECT_PENDING,))
        ]

    @staticmethod
    def _effect_from_row(row: sqlite3.Row) -> EffectRecord:
        return EffectRecord(
            action_id=row["action_id"], effect_type=row["effect_type"], target=row["target"],
            expected_prior_state=row["expected_prior_state"],
            request_digest=row["request_digest"], status=row["status"],
            created_at_utc=row["created_at_utc"], completed_at_utc=row["completed_at_utc"],
            resulting_state=row["resulting_state"], reconciliation=row["reconciliation"])

    # -- transactional outbox / inbox (S8.5) ---------------------------------

    def enqueue_outbound(self, message_id: str, envelope: dict[str, Any]) -> None:
        """Persist an outbound message BEFORE sending it (S8.5)."""
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(
                "INSERT INTO outbox(message_id, envelope, created_at_utc) VALUES(?, ?, ?)",
                (message_id, canonical_json(envelope).decode("utf-8"), to_utc_iso()))
            self.conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            self.conn.execute("ROLLBACK")
            raise JournalError("duplicate_outbound",
                               f"message_id {message_id!r} is already in the outbox") from exc
        except Exception:
            self.conn.execute("ROLLBACK")
            raise

    def mark_sent(self, message_id: str) -> None:
        self._simple_write("UPDATE outbox SET sent_at_utc = ? WHERE message_id = ?",
                           (to_utc_iso(), message_id))

    def unsent_outbound(self) -> list[dict[str, Any]]:
        return [
            json.loads(row["envelope"]) for row in
            self.conn.execute("SELECT envelope FROM outbox WHERE sent_at_utc = '' "
                              "ORDER BY created_at_utc")
        ]

    def record_inbound(self, message_id: str, envelope_digest: str) -> bool:
        """Record an inbound message id. Returns False when it was already seen."""
        try:
            self._simple_write(
                "INSERT INTO inbox(message_id, envelope_digest, received_at_utc) "
                "VALUES(?, ?, ?)", (message_id, envelope_digest, to_utc_iso()))
            return True
        except JournalError as exc:
            if exc.code == "constraint":
                return False
            raise

    # -- queued ASK items (S4.3) ---------------------------------------------

    def queue_ask(self, ask: QueuedAsk) -> None:
        self._simple_write(
            "INSERT INTO queued_asks(ask_id, run_id, task_id, question, request_digest, "
            "created_at_utc, classification) VALUES(?, ?, ?, ?, ?, ?, ?)",
            (ask.ask_id, ask.run_id, ask.task_id, ask.question, ask.request_digest,
             ask.created_at_utc, ask.classification))

    def open_asks(self) -> list[QueuedAsk]:
        return [
            QueuedAsk(
                ask_id=row["ask_id"], run_id=row["run_id"], task_id=row["task_id"],
                question=row["question"], request_digest=row["request_digest"],
                created_at_utc=row["created_at_utc"], classification=row["classification"],
                answered_at_utc=row["answered_at_utc"], answer=row["answer"])
            for row in self.conn.execute(
                "SELECT * FROM queued_asks WHERE answered_at_utc = '' ORDER BY created_at_utc")
        ]

    # -- backup / restore (S6, S13.11) ---------------------------------------

    def backup_to(self, destination: str | os.PathLike[str]) -> pathlib.Path:
        """Consistent online backup using SQLite's backup API."""
        dest = pathlib.Path(destination)
        dest.parent.mkdir(parents=True, exist_ok=True)
        target = sqlite3.connect(str(dest))
        try:
            self.conn.backup(target)
        finally:
            target.close()
        return dest

    @staticmethod
    def restore_from(backup_path: str | os.PathLike[str],
                     db_path: str | os.PathLike[str]) -> None:
        """Restore a backup over the journal. The caller must have it CLOSED."""
        source = pathlib.Path(backup_path)
        if not source.exists():
            raise JournalError("missing_backup", f"backup not found: {source}")
        target = pathlib.Path(db_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        for suffix in ("-wal", "-shm"):
            stale = pathlib.Path(str(target) + suffix)
            if stale.exists():
                stale.unlink()
        shutil.copyfile(source, target)

    # -- helper --------------------------------------------------------------

    def _simple_write(self, sql: str, params: Iterable[Any]) -> None:
        self.conn.execute("BEGIN IMMEDIATE")
        try:
            self.conn.execute(sql, tuple(params))
            self.conn.execute("COMMIT")
        except sqlite3.IntegrityError as exc:
            self.conn.execute("ROLLBACK")
            raise JournalError("constraint", str(exc)) from exc
        except Exception:
            self.conn.execute("ROLLBACK")
            raise
