# 🚀 FASTEST PATH TO PLATINUM TIER

## Method 1: Oracle Cloud Console (Easiest - 2 Minutes)

1. **Go to:** https://console.ap-mumbai-1.oraclecloud.com

2. **Navigate:**
   - Compute → Instances
   - Click: instance-20260121-0102
   - Click: "Connect" button
   - Select: "Launch SSH Console"

3. **Browser-based terminal opens** (no SSH key needed!)

4. **Copy-paste this command:**
   ```bash
   cd /home/ubuntu && curl -L https://raw.githubusercontent.com/MathNj/ai-employee-vault/master/CLOUD_DEPLOYMENT_ALL_IN_ONE.sh -o deploy.sh && chmod +x deploy.sh && ./deploy.sh
   ```

5. **When prompted, upload credentials:**
   - Click upload icon in SSH console
   - Upload from: `C:\Users\Najma-LP\Desktop\AI_Employee_Vault\mcp-servers\gmail-mcp\`
   - Files: `credentials.json` and `token.json`

6. **Finish setup:**
   ```bash
   cd /home/ubuntu/ai-employee-vault/credentials
   mv credentials.json gmail_readonly.json
   mv token.json gmail_token_readonly.json
   chmod 600 *.json
   cd ..
   bash finish_setup.sh
   ```

**Done! 🎉**

---

## Method 2: SSH from Your PC (Requires Matching Key)

Since the VM was created with `ssh-key-2026-01-20`, you'd need that private key to SSH directly. The browser-based console in Method 1 bypasses this requirement.

---

## Why Method 1 Works

The Oracle Cloud Console's browser-based SSH:
- ✅ Doesn't require your private SSH key
- ✅ Uses Oracle's authentication
- ✅ Works immediately
- ✅ No setup needed

**This is the fastest and easiest way!**

---

## After Deployment

**Verify services running:**
```bash
ps aux | grep cloud_email_watcher
tail -f /home/ubuntu/ai_employee/email_watcher.log
crontab -l
```

**Test workflow:**
1. Send yourself a test email
2. Wait 10-15 minutes
3. On local machine:
   ```bash
   cd AI_Employee_Vault
   git pull origin master
   dir Needs_Action\email\
   ```

**🚀 Platinum Tier complete in 8 minutes!**
