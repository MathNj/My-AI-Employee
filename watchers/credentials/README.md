# Gmail API Credentials Folder

This folder stores your Gmail API OAuth2 credentials.

## Required Files

### 1. credentials.json (or client_secret*.json)
**Source:** Downloaded from Google Cloud Console
**Setup:** Follow instructions in `../GMAIL_SETUP.md`
**Contains:** OAuth2 client ID and secret
**Security:** Protected by .gitignore - NEVER commit to Git

**Place your downloaded client_secret.json here and rename it to:**
- `credentials.json` (recommended)
- Or keep as `client_secret_*.json`

### 2. token.pickle (auto-generated)
**Created:** Automatically on first authentication
**Contains:** Your authenticated session token
**Security:** Protected by .gitignore - NEVER commit to Git
**Lifetime:** Refreshed automatically when expired

## Setup Instructions

1. **Download OAuth2 Credentials:**
   - Go to Google Cloud Console
   - Enable Gmail API
   - Create OAuth2 credentials (Desktop app)
   - Download the JSON file

2. **Place File Here:**
   ```
   watchers/credentials/
   ├── credentials.json        ← Your downloaded file (rename if needed)
   └── token.pickle            ← Auto-created on first run
   ```

3. **First Run:**
   ```bash
   python watchers/gmail_watcher.py
   ```
   Browser will open for authentication.

4. **Verify:**
   ```bash
   ls watchers/credentials/
   ```
   You should see both files.

## Security Notes

✅ **Protected by .gitignore**
All files in this folder are automatically excluded from Git commits.

✅ **Local Only**
These credentials are stored locally on your machine only.

✅ **Revocable**
You can revoke access anytime at: https://myaccount.google.com/permissions

## File Patterns Protected

The following patterns are ignored by Git:
- `client_secret*.json` (anywhere in vault)
- `credentials.json` (anywhere in vault)
- `token.pickle` (anywhere in vault)
- `watchers/credentials/*.json`
- `watchers/credentials/*.pickle`

## Troubleshooting

**File not found error?**
- Ensure file is named `credentials.json` or update path in `gmail_watcher.py`
- Check file is in this exact folder

**Permission errors?**
- File should be readable by your user account
- No special permissions needed

**Need to re-authenticate?**
```bash
# Delete token and re-run
rm watchers/credentials/token.pickle
python watchers/gmail_watcher.py
```

## What NOT to Do

❌ **NEVER commit these files to Git**
❌ **NEVER share these files publicly**
❌ **NEVER email or message these files**
❌ **NEVER upload to cloud storage**

## What TO Do

✅ **Keep these files in this folder**
✅ **Backup securely if needed (encrypted backup only)**
✅ **Revoke and regenerate if compromised**
✅ **Use different credentials for different projects**

---

**Current Status:**
- [ ] credentials.json placed in this folder
- [ ] token.pickle generated (after first run)
- [ ] Gmail watcher authenticated and working

**Next Steps:**
See `../GMAIL_SETUP.md` for complete setup instructions.
