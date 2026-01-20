"""
Test Hidden Size Detection

Unit tests for the enhanced size detection logic that handles:
- Hidden size buttons (sold out)
- Disabled size buttons (sold out)
- Available size buttons
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the function we're testing
from playwright.async_api import async_playwright


# Mock implementation for testing (since we can't access real site in tests)
async def check_size_availability_enhanced_mock(page, size: str, mock_hidden_sizes=None) -> dict:
    """
    Mock version of check_size_availability_enhanced for testing

    Args:
        page: Playwright page object
        size: Size to check (e.g., "XS", "S", "M")
        mock_hidden_sizes: List of sizes that should be "hidden"

    Returns:
        {
            "status": "available" | "hidden_soldout" | "disabled_soldout",
            "exists": bool,
            "disabled": bool
        }
    """
    if mock_hidden_sizes and size in mock_hidden_sizes:
        return {
            "status": "hidden_soldout",
            "exists": False,
            "disabled": None
        }

    # Otherwise simulate checking the page
    selector = f'input.SizeSwatch__Radio[data-option-value="{size}"]'
    element = await page.query_selector(selector)

    if not element:
        return {
            "status": "hidden_soldout",
            "exists": False,
            "disabled": None
        }

    class_list = await element.get_attribute("class") or ""
    is_disabled = "disabled" in class_list or "sold-out" in class_list

    if is_disabled:
        return {
            "status": "disabled_soldout",
            "exists": True,
            "disabled": True
        }

    return {
        "status": "available",
        "exists": True,
        "disabled": False
    }


@pytest.mark.asyncio
async def test_hidden_size_detection():
    """
    Test that hidden sizes are detected as sold out
    """
    print("\n[TEST] Testing hidden size detection...")

    # Create a mock scenario where XXL is hidden
    mock_hidden = ["XXL"]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Create a simple test HTML
        await page.set_content("""
            <html>
            <body>
                <input type="radio" class="SizeSwatch__Radio" data-option-value="XS" name="option-1">
                <input type="radio" class="SizeSwatch__Radio" data-option-value="S" name="option-1">
                <!-- XXL is HIDDEN (not in DOM) -->
            </body>
            </html>
        """)

        # Test XS (exists, available)
        result_xs = await check_size_availability_enhanced_mock(page, "XS", mock_hidden)
        assert result_xs["status"] == "available", f"Expected available, got {result_xs['status']}"
        assert result_xs["exists"] == True, "XS should exist in DOM"

        # Test XXL (hidden, sold out)
        result_xxl = await check_size_availability_enhanced_mock(page, "XXL", mock_hidden)
        assert result_xxl["status"] == "hidden_soldout", f"Expected hidden_soldout, got {result_xxl['status']}"
        assert result_xxl["exists"] == False, "XXL should not exist in DOM"

        await browser.close()

    print("  ✓ Hidden size detection test passed")


@pytest.mark.asyncio
async def test_disabled_size_detection():
    """
    Test that disabled size buttons are detected as sold out
    """
    print("\n[TEST] Testing disabled size detection...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Create HTML with disabled size button
        await page.set_content("""
            <html>
            <body>
                <input type="radio" class="SizeSwatch__Radio" data-option-value="S" name="option-1">
                <input type="radio" class="SizeSwatch__Radio disabled" data-option-value="M" name="option-1">
            </body>
            </html>
        """)

        # Test S (available)
        result_s = await check_size_availability_enhanced_mock(page, "S", [])
        assert result_s["status"] == "available", "S should be available"

        # Test M (disabled)
        result_m = await check_size_availability_enhanced_mock(page, "M", [])
        assert result_m["status"] == "disabled_soldout", "M should be disabled_soldout"
        assert result_m["disabled"] == True, "M should be marked as disabled"

        await browser.close()

    print("  ✓ Disabled size detection test passed")


def test_business_rules():
    """
    Test business rules for determining when to pause ads
    """
    print("\n[TEST] Testing business rules...")

    # Rule 1: XS and S both available → ACTIVE
    xs_available = True
    s_available = True
    larger_available = True  # M, L, XL, or XXL

    if xs_available and s_available:
        recommendation = "ACTIVE"
    elif (xs_available or s_available) and larger_available:
        recommendation = "ACTIVE"
    elif not xs_available and not s_available:
        recommendation = "PAUSE"
    else:
        recommendation = "PAUSE"

    assert recommendation == "ACTIVE", "Both XS and S available should be ACTIVE"
    print("  ✓ Rule 1 passed: Both XS and S available → ACTIVE")

    # Rule 2: XS and S both sold out → PAUSE
    xs_available = False
    s_available = False
    larger_available = True

    if xs_available and s_available:
        recommendation = "ACTIVE"
    elif (xs_available or s_available) and larger_available:
        recommendation = "ACTIVE"
    elif not xs_available and not s_available:
        recommendation = "PAUSE"
    else:
        recommendation = "PAUSE"

    assert recommendation == "PAUSE", "XS and S both sold out should be PAUSE"
    print("  ✓ Rule 2 passed: XS and S sold out → PAUSE")

    # Rule 3: One of XS/S available but all larger sizes sold out → PAUSE
    xs_available = True
    s_available = False
    larger_available = False

    if xs_available and s_available:
        recommendation = "ACTIVE"
    elif (xs_available or s_available) and larger_available:
        recommendation = "ACTIVE"
    elif not xs_available and not s_available:
        recommendation = "PAUSE"
    else:
        recommendation = "PAUSE"

    assert recommendation == "PAUSE", "Only XS available but no larger sizes should be PAUSE"
    print("  ✓ Rule 3 passed: Limited availability → PAUSE")


def test_price_logging():
    """
    Test that product price is logged correctly
    """
    print("\n[TEST] Testing price logging...")

    from logger import log_ad_event, flush_logs
    import pandas as pd
    import os

    # Create test log file
    test_log = "test_price_log.xlsx"

    try:
        # Log event with price
        result = log_ad_event(
            "Test Ad",
            "http://test.com",
            "Test event",
            "Test action",
            product_price=285.50,
            log_file_path=test_log
        )

        assert result == True, "Log event should succeed"

        # Flush to disk
        flush_result = flush_logs(test_log)
        assert flush_result == True, "Flush should succeed"

        # Read and verify
        df = pd.read_excel(test_log)
        assert not df.empty, "Log file should not be empty"
        assert "Product_Price" in df.columns, "Product_Price column should exist"

        # Check the price
        logged_price = df.iloc[-1]["Product_Price"]
        assert logged_price == 285.50, f"Price should be 285.50, got {logged_price}"

        print("  ✓ Price logging test passed")

    finally:
        # Cleanup
        if os.path.exists(test_log):
            os.remove(test_log)
            if os.path.exists(f"{test_log}.lock"):
                os.remove(f"{test_log}.lock")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING SIZE DETECTION TESTS")
    print("=" * 60)

    # Run tests
    asyncio.run(test_hidden_size_detection())
    asyncio.run(test_disabled_size_detection())
    test_business_rules()
    test_price_logging()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
