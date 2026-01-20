"""
Shared Logging Module for Ad Monitoring System

Provides thread-safe, buffered logging to Excel files with:
- File locking to prevent race conditions
- In-memory buffering to minimize disk I/O
- Atomic writes via temp file + rename
- Proper error handling with status returns
"""

import os
import fcntl
import tempfile
import shutil
import pandas as pd
from datetime import datetime
from typing import Optional, List, Dict


class AdEventLogger:
    """Thread-safe logger for ad events with buffering and file locking."""

    def __init__(self, log_file_path: str):
        """
        Initialize the logger.

        Args:
            log_file_path: Path to the Excel log file (relative or absolute)
        """
        self.log_file_path = log_file_path
        self._buffer: List[Dict] = []
        self._lock_file_path = f"{log_file_path}.lock"

    def log_event(self, ad_name: str, url: str, event: str, action: str, product_price: float = 0.0) -> bool:
        """
        Log a single event to the internal buffer with product price.

        Args:
            ad_name: Name of the ad
            url: URL associated with the ad
            event: Event description
            action: Action taken
            product_price: Product price in USD (NEW FIELD)

        Returns:
            True if event was buffered successfully, False otherwise
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._buffer.append({
                "Timestamp": timestamp,
                "Ad Name": ad_name,
                "URL": url,
                "Event": event,
                "Action": action,
                "Product_Price": product_price  # NEW FIELD
            })
            print(f"Buffered: {event} - {action} for {ad_name} (Price: ${product_price})")
            return True
        except Exception as e:
            print(f"Error buffering event: {e}")
            return False

    def flush(self) -> bool:
        """
        Write all buffered events to the Excel file atomically with file locking.

        Returns:
            True if flush was successful, False otherwise
        """
        if not self._buffer:
            return True  # Nothing to flush

        # Create lock file
        lock_fd = None
        try:
            # Create/open lock file
            lock_fd = open(self._lock_file_path, 'w')

            # Acquire exclusive lock (will block until available)
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)

            # Read existing data if file exists
            existing_df = pd.DataFrame()
            if os.path.exists(self.log_file_path):
                try:
                    existing_df = pd.read_excel(self.log_file_path)
                except Exception as e:
                    print(f"Warning: Could not read existing log file: {e}")

            # Combine existing data with new entries
            buffer_df = pd.DataFrame(self._buffer)
            combined_df = pd.concat([existing_df, buffer_df], ignore_index=True)

            # Atomic write: write to temp file, then rename
            temp_fd, temp_path = tempfile.mkstemp(
                suffix=".xlsx",
                dir=os.path.dirname(self.log_file_path) or "."
            )
            os.close(temp_fd)

            try:
                combined_df.to_excel(temp_path, index=False)

                # On Windows, we need to remove the target first
                if os.name == 'nt' and os.path.exists(self.log_file_path):
                    os.remove(self.log_file_path)

                # Atomic rename
                os.rename(temp_path, self.log_file_path)

                print(f"Flushed {len(self._buffer)} events to {self.log_file_path}")
                self._buffer.clear()
                return True

            except Exception as e:
                # Clean up temp file if rename failed
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                raise e

        except IOError as e:
            print(f"Error acquiring lock or writing log: {e}")
            return False
        except Exception as e:
            print(f"Error flushing log buffer: {e}")
            return False
        finally:
            # Release lock and close lock file
            if lock_fd:
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
                    # Try to remove lock file
                    if os.path.exists(self._lock_file_path):
                        os.remove(self._lock_file_path)
                except:
                    pass

    def get_buffer_size(self) -> int:
        """Return the number of buffered events."""
        return len(self._buffer)

    def has_pending_events(self) -> bool:
        """Check if there are pending events in the buffer."""
        return len(self._buffer) > 0


# Global logger instances (one per region)
_loggers: Dict[str, AdEventLogger] = {}


def get_logger(log_file_path: str) -> AdEventLogger:
    """
    Get or create a logger instance for the specified log file.

    Args:
        log_file_path: Path to the Excel log file

    Returns:
        AdEventLogger instance
    """
    # Normalize the path to use as a key
    abs_path = os.path.abspath(log_file_path)

    if abs_path not in _loggers:
        _loggers[abs_path] = AdEventLogger(log_file_path)

    return _loggers[abs_path]


def log_ad_event(ad_name: str, url: str, event: str, action: str, product_price: float = 0.0, log_file_path: str = "Ad_Status_Log.xlsx") -> bool:
    """
    Convenience function to log an event with product price (for backward compatibility).

    Note: This only buffers the event. You must call flush_logs() to write to disk.

    Args:
        ad_name: Name of the ad
        url: URL associated with the ad
        event: Event description
        action: Action taken
        product_price: Product price in USD (NEW PARAMETER)
        log_file_path: Path to the log file

    Returns:
        True if event was buffered successfully
    """
    logger = get_logger(log_file_path)
    return logger.log_event(ad_name, url, event, action, product_price)


def flush_logs(log_file_path: str = "Ad_Status_Log.xlsx") -> bool:
    """
    Flush all buffered events to disk.

    Args:
        log_file_path: Path to the log file

    Returns:
        True if flush was successful
    """
    logger = get_logger(log_file_path)
    return logger.flush()


def flush_all_logs() -> bool:
    """
    Flush all buffered logs for all regions.

    Returns:
        True if all flushes were successful
    """
    all_success = True
    for logger in _loggers.values():
        if not logger.flush():
            all_success = False
    return all_success
