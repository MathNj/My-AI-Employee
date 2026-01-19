#!/usr/bin/env python3
"""
Cross-Domain Analysis Script

Analyzes cross-domain impact and provides recommendations.

Usage:
    python analyze_cross_domain.py --file Needs_Action/WHATSAPP_invoice.md
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, time
from pathlib import Path

# Vault path
VAULT_PATH = Path(__file__).parent.parent.parent.parent


class CrossDomainAnalyzer:
    """Analyzes cross-domain impact of items."""

    def __init__(self, vault_path=None):
        self.vault_path = Path(vault_path) if vault_path else VAULT_PATH

        # Personal boundary settings
        self.personal_hours = {
            'start': 18,  # 6 PM
            'end': 9,     # 9 AM
            'weekend': True
        }

    def is_personal_time(self, timestamp_str=None):
        """Check if current time is personal time."""
        if timestamp_str:
            try:
                dt = datetime.fromisoformat(timestamp_str)
            except:
                dt = datetime.now()
        else:
            dt = datetime.now()

        # Check weekend
        if self.personal_hours['weekend'] and dt.weekday() >= 5:
            return True

        # Check hours
        hour = dt.hour
        if hour >= self.personal_hours['start'] or hour < self.personal_hours['end']:
            return True

        return False

    def analyze_personal_time_impact(self, item_path):
        """Check if item violates personal time boundaries."""
        content = item_path.read_text(encoding='utf-8')

        # Extract timestamp
        timestamp = None
        for line in content.split('\n'):
            if line.startswith('timestamp:') or 'timestamp:' in line:
                try:
                    timestamp = line.split(':', 1)[1].strip()
                    break
                except:
                    pass

        is_personal = self.is_personal_time(timestamp)

        return {
            'is_personal_time': is_personal,
            'timestamp': timestamp,
            'boundary_violation': is_personal
        }

    def analyze_business_impact(self, item_path, enrichment_data=None):
        """Assess business impact."""
        content = item_path.read_text(encoding='utf-8')

        impact = {
            'urgency': 'low',
            'client_importance': 'unknown',
            'revenue_impact': 'unknown',
            'deadline_proximity': 'none'
        }

        # Check urgency keywords
        content_lower = content.lower()
        if any(kw in content_lower for kw in ['urgent', 'emergency', 'asap', 'immediate']):
            impact['urgency'] = 'high'
        elif any(kw in content_lower for kw in ['important', 'priority', 'deadline']):
            impact['urgency'] = 'medium'

        # Check enrichment data if available
        if enrichment_data:
            entities = enrichment_data.get('entities_extracted', {})
            if entities.get('amounts'):
                try:
                    amount = float(entities['amounts'][0].replace(',', ''))
                    if amount > 5000:
                        impact['revenue_impact'] = 'high'
                    elif amount > 1000:
                        impact['revenue_impact'] = 'medium'
                    else:
                        impact['revenue_impact'] = 'low'
                except:
                    pass

        return impact

    def check_approval_requirements(self, item_path):
        """Determine if approval is needed."""
        content = item_path.read_text(encoding='utf-8')

        requirements = {
            'approval_required': False,
            'reason': None,
            'threshold_type': None
        }

        # Check amounts
        import re
        amounts = re.findall(r'\$\s?([\d,]+(?:\.\d{2})?)', content)
        if amounts:
            try:
                max_amount = float(amounts[0].replace(',', ''))
                if max_amount > 1000:
                    requirements['approval_required'] = True
                    requirements['reason'] = f"Amount ${max_amount:,.2f} exceeds $1,000 threshold"
                    requirements['threshold_type'] = 'amount'
            except:
                pass

        return requirements

    def generate_recommendations(self, item_path, personal_impact, business_impact, approval_req):
        """Generate actionable recommendations."""
        recommendations = []

        # Personal time recommendations
        if personal_impact['boundary_violation']:
            if business_impact['urgency'] == 'high':
                recommendations.append({
                    'type': 'interrupt',
                    'priority': 'high',
                    'message': 'Urgent business matter during personal time - consider interrupting'
                })
            else:
                recommendations.append({
                    'type': 'defer',
                    'priority': 'medium',
                    'message': 'Non-urgent business during personal time - defer to next business day'
                })

        # Business impact recommendations
        if business_impact['urgency'] == 'high':
            recommendations.append({
                'type': 'urgent_response',
                'priority': 'high',
                'message': 'High urgency detected - respond within 1 hour'
            })

        # Approval recommendations
        if approval_req['approval_required']:
            recommendations.append({
                'type': 'approval',
                'priority': 'high',
                'message': f"Approval required: {approval_req['reason']}"
            })

        return recommendations

    def analyze_file(self, file_path):
        """Perform complete cross-domain analysis."""
        file_path = Path(file_path)

        if not file_path.exists():
            print(f"Error: File not found: {file_path}")
            return False

        print(f"\n{'='*60}")
        print(f"Cross-Domain Analysis: {file_path.name}")
        print(f"{'='*60}\n")

        # Load enrichment if exists
        enrichment = {}
        content = file_path.read_text(encoding='utf-8')
        if 'domain:' in content:
            # Enrichment exists, parse it
            try:
                import yaml
                if content.startswith('---'):
                    parts = content.split('---', 2)
                    if len(parts) >= 2:
                        enrichment = yaml.safe_load(parts[1]) or {}
            except:
                pass

        # Analyze personal time impact
        print("[1] Personal Time Analysis")
        personal_impact = self.analyze_personal_time_impact(file_path)
        print(f"  Personal Time: {'Yes' if personal_impact['is_personal_time'] else 'No'}")
        print(f"  Boundary Violation: {'Yes' if personal_impact['boundary_violation'] else 'No'}")
        print()

        # Analyze business impact
        print("[2] Business Impact Analysis")
        business_impact = self.analyze_business_impact(file_path, enrichment)
        print(f"  Urgency: {business_impact['urgency'].upper()}")
        print(f"  Revenue Impact: {business_impact['revenue_impact'].upper()}")
        print()

        # Check approval requirements
        print("[3] Approval Requirements")
        approval_req = self.check_approval_requirements(file_path)
        print(f"  Approval Required: {'Yes' if approval_req['approval_required'] else 'No'}")
        if approval_req['reason']:
            print(f"  Reason: {approval_req['reason']}")
        print()

        # Generate recommendations
        print("[4] Recommendations")
        recommendations = self.generate_recommendations(
            file_path, personal_impact, business_impact, approval_req
        )

        if not recommendations:
            print("  No specific recommendations - standard processing applies")
        else:
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. [{rec['priority'].upper()}] {rec['message']}")

        print()
        print(f"{'='*60}\n")

        return True


def main():
    parser = argparse.ArgumentParser(description='Analyze cross-domain impact')
    parser.add_argument('--file', required=True, help='File to analyze')
    parser.add_argument('--vault', help='Vault path (default: auto-detect)')

    args = parser.parse_args()

    analyzer = CrossDomainAnalyzer(vault_path=args.vault)
    success = analyzer.analyze_file(args.file)

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
