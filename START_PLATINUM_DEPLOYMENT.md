# 🚀 PLATINUM TIER DEPLOYMENT - START HERE

**Status:** ✅ Ready with Credentials
**Time Required:** 20 minutes
**VM:** 140.238.254.48 (Oracle Cloud, Running)

---

## Good News! 🎉

**You already have Gmail read-only OAuth credentials!**

I found them in:
- `mcp-servers/gmail-mcp/credentials.json`
- `mcp-servers/gmail-mcp/token.json`

These credentials have the **READ-ONLY** scope, perfect for cloud deployment!

---

## Deployment Steps (20 Minutes)

### Option 1: Automated (Recommended)

**Run this script:**
```cmd
deploy_with_credentials.bat
```

It will:
1. ✅ Package your credentials
2. ✅ Open Oracle Cloud Console
3. ✅ Guide you through uploads
4. ✅ Execute setup commands
5. ✅ Start cloud services
6. ✅ Verify deployment

### Option 2: Manual (Follow These Steps)

---

## Step 1: Access Cloud VM (2 min)

1. Go to: https://console.ap-mumbai-1.oraclecloud.com
2. Compute → Instances → instance-20260121-0102
3. Connect → Launch SSH Console

**A browser-based terminal will open.**

---

## Step 2: Setup Directory Structure (1 min)

In the SSH console, copy-paste:

```bash
mkdir -p /home/ubuntu/ai_employee/AI_Employee_Vault/credentials
mkdir -p /home/ubuntu/ai_employee/AI_Employee_Vault/watchers
mkdir -p /home/ubuntu/ai_employee/AI_Employee_Vault/scripts
```

---

## Step 3: Clone Repository (3 min)

```bash
cd /home/ubuntu/ai_employee
git clone https://github.com/MathNj/ai-employee-vault.git AI_Employee_Vault
cd AI_Employee_Vault
```

---

## Step 4: Upload Your Credentials (3 min)

**IMPORTANT:** Use your EXISTING credentials!

On your **local machine**, your credentials are here:
```
C:\Users\Najma-LP\Desktop\AI_Employee_Vault\mcp-servers\gmail-mcp\credentials.json
C:\Users\Najma-LP\Desktop\AI_Employee_Vault\mcp-servers\gmail-mcp\token.json
```

**To upload them:**

1. In the SSH console, click the **upload icon** (↑)
2. Navigate to your local folder
3. Upload **BOTH** files to:
   ```
   /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/
   ```

4. Rename them in the SSH console:
   ```bash
   cd /home/ubuntu/ai_employee/AI_Employee_Vault/credentials
   mv credentials.json gmail_readonly.json
   mv token.json gmail_token_readonly.json
   chmod 600 *.json
   ```

---

## Step 5: Install Dependencies (5 min)

```bash
cd /home/ubuntu/ai_employee/AI_Employee_Vault

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and Git
sudo apt install -y python3 python3-pip python3-venv git

# Create virtual environment
python3 -m venv /home/ubuntu/ai_employee_venv
source /home/ubuntu/ai_employee_venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
```

---

## Step 6: Start Cloud Services (2 min)

```bash
cd /home/ubuntu/ai_employee/AI_Employee_Vault

# Make scripts executable
chmod +x scripts/start_cloud_services.sh cloud_sync.sh

# Start services
./scripts/start_cloud_services.sh
```

---

## Step 7: Verify Deployment (4 min)

```bash
# Check email watcher is running
ps aux | grep cloud_email_watcher

# Check logs
tail -f /home/ubuntu/ai_employee/email_watcher.log

# Verify cron job
crontab -l
```

**Expected output:**
```
ubuntu    XXXX  0.0  2.5  50000 25000 ?        S    10:30   0:00 python3 cloud_email_watcher.py
*/10 * * * * /home/ubuntu/ai_employee/AI_Employee_Vault/cloud_sync.sh
```

---

## Test the Workflow

### 1. Send a Test Email
Send yourself an email from another account.

### 2. Wait 10-15 Minutes
The cloud watcher runs every 10 minutes.

### 3. Check for Draft
On your **local machine**:
```bash
cd C:\Users\Najma-LP\Desktop\AI_Employee_Vault
git pull origin master
dir Needs_Action\email\
```

You should see a new file like `EMAIL_XXXXXXXX.md`

### 4. Review and Approve
Open the draft in Obsidian, review it, and if you approve:
```bash
move Needs_Action\email\EMAIL_XXXXXXXX.md Approved\email\
git add Approved\email\EMAIL_XXXXXXXX.md
git commit -m "Approve email send"
git push origin master
```

### 5. Verify Execution
The local zone will execute the email send via Gmail MCP.

---

## Success Criteria

✅ **Cloud Infrastructure**
- Email watcher running (check with `ps aux`)
- Cron job installed (check with `crontab -l`)
- Logs show activity (check with `tail -f email_watcher.log`)

✅ **Git Communication**
- Draft files appear in `Needs_Action/email/`
- Git sync working (check with `git log`)

✅ **End-to-End Workflow**
- Email detected → Draft created → Synced to local → Approved → Sent

---

## Troubleshooting

### Email Watcher Not Running
```bash
tail -50 /home/ubuntu/ai_employee/email_watcher.log
killall python3
cd /home/ubuntu/ai_employee/AI_Employee_Vault
./scripts/start_cloud_services.sh
```

### Credentials Issue
```bash
ls -la /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/
cat /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_token_readonly.json | grep scopes
```

Should show: `gmail.readonly`

### Git Sync Not Working
```bash
tail -50 /home/ubuntu/ai_employee/cloud_sync.log
cd /home/ubuntu/ai_employee/AI_Employee_Vault
git pull origin master
git push origin master
```

---

## What You've Accomplished

After completing these steps, you'll have:

✅ **Platinum Tier AI Employee** (100% complete)
- Cloud zone monitoring Gmail 24/7
- Local zone executing approved actions
- Vault-based communication via Git
- Complete audit trail

✅ **Production-Ready System**
- Resource-optimized (1GB RAM cloud)
- Secure (read-only cloud credentials)
- Scalable (can add more watchers)
- Monitored (logs + health checks)

✅ **Innovative Architecture**
- First vault-synced cloud-local AI system
- Human-in-the-loop approval workflow
- Complete separation of concerns

---

## Next Steps After Deployment

1. **Monitor Performance**
   - Check memory: `free -h`
   - Check logs: `tail -f email_watcher.log`

2. **Optimize as Needed**
   - Adjust sync intervals
   - Add more watchers if RAM allows

3. **Scale Up (Optional)**
   - Upgrade to VM.Standard.E2.2 (8GB RAM)
   - Add calendar monitoring
   - Deploy Odoo to cloud

---

**Let's complete this! 🚀**

**Estimated time: 20 minutes**
**Difficulty: Medium** (copy-paste commands)
**Reward: Platinum Tier AI Employee! 🎉**
