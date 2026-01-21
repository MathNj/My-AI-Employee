# Ad Management Enhancement Plan

**Date:** 2026-01-21
**Goal:** Enhance ad monitoring system with comprehensive analytics and automation

---

## Current System Analysis

### Existing Features
- ✅ Monitors product availability (in-stock/out-of-stock)
- ✅ Tracks ad status (on/off events)
- ✅ Shows revenue impact for out-of-stock products
- ✅ Dashboard with basic metrics
- ✅ Product data from URLS.csv (20 products)

### Missing Features (To Implement)
1. ❌ Ad spend tracking per product
2. ❌ Revenue impact calculation with ad spend
3. ❌ Heatmap visualization
4. ❌ Top selling products tracking
5. ❌ Worst selling products tracking
6. ❌ Back-in-stock alerts
7. ❌ Ad toggle automation (hide ads when sold out)

---

## Requirements Breakdown

### 1. Ad Spend Tracking
**What:** Track advertising spend for each product
**Data Needed:**
- Daily/hourly ad spend per product
- Ad spend source (Facebook Ads, Google Ads, etc.)
- Budget vs actual spend

**Implementation:**
- Add `ad_spend` column to URLS.csv
- Create ad spend logging system
- Track spend over time

### 2. Enhanced Revenue Impact
**What:** Calculate revenue loss considering ad spend
**Formula:**
```
Revenue Impact = (Days Out × Product Price × Conversion Rate) - Ad Spend
ROAS (Return on Ad Spend) = Revenue / Ad Spend
```

**Key Metrics:**
- Lost revenue from stockout
- Wasted ad spend on sold-out products
- ROAS by product
- Profit impact

### 3. Heatmap Visualization
**What:** Visual representation of performance metrics
**Types:**
- Stockout frequency heatmap
- Revenue impact heatmap
- Ad spend heatmap
- Time-based heatmap (day/week/month)

**Implementation:**
- Use Chart.js or Plotly
- Color-coded cells (green/red/yellow)
- Interactive filtering

### 4. Top Selling Products
**What:** Identify best performing products
**Metrics:**
- Sales volume
- Revenue generated
- ROAS
- Stockout frequency
- Profit margin

**Display:**
- Leaderboard table
- Performance charts
- Trend analysis

### 5. Worst Selling Products
**What:** Identify underperforming products
**Metrics:**
- Low sales volume
- Poor ROAS
- High stockout frequency
- Low profit margin

**Display:**
- Problem products table
- Action recommendations
- Optimization suggestions

### 6. Back-in-Stock Tracking
**What:** Alert when products return to stock
**Automation:**
- Monitor availability changes
- Log back-in-stock events
- Notify for ad reactivation
- Calculate missed opportunities

### 7. Ad Toggle Automation (Optional)
**What:** Automatically pause ads when sold out
**Automation:**
- Detect out-of-stock
- Pause ad (via API)
- Log action
- Restart ad when back in stock

**Challenges:**
- API integration required (Facebook Ads, Google Ads)
- Authentication setup
- Rate limiting

---

## Implementation Plan

### Phase 1: Data Structure Enhancement
**Duration:** 2 hours

**Tasks:**
1. Add new columns to URLS.csv:
   - `ad_spend_daily` - Daily ad budget
   - `ad_spend_actual` - Actual spend tracked
   - `sales_count` - Number of sales
   - `conversion_rate` - Conversion rate (0.0-1.0)
   - `days_since_last_stockout` - Days since last OOS
   - `total_stockout_days` - Total days OOS

2. Create new data file:
   - `ad_performance_log.csv` - Track daily performance
   - `stockout_history.csv` - Track stockout events

**Deliverable:**
- Enhanced CSV structure
- Data validation scripts

### Phase 2: Metrics Calculation Engine
**Duration:** 3 hours

**Tasks:**
1. Create `metrics_calculator.py`:
   - Calculate revenue impact with ad spend
   - Calculate ROAS
   - Track performance trends
   - Identify top/worst products

2. Formula implementation:
   ```python
   def calculate_revenue_impact(days_out, price, conversion_rate, ad_spend):
       lost_revenue = days_out * price * conversion_rate
       net_impact = lost_revenue - ad_spend
       roas = (price * conversion_rate) / ad_spend if ad_spend > 0 else 0
       return {
           'lost_revenue': lost_revenue,
           'wasted_ad_spend': ad_spend,
           'net_impact': net_impact,
           'roas': roas
       }
   ```

**Deliverable:**
- Metrics calculator module
- Formula documentation

### Phase 3: Dashboard Enhancements
**Duration:** 4 hours

**Tasks:**
1. Add new tabs to dashboard:
   - Ad Performance Tab
   - Heatmap Tab
   - Top/Worst Products Tab
   - Back-in-Stock Tab

2. Implement heatmap visualizations:
   - Stockout frequency heatmap
   - Revenue impact heatmap
   - Ad spend efficiency heatmap

3. Add performance tables:
   - Top 10 selling products
   - Bottom 10 selling products
   - Highest ROAS products
   - Lowest ROAS products

**Deliverable:**
- Enhanced dashboard HTML
- Interactive charts
- Performance tables

### Phase 4: Back-in-Stock Tracking
**Duration:** 2 hours

**Tasks:**
1. Create `stockout_tracker.py`:
   - Monitor availability changes
   - Detect back-in-stock events
   - Calculate missed opportunities
   - Send notifications

2. Logging system:
   - Log all stockout events
   - Log back-in-stock events
   - Track total downtime
   - Calculate opportunity cost

**Deliverable:**
- Stockout tracking module
- Event logging system

### Phase 5: Testing & Validation
**Duration:** 2 hours

**Tasks:**
1. Test with sample data
2. Validate calculations
3. Check dashboard performance
4. Verify all visualizations

**Deliverable:**
- Test report
- Bug fixes

---

## Data Model

### Enhanced URLS.csv Structure
```csv
URL,Ad Name,Product_Price,Category,Expected_Availability,Last_Price_Update,ad_spend_daily,ad_spend_actual,sales_count,conversion_rate,days_since_last_stockout,total_stockout_days
https://www.gulahmedshop.com/products/elegant-embroidered-lawn-3-piece,"Elegant Embroidered Lawn 3-Piece",495.00,Premium,"Fully Available (XS + S)",2026-01-20T10:30:00,50.00,45.50,15,0.02,5,12
```

### Ad Performance Log Structure
```csv
date,ad_name,status,ad_spend,revenue,roas,stockout_hours,conversion_count
2026-01-21,Elegant Embroidered Lawn 3-Piece,active,45.50,742.50,16.32,0,1
```

### Stockout History Structure
```csv
timestamp,ad_name,event,duration_hours,missed_sales,opportunity_cost
2026-01-21T10:00:00,Elegant Embroidered Lawn 3-Piece,out_of_stock,120,10,2475.00
2026-01-21T18:00:00,Elegant Embroidered Lawn 3-Piece,back_in_stock,0,0,0
```

---

## Dashboard Wireframe

### Tab 1: Overview (Current)
- Summary cards
- Current out-of-stock products
- Revenue impact
- Charts

### Tab 2: Ad Performance (NEW)
- Product list with ad spend
- ROAS by product
- Cost per acquisition
- Performance trend chart

### Tab 3: Heatmaps (NEW)
- Stockout frequency heatmap
- Revenue impact heatmap
- Ad spend heatmap
- Time filters (day/week/month)

### Tab 4: Top/Worst Products (NEW)
- Top 10 selling products table
- Bottom 10 selling products table
- Performance metrics
- Action recommendations

### Tab 5: Back-in-Stock (NEW)
- Recent back-in-stock events
- Missed opportunity calculation
- Time since back in stock
- Ad reactivation suggestions

---

## Metrics & KPIs

### Key Performance Indicators
1. **Revenue Impact**
   - Formula: Days Out × Price × Conversion Rate
   - Target: < PKR 50,000/month

2. **Wasted Ad Spend**
   - Formula: Ad Spend While Sold Out
   - Target: < PKR 5,000/month

3. **ROAS (Return on Ad Spend)**
   - Formula: Revenue / Ad Spend
   - Target: > 4.0

4. **Stockout Frequency**
   - Formula: Stockout Events / Total Days
   - Target: < 10%

### Performance Scores
- **Overall Score:** Combined metric of all KPIs
- **Priority Score:** Which products need attention first
- **Trend Score:** Improving or declining

---

## Technical Implementation

### File Structure
```
ad_management/
├── URLS.csv (enhanced)
├── ad_performance_log.csv (new)
├── stockout_history.csv (new)
├── metrics_calculator.py (new)
├── stockout_tracker.py (new)
├── heatmap_generator.py (new)
├── dashboard.py (enhanced)
└── 2Check_Availability.py (existing)
```

### Dependencies
```python
# Already installed
pandas, numpy, playwright, fastapi

# Need to add
plotly  # For interactive heatmaps
seaborn # For statistical visualizations
```

---

## Example Calculations

### Revenue Impact with Ad Spend
```
Product: Elegant Embroidered Lawn
Price: PKR 495
Days Out: 5
Conversion Rate: 2% (0.02)
Ad Spend Daily: PKR 50
Total Ad Spend: 5 × 50 = PKR 250

Lost Revenue = 5 × 495 × 0.02 = PKR 49.50
Wasted Ad Spend = PKR 250
Net Impact = PKR 49.50 - PKR 250 = -PKR 200.50 (loss)
ROAS = 49.50 / 250 = 0.20 (poor)
```

### Priority Score
```python
priority_score = (
    (days_out * 0.4) +
    (wasted_ad_spend / 1000 * 0.3) +
    (revenue_impact / 10000 * 0.3)
)
```

---

## User Stories

### Story 1: Ad Manager View
"As an ad manager, I want to see which products are wasting ad spend when sold out, so I can pause those ads and reallocate budget."

### Story 2: Product Performance
"As a product manager, I want to see top and worst selling products, so I can optimize my inventory."

### Story 3: Stockout Alerts
"As an operations manager, I want to be notified when products come back in stock, so I can resume advertising immediately."

### Story 4: Revenue Protection
"As a business owner, I want to see the revenue impact of stockouts, so I can prioritize inventory planning."

---

## Success Criteria

### Must Have (MVP)
1. ✅ Ad spend tracking per product
2. ✅ Enhanced revenue impact calculation (with ad spend)
3. ✅ Top 10 selling products table
4. ✅ Bottom 10 selling products table
5. ✅ Basic heatmap visualization
6. ✅ Back-in-stock tracking

### Should Have (Phase 2)
1. ⚠️ Ad toggle automation (pause ads when OOS)
2. ⚠️ Advanced heatmap interactivity
3. ⚠️ Forecasting and predictions
4. ⚠️ Export to Excel/PDF

### Could Have (Phase 3)
1. ⚠️ Machine learning recommendations
2. ⚠️ Real-time alerts (email/SMS)
3. ⚠️ Integration with ad platforms (Facebook/Google)

---

## Next Steps

**Question 1:** Do you want to proceed with implementing all these features?

**Question 2:** Should I start with Phase 1 (Data Structure) and work sequentially?

**Question 3:** Do you have actual ad spend data, or should I create sample/ad placeholder values?

**Question 4:** For the heatmap - which metrics are most important to visualize?

Let me know your preferences and I'll start implementing!
