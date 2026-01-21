#!/bin/bash
# PLATINUM TIER DEPLOYMENT - ALL IN ONE
# Copy-paste this ENTIRE script into the Oracle Cloud Console SSH

set -e

echo "=========================================="
echo "Platinum Tier Cloud Deployment"
echo "Started at: $(date)"
echo "=========================================="
echo ""

# Step 1: Clone repository
echo "[1/6] Cloning repository..."
cd /home/ubuntu
if [ -d "ai-employee-vault" ]; then
    echo "Repository exists, pulling latest..."
    cd ai-employee-vault
    git pull origin master
else
    git clone https://github.com/MathNj/ai-employee-vault.git ai-employee-vault
    cd ai-employee-vault
fi

# Step 2: Install dependencies
echo "[2/6] Installing system dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git curl

# Step 3: Create virtual environment
echo "[3/6] Creating Python virtual environment..."
python3 -m venv /home/ubuntu/ai_employee_venv
source /home/ubuntu/ai_employee_venv/bin/activate

# Step 4: Install Python packages
echo "[4/6] Installing Python packages..."
pip install --upgrade pip
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

# Step 5: Setup credentials directory
echo "[5/6] Setting up credentials directory..."
mkdir -p credentials
mkdir -p watchers

echo ""
echo "⚠️  CREDENTIALS UPLOAD REQUIRED"
echo "=================================="
echo ""
echo "You need to upload your Gmail credentials now:"
echo ""
echo "1. On your LOCAL machine, go to:"
echo "   C:\\Users\\Najma-LP\\Desktop\\AI_Employee_Vault\\mcp-servers\\gmail-mcp\\"
echo ""
echo "2. Upload these files to /home/ubuntu/ai-employee-vault/credentials/:"
echo "   - credentials.json"
echo "   - token.json"
echo ""
echo "3. In the SSH console, click the upload icon and upload both files"
echo ""
echo "4. After uploading, run these commands:"
echo "   cd /home/ubuntu/ai-employee-vault/credentials"
echo "   mv credentials.json gmail_readonly.json"
echo "   mv token.json gmail_token_readonly.json"
echo "   chmod 600 *.json"
echo ""
echo "5. Then come back and run: bash /home/ubuntu/ai-employee-vault/finish_setup.sh"
echo ""
echo "=================================="
echo ""

# Create finish script
cat > /home/ubuntu/ai-employee-vault/finish_setup.sh << 'EOF'
#!/bin/bash
echo "[6/6] Starting cloud services..."
cd /home/ubuntu/ai-employee-vault

# Make scripts executable
chmod +x scripts/start_cloud_services.sh cloud_sync.sh
chmod +x watchers/cloud_email_watcher.py

# Start services
./scripts/start_cloud_services.sh

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Verify services:"
echo "  ps aux | grep cloud_email_watcher"
echo "  tail -f /home/ubuntu/ai_employee/email_watcher.log"
echo "  crontab -l"
echo ""
EOF

chmod +x /home/ubuntu/ai-employee-vault/finish_setup.sh

echo "Setup script ready!"
echo ""
echo "NEXT: Upload credentials, then run:"
echo "  bash /home/ubuntu/ai-employee-vault/finish_setup.sh"
echo ""
