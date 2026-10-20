from payments.retry import backoff_seconds
from payments.retry import retry
from payments.testing import SimpleRegistry
from payments.testing import fail_once


def test_backoff_doubles():
    """Backoff should double each attempt."""
    assert backoff_seconds(1) == 1.0
    assert backoff_seconds(2) == 2.0


def test_retry_records_metric():
    registry = SimpleRegistry()
    retry(fail_once, registry=registry)
    assert registry.counter("payments.retry").count == 1


def test_retry_succeeds_after_one_failure():
    registry = SimpleRegistry()
    result = retry(fail_once, registry=registry)
    assert result == "ok"
