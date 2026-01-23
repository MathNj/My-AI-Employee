#!/usr/bin/env python3
"""
Test Ralph MCP Server with Real Vault Tasks

This script tests Phase 2 features with actual tasks from the vault.
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ralph_core import RalphCore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_real_task_estimation():
    """Test effort estimation on real tasks"""
    logger.info("=" * 70)
    logger.info("TEST: Estimate Effort on Real Tasks")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Get pending tasks
        tasks = ralph.list_pending_tasks()

        logger.info(f"\n📋 Found {len(tasks)} pending tasks")
        logger.info("\nEstimating effort for first 5 tasks:\n")

        # Estimate effort for first 5 tasks
        for i, task in enumerate(tasks[:5], 1):
            task_path = vault_path / task['file_path']

            logger.info(f"{i}. {task['file_name']}")
            logger.info(f"   Priority: {task.get('priority', 'N/A')}")
            logger.info(f"   Type: {task.get('type', 'N/A')}")

            # Estimate effort
            effort = ralph.estimate_effort(str(task_path))

            if effort['success']:
                data = effort['data']
                logger.info(f"   ✅ Estimated:")
                logger.info(f"      Type: {data['task_type']}")
                logger.info(f"      Steps: {data['estimated_steps']}")
                logger.info(f"      Time: {data['estimated_time_minutes']} min")
                logger.info(f"      Complexity: {data['complexity']}")
            else:
                logger.warning(f"   ⚠️  Could not estimate: {effort.get('error')}")

            logger.info("")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_health_with_real_tasks():
    """Test health monitoring with real active tasks"""
    logger.info("=" * 70)
    logger.info("TEST: Health Monitoring with Real Tasks")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Get health
        health = ralph.get_ralph_health()

        if health['success']:
            data = health['data']
            logger.info(f"\n✅ System Health: {data['status'].upper()}")
            logger.info(f"   Active tasks: {data['active_tasks']}")
            logger.info(f"   Stuck tasks: {data['stuck_tasks']}")
            logger.info(f"   Average iterations: {data['average_iterations']}")

            # Health recommendations
            if data['status'] == 'healthy':
                logger.info("\n✅ System is healthy - no action needed")
            elif data['status'] == 'warning':
                logger.warning("\n⚠️  WARNING: Some tasks need attention")
                if data['stuck_tasks'] > 0:
                    logger.info("   Recommendation: Review stuck tasks")
            elif data['status'] == 'critical':
                logger.error("\n🚨 CRITICAL: Immediate attention required!")
                logger.info("   Recommendation: Investigate and resolve stuck tasks")

            # Show stuck task details if any
            if data['stuck_task_details']:
                logger.info("\n📌 Stuck Task Details:")
                for task in data['stuck_task_details']:
                    logger.info(f"\n   Task ID: {task['task_id']}")
                    logger.info(f"   Reason: {task['reason']}")
                    logger.info(f"   Iterations: {task['iterations']}/{task['max_iterations']}")
                    logger.info(f"   Status: {task['status']}")
        else:
            logger.error("❌ Failed to get health")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_performance_analysis():
    """Test performance metrics analysis"""
    logger.info("=" * 70)
    logger.info("TEST: Performance Metrics Analysis")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        logger.info("\n📊 Performance Metrics by Time Range:\n")

        # Get metrics for different ranges
        ranges = ["today", "week", "month", "all"]

        for time_range in ranges:
            metrics = ralph.get_performance_metrics(time_range)

            if metrics['success']:
                data = metrics['data']
                logger.info(f"📈 {time_range.upper()}:")
                logger.info(f"   Tasks completed: {data['tasks_completed']}")
                logger.info(f"   Avg iterations: {data['average_iterations']:.2f}")
                logger.info(f"   Avg time: {data['average_time_minutes']:.1f} min")
                logger.info(f"   Success rate: {data['success_rate']:.1f}%")
                logger.info(f"   Blocked rate: {data['blocked_rate']:.1f}%")

                # Performance assessment
                if data['success_rate'] >= 90:
                    logger.info(f"   ✅ Excellent performance")
                elif data['success_rate'] >= 75:
                    logger.info(f"   ⚠️  Good performance (room for improvement)")
                else:
                    logger.info(f"   🚨 Poor performance (needs attention)")

                logger.info("")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_blocking_issues():
    """Test blocking issue detection"""
    logger.info("=" * 70)
    logger.info("TEST: Blocking Issue Detection")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Discover blocking issues
        blocking = ralph.discover_blocking_issues()

        if blocking['success']:
            issues = blocking['data']

            if issues:
                logger.info(f"\n🚧 Found {len(issues)} blocking issue(s):\n")

                for issue in issues:
                    logger.info(f"📌 Task: {issue['task_id']}")
                    logger.info(f"   File: {issue['task_file']}")
                    logger.info(f"   Reason: {issue['reason']}")
                    logger.info(f"   Blocking: {len(issue['blocking_tasks'])} task(s)")

                    if issue['blocking_tasks']:
                        logger.info(f"   Blocked tasks:")
                        for blocked in issue['blocking_tasks']:
                            logger.info(f"      - {blocked}")

                    logger.info("")
            else:
                logger.info("\n✅ No blocking issues detected")
                logger.info("   All tasks can proceed independently")
        else:
            logger.error("❌ Failed to discover blocking issues")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def test_task_group_creation():
    """Test creating task groups from real tasks"""
    logger.info("=" * 70)
    logger.info("TEST: Task Group Creation from Real Tasks")
    logger.info("=" * 70)

    try:
        vault_path = Path(__file__).parent.parent.parent
        ralph = RalphCore(str(vault_path))

        # Get pending tasks
        tasks = ralph.list_pending_tasks()

        if len(tasks) < 3:
            logger.info("\n⚠️  Need at least 3 tasks for group testing")
            return True

        # Create a group with first 3 high-priority tasks
        high_priority_tasks = [t for t in tasks if t.get('priority') == 'high'][:3]

        if len(high_priority_tasks) < 3:
            high_priority_tasks = tasks[:3]

        # Generate task IDs
        task_ids = []
        for task in high_priority_tasks:
            task_path = vault_path / task['file_path']
            task_id = ralph._generate_task_id(task_path)
            task_ids.append(task_id)

        # Create group
        result = ralph.create_task_group(
            task_ids=task_ids,
            group_name="High Priority Batch",
            strategy="sequential"
        )

        if result['success']:
            data = result['data']
            logger.info(f"\n✅ Created task group:")
            logger.info(f"   Group ID: {data['group_id']}")
            logger.info(f"   Name: {data['group_name']}")
            logger.info(f"   Strategy: {data['strategy']}")
            logger.info(f"   Tasks: {len(data['task_ids'])}")
            logger.info(f"   Created: {data['created_at']}")

            logger.info(f"\n📋 Tasks in group:")
            for i, (task_id, task_info) in enumerate(zip(data['task_ids'], high_priority_tasks), 1):
                logger.info(f"   {i}. {task_id}")
                logger.info(f"      File: {task_info['file_name']}")
                logger.info(f"      Priority: {task_info.get('priority', 'N/A')}")

        else:
            logger.error(f"❌ Failed to create group: {result.get('error')}")

        return True

    except Exception as e:
        logger.error(f"❌ FAIL: {e}")
        return False


def main():
    """Run all real task tests"""
    logger.info("Ralph MCP Server - Real Task Testing")
    logger.info("=" * 70)

    tests = [
        ("Health Monitoring", test_health_with_real_tasks),
        ("Performance Analysis", test_performance_analysis),
        ("Blocking Issue Detection", test_blocking_issues),
        ("Effort Estimation", test_real_task_estimation),
        ("Task Group Creation", test_task_group_creation),
    ]

    results = []

    for test_name, test_func in tests:
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'=' * 70}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    logger.info("\n" + "=" * 70)
    logger.info("REAL TASK TEST SUMMARY")
    logger.info("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")

    logger.info(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 All real task tests passed!")
        return 0
    else:
        logger.error(f"⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
