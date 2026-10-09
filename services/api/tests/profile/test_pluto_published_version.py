"""PLUTO published-version adapter + assessment tests (queue item B-06 slice 2).

Offline. Proves the slice's point: a published-version probe lets the data
version check (``app.profile.data_versions``) fire "Out of date" instead of
reading every PLUTO fact as current.

- The adapter turns a probe result into a ``PublishedVersion`` keyed on the
  dataset NAME the pins use.
- A real recorded 26v2 lot (the 215-16 Northern benchmark PLUTO row) pinned at
  26v2, with the recorded F09 probe (26v1), stays current - the probe is older.
- A SYNTHETIC lot pinned at 26v1, with a SYNTHETIC probe at 26v2, becomes
  "Out of date" with a reason naming both versions.

Inputs marked SYNTHETIC are hand-made to exercise the rule's edges; they are
never presented as official data.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.connectors import pluto_soda
from app.connectors.pluto_version_probe import (
    VERSION_PROBE_URL,
    fetch_published_version,
)
from app.profile.builder import build_property_profile
from app.profile.data_versions import (
    STATUS_CURRENT,
    STATUS_OUT_OF_DATE,
    PinnedSource,
    PublishedVersion,
    assess_data_versions,
    pins_from_site_facts,
    published_from_pins,
)
from app.profile.pluto_published_version import published_version_from_probe
from app.profile.site_facts import PLUTO_DATASET_NAME, build_site_facts
from app.resilience.transport import TransportResponse

PLUTO_FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "pluto"
BENCHMARK = Path(__file__).resolve().parents[1] / "fixtures" / "benchmark_215_16_northern"
BENCHMARK_PLUTO_FILE = "pluto_64uk-42ks_bbl_4073340070.json"
BENCHMARK_BBL = "4073340070"
BENCHMARK_RETRIEVED_AT = "2026-09-30T06:10:20Z"
F09_SEEN_AT = "2026-07-16T20:26:53Z"


class FakeTransport:
    def __init__(self, script: list):
        self.script = list(script)
        self.calls: list[dict] = []

    def __call__(self, url: str, headers: dict, timeout: float) -> TransportResponse:
        self.calls.append({"url": url, "headers": dict(headers), "timeout": timeout})
        step = self.script.pop(0)
        if isinstance(step, Exception):
            raise step
        return step


def _no_sleep(_seconds: float) -> None:
    return None


def _f09_response() -> TransportResponse:
    fixture = json.loads((PLUTO_FIXTURES / "F09_version_select.json").read_text("utf-8"))
    return TransportResponse(status=fixture["http_status"], body=fixture["response_body_raw"])


def _recorded_f09_probe():
    """The recorded F09 probe (26v1, seen 2026-07-16) through the real connector."""
    return fetch_published_version(
        transport=FakeTransport([_f09_response()]), sleep=_no_sleep,
        clock=lambda: datetime(2026, 7, 16, 20, 26, 53, tzinfo=UTC), correlation_id="b06s2")


def _benchmark_pluto_pins() -> tuple[PinnedSource, ...]:
    """Pins for the real recorded 26v2 benchmark lot, through the connector,
    profile builder and B-02 site facts (the established offline pattern)."""
    moment = datetime.fromisoformat(BENCHMARK_RETRIEVED_AT)
    body = (BENCHMARK / BENCHMARK_PLUTO_FILE).read_text("utf-8")
    result = pluto_soda.fetch_by_bbl(
        BENCHMARK_BBL, transport=lambda url, headers, timeout: TransportResponse(200, body),
        sleep=_no_sleep, clock=lambda: moment, correlation_id="b06s2",
        observation_event_id="b06s2")
    facts = build_site_facts(build_property_profile(result, clock=lambda: moment)).facts
    return pins_from_site_facts(facts)


# --------------------------------------------------------------------------
# Adapter
# --------------------------------------------------------------------------


def test_adapter_maps_probe_to_published_version() -> None:
    published = published_version_from_probe(_recorded_f09_probe())
    assert isinstance(published, PublishedVersion)
    assert published.dataset == PLUTO_DATASET_NAME  # keyed on the name the pins use
    assert published.version == "26v1"
    assert published.seen_at == F09_SEEN_AT
    assert published.query_ref == VERSION_PROBE_URL


# --------------------------------------------------------------------------
# Assessment: current vs out_of_date
# --------------------------------------------------------------------------


def test_26v2_lot_with_the_f09_26v1_probe_stays_current() -> None:
    pins = _benchmark_pluto_pins()
    assert [pin.version for pin in pins] == ["26v2"]  # the recorded release
    published = published_version_from_probe(_recorded_f09_probe())
    # The probe (26v1) is older than the pinned 26v2, so the lot stays current.
    report = assess_data_versions(pins, (*published_from_pins(pins), published))
    (source,) = report.sources
    assert source.dataset == PLUTO_DATASET_NAME
    assert source.status == STATUS_CURRENT
    assert report.out_of_date is False and report.fact_exception_labels() == {}


def test_26v1_lot_with_a_26v2_probe_is_out_of_date_naming_both() -> None:
    # SYNTHETIC lot pinned at 26v1.
    pin = PinnedSource(PLUTO_DATASET_NAME, "26v1", "2026-07-16T20:26:46Z",
                       "query://synthetic-lot")
    # SYNTHETIC probe body publishing a newer 26v2 release, through the real probe.
    synthetic_probe = fetch_published_version(
        transport=FakeTransport([TransportResponse(200, json.dumps([{"version": "26v2"}]))]),
        sleep=_no_sleep, clock=lambda: datetime(2026, 10, 1, tzinfo=UTC),
        correlation_id="syn")
    published = published_version_from_probe(synthetic_probe)
    assert published.version == "26v2"

    report = assess_data_versions([pin], (published, *published_from_pins([pin])))
    (source,) = report.sources
    assert source.status == STATUS_OUT_OF_DATE
    assert source.latest_known_version == "26v2"
    assert source.exception_label == "Out of date"
    # The reason names both the in-use version and the newer published one.
    assert "26v1" in source.reason and "26v2" in source.reason
    assert report.out_of_date is True
    assert report.fact_exception_labels() == {}  # the synthetic pin carries no fact ids
