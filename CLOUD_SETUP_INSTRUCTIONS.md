# Platinum Tier Cloud Setup - Step-by-Step Guide

**Oracle Cloud VM Details:**
- **Instance:** instance-20260121-0102
- **Public IP:** 140.238.254.48
- **Region:** ap-mumbai-1
- **Shape:** VM.Standard.E2.1.Micro (1 OCPU, 1GB RAM)
- **Status:** RUNNING

---

## Quick Reference: Copy-Paste Commands

### Step 1: Access Your VM (Browser-Based SSH)

1. Go to: https://console.ap-mumbai-1.oraclecloud.com
2. Navigate to: **Compute** → **Instances**
3. Click: **instance-20260121-0102**
4. Click **Connect** → **Launch SSH Console**

### Step 2: Run Setup Script

**Copy and paste this entire block into the SSH console:**

```bash
# Download and run setup script
cd /home/ubuntu
curl -L https://raw.githubusercontent.com/MathNj/ai-employee-vault/master/scripts/cloud_setup.sh -o cloud_setup.sh
chmod +x cloud_setup.sh
./cloud_setup.sh
```

**Expected output:**
```
==========================================
Platinum Tier Cloud Zone Setup
==========================================
Started at: [timestamp]

[1/7] Updating system packages...
[2/7] Installing Python, Git, and other dependencies...
[3/7] Creating workspace directory...
[4/7] Cloning AI Employee Vault repository...
[5/7] Creating Python virtual environment...
[6/7] Installing minimal Python dependencies...
[7/7] Creating cloud environment configuration...

==========================================
Setup Complete!
==========================================
```

### Step 3: Create Gmail Read-Only Credentials

**IMPORTANT SECURITY:** You need to create Gmail API credentials with READ-ONLY scope.

#### Option A: Quick Method (Recommended)

On your **local machine**, create a file `gmail_readonly.json`:

```json
{
  "installed": {
    "client_id": "YOUR_CLIENT_ID.apps.googleusercontent.com",
    "client_secret": "YOUR_CLIENT_SECRET",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": ["http://localhost"],
    "scopes": [
      "https://www.googleapis.com/auth/gmail.readonly"
    ]
  }
}
```

Then generate OAuth tokens using Python:

```python
# run_oauth.py - Run this on your LOCAL machine
from google_auth_oauthlib.flow import InstalledAppFlow

flow = InstalledAppFlow.from_client_secrets_file(
    'gmail_readonly.json',
    scopes=['https://www.googleapis.com/auth/gmail.readonly']
)

creds = flow.run_local_server(port=0)

# Save the credentials
with open('gmail_token_readonly.json', 'w') as f:
    f.write(creds.to_json())

print("Credentials saved to gmail_token_readonly.json")
```

#### Option B: Manual Method

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download JSON credentials
4. Run the OAuth flow locally to get refresh token
5. Create final credentials file with token

**Upload to Cloud VM:**
- In the SSH console, click the **upload** icon
- Upload your `gmail_token_readonly.json` file
- Move it to the correct location:

```bash
mkdir -p /home/ubuntu/ai_employee/AI_Employee_Vault/credentials
mv ~/gmail_token_readonly.json /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json
chmod 600 /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json
```

### Step 4: Start Cloud Services

```bash
cd /home/ubuntu/ai_employee/AI_Employee_Vault
chmod +x scripts/start_cloud_services.sh cloud_sync.sh
./scripts/start_cloud_services.sh
```

**Expected output:**
```
Starting Cloud Services at [timestamp]
Starting Cloud Email Watcher...
Email watcher started (PID: XXXX)
Checking cron job for sync...
Cron job installed: Sync every 10 minutes

==========================================
Cloud Services Started Successfully!
==========================================
```

### Step 5: Verify Services Are Running

```bash
# Check if email watcher is running
ps aux | grep cloud_email_watcher

# Check recent logs
tail -f /home/ubuntu/ai_employee/email_watcher.log

# Check sync logs
tail -f /home/ubuntu/ai_employee/cloud_sync.log

# Verify cron job is installed
crontab -l
```

**Expected output:**
```
ubuntu    XXXX  0.0  2.5  50000 25000 ?        S    10:30   0:00 python3 /home/ubuntu/ai_employee/AI_Employee_Vault/watchers/cloud_email_watcher.py
*/10 * * * * /home/ubuntu/ai_employee/AI_Employee_Vault/cloud_sync.sh >> /home/ubuntu/ai_employee/cloud_sync.log 2>&1
```

---

## Testing the Workflow

### Test 1: Send a Test Email

1. **Send yourself an email** from another account
2. **Wait 10-15 minutes** (for the watcher to detect it)
3. **Check on your local machine:**

```bash
cd C:\Users\Najma-LP\Desktop\AI_Employee_Vault
git pull origin master
ls -la Needs_Action/email/
```

**Expected:** You should see a new file like `EMAIL_XXXXXXXX.md`

### Test 2: Review and Approve

1. **Open the email draft** in Obsidian
2. **Review the content**
3. **If you approve, move it:**

```bash
mv Needs_Action/email/EMAIL_XXXXXXXX.md Approved/email/
git add Approved/email/EMAIL_XXXXXXXX.md
git commit -m "Approve email send"
git push origin master
```

### Test 3: Verify Execution

1. **Wait 10 minutes** (for cloud to sync)
2. **Check on cloud VM:**

```bash
tail -f /home/ubuntu/ai_employee/email_watcher.log
```

**Expected:** Email should be sent (via local zone Gmail MCP)

---

## Troubleshooting

### Problem: Email watcher not running

**Solution:**
```bash
# Check logs
tail -50 /home/ubuntu/ai_employee/email_watcher.log

# Restart
killall python3
cd /home/ubuntu/ai_employee/AI_Employee_Vault
./scripts/start_cloud_services.sh
```

### Problem: Gmail authentication failed

**Solution:**
```bash
# Check credentials file exists
ls -la /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/

# Verify it's read-only scope
cat /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json | grep scopes
```

**Expected:** Should show `gmail.readonly` scope

### Problem: Git sync failing

**Solution:**
```bash
# Check sync logs
tail -50 /home/ubuntu/ai_employee/cloud_sync.log

# Manual sync test
cd /home/ubuntu/ai_employee/AI_Employee_Vault
git pull origin master
git push origin master
```

### Problem: Out of memory (1GB constraint)

**Solution:**
```bash
# Check memory usage
free -h

# Restart services to free memory
killall python3
./scripts/start_cloud_services.sh
```

---

## Monitoring Commands

### Check System Resources

```bash
# Memory usage (should stay under 1GB)
free -h

# Disk usage
df -h

# CPU usage
top -bn1 | head -20
```

### Check Service Status

```bash
# All running processes
ps aux | grep -E "(email_watcher|cloud_sync)"

# Recent email watcher logs
tail -f /home/ubuntu/ai_employee/email_watcher.log

# Recent sync logs
tail -f /home/ubuntu/ai_employee/cloud_sync.log

# Cron jobs
crontab -l
```

### Check Git Status

```bash
cd /home/ubuntu/ai_employee/AI_Employee_Vault

# Git status
git status

# Recent commits
git log --oneline -5

# Pull latest
git pull origin master

# Push changes
git push origin master
```

---

## Success Criteria

### ✅ Platinum Tier Complete When:

1. **Cloud VM is running:**
   - ✅ Email watcher process running
   - ✅ Cron job installed (sync every 10 min)
   - ✅ Logs show successful operation

2. **Git sync is working:**
   - ✅ Cloud pushes to GitHub
   - ✅ Local pulls from GitHub
   - ✅ No merge conflicts

3. **End-to-end workflow tested:**
   - ✅ Email arrives in cloud
   - ✅ Draft created in Needs_Action/email/
   - ✅ Draft synced to local via Git
   - ✅ Human approves → moves to Approved/
   - ✅ Approval synced to cloud via Git
   - ✅ Email sent from local zone
   - ✅ Task moved to Done/
   - ✅ Audit trail logged

---

## Next Steps After Setup

### 1. Monitor Performance

```bash
# Check memory stays under 1GB
watch -n 60 'free -h'

# Check logs for errors
tail -f /home/ubuntu/ai_employee/email_watcher.log | grep ERROR
```

### 2. Configure Alerts (Optional)

Create a simple alert script:

```bash
# Create alert script
cat > /home/ubuntu/alert.sh << 'EOF'
#!/bin/bash
if ! pgrep -f cloud_email_watcher > /dev/null; then
    echo "ALERT: Email watcher not running! Restarting..."
    cd /home/ubuntu/ai_employee/AI_Employee_Vault
    ./scripts/start_cloud_services.sh
fi
EOF

chmod +x /home/ubuntu/alert.sh

# Add to cron (check every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/ubuntu/alert.sh") | crontab -
```

### 3. Scale Up (If Needed)

If 1GB RAM is insufficient:
1. Stop instance
2. Change shape to VM.Standard.E2.2 (2 OCPU, 8GB RAM)
3. Start instance
4. Update check intervals

---

## Security Verification

### Verify Cloud Zone Is Read-Only

```bash
# Check credentials scope
cat /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json | grep scopes

# Should show ONLY:
# "https://www.googleapis.com/auth/gmail.readonly"
```

### Verify No Secrets Sync

```bash
# Check .gitignore on cloud
cat /home/ubuntu/ai_employee/AI_Employee_Vault/.gitignore | grep -E "(\.env|credentials|token)"

# Should show these are ignored
```

---

## Completion Checklist

- [ ] Cloud VM accessed via browser SSH
- [ ] Setup script executed successfully
- [ ] Gmail read-only credentials created and uploaded
- [ ] Cloud services started (email watcher + sync)
- [ ] Services verified running (ps aux)
- [ ] Logs show successful operation
- [ ] Cron job installed (crontab -l)
- [ ] Test email sent
- [ ] Draft detected in Needs_Action/email/
- [ ] Draft synced to local machine
- [ ] Approval workflow tested
- [ ] Email sent from local zone
- [ ] Task moved to Done/
- [ ] Audit trail verified
- [ ] Documentation updated

---

## Support

**For issues or questions:**
- Check logs in `/home/ubuntu/ai_employee/`
- Review Git history for changes
- Check local `Logs/` directory for audit trail
- Refer to `PLATINUM_TIER_DEPLOYMENT.md`

**Oracle Cloud Console:**
https://console.ap-mumbai-1.oraclecloud.com

**GitHub Repository:**
https://github.com/MathNj/ai-employee-vault
