# Platinum Tier Cloud Deployment Guide

## Quick Start: Oracle Cloud VM Setup

Since we cannot update SSH keys on an existing instance, use the **Oracle Cloud Console** for browser-based SSH access.

### Step 1: Access Your Instance

1. Go to: https://console.ap-mumbai-1.oraclecloud.com
2. Navigate to: **Compute** → **Instances**
3. Find your instance: `instance-20260121-0102`
4. Click the instance name
5. Click **Connect** → **Launch SSH Console** (browser-based terminal)

### Step 2: Download and Run Setup Script

In the browser-based SSH console, run:

```bash
# Download the setup script
cd /home/ubuntu
curl -O https://raw.githubusercontent.com/MathNj/ai-employee-vault/master/scripts/cloud_setup.sh

# Make it executable
chmod +x cloud_setup.sh

# Run the setup
./cloud_setup.sh
```

### Step 3: Create Gmail Read-Only Credentials

**IMPORTANT**: You need Gmail API credentials with **READ-ONLY** scope for security.

On your local machine:

1. Go to: https://console.cloud.google.com/apis/credentials
2. Create OAuth 2.0 Client ID (Desktop app)
3. Download JSON credentials
4. Rename to: `gmail_readonly.json`
5. **IMPORTANT**: Edit the JSON and set `scopes` to read-only only:
   ```json
   "scopes": [
     "https://www.googleapis.com/auth/gmail.readonly"
   ]
   ```

Then upload to the VM (use the upload button in SSH console):

```bash
mkdir -p /home/ubuntu/ai_employee/AI_Employee_Vault/credentials
# Upload gmail_readonly.json here via the upload button
```

### Step 4: Start Cloud Services

```bash
cd /home/ubuntu/ai_employee/AI_Employee_Vault
chmod +x scripts/start_cloud_services.sh
chmod +x cloud_sync.sh
./scripts/start_cloud_services.sh
```

### Step 5: Verify Services Are Running

```bash
# Check email watcher is running
ps aux | grep cloud_email_watcher

# Check recent logs
tail -f /home/ubuntu/ai_employee/email_watcher.log

# Check sync logs
tail -f /home/ubuntu/ai_employee/cloud_sync.log
```

## What This Does

### Cloud Zone (Oracle VM - 1GB RAM)

**Runs:**
- ✅ Gmail watcher (read-only, creates draft tasks)
- ✅ Git sync every 10 minutes
- ✅ Creates task files in `Needs_Action/email/`

**Never Does:**
- ❌ Send emails
- ❌ Post to social media
- ❌ Process payments
- ❌ Access WhatsApp sessions

### Local Zone (Your Machine)

**Runs:**
- ✅ Reviews draft tasks from cloud
- ✅ Human approval via `/Approved/` directory
- ✅ Final email sending via Gmail MCP
- ✅ Social media posting
- ✅ Payment processing
- ✅ All credential storage

## How It Works

```
Cloud Zone                          Local Zone
(Oracle VM)                        (Your Machine)
    |                                     |
    | 1. Detects new email                |
    | 2. Creates draft in                 |
    |    Needs_Action/email/              |
    |                                     |
    |-------- Git Sync ------->           |
    |                                     | 3. You review draft
    |                                     | 4. Approve → Approved/
    |                                     |
    |<------ Git Sync -------            |
    |                                     |
    | 5. Executed by local zone           |
    |    (via Gmail MCP)                  |
    |                                     |
```

## Monitoring

### Cloud VM Status

```bash
# Check system resources (should stay under 1GB RAM)
free -h
df -h

# Check if services are running
ps aux | grep -E "(email_watcher|cloud_sync)"

# View logs
tail -f /home/ubuntu/ai_employee/email_watcher.log
```

### Local Machine Status

```bash
# Check for new tasks from cloud
ls -la Needs_Action/email/

# Review and approve
# Move draft to Approved/ to trigger action
mv Needs_Action/email/EMAIL_123.md Approved/email/

# Push approval to Git
git add Approved/email/EMAIL_123.md
git commit -m "Approve email send"
git push origin master
```

## Troubleshooting

### Cloud VM Issues

**Problem**: Email watcher not running
```bash
# Check logs
tail -50 /home/ubuntu/ai_employee/email_watcher.log

# Restart
killall python3
cd /home/ubuntu/ai_employee/AI_Employee_Vault
./scripts/start_cloud_services.sh
```

**Problem**: Git sync failing
```bash
# Check sync logs
tail -50 /home/ubuntu/ai_employee/cloud_sync.log

# Manual sync test
cd /home/ubuntu/ai_employee/AI_Employee_Vault
git pull origin master
git push origin master
```

**Problem**: Out of memory (1GB constraint)
```bash
# Check memory usage
free -h

# Restart services to free memory
killall python3
./scripts/start_cloud_services.sh
```

### Credentials Issues

**Problem**: Gmail authentication failed
```bash
# Check credentials file exists
ls -la /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/

# Verify it's read-only scope
cat /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json | grep scopes
```

## Next Steps After Setup

1. **Test the workflow**:
   - Send yourself a test email
   - Wait 10-15 minutes
   - Check `Needs_Action/email/` for draft task

2. **Set up local approval workflow**:
   - Review drafts in Obsidian
   - Move to `Approved/` to execute
   - Move to `Rejected/` to ignore

3. **Monitor performance**:
   - Check VM memory usage stays under 1GB
   - Adjust sync interval if needed (edit crontab)

4. **Scale up** (if needed):
   - Upgrade VM shape for more watchers
   - Add calendar monitoring
   - Add Odoo alerts

## Security Notes

- ✅ Cloud VM only has **READ-ONLY** Gmail credentials
- ✅ All write credentials stay on local machine
- ✅ No secrets synced to Git
- ✅ Human approval required for all actions
- ✅ Complete audit trail in `Logs/`

## Support

For issues or questions:
- Check logs in `/home/ubuntu/ai_employee/`
- Review Git history for changes
- Check local `Logs/` directory for audit trail
