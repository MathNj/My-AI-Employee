#!/usr/bin/env python3
"""
Watcher System Test Script

Quick verification script to test all watcher components are properly installed
and configured before running them.

Usage:
    python test_watchers.py

Author: Personal AI Employee Project
Created: 2026-01-12
"""

import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_check(description, passed, details=""):
    """Print a check result."""
    status = "✓" if passed else "✗"
    color = "\033[92m" if passed else "\033[91m"  # Green or Red
    reset = "\033[0m"
    print(f"{color}{status}{reset} {description}")
    if details:
        print(f"    {details}")


def test_python_version():
    """Test Python version is 3.10+."""
    print_header("Testing Python Version")
    version = sys.version_info
    required = (3, 10)
    passed = version >= required
    print_check(
        "Python version",
        passed,
        f"Found: {version.major}.{version.minor}.{version.micro}, Required: 3.10+"
    )
    return passed


def test_imports():
    """Test all required imports."""
    print_header("Testing Python Dependencies")

    results = []

    # Test watchdog
    try:
        import watchdog
        print_check("watchdog library", True, f"Version: {watchdog.__version__}")
        results.append(True)
    except ImportError:
        print_check("watchdog library", False, "Run: pip install watchdog")
        results.append(False)

    # Test Google libraries
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        print_check("Google API libraries", True, "Gmail API ready")
        results.append(True)
    except ImportError:
        print_check("Google API libraries", False, "Run: pip install google-api-python-client google-auth-oauthlib")
        results.append(False)

    # Test Playwright
    try:
        from playwright.sync_api import sync_playwright
        print_check("Playwright library", True, "WhatsApp automation ready")
        results.append(True)
    except ImportError:
        print_check("Playwright library", False, "Run: pip install playwright && playwright install chromium")
        results.append(False)

    # Test dotenv
    try:
        import dotenv
        print_check("python-dotenv", True, "Environment config ready")
        results.append(True)
    except ImportError:
        print_check("python-dotenv", False, "Run: pip install python-dotenv")
        results.append(False)

    return all(results)


def test_vault_structure():
    """Test vault folder structure."""
    print_header("Testing Vault Structure")

    vault_path = Path(__file__).parent.parent
    results = []

    # Test required folders
    folders = [
        ("Needs_Action", "Task output folder"),
        ("Logs", "Log storage folder"),
        ("Inbox", "File drop folder"),
    ]

    for folder, description in folders:
        path = vault_path / folder
        passed = path.exists()
        print_check(f"{folder}/", passed, description)
        if not passed:
            print(f"    Will be created automatically on first run")
        results.append(True)  # Non-critical, will be created

    return all(results)


def test_watcher_files():
    """Test watcher files exist."""
    print_header("Testing Watcher Files")

    watchers_path = Path(__file__).parent
    results = []

    files = [
        ("base_watcher.py", "Abstract base class"),
        ("gmail_watcher.py", "Gmail monitoring"),
        ("filesystem_watcher.py", "File monitoring"),
        ("whatsapp_watcher.py", "WhatsApp monitoring"),
        ("requirements.txt", "Dependencies list"),
        (".env.example", "Config template"),
        ("ecosystem.config.js", "PM2 configuration"),
    ]

    for filename, description in files:
        path = watchers_path / filename
        passed = path.exists()
        print_check(filename, passed, description)
        results.append(passed)

    return all(results)


def test_base_watcher():
    """Test base watcher can be imported."""
    print_header("Testing Base Watcher")

    try:
        from base_watcher import BaseWatcher
        print_check("Import BaseWatcher", True, "Abstract class loaded")

        # Check it has required methods
        has_check = hasattr(BaseWatcher, 'check_for_updates')
        print_check("check_for_updates() method", has_check, "Abstract method defined")

        has_create = hasattr(BaseWatcher, 'create_action_file')
        print_check("create_action_file() method", has_create, "Abstract method defined")

        has_run = hasattr(BaseWatcher, 'run')
        print_check("run() method", has_run, "Main loop defined")

        return has_check and has_create and has_run

    except Exception as e:
        print_check("Import BaseWatcher", False, str(e))
        return False


def test_gmail_credentials():
    """Test Gmail credentials."""
    print_header("Testing Gmail Credentials")

    creds_path = Path(__file__).parent / "credentials" / "credentials.json"
    passed = creds_path.exists()

    print_check(
        "Gmail credentials.json",
        passed,
        "Found" if passed else "Missing - See GMAIL_SETUP.md"
    )

    if not passed:
        print("    To set up:")
        print("    1. Go to console.cloud.google.com")
        print("    2. Enable Gmail API")
        print("    3. Create OAuth credentials")
        print("    4. Download credentials.json")
        print("    5. Place in watchers/credentials/")

    return True  # Non-critical for filesystem watcher


def test_configuration():
    """Test configuration files."""
    print_header("Testing Configuration")

    env_example = Path(__file__).parent / ".env.example"
    env_file = Path(__file__).parent / ".env"

    print_check(".env.example exists", env_example.exists(), "Configuration template")

    if env_file.exists():
        print_check(".env exists", True, "Configuration ready")
    else:
        print_check(".env exists", False, "Run: copy .env.example .env")
        print("    Then edit .env with your settings")

    return True  # Non-critical, will use defaults


def test_pm2():
    """Test PM2 is installed."""
    print_header("Testing PM2 Process Manager")

    import subprocess

    try:
        result = subprocess.run(
            ["pm2", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        passed = result.returncode == 0
        version = result.stdout.strip() if passed else ""
        print_check("PM2 installed", passed, f"Version: {version}" if version else "")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        passed = False
        print_check("PM2 installed", False, "Run: npm install -g pm2")
        print("    PM2 is optional but recommended for daemon mode")

    return True  # Non-critical


def run_all_tests():
    """Run all tests and return summary."""
    print_header("Watcher System Test Suite")
    print("Testing all components before running watchers...")

    tests = [
        ("Python Version", test_python_version),
        ("Dependencies", test_imports),
        ("Vault Structure", test_vault_structure),
        ("Watcher Files", test_watcher_files),
        ("Base Watcher", test_base_watcher),
        ("Gmail Credentials", test_gmail_credentials),
        ("Configuration", test_configuration),
        ("PM2 Installation", test_pm2),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\nError in {name}: {e}")
            results.append((name, False))

    # Print summary
    print_header("Test Summary")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "PASS" if result else "FAIL"
        color = "\033[92m" if result else "\033[91m"
        reset = "\033[0m"
        print(f"{color}{status:6}{reset} {name}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All tests passed! Your watcher system is ready.")
        print("\nNext steps:")
        print("  1. Configure .env file with your settings")
        print("  2. Set up Gmail credentials (if using Gmail watcher)")
        print("  3. Run: python filesystem_watcher.py (to test)")
        print("  4. Run: pm2 start ecosystem.config.js (for daemon mode)")
        print("\nSee QUICKSTART.md for detailed setup instructions.")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nFor help:")
        print("  - See TROUBLESHOOTING.md for solutions")
        print("  - Run: pip install -r requirements.txt")
        print("  - Check documentation in watchers/ folder")

    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
