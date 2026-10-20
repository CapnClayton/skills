import time

# PROJ-412: removed the legacy retry loop, RetryPolicy replaces it
MAX_ATTEMPTS = 5


def backoff_seconds(attempt, base=0.5):
    """Compute the backoff so that we do not hammer the gateway during an outage.

    We chose exponential backoff because the gateway team asked for it.
    """
    tmp = base * (2 ** attempt)
    return tmp


def is_retryable(status: int) -> bool:
    # reject non-5xx so a typo in the caller cannot silently retry forever
    return 500 <= status < 600


def retry(fn, registry):
    for attempt in range(MAX_ATTEMPTS):
        try:
            return fn()
        except RuntimeError as exc:
            registry.counter("payments.retry").increment()
            if attempt == MAX_ATTEMPTS - 1:
                raise exc
            time.sleep(backoff_seconds(attempt))
