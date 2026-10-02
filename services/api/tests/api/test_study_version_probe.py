"""The PLUTO published-version probe in study assembly (lane C, request B-4).

Offline and deterministic. Three layers are proven here, none touching the
network:

- :func:`app.api.v1.pluto_version_cache.published_versions_for_study` - the
  published-on-record set: a success ADDS the probe observation; any typed probe
  failure FAILS CLOSED (drops the probe AND the PLUTO self-observations, keeping
  other datasets) and logs; no probe / no PLUTO pin is retrieval-only.
- :class:`app.api.v1.pluto_version_cache.CachedVersionProbe` - a 15-minute,
  one-entry, thread-safe TTL cache that caches only successes (never failures),
  with an injected clock.
- :func:`app.api.v1.study_inputs.assemble_study_inputs` through
  ``pluto_study_inputs_provider`` with an injected probe: a probe NEWER than the
  pin -> ``out_of_date`` naming both versions; the benchmark pin (26v2) newer than
  the probe (26v1) -> still ``current``; any probe failure -> the PLUTO facts
  ``version_unknown`` while the study still assembles.
"""

from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.api.v1.pluto_version_cache import (
    VERSION_PROBE_TTL_SECONDS,
    CachedVersionProbe,
    published_versions_for_study,
)
from app.api.v1.study_inputs import pluto_study_inputs_provider
from app.connectors.pluto_soda import (
    DATASET_ID,
    SOURCE_ID,
    SourceTimeoutError,
    SourceUnavailableError,
    TransportResponse,
    fetch_by_bbl,
)
from app.connectors.pluto_version_probe import PlutoPublishedVersion
from app.profile.data_versions import (
    STATUS_CURRENT,
    STATUS_OUT_OF_DATE,
    STATUS_VERSION_UNKNOWN,
    PinnedSource,
    PublishedVersion,
    assess_data_versions,
    pins_from_site_facts,
)
from app.profile.site_facts import PLUTO_DATASET_NAME

FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
NORTHERN_BBL = "4073340070"
FIXED_CLOCK = lambda: datetime(2026, 9, 30, 12, 0, 0, tzinfo=UTC)  # noqa: E731
LANE_B_ON = {"LANE_B_ENABLED": "1"}
OTHER_DATASET = "DOF sales (w2pb-icbu)"


def _northern_body() -> str:
    return (FIXTURE_DIR / "pluto_64uk-42ks_bbl_4073340070.json").read_text(encoding="utf-8")


def _body_with_pluto_version(version: str) -> str:
    """The Northern body with every record's ``version`` set to ``version`` (a
    clearly-synthetic older-release variant; only the pin version is changed)."""
    records = json.loads(_northern_body())
    for record in records:
        record["version"] = version
    return json.dumps(records)


def _fetcher_over(body: str):
    def fetcher(bbl: str, correlation_id: str):
        return fetch_by_bbl(
            bbl,
            transport=lambda url, headers, timeout: TransportResponse(200, body),
            sleep=lambda seconds: None,
            clock=FIXED_CLOCK,
            correlation_id=correlation_id,
        )

    return fetcher


def _probe_returning(version: str):
    """A probe that returns a published PLUTO release ``version`` with provenance."""

    def probe(correlation_id: str) -> PlutoPublishedVersion:
        return PlutoPublishedVersion(
            dataset_id=DATASET_ID,
            version=version,
            seen_at="2026-09-30T12:00:00Z",
            query_ref="https://example/probe",
            source_id=SOURCE_ID,
            correlation_id=correlation_id,
        )

    return probe


def _failing_probe(exc: Exception):
    def probe(correlation_id: str):
        raise exc

    return probe


def _pluto_pin(version: str) -> PinnedSource:
    return PinnedSource(
        dataset=PLUTO_DATASET_NAME,
        version=version,
        retrieved_at="2026-09-30T12:00:00Z",
        query_ref="https://example/pluto",
        fact_ids=("lot_area",),
    )


def _other_pin() -> PinnedSource:
    return PinnedSource(
        dataset=OTHER_DATASET,
        version="socrata-rows-2026-09-01T00:00:00Z",
        retrieved_at="2026-09-30T12:00:00Z",
        query_ref="https://example/dof",
        fact_ids=("sale_price",),
    )


# ---------------------------------------------------------------------------
# published_versions_for_study: success / fail-closed / retrieval-only
# ---------------------------------------------------------------------------
def test_success_adds_the_probe_observation() -> None:
    pins = (_pluto_pin("26v1"),)
    published = published_versions_for_study(
        pins, version_probe=_probe_returning("26v2"), correlation_id="cid"
    )
    # Retrieval self-observation (26v1) PLUS the probe (26v2), keyed on PLUTO.
    pluto = [pv for pv in published if pv.dataset == PLUTO_DATASET_NAME]
    assert {pv.version for pv in pluto} == {"26v1", "26v2"}


def test_failure_drops_probe_and_pluto_self_obs_keeps_other(caplog) -> None:
    pins = (_pluto_pin("26v1"), _other_pin())
    with caplog.at_level(logging.WARNING, logger="app.api.v1.pluto_version_cache"):
        published = published_versions_for_study(
            pins,
            version_probe=_failing_probe(SourceTimeoutError("down", correlation_id="cid")),
            correlation_id="cid-fail",
        )
    # Fail closed: NO PLUTO observation on record (neither probe nor self-obs), so
    # the PLUTO pin will read version_unknown. The OTHER dataset is untouched.
    assert all(pv.dataset != PLUTO_DATASET_NAME for pv in published)
    assert any(pv.dataset == OTHER_DATASET for pv in published)
    # Surfaced: a WARNING with the correlation id and the bounded error type only.
    assert "study_pluto_version_probe_failed" in caplog.text
    assert "cid-fail" in caplog.text
    assert "timeout" in caplog.text


def test_no_probe_is_retrieval_only() -> None:
    pins = (_pluto_pin("26v1"),)
    published = published_versions_for_study(pins, version_probe=None, correlation_id="cid")
    assert [pv.version for pv in published] == ["26v1"]


def test_no_pluto_pin_does_not_call_the_probe() -> None:
    called: list[str] = []

    def probe(correlation_id: str):
        called.append(correlation_id)
        raise AssertionError("probe must not run without a PLUTO pin")

    published = published_versions_for_study(
        (_other_pin(),), version_probe=probe, correlation_id="cid"
    )
    assert called == []
    assert [pv.dataset for pv in published] == [OTHER_DATASET]


# ---------------------------------------------------------------------------
# CachedVersionProbe: 15-min TTL, one entry, success-only, injected clock
# ---------------------------------------------------------------------------
class _CountingProbe:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, correlation_id: str) -> PlutoPublishedVersion:
        self.calls += 1
        return _probe_returning("26v1")(correlation_id)


def test_cache_serves_within_ttl_and_re_probes_after_expiry() -> None:
    now = [1000.0]
    inner = _CountingProbe()
    cache = CachedVersionProbe(inner, clock=lambda: now[0])

    first = cache("c1")
    assert inner.calls == 1
    # Second call well within 15 minutes: served from cache, no re-probe.
    now[0] += VERSION_PROBE_TTL_SECONDS - 1
    second = cache("c2")
    assert inner.calls == 1
    assert second is first
    # Past the TTL: re-probe.
    now[0] += 2
    cache("c3")
    assert inner.calls == 2


def test_cache_never_caches_a_failure() -> None:
    now = [0.0]
    calls = {"n": 0}

    def flaky(correlation_id: str) -> PlutoPublishedVersion:
        calls["n"] += 1
        if calls["n"] == 1:
            raise SourceUnavailableError("down", correlation_id=correlation_id)
        return _probe_returning("26v1")(correlation_id)

    cache = CachedVersionProbe(flaky, clock=lambda: now[0])
    with pytest.raises(SourceUnavailableError):
        cache("c1")
    # The failure was NOT cached: the next call (same instant) re-probes and succeeds.
    assert cache("c2").version == "26v1"
    assert calls["n"] == 2


def test_cache_is_bounded_to_one_entry_and_thread_safe() -> None:
    inner = _CountingProbe()
    cache = CachedVersionProbe(inner, clock=lambda: 0.0)
    results: list[PlutoPublishedVersion] = []
    barrier = threading.Barrier(8)

    def worker() -> None:
        barrier.wait()
        results.append(cache("c"))

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    # Every caller gets a valid observation; the single slot never corrupts.
    assert len(results) == 8
    assert all(r.version == "26v1" for r in results)
    # One entry only: the second slot read (after warm-up) does not re-probe.
    warm = inner.calls
    cache("c")
    assert inner.calls == warm


# ---------------------------------------------------------------------------
# assemble_study_inputs via the provider with an injected probe
# ---------------------------------------------------------------------------
def _facts(provider, bbl=NORTHERN_BBL, correlation_id="cid", selected=None):
    inputs = provider(bbl, correlation_id, selected=selected) if selected else provider(
        bbl, correlation_id
    )
    return {fact["key"]: fact for fact in inputs.site_facts}


def test_probe_newer_than_benchmark_pin_is_current() -> None:
    # Benchmark pin 26v2 vs probe 26v1: nothing newer than the pin -> current.
    provider = pluto_study_inputs_provider(
        _fetcher_over(_northern_body()),
        clock=FIXED_CLOCK,
        env=LANE_B_ON,
        version_probe=_probe_returning("26v1"),
    )
    facts = _facts(provider)
    vc = facts["lot_area"]["source"]["version_check"]
    assert vc["status"] == STATUS_CURRENT
    assert vc["latest_known_version"] == "26v2"


def test_older_pin_vs_probe_is_out_of_date_naming_both_versions() -> None:
    # SYNTHETIC older pin (24v1) vs probe 26v1: a newer release is published.
    provider = pluto_study_inputs_provider(
        _fetcher_over(_body_with_pluto_version("24v1")),
        clock=FIXED_CLOCK,
        env=LANE_B_ON,
        version_probe=_probe_returning("26v1"),
    )
    facts = _facts(provider)
    vc = facts["lot_area"]["source"]["version_check"]
    assert vc["status"] == STATUS_OUT_OF_DATE
    assert vc["latest_known_version"] == "26v1"
    # The reason names BOTH the in-use pin and the newer published version.
    assert "24v1" in vc["reason"] and "26v1" in vc["reason"]


def test_probe_failure_fails_closed_to_version_unknown(caplog) -> None:
    provider = pluto_study_inputs_provider(
        _fetcher_over(_northern_body()),
        clock=FIXED_CLOCK,
        env=LANE_B_ON,
        version_probe=_failing_probe(
            SourceUnavailableError("down", correlation_id="x")
        ),
    )
    with caplog.at_level(logging.WARNING, logger="app.api.v1.pluto_version_cache"):
        inputs = provider(NORTHERN_BBL, "cid-vu")
    facts = {fact["key"]: fact for fact in inputs.site_facts}
    # The study STILL assembled (no exception), but the PLUTO facts are now
    # version_unknown - never a probe-masked "current".
    vc = facts["lot_area"]["source"]["version_check"]
    assert vc["status"] == STATUS_VERSION_UNKNOWN
    assert inputs.site is not None  # assembly succeeded despite the probe outage
    assert "study_pluto_version_probe_failed" in caplog.text


def test_fail_closed_mechanism_matches_the_rule_directly() -> None:
    # Guard the fail-closed MECHANISM against the rule: a PLUTO pin with NO PLUTO
    # observation on record is version_unknown; add back the self-observation and it
    # is current - proving the drop is what moves the status (red/green).
    pin = _pluto_pin("26v2")
    dropped = assess_data_versions((pin,), ())
    restored = assess_data_versions((pin,), (PublishedVersion(PLUTO_DATASET_NAME, "26v2",
                                                              pin.retrieved_at, pin.query_ref),))
    assert dropped.sources[0].status == STATUS_VERSION_UNKNOWN
    assert restored.sources[0].status == STATUS_CURRENT


def test_pins_from_recorded_pack_carry_the_pluto_dataset_name() -> None:
    # The drop filter keys on PLUTO_DATASET_NAME; prove the recorded pack's pins
    # actually carry it (else the fail-closed filter would silently match nothing).
    from app.profile.builder import build_property_profile
    from app.profile.site_facts import build_site_facts

    result = _fetcher_over(_northern_body())(NORTHERN_BBL, "cid")
    facts = build_site_facts(build_property_profile(result, clock=FIXED_CLOCK)).facts
    pins = pins_from_site_facts(facts)
    assert any(pin.dataset == PLUTO_DATASET_NAME for pin in pins)
