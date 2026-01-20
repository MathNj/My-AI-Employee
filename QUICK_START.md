# Platinum Tier Quick Start Card

**Print this and keep it handy!**

---

## 🚀 5-Minute Quick Start

### 1. Access Your Cloud VM
```
https://console.ap-mumbai-1.oraclecloud.com
→ Compute → Instances → instance-20260121-0102
→ Connect → Launch SSH Console
```

### 2. Copy-Paste This Command
```bash
cd /home/ubuntu && curl -L https://raw.githubusercontent.com/MathNj/ai-employee-vault/master/scripts/cloud_setup.sh -o cloud_setup.sh && chmod +x cloud_setup.sh && ./cloud_setup.sh
```

### 3. Create Gmail Credentials (On Your PC)
```bash
cd AI_Employee_Vault
python3 scripts/create_gmail_readonly_creds.py
```

### 4. Upload Credentials to Cloud
- In SSH console: Click upload icon
- Upload: `gmail_token_readonly.json`
- Run: `mv ~/gmail_token_readonly.json /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json`

### 5. Start Services
```bash
cd /home/ubuntu/ai_employee/AI_Employee_Vault
./scripts/start_cloud_services.sh
```

### 6. Verify
```bash
ps aux | grep cloud_email_watcher
tail -f /home/ubuntu/ai_employee/email_watcher.log
```

---

## 📊 Current Status

**Gold Tier:** ✅ 100% Complete
**Platinum Tier:** ⏳ 90% Complete (Ready for deployment)
**Time to Deploy:** ~40 minutes

---

## 🔗 Important Links

**Oracle Cloud Console:**
https://console.ap-mumbai-1.oraclecloud.com

**GitHub Repository:**
https://github.com/MathNj/ai-employee-vault

**Cloud VM IP:** 140.238.254.48

---

## 📚 Documentation

**Start Here:** `CLOUD_SETUP_INSTRUCTIONS.md`
**Analysis:** `REQUIREMENTS_vs_IMPLEMENTATION.md`
**Summary:** `PLATINUM_TIER_COMPLETE.md`

---

## ✅ Success Checklist

After deployment:
- [ ] Email watcher running (`ps aux | grep cloud_email_watcher`)
- [ ] Cron job installed (`crontab -l`)
- [ ] Credentials in place (`ls credentials/`)
- [ ] Logs show activity (`tail -f email_watcher.log`)
- [ ] Test email detected
- [ ] Draft synced to local
- [ ] Approval workflow tested
- [ ] Email sent successfully

---

## 🆘 Troubleshooting

**Services not running?**
```bash
killall python3
cd /home/ubuntu/ai_employee/AI_Employee_Vault
./scripts/start_cloud_services.sh
```

**Check logs:**
```bash
tail -50 /home/ubuntu/ai_employee/email_watcher.log
tail -50 /home/ubuntu/ai_employee/cloud_sync.log
```

**Verify Git:**
```bash
cd /home/ubuntu/ai_employee/AI_Employee_Vault
git pull origin master
git push origin master
```

---

## 🎯 What You've Built

✅ **Gold Tier AI Employee** (Complete)
- 22+ production skills
- 6 operational watchers
- 3 MCP servers
- 93.8% test pass rate

✅ **Platinum Tier Infrastructure** (Ready)
- Cloud deployment scripts
- Work-zone architecture
- Git sync automation
- Security protocols
- Helper tools & verification

**Total Completion:** 85% (Deployment pending)

---

**Generated:** 2026-01-21
**Status:** Ready for Platinum Tier Deployment 🚀
