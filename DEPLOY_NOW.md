# 🚀 PLATINUM TIER DEPLOYMENT - 3 SIMPLE STEPS

## Step 1: Access Cloud VM (1 minute)

1. Go to: https://console.ap-mumbai-1.oraclecloud.com
2. Compute → Instances → instance-20260121-0102
3. Click "Connect" → "Launch SSH Console"

## Step 2: Copy-Paste This Command (2 minutes)

In the SSH console, copy-paste:

```bash
cd /home/ubuntu && curl -L https://raw.githubusercontent.com/MathNj/ai-employee-vault/master/CLOUD_DEPLOYMENT_ALL_IN_ONE.sh -o deploy.sh && chmod +x deploy.sh && ./deploy.sh
```

Wait for it to finish. It will tell you when to upload credentials.

## Step 3: Upload Credentials & Finish (5 minutes)

When prompted:

1. On your **local machine**, go to:
   ```
   C:\Users\Najma-LP\Desktop\AI_Employee_Vault\mcp-servers\gmail-mcp\
   ```

2. In the SSH console, click the **upload icon** (↑)

3. Upload BOTH files:
   - `credentials.json`
   - `token.json`

4. In the SSH console, run:
   ```bash
   cd /home/ubuntu/ai-employee-vault/credentials
   mv credentials.json gmail_readonly.json
   mv token.json gmail_token_readonly.json
   chmod 600 *.json
   cd ..
   bash finish_setup.sh
   ```

## That's It! 🎉

**Verify:**
```bash
ps aux | grep cloud_email_watcher
tail -f /home/ubuntu/ai_employee/email_watcher.log
```

**Total time: 8 minutes**

---

## Test the Workflow

1. Send yourself a test email
2. Wait 10-15 minutes
3. On your local machine:
   ```bash
   cd AI_Employee_Vault
   git pull origin master
   dir Needs_Action\email\
   ```
4. See the draft created by cloud!

**🚀 Platinum Tier Complete!**
