# Google Calendar Watcher

**Intelligent calendar monitoring for the Personal AI Employee system**

Automatically monitors your Google Calendar for upcoming events and creates actionable task files in your Obsidian vault, giving your AI Employee time to prepare for meetings, appointments, and important events.

## Features

### Core Capabilities
- **Smart Event Detection**: Monitors events 1-48 hours ahead (configurable)
- **Multi-Calendar Support**: Track events across personal, work, and team calendars
- **Intelligent Priority**: Automatically assigns priority based on urgency and keywords
- **Rich Task Files**: Creates detailed markdown files with full event context
- **OAuth 2.0 Security**: Secure authentication with Google Calendar API
- **Duplicate Prevention**: Tracks processed events to avoid creating duplicate tasks
- **Auto-Refresh Tokens**: Credentials automatically refresh without re-authentication

### Event Information Captured
- Event title, description, and location
- Start/end times with duration calculation
- Attendee list with email addresses
- Time until event (for preparation planning)
- Calendar source (for multi-calendar setups)
- Direct link to event in Google Calendar
- Priority classification (urgent/high/medium/low)

### Integration Features
- **BaseWatcher Pattern**: Follows established watcher architecture
- **Structured Logging**: Daily logs with full activity tracking
- **JSON Action Logs**: Machine-readable event logs for analysis
- **PM2 Support**: Production-ready process management
- **Statistics Tracking**: Runtime stats and success metrics

## Quick Start

### 1. Install Dependencies

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### 2. Set Up Google Calendar API

Follow [CALENDAR_SETUP.md](./CALENDAR_SETUP.md) to:
1. Enable Google Calendar API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download and install credentials file

**Quick version:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Google Calendar API"
3. Create OAuth client ID (Desktop app)
4. Download as `calendar_credentials.json`
5. Place in `watchers/credentials/`

### 3. Run the Watcher

```bash
cd watchers
python calendar_watcher.py
```

First run will open browser for authentication - just sign in and approve!

### 4. Verify It Works

Create a test event 2-3 hours from now in Google Calendar, then:

```bash
# Check the logs
cat AI_Employee_Vault/Logs/calendarwatcher_*.log

# Check for task files
ls AI_Employee_Vault/Needs_Action/CALENDAR_*
```

## Usage

### Basic Commands

```bash
# Run with defaults (check every 5 min, look 1-48 hours ahead)
python calendar_watcher.py

# Custom check interval (10 minutes)
python calendar_watcher.py --interval 600

# Look further ahead (72 hours / 3 days)
python calendar_watcher.py --hours-ahead 72

# Notify earlier (3 hours minimum instead of 1)
python calendar_watcher.py --min-hours-ahead 3

# Monitor multiple calendars
python calendar_watcher.py --calendars primary work@company.com

# Custom vault path
python calendar_watcher.py --vault-path "/path/to/vault"

# Custom credentials file
python calendar_watcher.py --credentials "/path/to/creds.json"
```

### Multiple Calendars

To monitor work, personal, and team calendars:

```bash
# Get calendar IDs from Google Calendar settings
python calendar_watcher.py --calendars \
  primary \
  work@company.com \
  team@group.calendar.google.com
```

### Run as Service

**With PM2 (recommended):**

```bash
# Start calendar watcher
pm2 start ecosystem.config.js --only calendar-watcher

# View logs
pm2 logs calendar-watcher

# Stop/restart
pm2 stop calendar-watcher
pm2 restart calendar-watcher
```

**Manual background (Linux/Mac):**

```bash
nohup python calendar_watcher.py > calendar.out 2>&1 &
```

## Configuration

### Time Windows

Configure how far ahead to look for events:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--hours-ahead` | 48 | Maximum hours ahead to check |
| `--min-hours-ahead` | 1 | Minimum hours ahead to notify |
| `--interval` | 300 | Check interval in seconds |

**Examples:**

```bash
# Short notice (1-24 hours)
python calendar_watcher.py --hours-ahead 24

# Long notice (1-7 days)
python calendar_watcher.py --hours-ahead 168

# Immediate notice (30 min - 48 hours)
python calendar_watcher.py --min-hours-ahead 0.5

# Infrequent checks (every 15 minutes)
python calendar_watcher.py --interval 900
```

### Priority Detection

Events are automatically prioritized based on:

1. **Urgent**: Contains keywords (urgent, asap, critical, emergency, deadline)
2. **High**: Events within 3 hours OR contains meeting/client/interview keywords
3. **Medium**: Events within 24 hours OR general meeting keywords
4. **Low**: Events more than 24 hours away

Customize by editing `_determine_priority()` method in `calendar_watcher.py`.

### Environment Variables

Create `.env` file (copy from `.env.example`):

```bash
# Calendar watcher configuration
CALENDAR_CREDENTIALS_PATH=watchers/credentials/calendar_credentials.json
CALENDAR_CHECK_INTERVAL=300
CALENDAR_HOURS_AHEAD=48
CALENDAR_MIN_HOURS_AHEAD=1
CALENDAR_IDS=primary,work@company.com
```

## Output Format

### Task File Structure

When an event is detected, a markdown file is created:

**Filename:** `CALENDAR_{event_id}_{timestamp}_{event_summary}.md`

**Example:** `CALENDAR_abc123xyz_20260114_150530_Client_Strategy_Meeting.md`

**Content:**

```markdown
---
type: calendar_event
event_id: abc123xyz
calendar_id: primary
summary: Client Strategy Meeting
start_time: 2026-01-14T15:00:00
end_time: 2026-01-14T16:00:00
is_all_day: false
hours_until: 3
priority: high
status: pending
created: 2026-01-14T12:05:30
---

# Upcoming Event: Client Strategy Meeting

## Event Details
- **Event:** Client Strategy Meeting
- **Start:** 2026-01-14 15:00
- **End:** 2026-01-14 16:00
- **Duration:** 60 minutes
- **Location:** Conference Room B
- **Calendar:** primary
- **Time Until Event:** 3 hour(s)
- **Priority:** high

## Description
Quarterly strategy review with client leadership team.
Topics: Q1 results, Q2 planning, budget discussion.

## Attendees
- john.doe@client.com
- sarah.smith@client.com
- exec@client.com

## Preparation Actions
- [ ] Review event details and agenda
- [ ] Prepare necessary materials or documents
- [ ] Check location and travel time (if applicable)
- [ ] Review attendee list and context
- [ ] Set reminders if needed
- [ ] Confirm attendance if required

## Pre-Event Research
- [ ] Research attendees' backgrounds
- [ ] Review previous communications
- [ ] Prepare questions or talking points
- [ ] Gather relevant reports or data

## Notes
Add preparation notes and context here.

## Links
- [View in Google Calendar](https://calendar.google.com/...)
```

### Log Files

**Daily watcher log:** `AI_Employee_Vault/Logs/calendarwatcher_YYYY-MM-DD.log`

```
2026-01-14 12:05:30 - CalendarWatcher - INFO - CalendarWatcher initialized
2026-01-14 12:05:30 - CalendarWatcher - INFO -   Vault: C:\...\AI_Employee_Vault
2026-01-14 12:05:35 - CalendarWatcher - INFO - ✓ Google Calendar API authenticated
2026-01-14 12:10:30 - CalendarWatcher - INFO - Found 2 new upcoming event(s)
2026-01-14 12:10:31 - CalendarWatcher - INFO - ✓ Created task for event: Client Meeting (in 3h)
```

**Action log:** `AI_Employee_Vault/Logs/actions_YYYY-MM-DD.json`

```json
[
  {
    "timestamp": "2026-01-14T12:10:31",
    "watcher": "CalendarWatcher",
    "action": "calendar_event_detected",
    "details": {
      "event_id": "abc123xyz",
      "summary": "Client Strategy Meeting",
      "start_time": "2026-01-14T15:00:00",
      "hours_until": 3,
      "location": "Conference Room B",
      "attendees_count": 3,
      "priority": "high"
    },
    "task_file": "CALENDAR_abc123xyz_20260114_120531_Client_Strategy_Meeting.md"
  }
]
```

## Testing

### Run Test Suite

```bash
cd watchers
python test_calendar_watcher.py
```

**Tests include:**
1. Authentication
2. List available calendars
3. Check for upcoming events
4. Create task files
5. Time window configurations
6. Multiple calendar support
7. Priority detection logic

### Manual Testing

```bash
# 1. Create test event in Google Calendar
# 2. Run watcher manually
python calendar_watcher.py --interval 60 --hours-ahead 168

# 3. Wait 1 minute for check cycle
# 4. Verify task file created
ls -la AI_Employee_Vault/Needs_Action/CALENDAR_*

# 5. Review task file content
cat AI_Employee_Vault/Needs_Action/CALENDAR_*.md
```

## Architecture

### Class Hierarchy

```
BaseWatcher (abstract)
    ↓
CalendarWatcher
    ├── _authenticate()          # OAuth 2.0 flow
    ├── check_for_updates()      # Fetch upcoming events
    ├── create_action_file()     # Generate task files
    ├── _determine_priority()    # Priority classification
    ├── _parse_datetime()        # Time parsing
    └── _sanitize_filename()     # Safe filenames
```

### Data Flow

```
Google Calendar API
    ↓
CalendarWatcher.check_for_updates()
    ↓ (new events detected)
CalendarWatcher.create_action_file()
    ↓
Task file written to Needs_Action/
    ↓
BaseWatcher logs to action log
    ↓
Task Processor picks up file
    ↓
AI Employee processes event
```

### File Organization

```
watchers/
├── calendar_watcher.py          # Main watcher script
├── test_calendar_watcher.py     # Test suite
├── base_watcher.py              # Abstract base class
├── CALENDAR_SETUP.md            # Detailed setup guide
├── CALENDAR_QUICKSTART.md       # Quick start guide
├── CALENDAR_README.md           # This file
├── requirements.txt             # Python dependencies
├── ecosystem.config.js          # PM2 configuration
└── credentials/
    ├── calendar_credentials.json    # OAuth client secret
    └── calendar_token.pickle        # Saved auth token
```

## Troubleshooting

### "Credentials file not found"

**Solution:**
1. Verify file exists: `watchers/credentials/calendar_credentials.json`
2. Download from Google Cloud Console if missing
3. Ensure correct filename (exactly `calendar_credentials.json`)

### "OAuth 2.0 flow failed"

**Solution:**
1. Check you added yourself as test user in OAuth consent screen
2. Try different browser if popup is blocked
3. Verify Google Calendar API is enabled
4. Delete `calendar_token.pickle` and re-authenticate

### "No events found" but calendar has events

**Possible causes:**
- Events outside 1-48 hour window
- Wrong calendar being monitored
- Timezone differences

**Solution:**
```bash
# Look 7 days ahead
python calendar_watcher.py --hours-ahead 168

# Check specific calendar
python calendar_watcher.py --calendars your-calendar@gmail.com

# Start from now (0 hours minimum)
python calendar_watcher.py --min-hours-ahead 0
```

### Token expiration issues

**Solution:**
```bash
# Delete token and re-authenticate
rm watchers/credentials/calendar_token.pickle
python calendar_watcher.py
```

### Rate limiting

Google Calendar API limits:
- 1,000,000 queries/day
- 10,000 queries/100 seconds

**Solution:** Increase check interval if needed:
```bash
python calendar_watcher.py --interval 600  # 10 minutes
```

## Advanced Usage

### Custom Event Filtering

Edit `check_for_updates()` to filter events:

```python
# Only process events with specific attendees
if 'important@client.com' in [a.get('email') for a in event.get('attendees', [])]:
    upcoming_events.append(event)
```

### Custom Task Templates

Edit `create_action_file()` to customize output:

```python
# Add custom sections
task_content += """
## CRM Context
- [ ] Look up client in CRM
- [ ] Review previous interactions
- [ ] Check outstanding invoices
"""
```

### Integration with Other Tools

Parse task files programmatically:

```python
import yaml

# Read task file
with open('task_file.md', 'r') as f:
    content = f.read()

# Parse YAML frontmatter
frontmatter = yaml.safe_load(content.split('---')[1])

# Extract data
event_id = frontmatter['event_id']
priority = frontmatter['priority']
start_time = frontmatter['start_time']
```

## API Limits & Costs

### Google Calendar API

**Free tier includes:**
- 1,000,000 queries per day
- 10,000 queries per 100 seconds per user

**Watcher usage (5-min interval):**
- 12 queries per hour
- 288 queries per day
- **Well within free limits!**

**Cost:** FREE for normal usage

### Recommendations

- 5-minute interval: 288 queries/day (optimal)
- 10-minute interval: 144 queries/day (conservative)
- 1-minute interval: 1,440 queries/day (aggressive but still free)

## Security Best Practices

1. **Credentials:**
   - Keep `calendar_credentials.json` secure
   - Never commit to version control
   - Add to `.gitignore`

2. **Token storage:**
   - `calendar_token.pickle` contains access tokens
   - Also keep out of git
   - Delete if compromised

3. **OAuth scopes:**
   - Watcher uses read-only scopes
   - Cannot modify or delete events
   - Cannot access other Google services

4. **Revoke access:**
   - Visit [Google Account Permissions](https://myaccount.google.com/permissions)
   - Find "Personal AI Employee Calendar Watcher"
   - Click "Remove Access" if needed

## Performance

### Resource Usage

- **Memory:** ~50-100 MB typical, 200 MB limit
- **CPU:** Minimal (only during check cycles)
- **Disk:** ~1 KB per event task file
- **Network:** ~10 KB per API call

### Scalability

- Can monitor 10+ calendars simultaneously
- Handles hundreds of events per check
- Minimal impact on system resources

### Optimization Tips

1. **Adjust check interval** based on needs
2. **Filter calendars** to only monitor relevant ones
3. **Set appropriate time windows** to reduce noise
4. **Use PM2** for automatic restart and log rotation

## Integration with AI Employee

The Calendar Watcher is part of the complete AI Employee watcher system:

```
Calendar Watcher → Detects upcoming events
    ↓
Creates task files in Needs_Action/
    ↓
Task Processor → Analyzes event context
    ↓
AI Employee → Prepares for event
    ↓
Dashboard → Shows preparation status
    ↓
Approval Workflow → Review before action
```

**Complementary watchers:**
- **Gmail Watcher:** Related email communications
- **Filesystem Watcher:** Event-related documents
- **Slack Watcher:** Team discussions about events

## Contributing

To enhance the Calendar Watcher:

1. Follow BaseWatcher pattern
2. Add comprehensive logging
3. Include error handling
4. Update tests
5. Document changes

## Support & Documentation

- **Quick Start:** [CALENDAR_QUICKSTART.md](./CALENDAR_QUICKSTART.md)
- **Full Setup:** [CALENDAR_SETUP.md](./CALENDAR_SETUP.md)
- **Troubleshooting:** [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- **Base Class:** [base_watcher.py](./base_watcher.py)
- **Google API:** [Calendar API Reference](https://developers.google.com/calendar/api/v3/reference)

## License

Part of the Personal AI Employee Project

## Changelog

**v1.0.0** (2026-01-14)
- Initial release
- OAuth 2.0 authentication
- Multi-calendar support
- Priority detection
- PM2 integration
- Comprehensive testing
- Full documentation

---

**Status:** Production Ready ✓

**Tested on:**
- Windows 10/11
- Python 3.8+
- Google Calendar API v3

**Author:** Personal AI Employee Project

**Created:** 2026-01-14
