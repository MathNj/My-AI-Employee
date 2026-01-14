# Platform Setup Guide

Complete setup instructions for all social media platforms.

## LinkedIn (Already Configured)

✅ LinkedIn MCP server already installed and configured

**Verify Setup:**
```bash
# Check LinkedIn MCP in Claude Code config
cat ~/.config/claude-code/mcp.json | grep linkedin
```

**Test Connection:**
```bash
python scripts/test_connections.py --platform linkedin
```

---

## Facebook Setup

### Prerequisites

- Facebook Business Page (not personal profile)
- Meta Developer account
- Facebook App created

### Step 1: Create Meta Developer App

1. Visit https://developers.facebook.com/
2. Click "My Apps" → "Create App"
3. Select "Business" type
4. App name: "Personal AI Employee"
5. Contact email: your email
6. Click "Create App"

### Step 2: Configure App

1. **Add Facebook Login product:**
   - Dashboard → Add Product → Facebook Login
   - Settings → Valid OAuth Redirect URIs: `http://localhost:8080/callback`

2. **Add Required Permissions:**
   - `pages_manage_posts` - Post to pages
   - `pages_read_engagement` - Read analytics
   - `pages_show_list` - List your pages

3. **Get App Credentials:**
   - Settings → Basic
   - Copy App ID
   - Copy App Secret

### Step 3: Install Meta MCP Server

**Build from source** (Meta MCP doesn't exist yet):

```bash
cd ~/mcp-servers
mkdir meta-mcp
cd meta-mcp
npm init -y
npm install @modelcontextprotocol/sdk axios
```

Create `index.js` following the pattern in `references/meta_mcp_code.md`

### Step 4: Configure Environment

Add to `.env`:
```bash
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_REDIRECT_URI=http://localhost:8080/callback
META_PAGE_ID=your_facebook_page_id
```

### Step 5: Configure Claude Code

Edit `~/.config/claude-code/mcp.json`:
```json
{
  "mcpServers": {
    "meta": {
      "command": "node",
      "args": ["/path/to/meta-mcp/index.js"],
      "env": {
        "META_APP_ID": "${META_APP_ID}",
        "META_APP_SECRET": "${META_APP_SECRET}"
      }
    }
  }
}
```

### Step 6: Authenticate

```bash
python scripts/authenticate_meta.py
```

This opens browser for:
1. Facebook login
2. Grant permissions to app
3. Select page to manage
4. Save access token

**Setup Time:** 30-45 minutes

---

## Instagram Setup

Instagram uses the same Meta MCP server as Facebook.

### Prerequisites

- Instagram Business Account (not personal)
- Instagram account connected to Facebook Page
- Meta Developer App (from Facebook setup)

### Step 1: Connect Instagram to Facebook

1. Instagram app → Settings → Account
2. Switch to Professional Account → Business
3. Connect to Facebook Page

### Step 2: Add Instagram Permissions

In Meta Developer App:
1. Dashboard → Instagram Basic Display
2. Add permissions:
   - `instagram_basic`
   - `instagram_content_publish`

### Step 3: Get Instagram Business Account ID

```bash
# Via Graph API Explorer
https://developers.facebook.com/tools/explorer/

# Query: me/accounts
# Find your page → instagram_business_account → id
```

Add to `.env`:
```bash
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
```

**Setup Time:** 15-20 minutes (after Facebook setup)

---

## Twitter/X Setup

### Prerequisites

- Twitter/X account (can be personal or business)
- X Developer account
- Elevated API access (free tier available)

### Step 1: Create X Developer Account

1. Visit https://developer.twitter.com/
2. Sign up with Twitter account
3. Verify email
4. Complete developer questionnaire:
   - Use case: "Business automation and social media management"
   - No automation of engagement (likes/follows)
   - Posting original content only

### Step 2: Create App

1. Developer Portal → Projects & Apps
2. Create new App
3. App name: "Personal AI Employee"
4. Get credentials:
   - API Key (Consumer Key)
   - API Secret (Consumer Secret)

### Step 3: Enable OAuth 2.0

1. App Settings → User Authentication Settings
2. Enable OAuth 2.0
3. Type: Web App
4. Callback URL: `http://localhost:8080/callback`
5. Website URL: `http://localhost:8080`
6. Permissions:
   - Read and Write
   - Direct Messages (optional)

### Step 4: Install X MCP Server

**Build from source** (X MCP doesn't exist yet):

```bash
cd ~/mcp-servers
mkdir x-mcp
cd x-mcp
npm init -y
npm install @modelcontextprotocol/sdk twitter-api-v2
```

Create `index.js` following the pattern in `references/x_mcp_code.md`

### Step 5: Configure Environment

Add to `.env`:
```bash
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_secret
```

### Step 6: Configure Claude Code

Edit `~/.config/claude-code/mcp.json`:
```json
{
  "mcpServers": {
    "x": {
      "command": "node",
      "args": ["/path/to/x-mcp/index.js"],
      "env": {
        "X_API_KEY": "${X_API_KEY}",
        "X_API_SECRET": "${X_API_SECRET}"
      }
    }
  }
}
```

### Step 7: Authenticate

```bash
python scripts/authenticate_x.py
```

**Setup Time:** 30-40 minutes

---

## Testing All Platforms

Once all platforms configured:

```bash
# Test all connections
python scripts/test_connections.py --all

# Test individual platform
python scripts/test_connections.py --platform facebook
python scripts/test_connections.py --platform instagram
python scripts/test_connections.py --platform twitter
```

Expected output:
```
✓ LinkedIn: Connected (using existing MCP)
✓ Facebook: Connected (Page: Your Business Name)
✓ Instagram: Connected (Account: @yourbusiness)
✓ Twitter/X: Connected (@yourhandle)

All platforms ready!
```

---

## Summary

**Total Setup Time:** 1.5 - 2 hours

| Platform | Setup Time | MCP Status | Difficulty |
|----------|-----------|-----------|------------|
| LinkedIn | ✅ Done | ✅ Existing | Easy |
| Facebook | 30-45 min | ❌ Build needed | Medium |
| Instagram | 15-20 min | ❌ Build needed | Easy (uses Meta MCP) |
| Twitter/X | 30-40 min | ❌ Build needed | Medium |

**MCP Build Time:**
- Meta MCP: 3-4 hours
- X MCP: 2-3 hours

---

## Troubleshooting

**Facebook: "Invalid OAuth redirect URI"**
- Check redirect URI exactly matches in app settings
- Must be `http://localhost:8080/callback`

**Instagram: "Account not found"**
- Ensure Instagram is Business Account
- Verify connected to Facebook Page
- Check Instagram Account ID correct

**Twitter: "Read-only application cannot POST"**
- App permissions must be "Read and Write"
- Regenerate access tokens after changing permissions

**All Platforms: "Authentication failed"**
- Check credentials in `.env`
- Verify no extra spaces in values
- Restart Claude Code after config changes
