#!/usr/bin/env python3
"""
Web Search - Main Research Interface

Performs web searches using available search providers and returns
formatted research reports with source citations and confidence levels.

Usage:
    python web_search.py "search query"
    python web_search.py "search query" --provider brave
    python web_search.py "search query" --max-results 5
    python web_search.py "search query" --output report.md
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

# Vault path
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()
LOGS = VAULT_PATH / "Logs"
LOGS.mkdir(exist_ok=True)

# Search provider priority (fallback order)
PROVIDER_PRIORITY = ['brave', 'tavily', 'websearch']


def log_search(query, provider, results_count, status):
    """Log search activity."""
    log_file = LOGS / f"web_research_{datetime.now().strftime('%Y-%m-%d')}.json"

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "provider": provider,
        "results_count": results_count,
        "status": status,
        "skill": "web-researcher"
    }

    try:
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Warning: Failed to log search: {e}", file=sys.stderr)


def score_confidence(result: Dict, query: str) -> str:
    """
    Score confidence level for a search result.

    Returns: 'High', 'Medium', or 'Low'
    """
    score = 0

    # Factor 1: Domain authority (basic heuristic)
    domain = result.get('url', '').lower()
    high_authority = [
        '.gov', '.edu', 'wikipedia.org', 'github.com',
        'stackoverflow.com', 'docs.', 'developer.'
    ]
    medium_authority = [
        '.org', 'medium.com', 'blog.', 'news.'
    ]

    if any(auth in domain for auth in high_authority):
        score += 3
    elif any(auth in domain for auth in medium_authority):
        score += 2
    else:
        score += 1

    # Factor 2: Title/content relevance (simple keyword match)
    title = result.get('title', '').lower()
    description = result.get('description', '').lower()
    query_words = query.lower().split()

    matching_words = sum(1 for word in query_words
                        if word in title or word in description)
    relevance_ratio = matching_words / len(query_words) if query_words else 0

    if relevance_ratio > 0.7:
        score += 3
    elif relevance_ratio > 0.4:
        score += 2
    else:
        score += 1

    # Factor 3: Recency (if available)
    if result.get('published_date'):
        # Prefer recent results
        score += 1

    # Convert score to confidence level
    if score >= 6:
        return 'High'
    elif score >= 4:
        return 'Medium'
    else:
        return 'Low'


def format_research_report(query: str, results: List[Dict], status: str = 'success') -> str:
    """
    Format search results into required research report format.

    Args:
        query: The search query used
        results: List of search results
        status: 'success' or 'failed'

    Returns:
        Formatted markdown report
    """
    report = "### 🔍 Research Report\n\n"
    report += f"**Query:** \"{query}\"\n"

    if status == 'success' and results:
        report += "**Status:** ✅ Success\n\n"

        # Results table
        report += "| Key Finding | Source URL | Confidence |\n"
        report += "|------------|------------|------------|\n"

        for result in results:
            title = result.get('title', 'No title')[:80]
            url = result.get('url', 'No URL')
            confidence = result.get('confidence', 'Medium')

            # Escape pipe characters in title
            title = title.replace('|', '\\|')

            report += f"| {title} | {url} | {confidence} |\n"

        # Summary
        report += "\n**Summary:**\n"

        if len(results) > 0:
            high_conf = sum(1 for r in results if r.get('confidence') == 'High')

            report += f"Found {len(results)} relevant source(s). "

            if high_conf > 0:
                report += f"{high_conf} high-confidence source(s) identified. "

            # Check for conflicting information
            unique_domains = set(result.get('url', '').split('/')[2]
                               for result in results if result.get('url'))
            if len(unique_domains) < len(results) / 2:
                report += "Note: Multiple sources from similar domains - verify independently. "

            # Low confidence warning
            low_conf = sum(1 for r in results if r.get('confidence') == 'Low')
            if low_conf > len(results) / 2:
                report += "⚠️  Most sources have low confidence - human review recommended."
        else:
            report += "No relevant sources found."

    else:
        report += "**Status:** ❌ Failed\n\n"
        report += "| Key Finding | Source URL | Confidence |\n"
        report += "|------------|------------|------------|\n"
        report += "| No results | N/A | N/A |\n\n"

        report += "**Summary:**\n"
        report += "Search failed or returned no reliable results. "
        report += "Consider rephrasing query or using alternative search methods."

    report += "\n"
    return report


def search_with_brave(query: str, max_results: int = 3) -> Optional[List[Dict]]:
    """Search using Brave Search API."""
    try:
        # Import here to make it optional
        from brave_search import search_brave
        return search_brave(query, max_results)
    except ImportError:
        print("Brave Search not available (brave_search.py not found)", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Brave Search failed: {e}", file=sys.stderr)
        return None


def search_with_tavily(query: str, max_results: int = 3) -> Optional[List[Dict]]:
    """Search using Tavily API."""
    try:
        from tavily_search import search_tavily
        return search_tavily(query, max_results)
    except ImportError:
        print("Tavily Search not available (tavily_search.py not found)", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Tavily Search failed: {e}", file=sys.stderr)
        return None


def search_with_websearch(query: str, max_results: int = 3) -> Optional[List[Dict]]:
    """Search using Claude's built-in WebSearch (if available via MCP)."""
    # This would use Claude Code's WebSearch tool if available
    # For now, placeholder
    print("WebSearch tool not yet implemented", file=sys.stderr)
    return None


def perform_search(query: str, provider: Optional[str] = None,
                  max_results: int = 3) -> tuple[List[Dict], str]:
    """
    Perform web search using specified or available provider.

    Args:
        query: Search query
        provider: Specific provider to use, or None for auto
        max_results: Maximum number of results

    Returns:
        (results, provider_used)
    """
    providers_to_try = [provider] if provider else PROVIDER_PRIORITY

    for prov in providers_to_try:
        print(f"Trying {prov}...", file=sys.stderr)

        if prov == 'brave':
            results = search_with_brave(query, max_results)
        elif prov == 'tavily':
            results = search_with_tavily(query, max_results)
        elif prov == 'websearch':
            results = search_with_websearch(query, max_results)
        else:
            continue

        if results:
            return results, prov

    # No provider succeeded
    return [], 'none'


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Perform web research with source citations'
    )
    parser.add_argument(
        'query',
        help='Search query'
    )
    parser.add_argument(
        '--provider',
        choices=['brave', 'tavily', 'websearch'],
        help='Specific search provider to use'
    )
    parser.add_argument(
        '--max-results',
        type=int,
        default=3,
        help='Maximum number of results (default: 3)'
    )
    parser.add_argument(
        '--output',
        '-o',
        type=str,
        help='Output file path (optional)'
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Perform search
    if args.verbose:
        print(f"Searching for: {args.query}")

    results, provider_used = perform_search(
        args.query,
        args.provider,
        args.max_results
    )

    # Score confidence for each result
    for result in results:
        result['confidence'] = score_confidence(result, args.query)

    # Format report
    status = 'success' if results else 'failed'
    report = format_research_report(args.query, results, status)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report saved to: {output_path}")
    else:
        print(report)

    # Log activity
    log_search(args.query, provider_used, len(results), status)

    # Exit code
    sys.exit(0 if results else 1)


if __name__ == '__main__':
    main()
