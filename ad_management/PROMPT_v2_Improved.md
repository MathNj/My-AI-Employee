# Improved Prompt: E-Commerce Ad Monitoring Agent Implementation

## Context
You are building an intelligent e-commerce ad monitoring system for the AI Employee vault. The system tracks product availability on https://www.gulahmedshop.com/, calculates revenue impact from stockouts, and displays analytics in a real-time dashboard.

## Current State
- **Existing files:** `dashboard.py`, `1Download_Ads_Sheets.py`, `2Check_Availability.py`, `3Check_Availability.py`
- **Sample data:** `URLS.csv` (currently has placeholder data)
- **Functionality:** Basic stockout detection, event logging, simple dashboard

## Your Mission

### Step 1: Product Discovery & URL Collection
1. Visit **https://www.gulahmedshop.com/**
2. Navigate to product categories: "Newness Collection", "Best Sellers", "Seasonal"
3. Extract **15-25 product URLs** representing:
   - Various price points ($150 - $500)
   - Mixed size availability scenarios
   - Different categories
4. **CRITICAL:** Inspect product pages to identify:
   - How size buttons are rendered (hidden vs disabled for out-of-stock)
   - CSS selectors for: product title, price, size options, add-to-cart button
5. Populate `URLS.csv` with columns:
   ```
   URL,Ad Name,Product_Price,Category,Expected_Availability
   https://www.gulahmedshop.com/products/elegant-summer-dress,"Elegant Summer Dress",285,"Newness","Mixed"
   ```

### Step 2: Implement Hidden Size Detection
**Challenge:** The site HIDES out-of-stock size buttons instead of disabling them.

**Required Changes to `2Check_Availability.py`:**

```python
async def check_size_availability_enhanced(page, size):
    """
    Detect if size is hidden (sold out) vs visible (available)
    Returns: 'available' | 'hidden_soldout' | 'disabled_soldout'
    """
    selector = f'input.SizeSwatch__Radio[data-option-value="{size}"]'

    # Check if element exists in DOM
    element = await page.query_selector(selector)
    if not element:
        print(f"    Size {size} → HIDDEN (Sold Out)")
        return 'hidden_soldout'

    # Element exists, check if disabled
    class_list = await element.get_attribute('class') or ""
    if 'disabled' in class_list or 'sold-out' in class_list:
        print(f"    Size {size} → DISABLED (Sold Out)")
        return 'disabled_soldout'

    print(f"    Size {size} → AVAILABLE")
    return 'available'

async def scrape_product_with_price_and_sizes(page, url):
    """
    Enhanced product scraping with price and size detection
    """
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)

    # Extract title
    title_elem = await page.query_selector("h1.ProductMeta__Title")
    title = await title_elem.inner_text() if title_elem else "Unknown"

    # Extract price
    price_elem = await page.query_selector(".ProductMeta__Price span")
    price_text = await price_elem.inner_text() if price_elem else "$0"
    price = float(re.sub(r'[^\d.]', '', price_text))

    # Check all sizes
    sizes = ["XS", "S", "M", "L", "XL", "XXL"]
    size_status = {}
    available_sizes = []

    for size in sizes:
        status = await check_size_availability_enhanced(page, size)
        size_status[size] = status
        if status == 'available':
            available_sizes.append(size)

    # Determine availability rule
    xs_available = size_status.get("XS") == 'available'
    s_available = size_status.get("S") == 'available'
    m_available = size_status.get("M") == 'available'
    l_available = size_status.get("L") == 'available'
    xl_available = size_status.get("XL") == 'available'
    xxl_available = size_status.get("XXL") == 'available'

    # Business rules
    if xs_available and s_available:
        availability = "Both XS and S Available"
    elif (xs_available or s_available) and (m_available or l_available or xl_available or xxl_available):
        availability = "One of XS Or S Available and One of L, M, XL or XXL Available"
    elif not xs_available and not s_available:
        availability = "XS And S Sold Out"
    else:
        availability = "One of XS or S Available but All of L, M, XL, and XXL Sold Out"

    return {
        "title": title,
        "price": price,
        "url": url,
        "size_status": size_status,
        "availability": availability
    }
```

### Step 3: Enhanced Revenue Impact Tracking

**Update `dashboard.py` with these calculations:**

```python
def calculate_enhanced_revenue_metrics(df, conversion_rate=0.5):
    """
    Calculate revenue impact with per-product pricing
    """
    if df.empty:
        return 0, 0.0, 0.0, [], {}

    ad_metrics = []
    total_revenue_loss = 0.0
    total_downtime_days = 0.0

    for ad_name, group in df.groupby("Ad Name"):
        group = group.sort_values("Timestamp")

        # Get latest product price
        latest_price = 285.0  # Default
        if "Product_Price" in group.columns:
            latest_price = group.iloc[-1]["Product_Price"]

        # Calculate downtime
        is_oos = False
        oos_start = None
        ad_downtime = 0.0

        for _, row in group.iterrows():
            action = str(row.get("Action", "")).lower()
            timestamp = row["Timestamp"]

            if "off" in action and not is_oos:
                is_oos = True
                oos_start = timestamp
            elif "on" in action and is_oos and oos_start:
                ad_downtime += (timestamp - oos_start).total_seconds() / 86400
                is_oos = False
                oos_start = None

        # Currently offline
        if is_oos and oos_start:
            current_downtime = (datetime.now() - oos_start).total_seconds() / 86400
            ad_downtime += current_downtime

        # Revenue loss = (days out) × (price) × (conversion rate)
        revenue_loss = ad_downtime * latest_price * conversion_rate

        ad_metrics.append({
            "ad_name": ad_name,
            "url": group.iloc[-1]["URL"],
            "product_price": latest_price,
            "days_out": round(ad_downtime, 1),
            "revenue_loss": round(revenue_loss, 2),
            "priority_score": round(ad_downtime * latest_price, 2),
            "event_count": len(group)
        })

        total_revenue_loss += revenue_loss
        total_downtime_days += ad_downtime

    # Sort by priority score (downtime × price)
    ad_metrics.sort(key=lambda x: x["priority_score"], reverse=True)

    return len(ad_metrics), total_downtime_days, total_revenue_loss, ad_metrics
```

### Step 4: Dashboard Enhancements

**Add to `dashboard.py` HTML template:**

**A) Top Selling Products Section:**
```html
<!-- Insert after KPI Cards, before Charts -->
<div class="card p-5 mb-6">
    <div class="flex items-center justify-between mb-4">
        <div>
            <h3 class="text-lg font-bold">
                <i class="ph-fill ph-trend-up text-green-500 mr-2"></i>
                Top Selling Products
            </h3>
            <p class="text-xs text-muted">Ranked by product price (revenue impact)</p>
        </div>
        <span class="badge bg-blue-100 text-blue-700">Priority View</span>
    </div>
    <div class="overflow-x-auto">
        <table class="w-full">
            <thead>
                <tr style="background: var(--bg_hover);">
                    <th class="px-4 py-3 text-left text-xs font-black uppercase">Rank</th>
                    <th class="px-4 py-3 text-left text-xs font-black uppercase">Product</th>
                    <th class="px-4 py-3 text-left text-xs font-black uppercase">Price</th>
                    <th class="px-4 py-3 text-left text-xs font-black uppercase">Status</th>
                    <th class="px-4 py-3 text-left text-xs font-black uppercase">Days Out</th>
                    <th class="px-4 py-3 text-left text-xs font-black uppercase">Revenue Loss</th>
                </tr>
            </thead>
            <tbody>
                {% for product in top_products[:10] %}
                <tr class="table-row">
                    <td class="px-4 py-3 font-bold text-lg">{{ loop.index }}</td>
                    <td class="px-4 py-3 font-semibold">{{ product.ad_name }}</td>
                    <td class="px-4 py-3">
                        <span class="text-green-600 font-black text-lg">${{ product.product_price }}</span>
                    </td>
                    <td class="px-4 py-3">
                        {% if product.days_out > 0 %}
                            <span class="badge bg-gradient-to-r from-red-500 to-red-600 text-white">
                                Offline ({{ product.days_out }}d)
                            </span>
                        {% else %}
                            <span class="badge bg-green-100 text-green-700">Active</span>
                        {% endif %}
                    </td>
                    <td class="px-4 py-3 text-sm">{{ product.days_out }} days</td>
                    <td class="px-4 py-3">
                        <span class="text-red-600 font-bold">${{ product.revenue_loss }}</span>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

**B) Enhanced Offline Ads Table:**
Add columns to existing table:
- **Product Price:** Show individual product price
- **Revenue Loss:** Calculate per-ad loss
- **Priority Score:** Sort by (days_out × price)

### Step 5: Update Logger for Price Tracking

**Modify `logger.py`:**
```python
def log_ad_event_with_price(ad_name, url, event, action, product_price, log_file):
    """
    Log ad event with product price for revenue calculations
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = {
        "Timestamp": timestamp,
        "Ad Name": ad_name,
        "URL": url,
        "Event": event,
        "Action": action,
        "Product_Price": product_price  # NEW FIELD
    }

    # Append to Excel
    df = pd.DataFrame([new_row])
    if os.path.exists(log_file):
        df_existing = pd.read_excel(log_file)
        df_combined = pd.concat([df_existing, df], ignore_index=True)
        df_combined.to_excel(log_file, index=False)
    else:
        df.to_excel(log_file, index=False)
```

### Step 6: Create Agent Skill

**New file: `skills/ad_monitoring.py`**
```python
"""
Ad Monitoring Skill - Monitor e-commerce ads and track revenue impact
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ad_management"))

async def check_product_availability(product_url: str) -> dict:
    """
    Check if product is available for advertising

    Args:
        product_url: Product page URL

    Returns:
        {
            "available": bool,
            "title": str,
            "price": float,
            "size_status": dict,
            "recommendation": "ACTIVE" | "PAUSE"
        }
    """
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        result = await scrape_product_with_price_and_sizes(page, product_url)

        await browser.close()

        # Determine recommendation
        should_pause = "Sold Out" in result["availability"]

        return {
            "available": not should_pause,
            "title": result["title"],
            "price": result["price"],
            "size_status": result["size_status"],
            "recommendation": "PAUSE" if should_pause else "ACTIVE"
        }

async def get_revenue_impact_report(days: int = 7) -> dict:
    """
    Generate revenue impact report for specified period

    Args:
        days: Number of days to analyze

    Returns:
        {
            "period_days": int,
            "total_ads_monitored": int,
            "currently_offline": int,
            "total_revenue_loss": float,
            "top_impact_products": list,
            "recommendations": list
        }
    """
    import pandas as pd
    from datetime import datetime, timedelta

    log_file = "global/Ad_Status_Log.xlsx"
    df = pd.read_excel(log_file)

    # Filter by date
    cutoff = datetime.now() - timedelta(days=days)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df_filtered = df[df["Timestamp"] >= cutoff]

    # Calculate metrics
    currently_offline, total_days, total_loss, metrics = calculate_enhanced_revenue_metrics(df_filtered)

    return {
        "period_days": days,
        "total_ads_monitored": len(metrics),
        "currently_offline": currently_offline,
        "total_revenue_loss": round(total_loss, 2),
        "top_impact_products": metrics[:10],
        "recommendations": [
            f"Pause {m['ad_name']} (${m['revenue_loss']} loss)"
            for m in metrics[:3]
        ]
    }

async def refresh_dashboard_data() -> str:
    """
    Trigger dashboard data refresh

    Returns:
        Dashboard URL and status
    """
    dashboard_url = "http://localhost:8501"
    return {
        "status": "Dashboard refreshed",
        "url": dashboard_url,
        "note": "Data updates every 15 minutes automatically"
    }

# Skill metadata
SKILL_INFO = {
    "name": "ad_monitoring",
    "version": "1.0.0",
    "description": "Monitor e-commerce ads, track stockouts, calculate revenue loss",
    "triggers": [
        "check product availability",
        "how much revenue did we lose",
        "show ad performance",
        "refresh dashboard"
    ]
}
```

### Step 7: Testing & Validation

**Test Checklist:**

1. **Size Detection Test:**
   - [ ] Detect hidden size buttons as "sold out"
   - [ ] Detect disabled size buttons as "sold out"
   - [ ] Correctly identify available sizes
   - [ ] Apply business rules correctly (XS/S priority)

2. **Price Scraping Test:**
   - [ ] Extract accurate prices from 20 products
   - [ ] Handle currency symbols correctly ($, PKR, etc.)
   - [ ] Parse sale prices vs original prices

3. **Revenue Calculation Test:**
   - [ ] Calculate per-product revenue loss
   - [ ] Sum totals correctly across all ads
   - [ ] Apply conversion rate multiplier

4. **Dashboard Display Test:**
   - [ ] Top products sorted by price (descending)
   - [ ] Offline ads show individual revenue loss
   - [ ] Priority sorting works (downtime × price)

5. **End-to-End Test:**
   - [ ] Scrape 20 products from URLS.csv
   - [ ] Detect stockouts correctly
   - [ ] Log events with prices
   - [ ] Display accurate metrics in dashboard

## Acceptance Criteria

### Must Have (P0):
✅ Detect hidden size availability (not just disabled)
✅ Scrape and store product prices
✅ Calculate per-product revenue loss: `days_out × price × conversion_rate`
✅ Display top selling products sorted by price
✅ Show downtime in days + hours for each ad
✅ Dashboard shows individual and total revenue impact

### Should Have (P1):
⭐ Populate URLS.csv with 15-25 real products
⭐ Add priority score sorting (downtime × price)
⭐ Export revenue report to Excel
⭐ Configurable conversion rate parameter

### Nice to Have (P2):
🎯 Automated bid adjustment recommendations
🎯 Seasonal trend analysis
🎯 Competitor price comparison
🎯 Email/Slack alerts for high-value stockouts

## Deliverables

1. **Enhanced Code Files:**
   - `2Check_Availability.py` - Hidden size detection + price scraping
   - `dashboard.py` - Revenue calculations + top products section
   - `logger.py` - Price tracking in logs
   - `skills/ad_monitoring.py` - New agent skill

2. **Data:**
   - `URLS.csv` - Populated with 15-25 real products from gulahmedshop.com

3. **Documentation:**
   - Testing results (pass/fail for each test case)
   - Sample dashboard screenshots
   - API usage examples

## Success Metrics

- **Accuracy:** 95%+ correct size detection
- **Performance:** Scrape 20 products in < 2 minutes
- **Reliability:** 0 crashes in 24-hour monitoring period
- **Usability:** Dashboard loads in < 3 seconds

---

## Quick Start Commands

```bash
# 1. Populate URLS.csv
python scripts/scrape_product_urls.py

# 2. Test size detection
python tests/test_size_detection.py

# 3. Run monitoring pipeline
python ad_management/runner.py

# 4. Launch dashboard
python ad_management/dashboard.py
# Visit: http://localhost:8501

# 5. Test agent skill
python -c "
import asyncio
from skills.ad_monitoring import check_product_availability

result = asyncio.run(check_product_availability('https://www.gulahmedshop.com/products/sample'))
print(result)
"
```

---

## Example Expected Output

**Dashboard Top Selling Products Section:**
```
Rank | Product Name              | Price  | Status          | Days Out | Revenue Loss
-----|---------------------------|--------|-----------------|----------|-------------
1    | Elegant Embroidered Lawn | $495   | Offline (3.2d)  | 3.2      | $792.00
2    | Luxury Chiffon Collection | $425   | Active          | 0.0      | $0.00
3    | Summer Festive Edition    | $385   | Offline (1.5d)  | 1.5      | $288.75
...
```

**Revenue Impact API Response:**
```json
{
  "period_days": 7,
  "total_ads_monitored": 20,
  "currently_offline": 3,
  "total_revenue_loss": 1850.50,
  "top_impact_products": [
    {
      "ad_name": "Elegant Embroidered Lawn",
      "product_price": 495,
      "days_out": 3.2,
      "revenue_loss": 792.00,
      "priority_score": 1584
    }
  ],
  "recommendations": [
    "Pause Elegant Embroidered Lawn ($792 loss)",
    "Pause Summer Festive Edition ($288.75 loss)"
  ]
}
```

---

**Ready to implement? Start with Step 1: Visit gulahmedshop.com and scrape those product URLs!** 🚀
