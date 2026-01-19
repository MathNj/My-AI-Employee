#!/usr/bin/env python3
"""
Send email workaround - bypass encoding issues
"""
import sys
import os
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def send_email_via_gmail_mcp(to, subject, body):
    """Send email using Gmail MCP server"""

    # Import mcp client
    try:
        import subprocess
        import json

        # Prepare email data
        email_data = {
            "to": to,
            "subject": subject,
            "body": body
        }

        print(f"Preparing email to: {to}")

        # Check if Gmail MCP is available
        try:
            result = subprocess.run(
                ["npx", "@modelcontextprotocol/server-gmail", "--help"],
                capture_output=True,
                timeout=5
            )

            # Try to send via MCP
            mcp_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "send_email",
                    "arguments": email_data
                }
            }

            print("Gmail MCP detected - attempting to send...")

            # For now, provide manual instructions
            print("\n" + "="*70)
            print("EMAIL READY TO SEND")
            print("="*70)
            print(f"\nTo: {to}")
            print(f"Subject: {subject}")
            print(f"\nBody:\n{body}\n")
            print("="*70)
            print("\nTo send this email:")
            print("1. Open Gmail web interface")
            print("2. Compose new email")
            print("3. Copy the details above")
            print("4. Send to:", to)
            print("\nNote: Full Gmail MCP integration requires setup in mcp.json")
            print("="*70 + "\n")

            return False

        except Exception as e:
            print(f"Gmail MCP not available: {e}")
            print("\nPlease send manually using Gmail web interface")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    # Read approved email
    vault_path = Path.cwd()
    approved_file = vault_path / "Approved" / "EMAIL_20260119_ai_employee_announcement.md"

    if not approved_file.exists():
        print(f"File not found: {approved_file}")
        sys.exit(1)

    content = approved_file.read_text(encoding='utf-8')

    # Parse details
    lines = content.split('\n')
    to_email = None
    subject = None
    body = None

    for i, line in enumerate(lines):
        if line.startswith('to:'):
            to_email = line.split(':', 1)[1].strip()
        elif line.startswith('subject:'):
            subject = line.split(':', 1)[1].strip().strip('"')
        elif line.startswith('body:'):
            # Multi-line body
            body_lines = []
            for j in range(i+1, len(lines)):
                if lines[j].strip().startswith('created:'):
                    break
                body_lines.append(lines[j])
            body = '\n'.join(body_lines).strip('"').strip()
            break

    if to_email and subject and body:
        print(f"\nEmail details extracted:")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body length: {len(body)} characters\n")

        # Attempt to send
        success = send_email_via_gmail_mcp(to_email, subject, body)

        if success:
            # Move to Done
            done_file = vault_path / "Done" / approved_file.name
            done_file.parent.mkdir(parents=True, exist_ok=True)
            approved_file.rename(done_file)
            print("Email sent and moved to Done")
        else:
            print("\nEmail not sent automatically.")
            print("Please send manually using Gmail web interface.")
            print(f"File remains in: {approved_file}")
    else:
        print("Could not parse email details")
        sys.exit(1)
