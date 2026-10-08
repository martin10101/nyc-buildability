"""Direct test of ``app.api.v1.study_live_geometry.live_outline_provider`` (backlog DB-190 a;
task M5-T138, scenario S12).

The live outline provider had no direct test; mounting the results route is its WATCH trigger
(the route's live default binds it behind LIVE_SPATIAL_PROVIDER_ENABLED). This proves, OFFLINE,
that it returns the prepared tax-map outline from a recorded MapPLUTO response, and returns
NOTHING (None) on a typed connector failure or an outline it cannot prepare - never a fabricated
outline and never a raise. The module itself is READ-ONLY here: only this test is added.
"""

from __future__ import annotations

from app.api.v1.study_live_geometry import live_outline_provider
from app.connectors.mappluto_geometry_arcgis import (
    LotGeometryResult,
    MapPlutoGeometryConnectorError,
)
from app.spatial.site_geometry.outline import PreparedOutline
from tests.spatial._northern_replay import replay_lot_geometry


def test_live_outline_provider_returns_the_prepared_outline_from_a_recorded_response() -> None:
    """A recorded MapPLUTO lot-geometry response -> the provider returns a PreparedOutline for the
    lot (the EPSG:2263 outline prepared for measurement)."""
    provider = live_outline_provider(fetch_lot=lambda bbl, cid: replay_lot_geometry())
    prepared = provider("4073340070", "test-outline")
    assert isinstance(prepared, PreparedOutline)
    # the prepared outline is a usable polygon (a positive area), never empty
    assert prepared.polygon.area > 0


def test_live_outline_provider_returns_none_on_a_typed_connector_error() -> None:
    """A typed MapPLUTO connector failure -> the provider returns None (no usable outline, the
    reach stays unknown), never a raise and never a fabricated outline."""

    def failing_fetch(bbl: str, correlation_id: str) -> LotGeometryResult:
        raise MapPlutoGeometryConnectorError("recorded failure", correlation_id=correlation_id)

    provider = live_outline_provider(fetch_lot=failing_fetch)
    assert provider("4073340070", "test-outline") is None


def test_live_outline_provider_returns_none_when_the_outline_is_refused() -> None:
    """A lot-geometry response with no usable feature -> the MapPLUTO outline adapter refuses it,
    so the provider returns None rather than a fabricated outline."""
    recorded = replay_lot_geometry()
    # An otherwise-recorded result with no features: lot_outline_from_mappluto refuses it.
    import dataclasses

    empty = dataclasses.replace(recorded, features=())
    provider = live_outline_provider(fetch_lot=lambda bbl, cid: empty)
    assert provider("4073340070", "test-outline") is None
