# E-Commerce Ad Monitoring System - Implementation Plan

## Overview
Build an intelligent ad monitoring agent that tracks e-commerce product availability, calculates revenue impact from stockouts, and provides real-time analytics through a dashboard.

## Target Site
**Primary:** https://www.gulahmedshop.com/
- Size options: Small, Medium, Large, X-Large, XXL
- **Important:** Site HIDES out-of-stock sizes instead of disabling buttons

## Phase 1: Product Discovery & URL Collection

### Task 1.1: Site Structure Analysis
1. Navigate to https://www.gulahmedshop.com/
2. Identify product listing patterns:
   - Category pages structure
   - Product detail page URL patterns
   - Pagination behavior
3. Document CSS selectors for:
   - Product titles
   - Product links
   - Size buttons (hidden vs disabled detection)
   - Price elements
   - "Add to Cart" vs "Join Waitlist" buttons

### Task 1.2: Product URL Extraction
1. **Scrape Product Catalog:**
   - Extract 15-25 representative products
   - Include variations:
     - Different categories (Newness, Best Sellers, Seasonal)
     - Different price points ($150-$500 range)
     - Products with mixed availability (some sizes in stock, some out)

2. **Populate URLS.csv:**
   ```csv
   URL,Ad Name,Product_Price,Category
   https://example.com/product1,"Elegant Summer Dress",285,"Newness"
   https://example.com/product2,"Classic Kurta Set",195,"Best Sellers"
   ...
   ```

3. **Data Requirements:**
   - Minimum 15 product URLs
   - Real ad names from Google Ads or descriptive product names
   - Accurate prices (scraped or manual entry)
   - Category classification

## Phase 2: Availability Monitoring Implementation

### Task 2.1: Size Detection Logic (Critical)
**Challenge:** Site HIDES out-of-stock sizes (not disabled)

**Detection Strategy:**
```python
async def check_size_availability(page, size):
    """
    Check if size exists in DOM (hidden) vs visible but disabled
    Returns: 'available' | 'hidden_soldout' | 'disabled_soldout'
    """
    selector = f'inputSizeSwatch__Radio[data-option-value="{size}"]'

    # Check if element exists at all
    element = await page.query_selector(selector)
    if not element:
        return 'hidden_soldout'  # Size removed from DOM = sold out

    # Element exists, check if disabled
    class_list = await element.get_attribute('class') or ""
    if 'disabled' in class_list or 'sold-out' in class_list:
        return 'disabled_soldout'

    return 'available'
```

**Size Priority Rules (Match Business Logic):**
- **CRITICAL:** XS and S both available = AD ACTIVE
- **WARNING:** One of XS/S available AND one of M/L/XL/XXL available = AD ACTIVE
- **STOP AD:** XS and S both sold out = AD INACTIVE
- **STOP AD:** One of XS/S available BUT ALL of M/L/XL/XXL sold out = AD INACTIVE

### Task 2.2: Product Scraping Pipeline
**File:** `1Download_Ads_Sheets.py` (Already exists, enhance)

**Enhancements:**
1. Add price scraping to `scrape_product()` function
2. Store price in logger for revenue calculations
3. Handle hidden size detection

```python
async def scrape_product_with_price(page, url):
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)

    # Extract title
    title = await page.locator("h1.ProductMeta__Title").inner_text()

    # Extract price
    price_elem = await page.locator(".ProductMeta__Price").first
    price_text = await price_elem.inner_text()
    price = float(re.sub(r'[^\d.]', '', price_text))  # Parse price

    # Check all sizes
    size_status = {}
    for size in ["XS", "S", "M", "L", "XL", "XXL"]:
        status = await check_size_availability(page, size)
        size_status[size] = status

    return {
        "title": title,
        "price": price,
        "url": url,
        "size_status": size_status,
        "availability": calculate_availability_rule(size_status)
    }
```

### Task 2.3: Event Logging Enhancement
**File:** `logger.py` (Already exists)

**Add Price Tracking:**
```python
def log_ad_event_with_price(ad_name, url, event, action, price, log_file):
    """
    Log events with product price for revenue calculations
    """
    timestamp = datetime.now()
    log_entry = {
        "Timestamp": timestamp,
        "Ad Name": ad_name,
        "URL": url,
        "Event": event,
        "Action": action,
        "Product_Price": price  # NEW: Track price
    }
    append_to_excel(log_file, log_entry)
```

## Phase 3: Dashboard Analytics Implementation

### Task 3.1: Revenue Impact Calculation (Critical)
**File:** `dashboard.py` (Enhance existing)

**Requirements:**
1. **Per-Product Revenue Loss:**
   ```
   Revenue Loss = (Days Out of Stock) × (Product Price) × (Daily Conversion Rate)
   ```

2. **Daily Conversion Rate:**
   - Default: 0.5 sales/day per active ad
   - Configurable via dashboard parameter: `?conversion_rate=0.5`

3. **Display Requirements:**
   - **KPI Card:** Total Revenue Loss (sum across all ads)
   - **Offline Ads Table:** Per-ad revenue loss
   - **Top Selling Ads:** Sort by product price (descending)

**Implementation:**
```python
def calculate_revenue_metrics(df, conversion_rate=0.5):
    """
    Calculate revenue impact with product-specific prices
    """
    ad_metrics = {}

    for ad_name, group in df.groupby("Ad Name"):
        # Get product price from most recent log
        latest_price = group.iloc[-1].get("Product_Price", 285)

        # Calculate downtime
        total_days_out = calculate_downtime(group)

        # Revenue loss
        revenue_loss = total_days_out * latest_price * conversion_rate

        ad_metrics[ad_name] = {
            "product_price": latest_price,
            "days_out": total_days_out,
            "revenue_loss": revenue_loss,
            "url": group.iloc[-1]["URL"]
        }

    return ad_metrics
```

### Task 3.2: Top Selling Ads Section
**Add New Section to Dashboard:**

```html
<!-- Top Selling Products by Price -->
<div class="card p-5 mb-6">
    <h3 class="text-lg font-bold mb-4">
        <i class="ph-fill ph-trend-up text-green-500 mr-2"></i>
        Top Selling Products (by Price)
    </h3>
    <div class="overflow-x-auto">
        <table class="w-full">
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Product Name</th>
                    <th>Price</th>
                    <th>Status</th>
                    <th>Revenue Impact</th>
                </tr>
            </thead>
            <tbody>
                {% for product in top_products[:10] %}
                <tr class="table-row">
                    <td>{{ loop.index }}</td>
                    <td class="font-semibold">{{ product.ad_name }}</td>
                    <td class="text-green-600 font-bold">${{ product.price }}</td>
                    <td>
                        {% if product.status == 'available' %}
                            <span class="badge bg-green-100 text-green-700">Active</span>
                        {% else %}
                            <span class="badge bg-red-100 text-red-700">Offline</span>
                        {% endif %}
                    </td>
                    <td class="text-red-600 font-bold">${{ product.revenue_loss }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
```

### Task 3.3: Downtime Analytics Enhancement
**Enhance Existing Offline Ads Table:**

**Current:** Shows "Duration" and "Total Downtime"
**Add:**
1. **Time-based visualization:**
   - "Offline for 3 days 4 hours"
   - Progress bar showing % of month offline

2. **Revenue loss per row:**
   ```
   Column: Revenue Loss
   Value: $1,425 (5 days × $285 × 1.0 conversion)
   ```

3. **Actionable insights:**
   - Priority score: (Days Out) × (Price) = Priority Ranking
   - Sort by priority by default

## Phase 4: Automation & Scheduling

### Task 4.1: Monitoring Workflow
**File:** `runner.py` (Update existing)

**Enhanced Schedule:**
```python
scripts = [
    # Every 2 hours
    ("python3 1Download_Ads_Sheets.py", "Download Ads & Scrape Prices"),
    # Every 15 minutes
    ("python3 2Check_Availability.py", "Check Stockouts (Out of Stock)"),
    # Every 15 minutes
    ("python3 3Check_Availability.py", "Check Restocks (Back in Stock)")
]
```

**Cron Jobs:**
```bash
# Active Ads Refresh (Every 2 hours)
0 */2 * * * cd /path/to/ad_management && python3 1Download_Ads_Sheets.py

# Stockout Monitoring (Every 15 minutes)
*/15 * * * * cd /path/to/ad_management && python3 2Check_Availability.py

# Restock Monitoring (Every 15 minutes)
*/15 * * * * cd /path/to/ad_management && python3 3Check_Availability.py

# Dashboard Server (Always running)
@reboot cd /path/to/ad_management && python3 dashboard.py
```

### Task 4.2: Alert Configuration
**Slack Integration:**
1. **Immediate Alerts:**
   - Product goes out of stock (XS and S both sold out)
   - High-value product stockout (> $300)

2. **Daily Summary (9 AM):**
   - Top 5 products by revenue loss
   - Total downtime across all ads
   - Products back in stock

**Email Integration:**
- Weekly report: Revenue impact summary
- Monthly report: Performance trends

## Phase 5: Skill Implementation (Agent Integration)

### Task 5.1: Create Agent Skill
**New File:** `skills/ad_monitoring.py`

```python
"""
Ad Monitoring Skill for AI Employee System
Monitors e-commerce product availability and calculates revenue impact
"""

SKILL_NAME = "ad_monitoring"
SKILL_VERSION = "1.0.0"

async def check_product_availability(product_url: str) -> dict:
    """
    Check if product is available for advertising

    Args:
        product_url: URL to check

    Returns:
        {
            "available": bool,
            "size_status": {...},
            "price": float,
            "recommendation": "ACTIVE" | "PAUSE" | "WARNING"
        }
    """
    # Use 2Check_Availability.py logic
    pass

async def get_revenue_impact(days: int = 7) -> dict:
    """
    Calculate revenue impact for specified period

    Args:
        days: Number of days to analyze

    Returns:
        {
            "total_loss": float,
            "top_impact_products": [...],
            "recommendations": [...]
        }
    """
    # Read from Ad_Status_Log.xlsx
    pass

async def refresh_dashboard() -> str:
    """
    Trigger dashboard data refresh

    Returns:
        Dashboard URL
    """
    # Restart dashboard.py
    pass
```

### Task 5.2: Integration with AI Employee
**Add to Skills Manifest:**

```yaml
name: ad_monitoring
description: Monitor e-commerce ads, track stockouts, calculate revenue loss
triggers:
  - "check product availability"
  - "how much revenue did we lose"
  - "show ad performance"
  - "refresh dashboard"

parameters:
  product_url: string (optional)
  days: integer (default: 7)
  conversion_rate: float (default: 0.5)

output:
  - Availability status
  - Revenue impact report
  - Dashboard link
```

## Phase 6: Testing & Validation

### Task 6.1: Test Scenarios
**Test Data:**
1. Create 20 test products in URLS.csv
2. Include mixed availability scenarios

**Test Cases:**
- [ ] Product with all sizes available → Status: ACTIVE
- [ ] Product with XS/S sold out, M/L/XL available → Status: ACTIVE
- [ ] Product with XS/S sold out, M/L/XL sold out → Status: INACTIVE
- [ ] Product with XS available, M/L/XL sold out → Status: INACTIVE
- [ ] Price scraping accuracy (±5% tolerance)
- [ ] Revenue calculation accuracy

### Task 6.2: Performance Validation
**Target Metrics:**
- Scrape 20 products in < 2 minutes
- Dashboard load time < 3 seconds
- Memory usage < 500MB
- CPU usage < 20%

## Success Criteria

### Must Have (P0):
- ✅ Detect hidden size availability correctly
- ✅ Calculate per-product revenue loss
- ✅ Display top selling ads by price
- ✅ Show downtime for each ad in hours + days
- ✅ Dashboard shows revenue impact

### Should Have (P1):
- ⭐ Slack alerts for stockouts
- ⭐ Export revenue report to Excel
- ⭐ Historical trends (90-day retention)
- ⭐ Configurable conversion rate

### Nice to Have (P2):
- 🎯 Automated bidding adjustment recommendations
- 🎯 Competitor price tracking
- 🎯 Seasonal demand forecasting
- 🎯 A/B testing insights

## Implementation Checklist

### Phase 1: Discovery
- [ ] Analyze site structure for CSS selectors
- [ ] Scrape 20 product URLs
- [ ] Populate URLS.csv with accurate data
- [ ] Document size detection patterns

### Phase 2: Core Logic
- [ ] Implement hidden size detection
- [ ] Add price scraping to pipeline
- [ ] Enhance logger with price tracking
- [ ] Test size availability rules

### Phase 3: Dashboard
- [ ] Add revenue impact calculations
- [ ] Create Top Selling Ads section
- [ ] Enhance downtime display
- [ ] Add priority sorting

### Phase 4: Automation
- [ ] Configure cron jobs
- [ ] Set up Slack alerts
- [ ] Implement email reports
- [ ] Test monitoring pipeline

### Phase 5: Integration
- [ ] Create agent skill file
- [ ] Update skills manifest
- [ ] Test skill triggers
- [ ] Document API endpoints

### Phase 6: Testing
- [ ] Run test scenarios
- [ ] Validate revenue calculations
- [ ] Performance testing
- [ ] User acceptance testing

## Next Steps

**Immediate Actions:**
1. Visit https://www.gulahmedshop.com/ and inspect product pages
2. Document CSS selectors for size detection
3. Scrape 20 representative product URLs
4. Populate URLS.csv
5. Implement hidden size detection logic

**Week 1:** Complete Phase 1-2
**Week 2:** Complete Phase 3-4
**Week 3:** Complete Phase 5-6
**Week 4:** Testing & Documentation

---

## Notes for Implementation

**Critical Differences from Existing Code:**
1. **Size Detection:** Must handle HIDDEN sizes, not just disabled
2. **Price Tracking:** Currently mocked, needs real scraping
3. **Revenue Logic:** Currently uses daily revenue, needs per-product calculation
4. **Priority Sorting:** Currently by downtime, should be (downtime × price)

**File Modifications:**
- `2Check_Availability.py`: Add hidden size detection + price scraping
- `dashboard.py`: Add revenue calculations + top products section
- `logger.py`: Add Product_Price field to logs
- `URLS.csv`: Populate with real data

**New Files:**
- `skills/ad_monitoring.py`: Agent skill integration
- `tests/test_size_detection.py`: Unit tests for size logic
- `docs/AD_MONITORING_GUIDE.md`: User documentation
