# Gmail Watcher Setup Guide

Complete guide to setting up Gmail API credentials for the Gmail watcher.

## Prerequisites

- Google account with Gmail
- Python 3.13+
- Internet connection

## Step 1: Enable Gmail API

### 1.1 Go to Google Cloud Console

1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account

### 1.2 Create a New Project

1. Click the project dropdown at the top
2. Click **"New Project"**
3. Enter project name: `AI-Employee` (or your preferred name)
4. Click **"Create"**
5. Wait for the project to be created and select it

### 1.3 Enable Gmail API

1. In the left sidebar, go to **"APIs & Services"** → **"Library"**
2. Search for **"Gmail API"**
3. Click on **"Gmail API"**
4. Click **"Enable"**
5. Wait for the API to be enabled

## Step 2: Create OAuth2 Credentials

### 2.1 Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type (unless you have a Google Workspace)
3. Click **"Create"**
4. Fill in required fields:
   - **App name:** `Personal AI Employee`
   - **User support email:** Your email
   - **Developer contact:** Your email
5. Click **"Save and Continue"**
6. On "Scopes" page, click **"Save and Continue"** (we'll add scopes via code)
7. On "Test users" page:
   - Click **"Add Users"**
   - Add your Gmail address
   - Click **"Save and Continue"**
8. Review and click **"Back to Dashboard"**

### 2.2 Create Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"Create Credentials"** → **"OAuth client ID"**
3. Select **"Desktop app"** as application type
4. Name: `Gmail Watcher`
5. Click **"Create"**
6. Click **"Download JSON"** on the popup
7. Save the file (it will be named something like `client_secret_xxxxx.json`)

## Step 3: Set Up Credentials in Vault

### 3.1 Create Credentials Directory

```bash
mkdir -p watchers/credentials
```

### 3.2 Copy Credentials File

Rename and move the downloaded JSON file:

**Windows:**
```bash
move Downloads\client_secret_*.json watchers\credentials\credentials.json
```

**Linux/Mac:**
```bash
mv ~/Downloads/client_secret_*.json watchers/credentials/credentials.json
```

### 3.3 Verify File Location

```bash
ls watchers/credentials/
```

You should see: `credentials.json`

## Step 4: Install Dependencies

Install the required Google API libraries:

```bash
pip install -r watchers/requirements.txt
```

Or install individually:
```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

## Step 5: First Run (Authentication)

### 5.1 Start the Gmail Watcher

```bash
python watchers/gmail_watcher.py
```

### 5.2 Complete OAuth Flow

1. A browser window will open automatically
2. Sign in with your Google account (the one you added as test user)
3. You'll see a warning: **"Google hasn't verified this app"**
   - Click **"Advanced"**
   - Click **"Go to Personal AI Employee (unsafe)"**
4. Grant permissions:
   - Click **"Allow"** to grant read-only Gmail access
5. You should see: **"The authentication flow has completed"**
6. Close the browser tab and return to terminal

### 5.3 Verify Authentication

The terminal should show:
```
✓ Gmail API authenticated successfully
Gmail Watcher started
Monitoring for: unread important emails
```

**Success!** The watcher is now running and monitoring your Gmail.

## Step 6: Test the Watcher

### 6.1 Send Test Email

1. From another email account (or the same account), send yourself an email
2. **Important:** Mark the email as "Important" in Gmail (star or use priority inbox)
3. Keep it unread

### 6.2 Wait for Detection

The watcher checks every 2 minutes. You should see:
```
Found 1 new important email(s)
✓ Created task for email from: sender@example.com
```

### 6.3 Check Created Task

```bash
ls Needs_Action/
cat Needs_Action/EMAIL_*.md
```

You should see a task file with:
- Email subject and sender
- Preview of email content
- Suggested actions
- Link to Gmail

## Credentials Files Created

After setup, you'll have:

```
watchers/credentials/
├── credentials.json    # OAuth client credentials (from Google)
└── token.pickle        # Authenticated session token (auto-created)
```

**Important:**
- ✅ `credentials.json` - Keep private, don't commit to Git
- ✅ `token.pickle` - Keep private, don't commit to Git
- ✅ Both files are in `.gitignore` (if using Git)

## Configuration

### Change Check Interval

Edit `gmail_watcher.py`:
```python
CHECK_INTERVAL = 120  # Change to desired seconds
```

- 60 = 1 minute
- 120 = 2 minutes (default)
- 300 = 5 minutes

### Change Email Query

Edit `gmail_watcher.py` in the `check_for_updates()` method:
```python
# Current: unread + important
q='is:unread is:important'

# All unread emails:
q='is:unread'

# Unread from specific sender:
q='is:unread from:client@example.com'

# Unread with subject keyword:
q='is:unread subject:invoice'
```

See [Gmail search operators](https://support.google.com/mail/answer/7190) for more options.

## Troubleshooting

### "Credentials file not found"

**Solution:** Ensure `credentials.json` is in `watchers/credentials/`

```bash
ls watchers/credentials/credentials.json
```

### "OAuth2 flow failed"

**Possible causes:**
1. Browser didn't open - Check firewall settings
2. Wrong credentials - Re-download from Google Cloud Console
3. API not enabled - Enable Gmail API in Cloud Console

### "Access blocked: App not verified"

**Solution:** Add your email as a test user:
1. Go to Google Cloud Console
2. OAuth consent screen → Test users
3. Add your Gmail address

### "Token expired" Error

**Solution:** Delete token and re-authenticate:
```bash
rm watchers/credentials/token.pickle
python watchers/gmail_watcher.py
```

### No Emails Detected

**Checklist:**
- [ ] Email is marked as "Important" in Gmail
- [ ] Email is unread
- [ ] Watcher has been running for at least 2 minutes
- [ ] Check watcher logs: `cat Logs/gmail_watcher_*.log`

## Security Best Practices

### 1. Protect Credentials

**Never commit these files to Git:**
- `credentials.json`
- `token.pickle`

Add to `.gitignore`:
```
watchers/credentials/*.json
watchers/credentials/*.pickle
```

### 2. Limited Permissions

The watcher only requests **read-only** access to Gmail:
- Can read emails
- Cannot send emails
- Cannot delete emails
- Cannot modify emails

### 3. Revoke Access

To revoke Gmail API access:
1. Go to [Google Account Security](https://myaccount.google.com/permissions)
2. Find "Personal AI Employee"
3. Click "Remove Access"

## Running in Background

### Windows

```bash
start pythonw watchers\gmail_watcher.py
```

### Linux/Mac

```bash
nohup python watchers/gmail_watcher.py &
```

### Using Process Manager (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start Gmail watcher
pm2 start watchers/gmail_watcher.py --interpreter python3 --name gmail-watcher

# View logs
pm2 logs gmail-watcher

# Stop
pm2 stop gmail-watcher
```

## Integration with Other Components

The Gmail watcher integrates with:
- **task-processor:** Processes created email tasks
- **dashboard-updater:** Shows email detection in dashboard
- **Logs:** Records all detected emails

## Usage Patterns

### Monitor All Important Emails
```python
# Default configuration - already set
q='is:unread is:important'
```

### Monitor Specific Clients
```python
# Only emails from specific domain
q='is:unread from:@clientdomain.com'
```

### Monitor by Subject
```python
# Invoices and payments
q='is:unread (subject:invoice OR subject:payment)'
```

## Next Steps

After setup:
1. ✅ Gmail watcher running and detecting emails
2. ⏳ Process email tasks with task-processor
3. ⏳ Set up approval workflow for email responses
4. ⏳ Add Gmail MCP server for sending replies (Silver tier)

---

**🎉 Congratulations!**

Your Gmail watcher is now monitoring your inbox and creating tasks automatically!

*Part of Personal AI Employee*
*Gmail API Integration*
