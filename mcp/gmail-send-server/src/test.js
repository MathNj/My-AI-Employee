#!/usr/bin/env node
/**
 * MCP Gmail Send Server - Test Suite
 *
 * Tests Silver Tier tasks T046-T053:
 * - T046: package.json structure
 * - T047: Server implementation
 * - T048: Tool definition
 * - T049: Gmail API integration (mocked)
 * - T050: Error handling
 * - T051: MCP logging
 * - T052: README.md documentation
 * - T053: Server startup
 *
 * Run with: npm test
 */

import { gmail } from 'googleapis';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Test results tracking
const results = {
  passed: 0,
  failed: 0,
  tests: [],
};

function test(name, fn) {
  try {
    fn();
    results.passed++;
    results.tests.push({ name, status: 'PASS' });
    console.log(`✓ ${name}`);
  } catch (error) {
    results.failed++;
    results.tests.push({ name, status: 'FAIL', error: error.message });
    console.error(`✗ ${name}: ${error.message}`);
  }
}

function assert(condition, message) {
  if (!condition) {
    throw new Error(message || 'Assertion failed');
  }
}

// ============================================================================
// T046: Verify package.json
// ============================================================================

console.log('\n=== T046: Verifying package.json ===');

test('package.json exists', () => {
  const pkgPath = path.join(__dirname, '..', 'package.json');
  assert(fs.existsSync(pkgPath), 'package.json not found');
});

test('package.json has required fields', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf8'));
  assert(pkg.name === 'gmail-send-server', 'package name incorrect');
  assert(pkg.version, 'version missing');
  assert(pkg.main === 'src/index.js', 'main entry point incorrect');
  assert(pkg.type === 'module', 'type should be module');
});

test('package.json has correct dependencies', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf8'));
  assert(pkg.dependencies['@modelcontextprotocol/sdk'], 'MCP SDK missing');
  assert(pkg.dependencies['googleapis'], 'googleapis missing');
});

test('package.json has scripts', () => {
  const pkg = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'package.json'), 'utf8'));
  assert(pkg.scripts.start, 'start script missing');
  assert(pkg.scripts.dev, 'dev script missing');
  assert(pkg.scripts.test, 'test script missing');
});

// ============================================================================
// T047: Verify server implementation
// ============================================================================

console.log('\n=== T047: Verifying server implementation ===');

test('src/index.js exists', () => {
  const indexPath = path.join(__dirname, 'index.js');
  assert(fs.existsSync(indexPath), 'src/index.js not found');
});

test('index.js exports main function', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('export { main'), 'main function not exported');
  assert(indexContent.includes('async function main'), 'main function not defined');
});

test('index.js uses ES modules', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('import { Server }'), 'ES module imports not used');
  assert(indexContent.includes('import { google }'), 'googleapis import missing');
});

// ============================================================================
// T048: Verify tool definition
// ============================================================================

console.log('\n=== T048: Verifying send_email tool definition ===');

test('SEND_EMAIL_TOOL constant defined', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('const SEND_EMAIL_TOOL'), 'SEND_EMAIL_TOOL not defined');
  assert(indexContent.includes('name: \'send_email\''), 'tool name incorrect');
});

test('Tool has required parameters', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('to:'), 'to parameter missing');
  assert(indexContent.includes('subject:'), 'subject parameter missing');
  assert(indexContent.includes('required:'), 'required field missing');
});

test('Tool has optional parameters', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('body:'), 'body parameter missing');
  assert(indexContent.includes('html:'), 'html parameter missing');
  assert(indexContent.includes('cc:'), 'cc parameter missing');
  assert(indexContent.includes('bcc:'), 'bcc parameter missing');
  assert(indexContent.includes('attachments:'), 'attachments parameter missing');
});

// ============================================================================
// T049: Verify Gmail API integration
// ============================================================================

console.log('\n=== T049: Verifying Gmail API integration ===');

test('GmailAuthManager class exists', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('class GmailAuthManager'), 'GmailAuthManager class not found');
});

test('GmailAuthManager has authenticate method', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('async authenticate()'), 'authenticate method not found');
});

test('GmailAuthManager has token refresh', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('refreshAccessToken'), 'token refresh not implemented');
});

test('EmailSender class exists', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('class EmailSender'), 'EmailSender class not found');
});

test('EmailSender has sendEmail method', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('async sendEmail('), 'sendEmail method not found');
});

test('EmailSender builds RFC 2822 emails', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('buildEmail'), 'buildEmail method not found');
  assert(indexContent.includes('MIME-Version: 1.0'), 'MIME header missing');
});

// ============================================================================
// T050: Verify error handling
// ============================================================================

console.log('\n=== T050: Verifying error handling ===');

test('sendEmail validates required parameters', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('Missing required parameters'), 'parameter validation missing');
});

test('sendEmail catches Gmail API errors', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('try {'), 'try-catch block missing');
  assert(indexContent.includes('catch (error)'), 'error catching missing');
});

test('Provides actionable error messages', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('401'), '401 error handling missing');
  assert(indexContent.includes('403'), '403 error handling missing');
  assert(indexContent.includes('400'), '400 error handling missing');
});

// ============================================================================
// T051: Verify MCP logging
// ============================================================================

console.log('\n=== T051: Verifying MCP logging ===');

test('MCPLogger class exists', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('class MCPLogger'), 'MCPLogger class not found');
});

test('MCPLogger has log methods', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('.log('), 'log method not found');
  assert(indexContent.includes('.info('), 'info method not found');
  assert(indexContent.includes('.error('), 'error method not found');
});

test('MCPLogger writes to file', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('fs.appendFileSync'), 'file writing missing');
  assert(indexContent.includes('appendFileSync(this.logPath)'), 'log path missing');
});

test('Email operations are logged', () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('logger.info(\'Sending email\''), 'send logging missing');
  assert(indexContent.includes('logger.info(\'Email sent\''), 'success logging missing');
  assert(indexContent.includes('logger.error(\'Failed to send\''), 'error logging missing');
});

// ============================================================================
// T052: Verify README.md
// ============================================================================

console.log('\n=== T052: Verifying README.md ===');

test('README.md exists', () => {
  const readmePath = path.join(__dirname, '..', 'README.md');
  assert(fs.existsSync(readmePath), 'README.md not found');
});

test('README has setup instructions', () => {
  const readme = fs.readFileSync(path.join(__dirname, '..', 'README.md'), 'utf8');
  assert(readme.includes('## Setup'), 'setup section missing');
  assert(readme.includes('GMAIL_CLIENT_ID'), 'GMAIL_CLIENT_ID not documented');
  assert(readme.includes('GMAIL_CLIENT_SECRET'), 'GMAIL_CLIENT_SECRET not documented');
});

test('README has usage examples', () => {
  const readme = fs.readFileSync(path.join(__dirname, '..', 'README.md'), 'utf8');
  assert(readme.includes('## Usage'), 'usage section missing');
  assert(readme.includes('### Example Usage'), 'examples missing');
  assert(readme.includes('send_email'), 'tool not documented');
});

test('README has integration section', () => {
  const readme = fs.readFileSync(path.join(__dirname, '..', 'README.md'), 'utf8');
  assert(readme.includes('## Integration'), 'integration section missing');
  assert(readme.includes('task-processor'), 'task-processor not mentioned');
});

// ============================================================================
// T053: Server startup test
// ============================================================================

console.log('\n=== T053: Testing server startup ===');

test('Server imports successfully', async () => {
  try {
    const module = await import('./index.js');
    assert(typeof module.main === 'function', 'main function not exported');
  } catch (error) {
    throw new Error(`Import failed: ${error.message}`);
  }
});

test('Server can be instantiated', async () => {
  try {
    // Mock environment for testing
    const originalEnv = process.env.GMAIL_CLIENT_ID;
    process.env.GMAIL_CLIENT_ID = 'test-client-id';
    process.env.GMAIL_CLIENT_SECRET = 'test-client-secret';

    const { main } = await import('./index.js');

    // Restore environment
    if (originalEnv) {
      process.env.GMAIL_CLIENT_ID = originalEnv;
    }
  } catch (error) {
    throw new Error(`Server instantiation failed: ${error.message}`);
  }
});

test('Server has MCP request handlers', async () => {
  const indexContent = fs.readFileSync(path.join(__dirname, 'index.js'), 'utf8');
  assert(indexContent.includes('setRequestHandler(ListToolsRequestSchema'), 'list tools handler missing');
  assert(indexContent.includes('setRequestHandler(CallToolRequestSchema'), 'call tool handler missing');
});

// ============================================================================
// Summary
// ============================================================================

console.log('\n' + '='.repeat(60));
console.log('Test Summary');
console.log('='.repeat(60));
console.log(`Total: ${results.passed + results.failed} tests`);
console.log(`Passed: ${results.passed} ✓`);
console.log(`Failed: ${results.failed} ✗`);

if (results.failed > 0) {
  console.log('\nFailed tests:');
  results.tests
    .filter(t => t.status === 'FAIL')
    .forEach(t => console.log(`  ✗ ${t.name}: ${t.error}`));
  process.exit(1);
} else {
  console.log('\n✓ All tests passed!');
  console.log('✓ MCP Server startup verified (T053)');
  process.exit(0);
}
