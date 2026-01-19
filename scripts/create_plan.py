#!/usr/bin/env python3
"""
Plan Generator - Creates Plan.md files for complex tasks

For Silver Tier tasks T068, T073:
- Detects complex tasks (3+ steps OR >15 minutes execution time)
- Creates Plan.md in /Plans/active/ with objective, analysis, steps
- Monitors /Plans/active/ for execution tracking

Complex Task Criteria:
- 3 or more implementation steps OR
- Estimated execution time >15 minutes
"""

import os
import re
import json
import logging
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Configure logging
log_dir = Path("Logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "plan_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("PlanGenerator")

# Vault paths
VAULT_ROOT = Path("/")
NEEDS_ACTION = VAULT_ROOT / "Needs_Action"
PLANS_ACTIVE = VAULT_ROOT / "Plans" / "active"
PLANS_ARCHIVE = VAULT_ROOT / "Plans" / "archive"
DONE = VAULT_ROOT / "Done"


class ComplexTaskDetector:
    """
    Detects if a task is complex enough to require a Plan.md

    Complexity criteria (T068):
    - 3 or more implementation steps OR
    - Estimated execution time >15 minutes
    """

    COMPLEXITY_KEYWORDS = [
        "implement", "create", "build", "develop", "integrate",
        "refactor", "migrate", "design", "architecture"
    ]

    TIME_INDICATORS = [
        "minutes", "hours", "days", "week", "month"
    ]

    def __init__(self):
        self.step_count = 0
        self.estimated_time = 0
        self.complexity_score = 0

    def detect_complex_task(self, task_file: Path, content: str) -> Tuple[bool, Dict]:
        """
        Detect if task requires a Plan.md (T068)

        Args:
            task_file: Path to task markdown file
            content: File content as string

        Returns:
            Tuple of (is_complex, metadata_dict)
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

        # Determine complexity
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

            logger.info(f"[COMPLEX] {task_file.name}: {metadata['reason']}")
        else:
            logger.debug(f"[SIMPLE] {task_file.name}: {len(steps)} steps, {time_estimate} min")

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
                kw in line.lower() for kw in ['create', 'add', 'implement', 'build', 'write']
            ):
                steps.append(line)
            # Match step keywords
            elif line.lower().startswith(('step', 'then', 'next', 'after that')):
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


class PlanGenerator:
    """
    Plan generation for complex tasks (T073)

    Creates Plan.md files with:
    - Objective
    - Analysis
    - Proposed actions (steps)
    - Approval requirement
    - Execution tracking
    """

    def __init__(self):
        self.detector = ComplexTaskDetector()
        self.plans_created = 0
        self.plans_updated = 0

    def scan_needs_action(self) -> List[Tuple[Path, Dict]]:
        """
        Scan /Needs_Action for complex tasks (T073)

        Returns:
            List of (task_file, metadata) tuples for complex tasks
        """
        complex_tasks = []

        if not NEEDS_ACTION.exists():
            logger.warning(f"/Needs_Action folder not found: {NEEDS_ACTION}")
            return complex_tasks

        for file_path in NEEDS_ACTION.glob("*.md"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                is_complex, metadata = self.detector.detect_complex_task(file_path, content)

                if is_complex:
                    complex_tasks.append((file_path, metadata))

            except Exception as e:
                logger.error(f"[ERROR] Failed to read {file_path.name}: {e}")

        logger.info(f"[SCAN] Found {len(complex_tasks)} complex tasks in /Needs_Action")
        return complex_tasks

    def create_plan(self, task_file: Path, metadata: Dict) -> bool:
        """
        Create Plan.md in /Plans/active/ (T073)

        Args:
            task_file: Path to source task file
            metadata: Complexity metadata from detector

        Returns:
            True if plan created/updated, False otherwise
        """
        try:
            # Read task content
            with open(task_file, 'r', encoding='utf-8') as f:
                task_content = f.read()

            # Extract components
            objective = self._extract_objective(task_content, task_file.name)
            analysis = self._extract_analysis(task_content)
            steps = self.detector._extract_steps(task_content)

            # Create Plan.md content
            plan_content = self._generate_plan_markdown(
                task_file.name,
                objective,
                analysis,
                steps,
                metadata
            )

            # Create /Plans/active/ directory if needed
            PLANS_ACTIVE.mkdir(parents=True, exist_ok=True)

            # Write plan file
            plan_filename = f"PLAN_{task_file.stem}.md"
            plan_path = PLANS_ACTIVE / plan_filename

            with open(plan_path, 'w', encoding='utf-8') as f:
                f.write(plan_content)

            self.plans_created += 1
            logger.info(f"[CREATED] Plan: {plan_path}")

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
        metadata: Dict
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
*Generated by Plan Generator (Silver Tier T073)*
"""

        return plan

    def monitor_plans_folder(self) -> Dict[str, int]:
        """
        Monitor /Plans/active/ folder for plan execution tracking (T073)

        Returns:
            Summary dict with counts (total, completed, in_progress, overdue)
        """
        if not PLANS_ACTIVE.exists():
            return {'total': 0, 'completed': 0, 'in_progress': 0, 'overdue': 0}

        plans = list(PLANS_ACTIVE.glob("PLAN_*.md"))

        stats = {
            'total': len(plans),
            'completed': 0,
            'in_progress': 0,
            'overdue': 0
        }

        for plan_path in plans:
            try:
                with open(plan_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check status
                if '**Status**: Completed' in content:
                    stats['completed'] += 1
                elif '**Status**: In Progress' in content or '**Status**: Draft' in content:
                    stats['in_progress'] += 1

            except Exception as e:
                logger.warning(f"[WARN] Could not read plan {plan_path.name}: {e}")

        logger.info(f"[MONITOR] Plans: {stats['total']} total, "
                   f"{stats['completed']} completed, {stats['in_progress']} in progress")

        return stats

    def archive_completed_plan(self, plan_path: Path) -> bool:
        """
        Move completed plan to /Plans/archive/

        Args:
            plan_path: Path to plan in /Plans/active/

        Returns:
            True if archived successfully
        """
        try:
            PLANS_ARCHIVE.mkdir(parents=True, exist_ok=True)

            # Add completion timestamp
            with open(plan_path, 'r', encoding='utf-8') as f:
                content = f.read()

            content = content.replace(
                '**Completed**: TBD',
                f'**Completed**: {datetime.now().isoformat()}'
            )

            # Write to archive
            archive_path = PLANS_ARCHIVE / plan_path.name
            with open(archive_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Remove from active
            plan_path.unlink()

            logger.info(f"[ARCHIVED] {plan_path.name} -> {archive_path}")
            return True

        except Exception as e:
            logger.error(f"[ERROR] Failed to archive {plan_path.name}: {e}")
            return False


def main():
    """Main entry point for plan generation"""
    logger.info("=" * 60)
    logger.info("Plan Generator Started (Silver Tier T068, T073)")
    logger.info("=" * 60)

    generator = PlanGenerator()

    # Scan for complex tasks
    complex_tasks = generator.scan_needs_action()

    # Create plans for complex tasks
    for task_file, metadata in complex_tasks:
        logger.info(f"\n[PROCESSING] {task_file.name}")
        logger.info(f"  Reason: {metadata['reason']}")
        logger.info(f"  Steps: {metadata['step_count']}, Time: {metadata['estimated_minutes']} min")

        generator.create_plan(task_file, metadata)

    # Monitor existing plans
    stats = generator.monitor_plans_folder()

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Plan Generator Summary")
    logger.info("=" * 60)
    logger.info(f"Complex tasks found: {len(complex_tasks)}")
    logger.info(f"Plans created: {generator.plans_created}")
    logger.info(f"Existing plans: {stats['total']}")
    logger.info(f"  - Completed: {stats['completed']}")
    logger.info(f"  - In Progress: {stats['in_progress']}")
    logger.info("=" * 60)

    return generator.plans_created


if __name__ == "__main__":
    main()
