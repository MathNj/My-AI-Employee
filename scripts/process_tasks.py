#!/usr/bin/env python3
"""
Process Tasks Script

Core processing loop for AI Employee task processing.
Monitors /Needs_Action folder, creates action plans, executes approved actions, archives completed tasks.

Based on Silver Tier Phase 4 (T041, T054, T055) and Phase 5 (T054, T055).
Silver Tier Requirement 4: Claude reasoning loop that creates Plan.md files (T068, T073).
"""

import os
import sys
import time
import json
import logging
import shutil
import subprocess
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import defaultdict

# Configure UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Setup logging
log_dir = Path("/Logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "task_processor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ProcessTasks")


# ============================================================================
# MCP Action Queue (T055)
# ============================================================================

class MCPActionQueue:
    """
    MCP Action Queue for managing external service invocations

    Queues pending actions, processes sequentially, tracks status,
    and retries failed actions (up to 3 attempts).

    Logs all invocations to /Logs/mcp_actions.json
    """

    def __init__(self, queue_path: str = None):
        """
        Initialize MCP Action Queue

        Args:
            queue_path: Path to queue JSON file (default: /Needs_Action/mcp_queue.json)
        """
        self.queue_path = queue_path or "/Needs_Action/mcp_queue.json"
        self.log_path = "/Logs/mcp_actions.json"
        self.max_retries = 3

        # Initialize queue file
        self._ensure_queue_exists()

    def _ensure_queue_exists(self):
        """Create queue file if it doesn't exist"""
        queue_file = Path(self.queue_path)
        queue_file.parent.mkdir(parents=True, exist_ok=True)

        if not queue_file.exists():
            with open(queue_file, 'w') as f:
                json.dump({"queued": [], "processing": [], "completed": [], "failed": []}, f)

        # Ensure log directory exists
        log_file = Path(self.log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        if not log_file.exists():
            with open(log_file, 'w') as f:
                json.dump([], f)

    def enqueue(self, action_type: str, tool: str, params: dict, approval_file: str = None) -> str:
        """
        Add an action to the queue

        Args:
            action_type: Type of action (send_email, post_linkedin, etc.)
            tool: MCP server tool name
            params: Parameters to pass to the tool
            approval_file: Path to approval request file

        Returns:
            Action ID
        """
        try:
            action_id = f"{action_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

            action = {
                "action_id": action_id,
                "timestamp": datetime.now().isoformat(),
                "action_type": action_type,
                "tool": tool,
                "params": params,
                "status": "queued",
                "attempts": 0,
                "approval_file": approval_file
            }

            # Load current queue
            with open(self.queue_path, 'r') as f:
                queue = json.load(f)

            # Add to queued
            queue["queued"].append(action)

            # Save queue
            with open(self.queue_path, 'w') as f:
                json.dump(queue, f, indent=2)

            logger.info(f"[MCP-QUEUE] Enqueued action: {action_id}")
            return action_id

        except Exception as e:
            logger.error(f"[ERROR] Failed to enqueue action: {e}")
            return None

    def process_queue(self) -> Dict[str, int]:
        """
        Process all queued actions

        Returns:
            Summary of processing: {succeeded: count, failed: count, retried: count}
        """
        try:
            with open(self.queue_path, 'r') as f:
                queue = json.load(f)

            queued = queue.get("queued", [])
            results = {"succeeded": 0, "failed": 0, "retried": 0}

            # Process each queued action
            for action in queued:
                action_id = action["action_id"]
                logger.info(f"[MCP-QUEUE] Processing action: {action_id}")

                # Move to processing
                queue["processing"].append(action)

                # Invoke MCP tool
                result = self._invoke_mcp_tool(action)

                if result.get("success"):
                    # Success: move to completed
                    action["status"] = "succeeded"
                    action["result"] = result
                    action["completed_at"] = datetime.now().isoformat()
                    queue["completed"].append(action)
                    results["succeeded"] += 1

                    # Log to mcp_actions.json
                    self._log_action(action, result)

                else:
                    # Failure: retry or fail
                    action["attempts"] += 1

                    if action["attempts"] < self.max_retries:
                        # Re-queue for retry
                        action["status"] = "queued"
                        queue["queued"].append(action)
                        results["retried"] += 1
                        logger.warning(f"[MCP-QUEUE] Retrying action: {action_id} (attempt {action['attempts']})")
                    else:
                        # Max retries reached
                        action["status"] = "failed"
                        action["error"] = result.get("error", "Unknown error")
                        action["failed_at"] = datetime.now().isoformat()
                        queue["failed"].append(action)
                        results["failed"] += 1

                        # Log failure
                        self._log_action(action, result)

            # Clear processed actions from queued
            queue["queued"] = []

            # Save updated queue
            with open(self.queue_path, 'w') as f:
                json.dump(queue, f, indent=2)

            logger.info(f"[MCP-QUEUE] Processing complete: {results}")
            return results

        except Exception as e:
            logger.error(f"[ERROR] Failed to process queue: {e}")
            return {"succeeded": 0, "failed": 0, "retried": 0}

    def _invoke_mcp_tool(self, action: dict) -> dict:
        """
        Invoke MCP server tool (T054)

        Args:
            action: Action dict with tool and params

        Returns:
            Result dict with success and result/error
        """
        try:
            tool = action["tool"]
            params = action["params"]

            logger.info(f"[MCP] Invoking tool: {tool} with params: {params}")

            # TODO: Actual MCP server invocation
            # For Silver Tier, this is a placeholder that will be implemented
            # when the MCP server infrastructure is fully operational
            #
            # Future implementation:
            # - Connect to MCP server via stdio or HTTP
            # - Call tool with params
            # - Parse response
            # - Handle errors

            # Placeholder response
            logger.info(f"[MCP] TODO: Invoke {tool} MCP server (placeholder)")
            return {
                "success": True,
                "result": {
                    "message": f"Action {action['action_type']} completed (placeholder)",
                    "tool": tool,
                    "params": params
                }
            }

        except Exception as e:
            logger.error(f"[ERROR] MCP invocation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _log_action(self, action: dict, result: dict):
        """
        Log MCP action to /Logs/mcp_actions.json

        Args:
            action: Action dict
            result: Result dict from invocation
        """
        try:
            log_entry = {
                "timestamp": action.get("timestamp"),
                "action_id": action.get("action_id"),
                "action_type": action.get("action_type"),
                "tool": action.get("tool"),
                "params": action.get("params"),
                "status": action.get("status"),
                "attempts": action.get("attempts"),
                "approval_file": action.get("approval_file"),
                "result": result,
                "logged_at": datetime.now().isoformat()
            }

            # Append to log file
            with open(self.log_path, 'r') as f:
                logs = json.load(f)

            logs.append(log_entry)

            # Save log file
            with open(self.log_path, 'w') as f:
                json.dump(logs, f, indent=2)

            logger.debug(f"[MCP-LOG] Logged action: {action['action_id']}")

        except Exception as e:
            logger.error(f"[ERROR] Failed to log action: {e}")

    def get_queue_status(self) -> dict:
        """
        Get current queue status

        Returns:
            Dict with counts: queued, processing, completed, failed
        """
        try:
            with open(self.queue_path, 'r') as f:
                queue = json.load(f)

            return {
                "queued": len(queue.get("queued", [])),
                "processing": len(queue.get("processing", [])),
                "completed": len(queue.get("completed", [])),
                "failed": len(queue.get("failed", []))
            }

        except Exception as e:
            logger.error(f"[ERROR] Failed to get queue status: {e}")
            return {"queued": 0, "processing": 0, "completed": 0, "failed": 0}


class ApprovalProcessor:
    """
    Handles approval workflow: monitors /Approved folder, executes approved actions,
    moves files to /Done or /Rejected with status and reasons.
    """

    def __init__(self):
        self.approved_folder = Path("/Approved")
        self.rejected_folder = Path("/Rejected")
        self.done_folder = "/Done"
        self.check_interval = 5  # Check every 5 seconds
        self.mcp_queue = MCPActionQueue()  # T055: MCP Action Queue

    def check_approved_folder(self) -> List[Path]:
        """
        Check /Approved folder for approval requests to execute

        Returns:
            List of approved file paths
        """
        try:
            approved_folder = Path(self.approved_folder)
            if not approved_folder.exists():
                return []

            # Find all markdown files in /Approved
            approved_files = list(approved_folder.glob("*.md"))

            if approved_files:
                logger.info(f"[APPROVAL] Found {len(approved_files)} approved files")

            return approved_files

        except Exception as e:
            logger.error(f"[ERROR] Failed to check /Approved folder: {e}")
            return []

    def execute_approved_action(self, file_path: Path) -> bool:
        """
        Execute an approved action based on its type

        Args:
            file_path: Path to approved file

        Returns:
            True if execution succeeded, False otherwise
        """
        try:
            logger.info(f"[APPROVAL] Executing approved action: {file_path.name}")

            # Read file to get action details
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract frontmatter (if exists)
            if content.startswith('---'):
                _, frontmatter, content = content.split('---', 2)
                frontmatter_dict = self._parse_yaml_frontmatter(frontmatter)

                action_type = frontmatter_dict.get('action_type', '')
                target = frontmatter.get('target', '')
                data = frontmatter_dict.get('data', {})

                # Execute based on action type
                if action_type == 'SEND_EMAIL':
                    return self._execute_email(target, data, file_path, content)
                elif action_type == 'POST_LINKEDIN':
                    return self._execute_linkedin(data, file_path, content)
                elif action_type == 'POST_FACEBOOK':
                    return self._execute_facebook(data, file_path,)
                elif action_type == 'POST_INSTAGRAM':
                    return self._execute_instagram(data, file_path, content)
                elif action_type == 'PROCESS_PAYMENT':
                    return self._execute_payment(data, file_path, content)
                elif action_type == 'DELETE_FILE':
                    return self._execute_delete_file(data, file_path, content)
                else:
                    logger.warning(f"[APPROVAL] Unknown action type: {action_type}")
                    return False
            else:
                # No frontmatter, try to infer from content
                logger.warning(f"[APPROVAL] No frontmatter found, skipping execution")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Failed to execute approved action: {e}")
            return False

    def _execute_email(self, to: str, data: dict, file_path: Path, content: str) -> bool:
        """
        Execute email sending via MCP Gmail server (T054)

        Args:
            to: Recipient email address
            data: Email content (subject, body, attachments)
            file_path: Path to approval file
            content: Approval file content

        Returns:
            True if email queued/sent successfully, False otherwise
        """
        try:
            logger.info(f"[ACTION] Sending email to: {to}")

            # Build email parameters
            email_params = {
                "to": to,
                "subject": data.get("subject", ""),
                "body": data.get("body"),
                "html": data.get("html"),
                "cc": data.get("cc"),
                "bcc": data.get("bcc"),
                "attachments": data.get("attachments", [])
            }

            # Enqueue action to MCP queue (T055)
            action_id = self.mcp_queue.enqueue(
                action_type="send_email",
                tool="gmail-send",
                params=email_params,
                approval_file=str(file_path)
            )

            if action_id:
                logger.info(f"[MCP-QUEUE] Email action queued: {action_id}")

                # Process queue immediately
                results = self.mcp_queue.process_queue()

                if results["succeeded"] > 0:
                    logger.info(f"[OK] Email sent successfully via MCP: {action_id}")
                    return True
                elif results["retried"] > 0:
                    logger.warning(f"[WARN] Email queued for retry: {action_id}")
                    return True  # Still return True as it's being retried
                else:
                    logger.error(f"[ERROR] Email failed to send: {action_id}")
                    return False
            else:
                logger.error("[ERROR] Failed to enqueue email action")
                return False

        except Exception as e:
            logger.error(f"[ERROR] Email execution failed: {e}")
            return False

    def _execute_linkedin(self, data: dict, file_path: Path, content: str) -> bool:
        """Execute LinkedIn post via linkedin-poster skill"""
        # Placeholder for LinkedIn posting
        logger.info(f"[ACTION] Would post to LinkedIn: {data.get('content', '')}")
        return True  # Placeholder

    def _execute_facebook(self, data: dict, file_path: Path, content: str) -> bool:
        """Execute Facebook post via facebook-mcp server"""
        # Placeholder for Facebook posting
        logger.info(f"[ACTION] Would post to Facebook: {data.get('content', '')}")
        return True  # Placeholder

    def _execute_instagram(self, data: dict, file_path: Path, content: str) -> bool:
        """Execute Instagram post via instagram-mcp server"""
        # Placeholder for Instagram posting
        logger.info(f"[ACTION] Would post to Instagram: {data.get('content', '')}")
        return True  # Placeholder

    def _execute_payment(self, data: dict, file_path: Path, content: str) -> bool:
        """Execute payment via Xero MCP"""
        # Placeholder for payment execution
        logger.info(f"[ACTION] Would execute payment: {data.get('amount', '')} {data.get('currency', '')}")
        return True  # Placeholder

    def _execute_delete_file(self, data: dict, file_path: Path, content: str) -> bool:
        """Execute file deletion"""
        try:
            file_to_delete = data.get('file_path', '')
            if Path(file_to_delete).exists():
                os.remove(file_to_delete)
                logger.info(f"[OK] Deleted file: {file_to_delete}")
                return True
            else:
                logger.warning(f"[WARN] File not found: {file_to_delete}")
                return False
        except Exception as e:
            logger.error(f"[ERROR] File deletion failed: {e}")
            return False

    def _parse_yaml_frontmatter(self, frontmatter: str) -> Dict:
        """
        Parse YAML frontmatter string into dictionary

        Args:
            frontmatter: YAML frontmatter string (between --- markers)

        Returns:
            Dictionary of parsed key-value pairs
        """
        try:
            result = {}
            for line in frontmatter.strip().split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    result[key.strip()] = value.strip()
            return result
        except Exception as e:
            logger.warning(f"[WARN] Failed to parse frontmatter: {e}")
            return {}

    def process_rejected_action(self, file_path: Path) -> bool:
        """
        Move rejected file to /Done with rejection reason

        Args:
            file_path: Path to rejected file

        Returns:
            True if file moved to /Done with rejection reason, False otherwise
        """
        try:
            logger.info(f"[REJECT] Moving rejected file to /Done: {file_path.name}")

            # Create rejection reason
            rejection_reason = f"Rejected by user at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            # Read file to get context
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update status in file
            content = content.replace("status: pending", f"status: rejected\\nreason: {rejection_reason}")

            # Write updated content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Move to /Done
            done_path = Path(self.done_folder)
            shutil.move(str(file_path), str(done_path / file_path.name))

            logger.info(f"[OK] Rejected file moved to /Done: {file_path.name} → {done_path / file_path.name}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to process rejected action: {e}")
            return False

    def process_approved_actions(self) -> Dict[str, int]:
        """
        Main loop: Check /Approved folder, execute all approved actions

        Returns:
            Summary of processing results: {success: count, failure: count}
        """
        try:
            approved_files = self.check_approved_folder()

            success_count = 0
            failure_count = 0

            for approved_file in approved_files:
                logger.info(f"[APPROVAL] Processing: {approved_file.name}")

                # Execute the approved action
                success = self.execute_approved_action(approved_file)

                if success:
                    # Move to /Done
                    done_folder = Path(self.done_folder)
                    shutil.move(str(approved_file), str(done_folder / approved_file.name))
                    logger.info(f"[OK] Approved action completed: {approved_file.name}")
                    success_count += 1
                else:
                    # Move to /Failed
                    failed_folder = Path("/Failed")
                    shutil.copy(str(approved_file), str(failed_folder / approved_file.name))
                    logger.warning(f"[FAIL] Approved action failed: {approved_file.name}")
                    failure_count += 1

            logger.info(f"[APPROVAL] Processing complete: {success_count} succeeded, {failure_count} failed")
            return {"success": success_count, "failure": failure_count}

        except Exception as e:
            logger.error(f"[ERROR] process_approved_actions() failed: {e}")
            return {"success": 0, "failure": 0}

    def monitor_approved_folder(self):
        """
        Main loop: Monitor /Approved folder continuously and execute approved actions

        Runs until interrupted
        """
        try:
            logger.info("[APPROVAL] Starting approved folder monitor...")
            logger.info("[APPROVAL] Checking /Approved every {self.check_interval} seconds")
            logger.info("[APPROVAL] Press Ctrl+C to stop")

            while True:
                results = self.process_approved_actions()
                logger.info(f"[APPROVAL] Cycle complete: {results}")

                time.sleep(self.check_interval)

        except KeyboardInterrupt:
            logger.info("[APPROVAL] Approved folder monitor stopped by user")
        except Exception as e:
            logger.error(f"[ERROR] monitor_approved_folder() failed: {e}")
            raise


class TaskProcessor:
    """
    Main task processing coordinator

    Monitors /Needs_Action for new tasks, creates action plans, routes through approval workflow,
    and manages overall task lifecycle.

    Silver Tier T068, T073: Automatically creates Plan.md for complex tasks (3+ steps OR >15 min).
    """

    # Complexity detection keywords (T068)
    COMPLEXITY_KEYWORDS = [
        "implement", "create", "build", "develop", "integrate",
        "refactor", "migrate", "design", "architecture"
    ]

    def __init__(self):
        self.needs_action_folder = Path("/Needs_Action")
        self.pending_approval_folder = Path("/Pending_Approval")
        self.scheduled_folder = Path("/Scheduled")
        self.plans_active_folder = Path("/Plans/active")

        self.scheduled_queue = defaultdict(list)

    def scan_tasks(self) -> List[Path]:
        """
        Scan /Needs_Action for new tasks

        Returns:
            List of task file paths
        """
        try:
            if not self.needs_action_folder.exists():
                logger.warning("[TASKS] No /Needs_Action folder found, creating...")
                self.needs_action_folder.mkdir(parents=True, exist_ok=True)
                return []

            # Get all markdown files in /Needs_Action
            task_files = list(self.needs_action_folder.glob("*.md"))

            if task_files:
                logger.info(f"[TASKS] Found {len(task_files)} tasks in /Needs_Action")

            return task_files

        except Exception as e:
            logger.error(f"[ERROR] scan_tasks() failed: {e}")
            return []

    # ========================================================================
    # Plan Generator Integration (Silver Tier T068, T073)
    # ========================================================================

    def detect_complex_task(self, content: str) -> tuple:
        """
        Detect if task is complex enough to require a Plan.md (T068)

        Complexity criteria:
        - 3+ implementation steps (numbered lists, bullet points with actions)
        - Estimated execution time >15 minutes
        - Contains complexity keywords

        Args:
            content: Task file content

        Returns:
            Tuple of (is_complex: bool, metadata: dict)
        """
        metadata = {
            'step_count': 0,
            'estimated_minutes': 0,
            'complexity_keywords': [],
            'reason': ''
        }

        # Count implementation steps
        steps = self._extract_steps(content)
        metadata['step_count'] = len(steps)

        # Extract estimated time
        time_estimate = self._extract_time_estimate(content)
        metadata['estimated_minutes'] = time_estimate

        # Check for complexity keywords
        keywords_found = [kw for kw in self.COMPLEXITY_KEYWORDS if kw.lower() in content.lower()]
        metadata['complexity_keywords'] = keywords_found[:5]  # Limit to first 5

        # Determine complexity (T068)
        is_complex = (
            len(steps) >= 3 or
            time_estimate > 15 or
            len(keywords_found) >= 2
        )

        if is_complex:
            if len(steps) >= 3:
                metadata['reason'] = f"Has {len(steps)} implementation steps (threshold: 3)"
            elif time_estimate > 15:
                metadata['reason'] = f"Estimated {time_estimate} minutes (threshold: 15)"
            else:
                metadata['reason'] = f"Contains {len(keywords_found)} complexity keywords"

            logger.info(f"[COMPLEX] Task detected: {metadata['reason']}")
        else:
            logger.debug(f"[SIMPLE] Task: {len(steps)} steps, {time_estimate} min")

        return is_complex, metadata

    def _extract_steps(self, content: str) -> List[str]:
        """Extract implementation steps from content"""
        steps = []

        # Look for numbered lists, bullet points, or step keywords
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            # Match numbered lists (1., 2., etc.)
            if re.match(r'^\d+\.\s+\w', line):
                steps.append(line)
            # Match bullet points with action words
            elif line.startswith(('-', '*', '+')) and any(
                kw in line.lower() for kw in ['create', 'add', 'implement', 'build', 'write', 'develop']
            ):
                steps.append(line)
            # Match step keywords
            elif line.lower().startswith(('step', 'then', 'next', 'after that', 'additionally')):
                steps.append(line)

        return steps

    def _extract_time_estimate(self, content: str) -> int:
        """Extract estimated time in minutes"""
        # Look for explicit time mentions
        time_patterns = [
            r'(\d+)\s*minutes?',
            r'(\d+)\s*min',
            r'(\d+)\s*hours?',
            r'(\d+)\s*hr',
            r'(\d+)\s*days?',
        ]

        total_minutes = 0

        for pattern in time_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                value = int(match)
                if 'hour' in pattern or 'hr' in pattern:
                    total_minutes += value * 60
                elif 'day' in pattern:
                    total_minutes += value * 480  # 8 hours = 480 min
                else:
                    total_minutes += value

        # If no explicit time found, estimate based on complexity
        if total_minutes == 0:
            step_count = len(self._extract_steps(content))
            # Rough estimate: 5 minutes per step
            total_minutes = step_count * 5

        return total_minutes

    def create_plan_for_task(self, task_file: Path, metadata: dict) -> bool:
        """
        Create Plan.md in /Plans/active/ for complex task (T073)

        Args:
            task_file: Path to source task file
            metadata: Complexity metadata from detector

        Returns:
            True if plan created successfully, False otherwise
        """
        try:
            # Read task content
            with open(task_file, 'r', encoding='utf-8') as f:
                task_content = f.read()

            # Extract components
            objective = self._extract_objective(task_content, task_file.name)
            analysis = self._extract_analysis(task_content)
            steps = self._extract_steps(task_content)

            # Create Plan.md content
            plan_content = self._generate_plan_markdown(
                task_file.name,
                objective,
                analysis,
                steps,
                metadata
            )

            # Create /Plans/active/ directory if needed
            self.plans_active_folder.mkdir(parents=True, exist_ok=True)

            # Write plan file
            plan_filename = f"PLAN_{task_file.stem}.md"
            plan_path = self.plans_active_folder / plan_filename

            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            logger.info(f"[PLAN] Created: {plan_path}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to create plan for {task_file.name}: {e}")
            return False

    def _extract_objective(self, content: str, filename: str) -> str:
        """Extract objective from content or generate from filename"""
        # Look for explicit objective section
        obj_match = re.search(
            r'(?:Objective|Goal|Purpose|What):\s*\n+(.*?)(?:\n+#{|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )

        if obj_match:
            return obj_match.group(1).strip()[:500]  # Limit length

        # Generate from filename
        name_part = filename.replace('_', ' ').replace('-', ' ')
        return f"Complete task: {name_part}"

    def _extract_analysis(self, content: str) -> str:
        """Extract analysis section from content"""
        # Look for context, analysis, or background sections
        analysis_match = re.search(
            r'(?:Context|Analysis|Background|Why):\s*\n+(.*?)(?:\n+#{|\Z)',
            content,
            re.IGNORECASE | re.DOTALL
        )

        if analysis_match:
            return analysis_match.group(1).strip()[:1000]

        return "Analysis of requirements and dependencies..."

    def _generate_plan_markdown(
        self,
        task_filename: str,
        objective: str,
        analysis: str,
        steps: List[str],
        metadata: dict
    ) -> str:
        """Generate Plan.md markdown content"""

        step_items = "\n".join([
            f"- [ ] {step}" for step in steps
        ])

        created_time = datetime.now().isoformat()

        plan = f"""# Plan: {task_filename.replace('.md', '')}

**Source File**: {task_filename}
**Created**: {created_time}
**Status**: Draft

## Objective
{objective}

## Analysis
{analysis}

## Complexity Assessment
- **Step Count**: {metadata['step_count']} (threshold: 3)
- **Estimated Time**: {metadata['estimated_minutes']} minutes (threshold: 15)
- **Reason**: {metadata['reason']}

## Proposed Actions
{step_items if step_items else "- [ ] Implement task requirements"}

## Approval Required
- [ ] Review plan with stakeholder
- [ ] Obtain approval for execution
- [ ] Schedule implementation

## Execution Tracking
- **Started**: TBD
- **Completed**: TBD
- **Result**: TBD

## Deviation Detection
Any deviations from this plan must be documented with reasoning.

---
*Generated by Task Processor (Silver Tier T073)*
*Complex Task Detected: {metadata['reason']}*
"""

        return plan

    def process_tasks(self) -> Dict[str, int]:
        """
        Process all tasks in /Needs_Action

        Returns:
            Summary of processing: {created: count, processed: count, failed: count, errors: count}
        """
        try:
            task_files = self.scan_tasks()

            created_count = 0
            processed_count = 0
            failed_count = 0
            errors_count = 0

            for task_file in task_files:
                logger.info(f"[TASKS] Processing: {task_file.name}")

                # Process task and move to /Done or /Failed
                result = self._process_task(task_file)

                if result == "created":
                    created_count += 1
                elif result == "processed":
                    processed_count += 1
                elif result == "failed":
                    failed_count += 1
                elif result == "error":
                    errors_count += 1

            logger.info(f"[TASKS] Processing complete: {created_count} created, {processed_count} processed, {failed_count} failed, {errors_count} errors")
            return {"created": created_count, "processed": processed_count, "failed": failed_count, "errors": errors_count}

        except Exception as e:
            logger.error(f"[ERROR] process_tasks() failed: {e}")
            return {"created": 0, "processed": 0, "failed": 0, "errors": 0}

    def _process_task(self, task_file: Path) -> str:
        """
        Process a single task file

        Silver Tier T068, T073: For complex tasks, automatically create Plan.md before processing

        Args:
            task_file: Path to task file

        Returns:
            Status: "created", "processed", "failed", "error"
        """
        try:
            # Read task file
            with open(task_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Silver Tier T068: Detect complex tasks
            is_complex, metadata = self.detect_complex_task(content)

            # Silver Tier T073: Create Plan.md for complex tasks
            if is_complex:
                logger.info(f"[PLAN] Complex task detected: {task_file.name}")
                logger.info(f"[PLAN] Reason: {metadata['reason']}")

                # Create Plan.md
                plan_created = self.create_plan_for_task(task_file, metadata)

                if plan_created:
                    logger.info(f"[PLAN] Plan created for: {task_file.name}")
                else:
                    logger.warning(f"[PLAN] Failed to create plan for: {task_file.name}")

            # Continue with normal processing
            # Check if task is marked as pending
            if "status: pending" in content:
                return self._create_pending_approval(task_file, content)

            # Check if task requires approval
            if "requires_approval: yes" in content:
                return self._create_approval_request(task_file, content)

            # Otherwise, process immediately
            return self._process_task_immediately(task_file, content)

        except Exception as e:
            logger.error(f"[ERROR] _process_task() failed for {task_file}: {e}")
            return "error"

    def _create_pending_approval(self, task_file: Path, content: str) -> str:
        """
        Move task to /Pending_Approval for human review

        Args:
            task_file: Original task file
            content: Task content

        Returns:
            Status: "created"
        """
        try:
            pending_folder = Path(self.pending_approval_folder)
            pending_folder.mkdir(parents=True, exist_ok=True)

            # Move task file to /Pending_Approval
            pending_file = pending_folder / task_file.name

            shutil.move(str(task_file), str(pending_file))

            logger.info(f"[APPROVAL] Created approval request: {pending_file.name}")
            return "created"

        except Exception as e:
            logger.error(f"[ERROR] _create_pending_approval() failed for {task_file}: {e}")
            return "failed"

    def _create_approval_request(self, task_file: Path, content: str) -> str:
        """
        Create approval request file in /Pending_Approval

        Args:
            task_file: Original task file
            content: Task content

        Returns:
            Status: "created"
        """
        try:
            pending_folder = Path("/Pending_Approval")
            pending_folder.mkdir(parents=True, exist_ok=True)

            # Create approval request file from template
            template_path = Path("templates/approval_request.md")

            if template_path.exists():
                with open(template_path, 'r') as template:
                    template = template.read()

                # Replace placeholders with actual task details
                approval_content = template.replace(
                    "action_type: [SEND_EMAIL | POST_LINKEDIN | ... ]",
                    f"action_type: SEND_EMAIL"
                ).replace(
                    "target: [recipient email | ... ]",
                    f"target: {self._extract_field(content, 'to')}"
                ).replace(
                    "context: [Why this action is needed...]",
                    f"context: {self._extract_field(content, 'context')}"
                ).replace(
                    "impact: [What happens if approved...]",
                    f"impact: {self._extract_field(content, 'impact')}"
                ).replace(
                    "action_summary: [Summary...]",
                    f"action_summary: {self._extract_field(content, 'summary')}"
                ).replace(
                    "data: [Email subject/content...]",
                    f"data: {{to: {self._extract_field(content, 'to')}, subject: {self._extract_field(content, 'subject')}}}"
                ).replace(
                    "parameters: [Specific action parameters...]",
                    f"parameters: {self._extract_field(content, 'parameters')}"
                ).replace(
                    "[Date: YYYY-MM-DD]",
                    f"[Date: {datetime.now().strftime('%Y-%m-%d')}]"
                ).replace(
                    "[Time: HH:MM:SS]",
                    f"[Time: {datetime.now().strftime('%H:%M:%S')}]"
                )

                # Save approval request
                approval_file = pending_folder / f"approval_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
                with open(approval_file, 'w', encoding='utf-8') as f:
                    f.write(approval_content)

                # Move original task file to /Pending_Approval
                shutil.copy(str(task_file), str(pending_folder / task_file.name))

                # Update original file status
                self._update_file_status(task_file, "pending_approval")

                logger.info(f"[APPROVAL] Created approval request: {approval_file.name}")
                return "created"

            else:
                # Create basic approval request if template not found
                logger.warning(f"[APPROVAL] Template not found, creating basic approval request")
                return self._create_basic_approval_request(task_file, content)

        except Exception as e:
            logger.error(f"[ERROR] _create_approval_request() failed for {task_file}: {e}")
            return "failed"

    def _process_task_immediately(self, task_file: Path, content: str) -> str:
        """
        Process task immediately (no approval needed)

        Args:
            task_file: Task file path
            content: Task content

        Returns:
            Status: "processed"
        """
        try:
            # Process task logic here (file handling, business logic)
            result = self._handle_task(task_file, content)

            if result:
                # Move to /Done with completion timestamp
                self._complete_task(task_file, result)
                return "processed"
            else:
                # Move to /Failed with error details
                self._fail_task(task_file, result)
                return "failed"

        except Exception as e:
            logger.error(f"[ERROR] _process_task_immediately() failed for {task_file}: {e}")
            return "error"

    def _extract_field(self, content: str, field_name: str) -> str:
        """Extract field from task content"""
        import re

        if field_name == "to":
            match = re.search(r'to:\s*([^\\n]+)', content)
            return match.group(1) if match else "unknown"

        if field_name == "context":
            match = re.search(r'context:\s*(.+?)(?=\\n|\\n)', content, re.DOTALL)
            return match.group(1).strip() if match else "no context provided"

        if field_name == "impact":
            match = re.search(r'impact:\s*(.+?)(?=\\n|\\n)', content, re.DOTALL)
            return match.group(1).strip() if match else "no impact provided"

        if field_name == "summary":
            match = re.search(r'summary:\s*(.+?)(?=\\n|\\n)', content, re.DOTALL)
            return match.group(1).strip() if match else "no summary provided"

        if field_name == "subject":
            match = re.search(r'subject:\s*(.+?)(?=\\n|\\n)', content, re.DOTALL)
            return match.group(1).strip() if match else "no subject provided"

        if field_name == "parameters":
            match = re.search(r'parameters:\s*(.+?)(?=\\n|\\n)', content, re.DOTALL)
            return match.group(1).strip() if match else "no parameters provided"

        return f"[FIELD_NOT_FOUND: {field_name}]"

    def _create_basic_approval_request(self, task_file: Path, content: str) -> str:
        """Create basic approval request without template"""
        try:
            pending_folder = Path("/Pending_Approval")
            pending_folder.mkdir(parents=True, exist_ok=True)

            # Create basic approval request
            approval_content = f"""---
action_type: SEND_EMAIL
target: unknown
created_timestamp: {datetime.now().isoformat()}
status: pending
---

# Approval Request: {task_file.stem}

## Context
{content[:200]}...

## Action Details
- **Type**: SEND_EMAIL
- **Source**: {task_file.name}

## Approval Instructions
Move this file to `/Approved` to proceed with the action, or to `/Rejected` to cancel.

---
"""
            # Save approval request
            approval_file = pending_folder / f"approval_request_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(approval_file, 'w', encoding='utf-8') as f:
                f.write(approval_content)

            logger.info(f"[APPROVAL] Created basic approval request: {approval_file.name}")
            return "created"

        except Exception as e:
            logger.error(f"[ERROR] _create_basic_approval_request() failed: {e}")
            return "failed"

    def update_file_status(self, file_path: Path, status: str) -> bool:
        """Update file status"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Update or add status
            if "status:" in content:
                content = re.sub(r'status:\s*\w+', f'status: {status}', content)
            else:
                content = f"---\nstatus: {status}\n---\n\n{content}"

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except Exception as e:
            logger.error(f"[ERROR] update_file_status() failed: {e}")
            return False

    def _complete_task(self, file_path: Path, result: str) -> bool:
        """Move completed task to /Done with completion timestamp"""
        try:
            done_folder = Path("/Done")
            done_folder.mkdir(parents=True, exist_ok=True)

            # Add completion timestamp
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            completed_at = f"\n\n---\n**Completed**: {datetime.now().isoformat()}\n**Result**: {result}\n"
            content += completed_at

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Move to /Done
            shutil.move(str(file_path), str(done_folder / file_path.name))
            logger.info(f"[OK] Task completed: {file_path.name} → {done_folder / file_path.name}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] _complete_task() failed: {e}")
            return False

    def _fail_task(self, file_path: Path, result: str) -> bool:
        """Move failed task to /Failed with error details"""
        try:
            failed_folder = Path("/Failed")
            failed_folder.mkdir(parents=True, exist_ok=True)

            # Add failure details
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            failed_at = f"\n\n---\n**Failed**: {datetime.now().isoformat()}\n**Error**: {result}\n"
            content += failed_at

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Move to /Failed
            shutil.move(str(file_path), str(failed_folder / file_path.name))
            logger.info(f"[FAIL] Task failed: {file_path.name} → {failed_folder / file_path.name}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] _fail_task() failed: {e}")
            return False

    def _handle_task(self, task_file: Path, content: str) -> bool:
        """Handle task logic (file handling, business logic)"""
        # Placeholder for actual task handling logic
        # This would contain business-specific logic for processing different task types
        logger.info(f"[TASK] Handling task: {task_file.name}")
        return True


def main():
    """Main entry point"""
    processor = TaskProcessor()

    try:
        # Main processing loop
        while True:
            tasks = processor.scan_tasks()
            results = processor.process_tasks()

            if results["created"] > 0:
                logger.info(f"[TASKS] {results['created']} approval requests created")

            if results["processed"] > 0:
                logger.info(f"[TASKS] {results['processed']} tasks processed")

            # Wait before next scan
            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        logger.info("[TASKS] Task processor stopped by user")

    except Exception as e:
        logger.error(f"[ERROR] Task processor failed: {e}")
        raise


if __name__ == "__main__":
    main()
