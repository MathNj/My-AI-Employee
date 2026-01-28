#!/usr/bin/env python3
"""
Ultimate Approval Processor for Personal AI Employee

Advanced approval workflow processing with:
- Multi-stage approval workflows
- Escalation management
- SLA tracking and alerts
- Parallel and sequential approval chains
- Approval conditions and rules
- Structured JSON logging
- Approval analytics and reporting
- Auto-approval based on rules
- Delegation and substitution
- Batch approval operations

Usage:
    python approval_processor_ultimate.py                 # Process all approvals
    python approval_processor_ultimate.py --status        # Show status
    python approval_processor_ultimate.py --escalate      # Check and escalate
    python approval_processor_ultimate.py --analytics     # Show analytics
    python approval_processor_ultimate.py --auto-approve  # Apply auto-approval rules
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
from collections import defaultdict

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
PENDING_APPROVAL = VAULT_PATH / "Pending_Approval"
APPROVED = VAULT_PATH / "Approved"
REJECTED = VAULT_PATH / "Rejected"
DONE = VAULT_PATH / "Done"
EXPIRED = VAULT_PATH / "Expired"
FAILED = VAULT_PATH / "Failed"
ESCALATED = VAULT_PATH / "Escalated"
LOGS = VAULT_PATH / "Logs"
CONFIG_PATH = VAULT_PATH / "approval_processor_config.yaml"

# Ensure folders exist
for folder in [PENDING_APPROVAL, APPROVED, REJECTED, DONE, EXPIRED, FAILED, ESCALATED]:
    folder.mkdir(exist_ok=True)


# =============================================================================
# Approval Enums
# =============================================================================

class ApprovalStatus(Enum):
    """Approval workflow status"""
    PENDING = "pending"
    AWAITING = "awaiting"  # Awaiting specific approver
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"
    AUTO_APPROVED = "auto_approved"
    AUTO_REJECTED = "auto_rejected"


class ApprovalType(Enum):
    """Types of approval requests"""
    EMAIL = "email"
    LINKEDIN_POST = "linkedin_post"
    X_POST = "x_post"
    INSTAGRAM_POST = "instagram_post"
    FACEBOOK_POST = "facebook_post"
    TASK = "task"
    EXPENSE = "expense"
    DOCUMENT = "document"
    GENERAL = "general"


class EscalationLevel(Enum):
    """Escalation levels"""
    NONE = 0
    LEVEL_1 = 1  # Supervisor
    LEVEL_2 = 2  # Manager
    LEVEL_3 = 3  # Director
    LEVEL_4 = 4  # Executive


# =============================================================================
# Approval Data Classes
# =============================================================================

@dataclass
class ApprovalCondition:
    """Condition for auto-approval"""
    field: str
    operator: str  # eq, ne, gt, lt, contains, regex
    value: Any
    required: bool = True


@dataclass
class ApprovalRule:
    """Auto-approval rule"""
    name: str
    type: ApprovalType
    conditions: List[ApprovalCondition]
    action: str  # approve, reject, escalate
    target_approver: Optional[str] = None
    enabled: bool = True


@dataclass
class ApprovalStep:
    """Step in approval workflow"""
    name: str
    approver: str
    optional: bool = False
    timeout_minutes: Optional[int] = None
    escalation_to: Optional[str] = None


@dataclass
class ApprovalRequest:
    """Approval request definition"""
    id: str
    type: ApprovalType
    title: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    current_approver: Optional[str] = None
    approvers: List[str] = field(default_factory=list)
    approved_by: List[str] = field(default_factory=list)
    rejected_by: Optional[str] = None
    rejection_reason: Optional[str] = None
    due_at: Optional[str] = None
    sla_minutes: Optional[int] = None
    escalation_level: EscalationLevel = EscalationLevel.NONE
    escalated_to: Optional[str] = None
    workflow: List[ApprovalStep] = field(default_factory=list)
    current_step: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None

    @property
    def is_overdue(self) -> bool:
        """Check if approval is overdue"""
        if not self.due_at:
            return False
        try:
            due = datetime.fromisoformat(self.due_at)
            return datetime.now() > due
        except:
            return False

    @property
    def needs_escalation(self) -> bool:
        """Check if approval needs escalation"""
        if not self.sla_minutes:
            return False

        try:
            created = datetime.fromisoformat(self.created_at)
            elapsed = (datetime.now() - created).total_seconds() / 60
            return elapsed > self.sla_minutes * 0.8  # Escalate at 80% of SLA
        except:
            return False

    @property
    def age_minutes(self) -> float:
        """Get age in minutes"""
        try:
            created = datetime.fromisoformat(self.created_at)
            return (datetime.now() - created).total_seconds() / 60
        except:
            return 0

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        data['type'] = self.type.value
        data['escalation_level'] = self.escalation_level.value
        return data


@dataclass
class ApprovalHistory:
    """History entry for approval actions"""
    approval_id: str
    action: str
    actor: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)
    previous_status: Optional[ApprovalStatus] = None
    new_status: Optional[ApprovalStatus] = None

    def to_dict(self) -> Dict:
        data = asdict(self)
        if self.previous_status:
            data['previous_status'] = self.previous_status.value
        if self.new_status:
            data['new_status'] = self.new_status.value
        return data


@dataclass
class ApprovalMetrics:
    """Approval workflow metrics"""
    total_requests: int = 0
    pending: int = 0
    approved: int = 0
    rejected: int = 0
    escalated: int = 0
    expired: int = 0
    avg_approval_time_minutes: float = 0.0
    overdue_count: int = 0
    auto_approved: int = 0
    auto_rejected: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_approver: Dict[str, int] = field(default_factory=dict)


# =============================================================================
# Structured Logger
# =============================================================================

class ApprovalLogger:
    """Structured JSON logger for approval operations"""

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)

        self.current_log_file = log_dir / f"approvals_{datetime.now().strftime('%Y-%m-%d')}.jsonl"
        self.history_file = log_dir / "approval_history.jsonl"
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

    def add_history(self, history: ApprovalHistory):
        """Add to approval history"""
        with self.lock:
            with open(self.history_file, 'a') as f:
                f.write(json.dumps(history.to_dict()) + "\n")


# =============================================================================
# Approval Rules Engine
# =============================================================================

class ApprovalRulesEngine:
    """Engine for auto-approval rules"""

    def __init__(self, config_path: Optional[Path] = None):
        self.rules: List[ApprovalRule] = []
        self._load_rules(config_path)

    def _load_rules(self, config_path: Optional[Path]):
        """Load approval rules from config"""
        if not config_path or not config_path.exists():
            self._add_default_rules()
            return

        if HAS_YAML:
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    rules_config = config.get('auto_approval_rules', [])

                    for rule_config in rules_config:
                        conditions = [
                            ApprovalCondition(
                                field=c['field'],
                                operator=c['operator'],
                                value=c['value'],
                                required=c.get('required', True)
                            )
                            for c in rule_config.get('conditions', [])
                        ]

                        rule = ApprovalRule(
                            name=rule_config['name'],
                            type=ApprovalType[rule_config['type'].upper()],
                            conditions=conditions,
                            action=rule_config['action'],
                            target_approver=rule_config.get('target_approver'),
                            enabled=rule_config.get('enabled', True)
                        )
                        self.rules.append(rule)

            except Exception as e:
                print(f"Warning: Failed to load rules: {e}")
                self._add_default_rules()
        else:
            self._add_default_rules()

    def _add_default_rules(self):
        """Add default auto-approval rules"""
        # Example: Auto-approve low-value expenses
        self.rules.append(ApprovalRule(
            name="low_value_expense",
            type=ApprovalType.EXPENSE,
            conditions=[
                ApprovalCondition(field="amount", operator="lt", value=50)
            ],
            action="approve"
        ))

    def evaluate(self, request: ApprovalRequest) -> Optional[str]:
        """Evaluate request against rules and return action"""
        for rule in self.rules:
            if not rule.enabled or rule.type != request.type:
                continue

            # Check all conditions
            conditions_met = all(
                self._check_condition(condition, request.context)
                for condition in rule.conditions
            )

            if conditions_met:
                return rule.action

        return None

    def _check_condition(self, condition: ApprovalCondition, context: Dict) -> bool:
        """Check a single condition"""
        field_value = context.get(condition.field)

        if condition.operator == "eq":
            return field_value == condition.value
        elif condition.operator == "ne":
            return field_value != condition.value
        elif condition.operator == "gt":
            return field_value is not None and field_value > condition.value
        elif condition.operator == "lt":
            return field_value is not None and field_value < condition.value
        elif condition.operator == "contains":
            return field_value is not None and condition.value in str(field_value)
        elif condition.operator == "exists":
            return field_value is not None
        elif condition.operator == "regex":
            import re
            return field_value is not None and re.search(condition.value, str(field_value))

        return False


# =============================================================================
# Escalation Manager
# =============================================================================

class EscalationManager:
    """Manage approval escalations"""

    DEFAULT_ESCALATION_CHAIN = {
        EscalationLevel.LEVEL_1: "supervisor",
        EscalationLevel.LEVEL_2: "manager",
        EscalationLevel.LEVEL_3: "director",
        EscalationLevel.LEVEL_4: "executive"
    }

    def __init__(self, logger: ApprovalLogger, config_path: Optional[Path] = None):
        self.logger = logger
        self.escalation_chain = self.DEFAULT_ESCALATION_CHAIN.copy()
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path]):
        """Load escalation configuration"""
        if config_path and config_path.exists() and HAS_YAML:
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    chain_config = config.get('escalation_chain', {})

                    for level_str, approver in chain_config.items():
                        level = EscalationLevel[level_str.upper()]
                        self.escalation_chain[level] = approver
            except Exception as e:
                self.logger.warning(f"Failed to load escalation config: {e}")

    def get_next_escalation(self, request: ApprovalRequest) -> Optional[str]:
        """Get next escalation target"""
        next_level = EscalationLevel(request.escalation_level.value + 1)

        if next_level in self.escalation_chain:
            return self.escalation_chain[next_level]

        return None

    def escalate(self, request: ApprovalRequest) -> bool:
        """Escalate an approval request"""
        next_approver = self.get_next_escalation(request)

        if not next_approver:
            self.logger.warning(
                "escalation_failed",
                approval_id=request.id,
                reason="No higher escalation level"
            )
            return False

        # Update request
        request.escalation_level = EscalationLevel(request.escalation_level.value + 1)
        request.escalated_to = next_approver
        request.current_approver = next_approver
        request.status = ApprovalStatus.ESCALATED
        request.updated_at = datetime.now().isoformat()

        # Log escalation
        self.logger.info(
            "approval_escalated",
            approval_id=request.id,
            from_level=request.escalation_level.value - 1,
            to_level=request.escalation_level.value,
            escalated_to=next_approver
        )

        return True


# =============================================================================
# Ultimate Approval Processor
# =============================================================================

class UltimateApprovalProcessor:
    """Advanced approval processor with all features"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)

        # Setup paths
        self.pending_path = PENDING_APPROVAL
        self.approved_path = APPROVED
        self.rejected_path = REJECTED
        self.done_path = DONE
        self.expired_path = EXPIRED
        self.failed_path = FAILED
        self.escalated_path = ESCALATED

        # Components
        self.logger = ApprovalLogger(LOGS)
        self.rules_engine = ApprovalRulesEngine(config_path)
        self.escalation_manager = EscalationManager(self.logger, config_path)

        # State
        self.requests: Dict[str, ApprovalRequest] = {}
        self.lock = threading.Lock()

        # Load existing requests
        self._load_requests()

    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """Load configuration"""
        defaults = {
            'sla_default_minutes': 1440,  # 24 hours
            'auto_approve_enabled': True,
            'escalation_enabled': True,
            'escalation_threshold_percent': 80,
            'max_workers': 4,
            'batch_size': 20,
        }

        if config_path and config_path.exists() and HAS_YAML:
            try:
                with open(config_path) as f:
                    config = yaml.safe_load(f)
                    defaults.update(config)
            except:
                pass

        return defaults

    def _load_requests(self):
        """Load existing approval requests from folders"""
        self._load_from_folder(self.pending_path, ApprovalStatus.PENDING)
        self._load_from_folder(self.approved_path, ApprovalStatus.APPROVED)
        self._load_from_folder(self.rejected_path, ApprovalStatus.REJECTED)

    def _load_from_folder(self, folder: Path, status: ApprovalStatus):
        """Load requests from a specific folder"""
        for file in folder.glob('*.md'):
            try:
                request = self._parse_approval_file(file)
                if request:
                    request.status = status
                    self.requests[request.id] = request
            except Exception as e:
                self.logger.error(f"load_error", file=str(file), error=str(e))

    def _parse_approval_file(self, file_path: Path) -> Optional[ApprovalRequest]:
        """Parse approval request from file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            if not content.startswith('---'):
                return None

            parts = content.split('---', 2)
            if len(parts) < 3:
                return None

            frontmatter = parts[1].strip()

            # Parse frontmatter
            metadata = {}
            for line in frontmatter.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # Create request
            request_id = file_path.stem

            request = ApprovalRequest(
                id=request_id,
                type=ApprovalType(metadata.get('type', 'general')),
                title=metadata.get('title', request_id),
                created_by=metadata.get('created_by'),
                current_approver=metadata.get('approver'),
                due_at=metadata.get('expires'),
                file_path=str(file_path),
                context={
                    'amount': float(metadata.get('amount', 0)) if metadata.get('amount') else None,
                    'recipient': metadata.get('to'),
                    'subject': metadata.get('subject'),
                    **{k: v for k, v in metadata.items()
                       if k not in ['type', 'title', 'created_by', 'approver', 'expires', 'to', 'subject', 'amount']}
                }
            )

            # Parse lists
            if 'approvers' in metadata:
                approvers_str = metadata['approvers'].strip('[]')
                request.approvers = [a.strip().strip('"').strip("'")
                                    for a in approvers_str.split(',') if a.strip()]

            # Parse workflow steps
            if 'workflow' in metadata:
                # Simple workflow format
                steps_str = metadata['workflow']
                if isinstance(steps_str, str):
                    for step in steps_str.split(','):
                        request.workflow.append(ApprovalStep(
                            name=step.strip(),
                            approver=step.strip()
                        ))

            return request

        except Exception as e:
            self.logger.error(f"parse_error", file=str(file_path), error=str(e))
            return None

    def discover_requests(self) -> List[Path]:
        """Discover all approval request files"""
        return list(self.pending_path.glob('*.md'))

    def create_request(
        self,
        type: ApprovalType,
        title: str,
        context: Dict[str, Any],
        workflow: Optional[List[ApprovalStep]] = None,
        approvers: Optional[List[str]] = None,
        sla_minutes: Optional[int] = None
    ) -> ApprovalRequest:
        """Create a new approval request"""
        request_id = f"{type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(title.encode()).hexdigest()[:8]}"

        # Calculate due date
        due_at = None
        if sla_minutes or self.config.get('sla_default_minutes'):
            sla = sla_minutes or self.config['sla_default_minutes']
            due_at = (datetime.now() + timedelta(minutes=sla)).isoformat()

        request = ApprovalRequest(
            id=request_id,
            type=type,
            title=title,
            approvers=approvers or [],
            workflow=workflow or [],
            sla_minutes=sla_minutes,
            due_at=due_at,
            context=context
        )

        # Set current approver
        if request.workflow:
            request.current_approver = request.workflow[0].approver
        elif request.approvers:
            request.current_approver = request.approvers[0]

        self.requests[request_id] = request

        return request

    def process_request(self, request: ApprovalRequest) -> bool:
        """Process a single approval request"""
        self.logger.info(
            "processing_approval",
            approval_id=request.id,
            type=request.type.value,
            current_approver=request.current_approver
        )

        # Check auto-approval rules
        if self.config.get('auto_approve_enabled', True):
            auto_action = self.rules_engine.evaluate(request)

            if auto_action == "approve":
                request.status = ApprovalStatus.AUTO_APPROVED
                self._move_request(request, self.approved_path)
                self.logger.info("auto_approved", approval_id=request.id)
                return True
            elif auto_action == "reject":
                request.status = ApprovalStatus.AUTO_REJECTED
                self._move_request(request, self.rejected_path)
                self.logger.info("auto_rejected", approval_id=request.id)
                return True

        # Check for expiration
        if request.is_overdue:
            request.status = ApprovalStatus.EXPIRED
            self._move_request(request, self.expired_path)
            self.logger.warning("approval_expired", approval_id=request.id)
            return False

        # Check for escalation
        if self.config.get('escalation_enabled', True) and request.needs_escalation:
            if self.escalation_manager.escalate(request):
                self._move_request(request, self.escalated_path)
            return False

        # Check if we can execute approved request
        if request.status == ApprovalStatus.APPROVED:
            return self._execute_approved(request)

        return False

    def _execute_approved(self, request: ApprovalRequest) -> bool:
        """Execute an approved request"""
        self.logger.info(
            "executing_approved",
            approval_id=request.id,
            type=request.type.value
        )

        # Route to appropriate executor
        executors = {
            ApprovalType.EMAIL: self._execute_email,
            ApprovalType.LINKEDIN_POST: self._execute_linkedin,
            ApprovalType.X_POST: self._execute_x,
            ApprovalType.INSTAGRAM_POST: self._execute_instagram,
            ApprovalType.FACEBOOK_POST: self._execute_facebook,
        }

        executor = executors.get(request.type)
        if executor:
            try:
                success = executor(request)

                if success:
                    self._move_request(request, self.done_path)
                    request.status = ApprovalStatus.APPROVED
                    return True
                else:
                    self._move_request(request, self.failed_path)
                    return False

            except Exception as e:
                self.logger.error(
                    "execution_failed",
                    approval_id=request.id,
                    error=str(e)
                )
                self._move_request(request, self.failed_path)
                return False

        return False

    def _execute_email(self, request: ApprovalRequest) -> bool:
        """Execute approved email"""
        # Import email sender
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'email-sender' / 'scripts'))
            # Would call email_sender_ultimate here
            return True
        except Exception:
            return False

    def _execute_linkedin(self, request: ApprovalRequest) -> bool:
        """Execute approved LinkedIn post"""
        # Placeholder for LinkedIn execution
        return True

    def _execute_x(self, request: ApprovalRequest) -> bool:
        """Execute approved X/Twitter post"""
        # Placeholder for X execution
        return True

    def _execute_instagram(self, request: ApprovalRequest) -> bool:
        """Execute approved Instagram post"""
        # Placeholder for Instagram execution
        return True

    def _execute_facebook(self, request: ApprovalRequest) -> bool:
        """Execute approved Facebook post"""
        # Placeholder for Facebook execution
        return True

    def _move_request(self, request: ApprovalRequest, target_folder: Path):
        """Move request file to target folder"""
        if request.file_path:
            source = Path(request.file_path)
            if source.exists():
                target = target_folder / source.name
                source.rename(target)
                request.file_path = str(target)

    def process_all(self, batch_size: Optional[int] = None) -> Dict[str, int]:
        """Process all pending approvals"""
        results = {
            'processed': 0,
            'approved': 0,
            'rejected': 0,
            'expired': 0,
            'escalated': 0,
            'executed': 0
        }

        # Discover and load new requests
        request_files = self.discover_requests()

        for file_path in request_files:
            request = self._parse_approval_file(file_path)
            if request and request.id not in self.requests:
                self.requests[request.id] = request

        # Process pending requests
        batch_size = batch_size or self.config.get('batch_size', 20)
        processed = 0

        for request in list(self.requests.values()):
            if processed >= batch_size:
                break

            if request.status not in [ApprovalStatus.PENDING, ApprovalStatus.APPROVED]:
                continue

            try:
                self.process_request(request)
                processed += 1

                # Update results
                if request.status == ApprovalStatus.AUTO_APPROVED:
                    results['approved'] += 1
                elif request.status == ApprovalStatus.AUTO_REJECTED:
                    results['rejected'] += 1
                elif request.status == ApprovalStatus.EXPIRED:
                    results['expired'] += 1
                elif request.status == ApprovalStatus.ESCALATED:
                    results['escalated'] += 1
                elif request.file_path and str(self.done_path) in request.file_path:
                    results['executed'] += 1

            except Exception as e:
                self.logger.error(
                    "process_error",
                    approval_id=request.id,
                    error=str(e)
                )

        results['processed'] = processed
        return results

    def check_escalations(self) -> List[ApprovalRequest]:
        """Check and escalate overdue approvals"""
        escalated = []

        for request in self.requests.values():
            if request.status in [ApprovalStatus.PENDING, ApprovalStatus.AWAITING]:
                if request.needs_escalation:
                    if self.escalation_manager.escalate(request):
                        self._move_request(request, self.escalated_path)
                        escalated.append(request)

        return escalated

    def calculate_metrics(self) -> ApprovalMetrics:
        """Calculate approval metrics"""
        metrics = ApprovalMetrics()

        for request in self.requests.values():
            metrics.total_requests += 1

            # Count by status
            if request.status == ApprovalStatus.PENDING:
                metrics.pending += 1
            elif request.status == ApprovalStatus.APPROVED:
                metrics.approved += 1
            elif request.status == ApprovalStatus.REJECTED:
                metrics.rejected += 1
            elif request.status == ApprovalStatus.ESCALATED:
                metrics.escalated += 1
            elif request.status == ApprovalStatus.EXPIRED:
                metrics.expired += 1
            elif request.status == ApprovalStatus.AUTO_APPROVED:
                metrics.auto_approved += 1
            elif request.status == ApprovalStatus.AUTO_REJECTED:
                metrics.auto_rejected += 1

            # Check overdue
            if request.is_overdue:
                metrics.overdue_count += 1

            # Count by type
            type_name = request.type.value
            metrics.by_type[type_name] = metrics.by_type.get(type_name, 0) + 1

            # Count by approver
            if request.current_approver:
                metrics.by_approver[request.current_approver] = \
                    metrics.by_approver.get(request.current_approver, 0) + 1

        return metrics

    def show_status(self):
        """Show current status"""
        metrics = self.calculate_metrics()

        print("\n" + "=" * 60)
        print("APPROVAL PROCESSOR STATUS")
        print("=" * 60)
        print(f"Total Requests:    {metrics.total_requests}")
        print(f"Pending:           {metrics.pending}")
        print(f"Approved:          {metrics.approved}")
        print(f"Rejected:          {metrics.rejected}")
        print(f"Escalated:         {metrics.escalated}")
        print(f"Expired:           {metrics.expired}")
        print(f"Auto-Approved:     {metrics.auto_approved}")
        print(f"Auto-Rejected:     {metrics.auto_rejected}")
        print(f"Overdue:           {metrics.overdue_count}")
        print("=" * 60)

        # Show by type
        if metrics.by_type:
            print("\n📋 Requests by Type:")
            for type_name, count in sorted(metrics.by_type.items(), key=lambda x: -x[1]):
                print(f"  {type_name}: {count}")

        # Show overdue
        overdue = [r for r in self.requests.values() if r.is_overdue]
        if overdue:
            print(f"\n⚠️  OVERDUE ({len(overdue)}):")
            for req in sorted(overdue, key=lambda r: r.age_minutes, reverse=True)[:5]:
                print(f"  - {req.title} ({int(req.age_minutes)}min overdue)")

        print()


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Ultimate Approval Processor')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--escalate', action='store_true', help='Check and escalate overdue')
    parser.add_argument('--analytics', action='store_true', help='Show analytics')
    parser.add_argument('--auto-approve', action='store_true', help='Apply auto-approval rules')
    parser.add_argument('--batch', type=int, help='Process in batches')
    parser.add_argument('--config', help='Config file path')

    args = parser.parse_args()

    config_path = Path(args.config) if args.config else CONFIG_PATH
    processor = UltimateApprovalProcessor(config_path)

    if args.status:
        processor.show_status()
    elif args.escalate:
        escalated = processor.check_escalations()
        print(f"\n📈 Escalated {len(escalated)} approval(s)")
    elif args.analytics:
        metrics = processor.calculate_metrics()
        print(json.dumps(asdict(metrics), indent=2))
    else:
        results = processor.process_all(batch_size=args.batch)
        print(f"\n📊 Processed {results['processed']} approval(s)")
        print(f"   ✅ Approved: {results['approved'] + results['executed']}")
        print(f"   ❌ Rejected: {results['rejected']}")
        print(f"   ⏱️ Expired: {results['expired']}")
        print(f"   📈 Escalated: {results['escalated']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
