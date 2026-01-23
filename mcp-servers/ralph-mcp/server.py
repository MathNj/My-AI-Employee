#!/usr/bin/env python3
"""
Ralph MCP Server

Model Context Protocol server for Ralph Loop autonomous task completion.
Provides tools for task queue management, progress tracking, and iteration control.

Features:
- Task queue management (list, claim, get details)
- Progress tracking (update, get, check completion)
- Iteration control (should_continue, increment)
- State persistence (JSON files)
- Comprehensive error handling and logging
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

# Import Ralph Core
try:
    from ralph_core import RalphCore
    RALPH_CORE_AVAILABLE = True
except ImportError:
    RALPH_CORE_AVAILABLE = False
    print("ERROR: ralph_core not available", file=sys.stderr)
    sys.exit(1)

# Setup logging
LOG_PATH = Path(__file__).parent / 'logs'
LOG_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RalphMCP - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH / 'ralph-mcp.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class RalphMCPServer:
    """Ralph MCP Server implementation"""

    def __init__(self, vault_path: str):
        """
        Initialize MCP server

        Args:
            vault_path: Path to AI Employee vault
        """
        self.ralph = RalphCore(vault_path)
        logger.info("Ralph MCP Server initialized")

    def list_pending_tasks(self, arguments: dict) -> dict:
        """
        List all tasks in /Needs_Action folder

        Returns:
            List of task dictionaries with metadata
        """
        try:
            priority_filter = arguments.get('priority')
            type_filter = arguments.get('type')

            tasks = self.ralph.list_pending_tasks()

            # Apply filters
            if priority_filter:
                tasks = [t for t in tasks if t['priority'] == priority_filter]
            if type_filter:
                tasks = [t for t in tasks if t['type'] == type_filter]

            return {
                'success': True,
                'count': len(tasks),
                'tasks': tasks
            }

        except Exception as e:
            logger.error(f"Error in list_pending_tasks: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def claim_next_task(self, arguments: dict) -> dict:
        """
        Claim next available task for processing

        Returns:
            Task file path or None
        """
        try:
            priority = arguments.get('priority')
            task_type = arguments.get('type')

            task_path = self.ralph.claim_next_task(priority=priority, task_type=task_type)

            if task_path:
                return {
                    'success': True,
                    'task_path': task_path
                }
            else:
                return {
                    'success': False,
                    'error': 'No tasks available'
                }

        except Exception as e:
            logger.error(f"Error in claim_next_task: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_task_details(self, arguments: dict) -> dict:
        """
        Get full task content and metadata

        Returns:
            Task content with YAML frontmatter
        """
        try:
            task_file = arguments.get('task_file')

            if not task_file:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_file'
                }

            details = self.ralph.get_task_details(task_file)

            if details:
                return {
                    'success': True,
                    'data': details
                }
            else:
                return {
                    'success': False,
                    'error': 'Task file not found'
                }

        except Exception as e:
            logger.error(f"Error in get_task_details: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def create_ralph_state(self, arguments: dict) -> dict:
        """
        Create Ralph state for a new task

        Returns:
            Ralph state details
        """
        try:
            task_file = arguments.get('task_file')
            prompt = arguments.get('prompt')
            max_iterations = arguments.get('max_iterations', 10)
            completion_strategy = arguments.get('completion_strategy', 'file_movement')

            if not task_file or not prompt:
                return {
                    'success': False,
                    'error': 'Missing required parameters: task_file, prompt'
                }

            state = self.ralph.create_ralph_state(
                task_file=task_file,
                prompt=prompt,
                max_iterations=max_iterations,
                completion_strategy=completion_strategy
            )

            return {
                'success': True,
                'data': state.to_dict()
            }

        except Exception as e:
            logger.error(f"Error in create_ralph_state: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def update_progress(self, arguments: dict) -> dict:
        """
        Update task progress in Ralph state

        Returns:
            Updated state
        """
        try:
            task_id = arguments.get('task_id')
            status = arguments.get('status')
            notes = arguments.get('notes')

            if not task_id or not status:
                return {
                    'success': False,
                    'error': 'Missing required parameters: task_id, status'
                }

            state = self.ralph.update_progress(task_id, status, notes)

            if state:
                return {
                    'success': True,
                    'data': state.to_dict()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to update progress'
                }

        except Exception as e:
            logger.error(f"Error in update_progress: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_progress(self, arguments: dict) -> dict:
        """
        Get current progress for a task

        Returns:
            Progress details with history
        """
        try:
            task_id = arguments.get('task_id')

            if not task_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_id'
                }

            progress = self.ralph.get_progress(task_id)

            if progress:
                return {
                    'success': True,
                    'data': progress
                }
            else:
                return {
                    'success': False,
                    'error': 'Task state not found'
                }

        except Exception as e:
            logger.error(f"Error in get_progress: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def check_completion(self, arguments: dict) -> dict:
        """
        Check if task is complete

        Returns:
            Boolean + completion status
        """
        try:
            task_id = arguments.get('task_id')

            if not task_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_id'
                }

            completion = self.ralph.check_completion(task_id)

            return {
                'success': True,
                'data': completion
            }

        except Exception as e:
            logger.error(f"Error in check_completion: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def should_continue(self, arguments: dict) -> dict:
        """
        Check if Ralph should continue looping

        Returns:
            should_continue + reason
        """
        try:
            task_id = arguments.get('task_id')

            if not task_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_id'
                }

            result = self.ralph.should_continue(task_id)

            return {
                'success': True,
                'data': result
            }

        except Exception as e:
            logger.error(f"Error in should_continue: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def increment_iteration(self, arguments: dict) -> dict:
        """
        Increment iteration counter

        Returns:
            New iteration count
        """
        try:
            task_id = arguments.get('task_id')

            if not task_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_id'
                }

            iteration = self.ralph.increment_iteration(task_id)

            if iteration is not None:
                return {
                    'success': True,
                    'data': {
                        'iteration': iteration
                    }
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to increment iteration'
                }

        except Exception as e:
            logger.error(f"Error in increment_iteration: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def archive_state(self, arguments: dict) -> dict:
        """
        Archive completed task state

        Returns:
            Success status
        """
        try:
            task_id = arguments.get('task_id')

            if not task_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_id'
                }

            success = self.ralph.archive_state(task_id)

            return {
                'success': success,
                'data': {
                    'task_id': task_id,
                    'archived': success
                }
            }

        except Exception as e:
            logger.error(f"Error in archive_state: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Multi-Task Orchestration
    # ========================================================================

    def create_task_group(self, arguments: dict) -> dict:
        """Create a task group for batch processing"""
        try:
            task_ids = arguments.get('task_ids', [])
            group_name = arguments.get('group_name')
            strategy = arguments.get('strategy', 'sequential')

            if not task_ids or not group_name:
                return {
                    'success': False,
                    'error': 'Missing required parameters: task_ids, group_name'
                }

            result = self.ralph.create_task_group(
                task_ids=task_ids,
                group_name=group_name,
                strategy=strategy
            )

            return result

        except Exception as e:
            logger.error(f"Error in create_task_group: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def process_task_group(self, arguments: dict) -> dict:
        """Process all tasks in a group"""
        try:
            group_id = arguments.get('group_id')

            if not group_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: group_id'
                }

            result = self.ralph.process_task_group(group_id)

            return result

        except Exception as e:
            logger.error(f"Error in process_task_group: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Smart Task Discovery
    # ========================================================================

    def discover_blocking_issues(self, arguments: dict) -> dict:
        """Find tasks blocking other tasks"""
        try:
            return self.ralph.discover_blocking_issues()
        except Exception as e:
            logger.error(f"Error in discover_blocking_issues: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def estimate_effort(self, arguments: dict) -> dict:
        """Estimate task effort based on type and complexity"""
        try:
            task_file = arguments.get('task_file')

            if not task_file:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_file'
                }

            result = self.ralph.estimate_effort(task_file)

            return result

        except Exception as e:
            logger.error(f"Error in estimate_effort: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Approval Workflow Integration
    # ========================================================================

    def check_approval_status(self, arguments: dict) -> dict:
        """Check if pending approval is approved/rejected"""
        try:
            task_id = arguments.get('task_id')

            if not task_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_id'
                }

            result = self.ralph.check_approval_status(task_id)

            return result

        except Exception as e:
            logger.error(f"Error in check_approval_status: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def wait_for_approval(self, arguments: dict) -> dict:
        """Wait (with timeout) for human approval"""
        try:
            task_id = arguments.get('task_id')
            timeout_minutes = arguments.get('timeout_minutes', 60)
            poll_interval_seconds = arguments.get('poll_interval_seconds', 30)

            if not task_id:
                return {
                    'success': False,
                    'error': 'Missing required parameter: task_id'
                }

            result = self.ralph.wait_for_approval(
                task_id=task_id,
                timeout_minutes=timeout_minutes,
                poll_interval_seconds=poll_interval_seconds
            )

            return result

        except Exception as e:
            logger.error(f"Error in wait_for_approval: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Performance Metrics
    # ========================================================================

    def get_performance_metrics(self, arguments: dict) -> dict:
        """Get Ralph loop performance metrics"""
        try:
            time_range = arguments.get('time_range', 'all')

            result = self.ralph.get_performance_metrics(time_range)

            return result

        except Exception as e:
            logger.error(f"Error in get_performance_metrics: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    # ========================================================================
    # PHASE 2: Health Monitoring
    # ========================================================================

    def get_ralph_health(self, arguments: dict) -> dict:
        """Get Ralph loop system health"""
        try:
            result = self.ralph.get_ralph_health()

            return result

        except Exception as e:
            logger.error(f"Error in get_ralph_health: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def get_stuck_tasks(self, arguments: dict) -> dict:
        """Find tasks that exceeded max iterations"""
        try:
            result = self.ralph.get_stuck_tasks()

            return {
                'success': True,
                'data': result
            }

        except Exception as e:
            logger.error(f"Error in get_stuck_tasks: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


def main():
    """Main MCP server loop"""
    import os

    vault_path = os.getenv('VAULT_PATH', str(Path(__file__).parent.parent.parent))
    server = RalphMCPServer(vault_path)

    logger.info("Ralph MCP Server started")
    logger.info(f"Vault path: {vault_path}")
    logger.info("Waiting for requests...")

    try:
        # Read from stdin, write to stdout (MCP protocol)
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                # Parse JSON-RPC request
                request = json.loads(line)

                # Process request
                response = None

                if request.get('method') == 'tools/call':
                    # Handle tool call
                    params = request.get('params', {})
                    tool_name = params.get('name')
                    arguments = params.get('arguments', {})

                    logger.info(f"Tool call: {tool_name}")

                    # Route to appropriate method
                    method_map = {
                        'list_pending_tasks': server.list_pending_tasks,
                        'claim_next_task': server.claim_next_task,
                        'get_task_details': server.get_task_details,
                        'create_ralph_state': server.create_ralph_state,
                        'update_progress': server.update_progress,
                        'get_progress': server.get_progress,
                        'check_completion': server.check_completion,
                        'should_continue': server.should_continue,
                        'increment_iteration': server.increment_iteration,
                        'archive_state': server.archive_state,
                        # Phase 2 tools
                        'create_task_group': server.create_task_group,
                        'process_task_group': server.process_task_group,
                        'discover_blocking_issues': server.discover_blocking_issues,
                        'estimate_effort': server.estimate_effort,
                        'check_approval_status': server.check_approval_status,
                        'wait_for_approval': server.wait_for_approval,
                        'get_performance_metrics': server.get_performance_metrics,
                        'get_ralph_health': server.get_ralph_health,
                        'get_stuck_tasks': server.get_stuck_tasks,
                    }

                    if tool_name in method_map:
                        result = method_map[tool_name](arguments)

                        response = {
                            'jsonrpc': '2.0',
                            'id': request.get('id'),
                            'result': {
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': json.dumps(result, indent=2)
                                    }
                                ]
                            }
                        }
                    else:
                        response = {
                            'jsonrpc': '2.0',
                            'id': request.get('id'),
                            'error': {
                                'code': -32601,
                                'message': f'Unknown tool: {tool_name}'
                            }
                        }

                elif request.get('method') == 'tools/list':
                    # List available tools
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {
                            'tools': [
                                {
                                    'name': 'list_pending_tasks',
                                    'description': 'List all tasks in /Needs_Action folder',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'priority': {'type': 'string', 'description': 'Filter by priority'},
                                            'type': {'type': 'string', 'description': 'Filter by task type'}
                                        }
                                    }
                                },
                                {
                                    'name': 'claim_next_task',
                                    'description': 'Claim next available task for processing',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'priority': {'type': 'string', 'description': 'Filter by priority'},
                                            'type': {'type': 'string', 'description': 'Filter by task type'}
                                        }
                                    }
                                },
                                {
                                    'name': 'get_task_details',
                                    'description': 'Get full task content and metadata',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_file': {'type': 'string', 'description': 'Path to task file'}
                                        },
                                        'required': ['task_file']
                                    }
                                },
                                {
                                    'name': 'create_ralph_state',
                                    'description': 'Create Ralph state for a new task',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_file': {'type': 'string'},
                                            'prompt': {'type': 'string'},
                                            'max_iterations': {'type': 'integer', 'default': 10},
                                            'completion_strategy': {'type': 'string', 'default': 'file_movement'}
                                        },
                                        'required': ['task_file', 'prompt']
                                    }
                                },
                                {
                                    'name': 'update_progress',
                                    'description': 'Update task progress',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'},
                                            'status': {'type': 'string'},
                                            'notes': {'type': 'string'}
                                        },
                                        'required': ['task_id', 'status']
                                    }
                                },
                                {
                                    'name': 'get_progress',
                                    'description': 'Get current progress',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'}
                                        },
                                        'required': ['task_id']
                                    }
                                },
                                {
                                    'name': 'check_completion',
                                    'description': 'Check if task is complete',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'}
                                        },
                                        'required': ['task_id']
                                    }
                                },
                                {
                                    'name': 'should_continue',
                                    'description': 'Check if Ralph should continue looping',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'}
                                        },
                                        'required': ['task_id']
                                    }
                                },
                                {
                                    'name': 'increment_iteration',
                                    'description': 'Increment iteration counter',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'}
                                        },
                                        'required': ['task_id']
                                    }
                                },
                                {
                                    'name': 'archive_state',
                                    'description': 'Archive completed task state',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'}
                                        },
                                        'required': ['task_id']
                                    }
                                },
                                {
                                    'name': 'create_task_group',
                                    'description': 'Create a task group for batch processing',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_ids': {'type': 'array', 'items': {'type': 'string'}},
                                            'group_name': {'type': 'string'},
                                            'strategy': {'type': 'string', 'enum': ['sequential', 'parallel']}
                                        },
                                        'required': ['task_ids', 'group_name']
                                    }
                                },
                                {
                                    'name': 'process_task_group',
                                    'description': 'Process all tasks in a group',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'group_id': {'type': 'string'}
                                        },
                                        'required': ['group_id']
                                    }
                                },
                                {
                                    'name': 'discover_blocking_issues',
                                    'description': 'Find tasks blocking other tasks',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {}
                                    }
                                },
                                {
                                    'name': 'estimate_effort',
                                    'description': 'Estimate task effort based on type and complexity',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_file': {'type': 'string'}
                                        },
                                        'required': ['task_file']
                                    }
                                },
                                {
                                    'name': 'check_approval_status',
                                    'description': 'Check if pending approval is approved/rejected',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'}
                                        },
                                        'required': ['task_id']
                                    }
                                },
                                {
                                    'name': 'wait_for_approval',
                                    'description': 'Wait (with timeout) for human approval',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'task_id': {'type': 'string'},
                                            'timeout_minutes': {'type': 'integer', 'default': 60},
                                            'poll_interval_seconds': {'type': 'integer', 'default': 30}
                                        },
                                        'required': ['task_id']
                                    }
                                },
                                {
                                    'name': 'get_performance_metrics',
                                    'description': 'Get Ralph loop performance metrics',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'time_range': {'type': 'string', 'enum': ['today', 'week', 'month', 'all'], 'default': 'all'}
                                        }
                                    }
                                },
                                {
                                    'name': 'get_ralph_health',
                                    'description': 'Get Ralph loop system health',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {}
                                    }
                                },
                                {
                                    'name': 'get_stuck_tasks',
                                    'description': 'Find tasks that exceeded max iterations',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {}
                                    }
                                }
                            ]
                        }
                    }

                else:
                    # Unknown method
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'error': {
                            'code': -32601,
                            'message': f'Method not found: {request.get("method")}'
                        }
                    }

                # Send response
                if response:
                    sys.stdout.write(json.dumps(response) + '\n')
                    sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                continue

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        logger.info("Ralph MCP Server stopped")


if __name__ == "__main__":
    main()
