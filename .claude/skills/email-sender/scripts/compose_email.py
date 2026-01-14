#!/usr/bin/env python3
"""
Email Composer - Create emails from templates

Usage:
    python compose_email.py --list-templates
    python compose_email.py --template invoice --to "client@example.com" --invoice-number "INV-001"
    python compose_email.py --interactive
"""

import argparse
import sys
from pathlib import Path
import send_email

# Email templates
TEMPLATES = {
    'invoice': {
        'subject': 'Invoice {invoice_number} - {amount}',
        'body': '''Dear {recipient_name},

Please find attached invoice {invoice_number} for {amount}.

Payment is due by {due_date}.

If you have any questions, please don't hesitate to contact us.

Best regards,
{sender_name}''',
        'variables': ['recipient_name', 'invoice_number', 'amount', 'due_date', 'sender_name']
    },

    'inquiry-response': {
        'subject': 'Re: {inquiry_subject}',
        'body': '''Hello {recipient_name},

Thank you for your inquiry about {inquiry_topic}.

{response}

Please let me know if you need any additional information.

Best regards,
{sender_name}''',
        'variables': ['recipient_name', 'inquiry_topic', 'inquiry_subject', 'response', 'sender_name']
    },

    'report': {
        'subject': '{report_type} - {date}',
        'body': '''Team,

Here's the {report_type} for {date}.

Summary:
{summary}

{details}

Best regards,
{sender_name}''',
        'variables': ['report_type', 'date', 'summary', 'details', 'sender_name']
    },

    'meeting-followup': {
        'subject': 'Meeting Follow-up - {meeting_topic}',
        'body': '''Hi {recipient_name},

Thank you for meeting with me today to discuss {meeting_topic}.

Key takeaways:
{takeaways}

Action items:
{action_items}

Next steps:
{next_steps}

Best regards,
{sender_name}''',
        'variables': ['recipient_name', 'meeting_topic', 'takeaways', 'action_items', 'next_steps', 'sender_name']
    }
}


def list_templates():
    """Display all available templates."""
    print("📋 Available Email Templates:\n")
    for template_id, template in TEMPLATES.items():
        print(f"  {template_id}")
        print(f"    Subject: {template['subject']}")
        print(f"    Variables: {', '.join(template['variables'])}")
        print()


def generate_from_template(template_id, variables):
    """Generate email from template."""
    if template_id not in TEMPLATES:
        print(f"❌ Template '{template_id}' not found")
        return None, None

    template = TEMPLATES[template_id]

    try:
        subject = template['subject'].format(**variables)
        body = template['body'].format(**variables)
        return subject, body
    except KeyError as e:
        print(f"❌ Missing variable: {e}")
        print(f"   Required: {', '.join(template['variables'])}")
        return None, None


def main():
    parser = argparse.ArgumentParser(description='Email Composer')

    parser.add_argument('--list-templates', action='store_true',
                        help='List all available templates')
    parser.add_argument('--template', type=str,
                        help='Template ID to use')
    parser.add_argument('--to', type=str,
                        help='Recipient email address')

    # Common variables
    parser.add_argument('--recipient-name', type=str, default='Customer')
    parser.add_argument('--sender-name', type=str, default='Your Name')
    parser.add_argument('--invoice-number', type=str)
    parser.add_argument('--amount', type=str)
    parser.add_argument('--due-date', type=str)
    parser.add_argument('--inquiry-topic', type=str)
    parser.add_argument('--inquiry-subject', type=str)
    parser.add_argument('--response', type=str)
    parser.add_argument('--report-type', type=str)
    parser.add_argument('--date', type=str)
    parser.add_argument('--summary', type=str)
    parser.add_argument('--details', type=str, default='')

    parser.add_argument('--attach', action='append',
                        help='Attachment file path')
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without creating approval')

    args = parser.parse_args()

    if args.list_templates:
        list_templates()
        return

    if args.template and args.to:
        # Build variables dict
        variables = {
            'recipient_name': args.recipient_name,
            'sender_name': args.sender_name,
            'invoice_number': args.invoice_number or 'INV-XXX',
            'amount': args.amount or '$0.00',
            'due_date': args.due_date or 'TBD',
            'inquiry_topic': args.inquiry_topic or 'your inquiry',
            'inquiry_subject': args.inquiry_subject or 'Your Inquiry',
            'response': args.response or 'Thank you for reaching out.',
            'report_type': args.report_type or 'Report',
            'date': args.date or 'today',
            'summary': args.summary or 'No summary provided.',
            'details': args.details,
            'meeting_topic': getattr(args, 'meeting_topic', 'our meeting'),
            'takeaways': getattr(args, 'takeaways', '- Key point 1'),
            'action_items': getattr(args, 'action_items', '- Action 1'),
            'next_steps': getattr(args, 'next_steps', '- Follow up next week')
        }

        subject, body = generate_from_template(args.template, variables)

        if subject and body:
            print("📝 Generated Email:")
            print("─" * 60)
            print(f"To: {args.to}")
            print(f"Subject: {subject}")
            print()
            print(body)
            print("─" * 60)

            if not args.dry_run:
                send_email.create_approval_request(
                    args.to, subject, body, args.attach
                )
        return

    parser.print_help()


if __name__ == '__main__':
    main()
