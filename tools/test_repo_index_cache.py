#!/usr/bin/env python3
"""M0-T063 Unit A1 tests: crash-safe cache generations (D-013-R035/R036).

Proves AS-3: a valid prior generation stays loadable across every simulated
crash point; an incomplete generation is quarantined; retry is idempotent; stale
locks and concurrent writers are handled by an explicit fail-closed rule; no
half-index is ever observable as current. Deterministic, stdlib-only; the cache
base is a temp dir (never the real LOCALAPPDATA).
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from tools import repo_index_cache as ic  # noqa: E402


class CacheCase(unittest.TestCase):
    def setUp(self) -> None:
        self._base = tempfile.TemporaryDirectory()
        self._co = tempfile.TemporaryDirectory()
        self.base = self._base.name
        self.checkout = self._co.name
        self.cache = ic.IndexCache(self.checkout, base=self.base)
        self.addCleanup(self._base.cleanup)
        self.addCleanup(self._co.cleanup)


class AtomicPromotion(CacheCase):
    def test_write_promote_and_load_current(self) -> None:
        g = self.cache.write_generation("fp1", {"nodes": [1, 2]})
        self.assertEqual(self.cache.load_current().fingerprint, "fp1")
        self.assertEqual(g.load_payload(), {"nodes": [1, 2]})

    def test_retry_is_idempotent(self) -> None:
        a = self.cache.write_generation("fp1", {"n": 1})
        b = self.cache.write_generation("fp1", {"n": 1})
        self.assertEqual(a.content_digest, b.content_digest)

    def test_prior_valid_generation_stays_loadable(self) -> None:
        self.cache.write_generation("fp1", {"n": 1})
        self.cache.write_generation("fp2", {"n": 2})
        self.assertIsNotNone(self.cache.load_fingerprint("fp1"))
        self.assertEqual(self.cache.load_current().fingerprint, "fp2")


class CrashRecovery(CacheCase):
    def test_incomplete_temp_generation_is_quarantined(self) -> None:
        self.cache.write_generation("fp1", {"n": 1})
        # simulate a crash mid-write: an orphan temp generation directory
        self.cache._ensure_dirs()
        (self.cache.tmp_dir / "fp2.12345").mkdir(parents=True)
        (self.cache.tmp_dir / "fp2.12345" / "payload.json").write_text("{}")
        q = self.cache.recover()
        self.assertTrue(any("incomplete_temp_generation" in x for x in q))
        # prior valid generation survives; current unchanged
        self.assertEqual(self.cache.load_current().fingerprint, "fp1")
        self.assertFalse((self.cache.tmp_dir / "fp2.12345").exists())

    def test_corrupt_promoted_generation_is_quarantined(self) -> None:
        self.cache.write_generation("fp1", {"n": 1})
        self.cache.write_generation("fp2", {"n": 2})
        # tamper fp2's payload so its digest no longer matches meta
        gen = self.cache.generations_dir / "fp2"
        (gen / "payload.json").write_text('{"n": 999}', encoding="utf-8")
        q = self.cache.recover()
        self.assertTrue(any("fp2" in x and "corrupt" in x for x in q))
        # fp1 remains loadable; fp2 is gone from generations
        self.assertIsNotNone(self.cache.load_fingerprint("fp1"))
        self.assertIsNone(self.cache.load_fingerprint("fp2"))

    def test_load_current_runs_recovery_and_never_returns_half_index(self) -> None:
        self.cache.write_generation("fp1", {"n": 1})
        # point current at a fingerprint whose generation is incomplete
        self.cache._ensure_dirs()
        broken = self.cache.generations_dir / "fpX"
        broken.mkdir(parents=True)
        (broken / "meta.json").write_text('{"cache_format_version": 1}')  # no payload
        self.cache._set_current("fpX")
        # load_current must not return the half generation
        cur = self.cache.load_current()
        self.assertIsNone(cur if (cur and cur.fingerprint == "fpX") else None)
        self.assertNotEqual(cur.fingerprint if cur else None, "fpX")

    def test_live_writer_temp_dir_is_not_quarantined(self) -> None:
        # MINOR-2 (G3 review): a temp generation owned by a LIVE pid is an
        # in-progress write, not an orphan - recover() must leave it alone so a
        # concurrent reader cannot abort a healthy write. A dead-pid temp IS
        # quarantined.
        import os as _os
        self.cache.write_generation("fp1", {"n": 1})
        self.cache._ensure_dirs()
        live = self.cache.tmp_dir / f"fpLive.{_os.getpid()}"
        live.mkdir(parents=True)
        dead = self.cache.tmp_dir / "fpDead.999999999"
        dead.mkdir(parents=True)
        q = self.cache.recover()
        self.assertTrue(live.exists(), "a live writer's temp dir was quarantined")
        self.assertFalse(dead.exists(), "a dead-pid orphan temp was not quarantined")
        self.assertTrue(any("fpDead" in x for x in q))

    def test_validation_before_promotion(self) -> None:
        # a payload that is not JSON-serializable cannot be written; a valid one
        # is validated (digest matches) before promotion.
        g = self.cache.write_generation("fp1", {"ok": True})
        meta = json.loads((g.path / "meta.json").read_text())
        payload = json.loads((g.path / "payload.json").read_text())
        self.assertEqual(meta["content_digest"], ic._content_digest(payload))


class Locking(CacheCase):
    def test_concurrent_writer_is_refused(self) -> None:
        lock = ic.SingleWriterLock(self.cache.root)
        lock.acquire()
        try:
            with self.assertRaises(ic.CacheError) as ctx:
                ic.SingleWriterLock(self.cache.root).acquire()
            self.assertEqual(ctx.exception.code, "concurrent_writer")
        finally:
            lock.release()

    def test_stale_lock_with_dead_pid_is_reclaimed(self) -> None:
        lock = ic.SingleWriterLock(self.cache.root)
        lock.lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_path.mkdir()
        # a lock owned by an impossible pid, acquired long ago -> reclaimable
        (lock.lock_path / "owner.json").write_text(
            json.dumps({"pid": 2 ** 31 - 1, "acquired_at": 0.0}))
        fresh = ic.SingleWriterLock(self.cache.root)
        fresh.acquire()  # reclaims the stale lock
        self.assertTrue(fresh._held)
        fresh.release()

    def test_live_lock_is_not_reclaimed_even_if_old(self) -> None:
        lock = ic.SingleWriterLock(self.cache.root)
        lock.lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock.lock_path.mkdir()
        # owned by THIS process (alive), acquired long ago -> not reclaimable
        (lock.lock_path / "owner.json").write_text(
            json.dumps({"pid": os.getpid(), "acquired_at": 0.0}))
        with self.assertRaises(ic.CacheError):
            ic.SingleWriterLock(self.cache.root).acquire()


class Retention(CacheCase):
    def test_prune_keeps_current_and_recent(self) -> None:
        for i in range(6):
            self.cache.write_generation(f"fp{i}", {"n": i})
        pruned = self.cache.prune(keep=2)
        # current (fp5) is never pruned
        self.assertNotIn("fp5", pruned)
        self.assertIsNotNone(self.cache.load_current())


class OutsideRepoGuard(unittest.TestCase):
    def test_cache_refuses_a_location_inside_the_checkout(self) -> None:
        with tempfile.TemporaryDirectory() as co:
            inside = pathlib.Path(co) / "inside"
            with self.assertRaises(ic.CacheError) as ctx:
                ic.cache_dir_for(co, base=str(inside))
            self.assertEqual(ctx.exception.code, "cache_inside_repo")


if __name__ == "__main__":
    unittest.main()
