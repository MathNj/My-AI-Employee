#!/usr/bin/env python3
"""
Email Sender via Gmail MCP Server

Sends emails using the Gmail MCP server (OAuth) instead of SMTP.
This script is a wrapper that calls the Gmail MCP server.

The Gmail MCP server should be running before using this script.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# Configuration
VAULT_PATH = Path(__file__).parent.parent.parent.parent
PENDING_APPROVAL_PATH = VAULT_PATH / "Pending_Approval"
APPROVED_PATH = VAULT_PATH / "Approved"
LOGS_PATH = VAULT_PATH / "Logs"
MCP_SERVER_PATH = VAULT_PATH / "mcp-servers" / "gmail-mcp"


def send_via_mcp(to, subject, body, attachments=None, cc=None, bcc=None, html=False):
    """
    Send email using Gmail MCP server.

    Args:
        to: Recipient email (string or list)
        subject: Email subject
        body: Email body content
        attachments: List of file paths (optional)
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html: If True, body is HTML (default: False)

    Returns:
        True if successful, False otherwise
    """

    # Build email data
    email_data = {
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "body": body,
        "isHtml": html
    }

    if cc:
        email_data["cc"] = [cc] if isinstance(cc, str) else cc

    if bcc:
        email_data["bcc"] = [bcc] if isinstance(bcc, str) else bcc

    if attachments:
        email_data["attachments"] = [
            {"filename": Path(a).name, "path": str(a)}
            for a in (attachments if isinstance(attachments, list) else [attachments])
        ]

    # Call Gmail MCP server via stdio
    try:
        # The Gmail MCP server is a Node.js process
        mcp_executable = MCP_SERVER_PATH / "dist" / "index.js"

        if not mcp_executable.exists():
            print(f"❌ Gmail MCP server not found at: {mcp_executable}")
            print("   Please build the MCP server: cd mcp-servers/gmail-mcp && npm run build")
            return False

        # Create MCP request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": "send_email",
                "arguments": email_data
            }
        }

        # Call MCP server
        result = subprocess.run(
            ["node", str(mcp_executable)],
            input=json.dumps(request) + "\n",
            capture_output=True,
            text=True,
            cwd=str(MCP_SERVER_PATH),
            timeout=30
        )

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if "result" in response:
                print("✅ Email sent successfully via Gmail MCP")
                return True
            else:
                print(f"❌ Error: {response.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ MCP server error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("❌ Timeout sending email")
        return False
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False


def execute_approved_email(approved_file):
    """
    Execute an approved email request.

    Args:
        approved_file: Path to approved email markdown file
    """
    if not approved_file.exists():
        print(f"❌ File not found: {approved_file}")
        return False

    # Parse frontmatter
    content = approved_file.read_text(encoding='utf-8')
    lines = content.split('\n')

    frontmatter = {}
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            break
        if ':' in line:
            key, value = line.split(':', 1)
            frontmatter[key.strip()] = value.strip()

    # Extract email data
    to = frontmatter.get('to', frontmatter.get('recipient', ''))
    subject = frontmatter.get('subject', '')

    # Get body content (after frontmatter)
    body_start = None
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0:
            body_start = i + 1
            break

    body = '\n'.join(lines[body_start:]) if body_start else ""

    # Check for attachments
    attachments = None
    if 'attachments' in frontmatter:
        attachments = frontmatter['attachments'].split(',')

    # Send email
    print(f"\n📧 Sending Email:")
    print(f"   To: {to}")
    print(f"   Subject: {subject}")
    print(f"   Body: {body[:100]}...")

    success = send_via_mcp(
        to=to,
        subject=subject,
        body=body,
        attachments=attachments,
        html=frontmatter.get('format', 'text') == 'html'
    )

    if success:
        # Move to Done
        done_file = VAULT_PATH / "Done" / approved_file.name
        approved_file.rename(done_file)
        print(f"✅ Moved to: {done_file}")

        # Log action
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "email_sent",
            "to": to,
            "subject": subject,
            "method": "gmail_mcp",
            "file": approved_file.name
        }

        log_file = LOGS_PATH / f'emails_{datetime.now().strftime("%Y-%m-%d")}.json'
        logs = []
        if log_file.exists():
            logs = json.loads(log_file.read_text())
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

        return True
    else:
        print(f"❌ Failed to send email")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Send emails via Gmail MCP server')
    parser.add_argument('--execute-approved', help='Execute an approved email file')
    parser.add_argument('--to', help='Recipient email')
    parser.add_argument('--subject', help='Email subject')
    parser.add_argument('--body', help='Email body')
    parser.add_argument('--html', action='store_true', help='HTML format')

    args = parser.parse_args()

    if args.execute_approved:
        execute_approved_email(Path(args.execute_approved))
    elif args.to and args.subject and args.body:
        send_via_mcp(args.to, args.subject, args.body, html=args.html)
    else:
        print("Usage:")
        print("  python send_email.py --execute-approved <file>")
        print("  python send_email.py --to <email> --subject <subject> --body <body>")
