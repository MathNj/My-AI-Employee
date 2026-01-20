# Out of Stock
import nest_asyncio
import os
import sys
import smtplib
import requests
import asyncio
import pandas as pd
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from playwright.async_api import async_playwright

nest_asyncio.apply()

# Add parent directory to path to import shared logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import log_ad_event, flush_logs

counter = 0
current_date = datetime.now().strftime("%Y-%m-%d")

DRIVE_FILE_PATH = 'URLS.csv'
ACTIVE_AD_SHEET_PATH = "Active_Ads_List.csv"
LOG_FILE_PATH = "Ad_Status_Log.xlsx"

def ensure_urls_file():
    if not os.path.exists(DRIVE_FILE_PATH):
        pd.DataFrame(columns=["URL", "Ad Name"]).to_csv(DRIVE_FILE_PATH, index=False)
        print("Created URLS.csv with headers.")
    else:
        print("URLS.csv already exists.")

def load_stored_links():
    ensure_urls_file()
    stored_links = {}
    try:
        df = pd.read_csv(DRIVE_FILE_PATH)
        for _, row in df.iterrows():
            url = str(row.get("URL", "")).strip()
            ad_name = str(row.get("Ad Name", "")).strip()
            if url:
                stored_links.setdefault(url, []).append(ad_name)
    except Exception:
        pass
    return stored_links

def update_stored_links(new_urls, url_to_ads):
    rows_to_append = []
    for url in new_urls:
        ad_names = url_to_ads.get(url, ["Unknown Ad"])
        for ad_name in ad_names:
            rows_to_append.append({"URL": url, "Ad Name": ad_name})
    df_new = pd.DataFrame(rows_to_append)
    if os.path.exists(DRIVE_FILE_PATH):
        df_existing = pd.read_csv(DRIVE_FILE_PATH)
        df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df_combined = df_new
    df_combined.drop_duplicates(subset=["URL", "Ad Name"]).to_csv(DRIVE_FILE_PATH, index=False)

async def is_product_page(page):
    try:
        await page.wait_for_selector("h1.ProductMeta__Title", timeout=4000)
        await page.wait_for_selector("input.SizeSwatch__Radio", timeout=4000)
        return True
    except:
        return False

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
        print(f"    Size {size} → HIDDEN (Sold Out)")
        return {
            "status": "hidden_soldout",
            "exists": False,
            "disabled": None
        }

    # Element exists, check if disabled
    class_list = await element.get_attribute("class") or ""
    is_disabled = "disabled" in class_list or "sold-out" in class_list

    if is_disabled:
        print(f"    Size {size} → DISABLED (Sold Out)")
        return {
            "status": "disabled_soldout",
            "exists": True,
            "disabled": True
        }

    print(f"    Size {size} → AVAILABLE")
    return {
        "status": "available",
        "exists": True,
        "disabled": False
    }

async def check_sizes_availability(page):
    """
    Legacy wrapper for backward compatibility.
    Uses enhanced detection internally.
    """
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    availability_status = {}

    for size in sizes:
        status_info = await check_size_availability_enhanced(page, size)
        # Convert to boolean for backward compatibility
        availability_status[size] = status_info["status"] == "available"

    # Determine availability rule
    xs_available = availability_status.get("XS", False)
    s_available = availability_status.get("S", False)
    m_available = availability_status.get("M", False)
    l_available = availability_status.get("L", False)
    xl_available = availability_status.get("XL", False)
    xxl_available = availability_status.get("XXL", False)

    if xs_available and s_available:
        return "Both XS and S Available"
    elif (xs_available or s_available) and (m_available or l_available or xl_available or xxl_available):
        return "One of XS Or S Available and One of L, M, XL or XXL Available"
    elif not xs_available and not s_available:
        return "XS And S Sold Out"
    else:
        return "One of XS or S Available but All of L, M, XL, and XXL Sold Out"

async def scrape_product(page, url):
    """
    Enhanced product scraping with price and detailed size status

    Returns: {
        "title": str,
        "status": str,
        "availability": str,
        "URL": str,
        "price": float,  # NEW: Product price in USD
        "size_status": dict  # NEW: Detailed size status
    }
    """
    global counter
    import re

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        print(f"\nScraping URL: {url}")

        if "/collections/" in url:
            print("  Detected '/collections/' in URL. Checking if it's a product page...")
            if not await is_product_page(page):
                print("  Skipping. It's a collection landing page, not a product.")
                return None
            print("  Confirmed: This is a product page. Proceeding...")

        counter += 1

        # Extract title
        title_elem = page.locator("h1.ProductMeta__Title").first
        title = await title_elem.inner_text() if await title_elem.count() > 0 else "Title Not Found"

        # Extract price (NEW LOGIC)
        price = 0.0
        try:
            # Try original price first (for sale items)
            price_elem = await page.query_selector(".ProductMeta__Price--original")
            if not price_elem:
                # Fallback to regular price
                price_elem = await page.query_selector(".ProductMeta__Price span")

            if price_elem:
                price_text = await price_elem.inner_text()
                # Parse currency: "PKR 28,500" → 28500, "$285.00" → 285.00
                price_numeric = re.sub(r'[^\d.]', '', price_text)
                price = float(price_numeric) if price_numeric else 0.0

                # Convert PKR to USD (1 USD = 280 PKR)
                if "PKR" in price_text.upper() and price > 1000:
                    price = round(price / 280, 2)

                print(f"  Price: ${price} ({price_text})")
        except Exception as e:
            print(f"  Warning: Could not extract price: {e}")
            price = 0.0

        # Extract status
        status_elem = page.locator("div.ProductForm__BuyButtons").first
        status = await status_elem.inner_text() if await status_elem.count() > 0 else "Status Not Found"
        if "JOIN THE WAITLIST" in status:
            status = "Sold Out"

        # Check sizes with enhanced detection
        availability = await check_sizes_availability(page)

        # Get detailed size status (NEW)
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        size_status = {}
        for size in sizes:
            size_info = await check_size_availability_enhanced(page, size)
            size_status[size] = size_info

        if availability == "XS And S Sold Out" or availability == "One of XS or S Available but All of L, M, XL, and XXL Sold Out":
            print("Product appeared sold out, re-checking in 1 second...")
            await asyncio.sleep(1.0)
            second_check = await check_sizes_availability(page)
            if second_check != "XS And S Sold Out" and second_check != "One of XS or S Available but All of L, M, XL, and XXL Sold Out":
                print("False alarm — inconsistent results. Treating as available.")
                availability = second_check

        if availability == "XS And S Sold Out" or availability == "One of XS or S Available but All of L, M, XL, and XXL Sold Out":
            status = "Sold Out"

        # Return enhanced data structure
        return {
            "title": title,
            "status": status,
            "availability": availability,
            "URL": url,
            "price": price,  # NEW FIELD
            "size_status": size_status  # NEW FIELD
        }

    except Exception as e:
        print(f"  Error scraping {url}: {e}")
        return None

def process_product_data(product_data, ad_names):
    ad_names_text = "\n".join(ad_names)
    return (f"Product: {product_data['title']}\n"
            f"Ads: {ad_names_text}\n"
            f"URL: {product_data['URL']}\n"
            f"Buy Status: {product_data['status']}\n"
            f"Availability: {product_data['availability']}")

def process_multiple_products(products, url_to_ads):
    messages = []
    for product in products:
        if product:
            ad_names = url_to_ads.get(product['URL'], ["Unknown Ad"])
            messages.append(process_product_data(product, ad_names))
            
            # --- SPECIFIC LOGGING REQUIREMENT ---
            # ENHANCED: Now includes product price for revenue calculations
            product_price = product.get('price', 0.0)
            for ad_name in ad_names:
                log_ad_event(
                    ad_name,
                    product['URL'],
                    "Out of stock notification sent",
                    "Ad turned off",
                    product_price,  # NEW PARAMETER
                    LOG_FILE_PATH
                )
                
    return "\n\n".join(messages)

def send_slack_notification(message):
    slack_webhook_url = ""
    try:
        response = requests.post(slack_webhook_url, json={"text": message})
        response.raise_for_status()
        print("Slack notification sent!")
    except Exception as e:
        print(f"Error sending Slack notification: {e}")
        
def send_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print(f"Email sent to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

async def main():
    try:
        df = pd.read_csv(ACTIVE_AD_SHEET_PATH)
    except Exception as e:
        print("Error reading CSV:", e)
        return

    url_to_ads = {}
    for _, row in df.iterrows():
        url = str(row.get('URL')).strip()
        ad = str(row.get('Ad Name')).strip()
        if url.startswith("http"):
            url_to_ads.setdefault(url, []).append(ad)

    stored_links = load_stored_links()
    urls_to_check = [url for url in url_to_ads if url not in stored_links]

    if not urls_to_check:
        print("No new URLs to process.")
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.route("**/*", lambda route: route.abort() if route.request.resource_type in ["image", "stylesheet", "font", "media"] else route.continue_())

        products_info = []
        for url in urls_to_check:
            product = await scrape_product(page, url)
            if product:
                products_info.append(product)

        await page.close()
        await browser.close()

    sold_out_products = [p for p in products_info if p and (p['availability'] == "XS And S Sold Out" or p['availability'] == "One of XS or S Available but All of L, M, XL, and XXL Sold Out")]
    email_subject = f"Out of Stock Products Updates - {current_date}"
    
    # process_multiple_products also handles the logging now
    email_body = process_multiple_products(sold_out_products, url_to_ads) if sold_out_products else "No new products are sold out."

    sender_email = "" # REPLACE WITH GMAIL API
    sender_password = ""
    recipient_email = ""

    if sender_password and sold_out_products:
        send_email(sender_email, sender_password, recipient_email, email_subject, email_body)
        send_slack_notification(email_body)
        new_links = [product['URL'] for product in sold_out_products]
        update_stored_links(new_links, url_to_ads)
    elif not sold_out_products:
        print("No sold out products found.")
    else:
        print("Error: Email password not set.")

    # Flush all buffered logs to disk
    print("Flushing logs to disk...")
    flush_logs(LOG_FILE_PATH)

if __name__ == '__main__':
    asyncio.run(main())