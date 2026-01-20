@echo off
REM Platinum Tier One-Click Deployment
REM Run this on your local machine to guide you through deployment

echo ============================================================================
echo                     PLATINUM TIER DEPLOYMENT
echo ============================================================================
echo.
echo This script will guide you through deploying your AI Employee to the cloud.
echo.
echo STEP 1: Access Oracle Cloud Console
echo ============================================================================
echo.
echo 1. Opening browser...
echo.
timeout /t 2 >nul
start https://console.ap-mumbai-1.oraclecloud.com

echo.
echo 2. In the console:
echo    - Navigate to: Compute → Instances
echo    - Click: instance-20260121-0102
echo    - Click: Connect → Launch SSH Console
echo.
pause

echo.
echo ============================================================================
echo STEP 2: Copy This Command to SSH Console
echo ============================================================================
echo.
echo In the SSH console (browser), copy-paste this ENTIRE command:
echo.
echo cd /home/ubuntu ^&^& curl -L https://raw.githubusercontent.com/MathNj/ai-employee-vault/master/scripts/cloud_setup.sh -o cloud_setup.sh ^&^& chmod +x cloud_setup.sh ^&^& ./cloud_setup.sh
echo.
pause

echo.
echo ============================================================================
echo STEP 3: Create Gmail Credentials
echo ============================================================================
echo.
echo 1. Opening credentials helper...
echo.
timeout /t 2 >nul
python scripts\create_gmail_readonly_creds.py

echo.
echo 2. Upload the generated gmail_token_readonly.json to cloud VM:
echo    - In SSH console, click upload icon
echo    - Upload: gmail_token_readonly.json
echo.
pause

echo.
echo ============================================================================
echo STEP 4: Start Cloud Services
echo ============================================================================
echo.
echo Copy-paste this into SSH console:
echo.
echo cd /home/ubuntu/ai_employee/AI_Employee_Vault ^&^& ./scripts/start_cloud_services.sh
echo.
pause

echo.
echo ============================================================================
echo STEP 5: Verify Deployment
echo ============================================================================
echo.
echo Copy-paste these commands into SSH console:
echo.
echo ps aux ^| grep cloud_email_watcher
echo tail -f /home/ubuntu/ai_employee/email_watcher.log
echo crontab -l
echo.
pause

echo.
echo ============================================================================
echo                    DEPLOYMENT COMPLETE!
echo ============================================================================
echo.
echo Your Platinum Tier AI Employee is now running!
echo.
echo Next steps:
echo 1. Send yourself a test email
echo 2. Wait 10-15 minutes
echo 3. On your local machine:
echo    cd AI_Employee_Vault
echo    git pull origin master
echo    ls Needs_Action/email/
echo.
echo For troubleshooting, see: CLOUD_SETUP_INSTRUCTIONS.md
echo.
pause
