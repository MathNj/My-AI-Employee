#!/usr/bin/env python3
"""
Check Product Availability

Checks if a product is available for advertising by:
1. Extracting product title and price
2. Checking size availability (hidden vs disabled detection)
3. Determining advertising recommendation (ACTIVE/PAUSE)

Usage:
    python check_product.py --url "https://www.gulahmedshop.com/products/..."
"""

import asyncio
import argparse
import json
import sys
import re
from pathlib import Path
from playwright.async_api import async_playwright

# Add ad_management to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "ad_management"))


async def check_size_availability_enhanced(page, size: str) -> dict:
    """
    Check if size is available by detecting:
    1. Element exists in DOM (hidden) vs visible but disabled

    Returns: {
        "status": "available" | "hidden_soldout" | "disabled_soldout",
        "exists": bool,
        "disabled": bool
    }
    """
    selector = f'input.SizeSwatch__Radio[data-option-value="{size}"]'

    # CRITICAL: Check if element EXISTS in DOM (hidden = sold out)
    element = await page.query_selector(selector)

    if not element:
        # Size button not in DOM = HIDDEN = SOLD OUT
        return {
            "status": "hidden_soldout",
            "exists": False,
            "disabled": None
        }

    # Element exists, check if disabled
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


async def check_product_availability(product_url: str) -> dict:
    """
    Check if product is available for advertising.

    Args:
        product_url: Product page URL

    Returns:
        {
            "available": bool,
            "title": str,
            "price": float,
            "size_status": dict,
            "recommendation": "ACTIVE" | "PAUSE",
            "availability": str
        }
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            await page.goto(product_url, wait_until="domcontentloaded", timeout=30000)

            # Extract title
            title_elem = await page.query_selector("h1.ProductMeta__Title")
            title = await title_elem.inner_text() if title_elem else "Unknown"

            # Extract price
            price = 0.0
            price_elem = await page.query_selector(".ProductMeta__Price--original")
            if not price_elem:
                price_elem = await page.query_selector(".ProductMeta__Price span")

            if price_elem:
                price_text = await price_elem.inner_text()
                # Parse currency
                price_numeric = re.sub(r'[^\d.]', '', price_text)
                price = float(price_numeric) if price_numeric else 0.0

                # Convert PKR to USD
                if "PKR" in price_text.upper() and price > 1000:
                    price = round(price / 280, 2)

            # Check sizes
            sizes = ["XS", "S", "M", "L", "XL", "XXL"]
            size_status = {}
            available_sizes = []

            for size in sizes:
                status = await check_size_availability_enhanced(page, size)
                size_status[size] = status
                if status["status"] == "available":
                    available_sizes.append(size)

            # Determine availability
            xs_status = size_status.get("XS", {}).get("status", "hidden_soldout")
            s_status = size_status.get("S", {}).get("status", "hidden_soldout")

            xs_available = xs_status == "available"
            s_available = s_status == "available"

            # Count available larger sizes
            larger_available = sum(
                1 for s in ["M", "L", "XL", "XXL"]
                if size_status.get(s, {}).get("status") == "available"
            )

            # Business rules
            if xs_available and s_available:
                availability = "Fully Available (XS + S)"
                should_pause = False
            elif (xs_available or s_available) and larger_available > 0:
                availability = "Partial Available (Some sizes)"
                should_pause = False
            elif not xs_available and not s_available:
                availability = "XS and S Sold Out"
                should_pause = True
            else:
                availability = "Limited Availability"
                should_pause = True

            return {
                "available": not should_pause,
                "title": title,
                "price": price,
                "size_status": size_status,
                "availability": availability,
                "recommendation": "PAUSE" if should_pause else "ACTIVE"
            }

        except Exception as e:
            return {
                "error": f"Failed to check product: {str(e)}",
                "url": product_url
            }

        finally:
            await browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Check product availability for advertising"
    )

    parser.add_argument(
        "--url",
        required=True,
        help="Product page URL to check"
    )

    args = parser.parse_args()

    # Run check
    result = asyncio.run(check_product_availability(args.url))

    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
