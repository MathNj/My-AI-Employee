#!/usr/bin/env python3
"""
Tavily Search Integration

Integrates with Tavily Search API for AI-optimized web research.

Setup:
    1. Get API key from https://tavily.com/
    2. Save to watchers/credentials/tavily_api.json:
       {
         "api_key": "tvly-your-api-key"
       }

Usage:
    from tavily_search import search_tavily
    results = search_tavily("machine learning trends 2026", max_results=5)
"""

import os
import json
import requests
from pathlib import Path
from typing import List, Dict, Optional


# Credentials path
VAULT_PATH = Path(__file__).parent.parent.parent.parent.absolute()
CREDENTIALS_PATH = VAULT_PATH / "watchers" / "credentials" / "tavily_api.json"

# Tavily API endpoint
TAVILY_API_URL = "https://api.tavily.com/search"


def load_api_key() -> Optional[str]:
    """Load Tavily API key from credentials file."""
    try:
        if not CREDENTIALS_PATH.exists():
            print(f"Credentials file not found: {CREDENTIALS_PATH}")
            print("Create file with: {\"api_key\": \"tvly-your-api-key\"}")
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


def search_tavily(query: str, max_results: int = 3,
                 search_depth: str = 'basic',
                 include_answer: bool = False) -> List[Dict]:
    """
    Search using Tavily Search API.

    Args:
        query: Search query
        max_results: Maximum number of results (max 10)
        search_depth: 'basic' or 'advanced' (advanced uses more credits)
        include_answer: Whether to include AI-generated answer

    Returns:
        List of search results with title, url, description
    """
    api_key = load_api_key()
    if not api_key:
        raise ValueError("Tavily API key not configured")

    # Prepare request payload
    payload = {
        'api_key': api_key,
        'query': query,
        'max_results': min(max_results, 10),  # Tavily max is 10
        'search_depth': search_depth,
        'include_answer': include_answer,
        'include_raw_content': False,
        'include_images': False
    }

    try:
        # Make API request
        response = requests.post(
            TAVILY_API_URL,
            json=payload,
            timeout=15
        )

        # Check for errors
        if response.status_code == 401:
            raise ValueError("Invalid Tavily API key")
        elif response.status_code == 429:
            raise ValueError("Tavily API rate limit exceeded")
        elif response.status_code != 200:
            error_msg = response.json().get('error', 'Unknown error')
            raise ValueError(f"Tavily API error: {error_msg}")

        # Parse response
        data = response.json()

        # Extract results
        results = data.get('results', [])

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                'title': result.get('title', 'No title'),
                'url': result.get('url', ''),
                'description': result.get('content', ''),
                'score': result.get('score', 0),  # Tavily provides relevance score
                'published_date': result.get('published_date', None)
            })

        # If AI answer is included, add it as first result
        if include_answer and data.get('answer'):
            formatted_results.insert(0, {
                'title': 'AI-Generated Answer',
                'url': 'https://tavily.com',
                'description': data['answer'],
                'score': 1.0,
                'is_ai_answer': True
            })

        return formatted_results

    except requests.exceptions.Timeout:
        raise ValueError("Tavily API request timed out")
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Tavily API request failed: {e}")
    except json.JSONDecodeError:
        raise ValueError("Invalid response from Tavily API")


def main():
    """Test Tavily Search integration."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tavily_search.py 'search query'")
        sys.exit(1)

    query = ' '.join(sys.argv[1:])

    print(f"Searching Tavily for: {query}")
    print()

    try:
        results = search_tavily(query, max_results=5, include_answer=True)

        print(f"Found {len(results)} results:")
        print()

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")

            if result.get('is_ai_answer'):
                print(f"   ANSWER: {result['description']}")
            else:
                print(f"   Score: {result.get('score', 'N/A')}")
                print(f"   {result['description'][:150]}...")
            print()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
