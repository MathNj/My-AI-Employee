#!/usr/bin/env node

/**
 * Gmail MCP Server
 *
 * A Model Context Protocol server for Gmail integration with:
 * - OAuth 2.0 authentication
 * - Email reading, sending, searching
 * - Label management
 * - Human-in-the-Loop approval workflow
 * - Rate limiting and error handling
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
  ErrorCode,
  McpError
} from '@modelcontextprotocol/sdk/types.js';
import { GmailClient } from './gmail-client.js';
import { ApprovalManager } from './approval-manager.js';
import { RateLimiter } from './rate-limiter.js';
import { config } from './config.js';
import { logger } from './logger.js';

/**
 * Main MCP Server class
 */
class GmailMCPServer {
  private server: Server;
  private gmailClient: GmailClient;
  private approvalManager: ApprovalManager;
  private rateLimiter: RateLimiter;

  constructor() {
    this.server = new Server(
      {
        name: config.serverName,
        version: config.serverVersion
      },
      {
        capabilities: {
          tools: {},
          resources: {}
        }
      }
    );

    this.gmailClient = new GmailClient();
    this.approvalManager = new ApprovalManager(config.approvalVaultPath);
    this.rateLimiter = new RateLimiter(
      config.maxEmailsPerMinute,
      config.maxEmailsPerHour
    );

    this.setupHandlers();
    this.setupErrorHandling();
  }

  /**
   * Set up MCP protocol handlers
   */
  private setupHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: 'gmail_list_messages',
          description: 'List Gmail messages with optional filters (unread, important, from, to, subject)',
          inputSchema: {
            type: 'object',
            properties: {
              maxResults: {
                type: 'number',
                description: 'Maximum number of messages to return (default: 10, max: 100)',
                default: 10
              },
              query: {
                type: 'string',
                description: 'Gmail search query (e.g., "is:unread is:important", "from:user@example.com")'
              },
              labelIds: {
                type: 'array',
                items: { type: 'string' },
                description: 'Label IDs to filter by (e.g., ["INBOX", "IMPORTANT"])'
              }
            }
          }
        },
        {
          name: 'gmail_get_message',
          description: 'Get a specific Gmail message by ID with full content',
          inputSchema: {
            type: 'object',
            properties: {
              messageId: {
                type: 'string',
                description: 'The Gmail message ID'
              },
              format: {
                type: 'string',
                enum: ['full', 'metadata', 'minimal'],
                description: 'Message format (default: full)',
                default: 'full'
              }
            },
            required: ['messageId']
          }
        },
        {
          name: 'gmail_send_email',
          description: 'Send an email via Gmail (requires approval if configured). Creates approval request in HITL workflow.',
          inputSchema: {
            type: 'object',
            properties: {
              to: {
                type: 'string',
                description: 'Recipient email address (or comma-separated list)'
              },
              subject: {
                type: 'string',
                description: 'Email subject'
              },
              body: {
                type: 'string',
                description: 'Email body (plain text or HTML)'
              },
              cc: {
                type: 'string',
                description: 'CC recipients (comma-separated)'
              },
              bcc: {
                type: 'string',
                description: 'BCC recipients (comma-separated)'
              },
              replyTo: {
                type: 'string',
                description: 'Message ID to reply to (for threading)'
              },
              attachments: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    filename: { type: 'string' },
                    path: { type: 'string' },
                    contentType: { type: 'string' }
                  }
                },
                description: 'Email attachments'
              },
              skipApproval: {
                type: 'boolean',
                description: 'Skip approval workflow (use with caution)',
                default: false
              }
            },
            required: ['to', 'subject', 'body']
          }
        },
        {
          name: 'gmail_search_messages',
          description: 'Search Gmail messages with advanced Gmail search syntax',
          inputSchema: {
            type: 'object',
            properties: {
              query: {
                type: 'string',
                description: 'Gmail search query (supports all Gmail search operators)'
              },
              maxResults: {
                type: 'number',
                description: 'Maximum number of results (default: 20, max: 100)',
                default: 20
              }
            },
            required: ['query']
          }
        },
        {
          name: 'gmail_list_labels',
          description: 'List all Gmail labels',
          inputSchema: {
            type: 'object',
            properties: {}
          }
        },
        {
          name: 'gmail_create_label',
          description: 'Create a new Gmail label',
          inputSchema: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'Label name'
              },
              labelListVisibility: {
                type: 'string',
                enum: ['labelShow', 'labelShowIfUnread', 'labelHide'],
                description: 'Label visibility',
                default: 'labelShow'
              },
              messageListVisibility: {
                type: 'string',
                enum: ['show', 'hide'],
                description: 'Message list visibility',
                default: 'show'
              }
            },
            required: ['name']
          }
        },
        {
          name: 'gmail_modify_message',
          description: 'Modify message labels (add/remove labels, mark as read/unread)',
          inputSchema: {
            type: 'object',
            properties: {
              messageId: {
                type: 'string',
                description: 'Message ID to modify'
              },
              addLabelIds: {
                type: 'array',
                items: { type: 'string' },
                description: 'Label IDs to add'
              },
              removeLabelIds: {
                type: 'array',
                items: { type: 'string' },
                description: 'Label IDs to remove'
              }
            },
            required: ['messageId']
          }
        },
        {
          name: 'gmail_get_thread',
          description: 'Get an email thread (conversation) by thread ID',
          inputSchema: {
            type: 'object',
            properties: {
              threadId: {
                type: 'string',
                description: 'Thread ID'
              }
            },
            required: ['threadId']
          }
        }
      ]
    }));

    // List available resources
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => ({
      resources: [
        {
          uri: 'gmail://inbox',
          name: 'Inbox Messages',
          description: 'List of inbox messages',
          mimeType: 'application/json'
        },
        {
          uri: 'gmail://unread',
          name: 'Unread Messages',
          description: 'List of unread messages',
          mimeType: 'application/json'
        },
        {
          uri: 'gmail://important',
          name: 'Important Messages',
          description: 'List of important messages',
          mimeType: 'application/json'
        },
        {
          uri: 'gmail://labels',
          name: 'Gmail Labels',
          description: 'List of all Gmail labels',
          mimeType: 'application/json'
        }
      ]
    }));

    // Read resource
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const uri = request.params.uri;

      switch (uri) {
        case 'gmail://inbox':
          return this.readInboxResource();
        case 'gmail://unread':
          return this.readUnreadResource();
        case 'gmail://important':
          return this.readImportantResource();
        case 'gmail://labels':
          return this.readLabelsResource();
        default:
          throw new McpError(
            ErrorCode.InvalidRequest,
            `Unknown resource URI: ${uri}`
          );
      }
    });

    // Execute tool
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'gmail_list_messages':
            return await this.handleListMessages(args);
          case 'gmail_get_message':
            return await this.handleGetMessage(args);
          case 'gmail_send_email':
            return await this.handleSendEmail(args);
          case 'gmail_search_messages':
            return await this.handleSearchMessages(args);
          case 'gmail_list_labels':
            return await this.handleListLabels(args);
          case 'gmail_create_label':
            return await this.handleCreateLabel(args);
          case 'gmail_modify_message':
            return await this.handleModifyMessage(args);
          case 'gmail_get_thread':
            return await this.handleGetThread(args);
          default:
            throw new McpError(
              ErrorCode.MethodNotFound,
              `Unknown tool: ${name}`
            );
        }
      } catch (error) {
        logger.error(`Error executing tool ${name}:`, error);
        throw new McpError(
          ErrorCode.InternalError,
          `Error executing tool: ${error instanceof Error ? error.message : String(error)}`
        );
      }
    });
  }

  /**
   * Set up error handling
   */
  private setupErrorHandling(): void {
    this.server.onerror = (error) => {
      logger.error('MCP Server error:', error);
    };

    process.on('SIGINT', async () => {
      logger.info('Shutting down Gmail MCP Server...');
      await this.server.close();
      process.exit(0);
    });
  }

  // Resource readers
  private async readInboxResource() {
    const messages = await this.gmailClient.listMessages({ labelIds: ['INBOX'], maxResults: 20 });
    return {
      contents: [
        {
          uri: 'gmail://inbox',
          mimeType: 'application/json',
          text: JSON.stringify(messages, null, 2)
        }
      ]
    };
  }

  private async readUnreadResource() {
    const messages = await this.gmailClient.listMessages({ query: 'is:unread', maxResults: 20 });
    return {
      contents: [
        {
          uri: 'gmail://unread',
          mimeType: 'application/json',
          text: JSON.stringify(messages, null, 2)
        }
      ]
    };
  }

  private async readImportantResource() {
    const messages = await this.gmailClient.listMessages({ query: 'is:important', maxResults: 20 });
    return {
      contents: [
        {
          uri: 'gmail://important',
          mimeType: 'application/json',
          text: JSON.stringify(messages, null, 2)
        }
      ]
    };
  }

  private async readLabelsResource() {
    const labels = await this.gmailClient.listLabels();
    return {
      contents: [
        {
          uri: 'gmail://labels',
          mimeType: 'application/json',
          text: JSON.stringify(labels, null, 2)
        }
      ]
    };
  }

  // Tool handlers
  private async handleListMessages(args: any) {
    const messages = await this.gmailClient.listMessages(args);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(messages, null, 2)
        }
      ]
    };
  }

  private async handleGetMessage(args: any) {
    const message = await this.gmailClient.getMessage(args.messageId, args.format);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(message, null, 2)
        }
      ]
    };
  }

  private async handleSendEmail(args: any) {
    // Check rate limiting
    if (!this.rateLimiter.checkLimit()) {
      throw new McpError(
        ErrorCode.InternalError,
        'Rate limit exceeded. Please try again later.'
      );
    }

    // Check if approval is required
    if (config.requireApprovalForSend && !args.skipApproval) {
      const approvalId = await this.approvalManager.createApprovalRequest({
        type: 'email_send',
        action: 'gmail_send_email',
        parameters: args,
        expiresInHours: config.approvalTimeoutHours
      });

      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify({
              status: 'pending_approval',
              approvalId,
              message: 'Email send request created and requires approval',
              approvalPath: this.approvalManager.getApprovalPath(approvalId),
              instructions: 'Move the approval file to /Approved folder to send the email'
            }, null, 2)
          }
        ]
      };
    }

    // Send email directly if no approval required
    const result = await this.gmailClient.sendEmail(args);
    this.rateLimiter.recordSend();

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            status: 'sent',
            messageId: result.id,
            threadId: result.threadId
          }, null, 2)
        }
      ]
    };
  }

  private async handleSearchMessages(args: any) {
    const messages = await this.gmailClient.searchMessages(args.query, args.maxResults);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(messages, null, 2)
        }
      ]
    };
  }

  private async handleListLabels(args: any) {
    const labels = await this.gmailClient.listLabels();
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(labels, null, 2)
        }
      ]
    };
  }

  private async handleCreateLabel(args: any) {
    const label = await this.gmailClient.createLabel(args);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(label, null, 2)
        }
      ]
    };
  }

  private async handleModifyMessage(args: any) {
    const result = await this.gmailClient.modifyMessage(
      args.messageId,
      args.addLabelIds,
      args.removeLabelIds
    );
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }
      ]
    };
  }

  private async handleGetThread(args: any) {
    const thread = await this.gmailClient.getThread(args.threadId);
    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify(thread, null, 2)
        }
      ]
    };
  }

  /**
   * Start the MCP server
   */
  async start(): Promise<void> {
    // Initialize Gmail client
    await this.gmailClient.initialize();

    // Start server with stdio transport
    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    logger.info(`Gmail MCP Server started (${config.serverName} v${config.serverVersion})`);
    logger.info(`Approval workflow: ${config.requireApprovalForSend ? 'ENABLED' : 'DISABLED'}`);
  }
}

// Start the server
const server = new GmailMCPServer();
server.start().catch((error) => {
  logger.error('Failed to start Gmail MCP Server:', error);
  process.exit(1);
});
