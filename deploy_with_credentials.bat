@echo off
SETLOCAL EnableDelayedExpansion

echo ============================================================================
echo          PLATINUM TIER DEPLOYMENT - WITH CREDENTIALS
echo ============================================================================
echo.
echo Gmail read-only credentials: PREPARED
echo Deployment target: Oracle Cloud VM (140.238.254.48)
echo.
echo ============================================================================
echo.

echo STEP 1: Package Credentials
echo ============================================================================
echo.
echo Creating deployment package...
mkdir deployment_package 2>nul
mkdir deployment_package\credentials 2>nul

copy credentials\cloud\gmail_readonly.json deployment_package\credentials\ >nul
copy credentials\cloud\gmail_token_readonly.json deployment_package\credentials\ >nul
copy scripts\cloud_setup.sh deployment_package\ >nul
copy scripts\start_cloud_services.sh deployment_package\ >nul
copy cloud_sync.sh deployment_package\ >nul
copy watchers\cloud_email_watcher.py deployment_package\ >nul

echo ✓ Deployment package created in deployment_package\
echo.
pause

echo.
echo ============================================================================
echo STEP 2: Access Oracle Cloud Console
echo ============================================================================
echo.
echo Opening browser...
timeout /t 2 >nul
start https://console.ap-mumbai-1.oraclecloud.com

echo.
echo In the console:
echo   1. Navigate to: Compute -^> Instances
echo   2. Click: instance-20260121-0102
echo   3. Click: Connect -^> Launch SSH Console
echo.
pause

echo.
echo ============================================================================
echo STEP 3: Upload Deployment Package
echo ============================================================================
echo.
echo UPLOAD INSTRUCTIONS:
echo.
echo 1. In the SSH console, click the UPLOAD icon (looks like arrow up)
echo 2. Navigate to: C:\Users\Najma-LP\Desktop\AI_Employee_Vault\deployment_package
echo 3. Upload these files ONE BY ONE:
echo    - credentials/gmail_readonly.json
echo    - credentials/gmail_token_readonly.json
echo    - cloud_setup.sh
echo    - start_cloud_services.sh
echo    - cloud_sync.sh
echo    - cloud_email_watcher.py
echo.
echo IMPORTANT: Create the credentials directory first!
echo   In SSH console: mkdir -p /home/ubuntu/ai_employee/AI_Employee_Vault/credentials
echo.
pause

echo.
echo ============================================================================
echo STEP 4: Run Setup Script
echo ============================================================================
echo.
echo Copy-paste this into the SSH console:
echo.
echo cd /home/ubuntu ^&^& mkdir -p ai_employee ^&^& cd ai_employee
echo.
echo Then upload the files to: /home/ubuntu/ai_employee/AI_Employee_Vault/
echo.
echo After uploading, run:
echo.
echo chmod +x cloud_setup.sh start_cloud_services.sh cloud_sync.sh
echo mv cloud_*.sh watchers/cloud_email_watcher.py AI_Employee_Vault/
echo cd AI_Employee_Vault
echo ./cloud_setup.sh
echo.
pause

echo.
echo ============================================================================
echo STEP 5: Start Cloud Services
echo ============================================================================
echo.
echo Copy-paste into SSH console:
echo.
echo cd /home/ubuntu/ai_employee/AI_Employee_Vault
echo ./scripts/start_cloud_services.sh
echo.
pause

echo.
echo ============================================================================
echo STEP 6: Verify Deployment
echo ============================================================================
echo.
echo Copy-paste into SSH console:
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
echo Your Platinum Tier AI Employee is now running on Oracle Cloud!
echo.
echo TEST IT:
echo 1. Send yourself a test email
echo 2. Wait 10-15 minutes
echo 3. On your local machine:
echo    cd AI_Employee_Vault
echo    git pull origin master
echo    dir Needs_Action\email\
echo.
echo The cloud zone should have created a draft task file!
echo.
echo For troubleshooting, see: CLOUD_SETUP_INSTRUCTIONS.md
echo.
pause
