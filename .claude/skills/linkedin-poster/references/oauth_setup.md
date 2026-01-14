# LinkedIn OAuth Setup Guide

Complete step-by-step guide for setting up LinkedIn OAuth authentication.

## Prerequisites

- LinkedIn account
- Verified email address
- LinkedIn Page (personal or company) for app association

## Step 1: Create LinkedIn Developer Account

1. Visit https://www.linkedin.com/developers/
2. Sign in with your LinkedIn account
3. Accept Developer Terms of Service

## Step 2: Create LinkedIn App

1. Click **"Create app"** button
2. Fill in required information:
   - **App name:** Personal AI Employee (or your choice)
   - **LinkedIn Page:** Select your personal or company page
   - **Privacy policy URL:** (optional for development)
   - **App logo:** (optional, recommended for branding)
3. Check the box to agree to API Terms of Use
4. Click **"Create app"**

## Step 3: Configure App Settings

### Auth Tab

1. Go to **Auth** tab
2. Find **OAuth 2.0 settings** section
3. Under **Redirect URLs**, click **"Add redirect URL"**
4. Enter: `http://localhost:8080/callback`
5. Click **"Update"**

### Products Tab

1. Go to **Products** tab
2. Find **"Share on LinkedIn"** product
3. Click **"Request access"**
4. Fill out the form explaining your use case:
   ```
   Use Case: Personal AI Employee automation system that will
   post business updates, achievements, and thought leadership
   content to LinkedIn on behalf of the authenticated user.
   Posts will go through human approval before publishing.
   ```
5. Submit request
6. **Note:** Approval can take 24-48 hours for first-time apps

## Step 4: Get API Credentials

1. Go back to **Auth** tab
2. Find **Application credentials** section
3. Copy the **Client ID**
4. Click **"Show"** next to Client Secret
5. Copy the **Client Secret**
6. **Important:** Keep these secret and never commit to Git!

## Step 5: Store Credentials Locally

### Method 1: Using validation script (recommended)

```bash
python .claude/skills/linkedin-poster/scripts/validate_credentials.py --setup
```

This will prompt you to enter:
- Client ID
- Client Secret

And automatically save them to the correct location.

### Method 2: Manual setup

Create file: `watchers/credentials/linkedin_credentials.json`

```json
{
  "client_id": "your_client_id_here",
  "client_secret": "your_client_secret_here",
  "redirect_uri": "http://localhost:8080/callback",
  "scopes": ["w_member_social", "r_liteprofile"]
}
```

Replace `your_client_id_here` and `your_client_secret_here` with actual values.

## Step 6: Authenticate

Run the OAuth flow to get your access token:

```bash
python .claude/skills/linkedin-poster/scripts/linkedin_post.py --authenticate
```

This will:
1. Start a local server on port 8080
2. Open your browser to LinkedIn authorization page
3. Ask you to authorize the app
4. Redirect back to localhost with authorization code
5. Exchange code for access token
6. Save token for future use

## Step 7: Test Connection

Verify everything works:

```bash
python .claude/skills/linkedin-poster/scripts/test_connection.py
```

Expected output:
```
1. Testing credentials file...
   ✅ Credentials file found and valid
2. Testing OAuth token...
   ✅ Token found and valid
   ℹ️  Expires in 60 days
3. Testing API connection...
   ✅ API connection successful
   ℹ️  Connected as: Your Name
4. Testing post permissions...
   ✅ Post permissions check passed
```

## OAuth Scopes Explained

### w_member_social
- **Purpose:** Write access to member's social activity
- **Required for:** Creating posts on user's behalf
- **Permissions:** Post text, images, articles to profile

### r_liteprofile
- **Purpose:** Read basic profile information
- **Required for:** Getting user ID for post authorship
- **Permissions:** Read name, profile picture, user ID

## Token Lifecycle

### Access Token
- **Lifespan:** 60 days by default
- **Storage:** `watchers/credentials/linkedin_token.json`
- **Refresh:** Re-authenticate when expired

### When Tokens Expire
You'll see error: `Token expired or invalid`

Fix by re-authenticating:
```bash
python linkedin_post.py --authenticate
```

## Security Best Practices

### DO:
- ✅ Store credentials in `watchers/credentials/` (protected by .gitignore)
- ✅ Use environment variables in production
- ✅ Rotate credentials every 6 months
- ✅ Limit app scope to only what's needed
- ✅ Review LinkedIn audit log regularly

### DON'T:
- ❌ Commit credentials to Git
- ❌ Share credentials via email/chat
- ❌ Use production credentials for testing
- ❌ Grant more permissions than needed
- ❌ Store credentials in plain text on servers

## Troubleshooting

### "App not verified" Warning

When you first authenticate, you may see:
```
This app hasn't been verified by LinkedIn
```

**Solution:** Click "Advanced" → "Proceed to app"

This is normal for personal apps. For production apps, submit for LinkedIn verification.

### "Redirect URI Mismatch"

Error: `The redirect_uri does not match a registered application redirect URI`

**Solution:**
1. Check app settings → Auth tab
2. Ensure redirect URL is exactly: `http://localhost:8080/callback`
3. No trailing slash, exact port number
4. Protocol must be `http` for localhost

### "Insufficient Permissions"

Error: `The token does not have the required scope`

**Solution:**
1. Go to app → Products tab
2. Ensure "Share on LinkedIn" is approved
3. Wait 24-48 hours if just requested
4. Re-authenticate after approval

### Port 8080 Already in Use

Error: `Address already in use: ('localhost', 8080)`

**Solution:**
1. Find process using port 8080: `lsof -i :8080` (Mac/Linux) or `netstat -ano | findstr :8080` (Windows)
2. Kill the process
3. Or change redirect URI to different port (must update in app settings too)

### Token File Corrupted

Error: `Error reading token: Expecting value`

**Solution:**
```bash
# Remove token file
rm watchers/credentials/linkedin_token.json

# Re-authenticate
python linkedin_post.py --authenticate
```

## Rate Limits

LinkedIn API rate limits:
- **Posts per day:** 100 per member
- **API calls:** 100 per day per user
- **Burst limit:** 20 calls per 10 seconds

For this use case (a few posts per day), limits are not a concern.

## Production Considerations

### For Live Deployment

1. **Credentials Management:**
   - Use environment variables
   - Consider AWS Secrets Manager or similar
   - Never store in code repository

2. **Token Refresh:**
   - Implement automatic token refresh
   - Alert on expiration
   - Graceful degradation if auth fails

3. **Error Handling:**
   - Retry with exponential backoff
   - Log all API errors
   - Human notification on repeated failures

4. **Monitoring:**
   - Track successful posts
   - Monitor API rate limits
   - Alert on authentication failures

## Additional Resources

- [LinkedIn OAuth Documentation](https://learn.microsoft.com/en-us/linkedin/shared/authentication/authentication)
- [Share on LinkedIn API](https://learn.microsoft.com/en-us/linkedin/consumer/integrations/self-serve/share-on-linkedin)
- [LinkedIn API Best Practices](https://learn.microsoft.com/en-us/linkedin/shared/api-guide/best-practices)

## Support

If you encounter issues:

1. Check LinkedIn Developer Portal for API status
2. Review error messages in logs: `Logs/linkedin_activity_*.json`
3. Test connection: `python test_connection.py --verbose`
4. Re-authenticate: `python linkedin_post.py --authenticate`
5. Verify app settings in LinkedIn Developer Portal

---

**Setup Complete!** You're now ready to post to LinkedIn via the API.

Next: Create your first post with `python generate_post.py --list-templates`
