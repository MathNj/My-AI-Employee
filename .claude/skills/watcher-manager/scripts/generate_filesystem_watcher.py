#!/usr/bin/env python3
"""
Generate File System Watcher Script for Personal AI Employee

This script generates a complete filesystem watcher that monitors
the /Inbox folder and creates task files in /Needs_Action.
"""

from pathlib import Path
import sys


WATCHER_CODE = '''#!/usr/bin/env python3
"""
File System Watcher for Personal AI Employee

Monitors the Inbox folder and creates task files in Needs_Action
when new files are detected.
"""

import time
from pathlib import Path
from datetime import datetime
import shutil
import logging


# Configuration
VAULT_PATH = Path(__file__).parent.parent.resolve()
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"
CHECK_INTERVAL = 5  # seconds

# Setup logging
LOGS_PATH.mkdir(exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOGS_PATH / 'watcher.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FilesystemWatcher:
    """Monitor filesystem for new files and create action items"""

    def __init__(self, inbox_path, needs_action_path):
        self.inbox_path = Path(inbox_path)
        self.needs_action_path = Path(needs_action_path)
        self.processed_files = set()

        # Ensure directories exist
        self.inbox_path.mkdir(exist_ok=True)
        self.needs_action_path.mkdir(exist_ok=True)

    def check_for_new_files(self):
        """Check inbox for new files"""
        try:
            files = [f for f in self.inbox_path.iterdir() if f.is_file()]

            new_files = [f for f in files if f not in self.processed_files]

            return new_files
        except Exception as e:
            logger.error(f"Error checking for files: {e}")
            return []

    def create_action_file(self, source_file):
        """Create action file in Needs_Action folder"""
        try:
            timestamp = datetime.now().isoformat()
            file_size = source_file.stat().st_size

            # Create task file with metadata
            task_filename = f"FILE_{timestamp.replace(':', '-').replace('.', '-')}_{source_file.name}.md"
            task_path = self.needs_action_path / task_filename

            task_content = f"""---
type: file_drop
source_file: {source_file.name}
detected: {timestamp}
size_bytes: {file_size}
status: pending
priority: medium
---

# New File Detected: {source_file.name}

## File Information
- **Name:** {source_file.name}
- **Size:** {file_size:,} bytes
- **Detected:** {timestamp}
- **Location:** Inbox

## Suggested Actions
- [ ] Review file contents
- [ ] Determine purpose/category
- [ ] Process or archive
- [ ] Update dashboard

## Notes
Add notes about this file and any actions taken.
"""

            task_path.write_text(task_content, encoding='utf-8')
            logger.info(f"Created action file: {task_filename}")

            # Mark file as processed
            self.processed_files.add(source_file)

            return task_path

        except Exception as e:
            logger.error(f"Error creating action file for {source_file}: {e}")
            return None

    def run(self):
        """Main monitoring loop"""
        logger.info("Filesystem Watcher started")
        logger.info(f"Monitoring: {self.inbox_path}")
        logger.info(f"Output to: {self.needs_action_path}")
        logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
        logger.info("-" * 50)

        try:
            while True:
                new_files = self.check_for_new_files()

                for file in new_files:
                    logger.info(f"New file detected: {file.name}")
                    self.create_action_file(file)

                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("\\nWatcher stopped by user")
        except Exception as e:
            logger.error(f"Watcher error: {e}")
            raise


def main():
    """Entry point"""
    watcher = FilesystemWatcher(INBOX_PATH, NEEDS_ACTION_PATH)
    watcher.run()


if __name__ == "__main__":
    main()
'''


def generate_watcher(output_path=None):
    """
    Generate filesystem watcher script

    Args:
        output_path: Where to write the watcher script (defaults to watchers/filesystem_watcher.py)
    """
    if output_path is None:
        # Default to watchers/ folder in current directory
        output_path = Path.cwd() / 'watchers' / 'filesystem_watcher.py'
    else:
        output_path = Path(output_path)

    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write the watcher code
    output_path.write_text(WATCHER_CODE)

    # Make executable on Unix systems
    try:
        import os
        os.chmod(output_path, 0o755)
    except Exception:
        pass  # Windows doesn't need this

    print(f"Filesystem watcher generated: {output_path}")
    print()
    print("To use the watcher:")
    print(f"1. Review the script: {output_path}")
    print(f"2. Start the watcher: python {output_path}")
    print("3. Drop files in /Inbox to test")
    print("4. Check /Needs_Action for created task files")

    return output_path


def main():
    """Main entry point"""
    output_path = sys.argv[1] if len(sys.argv) > 1 else None

    print("Generating Filesystem Watcher...")
    print("-" * 50)

    result = generate_watcher(output_path)

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
