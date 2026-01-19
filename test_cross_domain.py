#!/usr/bin/env python3
"""
Quick Test Script for Cross-Domain Integration

Tests basic functionality of the cross-domain-bridge skill.
"""

import sys
import subprocess
from pathlib import Path

# Vault path
VAULT_PATH = Path(__file__).parent

def test_enrichment():
    """Test context enrichment."""
    print("="*60)
    print("TEST 1: Context Enrichment")
    print("="*60)

    # Create test file
    test_file = VAULT_PATH / "Needs_Action" / "TEST_invoice_request.md"
    test_file.write_text("""---
type: whatsapp_message
from: +1234567890
timestamp: 2026-01-19T10:30:00Z
---

Can you send me the invoice for January work? We need it for accounting.
""", encoding='utf-8')

    print(f"Created test file: {test_file.name}")
    print(f"Content preview:\n{test_file.read_text()[:200]}...\n")

    # Run enrichment
    import subprocess
    enrich_script = VAULT_PATH / ".claude" / "skills" / "cross-domain-bridge" / "scripts" / "enrich_context.py"

    print("Running enrichment...")
    result = subprocess.run(
        [sys.executable, str(enrich_script), "--file", str(test_file)],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
        return False

    # Show enriched file
    print("\nEnriched file content:")
    print("-"*60)
    enriched_content = test_file.read_text(encoding='utf-8')
    print(enriched_content[:500])

    # Check for enrichment fields
    if 'domain:' in enriched_content and 'business_relevance_score:' in enriched_content:
        print("\n[OK] Enrichment successful - fields found!")
        return True
    else:
        print("\n[FAIL] Enrichment failed - fields not found")
        return False

def test_analysis():
    """Test cross-domain analysis."""
    print("\n" + "="*60)
    print("TEST 2: Cross-Domain Analysis")
    print("="*60)

    test_file = VAULT_PATH / "Needs_Action" / "TEST_invoice_request.md"

    # Run analysis
    analyze_script = VAULT_PATH / ".claude" / "skills" / "cross-domain-bridge" / "scripts" / "analyze_cross_domain.py"

    print("Running analysis...")
    result = subprocess.run(
        [sys.executable, str(analyze_script), "--file", str(test_file)],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
        return False

    print("\n[OK] Analysis completed!")
    return True

def cleanup():
    """Clean up test files."""
    print("\n" + "="*60)
    print("CLEANUP")
    print("="*60)

    test_file = VAULT_PATH / "Needs_Action" / "TEST_invoice_request.md"
    if test_file.exists():
        test_file.unlink()
        print(f"Removed test file: {test_file.name}")

def main():
    """Run all tests."""
    print("\nCross-Domain Integration - Quick Test")
    print("="*60)

    results = []

    # Test 1: Enrichment
    try:
        results.append(("Enrichment", test_enrichment()))
    except Exception as e:
        print(f"ERROR in enrichment test: {e}")
        results.append(("Enrichment", False))

    # Test 2: Analysis
    try:
        results.append(("Analysis", test_analysis()))
    except Exception as e:
        print(f"ERROR in analysis test: {e}")
        results.append(("Analysis", False))

    # Cleanup
    cleanup()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} {test_name}")

    all_passed = all(r[1] for r in results)
    print("\n" + "="*60)
    if all_passed:
        print("ALL TESTS PASSED!")
        print("Cross-domain integration is working correctly.")
    else:
        print("SOME TESTS FAILED")
        print("Please review the errors above.")
    print("="*60 + "\n")

    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
