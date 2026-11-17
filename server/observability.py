"""Optional error reporting to a Sentry-compatible backend (GlitchTip).

The deployment supplies `SENTRY_DSN` and `SENTRY_ENVIRONMENT`. Reporting is a
no-op when the DSN is unset, and initialisation failures are swallowed so
telemetry can never stop the server from starting.

    from .observability import init_sentry, capture_exception

    init_sentry()
    ...
    capture_exception(exc)
"""

from __future__ import annotations

import os

_initialised = False


def init_sentry() -> bool:
    """Initialise the Sentry SDK if `SENTRY_DSN` is set.

    Returns whether reporting is active. Never raises: a malformed DSN or a
    missing package just leaves the server running without telemetry.
    """
    global _initialised
    if _initialised:
        return True

    dsn = (os.getenv("SENTRY_DSN") or "").strip()
    if not dsn:
        return False

    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            environment=os.getenv("SENTRY_ENVIRONMENT") or None,
            traces_sample_rate=0.0,
            send_default_pii=False,
        )
    except Exception:
        return False

    _initialised = True
    return True


def capture_exception(exc: BaseException) -> None:
    """Report an exception if reporting is active; otherwise do nothing."""
    if not _initialised:
        return
    try:
        import sentry_sdk

        sentry_sdk.capture_exception(exc)
    except Exception:
        pass
