#!/usr/bin/env python3
"""Crash-safe index cache generations (M0-T063 Unit A1, D-013-R031/R035/R036).

Cache generations live OUTSIDE the worktree, under the accepted per-checkout
LOCALAPPDATA namespace (keyed by the canonical-path sha256, reused from the
supervisor's durable_state - never the basename; D-013-R031/R078). This module
owns only the STORAGE contract; what a generation contains is the caller's
payload (the code-graph index in A2).

Crash-safety contract (D-013-R035/R036):
  * a generation is written to a TEMP directory, VALIDATED against its own
    recorded content digest, then ATOMICALLY promoted (os.replace of the
    directory) and only then does the `current` pointer advance;
  * a crash at any point leaves either the prior valid generation or a complete
    new one - never a half-index visible as current;
  * an incomplete/temp generation found on open is QUARANTINED with a reason,
    and the prior valid generation stays loadable;
  * a single-writer lock (atomic mkdir) prevents concurrent writers; a stale
    lock (dead pid / aged past the timeout) is reclaimed, recorded.

Nothing here trusts mtime for content decisions; mtime is used only for
operational lock-staleness, never as proof a generation is unchanged.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import pathlib
import shutil
import sys
import time
from typing import Any

_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from tools.agent_supervisor.durable_state import checkout_key  # noqa: E402

APP_DIR_NAME = "NYCBuildabilityContextIndex"
CACHE_FORMAT_VERSION = 1
LOCK_STALE_SECONDS = 900  # a lock older than this whose pid is dead is reclaimable


class CacheError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            import ctypes
            h = ctypes.windll.kernel32.OpenProcess(0x1000, False, pid)
            if h:
                ctypes.windll.kernel32.CloseHandle(h)
                return True
            return False
        os.kill(pid, 0)
        return True
    except (OSError, ValueError):
        return False


def _temp_owner_alive(temp_name: str) -> bool:
    """A temp generation is named `<fingerprint>.<pid>`; True if that pid lives."""
    try:
        return _pid_alive(int(temp_name.rsplit(".", 1)[-1]))
    except (ValueError, IndexError):
        return False


def _content_digest(payload: dict[str, Any]) -> str:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")
    h = hashlib.sha256()
    h.update(b"index_generation\x00")
    h.update(len(body).to_bytes(8, "big"))
    h.update(body)
    return h.hexdigest()


def rotate_jsonl_if_needed(path: str | os.PathLike[str], *,
                           max_bytes: int = 1_000_000, keep: int = 1) -> bool:
    """Bounded/rotated retention for an append-only JSONL log (D-018-R036).

    When the live file reaches `max_bytes` it is rotated to `<name>.1`
    (older rotations shift up; anything beyond `keep` rotations is dropped),
    so external telemetry/routing records stay bounded while recent history
    survives. Returns True when a rotation happened. Best-effort: an OSError
    never breaks the caller (telemetry must not fail a build)."""
    p = pathlib.Path(path)
    try:
        if not p.exists() or p.stat().st_size < max_bytes:
            return False
        for i in range(keep, 0, -1):
            newer = p if i == 1 else pathlib.Path(f"{p}.{i - 1}")
            older = pathlib.Path(f"{p}.{i}")
            if newer.exists():
                os.replace(newer, older)
        return True
    except OSError:
        return False


def append_jsonl_rotated(path: str | os.PathLike[str], record: dict, *,
                         max_bytes: int = 1_000_000, keep: int = 1) -> None:
    """Rotate-then-append one JSON record (shared R036 retention helper)."""
    p = pathlib.Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    rotate_jsonl_if_needed(p, max_bytes=max_bytes, keep=keep)
    with p.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(record, sort_keys=True) + "\n")


def cache_base_dir() -> pathlib.Path:
    if os.name == "nt":
        local = os.environ.get("LOCALAPPDATA")
        if not local:
            raise CacheError("no_localappdata",
                             "LOCALAPPDATA is not set; cannot locate the cache")
        return pathlib.Path(local) / APP_DIR_NAME
    state_home = os.environ.get("XDG_STATE_HOME")
    base = pathlib.Path(state_home) if state_home else pathlib.Path.home() / ".local" / "state"
    return base / APP_DIR_NAME


def cache_dir_for(checkout: str | os.PathLike[str], *,
                  base: str | os.PathLike[str] | None = None) -> pathlib.Path:
    """Per-checkout cache directory. Refuses any location inside the checkout."""
    base_dir = pathlib.Path(base) if base is not None else cache_base_dir()
    target = (base_dir / checkout_key(checkout)).resolve()
    checkout_resolved = pathlib.Path(checkout).resolve()
    if target == checkout_resolved or checkout_resolved in target.parents:
        raise CacheError("cache_inside_repo",
                         f"cache dir {target} is inside the checkout {checkout_resolved}; "
                         f"index cache must never live in the repository")
    return target


@dataclasses.dataclass(frozen=True)
class Generation:
    fingerprint: str
    content_digest: str
    path: pathlib.Path

    def load_payload(self) -> dict[str, Any]:
        data = json.loads((self.path / "payload.json").read_text(encoding="utf-8"))
        return data


class SingleWriterLock:
    """Atomic-mkdir lock. Reclaims a lock whose recorded pid is dead and whose
    age exceeds LOCK_STALE_SECONDS; records the reclaim."""

    def __init__(self, cache_dir: pathlib.Path) -> None:
        self.lock_path = cache_dir / "writer.lock"
        self._held = False

    def _pid_alive(self, pid: int) -> bool:
        return _pid_alive(pid)

    def acquire(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.lock_path.mkdir()
        except FileExistsError:
            meta = self._read_meta()
            aged = (time.time() - meta.get("acquired_at", 0)) > LOCK_STALE_SECONDS
            if aged and not self._pid_alive(int(meta.get("pid", -1))):
                shutil.rmtree(self.lock_path, ignore_errors=True)
                self.lock_path.mkdir()  # reclaim
            else:
                raise CacheError("concurrent_writer",
                                 f"another writer holds {self.lock_path} "
                                 f"(pid {meta.get('pid')})")
        (self.lock_path / "owner.json").write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": time.time()}),
            encoding="utf-8")
        self._held = True

    def _read_meta(self) -> dict[str, Any]:
        try:
            return json.loads((self.lock_path / "owner.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return {}

    def release(self) -> None:
        if self._held:
            shutil.rmtree(self.lock_path, ignore_errors=True)
            self._held = False

    def __enter__(self) -> "SingleWriterLock":
        self.acquire()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.release()


class IndexCache:
    """The generation store for one checkout."""

    def __init__(self, checkout: str | os.PathLike[str], *,
                 base: str | os.PathLike[str] | None = None) -> None:
        self.checkout = pathlib.Path(checkout).resolve()
        self.root = cache_dir_for(self.checkout, base=base)
        self.generations_dir = self.root / "generations"
        self.tmp_dir = self.root / "tmp"
        self.quarantine_dir = self.root / "quarantine"
        self.current_pointer = self.root / "current.json"

    def _ensure_dirs(self) -> None:
        for d in (self.generations_dir, self.tmp_dir, self.quarantine_dir):
            d.mkdir(parents=True, exist_ok=True)

    # -- recovery ---------------------------------------------------------
    def recover(self) -> list[str]:
        """Quarantine any incomplete temp generation; return quarantine reasons.
        Idempotent and safe to call on every open (D-013-R036)."""
        self._ensure_dirs()
        quarantined: list[str] = []
        for tmp in sorted(self.tmp_dir.glob("*")):
            if tmp.is_dir():
                # MINOR-2 (G3 review): a temp generation is named `<fp>.<pid>`.
                # If that pid is a LIVE process, the write is still in progress -
                # never yank it out from under an active writer (a concurrent
                # reader's recover() would otherwise abort a healthy write). Only
                # an orphan (dead-pid) temp generation is quarantined.
                if _temp_owner_alive(tmp.name):
                    continue
                dest = self.quarantine_dir / f"{tmp.name}.incomplete"
                shutil.rmtree(dest, ignore_errors=True)
                shutil.move(str(tmp), str(dest))
                (dest / "quarantine_reason.json").write_text(
                    json.dumps({"reason": "incomplete_temp_generation",
                                "recovered": True}), encoding="utf-8")
                quarantined.append(f"{tmp.name}:incomplete_temp_generation")
        # A promoted generation whose digest no longer matches its payload is
        # corrupt -> quarantine it (never load a half/edited index).
        for gen in sorted(self.generations_dir.glob("*")):
            if not gen.is_dir():
                continue
            if not self._generation_valid(gen):
                dest = self.quarantine_dir / f"{gen.name}.corrupt"
                shutil.rmtree(dest, ignore_errors=True)
                shutil.move(str(gen), str(dest))
                quarantined.append(f"{gen.name}:corrupt_generation")
        return quarantined

    def _generation_valid(self, gen: pathlib.Path) -> bool:
        try:
            meta = json.loads((gen / "meta.json").read_text(encoding="utf-8"))
            payload = json.loads((gen / "payload.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return False
        if meta.get("cache_format_version") != CACHE_FORMAT_VERSION:
            return False
        return meta.get("content_digest") == _content_digest(payload)

    # -- write ------------------------------------------------------------
    def write_generation(self, fingerprint: str, payload: dict[str, Any]) -> Generation:
        """Write, validate, atomically promote, then advance `current`.

        Reuses an existing valid generation for the same fingerprint (idempotent
        retry; D-013-R036). A crash before the final os.replace leaves the temp
        dir, which the next recover() quarantines - current never points at it.
        """
        self._ensure_dirs()
        self.recover()
        with SingleWriterLock(self.root):
            return self.write_generation_locked(fingerprint, payload)

    def write_generation_locked(self, fingerprint: str,
                                payload: dict[str, Any]) -> Generation:
        """Write/validate/promote WITHOUT acquiring the writer lock.

        The caller MUST already hold this store's SingleWriterLock — this
        exists so a transaction can cover load-current → conflict check →
        mutation → validation → promotion in ONE protected span
        (M0-T075 / D-018-R027); calling it unlocked forfeits that guarantee.
        """
        self._ensure_dirs()
        existing = self.generations_dir / fingerprint
        if existing.is_dir() and self._generation_valid(existing):
            self._set_current(fingerprint)
            return Generation(fingerprint, _content_digest(payload), existing)
        digest = _content_digest(payload)
        tmp = self.tmp_dir / f"{fingerprint}.{os.getpid()}"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        (tmp / "payload.json").write_text(
            json.dumps(payload, sort_keys=True, separators=(",", ":")),
            encoding="utf-8")
        (tmp / "meta.json").write_text(json.dumps({
            "cache_format_version": CACHE_FORMAT_VERSION,
            "fingerprint": fingerprint,
            "content_digest": digest,
        }, sort_keys=True), encoding="utf-8")
        # VALIDATE before promotion.
        if not self._generation_valid(tmp):
            shutil.rmtree(tmp, ignore_errors=True)
            raise CacheError("validation_failed",
                             "generation failed self-validation before promotion")
        # ATOMIC promotion: replace the target directory in one operation.
        if existing.exists():
            shutil.rmtree(existing, ignore_errors=True)
        os.replace(tmp, existing)
        self._set_current(fingerprint)
        return Generation(fingerprint, digest, existing)

    def _set_current(self, fingerprint: str) -> None:
        tmp = self.current_pointer.with_suffix(".json.tmp")
        tmp.write_text(json.dumps({"fingerprint": fingerprint,
                                   "cache_format_version": CACHE_FORMAT_VERSION}),
                       encoding="utf-8")
        os.replace(tmp, self.current_pointer)

    # -- read -------------------------------------------------------------
    def load_current(self) -> Generation | None:
        """The current valid generation, or None. Runs recovery first so a
        half-written or corrupt generation can never be returned as current."""
        self.recover()
        if not self.current_pointer.exists():
            return None
        try:
            ptr = json.loads(self.current_pointer.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        gen = self.generations_dir / ptr.get("fingerprint", "")
        if gen.is_dir() and self._generation_valid(gen):
            payload = json.loads((gen / "payload.json").read_text(encoding="utf-8"))
            return Generation(ptr["fingerprint"], _content_digest(payload), gen)
        return None

    def load_fingerprint(self, fingerprint: str) -> Generation | None:
        gen = self.generations_dir / fingerprint
        if gen.is_dir() and self._generation_valid(gen):
            payload = json.loads((gen / "payload.json").read_text(encoding="utf-8"))
            return Generation(fingerprint, _content_digest(payload), gen)
        return None

    # -- retention --------------------------------------------------------
    def prune(self, keep: int = 3) -> list[str]:
        """Keep the `keep` most-recently-modified valid generations plus the
        current one; return the fingerprints pruned. Bounded retention keeps a
        prior valid generation available for rollback (D-013-R071).

        Serialized under the single-writer lock (M0-T075, D-018-R035): pruning
        while another writer promotes raises `concurrent_writer` instead of
        racing it; callers treat that as skip-this-round."""
        with SingleWriterLock(self.root):
            return self._prune_locked(keep)

    def _prune_locked(self, keep: int) -> list[str]:
        self._ensure_dirs()
        current = None
        if self.current_pointer.exists():
            try:
                current = json.loads(
                    self.current_pointer.read_text(encoding="utf-8")).get("fingerprint")
            except (OSError, ValueError):
                current = None
        gens = [g for g in self.generations_dir.glob("*") if g.is_dir()]
        gens.sort(key=lambda g: g.stat().st_mtime, reverse=True)
        pruned: list[str] = []
        kept = 0
        for g in gens:
            if g.name == current or kept < keep:
                kept += 1 if g.name != current else 0
                continue
            shutil.rmtree(g, ignore_errors=True)
            pruned.append(g.name)
        return pruned


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("checkout")
    ap.add_argument("--base", default=None)
    args = ap.parse_args()
    cache = IndexCache(args.checkout, base=args.base)
    q = cache.recover()
    cur = cache.load_current()
    print(json.dumps({"cache_dir": str(cache.root),
                      "quarantined": q,
                      "current": cur.fingerprint if cur else None}, indent=2))
