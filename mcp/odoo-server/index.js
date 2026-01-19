#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const CONFIG = {
  ODOO_URL: process.env.ODOO_URL || 'http://localhost:8069',
  ODOO_DB: process.env.ODOO_DB || 'odoo',
  ODOO_API_KEY: process.env.ODOO_API_KEY || '',
};

async function odoo_get_status() {
  const response = await fetch(CONFIG.ODOO_URL + '/web?db=' + CONFIG.ODOO_DB);
  return {
    status: response.ok ? 'connected' : 'disconnected',
    url: CONFIG.ODOO_URL,
    database: CONFIG.ODOO_DB,
  };
}

async function odoo_list_models() {
  return {
    models: ['res.partner', 'account.move', 'account.payment', 'account.bank.statement'],
    info: 'Odoo External JSON-2 API uses /json/2/<model>/<method>'
  };
}

async function odoo_search_customers(args) {
  const params = {
    domain: [
      ['name', 'ilike', args.query],
      ['email', 'ilike', args.query]
    ],
    fields: ['id', 'name', 'email', 'phone', 'street', 'city']
  };

  const response = await fetch(CONFIG.ODOO_URL + '/json/2/res.partner/search_read', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + CONFIG.ODOO_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  const result = await response.json();
  return {
    results: result.results || result.data || [],
    count: result.count || 0
  };
}

async function odoo_create_customer(args) {
  const data = {
    name: args.name,
    email: args.email,
    type: 'contact',
    is_company: false,
    street: args.street || '',
    city: args.city || '',
    zip: args.zip || '',
    country_id: args.country_code || 'US'
  };

  const response = await fetch(CONFIG.ODOO_URL + '/json/2/res.partner/create', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + CONFIG.ODOO_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data }),
  });

  const result = await response.json();
  return { success: true, customer_id: result.id, customer_name: result.name };
}

async function odoo_get_invoice_status(args) {
  const params = {
    domain: [['id', '=', args.invoice_id]],
    fields: ['id', 'name', 'state', 'amount_total', 'payment_status']
  };

  const response = await fetch(CONFIG.ODOO_URL + '/json/2/account.move/search_read', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + CONFIG.ODOO_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(params),
  });

  const result = await response.json();
  const invoice = result.results?.[0] || result.data?.[0] || null;

  if (invoice) {
    return {
      invoice_id: invoice.id,
      name: invoice.name,
      state: invoice.state,
      amount_total: invoice.amount_total,
      payment_status: invoice.payment_status
    };
  }

  throw new Error('Invoice not found');
}

async function odoo_create_invoice(args) {
  const data = {
    partner_id: args.partner_id,
    move_type: 'out_invoice',
    journal_type: 'sale',
    invoice_line_ids: args.invoice_lines.map(l => [0, 0, {
      product_id: l.product_id,
      quantity: l.quantity,
      price_unit: l.price_unit,
    }])
  };

  const response = await fetch(CONFIG.ODOO_URL + '/json/2/account.move/create', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + CONFIG.ODOO_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data }),
  });

  const result = await response.json();
  return { success: true, invoice_id: result.id };
}

async function odoo_create_bill(args) {
  const data = {
    partner_id: args.partner_id,
    move_type: 'in_invoice',
    journal_type: 'purchase',
    invoice_line_ids: args.bill_lines.map(l => [0, 0, {
      product_id: l.product_id,
      quantity: l.quantity,
      price_unit: l.price_unit
    }])
  };

  const response = await fetch(CONFIG.ODOO_URL + '/json/2/account.move/create', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + CONFIG.ODOO_DATA_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data }),
  });

  const result = await response.json();
  return { success: true, bill_id: result.id };
}

async function odoo_record_payment(args) {
  const data = {
    amount: args.amount,
    payment_type: args.payment_type,
    partner_id: args.partner_id,
    journal_id: args.journal_id,
    move_id: args.move_id
  };

  const response = await fetch(CONFIG.ODOO_URL + '/json/2/account.payment/create', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + CONFIG.ODOO_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data }),
  });

  const result = await response.json();
  return { success: true, payment_id: result.id };
}

async function main() {
  const server = new Server({
    name: 'odoo-mcp-server',
    version: '1.0.0',
  }, {
    capabilities: {}
  });

  server.setRequestHandler(async () => ({
    tools: [
      {
        name: 'odoo_get_status',
        description: 'Get Odoo connection status',
        inputSchema: { type: 'object', properties: {} }
      },
      {
        name: 'odoo_list_models',
        description: 'List available Odoo models',
        inputSchema: { type: 'object', properties: {} }
      },
      {
        name: 'odoo_search_customers',
        description: 'Search customers by name or email',
        inputSchema: {
          type: 'object',
          properties: {
            query: { type: 'string' }
          },
          required: ['query']
        }
      },
      {
        name: 'odoo_get_invoice_status',
        description: 'Get invoice status',
        inputSchema: {
          type: 'object',
          properties: {
            invoice_id: { type: 'integer' }
          },
          required: ['invoice_id']
        }
      },
      {
        name: 'odoo_create_customer',
        description: 'Create customer in Odoo',
        inputSchema: {
          type: 'object',
          properties: {
            name: { type: 'string' },
            email: { type: 'string' }
          },
          required: ['name', 'email']
        }
      },
      {
        name: 'odoo_create_invoice',
        description: 'Create customer invoice',
        inputSchema: {
          type: 'object',
          properties: {
            partner_id: { type: 'integer' },
            lines: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  product_id: { type: 'integer' },
                  quantity: { type: 'number' },
                  price_unit: { type: 'number' }
                }
              }
            }
          },
          required: ['partner_id', 'lines']
        }
      },
      {
        name: 'odoo_create_bill',
        description: 'Create vendor bill',
        inputSchema: {
          type: 'object',
          properties: {
            partner_id: { type: 'integer' },
            lines: {
              type: 'array',
              items: {
                type: 'object',
                properties: {
                  product_id: { type: 'integer' },
                  quantity: { type: 'number' },
                  price_unit: { type: 'number' }
                }
              }
            }
          },
          required: ['partner_id', 'lines']
        }
      },
      {
        name: 'odoo_record_payment',
        description: 'Record payment',
        inputSchema: {
          type: 'object',
          properties: {
            amount: { type: 'number' },
            payment_type: { type: 'string' },
            partner_id: { type: 'integer' },
            journal_id: { type: 'integer' },
            move_id: { type: 'integer' }
          },
          required: ['amount', 'payment_type', 'partner_id', 'journal_id', 'move_id']
        }
      }
    ]
  }));

  server.setRequestHandler(async (request) => {
    const { name, arguments } = request.params;
    const args = JSON.parse(arguments || '{}');

    try {
      switch (name) {
        case 'odoo_get_status':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_get_status(), null, 2) }] };

        case 'odoo_list_models':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_list_models(), null, 2) }];

        case 'odoo_search_customers':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_search_customers(args), null, 2) }];

        case 'odoo_get_invoice_status':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_get_invoice_status(args), null, 2) }];

        case 'odoo_create_customer':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_create_customer(args), null, 2) }];

        case 'odoo_create_invoice':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_create_invoice(args), null, 2) }];

        case 'odoo_create_bill':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_create_bill(args), null, 2) }];

        case 'odoo_record_payment':
          return { content: [{ type: 'text', text: JSON.stringify(await odoo_record_payment(args), null, 2) }];

        default:
          throw new Error(`Unknown tool: ${name}`);
      }
    } catch (error) {
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({ success: false, error: error.message }, null, 2),
        }],
        isError: true
      };
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Odoo MCP Server running');
  console.error('Tools: odoo_get_status, odoo_list_models, odoo_search_customers, odoo_get_invoice_status, odoo_create_customer, odoo_create_invoice, odoo_create_bill, odoo_record_payment');
}

main().catch((error) => {
  console.error('Error:', error);
  process.exit(1);
}