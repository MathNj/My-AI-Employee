# MCP Server Setup Guide

Instructions for building and configuring MCP servers for Meta (Facebook/Instagram) and X (Twitter) platforms.

## Overview

The social-media-manager skill requires three MCP servers:

| Platform | MCP Server | Status | Build Time |
|----------|-----------|--------|------------|
| LinkedIn | linkedin-mcp | ✅ Existing | N/A |
| Facebook + Instagram | meta-mcp | ❌ Needs build | 4-5 hours |
| Twitter/X | x-mcp | ❌ Needs build | 3-4 hours |

---

## Meta MCP Server (Facebook + Instagram)

### Prerequisites

**Required Accounts:**
- Facebook Business Page (not personal profile)
- Instagram Business Account (connected to Facebook Page)
- Meta Developer Account

**Software Requirements:**
- Node.js 18+ or Python 3.11+
- npm or uv (for package management)

### Step 1: Create Meta Developer App

**Navigate to Meta Developer Portal:**
```
https://developers.facebook.com/apps/
```

**Create New App:**
1. Click "Create App"
2. Select use case: "Business"
3. App Display Name: "Personal AI Employee"
4. App Contact Email: your email
5. Click "Create App"

**Note App Credentials:**
- App ID: [copy from dashboard]
- App Secret: [Settings → Basic]

### Step 2: Configure App Permissions

**Add Products:**

**1. Facebook Login**
- Dashboard → Add Product → "Facebook Login"
- Settings → Valid OAuth Redirect URIs:
  ```
  http://localhost:8080/callback
  ```

**2. Instagram Basic Display**
- Dashboard → Add Product → "Instagram Basic Display"
- Configure as above

**Required Permissions:**

**Facebook Permissions:**
- `pages_show_list` - List pages user manages
- `pages_read_engagement` - Read engagement metrics
- `pages_manage_posts` - Create and manage posts
- `pages_manage_metadata` - Edit page metadata

**Instagram Permissions:**
- `instagram_basic` - Basic profile access
- `instagram_content_publish` - Publish content
- `instagram_manage_insights` - Read insights

### Step 3: Get Page and Account IDs

**Facebook Page ID:**
1. Go to your Facebook Page
2. Settings → Page Info
3. Copy "Page ID"

**Instagram Business Account ID:**

**Option A: Graph API Explorer**
```
https://developers.facebook.com/tools/explorer/

Query: me/accounts
Response includes: instagram_business_account { id }
```

**Option B: API Call**
```bash
curl -X GET "https://graph.facebook.com/v18.0/me/accounts?access_token=YOUR_TOKEN"
```

### Step 4: Build Meta MCP Server

**Choose Implementation Language:**

#### Option A: TypeScript Implementation

**Create Project:**
```bash
mkdir meta-mcp
cd meta-mcp
npm init -y
npm install @modelcontextprotocol/sdk axios dotenv
npm install --save-dev @types/node typescript tsx
```

**Create tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

**Create src/index.ts:**
```typescript
#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import axios from "axios";

const META_API_VERSION = "v18.0";
const GRAPH_API_BASE = `https://graph.facebook.com/${META_API_VERSION}`;

interface MetaConfig {
  accessToken: string;
  pageId: string;
  instagramAccountId?: string;
}

class MetaMCPServer {
  private server: Server;
  private config: MetaConfig;

  constructor() {
    this.config = {
      accessToken: process.env.META_ACCESS_TOKEN || "",
      pageId: process.env.META_PAGE_ID || "",
      instagramAccountId: process.env.INSTAGRAM_ACCOUNT_ID,
    };

    this.server = new Server(
      {
        name: "meta-mcp",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
    this.setupErrorHandling();
  }

  private setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "post_to_facebook",
          description: "Post message to Facebook Page",
          inputSchema: {
            type: "object",
            properties: {
              message: {
                type: "string",
                description: "Post content (max 63,206 characters)",
              },
              link: {
                type: "string",
                description: "Optional link to include",
              },
            },
            required: ["message"],
          },
        },
        {
          name: "post_to_instagram",
          description: "Post image with caption to Instagram",
          inputSchema: {
            type: "object",
            properties: {
              image_url: {
                type: "string",
                description: "URL of image to post (publicly accessible)",
              },
              caption: {
                type: "string",
                description: "Post caption (max 2,200 characters)",
              },
            },
            required: ["image_url", "caption"],
          },
        },
        {
          name: "get_facebook_insights",
          description: "Get engagement metrics for Facebook Page",
          inputSchema: {
            type: "object",
            properties: {
              metric: {
                type: "string",
                enum: ["page_impressions", "page_engaged_users", "page_fans"],
                description: "Metric to retrieve",
              },
              period: {
                type: "string",
                enum: ["day", "week", "days_28"],
                description: "Time period",
              },
            },
            required: ["metric"],
          },
        },
        {
          name: "get_instagram_insights",
          description: "Get engagement metrics for Instagram account",
          inputSchema: {
            type: "object",
            properties: {
              metric: {
                type: "string",
                enum: ["impressions", "reach", "profile_views"],
                description: "Metric to retrieve",
              },
              period: {
                type: "string",
                enum: ["day", "week", "days_28"],
                description: "Time period",
              },
            },
            required: ["metric"],
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        const { name, arguments: args } = request.params;

        switch (name) {
          case "post_to_facebook":
            return await this.postToFacebook(args);
          case "post_to_instagram":
            return await this.postToInstagram(args);
          case "get_facebook_insights":
            return await this.getFacebookInsights(args);
          case "get_instagram_insights":
            return await this.getInstagramInsights(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error: any) {
        return {
          content: [{ type: "text", text: `Error: ${error.message}` }],
          isError: true,
        };
      }
    });
  }

  private async postToFacebook(args: any) {
    const { message, link } = args;

    const response = await axios.post(
      `${GRAPH_API_BASE}/${this.config.pageId}/feed`,
      {
        message,
        link,
        access_token: this.config.accessToken,
      }
    );

    return {
      content: [
        {
          type: "text",
          text: `Posted to Facebook successfully. Post ID: ${response.data.id}`,
        },
      ],
    };
  }

  private async postToInstagram(args: any) {
    if (!this.config.instagramAccountId) {
      throw new Error("Instagram Account ID not configured");
    }

    const { image_url, caption } = args;

    // Step 1: Create media container
    const containerResponse = await axios.post(
      `${GRAPH_API_BASE}/${this.config.instagramAccountId}/media`,
      {
        image_url,
        caption,
        access_token: this.config.accessToken,
      }
    );

    const containerId = containerResponse.data.id;

    // Step 2: Publish media
    const publishResponse = await axios.post(
      `${GRAPH_API_BASE}/${this.config.instagramAccountId}/media_publish`,
      {
        creation_id: containerId,
        access_token: this.config.accessToken,
      }
    );

    return {
      content: [
        {
          type: "text",
          text: `Posted to Instagram successfully. Media ID: ${publishResponse.data.id}`,
        },
      ],
    };
  }

  private async getFacebookInsights(args: any) {
    const { metric, period = "day" } = args;

    const response = await axios.get(
      `${GRAPH_API_BASE}/${this.config.pageId}/insights`,
      {
        params: {
          metric,
          period,
          access_token: this.config.accessToken,
        },
      }
    );

    const data = response.data.data[0];
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(data, null, 2),
        },
      ],
    };
  }

  private async getInstagramInsights(args: any) {
    if (!this.config.instagramAccountId) {
      throw new Error("Instagram Account ID not configured");
    }

    const { metric, period = "day" } = args;

    const response = await axios.get(
      `${GRAPH_API_BASE}/${this.config.instagramAccountId}/insights`,
      {
        params: {
          metric,
          period,
          access_token: this.config.accessToken,
        },
      }
    );

    const data = response.data.data[0];
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(data, null, 2),
        },
      ],
    };
  }

  private setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error("[MCP Error]", error);
    };

    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Meta MCP Server running on stdio");
  }
}

const server = new MetaMCPServer();
server.run().catch(console.error);
```

**Update package.json:**
```json
{
  "name": "meta-mcp",
  "version": "1.0.0",
  "type": "module",
  "bin": {
    "meta-mcp": "./dist/index.js"
  },
  "scripts": {
    "build": "tsc",
    "start": "node dist/index.js",
    "dev": "tsx src/index.ts"
  }
}
```

**Build and Test:**
```bash
npm run build
npm start
```

#### Option B: Python Implementation

**Create Project:**
```bash
mkdir meta-mcp
cd meta-mcp
uv init
uv add mcp requests python-dotenv
```

**Create src/meta_mcp/server.py:**
```python
#!/usr/bin/env python3

import os
import asyncio
import requests
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

META_API_VERSION = "v18.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{META_API_VERSION}"

class MetaMCPServer:
    def __init__(self):
        self.access_token = os.getenv("META_ACCESS_TOKEN")
        self.page_id = os.getenv("META_PAGE_ID")
        self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

        if not self.access_token or not self.page_id:
            raise ValueError("META_ACCESS_TOKEN and META_PAGE_ID must be set")

    def get_tools(self) -> list[Tool]:
        return [
            Tool(
                name="post_to_facebook",
                description="Post message to Facebook Page",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Post content (max 63,206 characters)"
                        },
                        "link": {
                            "type": "string",
                            "description": "Optional link to include"
                        }
                    },
                    "required": ["message"]
                }
            ),
            Tool(
                name="post_to_instagram",
                description="Post image with caption to Instagram",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "image_url": {
                            "type": "string",
                            "description": "URL of image to post"
                        },
                        "caption": {
                            "type": "string",
                            "description": "Post caption (max 2,200 characters)"
                        }
                    },
                    "required": ["image_url", "caption"]
                }
            ),
        ]

    async def post_to_facebook(self, message: str, link: str = None):
        data = {
            "message": message,
            "access_token": self.access_token
        }
        if link:
            data["link"] = link

        response = requests.post(
            f"{GRAPH_API_BASE}/{self.page_id}/feed",
            data=data
        )
        response.raise_for_status()

        return [TextContent(
            type="text",
            text=f"Posted to Facebook successfully. Post ID: {response.json()['id']}"
        )]

    async def post_to_instagram(self, image_url: str, caption: str):
        if not self.instagram_account_id:
            raise ValueError("INSTAGRAM_ACCOUNT_ID not configured")

        # Create media container
        container_response = requests.post(
            f"{GRAPH_API_BASE}/{self.instagram_account_id}/media",
            data={
                "image_url": image_url,
                "caption": caption,
                "access_token": self.access_token
            }
        )
        container_response.raise_for_status()
        container_id = container_response.json()["id"]

        # Publish media
        publish_response = requests.post(
            f"{GRAPH_API_BASE}/{self.instagram_account_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": self.access_token
            }
        )
        publish_response.raise_for_status()

        return [TextContent(
            type="text",
            text=f"Posted to Instagram successfully. Media ID: {publish_response.json()['id']}"
        )]

async def main():
    meta_server = MetaMCPServer()

    async with stdio_server() as (read_stream, write_stream):
        server = Server("meta-mcp")

        @server.list_tools()
        async def list_tools() -> list[Tool]:
            return meta_server.get_tools()

        @server.call_tool()
        async def call_tool(name: str, arguments: dict):
            if name == "post_to_facebook":
                return await meta_server.post_to_facebook(**arguments)
            elif name == "post_to_instagram":
                return await meta_server.post_to_instagram(**arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")

        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
```

### Step 5: Configure Environment Variables

**Create .env file:**
```bash
META_ACCESS_TOKEN=your_long_lived_access_token
META_PAGE_ID=your_facebook_page_id
INSTAGRAM_ACCOUNT_ID=your_instagram_business_account_id
```

**Get Long-Lived Access Token:**
1. Go to Graph API Explorer
2. Generate short-lived token
3. Exchange for long-lived token:
```bash
curl -X GET "https://graph.facebook.com/v18.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
```

### Step 6: Configure Claude Code

**Edit ~/.config/claude-code/mcp.json:**
```json
{
  "mcpServers": {
    "meta": {
      "command": "node",
      "args": ["/path/to/meta-mcp/dist/index.js"],
      "env": {
        "META_ACCESS_TOKEN": "${META_ACCESS_TOKEN}",
        "META_PAGE_ID": "${META_PAGE_ID}",
        "INSTAGRAM_ACCOUNT_ID": "${INSTAGRAM_ACCOUNT_ID}"
      }
    }
  }
}
```

**For Python implementation:**
```json
{
  "mcpServers": {
    "meta": {
      "command": "uv",
      "args": ["run", "/path/to/meta-mcp/src/meta_mcp/server.py"],
      "env": {
        "META_ACCESS_TOKEN": "${META_ACCESS_TOKEN}",
        "META_PAGE_ID": "${META_PAGE_ID}",
        "INSTAGRAM_ACCOUNT_ID": "${INSTAGRAM_ACCOUNT_ID}"
      }
    }
  }
}
```

### Step 7: Test Meta MCP

**Test Facebook Posting:**
```bash
# Using Claude Code
claude "Use the meta MCP to post 'Test post from MCP' to Facebook"
```

**Test Instagram Posting:**
```bash
# Need publicly accessible image URL
claude "Use the meta MCP to post to Instagram with image https://example.com/image.jpg and caption 'Test post'"
```

---

## X (Twitter) MCP Server

### Prerequisites

**Required Accounts:**
- X (Twitter) account
- X Developer account with Elevated access

**Software Requirements:**
- Node.js 18+ or Python 3.11+
- npm or uv

### Step 1: Create X Developer Account

**Apply for Developer Account:**
```
https://developer.twitter.com/en/portal/petition/essential/basic-info
```

**Application Details:**
- Purpose: "Business automation and social media management"
- Will you analyze Twitter data: "No"
- Will you display Tweets: "No"
- Use case: Posting original business content

**Approval:** Usually instant to 24 hours

### Step 2: Create X App

**Navigate to Developer Portal:**
```
https://developer.twitter.com/en/portal/dashboard
```

**Create Project and App:**
1. Click "Create Project"
2. Project Name: "Personal AI Employee"
3. Use case: "Making a bot"
4. Description: "Automated social media management"
5. App Name: "AI Employee Bot"

**Note Credentials:**
- API Key (Consumer Key)
- API Secret (Consumer Secret)
- Bearer Token

### Step 3: Enable OAuth 2.0

**App Settings → User Authentication Setup:**

1. Enable OAuth 2.0: Yes
2. Type of App: "Web App"
3. Callback URL: `http://localhost:8080/callback`
4. Website URL: `http://localhost:8080`
5. Permissions:
   - Read and Write
   - Direct Messages (optional)

**Generate Access Tokens:**
- Keys and Tokens tab
- Generate Access Token and Secret
- Save both securely

### Step 4: Build X MCP Server

#### TypeScript Implementation

**Create Project:**
```bash
mkdir x-mcp
cd x-mcp
npm init -y
npm install @modelcontextprotocol/sdk twitter-api-v2 dotenv
npm install --save-dev @types/node typescript tsx
```

**Create src/index.ts:**
```typescript
#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { TwitterApi } from "twitter-api-v2";

class XMCPServer {
  private server: Server;
  private client: TwitterApi;

  constructor() {
    this.client = new TwitterApi({
      appKey: process.env.X_API_KEY || "",
      appSecret: process.env.X_API_SECRET || "",
      accessToken: process.env.X_ACCESS_TOKEN || "",
      accessSecret: process.env.X_ACCESS_SECRET || "",
    });

    this.server = new Server(
      {
        name: "x-mcp",
        version: "1.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
    this.setupErrorHandling();
  }

  private setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
      tools: [
        {
          name: "post_tweet",
          description: "Post a tweet (280 characters max)",
          inputSchema: {
            type: "object",
            properties: {
              text: {
                type: "string",
                description: "Tweet content (max 280 characters)",
                maxLength: 280,
              },
            },
            required: ["text"],
          },
        },
        {
          name: "post_thread",
          description: "Post a Twitter thread (multiple connected tweets)",
          inputSchema: {
            type: "object",
            properties: {
              tweets: {
                type: "array",
                items: { type: "string", maxLength: 280 },
                description: "Array of tweet texts",
              },
            },
            required: ["tweets"],
          },
        },
        {
          name: "get_user_info",
          description: "Get authenticated user's profile information",
          inputSchema: {
            type: "object",
            properties: {},
          },
        },
      ],
    }));

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      try {
        const { name, arguments: args } = request.params;

        switch (name) {
          case "post_tweet":
            return await this.postTweet(args);
          case "post_thread":
            return await this.postThread(args);
          case "get_user_info":
            return await this.getUserInfo();
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error: any) {
        return {
          content: [{ type: "text", text: `Error: ${error.message}` }],
          isError: true,
        };
      }
    });
  }

  private async postTweet(args: any) {
    const { text } = args;

    if (text.length > 280) {
      throw new Error("Tweet exceeds 280 characters");
    }

    const tweet = await this.client.v2.tweet(text);

    return {
      content: [
        {
          type: "text",
          text: `Tweet posted successfully! ID: ${tweet.data.id}`,
        },
      ],
    };
  }

  private async postThread(args: any) {
    const { tweets } = args;

    if (!Array.isArray(tweets) || tweets.length === 0) {
      throw new Error("tweets must be a non-empty array");
    }

    let previousTweetId: string | undefined;
    const results: string[] = [];

    for (const text of tweets) {
      if (text.length > 280) {
        throw new Error(`Tweet exceeds 280 characters: "${text}"`);
      }

      const tweetOptions: any = { text };
      if (previousTweetId) {
        tweetOptions.reply = { in_reply_to_tweet_id: previousTweetId };
      }

      const tweet = await this.client.v2.tweet(tweetOptions);
      previousTweetId = tweet.data.id;
      results.push(tweet.data.id);
    }

    return {
      content: [
        {
          type: "text",
          text: `Thread posted successfully! ${results.length} tweets. First ID: ${results[0]}`,
        },
      ],
    };
  }

  private async getUserInfo() {
    const user = await this.client.v2.me();

    return {
      content: [
        {
          type: "text",
          text: JSON.stringify(user.data, null, 2),
        },
      ],
    };
  }

  private setupErrorHandling() {
    this.server.onerror = (error) => {
      console.error("[MCP Error]", error);
    };

    process.on("SIGINT", async () => {
      await this.server.close();
      process.exit(0);
    });
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("X MCP Server running on stdio");
  }
}

const server = new XMCPServer();
server.run().catch(console.error);
```

### Step 5: Configure Environment Variables

**Create .env file:**
```bash
X_API_KEY=your_api_key
X_API_SECRET=your_api_secret
X_ACCESS_TOKEN=your_access_token
X_ACCESS_SECRET=your_access_secret
```

### Step 6: Configure Claude Code

**Edit ~/.config/claude-code/mcp.json:**
```json
{
  "mcpServers": {
    "x": {
      "command": "node",
      "args": ["/path/to/x-mcp/dist/index.js"],
      "env": {
        "X_API_KEY": "${X_API_KEY}",
        "X_API_SECRET": "${X_API_SECRET}",
        "X_ACCESS_TOKEN": "${X_ACCESS_TOKEN}",
        "X_ACCESS_SECRET": "${X_ACCESS_SECRET}"
      }
    }
  }
}
```

### Step 7: Test X MCP

**Test Single Tweet:**
```bash
claude "Use the x MCP to post 'Test tweet from MCP!'"
```

**Test Thread:**
```bash
claude "Use the x MCP to post a thread with these tweets: ['First tweet 🧵', 'Second tweet in thread', 'Final tweet']"
```

---

## Troubleshooting

### Meta MCP Issues

**Error: "Invalid OAuth access token"**
- Token expired (90 days for long-lived)
- Regenerate token following Step 5
- Update .env file

**Error: "Page not found"**
- Verify META_PAGE_ID is correct
- Check page permissions in Meta Business Suite

**Error: "Instagram account not found"**
- Verify Instagram is Business Account
- Check it's connected to Facebook Page
- Verify INSTAGRAM_ACCOUNT_ID is correct

**Error: "Rate limit exceeded"**
- Facebook: 200 calls/hour per user
- Wait for rate limit reset
- Implement exponential backoff

### X MCP Issues

**Error: "Read-only application"**
- App permissions must be "Read and Write"
- Regenerate access tokens after changing permissions

**Error: "Authentication failed"**
- Verify all 4 credentials in .env
- Check no extra spaces in values
- Regenerate credentials if needed

**Error: "Tweet exceeds 280 characters"**
- Count characters including spaces
- Use thread for longer content
- Consider shortening links

**Error: "Duplicate content"**
- Twitter prevents identical tweets
- Add timestamp or variation
- Wait before retrying

### General MCP Issues

**MCP server not connecting:**
- Check server process running: `ps aux | grep mcp`
- Verify path in mcp.json is absolute
- Check Claude Code logs: `~/.claude/logs/`

**Environment variables not loading:**
- Verify .env file location
- Check variable names match exactly
- Restart Claude Code after changes

---

## Rate Limits Summary

| Platform | Limits | Notes |
|----------|--------|-------|
| Facebook | 200 calls/hour per user | Per access token |
| Instagram | 200 calls/hour per user | Shared with Facebook |
| Twitter/X | 2,400 tweets/day | Standard access |
| Twitter/X | 50 tweets/15 min | Rate limiting window |

**Best Practice:**
- Implement exponential backoff
- Cache responses when possible
- Batch requests where allowed
- Monitor rate limit headers

---

## Security Checklist

- [ ] API keys stored in .env (not in code)
- [ ] .env added to .gitignore
- [ ] Long-lived tokens rotated every 60 days
- [ ] Minimum required permissions only
- [ ] MCP servers run with restricted user permissions
- [ ] Audit logging enabled
- [ ] Regular security reviews scheduled

---

## Next Steps

After building MCP servers:
1. Test all tools independently
2. Create approval workflow integration
3. Test with social-media-manager skill
4. Set up monitoring and logging
5. Document any custom modifications

For detailed usage with social-media-manager skill, see SKILL.md.
