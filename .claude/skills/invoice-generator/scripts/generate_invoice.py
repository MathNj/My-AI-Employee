#!/usr/bin/env python3
"""
Invoice Generator - Automatically generates professional PDF invoices

Triggers:
- Email requests for invoices (detected by Gmail watcher)
- Calendar events for recurring billing
- Manual requests via task files

Integration:
- Cross-domain bridge for business context
- Company handbook for company info
- Business goals for revenue tracking
"""

import sys
import os
import re
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# UTF-8 support for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - InvoiceGenerator - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class InvoiceLineItem:
    """Line item in an invoice"""
    description: str
    quantity: int = 1
    unit_price: float = 0.0
    total: float = 0.0

    def __post_init__(self):
        if self.total == 0.0 and self.unit_price > 0:
            self.total = self.quantity * self.unit_price


@dataclass
class InvoiceData:
    """Complete invoice data"""
    invoice_number: str
    date: str
    due_date: str

    # Client info
    client_name: str
    client_email: str = ""
    client_address: str = ""
    client_company: str = ""

    # Invoice details
    po_number: str = ""
    currency: str = "USD"
    payment_terms: str = "Net 30"
    tax_rate: float = 0.0
    tax_amount: float = 0.0
    subtotal: float = 0.0
    total: float = 0.0

    # Line items
    line_items: List[InvoiceLineItem] = field(default_factory=list)

    # Notes
    notes: str = ""
    payment_instructions: str = ""

    # Metadata
    source_email_message_id: str = ""
    source_email_date: str = ""


class InvoiceGenerator:
    """Generate professional PDF invoices"""

    def __init__(self, vault_path: Optional[Path] = None):
        """Initialize invoice generator"""
        if vault_path is None:
            # Get vault path - script is in .claude/skills/invoice-generator/scripts/
            # Go up 4 levels: scripts/ -> invoice-generator/ -> skills/ -> .claude/ -> vault_root
            self.vault_path = Path(__file__).resolve().parent.parent.parent.parent.parent
        else:
            self.vault_path = Path(vault_path)

        self.skills_path = self.vault_path / '.claude' / 'skills' / 'invoice-generator'
        self.invoices_path = self.vault_path / 'Invoices'
        self.company_handbook = self.vault_path / 'Company_Handbook.md'
        self.business_goals = self.vault_path / 'Business_Goals.md'

        # Ensure directories exist
        self.invoices_path.mkdir(exist_ok=True)
        (self.skills_path / 'templates').mkdir(parents=True, exist_ok=True)

        # Load company info
        self.company_info = self._load_company_info()

        # Load last invoice number
        self.last_invoice_number = self._load_last_invoice_number()

        logger.info("InvoiceGenerator initialized")
        logger.info(f"  Vault: {self.vault_path}")
        logger.info(f"  Invoices: {self.invoices_path}")

    def _load_company_info(self) -> Dict[str, Any]:
        """Load company information from Company_Handbook.md"""
        info = {
            'name': 'Your Company Name',
            'address': '',
            'email': '',
            'phone': '',
            'tax_id': '',
            'bank_name': '',
            'bank_account': '',
            'bank_routing': '',
            'payment_terms': 'Net 30',
            'currency': 'USD',
            'tax_rate': 0.0
        }

        if not self.company_handbook.exists():
            logger.warning("Company_Handbook.md not found - using defaults")
            return info

        try:
            content = self.company_handbook.read_text(encoding='utf-8')

            # Extract company information using regex
            patterns = {
                'name': r'Company Name[:\s]+([^\n]+)',
                'address': r'Address[:\s]+([^\n]+(?:\n[^\n]+){0,2})',
                'email': r'Email[:\s]+([^\n]+)',
                'phone': r'Phone[:\s]+([^\n]+)',
                'tax_id': r'Tax ID|VAT[:\s]+([^\n]+)',
                'bank_name': r'Bank Name[:\s]+([^\n]+)',
                'bank_account': r'Account Number[:\s]+([^\n]+)',
                'bank_routing': r'Routing Number[:\s]+([^\n]+)',
            }

            for key, pattern in patterns.items():
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    info[key] = match.group(1).strip()

            logger.info(f"Loaded company info for: {info['name']}")

        except Exception as e:
            logger.error(f"Error loading company info: {e}")

        return info

    def _load_last_invoice_number(self) -> str:
        """Load last invoice number to auto-increment"""
        number_file = self.invoices_path / 'last_invoice_number.txt'

        if number_file.exists():
            try:
                return number_file.read_text(encoding='utf-8').strip()
            except:
                pass

        # Default to start of year
        return f"INV-{datetime.now().year}-000"

    def _get_next_invoice_number(self) -> str:
        """Generate next sequential invoice number"""
        # Parse current number
        match = re.match(r'INV-(\d{4})-(\d+)', self.last_invoice_number)
        if match:
            year = int(match.group(1))
            num = int(match.group(2))

            # Check if year changed
            current_year = datetime.now().year
            if year != current_year:
                num = 0
                year = current_year

            # Increment
            num += 1
            new_number = f"INV-{year}-{num:03d}"

            # Save
            number_file = self.invoices_path / 'last_invoice_number.txt'
            number_file.write_text(new_number, encoding='utf-8')

            self.last_invoice_number = new_number
            return new_number

        # Fallback
        return f"INV-{datetime.now().year}-001"

    def parse_email_for_invoice_request(
        self,
        email_content: str,
        metadata: Dict[str, str]
    ) -> Optional[InvoiceData]:
        """
        Parse email to extract invoice request details

        Args:
            email_content: Email body text
            metadata: Email metadata (from, subject, date, message_id)

        Returns:
            InvoiceData if invoice request detected, None otherwise
        """
        # Check for invoice keywords
        invoice_keywords = [
            'invoice', 'bill', 'payment', 'receipt', 'statement',
            'purchase order', 'send invoice', 'please bill', 'charge for'
        ]

        content_lower = email_content.lower()
        subject_lower = metadata.get('subject', '').lower()

        has_keyword = any(kw in content_lower or kw in subject_lower for kw in invoice_keywords)

        if not has_keyword:
            return None

        logger.info("Invoice request detected in email")

        # Extract client information
        client_email = metadata.get('from', '')
        client_name = self._extract_client_name(email_content, client_email)
        client_company = self._extract_company_name(email_content)

        # Extract amount
        amount = self._extract_amount(email_content)
        if not amount:
            logger.warning("No amount found - flagging for manual review")

        # Extract PO number
        po_number = self._extract_po_number(email_content)

        # Extract due date
        due_date = self._extract_due_date(email_content)

        # Generate invoice number
        invoice_number = self._get_next_invoice_number()

        # Create line item
        service_description = self._extract_service_description(email_content)
        line_items = [
            InvoiceLineItem(
                description=service_description,
                quantity=1,
                unit_price=amount or 0.0,
                total=amount or 0.0
            )
        ]

        # Create invoice data
        invoice = InvoiceData(
            invoice_number=invoice_number,
            date=datetime.now().strftime('%Y-%m-%d'),
            due_date=due_date,
            client_name=client_name,
            client_email=client_email,
            client_company=client_company,
            po_number=po_number,
            currency=self.company_info['currency'],
            payment_terms=self.company_info['payment_terms'],
            tax_rate=self.company_info['tax_rate'],
            line_items=line_items,
            source_email_message_id=metadata.get('message_id', ''),
            source_email_date=metadata.get('date', '')
        )

        # Calculate totals
        invoice.subtotal = sum(item.total for item in invoice.line_items)
        invoice.tax_amount = invoice.subtotal * (invoice.tax_rate / 100)
        invoice.total = invoice.subtotal + invoice.tax_amount

        # Add payment instructions
        invoice.payment_instructions = self._generate_payment_instructions()

        logger.info(f"Created invoice {invoice_number} for {client_name}: ${invoice.total:.2f}")

        return invoice

    def _extract_client_name(self, email_content: str, email_address: str) -> str:
        """Extract client name from email"""
        # Try email signature first
        signature_patterns = [
            r'(?:Best|Regards|Sincerely|Thanks)[,\s]*\n(.+?)(?:\n|$)',
            r'(.+?)(?:\n.*?){0,2}\n(?:Thank|Best|Regards)',
        ]

        for pattern in signature_patterns:
            match = re.search(pattern, email_content, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and len(name) < 50:
                    return name

        # Fallback to email address
        if email_address:
            name_part = email_address.split('@')[0]
            return name_part.replace('.', ' ').title()

        return "Client"

    def _extract_company_name(self, email_content: str) -> str:
        """Extract company name from email"""
        patterns = [
            r'(?:from|at)\s+([A-Z][A-Za-z\s]+?(?:Inc|LLC|Ltd|Corp|Company))',
            r'([A-Z][A-Za-z\s]+?(?:Inc|LLC|Ltd|Corp|Company))',
        ]

        for pattern in patterns:
            match = re.search(pattern, email_content)
            if match:
                return match.group(1).strip()

        return ""

    def _extract_amount(self, email_content: str) -> Optional[float]:
        """Extract invoice amount from email"""
        # Try currency patterns: $1,000.00, 1000.00, etc.
        patterns = [
            r'\$\s*([\d,]+\.?\d*)',  # $1,000.00
            r'(?:amount|total|price|cost|invoice|bill)\s*[:\(]?\s*\$?\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*(?:USD|dollars?)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, email_content, re.IGNORECASE)
            if matches:
                # Use the first (or largest) amount found
                amounts = [float(m.replace(',', '')) for m in matches]
                return max(amounts) if amounts else None

        return None

    def _extract_po_number(self, email_content: str) -> str:
        """Extract purchase order number"""
        patterns = [
            r'(?:PO|P\.O\.|Purchase Order)\s*[:#]?\s*([A-Z0-9-]+)',
            r'(?:PO|P\.O\.|Purchase Order)[\s:]*([A-Z0-9-]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, email_content, re.IGNORECASE)
            if match:
                return match.group(1).upper()

        return ""

    def _extract_due_date(self, email_content: str) -> str:
        """Extract or calculate due date"""
        # Check for explicit due date
        patterns = [
            r'(?:due|pay by|payment due)\s*:?\s*(\d{4}-\d{2}-\d{2})',
            r'(?:due|pay by)\s*:?\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}',
        ]

        for pattern in patterns:
            match = re.search(pattern, email_content, re.IGNORECASE)
            if match:
                # Would need more sophisticated date parsing
                pass

        # Check for payment terms
        if 'net 15' in email_content.lower():
            days = 15
        elif 'net 30' in email_content.lower():
            days = 30
        elif 'net 60' in email_content.lower():
            days = 60
        elif 'immediate' in email_content.lower() or 'asap' in email_content.lower():
            days = 7
        else:
            days = 30  # Default

        due_date = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        return due_date

    def _extract_service_description(self, email_content: str) -> str:
        """Extract service description from email"""
        # Look for project context
        patterns = [
            r'(?:project|service|work|deliverables?)\s*:?\s*([^\n]+)',
            r'(?:for|regarding|concerning)\s+([^\n]+?)(?:\n|$)',
        ]

        for pattern in patterns:
            match = re.search(pattern, email_content, re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 10 and len(desc) < 200:
                    return desc

        # Fallback
        return "Professional Services"

    def _generate_payment_instructions(self) -> str:
        """Generate payment instructions from company info"""
        instructions = []

        if self.company_info['bank_name']:
            instructions.append(f"Bank: {self.company_info['bank_name']}")

        if self.company_info['bank_account']:
            instructions.append(f"Account Number: {self.company_info['bank_account']}")

        if self.company_info['bank_routing']:
            instructions.append(f"Routing Number: {self.company_info['bank_routing']}")

        if self.company_info['email']:
            instructions.append(f"Or send payment to: {self.company_info['email']}")

        return "\n".join(instructions) if instructions else "Contact us for payment details"

    def generate_html_invoice(self, invoice: InvoiceData) -> str:
        """
        Generate HTML invoice (can be converted to PDF)

        Args:
            invoice: InvoiceData object

        Returns:
            HTML string
        """
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Invoice {invoice.invoice_number}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 40px;
        }}
        .company-info h1 {{
            color: #2c3e50;
            margin: 0;
        }}
        .invoice-details {{
            text-align: right;
        }}
        .invoice-details h2 {{
            color: #e74c3c;
            margin: 0;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h3 {{
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            color: #2c3e50;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #3498db;
            color: white;
        }}
        .totals {{
            text-align: right;
        }}
        .total-row {{
            font-size: 1.2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="company-info">
            <h1>{self.company_info['name']}</h1>
            <p>{self.company_info['address'].replace(chr(10), '<br>')}</p>
            <p>Email: {self.company_info['email']}</p>
            <p>Phone: {self.company_info['phone']}</p>
        </div>
        <div class="invoice-details">
            <h2>INVOICE</h2>
            <p><strong>Invoice Number:</strong> {invoice.invoice_number}</p>
            <p><strong>Date:</strong> {invoice.date}</p>
            <p><strong>Due Date:</strong> {invoice.due_date}</p>
        </div>
    </div>

    <div class="section">
        <h3>Bill To:</h3>
        <p><strong>{invoice.client_name}</strong></p>
        {f'<p>{invoice.client_company}</p>' if invoice.client_company else ''}
        <p>{invoice.client_email}</p>
        {f'<p>{invoice.client_address}</p>' if invoice.client_address else ''}
        {f'<p><strong>PO Number:</strong> {invoice.po_number}</p>' if invoice.po_number else ''}
    </div>

    <div class="section">
        <h3>Line Items</h3>
        <table>
            <thead>
                <tr>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Unit Price</th>
                    <th>Total</th>
                </tr>
            </thead>
            <tbody>
"""

        for item in invoice.line_items:
            html += f"""
                <tr>
                    <td>{item.description}</td>
                    <td>{item.quantity}</td>
                    <td>{invoice.currency} {item.unit_price:,.2f}</td>
                    <td>{invoice.currency} {item.total:,.2f}</td>
                </tr>
"""

        html += f"""
            </tbody>
        </table>

        <div class="totals">
            <p><strong>Subtotal:</strong> {invoice.currency} {invoice.subtotal:,.2f}</p>
            {f'<p><strong>Tax ({invoice.tax_rate}%):</strong> {invoice.currency} {invoice.tax_amount:,.2f}</p>' if invoice.tax_rate > 0 else ''}
            <p class="total-row"><strong>Total:</strong> {invoice.currency} {invoice.total:,.2f}</p>
        </div>
    </div>

    <div class="section">
        <h3>Payment Terms</h3>
        <p>{invoice.payment_terms}</p>
    </div>

    {f'<div class="section"><h3>Payment Instructions</h3><p>{invoice.payment_instructions.replace(chr(10), "<br>")}</p></div>' if invoice.payment_instructions else ''}

    {f'<div class="section"><h3>Notes</h3><p>{invoice.notes}</p></div>' if invoice.notes else ''}

    <div class="footer">
        <p>Thank you for your business!</p>
        <p>If you have any questions, please contact us at {self.company_info['email']}</p>
    </div>
</body>
</html>
"""
        return html

    def create_approval_task(self, invoice: InvoiceData) -> Path:
        """
        Create approval task file in Pending_Approval/

        Args:
            invoice: InvoiceData object

        Returns:
            Path to created task file
        """
        pending_path = self.vault_path / 'Pending_Approval'
        pending_path.mkdir(exist_ok=True)

        filename = f"INVOICE_{invoice.invoice_number.replace('-', '_')}.md"
        task_file = pending_path / filename

        # Generate markdown content
        content = f"""---
type: invoice
action: generate_pdf
client: "{invoice.client_name}"
client_email: "{invoice.client_email}"
amount: {invoice.total:.2f}
currency: {invoice.currency}
invoice_number: {invoice.invoice_number}
po_number: {invoice.po_number}
due_date: {invoice.due_date}
status: pending_approval
---

# Invoice Request: {invoice.invoice_number}

## Client Information
- **Name:** {invoice.client_name}
{f'- **Company:** {invoice.client_company}' if invoice.client_company else ''}
- **Email:** {invoice.client_email}
{f'- **Address:** {invoice.client_address}' if invoice.client_address else ''}
{f'- **PO Number:** {invoice.po_number}' if invoice.po_number else ''}

## Invoice Details
- **Invoice Number:** {invoice.invoice_number}
- **Date:** {invoice.date}
- **Due Date:** {invoice.due_date} ({invoice.payment_terms})
- **Amount:** {invoice.currency} {invoice.total:,.2f}
{f'- **Tax ({invoice.tax_rate}%):** {invoice.currency} {invoice.tax_amount:,.2f}' if invoice.tax_rate > 0 else ''}
- **Subtotal:** {invoice.currency} {invoice.subtotal:,.2f}

## Line Items
"""

        for i, item in enumerate(invoice.line_items, 1):
            content += f"{i}. **{item.description}**\n"
            content += f"   - Quantity: {item.quantity}\n"
            content += f"   - Unit Price: {invoice.currency} {item.unit_price:,.2f}\n"
            content += f"   - Total: {invoice.currency} {item.total:,.2f}\n\n"

        if invoice.source_email_message_id:
            content += f"\n## Source Email\n"
            content += f"- **From:** {invoice.client_email}\n"
            content += f"- **Date:** {invoice.source_email_date}\n"
            content += f"- **Message ID:** {invoice.source_email_message_id}\n"

        if invoice.notes:
            content += f"\n## Notes\n{invoice.notes}\n"

        content += f"\n## Generated Invoice\n"
        content += f"[PDF will be attached after approval]\n\n"
        content += f"**Preview:** See HTML version in `Invoices/{invoice.invoice_number}.html`\n"

        task_file.write_text(content, encoding='utf-8')

        logger.info(f"Created approval task: {task_file}")

        return task_file

    def process_email(
        self,
        email_content: str,
        metadata: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Process email and generate invoice if request detected

        Args:
            email_content: Email body
            metadata: Email metadata

        Returns:
            Result dict with status and details
        """
        try:
            # Parse email for invoice request
            invoice = self.parse_email_for_invoice_request(email_content, metadata)

            if not invoice:
                return {
                    'success': False,
                    'reason': 'No invoice request detected'
                }

            # Generate HTML invoice
            html_invoice = self.generate_html_invoice(invoice)

            # Save HTML invoice
            html_file = self.invoices_path / f"{invoice.invoice_number}.html"
            html_file.write_text(html_invoice, encoding='utf-8')
            logger.info(f"Saved HTML invoice: {html_file}")

            # Create approval task
            task_file = self.create_approval_task(invoice)

            return {
                'success': True,
                'invoice_number': invoice.invoice_number,
                'amount': invoice.total,
                'client': invoice.client_name,
                'html_file': str(html_file),
                'task_file': str(task_file),
                'needs_approval': invoice.total > 5000  # Configurable threshold
            }

        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def test_invoice_generation(self) -> Dict[str, Any]:
        """Test invoice generation with sample data"""
        test_email = """
Hi John,

The website development project has been completed. Please send us an invoice for $5,000 as per our agreement.

Purchase Order: PO-2026-001
Payment Terms: Net 30

Best regards,
Jane Smith
Acme Corporation
"""

        test_metadata = {
            'from': 'jane.smith@acmecorp.com',
            'subject': 'Project Completion - Please Send Invoice',
            'date': '2026-01-21T12:00:00',
            'message_id': 'test123'
        }

        logger.info("Testing invoice generation...")
        result = self.process_email(test_email, test_metadata)

        if result['success']:
            logger.info(f"[OK] Test invoice generated: {result['invoice_number']}")
            logger.info(f"  Amount: ${result['amount']:.2f}")
            logger.info(f"  Client: {result['client']}")
        else:
            logger.error(f"[FAIL] Test failed: {result.get('error', result.get('reason'))}")

        return result


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description='Invoice Generator')
    parser.add_argument('--test', action='store_true', help='Run test')
    parser.add_argument('--client', help='Client name')
    parser.add_argument('--amount', type=float, help='Invoice amount')
    parser.add_argument('--service', help='Service description')

    args = parser.parse_args()

    generator = InvoiceGenerator()

    if args.test:
        generator.test_invoice_generation()
    elif args.client and args.amount:
        # Manual invoice creation
        from dataclasses import dataclass

        invoice = InvoiceData(
            invoice_number=generator._get_next_invoice_number(),
            date=datetime.now().strftime('%Y-%m-%d'),
            due_date=(datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
            client_name=args.client,
            currency=generator.company_info['currency'],
            payment_terms=generator.company_info['payment_terms'],
            line_items=[
                InvoiceLineItem(
                    description=args.service or "Professional Services",
                    quantity=1,
                    unit_price=args.amount,
                    total=args.amount
                )
            ]
        )
        invoice.subtotal = args.amount
        invoice.total = args.amount

        html = generator.generate_html_invoice(invoice)
        html_file = generator.invoices_path / f"{invoice.invoice_number}.html"
        html_file.write_text(html, encoding='utf-8')

        task_file = generator.create_approval_task(invoice)

        print(f"[OK] Invoice created: {invoice.invoice_number}")
        print(f"  HTML: {html_file}")
        print(f"  Task: {task_file}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
