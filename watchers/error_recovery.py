#!/usr/bin/env python3
"""
Error Recovery System for AI Employee

Provides retry logic, circuit breakers, and graceful degradation strategies.

Usage:
    @retry_with_backoff(max_attempts=3, base_delay=2, max_delay=60)
    def risky_function():
        # Will retry on transient errors
        pass

    breaker = CircuitBreaker(failure_threshold=5, timeout=60)
    if breaker.can_execute():
        try:
            # Execute operation
            breaker.record_success()
        except Exception:
            breaker.record_failure()
"""

import time
import logging
from enum import Enum
from typing import Callable, Optional, TypeVar
from functools import wraps
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ErrorCategory(Enum):
    """Categories of errors for different handling strategies"""
    TRANSIENT = "transient"  # Temporary failures (retry)
    AUTHENTICATION = "authentication"  # Auth failures (human needed)
    LOGIC = "logic"  # Logic errors (human review)
    DATA = "data"  # Data errors (quarantine)
    SYSTEM = "system"  # System errors (restart)


class TransientError(Exception):
    """Exception for transient failures that should be retried"""
    pass


class AuthenticationError(Exception):
    """Exception for authentication failures"""
    pass


class RetryConfig:
    """Configuration for retry behavior"""
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 2,
        max_delay: float = 60,
        exponential_base: float = 2
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base


class CircuitBreaker:
    """
    Circuit Breaker pattern to prevent cascading failures

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Circuit is tripped, requests fail immediately
    - HALF_OPEN: Testing if service has recovered
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        """
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (half-open state)
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if operation should be allowed based on circuit state"""
        if self.state == "CLOSED":
            return True

        elif self.state == "OPEN":
            # Check if timeout has elapsed
            if (datetime.now() - self.last_failure_time).total_seconds() >= self.timeout:
                logger.info("Circuit breaker: Moving to HALF_OPEN state")
                self.state = "HALF_OPEN"
                return True
            return False

        elif self.state == "HALF_OPEN":
            # Allow one request through to test
            return True

        return False

    def record_success(self):
        """Record a successful operation"""
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker: Service recovered, moving to CLOSED")
            self.state = "CLOSED"
            self.failure_count = 0
        elif self.state == "CLOSED":
            self.failure_count = 0

    def record_failure(self):
        """Record a failed operation"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            logger.warning(f"Circuit breaker: Threshold reached ({self.failure_threshold}), opening circuit")
            self.state = "OPEN"


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 2,
    max_delay: float = 60,
    exponential_base: float = 2
):
    """
    Decorator for retrying functions with exponential backoff

    Usage:
        @retry_with_backoff(max_attempts=3, base_delay=2, max_delay=60)
        def fetch_data():
            return requests.get("https://api.example.com")
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            config = RetryConfig(max_attempts, base_delay, max_delay, exponential_base)
            last_exception = None

            for attempt in range(1, config.max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Check if this is a transient error
                    if not _is_transient_error(e):
                        # Non-transient error, don't retry
                        raise

                    if attempt < config.max_attempts:
                        # Calculate delay with exponential backoff
                        delay = min(
                            config.base_delay * (config.exponential_base ** (attempt - 1)),
                            config.max_delay
                        )

                        logger.warning(
                            f"Retry {attempt}/{config.max_attempts} for {func.__name__}: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Failed after {config.max_attempts} attempts: {e}"
                        )

            raise last_exception

        return wrapper
    return decorator


def _is_transient_error(error: Exception) -> bool:
    """
    Determine if an error is transient (should retry) or permanent

    Transient errors:
    - Timeout
    - Connection refused (temporary)
    - Rate limit
    - Network unreachable (temporary)
    """
    error_str = str(error).lower()

    # Transient error indicators
    transient_keywords = [
        'timeout',
        'timed out',
        'connection reset',
        'connection refused',
        'rate limit',
        'too many requests',
        'service unavailable',
        'temporary',
        'try again',
        'network unreachable'
    ]

    return any(keyword in error_str for keyword in transient_keywords)


def categorize_error(error: Exception) -> ErrorCategory:
    """
    Categorize an error for appropriate handling strategy

    Args:
        error: The exception to categorize

    Returns:
        ErrorCategory enum value
    """
    error_str = str(error).lower()

    # Check by exception type first
    # Transient error types
    transient_types = (
        TimeoutError,
        ConnectionError,
        ConnectionRefusedError,
        ConnectionResetError,
    )
    if isinstance(error, transient_types):
        return ErrorCategory.TRANSIENT

    # Authentication error types
    auth_types = (
        PermissionError,
    )
    if isinstance(error, auth_types):
        return ErrorCategory.AUTHENTICATION

    # Then check by error message content
    # Check for authentication errors
    auth_keywords = ['authentication', 'unauthorized', 'invalid token', 'access denied', 'forbidden']
    if any(keyword in error_str for keyword in auth_keywords):
        return ErrorCategory.AUTHENTICATION

    # Check for transient errors
    if _is_transient_error(error):
        return ErrorCategory.TRANSIENT

    # Check for data errors
    data_keywords = ['corrupt', 'invalid format', 'missing required', 'parse error']
    if any(keyword in error_str for keyword in data_keywords):
        return ErrorCategory.DATA

    # Check for system errors
    system_keywords = ['out of memory', 'disk full', 'no space left']
    if any(keyword in error_str for keyword in system_keywords):
        return ErrorCategory.SYSTEM

    # Default to logic error (human review needed)
    return ErrorCategory.LOGIC


def handle_error_with_recovery(error: Exception, context: str = "") -> dict:
    """
    Handle an error with appropriate recovery strategy

    Args:
        error: The exception that occurred
        context: Additional context about where error occurred

    Returns:
        Dictionary with handling strategy and action
    """
    category = categorize_error(error)

    if category == ErrorCategory.TRANSIENT:
        return {
            "category": "transient",
            "action": "retry",
            "message": f"Transient error in {context}: {error}. Will retry with backoff."
        }

    elif category == ErrorCategory.AUTHENTICATION:
        return {
            "category": "authentication",
            "action": "alert_human",
            "message": f"Authentication failed in {context}: {error}. Human intervention required.",
            "urgent": True
        }

    elif category == ErrorCategory.DATA:
        return {
            "category": "data",
            "action": "quarantine",
            "message": f"Data error in {context}: {error}. Item quarantined for review."
        }

    elif category == ErrorCategory.SYSTEM:
        return {
            "category": "system",
            "action": "restart",
            "message": f"System error in {context}: {error}. Watchdog will restart process.",
            "urgent": True
        }

    else:  # LOGIC
        return {
            "category": "logic",
            "action": "human_review",
            "message": f"Logic error in {context}: {error}. Human review required."
        }


class GracefulDegradation:
    """
    Manages graceful degradation when services are unavailable
    """

    def __init__(self, vault_path):
        self.vault_path = vault_path
        self.queue_path = vault_path / "Failed" / "Queue"
        self.queue_path.mkdir(parents=True, exist_ok=True)

    def queue_for_later(self, item_data: dict, service_name: str) -> bool:
        """
        Queue an item for later processing when service is down

        Args:
            item_data: Data to process later
            service_name: Name of service that's down (e.g., "gmail", "odoo")

        Returns:
            True if queued successfully
        """
        try:
            import json
            from datetime import datetime

            queue_file = self.queue_path / f"{service_name}_queue_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            queue_data = {
                "queued_at": datetime.now().isoformat(),
                "service": service_name,
                "data": item_data
            }

            queue_file.write_text(json.dumps(queue_data, indent=2), encoding='utf-8')
            logger.info(f"Queued item for {service_name}: {queue_file.name}")
            return True

        except Exception as e:
            logger.error(f"Failed to queue item: {e}")
            return False

    def process_queue(self, service_name: str, processing_fn: Callable) -> int:
        """
        Process queued items when service is back online

        Args:
            service_name: Name of service
            processing_fn: Function to call with each queued item

        Returns:
            Number of items processed
        """
        import glob
        import json

        queue_files = list(self.queue_path.glob(f"{service_name}_queue_*.json"))
        processed = 0

        for queue_file in queue_files:
            try:
                queue_data = json.loads(queue_file.read_text(encoding='utf-8'))
                processing_fn(queue_data['data'])
                queue_file.unlink()  # Remove processed item
                processed += 1
                logger.info(f"Processed queued item: {queue_file.name}")

            except Exception as e:
                logger.error(f"Failed to process queued item {queue_file.name}: {e}")

        return processed
