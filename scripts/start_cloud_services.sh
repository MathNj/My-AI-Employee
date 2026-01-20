#!/bin/bash
# Start Cloud Services Script
# Runs cloud email watcher and sync cron job

VAULT_PATH="/home/ubuntu/ai_employee/AI_Employee_Vault"
VENV_PATH="/home/ubuntu/ai_employee_venv"

echo "Starting Cloud Services at $(date)"

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Check if credentials exist
if [ ! -f "$VAULT_PATH/credentials/gmail_readonly.json" ]; then
    echo "ERROR: Gmail credentials not found!"
    echo "Expected at: $VAULT_PATH/credentials/gmail_readonly.json"
    echo ""
    echo "Please create Gmail API credentials with read-only scope and upload them."
    exit 1
fi

# Start cloud email watcher in background
echo "Starting Cloud Email Watcher..."
cd "$VAULT_PATH"
nohup python3 watchers/cloud_email_watcher.py \
    "$VAULT_PATH" \
    "$VAULT_PATH/credentials/gmail_readonly.json" \
    > /home/ubuntu/ai_employee/email_watcher.log 2>&1 &

EMAIL_WATCHER_PID=$!
echo "Email watcher started (PID: $EMAIL_WATCHER_PID)"

# Setup cron job for sync if not already exists
echo "Checking cron job for sync..."
if ! crontab -l | grep -q "cloud_sync.sh"; then
    echo "Setting up cron job..."
    (crontab -l 2>/dev/null; echo "*/10 * * * * $VAULT_PATH/cloud_sync.sh >> /home/ubuntu/ai_employee/cloud_sync.log 2>&1") | crontab -
    echo "Cron job installed: Sync every 10 minutes"
else
    echo "Cron job already exists"
fi

echo ""
echo "=========================================="
echo "Cloud Services Started Successfully!"
echo "=========================================="
echo "Email Watcher PID: $EMAIL_WATCHER_PID"
echo "Logs:"
echo "  - Email watcher: /home/ubuntu/ai_employee/email_watcher.log"
echo "  - Sync: /home/ubuntu/ai_employee/cloud_sync.log"
echo ""
echo "To stop services:"
echo "  kill $EMAIL_WATCHER_PID"
echo "  crontab -e  # Remove the sync line"
echo ""
