#!/usr/bin/env python3
"""
LinkedIn Connection Test - Verify API connectivity

Tests:
- Credentials file exists and is valid
- OAuth token exists and is not expired
- API connection works
- User profile can be retrieved

Usage:
    python test_connection.py
    python test_connection.py --verbose
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
import requests

# Import paths from linkedin_post
from linkedin_post import (
    CREDENTIALS_PATH,
    TOKEN_PATH,
    load_credentials,
    load_token,
    get_user_id,
    API_BASE
)


def test_credentials():
    """Test if credentials file exists and is valid."""
    print("1. Testing credentials file...")

    if not CREDENTIALS_PATH.exists():
        print(f"   ❌ Credentials file not found: {CREDENTIALS_PATH}")
        return False

    try:
        creds = load_credentials()
        if not creds.get('client_id') or not creds.get('client_secret'):
            print("   ❌ Invalid credentials: missing client_id or client_secret")
            return False

        print(f"   ✅ Credentials file found and valid")
        return True
    except Exception as e:
        print(f"   ❌ Error reading credentials: {e}")
        return False


def test_token():
    """Test if OAuth token exists and is not expired."""
    print("2. Testing OAuth token...")

    if not TOKEN_PATH.exists():
        print(f"   ❌ Token file not found: {TOKEN_PATH}")
        print("   ℹ️  Run: python linkedin_post.py --authenticate")
        return False

    try:
        token_data = load_token()
        if not token_data:
            print("   ❌ Token expired or invalid")
            print("   ℹ️  Run: python linkedin_post.py --authenticate")
            return False

        expires_at = datetime.fromisoformat(token_data['expires_at'])
        days_remaining = (expires_at - datetime.now()).days

        print(f"   ✅ Token found and valid")
        print(f"   ℹ️  Expires in {days_remaining} days")
        return True
    except Exception as e:
        print(f"   ❌ Error reading token: {e}")
        return False


def test_api_connection(verbose=False):
    """Test API connection by retrieving user profile."""
    print("3. Testing API connection...")

    token_data = load_token()
    if not token_data:
        print("   ❌ No valid token available")
        return False

    access_token = token_data['access_token']

    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        response = requests.get(f"{API_BASE}/me", headers=headers)

        if response.status_code == 200:
            profile = response.json()
            user_id = profile.get('id')
            first_name = profile.get('localizedFirstName', 'Unknown')
            last_name = profile.get('localizedLastName', 'Unknown')

            print(f"   ✅ API connection successful")
            print(f"   ℹ️  Connected as: {first_name} {last_name}")

            if verbose:
                print(f"   ℹ️  User ID: {user_id}")
                print(f"   ℹ️  Profile: {json.dumps(profile, indent=2)}")

            return True
        else:
            print(f"   ❌ API request failed: {response.status_code}")
            if verbose:
                print(f"   ℹ️  Response: {response.text}")
            return False

    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return False


def test_post_permissions(verbose=False):
    """Test if account has permissions to create posts."""
    print("4. Testing post permissions...")

    token_data = load_token()
    if not token_data:
        print("   ❌ No valid token available")
        return False

    access_token = token_data['access_token']

    try:
        # Get user URN
        user_urn = get_user_id(access_token)
        if not user_urn:
            print("   ❌ Could not retrieve user ID")
            return False

        print(f"   ✅ Post permissions check passed")
        print(f"   ℹ️  User URN: {user_urn}")

        return True

    except Exception as e:
        print(f"   ❌ Permission check error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='LinkedIn Connection Test')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Show detailed output')

    args = parser.parse_args()

    print("=" * 60)
    print("LinkedIn API Connection Test")
    print("=" * 60)
    print()

    # Run all tests
    tests_passed = 0
    tests_total = 4

    if test_credentials():
        tests_passed += 1

    if test_token():
        tests_passed += 1

    if test_api_connection(args.verbose):
        tests_passed += 1

    if test_post_permissions(args.verbose):
        tests_passed += 1

    # Summary
    print()
    print("=" * 60)
    print(f"Test Results: {tests_passed}/{tests_total} passed")
    print("=" * 60)

    if tests_passed == tests_total:
        print("✅ All tests passed! LinkedIn integration is ready.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)


if __name__ == '__main__':
    main()
