#!/bin/bash
# Platinum Tier Cloud Setup Script
# Run this on Oracle Cloud Free Tier VM (VM.Standard.E2.1.Micro)
# Optimized for 1GB RAM constraint

set -e  # Exit on error

echo "=========================================="
echo "Platinum Tier Cloud Zone Setup"
echo "=========================================="
echo "Started at: $(date)"
echo ""

# Step 1: Update system
echo "[1/7] Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install dependencies
echo "[2/7] Installing Python, Git, and other dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl cron

# Step 3: Create workspace
echo "[3/7] Creating workspace directory..."
mkdir -p /home/ubuntu/ai_employee
cd /home/ubuntu/ai_employee

# Step 4: Clone repository
echo "[4/7] Cloning AI Employee Vault repository..."
if [ -d "AI_Employee_Vault" ]; then
    echo "Repository already exists, pulling latest changes..."
    cd AI_Employee_Vault
    git pull origin master
else
    git clone https://github.com/MathNj/ai-employee-vault.git AI_Employee_Vault
    cd AI_Employee_Vault
fi

# Step 5: Create virtual environment
echo "[5/7] Creating Python virtual environment..."
python3 -m venv /home/ubuntu/ai_employee_venv
source /home/ubuntu/ai_employee_venv/bin/activate

# Step 6: Install minimal dependencies
echo "[6/7] Installing minimal Python dependencies..."
pip install --upgrade pip
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2
pip install ics pytz

# Step 7: Create cloud environment file
echo "[7/7] Creating cloud environment configuration..."
cat > watchers/.env.cloud << 'ENVEOF'
# Cloud Zone Settings
ZONE=cloud
DRAFT_ONLY=true
WATCHER_MODE=minimal
RESOURCE_CONSTRAINED=true

# Logging
LOG_LEVEL=INFO
LOG_TO_FILE=false

# Git Sync Settings
GIT_SYNC_INTERVAL_SECONDS=600
ENVEOF

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo "Virtual environment: /home/ubuntu/ai_employee_venv"
echo "Repository: /home/ubuntu/ai_employee/AI_Employee_Vault"
echo ""
echo "Next Steps:"
echo "1. Upload your Gmail read-only credentials to:"
echo "   /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json"
echo ""
echo "2. Create cloud sync script:"
echo "   ./cloud_sync.sh"
echo ""
echo "3. Setup cron job for automated sync:"
echo "   crontab -e"
echo "   Add: */10 * * * * /home/ubuntu/ai_employee/AI_Employee_Vault/cloud_sync.sh"
echo ""
echo "Setup completed at: $(date)"
