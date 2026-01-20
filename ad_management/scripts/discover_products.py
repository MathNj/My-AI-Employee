#!/usr/bin/env python3
"""
Product Discovery Script for gulahmedshop.com

This script navigates to product category pages, extracts product URLs,
titles, prices, and detects size availability patterns.

Usage:
    python scripts/discover_products.py --output ../URLS.csv --max-products 25
"""

import asyncio
import argparse
import csv
import re
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# Target categories to scrape
TARGET_CATEGORIES = [
    {
        "name": "Newness Collection",
        "url": "https://www.gulahmedshop.com/collections/newness-collection"
    },
    {
        "name": "Best Sellers",
        "url": "https://www.gulahmedshop.com/collections/best-sellers"
    },
    {
        "name": "Seasonal",
        "url": "https://www.gulahmedshop.com/collections/seasonal"
    }
]

# CSS Selectors for gulahmedshop.com
CSS_SELECTORS = {
    "product_card": ".ProductItem",
    "product_link": ".ProductItem__Title a",
    "product_title": "h1.ProductMeta__Title",
    "price_element": ".ProductMeta__Price span",
    "size_button": "input.SizeSwatch__Radio",
    "price_original": ".ProductMeta__Price--original",
}


async def check_size_availability_enhanced(page, size: str) -> dict:
    """
    Check if size exists in DOM (hidden) vs visible but disabled

    Returns: {
        "status": "available" | "hidden_soldout" | "disabled_soldout",
        "exists": bool,
        "disabled": bool
    }
    """
    selector = f'input.SizeSwatch__Radio[data-option-value="{size}"]'

    # CRITICAL: Check if element EXISTS in DOM
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


async def scrape_product_details(page, url: str) -> dict:
    """
    Scrape detailed product information including price and sizes

    Returns:
        {
            "title": str,
            "price": float,
            "url": str,
            "size_status": dict,
            "availability": str,
            "category": str
        }
    """
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)

        # Extract title
        title_elem = await page.query_selector(CSS_SELECTORS["product_title"])
        title = await title_elem.inner_text() if title_elem else "Unknown Product"

        # Extract price (handle PKR/USD, sale prices)
        price_elem = await page.query_selector(CSS_SELECTORS["price_original"])
        if not price_elem:
            price_elem = await page.query_selector(CSS_SELECTORS["price_element"])

        price = 0.0
        price_text = ""
        if price_elem:
            price_text = await price_elem.inner_text()
            # Parse currency: "PKR 28,500" → 28500, "$285.00" → 285.00
            price_numeric = re.sub(r'[^\d.]', '', price_text)
            price = float(price_numeric) if price_numeric else 0.0

            # Convert PKR to USD (1 USD = 280 PKR)
            if "PKR" in price_text.upper() and price > 1000:
                price = round(price / 280, 2)

        # Check sizes with enhanced detection
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        size_status = {}
        available_sizes = []

        for size in sizes:
            status = await check_size_availability_enhanced(page, size)
            size_status[size] = status
            if status["status"] == "available":
                available_sizes.append(size)

        # Determine availability category
        xs_status = size_status.get("XS", {}).get("status", "hidden_soldout")
        s_status = size_status.get("S", {}).get("status", "hidden_soldout")

        xs_available = xs_status == "available"
        s_available = s_status == "available"

        # Count available larger sizes
        larger_available = sum(
            1 for s in ["M", "L", "XL", "XXL"]
            if size_status.get(s, {}).get("status") == "available"
        )

        # Business rules for categorization
        if xs_available and s_available:
            availability = "Fully Available (XS + S)"
        elif (xs_available or s_available) and larger_available > 0:
            availability = "Partial Available (Some sizes)"
        elif not xs_available and not s_available:
            availability = "XS and S Sold Out"
        else:
            availability = "Limited Availability"

        # Categorize by price
        if price < 250:
            category = "Budget"
        elif price < 350:
            category = "Mid-Range"
        else:
            category = "Premium"

        return {
            "title": title,
            "price": price,
            "url": url,
            "size_status": size_status,
            "availability": availability,
            "category": category
        }

    except Exception as e:
        print(f"    ✗ Error scraping {url}: {e}")
        return None


async def extract_product_links_from_category(page, category_url: str, max_products: int = 10) -> list:
    """
    Extract product links from a category page

    Returns:
        List of product URLs
    """
    try:
        await page.goto(category_url, wait_until="domcontentloaded", timeout=30000)

        # Wait for product cards to load
        await page.wait_for_selector(CSS_SELECTORS["product_card"], timeout=10000)

        # Extract product links
        product_links = []
        links = await page.query_selector_all(CSS_SELECTORS["product_link"])

        for link in links[:max_products]:
            href = await link.get_attribute("href")
            if href:
                # Ensure full URL
                if href.startswith("/"):
                    full_url = f"https://www.gulahmedshop.com{href}"
                else:
                    full_url = href

                # Filter out non-product pages
                if "/products/" in full_url:
                    product_links.append(full_url)

        return product_links

    except Exception as e:
        print(f"    ✗ Error extracting links from {category_url}: {e}")
        return []


async def discover_products(output_csv: str, max_products: int = 25, delay_seconds: int = 2):
    """
    Main product discovery function

    Args:
        output_csv: Path to output CSV file
        max_products: Maximum number of products to discover
        delay_seconds: Delay between requests (to avoid rate limiting)
    """
    products = []

    print(f"[*] Starting product discovery for gulahmedshop.com")
    print(f"    Target: {max_products} products")
    print(f"    Output: {output_csv}")
    print(f"    Delay: {delay_seconds}s between requests")
    print()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        page = await context.new_page()

        # Block images/stylesheets for faster loading
        await page.route("**/*", lambda route: route.abort()
                          if route.request.resource_type in ["image", "stylesheet", "font", "media"]
                          else route.continue_())

        for category in TARGET_CATEGORIES:
            if len(products) >= max_products:
                break

            print(f"[*] Category: {category['name']}")
            print(f"    URL: {category['url']}")

            # Extract product links
            remaining = max_products - len(products)
            links = await extract_product_links_from_category(
                page,
                category['url'],
                max_products=remaining
            )

            print(f"   Found {len(links)} product links")

            # Scrape each product
            for i, link in enumerate(links, 1):
                if len(products) >= max_products:
                    break

                print(f"    [{i}/{len(links)}] Scraping: {link[:60]}...")

                # Delay to avoid rate limiting
                if i > 1:
                    await asyncio.sleep(delay_seconds)

                # Scrape product details
                product = await scrape_product_details(page, link)

                if product:
                    products.append(product)
                    print(f"      [+] {product['title'][:50]}...")
                    print(f"          Price: ${product['price']} | Category: {product['category']} | {product['availability']}")
                else:
                    print(f"      [-] Failed to scrape")

            print()

        await browser.close()

    # Write to CSV
    print(f"[*] Writing {len(products)} products to {output_csv}")

    output_path = Path(output_csv)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "URL",
            "Ad Name",
            "Product_Price",
            "Category",
            "Expected_Availability",
            "Last_Price_Update"
        ])

        for product in products:
            writer.writerow([
                product['url'],
                product['title'],
                product['price'],
                product['category'],
                product['availability'],
                datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            ])

    # Summary statistics
    print()
    print("=" * 60)
    print("DISCOVERY SUMMARY")
    print("=" * 60)
    print(f"Total products discovered: {len(products)}")

    if products:
        price_distribution = {}
        category_distribution = {}

        for p in products:
            # Price distribution
            cat = p['category']
            price_distribution[cat] = price_distribution.get(cat, 0) + 1

            # Category distribution
            avail = p['availability']
            category_distribution[avail] = category_distribution.get(avail, 0) + 1

        print()
        print("Price Distribution:")
        for cat, count in sorted(price_distribution.items()):
            pct = (count / len(products)) * 100
            print(f"  {cat}: {count} ({pct:.1f}%)")

        print()
        print("Availability Distribution:")
        for avail, count in sorted(category_distribution.items()):
            pct = (count / len(products)) * 100
            print(f"  {avail}: {count} ({pct:.1f}%)")

        print()
        avg_price = sum(p['price'] for p in products) / len(products)
        print(f"Average price: ${avg_price:.2f}")
        print(f"Price range: ${min(p['price'] for p in products):.2f} - ${max(p['price'] for p in products):.2f}")

    print()
    print(f"[+] Discovery complete! Output saved to: {output_path.absolute()}")


def main():
    parser = argparse.ArgumentParser(
        description="Discover products from gulahmedshop.com",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default discovery (25 products)
  python discover_products.py

  # Discover 50 products with 3 second delay
  python discover_products.py --max-products 50 --delay 3

  # Custom output path
  python discover_products.py --output ../my_products.csv
        """
    )

    parser.add_argument(
        "--output",
        default="../URLS.csv",
        help="Output CSV file path (default: ../URLS.csv)"
    )

    parser.add_argument(
        "--max-products",
        type=int,
        default=25,
        help="Maximum number of products to discover (default: 25)"
    )

    parser.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Delay between requests in seconds (default: 2)"
    )

    args = parser.parse_args()

    # Run discovery
    asyncio.run(discover_products(
        output_csv=args.output,
        max_products=args.max_products,
        delay_seconds=args.delay
    ))


if __name__ == "__main__":
    main()
