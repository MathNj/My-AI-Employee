/**
 * PM2 Ecosystem Configuration for Personal AI Employee Watchers
 *
 * PM2 is a production-ready process manager for Node.js applications,
 * but it also works excellently with Python scripts.
 *
 * Installation:
 *   npm install -g pm2
 *
 * Usage:
 *   pm2 start ecosystem.config.js            # Start all watchers
 *   pm2 start ecosystem.config.js --only gmail  # Start specific watcher
 *   pm2 stop all                             # Stop all watchers
 *   pm2 restart all                          # Restart all watchers
 *   pm2 logs                                 # View logs
 *   pm2 monit                                # Monitor performance
 *   pm2 status                               # Check status
 *   pm2 save                                 # Save current process list
 *   pm2 startup                              # Generate startup script (run on boot)
 *
 * Features:
 * - Auto-restart on crash
 * - Log management with rotation
 * - Process monitoring
 * - Startup on system boot
 * - Memory and CPU monitoring
 *
 * Author: Personal AI Employee Project
 * Created: 2026-01-12
 */

/**
 * Resolve paths relative to this config file
 */
const path = require('path');
const watchersDir = __dirname;
const vaultDir = path.resolve(__dirname, '..');
const logsDir = path.resolve(vaultDir, 'Logs');

module.exports = {
  apps: [
    {
      // Gmail Watcher - Monitors important emails
      name: 'gmail-watcher',
      script: 'gmail_watcher.py',
      interpreter: 'python3',
      cwd: watchersDir,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      error_file: path.join(logsDir, 'pm2-gmail-error.log'),
      out_file: path.join(logsDir, 'pm2-gmail-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 5000,
    },

    {
      // Filesystem Watcher - Monitors Inbox folder
      name: 'filesystem-watcher',
      script: 'filesystem_watcher.py',
      interpreter: 'python3',
      cwd: watchersDir,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '150M',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      error_file: path.join(logsDir, 'pm2-filesystem-error.log'),
      out_file: path.join(logsDir, 'pm2-filesystem-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 5000,
    },

    {
      // WhatsApp Watcher - Monitors WhatsApp Web
      name: 'whatsapp-watcher',
      script: 'whatsapp_watcher.py',
      interpreter: 'python3',
      cwd: watchersDir,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',  // Higher limit for browser automation
      env: {
        PYTHONUNBUFFERED: '1',
        WHATSAPP_HEADLESS: 'true',
      },
      error_file: path.join(logsDir, 'pm2-whatsapp-error.log'),
      out_file: path.join(logsDir, 'pm2-whatsapp-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 5000,
    },

    {
      // Google Calendar Watcher - Monitors upcoming events
      name: 'calendar-watcher',
      script: 'calendar_watcher.py',
      interpreter: 'python3',
      cwd: watchersDir,
      args: '--interval 300 --hours-ahead 48 --min-hours-ahead 1',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      error_file: path.join(logsDir, 'pm2-calendar-error.log'),
      out_file: path.join(logsDir, 'pm2-calendar-out.log'),
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
      min_uptime: '10s',
      max_restarts: 10,
      restart_delay: 5000,
    },
  ],

  /**
   * Deployment configuration (optional)
   * Uncomment and configure if deploying to remote servers
   */
  // deploy: {
  //   production: {
  //     user: 'username',
  //     host: 'your-server.com',
  //     ref: 'origin/master',
  //     repo: 'git@github.com:username/ai-employee.git',
  //     path: '/home/username/ai-employee',
  //     'post-deploy': 'pip install -r requirements.txt && pm2 reload ecosystem.config.js',
  //   },
  // },
};

/**
 * Quick Reference Commands
 * ========================
 *
 * Start all watchers:
 *   pm2 start ecosystem.config.js
 *
 * Start specific watcher:
 *   pm2 start ecosystem.config.js --only gmail-watcher
 *   pm2 start ecosystem.config.js --only filesystem-watcher
 *   pm2 start ecosystem.config.js --only whatsapp-watcher
 *   pm2 start ecosystem.config.js --only calendar-watcher
 *
 * Stop all:
 *   pm2 stop all
 *
 * Stop specific:
 *   pm2 stop gmail-watcher
 *
 * Restart all:
 *   pm2 restart all
 *
 * Delete all (remove from PM2):
 *   pm2 delete all
 *
 * View logs:
 *   pm2 logs                    # All logs
 *   pm2 logs gmail-watcher      # Specific watcher
 *   pm2 logs --lines 100        # Last 100 lines
 *
 * Monitor:
 *   pm2 monit                   # Real-time monitoring
 *   pm2 status                  # Status table
 *   pm2 info gmail-watcher      # Detailed info
 *
 * Save configuration (persist across reboots):
 *   pm2 save
 *   pm2 startup                 # Generate startup script
 *
 * Update PM2:
 *   pm2 update
 *
 * Flush logs:
 *   pm2 flush
 */
