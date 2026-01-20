# Back in Stock
import nest_asyncio
import pandas as pd
import smtplib
import requests
import time
import asyncio
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from playwright.async_api import async_playwright
from datetime import datetime

nest_asyncio.apply()

# Add parent directory to path to import shared logger
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from logger import log_ad_event, flush_logs

current_date = datetime.now().strftime("%Y-%m-%d")
LOG_FILE_PATH = "Ad_Status_Log.xlsx"

async def check_availability_xs_s(page):
    small_sizes = ["XS", "S"]
    large_sizes = ["M", "L", "XL", "XXL"]
    available_small = []
    available_large = []

    all_sizes = small_sizes + large_sizes
    for size in all_sizes:
        print(f"Checking size: {size}")
        size_locator = page.locator(f'input.SizeSwatch__Radio[data-option-value="{size}"]')

        await asyncio.sleep(3)
        if await size_locator.count() > 0:
            class_list = await size_locator.first.get_attribute("class") or ""
            print(f"  Found element for size {size}, class attribute: '{class_list}'")
            if "disabled" not in class_list and "sold-out" not in class_list:
                print(f"  Size {size} is available!")
                if size in small_sizes:
                    available_small.append(size)
                else:
                    available_large.append(size)
        else:
            print(f"  No element found for size {size}.")

    if len(available_small) == 2: 
        status = "back in stock"
    elif len(available_small) >= 1 and len(available_large) >= 1:  
        status = "back in stock"
    elif len(available_small) >= 1 and len(available_large) == 0: 
        status = "One of XS or S Available and All of L,M,XL,XXL Sold Out"
    else:  
        status = "XS and S Sold Out"

    print(f"Availability status: {status}")
    return status

async def scrape_product(url):
    print(f"\nStarting to scrape URL: {url}")
    async with async_playwright() as p:
        print("Launching Chromium browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            print("Navigating to the URL...")
            start_time = time.time()
            await page.goto(url, timeout=60000)
            elapsed = time.time() - start_time
            print(f"Page loaded in {elapsed:.2f} seconds.")

            title_elem = page.locator("h1.ProductMeta__Title").first
            title = await title_elem.inner_text() if await title_elem.count() > 0 else "Title Not Found"
            print(f"Product title: {title}")
            print(f"Product URL: {url}")

            status_elem = page.locator("div.ProductForm__BuyButtons").first
            status = await status_elem.inner_text() if await status_elem.count() > 0 else "Status Not Found"
            print(f"Product status from page: {status}")

            availability_status = await check_availability_xs_s(page)
            print(f"Availability: {availability_status}")

            return {"title": title, "status": status, "availability": availability_status, "URL": url}

        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
        finally:
            print("Closing browser...\n")
            await browser.close()

async def scrape_multiple_products(urls):
    products_info = []
    for url in urls:
        product_info = await scrape_product(url)
        products_info.append(product_info)
    return products_info

def process_product_data(product_data):
    return (f"Product: {product_data['title']}\n"
            f"URL: {product_data['URL']}\n"
            f"Availability: {product_data['availability']}")

def process_multiple_products(products):
    return "\n\n".join(process_product_data(product) for product in products)

def send_slack_notification(message):
    slack_webhook_url = ""
    payload = {"text": message}

    try:
        response = requests.post(slack_webhook_url, json=payload)
        response.raise_for_status()
        print("Slack notification sent successfully!")
    except Exception as e:
        print(f"Error sending Slack notification: {e}")

def send_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        print("Preparing email...")
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        print("Connecting to SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        print("Sending email...")
        server.sendmail(sender_email, recipient_email, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

async def main():
    csv_path = 'URLS.csv'
    try:
        df = pd.read_csv(csv_path)
        urls_with_ads = list(df[['URL', 'Ad Name']].dropna().itertuples(index=False, name=None))
    except Exception as e:
        print("Error reading URLS.csv:", e)
        return

    if not urls_with_ads:
        print("No URLs found in the CSV.")
        return
    print(f"Found {len(urls_with_ads)} entries in CSV.")

    urls = [url for url, _ in urls_with_ads]
    url_to_ads = {}
    for url, ad_name in urls_with_ads:
        url_to_ads.setdefault(url, []).append(ad_name)

    print("\nStarting product scraping process...")
    products_info = await scrape_multiple_products(urls)

    available_products = [p for p in products_info if p and p['availability'] == "back in stock"]

    available_products_grouped = {}
    for p in available_products:
        url = p['URL']
        if url not in available_products_grouped:
            available_products_grouped[url] = {
                "title": p['title'],
                "availability": p['availability'],
                "URL": url,
                "ads": set(url_to_ads.get(url, ["Unknown Ad"]))
            }
        else:
            available_products_grouped[url]["ads"].update(url_to_ads.get(url, ["Unknown Ad"]))

    def format_with_ads(product):
        ads_formatted = "\n  - " + "\n  - ".join(sorted(product["ads"]))
        return (f"Product: {product['title']}\n"
                f"Ads:{ads_formatted}\n"
                f"URL: {product['URL']}\n"
                f"Availability: {product['availability']}")

    # --- LOGGING ---
    if available_products_grouped:
        for url, data in available_products_grouped.items():
            for ad_name in data["ads"]:
                log_ad_event(ad_name, url, "Back in stock notification sent", "Ad turned on", LOG_FILE_PATH)

    if available_products_grouped:
        message = "\n\n".join(format_with_ads(p) for p in available_products_grouped.values())
        subject = f"BACK IN STOCK Status Updates - {current_date}"
    else:
        message = "NO NEW PRODUCTS are BACK IN STOCK"
        subject = f"BACK IN STOCK Status Updates - {current_date}"

    sender_email = "" # Replace with gmail api
    sender_password = ""
    recipient_email = ""

    if sender_password and available_products_grouped:
        send_email(sender_email, sender_password, recipient_email, subject, message)
        send_slack_notification(message)
        
    if available_products:
        available_urls = {p['URL'] for p in available_products}
        df_remaining = df[~df['URL'].isin(available_urls)]
        try:
            df_remaining.to_csv(csv_path, index=False)
            print("Updated URLS.csv: removed back-in-stock products.")
        except Exception as e:
            print("Error updating CSV:", e)

    # Flush all buffered logs to disk
    print("Flushing logs to disk...")
    flush_logs(LOG_FILE_PATH)

if __name__ == '__main__':
    asyncio.run(main())