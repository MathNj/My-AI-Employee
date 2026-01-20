/**
 * PM2 Ecosystem Configuration for Windows
 */

module.exports = {
  apps: [
    {
      name: 'gmail-watcher',
      script: 'gmail_watcher.py',
      interpreter: 'python',
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      error_file: '../Logs/pm2-gmail-error.log',
      out_file: '../Logs/pm2-gmail-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
    },
    {
      name: 'filesystem-watcher',
      script: 'filesystem_watcher.py',
      interpreter: 'python',
      cwd: __dirname,
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '150M',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      error_file: '../Logs/pm2-filesystem-error.log',
      out_file: '../Logs/pm2-filesystem-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
    },
    {
      name: 'calendar-watcher',
      script: 'calendar_watcher.py',
      interpreter: 'python',
      cwd: __dirname,
      args: '--interval 300 --hours-ahead 48 --min-hours-ahead 1',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '200M',
      env: {
        PYTHONUNBUFFERED: '1',
      },
      error_file: '../Logs/pm2-calendar-error.log',
      out_file: '../Logs/pm2-calendar-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss',
      merge_logs: true,
    },
  ],
};
