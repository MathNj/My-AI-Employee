#!/usr/bin/env python3
"""
Brave Search Integration

Integrates with Brave Search API for web research.

Setup:
    1. Get API key from https://brave.com/search/api/
    2. Save to watchers/credentials/brave_api.json:
       {
         "api_key": "your-brave-api-key"
       }

Usage:
    from brave_search import search_brave
    results = search_brave("Python async programming", max_results=5)
"""

import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional


# Credentials path
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()
CREDENTIALS_PATH = VAULT_PATH / "watchers" / "credentials" / "brave_api.json"

# Brave Search API endpoint
BRAVE_API_URL = "https://api.search.brave.com/res/v1/web/search"


def load_api_key() -> Optional[str]:
    """Load Brave API key from credentials file."""
    try:
        if not CREDENTIALS_PATH.exists():
            print(f"Credentials file not found: {CREDENTIALS_PATH}")
            print("Create file with: {\"api_key\": \"your-brave-api-key\"}")
            return None

        with open(CREDENTIALS_PATH, 'r', encoding='utf-8') as f:
            creds = json.load(f)

        api_key = creds.get('api_key')
        if not api_key:
            print("API key not found in credentials file")
            return None

        return api_key

    except Exception as e:
        print(f"Error loading API key: {e}")
        return None


def search_brave(query: str, max_results: int = 3,
                country: str = 'US', language: str = 'en') -> List[Dict]:
    """
    Search using Brave Search API.

    Args:
        query: Search query
        max_results: Maximum number of results to return
        country: Country code (default: US)
        language: Language code (default: en)

    Returns:
        List of search results with title, url, description
    """
    api_key = load_api_key()
    if not api_key:
        raise ValueError("Brave API key not configured")

    # Prepare request
    headers = {
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip',
        'X-Subscription-Token': api_key
    }

    params = {
        'q': query,
        'count': max_results,
        'country': country,
        'search_lang': language,
        'safesearch': 'moderate',
        'text_decorations': False,
        'spellcheck': True
    }

    try:
        # Make API request
        response = requests.get(
            BRAVE_API_URL,
            headers=headers,
            params=params,
            timeout=10
        )

        # Check for errors
        if response.status_code == 401:
            raise ValueError("Invalid Brave API key")
        elif response.status_code == 429:
            raise ValueError("Brave API rate limit exceeded")
        elif response.status_code != 200:
            raise ValueError(f"Brave API error: {response.status_code}")

        # Parse response
        data = response.json()

        # Extract web results
        web_results = data.get('web', {}).get('results', [])

        # Format results
        formatted_results = []
        for result in web_results[:max_results]:
            formatted_results.append({
                'title': result.get('title', 'No title'),
                'url': result.get('url', ''),
                'description': result.get('description', ''),
                'published_date': result.get('age', None)
            })

        return formatted_results

    except requests.exceptions.Timeout:
        raise ValueError("Brave API request timed out")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Brave API request failed: {e}")
    except json.JSONDecodeError:
        raise ValueError("Invalid response from Brave API")


def main():
    """Test Brave Search integration."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python brave_search.py 'search query'")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    print(f"Searching Brave for: {query}")
    print()

    try:
        results = search_brave(query, max_results=5)

        print(f"Found {len(results)} results:")
        print()

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   {result['description'][:150]}...")
            print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
