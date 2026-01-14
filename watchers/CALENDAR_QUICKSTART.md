# Google Calendar Watcher - Quick Start Guide

Get the Calendar Watcher running in 5 minutes!

## What It Does

The Calendar Watcher monitors your Google Calendar and automatically creates task files for upcoming events. This gives your AI Employee time to prepare for meetings, interviews, and important appointments.

**Key Features:**
- Monitors events 1-48 hours ahead (configurable)
- Creates detailed task files with event info
- Tracks attendees, location, description
- Prioritizes based on urgency and keywords
- Supports multiple calendars
- OAuth 2.0 secure authentication

## Quick Setup (5 Minutes)

### Step 1: Install Dependencies (1 minute)

```bash
cd watchers
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### Step 2: Get Google Calendar API Credentials (3 minutes)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable "Google Calendar API"
4. Create OAuth 2.0 credentials:
   - OAuth consent screen → External → Fill basic info
   - Credentials → Create OAuth client ID → Desktop app
5. Download the JSON file
6. Rename it to `calendar_credentials.json`
7. Place it in `watchers/credentials/`

**Detailed instructions:** See [CALENDAR_SETUP.md](./CALENDAR_SETUP.md)

### Step 3: Run the Watcher (1 minute)

```bash
cd watchers
python calendar_watcher.py
```

**First run:**
- Browser opens automatically
- Sign in with Google
- Click "Allow" for calendar access
- Done! Credentials saved for future runs

## Verify It Works

1. **Check the logs:**
   ```bash
   tail -f AI_Employee_Vault/Logs/calendarwatcher_*.log
   ```

   You should see:
   ```
   ✓ Google Calendar API authenticated successfully
   CalendarWatcher started
   ```

2. **Create a test event:**
   - Go to [Google Calendar](https://calendar.google.com)
   - Create an event 2-3 hours from now
   - Wait 5 minutes (default check interval)
   - Check `AI_Employee_Vault/Needs_Action/`
   - You should see a new `CALENDAR_*.md` file!

3. **View the task file:**
   ```bash
   ls AI_Employee_Vault/Needs_Action/CALENDAR_*
   cat AI_Employee_Vault/Needs_Action/CALENDAR_*.md
   ```

## Example Output

When the watcher detects an upcoming event, it creates a file like this:

```markdown
---
type: calendar_event
event_id: abc123xyz
summary: Client Strategy Meeting
start_time: 2026-01-14T15:00:00
priority: high
---

# Upcoming Event: Client Strategy Meeting

## Event Details
- **Event:** Client Strategy Meeting
- **Start:** 2026-01-14 15:00
- **End:** 2026-01-14 16:00
- **Duration:** 60 minutes
- **Location:** Conference Room B
- **Time Until Event:** 3 hour(s)
- **Priority:** high

## Attendees
- john@company.com
- sarah@company.com

## Preparation Actions
- [ ] Review event details and agenda
- [ ] Prepare necessary materials
- [ ] Check location and travel time
- [ ] Review attendee backgrounds
```

## Configuration Options

### Basic Usage

```bash
# Default: Check every 5 minutes, look 1-48 hours ahead
python calendar_watcher.py

# Custom check interval (every 10 minutes)
python calendar_watcher.py --interval 600

# Look further ahead (72 hours)
python calendar_watcher.py --hours-ahead 72

# Get notified earlier (3 hours minimum)
python calendar_watcher.py --min-hours-ahead 3
```

### Multiple Calendars

```bash
# Monitor work calendar too
python calendar_watcher.py --calendars primary work@company.com

# Monitor team calendars
python calendar_watcher.py --calendars primary team@group.calendar.google.com
```

**Get your calendar IDs:**
1. Go to Google Calendar
2. Click ⋮ next to a calendar → Settings
3. Scroll to "Integrate calendar"
4. Copy the "Calendar ID"

### Custom Vault Path

```bash
python calendar_watcher.py --vault-path "/path/to/your/vault"
```

## Run as Background Service

### Option 1: PM2 (Recommended)

Add to `ecosystem.config.js`:

```javascript
{
  name: 'calendar-watcher',
  script: 'calendar_watcher.py',
  interpreter: 'python3',
  cwd: './watchers',
  args: '--interval 300',
  autorestart: true
}
```

Start it:
```bash
pm2 start ecosystem.config.js --only calendar-watcher
pm2 save
pm2 logs calendar-watcher
```

### Option 2: Run in Background (Linux/Mac)

```bash
nohup python calendar_watcher.py > calendar_watcher.out 2>&1 &
```

Stop it:
```bash
pkill -f calendar_watcher.py
```

### Option 3: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task → "Calendar Watcher"
3. Trigger: At system startup
4. Action: Start a program
   - Program: `python`
   - Arguments: `C:\path\to\watchers\calendar_watcher.py`
5. Save and run

## Testing

Run the comprehensive test suite:

```bash
cd watchers
python test_calendar_watcher.py
```

Tests include:
- ✓ Authentication
- ✓ List calendars
- ✓ Check upcoming events
- ✓ Create task files
- ✓ Time window configurations
- ✓ Multiple calendar support
- ✓ Priority detection

## Common Issues & Solutions

### "Credentials file not found"

**Fix:**
```bash
# Check file exists
ls watchers/credentials/calendar_credentials.json

# If missing, download from Google Cloud Console
# Rename to calendar_credentials.json
# Place in watchers/credentials/
```

### "OAuth 2.0 flow failed"

**Fix:**
1. Delete old token: `rm watchers/credentials/calendar_token.pickle`
2. Run again: `python calendar_watcher.py`
3. Complete authentication in browser

### "No events found" but you have events

**Possible causes:**
- Events are outside 1-48 hour window
- Monitoring wrong calendar (not 'primary')
- Event times in different timezone

**Fix:**
```bash
# Look 7 days ahead instead
python calendar_watcher.py --hours-ahead 168

# Monitor specific calendar
python calendar_watcher.py --calendars your-calendar-id@gmail.com
```

### Authentication keeps expiring

**Fix:** This shouldn't happen - tokens auto-refresh. If it does:
1. Delete token file
2. Re-authenticate
3. Check OAuth consent screen is configured correctly

## Integration with AI Employee

The Calendar Watcher is part of the Personal AI Employee watcher system:

```
Calendar Watcher
    ↓
Creates task files in Needs_Action/
    ↓
Task Processor picks them up
    ↓
AI analyzes and takes action
    ↓
Updates Dashboard
```

**Next steps:**
1. Set up other watchers (Gmail, WhatsApp, Filesystem)
2. Configure Task Processor to handle calendar events
3. Set up Dashboard updates
4. Integrate with approval workflow

## Tips & Best Practices

1. **Set appropriate time windows:**
   - Too short (1-6h): Not enough prep time
   - Too long (7+ days): Creates noise
   - Recommended: 1-48 hours for most use cases

2. **Use multiple calendars wisely:**
   - Separate work and personal
   - Monitor team calendars for important meetings
   - Filter by calendar in task processor

3. **Customize priorities:**
   - Edit `_determine_priority()` method
   - Add company-specific keywords
   - Adjust timing thresholds

4. **Monitor the logs:**
   - Check `AI_Employee_Vault/Logs/calendarwatcher_*.log`
   - Look for errors or missed events
   - Adjust settings based on patterns

5. **Rate limiting:**
   - Default 5-minute interval is safe
   - Google allows 1M queries/day
   - 288 queries/day at 5-minute intervals

## Advanced Usage

### Custom Event Filtering

Modify `check_for_updates()` to filter events:

```python
# Only monitor events with "Client" in title
if 'Client' in event.get('summary', ''):
    upcoming_events.append(event)
```

### Custom Task Templates

Modify `create_action_file()` to customize task format:

```python
# Add custom preparation checklist
task_content += """
## Custom Prep
- [ ] Review CRM notes
- [ ] Check previous invoices
- [ ] Prepare proposal draft
"""
```

### Integration with Other Systems

The watcher outputs structured markdown with YAML frontmatter - easy to parse:

```python
import yaml

with open('task_file.md', 'r') as f:
    content = f.read()
    frontmatter = yaml.safe_load(content.split('---')[1])
    event_id = frontmatter['event_id']
    priority = frontmatter['priority']
```

## Support & Resources

- **Full setup guide:** [CALENDAR_SETUP.md](./CALENDAR_SETUP.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **API docs:** [Google Calendar API](https://developers.google.com/calendar/api/v3/reference)
- **Base watcher class:** [base_watcher.py](./base_watcher.py)

## What's Next?

1. **Run all watchers together:** See [RUN_ALL_WATCHERS.md](./RUN_ALL_WATCHERS.md)
2. **Set up Gmail watcher:** Get notified about important emails
3. **Set up WhatsApp watcher:** Monitor business messages
4. **Configure Task Processor:** Automatically handle detected tasks
5. **Dashboard integration:** See all activities in one place

---

**Quick command reference:**

```bash
# Start watcher
python calendar_watcher.py

# Test watcher
python test_calendar_watcher.py

# Run in background with PM2
pm2 start ecosystem.config.js --only calendar-watcher

# View logs
tail -f AI_Employee_Vault/Logs/calendarwatcher_*.log

# Check for task files
ls AI_Employee_Vault/Needs_Action/CALENDAR_*
```

Happy monitoring! Your AI Employee is now aware of your calendar. 📅
