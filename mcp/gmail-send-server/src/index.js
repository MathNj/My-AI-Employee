#!/usr/bin/env node
/**
 * MCP Gmail Send Server
 *
 * Model Context Protocol server for sending emails via Gmail API.
 * Implements Silver Tier tasks T046-T056.
 *
 * Provides the `send_email` tool that:
 * - Authenticates with Gmail API using OAuth2
 * - Sends emails with optional attachments
 * - Logs all operations to MCP server log
 * - Returns detailed success/error responses
 *
 * Usage:
 *   npm start              # Start MCP server on stdio
 *   npm run dev            # Start with file watch
 *   npm test               # Run integration test
 *
 * Environment Variables:
 *   GMAIL_CLIENT_ID       - Gmail OAuth2 client ID
 *   GMAIL_CLIENT_SECRET   - Gmail OAuth2 client secret
 *   GMAIL_REDIRECT_URI    - OAuth2 redirect URI (default: http://localhost:3000)
 *   GMAIL_TOKEN_PATH      - Path to save OAuth2 tokens (default: tokens/gmail-token.json)
 *   MCP_LOG_PATH          - Path to MCP log file (default: Logs/mcp_server.log)
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// ============================================================================
// Configuration
// ============================================================================

const CONFIG = {
  GMAIL_CLIENT_ID: process.env.GMAIL_CLIENT_ID || '',
  GMAIL_CLIENT_SECRET: process.env.GMAIL_CLIENT_SECRET || '',
  GMAIL_REDIRECT_URI: process.env.GMAIL_REDIRECT_URI || 'http://localhost:3000',
  GMAIL_TOKEN_PATH: process.env.GMAIL_TOKEN_PATH || path.join(process.cwd(), 'tokens', 'gmail-token.json'),
  MCP_LOG_PATH: process.env.MCP_LOG_PATH || path.join(process.cwd(), 'Logs', 'mcp_server.log'),
  SCOPES: ['https://www.googleapis.com/auth/gmail.send'],
};

// ============================================================================
// Logging
// ============================================================================

class MCPLogger {
  constructor(logPath) {
    this.logPath = logPath;
    this.logDir = path.dirname(logPath);
    this.ensureLogDirectory();
  }

  ensureLogDirectory() {
    if (!fs.existsSync(this.logDir)) {
      fs.mkdirSync(this.logDir, { recursive: true });
    }
  }

  log(level, message, metadata = {}) {
    const timestamp = new Date().toISOString();
    const logEntry = {
      timestamp,
      level,
      message,
      ...metadata,
    };

    const logLine = JSON.stringify(logEntry);

    // Write to file
    try {
      fs.appendFileSync(this.logPath, logLine + '\n');
    } catch (err) {
      console.error(`[ERROR] Failed to write to log: ${err.message}`);
    }

    // Also output to console
    console.log(`[${timestamp}] [${level}] ${message}`);
  }

  info(message, metadata) {
    this.log('INFO', message, metadata);
  }

  error(message, metadata) {
    this.log('ERROR', message, metadata);
  }

  warn(message, metadata) {
    this.log('WARN', message, metadata);
  }
}

const logger = new MCPLogger(CONFIG.MCP_LOG_PATH);

// ============================================================================
// Gmail OAuth2 Manager
// ============================================================================

class GmailAuthManager {
  constructor() {
    this.oauth2Client = new google.auth.OAuth2(
      CONFIG.GMAIL_CLIENT_ID,
      CONFIG.GMAIL_CLIENT_SECRET,
      CONFIG.GMAIL_REDIRECT_URI
    );
    this.gmail = null;
  }

  /**
   * Load existing tokens or authenticate
   * T049: Implement Gmail API integration
   */
  async authenticate() {
    // Try to load existing tokens
    if (fs.existsSync(CONFIG.GMAIL_TOKEN_PATH)) {
      try {
        const tokens = JSON.parse(fs.readFileSync(CONFIG.GMAIL_TOKEN_PATH, 'utf8'));
        this.oauth2Client.setCredentials(tokens);

        // Check if token is expired and refresh if needed
        if (tokens.expiry_date && tokens.expiry_date < Date.now()) {
          const { credentials } = await this.oauth2Client.refreshAccessToken();
          this.saveTokens(credentials);
          logger.info('Refreshed Gmail access token');
        } else {
          logger.info('Loaded existing Gmail tokens');
        }

        this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
        return true;
      } catch (err) {
        logger.error('Failed to load tokens', { error: err.message });
      }
    }

    // No valid tokens found
    logger.warn('No valid Gmail tokens found. Please run authentication flow.');
    return false;
  }

  /**
   * Save OAuth2 tokens to file
   */
  saveTokens(tokens) {
    const tokenDir = path.dirname(CONFIG.GMAIL_TOKEN_PATH);
    if (!fs.existsSync(tokenDir)) {
      fs.mkdirSync(tokenDir, { recursive: true });
    }
    fs.writeFileSync(CONFIG.GMAIL_TOKEN_PATH, JSON.stringify(tokens, null, 2));
    logger.info('Saved Gmail tokens', { path: CONFIG.GMAIL_TOKEN_PATH });
  }

  /**
   * Generate authentication URL for user to authorize
   */
  getAuthUrl() {
    return this.oauth2Client.generateAuthUrl({
      access_type: 'offline',
      scope: CONFIG.SCOPES,
    });
  }

  /**
   * Exchange authorization code for tokens
   */
  async getToken(code) {
    const { tokens } = await this.oauth2Client.getAccessToken(code);
    this.saveTokens(tokens);
    this.oauth2Client.setCredentials(tokens);
    this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
    return tokens;
  }

  /**
   * Check if authenticated
   */
  isAuthenticated() {
    return this.gmail !== null;
  }
}

// ============================================================================
// Email Sender
// ============================================================================

class EmailSender {
  constructor(authManager) {
    this.auth = authManager;
  }

  /**
   * Send email via Gmail API
   * T048: Define send_email tool
   * T049: Implement Gmail API integration
   * T050: Add error handling
   */
  async sendEmail(params) {
    const { to, subject, body, html, cc, bcc, attachments } = params;

    // Validate required parameters
    if (!to || !subject || (!body && !html)) {
      throw new Error('Missing required parameters: to, subject, and (body or html) are required');
    }

    logger.info('Sending email', { to, subject });

    try {
      // Build email
      const email = this.buildEmail({ to, subject, body, html, cc, bcc, attachments });

      // Encode to base64url
      const base64Email = Buffer.from(email)
        .toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=+$/, '');

      // Send via Gmail API
      const response = await this.auth.gmail.users.messages.send({
        userId: 'me',
        resource: {
          raw: base64Email,
        },
      });

      logger.info('Email sent successfully', {
        id: response.data.id,
        threadId: response.data.threadId,
        to,
        subject,
      });

      return {
        success: true,
        messageId: response.data.id,
        threadId: response.data.threadId,
        labelIds: response.data.labelIds,
      };

    } catch (error) {
      // T050: Add error handling
      logger.error('Failed to send email', {
        error: error.message,
        code: error.code,
        to,
        subject,
      });

      // Provide actionable error messages
      let errorMessage = error.message;

      if (error.code === 401) {
        errorMessage = 'Authentication failed. Please re-authenticate with Gmail.';
      } else if (error.code === 403) {
        errorMessage = 'Permission denied. Check Gmail API scopes.';
      } else if (error.code === 400) {
        errorMessage = 'Invalid request. Check email parameters.';
      }

      throw new Error(errorMessage);
    }
  }

  /**
   * Build RFC 2822 email message
   */
  buildEmail(params) {
    const { to, subject, body, html, cc, bcc, attachments } = params;

    let email = '';

    // Headers
    email += `To: ${to}\r\n`;
    email += `Subject: ${subject}\r\n`;

    if (cc) {
      email += `Cc: ${cc}\r\n`;
    }

    if (bcc) {
      email += `Bcc: ${bcc}\r\n`;
    }

    email += 'MIME-Version: 1.0\r\n';

    // Handle attachments
    if (attachments && attachments.length > 0) {
      const boundary = 'boundary_' + Date.now();
      email += `Content-Type: multipart/mixed; boundary="${boundary}"\r\n\r\n`;

      // Body part
      email += `--${boundary}\r\n`;
      if (html) {
        email += 'Content-Type: text/html; charset="UTF-8"\r\n\r\n';
        email += html + '\r\n';
      } else {
        email += 'Content-Type: text/plain; charset="UTF-8"\r\n\r\n';
        email += body + '\r\n';
      }

      // Attachment parts
      for (const attachment of attachments) {
        email += `--${boundary}\r\n`;
        email += `Content-Type: ${attachment.contentType || 'application/octet-stream'}; name="${attachment.filename}"\r\n`;
        email += 'Content-Transfer-Encoding: base64\r\n';
        email += `Content-Disposition: attachment; filename="${attachment.filename}"\r\n\r\n`;
        email += attachment.content + '\r\n';
      }

      email += `--${boundary}--\r\n`;
    } else {
      // Simple email without attachments
      if (html) {
        email += 'Content-Type: text/html; charset="UTF-8"\r\n\r\n';
        email += html;
      } else {
        email += 'Content-Type: text/plain; charset="UTF-8"\r\n\r\n';
        email += body;
      }
    }

    return email;
  }
}

// ============================================================================
// MCP Server
// ============================================================================

// T048: Define send_email tool
const SEND_EMAIL_TOOL: Tool = {
  name: 'send_email',
  description: 'Send an email via Gmail API. Supports plain text, HTML, CC, BCC, and file attachments.',
  inputSchema: {
    type: 'object',
    properties: {
      to: {
        type: 'string',
        description: 'Recipient email address (required)',
      },
      subject: {
        type: 'string',
        description: 'Email subject line (required)',
      },
      body: {
        type: 'string',
        description: 'Plain text email body (optional if html is provided)',
      },
      html: {
        type: 'string',
        description: 'HTML email body (optional if body is provided)',
      },
      cc: {
        type: 'string',
        description: 'CC recipient email address (optional)',
      },
      bcc: {
        type: 'string',
        description: 'BCC recipient email address (optional)',
      },
      attachments: {
        type: 'array',
        description: 'Array of file attachments (optional)',
        items: {
          type: 'object',
          properties: {
            filename: { type: 'string', description: 'Attachment filename' },
            content: { type: 'string', description: 'Base64-encoded file content' },
            contentType: { type: 'string', description: 'MIME type (e.g., application/pdf)' },
          },
          required: ['filename', 'content'],
        },
      },
    },
    required: ['to', 'subject'],
  },
};

// T047: Implement mcp/gmail-send-server/src/index.ts
async function main() {
  logger.info('Gmail Send MCP Server starting...');

  // Initialize authentication
  const authManager = new GmailAuthManager();
  const isAuthenticated = await authManager.authenticate();

  if (!isAuthenticated) {
    logger.error('Gmail authentication failed. Please set up OAuth2 credentials.');
    logger.info('To authenticate, visit:', authManager.getAuthUrl());
    process.exit(1);
  }

  // Initialize email sender
  const emailSender = new EmailSender(authManager);

  // Create MCP server
  const server = new Server(
    {
      name: 'gmail-send-server',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // Handle list tools request
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    logger.info('Listing available tools');
    return {
      tools: [SEND_EMAIL_TOOL],
    };
  });

  // Handle tool execution request
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;

    if (name === 'send_email') {
      try {
        logger.info('Executing send_email tool', args);
        const result = await emailSender.sendEmail(args);
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        logger.error('send_email tool failed', { error: error.message });
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                success: false,
                error: error.message,
              }),
            },
          ],
          isError: true,
        };
      }
    }

    return {
      content: [
        {
          type: 'text',
          text: `Unknown tool: ${name}`,
        },
      ],
      isError: true,
    };
  });

  // Start server on stdio
  const transport = new StdioServerTransport();
  await server.connect(transport);

  logger.info('Gmail Send MCP Server running on stdio');
  logger.info('Available tools: send_email');
}

// ============================================================================
// CLI Entry Point
// ============================================================================

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((err) => {
    logger.error('Server error', { error: err.message });
    console.error(err);
    process.exit(1);
  });
}

export { main, GmailAuthManager, EmailSender };
