#!/bin/bash
# Odoo Community Initialization Script
# This script sets up Odoo Community with Accounting module and generates API key

set -e

# Configuration
ODOO_CONTAINER="odoo"
ODOO_ADMIN_PASSWORD="admin"
ODOO_DB="ai_employee"
ODOO_COUNTRY="US"
ODOO_PHONE=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Wait for PostgreSQL to be ready
log "Waiting for PostgreSQL..."
until docker exec odoo-postgres pg_isready; do
    sleep 1
done

# Initialize Odoo database
log "Initializing Odoo database..."
docker exec -u postgres odoo odoo --init --stop-after-init
log "Database initialized"

# Generate API key for automated integration
log "Generating API key..."

# We'll use Python script to generate API key via Odoo RPC
cat > /tmp/generate_api_key.py << 'EOF'
import requests
import sys

# Configuration
ODOO_URL = "http://localhost:8069"
ODOO_DB = "odoo"
ODOO_ADMIN_USER = "admin"
ODOO_ADMIN_PASSWORD = "admin"

def get_uid():
    """Get user ID via common API"""
    response = requests.post(f"{ODOO_URL}/web/session/authenticate", json={
        "db": ODOO_DB,
        "login": ODOO_ADMIN_USER,
        "password": ODOO_ADMIN_PASSWORD
    })

    if response.status_code != 200:
        print(f"Failed to authenticate: {response.status_code}")
        sys.exit(1)

    data = response.json()
    return data["uid"]

def create_api_key():
    """Create API key via RPC"""
    import xmlrpc.client

    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = get_uid()

    # Get current user
    user_obj = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
    users = user_obj.execute_kw(
        ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
        'res.users', 'search_read',
        [[['id', '=', uid]],
        {'fields': ['id', 'name']}
    )

    if users and len(users) > 0:
        user_data = users[0]
        user_id = user_data['id']

        # Create API key via RPC
        key_obj = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
        key_id = key_obj.execute_kw(
            ODOO_DB, uid, ODOO_ADMIN_PASSWORD,
            'res.users.apikeys', 'create',
            [{
                'name': 'AI Employee MCP Integration',
                'user_id': user_id,
                'duration': 90  # 90 days
            }]
        )

        # Retrieve key value
        key = key_obj.execute_kw(
            ODOO_DB, uid, ODOO_PASSWORD,
            'res.users.apikeys', 'read',
            [[['id', '=', key_id]],
            {'fields': ['key']}
        )

        return key[0]['key']

    print("\n✅ API Key generated successfully!")
    return key

if __name__ == '__main__':
    print("=" * 60)
    print("Odoo API Key Generator")
    print("=" * 60)
    print()

    key = create_api_key()

    print("\n⚠️  IMPORTANT: Copy this key now! It won't be shown again!")
    print()
    print(f"API_KEY={key}")
    print()
    print("=" * 60)
    print("Configuration Instructions:")
    print("=" * 60)
    print()
    print("1. Copy the API key above")
    print("2. Add to .env file:")
    print(f"   ODOO_API_KEY={key}")
    print("3. Restart Odoo container to apply changes")
    print()
    print("=" * 60)
EOF

# Run the Python script
docker exec odoo python3 /tmp/generate_api_key.py

# Wait for user to copy API key
log ""
log "📝 Copy the API key above before proceeding..."
log "Press Enter once you've saved the API key to .env file"
read -p

# Stop Odoo for environment variable updates
log "Restarting Odoo to apply environment variable..."
docker-compose restart odoo

log "Waiting for Odoo to start..."
sleep 10

log "=" * 60
log "Odoo Community Installation Complete!"
log "=" * 60
log ""
log "Next Steps:"
log "1. Copy the API key and add to .env file: ODOO_API_KEY=<your-api-key>"
log "2. Run: pip install -r watchers/requirements.txt"
log "3. Run: python watchers/odoo_watcher.py"
log "4. Test the JSON-2 API connection"
log ""
log "=" * 60
log "Odoo Web Interface:"
log "http://localhost:8069"
log "Username: admin"
log "Password: admin"
log "=" * 60
