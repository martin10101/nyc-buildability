# Producer report — M0-T176

D-091 TW1 follow-up to M0-T171: the review-slot lock must WAIT through Windows
sharing-violation `PermissionError`s instead of refusing at once.

- Worktree: `/root/project/w-M0-T176`
- Branch: `task/M0-T176-review-slots-windows`
- Claim seam (start HEAD): `ecc8288d67fea1196081615707743940516b4b7b`
- Directive refs: D-091 (D-091-R001, D-091-R007)
- Files changed (producer scope):
  - `tools/agent_supervisor/review_slots.py`
  - `tools/test_agent_supervisor_review_slots.py`

---

## 1. The defect (restated from evidence)

`_SlotLock.acquire` catches only `FileExistsError` as "busy" and retries to the
deadline; every other `OSError` becomes an immediate `slot_lock_error` refusal. On
windows-latest, `os.open(O_CREAT|O_EXCL|O_WRONLY)` can raise `PermissionError`
(ERROR_ACCESS_DENIED) when the just-released previous lock file is **delete-pending**
— another racer's short `_read_holder` read still has the file open after the holder
unlinked it, so the name cannot yet be re-created. That `PermissionError` fell to the
generic `except OSError` branch and refused at once, so a racer that should have won a
free slot was refused. Result: `RaceTests::test_global_last_slot_never_double_taken`
flaked `AssertionError 1 != 2` (6 racers, 2 global slots, only 1 winner) in PR #312 CI
(run 37001721581). Safety was never violated (it can only ever refuse, never
over-admit), but liveness was, and the race test flaked on every PR. M0-T171's G3/G4
delta note (d) predicted exactly this and recommended the fix as optional hardening.

## 2. Design

Minimal, fail-closed, POSIX-unchanged.

- In `acquire`, add an `except PermissionError as exc:` branch **between**
  `except FileExistsError` and the generic `except OSError`. (`PermissionError` and
  `FileExistsError` are sibling `OSError` subclasses — neither subclasses the other —
  so ordering only requires both to precede the generic `OSError` branch.)
- On Windows, treat it as a transient "busy": wait one poll and retry to the same
  deadline exactly like `FileExistsError`; refuse only at the timeout with
  `slot_lock_timeout`.
- **Never** take over on a `PermissionError`. The branch does not call
  `_holder_is_stale`/`_take_over` at all. A delete-pending file is unreadable, so it
  can never be *proven* dead/reused; and the pending delete clears on its own, after
  which the next `O_EXCL` create succeeds. A genuinely-stale, non-delete-pending lock
  surfaces as `FileExistsError` (not `PermissionError`) and still uses the existing
  stale-takeover path, so no takeover capability is lost on Windows.
- On POSIX, a `PermissionError` from an `O_EXCL` create is never a delete-pending race
  — it is a real permission fault — so it still fails closed at once with
  `slot_lock_error` (behavior unchanged). The branch guards on `not _is_windows()`.
- Every other `OSError` (e.g. EIO) still refuses immediately with `slot_lock_error`,
  on both platforms.
- Factored the "wait one poll, or raise `slot_lock_timeout` at the deadline" tail into
  `_SlotLock._wait_or_fail_closed(deadline)` so the `FileExistsError` and
  `PermissionError` busy-paths share one timeout implementation (no duplicated message).

### The `_is_windows()` platform seam (why not patch `os.name`)

The packet asks for deterministic tests that "patch `os.name` and `os.open` ... and
avoid real Windows-only calls". Patching the global `os.name = "nt"` is **not viable**
on a POSIX host: `pathlib.Path(...)` (the base `Path`) dispatches to `WindowsPath`
when `os.name == "nt"`, and `WindowsPath` raises `NotImplementedError: cannot
instantiate 'WindowsPath' on your system` on Linux. `_SlotLock.__init__` constructs a
`pathlib.Path(...)` inside `try_reserve` (via `self._lock()`), so patching `os.name`
globally crashes the test, not the branch. I verified this empirically (the first test
run failed with exactly that `WindowsPath` `NotImplementedError`).

So I introduced a one-line module seam `review_slots._is_windows()` (`return os.name
== "nt"`) and the acquire branch calls it. Production behavior is identical to reading
`os.name` (platform never changes mid-process); tests patch `review_slots._is_windows`
to simulate each platform without touching the global `os` module, so `pathlib` stays
on its real flavour. `os.open` is still patched directly (it is used only for the
O_EXCL lock create in this module; builtin `open()` used by the state-file writer goes
through the C `_io` layer and is unaffected by patching the Python-level `os.open`).

## 3. Full diff of `review_slots.py`

```diff
diff --git a/tools/agent_supervisor/review_slots.py b/tools/agent_supervisor/review_slots.py
index 1bb483f5..837a6d4e 100644
--- a/tools/agent_supervisor/review_slots.py
+++ b/tools/agent_supervisor/review_slots.py
@@ -75,6 +75,18 @@ DEFAULT_LOCK_TIMEOUT_S = 10.0
 DEFAULT_LOCK_POLL_S = 0.01
 
 
+def _is_windows() -> bool:
+    """True on Windows (``os.name == 'nt'``).
+
+    The lock's handling of a delete-pending ``PermissionError`` is Windows-only, so
+    the acquire loop branches on this. It is a named indirection over ``os.name`` so
+    the behaviour can be exercised deterministically on either host without patching
+    the global ``os.name`` (which would make ``pathlib`` dispatch ``WindowsPath`` and
+    break on POSIX). Platform never changes mid-process, so this is a pure read.
+    """
+    return os.name == "nt"
+
+
 class SlotError(Exception):
     """A slot could not be reserved safely. Always carries a code; never fails open."""
 
@@ -193,6 +205,14 @@ class _SlotLock:
     reused pid) is taken over with the same temp-write + `os.replace` + re-read
     confirmation `locking.SingleInstanceLock` uses; a holder whose liveness cannot
     be read makes the wait time out and fail closed.
+
+    On Windows the create can also raise `PermissionError` (ERROR_ACCESS_DENIED)
+    while a just-released lock file is delete-pending because a racer still has it
+    open for a liveness read. That is treated as a transient "busy" and waited out
+    to the same deadline (never a stale takeover, since a delete-pending file is
+    unreadable); only a lock that never clears times out and fails closed. POSIX
+    does not produce this for an O_EXCL create, so a PermissionError there stays an
+    immediate fail-closed `slot_lock_error`.
     """
 
     def __init__(self, path: pathlib.Path, *, pid: int, start_token: str,
@@ -213,6 +233,12 @@ class _SlotLock:
         })
 
     def _read_holder(self) -> dict[str, Any] | None:
+        # read_text opens, reads, and closes in the one call, so the read handle is
+        # short-lived by construction. That matters on Windows: the shorter a racer
+        # holds this file open, the narrower the delete-pending window in which a
+        # concurrent O_EXCL create sees PermissionError. Never widen this to a held
+        # handle. A delete-pending or mid-write read raises OSError here and is read
+        # as "unreadable" (None) -> wait, never steal.
         try:
             holder = json.loads(self.path.read_text(encoding="utf-8"))
         except (OSError, ValueError):
@@ -245,6 +271,21 @@ class _SlotLock:
         confirmed = self._read_holder()
         return bool(confirmed and confirmed.get("lock_id") == self._lock_id)
 
+    def _wait_or_fail_closed(self, deadline: float) -> None:
+        """Sleep one poll, or raise slot_lock_timeout once the deadline has passed.
+
+        Shared by every "busy" outcome of the O_EXCL create — an existing lock file
+        we could not take over, or (on Windows) a delete-pending one: real
+        contenders serialize by waiting, and a lock that never clears refuses
+        fail-closed at the timeout rather than guessing a slot is free.
+        """
+        if time.monotonic() >= deadline:
+            raise SlotError(
+                "slot_lock_timeout",
+                f"the slot lock {self.path} was held past {self.timeout_s:g}s; "
+                f"refusing the reservation (fail closed)")
+        time.sleep(self.poll_s)
+
     def acquire(self) -> None:
         self.path.parent.mkdir(parents=True, exist_ok=True)
         deadline = time.monotonic() + self.timeout_s
@@ -253,14 +294,28 @@ class _SlotLock:
             try:
                 fd = os.open(str(self.path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
             except FileExistsError:
+                # The lock file exists: take over only a readable, provably
+                # dead/reused holder; otherwise wait out the deadline.
                 if self._holder_is_stale() and self._take_over():
                     return
-                if time.monotonic() >= deadline:
+                self._wait_or_fail_closed(deadline)
+                continue
+            except PermissionError as exc:
+                # Windows only: O_CREAT|O_EXCL can raise PermissionError
+                # (ERROR_ACCESS_DENIED) while a prior holder's lock file is
+                # delete-pending — a racer's short liveness read still has it open
+                # after the holder unlinked it. That is a transient "busy", not a
+                # real permission fault, so wait to the deadline exactly like
+                # FileExistsError and refuse only at the timeout. NEVER take over on
+                # it: a delete-pending file cannot be read, so it can never be proven
+                # stale, and the pending delete clears on its own. On POSIX, O_EXCL
+                # does not produce this for a delete-pending race, so a PermissionError
+                # there is a real fault and still fails closed at once (unchanged).
+                if not _is_windows():
                     raise SlotError(
-                        "slot_lock_timeout",
-                        f"the slot lock {self.path} was held past {self.timeout_s:g}s; "
-                        f"refusing the reservation (fail closed)")
-                time.sleep(self.poll_s)
+                        "slot_lock_error",
+                        f"could not acquire slot lock {self.path}: {exc}") from exc
+                self._wait_or_fail_closed(deadline)
                 continue
             except OSError as exc:
                 raise SlotError("slot_lock_error",
```

Test file (`tools/test_agent_supervisor_review_slots.py`) changes, summarized:
- top-level `import errno`, `import os`, `from unittest import mock`, and
  `from tools.agent_supervisor import review_slots` (needed to patch the seam);
- `test_lock_error_fails_closed` rewritten: the directory-at-lock-path now asserts
  `slot_lock_timeout` on **both** platforms (no more `os.name` branch); comment updated;
- new `WindowsSharingViolationTests` class with a `_failing_open` helper (wraps the
  real `os.open`, raises the injected error the first N creates, then delegates) and
  four tests (below).

## 4. Per-site sharing-violation analysis ("fix only what is real")

1. **`acquire` O_EXCL create — FIXED.** The one real spurious-refusal site. See §2.

2. **`_read_holder` — already correct, documented, no behavior change.**
   `pathlib.Path.read_text()` opens, reads, and closes within the one call, so the
   read handle is short-lived by construction — this is what keeps the delete-pending
   window narrow for other racers. If the file is itself delete-pending/mid-write when
   *this* process reads it, `read_text` raises `OSError` (PermissionError is an
   `OSError`), already caught by `except (OSError, ValueError): return None` → treated
   as "unreadable" → not stale → wait, never steal. Correct as-is; I added a comment
   pinning the short-lived-handle invariant so a future edit does not widen it.

3. **`_take_over` + `os.replace` — already correct, no change.** `_take_over` runs
   only after `_holder_is_stale()` is True (holder readable AND provably dead/reused).
   If `os.replace` (or the temp write) hits a Windows sharing violation it raises
   `OSError` → caught → `temp.unlink()` (suppressed) → `return False` → the acquire
   loop simply retries to the deadline. A failed takeover can only ever degrade to a
   wait/retry; it can never grant a slot. The re-read-confirm (`confirmed.lock_id ==
   self._lock_id`) still elects exactly one winner among concurrent takeovers
   (the inherited N1 note from locking.py; safety-preserving). No change needed.

4. **`release`'s unlink — already correct, no change; delete-pending reasoned through.**
   `release` first reads the holder and returns WITHOUT unlinking unless the on-disk
   `lock_id` equals *this* lock's id — so it can never remove or forge another holder's
   lock. The unlink is wrapped in `contextlib.suppress(OSError)`. Delete-pending walk-through:
   the empirically-observed defect (a delete-pending `PermissionError` on a later
   `O_EXCL` create) implies the readers opened the file sharing delete, so the holder's
   `unlink()` **succeeds** and merely marks the file delete-pending; it then vanishes
   once the racer's short read closes, and the waiting creator (fixed in §2) retries
   through the brief window. In the alternative world where a reader did not share
   delete, the `unlink` would raise `PermissionError` — suppressed, the file stays our
   own lock — but in that world an `O_EXCL` create on the still-present file raises
   `FileExistsError`, not `PermissionError`, so the §1 defect would not arise. Either
   way release never removes/forges another's lock and never crashes. No change needed.

5. **State-file reads/writes (`_read_raw`, `_read_live`, `_write`) — no contention
   possible, no change.** All run **only** while holding `_SlotLock` (`try_reserve`,
   `release`, and `active` each wrap their body in `with self._lock():`). The lock is
   exclusive and cross-process, so exactly one process touches `review_slots.json` at a
   time — there is no concurrent reader to cause a Windows sharing violation on the
   state file. `_write` additionally writes to a pid-suffixed temp (`.{pid}.tmp`) and
   `os.replace`s it, so even the temp name cannot collide. Confirmed contention-free.

Net: the only production behavior change is the `acquire` PermissionError branch; all
other sites were already fail-safe against sharing violations and are left untouched
(two doc-only comments added).

## 5. Scenario → test mapping

| Packet scenario | Test | Asserts |
|---|---|---|
| primary: transient PermissionError (both platforms) → wait then succeed, no refusal | `WindowsSharingViolationTests::test_transient_permission_error_waits_then_succeeds_as_nt` | fail twice as nt then succeed; `admitted` True, reservation not None, `os.open` called 3x (proves it waited), one live slot |
| persistent: lock path unusable → refuse at deadline, admitted False, no reservation (slot_lock_timeout on both) | `test_persistent_permission_error_times_out_as_nt` **and** `FailureAndReclaimTests::test_lock_error_fails_closed` (directory at lock path; now `slot_lock_timeout` on both platforms) | admitted False, `slot_lock_timeout`, reservation None; retried (>1 create) |
| race: separate-process races still give exactly 2 global / 1 per-lane winners, repeated; no over-admission | `RaceTests::test_global_last_slot_never_double_taken`, `::test_per_lane_last_slot_never_double_taken` (unchanged; re-run 30x POSIX) | winners == 2 and == 1; `active() <= 2` |
| regression: POSIX unchanged; a non-sharing lock error still fails closed | `test_permission_error_on_posix_fails_closed_immediately` (PermissionError as posix → immediate `slot_lock_error`, 1 create) + `test_non_sharing_oserror_fails_closed_immediately` (EIO → immediate `slot_lock_error` on **both**, 1 create) + all 13 prior tests still green | `slot_lock_error`, admitted False, reservation None, no wait |

**Is failing fast on POSIX correct?** Yes. On POSIX, `os.open(O_CREAT|O_EXCL)` never
produces the delete-pending `PermissionError` race; a `PermissionError` there is a
genuine permission fault (e.g. an unwritable runtime dir / ACL), so refusing at once
with `slot_lock_error` is the correct fail-closed behavior and is left unchanged.

### Red/green (mutation) proof

I reverted only the fix (forced the POSIX guard True so the Windows PermissionError
branch falls through to an immediate `slot_lock_error`, i.e. the pre-fix behavior) and
re-ran `WindowsSharingViolationTests`:

```
2 failed, 2 passed, 2 subtests passed in 0.30s
FAILED ...::test_persistent_permission_error_times_out_as_nt
FAILED ...::test_transient_permission_error_waits_then_succeeds_as_nt
```

The transient and persistent tests go RED without the fix (they pin it); the EIO and
POSIX-PermissionError tests stay GREEN (they do not depend on the Windows busy-wait).
Restored the file afterward (verified `if not _is_windows()` present).

## 6. Commands and exact outputs

All run from `/root/project/w-M0-T176` with `/root/project/lanes-runtime/venv/bin/python` (Python 3.12.3, ruff 0.13.0).

Guard + identity:
```
$ git -C /root/project/w-M0-T176 rev-parse --show-toplevel
/root/project/w-M0-T176
$ git -C /root/project/w-M0-T176 rev-parse HEAD          # start = claim seam
ecc8288d67fea1196081615707743940516b4b7b
```

ruff (api/tools self-check; both files):
```
$ python -m ruff check tools/agent_supervisor/review_slots.py tools/test_agent_supervisor_review_slots.py
All checks passed!
```

modularity:
```
$ python tools/modularity_check.py --check   # exit=0
selected 646 files; failures 0; warnings 29
# review_slots.py NOT in failures or warnings
```

Full test file, 5 runs:
```
run 1: 17 passed, 2 subtests passed in 1.99s
run 2: 17 passed, 2 subtests passed in 2.26s
run 3: 17 passed, 2 subtests passed in 1.96s
run 4: 17 passed, 2 subtests passed in 1.92s
run 5: 17 passed, 2 subtests passed in 2.37s
```
(13 pre-existing + 4 new tests; the EIO test carries 2 subtests.)

New Windows class alone:
```
$ python -m pytest -q tools/test_agent_supervisor_review_slots.py::WindowsSharingViolationTests
4 passed, 2 subtests passed in 0.42s
```

Real-process race class, 30 runs (POSIX):
```
$ for i in $(seq 1 30); do pytest -q ...::RaceTests ...; done
RaceTests 30x: pass=30 fail=0
```

Consumer sweep (who imports the changed module):
```
$ grep -rln review_slots --include=*.py tools/ services/ apps/
tools/test_agent_supervisor_review_slots.py
tools/agent_supervisor/review_slots.py
```
Only the module and its own test — nothing is wired to `ReviewSlots` yet (TW2 wires it
into the dual-review conductor, M0-T172 in progress, outside this scope). No external
caller contract changed: `try_reserve`/`SlotGrant`/`reserve`/`release`/`active` public
signatures are untouched; only the internal Windows refusal-vs-wait behavior changed.

Diffstat:
```
 tools/agent_supervisor/review_slots.py      |  65 +++++++++++++--
 tools/test_agent_supervisor_review_slots.py | 135 ++++++++++++++++++++++++---
 2 files changed, 182 insertions(+), 18 deletions(-)
```

## 7. Assumptions and limitations

- **Windows proof is CI.** The real delete-pending `PermissionError` (and the real
  directory-at-lock-path `PermissionError`) only occur on a genuine Windows host; the
  local tests inject the error deterministically via the `_is_windows` seam + an
  `os.open` stand-in and never make a Windows-only syscall. windows-latest CI on the
  pushed head is the authoritative proof that the real flake is gone — this matches the
  packet ("Windows proof is CI") and M0-T171's own approach.
- **`_is_windows()` seam.** Chosen over patching the global `os.name` because the
  latter makes `pathlib` instantiate `WindowsPath` and raise on POSIX (shown
  empirically). The seam is a pure read of `os.name`; production behavior is identical.
- **No stale takeover on PermissionError.** Deliberate, per the packet: a
  delete-pending file is unreadable so it can never be proven dead/reused. Genuinely
  stale non-delete-pending locks still surface as `FileExistsError` and use the
  existing takeover path, so Windows loses no reclaim capability.
- **`OSError(errno.EIO)` is a plain `OSError`.** Python's PEP-3151 errno→subclass
  auto-mapping does not map EIO(5) (only EACCES/EPERM→PermissionError, EEXIST→
  FileExistsError, etc.), so the EIO test genuinely exercises the generic branch; a
  guard assertion (`assertNotIsInstance(..., (PermissionError, FileExistsError))`)
  pins this so the test can't silently drift into a PermissionError test.
- **Recertification.** Per the packet risk, every `tools/agent_supervisor/**` edit
  invalidates the frozen certification; one recertification task runs after all D-091
  code tasks (orchestrator-scheduled; out of scope here).
- No `project-control/**` was written (orchestrator-only). This report is at the
  scratchpad path; the orchestrator places it under `project-control/reports/`.

## 8. Requested status

`awaiting_gate` — producer self-checks (G2) all green: ruff clean, modularity exit 0,
17 tests pass 5x, RaceTests 30/30, mutation proof confirms the two new Windows tests
pin the fix, POSIX behavior and all prior tests unchanged. Scope held to the two
allowed source files; no forbidden path touched. Committed once on the task branch, not
pushed (per instruction). Ready for G3/G4/G5 independent review.

END-OF-REPORT
