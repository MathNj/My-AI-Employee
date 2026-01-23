#!/usr/bin/env python3
"""
WhatsApp MCP Server

Model Context Protocol server for WhatsApp messaging.
Provides tools to send WhatsApp messages via Playwright automation.

Features:
- Send text messages to individuals and groups
- Human-in-the-Loop approval workflow integration
- Persistent browser session (shares with WhatsApp watcher)
- Comprehensive error handling and retry logic
- Detailed audit logging
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Optional

# Import WhatsApp sender
try:
    from whatsapp_sender import WhatsAppSender
    WHATSAPP_SENDER_AVAILABLE = True
except ImportError:
    WHATSAPP_SENDER_AVAILABLE = False
    print("ERROR: whatsapp_sender not available", file=sys.stderr)
    sys.exit(1)

# Setup logging
LOG_PATH = Path(__file__).parent / 'logs'
LOG_PATH.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - WhatsAppMCP - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH / 'whatsapp-mcp.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)


class WhatsAppMCPServer:
    """WhatsApp MCP Server implementation"""

    def __init__(self):
        """Initialize MCP server"""
        self.sender = None
        logger.info("WhatsApp MCP Server initialized")

    def _get_sender(self) -> WhatsAppSender:
        """Get or initialize WhatsApp sender"""
        if self.sender is None:
            self.sender = WhatsAppSender(
                session_path=None,  # Use default (same as watcher)
                headless=True  # Run in headless mode
            )
        return self.sender

    def send_message(self, arguments: dict) -> dict:
        """
        Send a WhatsApp message.

        Args:
            arguments: Dict containing:
                - to (str, required): Contact name or group name
                - message (str, required): Message content to send

        Returns:
            Result dict with success status and details
        """
        try:
            # Validate arguments
            to = arguments.get('to')
            message = arguments.get('message')

            if not to:
                return {
                    'success': False,
                    'error': 'Missing required parameter: to'
                }

            if not message:
                return {
                    'success': False,
                    'error': 'Missing required parameter: message'
                }

            logger.info(f"Sending WhatsApp message to: {to}")

            # Get sender and send message
            sender = self._get_sender()
            result = sender.send_message(to=to, message=message)

            if result['success']:
                logger.info(f"Message sent successfully to {to}")
                return {
                    'success': True,
                    'data': result
                }
            else:
                logger.error(f"Failed to send message: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }

        except Exception as e:
            logger.error(f"Error in send_message: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    def cleanup(self):
        """Clean up resources"""
        if self.sender:
            self.sender.cleanup()
            self.sender = None


def main():
    """Main MCP server loop"""
    server = WhatsAppMCPServer()

    logger.info("WhatsApp MCP Server started")
    logger.info("Waiting for requests...")

    try:
        # Read from stdin, write to stdout (MCP protocol)
        while True:
            line = sys.stdin.readline()
            if not line:
                break

            try:
                # Parse JSON-RPC request
                request = json.loads(line)

                # Process request
                response = None

                if request.get('method') == 'tools/call':
                    # Handle tool call
                    params = request.get('params', {})
                    tool_name = params.get('name')
                    arguments = params.get('arguments', {})

                    logger.info(f"Tool call: {tool_name}")

                    if tool_name == 'send_whatsapp_message':
                        result = server.send_message(arguments)

                        response = {
                            'jsonrpc': '2.0',
                            'id': request.get('id'),
                            'result': {
                                'content': [
                                    {
                                        'type': 'text',
                                        'text': json.dumps(result, indent=2)
                                    }
                                ]
                            }
                        }
                    else:
                        response = {
                            'jsonrpc': '2.0',
                            'id': request.get('id'),
                            'error': {
                                'code': -32601,
                                'message': f'Unknown tool: {tool_name}'
                            }
                        }

                elif request.get('method') == 'tools/list':
                    # List available tools
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'result': {
                            'tools': [
                                {
                                    'name': 'send_whatsapp_message',
                                    'description': 'Send a WhatsApp message to a contact or group',
                                    'inputSchema': {
                                        'type': 'object',
                                        'properties': {
                                            'to': {
                                                'type': 'string',
                                                'description': 'Contact name or group name'
                                            },
                                            'message': {
                                                'type': 'string',
                                                'description': 'Message content to send'
                                            }
                                        },
                                        'required': ['to', 'message']
                                    }
                                }
                            ]
                        }
                    }

                else:
                    # Unknown method
                    response = {
                        'jsonrpc': '2.0',
                        'id': request.get('id'),
                        'error': {
                            'code': -32601,
                            'message': f'Method not found: {request.get("method")}'
                        }
                    }

                # Send response
                if response:
                    sys.stdout.write(json.dumps(response) + '\n')
                    sys.stdout.flush()

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                continue

    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    finally:
        server.cleanup()
        logger.info("WhatsApp MCP Server stopped")


if __name__ == "__main__":
    main()
