#!/usr/bin/env python3
"""
LinkedIn Credentials Validator and Setup

Validates existing credentials or guides through setup process.

Usage:
    python validate_credentials.py --setup      # Interactive setup
    python validate_credentials.py --validate   # Validate existing
    python validate_credentials.py --show       # Show current config
"""

import json
import sys
import argparse
from pathlib import Path
from getpass import getpass

# Import paths from linkedin_post
from linkedin_post import CREDENTIALS_PATH


def setup_credentials():
    """Interactive setup wizard for LinkedIn credentials."""
    print("=" * 60)
    print("LinkedIn API Credentials Setup")
    print("=" * 60)
    print()
    print("You need to create a LinkedIn App to get API credentials.")
    print()
    print("Steps:")
    print("1. Go to: https://www.linkedin.com/developers/")
    print("2. Click 'Create app'")
    print("3. Fill in app details:")
    print("   - App name: Personal AI Employee")
    print("   - LinkedIn Page: Your personal page or company page")
    print("   - App logo: Optional")
    print("4. Under 'Auth' tab:")
    print("   - Add redirect URL: http://localhost:8080/callback")
    print("5. Under 'Products' tab:")
    print("   - Request access to 'Share on LinkedIn'")
    print("6. Copy Client ID and Client Secret from 'Auth' tab")
    print()
    print("=" * 60)
    print()

    # Get credentials from user
    client_id = input("Enter your Client ID: ").strip()
    client_secret = getpass("Enter your Client Secret (hidden): ").strip()

    if not client_id or not client_secret:
        print("❌ Client ID and Client Secret are required")
        sys.exit(1)

    # Create credentials object
    credentials = {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': 'http://localhost:8080/callback',
        'scopes': ['w_member_social', 'r_liteprofile'],
        'created_at': Path(__file__).stat().st_mtime
    }

    # Save credentials
    CREDENTIALS_PATH.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(CREDENTIALS_PATH, 'w') as f:
            json.dump(credentials, f, indent=2)

        print()
        print("✅ Credentials saved successfully!")
        print(f"   Location: {CREDENTIALS_PATH}")
        print()
        print("Next steps:")
        print("1. Run: python test_connection.py")
        print("2. If test fails, run: python linkedin_post.py --authenticate")
        print()

    except Exception as e:
        print(f"❌ Error saving credentials: {e}")
        sys.exit(1)


def validate_credentials():
    """Validate existing credentials file."""
    print("=" * 60)
    print("LinkedIn Credentials Validation")
    print("=" * 60)
    print()

    if not CREDENTIALS_PATH.exists():
        print(f"❌ Credentials file not found: {CREDENTIALS_PATH}")
        print()
        print("Run setup: python validate_credentials.py --setup")
        sys.exit(1)

    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            creds = json.load(f)

        # Validate required fields
        required_fields = ['client_id', 'client_secret']
        missing = [f for f in required_fields if f not in creds or not creds[f]]

        if missing:
            print(f"❌ Missing required fields: {', '.join(missing)}")
            sys.exit(1)

        print("✅ Credentials file is valid")
        print()
        print("Configuration:")
        print(f"  Client ID: {creds['client_id'][:10]}...")
        print(f"  Client Secret: {'*' * 20}")
        print(f"  Redirect URI: {creds.get('redirect_uri', 'http://localhost:8080/callback')}")
        print(f"  Scopes: {', '.join(creds.get('scopes', ['w_member_social', 'r_liteprofile']))}")
        print()
        print("✅ All checks passed!")

    except json.JSONDecodeError:
        print("❌ Invalid JSON in credentials file")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading credentials: {e}")
        sys.exit(1)


def show_config():
    """Display current configuration (redacted)."""
    print("=" * 60)
    print("Current LinkedIn Configuration")
    print("=" * 60)
    print()

    if not CREDENTIALS_PATH.exists():
        print("❌ No credentials file found")
        print(f"   Expected location: {CREDENTIALS_PATH}")
        print()
        print("Run setup: python validate_credentials.py --setup")
        return

    try:
        with open(CREDENTIALS_PATH, 'r') as f:
            creds = json.load(f)

        print("Credentials:")
        print(f"  File: {CREDENTIALS_PATH}")
        print(f"  Client ID: {creds.get('client_id', 'Not set')[:10]}... (redacted)")
        print(f"  Client Secret: {'*' * 20} (hidden)")
        print(f"  Redirect URI: {creds.get('redirect_uri', 'Not set')}")
        print(f"  Scopes: {', '.join(creds.get('scopes', []))}")
        print()

    except Exception as e:
        print(f"❌ Error reading configuration: {e}")


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Credentials Management')

    parser.add_argument('--setup', action='store_true',
                        help='Interactive setup wizard')
    parser.add_argument('--validate', action='store_true',
                        help='Validate existing credentials')
    parser.add_argument('--show', action='store_true',
                        help='Show current configuration')

    args = parser.parse_args()

    if args.setup:
        setup_credentials()
    elif args.validate:
        validate_credentials()
    elif args.show:
        show_config()
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
