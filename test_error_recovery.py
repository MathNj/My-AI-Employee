#!/usr/bin/env python3
"""
Test Error Recovery System

Verifies that error_recovery.py works correctly with:
- Retry with backoff
- Circuit breaker
- Error categorization
- Graceful degradation
"""

import sys
from pathlib import Path

# Add watchers to path
watchers_path = Path(__file__).parent / "watchers"
sys.path.insert(0, str(watchers_path))

from error_recovery import (
    retry_with_backoff,
    handle_error_with_recovery,
    ErrorCategory,
    CircuitBreaker,
    GracefulDegradation
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Test counters
test_count = 0
passed_count = 0


def test_retry_with_backoff():
    """Test retry decorator with exponential backoff"""
    global test_count, passed_count
    test_count += 1

    print("\n" + "="*70)
    print(f"Test {test_count}: Retry with Exponential Backoff")
    print("="*70)

    attempt_count = {'count': 0}

    @retry_with_backoff(max_attempts=3, base_delay=0.1, max_delay=1)
    def flaky_function():
        attempt_count['count'] += 1
        if attempt_count['count'] < 3:
            raise ConnectionError("Transient error!")
        return "Success!"

    try:
        result = flaky_function()
        print(f"[PASS] Function succeeded after {attempt_count['count']} attempts")
        print(f"   Result: {result}")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] Function failed after all retries: {e}")

    return attempt_count['count'] == 3 and result == "Success!"


def test_circuit_breaker():
    """Test circuit breaker pattern"""
    global test_count, passed_count
    test_count += 1

    print("\n" + "="*70)
    print(f"Test {test_count}: Circuit Breaker Pattern")
    print("="*70)

    breaker = CircuitBreaker(failure_threshold=3, timeout=2)

    # Simulate failures
    for i in range(5):
        if i < 3:
            breaker.record_failure()
            state = breaker.can_execute()
            print(f"   Failure {i+1}: Can execute = {state}")
        else:
            state = breaker.can_execute()
            print(f"   After {i} failures: Circuit open = {not state}")

    # Test that circuit is open
    if not breaker.can_execute():
        print("[PASS] Circuit breaker opened after threshold")
        passed_count += 1
    else:
        print("[FAIL] Circuit breaker did not open")

    # Test recovery
    breaker.record_success()
    if breaker.can_execute():
        print("[PASS] Circuit breaker closed after success")
        passed_count += 1
    else:
        print("[FAIL] Circuit breaker did not close")


def test_error_categorization():
    """Test error categorization"""
    global test_count, passed_count
    test_count += 1

    print("\n" + "="*70)
    print(f"Test {test_count}: Error Categorization")
    print("="*70)

    errors_to_test = [
        (ConnectionError("Network timeout"), ErrorCategory.TRANSIENT),
        (PermissionError("Access denied"), ErrorCategory.AUTHENTICATION),
        (ValueError("Invalid data"), ErrorCategory.LOGIC),
        (KeyError("Missing field"), ErrorCategory.DATA),
        (RuntimeError("System crash"), ErrorCategory.SYSTEM),
    ]

    all_passed = True
    for error, expected_category in errors_to_test:
        recovery = handle_error_with_recovery(error, "test operation")
        actual_category = recovery.get('category')

        if actual_category == expected_category.value:
            print(f"   [OK] {error.__class__.__name__}: {actual_category}")
        else:
            print(f"   [FAIL] {error.__class__.__name__}: Expected {expected_category.value}, got {actual_category}")
            all_passed = False

    if all_passed:
        print("[PASS] All errors categorized correctly")
        passed_count += 1
    else:
        print("[FAIL] Some errors misclassified")


def test_graceful_degradation():
    """Test graceful degradation queue"""
    global test_count, passed_count
    test_count += 1

    print("\n" + "="*70)
    print(f"Test {test_count}: Graceful Degradation")
    print("="*70)

    degradation = GracefulDegradation(vault_path=Path(__file__).parent)

    # Queue items when service is down
    test_items = [
        {"type": "email", "to": "client@example.com", "subject": "Test 1"},
        {"type": "email", "to": "client2@example.com", "subject": "Test 2"},
    ]

    queued = 0
    for item in test_items:
        if degradation.queue_for_later(item, "email_service"):
            queued += 1

    if queued == len(test_items):
        print(f"[PASS] Queued {queued} items successfully")
        passed_count += 1
    else:
        print(f"[FAIL] Only queued {queued}/{len(test_items)} items")

    # Process queue (this would normally be done when service recovers)
    def process_fn(item):
        print(f"   Processing: {item['type']} to {item.get('to', 'unknown')}")
        return True

    processed = degradation.process_queue("email_service", process_fn)
    print(f"   Processed {processed} items from queue")


def test_real_scenario():
    """Test real-world scenario: API timeout with retry"""
    global test_count, passed_count
    test_count += 1

    print("\n" + "="*70)
    print(f"Test {test_count}: Real-World Scenario - API Timeout")
    print("="*70)

    attempts = {'count': 0}

    @retry_with_backoff(max_attempts=3, base_delay=0.1, max_delay=1)
    def mock_api_call():
        attempts['count'] += 1
        if attempts['count'] < 2:
            raise TimeoutError("API timeout")
        # Simulate successful response
        return {"status": "success", "data": "API response"}

    try:
        result = mock_api_call()
        print(f"[PASS] API call succeeded after {attempts['count']} attempts")
        print(f"   Response: {result}")
        passed_count += 1
    except Exception as e:
        print(f"[FAIL] API call failed: {e}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("ERROR RECOVERY SYSTEM TEST SUITE")
    print("="*70)

    # Run tests
    test_retry_with_backoff()
    test_circuit_breaker()
    test_error_categorization()
    test_graceful_degradation()
    test_real_scenario()

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {test_count}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {test_count - passed_count}")
    print(f"Success Rate: {(passed_count/test_count*100):.1f}%")

    if passed_count == test_count:
        print("\n[SUCCESS] ALL TESTS PASSED - Error recovery system is working!")
        return 0
    else:
        print(f"\n[WARNING] {test_count - passed_count} TEST(S) FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
