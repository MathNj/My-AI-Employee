#!/bin/bash
# Cloud Git Sync Script
# Syncs work-zone directories between cloud and local via Git
# Optimized for resource-constrained VM (1GB RAM)

# Exit on error, but handle errors gracefully
set -e

# Configuration with environment variable overrides
VAULT_PATH="${VAULT_PATH:-/home/ubuntu/ai_employee/AI_Employee_Vault}"
LOG_FILE="${LOG_FILE:-/home/ubuntu/ai_employee/cloud_sync.log}"
MAX_RETRIES=3
RETRY_DELAY=5

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to handle errors
error_exit() {
    log "ERROR: $1"
    log "Sync failed - exiting with error"
    exit 1
}

# Function to retry git operations
retry_git() {
    local operation="$1"
    shift
    local args=("$@")

    for attempt in $(seq 1 $MAX_RETRIES); do
        log "Attempt $attempt/$MAX_RETRIES: $operation"

        if git "${args[@]}" 2>&1 | tee -a "$LOG_FILE"; then
            log "SUCCESS: $operation completed"
            return 0
        else
            exit_code=$?

            if [ $attempt -lt $MAX_RETRIES ]; then
                log "WARNING: $operation failed (exit code: $exit_code), retrying in ${RETRY_DELAY}s..."
                sleep $RETRY_DELAY
            else
                log "ERROR: $operation failed after $MAX_RETRIES attempts (exit code: $exit_code)"
                return $exit_code
            fi
        fi
    done
}

# Validate vault path exists
if [ ! -d "$VAULT_PATH" ]; then
    error_exit "Vault path does not exist: $VAULT_PATH"
fi

# Change to vault directory
cd "$VAULT_PATH" || error_exit "Failed to change to vault directory: $VAULT_PATH"

# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    error_exit "Not a git repository: $VAULT_PATH"
fi

log "=== Starting sync ==="
log "Vault: $VAULT_PATH"
log "Branch: $(git branch --show-current)"

# Step 1: Stash any local changes to avoid conflicts
log "Stashing any local changes..."
if git stash push -m "Auto-stash before sync $(date '+%Y-%m-%d %H:%M:%S')" 2>&1 | tee -a "$LOG_FILE"; then
    log "Local changes stashed (if any)"
else
    log "No changes to stash or stash failed"
fi

# Step 2: Pull any approvals from local zone
log "Pulling changes from Git..."
if ! retry_git "git pull" pull origin master; then
    log "WARNING: Git pull failed, continuing anyway"
fi

# Step 3: Check Approved/ directory for tasks to execute
log "Checking for approved tasks..."
if [ -d "Approved" ]; then
    approved_count=$(find Approved -name "*.md" -type f 2>/dev/null | wc -l)
    if [ $approved_count -gt 0 ]; then
        log "Found $approved_count approved tasks"
        # Note: Actual execution happens via separate executor script
    else
        log "No approved tasks found"
    fi
else
    log "Approved directory not found"
fi

# Step 4: Push new tasks created by cloud watchers
log "Pushing new tasks to Git..."

# Add files with error handling
for dir in Needs_Action Updates Signals; do
    if [ -d "$dir" ]; then
        log "Adding files from $dir/..."
        git add "$dir/" 2>&1 | tee -a "$LOG_FILE" || log "Warning: Failed to add $dir/"
    else
        log "Directory $dir/ not found, skipping"
    fi
done

# Check if there are changes to commit
if git diff --cached --quiet; then
    log "No new changes to commit"
else
    # Show what will be committed
    log "Changes to be committed:"
    git diff --cached --stat | tee -a "$LOG_FILE"

    # Commit with proper error handling
    commit_msg="Cloud: Sync from $(date '+%Y-%m-%d %H:%M:%S')"
    if git commit -m "$commit_msg" 2>&1 | tee -a "$LOG_FILE"; then
        log "Commit successful"

        # Push with retry logic
        if retry_git "git push" push origin master; then
            log "Changes pushed successfully"
        else
            error_exit "Failed to push changes after $MAX_RETRIES attempts"
        fi
    else
        error_exit "Failed to commit changes"
    fi
fi

log "=== Sync completed successfully ==="
echo "" | tee -a "$LOG_FILE"

# Exit successfully
exit 0
