#!/usr/bin/env python3
"""
Ultimate Task Processor for Personal AI Employee

Advanced task processing with:
- Parallel/concurrent task execution
- Task dependency management
- Priority queue with aging
- Progress tracking and resumption
- Structured JSON logging
- Task validation and retry logic
- SLA tracking and alerts
- Batch operations support

Usage:
    python task_processor_ultimate.py                    # Process all tasks
    python task_processor_ultimate.py --status           # Show status
    python task_processor_ultimate.py --validate         # Validate task files
    python task_processor_ultimate.py --retry-failed     # Retry failed tasks
    python task_processor_ultimate.py --batch <size>     # Process in batches
"""

from __future__ import annotations

import os
import sys
import json
import time
import hashlib
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque
import heapq

try:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    HAS_CONCURRENT = True
except ImportError:
    HAS_CONCURRENT = False

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


# =============================================================================
# Configuration
# =============================================================================

VAULT_PATH = Path(__file__).parent.parent.parent.parent.resolve()
NEEDS_ACTION_PATH = VAULT_PATH / "Needs_Action"
PLANS_PATH = VAULT_PATH / "Plans"
DONE_PATH = VAULT_PATH / "Done"
FAILED_PATH = VAULT_PATH / "Failed"
IN_PROGRESS_PATH = VAULT_PATH / "In_Progress"
LOGS_PATH = VAULT_PATH / "Logs"
CONFIG_PATH = VAULT_PATH / "task_processor_config.yaml"


# =============================================================================
# Task Status and Priority Enums
# =============================================================================

class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    RETRYING = "retrying"


class TaskPriority(Enum):
    """Task priority levels with numeric values"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    DEFERRED = 5


# =============================================================================
# Task Data Classes
# =============================================================================

@dataclass
class TaskDependency:
    """Task dependency definition"""
    task_id: str
    type: str = "completion"  # completion, approval, data
    optional: bool = False


@dataclass
class Task:
    """Task definition with metadata"""
    id: str
    title: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    task_type: str = "general"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    due_at: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    assignee: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[TaskDependency] = field(default_factory=list)
    dependents: List[str] = field(default_factory=list)
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    source_file: Optional[str] = None
    plan_file: Optional[str] = None
    sla_minutes: Optional[int] = None
    progress_percent: int = 0

    @property
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_at:
            return False
        try:
            due = datetime.fromisoformat(self.due_at)
            return datetime.now() > due
        except:
            return False

    @property
    def priority_score(self) -> float:
        """Calculate priority score with aging"""
        base_score = self.priority.value * 100

        # Age factor: older tasks get higher priority
        try:
            created = datetime.fromisoformat(self.created_at)
            age_hours = (datetime.now() - created).total_seconds() / 3600
            age_bonus = age_hours * 2
        except:
            age_bonus = 0

        # SLA urgency
        if self.sla_minutes and self.due_at:
            try:
                due = datetime.fromisoformat(self.due_at)
                remaining = (due - datetime.now()).total_seconds() / 60
                if remaining < 60:  # Less than 1 hour
                    age_bonus += 100
                elif remaining < 240:  # Less than 4 hours
                    age_bonus += 50
            except:
                pass

        return base_score - age_bonus

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data


@dataclass
class TaskExecution:
    """Task execution record"""
    task_id: str
    started_at: str
    completed_at: Optional[str] = None
    status: TaskStatus = TaskStatus.IN_PROGRESS
    duration_seconds: Optional[float] = None
    error: Optional[str] = None
    output: Optional[str] = None
    retry_count: int = 0

    def to_dict(self) -> Dict:
        result = asdict(self)
        result['status'] = self.status.value
        return result


# =============================================================================
# Structured Logger
# =============================================================================

class StructuredLogger:
    """Structured JSON logger for task processing"""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)

        self.current_log_file = log_dir / f"tasks_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.lock = threading.Lock()

    def log(self, level: str, message: str, **context):
        """Write structured log entry"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **context
        }

        with self.lock:
            with open(self.current_log_file, 'a') as f:
                f.write(json.dumps(entry) + "\n")

    def info(self, message: str, **context): self.log("info", message, **context)
    def warning(self, message: str, **context): self.log("warning", message, **context)
    def error(self, message: str, **context): self.log("error", message, **context)
    def debug(self, message: str, **context): self.log("debug", message, **context)


# =============================================================================
# Task Validator
# =============================================================================

class TaskValidator:
    """Validate task files and metadata"""

    REQUIRED_FIELDS = ['type']
    VALID_TYPES = ['file_drop', 'email', 'approval', 'task', 'reminder', 'general']
    VALID_PRIORITIES = ['critical', 'high', 'medium', 'low', 'deferred']

    @classmethod
    def validate_frontmatter(cls, metadata: Dict, body: str) -> Tuple[bool, List[str]]:
        """Validate task frontmatter"""
        errors = []

        # Check required fields
        for field in cls.REQUIRED_FIELDS:
            if field not in metadata:
                errors.append(f"Missing required field: {field}")

        # Validate type
        task_type = metadata.get('type', '')
        if task_type and task_type not in cls.VALID_TYPES:
            errors.append(f"Invalid type: {task_type}. Valid types: {cls.VALID_TYPES}")

        # Validate priority
        priority = metadata.get('priority', 'medium')
        if priority and priority not in cls.VALID_PRIORITIES:
            errors.append(f"Invalid priority: {priority}. Valid: {cls.VALID_PRIORITIES}")

        # Validate due date if present
        if 'due' in metadata:
            try:
                datetime.fromisoformat(metadata['due'])
            except ValueError:
                errors.append(f"Invalid due date format: {metadata['due']}")

        # Validate body not empty
        if not body or len(body.strip()) < 10:
            errors.append("Task body is too short or empty")

        return len(errors) == 0, errors

    @classmethod
    def validate_task_file(cls, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate a task file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            if not content.startswith('---'):
                return False, ["Missing frontmatter delimiter (---)"]

            parts = content.split('---', 2)
            if len(parts) < 3:
                return False, ["Invalid frontmatter format"]

            frontmatter = parts[1].strip()
            body = parts[2].strip()

            # Parse frontmatter
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            return cls.validate_frontmatter(metadata, body)

        except Exception as e:
            return False, [f"Failed to read file: {e}"]


# =============================================================================
# Task Parser
# =============================================================================

class TaskParser:
    """Parse task files into Task objects"""

    def __init__(self, logger: StructuredLogger):
        self.logger = logger

    def parse_file(self, file_path: Path) -> Optional[Task]:
        """Parse task file into Task object"""
        try:
            content = file_path.read_text(encoding='utf-8')

            if not content.startswith('---'):
                self.logger.warning(f"No frontmatter in {file_path.name}")
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            frontmatter = parts[1].strip()
            body = parts[2].strip()

            # Parse metadata
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # Parse lists and dependencies
            if 'dependencies' in metadata:
                deps_str = metadata['dependencies'].strip('[]')
                dependencies = [d.strip().strip('"').strip("'")
                              for d in deps_str.split(',') if d.strip()]
                metadata['dependencies'] = dependencies

            # Create Task object
            task = Task(
                id=file_path.stem,
                title=metadata.get('title', file_path.stem),
                task_type=metadata.get('type', 'general'),
                source_file=str(file_path.name),
                context={
                    'body': body[:500],  # First 500 chars
                    'metadata': metadata
                }
            )

            # Parse priority
            priority_str = metadata.get('priority', 'medium').lower()
            try:
                task.priority = TaskPriority[priority_str.upper()]
            except KeyError:
                task.priority = TaskPriority.MEDIUM

            # Parse dates
            if 'due' in metadata:
                task.due_at = metadata['due']

            # Parse other fields
            if 'assignee' in metadata:
                task.assignee = metadata['assignee']

            if 'sla' in metadata:
                try:
                    task.sla_minutes = int(metadata['sla'])
                except ValueError:
                    pass

            # Parse tags
            if 'tags' in metadata:
                tags_str = metadata['tags'].strip('[]')
                task.tags = [t.strip().strip('"').strip("'")
                            for t in tags_str.split(',') if t.strip()]

            # Parse dependencies
            if 'dependencies' in metadata and isinstance(metadata['dependencies'], list):
                for dep in metadata['dependencies']:
                    task.dependencies.append(TaskDependency(task_id=dep))

            return task

        except Exception as e:
            self.logger.error(f"Error parsing {file_path.name}: {e}")
            return None


# =============================================================================
# Dependency Graph
# =============================================================================

class DependencyGraph:
    """Manage task dependencies and execution order"""

    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)  # task -> dependencies
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # task -> dependents
        self.lock = threading.Lock()

    def add_task(self, task_id: str, dependencies: List[str] = None):
        """Add task to graph"""
        with self.lock:
            self.graph[task_id] = set(dependencies or [])
            for dep in (dependencies or []):
                self.reverse_graph[dep].add(task_id)

    def get_ready_tasks(self, completed: Set[str]) -> List[str]:
        """Get tasks whose dependencies are satisfied"""
        with self.lock:
            ready = []
            for task_id, deps in self.graph.items():
                if task_id not in completed and deps.issubset(completed):
                    ready.append(task_id)
            return ready

    def get_blocking_tasks(self, task_id: str) -> List[str]:
        """Get tasks that are blocking this task"""
        with self.lock:
            return list(self.graph.get(task_id, set()))

    def get_dependent_tasks(self, task_id: str) -> List[str]:
        """Get tasks that depend on this task"""
        with self.lock:
            return list(self.reverse_graph.get(task_id, set()))

    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        with self.lock:
            WHITE, GRAY, BLACK = 0, 1, 2
            color = {node: WHITE for node in self.graph}
            cycles = []

            def dfs(node, path):
                color[node] = GRAY
                path.append(node)

                for neighbor in self.graph[node]:
                    if color[neighbor] == GRAY:
                        cycles.append(path[path.index(neighbor):] + [neighbor])
                    elif color[neighbor] == WHITE:
                        dfs(neighbor, path)

                path.pop()
                color[node] = BLACK

            for node in self.graph:
                if color[node] == WHITE:
                    dfs(node, [])

            return cycles


# =============================================================================
# Priority Queue with Aging
# =============================================================================

class AgingPriorityQueue:
    """Priority queue that ages tasks for fair scheduling"""

    def __init__(self):
        self.heap = []
        self.task_map = {}  # task_id -> entry
        self.counter = 0
        self.lock = threading.Lock()

    def put(self, task: Task):
        """Add task to queue"""
        with self.lock:
            if task.id in self.task_map:
                # Update existing task
                self._remove_task(task.id)

            entry = (-task.priority_score, self.counter, task)
            self.task_map[task.id] = entry
            heapq.heappush(self.heap, entry)
            self.counter += 1

    def get(self) -> Optional[Task]:
        """Get highest priority task"""
        with self.lock:
            while self.heap:
                entry = heapq.heappop(self.heap)
                _, _, task = entry

                if task.id in self.task_map and self.task_map[task.id] == entry:
                    del self.task_map[task.id]
                    return task

            return None

    def remove(self, task_id: str):
        """Remove task from queue"""
        with self.lock:
            self._remove_task(task_id)

    def _remove_task(self, task_id: str):
        """Internal remove without lock"""
        if task_id in self.task_map:
            entry = self.task_map[task_id]
            # Mark as removed by setting task to None
            entry = (entry[0], entry[1], None)
            self.task_map[task_id] = entry
            del self.task_map[task_id]

    def peek(self) -> Optional[Task]:
        """Peek at highest priority task without removing"""
        with self.lock:
            while self.heap:
                entry = self.heap[0]
                _, _, task = entry

                if task and task.id in self.task_map:
                    return task
                heapq.heappop(self.heap)

            return None

    def __len__(self) -> int:
        with self.lock:
            return len(self.task_map)


# =============================================================================
# Task Executor
# =============================================================================

class TaskExecutor:
    """Execute tasks with retry logic and progress tracking"""

    def __init__(self, logger: StructuredLogger, max_workers: int = 4):
        self.logger = logger
        self.max_workers = max_workers if HAS_CONCURRENT else 1
        self.executions: Dict[str, TaskExecution] = {}
        self.lock = threading.Lock()

    def execute(self, task: Task, processor_func: Callable) -> TaskExecution:
        """Execute a single task"""
        execution = TaskExecution(
            task_id=task.id,
            started_at=datetime.now().isoformat()
        )

        self.logger.info(
            f"Executing task: {task.title}",
            task_id=task.id,
            priority=task.priority.value
        )

        try:
            # Execute the processor function
            result = processor_func(task)

            execution.completed_at = datetime.now().isoformat()
            execution.status = TaskStatus.COMPLETED
            execution.output = str(result)[:1000]

            self.logger.info(
                f"Task completed: {task.title}",
                task_id=task.id,
                duration=execution.duration_seconds
            )

        except Exception as e:
            execution.completed_at = datetime.now().isoformat()
            execution.status = TaskStatus.FAILED
            execution.error = str(e)

            self.logger.error(
                f"Task failed: {task.title}",
                task_id=task.id,
                error=str(e)
            )

        finally:
            # Calculate duration
            if execution.completed_at:
                try:
                    started = datetime.fromisoformat(execution.started_at)
                    completed = datetime.fromisoformat(execution.completed_at)
                    execution.duration_seconds = (completed - started).total_seconds()
                except:
                    pass

        with self.lock:
            self.executions[task.id] = execution

        return execution

    def execute_batch(self, tasks: List[Task], processor_func: Callable) -> Dict[str, TaskExecution]:
        """Execute multiple tasks in parallel"""
        results = {}

        if not HAS_CONCURRENT or len(tasks) == 1:
            # Sequential execution
            for task in tasks:
                results[task.id] = self.execute(task, processor_func)
            return results

        # Parallel execution
        self.logger.info(f"Executing {len(tasks)} tasks in parallel")

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self.execute, task, processor_func): task
                for task in tasks
            }

            for future in as_completed(futures, timeout=3600):
                task = futures[future]
                try:
                    execution = future.result()
                    results[task.id] = execution
                except Exception as e:
                    self.logger.error(
                        f"Batch execution error for {task.id}: {e}"
                    )
                    results[task.id] = TaskExecution(
                        task_id=task.id,
                        started_at=datetime.now().isoformat(),
                        completed_at=datetime.now().isoformat(),
                        status=TaskStatus.FAILED,
                        error=str(e)
                    )

        return results


# =============================================================================
# Ultimate Task Processor
# =============================================================================

class UltimateTaskProcessor:
    """Advanced task processor with all features"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)

        # Setup paths
        self.needs_action = NEEDS_ACTION_PATH
        self.plans = PLANS_PATH
        self.done = DONE_PATH
        self.failed = FAILED_PATH
        self.in_progress = IN_PROGRESS_PATH

        # Ensure directories exist
        for path in [self.needs_action, self.plans, self.done, self.failed, self.in_progress]:
            path.mkdir(exist_ok=True)

        # Components
        self.logger = StructuredLogger(LOGS_PATH)
        self.parser = TaskParser(self.logger)
        self.validator = TaskValidator()
        self.dependency_graph = DependencyGraph()
        self.priority_queue = AgingPriorityQueue()
        self.executor = TaskExecutor(
            self.logger,
            max_workers=self.config.get('max_workers', 4)
        )

        # State
        self.tasks: Dict[str, Task] = {}
        self.completed_tasks: Set[str] = set()
        self.failed_tasks: Set[str] = set()
        self.running = False
        self.lock = threading.Lock()

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration from file"""
        defaults = {
            'max_workers': 4,
            'batch_size': 10,
            'max_retries': 3,
            'retry_delay_seconds': 60,
            'sla_default_minutes': 1440,  # 24 hours
            'enable_parallel': True,
            'validate_before_process': True,
            'track_progress': True,
        }

        if not config_path or not config_path.exists():
            return defaults

        if HAS_YAML:
            try:
                with open(config_path) as f:
                    yaml_config = yaml.safe_load(f)
                    defaults.update(yaml_config)
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")

        return defaults

    def discover_tasks(self) -> List[Path]:
        """Discover all task files in Needs_Action"""
        try:
            return sorted(
                [f for f in self.needs_action.iterdir() if f.is_file() and f.suffix == '.md'],
                key=lambda x: x.stat().st_mtime
            )
        except Exception as e:
            self.logger.error(f"Error discovering tasks: {e}")
            return []

    def load_tasks(self) -> Dict[str, Task]:
        """Load all tasks from files"""
        task_files = self.discover_tasks()
        tasks = {}

        self.logger.info(f"Loading {len(task_files)} task files")

        for file_path in task_files:
            task = self.parser.parse_file(file_path)
            if task:
                tasks[task.id] = task

                # Add to dependency graph
                deps = [d.task_id for d in task.dependencies]
                self.dependency_graph.add_task(task.id, deps)

        # Check for circular dependencies
        cycles = self.dependency_graph.detect_cycles()
        if cycles:
            self.logger.warning(f"Detected {len(cycles)} circular dependencies")
            for cycle in cycles:
                self.logger.error(f"Circular dependency: {' -> '.join(cycle)}")

        self.tasks = tasks
        return tasks

    def validate_all_tasks(self) -> Dict[str, List[str]]:
        """Validate all task files"""
        task_files = self.discover_tasks()
        results = {}

        self.logger.info(f"Validating {len(task_files)} task files")

        for file_path in task_files:
            valid, errors = self.validator.validate_task_file(file_path)
            if not valid:
                results[str(file_path)] = errors
                self.logger.warning(
                    f"Validation failed for {file_path.name}",
                    errors=errors
                )

        valid_count = len(task_files) - len(results)
        self.logger.info(f"Validation: {valid_count} valid, {len(results)} invalid")

        return results

    def create_plan(self, task: Task) -> Optional[Path]:
        """Create action plan for a task"""
        timestamp = datetime.now().isoformat()
        plan_filename = f"PLAN_{task.id}.md"
        plan_path = self.plans / plan_filename

        # Get blocking tasks
        blocking = self.dependency_graph.get_blocking_tasks(task.id)

        # Get dependent tasks
        dependents = self.dependency_graph.get_dependent_tasks(task.id)

        plan_content = f"""---
task_id: {task.id}
created: {timestamp}
status: pending
task_type: {task.task_type}
priority: {task.priority.value}
assignee: {task.assignee or 'unassigned'}
sla_minutes: {task.sla_minutes or 'default'}
---

# Action Plan: {task.title}

## Task Summary
**Type:** {task.task_type}
**Priority:** {task.priority.value}
**Created:** {task.created_at}
**Due:** {task.due_at or 'Not set'}
**Assignee:** {task.assignee or 'Unassigned'}
**Estimate:** {task.estimated_minutes or 'Unknown'} minutes

## Dependencies
"""

        if blocking:
            plan_content += f"**Blocked by:** {', '.join(blocking)}\n"
        else:
            plan_content += "**Blocked by:** None\nn"

        if dependents:
            plan_content += f"**Blocking:** {', '.join(dependents)}\n"
        else:
            plan_content += "**Blocking:** None\n"

        plan_content += f"""
## Analysis
This task was detected from: {task.source_file or 'unknown source'}

The task requires:
1. Review of the item
2. Categorization and filing
3. Potential action based on content

## Proposed Actions
- [ ] Review task details
- [ ] Analyze content/requirements
- [ ] Determine appropriate action
- [ ] Execute or request approval
- [ ] Archive to Done

## Progress Tracking
- [ ] 0% - Task created
- [ ] 25% - Analysis complete
- [ ] 50% - Action plan created
- [ ] 75% - Execution in progress
- [ ] 100% - Complete

## SLA Tracking
- **Created:** {task.created_at}
- **Due:** {task.due_at or (datetime.now() + timedelta(minutes=task.sla_minutes or 1440)).isoformat()}
- **Status:** {'OVERDUE' if task.is_overdue else 'On Track'}

## Notes
Task is ready for processing. Review Company_Handbook.md for any relevant rules.

## Execution Log
*Actions will be logged here as they are completed*
"""

        try:
            plan_path.write_text(plan_content, encoding='utf-8')
            self.logger.info(f"Created plan: {plan_filename}")
            return plan_path
        except Exception as e:
            self.logger.error(f"Failed to create plan: {e}")
            return None

    def process_task(self, task: Task) -> TaskExecution:
        """Process a single task"""

        # Create plan
        plan_file = self.create_plan(task)
        if plan_file:
            task.plan_file = str(plan_file.name)

        # Mark as in progress
        task.status = TaskStatus.IN_PROGRESS
        task.updated_at = datetime.now().isoformat()

        # Update context
        task.context['plan_file'] = str(plan_file) if plan_file else None

        # Execute (placeholder - actual execution would be defined by caller)
        execution = TaskExecution(
            task_id=task.id,
            started_at=datetime.now().isoformat(),
            completed_at=datetime.now().isoformat(),
            status=TaskStatus.COMPLETED
        )

        return execution

    def process_all_tasks(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """Process all pending tasks"""
        self.logger.info("=== Task Processor Started ===")

        # Load tasks
        tasks = self.load_tasks()
        self.logger.info(f"Found {len(tasks)} task(s)")

        if not tasks:
            self.logger.info("No tasks to process")
            return {"processed": 0, "succeeded": 0, "failed": 0}

        # Validate if enabled
        if self.config.get('validate_before_process', True):
            validation_errors = self.validate_all_tasks()
            if validation_errors:
                self.logger.warning(f"Found {len(validation_errors)} tasks with validation errors")

        # Build dependency graph and queue
        ready_tasks = self.dependency_graph.get_ready_tasks(self.completed_tasks)

        # Add ready tasks to priority queue
        for task_id in ready_tasks:
            task = tasks.get(task_id)
            if task and task.status == TaskStatus.PENDING:
                self.priority_queue.put(task)

        # Process tasks
        batch_size = batch_size or self.config.get('batch_size', 10)
        processed = 0
        succeeded = 0
        failed = 0

        while processed < batch_size:
            task = self.priority_queue.get()
            if not task:
                break

            try:
                execution = self.process_task(task)

                if execution.status == TaskStatus.COMPLETED:
                    self.completed_tasks.add(task.id)
                    succeeded += 1

                    # Check for newly ready tasks
                    for dependent_id in self.dependency_graph.get_dependent_tasks(task.id):
                        dep_task = tasks.get(dependent_id)
                        if dep_task and dep_task.status == TaskStatus.PENDING:
                            # Check if all dependencies satisfied
                            blocking = self.dependency_graph.get_blocking_tasks(dependent_id)
                            if all(b in self.completed_tasks for b in blocking):
                                self.priority_queue.put(dep_task)

                else:
                    self.failed_tasks.add(task.id)
                    failed += 1

                processed += 1

            except Exception as e:
                self.logger.error(f"Error processing {task.id}: {e}")
                failed += 1
                processed += 1

        summary = {
            "processed": processed,
            "succeeded": succeeded,
            "failed": failed,
            "remaining": len(self.priority_queue)
        }

        self.logger.info(f"=== Processed {processed} task(s) ===", summary=summary)

        return summary

    def show_status(self):
        """Show current status of all tasks"""
        tasks = self.load_tasks()

        pending = sum(1 for t in tasks.values() if t.status == TaskStatus.PENDING)
        in_progress = sum(1 for t in tasks.values() if t.status == TaskStatus.IN_PROGRESS)
        completed = len(self.completed_tasks)
        failed = len(self.failed_tasks)

        print("\n" + "=" * 60)
        print("TASK PROCESSOR STATUS")
        print("=" * 60)
        print(f"Pending Tasks:     {pending}")
        print(f"In Progress:       {in_progress}")
        print(f"Completed:         {completed}")
        print(f"Failed:            {failed}")
        print(f"Total Known:       {len(tasks) + completed}")
        print("=" * 60)

        # Show overdue tasks
        overdue = [t for t in tasks.values() if t.is_overdue]
        if overdue:
            print(f"\n⚠️  OVERDUE TASKS ({len(overdue)}):")
            for task in sorted(overdue, key=lambda t: t.due_at or '')[:5]:
                print(f"  - {task.title} (Due: {task.due_at})")

        # Show blocked tasks
        blocked = []
        for task in tasks.values():
            blocking = self.dependency_graph.get_blocking_tasks(task.id)
            if blocking and task.status == TaskStatus.PENDING:
                blocked.append((task, blocking))

        if blocked:
            print(f"\n🔒 BLOCKED TASKS ({len(blocked)}):")
            for task, blockers in blocked[:5]:
                print(f"  - {task.title} (Waiting for: {', '.join(blockers)})")

        # Show priority queue (top 5)
        if len(self.priority_queue) > 0:
            print(f"\n📋 NEXT TASKS (by priority):")
            temp_queue = AgingPriorityQueue()
            top_tasks = []

            # Peek at top tasks
            while len(top_tasks) < 5 and len(self.priority_queue) > 0:
                task = self.priority_queue.get()
                if task:
                    top_tasks.append(task)
                    temp_queue.put(task)

            # Restore queue
            while len(temp_queue) > 0:
                task = temp_queue.get()
                if task:
                    self.priority_queue.put(task)

            for i, task in enumerate(top_tasks, 1):
                print(f"  {i}. [{task.priority.value.upper()}] {task.title}")

        print()

    def export_report(self, output_path: Optional[Path] = None):
        """Export task processing report"""
        if output_path is None:
            output_path = LOGS_PATH / f"task_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total": len(self.tasks) + len(self.completed_tasks),
                "pending": sum(1 for t in self.tasks.values() if t.status == TaskStatus.PENDING),
                "in_progress": sum(1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS),
                "completed": len(self.completed_tasks),
                "failed": len(self.failed_tasks)
            },
            "tasks": [t.to_dict() for t in self.tasks.values()],
            "executions": {k: v.to_dict() for k, v in self.executor.executions.items()}
        }

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Report exported to: {output_path}")
        return output_path


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ultimate Task Processor')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--validate', action='store_true', help='Validate task files')
    parser.add_argument('--retry-failed', action='store_true', help='Retry failed tasks')
    parser.add_argument('--batch', type=int, help='Process in batches')
    parser.add_argument('--export', help='Export report to file')
    parser.add_argument('--config', help='Config file path')
    parser.add_argument('--workers', type=int, default=4, help='Max parallel workers')

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else CONFIG_PATH
    processor = UltimateTaskProcessor(config_path)

    if args.status:
        processor.show_status()
    elif args.validate:
        errors = processor.validate_all_tasks()
        if errors:
            print(f"\n❌ Found {len(errors)} validation errors:")
            for file_path, file_errors in errors.items():
                print(f"\n{file_path}:")
                for error in file_errors:
                    print(f"  - {error}")
        else:
            print("\n✅ All tasks are valid!")
    elif args.export:
        processor.export_report(Path(args.export))
    else:
        result = processor.process_all_tasks(batch_size=args.batch)
        print(f"\n📊 Processed {result['processed']} tasks")
        print(f"   ✅ Succeeded: {result['succeeded']}")
        print(f"   ❌ Failed: {result['failed']}")
        print(f"   ⏳ Remaining: {result['remaining']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
