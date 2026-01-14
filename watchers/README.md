# Filesystem Watcher

This folder contains the filesystem watcher script that monitors the `/Inbox` folder for new files.

## Overview

The filesystem watcher uses the `watchdog` library for **real-time event detection** instead of polling. This provides:
- ✅ Instant detection of new files
- ✅ Lower CPU usage (event-driven)
- ✅ More reliable than polling
- ✅ Recommended approach from Requirements.md

## Installation

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Or install watchdog directly:
```bash
pip install watchdog
```

### Step 2: Verify Installation

```bash
python -c "import watchdog; print('Watchdog installed:', watchdog.__version__)"
```

## Usage

### Start the Watcher

**Option 1: Run in terminal (foreground)**
```bash
python filesystem_watcher.py
```

**Option 2: Run in background (Windows)**
```bash
start pythonw filesystem_watcher.py
```

**Option 3: Run in background (Linux/Mac)**
```bash
nohup python filesystem_watcher.py &
```

### Stop the Watcher

**If running in terminal:**
Press `Ctrl+C`

**If running in background (Windows):**
```bash
tasklist | findstr python
taskkill /PID <process_id> /F
```

**If running in background (Linux/Mac):**
```bash
ps aux | grep filesystem_watcher
kill <process_id>
```

## How It Works

1. **Monitors:** The `/Inbox` folder continuously
2. **Detects:** When a new file is created/copied into Inbox
3. **Creates:** A task file in `/Needs_Action` with metadata
4. **Logs:** All detections to `/Logs/actions_YYYY-MM-DD.json`

## Task File Format

When a file is detected, a task file is created with this structure:

```markdown
---
type: file_drop
source_file: document.pdf
detected: 2026-01-11T22:30:00
size_bytes: 102400
file_extension: .pdf
status: pending
priority: medium
---

# New File Detected: document.pdf

## File Information
- **Name:** document.pdf
- **Size:** 102,400 bytes (100.0 KB)
- **Type:** .pdf
- **Detected:** 2026-01-11T22:30:00

## Suggested Actions
- [ ] Review file contents
- [ ] Determine purpose/category
- [ ] Process according to file type
- [ ] Archive to appropriate location
```

## Priority Determination

Files are automatically assigned priority based on:

**High Priority:**
- Filenames containing: urgent, asap, critical, important, invoice, payment

**Medium Priority:**
- Document types: .pdf, .docx, .xlsx, .doc, .xls
- All other files

**Low Priority:**
- (Can be customized in the script)

## Features

### Automatic File Detection
- Real-time monitoring with watchdog library
- Instant task creation when files are added

### Smart Metadata
- File size (bytes and human-readable)
- File extension/type
- Detection timestamp
- Automatic priority assignment

### Logging
- All detections logged to JSON files
- Daily log rotation
- Both file and console logging

### Error Handling
- Graceful handling of file access errors
- Skips temporary/hidden files
- Waits for files to finish writing

## Testing

### Test the Watcher

1. **Start the watcher:**
   ```bash
   python filesystem_watcher.py
   ```

2. **In another terminal/window, create a test file:**
   ```bash
   echo "Test content" > Inbox/test.txt
   ```

3. **Check the results:**
   ```bash
   ls Needs_Action/
   ```

   You should see a new task file like:
   `FILE_2026-01-11-22-30-00_test.txt.md`

4. **View the task:**
   ```bash
   cat Needs_Action/FILE_*.md
   ```

## Customization

Edit `filesystem_watcher.py` to customize:

### Change Priority Rules
Modify the `determine_priority()` method:
```python
def determine_priority(self, filename: str, extension: str) -> str:
    # Add your custom priority logic here
    if 'client' in filename.lower():
        return 'high'
    # ... etc
```

### Add File Filtering
Modify the `on_created()` method:
```python
def on_created(self, event):
    source = Path(event.src_path)

    # Skip certain file types
    if source.suffix in ['.tmp', '.temp']:
        return
```

### Change Check Behavior
The watchdog library handles event detection automatically. No polling configuration needed!

## Troubleshooting

### Watcher Not Detecting Files

**Check 1:** Is watchdog installed?
```bash
pip show watchdog
```

**Check 2:** Is the watcher running?
Check terminal output or process list

**Check 3:** Are you dropping files in the right folder?
```bash
pwd  # Should be in vault root
ls Inbox/  # Should see your test file
```

### Permission Errors

If you see permission errors:
```bash
# Windows: Run as administrator
# Linux/Mac: Check folder permissions
chmod 755 watchers/
```

### Files Not Creating Tasks

Check the logs:
```bash
cat Logs/watcher_2026-01-11.log
```

## Performance

The watchdog-based watcher is highly efficient:
- **CPU usage:** Near zero when idle
- **Memory:** ~10-20 MB
- **Detection latency:** <100ms typically
- **Suitable for:** 24/7 operation

## Integration

The watcher integrates with:
- **task-processor:** Processes the created task files
- **dashboard-updater:** Shows watcher status
- **Logs:** Records all activity

## Next Steps

After setting up the watcher:
1. ✅ Install dependencies
2. ✅ Start the watcher
3. ✅ Test by dropping a file in Inbox
4. ⏳ Process tasks with task-processor
5. ⏳ Update dashboard to see results

---

*Part of Personal AI Employee Bronze Tier*
*Using watchdog library for real-time file detection*
