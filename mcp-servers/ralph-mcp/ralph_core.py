#!/usr/bin/env python3
"""
Ralph Core - Task queue and progress tracking for Ralph Loop

Implements the core functionality for autonomous task completion:
- Task queue management (list, claim, get details)
- Progress tracking (update, get, check completion)
- Iteration control (should_continue, increment)
- State persistence (JSON files)

Phase 2 Features:
- Multi-task orchestration (task groups, batch processing)
- Smart task discovery (blocking issues, effort estimation)
- Approval workflow integration (check status, wait for approval)
- Performance metrics (success rate, average iterations)
- Health monitoring (stuck tasks, system health)
"""

import sys
from pathlib import Path
import logging
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict, field
import hashlib
import time

logger = logging.getLogger(__name__)


@dataclass
class RalphState:
    """Ralph loop state for a task"""
    task_id: str
    original_path: str
    target_path: str
    max_iterations: int
    current_iteration: int
    prompt: str
    completion_strategy: str  # "file_movement" or "promise"
    started_at: str
    status: str  # "in_progress", "blocked", "waiting_approval", "complete"
    notes: List[str]
    history: List[Dict]

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'RalphState':
        """Create from dictionary"""
        return cls(**data)


class RalphCore:
    """
    Ralph Core - Task queue and progress tracking

    Manages the autonomous task completion loop with state persistence
    and progress tracking across iterations.
    """

    def __init__(self, vault_path: str):
        """
        Initialize Ralph Core

        Args:
            vault_path: Path to AI Employee vault root
        """
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / "Needs_Action"
        self.done = self.vault_path / "Done"
        self.ralph_dir = self.vault_path / "Ralph"
        self.state_dir = self.ralph_dir / "state"
        self.archive_dir = self.ralph_dir / "archive"

        # Create directories
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Ralph Core initialized")
        logger.info(f"  Vault path: {self.vault_path}")
        logger.info(f"  State directory: {self.state_dir}")

    def _generate_task_id(self, task_file: Path) -> str:
        """Generate unique task ID from file path and timestamp"""
        timestamp = datetime.now().isoformat()
        unique_string = f"{task_file}_{timestamp}"
        hash_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        return f"ralph_{hash_id}"

    def list_pending_tasks(self) -> List[Dict]:
        """
        List all tasks in /Needs_Action folder

        Returns:
            List of task dictionaries with metadata
        """
        try:
            tasks = []
            task_files = list(self.needs_action.glob("*.md"))
            task_files.extend(self.needs_action.rglob("*.md"))

            # Remove duplicates
            task_files = list(set(task_files))

            for task_file in task_files:
                try:
                    # Parse frontmatter
                    content = task_file.read_text(encoding='utf-8')
                    metadata = self._parse_frontmatter(content)

                    tasks.append({
                        'file_path': str(task_file.relative_to(self.vault_path)),
                        'file_name': task_file.name,
                        'type': metadata.get('type', 'unknown'),
                        'priority': metadata.get('priority', 'medium'),
                        'status': metadata.get('status', 'pending'),
                        'created': metadata.get('received', metadata.get('created', 'unknown')),
                        'size_bytes': len(content)
                    })
                except Exception as e:
                    logger.warning(f"Error parsing task {task_file.name}: {e}")
                    continue

            logger.info(f"Found {len(tasks)} pending tasks")
            return tasks

        except Exception as e:
            logger.error(f"Error listing pending tasks: {e}")
            return []

    def claim_next_task(
        self,
        priority: Optional[str] = None,
        task_type: Optional[str] = None
    ) -> Optional[str]:
        """
        Claim next available task for processing

        Args:
            priority: Filter by priority (high/medium/low)
            task_type: Filter by task type (email/whatsapp/etc)

        Returns:
            Task file path or None if no tasks available
        """
        try:
            tasks = self.list_pending_tasks()

            # Filter tasks
            if priority:
                tasks = [t for t in tasks if t['priority'] == priority]
            if task_type:
                tasks = [t for t in tasks if t['type'] == task_type]

            if not tasks:
                logger.info("No tasks matching criteria")
                return None

            # Sort by priority (high > medium > low)
            priority_order = {'high': 0, 'medium': 1, 'low': 2}
            tasks.sort(key=lambda t: priority_order.get(t['priority'], 99))

            # Get first task
            task = tasks[0]
            task_path = self.vault_path / task['file_path']

            logger.info(f"Claimed task: {task['file_name']}")
            return str(task_path)

        except Exception as e:
            logger.error(f"Error claiming task: {e}")
            return None

    def get_task_details(self, task_file: str) -> Optional[Dict]:
        """
        Get full task content and metadata

        Args:
            task_file: Path to task file

        Returns:
            Task content with YAML frontmatter or None
        """
        try:
            task_path = Path(task_file)

            if not task_path.exists():
                logger.error(f"Task file not found: {task_file}")
                return None

            content = task_path.read_text(encoding='utf-8')
            metadata = self._parse_frontmatter(content)

            # Extract body content
            body = self._extract_body(content)

            return {
                'file_path': str(task_path.relative_to(self.vault_path)),
                'file_name': task_path.name,
                'metadata': metadata,
                'body': body,
                'full_content': content
            }

        except Exception as e:
            logger.error(f"Error getting task details: {e}")
            return None

    def create_ralph_state(
        self,
        task_file: str,
        prompt: str,
        max_iterations: int = 10,
        completion_strategy: str = "file_movement"
    ) -> RalphState:
        """
        Create Ralph state for a new task

        Args:
            task_file: Path to task file
            prompt: Original prompt
            max_iterations: Maximum iterations allowed
            completion_strategy: "file_movement" or "promise"

        Returns:
            RalphState object
        """
        try:
            task_path = Path(task_file)
            task_id = self._generate_task_id(task_path)

            state = RalphState(
                task_id=task_id,
                original_path=str(task_path.relative_to(self.vault_path)),
                target_path=f"Done/{task_path.name}",
                max_iterations=max_iterations,
                current_iteration=1,
                prompt=prompt,
                completion_strategy=completion_strategy,
                started_at=datetime.now().isoformat(),
                status="in_progress",
                notes=[],
                history=[]
            )

            # Save state
            self._save_state(state)

            logger.info(f"Created Ralph state for task: {task_id}")
            return state

        except Exception as e:
            logger.error(f"Error creating Ralph state: {e}")
            raise

    def update_progress(
        self,
        task_id: str,
        status: str,
        notes: Optional[str] = None
    ) -> Optional[RalphState]:
        """
        Update task progress in Ralph state

        Args:
            task_id: Task identifier
            status: New status (in_progress/blocked/waiting_approval)
            notes: Progress notes

        Returns:
            Updated RalphState or None
        """
        try:
            state = self._load_state(task_id)

            if not state:
                logger.error(f"Task state not found: {task_id}")
                return None

            # Update status
            state.status = status

            # Add notes
            if notes:
                state.notes.append(f"{datetime.now().isoformat()}: {notes}")

            # Add to history
            state.history.append({
                'iteration': state.current_iteration,
                'timestamp': datetime.now().isoformat(),
                'status': status,
                'notes': notes
            })

            # Save state
            self._save_state(state)

            logger.info(f"Updated progress for {task_id}: {status}")
            return state

        except Exception as e:
            logger.error(f"Error updating progress: {e}")
            return None

    def get_progress(self, task_id: str) -> Optional[Dict]:
        """
        Get current progress for a task

        Args:
            task_id: Task identifier

        Returns:
            Progress details with history
        """
        try:
            state = self._load_state(task_id)

            if not state:
                logger.error(f"Task state not found: {task_id}")
                return None

            return {
                'task_id': state.task_id,
                'status': state.status,
                'current_iteration': state.current_iteration,
                'max_iterations': state.max_iterations,
                'started_at': state.started_at,
                'elapsed_minutes': self._calculate_elapsed(state.started_at),
                'notes': state.notes,
                'history': state.history
            }

        except Exception as e:
            logger.error(f"Error getting progress: {e}")
            return None

    def check_completion(self, task_id: str) -> Dict:
        """
        Check if task is complete (file moved to /Done)

        Args:
            task_id: Task identifier

        Returns:
            Boolean + completion status
        """
        try:
            state = self._load_state(task_id)

            if not state:
                return {
                    'complete': False,
                    'reason': 'Task state not found'
                }

            # Check if file exists in Done
            done_file = self.vault_path / state.target_path

            if done_file.exists():
                return {
                    'complete': True,
                    'reason': 'File found in Done folder',
                    'file_path': str(done_file.relative_to(self.vault_path))
                }

            # Check promise-based completion
            if state.completion_strategy == "promise":
                # Check last history entry for promise
                if state.history:
                    last_entry = state.history[-1]
                    if '<promise>TASK_COMPLETE</promise>' in str(last_entry):
                        return {
                            'complete': True,
                            'reason': 'Task completion promise detected'
                        }

            return {
                'complete': False,
                'reason': 'Task not yet complete',
                'status': state.status
            }

        except Exception as e:
            logger.error(f"Error checking completion: {e}")
            return {
                'complete': False,
                'reason': f'Error: {str(e)}'
            }

    def should_continue(self, task_id: str) -> Dict:
        """
        Check if Ralph should continue looping

        Args:
            task_id: Task identifier

        Returns:
            should_continue + reason
        """
        try:
            state = self._load_state(task_id)

            if not state:
                return {
                    'should_continue': False,
                    'reason': 'Task state not found'
                }

            # Check max iterations
            if state.current_iteration >= state.max_iterations:
                return {
                    'should_continue': False,
                    'reason': f'Max iterations reached ({state.max_iterations})'
                }

            # Check if complete
            completion = self.check_completion(task_id)
            if completion['complete']:
                return {
                    'should_continue': False,
                    'reason': 'Task is complete'
                }

            return {
                'should_continue': True,
                'reason': 'Task in progress'
            }

        except Exception as e:
            logger.error(f"Error checking should_continue: {e}")
            return {
                'should_continue': False,
                'reason': f'Error: {str(e)}'
            }

    def increment_iteration(self, task_id: str) -> Optional[int]:
        """
        Increment iteration counter

        Args:
            task_id: Task identifier

        Returns:
            New iteration count or None
        """
        try:
            state = self._load_state(task_id)

            if not state:
                logger.error(f"Task state not found: {task_id}")
                return None

            state.current_iteration += 1

            # Save state
            self._save_state(state)

            logger.info(f"Incremented iteration for {task_id}: {state.current_iteration}")
            return state.current_iteration

        except Exception as e:
            logger.error(f"Error incrementing iteration: {e}")
            return None

    def _parse_frontmatter(self, content: str) -> Dict:
        """Parse YAML frontmatter from markdown content"""
        metadata = {}

        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 2:
                frontmatter = parts[1].strip()
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip().strip('"')

        return metadata

    def _extract_body(self, content: str) -> str:
        """Extract body content from markdown"""
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) > 2:
                return parts[2].strip()
            elif len(parts) == 2:
                return parts[1].strip()

        return content

    def _calculate_elapsed(self, started_at: str) -> float:
        """Calculate elapsed time in minutes"""
        try:
            start = datetime.fromisoformat(started_at)
            elapsed = (datetime.now() - start).total_seconds() / 60
            return round(elapsed, 2)
        except:
            return 0.0

    def _get_state_file(self, task_id: str) -> Path:
        """Get state file path for task"""
        return self.state_dir / f"{task_id}.json"

    def _save_state(self, state: RalphState) -> None:
        """Save Ralph state to file"""
        state_file = self._get_state_file(state.task_id)
        state_file.write_text(json.dumps(state.to_dict(), indent=2), encoding='utf-8')

    def _load_state(self, task_id: str) -> Optional[RalphState]:
        """Load Ralph state from file"""
        state_file = self._get_state_file(task_id)

        if not state_file.exists():
            return None

        try:
            data = json.loads(state_file.read_text(encoding='utf-8'))
            return RalphState.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading state: {e}")
            return None

    def archive_state(self, task_id: str) -> bool:
        """
        Archive completed task state

        Args:
            task_id: Task identifier

        Returns:
            True if successful
        """
        try:
            state_file = self._get_state_file(task_id)

            if not state_file.exists():
                logger.warning(f"State file not found: {task_id}")
                return False

            # Move to archive
            archive_file = self.archive_dir / f"{task_id}.json"
            state_file.rename(archive_file)

            logger.info(f"Archived state for {task_id}")
            return True

        except Exception as e:
            logger.error(f"Error archiving state: {e}")
            return False

    # ========================================================================
    # PHASE 2: Multi-Task Orchestration
    # ========================================================================

    def create_task_group(
        self,
        task_ids: List[str],
        group_name: str,
        strategy: str = "sequential"
    ) -> Dict:
        """
        Create a task group for batch processing

        Args:
            task_ids: List of task IDs to group
            group_name: Name for the group
            strategy: "sequential" or "parallel"

        Returns:
            Group details with group ID
        """
        try:
            group_id = f"group_{hashlib.md5(group_name.encode()).hexdigest()[:12]}"

            group = {
                'group_id': group_id,
                'group_name': group_name,
                'task_ids': task_ids,
                'strategy': strategy,
                'created_at': datetime.now().isoformat(),
                'status': 'pending'
            }

            # Save group file
            group_file = self.ralph_dir / 'groups' / f"{group_id}.json"
            group_file.parent.mkdir(exist_ok=True)
            group_file.write_text(json.dumps(group, indent=2), encoding='utf-8')

            logger.info(f"Created task group: {group_name} ({len(task_ids)} tasks)")

            return {
                'success': True,
                'data': group
            }

        except Exception as e:
            logger.error(f"Error creating task group: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def process_task_group(self, group_id: str) -> Dict:
        """
        Process all tasks in a group

        Args:
            group_id: Group identifier

        Returns:
            Processing results
        """
        try:
            group_file = self.ralph_dir / 'groups' / f"{group_id}.json"

            if not group_file.exists():
                return {
                    'success': False,
                    'error': 'Group not found'
                }

            group = json.loads(group_file.read_text(encoding='utf-8'))
            strategy = group.get('strategy', 'sequential')
            task_ids = group.get('task_ids', [])

            results = []

            if strategy == 'sequential':
                # Process tasks one by one
                for task_id in task_ids:
                    state = self._load_state(task_id)
                    if state:
                        results.append({
                            'task_id': task_id,
                            'status': state.status,
                            'iteration': state.current_iteration
                        })
            else:
                # Parallel - just return list of states
                for task_id in task_ids:
                    state = self._load_state(task_id)
                    if state:
                        results.append({
                            'task_id': task_id,
                            'status': state.status,
                            'iteration': state.current_iteration
                        })

            return {
                'success': True,
                'data': {
                    'group_id': group_id,
                    'strategy': strategy,
                    'results': results
                }
            }

        except Exception as e:
            logger.error(f"Error processing task group: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Smart Task Discovery
    # ========================================================================

    def discover_blocking_issues(self) -> Dict:
        """
        Find tasks blocking other tasks

        Returns:
            Dict with success status and list of blocking task relationships
        """
        try:
            blocking_tasks = []

            # Get all active states
            state_files = list(self.state_dir.glob('*.json'))

            for state_file in state_files:
                try:
                    state = self._load_state(state_file.stem)
                    if state and state.status == 'blocked':
                        # This task is blocked
                        blocking_tasks.append({
                            'task_id': state.task_id,
                            'task_file': state.original_path,
                            'reason': state.notes[-1] if state.notes else 'Blocked',
                            'blocking_tasks': []  # Could be enhanced with actual dependency tracking
                        })
                except Exception as e:
                    logger.debug(f"Error checking state {state_file.name}: {e}")
                    continue

            logger.info(f"Found {len(blocking_tasks)} blocking tasks")

            return {
                'success': True,
                'data': blocking_tasks
            }

        except Exception as e:
            logger.error(f"Error discovering blocking issues: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def estimate_effort(self, task_file: str) -> Dict:
        """
        Estimate task effort based on type and complexity

        Args:
            task_file: Path to task file

        Returns:
            Effort estimation
        """
        try:
            task_path = Path(task_file)

            if not task_path.exists():
                return {
                    'success': False,
                    'error': 'Task file not found'
                }

            # Get task details
            details = self.get_task_details(task_file)
            if not details:
                return {
                    'success': False,
                    'error': 'Failed to get task details'
                }

            metadata = details['metadata']
            task_type = metadata.get('type', 'unknown')
            body_length = len(details.get('body', ''))

            # Estimate based on task type
            effort_matrix = {
                'email': {'steps': 3, 'time': 5},      # Read, approve, send
                'whatsapp': {'steps': 2, 'time': 3},  # Read, send
                'linkedin_post': {'steps': 3, 'time': 8},
                'facebook_post': {'steps': 3, 'time': 8},
                'instagram_post': {'steps': 3, 'time': 8},
                'x_post': {'steps': 3, 'time': 8},
                'slack_event': {'steps': 2, 'time': 3},
                'calendar_event': {'steps': 2, 'time': 3},
                'odoo_invoice': {'steps': 5, 'time': 15},
            }

            base_effort = effort_matrix.get(task_type, {'steps': 3, 'time': 10})

            # Adjust based on content length
            complexity_multiplier = 1.0
            if body_length > 1000:
                complexity_multiplier = 1.5
            elif body_length > 2000:
                complexity_multiplier = 2.0

            estimated_steps = int(base_effort['steps'] * complexity_multiplier)
            estimated_time = int(base_effort['time'] * complexity_multiplier)

            # Determine complexity level
            if estimated_steps <= 3:
                complexity = "low"
            elif estimated_steps <= 5:
                complexity = "medium"
            else:
                complexity = "high"

            return {
                'success': True,
                'data': {
                    'task_type': task_type,
                    'estimated_steps': estimated_steps,
                    'estimated_time_minutes': estimated_time,
                    'complexity': complexity,
                    'content_length': body_length
                }
            }

        except Exception as e:
            logger.error(f"Error estimating effort: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Approval Workflow Integration
    # ========================================================================

    def check_approval_status(self, task_id: str) -> Dict:
        """
        Check if pending approval is approved/rejected

        Args:
            task_id: Task waiting for approval

        Returns:
            Approval status
        """
        try:
            state = self._load_state(task_id)

            if not state:
                return {
                    'success': False,
                    'error': 'Task state not found'
                }

            # Check if task is waiting for approval
            if state.status != 'waiting_approval':
                return {
                    'success': True,
                    'data': {
                        'status': 'not_waiting',
                        'message': 'Task is not waiting for approval'
                    }
                }

            # Check /Approved and /Rejected folders
            approved_path = self.vault_path / "Approved"
            rejected_path = self.vault_path / "Rejected"
            pending_path = self.vault_path / "Pending_Approval"

            task_name = Path(state.original_path).name

            # Check if approved
            approved_files = list(approved_path.rglob(f"**/{task_name}"))
            if approved_files:
                return {
                    'success': True,
                    'data': {
                        'status': 'approved',
                        'approved_at': datetime.fromtimestamp(
                            approved_files[0].stat().st_mtime
                        ).isoformat(),
                        'approved_by': 'human'  # Could be auto-approver in future
                    }
                }

            # Check if rejected
            rejected_files = list(rejected_path.rglob(f"**/{task_name}"))
            if rejected_files:
                return {
                    'success': True,
                    'data': {
                        'status': 'rejected',
                        'rejected_at': datetime.fromtimestamp(
                            rejected_files[0].stat().st_mtime
                        ).isoformat()
                    }
                }

            # Check if still pending
            pending_files = list(pending_path.rglob(f"**/{task_name}"))
            if pending_files:
                return {
                    'success': True,
                    'data': {
                        'status': 'pending',
                        'pending_since': datetime.fromtimestamp(
                            pending_files[0].stat().st_mtime
                        ).isoformat()
                    }
                }

            return {
                'success': True,
                'data': {
                    'status': 'not_found',
                    'message': 'Approval file not found in any folder'
                }
            }

        except Exception as e:
            logger.error(f"Error checking approval status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def wait_for_approval(
        self,
        task_id: str,
        timeout_minutes: int = 60,
        poll_interval_seconds: int = 30
    ) -> Dict:
        """
        Wait (with timeout) for human approval

        Args:
            task_id: Task waiting for approval
            timeout_minutes: Maximum time to wait
            poll_interval_seconds: Time between checks

        Returns:
            Approval decision or timeout
        """
        try:
            start_time = datetime.now()
            timeout = timedelta(minutes=timeout_minutes)

            logger.info(f"Waiting for approval (timeout: {timeout_minutes} minutes)")

            while (datetime.now() - start_time) < timeout:
                # Check approval status
                status_result = self.check_approval_status(task_id)

                if not status_result['success']:
                    return {
                        'success': False,
                        'error': status_result.get('error')
                    }

                status_data = status_result['data']
                status = status_data.get('status')

                if status == 'approved':
                    logger.info("✓ Approval received!")
                    return {
                        'success': True,
                        'data': {
                            'decision': 'approved',
                            'approved_at': status_data.get('approved_at')
                        }
                    }
                elif status == 'rejected':
                    logger.warning("✗ Approval rejected")
                    return {
                        'success': True,
                        'data': {
                            'decision': 'rejected',
                            'rejected_at': status_data.get('rejected_at')
                        }
                    }
                elif status == 'not_found':
                    logger.warning("Approval file not found")
                    return {
                        'success': False,
                        'error': 'Approval file not found'
                    }

                # Still pending, wait and retry
                logger.debug(f"Still pending, waiting {poll_interval_seconds}s...")
                time.sleep(poll_interval_seconds)

            # Timeout
            logger.warning(f"Approval timeout after {timeout_minutes} minutes")
            return {
                'success': True,
                'data': {
                    'decision': 'timeout',
                    'timeout_minutes': timeout_minutes
                }
            }

        except Exception as e:
            logger.error(f"Error waiting for approval: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Performance Metrics
    # ========================================================================

    def get_performance_metrics(self, time_range: str = "all") -> Dict:
        """
        Get Ralph loop performance metrics

        Args:
            time_range: "today", "week", "month", "all"

        Returns:
            Performance metrics
        """
        try:
            # Get archived states
            archived_files = list(self.archive_dir.glob('*.json'))

            # Filter by time range
            now = datetime.now()
            if time_range == "today":
                cutoff = now - timedelta(days=1)
            elif time_range == "week":
                cutoff = now - timedelta(weeks=1)
            elif time_range == "month":
                cutoff = now - timedelta(days=30)
            else:  # all
                cutoff = datetime.fromtimestamp(0)

            filtered_files = []
            for f in archived_files:
                try:
                    mtime = datetime.fromtimestamp(f.stat().st_mtime)
                    if mtime >= cutoff:
                        filtered_files.append(f)
                except:
                    continue

            if not filtered_files:
                return {
                    'success': True,
                    'data': {
                        'tasks_completed': 0,
                        'average_iterations': 0,
                        'average_time_minutes': 0,
                        'success_rate': 0.0,
                        'blocked_rate': 0.0
                    }
                }

            # Analyze states
            total_tasks = len(filtered_files)
            total_iterations = 0
            total_time = 0.0
            successful = 0
            blocked = 0

            for f in filtered_files:
                try:
                    data = json.loads(f.read_text(encoding='utf-8'))
                    total_iterations += data.get('current_iteration', 0)

                    # Calculate elapsed time
                    started_at = data.get('started_at', '')
                    if started_at:
                        try:
                            start = datetime.fromisoformat(started_at)
                            archived_time = datetime.fromtimestamp(f.stat().st_mtime)
                            elapsed = (archived_time - start).total_seconds() / 60
                            total_time += elapsed
                        except:
                            pass

                    status = data.get('status', '')
                    if status == 'complete':
                        successful += 1
                    elif status == 'blocked':
                        blocked += 1

                except Exception as e:
                    logger.debug(f"Error analyzing {f.name}: {e}")
                    continue

            # Calculate averages
            avg_iterations = total_iterations / total_tasks if total_tasks > 0 else 0
            avg_time = total_time / total_tasks if total_tasks > 0 else 0
            success_rate = (successful / total_tasks * 100) if total_tasks > 0 else 0
            blocked_rate = (blocked / total_tasks * 100) if total_tasks > 0 else 0

            return {
                'success': True,
                'data': {
                    'time_range': time_range,
                    'tasks_completed': total_tasks,
                    'average_iterations': round(avg_iterations, 2),
                    'average_time_minutes': round(avg_time, 2),
                    'success_rate': round(success_rate, 2),
                    'blocked_rate': round(blocked_rate, 2)
                }
            }

        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Health Monitoring
    # ========================================================================

    def get_ralph_health(self) -> Dict:
        """
        Get Ralph loop system health

        Returns:
            Health status
        """
        try:
            # Get active tasks
            active_states = list(self.state_dir.glob('*.json'))

            # Get stuck tasks
            stuck_tasks = []
            for state_file in active_states:
                try:
                    state = self._load_state(state_file.stem)
                    if state:
                        if state.current_iteration >= state.max_iterations:
                            stuck_tasks.append({
                                'task_id': state.task_id,
                                'reason': 'Max iterations reached',
                                'iterations': state.current_iteration,
                                'max_iterations': state.max_iterations,
                                'status': state.status
                            })
                        elif state.status == 'blocked':
                            stuck_tasks.append({
                                'task_id': state.task_id,
                                'reason': f'Blocked: {state.notes[-1] if state.notes else "Unknown"}',
                                'iterations': state.current_iteration,
                                'max_iterations': state.max_iterations,
                                'status': state.status
                            })
                except Exception as e:
                    logger.debug(f"Error checking {state_file.name}: {e}")
                    continue

            # Calculate metrics
            total_active = len(active_states)
            total_stuck = len(stuck_tasks)
            avg_iterations = 0

            if active_states:
                total_iters = 0
                for state_file in active_states:
                    try:
                        state = self._load_state(state_file.stem)
                        if state:
                            total_iters += state.current_iteration
                    except:
                        continue
                avg_iterations = total_iters / len(active_states)

            # Determine health status
            if total_stuck > 0:
                health_status = "warning" if total_stuck < 3 else "critical"
            elif total_active > 20:
                health_status = "warning"  # Too many active tasks
            else:
                health_status = "healthy"

            return {
                'success': True,
                'data': {
                    'status': health_status,
                    'active_tasks': total_active,
                    'stuck_tasks': total_stuck,
                    'average_iterations': round(avg_iterations, 2),
                    'stuck_task_details': stuck_tasks
                }
            }

        except Exception as e:
            logger.error(f"Error getting health: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_stuck_tasks(self) -> List[Dict]:
        """
        Find tasks that exceeded max iterations

        Returns:
            Array of stuck task IDs with reasons
        """
        try:
            stuck_tasks = []
            active_states = list(self.state_dir.glob('*.json'))

            for state_file in active_states:
                try:
                    state = self._load_state(state_file.stem)
                    if state and state.current_iteration >= state.max_iterations:
                        stuck_tasks.append({
                            'task_id': state.task_id,
                            'original_path': state.original_path,
                            'iterations': state.current_iteration,
                            'max_iterations': state.max_iterations,
                            'status': state.status,
                            'reason': 'Max iterations reached'
                        })
                except Exception as e:
                    logger.debug(f"Error checking {state_file.name}: {e}")
                    continue

            logger.info(f"Found {len(stuck_tasks)} stuck tasks")

            return stuck_tasks

        except Exception as e:
            logger.error(f"Error getting stuck tasks: {e}")
            return []