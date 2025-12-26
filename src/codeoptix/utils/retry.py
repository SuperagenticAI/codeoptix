"""Retry utilities for resilient API calls."""

import time
from collections.abc import Callable
from functools import wraps

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


class RetryableError(Exception):
    """Base exception for retryable errors."""


class APIError(RetryableError):
    """API-related errors that can be retried."""


class RateLimitError(APIError):
    """Rate limit errors."""


class TimeoutError(APIError):
    """Timeout errors."""


def retry_with_backoff(
    max_attempts: int = 3,
    initial_wait: float = 1.0,
    max_wait: float = 60.0,
    exponential_base: float = 2.0,
    retry_on: tuple[type[Exception], ...] | None = None,
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds
        exponential_base: Base for exponential backoff
        retry_on: Tuple of exception types to retry on (default: APIError, RateLimitError)

    Returns:
        Decorated function with retry logic
    """
    if retry_on is None:
        retry_on = (APIError, RateLimitError, TimeoutError)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            wait_time = initial_wait

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except retry_on as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        # Calculate wait time with exponential backoff
                        wait_time = min(initial_wait * (exponential_base**attempt), max_wait)
                        time.sleep(wait_time)
                    else:
                        # Last attempt failed
                        raise
                except Exception:
                    # Non-retryable exception
                    raise

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator


def retry_llm_call(max_attempts: int = 3, initial_wait: float = 1.0, max_wait: float = 60.0):
    """
    Specialized retry decorator for LLM API calls.

    Handles common LLM API errors:
    - Rate limiting
    - Timeouts
    - Temporary service errors

    Args:
        max_attempts: Maximum number of retry attempts
        initial_wait: Initial wait time in seconds
        max_wait: Maximum wait time in seconds

    Returns:
        Decorated function with LLM-specific retry logic
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=initial_wait, max=max_wait),
        retry=retry_if_exception_type((APIError, RateLimitError, TimeoutError)),
        reraise=True,
    )


def handle_api_error(error: Exception, context: str | None = None) -> str:
    """
    Generate user-friendly error messages from API errors.

    Args:
        error: The exception that occurred
        context: Optional context about where the error occurred

    Returns:
        User-friendly error message
    """
    error_type = type(error).__name__
    error_msg = str(error)

    # Common error patterns
    if "rate limit" in error_msg.lower() or "429" in error_msg:
        return f"Rate limit exceeded. Please wait before retrying. {context or ''}"
    if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
        return f"Request timed out. The service may be slow. Try again. {context or ''}"
    if "authentication" in error_msg.lower() or "401" in error_msg or "403" in error_msg:
        return f"Authentication failed. Please check your API key. {context or ''}"
    if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
        return f"API quota exceeded. Please check your account limits. {context or ''}"
    return f"API error ({error_type}): {error_msg}. {context or ''}"
