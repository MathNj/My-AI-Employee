#!/usr/bin/env python3
"""
Xero OAuth 2.0 Authentication Helper
Completes the OAuth flow and saves the token for the watcher to use.
"""

import json
from pathlib import Path
from xero.auth import OAuth2Credentials
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

CREDENTIALS_DIR = Path(__file__).parent / "credentials"
CREDENTIALS_FILE = CREDENTIALS_DIR / "xero_credentials.json"
TOKEN_FILE = CREDENTIALS_DIR / "xero_token.json"

# Global to store the authorization code
auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    """Handle the OAuth callback"""

    def do_GET(self):
        global auth_code

        # Parse the callback URL
        query_components = parse_qs(urlparse(self.path).query)

        if 'code' in query_components:
            auth_code = query_components['code'][0]

            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                <h1>Authentication Successful!</h1>
                <p>You can close this window and return to the terminal.</p>
                </body>
                </html>
            """)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
                <html>
                <body>
                <h1>Authentication Failed</h1>
                <p>No authorization code received.</p>
                </body>
                </html>
            """)

    def log_message(self, format, *args):
        """Suppress log messages"""
        pass


def main():
    """Run Xero OAuth authentication flow"""
    print("=" * 70)
    print("Xero OAuth 2.0 Authentication")
    print("=" * 70)

    # Load credentials
    if not CREDENTIALS_FILE.exists():
        print(f"Error: Credentials file not found at {CREDENTIALS_FILE}")
        print("Please create xero_credentials.json with your client_id and client_secret")
        return

    with open(CREDENTIALS_FILE, 'r') as f:
        creds_data = json.load(f)

    client_id = creds_data['client_id']
    client_secret = creds_data['client_secret']
    redirect_uri = creds_data.get('redirect_uri', 'http://localhost:8080')

    print(f"\nClient ID: {client_id[:20]}...")
    print(f"Redirect URI: {redirect_uri}")

    # Create OAuth2 credentials
    credentials = OAuth2Credentials(
        client_id=client_id,
        client_secret=client_secret,
        callback_uri=redirect_uri,
        scope='accounting.transactions accounting.settings'
    )

    # Generate authorization URL
    auth_url = credentials.generate_url()

    print("\n" + "=" * 70)
    print("STEP 1: Authorize Xero Access")
    print("=" * 70)
    print("\nOpening browser for authorization...")
    print(f"\nIf the browser doesn't open, visit this URL:")
    print(f"\n{auth_url}\n")

    # Open browser
    webbrowser.open(auth_url)

    print("=" * 70)
    print("STEP 2: Waiting for callback...")
    print("=" * 70)
    print("\nStarting local server on http://localhost:8080")
    print("Please complete the authorization in your browser...")

    # Try to start callback server, or fall back to manual entry
    try:
        server = HTTPServer(('localhost', 8080), CallbackHandler)
        print("\n✓ Callback server started successfully")

        # Wait for one request (the callback)
        server.handle_request()

        if not auth_code:
            print("\nError: No authorization code received!")
            return

        print(f"\n✓ Received authorization code: {auth_code[:20]}...")

    except Exception as e:
        print(f"\nCouldn't start callback server: {e}")
        print("\n" + "=" * 70)
        print("MANUAL CODE ENTRY MODE")
        print("=" * 70)
        print("\nAfter authorizing in the browser, you'll be redirected to:")
        print("http://localhost:8080/?code=XXXXX&...")
        print("\nCopy the 'code' parameter from the URL and paste it below:")
        auth_code = input("\nAuthorization code: ").strip()

        if not auth_code:
            print("\nError: No code entered!")
            return

    # Exchange code for token
    print("\n=" * 70)
    print("STEP 3: Exchanging code for access token...")
    print("=" * 70)

    try:
        credentials.verify(auth_code)
        token = credentials.token

        print(f"\n✓ Access token received!")
        print(f"  Expires in: {token.get('expires_in', 'N/A')} seconds")

        # Save token
        with open(TOKEN_FILE, 'w') as f:
            json.dump(token, f, indent=2)

        print(f"\n✓ Token saved to: {TOKEN_FILE}")

        print("\n" + "=" * 70)
        print("SUCCESS! Xero authentication complete")
        print("=" * 70)
        print("\nYou can now run the Xero watcher:")
        print("  python watchers/xero_watcher.py")

    except Exception as e:
        print(f"\nError exchanging code for token: {e}")
        return


if __name__ == "__main__":
    main()
