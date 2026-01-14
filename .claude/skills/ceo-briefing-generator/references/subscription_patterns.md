# Subscription Pattern Database

Complete database of subscription patterns for automated detection and audit.

## Core Subscription Patterns

These patterns are used to automatically identify subscription charges in transaction data.

### Software & Productivity

```python
SOFTWARE_SUBSCRIPTIONS = {
    # Development Tools
    'github.com': 'GitHub',
    'gitlab.com': 'GitLab',
    'bitbucket.org': 'Bitbucket',
    'jetbrains.com': 'JetBrains',
    'visualstudio.com': 'Visual Studio',

    # Project Management
    'atlassian.com': 'Atlassian (Jira/Confluence)',
    'asana.com': 'Asana',
    'monday.com': 'Monday.com',
    'trello.com': 'Trello',
    'basecamp.com': 'Basecamp',
    'clickup.com': 'ClickUp',

    # Documentation & Knowledge
    'notion.so': 'Notion',
    'confluence.atlassian.com': 'Confluence',
    'coda.io': 'Coda',
    'roamresearch.com': 'Roam Research',
    'obsidian.md': 'Obsidian Sync',

    # Communication
    'slack.com': 'Slack',
    'teams.microsoft.com': 'Microsoft Teams',
    'discord.com': 'Discord Nitro',
    'zoom.us': 'Zoom',
    'gotomeeting.com': 'GoToMeeting',

    # Design & Creative
    'adobe.com': 'Adobe Creative Cloud',
    'figma.com': 'Figma',
    'sketch.com': 'Sketch',
    'canva.com': 'Canva Pro',
    'invisionapp.com': 'InVision',

    # Cloud Storage
    'dropbox.com': 'Dropbox',
    'box.com': 'Box',
    'onedrive.microsoft.com': 'OneDrive',
    'drive.google.com': 'Google Drive',
    'icloud.com': 'iCloud+',

    # Office Suites
    'google.com/workspace': 'Google Workspace',
    'microsoft.com/microsoft-365': 'Microsoft 365',
    'office.com': 'Microsoft Office',
    'zoho.com': 'Zoho Workplace',
}
```

### Business & Finance

```python
BUSINESS_SUBSCRIPTIONS = {
    # Accounting
    'xero.com': 'Xero',
    'quickbooks.intuit.com': 'QuickBooks',
    'freshbooks.com': 'FreshBooks',
    'wave.com': 'Wave',

    # CRM
    'salesforce.com': 'Salesforce',
    'hubspot.com': 'HubSpot',
    'pipedrive.com': 'Pipedrive',
    'zoho.com/crm': 'Zoho CRM',

    # Payment Processing
    'stripe.com': 'Stripe',
    'paypal.com': 'PayPal Business',
    'square.com': 'Square',
    'braintree.com': 'Braintree',

    # Business Services
    'docusign.com': 'DocuSign',
    'hellosign.com': 'HelloSign',
    'pandadoc.com': 'PandaDoc',
    'signrequest.com': 'SignRequest',
}
```

### Marketing & Analytics

```python
MARKETING_SUBSCRIPTIONS = {
    # Email Marketing
    'mailchimp.com': 'Mailchimp',
    'convertkit.com': 'ConvertKit',
    'activecampaign.com': 'ActiveCampaign',
    'constantcontact.com': 'Constant Contact',
    'sendgrid.com': 'SendGrid',

    # SEO & Analytics
    'google.com/analytics': 'Google Analytics 360',
    'semrush.com': 'SEMrush',
    'ahrefs.com': 'Ahrefs',
    'moz.com': 'Moz Pro',

    # Social Media Management
    'hootsuite.com': 'Hootsuite',
    'buffer.com': 'Buffer',
    'sproutsocial.com': 'Sprout Social',
    'later.com': 'Later',

    # Advertising
    'facebook.com/business': 'Facebook Ads',
    'ads.google.com': 'Google Ads',
    'linkedin.com/advertising': 'LinkedIn Ads',
}
```

### Entertainment & Personal

```python
ENTERTAINMENT_SUBSCRIPTIONS = {
    # Streaming
    'netflix.com': 'Netflix',
    'spotify.com': 'Spotify',
    'apple.com/music': 'Apple Music',
    'youtube.com/premium': 'YouTube Premium',
    'primevideo.com': 'Amazon Prime Video',
    'hulu.com': 'Hulu',
    'disneyplus.com': 'Disney+',

    # News & Media
    'nytimes.com': 'New York Times',
    'wsj.com': 'Wall Street Journal',
    'medium.com': 'Medium Membership',
}
```

### Infrastructure & Hosting

```python
INFRASTRUCTURE_SUBSCRIPTIONS = {
    # Cloud Computing
    'aws.amazon.com': 'Amazon Web Services',
    'azure.microsoft.com': 'Microsoft Azure',
    'cloud.google.com': 'Google Cloud Platform',
    'digitalocean.com': 'DigitalOcean',
    'linode.com': 'Linode',
    'heroku.com': 'Heroku',

    # Domain & Hosting
    'godaddy.com': 'GoDaddy',
    'namecheap.com': 'Namecheap',
    'hover.com': 'Hover',
    'bluehost.com': 'Bluehost',
    'siteground.com': 'SiteGround',

    # CDN & Security
    'cloudflare.com': 'Cloudflare',
    'fastly.com': 'Fastly',
    'akamai.com': 'Akamai',
}
```

---

## Detection Logic

### Pattern Matching

```python
def detect_subscription(transaction):
    """
    Detect if transaction is a subscription based on pattern matching
    """
    description = transaction['description'].lower()
    vendor = transaction.get('vendor', '').lower()

    # Combine all subscription patterns
    ALL_PATTERNS = {
        **SOFTWARE_SUBSCRIPTIONS,
        **BUSINESS_SUBSCRIPTIONS,
        **MARKETING_SUBSCRIPTIONS,
        **ENTERTAINMENT_SUBSCRIPTIONS,
        **INFRASTRUCTURE_SUBSCRIPTIONS,
    }

    # Check description and vendor
    for pattern, name in ALL_PATTERNS.items():
        if pattern in description or pattern in vendor:
            return {
                'detected': True,
                'name': name,
                'pattern': pattern,
                'amount': transaction['amount'],
                'date': transaction['date'],
                'confidence': 'high'
            }

    # Additional heuristics
    if is_recurring_charge(transaction):
        return {
            'detected': True,
            'name': transaction.get('vendor', 'Unknown Subscription'),
            'pattern': 'recurring',
            'amount': transaction['amount'],
            'date': transaction['date'],
            'confidence': 'medium'
        }

    return {'detected': False}


def is_recurring_charge(transaction):
    """
    Detect if charge is recurring based on transaction history
    """
    # Check if same amount charged monthly
    # Check if same vendor charged regularly
    # Pattern: 3+ charges at regular intervals
    pass
```

### Frequency Detection

```python
def detect_billing_frequency(transactions, subscription):
    """
    Detect billing frequency (monthly, annual, etc.)
    """
    charges = [
        t for t in transactions
        if subscription['pattern'] in t['description'].lower()
    ]

    if len(charges) < 2:
        return 'monthly'  # default assumption

    # Calculate days between charges
    intervals = []
    for i in range(len(charges) - 1):
        days = (charges[i+1]['date'] - charges[i]['date']).days
        intervals.append(days)

    avg_interval = sum(intervals) / len(intervals)

    if 25 <= avg_interval <= 35:
        return 'monthly'
    elif 85 <= avg_interval <= 95:
        return 'quarterly'
    elif 350 <= avg_interval <= 380:
        return 'annual'
    else:
        return 'irregular'
```

---

## Categorization

### By Function

```python
SUBSCRIPTION_CATEGORIES = {
    'Development': [
        'GitHub', 'GitLab', 'JetBrains', 'Visual Studio'
    ],
    'Productivity': [
        'Notion', 'Asana', 'Monday.com', 'Trello'
    ],
    'Communication': [
        'Slack', 'Zoom', 'Microsoft Teams'
    ],
    'Design': [
        'Adobe Creative Cloud', 'Figma', 'Canva Pro'
    ],
    'Storage': [
        'Dropbox', 'Box', 'Google Drive', 'OneDrive'
    ],
    'Business Tools': [
        'Xero', 'QuickBooks', 'DocuSign', 'Salesforce'
    ],
    'Marketing': [
        'Mailchimp', 'HubSpot', 'SEMrush', 'Hootsuite'
    ],
    'Infrastructure': [
        'AWS', 'Azure', 'Google Cloud', 'DigitalOcean'
    ],
    'Entertainment': [
        'Netflix', 'Spotify', 'YouTube Premium'
    ]
}


def categorize_subscription(subscription_name):
    """Categorize subscription by function"""
    for category, subscriptions in SUBSCRIPTION_CATEGORIES.items():
        if subscription_name in subscriptions:
            return category
    return 'Other'
```

### By Business Essentiality

```python
ESSENTIALITY_LEVELS = {
    'Critical': {
        'description': 'Business cannot operate without',
        'examples': ['Xero', 'Google Workspace', 'GitHub', 'AWS']
    },
    'Important': {
        'description': 'Significant impact if removed',
        'examples': ['Slack', 'Asana', 'Zoom', 'Dropbox']
    },
    'Useful': {
        'description': 'Nice to have, productivity boost',
        'examples': ['Notion', 'Canva Pro', 'Grammarly']
    },
    'Optional': {
        'description': 'Minimal business impact',
        'examples': ['Spotify', 'Netflix', 'Medium']
    }
}
```

---

## Audit Rules

### Unused Subscription Detection

```python
UNUSED_CRITERIA = {
    'no_login_days': 30,          # Flag if no login in 30+ days
    'low_usage_threshold': 0.10,  # Flag if <10% usage
    'no_api_calls_days': 30,      # Flag if no API calls in 30+ days
    'no_file_access_days': 45,    # Flag if no files accessed in 45+ days
}


def check_if_unused(subscription, activity_data):
    """
    Check if subscription is unused based on criteria
    """
    findings = []

    # Check login activity
    if activity_data.get('last_login'):
        days_since_login = (datetime.now() - activity_data['last_login']).days
        if days_since_login > UNUSED_CRITERIA['no_login_days']:
            findings.append({
                'rule': 'no_login',
                'severity': 'high',
                'message': f"No login in {days_since_login} days"
            })

    # Check usage metrics
    if activity_data.get('usage_percentage'):
        if activity_data['usage_percentage'] < UNUSED_CRITERIA['low_usage_threshold']:
            findings.append({
                'rule': 'low_usage',
                'severity': 'medium',
                'message': f"Only {activity_data['usage_percentage']*100:.0f}% usage"
            })

    return findings
```

### Duplicate Functionality Detection

```python
DUPLICATE_GROUPS = [
    {
        'name': 'Project Management',
        'services': ['Asana', 'Monday.com', 'Trello', 'ClickUp', 'Jira'],
        'recommendation': 'Choose one primary tool'
    },
    {
        'name': 'Cloud Storage',
        'services': ['Dropbox', 'Box', 'Google Drive', 'OneDrive', 'iCloud+'],
        'recommendation': 'Consolidate to one or two services'
    },
    {
        'name': 'Communication',
        'services': ['Slack', 'Microsoft Teams', 'Discord'],
        'recommendation': 'Use one primary communication platform'
    },
    {
        'name': 'Video Conferencing',
        'services': ['Zoom', 'Google Meet', 'Microsoft Teams', 'GoToMeeting'],
        'recommendation': 'Consolidate to one service'
    },
    {
        'name': 'Documentation',
        'services': ['Notion', 'Confluence', 'Coda', 'Google Docs'],
        'recommendation': 'Standardize on one documentation platform'
    }
]


def find_duplicates(active_subscriptions):
    """
    Find subscriptions with duplicate functionality
    """
    duplicates = []

    for group in DUPLICATE_GROUPS:
        active_in_group = [
            sub for sub in active_subscriptions
            if sub['name'] in group['services']
        ]

        if len(active_in_group) > 1:
            total_cost = sum(sub['amount'] for sub in active_in_group)
            duplicates.append({
                'group': group['name'],
                'subscriptions': active_in_group,
                'total_cost': total_cost,
                'recommendation': group['recommendation'],
                'potential_savings': total_cost - min(sub['amount'] for sub in active_in_group)
            })

    return duplicates
```

### Cost Increase Detection

```python
def check_price_increase(subscription, historical_data, threshold=0.20):
    """
    Check if subscription price has increased
    """
    if not historical_data:
        return False

    previous_prices = [h['amount'] for h in historical_data]
    if not previous_prices:
        return False

    avg_previous = sum(previous_prices) / len(previous_prices)
    current_price = subscription['amount']

    increase_percentage = (current_price - avg_previous) / avg_previous

    if increase_percentage > threshold:
        return {
            'detected': True,
            'previous_avg': avg_previous,
            'current': current_price,
            'increase_pct': increase_percentage * 100,
            'annual_impact': (current_price - avg_previous) * 12
        }

    return False
```

---

## Recommendations Engine

### Cost Optimization

```python
def generate_cost_recommendations(subscriptions, usage_data, duplicates):
    """
    Generate cost optimization recommendations
    """
    recommendations = []

    # Unused subscriptions
    for sub in subscriptions:
        if sub.get('unused'):
            annual_cost = sub['amount'] * 12
            recommendations.append({
                'type': 'cancel_unused',
                'subscription': sub['name'],
                'reason': 'No activity in 30+ days',
                'action': 'Cancel subscription',
                'savings': annual_cost,
                'priority': 'high'
            })

    # Duplicates
    for dup in duplicates:
        recommendations.append({
            'type': 'consolidate_duplicates',
            'group': dup['group'],
            'subscriptions': [s['name'] for s in dup['subscriptions']],
            'action': f"Keep one, cancel others. {dup['recommendation']}",
            'savings': dup['potential_savings'] * 12,
            'priority': 'medium'
        })

    # Downgrade opportunities
    for sub in subscriptions:
        if sub.get('usage_percentage') and sub['usage_percentage'] < 0.30:
            if has_cheaper_tier(sub['name']):
                potential_savings = sub['amount'] * 0.30  # Assume 30% savings
                recommendations.append({
                    'type': 'downgrade_tier',
                    'subscription': sub['name'],
                    'reason': f"Only using {sub['usage_percentage']*100:.0f}% of features",
                    'action': 'Consider downgrading to cheaper tier',
                    'savings': potential_savings * 12,
                    'priority': 'medium'
                })

    # Sort by savings potential
    recommendations.sort(key=lambda x: x.get('savings', 0), reverse=True)

    return recommendations
```

---

## Custom Patterns

### Adding Your Subscriptions

```python
# Add to scripts/audit_subscriptions.py
CUSTOM_PATTERNS = {
    'yourcompany.com': 'Your Service',
    'specificapp.io': 'Specific App Name',
}

# Merge with main patterns
ALL_PATTERNS = {
    **SOFTWARE_SUBSCRIPTIONS,
    **BUSINESS_SUBSCRIPTIONS,
    **CUSTOM_PATTERNS,
}
```

### Industry-Specific Patterns

```python
# Legal Industry
LEGAL_SUBSCRIPTIONS = {
    'lexisnexis.com': 'LexisNexis',
    'westlaw.com': 'Westlaw',
    'casetext.com': 'Casetext',
}

# Medical Industry
MEDICAL_SUBSCRIPTIONS = {
    'uptodate.com': 'UpToDate',
    'epocrates.com': 'Epocrates',
    'medscape.com': 'Medscape',
}

# Real Estate
REAL_ESTATE_SUBSCRIPTIONS = {
    'zillow.com/premier': 'Zillow Premier Agent',
    'realtor.com': 'Realtor.com Pro',
    'mls.com': 'MLS Access',
}
```

---

## Reporting Format

### Subscription Summary

```markdown
## Active Subscriptions

**Total Count:** 15
**Total Monthly Cost:** $1,247
**Total Annual Cost:** $14,964

### By Category
| Category | Count | Monthly Cost | Annual Cost |
|----------|-------|--------------|-------------|
| Productivity | 4 | $312 | $3,744 |
| Communication | 3 | $185 | $2,220 |
| Infrastructure | 3 | $450 | $5,400 |
| Marketing | 2 | $150 | $1,800 |
| Design | 2 | $100 | $1,200 |
| Other | 1 | $50 | $600 |

### By Essentiality
- Critical: 5 subscriptions ($780/month)
- Important: 6 subscriptions ($347/month)
- Useful: 3 subscriptions ($100/month)
- Optional: 1 subscription ($20/month)
```

### Optimization Opportunities

```markdown
## Cost Optimization Opportunities

**Total Potential Savings:** $3,240/year

### High Priority (Act This Week)
1. **Cancel: Notion** - $15/month
   - No activity in 45 days
   - Duplicate with Google Docs
   - Annual savings: $180

2. **Consolidate: Project Management** - $40/month savings
   - Active: Asana ($25), Trello ($10), Monday.com ($25)
   - Recommendation: Keep Asana, cancel others
   - Annual savings: $420

### Medium Priority (Review This Month)
3. **Downgrade: Adobe Creative Cloud** - $35/month savings
   - Low usage (15% of features)
   - Consider Photography plan ($19.99 vs $54.99)
   - Annual savings: $420

4. **Review: Zoom** - $20/month
   - Price increased 25% last renewal
   - Consider alternatives or negotiate
   - Annual savings: $60 (if switch to $15/month plan)
```

---

## Integration with CEO Briefing

### Data Flow

```
Subscription Audit
    ↓
Pattern Detection (identify all subscriptions)
    ↓
Usage Analysis (check activity)
    ↓
Duplicate Detection (find overlaps)
    ↓
Cost Analysis (calculate optimization opportunities)
    ↓
Generate Recommendations
    ↓
Include in CEO Briefing
    ↓
Track Actions Taken
    ↓
Measure Actual Savings
```

### Briefing Section Format

```markdown
## 💳 Subscription Audit

### Summary
- **Total Subscriptions:** 15 ($1,247/month, $14,964/year)
- **Unused:** 2 subscriptions ($30/month)
- **Duplicates:** 1 group (3 subscriptions, $60/month waste)
- **Optimization Potential:** $3,240/year

### Quick Wins
1. ✅ Cancel Notion ($180/year) - No activity in 45 days
2. ✅ Downgrade Adobe ($420/year) - Low usage, cheaper plan available
3. ⚠️ Review Zoom ($60/year) - Price increased, consider alternatives

### Action Required
- [ ] Review and cancel unused subscriptions
- [ ] Consolidate project management tools
- [ ] Renegotiate or switch high-cost services

**Next Audit:** Monthly (3rd week)
```

---

## Performance Tracking

### Measure Audit Effectiveness

```python
AUDIT_METRICS = {
    'subscriptions_identified': 0,
    'unused_detected': 0,
    'duplicates_found': 0,
    'recommendations_generated': 0,
    'actions_taken': 0,
    'actual_savings': 0.0,
}


def track_audit_performance(audit_results, actions_taken):
    """Track effectiveness of subscription audits"""

    metrics = {
        'date': datetime.now(),
        'subscriptions_audited': len(audit_results['subscriptions']),
        'potential_savings': audit_results['total_potential_savings'],
        'recommendations': len(audit_results['recommendations']),
        'actions_taken': len(actions_taken),
        'actual_savings': sum(a['savings'] for a in actions_taken),
        'roi': calculate_roi(actions_taken)
    }

    return metrics
```

---

## Best Practices

1. **Run Monthly:** Schedule comprehensive audit monthly
2. **Track Actions:** Monitor which recommendations are acted upon
3. **Measure Savings:** Calculate actual savings achieved
4. **Update Patterns:** Add new subscriptions as discovered
5. **Customize Rules:** Adjust thresholds based on business needs
6. **Review Essentiality:** Update critical vs optional classifications quarterly

---

**Note:** This database should be continuously updated as new subscription services emerge and business needs change.
