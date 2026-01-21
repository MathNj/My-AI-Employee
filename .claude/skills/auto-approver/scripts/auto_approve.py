#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-Approver - AI-powered approval decision system

Uses Claude's reasoning to automatically approve, reject, or hold
pending action requests based on context and Company_Handbook.md rules.
"""

import sys
import io
# Configure UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from pathlib import Path
import json
import shutil
import logging
import time
import argparse
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess

# Setup logging first with UTF-8 support
logger = logging.getLogger(__name__)

# Create UTF-8 stream handler
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[stream_handler],
    force=True  # Override any existing configuration
)

# Error Recovery and Audit Logging
try:
    watchers_path = Path(__file__).parent.parent.parent.parent / "watchers"
    sys.path.insert(0, str(watchers_path))
    from error_recovery import retry_with_backoff, handle_error_with_recovery
    from audit_logger import log_approval, log_error
    _import_error = None
except ImportError as e:
    # Define fallback functions if modules not available
    _import_error = str(e)
    logger.warning(f"Could not import error_recovery/audit_logger modules: {e}")

    def retry_with_backoff(func, max_attempts=3, base_delay=1):
        """Fallback retry decorator"""
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(base_delay * (2 ** attempt))
            return wrapper
        return wrapper

    def handle_error_with_recovery(error, context=""):
        """Fallback error handler"""
        logger.error(f"Error in {context}: {error}")
        return None

    def log_approval(decision, details):
        """Fallback approval logger"""
        logger.info(f"Approval decision: {decision} - {details}")

    def log_error(error, context=""):
        """Fallback error logger"""
        logger.error(f"Error in {context}: {error}")

# Configuration
SCRIPT_PATH = Path(__file__).parent
VAULT_PATH = SCRIPT_PATH.parent.parent.parent.parent
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
REJECTED_PATH = VAULT_PATH / "Rejected"
LOGS_PATH = VAULT_PATH / "Logs"
CONFIG_PATH = SCRIPT_PATH.parent / "config"
COMPANY_HANDBOOK = VAULT_PATH / "Company_Handbook.md"

# Setup file logging with UTF-8 encoding
LOGS_PATH.mkdir(exist_ok=True)
log_file = LOGS_PATH / f'auto_approver_{datetime.now().strftime("%Y-%m-%d")}.log'
file_handler = logging.FileHandler(log_file, encoding='utf-8')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)


class AutoApprover:
    """AI-powered auto-approval system"""

    def __init__(self, config_path: Path = None):
        self.config = self.load_config(config_path)
        self.known_contacts = self.load_known_contacts()
        self.company_handbook = self.load_company_handbook()
        self.decisions_log = []

    def load_config(self, config_path: Path = None) -> Dict:
        """Load configuration from config.json"""
        config_file = config_path or CONFIG_PATH / "config.json"

        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            # Default configuration
            return {
                "check_interval": 30,
                "confidence_threshold": 0.85,
                "dry_run": False,
                "learn_from_corrections": True,
                "rules": {
                    "email": {
                        "known_contact_threshold": 5,
                        "pattern_match_required": True,
                        "max_recipients": 1
                    },
                    "social_media": {
                        "scheduled_only": True,
                        "controversial_keywords": ["politics", "religion"],
                        "max_posts_per_day": 3
                    },
                    "payments": {
                        "auto_approve": False,
                        "max_amount": 0
                    }
                }
            }

    def load_known_contacts(self) -> Dict:
        """Load known contacts database"""
        contacts_file = CONFIG_PATH / "known_contacts.json"

        if contacts_file.exists():
            with open(contacts_file, 'r') as f:
                return json.load(f).get("contacts", {})
        else:
            # Initialize empty contacts
            return {}

    def load_company_handbook(self) -> str:
        """Load Company_Handbook.md for rules"""
        if COMPANY_HANDBOOK.exists():
            return COMPANY_HANDBOOK.read_text(encoding='utf-8')
        else:
            logger.warning("Company_Handbook.md not found")
            return ""

    def get_cross_domain_context(self, frontmatter: Dict) -> Dict:
        """
        Load cross-domain enrichment data from frontmatter.

        Extracts domain classification, business relevance, and entities
        that were added by the cross-domain-bridge skill.
        """
        context = {
            'domain': frontmatter.get('domain', 'personal'),
            'business_relevance_score': frontmatter.get('business_relevance_score', 0.0),
            'entities_extracted': frontmatter.get('entities_extracted', {}),
            'approval_required': frontmatter.get('approval_required', False),
            'approval_reason': frontmatter.get('approval_reason', ''),
            'personal_boundary_violation': frontmatter.get('personal_boundary_violation', False)
        }
        return context

    def get_pending_files(self) -> List[Path]:
        """Get all files in Pending_Approval including subdirectories"""
        if not PENDING_APPROVAL_PATH.exists():
            return []

        # Get all .md files in root
        files = list(PENDING_APPROVAL_PATH.glob("*.md"))

        # Get all .md files in subdirectories recursively
        files.extend(PENDING_APPROVAL_PATH.rglob("*.md"))

        # Remove duplicates and sort
        files = list(set(files))
        files.sort(key=lambda x: x.stat().st_mtime)

        return files

    def parse_frontmatter(self, file_path: Path) -> Dict:
        """Parse YAML frontmatter from markdown file"""
        content = file_path.read_text(encoding='utf-8')
        lines = content.split('\n')

        if not lines[0].startswith('---'):
            return {}

        frontmatter = {}
        for line in lines[1:]:
            if line.startswith('---'):
                break
            if ':' in line:
                key, value = line.split(':', 1)
                frontmatter[key.strip()] = value.strip()

        return frontmatter

    def analyze_with_claude(self, file_path: Path) -> Dict:
        """
        Use Claude AI to analyze and decide on approval request.

        This function calls Claude Code with the skill to get AI reasoning.
        """
        frontmatter = self.parse_frontmatter(file_path)
        content = file_path.read_text(encoding='utf-8')

        # Build analysis prompt
        prompt = f"""Analyze this approval request and decide: APPROVE, REJECT, or HOLD

Request File: {file_path.name}
Type: {frontmatter.get('type', 'unknown')}

Frontmatter:
{json.dumps(frontmatter, indent=2)}

Content:
{content}

Context from Company_Handbook:
{self.company_handbook[:2000]}  # First 2000 chars

Known Contacts:
{json.dumps(self.known_contacts, indent=2)}

Your task:
1. Analyze the request (recipient, content, type, urgency)
2. Check if recipient is a known contact
3. Evaluate against Company_Handbook rules
4. Consider safety and appropriateness
5. Make a decision: APPROVE, REJECT, or HOLD

Respond in JSON format:
{{
  "decision": "approve|reject|hold",
  "confidence": 0.0-1.0,
  "reasoning": "Detailed explanation of your decision",
  "safety_concerns": ["any concerns or null"],
  "recommendation": "what to do next"
}}
"""

        # In a real implementation, this would call Claude's API
        # For now, we'll do rule-based analysis as placeholder
        return self.rule_based_analysis(frontmatter, content)

    def rule_based_analysis(self, frontmatter: Dict, content: str) -> Dict:
        """
        Fallback rule-based analysis with cross-domain context integration

        This analyzes the request using:
        1. Configured rules
        2. Known contacts database
        3. Cross-domain enrichment (from cross-domain-bridge skill)
        """
        # Load cross-domain context
        cross_domain_ctx = self.get_cross_domain_context(frontmatter)

        request_type = frontmatter.get('type', 'unknown')
        recipient = frontmatter.get('recipient', frontmatter.get('to', ''))
        subject = frontmatter.get('subject', '')

        # Check if known contact
        known_contact = self.known_contacts.get(recipient, {})
        interaction_count = known_contact.get('interactions', 0)
        trust_score = known_contact.get('trust_score', 0.0)

        # CROSS-DOMAIN CHECKS
        # If cross-domain bridge flagged as requiring approval, respect that
        if cross_domain_ctx.get('approval_required'):
            return {
                "decision": "hold",
                "confidence": 0.95,
                "reasoning": f"Cross-domain analysis requires approval: {cross_domain_ctx.get('approval_reason', 'Unknown reason')}",
                "safety_concerns": ["Cross-domain approval required"],
                "recommendation": "Hold for human review"
            }

        # Check personal boundary violation
        if cross_domain_ctx.get('personal_boundary_violation'):
            # Check business importance to decide
            if cross_domain_ctx.get('business_relevance_score', 0) < 0.7:
                return {
                    "decision": "defer",
                    "confidence": 0.85,
                    "reasoning": "Non-urgent business matter during personal time. Deferring to next business day (9 AM).",
                    "safety_concerns": ["Personal boundary"],
                    "recommendation": "Defer to 9 AM next business day"
                }

        # Email analysis
        if request_type == 'email':
            email_rules = self.config['rules']['email']

            # Check if it's a known contact with enough interactions
            if interaction_count >= email_rules['known_contact_threshold']:
                # Check for safe content
                if self.is_safe_content(subject, content):
                    return {
                        "decision": "approve",
                        "confidence": min(0.95, 0.7 + (trust_score * 0.2)),
                        "reasoning": f"Email to known contact {recipient} with {interaction_count} previous interactions. Trust score: {trust_score:.2f}.",
                        "safety_concerns": None,
                        "recommendation": "Move to /Approved"
                    }
                else:
                    return {
                        "decision": "hold",
                        "confidence": 0.90,
                        "reasoning": "Content contains keywords that require human review.",
                        "safety_concerns": ["Potential sensitive content"],
                        "recommendation": "Hold for human review"
                    }
            else:
                return {
                    "decision": "hold",
                    "confidence": 0.95,
                    "reasoning": f"New or unknown contact (only {interaction_count} interactions). Requires human verification.",
                    "safety_concerns": ["Unknown recipient"],
                    "recommendation": "Hold for human review"
                }

        # Social media analysis
        elif request_type in ['linkedin_post', 'social_media']:
            social_rules = self.config['rules']['social_media']

            if self.is_safe_content(subject, content):
                return {
                    "decision": "approve",
                    "confidence": 0.85,
                    "reasoning": "Social media post with safe, professional content.",
                    "safety_concerns": None,
                    "recommendation": "Move to /Approved"
                }
            else:
                return {
                    "decision": "hold",
                    "confidence": 0.90,
                    "reasoning": "Social media post contains topics requiring review.",
                    "safety_concerns": ["Potential controversial content"],
                    "recommendation": "Hold for human review"
                }

        # Default: hold for review
        return {
            "decision": "hold",
            "confidence": 0.80,
            "reasoning": f"Request type '{request_type}' requires human review.",
            "safety_concerns": ["Unknown request type"],
            "recommendation": "Hold for human review"
        }

    def is_safe_content(self, subject: str, content: str) -> bool:
        """Check if content is safe for auto-approval"""
        text = (subject + " " + content).lower()

        # Check for controversial keywords
        controversial_keywords = self.config['rules']['social_media']['controversial_keywords']
        for keyword in controversial_keywords:
            if keyword.lower() in text:
                return False

        # Check for urgency flags (hold unless known contact)
        urgent_keywords = ['urgent', 'asap', 'immediate', 'emergency']
        if any(kw in text for kw in urgent_keywords):
            return False

        # Check for financial keywords
        financial_keywords = ['payment', 'invoice', 'transfer', 'bank', 'credit card']
        if any(kw in text for kw in financial_keywords):
            return False

        return True

    def process_file(self, file_path: Path, dry_run: bool = False) -> Dict:
        """Process a single approval request"""
        logger.info(f"Processing: {file_path.name}")

        # Parse frontmatter to get item type
        frontmatter = self.parse_frontmatter(file_path)

        # Analyze with Claude (or rules as fallback)
        analysis = self.analyze_with_claude(file_path)

        decision = analysis['decision']
        confidence = analysis['confidence']
        reasoning = analysis['reasoning']

        # Check confidence threshold
        if confidence < self.config['confidence_threshold']:
            logger.info(f"Confidence {confidence:.2f} below threshold {self.config['confidence_threshold']:.2f} - holding for review")
            decision = 'hold'

        # Log to audit trail (standardized format)
        try:
            item_type = frontmatter.get('type', 'unknown')
            log_approval(
                item_type=item_type,
                item_id=file_path.name,
                decision=decision,
                confidence=confidence,
                reasoning=reasoning
            )
        except Exception as e:
            logger.warning(f"Failed to log to audit trail: {e}")

        # Log the decision (legacy format for backward compatibility)
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "request_file": file_path.name,
            "decision": decision,
            "confidence": confidence,
            "reasoning": reasoning,
            "dry_run": dry_run
        }
        self.decisions_log.append(log_entry)

        # Execute decision
        if not dry_run:
            if decision == 'approve':
                # Preserve subdirectory structure
                relative_path = file_path.relative_to(PENDING_APPROVAL_PATH)
                dest_path = APPROVED_PATH / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"[+] APPROVED: {relative_path}")
                logger.info(f"   Reasoning: {reasoning}")

            elif decision == 'reject':
                # Preserve subdirectory structure
                relative_path = file_path.relative_to(PENDING_APPROVAL_PATH)
                dest_path = REJECTED_PATH / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file_path), str(dest_path))
                logger.info(f"[-] REJECTED: {relative_path}")
                logger.info(f"   Reasoning: {reasoning}")

            else:  # hold
                relative_path = file_path.relative_to(PENDING_APPROVAL_PATH)
                logger.info(f"[=] HELD: {relative_path}")
                logger.info(f"   Reasoning: {reasoning}")
        else:
            logger.info(f"[DRY RUN] Would {decision.upper()}: {file_path.name}")
            logger.info(f"   Confidence: {confidence:.2f}")
            logger.info(f"   Reasoning: {reasoning}")

        return log_entry

    def save_decision_log(self):
        """Save all decisions to log file"""
        log_file = LOGS_PATH / f'auto_approver_decisions_{datetime.now().strftime("%Y-%m-%d")}.json'

        existing_logs = []
        if log_file.exists():
            with open(log_file, 'r') as f:
                existing_logs = json.load(f)

        existing_logs.extend(self.decisions_log)

        with open(log_file, 'w') as f:
            json.dump(existing_logs, f, indent=2)

    def run_once(self, dry_run: bool = False):
        """Process all pending files once"""
        pending_files = self.get_pending_files()

        if not pending_files:
            logger.info("No pending approvals to process")
            return

        logger.info(f"Found {len(pending_files)} pending approval(s)")

        for file_path in pending_files:
            try:
                self.process_file(file_path, dry_run)
            except Exception as e:
                logger.error(f"Error processing {file_path.name}: {e}")

                # Use error recovery system
                try:
                    recovery_strategy = handle_error_with_recovery(e, f"auto_approver processing {file_path.name}")
                    logger.info(f"Error recovery: {recovery_strategy['message']}")

                    # Log error to audit trail
                    log_error(
                        action_type="approval",
                        actor="auto_approver",
                        error=str(e),
                        context={"file": file_path.name},
                        skill="auto-approver"
                    )
                except Exception as recovery_error:
                    logger.error(f"Failed to handle error recovery: {recovery_error}")

        # Save decision log
        self.save_decision_log()

    def run_continuous(self, dry_run: bool = False):
        """Run continuous monitoring loop"""
        logger.info("=" * 70)
        logger.info("Auto-Approver Started")
        logger.info(f"Check interval: {self.config['check_interval']} seconds")
        logger.info(f"Confidence threshold: {self.config['confidence_threshold']}")
        logger.info(f"Dry run: {dry_run}")
        logger.info("=" * 70)

        try:
            while True:
                self.run_once(dry_run)
                time.sleep(self.config['check_interval'])

        except KeyboardInterrupt:
            logger.info("\n" + "=" * 70)
            logger.info("Auto-Approver Stopped")
            logger.info("=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI-powered auto-approver')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--dry-run', action='store_true', help='Show decisions without executing')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Create auto-approver
    approver = AutoApprover()

    if args.once:
        approver.run_once(dry_run=args.dry_run)
    else:
        approver.run_continuous(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
