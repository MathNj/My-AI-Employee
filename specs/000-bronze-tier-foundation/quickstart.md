# Bronze Tier Quickstart Guide

**Feature**: Bronze Tier Foundation - Personal AI Employee
**Estimated Setup Time**: 30-45 minutes
**Implementation Time**: 8-12 hours

This guide walks you through setting up Bronze Tier from scratch. Follow steps sequentially for best results.

---

## Prerequisites (Complete Before Starting)

### Required Software

| Software | Version | Purpose | Installation |
|----------|---------|---------|--------------|
| **Obsidian** | 1.10.6+ | Knowledge base GUI | https://obsidian.md/download |
| **Python** | 3.13+ | Watcher scripts | https://www.python.org/downloads/ |
| **Claude Code** | Latest | Reasoning engine | https://claude.com/product/claude-code |
| **Git** | Any | Version control (optional but recommended) | https://git-scm.com/ |

### System Requirements

- **RAM**: 8GB minimum, 16GB recommended
- **Disk Space**: 1GB free (500MB for vault, 500MB for dependencies)
- **Internet**: Stable connection for API calls (10+ Mbps)
- **OS**: Windows 10+, macOS 12+, or Linux (Ubuntu 20.04+)

### Account Setup

- **Claude Code Account**: Active subscription (Pro) or use free Gemini API with Claude Code Router
- **Gmail Account** (optional, only if choosing Gmail watcher): Enable API access in Google Cloud Console

---

## Setup Process

### Phase 1: Environment Setup (10 minutes)

#### Step 1.1: Create Project Directory

```bash
# Choose a location for your project
mkdir -p ~/Projects/AI_Employee
cd ~/Projects/AI_Employee

# Initialize git repository (optional)
git init
git branch -m main
```

#### Step 1.2: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify Python version
python --version  # Should be 3.13 or higher
```

#### Step 1.3: Create Directory Structure

```bash
# Create watchers directory
mkdir -p watchers

# Create docs directory
mkdir -p docs

# Create tests directory
mkdir -p tests/integration
```

---

### Phase 2: Obsidian Vault Setup (5 minutes)

#### Step 2.1: Choose Vault Location

**Option A: Inside Project** (simpler, keeps everything together)
```bash
# Create vault in project directory
mkdir -p vault
VAULT_PATH="$(pwd)/vault"
```

**Option B: Separate Location** (better if you already have an Obsidian vault)
```bash
# Use existing Obsidian vault or create new one
VAULT_PATH="/path/to/your/obsidian/vault"
```

#### Step 2.2: Open Vault in Obsidian

1. Launch Obsidian application
2. Click "Open folder as vault"
3. Navigate to your vault path and select it
4. Verify vault opens successfully

**Note**: Keep Obsidian open during testing to see changes in real-time.

---

### Phase 3: Watcher Selection & Setup (15-20 minutes)

#### Step 3.1: Choose Your Watcher

**Bronze Tier Rule**: Choose **ONE** watcher (not both)

| Watcher | Difficulty | Setup Time | Use Cases |
|---------|------------|------------|-----------|
| **File System** | Beginner | 5 min | Drop files, manual testing, simple automation |
| **Gmail** | Intermediate | 20 min | Email monitoring, real-world workflows |

**Recommendation**: Start with **File System** for fastest path to working system.

#### Step 3.2: File System Watcher Setup (Recommended)

```bash
# Create Inbox folder in vault
mkdir -p "$VAULT_PATH/Inbox"
mkdir -p "$VAULT_PATH/Needs_Action"
mkdir -p "$VAULT_PATH/Done"
mkdir -p "$VAULT_PATH/Errors"
mkdir -p "$VAULT_PATH/Logs"

# Install watchdog library
pip install watchdog==4.0.0

# Create watcher config
cat > watchers/watcher_config.yaml <<EOF
filesystem_watcher:
  enabled: true
  check_interval_sec: 30
  watched_path: "$VAULT_PATH/Inbox"
  recursive: false
  vault_path: "$VAULT_PATH"
  file_filters:
    - "*.pdf"
    - "*.docx"
    - "*.txt"
    - "*.md"
  ignore_patterns:
    - ".*"
    - "*.tmp"
  min_file_size_bytes: 100
  settle_time_sec: 2

logging:
  log_level: INFO
  log_path: "$VAULT_PATH/Logs/watcher_{date}.log"
  max_log_size_mb: 10
EOF
```

#### Step 3.3: Gmail Watcher Setup (Advanced)

**Prerequisites**:
1. Google Cloud Project with Gmail API enabled
2. OAuth 2.0 credentials (client ID, client secret)
3. Gmail account for testing

**Setup Steps**:

```bash
# Install Gmail API libraries
pip install google-auth==2.27.0 \
            google-auth-oauthlib==1.2.0 \
            google-auth-httplib2==0.2.0 \
            google-api-python-client==2.116.0

# Create .env file for credentials
cat > watchers/.env <<EOF
GMAIL_CLIENT_ID=your-client-id.apps.googleusercontent.com
GMAIL_CLIENT_SECRET=your-client-secret
GMAIL_USER_EMAIL=your-email@gmail.com
EOF

# Create vault folders (if not already created)
mkdir -p "$VAULT_PATH/Needs_Action"
mkdir -p "$VAULT_PATH/Done"
mkdir -p "$VAULT_PATH/Errors"
mkdir -p "$VAULT_PATH/Logs"

# Create watcher config
cat > watchers/watcher_config.yaml <<EOF
gmail_watcher:
  enabled: true
  check_interval_sec: 120  # 2 minutes
  max_results: 10
  labels:
    - INBOX
  credentials_path: .env
  token_path: token.json
  vault_path: "$VAULT_PATH"
  scopes:
    - https://www.googleapis.com/auth/gmail.readonly

logging:
  log_level: INFO
  log_path: "$VAULT_PATH/Logs/watcher_{date}.log"
  max_log_size_mb: 10
EOF
```

**Gmail API Setup** (if not done):
1. Go to https://console.cloud.google.com/
2. Create new project: "AI Employee"
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app type)
5. Download credentials.json, save as `watchers/.env` (convert to KEY=VALUE format)

---

### Phase 4: Install Dependencies (5 minutes)

#### Step 4.1: Create requirements.txt

```bash
cat > watchers/requirements.txt <<EOF
# Common dependencies
pyyaml==6.0.1
python-frontmatter==1.1.0

# File System Watcher (if chosen)
watchdog==4.0.0

# Gmail Watcher (if chosen)
google-auth==2.27.0
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.116.0

# Testing (optional)
pytest==8.0.0
EOF
```

#### Step 4.2: Install All Dependencies

```bash
cd watchers
pip install -r requirements.txt

# Verify installation
python -c "import yaml; import frontmatter; print('Dependencies OK')"
```

---

### Phase 5: Initial Testing (10 minutes)

#### Step 5.1: Test File System Watcher (If Chosen)

**Terminal 1 - Start Watcher**:
```bash
cd watchers
python filesystem_watcher.py
```

**Terminal 2 - Trigger Event**:
```bash
# Create test file
echo "Test invoice content" > "$VAULT_PATH/Inbox/test_invoice.txt"

# Wait 30-60 seconds for detection

# Check for action file
ls -lh "$VAULT_PATH/Needs_Action/"
# Should see: FILE_YYYYMMDD_HHMMSS_test-invoice.md
```

**Verify Action File Format**:
```bash
cat "$VAULT_PATH/Needs_Action/FILE_"*test-invoice.md

# Expected output:
# ---
# type: file
# source: FileSystem
# timestamp: 2026-01-17T14:30:00Z
# status: pending
# payload:
#   filename: test_invoice.txt
#   path: /path/to/vault/Inbox/test_invoice.txt
#   ...
# ---
#
# # File Event
# File detected: test_invoice.txt
```

**Check Logs**:
```bash
tail -f "$VAULT_PATH/Logs/watcher_$(date +%Y-%m-%d).log"

# Expected entries:
# 2026-01-17 14:30:00 | INFO | FileSystem watcher started
# 2026-01-17 14:30:30 | INFO | Check cycle #1 - 0 files detected
# 2026-01-17 14:31:00 | INFO | Check cycle #2 - 1 file detected: test_invoice.txt
# 2026-01-17 14:31:05 | INFO | Action file created: FILE_20260117_143100_test-invoice.md
```

#### Step 5.2: Test Gmail Watcher (If Chosen)

**Terminal 1 - Start Watcher**:
```bash
cd watchers
python gmail_watcher.py

# First run will prompt for OAuth consent
# Follow browser prompts to authorize
# Token saved to token.json for future runs
```

**Trigger Event**:
- Send test email to your Gmail account
- Wait 2-5 minutes for next check cycle

**Verify Action File**:
```bash
ls "$VAULT_PATH/Needs_Action/EMAIL_"*.md
cat "$VAULT_PATH/Needs_Action/EMAIL_"*.md
```

---

### Phase 6: Claude Code Integration (5 minutes)

#### Step 6.1: Authenticate Claude Code

```bash
# Navigate to vault directory
cd "$VAULT_PATH"

# Start Claude Code
claude-code

# Verify Claude can access vault
# In Claude Code, run:
ls -lh
# Should see: Inbox/, Needs_Action/, Done/, Dashboard.md, etc.
```

#### Step 6.2: Test Vault Read/Write

**In Claude Code**, run these commands:

```bash
# Test read
cat Company_Handbook.md

# Test write to Dashboard
echo "- $(date +%Y-%m-%d\ %H:%M) | TEST | Manual test entry | ✅ Complete" >> Dashboard.md

# Verify append worked
tail Dashboard.md
```

---

## Usage Workflow

### Daily Operation

**1. Start Watcher** (Terminal 1):
```bash
cd ~/Projects/AI_Employee/watchers
source ../venv/bin/activate
python filesystem_watcher.py  # or gmail_watcher.py
```

**2. Monitor Activity**:
- Open Obsidian vault
- Watch /Needs_Action folder for new action files
- Check watcher log in /Logs folder

**3. Process Tasks** (Terminal 2):
```bash
cd "$VAULT_PATH"
claude-code

# In Claude Code:
/task-processor --vault_path "$VAULT_PATH"
```

**4. Verify Results**:
- Check Dashboard.md for activity log entries
- Verify action files moved from /Needs_Action to /Done
- Inspect completed files for processing metadata

---

## Troubleshooting

### Watcher Not Detecting Files

**Symptom**: Drop file in Inbox, no action file created

**Checks**:
```bash
# Verify watcher is running
ps aux | grep watcher

# Check watcher log for errors
tail -f "$VAULT_PATH/Logs/watcher_$(date +%Y-%m-%d).log"

# Verify config path is correct
grep "vault_path" watchers/watcher_config.yaml

# Check file permissions
ls -l "$VAULT_PATH/Inbox"
```

**Solution**: Ensure vault_path in watcher_config.yaml is absolute path, not relative

---

### Action File Has Invalid Format

**Symptom**: task-processor skill reports validation error

**Check**:
```bash
# Inspect action file
cat "$VAULT_PATH/Needs_Action/FILE_"*.md

# Validate YAML frontmatter
python -c "
import frontmatter
with open('path/to/action_file.md') as f:
    post = frontmatter.load(f)
    print(post.metadata)
"
```

**Solution**: Check for missing required fields (type, source, timestamp, status, payload)

---

### Gmail OAuth Token Expired

**Symptom**: Gmail watcher crashes with "credentials expired"

**Solution**:
```bash
# Delete old token
rm watchers/token.json

# Restart watcher (will prompt for re-auth)
python gmail_watcher.py
```

---

### Claude Code Cannot Write to Vault

**Symptom**: "Permission denied" when updating Dashboard.md

**Check**:
```bash
# Verify vault directory permissions
ls -ld "$VAULT_PATH"

# Check if Obsidian has vault locked
ps aux | grep Obsidian
```

**Solution**:
- Close Obsidian temporarily
- Verify file permissions allow write access
- Re-run Claude Code command

---

### Watcher Log File Growing Too Large

**Symptom**: watcher_YYYY-MM-DD.log exceeds 10MB

**Solution**:
```bash
# Archive old log
mv "$VAULT_PATH/Logs/watcher_2026-01-17.log" \
   "$VAULT_PATH/Logs/archive/watcher_2026-01-17.log.gz"

# Restart watcher (creates new log file)
```

---

## Next Steps

### After Successful Bronze Tier Setup

1. **Validate Architecture**:
   - Run watcher for 24 hours continuously
   - Process 50+ test action files
   - Verify 95% success rate

2. **Document Your Setup**:
   - Create README.md with your specific configuration
   - Record any custom modifications
   - Note which watcher you chose and why

3. **Record Demo Video** (5-10 minutes):
   - Show watcher detecting event
   - Show action file creation
   - Show Claude Code processing
   - Show Dashboard update

4. **Consider Silver Tier Upgrade**:
   - Add second watcher (both Gmail AND File System)
   - Implement first MCP server (e.g., Gmail send)
   - Add human-in-the-loop approval workflow
   - Add scheduling (cron/Task Scheduler)

---

## Bronze Tier Completion Checklist

- [ ] Obsidian vault created with folder structure
- [ ] Dashboard.md and Company_Handbook.md populated
- [ ] ONE watcher script running (Gmail OR File System)
- [ ] Action files created in /Needs_Action with correct metadata
- [ ] Claude Code authenticated and can read vault
- [ ] Claude Code can write to Dashboard.md
- [ ] task-processor skill successfully processes action files
- [ ] vault-setup skill creates vault structure
- [ ] dashboard-updater skill refreshes status section
- [ ] Watcher runs 1+ hours without crashing
- [ ] End-to-end test: Event → Action File → Processing → Done
- [ ] All Bronze tier success criteria validated (from spec.md)
- [ ] README.md written with setup instructions
- [ ] Demo video recorded showing key workflow

**Estimated Total Time**: 8-12 hours (setup: 1 hour, implementation: 7-11 hours)

---

## Resources

- **Obsidian Help**: https://help.obsidian.md/
- **Claude Code Docs**: https://docs.anthropic.com/claude-code
- **Gmail API Guide**: https://developers.google.com/gmail/api/quickstart/python
- **Python watchdog**: https://python-watchdog.readthedocs.io/
- **Hackathon Resources**: Requirements2.md in repository root

---

**Quickstart Complete**: Follow these steps sequentially for successful Bronze Tier setup. For issues, check Troubleshooting section or review spec.md and plan.md for architectural details.
