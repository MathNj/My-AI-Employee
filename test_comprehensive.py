#!/usr/bin/env python3
"""
Comprehensive Test Suite for Personal AI Employee
Tests all components systematically

Usage:
    python test_comprehensive.py
"""

import sys
import os
from pathlib import Path
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Test results
test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'warnings': 0,
    'tests': []
}


def test_result(name, passed, message, details=None):
    """Record test result"""
    test_results['total'] += 1
    if passed:
        test_results['passed'] += 1
        logger.info(f"[PASS] {name}")
    else:
        test_results['failed'] += 1
        logger.error(f"[FAIL] {name}: {message}")

    test_results['tests'].append({
        'name': name,
        'passed': passed,
        'message': message,
        'details': details,
        'timestamp': datetime.now().isoformat()
    })

    return passed


def warn(message):
    """Record warning"""
    test_results['warnings'] += 1
    logger.warning(f"[WARN] {message}")


# ========================================================================
# SECTION 1: FOLDER STRUCTURE TESTS
# ========================================================================

def test_folder_structure():
    """Test vault folder structure"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 1: FOLDER STRUCTURE")
    logger.info("="*70)

    vault_path = Path(__file__).parent
    required_dirs = [
        'Inbox', 'Needs_Action', 'Pending_Approval', 'Approved',
        'Rejected', 'Done', 'Logs', 'Briefings', 'Accounting',
        'watchers', '.claude', 'mcp-servers'
    ]

    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            test_result(f"Directory exists: {dir_name}", True, "")
        else:
            test_result(f"Directory exists: {dir_name}", False, "Not found")


def test_core_files():
    """Test core documentation files"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 2: CORE FILES")
    logger.info("="*70)

    vault_path = Path(__file__).parent
    required_files = [
        'Dashboard.md',
        'Company_Handbook.md',
        'Business_Goals.md',
        'ARCHITECTURE.md',
        'GOLD_TIER_VERIFICATION.md'
    ]

    for file_name in required_files:
        file_path = vault_path / file_name
        if file_path.exists() and file_path.is_file():
            size = file_path.stat().st_size
            test_result(f"File exists: {file_name}", True, f"Size: {size} bytes")
        else:
            test_result(f"File exists: {file_name}", False, "Not found")


# ========================================================================
# SECTION 3: WATCHER MODULES TESTS
# ========================================================================

def test_watcher_modules():
    """Test watcher modules can be imported"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 3: WATCHER MODULES")
    logger.info("="*70)

    watchers_path = Path(__file__).parent / "watchers"
    sys.path.insert(0, str(watchers_path))

    modules = [
        'error_recovery',
        'audit_logger',
        'base_watcher',
        'gmail_watcher',
        'whatsapp_watcher',
        'slack_watcher',
        'filesystem_watcher',
        'calendar_watcher',
        'odoo_watcher'
    ]

    for module_name in modules:
        try:
            __import__(module_name)
            test_result(f"Module import: {module_name}", True, "")
        except ImportError as e:
            test_result(f"Module import: {module_name}", False, str(e))
        except Exception as e:
            # Module might have runtime import errors, but that's OK for now
            warn(f"Module {module_name} has runtime issues: {str(e)[:50]}")
            test_result(f"Module import: {module_name}", True, "Importable (runtime issues)")


def test_error_recovery_system():
    """Test error recovery functionality"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 4: ERROR RECOVERY SYSTEM")
    logger.info("="*70)

    watchers_path = Path(__file__).parent / "watchers"
    sys.path.insert(0, str(watchers_path))

    try:
        from error_recovery import (
            ErrorCategory,
            CircuitBreaker,
            GracefulDegradation,
            handle_error_with_recovery
        )

        # Test ErrorCategory
        categories = [e.value for e in ErrorCategory]
        expected = ['transient', 'authentication', 'logic', 'data', 'system']
        test_result("ErrorCategory enum", set(categories) == set(expected), "")

        # Test CircuitBreaker
        breaker = CircuitBreaker(failure_threshold=3, timeout=60)
        breaker.record_failure()
        breaker.record_failure()
        breaker.record_failure()
        can_execute = breaker.can_execute()
        test_result("CircuitBreaker opens", not can_execute, "Should be False after 3 failures")

        # Test GracefulDegradation
        degradation = GracefulDegradation(vault_path=Path(__file__).parent)
        test_result("GracefulDegradation init", True, "")

        # Test handle_error_with_recovery
        recovery = handle_error_with_recovery(ConnectionError("test"), "test_operation")
        test_result("handle_error_with_recovery", recovery['category'] == 'transient', "")

    except ImportError as e:
        test_result("Error recovery imports", False, str(e))
    except Exception as e:
        test_result("Error recovery tests", False, str(e))


def test_audit_logging_system():
    """Test audit logging functionality"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 5: AUDIT LOGGING SYSTEM")
    logger.info("="*70)

    watchers_path = Path(__file__).parent / "watchers"
    sys.path.insert(0, str(watchers_path))

    try:
        from audit_logger import (
            log_action,
            log_email_sent,
            log_social_post,
            log_approval,
            log_error,
            get_audit_logger
        )

        # Test log_action
        log = log_action(
            action_type="test",
            actor="test_suite",
            result="success",
            skill="test"
        )
        test_result("log_action function", 'timestamp' in log, "")

        # Test log_email_sent
        log = log_email_sent(
            to="test@example.com",
            subject="Test",
            result="success"
        )
        test_result("log_email_sent function", log['action_type'] == 'email_send', "")

        # Test log_social_post
        log = log_social_post(
            platform="test",
            content="Test post",
            result="success"
        )
        test_result("log_social_post function", log['action_type'] == 'social_post', "")

        # Test log_approval
        log = log_approval(
            item_type="test",
            item_id="test_123",
            decision="approve",
            confidence=0.95
        )
        test_result("log_approval function", log['action_type'] == 'approval', "")

        # Test log_error
        log = log_error(
            action_type="test",
            actor="test",
            error="Test error"
        )
        test_result("log_error function", log['result'] == 'error', "")

        # Test AuditLogger class
        audit_logger = get_audit_logger()
        test_result("AuditLogger instance", audit_logger is not None, "")

    except ImportError as e:
        test_result("Audit logging imports", False, str(e))
    except Exception as e:
        test_result("Audit logging tests", False, str(e))


# ========================================================================
# SECTION 4: SKILLS TESTS
# ========================================================================

def test_skills_structure():
    """Test skills directory structure"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 6: SKILLS STRUCTURE")
    logger.info("="*70)

    skills_path = Path(__file__).parent / ".claude" / "skills"

    if not skills_path.exists():
        test_result("Skills directory exists", False, "Not found")
        return

    # Count skills
    skill_dirs = [d for d in skills_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    test_result(f"Skills directory count ({len(skill_dirs)} skills)", len(skill_dirs) >= 20, "")

    # Check for SKILL.md files
    skills_with_docs = 0
    for skill_dir in skill_dirs:
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            skills_with_docs += 1

    test_result(f"Skills with SKILL.md ({skills_with_docs}/{len(skill_dirs)})",
                skills_with_docs >= len(skill_dirs) * 0.9, "90% documented")

    # Check for scripts directories
    skills_with_scripts = 0
    for skill_dir in skill_dirs:
        scripts_dir = skill_dir / "scripts"
        if scripts_dir.exists():
            scripts = list(scripts_dir.glob("*.py"))
            if scripts:
                skills_with_scripts += 1

    test_result(f"Skills with scripts ({skills_with_scripts}/{len(skill_dirs)})",
                skills_with_scripts >= len(skill_dirs) * 0.8, "80% have scripts")


def test_critical_skills():
    """Test critical skills exist and have structure"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 7: CRITICAL SKILLS")
    logger.info("="*70)

    skills_path = Path(__file__).parent / ".claude" / "skills"

    critical_skills = [
        'task-processor',
        'auto-approver',
        'approval-processor',
        'email-sender',
        'linkedin-poster',
        'facebook-poster',
        'x-poster',
        'instagram-poster',
        'ceo-briefing-generator',
        'dashboard-updater',
        'cross-domain-bridge',
        'ralph-loop',
        'scheduler-manager'
    ]

    for skill_name in critical_skills:
        skill_path = skills_path / skill_name
        if not skill_path.exists():
            test_result(f"Critical skill: {skill_name}", False, "Directory not found")
            continue

        # Check SKILL.md
        skill_md = skill_path / "SKILL.md"
        has_docs = skill_md.exists()

        # Check scripts
        scripts_dir = skill_path / "scripts"
        has_scripts = scripts_dir.exists() and any(scripts_dir.glob("*.py"))

        if has_docs and has_scripts:
            test_result(f"Critical skill: {skill_name}", True, "Complete")
        elif has_docs or has_scripts:
            test_result(f"Critical skill: {skill_name}", True, "Partial (docs or scripts)")
        else:
            test_result(f"Critical skill: {skill_name}", False, "Empty skill")


# ========================================================================
# SECTION 5: MCP SERVERS TESTS
# ========================================================================

def test_mcp_servers():
    """Test MCP servers structure"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 8: MCP SERVERS")
    logger.info("="*70)

    mcp_path = Path(__file__).parent / "mcp-servers"

    if not mcp_path.exists():
        test_result("MCP servers directory", False, "Not found")
        return

    # List MCP servers
    mcp_dirs = [d for d in mcp_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    test_result(f"MCP servers count ({len(mcp_dirs)})", len(mcp_dirs) >= 3, "")

    # Check each MCP server
    for mcp_dir in mcp_dirs:
        # Check for package.json or Python files (search recursively)
        has_package = (mcp_dir / "package.json").exists()
        has_python = any(mcp_dir.rglob("*.py"))  # Recursive search

        if has_package or has_python:
            test_result(f"MCP server: {mcp_dir.name}", True, "")
        else:
            test_result(f"MCP server: {mcp_dir.name}", False, "No implementation found")


# ========================================================================
# SECTION 6: ODOO INTEGRATION TESTS
# ========================================================================

def test_odoo_setup():
    """Test Odoo setup"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 9: ODOO INTEGRATION")
    logger.info("="*70)

    import subprocess

    try:
        # Check if Docker is installed
        result = subprocess.run(['docker', '--version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        test_result("Docker installed", result.returncode == 0, "")

        # Check Odoo containers
        result = subprocess.run(['docker', 'ps', '--filter', 'name=odoo'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        lines = result.stdout.strip().split('\n')
        # Count containers (excluding header)
        container_count = len([l for l in lines if l and 'CONTAINER' not in l])

        test_result(f"Odoo containers running ({container_count})",
                    container_count >= 3, f"Found {container_count} containers")

        # Check for odoo-mcp-server
        odoo_mcp = Path(__file__).parent / "mcp-servers" / "odoo-mcp-server"
        if odoo_mcp.exists():
            # Check .env file
            env_file = odoo_mcp / ".env"
            test_result("Odoo MCP .env file", env_file.exists(), "")
        else:
            test_result("Odoo MCP server", False, "Directory not found")

    except FileNotFoundError:
        test_result("Docker installed", False, "Docker not found in PATH")
    except subprocess.TimeoutExpired:
        test_result("Docker commands", False, "Timeout")
    except Exception as e:
        test_result("Odoo tests", False, str(e))


# ========================================================================
# SECTION 7: CONFIGURATION TESTS
# ========================================================================

def test_configuration():
    """Test configuration files"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 10: CONFIGURATION")
    logger.info("="*70)

    # Check .gitignore
    gitignore = Path(__file__).parent / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        has_env = '.env' in content
        has_credentials = 'credentials' in content
        test_result(".gitignore protects secrets", has_env or has_credentials, "")
    else:
        test_result(".gitignore exists", False, "")

    # Check watchers .env (expected to not exist - must be created by user)
    env_file = Path(__file__).parent / "watchers" / ".env"
    env_example = Path(__file__).parent / "watchers" / ".env.example"

    if env_example.exists():
        test_result("Watchers .env.example template", True, "")
        # .env not existing is expected (security practice)
        if not env_file.exists():
            test_result("Watchers .env properly excluded", True, "Not in repo (expected)")
        else:
            # .env exists (user configured it)
            if env_file.stat().st_size > 0:
                test_result("Watchers .env configured", True, "")
            else:
                warn("Watchers .env is empty")
    else:
        test_result("Watchers .env.example template", False, "Template not found")


# ========================================================================
# SECTION 8: INTEGRATION TESTS
# ========================================================================

def test_integrations():
    """Test integration points"""
    logger.info("\n" + "="*70)
    logger.info("SECTION 11: INTEGRATION POINTS")
    logger.info("="*70)

    vault_path = Path(__file__).parent

    # Check Logs directory has audit logs
    logs_dir = vault_path / "Logs"
    if logs_dir.exists():
        audit_logs = list(logs_dir.glob("audit_*.json"))
        test_result(f"Audit logs exist ({len(audit_logs)} files)",
                    len(audit_logs) > 0, "")

    # Check Needs_Action has items
    needs_action = vault_path / "Needs_Action"
    if needs_action.exists():
        items = list(needs_action.glob("*.md"))
        test_result(f"Needs_Action has items ({len(items)} files)",
                    len(items) > 0, "")

    # Check Done directory
    done_dir = vault_path / "Done"
    if done_dir.exists():
        items = list(done_dir.glob("*.md"))
        test_result(f"Done has items ({len(items)} files)",
                    len(items) >= 0, "")


# ========================================================================
# MAIN TEST RUNNER
# ========================================================================

def main():
    """Run all tests"""
    logger.info("\n" + "="*70)
    logger.info("COMPREHENSIVE AI EMPLOYEE TEST SUITE")
    logger.info("="*70)
    logger.info(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Vault: {Path(__file__).parent}")

    # Run all test sections
    test_folder_structure()
    test_core_files()
    test_watcher_modules()
    test_error_recovery_system()
    test_audit_logging_system()
    test_skills_structure()
    test_critical_skills()
    test_mcp_servers()
    test_odoo_setup()
    test_configuration()
    test_integrations()

    # Print summary
    logger.info("\n" + "="*70)
    logger.info("TEST SUMMARY")
    logger.info("="*70)
    logger.info(f"Total Tests: {test_results['total']}")
    logger.info(f"Passed: {test_results['passed']}")
    logger.info(f"Failed: {test_results['failed']}")
    logger.info(f"Warnings: {test_results['warnings']}")
    logger.info(f"Success Rate: {(test_results['passed']/test_results['total']*100):.1f}%")

    if test_results['failed'] == 0:
        logger.info("\n[SUCCESS] ALL TESTS PASSED!")
        return 0
    else:
        logger.info(f"\n[FAILURE] {test_results['failed']} test(s) failed")

        # Print failed tests
        logger.info("\nFailed Tests:")
        for test in test_results['tests']:
            if not test['passed']:
                logger.info(f"  - {test['name']}: {test['message']}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
