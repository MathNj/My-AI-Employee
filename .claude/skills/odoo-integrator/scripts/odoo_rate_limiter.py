#!/usr/bin/env python3
"""
Odoo Rate Limiter

Token bucket rate limiter for controlling API request rates.
Supports per-second, per-minute, and burst rate limiting.

Usage:
    from odoo_rate_limiter import RateLimiter

    limiter = RateLimiter(requests_per_second=10)
    limiter.acquire()  # Blocks if rate limit exceeded
"""

from __future__ import annotations

import time
import threading
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field
from collections import deque

from odoo_sync_config import RateLimitConfig


@dataclass
class RateLimiterConfig:
    """Configuration for rate limiter"""
    requests_per_second: float = 10
    requests_per_minute: int = 500
    burst: int = 20


class TokenBucket:
    """Token bucket rate limiter"""

    def __init__(self, rate: float, capacity: int):
        """
        Initialize token bucket.

        Args:
            rate: Tokens added per second
            capacity: Maximum tokens (burst capacity)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.time()
        self.lock = threading.Lock()

    def _refill(self):
        """Refill tokens based on elapsed time"""
        now = time.time()
        elapsed = now - self.last_update

        # Add tokens based on rate
        self.tokens = min(
            self.capacity,
            self.tokens + elapsed * self.rate
        )
        self.last_update = now

    def acquire(self, tokens: int = 1) -> bool:
        """
        Try to acquire tokens.

        Returns:
            True if tokens acquired, False otherwise
        """
        with self.lock:
            self._refill()

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False

    def acquire_blocking(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Acquire tokens, blocking if necessary.

        Args:
            tokens: Number of tokens to acquire
            timeout: Maximum time to wait (None = wait forever)

        Returns:
            True if acquired, False if timeout
        """
        start = time.time()

        while True:
            if self.acquire(tokens):
                return True

            if timeout is not None:
                elapsed = time.time() - start
                if elapsed >= timeout:
                    return False

            # Calculate wait time
            with self.lock:
                self._refill()
                tokens_needed = tokens - self.tokens
                wait_time = tokens_needed / self.rate if tokens_needed > 0 else 0.1

            if timeout is not None:
                remaining = timeout - (time.time() - start)
                wait_time = min(wait_time, remaining)

            time.sleep(wait_time)

    def get_available_tokens(self) -> float:
        """Get current available tokens"""
        with self.lock:
            self._refill()
            return self.tokens


class SlidingWindowLogger:
    """Sliding window rate limiter for per-minute limits"""

    def __init__(self, limit: int, window_seconds: int = 60):
        """
        Initialize sliding window logger.

        Args:
            limit: Max requests in window
            window_seconds: Window size in seconds
        """
        self.limit = limit
        self.window = window_seconds
        self.requests = deque()
        self.lock = threading.Lock()

    def acquire(self) -> bool:
        """
        Try to acquire (log a request).

        Returns:
            True if under limit, False otherwise
        """
        with self.lock:
            now = time.time()

            # Remove old requests outside window
            cutoff = now - self.window
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()

            # Check if under limit
            if len(self.requests) < self.limit:
                self.requests.append(now)
                return True

            return False

    def get_count(self) -> int:
        """Get current request count in window"""
        with self.lock:
            now = time.time()
            cutoff = now - self.window
            while self.requests and self.requests[0] < cutoff:
                self.requests.popleft()
            return len(self.requests)


class RateLimiter:
    """Combined rate limiter with token bucket and sliding window"""

    def __init__(self, config: Optional[RateLimiterConfig] = None):
        """
        Initialize rate limiter.

        Args:
            config: Rate limiter configuration
        """
        if config is None:
            config = RateLimiterConfig()

        # Per-second limiter (token bucket)
        self.token_bucket = TokenBucket(
            rate=config.requests_per_second,
            capacity=config.burst
        )

        # Per-minute limiter (sliding window)
        self.sliding_window = SlidingWindowLogger(
            limit=config.requests_per_minute,
            window_seconds=60
        )

        self.enabled = True
        self.total_requests = 0
        self.rejected_requests = 0
        self.lock = threading.Lock()

    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make a request.

        Args:
            blocking: If True, wait until permit available
            timeout: Max wait time if blocking

        Returns:
            True if permit acquired, False otherwise
        """
        with self.lock:
            self.total_requests += 1

        if not self.enabled:
            return True

        # Try sliding window (minute limit)
        if not self.sliding_window.acquire():
            with self.lock:
                self.rejected_requests += 1
            return False

        # Try token bucket (second/second + burst)
        if blocking:
            acquired = self.token_bucket.acquire_blocking(timeout=timeout)
        else:
            acquired = self.token_bucket.acquire()

        if not acquired:
            with self.lock:
                self.rejected_requests += 1

        return acquired

    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        with self.lock:
            return {
                'enabled': self.enabled,
                'total_requests': self.total_requests,
                'rejected_requests': self.rejected_requests,
                'rejection_rate': (
                    self.rejected_requests / self.total_requests
                    if self.total_requests > 0 else 0
                ),
                'available_tokens': self.token_bucket.get_available_tokens(),
                'current_minute_count': self.sliding_window.get_count()
            }

    def reset(self):
        """Reset statistics"""
        with self.lock:
            self.total_requests = 0
            self.rejected_requests = 0


class SmartRateLimiter(RateLimiter):
    """Rate limiter with adaptive backoff based on responses"""

    def __init__(self, config: Optional[RateLimiterConfig] = None):
        super().__init__(config)
        self.consecutive_timeouts = 0
        self.consecutive_rate_limits = 0
        self.adaptive_rate_multiplier = 1.0
        self.last_backoff = 0

    def record_response(self, status_code: Optional[int] = None,
                        is_timeout: bool = False,
                        is_rate_limited: bool = False):
        """
        Record API response for adaptive rate adjustment.

        Args:
            status_code: HTTP status code
            is_timeout: Request timed out
            is_rate_limited: Received 429 rate limit response
        """
        if is_rate_limited or status_code == 429:
            self.consecutive_rate_limits += 1
            # Reduce rate by 50%
            self.adaptive_rate_multiplier *= 0.5
            self.adaptive_rate_multiplier = max(0.1, self.adaptive_rate_multiplier)

            # Add backoff
            self.last_backoff = min(60, 2 ** self.consecutive_rate_limits)

        elif is_timeout:
            self.consecutive_timeouts += 1
            # Reduce rate by 25%
            self.adaptive_rate_multiplier *= 0.75
            self.adaptive_rate_multiplier = max(0.1, self.adaptive_rate_multiplier)

        elif status_code and 200 <= status_code < 300:
            # Success - gradually recover rate
            self.consecutive_timeouts = 0
            self.consecutive_rate_limits = 0
            self.last_backoff = 0

            # Increase rate by 10% each success
            self.adaptive_rate_multiplier = min(1.0, self.adaptive_rate_multiplier * 1.1)

    def get_wait_time(self) -> float:
        """Get recommended wait time before next request"""
        if self.last_backoff > 0:
            return self.last_backoff

        # Calculate wait based on current rate
        current_rate = self.token_bucket.rate * self.adaptive_rate_multiplier

        if self.token_bucket.get_available_tokens() < 1:
            return 1.0 / current_rate if current_rate > 0 else 1.0

        return 0

    def acquire(self, blocking: bool = True, timeout: Optional[float] = None) -> bool:
        """Acquire with adaptive rate adjustment"""
        # Apply adaptive rate
        original_rate = self.token_bucket.rate
        self.token_bucket.rate = original_rate * self.adaptive_rate_multiplier

        result = super().acquire(blocking, timeout)

        # Restore original rate
        self.token_bucket.rate = original_rate

        return result

    def get_stats(self) -> dict:
        """Get extended statistics"""
        stats = super().get_stats()
        stats.update({
            'adaptive_rate_multiplier': self.adaptive_rate_multiplier,
            'consecutive_timeouts': self.consecutive_timeouts,
            'consecutive_rate_limits': self.consecutive_rate_limits,
            'recommended_wait_time': self.get_wait_time()
        })
        return stats


# =============================================================================
# Decorator for rate limiting
# =============================================================================

def rate_limit(limiter: RateLimiter):
    """Decorator to rate limit a function"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            limiter.acquire(blocking=True)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# Context Manager for rate limiting
# =============================================================================

class RateLimitContext:
    """Context manager for rate limiting a block of code"""

    def __init__(self, limiter: RateLimiter):
        self.limiter = limiter

    def __enter__(self):
        self.limiter.acquire(blocking=True)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def limit_rate(limiter: RateLimiter):
    """Create a rate limit context manager"""
    return RateLimitContext(limiter)


if __name__ == "__main__":
    # Test rate limiter
    import argparse

    parser = argparse.ArgumentParser(description='Test rate limiter')
    parser.add_argument('--rps', type=float, default=10,
                       help='Requests per second')
    parser.add_argument('--rpm', type=int, default=500,
                       help='Requests per minute')
    parser.add_argument('--burst', type=int, default=20,
                       help='Burst capacity')
    parser.add_argument('--test-seconds', type=int, default=5,
                       help='Test duration in seconds')

    args = parser.parse_args()

    config = RateLimiterConfig(
        requests_per_second=args.rps,
        requests_per_minute=args.rpm,
        burst=args.burst
    )

    limiter = SmartRateLimiter(config)

    print(f"Testing rate limiter: {args.rps} req/s, {args.rpm} req/min, burst {args.burst}")
    print(f"Running for {args.test_seconds} seconds...")

    import time
    start = time.time()
    requests_made = 0

    while time.time() - start < args.test_seconds:
        if limiter.acquire(blocking=True, timeout=1):
            requests_made += 1
            print(f"[{requests_made}] Request allowed at {time.time() - start:.1f}s")

    stats = limiter.get_stats()
    print(f"\nFinal stats:")
    print(f"  Requests made: {requests_made}")
    print(f"  Rejected: {stats['rejected_requests']}")
    print(f"  Rejection rate: {stats['rejection_rate']:.1%}")
