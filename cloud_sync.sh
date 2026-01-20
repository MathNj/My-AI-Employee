#!/bin/bash
# Cloud Git Sync Script
# Syncs work-zone directories between cloud and local via Git
# Optimized for resource-constrained VM (1GB RAM)

set -e

VAULT_PATH="/home/ubuntu/ai_employee/AI_Employee_Vault"
LOG_FILE="/home/ubuntu/ai_employee/cloud_sync.log"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

cd "$VAULT_PATH"

log "=== Starting sync ==="

# Step 1: Pull any approvals from local zone
log "Pulling changes from Git..."
git pull origin master 2>&1 | grep -v "^From" | grep -v "^   " | grep -v "^*" | tee -a "$LOG_FILE" || true

# Step 2: Check Approved/ directory for tasks to execute
log "Checking for approved tasks..."
if [ -d "Approved" ] && [ "$(ls -A Approved/*.md 2>/dev/null)" ]; then
    log "Found $(ls -1 Approved/*.md 2>/dev/null | wc -l) approved tasks"
    # Note: Actual execution happens via separate executor script
    # This just logs them
fi

# Step 3: Push new tasks created by cloud watchers
log "Pushing new tasks to Git..."
git add Needs_Action/ Updates/ Signals/ 2>&1 | tee -a "$LOG_FILE" || true

# Check if there are changes to commit
if git diff --cached --quiet; then
    log "No new changes to commit"
else
    git commit -m "Cloud: Sync from $(date '+%Y-%m-%d %H:%M')" 2>&1 | tee -a "$LOG_FILE"
    git push origin master 2>&1 | tee -a "$LOG_FILE"
    log "Changes pushed successfully"
fi

log "=== Sync completed ==="
echo "" | tee -a "$LOG_FILE"
