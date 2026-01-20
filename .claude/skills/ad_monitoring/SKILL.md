---
name: ad_monitoring
description: Monitor e-commerce ads for stockouts, calculate revenue impact, and track product availability. Use when you need to (1) Check product availability, (2) Generate revenue loss reports, (3) Refresh dashboard data, or (4) Get ad performance metrics.
---

# Ad Monitoring Skill

## Overview
Monitors gulahmedshop.com product availability, tracks stockout duration, calculates revenue impact, and displays real-time analytics in FastAPI dashboard.

## Quick Start
```bash
# Check single product availability
cd .claude/skills/ad_monitoring
python scripts/check_product.py --url "https://www.gulahmedshop.com/products/..."

# Generate revenue impact report
python scripts/revenue_report.py --days 7

# Refresh dashboard
python scripts/refresh_dashboard.py
```

## Core Features

### 1. Hidden Size Detection
- Detects if size buttons are **hidden from DOM** (sold out) vs **visible but disabled**
- Returns detailed status: `"available" | "hidden_soldout" | "disabled_soldout"`
- Critical for sites that hide out-of-stock sizes instead of disabling them

### 2. Real-Time Price Scraping
- Extracts actual prices from product pages
- Handles PKR → USD conversion (1 USD = 280 PKR)
- Supports sale prices and original prices

### 3. Revenue Impact Calculation
- Formula: `days_out × product_price × conversion_rate`
- Per-product revenue loss tracking
- Priority scoring: `downtime_days × product_price`

### 4. Dashboard Analytics
- Top Selling Products section (ranked by revenue impact)
- Enhanced Offline Ads table with Product Price, Revenue Loss, Priority Score
- Configurable conversion rate parameter

## Integration with AI Employee System

### File Locations
```
ad_management/
├── 2Check_Availability.py     # Main monitoring script with hidden size detection
├── dashboard.py                # FastAPI dashboard with enhanced metrics
├── logger.py                   # Logging with Product_Price tracking
└── URLS.csv                    # Product data source
```

### Data Flow
```
1. 2Check_Availability.py scrapes products
   → Extracts price and checks sizes
   → Logs events with Product_Price

2. logger.py buffers events
   → Writes to Ad_Status_Log.xlsx

3. dashboard.py reads log file
   → Calculates revenue impact per product
   → Displays in dashboard with Top Products
```

## Core Functions

### check_product_availability(product_url: str) -> dict
Check if product is available for advertising.

**Returns:**
```json
{
  "available": true/false,
  "title": "Product Name",
  "price": 285.00,
  "size_status": {
    "XS": {"status": "available", "exists": true, "disabled": false},
    "S": {"status": "hidden_soldout", "exists": false, "disabled": null},
    ...
  },
  "recommendation": "ACTIVE" | "PAUSE"
}
```

### get_revenue_impact(days: int = 7, conversion_rate: float = 0.5) -> dict
Generate revenue impact report for specified period.

**Returns:**
```json
{
  "period_days": 7,
  "total_ads_monitored": 20,
  "currently_offline": 3,
  "total_revenue_loss": 1850.50,
  "top_impact_products": [
    {
      "ad_name": "Elegant Embroidered Lawn",
      "product_price": 495.00,
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

### refresh_dashboard() -> str
Trigger dashboard data refresh.

**Returns:**
```json
{
  "status": "Dashboard refreshed",
  "url": "http://localhost:8501",
  "last_update": "2026-01-20 10:30:00",
  "note": "Data updates every 15 minutes automatically"
}
```

## Usage Examples

### Example 1: Check Product Availability
```python
from scripts.check_product import check_product_availability
import asyncio

result = asyncio.run(check_product_availability(
    "https://www.gulahmedshop.com/products/elegant-summer-dress"
))

print(f"Product: {result['title']}")
print(f"Price: ${result['price']}")
print(f"Status: {result['recommendation']}")
```

### Example 2: Generate Revenue Report
```python
from scripts.revenue_report import get_revenue_impact

report = get_revenue_impact(days=7, conversion_rate=0.5)

print(f"Total Revenue Loss: ${report['total_revenue_loss']}")
print(f"Currently Offline: {report['currently_offline']} ads")

for product in report['top_impact_products'][:5]:
    print(f"  - {product['ad_name']}: ${product['revenue_loss']} loss")
```

### Example 3: Refresh Dashboard
```python
from scripts.refresh_dashboard import refresh_dashboard

status = refresh_dashboard()
print(status['status'])
print(f"Dashboard: {status['url']}")
```

## Scheduling

### Manual Execution
```bash
# Run availability check
python ad_management/2Check_Availability.py

# Launch dashboard
python ad_management/dashboard.py
# Visit: http://localhost:8501
```

### Automated Scheduling (Every 15 minutes)
Use the scheduler-manager skill:
```bash
python .claude/skills/scheduler-manager/scripts/schedule_task.py \
  --name "ad-monitoring-check" \
  --command "python ad_management/2Check_Availability.py" \
  --schedule "*/15 * * * *"
```

## Technical Details

### Size Detection Logic
The site HIDES out-of-stock sizes from DOM (not just disabled).

**Detection:**
1. Check if element exists in DOM using `page.query_selector()`
2. If not exists → `"hidden_soldout"`
3. If exists, check for `"disabled"` or `"sold-out"` class
4. Return detailed status

**Business Rules:**
- **ACTIVE**: XS and S both available
- **ACTIVE**: One of XS/S available AND one of M/L/XL/XXL available
- **PAUSE**: XS and S both sold out
- **PAUSE**: One of XS/S available but ALL of M/L/XL/XXL sold out

### Price Scraping Logic
**Selectors:**
- Original price: `.ProductMeta__Price--original`
- Regular price: `.ProductMeta__Price span`

**Currency Handling:**
- Parse numeric value: `re.sub(r'[^\d.]', '', price_text)`
- Convert PKR to USD: `price / 280` if `price > 1000`

### Revenue Calculation
**Formula:**
```
Revenue Loss = (days_out) × (product_price) × (conversion_rate)
Priority Score = (days_out) × (product_price)
```

**Parameters:**
- `conversion_rate`: Daily conversion rate (default: 0.5 = 50%)
- `days_out`: Total days product has been out of stock
- `product_price`: Latest price from logs (USD)

## Dashboard Configuration

### Access Dashboard
```bash
# Start dashboard server
python ad_management/dashboard.py

# Visit in browser
http://localhost:8501

# With custom conversion rate
http://localhost:8501?conversion_rate=0.7

# Change theme
http://localhost:8501?theme=white
```

### Dashboard Sections
1. **KPI Cards** - Currently Offline, Total Downtime, Revenue Impact, Total Events
2. **Top Selling Products** - Top 10 by revenue impact (priority score)
3. **Charts** - Event Activity (line/bar), Product Impact (pie chart)
4. **Daily Summary** - Stockouts, Restocks, Events per day
5. **Offline Ads Table** - Enhanced with Product Price, Revenue Loss, Priority Score
6. **Event History** - Full audit trail

## Troubleshooting

### Issue: Size detection not working
**Solution**: Check if CSS selectors match site structure. Inspect product page and update selectors in `2Check_Availability.py:81-142`.

### Issue: Price scraping returns 0
**Solution**: Verify price elements exist. Check for sale prices vs regular prices. Update currency conversion if needed.

### Issue: Revenue calculations incorrect
**Solution**: Ensure `Product_Price` field is populated in logs. Check conversion rate parameter. Verify log file has data.

### Issue: Dashboard not showing data
**Solution**: Check that `Ad_Status_Log.xlsx` exists and has data. Verify log file has `Product_Price` column.

## Success Metrics

- **Size Detection Accuracy**: ≥95%
- **Price Scraping Accuracy**: ≥95%
- **Performance**: Scrape 20 products in < 120 seconds
- **Dashboard Load Time**: < 3 seconds
- **Test Coverage**: ≥80%

## Dependencies

- Playwright (browser automation)
- Pandas (data processing)
- FastAPI (dashboard server)
- Jinja2 (HTML templating)
- OpenPyXL (Excel logging)

## Version History

- **v1.0** (2026-01-20) - Initial implementation
  - Hidden size detection
  - Price scraping
  - Revenue impact calculation
  - Top Selling Products dashboard
  - Agent skill integration
