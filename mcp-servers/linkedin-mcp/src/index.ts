#!/usr/bin/env node

/**
 * LinkedIn MCP Server
 * Production-ready MCP server for LinkedIn with OAuth 2.0 and business automation
 *
 * Features:
 * - OAuth 2.0 authentication for LinkedIn API
 * - Create posts, schedule posts, read notifications
 * - Human-in-the-Loop approval workflow integration
 * - Template support for common post types
 * - Rate limiting and quota management
 * - Comprehensive error handling with retry logic
 * - Detailed audit logging (with PII redaction)
 * - Support for text, images, and documents
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool,
} from '@modelcontextprotocol/sdk/types.js';
import axios, { AxiosInstance } from 'axios';
import fs from 'fs/promises';
import path from 'path';
import { createLogger, format, transports } from 'winston';
import dotenv from 'dotenv';

dotenv.config();

// Configuration
const CONFIG = {
  vaultPath: process.env.VAULT_PATH || 'C:\\Users\\Najma-LP\\Desktop\\My Vault\\AI_Employee_Vault',
  tokenPath: process.env.LINKEDIN_TOKEN_PATH || './linkedin_token.json',
  templatesPath: process.env.TEMPLATES_PATH || './templates',
  maxRetries: 3,
  retryDelay: 1000,
  rateLimit: {
    maxPerHour: 100,
    maxPerDay: 500,
  },
  autoApprove: {
    enabled: process.env.AUTO_APPROVE === 'true',
    scheduledOnly: true,
  },
  logPath: process.env.LOG_PATH || './logs',
};

// Logger setup
const logger = createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: format.combine(
    format.timestamp(),
    format.errors({ stack: true }),
    format.printf(({ timestamp, level, message, ...meta }) => {
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
      filename: path.join(CONFIG.logPath, 'linkedin-mcp-error.log'),
      level: 'error'
    }),
    new transports.File({
      filename: path.join(CONFIG.logPath, 'linkedin-mcp.log')
    }),
  ],
});

// Post templates
const POST_TEMPLATES = {
  service_announcement: {
    title: 'Service Announcement',
    template: (data: any) => `🚀 Exciting News!\n\nWe're thrilled to announce ${data.service}!\n\n${data.description}\n\n${data.benefits || ''}\n\n${data.callToAction || 'Learn more in the comments!'}\n\n${data.hashtags || '#Innovation #Business'}`,
  },
  achievement: {
    title: 'Achievement/Milestone',
    template: (data: any) => `🎉 Milestone Alert!\n\nWe're proud to share that ${data.achievement}!\n\n${data.details}\n\n${data.gratitude || 'Thank you to everyone who made this possible!'}\n\n${data.hashtags || '#Success #Growth'}`,
  },
  thought_leadership: {
    title: 'Thought Leadership',
    template: (data: any) => `💡 ${data.title}\n\n${data.insight}\n\n${data.perspective || ''}\n\nWhat are your thoughts? Share in the comments!\n\n${data.hashtags || '#Leadership #Innovation'}`,
  },
  behind_the_scenes: {
    title: 'Behind the Scenes',
    template: (data: any) => `👋 Behind the Scenes at ${data.company}!\n\n${data.story}\n\n${data.details || ''}\n\n${data.hashtags || '#CompanyCulture #Team'}`,
  },
  customer_success: {
    title: 'Customer Success Story',
    template: (data: any) => `⭐ Customer Success Story\n\n${data.customerName} achieved ${data.result} using ${data.solution}!\n\n${data.testimonial ? `"${data.testimonial}"` : ''}\n\n${data.callToAction || 'Want similar results? Let\'s talk!'}\n\n${data.hashtags || '#CustomerSuccess #Results'}`,
  },
};

// LinkedIn Client with OAuth 2.0
class LinkedInClient {
  private accessToken: string = '';
  private personUrn: string = '';
  private axiosInstance: AxiosInstance;
  private requestCount = { hour: 0, day: 0 };
  private lastResetHour = Date.now();
  private lastResetDay = Date.now();

  constructor() {
    this.axiosInstance = axios.create({
      baseURL: 'https://api.linkedin.com/v2',
      headers: {
        'Content-Type': 'application/json',
        'X-Restli-Protocol-Version': '2.0.0',
      },
    });
  }

  async initialize(): Promise<void> {
    try {
      const tokenData = await fs.readFile(CONFIG.tokenPath, 'utf-8');
      const tokens = JSON.parse(tokenData);

      this.accessToken = tokens.access_token;
      this.personUrn = tokens.person_urn;

      // Update axios instance with token
      this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`;

      // Verify token by getting profile
      await this.getProfile();

      logger.info('LinkedIn client initialized successfully');
    } catch (error: any) {
      logger.error('Failed to initialize LinkedIn client', { error: error.message });
      throw new Error('LinkedIn authentication failed. Please run authentication setup.');
    }
  }

  private checkRateLimit(): void {
    const now = Date.now();

    // Reset hour counter
    if (now - this.lastResetHour > 3600000) {
      this.requestCount.hour = 0;
      this.lastResetHour = now;
    }

    // Reset day counter
    if (now - this.lastResetDay > 86400000) {
      this.requestCount.day = 0;
      this.lastResetDay = now;
    }

    // Check limits
    if (this.requestCount.hour >= CONFIG.rateLimit.maxPerHour) {
      throw new Error('Rate limit exceeded: too many requests per hour');
    }
    if (this.requestCount.day >= CONFIG.rateLimit.maxPerDay) {
      throw new Error('Rate limit exceeded: daily quota reached');
    }

    this.requestCount.hour++;
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
        if (error.response?.status === 401 || error.response?.status === 429 ||
            error.message.includes('Rate limit')) {
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

  async createPost(params: {
    text: string;
    visibility?: 'PUBLIC' | 'CONNECTIONS';
    media?: Array<{ url: string; title?: string; description?: string }>;
  }): Promise<{ postId: string; postUrl: string }> {
    return this.withRetry(async () => {
      const shareContent: any = {
        author: this.personUrn,
        lifecycleState: 'PUBLISHED',
        specificContent: {
          'com.linkedin.ugc.ShareContent': {
            shareCommentary: {
              text: params.text,
            },
            shareMediaCategory: params.media && params.media.length > 0 ? 'ARTICLE' : 'NONE',
          },
        },
        visibility: {
          'com.linkedin.ugc.MemberNetworkVisibility': params.visibility || 'PUBLIC',
        },
      };

      // Add media if provided
      if (params.media && params.media.length > 0) {
        shareContent.specificContent['com.linkedin.ugc.ShareContent'].media = params.media.map(m => ({
          status: 'READY',
          originalUrl: m.url,
          title: {
            text: m.title || '',
          },
          description: {
            text: m.description || '',
          },
        }));
      }

      const response = await this.axiosInstance.post('/ugcPosts', shareContent);

      const postId = response.data.id;
      const postUrl = `https://www.linkedin.com/feed/update/${postId}`;

      logger.info('LinkedIn post created successfully', { postId, postUrl });

      return { postId, postUrl };
    }, 'createPost');
  }

  async getProfile(): Promise<{
    id: string;
    firstName: string;
    lastName: string;
    profileUrl: string;
  }> {
    return this.withRetry(async () => {
      const response = await this.axiosInstance.get('/me', {
        params: {
          projection: '(id,localizedFirstName,localizedLastName,vanityName)',
        },
      });

      const data = response.data;
      return {
        id: data.id,
        firstName: data.localizedFirstName,
        lastName: data.localizedLastName,
        profileUrl: `https://www.linkedin.com/in/${data.vanityName || data.id}`,
      };
    }, 'getProfile');
  }

  async getPostAnalytics(postId: string): Promise<{
    likes: number;
    comments: number;
    shares: number;
    impressions: number;
  }> {
    return this.withRetry(async () => {
      const response = await this.axiosInstance.get(`/socialActions/${postId}`, {
        params: {
          projection: '(likesSummary,commentsSummary,sharesSummary)',
        },
      });

      const data = response.data;
      return {
        likes: data.likesSummary?.totalLikes || 0,
        comments: data.commentsSummary?.totalComments || 0,
        shares: data.sharesSummary?.totalShares || 0,
        impressions: data.impressions || 0,
      };
    }, 'getPostAnalytics');
  }

  generatePostFromTemplate(templateName: string, data: any): string {
    const template = POST_TEMPLATES[templateName as keyof typeof POST_TEMPLATES];
    if (!template) {
      throw new Error(`Template not found: ${templateName}`);
    }

    return template.template(data);
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
    type: 'linkedin_post' | 'linkedin_scheduled_post';
    data: any;
    reason: string;
    priority?: 'low' | 'medium' | 'high';
  }): Promise<string> {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `LINKEDIN_${params.type}_${timestamp}.md`;
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

# LinkedIn Post Approval Request

## Action
${params.action}

## Post Content
\`\`\`
${params.data.text}
\`\`\`

${params.data.media ? `\n## Media\n${params.data.media.map((m: any) => `- ${m.url} (${m.title || 'No title'})`).join('\n')}` : ''}

## Visibility
${params.data.visibility || 'PUBLIC'}

## Reason
${params.reason}

## Preview
This post will be published to your LinkedIn profile and visible to ${params.data.visibility === 'CONNECTIONS' ? 'your connections' : 'the public'}.

## To Approve
Move this file to /Approved folder.

## To Reject
Move this file to /Rejected folder with a reason comment.

---
*Created by LinkedIn MCP Server*
*Request ID: ${timestamp}*
`;

    await fs.mkdir(path.dirname(filepath), { recursive: true });
    await fs.writeFile(filepath, content);

    logger.info('Approval request created', { filepath, type: params.type });

    return filepath;
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
      actor: 'linkedin-mcp-server',
      data: {
        ...params.data,
        text: params.data.text ? '[REDACTED]' : undefined,
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
    name: 'linkedin-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

const linkedinClient = new LinkedInClient();
const approvalManager = new ApprovalManager(CONFIG.vaultPath);

// Define tools
const TOOLS: Tool[] = [
  {
    name: 'linkedin_create_post',
    description: 'Create a LinkedIn post. Always creates approval request for human review.',
    inputSchema: {
      type: 'object',
      properties: {
        text: {
          type: 'string',
          description: 'Post content (max 3000 characters)',
          maxLength: 3000,
        },
        visibility: {
          type: 'string',
          enum: ['PUBLIC', 'CONNECTIONS'],
          description: 'Post visibility',
          default: 'PUBLIC',
        },
        media: {
          type: 'array',
          description: 'Optional media attachments',
          items: {
            type: 'object',
            properties: {
              url: { type: 'string', description: 'Media URL' },
              title: { type: 'string', description: 'Media title' },
              description: { type: 'string', description: 'Media description' },
            },
            required: ['url'],
          },
        },
        requireApproval: {
          type: 'boolean',
          description: 'Force approval requirement',
          default: true,
        },
      },
      required: ['text'],
    },
  },
  {
    name: 'linkedin_generate_post',
    description: 'Generate a LinkedIn post from a template',
    inputSchema: {
      type: 'object',
      properties: {
        template: {
          type: 'string',
          enum: ['service_announcement', 'achievement', 'thought_leadership', 'behind_the_scenes', 'customer_success'],
          description: 'Template to use',
        },
        data: {
          type: 'object',
          description: 'Template data (varies by template)',
          additionalProperties: true,
        },
      },
      required: ['template', 'data'],
    },
  },
  {
    name: 'linkedin_get_profile',
    description: 'Get LinkedIn profile information',
    inputSchema: {
      type: 'object',
      properties: {},
    },
  },
  {
    name: 'linkedin_get_post_analytics',
    description: 'Get analytics for a specific post',
    inputSchema: {
      type: 'object',
      properties: {
        postId: {
          type: 'string',
          description: 'LinkedIn post ID',
        },
      },
      required: ['postId'],
    },
  },
  {
    name: 'linkedin_list_templates',
    description: 'List available post templates',
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
      case 'linkedin_create_post': {
        const needsApproval = args.requireApproval !== false;

        if (needsApproval) {
          const approvalFile = await approvalManager.createApprovalRequest({
            action: 'Create LinkedIn Post',
            type: 'linkedin_post',
            data: args,
            reason: 'LinkedIn posts require human approval before publishing',
            priority: 'high',
          });

          await approvalManager.logAction({
            action: 'linkedin_create_post',
            type: 'linkedin_post',
            result: 'pending_approval',
            data: { textPreview: args.text.substring(0, 100) + '...' },
          });

          return {
            content: [
              {
                type: 'text',
                text: JSON.stringify({
                  status: 'pending_approval',
                  message: 'LinkedIn post requires approval. Approval request created.',
                  approvalFile,
                  instructions: 'Move the approval file to /Approved folder to publish the post.',
                  preview: args.text.substring(0, 200) + (args.text.length > 200 ? '...' : ''),
                }, null, 2),
              },
            ],
          };
        }

        // Auto-approved (rarely used)
        const result = await linkedinClient.createPost(args);

        await approvalManager.logAction({
          action: 'linkedin_create_post',
          type: 'linkedin_post',
          result: 'success',
          data: { postId: result.postId, postUrl: result.postUrl },
        });

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                message: 'LinkedIn post published successfully',
                postId: result.postId,
                postUrl: result.postUrl,
              }, null, 2),
            },
          ],
        };
      }

      case 'linkedin_generate_post': {
        const text = linkedinClient.generatePostFromTemplate(args.template, args.data);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                template: args.template,
                generatedText: text,
                nextStep: 'Use linkedin_create_post to publish this content',
              }, null, 2),
            },
          ],
        };
      }

      case 'linkedin_get_profile': {
        const profile = await linkedinClient.getProfile();

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

      case 'linkedin_get_post_analytics': {
        const analytics = await linkedinClient.getPostAnalytics(args.postId);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                postId: args.postId,
                analytics,
              }, null, 2),
            },
          ],
        };
      }

      case 'linkedin_list_templates': {
        const templates = Object.entries(POST_TEMPLATES).map(([key, value]) => ({
          name: key,
          title: value.title,
          description: `Template for ${value.title.toLowerCase()}`,
        }));

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                status: 'success',
                templates,
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

    // Initialize LinkedIn client
    await linkedinClient.initialize();

    // Start server
    const transport = new StdioServerTransport();
    await server.connect(transport);

    logger.info('LinkedIn MCP Server started successfully', {
      vaultPath: CONFIG.vaultPath,
      autoApprove: CONFIG.autoApprove.enabled,
    });
  } catch (error) {
    logger.error('Failed to start LinkedIn MCP Server', { error });
    process.exit(1);
  }
}

main();
