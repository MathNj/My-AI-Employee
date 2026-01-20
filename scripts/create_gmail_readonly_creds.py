#!/usr/bin/env python3
"""
Gmail Read-Only Credentials Generator
Run this on your LOCAL machine to generate OAuth credentials for cloud deployment

Usage:
    python3 create_gmail_readonly_creds.py
"""

import os
import json
from pathlib import Path

def print_header():
    """Print instructions header"""
    print("=" * 70)
    print("Gmail Read-Only Credentials Generator")
    print("Platinum Tier Cloud Deployment")
    print("=" * 70)
    print()

def step_1_create_oauth_client():
    """Step 1: Create OAuth client"""
    print("STEP 1: Create OAuth 2.0 Client ID")
    print("-" * 70)
    print()
    print("1. Go to: https://console.cloud.google.com/apis/credentials")
    print("2. Select your project (or create a new one)")
    print("3. Click 'Create Credentials' → 'OAuth client ID'")
    print("4. Application type: Desktop app")
    print("5. Name: 'AI Employee Cloud - Read Only'")
    print("6. Click 'Create'")
    print("7. Download the JSON file")
    print()
    input("Press Enter once you've downloaded the JSON file...")
    print()

def step_2_configure_credentials():
    """Step 2: Configure credentials"""
    print("STEP 2: Configure Credentials for Read-Only Access")
    print("-" * 70)
    print()
    print("Rename your downloaded JSON file to: gmail_client_secret.json")
    print("Place it in the same directory as this script")
    print()
    input("Press Enter when ready...")
    print()

    # Check if file exists
    client_secret_path = Path("gmail_client_secret.json")
    if not client_secret_path.exists():
        print("ERROR: gmail_client_secret.json not found!")
        print("Please download the OAuth client JSON file and rename it.")
        return False

    print("✓ Client secret file found")
    print()
    return True

def step_3_generate_token():
    """Step 3: Generate OAuth token"""
    print("STEP 3: Generate OAuth Token (Read-Only)")
    print("-" * 70)
    print()
    print("This will open a browser window for OAuth authentication.")
    print("You'll be asked to grant read-only access to Gmail.")
    print()

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow

        # Load client secrets
        client_secret_path = Path("gmail_client_secret.json")
        flow = InstalledAppFlow.from_client_secrets_file(
            str(client_secret_path),
            scopes=['https://www.googleapis.com/auth/gmail.readonly']
        )

        print("Opening browser for authentication...")
        creds = flow.run_local_server(port=0)

        # Save credentials
        token_path = Path("gmail_token_readonly.json")
        with open(token_path, 'w') as f:
            f.write(creds.to_json())

        print()
        print("✓ Credentials saved to: gmail_token_readonly.json")
        print()
        return True

    except ImportError:
        print("ERROR: Required libraries not installed!")
        print()
        print("Install them with:")
        print("  pip install google-auth-oauthlib")
        print()
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def step_4_verify():
    """Step 4: Verify credentials"""
    print("STEP 4: Verify Credentials")
    print("-" * 70)
    print()

    token_path = Path("gmail_token_readonly.json")
    if not token_path.exists():
        print("ERROR: gmail_token_readonly.json not found!")
        return False

    with open(token_path) as f:
        creds = json.load(f)

    # Verify scopes
    scopes = creds.get('scopes', [])
    readonly_scope = 'https://www.googleapis.com/auth/gmail.readonly'

    print("Scopes in credentials:")
    for scope in scopes:
        status = "✓" if scope == readonly_scope else "⚠"
        print(f"  {status} {scope}")

    if readonly_scope in scopes:
        print()
        print("✓ Read-only scope verified!")
        print()
        return True
    else:
        print()
        print("ERROR: Read-only scope not found!")
        print()
        return False

def step_5_upload_instructions():
    """Step 5: Upload instructions"""
    print("STEP 5: Upload to Cloud VM")
    print("-" * 70)
    print()
    print("Your credentials are ready: gmail_token_readonly.json")
    print()
    print("To upload to the cloud VM:")
    print()
    print("1. Access your VM: https://console.ap-mumbai-1.oraclecloud.com")
    print("2. Navigate to: Compute → Instances → instance-20260121-0102")
    print("3. Click 'Connect' → 'Launch SSH Console'")
    print("4. In the SSH console, create the directory:")
    print("   mkdir -p /home/ubuntu/ai_employee/AI_Employee_Vault/credentials")
    print()
    print("5. Click the upload icon in the SSH console")
    print("6. Upload: gmail_token_readonly.json")
    print()
    print("7. Move it to the correct location:")
    print("   mv ~/gmail_token_readonly.json /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json")
    print()
    print("8. Set correct permissions:")
    print("   chmod 600 /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/gmail_readonly.json")
    print()
    print("9. Verify:")
    print("   ls -la /home/ubuntu/ai_employee/AI_Employee_Vault/credentials/")
    print()

def main():
    """Main workflow"""
    print_header()

    # Step 1
    step_1_create_oauth_client()

    # Step 2
    if not step_2_configure_credentials():
        return

    # Step 3
    if not step_3_generate_token():
        return

    # Step 4
    if not step_4_verify():
        return

    # Step 5
    step_5_upload_instructions()

    print("=" * 70)
    print("Setup Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Upload credentials to cloud VM (see Step 5 above)")
    print("2. Start cloud services:")
    print("   cd /home/ubuntu/ai_employee/AI_Employee_Vault")
    print("   ./scripts/start_cloud_services.sh")
    print("3. Test the workflow (send yourself an email)")
    print()
    print("For detailed instructions, see: CLOUD_SETUP_INSTRUCTIONS.md")
    print()

if __name__ == "__main__":
    main()
