import time
from collections.abc import Callable
from functools import wraps
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError


DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 1.0

RETRYABLE_ERROR_CODES = {
    "Throttling",
    "ThrottlingException",
    "TooManyRequestsException",
    "RequestLimitExceeded",
    "ProvisionedThroughputExceededException",
    "RequestThrottled",
    "SlowDown",
    "InternalError",
    "ServiceUnavailable",
    "InternalFailure",
}


class AWSRetryError(Exception):
    """Raised when an AWS operation fails after all retry attempts."""


def is_retryable_error(error: Exception) -> bool:
    """
    Determine whether an AWS error should be retried.

    AWS throttling errors and temporary service failures are
    considered retryable. Other errors are not retried.
    """
    if isinstance(error, ClientError):
        error_code = error.response.get("Error", {}).get("Code", "")
        return error_code in RETRYABLE_ERROR_CODES

    if isinstance(error, BotoCoreError):
        return error.__class__.__name__ in {
        "EndpointConnectionError",
        "ConnectionClosedError",
        "ReadTimeoutError",
        "ConnectTimeoutError",
        }

    return False


def retry_aws_operation(
    max_retries: int = DEFAULT_MAX_RETRIES,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
):
    """
    Retry an AWS operation when a temporary or throttling error occurs.

    Args:
        max_retries: Maximum number of retries after the initial attempt.
        backoff_factor: Base delay in seconds between retry attempts.

    Returns:
        A decorator that retries the wrapped AWS operation.

    Raises:
        ValueError: If retry configuration is invalid.
        AWSRetryError: If all retry attempts are exhausted.
    """
    if max_retries < 0:
        raise ValueError("max_retries cannot be negative.")

    if backoff_factor < 0:
        raise ValueError("backoff_factor cannot be negative.")

    def decorator(func: Callable[..., Any]):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except Exception as exc:
                    if not is_retryable_error(exc):
                        raise

                    if attempt == max_retries:
                        raise AWSRetryError(
                            f"AWS operation '{func.__name__}' failed "
                            f"after {max_retries} retries."
                        ) from exc

                    delay = backoff_factor * (2 ** attempt)
                    time.sleep(delay)

        return wrapper

    return decorator