# Email Templates Library

Professional email templates for common business scenarios.

## Template Usage

```bash
python compose_email.py --template <template-name> --to "..." --<variables>
```

---

## 1. Invoice Email

**Use for:** Sending invoices to clients

**Template:**
```
Subject: Invoice {invoice_number} - {amount}

Dear {recipient_name},

Please find attached invoice {invoice_number} for {amount}.

Payment is due by {due_date}.

If you have any questions, please don't hesitate to contact us.

Best regards,
{sender_name}
```

**Usage:**
```bash
python compose_email.py --template invoice \
  --to "client@example.com" \
  --recipient-name "John Doe" \
  --invoice-number "INV-001" \
  --amount "$1,500" \
  --due-date "January 31, 2026" \
  --attach "/path/to/invoice.pdf"
```

---

## 2. Inquiry Response

**Use for:** Replying to customer questions

**Template:**
```
Subject: Re: {inquiry_subject}

Hello {recipient_name},

Thank you for your inquiry about {inquiry_topic}.

{response}

Please let me know if you need any additional information.

Best regards,
{sender_name}
```

**Usage:**
```bash
python compose_email.py --template inquiry-response \
  --to "customer@example.com" \
  --recipient-name "Jane Smith" \
  --inquiry-topic "pricing" \
  --inquiry-subject "Pricing Information" \
  --response "Our pricing starts at $500/month..."
```

---

## 3. Business Report

**Use for:** Weekly/monthly status reports

**Template:**
```
Subject: {report_type} - {date}

Team,

Here's the {report_type} for {date}.

Summary:
{summary}

{details}

Best regards,
{sender_name}
```

**Usage:**
```bash
python compose_email.py --template report \
  --to "team@company.com" \
  --report-type "Weekly Status Report" \
  --date "Week of January 6-12" \
  --summary "Completed 10 tasks, 2 in progress" \
  --details "See attached for full details"
```

---

## 4. Meeting Follow-up

**Use for:** Post-meeting summaries

**Template:**
```
Subject: Meeting Follow-up - {meeting_topic}

Hi {recipient_name},

Thank you for meeting with me today to discuss {meeting_topic}.

Key takeaways:
{takeaways}

Action items:
{action_items}

Next steps:
{next_steps}

Best regards,
{sender_name}
```

**Usage:**
```bash
python compose_email.py --template meeting-followup \
  --to "partner@company.com" \
  --recipient-name "Alex" \
  --meeting-topic "Q1 Partnership" \
  --takeaways "- Agreed on timeline\n- Budget approved" \
  --action-items "- Draft contract by Friday\n- Schedule kickoff meeting"
```

---

## Custom Templates

To add your own templates, edit `scripts/compose_email.py` and add to the TEMPLATES dict:

```python
'template-name': {
    'subject': 'Subject with {variable}',
    'body': '''Email body with {variables}''',
    'variables': ['variable1', 'variable2']
}
```

---

## Email Best Practices

### Subject Lines
- Clear and specific
- Include key information (invoice number, date)
- Max 50 characters

### Body Content
- Personalize with recipient name
- Clear purpose in first sentence
- Short paragraphs (2-3 lines)
- Clear call-to-action
- Professional closing

### Attachments
- Mention attachments in body
- Use descriptive filenames
- Keep under 25 MB total

---

**Need more templates?** Create custom templates or ask Claude Code to generate email content.
