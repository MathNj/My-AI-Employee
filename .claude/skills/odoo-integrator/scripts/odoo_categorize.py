#!/usr/bin/env python3
"""
Odoo Categorize Script for AI Employee

Automatically categorizes expenses using AI and rule-based matching.
Uses the Odoo MCP server for all operations.

Usage:
    python odoo_categorize.py --auto
    python odoo_categorize.py --review
    python odoo_categorize.py --export-rules
"""

import os
import sys
import json
import logging
import argparse
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
log_dir = Path(__file__).parent.parent.parent.parent / "Logs"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / "odoo_integrator_2026-01-18.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("odoo_categorize")


class OdooCategorizer:
    """Categorize Odoo expenses using AI and rules"""

    def __init__(self):
        self.mcp_url = os.getenv("ODOO_MCP_URL", "http://localhost:8000")
        self.vault_path = Path(os.getenv("VAULT_PATH", "."))
        self.accounting_path = self.vault_path / "Accounting"
        self.rules_file = Path(__file__).parent.parent / "references" / "category_rules.json"

        # Load category rules
        self.rules = self._load_rules()

        # Track statistics
        self.stats = {
            "processed": 0,
            "categorized": 0,
            "manual_review": 0,
            "confidence_total": 0.0
        }

    def _load_rules(self) -> Dict:
        """Load category rules from file"""
        if self.rules_file.exists():
            with open(self.rules_file, 'r') as f:
                return json.load(f)

        # Default rules
        return {
            "categories": [
                {
                    "name": "Software Expenses",
                    "account_code": "6000",
                    "description": "Software licenses, SaaS subscriptions",
                    "keywords": ["software", "saas", "subscription", "license", "cloud"],
                    "vendors": ["microsoft.com", "google.com", "adobe.com", "amazon aws"]
                },
                {
                    "name": "Office Supplies",
                    "account_code": "6050",
                    "description": "Office supplies and stationery",
                    "keywords": ["office", "supplies", "stationery", "paper", "ink"],
                    "vendors": ["staples.com", "office depot"]
                },
                {
                    "name": "Travel Expenses",
                    "account_code": "6100",
                    "description": "Business travel and accommodation",
                    "keywords": ["travel", "hotel", "airline", "flight", "rental car", "uber", "lyft"],
                    "vendors": ["expedia.com", "airbnb.com", "uber.com"]
                },
                {
                    "name": "Marketing",
                    "account_code": "6200",
                    "description": "Marketing and advertising",
                    "keywords": ["marketing", "advertising", "social media", "facebook ads", "google ads"],
                    "vendors": ["facebook.com", "google.com", "linkedin.com"]
                },
                {
                    "name": "Professional Services",
                    "account_code": "6300",
                    "description": "Professional services and consulting",
                    "keywords": ["consulting", "legal", "accounting", "professional"],
                    "vendors": []
                },
                {
                    "name": "Utilities",
                    "account_code": "6400",
                    "description": "Utilities and services",
                    "keywords": ["electric", "water", "gas", "internet", "phone", "utility"],
                    "vendors": []
                }
            ]
        }

    def _call_mcp(self, tool_name: str, arguments: Dict) -> Any:
        """Call Odoo MCP server tool"""
        try:
            response = requests.post(
                f"{self.mcp_url}/",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                return None

            result = data.get("result", {})
            if "content" in result and len(result["content"]) > 0:
                text = result["content"][0].get("text", "")
                return json.loads(text) if text else None

            return result

        except Exception as e:
            logger.error(f"MCP call failed: {e}")
            return None

    def _match_category(self, description: str, partner_name: str = "") -> Optional[Dict]:
        """Match transaction to category using rules"""
        if not description:
            return None

        desc_lower = description.lower()
        partner_lower = partner_name.lower() if partner_name else ""

        best_match = None
        best_score = 0

        for category in self.rules["categories"]:
            score = 0

            # Check keywords
            for keyword in category.get("keywords", []):
                if keyword.lower() in desc_lower:
                    score += 2

            # Check vendors
            for vendor in category.get("vendors", []):
                if vendor.lower() in partner_lower or vendor.lower() in desc_lower:
                    score += 3

            if score > best_score:
                best_score = score
                best_match = category

        if best_score >= 2:
            return {
                "category": best_match["name"],
                "account_code": best_match["account_code"],
                "confidence": min(best_score / 5.0, 1.0),  # Max confidence 1.0
                "method": "rule_based"
            }

        return None

    def _ai_categorize(self, description: str, amount: float, partner_name: str = "") -> Optional[Dict]:
        """Use AI to categorize transaction (placeholder for Claude integration)"""
        # This would call Claude to categorize
        # For now, return None to indicate manual review needed
        logger.debug(f"AI categorization not implemented for: {description}")
        return None

    def categorize_expenses(self, auto: bool = True, limit: int = 100) -> Dict:
        """Categorize uncategorized expenses"""
        logger.info("Categorizing expenses...")

        # Find uncategorized journal entries
        result = self._call_mcp("search_records", {
            "model": "account.move.line",
            "domain": [
                ["account_id", "=", None],  # No account set
                ["parent_id.state", "=", "posted"]
            ],
            "fields": ["id", "name", "amount", "partner_id", "date", "account_id"],
            "limit": limit
        })

        if not result or "records" not in result:
            logger.warning("No uncategorized expenses found")
            return self.stats

        expenses = result["records"]
        self.stats["processed"] = len(expenses)

        logger.info(f"Processing {len(expenses)} uncategorized expenses")

        categorized = []
        manual_review = []

        for expense in expenses:
            exp_id = expense["id"]
            description = expense.get("name", "")
            amount = expense.get("amount", 0.0)
            partner = expense.get("partner_id", [])
            partner_name = partner[1] if isinstance(partner, list) and len(partner) > 1 else ""

            # Try rule-based matching first
            category = self._match_category(description, partner_name)

            # Fall back to AI if enabled and no rule match
            if not category and auto:
                category = self._ai_categorize(description, amount, partner_name)

            if category:
                categorized.append({
                    "id": exp_id,
                    "description": description,
                    "amount": amount,
                    "category": category["category"],
                    "account_code": category["account_code"],
                    "confidence": category["confidence"],
                    "method": category["method"]
                })
                self.stats["categorized"] += 1
                self.stats["confidence_total"] += category["confidence"]

                logger.info(f"✓ {description[:50]:50} -> {category['category']} ({category['confidence']:.0%})")

            else:
                manual_review.append({
                    "id": exp_id,
                    "description": description,
                    "amount": amount,
                    "partner": partner_name
                })
                self.stats["manual_review"] += 1

                logger.warning(f"? {description[:50]:50} -> MANUAL REVIEW")

        # Save results
        if categorized:
            self._save_categorization(categorized)

        if manual_review:
            self._save_manual_review(manual_review)

        return self.stats

    def _save_categorization(self, categorized: List[Dict]):
        """Save categorization results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.accounting_path / "Categorization" / f"{timestamp}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "count": len(categorized),
                "items": categorized
            }, f, indent=2)

        logger.info(f"Saved categorization to {file_path.name}")

    def _save_manual_review(self, manual_review: List[Dict]):
        """Save items requiring manual review"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = self.accounting_path / "Manual_Review" / f"{timestamp}.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "count": len(manual_review),
                "items": manual_review
            }, f, indent=2)

        logger.info(f"Saved {len(manual_review)} items for manual review to {file_path.name}")

    def review_categorization(self, limit: int = 50):
        """Review recent categorizations"""
        logger.info("Reviewing recent categorizations...")

        # Find most recent categorization file
        cat_dir = self.accounting_path / "Categorization"
        if not cat_dir.exists():
            logger.warning("No categorization files found")
            return

        files = sorted(cat_dir.glob("*.json"), reverse=True)[:1]

        if not files:
            logger.warning("No categorization files found")
            return

        with open(files[0], 'r') as f:
            data = json.load(f)

        items = data.get("items", [])

        print(f"\n📋 Categorization Review ({files[0].name})")
        print("=" * 80)

        for i, item in enumerate(items[:limit], 1):
            print(f"\n{i}. {item['description'][:60]}")
            print(f"   Amount: ${item.get('amount', 0):.2f}")
            print(f"   Category: {item['category']} ({item['account_code']})")
            print(f"   Confidence: {item['confidence']:.0%}")
            print(f"   Method: {item['method']}")

        print(f"\nTotal: {len(items)} items")

    def export_rules(self):
        """Export category rules to file"""
        self.rules_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.rules_file, 'w') as f:
            json.dump(self.rules, f, indent=2)

        logger.info(f"Exported {len(self.rules['categories'])} category rules to {self.rules_file}")

    def print_summary(self):
        """Print categorization summary"""
        total = self.stats["processed"]
        categorized = self.stats["categorized"]
        manual = self.stats["manual_review"]
        avg_confidence = self.stats["confidence_total"] / categorized if categorized > 0 else 0

        print("\n" + "=" * 60)
        print("📊 Categorization Summary")
        print("=" * 60)
        print(f"Processed:     {total}")
        print(f"Categorized:   {categorized} ({categorized/total*100:.0f}%)" if total > 0 else "Categorized:   0")
        print(f"Manual Review: {manual} ({manual/total*100:.0f}%)" if total > 0 else "Manual Review: 0")
        print(f"Avg Confidence: {avg_confidence:.1%}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Categorize Odoo expenses using AI and rules"
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Auto categorize
    auto_parser = subparsers.add_parser("auto", help="Auto-categorize expenses")
    auto_parser.add_argument("--limit", type=int, default=100, help="Max expenses to process")

    # Review
    review_parser = subparsers.add_parser("review", help="Review categorizations")
    review_parser.add_argument("--limit", type=int, default=50, help="Max items to review")

    # Export rules
    subparsers.add_parser("export-rules", help="Export category rules")

    args = parser.parse_args()

    # Load environment
    from dotenv import load_dotenv
    load_dotenv()

    # Create categorizer
    categorizer = OdooCategorizer()

    if args.command == "auto":
        categorizer.categorize_expenses(auto=True, limit=args.limit)
        categorizer.print_summary()
    elif args.command == "review":
        categorizer.review_categorization(limit=args.limit)
    elif args.command == "export-rules":
        categorizer.export_rules()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
