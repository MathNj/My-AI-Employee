# Xero API Reference

Quick reference for Xero API endpoints used by xero-integrator skill.

## Authentication

**OAuth 2.0 Flow:**
1. Authorization URL: `https://login.xero.com/identity/connect/authorize`
2. Token URL: `https://identity.xero.com/connect/token`
3. Scopes: `accounting.transactions accounting.reports.read accounting.contacts`

## MCP Server Tools

The Xero MCP server exposes these tools:

### xero_get_transactions

Fetch transactions for date range.

**Parameters:**
```json
{
  "start_date": "2026-01-01",
  "end_date": "2026-01-31",
  "type": "all",  // or "income", "expense"
  "status": "all"  // or "paid", "pending"
}
```

**Returns:**
```json
[
  {
    "id": "TX001",
    "date": "2026-01-12",
    "contact": "Vendor Name",
    "description": "Transaction description",
    "amount": -45.00,
    "category": null,
    "account": "Business Checking"
  }
]
```

### xero_get_invoices

Retrieve invoices.

**Parameters:**
```json
{
  "status": "all",  // "paid", "unpaid", "overdue"
  "start_date": "2026-01-01",
  "end_date": "2026-01-31"
}
```

### xero_create_invoice

Create new invoice.

**Parameters:**
```json
{
  "contact": "Client Name",
  "line_items": [
    {
      "description": "Consulting Services",
      "quantity": 10,
      "unit_amount": 150.00,
      "account_code": "200"
    }
  ],
  "due_date": "2026-02-12"
}
```

### xero_update_transaction

Update transaction category.

**Parameters:**
```json
{
  "transaction_id": "TX001",
  "category": "Office Supplies"
}
```

## Rate Limits

- **API Calls:** 60 per minute
- **Daily Limit:** 5,000 calls per day
- **Burst:** 10 concurrent connections

**Handling Rate Limits:**
```python
if response.status_code == 429:
    retry_after = response.headers.get('Retry-After', 60)
    time.sleep(retry_after)
    retry_request()
```

## Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| 401 | Unauthorized | Refresh OAuth token |
| 403 | Forbidden | Check scopes/permissions |
| 404 | Not Found | Verify resource ID |
| 429 | Rate Limit | Wait and retry |
| 500 | Server Error | Retry with backoff |

## Full API Documentation

https://developer.xero.com/documentation/api/accounting/overview
