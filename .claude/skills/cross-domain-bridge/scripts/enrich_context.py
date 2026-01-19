#!/usr/bin/env python3
"""
Context Enrichment Script for Cross-Domain Bridge

Extracts business entities and enriches items with cross-domain context.

Usage:
    python enrich_context.py --file Needs_Action/EMAIL_client_xyz.md
    python enrich_context.py --all
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

# Add vault path
VAULT_PATH = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(VAULT_PATH))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('cross-domain-bridge')


class ContextEnricher:
    """Enriches items with cross-domain business context."""

    def __init__(self, vault_path=None):
        self.vault_path = Path(vault_path) if vault_path else VAULT_PATH
        self.logs_path = self.vault_path / "Logs"
        self.logs_path.mkdir(exist_ok=True)

        # Load business context
        self.business_goals = self._load_business_goals()
        self.company_handbook = self._load_company_handbook()
        self.dashboard = self._load_dashboard()

        # Business keywords for entity extraction
        self.business_keywords = [
            'invoice', 'payment', 'project', 'deadline', 'client',
            'contract', 'proposal', 'deliverable', 'milestone',
            'meeting', 'call', 'urgent', 'asap', 'emergency'
        ]

    def _load_business_goals(self):
        """Load Business_Goals.md for context."""
        goals_path = self.vault_path / "Business_Goals.md"
        if not goals_path.exists():
            logger.warning(f"Business_Goals.md not found at {goals_path}")
            return {}

        try:
            content = goals_path.read_text(encoding='utf-8')
            # Parse frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    import yaml
                    try:
                        return yaml.safe_load(parts[1]) or {}
                    except:
                        pass
            return {}
        except Exception as e:
            logger.error(f"Error loading Business_Goals.md: {e}")
            return {}

    def _load_company_handbook(self):
        """Load Company_Handbook.md for rules."""
        handbook_path = self.vault_path / "Company_Handbook.md"
        if not handbook_path.exists():
            logger.warning(f"Company_Handbook.md not found at {handbook_path}")
            return {}

        try:
            content = handbook_path.read_text(encoding='utf-8')
            # Extract approval rules (simplified)
            rules = {}
            for line in content.split('\n'):
                if 'approval' in line.lower() and '|' in line:
                    # Parse table row
                    parts = line.split('|')
                    if len(parts) >= 3:
                        category = parts[1].strip().lower()
                        threshold = parts[2].strip()
                        rules[category] = threshold
            return rules
        except Exception as e:
            logger.error(f"Error loading Company_Handbook.md: {e}")
            return {}

    def _load_dashboard(self):
        """Load Dashboard.md for current status."""
        dashboard_path = self.vault_path / "Dashboard.md"
        if not dashboard_path.exists():
            return {}

        try:
            content = dashboard_path.read_text(encoding='utf-8')
            # Extract current revenue (simplified)
            revenue_match = re.search(r'Revenue.*?\$?([\d,]+)', content)
            return {
                'current_revenue': revenue_match.group(1) if revenue_match else '0'
            }
        except Exception as e:
            logger.error(f"Error loading Dashboard.md: {e}")
            return {}

    def extract_entities(self, content):
        """Extract business entities from text."""
        entities = {
            'clients': [],
            'projects': [],
            'keywords': [],
            'amounts': []
        }

        # Extract client names (simplified - looks for capitalized names)
        # In production, use NLP or predefined list
        client_patterns = re.findall(r'\b([A-Z][a-z]+ (?:Inc|LLC|Ltd|Corp|Company)?)\b', content)
        entities['clients'] = list(set(client_patterns))

        # Extract project names (common patterns)
        project_patterns = re.findall(r'\b(Project [A-Z][a-z]+|[A-Z][a-z]+ Project)\b', content)
        entities['projects'] = list(set(project_patterns))

        # Extract business keywords
        content_lower = content.lower()
        for keyword in self.business_keywords:
            if keyword in content_lower:
                entities['keywords'].append(keyword)

        # Extract monetary amounts
        amounts = re.findall(r'\$\s?([\d,]+(?:\.\d{2})?)', content)
        entities['amounts'] = amounts

        return entities

    def classify_domain(self, item_content, entities):
        """Classify item as personal, business, or cross-domain."""
        business_score = 0

        # Score based on entities
        if entities['clients']:
            business_score += 3
        if entities['projects']:
            business_score += 3
        if any(kw in entities['keywords'] for kw in ['invoice', 'payment', 'project', 'client']):
            business_score += 2
        if entities['amounts']:
            business_score += 1

        # Classify
        if business_score >= 5:
            return 'business'
        elif business_score >= 2:
            return 'cross_domain'
        else:
            return 'personal'

    def score_business_relevance(self, entities, domain):
        """Score business relevance (0.0 to 1.0)."""
        if domain == 'personal':
            return 0.0

        score = 0.5  # Base score for business-related

        # Add points for business entities
        if entities['clients']:
            score += 0.2
        if entities['projects']:
            score += 0.2
        if entities['amounts']:
            score += 0.1

        return min(1.0, score)

    def enrich_file(self, file_path):
        """Enrich a single file with cross-domain context."""
        file_path = Path(file_path)

        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False

        logger.info(f"Enriching file: {file_path}")

        try:
            # Read file
            content = file_path.read_text(encoding='utf-8')

            # Extract entities
            entities = self.extract_entities(content)

            # Classify domain
            domain = self.classify_domain(content, entities)

            # Score business relevance
            business_relevance = self.score_business_relevance(entities, domain)

            # Build enrichment data
            enrichment = {
                'domain': domain,
                'business_relevance_score': round(business_relevance, 2),
                'entities_extracted': {
                    'clients': entities['clients'],
                    'projects': entities['projects'],
                    'keywords': entities['keywords'],
                    'amounts': entities['amounts']
                },
                'enriched_at': datetime.now().isoformat(),
                'enriched_by': 'cross-domain-bridge'
            }

            # Check if approval required (based on amounts)
            if entities['amounts']:
                try:
                    max_amount = float(entities['amounts'][0].replace(',', ''))
                    if max_amount > 1000:  # Default threshold
                        enrichment['approval_required'] = True
                        enrichment['approval_reason'] = f"Amount ${max_amount:,.2f} exceeds threshold"
                except:
                    pass

            # Update file frontmatter
            updated_content = self._update_frontmatter(content, enrichment)

            # Write back
            file_path.write_text(updated_content, encoding='utf-8')

            logger.info(f"[OK] Enriched {file_path.name}")
            logger.info(f"  Domain: {domain}")
            logger.info(f"  Business Relevance: {business_relevance:.2f}")
            logger.info(f"  Entities: {len(entities['clients'])} clients, {len(entities['projects'])} projects")

            # Log activity
            self._log_enrichment(file_path, enrichment)

            return True

        except Exception as e:
            logger.error(f"Error enriching {file_path}: {e}")
            return False

    def _update_frontmatter(self, content, enrichment):
        """Update or add frontmatter to file."""
        lines = content.split('\n')

        # Check if frontmatter exists
        if content.startswith('---'):
            # Find end of frontmatter
            try:
                end_idx = lines.index('---', 1)
                # Insert enrichment after frontmatter
                for key, value in enrichment.items():
                    if isinstance(value, dict):
                        lines.insert(end_idx, f"{key}:")
                        for k, v in value.items():
                            if isinstance(v, list):
                                lines.insert(end_idx + 1, f"  {k}: {json.dumps(v)}")
                            else:
                                lines.insert(end_idx + 1, f"  {k}: {v}")
                        end_idx += len(value) + 1
                    elif isinstance(value, list):
                        lines.insert(end_idx, f"{key}: {json.dumps(value)}")
                        end_idx += 1
                    else:
                        lines.insert(end_idx, f"{key}: {value}")
                        end_idx += 1
                return '\n'.join(lines)
            except ValueError:
                pass

        # No frontmatter, create it
        frontmatter = "---\n"
        for key, value in enrichment.items():
            if isinstance(value, dict):
                frontmatter += f"{key}:\n"
                for k, v in value.items():
                    if isinstance(v, list):
                        frontmatter += f"  {k}: {json.dumps(v)}\n"
                    else:
                        frontmatter += f"  {k}: {v}\n"
            elif isinstance(value, list):
                frontmatter += f"{key}: {json.dumps(value)}\n"
            else:
                frontmatter += f"{key}: {value}\n"
        frontmatter += "---\n\n"

        return frontmatter + content

    def _log_enrichment(self, file_path, enrichment):
        """Log enrichment activity."""
        log_file = self.logs_path / f"cross_domain_{datetime.now().strftime('%Y-%m-%d')}.json"

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "context_enrichment",
            "file": str(file_path.relative_to(self.vault_path)) if file_path.is_relative_to(self.vault_path) else str(file_path.name),
            "domain": enrichment['domain'],
            "business_relevance_score": enrichment['business_relevance_score'],
            "entities_extracted": enrichment['entities_extracted'],
            "skill": "cross-domain-bridge"
        }

        try:
            logs = []
            if log_file.exists():
                logs = json.loads(log_file.read_text())

            logs.append(log_entry)

            log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')
        except Exception as e:
            logger.error(f"Error logging enrichment: {e}")


def main():
    parser = argparse.ArgumentParser(description='Enrich items with cross-domain context')
    parser.add_argument('--file', help='Specific file to enrich')
    parser.add_argument('--all', action='store_true', help='Enrich all files in Needs_Action')
    parser.add_argument('--vault', help='Vault path (default: auto-detect)')

    args = parser.parse_args()

    enricher = ContextEnricher(vault_path=args.vault)

    if args.file:
        # Enrich single file
        success = enricher.enrich_file(args.file)
        sys.exit(0 if success else 1)

    elif args.all:
        # Enrich all files in Needs_Action
        needs_action = enricher.vault_path / "Needs_Action"
        if not needs_action.exists():
            logger.error(f"Needs_Action folder not found: {needs_action}")
            sys.exit(1)

        files = list(needs_action.glob("*.md"))
        if not files:
            logger.info("No files found in Needs_Action")
            sys.exit(0)

        logger.info(f"Enriching {len(files)} files...")

        success_count = 0
        for file_path in files:
            if enricher.enrich_file(file_path):
                success_count += 1

        logger.info(f"Enriched {success_count}/{len(files)} files successfully")
        sys.exit(0 if success_count == len(files) else 1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
