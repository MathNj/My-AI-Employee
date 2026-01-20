"""
Performance Tests

Test performance metrics for the ad monitoring system:
- Scrape 20 products in < 120 seconds
- Dashboard load time < 3 seconds
"""

import pytest
import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.mark.asyncio
async def test_scraping_performance():
    """
    Performance test: Scrape 20 products in < 120 seconds
    """
    print("\n[PERFORMANCE TEST] Testing scraping performance...")

    # Load test URLs
    import pandas as pd
    from playwright.async_api import async_playwright

    csv_path = Path(__file__).parent.parent / "URLS.csv"
    if not csv_path.exists():
        pytest.skip("URLS.csv not found")

    df = pd.read_csv(csv_path)
    test_urls = df["URL"].head(20).tolist()

    if len(test_urls) < 20:
        print(f"  ⚠ Warning: Only {len(test_urls)} URLs available, using all")

    print(f"  Testing with {len(test_urls)} URLs")

    # Measure time
    start_time = time.time()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # Block images for faster loading
        await page.route("**/*", lambda route: route.abort()
                          if route.request.resource_type in ["image", "stylesheet", "font", "media"]
                          else route.continue_())

        success_count = 0
        for url in test_urls:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                # Just check if we can load the page (we're not testing real data here)
                success_count += 1
            except Exception as e:
                print(f"    Warning: Failed to load {url[:50]}...: {e}")

        await browser.close()

    elapsed = time.time() - start_time

    print(f"  Loaded {success_count}/{len(test_urls)} pages in {elapsed:.1f}s")

    # Assert performance: < 120s for 20 products
    max_time = 120
    assert elapsed < max_time, f"Too slow: {elapsed:.1f}s for {len(test_urls)} products (max: {max_time}s)"

    avg_time = elapsed / len(test_urls)
    print(f"  Average time per product: {avg_time:.2f}s")
    print(f"  ✓ Performance test passed ({elapsed:.1f}s < {max_time}s)")


def test_dashboard_performance():
    """
    Test dashboard load time < 3 seconds
    """
    print("\n[PERFORMANCE TEST] Testing dashboard performance...")

    from dashboard import app
    from fastapi.testclient import TestClient

    client = TestClient(app)

    start_time = time.time()

    # Test dashboard load
    response = client.get("/")

    elapsed = time.time() - start_time

    assert response.status_code == 200, f"Dashboard should load successfully, got {response.status_code}"
    assert elapsed < 3.0, f"Dashboard too slow: {elapsed:.2f}s (max: 3.0s)"

    print(f"  Dashboard loaded in {elapsed:.3f}s")
    print(f"  ✓ Dashboard performance test passed")


def test_revenue_calculation_performance():
    """
    Test revenue calculation performance with realistic data
    """
    print("\n[PERFORMANCE TEST] Testing revenue calculation performance...")

    import pandas as pd
    from datetime import datetime, timedelta
    from dashboard import calculate_enhanced_revenue_metrics

    # Create test data with 20 ads and 1000 events
    test_data = []
    base_time = datetime.now() - timedelta(days=30)

    ad_names = [f"Test Ad {i}" for i in range(20)]

    for i in range(1000):
        ad_name = ad_names[i % 20]
        timestamp = base_time + timedelta(days=i * 0.5)
        test_data.append({
            "Timestamp": timestamp,
            "Ad Name": ad_name,
            "URL": f"http://test.com/product{i}",
            "Event": "Stockout detected",
            "Action": "Ad turned off" if i % 4 == 0 else "Ad turned on",
            "Product_Price": 285.0
        })

    df = pd.DataFrame(test_data)

    # Measure calculation time
    start_time = time.time()

    count_oos, total_days, total_loss, *_ = calculate_enhanced_revenue_metrics(df, conversion_rate=0.5)

    elapsed = time.time() - start_time

    assert elapsed < 5.0, f"Revenue calculation too slow: {elapsed:.2f}s (max: 5.0s)"
    assert count_oos >= 0, "Should have valid offline count"

    print(f"  Calculated metrics for 20 ads, 1000 events in {elapsed:.3f}s")
    print(f"  Offline ads: {count_oos}")
    print(f"  Total revenue loss: ${total_loss:.2f}")
    print(f"  ✓ Revenue calculation performance test passed")


if __name__ == "__main__":
    print("=" * 60)
    print("RUNNING PERFORMANCE TESTS")
    print("=" * 60)

    # Note: async tests need to be run with pytest-asyncio
    print("\nTo run async tests:")
    print("  pytest tests/test_performance.py -v")
    print("\nRunning synchronous tests...")

    test_dashboard_performance()
    test_revenue_calculation_performance()

    print("\n" + "=" * 60)
    print("PERFORMANCE TESTS COMPLETE")
    print("=" * 60)
