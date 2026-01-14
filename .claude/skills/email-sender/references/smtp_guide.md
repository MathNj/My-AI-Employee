# SMTP Configuration Guide

Complete guide for setting up SMTP email sending.

## Gmail Setup (Recommended)

### Step 1: Enable 2-Factor Authentication

1. Go to: https://myaccount.google.com/security
2. Under "Signing in to Google", enable "2-Step Verification"
3. Complete the setup process

### Step 2: Create App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Select app: "Mail"
3. Select device: "Other (Custom name)"
4. Enter: "Personal AI Employee"
5. Click "Generate"
6. **Copy the 16-character password** (you won't see it again)

### Step 3: Configure SMTP

Create `watchers/credentials/smtp_config.json`:

```json
{
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "email_address": "your-email@gmail.com",
  "email_password": "your-app-password-here",
  "use_tls": true
}
```

Replace:
- `your-email@gmail.com` - Your Gmail address
- `your-app-password-here` - The 16-character app password

### Step 4: Test Connection

```bash
python .claude/skills/email-sender/scripts/test_email.py
```

Expected output:
```
1. Testing SMTP configuration...
   ✅ SMTP configuration found
2. Testing SMTP connection...
   ✅ SMTP connection test passed
```

## Other Email Providers

### Outlook/Office 365

```json
{
  "smtp_server": "smtp-mail.outlook.com",
  "smtp_port": 587,
  "email_address": "your-email@outlook.com",
  "email_password": "your-password",
  "use_tls": true
}
```

### Yahoo Mail

```json
{
  "smtp_server": "smtp.mail.yahoo.com",
  "smtp_port": 465,
  "email_address": "your-email@yahoo.com",
  "email_password": "your-app-password",
  "use_tls": false
}
```

Note: Yahoo also requires app password.

### Custom SMTP Server

```json
{
  "smtp_server": "mail.yourdomain.com",
  "smtp_port": 587,
  "email_address": "you@yourdomain.com",
  "email_password": "your-password",
  "use_tls": true
}
```

## Common Issues

### "Authentication Failed"

**For Gmail:**
- Use app password, not regular password
- Enable 2FA first
- Verify email address is correct

**For other providers:**
- Check if app passwords required
- Verify SMTP server and port
- Test credentials manually

### "Connection Refused"

- Check firewall settings
- Verify SMTP port (usually 587 or 465)
- Try alternative port if blocked

### "TLS Error"

- Try setting `use_tls` to `false`
- Or change port to 465 (SSL)

## Security Best Practices

1. **Use app passwords** (never regular passwords)
2. **Store in credentials directory** (protected by .gitignore)
3. **Rotate passwords** every 6 months
4. **Revoke if compromised**
5. **One app password per application**

## Testing

```bash
# Test configuration
python scripts/test_email.py

# Send test email
python scripts/test_email.py --send-test --to "your-email@example.com"
```

---

**Setup Complete!** You can now send emails via SMTP.
