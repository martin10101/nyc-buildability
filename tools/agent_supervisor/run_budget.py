#!/usr/bin/env python3
"""Durable owner-controlled run budgets for the bounded mode (D-023 item 1).

Qualifying evidence (AD-093 Section 0A.10, "a requirement explicitly listed in
this directive"): D-023-R011 asks for a genuinely bounded unattended mode, and
owner amendment D-023-R037 corrects it - the run length is OWNER-CONTROLLED and
a run may run as long as the owner wants, including with NO wall-clock limit at
all. This module is the whole of that budget model, and it is deliberately the
only place in the package that knows what "the run's remaining time" means.

The rules it implements, none of which a run can talk its way out of:

* **No hardcoded maximum, no default ceiling (D-023-R037).** The wall-clock
  budget is ``None`` unless the OWNER supplies one at launch. ``None`` means
  unlimited, and an unlimited run is never stopped by any timer here - there is
  no constant in this module (or anywhere else) that caps a run length, and
  `test_agent_supervisor_bounded_mode.py` asserts that at the source level.
* **Persisted at run start, durably.** The run identity, the budget EXACTLY as
  the owner supplied it, the run-start instant, and the monotonic counter
  snapshots are committed through the transactional journal (WAL +
  ``synchronous=FULL``, one ``BEGIN IMMEDIATE``/``COMMIT`` per write), so a
  power cut cannot lose them.
* **A crash-resume reloads the ORIGINAL start instant and the ORIGINAL budget.**
  Elapsed time and counters never reset, never extend, and never shrink from the
  run's own actions: the persisted record wins, a launch naming a DIFFERENT
  budget for the SAME run id is a fail-closed ``budget_conflict`` refusal (a new
  budget needs a new run id, which the owner chooses), and elapsed seconds are
  clamped to a persisted HIGH-WATER mark so a clock that jumps backwards - by
  NTP, by a manual change, or by a hostile local actor - can never hand the run
  more time than it has already used.
* **A present-but-unreadable record REFUSES; only an absent one starts fresh**
  (C1, G5 M1). A deleted record, a non-record payload, a null ``started_at_epoch``,
  an unreadable budget block, and a budget block that no longer matches its own
  recorded digest are five distinct corruptions, and every one of them is a typed,
  audited refusal. Treating any of them as a first launch is precisely how a run
  would reset its own bounds, and it would bypass every other guarantee here at
  once - because the record they defend would simply have been replaced.
* **A daily cap stays daily** (C4, G5 I2). Per-DAY tallies are evaluated against
  the CURRENT injected-clock day, so a peak from an earlier day neither exhausts
  the run nor is restored into a fresh breaker. Per-RUN tallies stay monotonic:
  they bound the run, not the day.
* **Deterministic exhaustion.** A budgeted run stops at exhaustion with an
  explicit machine-readable exit reason (`refusals.BUDGET_EXHAUSTED`), between
  cycles, never mid-unit (S11.2: the in-flight unit is always finished first).

CLOCK INJECTION. The package's style is deterministic and replayable: the
per-day circuit breakers take the UTC day FROM THE CALLER
(`circuit_breakers.record_daily`) so a breaker never reads a clock. The same
discipline applies here, with ONE injection seam: a `clock` callable returning
POSIX epoch seconds. `system_clock` is the production wiring; every test passes a
list-driven fake. Nothing else in this module calls `time`, and the UTC day the
per-day breakers need is DERIVED from that one seam
(`RunBudgetLedger.utc_day`), so the budget and the breakers can never disagree
about what day it is.
"""
from __future__ import annotations

import dataclasses
import datetime as _dt
import time
from typing import Any, Callable, Mapping

from .circuit_breakers import COUNTER_LIMITS, PER_DAY_COUNTERS
from .config import Limits
from .models import digest_of, to_utc_iso

#: The sentinel that means "the journal has NO run-budget row for this run".
#: `get_state` returns its default for a missing row, and a row holding JSON
#: `null` reads back as `None` - so `None` cannot be used to tell "absent" from
#: "present but empty". That distinction is the whole of C1: absent is a first
#: launch, present-but-unreadable is a refusal.
_ABSENT: Any = object()

#: The durable state key one run's budget record lives under.
RUN_BUDGET_KEY = "run_budget"

#: Bumped only together with a documented migration of the record shape.
BUDGET_RECORD_SCHEMA_VERSION = "1.0.0"

#: What an owner-supplied wall clock of `None` means, spelled out so callers read
#: as the directive does. There is NO companion "maximum" constant, by design
#: (D-023-R037): a ceiling here would be exactly the hardcoded limit the owner
#: prohibited.
UNLIMITED: None = None


class BudgetError(Exception):
    """A budget rule was violated. Always carries a code; never fails open."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


# --------------------------------------------------------------------------
# The clock seam
# --------------------------------------------------------------------------

#: A clock is any zero-argument callable returning POSIX epoch seconds (UTC).
Clock = Callable[[], float]


def system_clock() -> float:
    """POSIX epoch seconds. The ONE place the bounded mode reads a wall clock.

    Wall clock, not `time.monotonic()`, on purpose: a monotonic reading is
    meaningless across the process restart a crash-resume is made of, and the
    run-start instant must survive one. The hazard wall clock brings - it can go
    BACKWARDS - is handled where it belongs, in `RunBudgetLedger.elapsed`, which
    clamps to a durable high-water mark.
    """
    return time.time()


def utc_day_for(epoch_seconds: float) -> str:
    """The UTC calendar day (``YYYY-MM-DD``) of an epoch instant.

    The per-day circuit breakers refuse to accrue against an unknown day, and
    they take the day from their caller so they never read a clock. This is the
    single derivation the supervisor uses, so the budget's notion of "today" and
    the breakers' notion of "today" are the same fact.
    """
    return _dt.datetime.fromtimestamp(float(epoch_seconds),
                                      _dt.timezone.utc).strftime("%Y-%m-%d")


def utc_iso_for(epoch_seconds: float) -> str:
    """The package's fixed, sortable UTC stamp for an epoch instant."""
    return to_utc_iso(_dt.datetime.fromtimestamp(float(epoch_seconds),
                                                 _dt.timezone.utc))


# --------------------------------------------------------------------------
# The budget
# --------------------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class RunBudget:
    """One run's bounds EXACTLY as the owner supplied them.

    `wall_clock_seconds` is `None` for an unlimited run - the default, and the
    only default there is (D-023-R037). `counter_limits` are the existing S13.8
    circuit-breaker hard thresholds, carried here so the durable record states
    every bound the run is held to rather than only the temporal one.
    """

    wall_clock_seconds: float | None = None
    counter_limits: Mapping[str, int] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.wall_clock_seconds is not None:
            value = self.wall_clock_seconds
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise BudgetError(
                    "bad_wall_clock",
                    f"an owner-supplied wall-clock budget must be a number of seconds or "
                    f"omitted entirely for an unlimited run; got {value!r}")
            if value != value or value in (float("inf"), float("-inf")):
                raise BudgetError(
                    "bad_wall_clock",
                    "a wall-clock budget must be a finite number of seconds; an infinite "
                    "budget is expressed by omitting it (unlimited), never by a sentinel")
            if value <= 0:
                raise BudgetError(
                    "bad_wall_clock",
                    f"an owner-supplied wall-clock budget must be greater than zero "
                    f"seconds; got {value!r}. Omit it entirely for an unlimited run - "
                    f"zero is not how 'no limit' is spelled")
            object.__setattr__(self, "wall_clock_seconds", float(value))
        unknown = sorted(set(self.counter_limits) - set(COUNTER_LIMITS))
        if unknown:
            raise BudgetError(
                "unknown_counter_limit",
                f"the budget names counters that are not S13.8 breakers: {unknown}. A typo "
                f"must never become an unenforced bound")
        object.__setattr__(self, "counter_limits",
                           {name: int(self.counter_limits[name])
                            for name in sorted(self.counter_limits)})

    @classmethod
    def from_limits(cls, limits: Limits, *,
                    wall_clock_seconds: float | None = UNLIMITED) -> "RunBudget":
        """Build a budget from the immutable controller limits.

        The counter bounds come from the manifest-covered `config.toml` (S3.1:
        limits are immutable config a runtime model change can never move); the
        wall clock comes from the OWNER at launch and defaults to unlimited.
        """
        return cls(
            wall_clock_seconds=wall_clock_seconds,
            counter_limits={name: int(getattr(limits, field))
                            for name, field in COUNTER_LIMITS.items()})

    @property
    def unlimited(self) -> bool:
        """True when no owner wall-clock budget was supplied (D-023-R037)."""
        return self.wall_clock_seconds is None

    def to_dict(self) -> dict[str, Any]:
        return {"wall_clock_seconds": self.wall_clock_seconds,
                "unlimited": self.unlimited,
                "counter_limits": dict(self.counter_limits)}

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RunBudget":
        """Rebuild a budget from its persisted form, or raise a TYPED error.

        C5 (G5 I4): every corruption shape leaves through `BudgetError`. A bare
        `float()` on a tampered `wall_clock_seconds` used to raise
        ValueError/TypeError, which no caller catches, so a corrupt record
        surfaced as a traceback and the generic exit 1 that `refusals.py`
        numbers its codes from 10 specifically to avoid.
        """
        if not isinstance(data, Mapping):
            raise BudgetError("unreadable_budget",
                              "the persisted budget is not a record; refusing to guess it")
        raw = data.get("wall_clock_seconds", None)
        wall: float | None = None
        if raw is not None:
            try:
                wall = float(raw)
            except (TypeError, ValueError) as exc:
                raise BudgetError(
                    "unreadable_budget",
                    f"the persisted wall-clock budget {raw!r} is not a number "
                    f"({exc}); a budget that cannot be read is never guessed at") from exc
        limits = data.get("counter_limits", {}) or {}
        if not isinstance(limits, Mapping):
            raise BudgetError(
                "unreadable_budget",
                f"the persisted counter limits are {type(limits).__name__}, not a record")
        try:
            counter_limits = {str(name): int(value) for name, value in limits.items()}
        except (TypeError, ValueError) as exc:
            raise BudgetError(
                "unreadable_budget",
                f"a persisted counter limit is not an integer ({exc})") from exc
        return cls(wall_clock_seconds=wall, counter_limits=counter_limits)

    def digest(self) -> str:
        """Identity of the bounds themselves - what a resume is compared against."""
        return digest_of(self.to_dict())


@dataclasses.dataclass(frozen=True)
class BudgetVerdict:
    """Whether the run may take another step, and why not when it may not."""

    exhausted: bool
    dimension: str = ""
    reason_code: str = ""
    reason: str = ""
    elapsed_seconds: float = 0.0
    wall_clock_seconds: float | None = None
    remaining_seconds: float | None = None
    exhausted_counters: tuple[str, ...] = ()

    @property
    def unlimited(self) -> bool:
        return self.wall_clock_seconds is None

    def to_dict(self) -> dict[str, Any]:
        data = dataclasses.asdict(self)
        data["exhausted_counters"] = list(self.exhausted_counters)
        data["unlimited"] = self.unlimited
        return data


# --------------------------------------------------------------------------
# The durable ledger
# --------------------------------------------------------------------------


class RunBudgetLedger:
    """The durable record of one run's budget, elapsed time, and tallies.

    Open it with `start()`. On a first launch that persists the record; on a
    crash-resume it RELOADS the original, and the reloaded start instant and
    budget are authoritative for the rest of the run.
    """

    def __init__(self, journal: Any, *, run_id: str, budget: RunBudget,
                 clock: Clock = system_clock, audit: Any = None) -> None:
        self.journal = journal
        self.run_id = str(run_id)
        self.budget = budget
        self._clock = clock
        #: C6 (G5 I5): the hash-chained audit log. A budget that starts, resumes,
        #: or REFUSES is a security-relevant event, and `budget_conflict` is the
        #: canonical "a run tried to change its own bounds" tamper signal - the
        #: one a reviewer most wants in a tamper-evident log. Default None keeps
        #: every existing caller and test unchanged.
        self.audit = audit
        self._record: dict[str, Any] | None = None
        self._resumed = False

    # -- identity ------------------------------------------------------------

    def key(self) -> str:
        return f"{RUN_BUDGET_KEY}/{self.run_id}"

    @property
    def resumed(self) -> bool:
        """True when `start()` found an existing record for this run id."""
        return self._resumed

    def now(self) -> float:
        """The current instant, through the injected seam. Never `time.time()`."""
        return float(self._clock())

    def utc_day(self) -> str:
        """Today's UTC day, for `CircuitBreakers.record_daily` (one seam)."""
        return utc_day_for(self.now())

    # -- lifecycle -----------------------------------------------------------

    def _audit(self, event: str, **detail: Any) -> None:
        """Seal one budget lifecycle event. Never masks the caller's outcome.

        A damaged audit chain refuses new appends by design (`audit_log.append`).
        That refusal must not swallow a `budget_conflict` - the broken chain is
        itself recorded evidence, and the caller still fails closed - so the
        append is best-effort and the raise that follows it is not.
        """
        if self.audit is None:
            return
        try:
            self.audit.append(event, run_id=self.run_id,
                              policy_result=str(detail.get("reason_code", "") or event),
                              detail={"run_budget_key": self.key(), **detail})
        except Exception:  # pragma: no cover - a damaged chain is its own evidence
            pass

    def _refuse(self, code: str, message: str) -> "BudgetError":
        """Seal a budget refusal and return the typed error for the caller to raise."""
        self._audit("run_budget_refused", reason_code=code, message=message)
        return BudgetError(code, message)

    def start(self) -> dict[str, Any]:
        """Persist the budget at run start, or reload the ORIGINAL on a resume.

        Three outcomes, and exactly three (C1, G5 M1):

        1. **No record at all** - a legitimate first launch. Mint the record.
        2. **A well-formed started record** - a resume. Reload the ORIGINAL start
           instant and budget, and refuse `budget_conflict` if this launch names
           different bounds: a run's own arguments must never extend, shrink, or
           reset its budget mid-run. Different bounds are an owner act on a NEW
           run id.
        3. **A record that is present but not a well-formed started record** -
           REFUSE, typed and audited.

        Case 3 is the containment break this replaces. `start()` previously took
        the resume branch only on `isinstance(existing, Mapping) and
        existing.get("started_at_epoch") is not None`, so a DELETED record, a
        non-Mapping record, and an intact record with `started_at_epoch: null`
        all fell through to the fresh-start path - minting a new start instant,
        zeroing the elapsed high-water mark, emptying the tallies, and never
        reaching the `budget_conflict` check. The supervised worker runs as the
        same OS user on the same host and can write the journal, so nulling one
        JSON field bought it an unlimited run with fresh model-call,
        external-write, restart, and livelock allowances - defeating every other
        monotonicity guarantee at once, because the record they defend was simply
        replaced. "Present but unreadable" is now the opposite of "absent": the
        first is a refusal, only the second is a fresh start.
        """
        existing = self.journal.get_state(self.key(), _ABSENT)
        if existing is _ABSENT:
            return self._first_launch()
        return self._resume(existing)

    def _resume(self, existing: Any) -> dict[str, Any]:
        """Reload a PRESENT record, or refuse it. Never falls through to a fresh start."""
        if not isinstance(existing, Mapping):
            raise self._refuse(
                "budget_record_unreadable",
                f"the persisted run-budget record for {self.run_id!r} is "
                f"{type(existing).__name__}, not a record. A run-budget key that exists "
                f"but cannot be read is a REFUSAL, never a fresh budget - treating it as a "
                f"first launch is exactly how a run would reset its own bounds")
        started = existing.get("started_at_epoch")
        if not isinstance(started, (int, float)) or isinstance(started, bool) \
                or started != started or started <= 0:
            raise self._refuse(
                "budget_record_malformed",
                f"the persisted run-budget record for {self.run_id!r} carries "
                f"started_at_epoch={started!r}, which is not a real run-start instant. "
                f"The record is present, so this is a REFUSAL: a run that has already "
                f"started cannot re-start with a clean clock and empty tallies")
        record = dict(existing)
        try:
            persisted = RunBudget.from_dict(record.get("budget", {}) or {})
        except BudgetError as exc:
            raise self._refuse(
                "budget_record_malformed",
                f"the persisted run-budget record for {self.run_id!r} carries an "
                f"unreadable budget ({exc.message}); refusing rather than replacing it "
                f"with the bounds this launch happens to name") from exc
        # The record states its own budget digest. A mismatch means the budget
        # block was rewritten under the record, which the conflict check below
        # would otherwise accept as "the persisted budget".
        recorded_digest = str(record.get("budget_digest", "") or "")
        if recorded_digest and recorded_digest != persisted.digest():
            raise self._refuse(
                "budget_record_tampered",
                f"the persisted run-budget record for {self.run_id!r} does not match its "
                f"own recorded budget digest; the budget block was rewritten after the "
                f"run started")
        if persisted.digest() != self.budget.digest():
            raise self._refuse(
                "budget_conflict",
                f"run {self.run_id!r} was started with a different budget "
                f"({persisted.to_dict()}) and that persisted budget is authoritative; "
                f"a run can never extend, shrink, or reset its own bounds by "
                f"re-launching with new arguments. Start a NEW run id "
                f"(`--run-id <fresh-id>`) to use different bounds")
        # The ORIGINAL budget object, not the supplied one: identical by digest,
        # but the persisted record stays the single source.
        self.budget = persisted
        record["resumes"] = int(record.get("resumes", 0) or 0) + 1
        record["resumed_at_utc"] = to_utc_iso()
        self._resumed = True
        self._record = record
        self._commit()
        self._audit("run_budget_resumed", reason_code="run_budget_resumed",
                    resumes=record["resumes"],
                    started_at_utc=record.get("started_at_utc", ""),
                    budget_digest=self.budget.digest())
        return dict(record)

    def _first_launch(self) -> dict[str, Any]:
        """Mint the record. Reached ONLY when no run-budget key exists at all."""
        started = self.now()
        record = {
            "schema_version": BUDGET_RECORD_SCHEMA_VERSION,
            "run_id": self.run_id,
            "budget": self.budget.to_dict(),
            "budget_digest": self.budget.digest(),
            "started_at_epoch": started,
            "started_at_utc": utc_iso_for(started),
            "started_day_utc": utc_day_for(started),
            "elapsed_high_water_seconds": 0.0,
            "observed_at_epoch": started,
            "backwards_clock_observations": 0,
            "counters": {},
            "counter_day_utc": "",
            "resumes": 0,
            "exit_reason": "",
            "exit_detail": "",
            "stopped_at_utc": "",
        }
        self._resumed = False
        self._record = record
        self._commit()
        self._audit("run_budget_started", reason_code="run_budget_started",
                    started_at_utc=record["started_at_utc"],
                    budget=self.budget.to_dict(),
                    budget_digest=record["budget_digest"])
        return dict(record)

    def record(self) -> dict[str, Any]:
        """The durable record. `start()` must have run first (fail closed)."""
        if self._record is None:
            raise BudgetError(
                "budget_not_started",
                "the run budget was never started, so there is no persisted run-start "
                "instant to measure against; refusing to invent one")
        return self._record

    def _commit(self) -> None:
        """One transactional, durably flushed write of the whole record."""
        self.journal.set_state(self.key(), self.record())

    # -- elapsed time --------------------------------------------------------

    def elapsed(self) -> float:
        """Seconds since the PERSISTED run start, clamped to the high-water mark.

        The clamp is what makes elapsed time UNSHRINKABLE: a clock moved
        backwards (an NTP correction, a manual change, a hostile local edit)
        would otherwise hand a budgeted run back time it has already spent. The
        high-water mark only ever rises, and it is durable, so a crash-resume
        picks it back up.

        HONEST LIMIT, stated rather than papered over: a wall clock is the only
        measure that survives the process restart a crash-resume is made of, so
        a clock moved backwards cannot shrink elapsed but does PAUSE its accrual
        until the clock catches up to the mark. Each such observation is counted
        in the durable record (`backwards_clock_observations`) so the anomaly is
        visible to the operator instead of silently buying a run more time.
        """
        record = self.record()
        raw = self.now() - float(record["started_at_epoch"])
        high_water = float(record.get("elapsed_high_water_seconds", 0.0) or 0.0)
        return max(raw, high_water, 0.0)

    def observe(self) -> float:
        """Advance and PERSIST the elapsed high-water mark. Returns the elapsed.

        The loop calls this once per cycle - cheap enough at that cadence, and
        frequent enough that a crash loses at most one cycle of the mark.
        """
        record = self.record()
        now = self.now()
        raw = now - float(record["started_at_epoch"])
        high_water = float(record.get("elapsed_high_water_seconds", 0.0) or 0.0)
        if raw < high_water:
            record["backwards_clock_observations"] = int(
                record.get("backwards_clock_observations", 0) or 0) + 1
        elapsed = max(raw, high_water, 0.0)
        record["elapsed_high_water_seconds"] = elapsed
        record["observed_at_epoch"] = now
        self._commit()
        return elapsed

    # -- verdicts ------------------------------------------------------------

    def check(self) -> BudgetVerdict:
        """Is the run still within its budget? An unlimited run always is.

        This is the timer, and it is the ONLY timer: with no owner-supplied
        wall clock there is nothing here that can stop a run, however long it
        runs (D-023-R037).
        """
        record = self.record()
        elapsed = self.elapsed()
        wall = self.budget.wall_clock_seconds
        counters = self._exhausted_counters(record.get("counters", {}) or {})
        if counters:
            return BudgetVerdict(
                True, "counter", "budget_exhausted",
                f"the run reached its owner-set counter bound(s) {list(counters)}; the "
                f"tally is durable, so it neither resets nor shrinks on a resume. Start a "
                f"NEW run id (`--run-id <fresh-id>`) to begin a run with a fresh allowance; "
                f"the exhausted record stays intact as evidence",
                elapsed, wall, None, counters)
        if wall is None:
            return BudgetVerdict(
                False, "", "", "no owner wall-clock budget was supplied, so no timer can "
                               "stop this run (D-023-R037)",
                elapsed, None, None, ())
        if elapsed >= wall:
            return BudgetVerdict(
                True, "wall_clock", "budget_exhausted",
                f"the owner-set wall-clock budget of {wall:g}s is spent "
                f"({elapsed:.3f}s elapsed since {record['started_at_utc']}); the run stops "
                f"deterministically rather than continuing past what the owner authorized",
                elapsed, wall, 0.0, ())
        return BudgetVerdict(False, "", "", "", elapsed, wall, wall - elapsed, ())

    def stale_day(self) -> bool:
        """True when the persisted tallies were accrued on an EARLIER UTC day."""
        recorded = str(self.record().get("counter_day_utc", "") or "")
        return bool(recorded) and recorded != self.utc_day()

    def _exhausted_counters(self, counters: Mapping[str, Any]) -> tuple[str, ...]:
        """Counter names whose persisted tally has reached their owner-set bound.

        C4 (G5 I2): a PER-DAY counter is only exhausted while its window is still
        today's. The live `CircuitBreakers` rolls per-day counters to zero when
        the UTC day advances (`record_daily`), but the persisted record keeps the
        peak - so a run that hit `model_calls_per_day` on day 1 stayed "exhausted"
        forever on that run id, silently turning a DAILY cap into a permanent one
        and stranding exactly the long-running case D-023-R011 asks for. Per-RUN
        counters are unaffected and stay monotonic: they are bounds on the run,
        not on the day.
        """
        limits = self.budget.counter_limits
        stale = self.stale_day()
        return tuple(
            name for name in sorted(counters)
            if name in limits
            and not (stale and name in PER_DAY_COUNTERS)
            and int(counters.get(name, 0) or 0) >= int(limits[name]))

    # -- counter tallies -----------------------------------------------------

    def persist_counters(self, snapshot: Mapping[str, int], *, day: str = "") -> None:
        """Persist the breaker tallies alongside the budget (crash-resume input).

        Monotonic by construction: a persisted tally is never lowered, so a run
        cannot shrink its own counters by writing a smaller snapshot after a
        crash, a partial restore, or a rebuilt `CircuitBreakers`.
        """
        record = self.record()
        current = dict(record.get("counters", {}) or {})
        unknown = sorted(set(snapshot) - set(COUNTER_LIMITS))
        if unknown:
            raise BudgetError(
                "unknown_counter_limit",
                f"refusing to persist tallies for unknown counters {unknown}; an unknown "
                f"name is a typo, and a typo must never become an unenforced bound")
        # C4: when the UTC day advances, the PER-DAY tallies start from what the
        # live breaker now reads rather than from yesterday's peak - the breaker
        # has already rolled them, and max()-ing against the peak is what made a
        # daily cap permanent. Per-run counters stay monotonic.
        rolled = bool(day) and day != str(record.get("counter_day_utc", "") or "")
        for name, value in snapshot.items():
            if rolled and name in PER_DAY_COUNTERS:
                current[name] = int(value)
                continue
            current[name] = max(int(current.get(name, 0) or 0), int(value))
        record["counters"] = current
        if day:
            record["counter_day_utc"] = day
        self._commit()

    def restore_counters(self, breakers: Any) -> dict[str, int]:
        """Reconcile a fresh `CircuitBreakers` with the persisted tallies.

        A resumed run re-enters with the tallies it left behind. `restore` takes
        the HIGHER of the two per counter, so reconciliation can only ever raise
        a tally - a crash is never a way to earn back model calls, external
        writes, restarts, or livelock allowance.

        C4: PER-DAY tallies from an earlier UTC day are NOT restored - their
        window has rolled and the day's allowance is genuinely fresh. Per-run
        tallies are always restored.

        C5 (G5 I4): a tally name the record should not contain leaves through a
        TYPED `BudgetError`. `persist_counters` validates names on write; this
        validates them on READ, so a hand-edited record raises the same error
        class `cmd_start` maps to a structured refusal rather than a `BreakerError`
        that nothing catches.
        """
        record = self.record()
        counters = dict(record.get("counters", {}) or {})
        if breakers is None or not counters:
            return counters
        unknown = sorted(set(counters) - set(COUNTER_LIMITS))
        if unknown:
            raise self._refuse(
                "unknown_counter_limit",
                f"the persisted run-budget record names counters that are not S13.8 "
                f"breakers: {unknown}. A tally the breakers do not know is an unenforceable "
                f"bound, so the record is refused rather than partially restored")
        recorded_day = str(record.get("counter_day_utc", "") or "")
        stale = self.stale_day()
        restorable = {name: value for name, value in counters.items()
                      if not (stale and name in PER_DAY_COUNTERS)}
        try:
            breakers.restore(restorable, day="" if stale else recorded_day)
        except Exception as exc:  # BreakerError and anything else -> typed refusal
            raise self._refuse(
                "unrestorable_counters",
                f"the persisted tallies could not be reconciled with the breakers "
                f"({exc}); refusing rather than resuming with an unknown allowance") from exc
        return dict(breakers.snapshot())

    # -- termination ---------------------------------------------------------

    def finalize(self, *, exit_reason: str, detail: str = "") -> dict[str, Any]:
        """Record the machine-readable exit reason and the final elapsed/tallies.

        Safe cleanup means exactly this: the record is closed with the truth, and
        NOTHING else is touched. No durable hold, emergency stop, manual pause,
        usage-limit deadline, lock, or approval is cleared by a budget stop - a
        run running out of budget is not a reason to release a safety flag.
        """
        record = self.record()
        record["elapsed_high_water_seconds"] = self.elapsed()
        record["observed_at_epoch"] = self.now()
        record["exit_reason"] = str(exit_reason)
        record["exit_detail"] = str(detail)
        record["stopped_at_utc"] = to_utc_iso()
        self._commit()
        return dict(record)

    # -- reporting -----------------------------------------------------------

    def report(self) -> dict[str, Any]:
        """A read-only summary for the run payload and the audit record."""
        record = self.record()
        verdict = self.check()
        return {
            "run_id": self.run_id,
            "budget": self.budget.to_dict(),
            "budget_digest": self.budget.digest(),
            "started_at_utc": record["started_at_utc"],
            "elapsed_seconds": verdict.elapsed_seconds,
            "remaining_seconds": verdict.remaining_seconds,
            "unlimited": self.budget.unlimited,
            "resumed": self._resumed,
            "resumes": int(record.get("resumes", 0) or 0),
            "counters": dict(record.get("counters", {}) or {}),
            "counter_day_utc": record.get("counter_day_utc", ""),
            "counter_day_is_stale": self.stale_day(),
            "backwards_clock_observations": int(
                record.get("backwards_clock_observations", 0) or 0),
            "exhausted": verdict.exhausted,
            "exit_reason": record.get("exit_reason", ""),
        }


def load_record(journal: Any, run_id: str) -> dict[str, Any] | None:
    """Read one run's persisted budget record without opening a ledger."""
    data = journal.get_state(f"{RUN_BUDGET_KEY}/{run_id}", None)
    return dict(data) if isinstance(data, Mapping) else None
