#!/usr/bin/env python3
"""
Ralph MCP Integration Script

Integrates Ralph Loop skill with Ralph MCP Server for state management
and progress tracking. Provides autonomous task completion with MCP tools.

Usage:
    python ralph_mcp.py --max-iterations 10 --priority high
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add MCP server to path
script_dir = Path(__file__).parent
vault_root = script_dir.parent.parent.parent.parent
mcp_path = vault_root / 'mcp-servers' / 'ralph-mcp'
sys.path.insert(0, str(mcp_path))

from ralph_core import RalphCore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - RalphLoop - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RalphMCPIntegration:
    """Ralph Loop integration with MCP server"""

    def __init__(
        self,
        vault_path: str,
        max_iterations: int = 10,
        priority: Optional[str] = None,
        task_type: Optional[str] = None
    ):
        """
        Initialize Ralph MCP integration

        Args:
            vault_path: Path to AI Employee vault
            max_iterations: Maximum loop iterations
            priority: Filter tasks by priority
            task_type: Filter tasks by type
        """
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations
        self.priority = priority
        self.task_type = task_type

        # Initialize Ralph Core
        self.ralph = RalphCore(str(self.vault_path))

        # Ralph directories
        self.ralph_dir = self.vault_path / "Ralph"
        self.progress_file = self.ralph_dir / "progress_mcp.txt"

        # Create directories
        self.ralph_dir.mkdir(exist_ok=True)

        logger.info(f"Ralph MCP Integration initialized")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Max iterations: {max_iterations}")
        logger.info(f"  Priority filter: {priority or 'None'}")
        logger.info(f"  Type filter: {task_type or 'None'}")

    def run(self) -> int:
        """
        Run Ralph loop with MCP integration

        Returns:
            Exit code (0 = success, 1 = failure)
        """
        # Initialize progress file
        self._init_progress_file()

        # Claim next task
        logger.info("Claiming next task...")
        task_path = self.ralph.claim_next_task(
            priority=self.priority,
            task_type=self.task_type
        )

        if not task_path:
            logger.warning("No tasks available to process")
            return 0

        logger.info(f"Claimed task: {Path(task_path).name}")

        # Get task details
        task_details = self.ralph.get_task_details(task_path)
        if not task_details:
            logger.error("Failed to get task details")
            return 1

        # Create prompt from task
        prompt = self._create_prompt(task_details)

        # Create Ralph state
        logger.info("Creating Ralph state...")
        state = self.ralph.create_ralph_state(
            task_file=task_path,
            prompt=prompt,
            max_iterations=self.max_iterations,
            completion_strategy="file_movement"
        )

        logger.info(f"Task ID: {state.task_id}")
        logger.info(f"Max iterations: {state.max_iterations}")

        # Main Ralph loop
        logger.info("")
        logger.info("Starting Ralph loop...")
        logger.info("")

        for iteration in range(1, self.max_iterations + 1):
            logger.info("=" * 70)
            logger.info(f"RALPH ITERATION {iteration}/{self.max_iterations}")
            logger.info("=" * 70)
            logger.info("")

            # Check if should continue
            should_continue_result = self.ralph.should_continue(state.task_id)
            if not should_continue_result['should_continue']:
                logger.info(f"Stopping: {should_continue_result['reason']}")
                self._update_progress(f"Iteration {iteration}: {should_continue_result['reason']}")

                if "complete" in should_continue_result['reason'].lower():
                    logger.info("")
                    logger.info("✓ TASK COMPLETE!")
                    return 0
                else:
                    logger.warning("")
                    logger.warning("⚠ Task incomplete")
                    return 1

            # Update progress
            self._update_progress(f"Iteration {iteration}: Processing task...")

            # Claude processes task here
            # In actual use, this would be handled by Claude Code
            logger.info(f"Task: {task_details['metadata'].get('type', 'unknown')}")
            logger.info(f"File: {task_details['file_name']}")
            logger.info("")
            logger.info("ACTION REQUIRED:")
            logger.info("  Claude Code should process this task now.")
            logger.info("  When complete, move the task file to /Done")
            logger.info("")

            # Check if complete
            completion = self.ralph.check_completion(state.task_id)
            if completion['complete']:
                logger.info(f"✓ Task complete: {completion['reason']}")
                self._update_progress(f"Iteration {iteration}: Task complete - {completion['reason']}")

                # Archive state
                self.ralph.archive_state(state.task_id)
                logger.info(f"State archived: {state.task_id}")

                logger.info("")
                logger.info("=" * 70)
                logger.info("RALPH LOOP COMPLETE")
                logger.info("=" * 70)
                return 0

            # Update progress state
            self.ralph.update_progress(
                task_id=state.task_id,
                status="in_progress",
                notes=f"Iteration {iteration} - Processing task"
            )

            # Increment iteration
            self.ralph.increment_iteration(state.task_id)

            # Wait before next iteration
            if iteration < self.max_iterations:
                logger.info("")
                logger.info("Task incomplete. Waiting 2 seconds before next iteration...")
                logger.info("")
                import time
                time.sleep(2)

        # Max iterations reached
        logger.warning("")
        logger.warning("=" * 70)
        logger.warning("MAX ITERATIONS REACHED")
        logger.warning("=" * 70)
        logger.warning(f"Task did not complete after {self.max_iterations} iterations")
        logger.warning("Task ID: " + state.task_id)
        logger.warning("")
        logger.warning("Consider:")
        logger.warning("  - Increasing max iterations")
        logger.warning("  - Splitting task into smaller sub-tasks")
        logger.warning("  - Checking for errors in progress file")
        logger.warning("")

        return 1

    def _create_prompt(self, task_details: dict) -> str:
        """Create prompt from task details"""
        metadata = task_details['metadata']
        body = task_details['body']

        prompt = f"""Process this task and move it to /Done when complete.

Task Type: {metadata.get('type', 'unknown')}
Priority: {metadata.get('priority', 'medium')}
File: {task_details['file_name']}

Task Details:
{body}

Instructions:
1. Read the full task content
2. Process according to task type
3. Take necessary actions (create approvals, send messages, etc.)
4. Move the task file to /Done when complete
5. Use appropriate MCP servers for actions

Complete the task and move the file to /Done to signal completion.
"""
        return prompt

    def _init_progress_file(self):
        """Initialize progress file"""
        if not self.progress_file.exists():
            content = f"""# Ralph Progress Log (MCP Integration)
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Vault: {self.vault_path}
Max Iterations: {self.max_iterations}

---

## Progress

"""
            self.progress_file.write_text(content, encoding='utf-8')

    def _update_progress(self, message: str):
        """Update progress file"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        entry = f"\n## {timestamp}\n{message}\n"

        with open(self.progress_file, 'a', encoding='utf-8') as f:
            f.write(entry)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Ralph Loop with MCP Integration',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process next high-priority task (max 10 iterations)
  python ralph_mcp.py --priority high

  # Process next email task (max 15 iterations)
  python ralph_mcp.py --type email --max-iterations 15

  # Process any available task
  python ralph_mcp.py
        """
    )

    parser.add_argument(
        '--vault-path',
        default=str(vault_root),
        help='Path to AI Employee vault'
    )
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum loop iterations (default: 10)'
    )
    parser.add_argument(
        '--priority',
        choices=['high', 'medium', 'low'],
        help='Filter tasks by priority'
    )
    parser.add_argument(
        '--type',
        help='Filter tasks by type (email, whatsapp, etc.)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Run Ralph loop
    ralph = RalphMCPIntegration(
        vault_path=args.vault_path,
        max_iterations=args.max_iterations,
        priority=args.priority,
        task_type=args.type
    )

    try:
        exit_code = ralph.run()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("")
        logger.info("Ralph loop interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
