#!/usr/bin/env python3
"""
Email Sender - Send emails via MCP or SMTP after approval

This script handles:
- Email composition
- MCP server integration
- SMTP fallback
- Approval workflow integration
- Attachment handling
- Activity logging

Usage:
    # Create approval request
    python send_email.py --to "client@example.com" --subject "Invoice" --body "..." --create-approval

    # Execute approved email
    python send_email.py --execute-approved /path/to/approved.md

    # Dry run (test mode)
    python send_email.py --to "..." --subject "..." --body "..." --dry-run
"""

import json
import os
import sys
import argparse
import smtplib
from datetime import datetime, timedelta
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent / "AI_Employee_Vault"
SMTP_CONFIG_PATH = Path(__file__).parent.parent.parent.parent / "watchers" / "credentials" / "smtp_config.json"
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
LOGS_PATH = VAULT_PATH / "Logs"


def load_smtp_config():
    """Load SMTP configuration from file."""
    if not SMTP_CONFIG_PATH.exists():
        return None

    try:
        with open(SMTP_CONFIG_PATH, 'r') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"⚠️ Error loading SMTP config: {e}")
        return None


def send_via_smtp(to, subject, body, attachments=None, html=False, dry_run=False):
    """
    Send email via SMTP.

    Args:
        to: Recipient email (or list of emails)
        subject: Email subject
        body: Email body content
        attachments: List of file paths to attach
        html: If True, body is HTML
        dry_run: If True, don't actually send

    Returns:
        True if successful, False otherwise
    """
    config = load_smtp_config()

    if not config:
        print("❌ SMTP configuration not found")
        print("   Create: watchers/credentials/smtp_config.json")
        return False

    # Extract config
    smtp_server = config.get('smtp_server', 'smtp.gmail.com')
    smtp_port = config.get('smtp_port', 587)
    email_address = config.get('email_address')
    email_password = config.get('email_password')
    use_tls = config.get('use_tls', True)

    if not email_address or not email_password:
        print("❌ Email address or password missing in config")
        return False

    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_address
    msg['To'] = to if isinstance(to, str) else ', '.join(to)
    msg['Subject'] = subject

    # Attach body
    if html:
        msg.attach(MIMEText(body, 'html'))
    else:
        msg.attach(MIMEText(body, 'plain'))

    # Attach files
    if attachments:
        for filepath in attachments:
            filepath = Path(filepath)
            if not filepath.exists():
                print(f"⚠️ Attachment not found: {filepath}")
                continue

            with open(filepath, 'rb') as f:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {filepath.name}'
                )
                msg.attach(part)

    if dry_run:
        print("🧪 DRY RUN - Email preview:")
        print("─" * 60)
        print(f"From: {email_address}")
        print(f"To: {msg['To']}")
        print(f"Subject: {subject}")
        print(f"Body: {body[:200]}...")
        if attachments:
            print(f"Attachments: {', '.join([Path(a).name for a in attachments])}")
        print("─" * 60)
        return True

    # Send email
    try:
        print(f"📤 Sending email via SMTP ({smtp_server})...")

        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)

        server.login(email_address, email_password)
        server.send_message(msg)
        server.quit()

        print("✅ Email sent successfully!")
        log_activity('email_sent_smtp', {
            'to': to,
            'subject': subject,
            'attachments': len(attachments) if attachments else 0
        })
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ SMTP Authentication failed")
        print("   - For Gmail, use app password (not account password)")
        print("   - Generate at: https://myaccount.google.com/apppasswords")
        return False
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        log_activity('email_failed_smtp', {
            'to': to,
            'subject': subject,
            'error': str(e)
        })
        return False


def send_via_mcp(to, subject, body, attachments=None, html=False, dry_run=False):
    """
    Send email via MCP server.

    Note: MCP integration requires MCP server to be configured in Claude Code.
    This is a placeholder for MCP integration.

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        attachments: List of file paths
        html: If True, body is HTML
        dry_run: If True, don't send

    Returns:
        True if successful, False otherwise
    """
    print("⚠️ MCP integration not yet implemented")
    print("   Falling back to SMTP...")
    return False


def send_email(to, subject, body, attachments=None, html=False, method='auto', dry_run=False):
    """
    Send email using specified method with automatic fallback.

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        attachments: List of file paths to attach
        html: If True, body is HTML
        method: 'mcp', 'smtp', or 'auto'
        dry_run: If True, don't actually send

    Returns:
        True if successful, False otherwise
    """
    if method == 'auto':
        # Try MCP first, fall back to SMTP
        success = send_via_mcp(to, subject, body, attachments, html, dry_run)
        if not success:
            success = send_via_smtp(to, subject, body, attachments, html, dry_run)
        return success
    elif method == 'mcp':
        return send_via_mcp(to, subject, body, attachments, html, dry_run)
    elif method == 'smtp':
        return send_via_smtp(to, subject, body, attachments, html, dry_run)
    else:
        print(f"❌ Unknown method: {method}")
        return False


def create_approval_request(to, subject, body, attachments=None, html=False):
    """
    Create an approval request file in /Pending_Approval folder.

    Args:
        to: Recipient email
        subject: Email subject
        body: Email body
        attachments: List of file paths
        html: If True, body is HTML

    Returns:
        Path to created approval file
    """
    timestamp = datetime.now().isoformat().replace(':', '-').replace('.', '-')
    filename = f"EMAIL_{timestamp}.md"
    filepath = PENDING_APPROVAL_PATH / filename

    # Ensure directory exists
    PENDING_APPROVAL_PATH.mkdir(parents=True, exist_ok=True)

    # Format attachments display
    if attachments:
        attachment_list = []
        for att in attachments:
            att_path = Path(att)
            size = att_path.stat().st_size if att_path.exists() else 0
            size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.1f} MB"
            attachment_list.append(f"- {att_path.name} ({size_str})")
        attachments_display = "\n".join(attachment_list)
    else:
        attachments_display = "*No attachments*"

    # Create approval file content
    content = f"""---
type: email
action: send_email
to: "{to}"
subject: "{subject}"
body: "{body[:200]}..."
body_full: |
{body}
attachments: {json.dumps([str(a) for a in attachments] if attachments else [])}
html: {html}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=1)).isoformat()}
status: pending
---

# Email Approval Request

## Email Preview

**To:** {to}
**Subject:** {subject}

{body}

---

## Attachments

{attachments_display}

---

## Email Details

- **Type:** {"HTML" if html else "Plain Text"}
- **Character Count:** {len(body)}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Expires:** {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}

## Approval Instructions

**To Approve:**
Move this file to `/Approved` folder

**To Reject:**
Move this file to `/Rejected` folder

**Note:** This approval expires in 24 hours

---

*Created by email-sender skill*
"""

    # Write approval file
    filepath.write_text(content, encoding='utf-8')

    print(f"✅ Approval request created: {filename}")
    print(f"   Location: {filepath}")
    print(f"   Expires: {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')}")

    log_activity('email_approval_created', {
        'file': filename,
        'to': to,
        'subject': subject
    })

    return filepath


def execute_approved_email(approval_file_path):
    """
    Execute an email from an approved approval file.

    Args:
        approval_file_path: Path to approved file

    Returns:
        True if successful, False otherwise
    """
    approval_path = Path(approval_file_path)

    if not approval_path.exists():
        print(f"❌ Approval file not found: {approval_path}")
        return False

    # Read approval file
    content = approval_path.read_text(encoding='utf-8')

    # Extract frontmatter
    if not content.startswith('---'):
        print("❌ Invalid approval file format")
        return False

    parts = content.split('---', 2)
    if len(parts) < 3:
        print("❌ Invalid approval file format")
        return False

    # Parse frontmatter (simple YAML parsing)
    frontmatter = {}
    in_multiline = False
    multiline_key = None
    multiline_content = []

    for line in parts[1].strip().split('\n'):
        if in_multiline:
            if line and not line.startswith(' '):
                # End of multiline
                frontmatter[multiline_key] = '\n'.join(multiline_content)
                in_multiline = False
                multiline_content = []
            else:
                multiline_content.append(line.strip())

        if ':' in line and not in_multiline:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()

            if value == '|':
                # Start of multiline
                in_multiline = True
                multiline_key = key
            elif value.startswith('['):
                # JSON array
                try:
                    frontmatter[key] = json.loads(value)
                except:
                    frontmatter[key] = value
            elif value in ['true', 'false']:
                frontmatter[key] = value == 'true'
            else:
                frontmatter[key] = value.strip('"')

    # Handle final multiline
    if in_multiline:
        frontmatter[multiline_key] = '\n'.join(multiline_content)

    # Extract email parameters
    to = frontmatter.get('to', '')
    subject = frontmatter.get('subject', '')
    body = frontmatter.get('body_full', frontmatter.get('body', ''))
    attachments = frontmatter.get('attachments', [])
    html = frontmatter.get('html', False)

    if not to or not subject:
        print("❌ Missing required fields (to, subject)")
        return False

    print(f"📤 Executing approved email...")
    print(f"   To: {to}")
    print(f"   Subject: {subject}")

    # Send email
    success = send_email(to, subject, body, attachments, html)

    if success:
        # Move approval file to Done folder
        done_path = VAULT_PATH / "Done" / approval_path.name
        done_path.parent.mkdir(parents=True, exist_ok=True)
        approval_path.rename(done_path)
        print(f"✅ Moved approval file to Done")

    return success


def log_activity(action, details):
    """Log activity to JSON log file."""
    LOGS_PATH.mkdir(parents=True, exist_ok=True)

    log_date = datetime.now().strftime('%Y-%m-%d')
    log_file = LOGS_PATH / f'email_activity_{log_date}.json'

    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details,
        'skill': 'email-sender'
    }

    # Read existing logs
    if log_file.exists():
        try:
            logs = json.loads(log_file.read_text())
        except:
            logs = []
    else:
        logs = []

    # Append new entry
    logs.append(log_entry)

    # Write back
    log_file.write_text(json.dumps(logs, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Email Sender')

    parser.add_argument('--to', type=str,
                        help='Recipient email address')
    parser.add_argument('--subject', type=str,
                        help='Email subject')
    parser.add_argument('--body', type=str,
                        help='Email body (plain text)')
    parser.add_argument('--body-html', type=str,
                        help='Email body (HTML)')
    parser.add_argument('--attach', action='append',
                        help='Attachment file path (can use multiple times)')
    parser.add_argument('--create-approval', action='store_true',
                        help='Create approval request instead of sending')
    parser.add_argument('--execute-approved', type=str,
                        help='Execute approved email from file path')
    parser.add_argument('--method', choices=['auto', 'mcp', 'smtp'], default='auto',
                        help='Sending method (default: auto)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Test mode - show preview without sending')
    parser.add_argument('--send-now', action='store_true',
                        help='Send immediately without approval (not recommended)')

    args = parser.parse_args()

    # Execute approved email
    if args.execute_approved:
        success = execute_approved_email(args.execute_approved)
        sys.exit(0 if success else 1)

    # Create or send email
    if args.to and args.subject:
        body = args.body_html if args.body_html else (args.body or '')
        html = bool(args.body_html)

        if args.create_approval:
            create_approval_request(args.to, args.subject, body, args.attach, html)
        elif args.send_now:
            print("⚠️ Sending without approval (not recommended for production)")
            send_email(args.to, args.subject, body, args.attach, html, args.method, args.dry_run)
        else:
            # Default: create approval
            create_approval_request(args.to, args.subject, body, args.attach, html)
        return

    # No valid command
    parser.print_help()


if __name__ == '__main__':
    main()
