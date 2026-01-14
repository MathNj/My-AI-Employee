# Expense Categorization Rules

AI-powered expense categorization rules for automatic transaction classification.

## How Categorization Works

1. **Pattern Matching:** Match vendor name against known patterns
2. **Keyword Analysis:** Analyze transaction description for category keywords
3. **Learning:** Learn from human corrections and update rules
4. **Confidence Scoring:** Calculate confidence (0-100%) for each match

## Confidence Thresholds

- **90-100%:** Auto-apply (High confidence)
- **70-89%:** Suggest, require review (Medium confidence)
- **0-69%:** Mark as uncategorized (Low confidence)

## Category Rules

### Office Supplies

```yaml
category: Office Supplies
patterns:
  - staples
  - office depot
  - officemax
  - amazon.com
keywords:
  - paper
  - pens
  - supplies
  - folders
  - desk
confidence_boost: 10 # if keyword matches
```

**Common Vendors:**
- Staples → 95% confidence
- Office Depot → 95% confidence
- Amazon (with "office" in description) → 85% confidence

---

### Software & Subscriptions

```yaml
category: Software & Subscriptions
patterns:
  - adobe.com
  - microsoft.com
  - slack.com
  - notion.so
  - github.com
  - dropbox.com
  - atlassian.net
keywords:
  - subscription
  - software
  - saas
  - license
confidence_boost: 15
```

**Common Vendors:**
- Adobe → 98% confidence
- Microsoft 365 → 98% confidence
- Slack → 95% confidence
- Notion → 95% confidence
- GitHub → 90% confidence

**Subscription Patterns (from Requirements.md):**
```python
SUBSCRIPTION_PATTERNS = {
    'netflix.com': 'Entertainment',
    'spotify.com': 'Entertainment',
    'adobe.com': 'Software & Subscriptions',
    'notion.so': 'Software & Subscriptions',
    'slack.com': 'Software & Subscriptions',
}
```

---

### Marketing & Advertising

```yaml
category: Marketing & Advertising
patterns:
  - google.com/ads
  - facebook.com
  - linkedin.com
  - twitter.com
  - mailchimp.com
keywords:
  - advertising
  - marketing
  - campaign
  - promotion
  - ad spend
confidence_boost: 20
```

**Common Vendors:**
- Google Ads → 99% confidence
- Facebook Ads → 99% confidence
- LinkedIn Ads → 99% confidence

---

### Travel & Entertainment

```yaml
category: Travel & Entertainment
patterns:
  - delta.com
  - united.com
  - marriott.com
  - hilton.com
  - uber.com
  - lyft.com
  - airbnb.com
keywords:
  - flight
  - hotel
  - travel
  - conference
  - uber
  - taxi
confidence_boost: 12
```

**Subcategories:**
- **Flights:** Airlines (Delta, United, Southwest)
- **Hotels:** Marriott, Hilton, Hyatt
- **Ground Transport:** Uber, Lyft, rental cars
- **Meals:** Restaurant charges during travel

---

### Utilities & Internet

```yaml
category: Utilities
patterns:
  - comcast.com
  - verizon.com
  - att.com
  - spectrum.com
keywords:
  - internet
  - phone
  - electricity
  - water
  - gas
  - utility
confidence_boost: 18
```

**Common Vendors:**
- Comcast/Xfinity → 95% confidence
- Verizon → 95% confidence
- AT&T → 95% confidence

---

### Professional Services

```yaml
category: Professional Services
patterns:
  - lawyer
  - accountant
  - cpa
  - consulting
keywords:
  - legal
  - accounting
  - consulting
  - advisory
  - professional fees
confidence_boost: 8
```

**Subcategories:**
- **Legal:** Law firms, legal fees
- **Accounting:** CPA, bookkeeping
- **Consulting:** Business advisors

---

### Bank Fees & Interest

```yaml
category: Bank Fees
patterns:
  - monthly fee
  - service charge
  - overdraft
  - wire transfer
keywords:
  - fee
  - charge
  - interest
  - maintenance
confidence_boost: 25
```

---

### Revenue Categories

### Product Sales

```yaml
category: Product Sales
keywords:
  - sale
  - product
  - item sold
  - merchandise
amount_direction: positive # Income
confidence_boost: 15
```

### Service Revenue

```yaml
category: Service Revenue
keywords:
  - consulting
  - service
  - project
  - hourly
  - retainer
amount_direction: positive
confidence_boost: 15
```

### Client Payments

```yaml
category: Client Payment
patterns:
  - payment received
  - invoice payment
keywords:
  - payment
  - invoice
  - client
amount_direction: positive
confidence_boost: 20
```

---

## Custom Rules

Add your specific vendors here:

```yaml
# Example: Your common vendors
- pattern: "your_vendor_name"
  category: "Your Category"
  confidence: 90

# Example: Specific client
- pattern: "Client A LLC"
  category: "Client Payment"
  keywords: ["payment", "invoice"]
  confidence: 95
```

## Learning from Corrections

When you correct a categorization:

**Original:**
```
Transaction: Amazon.com - $150.00
AI Suggested: Office Supplies (75% confidence)
Human Corrected: Books & Education
```

**System learns:**
```yaml
- pattern: "amazon.com"
  keywords: ["book", "education", "course"]
  category: "Books & Education"
  confidence: 80
  learned_from: human_correction
  date_learned: 2026-01-12
```

## Special Cases

### Split Transactions

Some transactions need splitting:

```
Amazon.com - $500
  → $300 Office Supplies (Paper, pens)
  → $200 Books & Education (Technical books)
```

**Rule:**
```yaml
split_if:
  - amount > 200
  - vendor: "amazon.com"
  - description_contains: ["multiple items"]
action: create_approval_request
```

### Recurring Transactions

Auto-categorize if seen before:

```yaml
recurring_detection:
  - same_vendor: true
  - same_amount: true (±5%)
  - monthly_pattern: true
action: auto_apply_last_category
confidence_boost: 25
```

## Error Handling

### Uncertain Categorization

If confidence < 70%:

1. Mark as "Needs Review"
2. Create approval file in `/Pending_Approval`
3. Include AI suggestion + reasoning
4. Wait for human decision
5. Learn from decision

### Conflicting Rules

If multiple rules match:

1. Calculate confidence for each
2. Select highest confidence
3. If difference < 10%, mark for review
4. Log conflict for rule refinement

## Tax Categories

Map expense categories to tax classifications:

```yaml
tax_deductible:
  - Office Supplies: 100%
  - Software & Subscriptions: 100%
  - Professional Services: 100%
  - Travel (Business): 100%
  - Meals (Business): 50%
  - Entertainment: 0%

tax_category_mapping:
  Office Supplies: "Business Supplies"
  Software & Subscriptions: "Computer & Internet"
  Marketing & Advertising: "Advertising"
  Professional Services: "Legal & Professional"
```

## Performance Metrics

Track categorization accuracy:

```yaml
metrics:
  total_transactions: 1000
  auto_categorized: 850
  requires_review: 100
  uncategorized: 50
  accuracy_rate: 95% # (correct auto-cat / total auto-cat)
  review_rate: 10% # (requires review / total)
```

## Updating Rules

### Manual Update

Edit this file and add new rules.

### Automatic Learning

System automatically adds rules when:
- Human corrects 3+ transactions with same pattern
- Confidence threshold met (80%+)
- No conflicting existing rule

### Rule Validation

Before applying new rules:
1. Test against last 30 days transactions
2. Calculate accuracy impact
3. Ensure no conflicts with existing rules
4. Log validation results

---

**Last Updated:** 2026-01-12
**Rules Version:** 1.0
**Auto-Learning:** Enabled
