#!/usr/bin/env python3
"""
Convert Gmail token.pickle (Python) to token.json (Node.js MCP server)
"""

import pickle
import json
import sys
from pathlib import Path

def convert_pickle_to_json(pickle_path, json_path):
    """Convert pickle token file to JSON format"""
    try:
        # Read pickle file
        with open(pickle_path, 'rb') as f:
            token_data = pickle.load(f)

        # Extract token info
        # The token object should have: token, refresh_token, token_uri, client_id, client_secret, scopes
        json_data = {
            'token': token_data.token,
            'refresh_token': token_data.refresh_token,
            'token_uri': token_data.token_uri,
            'client_id': token_data.client_id,
            'client_secret': token_data.client_secret,
            'scopes': token_data.scopes,
            'expiry': token_data.expiry.isoformat() if hasattr(token_data, 'expiry') else None
        }

        # Write JSON file
        with open(json_path, 'w') as f:
            json.dump(json_data, f, indent=2)

        print(f"OK - Successfully converted {pickle_path} to {json_path}")
        return True

    except Exception as e:
        print(f"ERROR - Error converting token: {e}")
        return False

if __name__ == '__main__':
    pickle_path = Path(__file__).parent.parent.parent / 'watchers' / 'credentials' / 'token.pickle'
    json_path = Path(__file__).parent / 'token.json'

    if not pickle_path.exists():
        print(f"ERROR - Pickle file not found: {pickle_path}")
        sys.exit(1)

    convert_pickle_to_json(pickle_path, json_path)
