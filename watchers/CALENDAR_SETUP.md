# Google Calendar API Setup Guide

This guide walks you through setting up Google Calendar API credentials for the Calendar Watcher.

## Overview

The Calendar Watcher monitors your Google Calendar for upcoming events and creates actionable task files in the AI Employee vault. It uses OAuth 2.0 authentication to securely access your calendar data.

## Prerequisites

- Google account with access to Google Calendar
- Python 3.8 or higher
- Internet connection for OAuth authentication

## Step 1: Enable Google Calendar API

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)

2. Create a new project (or select existing):
   - Click the project dropdown at the top
   - Click "New Project"
   - Name it "Personal AI Employee" or similar
   - Click "Create"

3. Enable the Google Calendar API:
   - In the left sidebar, go to "APIs & Services" > "Library"
   - Search for "Google Calendar API"
   - Click on it and click "Enable"

## Step 2: Create OAuth 2.0 Credentials

1. Configure OAuth consent screen:
   - Go to "APIs & Services" > "OAuth consent screen"
   - Choose "External" user type (unless you have Google Workspace)
   - Click "Create"
   - Fill in the required fields:
     - App name: "Personal AI Employee Calendar Watcher"
     - User support email: Your email
     - Developer contact: Your email
   - Click "Save and Continue"
   - Skip adding scopes (we'll add them in code)
   - Click "Save and Continue"
   - Add your email as a test user
   - Click "Save and Continue"

2. Create OAuth credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Desktop app" as the application type
   - Name it "Calendar Watcher Desktop Client"
   - Click "Create"

3. Download credentials:
   - Click the download button (⬇️) next to your newly created OAuth client
   - This downloads a JSON file named something like `client_secret_xxxxx.json`

## Step 3: Install Credentials

1. Rename the downloaded file to `calendar_credentials.json`

2. Move it to the watchers credentials folder:
   ```bash
   # Navigate to your vault
   cd "C:\Users\Najma-LP\Desktop\My Vault"

   # Create credentials folder if it doesn't exist
   mkdir -p watchers/credentials

   # Move the file (adjust source path as needed)
   mv ~/Downloads/calendar_credentials.json watchers/credentials/
   ```

3. Verify the file is in the correct location:
   ```bash
   ls watchers/credentials/calendar_credentials.json
   ```

## Step 4: Install Python Dependencies

Install the required Python packages:

```bash
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

Or if using a requirements file:

```bash
cd watchers
pip install -r requirements.txt
```

## Step 5: First Run Authentication

Run the calendar watcher for the first time:

```bash
cd watchers
python calendar_watcher.py
```

**Authentication Flow:**

1. Your default web browser will open automatically
2. You'll see a Google authentication page
3. Sign in with your Google account
4. You may see a warning "Google hasn't verified this app"
   - Click "Advanced"
   - Click "Go to Personal AI Employee Calendar Watcher (unsafe)"
5. Review the permissions requested:
   - See events from all calendars
   - See and download events from all calendars
6. Click "Allow"
7. Browser will show "The authentication flow has completed"
8. Return to your terminal - authentication is complete!

The watcher will save your credentials in `watchers/credentials/calendar_token.pickle` for future runs.

## Step 6: Verify It Works

After authentication, the watcher should:

1. Connect to Google Calendar successfully
2. Display: `✓ Google Calendar API authenticated successfully`
3. Start monitoring for upcoming events
4. Log activity to `AI_Employee_Vault/Logs/calendarwatcher_YYYY-MM-DD.log`

Check for upcoming events:
- The watcher looks 1-48 hours ahead by default
- Creates task files in `AI_Employee_Vault/Needs_Action/`
- Files are named `CALENDAR_{event_id}_{timestamp}_{event_name}.md`

## Configuration Options

You can customize the watcher behavior with command-line arguments:

```bash
# Custom check interval (5 minutes = 300 seconds)
python calendar_watcher.py --interval 300

# Look further ahead (72 hours)
python calendar_watcher.py --hours-ahead 72

# Notify earlier (3 hours minimum)
python calendar_watcher.py --min-hours-ahead 3

# Monitor specific calendars
python calendar_watcher.py --calendars primary work@example.com

# Custom vault path
python calendar_watcher.py --vault-path "/path/to/vault"

# Custom credentials file
python calendar_watcher.py --credentials "/path/to/creds.json"
```

## Multiple Calendar Support

To monitor multiple calendars:

1. Get your calendar IDs:
   - Go to [Google Calendar](https://calendar.google.com)
   - Click the three dots next to a calendar
   - Select "Settings and sharing"
   - Scroll to "Integrate calendar"
   - Copy the "Calendar ID" (looks like `email@example.com` or `randomstring@group.calendar.google.com`)

2. Run watcher with multiple calendars:
   ```bash
   python calendar_watcher.py --calendars primary work@company.com team@group.calendar.google.com
   ```

## Troubleshooting

### "Credentials file not found"

**Problem:** The watcher can't find `calendar_credentials.json`

**Solution:**
1. Verify file location: `watchers/credentials/calendar_credentials.json`
2. Check filename is exactly `calendar_credentials.json`
3. Use `--credentials` flag to specify custom path

### "OAuth 2.0 flow failed"

**Problem:** Browser authentication didn't complete

**Solution:**
1. Ensure your browser isn't blocking popups
2. Try again - sometimes it fails on first attempt
3. Check you're signing in with the correct Google account
4. Verify you added yourself as a test user in OAuth consent screen

### "Calendar service not initialized"

**Problem:** Authentication succeeded but service creation failed

**Solution:**
1. Delete `watchers/credentials/calendar_token.pickle`
2. Run the watcher again to re-authenticate
3. Verify Google Calendar API is enabled in Cloud Console

### "No events found" but you have events

**Problem:** Watcher isn't detecting your events

**Solution:**
1. Check the time window settings:
   - Default is 1-48 hours ahead
   - Events outside this window won't be detected
2. Verify calendar ID:
   - Default is `primary` (your main calendar)
   - Use `--calendars` to specify other calendars
3. Check event times:
   - Watcher uses UTC internally
   - Timezone conversions may affect timing

### "Token expired" or "Invalid credentials"

**Problem:** Saved credentials are no longer valid

**Solution:**
1. Delete the token file:
   ```bash
   rm watchers/credentials/calendar_token.pickle
   ```
2. Run the watcher again to re-authenticate

### Rate Limiting

**Problem:** Getting "Quota exceeded" or "Rate limit" errors

**Solution:**
1. Increase check interval:
   ```bash
   python calendar_watcher.py --interval 600  # 10 minutes
   ```
2. Google Calendar API quotas:
   - 1,000,000 queries per day (very generous)
   - Unlikely to hit with reasonable check intervals

## Security Best Practices

1. **Keep credentials secure:**
   - Never commit `calendar_credentials.json` to git
   - Add to `.gitignore`
   - Don't share your credentials file

2. **Token storage:**
   - `calendar_token.pickle` contains access tokens
   - Also keep this out of version control
   - Delete if you suspect compromise

3. **OAuth scopes:**
   - Watcher only requests read-only access
   - Cannot modify or delete events
   - Cannot access other Google services

4. **Revoke access:**
   - If needed, revoke access at [Google Account Security](https://myaccount.google.com/permissions)
   - Look for "Personal AI Employee Calendar Watcher"
   - Click "Remove Access"

## Running as a Service

### Using PM2 (Recommended)

Add to your PM2 ecosystem configuration:

```javascript
module.exports = {
  apps: [
    {
      name: 'calendar-watcher',
      script: 'calendar_watcher.py',
      interpreter: 'python3',
      cwd: './watchers',
      args: '--interval 300 --hours-ahead 48',
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1'
      }
    }
  ]
}
```

Start with PM2:
```bash
pm2 start ecosystem.config.js --only calendar-watcher
pm2 save
```

### Using systemd (Linux)

Create `/etc/systemd/system/calendar-watcher.service`:

```ini
[Unit]
Description=Google Calendar Watcher for AI Employee
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/vault/watchers
ExecStart=/usr/bin/python3 calendar_watcher.py --interval 300
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable calendar-watcher
sudo systemctl start calendar-watcher
sudo systemctl status calendar-watcher
```

## Testing

Test the watcher without waiting for real events:

```bash
# Run in test mode (manual testing)
cd watchers
python calendar_watcher.py --interval 60 --hours-ahead 168  # Check 7 days ahead
```

Create a test event:
1. Go to Google Calendar
2. Create an event 2-3 hours from now
3. Wait for the next check cycle
4. Verify task file appears in `AI_Employee_Vault/Needs_Action/`

## Next Steps

1. **Integrate with other watchers:** Run multiple watchers simultaneously with PM2
2. **Customize priorities:** Modify `_determine_priority()` method for your needs
3. **Add custom calendars:** Monitor work, personal, team calendars separately
4. **Adjust timing:** Change `hours_ahead` and `min_hours_ahead` to suit your workflow

## API Limits

Google Calendar API has generous limits:
- **Queries per day:** 1,000,000
- **Queries per 100 seconds:** 10,000
- **Queries per user per 100 seconds:** 5,000

With a 5-minute check interval, you'll use:
- 12 queries per hour
- 288 queries per day

Well within limits!

## Support

For issues:
1. Check logs in `AI_Employee_Vault/Logs/`
2. Review this troubleshooting guide
3. Verify Google Calendar API is enabled
4. Ensure credentials are correctly placed
5. Try re-authenticating by deleting token file

## References

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/v3/reference)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Python Client Library](https://github.com/googleapis/google-api-python-client)
