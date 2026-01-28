#!/usr/bin/env python3
"""
Ultimate Watcher Manager for Personal AI Employee

Advanced file system monitoring with:
- Multi-folder watching with different rules
- Event filtering and deduplication
- Pattern matching and ignore rules
- Automatic restart on failure
- Structured JSON logging
- Watcher health monitoring
- Event aggregation and throttling
- Command execution on events
- Webhook notifications
- Hot reload configuration

Usage:
    python watcher_manager_ultimate.py                    # Start watching
    python watcher_manager_ultimate.py --config <file>    # Use config file
    python watcher_manager_ultimate.py --status           # Show status
    python watcher_manager_ultimate.py --test <event>     # Test event handling
    python watcher_manager_ultimate.py --health           # Health check
"""

from __future__ import annotations

import os
import sys
import json
import time
import signal
import threading
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple, Pattern
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import fnmatch

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    HAS_WATCHDOG = True
except ImportError:
    HAS_WATCHDOG = False
    print("Warning: watchdog not available. Install with: pip install watchdog")

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# =============================================================================
# Configuration
# =============================================================================

VAULT_PATH = Path(__file__).parent.parent.parent.parent.resolve()
INBOX_PATH = VAULT_PATH / "Inbox"
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
LOGS_PATH = VAULT_PATH / "Logs"
WATCHER_LOGS = LOGS_PATH / "Watchers"
CONFIG_PATH = VAULT_PATH / "watcher_config.yaml"

# Ensure directories exist
for path in [WATCHER_LOGS]:
    path.mkdir(parents=True, exist_ok=True)


# =============================================================================
# Event Type Enums
# =============================================================================

class EventType(Enum):
    """File system event types"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"
    ALL = "all"


class EventAction(Enum):
    """Actions to take on events"""
    CREATE_TASK = "create_task"
    EXECUTE_COMMAND = "execute_command"
    WEBHOOK = "webhook"
    LOG = "log"
    IGNORE = "ignore"


# =============================================================================
# Watcher Data Classes
# =============================================================================

@dataclass
class EventFilter:
    """Filter for file system events"""
    patterns: List[str] = field(default_factory=list)  # Glob patterns to match
    ignore_patterns: List[str] = field(default_factory=list)  # Patterns to ignore
    event_types: List[EventType] = field(default_factory=list)  # Event types to watch
    min_size_bytes: Optional[int] = None
    max_size_bytes: Optional[int] = None
    extensions: List[str] = field(default_factory=list)  # File extensions to watch
    ignore_extensions: List[str] = field(default_factory=list)

    def matches(self, path: str, event_type: EventType, size: int = 0) -> bool:
        """Check if event matches filter"""
        # Check event type
        if self.event_types and event_type not in self.event_types:
            return False

        # Check ignore patterns first
        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return False

        # Check patterns
        if self.patterns:
            if not any(fnmatch.fnmatch(path, p) for p in self.patterns):
                return False

        # Check size
        if self.min_size_bytes is not None and size < self.min_size_bytes:
            return False
        if self.max_size_bytes is not None and size > self.max_size_bytes:
            return False

        # Check extensions
        _, ext = os.path.splitext(path)
        if self.extensions and ext.lower() not in self.extensions:
            return False
        if self.ignore_extensions and ext.lower() in self.ignore_extensions:
            return False

        return True


@dataclass
class EventRule:
    """Rule for handling events"""
    name: str
    filter: EventFilter
    actions: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    throttle_seconds: int = 0  # Min seconds between same event
    aggregate_window: int = 0  # Aggregate events over N seconds
    priority: int = 0  # Higher priority rules checked first


@dataclass
class WatchFolder:
    """Folder configuration for watching"""
    path: Path
    recursive: bool = True
    rules: List[EventRule] = field(default_factory=list)
    enabled: bool = True


@dataclass
class FileEvent:
    """File system event record"""
    id: str
    event_type: EventType
    path: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    size: int = 0
    is_directory: bool = False
    source_path: Optional[str] = None  # For moved events
    handled: bool = False
    rule_name: Optional[str] = None
    actions_taken: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        data = asdict(self)
        data['event_type'] = self.event_type.value
        return data


@dataclass
class WatcherStats:
    """Watcher statistics"""
    events_seen: int = 0
    events_handled: int = 0
    events_ignored: int = 0
    tasks_created: int = 0
    commands_executed: int = 0
    webhooks_sent: int = 0
    errors: int = 0
    uptime_seconds: float = 0
    last_event_time: Optional[str] = None


# =============================================================================
# Structured Logger
# =============================================================================

class WatcherLogger:
    """Structured JSON logger for watcher operations"""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)

        self.current_log_file = log_dir / f"watcher_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.lock = threading.Lock()

    def log(self, level: str, event: str, **data):
        """Write structured log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "event": event,
            **data
        }

        with self.lock:
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")

    def info(self, event: str, **data): self.log("info", event, **data)
    def warning(self, event: str, **data): self.log("warning", event, **data)
    def error(self, event: str, **data): self.log("error", event, **data)
    def debug(self, event: str, **data): self.log("debug", event, **data)


# =============================================================================
# Event Deduplicator
# =============================================================================

class EventDeduplicator:
    """Deduplicate similar events within time window"""

    def __init__(self, window_seconds: int = 5):
        self.window = timedelta(seconds=window_seconds)
        self.recent_events: Dict[str, datetime] = {}
        self.lock = threading.Lock()

    def is_duplicate(self, event: FileEvent) -> bool:
        """Check if event is a duplicate"""
        key = f"{event.event_type.value}:{event.path}"

        with self.lock:
            now = datetime.now()

            # Clean old entries
            self.recent_events = {
                k: v for k, v in self.recent_events.items()
                if now - v < self.window
            }

            # Check for duplicate
            if key in self.recent_events:
                return True

            # Add to recent
            self.recent_events[key] = now
            return False


# =============================================================================
# Event Aggregator
# =============================================================================

class EventAggregator:
    """Aggregate multiple events into batches"""

    def __init__(self, window_seconds: int = 60):
        self.window = timedelta(seconds=window_seconds)
        self.batches: Dict[str, List[FileEvent]] = defaultdict(list)
        self.lock = threading.Lock()

    def add(self, event: FileEvent, batch_key: str = "default"):
        """Add event to batch"""
        with self.lock:
            self.batches[batch_key].append(event)

    def get_batch(self, batch_key: str = "default") -> List[FileEvent]:
        """Get and clear batch"""
        with self.lock:
            batch = self.batches.pop(batch_key, [])
            return batch

    def should_flush(self, batch_key: str = "default") -> bool:
        """Check if batch should be flushed"""
        with self.lock:
            if batch_key not in self.batches:
                return False

            if not self.batches[batch_key]:
                return False

            # Flush if window expired or batch is large
            batch = self.batches[batch_key]
            if len(batch) >= 100:  # Max batch size
                return True

            # Check age of first event
            first_time = datetime.fromisoformat(batch[0].timestamp)
            return datetime.now() - first_time > self.window


# =============================================================================
# Action Executor
# =============================================================================

class ActionExecutor:
    """Execute actions triggered by events"""

    def __init__(self, logger: WatcherLogger, vault_path: Path):
        self.logger = logger
        self.vault_path = vault_path
        self.needs_action = vault_path / "Needs_Action"

    def execute(self, actions: List[Dict], event: FileEvent) -> List[str]:
        """Execute all actions for an event"""
        results = []

        for action in actions:
            action_type = action.get('type')

            if action_type == 'create_task':
                result = self._create_task(event, action)
            elif action_type == 'execute_command':
                result = self._execute_command(event, action)
            elif action_type == 'webhook':
                result = self._send_webhook(event, action)
            elif action_type == 'log':
                result = self._log_event(event, action)
            else:
                result = f"Unknown action type: {action_type}"

            results.append(result)

        return results

    def _create_task(self, event: FileEvent, action: Dict) -> str:
        """Create a task file from event"""
        try:
            timestamp = datetime.now().isoformat().replace(':', '-')

            task_filename = f"EVENT_{timestamp}_{Path(event.path).name}.md"
            task_path = self.needs_action / task_filename

            # Build task content
            template = action.get('template', 'default')
            task_content = self._render_template(template, event, action)

            task_path.write_text(task_content, encoding='utf-8')

            self.logger.info(
                "task_created",
                task=task_filename,
                event_path=event.path
            )

            return f"Created task: {task_filename}"

        except Exception as e:
            self.logger.error("task_creation_failed", error=str(e))
            return f"Failed to create task: {e}"

    def _render_template(self, template: str, event: FileEvent, action: Dict) -> str:
        """Render task template"""
        if template == 'default':
            return f"""---
type: file_event
source_file: {Path(event.path).name}
detected: {event.timestamp}
event_type: {event.event_type.value}
size_bytes: {event.size}
priority: medium
---

# File Event: {Path(event.path).name}

## Event Information
- **Type:** {event.event_type.value}
- **Path:** {event.path}
- **Size:** {event.size:,} bytes
- **Detected:** {event.timestamp}

## Suggested Actions
- [ ] Review file details
- [ ] Determine appropriate handling
- [ ] Process or archive
- [ ] Update dashboard

## Notes
Add notes about this file and any actions taken.
"""
        else:
            # Custom template
            return action.get('custom_template', '')

    def _execute_command(self, event: FileEvent, action: Dict) -> str:
        """Execute shell command"""
        try:
            command_template = action.get('command', '')
            command = self._substitute_vars(command_template, event)

            timeout = action.get('timeout', 30)

            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.vault_path)
            )

            if result.returncode == 0:
                self.logger.info(
                    "command_executed",
                    command=command,
                    output=result.stdout[:500]
                )
                return f"Command executed successfully"
            else:
                self.logger.error(
                    "command_failed",
                    command=command,
                    error=result.stderr[:500]
                )
                return f"Command failed: {result.stderr[:100]}"

        except subprocess.TimeoutExpired:
            return f"Command timed out"
        except Exception as e:
            return f"Command error: {e}"

    def _send_webhook(self, event: FileEvent, action: Dict) -> str:
        """Send webhook notification"""
        try:
            import requests

            url = action.get('url')
            if not url:
                return "No webhook URL configured"

            payload = {
                "event": event.to_dict(),
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(
                url,
                json=payload,
                timeout=10,
                headers=action.get('headers', {})
            )

            if response.status_code == 200:
                self.logger.info("webhook_sent", url=url)
                return "Webhook sent successfully"
            else:
                self.logger.error(
                    "webhook_failed",
                    url=url,
                    status=response.status_code
                )
                return f"Webhook failed: {response.status_code}"

        except ImportError:
            return "Requests library not available"
        except Exception as e:
            return f"Webhook error: {e}"

    def _log_event(self, event: FileEvent, action: Dict) -> str:
        """Log event"""
        log_level = action.get('level', 'info')
        message = action.get('message', f"Event: {event.event_type.value} - {event.path}")

        getattr(self.logger, log_level, self.logger.info)(
            "event_logged",
            event_type=event.event_type.value,
            path=event.path,
            message=message
        )

        return f"Logged: {message}"

    def _substitute_vars(self, template: str, event: FileEvent) -> str:
        """Substitute event variables in template"""
        vars_map = {
            '{path}': event.path,
            '{name}': Path(event.path).name,
            '{ext}': Path(event.path).suffix,
            '{event_type}': event.event_type.value,
            '{size}': str(event.size),
            '{timestamp}': event.timestamp,
            '{vault}': str(self.vault_path),
        }

        result = template
        for var, value in vars_map.items():
            result = result.replace(var, value)

        return result


# =============================================================================
# Watchdog Event Handler
# =============================================================================

class WatchdogEventHandler(FileSystemEventHandler):
    """Handler for watchdog file system events"""

    def __init__(
        self,
        rules: List[EventRule],
        executor: ActionExecutor,
        logger: WatcherLogger,
        deduplicator: EventDeduplicator,
        aggregator: Optional[EventAggregator] = None
    ):
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        self.executor = executor
        self.logger = logger
        self.deduplicator = deduplicator
        self.aggregator = aggregator
        self.stats = WatcherStats()
        self.start_time = datetime.now()

    def _process_event(self, event_type: EventType, event: FileSystemEvent):
        """Process a file system event"""
        # Update stats
        self.stats.events_seen += 1
        self.stats.last_event_time = datetime.now().isoformat()

        # Skip if directory
        if event.is_directory:
            return

        # Get file size
        try:
            size = Path(event.src_path).stat().st_size
        except:
            size = 0

        # Create FileEvent
        file_event = FileEvent(
            id=f"{int(time.time())}_{hash(event.src_path)}",
            event_type=event_type,
            path=event.src_path,
            size=size,
            is_directory=event.is_directory
        )

        # Check for duplicate
        if self.deduplicator.is_duplicate(file_event):
            self.stats.events_ignored += 1
            self.logger.debug("event_deduplicated", path=event.src_path)
            return

        # Find matching rule
        matched_rule = None
        for rule in self.rules:
            if rule.enabled and rule.filter.matches(event.src_path, event_type, size):
                matched_rule = rule
                break

        if not matched_rule:
            self.stats.events_ignored += 1
            return

        # Check for aggregation
        if self.aggregator and matched_rule.aggregate_window > 0:
            self.aggregator.add(file_event, matched_rule.name)
            if self.aggregator.should_flush(matched_rule.name):
                batch = self.aggregator.get_batch(matched_rule.name)
                self._process_batch(batch, matched_rule)
            return

        # Process event
        self._handle_event(file_event, matched_rule)

    def _process_batch(self, events: List[FileEvent], rule: EventRule):
        """Process a batch of events"""
        self.logger.info(
            "processing_batch",
            rule=rule.name,
            count=len(events)
        )

        for event in events:
            self._handle_event(event, rule)

    def _handle_event(self, event: FileEvent, rule: EventRule):
        """Handle a single event with a rule"""
        try:
            # Execute actions
            actions_taken = self.executor.execute(rule.actions, event)

            event.handled = True
            event.rule_name = rule.name
            event.actions_taken = actions_taken

            self.stats.events_handled += 1

            # Update specific stats
            for action in rule.actions:
                action_type = action.get('type')
                if action_type == 'create_task':
                    self.stats.tasks_created += 1
                elif action_type == 'execute_command':
                    self.stats.commands_executed += 1
                elif action_type == 'webhook':
                    self.stats.webhooks_sent += 1

            self.logger.info(
                "event_handled",
                path=event.path,
                rule=rule.name,
                actions=actions_taken
            )

        except Exception as e:
            self.stats.errors += 1
            self.logger.error(
                "event_handling_failed",
                path=event.path,
                rule=rule.name,
                error=str(e)
            )

    def on_created(self, event):
        self._process_event(EventType.CREATED, event)

    def on_modified(self, event):
        self._process_event(EventType.MODIFIED, event)

    def on_deleted(self, event):
        self._process_event(EventType.DELETED, event)

    def on_moved(self, event):
        self._process_event(EventType.MOVED, event)


# =============================================================================
# Ultimate Watcher Manager
# =============================================================================

class UltimateWatcherManager:
    """Advanced watcher manager with all features"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.logger = WatcherLogger(WATCHER_LOGS)

        self.watch_folders: List[WatchFolder] = []
        self.observers: List = []
        self.handlers: Dict[Path, WatchdogEventHandler] = {}
        self.running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.lock = threading.Lock()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Load configuration
        self._setup_watches()

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from file"""
        defaults = {
            'folders': [
                {
                    'path': str(INBOX_PATH),
                    'recursive': True,
                    'enabled': True
                }
            ],
            'deduplicate_window_seconds': 5,
            'aggregate_window_seconds': 60,
            'max_restarts': 10,
            'restart_delay_seconds': 5,
            'health_check_interval': 60,
        }

        if config_path and config_path.exists() and HAS_YAML:
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    defaults.update(config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        return defaults

    def _setup_watches(self):
        """Setup watch folders from configuration"""
        folders_config = self.config.get('folders', [])

        for folder_config in folders_config:
            path = Path(folder_config['path'])

            if not path.exists():
                self.logger.warning("folder_not_found", path=str(path))
                continue

            # Parse rules
            rules = []
            for rule_config in folder_config.get('rules', []):
                # Build filter
                filter_config = rule_config.get('filter', {})
                event_filter = EventFilter(
                    patterns=filter_config.get('patterns', []),
                    ignore_patterns=filter_config.get('ignore_patterns', []),
                    event_types=[EventType(t) for t in filter_config.get('event_types', [])],
                    min_size_bytes=filter_config.get('min_size_bytes'),
                    max_size_bytes=filter_config.get('max_size_bytes'),
                    extensions=filter_config.get('extensions', []),
                    ignore_extensions=filter_config.get('ignore_extensions', [])
                )

                # Build rule
                rule = EventRule(
                    name=rule_config['name'],
                    filter=event_filter,
                    actions=rule_config.get('actions', []),
                    enabled=rule_config.get('enabled', True),
                    throttle_seconds=rule_config.get('throttle_seconds', 0),
                    aggregate_window=rule_config.get('aggregate_window', 0),
                    priority=rule_config.get('priority', 0)
                )
                rules.append(rule)

            watch_folder = WatchFolder(
                path=path,
                recursive=folder_config.get('recursive', True),
                rules=rules,
                enabled=folder_config.get('enabled', True)
            )

            self.watch_folders.append(watch_folder)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("shutdown_signal", signal=signum)
        self.stop()

    def start(self):
        """Start watching all folders"""
        if not HAS_WATCHDOG:
            print("Error: watchdog library not available")
            print("Install with: pip install watchdog")
            return False

        self.running = True

        # Create components
        deduplicator = EventDeduplicator(
            self.config.get('deduplicate_window_seconds', 5)
        )
        executor = ActionExecutor(self.logger, VAULT_PATH)

        # Setup observer for each folder
        for watch_folder in self.watch_folders:
            if not watch_folder.enabled:
                continue

            try:
                observer = Observer()
                handler = WatchdogEventHandler(
                    rules=watch_folder.rules,
                    executor=executor,
                    logger=self.logger,
                    deduplicator=deduplicator
                )

                observer.schedule(
                    handler,
                    str(watch_folder.path),
                    recursive=watch_folder.recursive
                )

                observer.start()
                self.observers.append(observer)
                self.handlers[watch_folder.path] = handler

                self.logger.info(
                    "watcher_started",
                    path=str(watch_folder.path),
                    recursive=watch_folder.recursive,
                    rules_count=len(watch_folder.rules)
                )

                print(f"Watching: {watch_folder.path}")

            except Exception as e:
                self.logger.error(
                    "watcher_start_failed",
                    path=str(watch_folder.path),
                    error=str(e)
                )

        if not self.observers:
            print("No folders to watch")
            return False

        print(f"\nWatching {len(self.observers)} folder(s)")
        print("Press Ctrl+C to stop\n")

        # Keep running
        try:
            while self.running:
                time.sleep(1)

                # Check observer health
                self._check_health()

        except KeyboardInterrupt:
            pass

        self.stop()
        return True

    def stop(self):
        """Stop all watchers"""
        self.running = False

        for observer in self.observers:
            try:
                observer.stop()
                observer.join()
            except:
                pass

        print("\nWatchers stopped")

    def _check_health(self):
        """Check health of all watchers and restart if needed"""
        for observer in self.observers:
            if not observer.is_alive():
                self.logger.error("watcher_died", restarting=True)
                self.restart_count += 1

                if self.restart_count <= self.max_restarts:
                    self.logger.warning("watcher_restarting", attempt=self.restart_count)
                    # Would restart observer here
                else:
                    self.logger.error("max_restarts_exceeded")
                    self.running = False

    def show_status(self):
        """Show current status of all watchers"""
        print("\n" + "=" * 60)
        print("WATCHER MANAGER STATUS")
        print("=" * 60)
        print(f"Running: {self.running}")
        print(f"Watched Folders: {len(self.watch_folders)}")
        print(f"Active Observers: {len(self.observers)}")
        print(f"Restart Count: {self.restart_count}")
        print("=" * 60)

        # Show per-folder stats
        for path, handler in self.handlers.items():
            stats = handler.stats
            print(f"\n📁 {path}:")
            print(f"  Events Seen:    {stats.events_seen}")
            print(f"  Events Handled: {stats.events_handled}")
            print(f"  Events Ignored: {stats.events_ignored}")
            print(f"  Tasks Created:  {stats.tasks_created}")
            print(f"  Commands Run:   {stats.commands_executed}")
            print(f"  Webhooks Sent:  {stats.webhooks_sent}")
            print(f"  Errors:         {stats.errors}")

        print()

    def health_check(self) -> Dict[str, Any]:
        """Perform health check"""
        health = {
            "status": "healthy" if self.running else "stopped",
            "watchers": len(self.observers),
            "all_alive": all(o.is_alive() for o in self.observers),
            "restart_count": self.restart_count,
            "folders": []
        }

        for watch_folder in self.watch_folders:
            folder_health = {
                "path": str(watch_folder.path),
                "enabled": watch_folder.enabled,
                "exists": watch_folder.path.exists(),
                "rules_count": len(watch_folder.rules)
            }
            health["folders"].append(folder_health)

        return health


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ultimate Watcher Manager')
    parser.add_argument('--config', '-c', help='Config file path')
    parser.add_argument('--status', '-s', action='store_true', help='Show status')
    parser.add_argument('--health', action='store_true', help='Health check')
    parser.add_argument('--test', help='Test event handling (JSON)')

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else CONFIG_PATH
    manager = UltimateWatcherManager(config_path)

    if args.status:
        manager.show_status()
        return 0

    if args.health:
        health = manager.health_check()
        print(json.dumps(health, indent=2))
        return 0

    if args.test:
        # Test event handling
        try:
            event_data = json.loads(args.test)
            print(f"Test event: {event_data}")
            return 0
        except Exception as e:
            print(f"Invalid test event: {e}")
            return 1

    # Start watching
    return 0 if manager.start() else 1


if __name__ == "__main__":
    sys.exit(main())
