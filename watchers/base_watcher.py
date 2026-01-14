#!/usr/bin/env python3
"""
Base Watcher Class for Personal AI Employee

Abstract base class that all watchers inherit from. Provides common
functionality for logging, folder creation, run loop, and exception handling.

All watcher implementations should inherit from this class and implement
the abstract methods: check_for_updates() and create_action_file().

Author: Personal AI Employee Project
Created: 2026-01-12
"""

import time
import logging
import sys
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Any
import json


class BaseWatcher(ABC):
    """
    Abstract base class for all watcher implementations.

    Provides common functionality:
    - Logging setup with file and console handlers
    - Folder creation and validation
    - Main run loop with exception handling
    - Configurable check interval
    - Processed items tracking
    - Action logging to JSON files

    Subclasses must implement:
    - check_for_updates(): Check external source for new items
    - create_action_file(): Create task file in Needs_Action folder
    """

    def __init__(
        self,
        vault_path: str,
        check_interval: int = 60,
        watcher_name: Optional[str] = None
    ):
        """
        Initialize the base watcher.

        Args:
            vault_path: Absolute path to the Obsidian vault root
            check_interval: Time in seconds between checks (default: 60)
            watcher_name: Name of the watcher for logging (default: class name)
        """
        # Set up paths
        self.vault_path = Path(vault_path).resolve()
        self.needs_action = self.vault_path / 'Needs_Action'
        self.logs_path = self.vault_path / 'Logs'
        self.check_interval = check_interval
        self.watcher_name = watcher_name or self.__class__.__name__

        # Validate vault path exists
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")

        # Create required directories
        self._create_directories()

        # Set up logging
        self.logger = self._setup_logging()

        # Track processed items to avoid duplicates
        self.processed_items = set()
        self._load_processed_items()

        # Statistics
        self.start_time = datetime.now()
        self.total_checks = 0
        self.total_items_processed = 0
        self.total_errors = 0

        self.logger.info(f"{self.watcher_name} initialized")
        self.logger.info(f"  Vault: {self.vault_path}")
        self.logger.info(f"  Output: {self.needs_action}")
        self.logger.info(f"  Check interval: {self.check_interval}s")

    def _create_directories(self):
        """Create required directories if they don't exist."""
        directories = [
            self.needs_action,
            self.logs_path,
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> logging.Logger:
        """
        Set up logging with both file and console handlers.

        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(self.watcher_name)
        logger.setLevel(logging.INFO)

        # Avoid duplicate handlers if logger already configured
        if logger.handlers:
            return logger

        # Create formatters
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File handler - daily log file
        log_filename = f'{self.watcher_name.lower()}_{datetime.now().strftime("%Y-%m-%d")}.log'
        file_handler = logging.FileHandler(
            self.logs_path / log_filename,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def _load_processed_items(self):
        """Load previously processed item IDs from persistent storage."""
        processed_file = self.logs_path / f'{self.watcher_name.lower()}_processed.json'

        if processed_file.exists():
            try:
                with open(processed_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.processed_items = set(data.get('items', []))
                    self.logger.info(f"Loaded {len(self.processed_items)} processed items from cache")
            except Exception as e:
                self.logger.error(f"Error loading processed items: {e}")
                self.processed_items = set()

    def _save_processed_items(self):
        """Save processed item IDs to persistent storage."""
        processed_file = self.logs_path / f'{self.watcher_name.lower()}_processed.json'

        try:
            data = {
                'watcher': self.watcher_name,
                'last_updated': datetime.now().isoformat(),
                'count': len(self.processed_items),
                'items': list(self.processed_items)
            }

            with open(processed_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error saving processed items: {e}")

    def mark_as_processed(self, item_id: str):
        """
        Mark an item as processed to avoid duplicate processing.

        Args:
            item_id: Unique identifier for the processed item
        """
        self.processed_items.add(item_id)
        self._save_processed_items()

    def is_processed(self, item_id: str) -> bool:
        """
        Check if an item has already been processed.

        Args:
            item_id: Unique identifier to check

        Returns:
            True if item has been processed, False otherwise
        """
        return item_id in self.processed_items

    def log_action(
        self,
        action_type: str,
        details: dict,
        task_filename: Optional[str] = None
    ):
        """
        Log a watcher action to the daily action log.

        Args:
            action_type: Type of action (e.g., 'email_detected', 'file_detected')
            details: Dictionary with action details
            task_filename: Name of the created task file (optional)
        """
        log_date = datetime.now().strftime('%Y-%m-%d')
        log_file = self.logs_path / f'actions_{log_date}.json'

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "watcher": self.watcher_name,
            "action": action_type,
            "details": details
        }

        if task_filename:
            log_entry["task_file"] = task_filename

        try:
            # Read existing logs or create new list
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            else:
                logs = []

            # Append new entry
            logs.append(log_entry)

            # Write back
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error writing to action log: {e}")

    def get_statistics(self) -> dict:
        """
        Get watcher statistics.

        Returns:
            Dictionary with runtime statistics
        """
        runtime = datetime.now() - self.start_time

        return {
            'watcher': self.watcher_name,
            'start_time': self.start_time.isoformat(),
            'runtime_seconds': int(runtime.total_seconds()),
            'total_checks': self.total_checks,
            'items_processed': self.total_items_processed,
            'errors': self.total_errors,
            'check_interval': self.check_interval,
            'success_rate': (
                (self.total_checks - self.total_errors) / self.total_checks * 100
                if self.total_checks > 0 else 0
            )
        }

    @abstractmethod
    def check_for_updates(self) -> List[Any]:
        """
        Check external source for new items.

        This method must be implemented by subclasses to check their
        specific data source (Gmail, WhatsApp, filesystem, etc.) and
        return a list of new items to process.

        Returns:
            List of new items to process (format depends on watcher type)

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement check_for_updates()")

    @abstractmethod
    def create_action_file(self, item: Any) -> Optional[Path]:
        """
        Create a task file in Needs_Action folder for the given item.

        This method must be implemented by subclasses to create
        appropriately formatted task files for their specific item type.

        Args:
            item: Item to create task file for (format depends on watcher type)

        Returns:
            Path to the created task file, or None if creation failed

        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError("Subclasses must implement create_action_file()")

    def run(self):
        """
        Main monitoring loop.

        Continuously checks for updates, creates task files, and handles
        errors gracefully. Runs until interrupted by Ctrl+C.
        """
        self.logger.info("=" * 70)
        self.logger.info(f"{self.watcher_name} started")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info(f"Press Ctrl+C to stop")
        self.logger.info("=" * 70)

        try:
            while True:
                try:
                    # Increment check counter
                    self.total_checks += 1

                    # Check for new items
                    new_items = self.check_for_updates()

                    # Process each new item
                    if new_items:
                        self.logger.info(f"Found {len(new_items)} new item(s)")

                        for item in new_items:
                            try:
                                # Create task file
                                task_path = self.create_action_file(item)

                                if task_path:
                                    self.total_items_processed += 1
                                    self.logger.info(f"✓ Created task: {task_path.name}")

                            except Exception as e:
                                self.total_errors += 1
                                self.logger.error(f"Error creating task file: {e}", exc_info=True)

                    # Wait before next check
                    time.sleep(self.check_interval)

                except KeyboardInterrupt:
                    # Allow Ctrl+C to break the loop
                    raise

                except Exception as e:
                    # Log error but continue running
                    self.total_errors += 1
                    self.logger.error(f"Error in check cycle: {e}", exc_info=True)
                    self.logger.info(f"Waiting {self.check_interval}s before retry...")
                    time.sleep(self.check_interval)

        except KeyboardInterrupt:
            # Graceful shutdown
            self._shutdown()

    def _shutdown(self):
        """Perform graceful shutdown and display statistics."""
        self.logger.info("\n" + "=" * 70)
        self.logger.info(f"Stopping {self.watcher_name}...")

        # Display statistics
        stats = self.get_statistics()
        self.logger.info(f"Runtime: {stats['runtime_seconds']}s")
        self.logger.info(f"Total checks: {stats['total_checks']}")
        self.logger.info(f"Items processed: {stats['items_processed']}")
        self.logger.info(f"Errors: {stats['errors']}")
        self.logger.info(f"Success rate: {stats['success_rate']:.1f}%")

        # Save final state
        self._save_processed_items()

        self.logger.info(f"✓ {self.watcher_name} stopped successfully")
        self.logger.info("=" * 70)

        sys.exit(0)


# Example usage and testing
if __name__ == "__main__":
    # This will fail because BaseWatcher is abstract
    print("BaseWatcher is an abstract class and cannot be instantiated directly.")
    print("Subclasses must implement: check_for_updates() and create_action_file()")
    print("\nExample watchers that inherit from BaseWatcher:")
    print("  - GmailWatcher")
    print("  - WhatsAppWatcher")
    print("  - FilesystemWatcher")
