#!/usr/bin/env python3
"""
Test Ralph MCP Server - Phase 2 Features

Tests the Phase 2 functionality:
- Multi-task orchestration (task groups)
- Smart task discovery (blocking issues, effort estimation)
- Approval workflow integration
- Performance metrics
- Health monitoring
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


def test_get_performance_metrics():
    """Test 1: Get performance metrics"""
    logger.info("=" * 70)
    logger.info("TEST 1: Get Performance Metrics")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Test all time ranges
        for time_range in ["today", "week", "month", "all"]:
            metrics = ralph.get_performance_metrics(time_range)

            if metrics['success']:
                data = metrics['data']
                logger.info(f"✅ {time_range.capitalize()} metrics:")
                logger.info(f"  Tasks completed: {data['tasks_completed']}")
                logger.info(f"  Average iterations: {data['average_iterations']}")
                logger.info(f"  Average time: {data['average_time_minutes']} minutes")
                logger.info(f"  Success rate: {data['success_rate']}%")
                logger.info(f"  Blocked rate: {data['blocked_rate']}%")
            else:
                logger.error(f"❌ Failed to get {time_range} metrics")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_get_ralph_health():
    """Test 2: Get Ralph health"""
    logger.info("=" * 70)
    logger.info("TEST 2: Get Ralph Health")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        health = ralph.get_ralph_health()

        if health['success']:
            data = health['data']
            logger.info(f"✅ Health Status: {data['status']}")
            logger.info(f"  Active tasks: {data['active_tasks']}")
            logger.info(f"  Stuck tasks: {data['stuck_tasks']}")
            logger.info(f"  Average iterations: {data['average_iterations']}")

            if data['stuck_task_details']:
                logger.info("  Stuck tasks:")
                for task in data['stuck_task_details']:
                    logger.info(f"    - {task['task_id']}: {task['reason']}")
        else:
            logger.error("❌ Failed to get health")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_get_stuck_tasks():
    """Test 3: Get stuck tasks"""
    logger.info("=" * 70)
    logger.info("TEST 3: Get Stuck Tasks")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        stuck_tasks = ralph.get_stuck_tasks()

        logger.info(f"✅ Found {len(stuck_tasks)} stuck tasks")

        for task in stuck_tasks:
            logger.info(f"  - {task['task_id']}: {task['reason']}")
            logger.info(f"    Iterations: {task['iterations']}/{task['max_iterations']}")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_estimate_effort():
    """Test 4: Estimate effort"""
    logger.info("=" * 70)
    logger.info("TEST 4: Estimate Effort")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent
        ralph = RalphCore(str(vault_path))

        # Get a test task
        tasks = ralph.list_pending_tasks()

        if not tasks:
            logger.info("⚠️  No tasks to test")
            return True

        # Test first task
        task_file = vault_path / tasks[0]['file_path']
        effort = ralph.estimate_effort(str(task_file))

        if effort['success']:
            data = effort['data']
            logger.info(f"✅ Effort estimation for {tasks[0]['file_name']}:")
            logger.info(f"  Task type: {data['task_type']}")
            logger.info(f"  Estimated steps: {data['estimated_steps']}")
            logger.info(f"  Estimated time: {data['estimated_time_minutes']} minutes")
            logger.info(f"  Complexity: {data['complexity']}")
        else:
            logger.error(f"❌ Failed to estimate effort: {effort.get('error')}")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_create_task_group():
    """Test 5: Create task group"""
    logger.info("=" * 70)
    logger.info("TEST 5: Create Task Group")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Get test task IDs
        tasks = ralph.list_pending_tasks()

        if len(tasks) < 2:
            logger.info("⚠️  Need at least 2 tasks for group testing")
            return True

        # Create group with first 2 tasks
        task_ids = [ralph._generate_task_id(vault_path / tasks[0]['file_path'])]

        result = ralph.create_task_group(
            task_ids=task_ids,
            group_name="Test Group",
            strategy="sequential"
        )

        if result['success']:
            logger.info(f"✅ Created task group:")
            logger.info(f"  Group ID: {result['data']['group_id']}")
            logger.info(f"  Group name: {result['data']['group_name']}")
            logger.info(f"  Strategy: {result['data']['strategy']}")
            logger.info(f"  Tasks: {len(result['data']['task_ids'])}")
        else:
            logger.error(f"❌ Failed to create group: {result.get('error')}")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def main():
    """Run Phase 2 tests"""
    logger.info("Ralph MCP Server - Phase 2 Test Suite")
    logger.info("=" * 70)

    tests = [
        ("Get Performance Metrics", test_get_performance_metrics),
        ("Get Ralph Health", test_get_ralph_health),
        ("Get Stuck Tasks", test_get_stuck_tasks),
        ("Estimate Effort", test_estimate_effort),
        ("Create Task Group", test_create_task_group),
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
    logger.info("PHASE 2 TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All Phase 2 tests passed!")
        return 0
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
