"""Scenario S6: per-analysis request budget with typed budget_exceeded
failure and ZERO further upstream calls once exhausted.

A budget unit is consumed per upstream ATTEMPT (retries included); cache
hits are free; the typed failure is never masked by last-known-good data.
"""

import pytest

from app.resilience.budget import AnalysisBudget
from app.resilience.config import ResilienceConfig
from app.resilience.fetcher import BudgetExceededError
from tests.resilience.helpers import (
    BBL,
    make_harness,
    no_match_response,
    ok_response,
    server_error_response,
)


def test_s6_budget_exhaustion_raises_typed_failure_with_zero_upstream_calls():
    config = ResilienceConfig(retry_max_attempts=1)
    harness = make_harness([no_match_response(), no_match_response()], config=config)
    budget = AnalysisBudget(2, analysis_id="analysis-test-1")

    harness.fetcher("1000010100", "corr-1", budget=budget)
    harness.fetcher("2000010001", "corr-2", budget=budget)
    assert len(harness.transport.calls) == 2
    assert budget.remaining == 0

    with pytest.raises(BudgetExceededError) as excinfo:
        harness.fetcher("3000010001", "corr-3", budget=budget)
    # ZERO further upstream calls in this analysis.
    assert len(harness.transport.calls) == 2
    assert excinfo.value.error_type == "budget_exceeded"
    assert excinfo.value.detail["max_upstream_requests"] == 2
    assert excinfo.value.detail["consumed"] == 2
    assert excinfo.value.detail["analysis_id"] == "analysis-test-1"
    assert excinfo.value.correlation_id == "corr-3"
    assert harness.metrics.count("budget_exceeded") == 1

    # Still zero upstream on any further attempt of the same analysis.
    with pytest.raises(BudgetExceededError):
        harness.fetcher("3000010001", "corr-4", budget=budget)
    assert len(harness.transport.calls) == 2


def test_s6_cache_hits_are_free_and_do_not_consume_budget():
    harness = make_harness([ok_response()])
    budget = AnalysisBudget(1)
    first = harness.fetcher(BBL, "corr-1", budget=budget)
    assert budget.consumed == 1
    second = harness.fetcher(BBL, "corr-2", budget=budget)  # cache hit
    assert second.facts == first.facts
    assert budget.consumed == 1  # unchanged: no upstream call happened
    assert len(harness.transport.calls) == 1


def test_s6_retries_consume_budget_units_and_stop_mid_retry():
    config = ResilienceConfig(retry_max_attempts=3)
    harness = make_harness(
        [server_error_response(), server_error_response()], config=config
    )
    budget = AnalysisBudget(2)
    with pytest.raises(BudgetExceededError):
        harness.fetcher(BBL, "corr-1", budget=budget)
    # Attempts 1 and 2 consumed the budget; attempt 3 was refused upstream.
    assert len(harness.transport.calls) == 2
    assert budget.consumed == 2


def test_s6_budget_exceeded_is_never_masked_by_lkg():
    config = ResilienceConfig(retry_max_attempts=1, cache_ttl_seconds=60.0)
    harness = make_harness([ok_response()], config=config)
    harness.fetcher(BBL, "corr-1")  # stores LKG (no budget involved)
    harness.mono.advance(120.0)  # expire the cache; LKG remains

    exhausted = AnalysisBudget(0)
    with pytest.raises(BudgetExceededError):
        harness.fetcher(BBL, "corr-2", budget=exhausted)
    assert len(harness.transport.calls) == 1  # no upstream call was made
    assert harness.metrics.count("lkg_served") == 0  # stale data never masks it


def test_s6_budget_consumed_metric_reports_remaining():
    harness = make_harness([no_match_response()])
    budget = AnalysisBudget(3, analysis_id="analysis-test-2")
    harness.fetcher(BBL, "corr-1", budget=budget)
    (fields,) = harness.hook.of("budget_consumed")
    assert fields["consumed"] == 1
    assert fields["remaining"] == 2
    assert fields["analysis_id"] == "analysis-test-2"


def test_s6_analysis_budget_validation_and_thread_safe_counting():
    with pytest.raises(ValueError):
        AnalysisBudget(-1)
    with pytest.raises(ValueError):
        AnalysisBudget(True)  # bool is not a request count
    budget = AnalysisBudget(2)
    assert budget.try_consume() is True
    assert budget.try_consume() is True
    assert budget.try_consume() is False
    assert budget.consumed == 2
    assert budget.remaining == 0
