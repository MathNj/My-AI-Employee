#!/usr/bin/env python3
"""
File System Watcher for Personal AI Employee

Uses watchdog library for real-time file detection in the Inbox folder.
When new files are detected, creates task files in Needs_Action folder.

Based on the architecture from Requirements.md
"""

import sys
from pathlib import Path

# Fix import conflict: remove current directory from sys.path to avoid
# Python finding filesystem_watcher.py when importing 'watchdog' package
if str(Path(__file__).parent) in sys.path:
    sys.path.remove(str(Path(__file__).parent))

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from datetime import datetime
import shutil
import logging
import time
import sys


# Configuration
VAULT_PATH = Path(__file__).parent.parent  # Root of the vault
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"

# Setup logging
LOGS_PATH.mkdir(exist_ok=True)
log_file = LOGS_PATH / f'watcher_{datetime.now().strftime("%Y-%m-%d")}.log'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InboxWatcherHandler(FileSystemEventHandler):
    """
    Event handler for Inbox folder monitoring.

    Detects new files and creates corresponding task files in Needs_Action.
    """

    def __init__(self, vault_path: str):
        super().__init__()
        self.vault_path = Path(vault_path)
        self.inbox = self.vault_path / 'Inbox'
        self.needs_action = self.vault_path / 'Needs_Action'

        # Ensure directories exist
        self.inbox.mkdir(exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)

        logger.info(f"Watcher initialized")
        logger.info(f"  Monitoring: {self.inbox}")
        logger.info(f"  Output to: {self.needs_action}")

    def on_created(self, event):
        """
        Called when a file or directory is created.

        Args:
            event: FileSystemEvent containing information about the created file
        """
        # Ignore directory creation
        if event.is_directory:
            return

        # Get the source file path
        source = Path(event.src_path)

        # Skip temporary files and hidden files
        if source.name.startswith('.') or source.name.startswith('~'):
            logger.debug(f"Skipping temporary/hidden file: {source.name}")
            return

        # Wait a moment to ensure file is fully written
        time.sleep(0.5)

        try:
            # Create task file in Needs_Action
            self.create_task_file(source)
            logger.info(f"✓ Created task for: {source.name}")

        except Exception as e:
            logger.error(f"Error processing {source.name}: {e}")

    def create_task_file(self, source_file: Path):
        """
        Create a task file in Needs_Action folder with metadata.

        Args:
            source_file: Path to the detected file
        """
        timestamp = datetime.now().isoformat()

        # Get file information
        try:
            file_size = source_file.stat().st_size
            file_extension = source_file.suffix.lower()
        except Exception as e:
            logger.error(f"Error reading file stats for {source_file}: {e}")
            file_size = 0
            file_extension = ""

        # Create task filename with timestamp to avoid conflicts
        safe_timestamp = timestamp.replace(':', '-').replace('.', '-')
        task_filename = f"FILE_{safe_timestamp}_{source_file.name}.md"
        task_path = self.needs_action / task_filename

        # Determine priority based on file type or keywords
        priority = self.determine_priority(source_file.name, file_extension)

        # Create task content with frontmatter
        task_content = f"""---
type: file_drop
source_file: {source_file.name}
original_path: {str(source_file)}
detected: {timestamp}
size_bytes: {file_size}
file_extension: {file_extension}
status: pending
priority: {priority}
---

# New File Detected: {source_file.name}

## File Information
- **Name:** {source_file.name}
- **Size:** {file_size:,} bytes ({self.format_size(file_size)})
- **Type:** {file_extension or 'No extension'}
- **Detected:** {timestamp}
- **Location:** Inbox

## File Details
- **Extension:** {file_extension or 'none'}
- **Priority:** {priority}
- **Status:** Pending processing

## Suggested Actions
- [ ] Review file contents
- [ ] Determine purpose/category
- [ ] Process according to file type
- [ ] Archive to appropriate location
- [ ] Update dashboard

## Processing Notes
Add notes here about actions taken on this file.

---

*Task created by Filesystem Watcher*
*Timestamp: {timestamp}*
"""

        # Write task file
        task_path.write_text(task_content, encoding='utf-8')

        # Log the action
        self.log_action(source_file.name, task_filename)

    def determine_priority(self, filename: str, extension: str) -> str:
        """
        Determine task priority based on filename and extension.

        Args:
            filename: Name of the file
            extension: File extension

        Returns:
            Priority level (high, medium, low)
        """
        filename_lower = filename.lower()

        # High priority keywords
        high_priority_keywords = ['urgent', 'asap', 'critical', 'important', 'invoice', 'payment']
        if any(keyword in filename_lower for keyword in high_priority_keywords):
            return 'high'

        # High priority file types
        high_priority_extensions = ['.pdf', '.docx', '.xlsx', '.doc', '.xls']
        if extension in high_priority_extensions:
            return 'medium'

        # Default priority
        return 'medium'

    def format_size(self, bytes_size: int) -> str:
        """
        Format file size in human-readable format.

        Args:
            bytes_size: Size in bytes

        Returns:
            Formatted size string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

    def log_action(self, source_filename: str, task_filename: str):
        """
        Log the watcher action to the logs folder.

        Args:
            source_filename: Original file name
            task_filename: Created task file name
        """
        import json

        log_date = datetime.now().strftime('%Y-%m-%d')
        log_file = LOGS_PATH / f'actions_{log_date}.json'

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "file_detected",
            "details": {
                "source": source_filename,
                "task_created": task_filename,
                "watcher": "filesystem_watcher"
            }
        }

        try:
            # Read existing logs or create new list
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            else:
                logs = []

            # Append new entry
            logs.append(log_entry)

            # Write back
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error(f"Error writing to action log: {e}")


def main():
    """
    Main entry point for the filesystem watcher.
    """
    logger.info("=" * 60)
    logger.info("Personal AI Employee - Filesystem Watcher")
    logger.info("=" * 60)
    logger.info(f"Vault: {VAULT_PATH}")
    logger.info(f"Watching: {INBOX_PATH}")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)

    # Ensure inbox directory exists
    INBOX_PATH.mkdir(exist_ok=True)
    NEEDS_ACTION_PATH.mkdir(exist_ok=True)

    # Create event handler
    event_handler = InboxWatcherHandler(VAULT_PATH)

    # Create observer
    observer = Observer()
    observer.schedule(event_handler, str(INBOX_PATH), recursive=False)

    # Start watching
    observer.start()
    logger.info("✓ Watcher started successfully")
    logger.info(f"  Drop files in: {INBOX_PATH}")
    logger.info(f"  Tasks created in: {NEEDS_ACTION_PATH}")
    logger.info("")

    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("\n" + "=" * 60)
        logger.info("Stopping watcher...")
        observer.stop()
        observer.join()
        logger.info("✓ Watcher stopped successfully")
        logger.info("=" * 60)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Watcher error: {e}")
        observer.stop()
        observer.join()
        sys.exit(1)


if __name__ == "__main__":
    main()
