# Ad Monitoring System - Integration Guide

**Status**: ✅ **FULLY INTEGRATED** with AI Employee System
**Date**: 2026-01-20

---

## 🎯 Overview

The Ad Monitoring system has been successfully integrated with the existing AI Employee application. This document describes how to use the new features.

---

## ✅ Integration Points

### 1. Orchestrator Integration

**File Modified:** `watchers/orchestrator.py` (lines 207-223)

**New Processes Added:**
```python
# Ad Monitoring (NEW)
self.processes['ad_monitor'] = Process(
    name='Ad Monitor',
    script='../ad_management/2Check_Availability.py',
    enabled=False,  # Disabled by default - user can enable
    restart_on_fail=True
)

# Dashboard Server (NEW)
self.processes['dashboard'] = Process(
    name='Dashboard',
    script='../ad_management/dashboard.py',
    enabled=False,  # Disabled by default
    restart_on_fail=True
)
```

**Usage:**
```bash
# Start orchestrator with ad monitoring enabled
cd watchers
python orchestrator.py

# Or enable ad monitoring by editing orchestrator.py
# Change: enabled=False → enabled=True
```

---

## 🚀 Quick Start Commands

### Option 1: Standalone Mode (Recommended for Testing)

```bash
# 1. Start the dashboard
cd ad_management
python dashboard.py
# Visit: http://localhost:8501

# 2. Run availability check (in separate terminal)
cd ad_management
python 2Check_Availability.py
```

### Option 2: Via Orchestrator (Production Mode)

```bash
# 1. Edit watchers/orchestrator.py
# Change enabled=False to enabled=True for:
#   - ad_monitor process
#   - dashboard process

# 2. Start orchestrator
cd watchers
python orchestrator.py

# 3. Check status
python orchestrator.py --status
```

### Option 3: Via Claude Code Skill (AI Assistant Mode)

Just ask Claude:
```
"Check product availability for https://www.gulahmedshop.com/products/elegant-summer-dress"
"Generate revenue impact report for last 7 days"
"Refresh the ad monitoring dashboard"
```

---

## 📋 Skill Triggers

The ad_monitoring skill responds to these triggers:

### User Prompts:
- "check product availability"
- "how much revenue did we lose"
- "show ad performance"
- "refresh dashboard"
- "generate revenue report"
- "ad monitoring status"

### Examples:
```
User: "Check if https://www.gulahmedshop.com/products/summer-dress is available"
Claude: Runs check_product_availability() and returns status

User: "How much revenue did we lose in the last 7 days?"
Claude: Runs get_revenue_impact(days=7) and returns report

User: "Refresh the dashboard"
Claude: Runs refresh_dashboard() and confirms status
```

---

## 🔧 Configuration

### Enable Ad Monitoring in Orchestrator

Edit `watchers/orchestrator.py`:

```python
# Find this section (lines 207-221)
self.processes['ad_monitor'] = Process(
    name='Ad Monitor',
    script='../ad_management/2Check_Allailability.py',
    enabled=False,  # CHANGE TO: enabled=True
    restart_on_fail=True
)
```

### Schedule Automated Monitoring

Use the scheduler-manager skill:

```bash
# Schedule ad monitoring every 15 minutes
python .claude/skills/scheduler-manager/scripts/schedule_task.py \
  --name "ad-monitoring-check" \
  --command "python ad_management/2Check_Availability.py" \
  --schedule "*/15 * * * *" \
  --enabled yes
```

---

## 📊 Dashboard Features

### Access Dashboard
```bash
cd ad_management
python dashboard.py
# Visit: http://localhost:8501
```

### Dashboard URL Parameters
```
http://localhost:8501?conversion_rate=0.7&theme=white
```

**Parameters:**
- `conversion_rate`: Daily conversion rate (0.0-1.0, default: 0.5)
- `theme`: Theme ("white" or "black", default: "black")
- `region": Region ("global", default: "global")

### Dashboard Sections

1. **KPI Cards** (Top)
   - Currently Offline
   - Total Downtime
   - Revenue Impact
   - Total Events

2. **Top Selling Products** (NEW!)
   - Top 10 products by revenue impact
   - Shows: Rank, Product, Price, Status, Downtime, Revenue Loss
   - Sorted by: Priority Score = (downtime × price)

3. **Charts**
   - Event Activity (line/bar chart)
   - Product Impact (pie chart)

4. **Daily Summary**
   - Date-wise breakdown
   - Stockouts, Restocks, Events

5. **Offline Ads Table** (ENHANCED!)
   - **NEW columns**: Product Price, Revenue Loss, Priority Score
   - Sorted by priority score

6. **Event History**
   - Full audit trail
   - Color-coded badges

---

## 🔗 Integration with Existing Skills

### With dashboard-updater Skill

The dashboard-updater skill can now include ad monitoring metrics:

```python
# When dashboard-updater refreshes, it will also show:
# - Top selling products
# - Revenue impact calculations
# - Ad performance metrics
```

### With approval-processor Skill

Ad monitoring can trigger approval workflows:

```python
# When high-value product goes out of stock
# Ad monitoring creates task in /Pending_Approval/ad/

# Approval processor reviews and decides:
# - Send alert email
# - Pause ad campaign
# - Notify team
```

### With email-sender Skill

Automated email notifications for stockouts:

```python
# In 2Check_Availability.py
# When product goes out of stock:
#   → Log event with Product_Price
#   → Trigger email-sender skill
#   → Send alert: "Product X ($Y) sold out - Revenue loss: $Z"
```

---

## 📁 File Structure

```
AI_Employee_Vault/
├── watchers/
│   ├── orchestrator.py                    # UPDATED: Added ad_monitor & dashboard
│   └── ...
├── ad_management/                           # NEW DIRECTORY
│   ├── 2Check_Availability.py          # Enhanced: Hidden size + price
│   ├── dashboard.py                       # Enhanced: Revenue metrics + Top Products
│   ├── logger.py                          # Enhanced: Product_Price field
│   ├── URLS.csv                            # NEW: 20 products
│   ├── scripts/
│   │   └── discover_products.py          # NEW: Product discovery
│   └── tests/
│       ├── test_size_detection.py        # NEW: Unit tests
│       └── test_performance.py           # NEW: Performance tests
├── .claude/skills/
│   ├── ad_monitoring/                       # NEW SKILL
│   │   ├── SKILL.md                        # Skill documentation
│   │   ├── ad_monitoring.py                # Skill wrapper for Claude Code
│   │   └── scripts/
│   │       ├── check_product.py
│   │       ├── revenue_report.py
│   │       └── refresh_dashboard.py
│   └── ... (existing skills)
└── CLAUDE.md                                    # UPDATED: Current work section
```

---

## 🧪 Testing

### Run Tests
```bash
cd ad_management

# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_size_detection.py -v
pytest tests/test_performance.py -v
```

### Manual Testing

1. **Test Dashboard:**
   ```bash
   python dashboard.py
   # Visit http://localhost:8501
   # Verify Top Selling Products section appears
   ```

2. **Test Availability Check:**
   ```bash
   python 2Check_Availability.py
   # Verify size detection works
   # Verify price scraping works
   # Check logs for Product_Price field
   ```

3. **Test Skill Integration:**
   ```bash
   # Via Claude Code
   "Check product availability for https://www.gulahmedshop.com/products/test"
   # Should return availability status
   ```

---

## 📈 Example Workflows

### Workflow 1: Daily Monitoring

1. **Orchestrator** starts `2Check_Availability.py` (every 15 minutes)
2. **Ad Monitor** scrapes products, detects stockouts
3. **Logger** records events with Product_Price
4. **Dashboard** updates with revenue impact
5. **Human** reviews dashboard, takes action

### Workflow 2: Revenue Analysis

1. **User asks**: "How much revenue did we lose last week?"
2. **Claude** calls `ad_monitoring` skill
3. **Skill** generates report via `get_revenue_impact(days=7)`
4. **Result**: $1,850.50 loss, 3 products offline

### Workflow 3: Product Check

1. **User asks**: "Is the summer dress still available?"
2. **Claude** calls `check_product_availability()`
3. **System**: Checks sizes, extracts price
4. **Result**: "XS and S sold out - PAUSE recommendation"

---

## 🔒 Security & Permissions

### Files NOT Synced to Git
```
.env, .env.*                     # Credentials
credentials/                         # API keys
sessions/                            # Browser sessions
ad_management/global/Ad_Status_Log.xlsx  # Local logs (if in global/)
```

### Orchestrator Permissions
- **ad_monitor**: Disabled by default (user must enable)
- **dashboard**: Disabled by default (user must enable)
- **Reason**: User controls when to run monitoring

### Data Privacy
- Product URLs: Safe to sync (public data)
- Ad names: Safe to sync (public info)
- Prices: Safe to sync (public info)
- **Credentials**: NEVER synced (always local)

---

## 🎓 Training & Documentation

### For Users
1. **Quick Start**: See IMPLEMENTATION_COMPLETE.md
2. **Skill Usage**: See .claude/skills/ad_monitoring/SKILL.md
3. **Dashboard**: Visit http://localhost:8501

### For Developers
1. **Implementation Plan**: `.claude/plans/ad-monitoring-enhancement.md`
2. **Test Suite**: `ad_management/tests/`
3. **Code Structure**: See inline comments

---

## 🆘 Troubleshooting

### Issue: Orchestrator can't find ad_monitor scripts
**Solution**: Ensure paths are correct:
```python
script='../ad_management/2Check_Availability.py'  # Relative path from watchers/
```

### Issue: Dashboard shows no data
**Solution**:
1. Run `2Check_Availability.py` first to generate logs
2. Verify `global/Ad_Status_Log.xlsx` exists
3. Check logs have `Product_Price` column

### Issue: Skill not found by Claude Code
**Solution**:
1. Verify file exists: `.claude/skills/ad_monitoring/ad_monitoring.py`
2. Check SKILL.md exists in same directory
3. Restart Claude Code application

### Issue: Price extraction returns 0
**Solution**:
1. Verify product page structure hasn't changed
2. Check CSS selectors: `.ProductMeta__Price span`
3. Test manually with browser inspector

---

## 📞 Support

### Getting Help
1. Check documentation: `ad_management/IMPLEMENTATION_COMPLETE.md`
2. Check skill docs: `.claude/skills/ad_monitoring/SKILL.md`
3. Review logs: `ad_management/global/Ad_Status_Log.xlsx`
4. Check orchestrator status: `python watchers/orchestrator.py --status`

### Common Issues
- **Playwright not installed**: `pip install playwright && playwright install chromium`
- **Missing dependencies**: `pip install -r requirements.txt`
- **Port 8501 in use**: Change port in `dashboard.py` or kill existing process

---

## 🎉 Summary

✅ **Orchestrator Integration**: Ad monitoring processes added
✅ **Skill Wrapper Created**: ad_monitoring.py for Claude Code
✅ **Existing Skills Compatible**: Works with dashboard-updater, approval-processor, etc.
✅ **Documentation Complete**: Integration guide, troubleshooting, usage examples
✅ **Test Suite Ready**: Unit tests + performance benchmarks
✅ **Production Ready**: Can be enabled in orchestrator by changing `enabled=False` to `enabled=True`

---

## 🚀 Next Steps

1. **Enable in Orchestrator**: Edit `watchers/orchestrator.py` to set `enabled=True`
2. **Test Integration**: Run orchestrator and verify ad_monitor starts
3. **Launch Dashboard**: Start dashboard server and verify Top Products section
4. **Schedule Monitoring**: Use scheduler-manager skill for 15-minute checks
5. **Monitor Performance**: Watch logs and dashboard for accuracy

---

**The Ad Monitoring system is now fully integrated with the AI Employee application!**
