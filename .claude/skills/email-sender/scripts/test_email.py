#!/usr/bin/env python3
"""
Email Connection Test - Verify SMTP/MCP configuration

Usage:
    python test_email.py              # Test all
    python test_email.py --smtp       # Test SMTP only
    python test_email.py --mcp        # Test MCP only
    python test_email.py --send-test --to "your-email@example.com"
"""

import argparse
import sys
from pathlib import Path
import send_email

def test_smtp_config():
    """Test SMTP configuration."""
    print("1. Testing SMTP configuration...")

    config = send_email.load_smtp_config()
    if not config:
        print("   ❌ SMTP config not found")
        print("   ℹ️  Create: watchers/credentials/smtp_config.json")
        return False

    required = ['smtp_server', 'email_address', 'email_password']
    missing = [f for f in required if f not in config or not config[f]]

    if missing:
        print(f"   ❌ Missing fields: {', '.join(missing)}")
        return False

    print("   ✅ SMTP configuration found")
    print(f"   ℹ️  Server: {config.get('smtp_server')}:{config.get('smtp_port', 587)}")
    print(f"   ℹ️  Email: {config.get('email_address')}")
    return True


def test_smtp_connection():
    """Test SMTP connection."""
    print("2. Testing SMTP connection...")

    try:
        # Send test email (dry run)
        result = send_email.send_via_smtp(
            to="test@example.com",
            subject="Test",
            body="Test email",
            dry_run=True
        )

        if result:
            print("   ✅ SMTP connection test passed (dry run)")
            return True
        else:
            print("   ❌ SMTP connection test failed")
            return False
    except Exception as e:
        print(f"   ❌ SMTP connection error: {e}")
        return False


def test_mcp():
    """Test MCP configuration."""
    print("3. Testing MCP server...")
    print("   ⚠️  MCP integration not yet implemented")
    print("   ℹ️  Will fall back to SMTP")
    return False


def send_test_email(to):
    """Send actual test email."""
    print(f"\n📤 Sending test email to {to}...")

    result = send_email.send_email(
        to=to,
        subject="Test Email from email-sender skill",
        body="This is a test email.\n\nIf you received this, the email-sender skill is working!",
        method='auto',
        dry_run=False
    )

    if result:
        print("✅ Test email sent successfully!")
        print("   Check your inbox (and spam folder)")
    else:
        print("❌ Failed to send test email")

    return result


def main():
    parser = argparse.ArgumentParser(description='Email Connection Test')

    parser.add_argument('--smtp', action='store_true',
                        help='Test SMTP only')
    parser.add_argument('--mcp', action='store_true',
                        help='Test MCP only')
    parser.add_argument('--send-test', action='store_true',
                        help='Send actual test email')
    parser.add_argument('--to', type=str,
                        help='Recipient for test email')

    args = parser.parse_args()

    print("=" * 60)
    print("Email Sender Configuration Test")
    print("=" * 60)
    print()

    if args.send_test:
        if not args.to:
            print("❌ --to required for --send-test")
            sys.exit(1)
        send_test_email(args.to)
        return

    tests_passed = 0
    tests_total = 0

    if not args.mcp:
        tests_total += 2
        if test_smtp_config():
            tests_passed += 1
        if test_smtp_connection():
            tests_passed += 1

    if not args.smtp:
        tests_total += 1
        if test_mcp():
            tests_passed += 1

    print()
    print("=" * 60)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    print("=" * 60)

    if tests_passed == tests_total:
        print("✅ All tests passed! Email sender is ready.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
