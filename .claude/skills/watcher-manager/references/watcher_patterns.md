# Watcher Patterns Reference

## File System Watcher Patterns

### Basic Pattern
Monitor a single folder for any new files.

**Use case:** Simple file drop monitoring
**Configuration:**
- Watch path: `/Inbox`
- Interval: 5 seconds
- File types: All

### Filtered Pattern
Monitor for specific file types only.

**Use case:** Only process PDFs, Word docs, etc.
**Configuration:**
```python
# In the watcher, add file filtering:
valid_extensions = {'.pdf', '.docx', '.txt', '.md'}
files = [f for f in inbox_path.iterdir()
         if f.is_file() and f.suffix.lower() in valid_extensions]
```

### Archive Pattern
Move processed files instead of leaving them in Inbox.

**Use case:** Clean up Inbox after detection
**Implementation:**
```python
# After creating action file:
archive_path = VAULT_PATH / "Inbox" / "Processed"
archive_path.mkdir(exist_ok=True)
shutil.move(source_file, archive_path / source_file.name)
```

## Watcher Lifecycle

### Starting the Watcher

**Terminal (foreground):**
```bash
python watchers/filesystem_watcher.py
```

**Background (Windows):**
```bash
start pythonw watchers/filesystem_watcher.py
```

**Background (Linux/Mac):**
```bash
nohup python watchers/filesystem_watcher.py &
```

### Stopping the Watcher

**Foreground:** Press Ctrl+C

**Background Windows:**
```bash
taskkill /F /IM pythonw.exe
```

**Background Linux/Mac:**
```bash
pkill -f filesystem_watcher.py
```

## Task File Format

Task files created by watchers should follow this format:

```markdown
---
type: file_drop
source_file: example.pdf
detected: 2026-01-11T10:30:00
size_bytes: 102400
status: pending
priority: medium
---

# New File Detected: example.pdf

## File Information
- **Name:** example.pdf
- **Size:** 102,400 bytes
- **Detected:** 2026-01-11T10:30:00
- **Location:** Inbox

## Suggested Actions
- [ ] Review file contents
- [ ] Determine purpose/category
- [ ] Process or archive
- [ ] Update dashboard

## Notes
[Space for Claude to add processing notes]
```

## Monitoring Multiple Folders

To watch multiple folders, run separate watcher instances with different configurations:

```python
# watcher_documents.py - monitors /Inbox/Documents
# watcher_images.py - monitors /Inbox/Images
# watcher_data.py - monitors /Inbox/Data
```

## Error Handling

### File Lock Errors
If files are being written when detected:
```python
try:
    file_size = source_file.stat().st_size
except PermissionError:
    logger.warning(f"File locked, will retry: {source_file}")
    return None
```

### Network Folder Monitoring
For network drives, increase check interval:
```python
CHECK_INTERVAL = 30  # seconds, for network drives
```

## Performance Considerations

**Small intervals (1-5 seconds):**
- Good for: Local drives, time-sensitive tasks
- Trade-off: Higher CPU usage

**Medium intervals (10-30 seconds):**
- Good for: Most use cases, balanced performance
- Trade-off: Slight delay in detection

**Large intervals (60+ seconds):**
- Good for: Network drives, low-priority monitoring
- Trade-off: Delayed response

## Advanced: watchdog Library

For more sophisticated file monitoring, use the `watchdog` library:

```python
pip install watchdog

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # File was created, process it
            self.create_action_file(Path(event.src_path))
```

Benefits:
- Real-time event detection (no polling)
- Lower CPU usage
- More reliable for large folders
