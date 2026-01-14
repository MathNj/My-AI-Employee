#!/usr/bin/env python3
"""
Plan Generator - Task to Execution Plan Converter

Converts tasks, events, or requests into deterministic, auditable execution plans.

This script performs ANALYSIS AND DECOMPOSITION ONLY.
It never executes actions, calls MCP servers, or moves approval files.

Usage:
    python generate_plan.py /path/to/task.md
    python generate_plan.py /path/to/task.md --output /Plans/custom_name.md
    python generate_plan.py --scan-needs-action
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Vault paths
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()
NEEDS_ACTION = VAULT_PATH / "Needs_Action"
PLANS = VAULT_PATH / "Plans"
COMPANY_HANDBOOK = VAULT_PATH / "Company_Handbook.md"
BUSINESS_GOALS = VAULT_PATH / "Business_Goals.md"
LOGS = VAULT_PATH / "Logs"

# Ensure directories exist
for folder in [NEEDS_ACTION, PLANS, LOGS]:
    folder.mkdir(exist_ok=True)

# Skill mappings - which skill handles which type of action
SKILL_MAPPINGS = {
    'email': 'email-sender',
    'linkedin_post': 'linkedin-poster',
    'web_research': 'web-researcher',
    'file_operation': 'vault management (manual)',
    'dashboard_update': 'dashboard-updater',
    'schedule_task': 'scheduler-manager'
}

# Approval thresholds (defaults - should read from Company_Handbook.md)
APPROVAL_THRESHOLDS = {
    'email_new_contact': True,
    'email_known_contact': False,
    'linkedin_post': True,
    'payment_any': True,
    'web_research_sensitive': True
}


def log_activity(action: str, details: Dict):
    """Log plan generation activity."""
    log_file = LOGS / f"plan_generation_{datetime.now().strftime('%Y-%m-%d')}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details,
        "skill": "plan-generator"
    }

    try:
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to log activity: {e}", file=sys.stderr)


def parse_frontmatter(file_path: Path) -> Tuple[Dict, str]:
    """
    Parse frontmatter and body from markdown file.

    Returns:
        (metadata_dict, body_content)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if not content.startswith('---'):
            return {}, content

        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content

        frontmatter_text = parts[1].strip()
        body = parts[2].strip()

        # Simple YAML parsing
        metadata = {}
        for line in frontmatter_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"').strip("'")

        return metadata, body

    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)
        return {}, ""


def analyze_task(metadata: Dict, body: str) -> Dict:
    """
    Analyze task to determine type, complexity, and requirements.

    Returns analysis dict with:
    - task_type: email, research, multi-step, etc.
    - complexity: simple, medium, complex
    - requires_research: bool
    - requires_approval: bool
    - estimated_steps: int
    """
    analysis = {
        'task_type': metadata.get('type', 'general'),
        'complexity': 'simple',
        'requires_research': False,
        'requires_approval': False,
        'estimated_steps': 1,
        'suggested_skills': []
    }

    # Detect task type from metadata or content
    task_type = metadata.get('type', '').lower()
    priority = metadata.get('priority', 'normal').lower()

    # Check if research needed
    research_keywords = ['verify', 'research', 'find', 'lookup', 'check', 'investigate']
    if any(kw in body.lower() for kw in research_keywords):
        analysis['requires_research'] = True
        analysis['suggested_skills'].append('web-researcher')

    # Check if email task
    if task_type == 'email' or 'email' in body.lower():
        analysis['task_type'] = 'email'
        analysis['suggested_skills'].append('email-sender')
        analysis['requires_approval'] = True  # Default for emails

    # Check if LinkedIn task
    if 'linkedin' in body.lower() or task_type == 'linkedin_post':
        analysis['task_type'] = 'linkedin_post'
        analysis['suggested_skills'].append('linkedin-poster')
        analysis['requires_approval'] = True

    # Estimate complexity
    word_count = len(body.split())
    if word_count > 500 or len(analysis['suggested_skills']) > 2:
        analysis['complexity'] = 'complex'
        analysis['estimated_steps'] = 5
    elif word_count > 200 or len(analysis['suggested_skills']) > 1:
        analysis['complexity'] = 'medium'
        analysis['estimated_steps'] = 3
    else:
        analysis['estimated_steps'] = 1 + len(analysis['suggested_skills'])

    return analysis


def decompose_task(task_name: str, metadata: Dict, body: str, analysis: Dict) -> List[Dict]:
    """
    Decompose task into execution steps.

    Each step includes:
    - step_number: int
    - description: str
    - skill: str (which skill handles this)
    - requires_approval: bool
    - dependencies: list of step numbers
    - estimated_time: str
    """
    steps = []
    step_num = 1

    # Step 1: Research if needed
    if analysis['requires_research']:
        steps.append({
            'step_number': step_num,
            'description': 'Research required information using web-researcher',
            'skill': 'web-researcher',
            'requires_approval': False,
            'dependencies': [],
            'estimated_time': '2-5 minutes',
            'notes': 'Gather evidence and verify facts before proceeding'
        })
        step_num += 1

    # Step 2: Main action based on task type
    if analysis['task_type'] == 'email':
        # Email composition
        steps.append({
            'step_number': step_num,
            'description': 'Compose email using email-sender',
            'skill': 'email-sender',
            'requires_approval': analysis['requires_approval'],
            'dependencies': [step_num - 1] if analysis['requires_research'] else [],
            'estimated_time': '5-10 minutes',
            'notes': f"Create approval request - TO: {metadata.get('to', 'TBD')}"
        })
        step_num += 1

    elif analysis['task_type'] == 'linkedin_post':
        # LinkedIn post
        steps.append({
            'step_number': step_num,
            'description': 'Create LinkedIn post using linkedin-poster',
            'skill': 'linkedin-poster',
            'requires_approval': True,
            'dependencies': [step_num - 1] if analysis['requires_research'] else [],
            'estimated_time': '10-15 minutes',
            'notes': 'Generate post content and create approval request'
        })
        step_num += 1

    elif analysis['task_type'] == 'general':
        # Generic task - need to read task details
        steps.append({
            'step_number': step_num,
            'description': f'Execute task: {task_name}',
            'skill': 'task-specific (TBD)',
            'requires_approval': True,  # Default to safe
            'dependencies': [step_num - 1] if analysis['requires_research'] else [],
            'estimated_time': 'TBD',
            'notes': 'Review task details and determine specific actions needed'
        })
        step_num += 1

    # Step N: Human approval (if any step requires it)
    if any(step['requires_approval'] for step in steps):
        approval_steps = [s['step_number'] for s in steps if s['requires_approval']]
        steps.append({
            'step_number': step_num,
            'description': 'Human review and approval',
            'skill': 'approval-processor (human action)',
            'requires_approval': False,  # This IS the approval step
            'dependencies': approval_steps,
            'estimated_time': '< 24 hours',
            'notes': 'Move approval file from /Pending_Approval to /Approved'
        })
        step_num += 1

    # Step N+1: Execution (if approval was needed)
    if any(step['requires_approval'] for step in steps):
        steps.append({
            'step_number': step_num,
            'description': 'Execute approved actions',
            'skill': 'approval-processor (automated)',
            'requires_approval': False,
            'dependencies': [step_num - 1],
            'estimated_time': '1-5 minutes',
            'notes': 'approval-processor detects approval and routes to executor'
        })
        step_num += 1

    # Step Final: Mark complete
    steps.append({
        'step_number': step_num,
        'description': 'Move task to Done and update Dashboard',
        'skill': 'dashboard-updater',
        'requires_approval': False,
        'dependencies': [step_num - 1],
        'estimated_time': '< 1 minute',
        'notes': 'Update status and log completion'
    })

    return steps


def generate_plan_content(task_file: Path, metadata: Dict, body: str, analysis: Dict, steps: List[Dict]) -> str:
    """Generate formatted plan content."""
    plan = f"""---
task_file: {task_file.name}
created: {datetime.now().isoformat()}Z
status: pending
complexity: {analysis['complexity']}
estimated_steps: {len(steps)}
requires_approval: {any(s['requires_approval'] for s in steps)}
---

# Execution Plan: {task_file.stem}

## Task Summary

**Source:** `{task_file.name}`
**Type:** {analysis['task_type']}
**Complexity:** {analysis['complexity']}
**Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Original Task

{body[:500]}{'...' if len(body) > 500 else ''}

## Analysis

- **Estimated Steps:** {len(steps)}
- **Requires Research:** {'Yes' if analysis['requires_research'] else 'No'}
- **Requires Approval:** {'Yes' if any(s['requires_approval'] for s in steps) else 'No'}
- **Skills Involved:** {', '.join(set(s['skill'] for s in steps))}

## Execution Steps

"""

    # Add steps
    for step in steps:
        plan += f"### Step {step['step_number']}: {step['description']}\n\n"
        plan += f"**Skill:** `{step['skill']}`\n"
        plan += f"**Approval Required:** {'✅ Yes' if step['requires_approval'] else '❌ No'}\n"

        if step['dependencies']:
            plan += f"**Dependencies:** Steps {', '.join(map(str, step['dependencies']))}\n"
        else:
            plan += f"**Dependencies:** None\n"

        plan += f"**Estimated Time:** {step['estimated_time']}\n\n"

        if step['notes']:
            plan += f"**Notes:** {step['notes']}\n\n"

        # Checkbox
        plan += f"- [ ] Step {step['step_number']} complete\n\n"

    # Add approval section if needed
    if any(s['requires_approval'] for s in steps):
        plan += """## Approval Checkpoints

The following steps require human approval before execution:

"""
        for step in steps:
            if step['requires_approval']:
                plan += f"- [ ] Step {step['step_number']}: {step['description']}\n"

        plan += """
**Action Required:**
1. Review approval request in `/Pending_Approval`
2. Verify details are correct
3. Move to `/Approved` to proceed or `/Rejected` to cancel

"""

    # Add safety notes
    plan += """## Safety & Constraints

- ✅ This plan defines WHAT to do, not HOW (execution details in skill docs)
- ✅ All approval thresholds from Company_Handbook.md must be respected
- ✅ External actions (email, posts) require human approval by default
- ✅ No steps execute until approved (where applicable)

## Next Actions

1. Review this plan
2. Proceed with Step 1
3. Complete checkboxes as steps finish
4. Move to /Done when complete

---

*Generated by plan-generator skill*
*Plan is deterministic and auditable*
"""

    return plan


def save_plan(task_file: Path, plan_content: str, output_path: Optional[Path] = None) -> Path:
    """Save plan to file."""
    if output_path:
        plan_path = output_path
    else:
        # Generate plan filename
        task_name = task_file.stem.replace('TASK_', '').replace('EMAIL_', '').replace('FILE_', '')
        timestamp = datetime.now().strftime('%Y-%m-%d')
        plan_path = PLANS / f"PLAN_{task_name}_{timestamp}.md"

        # Handle duplicates
        counter = 1
        while plan_path.exists():
            plan_path = PLANS / f"PLAN_{task_name}_{timestamp}_{counter}.md"
            counter += 1

    # Write plan
    plan_path.write_text(plan_content, encoding='utf-8')
    return plan_path


def process_task_file(task_file: Path, output_path: Optional[Path] = None, verbose: bool = False) -> Optional[Path]:
    """
    Process a single task file and generate execution plan.

    Returns:
        Path to generated plan file, or None if failed
    """
    if verbose:
        print(f"\nProcessing: {task_file.name}")

    try:
        # Parse task
        metadata, body = parse_frontmatter(task_file)

        if not body:
            print(f"Warning: No content in {task_file.name}")
            return None

        # Analyze
        analysis = analyze_task(metadata, body)

        if verbose:
            print(f"  Type: {analysis['task_type']}")
            print(f"  Complexity: {analysis['complexity']}")
            print(f"  Estimated steps: {analysis['estimated_steps']}")

        # Decompose
        steps = decompose_task(task_file.stem, metadata, body, analysis)

        # Generate plan content
        plan_content = generate_plan_content(task_file, metadata, body, analysis, steps)

        # Save
        plan_path = save_plan(task_file, plan_content, output_path)

        if verbose:
            print(f"  ✅ Plan created: {plan_path.name}")

        # Log activity
        log_activity("plan_generated", {
            "task_file": task_file.name,
            "plan_file": plan_path.name,
            "complexity": analysis['complexity'],
            "steps": len(steps),
            "requires_approval": any(s['requires_approval'] for s in steps)
        })

        return plan_path

    except Exception as e:
        print(f"Error processing {task_file.name}: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return None


def scan_needs_action(verbose: bool = False) -> List[Path]:
    """Scan Needs_Action folder and generate plans for all tasks."""
    task_files = list(NEEDS_ACTION.glob('*.md'))

    if not task_files:
        print("No tasks found in Needs_Action folder")
        return []

    print(f"\nFound {len(task_files)} task(s) in Needs_Action")

    generated_plans = []
    for task_file in task_files:
        plan_path = process_task_file(task_file, verbose=verbose)
        if plan_path:
            generated_plans.append(plan_path)

    print(f"\n✅ Generated {len(generated_plans)} plan(s)")
    return generated_plans


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate execution plans from tasks'
    )
    parser.add_argument(
        'task_file',
        nargs='?',
        type=str,
        help='Path to task file'
    )
    parser.add_argument(
        '--scan-needs-action',
        action='store_true',
        help='Scan and process all files in Needs_Action folder'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output plan file path (optional)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    if args.scan_needs_action:
        # Scan mode
        scan_needs_action(verbose=args.verbose)
    elif args.task_file:
        # Single file mode
        task_file = Path(args.task_file)
        if not task_file.exists():
            print(f"Error: File not found: {task_file}")
            sys.exit(1)

        output_path = Path(args.output) if args.output else None
        plan_path = process_task_file(task_file, output_path, verbose=args.verbose)

        if plan_path:
            print(f"\n✅ Plan generated: {plan_path}")
            sys.exit(0)
        else:
            print("\n❌ Plan generation failed")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
