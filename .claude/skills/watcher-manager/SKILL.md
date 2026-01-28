---
name: watcher-manager
description: Create and manage watcher scripts that monitor inputs for Personal AI Employee. Use when the user needs to set up file system monitoring, create watcher scripts, or configure automated detection of new tasks. Triggers include "create watcher", "set up file monitoring", "monitor inbox folder", "watch for new files", or "configure watcher script".
---

# Watcher Manager

## Overview

This skill creates and manages Python watcher scripts that monitor various inputs (file systems, emails, messages) and automatically create task files in the `/Needs_Action` folder when new items are detected.

## Bronze Tier Focus

For Bronze tier, focus on **file system watching** - monitoring a folder for new files and automatically creating action items.

## Core Workflow

### 1. Create File System Watcher

Use `scripts/generate_filesystem_watcher.py` to create a watcher script that:
- Monitors the `/Inbox` folder for new files
- Creates corresponding task files in `/Needs_Action`
- Generates metadata about detected files
- Runs continuously in the background

### 2. Configure Watcher Parameters

Customize the watcher with these parameters:
- **Watch folder:** Which folder to monitor (default: `/Inbox`)
- **Check interval:** How often to check (default: 5 seconds)
- **File patterns:** Which file types to watch (default: all files)
- **Auto-start:** Whether to start on system boot

### 3. Start/Stop Watcher

**To start the watcher:**
```bash
python watchers/filesystem_watcher.py
```

**To run in background (Windows):**
```bash
start pythonw watchers/filesystem_watcher.py
```

**To stop the watcher:**
- Find the Python process and terminate it
- Or use Ctrl+C if running in terminal

### 4. Test Watcher

Verify the watcher works:
1. Start the watcher script
2. Drop a test file in `/Inbox`
3. Check that a task file appears in `/Needs_Action` within a few seconds
4. Verify the task file has correct metadata

## Usage Patterns

**Creating a new filesystem watcher:**
1. Run `python scripts/generate_filesystem_watcher.py`
2. Review the generated script in `/watchers/filesystem_watcher.py`
3. Test the watcher with a sample file
4. Configure for background execution

**Customizing watcher behavior:**
- Edit the generated script to change check interval
- Modify file pattern matching in the script
- Adjust metadata format in task file creation

## Implementation Details

The filesystem watcher:
- Uses Python's `watchdog` library for efficient file monitoring
- Creates task files with frontmatter metadata
- Logs all detected files
- Handles errors gracefully (network issues, file locks, etc.)
- Moves original files from `/Inbox` to an archive location

## Resources

### scripts/generate_filesystem_watcher.py
Basic script that generates a simple filesystem watcher Python script.

### scripts/watcher_manager_ultimate.py
**NEW: Enhanced watcher manager with:**
- Multi-folder watching with different rules per folder
- Event filtering and deduplication
- Pattern matching (glob) and ignore rules
- Automatic restart on failure
- Structured JSON logging
- Watcher health monitoring
- Event aggregation and throttling
- Command execution on events
- Webhook notifications
- Hot reload configuration

**Usage:**
```bash
# Start watching with enhanced features
python .claude/skills/watcher-manager/scripts/watcher_manager_ultimate.py

# Use custom config
python .claude/skills/watcher-manager/scripts/watcher_manager_ultimate.py --config watcher_config.yaml

# Show status
python .claude/skills/watcher-manager/scripts/watcher_manager_ultimate.py --status

# Health check
python .claude/skills/watcher-manager/scripts/watcher_manager_ultimate.py --health
```

**Configuration (watcher_config.yaml):**
```yaml
folders:
  - path: /path/to/Inbox
    recursive: true
    enabled: true
    rules:
      - name: create_tasks
        filter:
          patterns: ["*.pdf", "*.docx"]
          ignore_patterns: ["*.tmp"]
          extensions: [".pdf", ".docx"]
        actions:
          - type: create_task
          - type: log
            level: info
        priority: 10

deduplicate_window_seconds: 5
aggregate_window_seconds: 60
max_restarts: 10
health_check_interval: 60
```

### references/watcher_patterns.md
Detailed patterns and examples for different watcher configurations.

## Version History

**v2.0.0** (2026-01-26) - Ultimate Edition
- ✅ Multi-folder watching support
- ✅ Advanced event filtering and deduplication
- ✅ Health monitoring and auto-restart
- ✅ Structured JSON logging
- ✅ Event aggregation and throttling
- ✅ Webhook notifications
- ✅ Command execution on events
- ✅ Hot reload configuration

**v1.0.0** - Initial basic watcher generator
