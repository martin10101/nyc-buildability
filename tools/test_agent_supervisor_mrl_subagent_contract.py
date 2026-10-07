"""M0-T136 C-B3: bounded-subagent contract, controller ledger, restricted profile, hook
(D-024-R566..R579). Paired positive/negative cases for every contract clause."""
from __future__ import annotations

import collections
import errno
import json
import os
import pathlib
import platform
import subprocess
import sys
import threading
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.agent_supervisor import mrl_subagent_contract as msc  # noqa: E402
from tools.agent_supervisor import mrl_subagent_hook as hook  # noqa: E402
from tools.agent_supervisor.mrl_worker_result import ContractError  # noqa: E402

HOOK = ROOT / "tools" / "agent_supervisor" / "mrl_subagent_hook.py"


def _contract(**over):
    base = dict(run_id="run-1", task_id="M0-T999", repo_root="C:/repo", allowed_paths=("tools/",),
                tools_inventory=("Read", "Grep", "Glob", "Edit", "Agent"),
                agent_inventory=("Explore", "code-reviewer"), max_concurrent=2, max_total=3)
    base.update(over)
    return msc.SubagentContract(**base)


@pytest.fixture
def ledger(tmp_path):
    return msc.SubagentLedger.create(tmp_path / "ledger.json", _contract(), primary_id="run-1.primary")


def _req(ledger, **over):
    base = dict(parent_id="run-1.primary", subagent_type="Explore", description="d", depth=1,
                background=False)
    base.update(over)
    return ledger.request(**base)


# ---------------------------------------------------------------- contract

class TestContract:
    def test_valid_contract_round_trips(self):
        c = _contract()
        assert msc.SubagentContract.from_dict(c.to_dict()) == c

    @pytest.mark.parametrize("over", [
        dict(max_depth=2),                      # depth is fixed at one (R568)
        dict(foreground_only=False),            # foreground only (R569)
        dict(writer_policy="isolated-worktrees"),  # not implemented in Tranche B -> refused
        dict(writer_policy="anything-goes"),
        dict(max_concurrent=3, max_total=2),
        dict(max_concurrent=-1),
        dict(max_total=True),
        dict(run_id=""),
        dict(allowed_paths=("tools/", "")),
        dict(tools_inventory=("Read", 3)),
    ])
    def test_invalid_contract_refuses(self, over):
        with pytest.raises(ContractError):
            _contract(**over)

    def test_malformed_dict_refuses(self):
        with pytest.raises(ContractError, match="malformed"):
            msc.SubagentContract.from_dict({"run_id": "x"})


# ---------------------------------------------------------------- ledger accounting

class TestLedger:
    def test_issue_release_and_accounting(self, ledger):
        d1 = _req(ledger)
        d2 = _req(ledger, subagent_type="code-reviewer")
        assert d1.allowed and d2.allowed and d1.child_id == "run-1.primary.c001" and d2.child_id.endswith("c002")
        acc = ledger.accounting()
        assert acc["processes_total"] == 3 and acc["subagents_live"] == 2
        ledger.release(d1.child_id)
        assert ledger.accounting()["subagents_live"] == 1
        assert ledger.accounting()["unreleased_child_ids"] == [d2.child_id]

    def test_concurrent_limit_denies_then_frees(self, ledger):
        a = _req(ledger)
        _req(ledger)
        denied = _req(ledger)
        assert not denied.allowed and "concurrent limit 2" in denied.reason
        ledger.release(a.child_id)
        assert _req(ledger).allowed

    def test_total_limit_denies_even_after_release(self, ledger):
        ids = []
        for _ in range(3):
            d = _req(ledger)
            assert d.allowed
            ids.append(d.child_id)
            ledger.release(d.child_id)
        over = _req(ledger)
        assert not over.allowed and "total limit 3" in over.reason
        assert ledger.accounting()["subagents_denied"] == 1

    @pytest.mark.parametrize("over, fragment", [
        (dict(depth=2), "depth 2 exceeds"),
        (dict(parent_id="run-1.primary.c001"), "depth>1"),
        (dict(background=True), "foreground only"),
        (dict(isolation="worktree"), "git worktree"),
        (dict(mcp=True), "MCP access is denied"),
        (dict(subagent_type="general-purpose"), "outside the controller inventory"),
        (dict(subagent_type=""), "outside the controller inventory"),
    ])
    def test_each_clause_denies(self, ledger, over, fragment):
        d = _req(ledger, **over)
        assert not d.allowed and fragment in d.reason
        assert ledger.accounting()["subagents_issued"] == 0

    def test_release_unknown_or_twice_refuses(self, ledger):
        d = _req(ledger)
        ledger.release(d.child_id)
        with pytest.raises(ContractError):
            ledger.release(d.child_id)
        with pytest.raises(ContractError):
            ledger.release("run-1.primary.c999")
        with pytest.raises(ContractError, match="no live subagent"):
            ledger.release_latest_live()

    def test_close_stops_issuance(self, ledger):
        acc = ledger.close()
        assert acc["closed"] is True
        d = _req(ledger)
        assert not d.allowed and "closed" in d.reason

    def test_bad_schema_or_missing_file_refuses(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text('{"schema": "other"}', encoding="utf-8")
        with pytest.raises(ContractError, match="schema"):
            msc.SubagentLedger(bad).accounting()
        with pytest.raises(ContractError, match="unreadable"):
            msc.SubagentLedger(tmp_path / "missing.json").accounting()

    def test_parallel_requests_never_exceed_limits(self, tmp_path):
        led = msc.SubagentLedger.create(tmp_path / "l.json", _contract(max_concurrent=2, max_total=5),
                                        primary_id="run-1.primary")
        results = []

        def worker():
            results.append(_req(led).allowed)

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert results.count(True) == 2 and results.count(False) == 6

    def test_lock_timeout_fails_closed(self, ledger, monkeypatch):
        monkeypatch.setattr(msc, "_LOCK_TIMEOUT_S", 0.05)
        lock = ledger.path.with_suffix(".json.lock")
        lock.write_text("held", encoding="utf-8")
        with pytest.raises(ContractError, match="fail closed"):
            _req(ledger)


# ------------------------------------------------- exclusive lock: Windows delete-pending (M0-T186)

def _failing_lock_open(error: OSError, *, fail_times: int):
    """A stand-in for ``os.open`` that raises ``error`` on the first ``fail_times``
    LOCK-file creates, then delegates to the real ``os.open``.

    Returns ``(fake_open, state)``; ``state['calls']`` counts lock-create attempts so
    a test can prove the acquire loop retried (waited) or stayed loud one-shot. Only
    paths ending in ``.lock`` are affected, so the ledger's own reads/writes pass
    straight through. A huge ``fail_times`` models a fault that never clears. Host-
    independent: it injects the Windows delete-pending failure on any OS, so the
    transient / never-clears behaviour is pinned deterministically everywhere; the
    raw Win32 fact is pinned separately by the nt-only platform test below.
    """
    real_open = msc.os.open
    state = {"calls": 0}

    def fake_open(path, flags, *args, **kwargs):  # type: ignore[no-untyped-def]
        if str(path).endswith(".lock"):
            state["calls"] += 1
            if state["calls"] <= fail_times:
                raise error
        return real_open(path, flags, *args, **kwargs)

    return fake_open, state


class TestExclusiveWindowsDeletePending:
    """S5: ``_exclusive()``'s acquire loop treats ONLY the proven transient Windows
    delete-pending ``PermissionError`` as 'lock busy' — retried within the lock's own
    deadline, then the module's own fail-closed refusal — while every other error
    stays loud.

    On windows-latest ``os.open(O_CREAT|O_EXCL)`` can raise ``PermissionError``
    (ERROR_ACCESS_DENIED) when another thread's ``lock.unlink()`` (its ``finally``) is
    in flight, so the lock file is delete-pending: the directory entry still exists
    but the create is denied rather than told the file already exists. The pre-repair
    loop caught only ``FileExistsError``, so that ``PermissionError`` reached the
    caller unhandled and a worker thread died (CI run 37519342596, job 112460379795).
    Every case here is injected deterministically on BOTH hosts by patching
    ``msc._is_windows`` (the platform seam) and ``msc.os.open`` — no real Windows-only
    syscall — so these run identically everywhere; the raw Win32 fact is pinned by the
    nt-only test at the end.
    """

    def test_transient_windows_permission_error_waits_then_succeeds(self, ledger, monkeypatch):
        # S5(i): the create fails twice with the Windows delete-pending error, then
        # succeeds -> the request is SERVED and the limits are intact (exactly one
        # issued, nothing lost). RED pre-repair: the PermissionError reaches the caller
        # unhandled instead of being waited out, so this line raises before the assert.
        monkeypatch.setattr(msc, "_is_windows", lambda: True, raising=False)
        fake_open, state = _failing_lock_open(
            PermissionError(errno.EACCES, "delete pending"), fail_times=2)
        monkeypatch.setattr(msc.os, "open", fake_open)
        decision = _req(ledger)
        assert decision.allowed is True
        assert state["calls"] == 3                            # 2 busy retries + 1 success
        assert ledger.accounting()["subagents_issued"] == 1   # served exactly once

    def test_persistent_windows_permission_error_times_out_fail_closed(self, ledger, monkeypatch):
        # S5(ii): a delete-pending PermissionError that NEVER clears is bounded by the
        # lock's own deadline and ends in the module's typed fail-closed refusal
        # (ContractError '...fail closed'), never an admission and never an unbounded
        # loop. RED pre-repair: the raw PermissionError reaches the caller instead of
        # the typed refusal, so pytest.raises(ContractError) does not match it.
        monkeypatch.setattr(msc, "_is_windows", lambda: True, raising=False)
        monkeypatch.setattr(msc, "_LOCK_TIMEOUT_S", 0.2)
        fake_open, state = _failing_lock_open(
            PermissionError(errno.EACCES, "delete pending"), fail_times=10 ** 9)
        monkeypatch.setattr(msc.os, "open", fake_open)
        with pytest.raises(ContractError, match="fail closed"):
            _req(ledger)
        assert state["calls"] > 1                             # it retried (waited), not one-shot
        assert ledger.accounting()["subagents_issued"] == 0   # nothing admitted

    def test_non_permission_oserror_at_create_stays_loud(self, ledger, monkeypatch):
        # S5(iii): an OSError that is NOT the transient PermissionError (EIO) is caught
        # by NEITHER except branch, so it reaches the caller at once on either platform
        # -- never waited out, never turned into a refusal. (No _is_windows patch: the
        # error is not a PermissionError, so the Windows branch is never consulted.)
        assert not isinstance(OSError(errno.EIO, "x"), (PermissionError, FileExistsError))
        fake_open, state = _failing_lock_open(
            OSError(errno.EIO, "simulated I/O error"), fail_times=10 ** 9)
        monkeypatch.setattr(msc.os, "open", fake_open)
        with pytest.raises(OSError) as exc:
            _req(ledger)
        assert not isinstance(exc.value, ContractError)       # the raw fault, not a refusal
        assert state["calls"] == 1                            # immediate, no retry/wait

    def test_permission_error_on_posix_stays_loud(self, ledger, monkeypatch):
        # S5(iii): on POSIX an O_EXCL create never yields a delete-pending
        # PermissionError, so a real one is a genuine permission fault and stays loud
        # (re-raised at once) -- only Windows treats it as transient 'busy'.
        monkeypatch.setattr(msc, "_is_windows", lambda: False, raising=False)
        fake_open, state = _failing_lock_open(
            PermissionError(errno.EACCES, "real permission fault"), fail_times=10 ** 9)
        monkeypatch.setattr(msc.os, "open", fake_open)
        with pytest.raises(PermissionError):
            _req(ledger)
        assert state["calls"] == 1                            # no wait on POSIX

    @pytest.mark.skipif(
        os.name != "nt",
        reason="Windows-only platform fact: on POSIX an O_EXCL create never raises "
        "PermissionError for a delete race, so the mechanism cannot be exercised there. "
        "This pins the Win32 behaviour the repair rests on; DEMONSTRATED on "
        "windows-latest, never assumed from memory of the API.")
    def test_windows_delete_pending_create_raises_permission_error_platform_fact(self, tmp_path):
        # S5(iv) / S3: a file that another handle (opened the way os.open opens it,
        # sharing delete) still holds open AFTER an unlink is delete-pending; an O_EXCL
        # create on that name raises PermissionError and does NOT create the file.
        # This is candidate (a)'s mechanism, proven on the platform.
        lock = tmp_path / "l.json.lock"
        fd = os.open(str(lock), os.O_CREAT | os.O_WRONLY)   # os.open shares delete on Windows
        try:
            os.unlink(str(lock))                            # delete-pending while fd is open
            with pytest.raises(PermissionError):
                os.open(str(lock), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        finally:
            os.close(fd)


# ---------------------------------------------- Windows lock PROBES (M0-T186 round 2; NEVER merged)

def _describe_exc(exc: BaseException) -> str:
    """One-line description of an exception for a probe message: class, errno, winerror.

    Cross-platform safe: ``winerror`` is ``None`` off Windows. On windows-latest
    ``os.open`` surfaces BOTH a pending-delete (ERROR_ACCESS_DENIED, winerror 5) and a
    sharing violation (ERROR_SHARING_VIOLATION, winerror 32) as ``errno 13``, so only
    the ``winerror`` tells them apart — that is what these probes capture.
    """
    if isinstance(exc, OSError):
        return f"{type(exc).__name__}(errno={exc.errno}, winerror={getattr(exc, 'winerror', None)})"
    return type(exc).__name__


def _try_excl_create(path: str) -> str:
    """Attempt ``os.open(O_CREAT|O_EXCL|O_WRONLY)`` on ``path``; close any fd; return
    exactly what happened as a string (never raises)."""
    fd = None
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        return "ok(created)"
    except BaseException as exc:  # noqa: BLE001 - a probe records every outcome verbatim
        return _describe_exc(exc)
    finally:
        if fd is not None:
            os.close(fd)


_WIN_ONLY = pytest.mark.skipif(
    os.name != "nt",
    reason="Windows-only PROBE (M0-T186 round 2): it measures the Win32 create/unlink "
    "behaviour the repair rests on. It is for the ci-exp branch only and ends in "
    "pytest.fail so its observations print in the CI FAILURES section; it is NEVER merged "
    "and asserts nothing. Skipped off Windows, where the mechanism cannot be exercised.")


@_WIN_ONLY
class TestWindowsLockProbes:
    """Windows-only experiment to FIND OUT (not assume) what the exclusive create and
    the unlink actually do on windows-latest. Each probe is bounded in time, closes
    every handle in ``finally``, writes only under ``tmp_path``, changes no existing
    test, and ends with ``pytest.fail(<observed facts>)`` so the facts land in the CI
    log. Round-1's platform-fact test was wrong: on windows-latest the ``os.unlink`` of
    a file an ``os.open`` handle still held raised ERROR_SHARING_VIOLATION (WinError 32)
    at the UNLINK (frozen job 112576591960), so it never reached its create and proved
    nothing about the create. These probes decide between candidate (a) (a delete-pending
    create denied by the OS) and candidate (b) (another process holding the file).
    """

    def test_p1_environment(self, tmp_path):
        import ctypes
        from ctypes import wintypes

        root = os.path.splitdrive(str(tmp_path))[0] + "\\"
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        fs_buf = ctypes.create_unicode_buffer(261)
        vol_buf = ctypes.create_unicode_buffer(261)
        serial = wintypes.DWORD()
        max_comp = wintypes.DWORD()
        flags = wintypes.DWORD()
        ok = kernel32.GetVolumeInformationW(
            wintypes.LPCWSTR(root), vol_buf, ctypes.sizeof(vol_buf), ctypes.byref(serial),
            ctypes.byref(max_comp), ctypes.byref(flags), fs_buf, ctypes.sizeof(fs_buf))
        fs_name = fs_buf.value if ok else f"GetVolumeInformationW_failed(err={ctypes.get_last_error()})"
        pytest.fail(
            "P1 environment: "
            f"getwindowsversion={tuple(sys.getwindowsversion())}; "
            f"platform={platform.platform()}; python={sys.version.split()[0]}; "
            f"tmp_volume_root={root!r}; tmp_filesystem={fs_name!r}")

    def test_p2_pending_delete_with_share_delete_handle(self, tmp_path):
        import ctypes
        from ctypes import wintypes

        path = str(tmp_path / "p2.lock")
        fd = os.open(path, os.O_CREAT | os.O_WRONLY)
        os.close(fd)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel32.CreateFileW.restype = wintypes.HANDLE
        kernel32.CreateFileW.argtypes = [
            wintypes.LPCWSTR, wintypes.DWORD, wintypes.DWORD, wintypes.LPVOID,
            wintypes.DWORD, wintypes.DWORD, wintypes.HANDLE]
        kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
        share_rwd = 0x1 | 0x2 | 0x4  # READ | WRITE | DELETE
        invalid = ctypes.c_void_p(-1).value
        handle = kernel32.CreateFileW(path, 0x80000000, share_rwd, None, 3, 0x80, None)
        if not handle or handle == invalid:
            pytest.fail(f"P2 setup: CreateFileW(share RWD) failed err={ctypes.get_last_error()}")
        closed = False
        try:
            try:
                os.unlink(path)
                unlink_result = "ok"
            except OSError as exc:
                unlink_result = _describe_exc(exc)
            exists_after = os.path.exists(path)
            create_while_open = _try_excl_create(path)
            kernel32.CloseHandle(handle)
            closed = True
            create_after_close = _try_excl_create(path)
        finally:
            if not closed:
                kernel32.CloseHandle(handle)
        pytest.fail(
            "P2 share-delete handle held open: "
            f"unlink={unlink_result}; path_exists_after_unlink={exists_after}; "
            f"O_EXCL_create_while_handle_open={create_while_open}; "
            f"O_EXCL_create_after_handle_closed={create_after_close}")

    def test_p3_pending_delete_with_plain_os_open_handle(self, tmp_path):
        path = str(tmp_path / "p3.lock")
        holder = os.open(path, os.O_CREAT | os.O_RDONLY)  # the way os.open opens it
        closed = False
        try:
            try:
                os.unlink(path)
                unlink_result = "ok"
            except OSError as exc:
                unlink_result = _describe_exc(exc)
            exists_after = os.path.exists(path)
            create_while_open = _try_excl_create(path)
            os.close(holder)
            closed = True
            create_after_close = _try_excl_create(path)
        finally:
            if not closed:
                os.close(holder)
        pytest.fail(
            "P3 plain os.open handle held open (no explicit share-delete): "
            f"unlink={unlink_result}; path_exists_after_unlink={exists_after}; "
            f"O_EXCL_create_while_handle_open={create_while_open}; "
            f"O_EXCL_create_after_handle_closed={create_after_close}")

    def test_p4_real_race_raw_os_calls(self, tmp_path):
        # 8 threads loop the literal pre-fix sequence (O_EXCL create, close, unlink) on
        # ONE path with no third handle, bounded by time AND an iteration cap. Count per
        # outcome what the CREATE raised and what the UNLINK raised. This shows whether
        # the real race alone yields a PermissionError at the create (candidate (a)) with
        # no external process involved.
        path = str(tmp_path / "p4race.lock")
        n, time_budget_s, cap = 8, 20.0, 400_000
        barrier = threading.Barrier(n)
        per_thread: list = [None] * n

        def worker(idx: int) -> None:
            c = collections.Counter()
            iters = 0
            barrier.wait()
            deadline = time.monotonic() + time_budget_s
            while time.monotonic() < deadline and iters < cap:
                iters += 1
                try:
                    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                except FileExistsError:
                    c["create:FileExistsError"] += 1
                    continue
                except OSError as exc:
                    c[f"create:{_describe_exc(exc)}"] += 1
                    continue
                c["create:ok"] += 1
                os.close(fd)
                try:
                    os.unlink(path)
                    c["unlink:ok"] += 1
                except OSError as exc:
                    c[f"unlink:{_describe_exc(exc)}"] += 1
            per_thread[idx] = (c, iters)

        start = time.monotonic()
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.monotonic() - start
        totals = collections.Counter()
        total_iters = 0
        for c, iters in per_thread:
            totals.update(c)
            total_iters += iters
        pytest.fail(
            f"P4 real race ({n} threads, {total_iters} iterations, {elapsed:.1f}s elapsed, "
            f"budget {time_budget_s}s/cap {cap}): {dict(sorted(totals.items()))}")

    def test_p5_real_race_through_repaired_exclusive(self, tmp_path):
        # 8 threads contend on the REPAIRED _exclusive() for a bounded time. Count
        # acquisitions, typed ContractError refusals, and any other exception that
        # escapes; a guarded counter checks that at most one thread is ever inside the
        # section (mutual exclusion). Reports what the repaired lock does on Windows.
        base = tmp_path / "p5.json"
        n, time_budget_s, cap = 8, 15.0, 400_000
        barrier = threading.Barrier(n)
        per_thread: list = [None] * n
        inside = {"cur": 0, "max": 0}
        inside_lock = threading.Lock()

        def worker(idx: int) -> None:
            c = collections.Counter()
            iters = 0
            barrier.wait()
            deadline = time.monotonic() + time_budget_s
            while time.monotonic() < deadline and iters < cap:
                iters += 1
                try:
                    with msc._exclusive(base):
                        with inside_lock:
                            inside["cur"] += 1
                            inside["max"] = max(inside["max"], inside["cur"])
                        with inside_lock:
                            inside["cur"] -= 1
                        c["acquired"] += 1
                except ContractError:
                    c["refused:ContractError"] += 1
                except BaseException as exc:  # noqa: BLE001 - a probe records every escape
                    c[f"escaped:{_describe_exc(exc)}"] += 1
            per_thread[idx] = (c, iters)

        start = time.monotonic()
        threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        elapsed = time.monotonic() - start
        totals = collections.Counter()
        total_iters = 0
        for c, iters in per_thread:
            totals.update(c)
            total_iters += iters
        pytest.fail(
            f"P5 repaired _exclusive race ({n} threads, {total_iters} iterations, "
            f"{elapsed:.1f}s, budget {time_budget_s}s/cap {cap}): "
            f"max_concurrent_inside={inside['max']} (expect 1); {dict(sorted(totals.items()))}")


# ---------------------------------------------------------------- restricted profile

class TestRestrictedProfile:
    def _build(self, tmp_path, **over):
        # every inventory tool explicitly allowed or denied (M0-T142 R692)
        kw = dict(ledger_path=tmp_path / "ledger.json", hook_script=HOOK, allow_rules=("Read", "Grep", "Glob"),
                  deny_rules=("Edit", "Agent"), profile_dir=tmp_path / "profile", model="claude-opus-4-8")
        kw.update(over)
        return msc.build_restricted_profile(_contract(), **kw)

    def test_flags_compose_every_real_mechanism(self, tmp_path):
        p = self._build(tmp_path)
        flags = list(p.argv_flags)
        assert flags[:3] == ["--restricted", "--permission-mode", "dontAsk"]
        assert flags[flags.index("--tools") + 1] == "Read,Grep,Glob,Edit,Agent"
        assert "--strict-mcp-config" in flags and "--mcp-config" not in flags
        assert flags[flags.index("--settings") + 1] == p.profile_path
        assert "--allowedTools" in flags and "--disallowedTools" in flags
        assert flags[flags.index("--disallowedTools") + 1:] == ["Edit", "Agent", "mcp__*"]
        assert set(json.loads(flags[flags.index("--agents") + 1])) == {"Explore", "code-reviewer"}
        written = json.loads(pathlib.Path(p.profile_path).read_text(encoding="utf-8"))
        assert written["permissions"]["defaultMode"] == "dontAsk"
        assert "mcp__*" in written["permissions"]["deny"]
        pre = written["hooks"]["PreToolUse"][0]
        assert pre["matcher"] == "Agent|Task" and "--event pre" in pre["hooks"][0]["command"]
        assert str(HOOK) in pre["hooks"][0]["command"]
        assert written["hooks"]["PostToolUse"][0]["hooks"][0]["command"].endswith("--event post")
        assert written["mrl"]["allowed_paths"] == ["tools/"] and written["mrl"]["task_id"] == "M0-T999"
        assert all(a["tools"] == ["Read", "Grep", "Glob"] and a["model"] == "claude-opus-4-8"
                   for a in p.agents.values())
        assert len(p.identity_sha256) == 64

    def test_tools_alone_grants_nothing(self, tmp_path):
        p = self._build(tmp_path, allow_rules=(),
                        deny_rules=("Read", "Grep", "Glob", "Edit", "Agent"))
        assert "--tools" in p.argv_flags and "--allowedTools" not in p.argv_flags
        assert p.effective_grants() == frozenset()
        q = self._build(tmp_path, allow_rules=("Read", "Edit(tools/**)"),
                        deny_rules=("Grep", "Glob", "Agent"))
        assert q.effective_grants() == frozenset({"Read", "Edit"})

    def test_deny_beats_allow_and_inventory(self, tmp_path):
        p = self._build(tmp_path, allow_rules=("Read", "Edit"),
                        deny_rules=("Edit", "Grep", "Glob", "Agent"))
        assert p.effective_grants() == frozenset({"Read"})

    def test_unpinned_inventory_tool_refuses(self, tmp_path):
        """M0-T142 (R688/R692): 2.1.252 dontAsk EXECUTES read-only commands for a
        tool merely absent from the allow rules - so an inventory tool that is
        neither allowed nor denied refuses the profile outright."""
        with pytest.raises(ContractError, match="neither allow-ruled nor deny-ruled"):
            self._build(tmp_path, deny_rules=("Edit",))  # Agent left unpinned

    def test_bash_bare_deny_is_load_bearing(self, tmp_path):
        """AS-PB-1: the canary shape - Bash in the inventory, bare-denied - flows
        into BOTH permissions.deny and --disallowedTools."""
        p = msc.build_restricted_profile(
            _contract(tools_inventory=("Bash", "Read", "Grep", "Glob", "Agent")),
            ledger_path=tmp_path / "l.json", hook_script=HOOK,
            allow_rules=("Read", "Grep", "Glob", "Agent"), deny_rules=("Bash",),
            profile_dir=tmp_path / "p", model="claude-opus-4-8")
        flags = list(p.argv_flags)
        assert flags[flags.index("--disallowedTools") + 1:] == ["Bash", "mcp__*"]
        written = json.loads(pathlib.Path(p.profile_path).read_text(encoding="utf-8"))
        assert "Bash" in written["permissions"]["deny"]
        assert "Bash" not in written["permissions"]["allow"]
        assert p.effective_grants() == frozenset({"Read", "Grep", "Glob", "Agent"})

    def test_allow_outside_inventory_refuses(self, tmp_path):
        with pytest.raises(ContractError, match="outside the inventory"):
            self._build(tmp_path, allow_rules=("WebFetch",))

    def test_mcp_allow_refuses(self, tmp_path):
        with pytest.raises(ContractError, match="MCP"):
            msc.build_restricted_profile(_contract(tools_inventory=("Read", "mcp__x__y")),
                                         ledger_path=tmp_path / "l.json", hook_script=HOOK,
                                         allow_rules=("mcp__x__y",), profile_dir=tmp_path, model="m")

    def test_missing_hook_or_model_refuses(self, tmp_path):
        with pytest.raises(ContractError, match="hook"):
            self._build(tmp_path, hook_script=tmp_path / "nope.py")
        with pytest.raises(ContractError, match="model"):
            self._build(tmp_path, model="")

    def test_managed_policy_is_accounted_present_and_absent(self, tmp_path):
        absent = self._build(tmp_path, managed_settings_path=tmp_path / "managed-settings.json")
        assert absent.settings["mrl"]["managed_policy"] == {
            "path": str(tmp_path / "managed-settings.json"), "present": False, "sha256": None}
        (tmp_path / "managed-settings.json").write_text('{"permissions": {}}', encoding="utf-8")
        present = self._build(tmp_path, managed_settings_path=tmp_path / "managed-settings.json")
        assert present.settings["mrl"]["managed_policy"]["present"] is True
        assert present.identity_sha256 != absent.identity_sha256   # unaccounted policy changes identity

    def test_identity_changes_with_profile_bytes(self, tmp_path):
        a = self._build(tmp_path)
        b = self._build(tmp_path, allow_rules=("Read",),
                        deny_rules=("Grep", "Glob", "Edit", "Agent"))
        assert a.identity_sha256 != b.identity_sha256

    def test_identity_is_policy_not_run_dir(self, tmp_path):
        # Same policy in two different run directories -> same pinnable identity ...
        a = self._build(tmp_path, ledger_path=tmp_path / "run-a" / "ledger.json", profile_dir=tmp_path / "run-a")
        b = self._build(tmp_path, ledger_path=tmp_path / "run-b" / "ledger.json", profile_dir=tmp_path / "run-b")
        assert a.identity_sha256 == b.identity_sha256
        # ... while a modified hook script (same rules) changes it.
        edited = tmp_path / "hook_copy.py"
        edited.write_bytes(HOOK.read_bytes() + b"\n# tampered\n")
        c = self._build(tmp_path, hook_script=edited, profile_dir=tmp_path / "run-c")
        assert c.identity_sha256 != a.identity_sha256


# ---------------------------------------------------------------- hook (in-process and real subprocess)

def _payload(**over):
    base = {"hook_event_name": "PreToolUse", "tool_name": "Agent",
            "tool_input": {"subagent_type": "Explore", "description": "trace", "prompt": "x"}}
    base.update(over)
    return base


class TestHook:
    def test_pre_allows_and_post_releases(self, ledger, capsys):
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 0
        assert json.loads(capsys.readouterr().out)["mrl_child_id"] == "run-1.primary.c001"
        assert ledger.accounting()["subagents_live"] == 1
        assert hook.decide(_payload(hook_event_name="PostToolUse"), ledger, "run-1.primary", "post") == 0
        assert ledger.accounting()["subagents_live"] == 0

    def test_pre_from_a_subagent_is_depth_two_and_denied(self, ledger, capsys):
        assert hook.decide(_payload(agent_type="Explore"), ledger, "run-1.primary", "pre") == 2
        assert "depth 2" in capsys.readouterr().err
        assert hook.decide(_payload(agent_id="abc"), ledger, "run-1.primary", "pre") == 2

    def test_pre_out_of_inventory_background_isolation_mcp_denied(self, ledger, capsys):
        for tool_input in ({"subagent_type": "general-purpose", "description": "d"},
                           {"subagent_type": "Explore", "run_in_background": True},
                           {"subagent_type": "Explore", "isolation": "worktree"},
                           {"subagent_type": "mcp__server__agent"}):
            assert hook.decide(_payload(tool_input=tool_input), ledger, "run-1.primary", "pre") == 2
        assert hook.decide(_payload(tool_name="mcp__x__spawn"), ledger, "run-1.primary", "pre") == 2
        assert ledger.accounting()["subagents_denied"] == 5

    def test_over_limit_denied(self, ledger):
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 0
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 0
        assert hook.decide(_payload(), ledger, "run-1.primary", "pre") == 2

    def test_malformed_payload_fails_closed(self, ledger):
        assert hook.decide("not-an-object", ledger, "run-1.primary", "pre") == 2
        assert hook.decide({"tool_name": "Agent"}, ledger, "run-1.primary", "pre") == 2
        assert hook.decide({"tool_input": "str"}, ledger, "run-1.primary", "pre") == 2

    def test_post_never_blocks_even_with_nothing_live(self, ledger, capsys):
        assert hook.decide(_payload(), ledger, "run-1.primary", "post") == 0
        assert "accounting warning" in capsys.readouterr().err

    def test_real_subprocess_invocation_matches_profile_command(self, tmp_path):
        contract = _contract(max_concurrent=1, max_total=1)
        ledger = msc.SubagentLedger.create(tmp_path / "ledger.json", contract, primary_id="run-1.primary")
        profile = msc.build_restricted_profile(contract, ledger_path=ledger.path, hook_script=HOOK,
                                               allow_rules=("Read",),
                                               deny_rules=("Grep", "Glob", "Edit", "Agent"),
                                               profile_dir=tmp_path / "p", model="m")
        cmd = profile.settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        assert cmd.startswith(f'"{sys.executable}"')
        base = [sys.executable, str(HOOK), "--ledger", str(ledger.path), "--parent", "run-1.primary"]
        first = subprocess.run([*base, "--event", "pre"], input=json.dumps(_payload()), capture_output=True,
                               text=True, timeout=60)
        assert first.returncode == 0, first.stderr
        assert json.loads(first.stdout)["mrl_child_id"] == "run-1.primary.c001"
        second = subprocess.run([*base, "--event", "pre"], input=json.dumps(_payload()), capture_output=True,
                                text=True, timeout=60)
        assert second.returncode == 2 and "concurrent limit 1" in second.stderr
        post = subprocess.run([*base, "--event", "post"], input=json.dumps(_payload()), capture_output=True,
                              text=True, timeout=60)
        assert post.returncode == 0
        garbage = subprocess.run([*base, "--event", "pre"], input="{not json", capture_output=True,
                                 text=True, timeout=60)
        assert garbage.returncode == 2 and "fail closed" in garbage.stderr
        acc = ledger.accounting()
        assert acc == {"primary_id": "run-1.primary", "processes_total": 2, "subagents_issued": 1,
                       "subagents_live": 0, "subagents_denied": 1, "unreleased_child_ids": [], "closed": False}
