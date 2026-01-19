#!/usr/bin/env python3
"""
Simple email sender - workaround for encoding issues
"""
import sys
import os
from pathlib import Path
import subprocess

# Fix encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def send_email_simple(to, subject, body):
    """Send email using Gmail MCP or provide instructions"""

    print(f"\n📧 Email Details:")
    print(f"   To: {to}")
    print(f"   Subject: {subject}")
    print(f"   Body: {body[:100]}...")
    print(f"\n⚠️  Email sending requires Gmail MCP server configuration.")
    print(f"   Please configure the Gmail MCP server to send this email.")
    print(f"   Or send manually using the content above.\n")

    # Try to use Gmail MCP if available
    try:
        # Check if MCP Gmail server is available
        result = subprocess.run(
            ["npx", "@modelcontextprotocol/server-gmail", "--help"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✅ Gmail MCP detected - but needs proper configuration")
            return False
    except:
        pass

    print("❌ Gmail MCP not configured. Please:")
    print("   1. Install: npm install -g @modelcontextprotocol/server-gmail")
    print("   2. Configure in ~/.config/claude-code/mcp.json")
    print("   3. Or send manually using Gmail web interface\n")

    return False

if __name__ == "__main__":
    # Read approved email
    approved_file = Path("Approved/EMAIL_20260119_ai_employee_announcement.md")

    if not approved_file.exists():
        print(f"❌ File not found: {approved_file}")
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
        success = send_email_simple(to_email, subject, body)

        if success:
            # Move to Done
            done_file = Path("Done/EMAIL_20260119_ai_employee_announcement.md")
            approved_file.rename(done_file)
            print("✅ Moved to Done")
        else:
            print("⚠️  Email not sent - approval file remains in Approved")
            print("   You can send manually using Gmail web interface")
    else:
        print("❌ Could not parse email details")
