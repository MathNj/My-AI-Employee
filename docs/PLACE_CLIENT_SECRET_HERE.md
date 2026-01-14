# 📍 Where to Place Your client_secret.json

## Quick Instructions

You mentioned you have a `client_secret.json` file. Here's where to place it:

### Option 1: Recommended Location (Organized)
```
watchers/credentials/credentials.json
```

**Steps:**
1. Move/copy your `client_secret.json` to `watchers/credentials/`
2. Rename it to `credentials.json`

```bash
# Windows
move client_secret.json watchers\credentials\credentials.json

# Linux/Mac
mv client_secret.json watchers/credentials/credentials.json
```

### Option 2: Keep Original Name (Also Works)
```
watchers/credentials/client_secret.json
```

**Steps:**
1. Move/copy your `client_secret.json` to `watchers/credentials/`
2. Keep the original name
3. Update the watcher to use this filename

```bash
# Windows
move client_secret.json watchers\credentials\

# Linux/Mac
mv client_secret.json watchers/credentials/
```

Then run:
```bash
python watchers/gmail_watcher.py watchers/credentials/client_secret.json
```

### Option 3: Current Folder (Quick Testing)
If you place it in the vault root folder, it will also be protected:

```
AI_Employee_Vault/
├── client_secret.json  ← Here (protected by .gitignore)
└── ...
```

**Note:** The Gmail watcher by default looks in `watchers/credentials/credentials.json`, so you'll need to specify the path:

```bash
python watchers/gmail_watcher.py ./client_secret.json
```

## Git Protection ✅

Your `client_secret.json` is now protected by `.gitignore`:

```gitignore
# These patterns are ignored (won't be committed to Git)
client_secret*.json        ← Your file
credentials.json
token.pickle
watchers/credentials/*.json
watchers/credentials/*.pickle
```

**Verification:**
```bash
# Check if file would be ignored by Git
git check-ignore -v client_secret.json

# Should output: .gitignore:9:client_secret*.json
```

## What Happens After You Place It

1. **Place file** in `watchers/credentials/` as `credentials.json`

2. **Run Gmail watcher:**
   ```bash
   python watchers/gmail_watcher.py
   ```

3. **Browser opens** for OAuth2 authentication

4. **Grant permissions** (read-only Gmail access)

5. **`token.pickle` created** automatically (also protected)

6. **Watcher starts** monitoring Gmail

## File Structure After Setup

```
watchers/credentials/
├── README.md              ✅ Already created
├── credentials.json       ⏳ You'll place this
└── token.pickle          ⏳ Auto-created after auth
```

All files protected by .gitignore ✅

## Quick Commands

**After placing the file, verify:**
```bash
# Check file exists
ls watchers/credentials/credentials.json

# Check it's ignored by Git
git check-ignore watchers/credentials/credentials.json

# Test the watcher
python watchers/gmail_watcher.py
```

## Security Checklist

- [x] `.gitignore` updated to protect credentials
- [x] `client_secret*.json` pattern added
- [x] `credentials.json` pattern added
- [x] `token.pickle` pattern added
- [x] `watchers/credentials/` folder protected
- [ ] Place your `client_secret.json` file
- [ ] Run first authentication
- [ ] Verify `token.pickle` created
- [ ] Test Gmail watcher

## Need Help?

See the complete setup guide:
```bash
cat watchers/GMAIL_SETUP.md
```

Or the credentials folder guide:
```bash
cat watchers/credentials/README.md
```

---

**🎯 Recommended Action:**

```bash
# If client_secret.json is in the current directory:
move client_secret.json watchers\credentials\credentials.json

# Then run:
python watchers/gmail_watcher.py
```

**Status:** Ready to authenticate!
