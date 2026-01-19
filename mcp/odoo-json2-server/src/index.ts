import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import axios from 'axios';
import dotenv from 'dotenv';

dotenv.config();

// Odoo configuration
const ODOO_CONFIG = {
  url: process.env.ODOO_URL || 'http://localhost:8069',
  database: process.env.ODOO_DATABASE || 'ai_employee',
  apiKey: process.env.ODOO_API_KEY || '',
};

// Odoo client for External JSON-2 API
class OdooJSON2Client {
  private baseUrl: string;
  private headers: any;

  constructor(config: typeof ODOO_CONFIG) {
    this.baseUrl = config.url.replace(/\/$/, ''); // Remove trailing slash
    this.headers = {
      'Authorization': `bearer ${config.apiKey}`,
      'X-Odoo-Database': config.database,
      'Content-Type': 'application/json',
      'User-Agent': 'ai-employee-odoo-json2-server/1.0.0',
    };
  }

  async call(model: string, method: string, data: any = {}): Promise<any> {
    try {
      const url = `${this.baseUrl}/json/2/${model}/${method}`;
      const response = await axios.post(url, data, {
        headers: this.headers,
        timeout: 10000,
      });

      if (response.status !== 200) {
        throw new Error(`Odoo API error: ${response.status} ${response.statusText}`);
      }

      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(`Odoo API error: ${error.response.status} ${JSON.stringify(error.response.data)}`);
      }
      throw error;
    }
  }

  // Accounting operations
  async createInvoice(data: InvoiceData): Promise<number> {
    const result = await this.call('account.move', 'create', {
      values: {
        move_type: 'out_invoice',
        partner_id: data.customerId,
        invoice_date: data.invoiceDate || new Date().toISOString().split('T')[0],
        invoice_line_ids: data.items.map(item => [
          0, 0, {
            product_id: item.productId,
            quantity: item.quantity,
            price_unit: item.priceUnit,
          }
        ])
      }
    });
    return result.id;
  }

  async createBill(data: BillData): Promise<number> {
    const result = await this.call('account.move', 'create', {
      values: {
        move_type: 'in_invoice',
        partner_id: data.vendorId,
        invoice_date: data.billDate || new Date().toISOString().split('T')[0],
        invoice_line_ids: data.items.map(item => [
          0, 0, {
            product_id: item.productId,
            quantity: item.quantity,
            price_unit: item.priceUnit,
          }
        ])
      }
    });
    return result.id;
  }

  async recordPayment(data: PaymentData): Promise<number> {
    const result = await this.call('account.payment', 'create', {
      values: {
        amount: data.amount,
        payment_type: 'inbound',
        partner_type: 'customer',
        payment_method_line_id: data.paymentMethodId,
        invoice_ids: [[6, 0, [data.invoiceId]]
      }
    });
    return result.id;
  }

  async reconcileBank(statementLineIds: number[]): Promise<void> {
    await this.call('account.bank.statement.line', 'reconcile', {
      ids: statementLineIds
    });
  }

  async searchInvoices(domain: any[], fields: string[] = [], limit = 20): Promise<any[]> {
    return await this.call('account.move', 'search_read', {
      context: {lang: 'en_US'},
      domain: domain,
      fields: fields.length > 0 ? fields : ['id', 'name', 'amount_total', 'invoice_date', 'state'],
      order: 'invoice_date desc',
      limit: limit
    });
  }

  async getInvoice(invoiceId: number): Promise<any> {
    const results = await this.call('account.move', 'read', {
      ids: [invoiceId],
      context: {lang: 'en_US'}
    });
    return results[0];
  }

  async generateReport(reportType: string, dateFrom?: string, dateTo?: string): Promise<any> {
    const domain: any[] = [['state', '=', 'posted']];

    if (dateFrom) {
      domain.push(['date', '>=', dateFrom]);
    }

    if (dateTo) {
      domain.push(['date', '<=', dateTo]);
    }

    let model = 'account.move';
    let fields = ['id', 'date', 'amount_total', 'move_type'];

    if (reportType === 'profit_loss') {
      model = 'account.move.line';
      fields = ['id', 'date', 'debit', 'credit', 'account_id'];
    } else if (reportType === 'balance_sheet') {
      model = 'account.account';
      fields = ['id', 'code', 'name', 'current_balance'];
    }

    return await this.call(model, 'search_read', {
      context: {lang: 'en_US'},
      domain: domain,
      fields: fields,
      order: 'date desc'
    });
  }

  async queryAccounts(accountType?: string): Promise<any> {
    const domain: any[] = [];

    if (accountType && accountType === 'vendor') {
      domain.push(['supplier_rank', '>', 0]);
    }

    const results = await this.call('res.partner', 'search_read', {
      context: {lang: 'en_US'},
      domain: domain,
      fields: ['id', 'name', 'email', 'phone', 'supplier_rank', 'customer_rank']
    });

    return {
      success: true,
      partners: results
    };
  }
}

// Type definitions
interface InvoiceData {
  customerId: number;
  items: InvoiceItem[];
  invoiceDate?: string;
}

interface InvoiceItem {
  productId: number;
  quantity: number;
  priceUnit: number;
}

interface BillData {
  vendorId: number;
  items: InvoiceItem[];
  billDate?: string;
}

interface PaymentData {
  amount: number;
  paymentMethodId: number;
  invoiceId: number;
}

// MCP Server
class OdooJSON2MCPServer {
  private server: Server;
  private odooClient: OdooJSON2Client;

  constructor() {
    this.server = new Server(
      {
        name: 'odoo-json2-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.odooClient = new OdooJSON2Client(ODOO_CONFIG);
  }

  async start(): Promise<void> {
    // Register tools
    await this.registerTools();

    // Connect to transport
    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    console.error('[ODOO MCP] Server running on stdio');
  }

  private async registerTools(): Promise<void> {
    // List tools
    this.server.setRequestHandler('tools/list', async () => ({
      tools: [
        {
          name: 'create_invoice',
          description: 'Create a customer invoice in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              customerId: {
                type: 'number',
                description: 'Customer partner ID'
              },
              items: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    productId: {type: 'number'},
                    quantity: {type: 'number'},
                    priceUnit: {type: 'number'}
                  }
                }
              }
            },
            required: ['customerId', 'items']
          }
        },
        {
          name: 'create_bill',
          description: 'Create a vendor bill in Odoo',
          inputSchema: {
            type: 'object',
            properties: {
              vendorId: {
                type: 'number',
                description: 'Vendor partner ID'
              },
              items: {
                type: 'array',
                items: {
                  type: 'object',
                  properties: {
                    productId: {type: 'number'},
                    quantity: {type: 'number'},
                    priceUnit: {type: 'number'}
                  }
                }
              }
            },
            required: ['vendorId', 'items']
          }
        },
        {
          name: 'record_payment',
          description: 'Record a payment for an invoice',
          inputSchema: {
            type: 'object',
            properties: {
              amount: {type: 'number'},
              paymentMethodId: {type: 'number'},
              invoiceId: {type: 'number'}
            },
            required: ['amount', 'paymentMethodId', 'invoiceId']
          }
        },
        {
          name: 'reconcile_bank',
          description: 'Reconcile bank statement lines',
          inputSchema: {
            type: 'object',
            properties: {
              statementLineIds: {
                type: 'array',
                items: {type: 'number'}
              }
            },
            required: ['statementLineIds']
          }
        },
        {
          name: 'search_invoices',
          description: 'Search for invoices with domain filter',
          inputSchema: {
            type: 'object',
            properties: {
              domain: {
                type: 'array',
                description: 'Odoo domain filter'
              },
              fields: {
                type: 'array',
                items: {type: 'string'}
              },
              limit: {type: 'number'}
            }
          }
        },
        {
          name: 'get_invoice',
          description: 'Get invoice details by ID',
          inputSchema: {
            type: 'object',
            properties: {
              invoiceId: {type: 'number'}
            },
            required: ['invoiceId']
          }
        },
        {
          name: 'generate_report',
          description: 'Generate financial reports',
          inputSchema: {
            type: 'object',
            properties: {
              reportType: {
                type: 'string',
                enum: ['profit_loss', 'balance_sheet', 'aged_receivables']
              },
              dateFrom: {type: 'string'},
              dateTo: {type: 'string'}
            },
            required: ['reportType']
          }
        },
        {
          name: 'query_accounts',
          description: 'Query chart of accounts',
          inputSchema: {
            type: 'object',
            properties: {
              accountType: {type: 'string'}
            }
          }
        }
      ]
    }));

    // Handle tool calls
    this.server.setRequestHandler('tools/call', async (request) => {
      const { name, arguments: args } = request.params;

      try {
        let result;

        switch (name) {
          case 'create_invoice':
            result = await this.createInvoice(args);
            break;
          case 'create_bill':
            result = await this.createBill(args);
            break;
          case 'record_payment':
            result = await this.recordPayment(args);
            break;
          case 'reconcile_bank':
            result = await this.reconcileBank(args);
            break;
          case 'search_invoices':
            result = await this.searchInvoices(args);
            break;
          case 'get_invoice':
            result = await this.getInvoice(args);
            break;
          case 'generate_report':
            result = await this.generateReport(args);
            break;
          case 'query_accounts':
            result = await this.queryAccounts(args);
            break;
          default:
            throw new Error(`Unknown tool: ${name}`);
        }

        // Log action
        this.logAction(name, args, result);

        return {
          content: [{type: 'text', text: JSON.stringify(result, null, 2)}]
        };
      } catch (error) {
        console.error(`[ODOO MCP] Error in ${name}:`, error);

        // Return error response
        return {
          content: [{type: 'text', text: JSON.stringify({
            error: error instanceof Error ? error.message : String(error),
            tool: name,
            retry_possible: true,
            suggested_action: 'Check Odoo connection and authentication'
          }, null, 2)}],
          isError: true
        };
      }
    });
  }

  private async createInvoice(args: any): Promise<any> {
    const result = await this.odooClient.createInvoice(args);
    return {
      success: true,
      invoice_id: result,
      message: `Invoice created with ID: ${result}`
    };
  }

  private async createBill(args: any): Promise<any> {
    const result = await this.odooClient.createBill(args);
    return {
      success: true,
      bill_id: result,
      message: `Bill created with ID: ${result}`
    };
  }

  private async recordPayment(args: any): Promise<any> {
    const result = await this.odooClient.recordPayment(args);
    return {
      success: true,
      payment_id: result,
      message: `Payment recorded with ID: ${result}`
    };
  }

  private async reconcileBank(args: any): Promise<any> {
    await this.odooClient.reconcileBank(args.statementLineIds);
    return {
      success: true,
      reconciled_count: args.statementLineIds.length,
      message: `Reconciled ${args.statementLineIds.length} statement lines`
    };
  }

  private async searchInvoices(args: any): Promise<any> {
    const results = await this.odooClient.searchInvoices(
      args.domain || [],
      args.fields || [],
      args.limit || 20
    );
    return {
      success: true,
      invoices: results,
      count: results.length
    };
  }

  private async getInvoice(args: any): Promise<any> {
    const result = await this.odooClient.getInvoice(args.invoiceId);
    return {
      success: true,
      invoice: result
    };
  }

  private async generateReport(args: any): Promise<any> {
    const results = await this.odooClient.generateReport(
      args.reportType,
      args.dateFrom,
      args.dateTo
    );
    return {
      success: true,
      report_type: args.reportType,
      data: results
    };
  }

  private async queryAccounts(args: any): Promise<any> {
    const results = await this.odooClient.queryAccounts(args.accountType);
    return {
      success: true,
      partners: results.partners
    };
  }

  private logAction(toolName: string, inputArgs: any, result: any): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      action_type: toolName,
      input_params: inputArgs,
      output_result: result,
      source: 'odoo_json2_mcp_server'
    };

    const logPath = '/Logs/odoo_actions_2026-01-17.json';
    const fs = require('fs');
    fs.appendFileSync(logPath, JSON.stringify(logEntry) + '\n');
  }
}

// Start server
const server = new OdooJSON2MCPServer();
server.start().catch(console.error);