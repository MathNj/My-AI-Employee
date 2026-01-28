#!/usr/bin/env python3
"""
Odoo Structured Logging Module

Provides structured JSON logging for better parsing and analysis.
Supports multiple outputs, log rotation, and contextual logging.

Usage:
    from odoo_structured_log import get_logger

    logger = get_logger("my_module")
    logger.info("Processing invoice", invoice_id=123, amount=1500.00)
"""

from __future__ import annotations

import sys
import json
import logging
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union
from contextlib import contextmanager
from functools import wraps
import traceback

try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    # Fallback implementation
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }

            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)

            # Add extra fields
            if hasattr(record, 'extra_fields'):
                log_entry.update(record.extra_fields)

            return json.dumps(log_entry)

    jsonlogger = type('jsonlogger', (), {'JsonFormatter': JsonFormatter})


# =============================================================================
# Structured Logger
# =============================================================================

class StructuredLogger:
    """Logger with structured JSON output and contextual fields"""

    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        self._context: Dict[str, Any] = {}
        self._lock = threading.Lock()

        # Clear existing handlers
        self.logger.handlers.clear()

    def add_handler(self, handler: logging.Handler):
        """Add a handler to the logger"""
        self.logger.addHandler(handler)

    def configure(self, output_config: list, log_dir: Path = None):
        """
        Configure logger from output config.

        Args:
            output_config: List of output configs from YAML
            log_dir: Base directory for log files
        """
        for output in output_config:
            output_type = output.get('type')

            if output_type == 'console':
                handler = self._create_console_handler(output)
            elif output_type == 'file':
                handler = self._create_file_handler(output, log_dir)
            else:
                continue

            self.add_handler(handler)

    def _create_console_handler(self, config: Dict) -> logging.Handler:
        """Create console handler"""
        import sys

        handler = logging.StreamHandler(sys.stdout)

        if config.get('format') == 'json' or self.logger.level == logging.DEBUG:
            formatter = jsonlogger.JsonFormatter(
                '%(asctime)s %(level)s %(name)s %(message)s'
            )
        else:
            import colorlog
            formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )

        handler.setFormatter(formatter)
        return handler

    def _create_file_handler(self, config: Dict, log_dir: Path = None) -> logging.Handler:
        """Create rotating file handler"""
        from logging.handlers import RotatingFileHandler

        file_path = Path(config.get('path', './Logs/odoo_sync.log'))

        if log_dir and not file_path.is_absolute():
            file_path = log_dir / file_path

        file_path.parent.mkdir(parents=True, exist_ok=True)

        max_bytes = self._parse_size(config.get('max_size', '10MB'))
        backup_count = config.get('backup_count', 5)

        handler = RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )

        # Use JSON format for files
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(level)s %(name)s %(message)s'
        )
        handler.setFormatter(formatter)

        return handler

    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper()
        multipliers = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3}

        for suffix, multiplier in multipliers.items():
            if size_str.endswith(suffix):
                return int(size_str[:-len(suffix)]) * multiplier

        return int(size_str)

    # Contextual logging methods
    @contextmanager
    def context(self, **kwargs):
        """Add contextual fields to all log messages in this block"""
        with self._lock:
            old_context = self._context.copy()
            self._context.update(kwargs)

        try:
            yield
        finally:
            with self._lock:
                self._context = old_context

    def bind(self, **kwargs) -> 'StructuredLogger':
        """Return a new logger with bound context"""
        new_logger = StructuredLogger(self.logger.name, self.logger.level)
        new_logger._context = {**self._context, **kwargs}
        return new_logger

    def _log(self, level: int, msg: str, **kwargs):
        """Internal logging method"""
        extra = {'extra_fields': {**self._context, **kwargs}}
        self.logger.log(level, msg, extra=extra)

    def debug(self, msg: str, **kwargs):
        self._log(logging.DEBUG, msg, **kwargs)

    def info(self, msg: str, **kwargs):
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs):
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs):
        self._log(logging.ERROR, msg, **kwargs)

    def critical(self, msg: str, **kwargs):
        self._log(logging.CRITICAL, msg, **kwargs)

    def exception(self, msg: str, **kwargs):
        """Log exception with traceback"""
        extra = {'extra_fields': {**self._context, **kwargs}}
        self.logger.error(msg, exc_info=True, extra=extra)


# =============================================================================
# Logger Registry
# =============================================================================

_logger_cache: Dict[str, StructuredLogger] = {}
_logger_lock = threading.Lock()
_config_loaded = False


def get_logger(name: str, level: str = "INFO") -> StructuredLogger:
    """Get or create a structured logger"""
    with _logger_lock:
        if name not in _logger_cache:
            _logger_cache[name] = StructuredLogger(name, level)
        return _logger_cache[name]


def configure_loggers(config: Dict, log_dir: Path = None):
    """Configure all loggers from config"""
    global _config_loaded

    root_config = config.get('logging', {})
    level = root_config.get('level', 'INFO')
    format_type = root_config.get('format', 'text')
    outputs = root_config.get('output', [])

    for logger_name, logger in _logger_cache.items():
        logger.logger.setLevel(getattr(logging, level.upper()))
        logger.configure(outputs, log_dir)

    _config_loaded = True


# =============================================================================
# Utility Decorators
# =============================================================================

def log_execution(logger: Optional[StructuredLogger] = None,
                  level: str = "info",
                  log_args: bool = True,
                  log_result: bool = False,
                  log_exceptions: bool = True):
    """
    Decorator to log function execution.

    Usage:
        @log_execution()
        def my_function(arg1, arg2):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__module__)
            func_name = func.__name__

            log_data = {
                "function": func_name,
                "module": func.__module__
            }

            if log_args:
                log_data["args"] = str(args)[:200]  # Truncate long args
                log_data["kwargs"] = list(kwargs.keys())

            getattr(_logger, level)(f"Calling {func_name}", **log_data)

            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start

                completion_data = {
                    "function": func_name,
                    "duration_seconds": round(duration, 3)
                }

                if log_result:
                    completion_data["result"] = str(result)[:200]

                getattr(_logger, level)(f"Completed {func_name}", **completion_data)
                return result

            except Exception as e:
                duration = time.time() - start
                error_data = {
                    "function": func_name,
                    "duration_seconds": round(duration, 3),
                    "error_type": type(e).__name__,
                    "error_message": str(e)
                }

                if log_exceptions:
                    _logger.exception(f"Error in {func_name}", **error_data)
                else:
                    _logger.error(f"Error in {func_name}", **error_data)

                raise

        return wrapper
    return decorator


def log_errors(logger: Optional[StructuredLogger] = None):
    """Decorator to log only exceptions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            _logger = logger or get_logger(func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                _logger.error(
                    f"Error in {func.__name__}",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    function=func.__name__
                )
                raise
        return wrapper
    return decorator


# =============================================================================
# Timing Context
# =============================================================================

@contextmanager
def log_duration(logger: StructuredLogger, operation: str, level: str = "debug"):
    """Context manager to log operation duration"""
    start = time.time()
    logger.debug(f"Starting: {operation}")
    try:
        yield
    finally:
        duration = time.time() - start
        getattr(logger, level)(
            f"Finished: {operation}",
            operation=operation,
            duration_seconds=round(duration, 3)
        )


# =============================================================================
# Progress Tracking
# =============================================================================

class ProgressLogger:
    """Logger for long-running operations"""

    def __init__(self, logger: StructuredLogger, operation: str,
                 total: int, log_interval: int = 10):
        self.logger = logger
        self.operation = operation
        self.total = total
        self.log_interval = log_interval
        self.current = 0
        self.start_time = time.time()
        self.last_log_time = time.time()
        self.last_log_count = 0

    def update(self, n: int = 1):
        """Update progress"""
        self.current += n

        # Log at intervals or when complete
        now = time.time()
        elapsed_since_log = now - self.last_log_time
        progress_pct = (self.current / self.total) * 100

        should_log = (
            self.current >= self.total or
            progress_pct >= 100 or
            (self.current > 0 and self.current % self.log_interval == 0) or
            elapsed_since_log >= 5  # Log at least every 5 seconds
        )

        if should_log:
            rate = (self.current - self.last_log_count) / elapsed_since_log if elapsed_since_log > 0 else 0
            eta = (self.total - self.current) / rate if rate > 0 else 0

            self.logger.info(
                f"Progress: {self.operation}",
                operation=self.operation,
                current=self.current,
                total=self.total,
                progress_percent=round(progress_pct, 1),
                rate_per_second=round(rate, 2),
                eta_seconds=round(eta, 1),
                elapsed_seconds=round(now - self.start_time, 1)
            )

            self.last_log_time = now
            self.last_log_count = self.current

    def complete(self):
        """Mark operation as complete"""
        duration = time.time() - self.start_time
        self.logger.info(
            f"Completed: {self.operation}",
            operation=self.operation,
            total=self.total,
            duration_seconds=round(duration, 2),
            avg_rate=round(self.total / duration, 2) if duration > 0 else 0
        )


# =============================================================================
# Standalone Test
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test structured logging')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                       help='Log format')
    parser.add_argument('--level', default='INFO',
                       help='Log level')

    args = parser.parse_args()

    # Get logger
    logger = get_logger("test", args.level)

    # Configure handler
    handler = logging.StreamHandler(sys.stdout)
    if args.format == 'json':
        handler.setFormatter(jsonlogger.JsonFormatter('%(message)s'))
    else:
        handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'))
    logger.add_handler(handler)

    # Test logging
    logger.info("Application starting", version="1.0.0", environment="test")

    # Test with context
    with logger.context(request_id="12345", user_id="abc"):
        logger.info("Processing request")

        logger.info("Database query", query="SELECT * FROM invoices", duration_ms=45)

        # Test progress
        progress = ProgressLogger(logger, "Syncing invoices", total=100)
        for i in range(0, 101, 10):
            progress.update(10)
        progress.complete()

    # Test error
    try:
        1 / 0
    except Exception:
        logger.exception("Division by zero occurred")

    logger.info("Application shutting down")
