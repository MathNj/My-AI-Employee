#!/usr/bin/env python3
"""
Auto-Approver Watcher Wrapper

This wrapper integrates the auto-approver skill into the orchestrator
alongside the other watchers. Runs continuously and monitors /Pending_Approval
for intelligent auto-approval decisions.
"""

import sys
from pathlib import Path

# Add the auto-approver scripts to path
auto_approver_script = Path(__file__).parent.parent / ".claude" / "skills" / "auto-approver" / "scripts" / "auto_approve.py"

# Run the auto-approver
if __name__ == "__main__":
    import subprocess
    result = subprocess.run([sys.executable, str(auto_approver_script)], cwd=Path(__file__).parent)
    sys.exit(result.returncode)
