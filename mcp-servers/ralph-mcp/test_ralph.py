#!/usr/bin/env python3
"""
Test Ralph MCP Server

Tests the Ralph Core functionality.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ralph_core import RalphCore
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_list_pending_tasks():
    """Test 1: List pending tasks"""
    logger.info("=" * 70)
    logger.info("TEST 1: List Pending Tasks")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        tasks = ralph.list_pending_tasks()

        logger.info(f"✅ Found {len(tasks)} pending tasks")

        for task in tasks[:5]:  # Show first 5
            logger.info(f"  - {task['file_name']} ({task['type']}, {task['priority']})")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_claim_next_task():
    """Test 2: Claim next task"""
    logger.info("=" * 70)
    logger.info("TEST 2: Claim Next Task")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        task_path = ralph.claim_next_task()

        if task_path:
            logger.info(f"✅ Claimed task: {Path(task_path).name}")
            return True
        else:
            logger.info("⚠️  No tasks to claim")
            return True  # Not a failure, just no tasks

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_create_ralph_state():
    """Test 3: Create Ralph state"""
    logger.info("=" * 70)
    logger.info("TEST 3: Create Ralph State")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Create a dummy task file for testing
        test_task = vault_path / "Needs_Action" / "TEST_ralph_test.md"
        test_task.write_text("""---
type: test
priority: medium
---

# Test Task

This is a test task for Ralph MCP.
""")

        # Create Ralph state
        state = ralph.create_ralph_state(
            task_file=str(test_task),
            prompt="Test prompt for Ralph",
            max_iterations=5
        )

        logger.info(f"✅ Created Ralph state: {state.task_id}")
        logger.info(f"  Original path: {state.original_path}")
        logger.info(f"  Max iterations: {state.max_iterations}")
        logger.info(f"  Status: {state.status}")

        # Cleanup
        test_task.unlink()
        ralph.archive_state(state.task_id)

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_update_progress():
    """Test 4: Update progress"""
    logger.info("=" * 70)
    logger.info("TEST 4: Update Progress")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Create a test state
        test_task = vault_path / "Needs_Action" / "TEST_progress.md"
        test_task.write_text("---\ntype: test\n---\n# Test")

        state = ralph.create_ralph_state(
            task_file=str(test_task),
            prompt="Test",
            max_iterations=5
        )

        # Update progress
        updated = ralph.update_progress(
            task_id=state.task_id,
            status="in_progress",
            notes="Making good progress"
        )

        if updated and updated.status == "in_progress":
            logger.info(f"✅ Progress updated: {updated.status}")
            logger.info(f"  Notes: {updated.notes[-1][:50]}")
        else:
            logger.error("❌ Progress update failed")
            return False

        # Cleanup
        test_task.unlink()
        ralph.archive_state(state.task_id)

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_should_continue():
    """Test 5: Should continue"""
    logger.info("=" * 70)
    logger.info("TEST 5: Should Continue")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Create a test state
        test_task = vault_path / "Needs_Action" / "TEST_continue.md"
        test_task.write_text("---\ntype: test\n---\n# Test")

        state = ralph.create_ralph_state(
            task_file=str(test_task),
            prompt="Test",
            max_iterations=5
        )

        # Check should_continue
        result = ralph.should_continue(state.task_id)

        if result['should_continue']:
            logger.info(f"✅ Should continue: {result['reason']}")
        else:
            logger.info(f"⚠️  Should not continue: {result['reason']}")

        # Increment to max
        for _ in range(state.max_iterations):
            ralph.increment_iteration(state.task_id)

        # Check again
        result = ralph.should_continue(state.task_id)

        if not result['should_continue']:
            logger.info(f"✅ Correctly stopped: {result['reason']}")
        else:
            logger.error("❌ Should have stopped at max iterations")
            return False

        # Cleanup
        test_task.unlink()
        ralph.archive_state(state.task_id)

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Ralph MCP Server - Test Suite")
    logger.info("=" * 70)

    tests = [
        ("List Pending Tasks", test_list_pending_tasks),
        ("Claim Next Task", test_claim_next_task),
        ("Create Ralph State", test_create_ralph_state),
        ("Update Progress", test_update_progress),
        ("Should Continue", test_should_continue),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\nRunning: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
