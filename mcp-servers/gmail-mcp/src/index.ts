#!/usr/bin/env node

/**
 * Gmail MCP Server
 * Production-ready MCP server for Gmail with OAuth 2.0 and HITL approval workflow
 *
 * Features:
 * - OAuth 2.0 authentication with automatic token refresh
 * - Send, read, search, draft emails
 * - Human-in-the-Loop approval workflow integration
 * - Attachment support (invoices, reports, documents)
 * - Rate limiting and quota management
 * - Comprehensive error handling with retry logic
 * - Detailed audit logging (with PII redaction)
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import { google, gmail_v1 } from 'googleapis';
import { OAuth2Client } from 'google-auth-library';
import fs from 'fs/promises';
import path from 'path';
import { createLogger, format, transports } from 'winston';
import dotenv from 'dotenv';

dotenv.config();

// Configuration
const CONFIG = {
  vaultPath: process.env.VAULT_PATH || 'C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault',
  credentialsPath: process.env.GMAIL_CREDENTIALS_PATH || './credentials.json',
  tokenPath: process.env.GMAIL_TOKEN_PATH || './token.json',
  maxRetries: 3,
  retryDelay: 1000,
  rateLimit: {
    maxPerMinute: 60,
    maxPerDay: 10000,
  },
  autoApprove: {
    enabled: process.env.AUTO_APPROVE === 'true',
    maxRecipients: 1,
    knownContactsOnly: true,
  },
  logPath: process.env.LOG_PATH || './logs',
};

// Logger setup with PII redaction
const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.printf(({ timestamp, level, message, ...meta }) => {
      // Redact sensitive information
      const sanitized = JSON.stringify(meta).replace(
        /(token|password|secret|key)":"[^"]+"/gi,
        '$1":"***REDACTED***"'
      );
      return `${timestamp} [${level.toUpperCase()}] ${message} ${sanitized !== '{}' ? sanitized : ''}`;
    })
  ),
  transports: [
    new transports.Console(),
    new transports.File({
      filename: path.join(CONFIG.logPath, 'gmail-mcp-error.log'),
      level: 'error'
    }),
    new transports.File({
      filename: path.join(CONFIG.logPath, 'gmail-mcp.log')
    }),
  ],
});

// Gmail Client with OAuth 2.0
class GmailClient {
  private oauth2Client: OAuth2Client;
  private gmail: gmail_v1.Gmail | null = null;
  private requestCount = { minute: 0, day: 0 };
  private lastResetMinute = Date.now();
  private lastResetDay = Date.now();

  constructor() {
    this.oauth2Client = new google.auth.OAuth2(
      process.env.GMAIL_CLIENT_ID,
      process.env.GMAIL_CLIENT_SECRET,
      process.env.GMAIL_REDIRECT_URI || 'urn:ietf:wg:oauth:2.0:oob'
    );
  }

  async initialize(): Promise<void> {
    try {
      // Load token from file
      const tokenData = await fs.readFile(CONFIG.tokenPath, 'utf-8');
      const tokens = JSON.parse(tokenData);

      this.oauth2Client.setCredentials(tokens);

      // Check if token needs refresh
      if (tokens.expiry_date && tokens.expiry_date < Date.now()) {
        logger.info('Token expired, refreshing...');
        const { credentials } = await this.oauth2Client.refreshAccessToken();
        await this.saveToken(credentials);
        this.oauth2Client.setCredentials(credentials);
      }

      this.gmail = google.gmail({ version: 'v1', auth: this.oauth2Client });
      logger.info('Gmail client initialized successfully');
    } catch (error) {
      logger.error('Failed to initialize Gmail client', { error });
      throw new Error('Gmail authentication failed. Please run authentication setup.');
    }
  }

  private async saveToken(credentials: any): Promise<void> {
    await fs.writeFile(CONFIG.tokenPath, JSON.stringify(credentials, null, 2));
    logger.info('Token saved successfully');
  }

  private checkRateLimit(): void {
    const now = Date.now();

    // Reset minute counter
    if (now - this.lastResetMinute > 60000) {
      this.requestCount.minute = 0;
      this.lastResetMinute = now;
    }

    // Reset day counter
    if (now - this.lastResetDay > 86400000) {
      this.requestCount.day = 0;
      this.lastResetDay = now;
    }

    // Check limits
    if (this.requestCount.minute >= CONFIG.rateLimit.maxPerMinute) {
      throw new Error('Rate limit exceeded: too many requests per minute');
    }
    if (this.requestCount.day >= CONFIG.rateLimit.maxPerDay) {
      throw new Error('Rate limit exceeded: daily quota reached');
    }

    this.requestCount.minute++;
    this.requestCount.day++;
  }

  private async withRetry<T>(
    operation: () => Promise<T>,
    operationName: string
  ): Promise<T> {
    let lastError: Error | null = null;

    for (let attempt = 0; attempt < CONFIG.maxRetries; attempt++) {
      try {
        this.checkRateLimit();
        return await operation();
      } catch (error: any) {
        lastError = error;

        // Don't retry on auth errors or rate limits
        if (error.code === 401 || error.code === 403 || error.message.includes('Rate limit')) {
          throw error;
        }

        const delay = CONFIG.retryDelay * Math.pow(2, attempt);
        logger.warn(`${operationName} failed, retrying in ${delay}ms`, {
          attempt: attempt + 1,
          error: error.message
        });

        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError || new Error(`${operationName} failed after ${CONFIG.maxRetries} attempts`);
  }

  async sendEmail(params: {
    to: string | string[];
    subject: string;
    body: string;
    cc?: string | string[];
    bcc?: string | string[];
    attachments?: Array<{ filename: string; path: string; mimeType?: string }>;
    isHtml?: boolean;
  }): Promise<{ messageId: string; threadId: string }> {
    if (!this.gmail) throw new Error('Gmail client not initialized');

    const toAddresses = Array.isArray(params.to) ? params.to : [params.to];
    const ccAddresses = params.cc ? (Array.isArray(params.cc) ? params.cc : [params.cc]) : [];
    const bccAddresses = params.bcc ? (Array.isArray(params.bcc) ? params.bcc : [params.bcc]) : [];

    // Build email message
    const boundary = '----=_Part_' + Date.now();
    let message = [
      'MIME-Version: 1.0',
      `To: ${toAddresses.join(', ')}`,
      ccAddresses.length > 0 ? `Cc: ${ccAddresses.join(', ')}` : '',
      bccAddresses.length > 0 ? `Bcc: ${bccAddresses.join(', ')}` : '',
      `Subject: ${params.subject}`,
      `Content-Type: multipart/mixed; boundary="${boundary}"`,
      '',
      `--${boundary}`,
      `Content-Type: ${params.isHtml ? 'text/html' : 'text/plain'}; charset=UTF-8`,
      '',
      params.body,
    ].filter(Boolean).join('\n');

    // Add attachments
    if (params.attachments && params.attachments.length > 0) {
      for (const attachment of params.attachments) {
        const fileContent = await fs.readFile(attachment.path);
        const base64Content = fileContent.toString('base64');

        message += `\n--${boundary}\n`;
        message += `Content-Type: ${attachment.mimeType || 'application/octet-stream'}; name="${attachment.filename}"\n`;
        message += `Content-Disposition: attachment; filename="${attachment.filename}"\n`;
        message += `Content-Transfer-Encoding: base64\n\n`;
        message += base64Content;
      }
    }

    message += `\n--${boundary}--`;

    // Encode message
    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    return this.withRetry(async () => {
      const response = await this.gmail!.users.messages.send({
        userId: 'me',
        requestBody: {
          raw: encodedMessage,
        },
      });

      logger.info('Email sent successfully', {
        messageId: response.data.id,
        to: toAddresses,
        subject: params.subject,
      });

      return {
        messageId: response.data.id!,
        threadId: response.data.threadId!,
      };
    }, 'sendEmail');
  }

  async readEmails(params: {
    query?: string;
    maxResults?: number;
    labelIds?: string[];
    includeSpamTrash?: boolean;
  }): Promise<Array<{
    id: string;
    threadId: string;
    from: string;
    to: string;
    subject: string;
    snippet: string;
    date: string;
    labels: string[];
    isUnread: boolean;
  }>> {
    if (!this.gmail) throw new Error('Gmail client not initialized');

    return this.withRetry(async () => {
      const response = await this.gmail!.users.messages.list({
        userId: 'me',
        q: params.query,
        maxResults: params.maxResults || 10,
        labelIds: params.labelIds,
        includeSpamTrash: params.includeSpamTrash || false,
      });

      if (!response.data.messages) {
        return [];
      }

      const emails = await Promise.all(
        response.data.messages.map(async (msg) => {
          const detail = await this.gmail!.users.messages.get({
            userId: 'me',
            id: msg.id!,
          });

          const headers = detail.data.payload?.headers || [];
          const getHeader = (name: string) =>
            headers.find((h) => h.name?.toLowerCase() === name.toLowerCase())?.value || '';

          return {
            id: detail.data.id!,
            threadId: detail.data.threadId!,
            from: getHeader('from'),
            to: getHeader('to'),
            subject: getHeader('subject'),
            snippet: detail.data.snippet || '',
            date: getHeader('date'),
            labels: detail.data.labelIds || [],
            isUnread: detail.data.labelIds?.includes('UNREAD') || false,
          };
        })
      );

      logger.info('Emails retrieved successfully', { count: emails.length });
      return emails;
    }, 'readEmails');
  }

  async searchEmails(query: string, maxResults: number = 10): Promise<any[]> {
    return this.readEmails({ query, maxResults });
  }

  async draftEmail(params: {
    to: string | string[];
    subject: string;
    body: string;
    cc?: string | string[];
    isHtml?: boolean;
  }): Promise<{ draftId: string; messageId: string }> {
    if (!this.gmail) throw new Error('Gmail client not initialized');

    const toAddresses = Array.isArray(params.to) ? params.to : [params.to];
    const ccAddresses = params.cc ? (Array.isArray(params.cc) ? params.cc : [params.cc]) : [];

    const message = [
      `To: ${toAddresses.join(', ')}`,
      ccAddresses.length > 0 ? `Cc: ${ccAddresses.join(', ')}` : '',
      `Subject: ${params.subject}`,
      `Content-Type: ${params.isHtml ? 'text/html' : 'text/plain'}; charset=UTF-8`,
      '',
      params.body,
    ].filter(Boolean).join('\n');

    const encodedMessage = Buffer.from(message)
      .toString('base64')
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');

    return this.withRetry(async () => {
      const response = await this.gmail!.users.drafts.create({
        userId: 'me',
        requestBody: {
          message: {
            raw: encodedMessage,
          },
        },
      });

      logger.info('Draft created successfully', {
        draftId: response.data.id,
        subject: params.subject,
      });

      return {
        draftId: response.data.id!,
        messageId: response.data.message?.id!,
      };
    }, 'draftEmail');
  }

  async getProfile(): Promise<{ emailAddress: string; messagesTotal: number; threadsTotal: number }> {
    if (!this.gmail) throw new Error('Gmail client not initialized');

    return this.withRetry(async () => {
      const response = await this.gmail!.users.getProfile({ userId: 'me' });
      return {
        emailAddress: response.data.emailAddress!,
        messagesTotal: response.data.messagesTotal!,
        threadsTotal: response.data.threadsTotal!,
      };
    }, 'getProfile');
  }
}

// Approval Workflow Manager
class ApprovalManager {
  private vaultPath: string;

  constructor(vaultPath: string) {
    this.vaultPath = vaultPath;
  }

  async createApprovalRequest(params: {
    action: string;
    type: 'email_send' | 'email_reply' | 'email_draft';
    data: any;
    reason: string;
    priority?: 'low' | 'medium' | 'high';
  }): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `EMAIL_${params.type}_${timestamp}.md`;
    const filepath = path.join(this.vaultPath, 'Pending_Approval', filename);

    const content = `---
type: approval_request
action: ${params.action}
category: ${params.type}
created: ${new Date().toISOString()}
expires: ${new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()}
status: pending
priority: ${params.priority || 'medium'}
---

# Email Approval Request

## Action
${params.action}

## Details
**To:** ${Array.isArray(params.data.to) ? params.data.to.join(', ') : params.data.to}
${params.data.cc ? `**Cc:** ${Array.isArray(params.data.cc) ? params.data.cc.join(', ') : params.data.cc}` : ''}
**Subject:** ${params.data.subject}

## Email Body
\`\`\`
${params.data.body}
\`\`\`

${params.data.attachments ? `\n## Attachments\n${params.data.attachments.map((a: any) => `- ${a.filename}`).join('\n')}` : ''}

## Reason
${params.reason}

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with a reason comment.

---
*Created by Gmail MCP Server*
*Request ID: ${timestamp}*
`;

    await fs.mkdir(path.dirname(filepath), { recursive: true });
    await fs.writeFile(filepath, content);

    logger.info('Approval request created', { filepath, type: params.type });

    return filepath;
  }

  async checkAutoApprove(params: { to: string | string[] }): Promise<boolean> {
    if (!CONFIG.autoApprove.enabled) return false;

    const recipients = Array.isArray(params.to) ? params.to : [params.to];

    // Check recipient count
    if (recipients.length > CONFIG.autoApprove.maxRecipients) {
      logger.info('Auto-approve denied: too many recipients', { count: recipients.length });
      return false;
    }

    // Could add known contacts check here
    // For now, only single recipient emails can be auto-approved
    return recipients.length === 1;
  }

  async logAction(params: {
    action: string;
    type: string;
    result: 'success' | 'failure' | 'pending_approval';
    data: any;
    error?: string;
  }): Promise<void> {
    const logDir = path.join(this.vaultPath, 'Logs');
    const logFile = path.join(logDir, `actions_${new Date().toISOString().split('T')[0]}.json`);

    await fs.mkdir(logDir, { recursive: true });

    const logEntry = {
      timestamp: new Date().toISOString(),
      action: params.action,
      type: params.type,
      result: params.result,
      actor: 'gmail-mcp-server',
      data: {
        ...params.data,
        // Redact sensitive information
        body: params.data.body ? '[REDACTED]' : undefined,
      },
      error: params.error,
    };

    try {
      let logs = [];
      try {
        const existing = await fs.readFile(logFile, 'utf-8');
        logs = JSON.parse(existing);
      } catch {
        // File doesn't exist yet
      }

      logs.push(logEntry);
      await fs.writeFile(logFile, JSON.stringify(logs, null, 2));

      logger.info('Action logged', { action: params.action, result: params.result });
    } catch (error) {
      logger.error('Failed to write log', { error });
    }
  }
}

// MCP Server Implementation
const server = new Server(
  {
    name: 'gmail-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const gmailClient = new GmailClient();
const approvalManager = new ApprovalManager(CONFIG.vaultPath);

// Define tools
const TOOLS: Tool[] = [
  {
    name: 'gmail_send_email',
    description: 'Send an email via Gmail. Creates approval request for human review unless auto-approved.',
    inputSchema: {
      type: 'object',
      properties: {
        to: {
          type: ['string', 'array'],
          description: 'Recipient email address(es)',
          items: { type: 'string' },
        },
        subject: {
          type: 'string',
          description: 'Email subject',
        },
        body: {
          type: 'string',
          description: 'Email body content',
        },
        cc: {
          type: ['string', 'array'],
          description: 'CC email address(es)',
          items: { type: 'string' },
        },
        bcc: {
          type: ['string', 'array'],
          description: 'BCC email address(es)',
          items: { type: 'string' },
        },
        attachments: {
          type: 'array',
          description: 'File attachments',
          items: {
            type: 'object',
            properties: {
              filename: { type: 'string' },
              path: { type: 'string' },
              mimeType: { type: 'string' },
            },
            required: ['filename', 'path'],
          },
        },
        isHtml: {
          type: 'boolean',
          description: 'Whether email body is HTML',
          default: false,
        },
        requireApproval: {
          type: 'boolean',
          description: 'Force approval requirement',
          default: true,
        },
      },
      required: ['to', 'subject', 'body'],
    },
  },
  {
    name: 'gmail_read_emails',
    description: 'Read emails from Gmail inbox with optional filtering',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Gmail search query (e.g., "is:unread from:client@example.com")',
        },
        maxResults: {
          type: 'number',
          description: 'Maximum number of emails to retrieve',
          default: 10,
          minimum: 1,
          maximum: 100,
        },
        labelIds: {
          type: 'array',
          description: 'Filter by label IDs (e.g., ["INBOX", "IMPORTANT"])',
          items: { type: 'string' },
        },
        includeSpamTrash: {
          type: 'boolean',
          description: 'Include spam and trash',
          default: false,
        },
      },
    },
  },
  {
    name: 'gmail_search_emails',
    description: 'Search emails using Gmail search syntax',
    inputSchema: {
      type: 'object',
      properties: {
        query: {
          type: 'string',
          description: 'Search query using Gmail syntax',
        },
        maxResults: {
          type: 'number',
          description: 'Maximum results',
          default: 10,
        },
      },
      required: ['query'],
    },
  },
  {
    name: 'gmail_draft_email',
    description: 'Create an email draft in Gmail',
    inputSchema: {
      type: 'object',
      properties: {
        to: {
          type: ['string', 'array'],
          description: 'Recipient email address(es)',
          items: { type: 'string' },
        },
        subject: {
          type: 'string',
          description: 'Email subject',
        },
        body: {
          type: 'string',
          description: 'Email body',
        },
        cc: {
          type: ['string', 'array'],
          description: 'CC addresses',
          items: { type: 'string' },
        },
        isHtml: {
          type: 'boolean',
          description: 'HTML email',
          default: false,
        },
      },
      required: ['to', 'subject', 'body'],
    },
  },
  {
    name: 'gmail_get_profile',
    description: 'Get Gmail account profile information',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
];

// Register tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    const { name, arguments: args } = request.params;

    switch (name) {
      case 'gmail_send_email': {
        const needsApproval = args.requireApproval !== false ||
                             !(await approvalManager.checkAutoApprove({ to: args.to }));

        if (needsApproval) {
          const approvalFile = await approvalManager.createApprovalRequest({
            action: 'Send Email',
            type: 'email_send',
            data: args,
            reason: 'Email requires human approval before sending',
            priority: args.attachments?.length > 0 ? 'high' : 'medium',
          });

          await approvalManager.logAction({
            action: 'gmail_send_email',
            type: 'email_send',
            result: 'pending_approval',
            data: { to: args.to, subject: args.subject },
          });

          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify({
                  status: 'pending_approval',
                  message: 'Email requires approval. Approval request created.',
                  approvalFile,
                  instructions: 'Move the approval file to /Approved folder to send the email.',
                }, null, 2),
              },
            ],
          };
        }

        // Auto-approved, send immediately
        const result = await gmailClient.sendEmail(args);

        await approvalManager.logAction({
          action: 'gmail_send_email',
          type: 'email_send',
          result: 'success',
          data: { to: args.to, subject: args.subject, messageId: result.messageId },
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                message: 'Email sent successfully',
                messageId: result.messageId,
                threadId: result.threadId,
              }, null, 2),
            },
          ],
        };
      }

      case 'gmail_read_emails': {
        const emails = await gmailClient.readEmails(args);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                count: emails.length,
                emails,
              }, null, 2),
            },
          ],
        };
      }

      case 'gmail_search_emails': {
        const emails = await gmailClient.searchEmails(args.query, args.maxResults);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                count: emails.length,
                emails,
              }, null, 2),
            },
          ],
        };
      }

      case 'gmail_draft_email': {
        const result = await gmailClient.draftEmail(args);

        await approvalManager.logAction({
          action: 'gmail_draft_email',
          type: 'email_draft',
          result: 'success',
          data: { to: args.to, subject: args.subject, draftId: result.draftId },
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                message: 'Draft created successfully',
                draftId: result.draftId,
                messageId: result.messageId,
              }, null, 2),
            },
          ],
        };
      }

      case 'gmail_get_profile': {
        const profile = await gmailClient.getProfile();

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                profile,
              }, null, 2),
            },
          ],
        };
      }

      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error: any) {
    logger.error('Tool execution failed', {
      tool: request.params.name,
      error: error.message
    });

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            status: 'error',
            error: error.message,
            details: error.stack,
          }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// Server startup
async function main() {
  try {
    // Ensure log directory exists
    await fs.mkdir(CONFIG.logPath, { recursive: true });

    // Initialize Gmail client
    await gmailClient.initialize();

    // Start server
    const transport = new StdioServerTransport();
    await server.connect(transport);

    logger.info('Gmail MCP Server started successfully', {
      vaultPath: CONFIG.vaultPath,
      autoApprove: CONFIG.autoApprove.enabled,
    });
  } catch (error) {
    logger.error('Failed to start Gmail MCP Server', { error });
    process.exit(1);
  }
}

main();
