#!/usr/bin/env python3
"""
Odoo Sync Admin Dashboard

Simple web-based dashboard for monitoring Odoo sync operations.

Features:
- Real-time health status
- Recent sync history
- Job scheduling overview
- Alert history
- Metrics visualization

Usage:
    python odoo_dashboard.py --port 8080
"""

from __future__ import annotations

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    from flask import Flask, render_template_string, jsonify, request
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    print("Flask not available. Install with: pip install flask")

if HAS_FLASK:
    try:
        from flask_compress import Compress
        HAS_COMPRESS = True
    except ImportError:
        HAS_COMPRESS = False

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Dashboard Templates
# =============================================================================

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Odoo Sync Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 1.5rem; font-weight: 600; }
        .refresh-btn {
            background: rgba(255,255,255,0.2);
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 6px;
            color: white;
            cursor: pointer;
            font-size: 0.875rem;
        }
        .refresh-btn:hover { background: rgba(255,255,255,0.3); }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .card {
            background: #1e293b;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3);
        }
        .card h3 {
            font-size: 0.875rem;
            color: #94a3b8;
            margin-bottom: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: 700;
            color: #f8fafc;
        }
        .stat-label {
            color: #64748b;
            font-size: 0.875rem;
        }
        .status-healthy { color: #22c55e; }
        .status-degraded { color: #f59e0b; }
        .status-unhealthy { color: #ef4444; }
        .table {
            width: 100%;
            border-collapse: collapse;
        }
        .table th, .table td {
            text-align: left;
            padding: 0.75rem;
            border-bottom: 1px solid #334155;
        }
        .table th {
            color: #94a3b8;
            font-weight: 500;
            font-size: 0.75rem;
            text-transform: uppercase;
        }
        .table tr:hover { background: #334155; }
        .badge {
            display: inline-block;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
            font-weight: 500;
        }
        .badge-success { background: #22c55e33; color: #22c55e; }
        .badge-warning { background: #f59e0b33; color: #f59e0b; }
        .badge-error { background: #ef444433; color: #ef4444; }
        .badge-info { background: #3b82f633; color: #3b82f6; }
        .chart-container {
            height: 200px;
            position: relative;
        }
        .alert-list {
            max-height: 300px;
            overflow-y: auto;
        }
        .alert-item {
            padding: 0.75rem;
            border-left: 3px solid #64748b;
            margin-bottom: 0.5rem;
            background: #334155;
            border-radius: 0 6px 6px 0;
        }
        .alert-item.critical { border-left-color: #ef4444; }
        .alert-item.warning { border-left-color: #f59e0b; }
        .alert-item.info { border-left-color: #3b82f6; }
        .alert-time {
            font-size: 0.75rem;
            color: #94a3b8;
        }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.875rem;
        }
        .empty-state {
            text-align: center;
            padding: 2rem;
            color: #64748b;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Odoo Sync Dashboard</h1>
        <button class="refresh-btn" onclick="location.reload()">Refresh</button>
    </div>

    <div class="container">
        <!-- Status Cards -->
        <div class="grid">
            <div class="card">
                <h3>Overall Status</h3>
                <div class="stat-value" id="overall-status">Loading...</div>
            </div>
            <div class="card">
                <h3>Last Sync</h3>
                <div class="stat-value" id="last-sync">-</div>
                <div class="stat-label" id="sync-lag"></div>
            </div>
            <div class="card">
                <h3>Records Synced</h3>
                <div class="stat-value" id="records-synced">-</div>
            </div>
            <div class="card">
                <h3>Error Rate</h3>
                <div class="stat-value" id="error-rate">-</div>
            </div>
        </div>

        <div class="grid">
            <!-- Health Checks -->
            <div class="card" style="grid-column: span 2;">
                <h3>System Health</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Check</th>
                            <th>Status</th>
                            <th>Message</th>
                        </tr>
                    </thead>
                    <tbody id="health-table">
                        <tr><td colspan="3" class="empty-state">Loading...</td></tr>
                    </tbody>
                </table>
            </div>

            <!-- Recent Alerts -->
            <div class="card">
                <h3>Recent Alerts</h3>
                <div id="alert-list" class="alert-list">
                    <div class="empty-state">No recent alerts</div>
                </div>
            </div>
        </div>

        <div class="grid">
            <!-- Sync Chart -->
            <div class="card" style="grid-column: span 2;">
                <h3>Sync Activity (24h)</h3>
                <div class="chart-container">
                    <canvas id="sync-chart"></canvas>
                </div>
            </div>

            <!-- Scheduled Jobs -->
            <div class="card">
                <h3>Scheduled Jobs</h3>
                <table class="table">
                    <thead>
                        <tr>
                            <th>Job</th>
                            <th>Status</th>
                            <th>Next Run</th>
                        </tr>
                    </thead>
                    <tbody id="jobs-table">
                        <tr><td colspan="3" class="empty-state">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>Odoo Sync Dashboard | Auto-refresh every 30 seconds</p>
    </div>

    <script>
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);

        // Fetch data on load
        document.addEventListener('DOMContentLoaded', async () => {
            await Promise.all([
                loadHealth(),
                loadAlerts(),
                loadJobs(),
                loadSyncChart()
            ]);
        });

        async function loadHealth() {
            try {
                const res = await fetch('/api/health');
                const data = await res.json();

                // Update overall status
                const statusEl = document.getElementById('overall-status');
                statusEl.textContent = data.status.toUpperCase();
                statusEl.className = 'stat-value status-' + data.status;

                // Update health table
                const table = document.getElementById('health-table');
                table.innerHTML = data.checks.map(check => `
                    <tr>
                        <td>${check.name}</td>
                        <td><span class="badge badge-${check.status === 'healthy' ? 'success' : check.status === 'degraded' ? 'warning' : 'error'}">${check.status}</span></td>
                        <td>${check.message}</td>
                    </tr>
                `).join('');

                // Update sync stats
                document.getElementById('last-sync').textContent = new Date().toLocaleTimeString();

            } catch (e) {
                console.error('Failed to load health:', e);
            }
        }

        async function loadAlerts() {
            try {
                const res = await fetch('/api/alerts');
                const alerts = await res.json();

                const list = document.getElementById('alert-list');
                if (alerts.length === 0) {
                    list.innerHTML = '<div class="empty-state">No recent alerts</div>';
                    return;
                }

                list.innerHTML = alerts.slice(0, 10).map(alert => `
                    <div class="alert-item ${alert.severity}">
                        <div><strong>${alert.name}</strong></div>
                        <div style="font-size: 0.875rem; margin-top: 0.25rem;">${alert.message}</div>
                        <div class="alert-time">${new Date(alert.timestamp).toLocaleString()}</div>
                    </div>
                `).join('');

            } catch (e) {
                console.error('Failed to load alerts:', e);
            }
        }

        async function loadJobs() {
            try {
                const res = await fetch('/api/jobs');
                const jobs = await res.json();

                const table = document.getElementById('jobs-table');
                table.innerHTML = jobs.map(job => `
                    <tr>
                        <td>${job.name}</td>
                        <td><span class="badge badge-${job.enabled ? 'success' : 'info'}">${job.enabled ? 'enabled' : 'disabled'}</span></td>
                        <td>${new Date(job.next_run).toLocaleString()}</td>
                    </tr>
                `).join('');

            } catch (e) {
                console.error('Failed to load jobs:', e);
            }
        }

        async function loadSyncChart() {
            try {
                const res = await fetch('/api/sync-history');
                const history = await res.json();

                const ctx = document.getElementById('sync-chart').getContext('2d');
                new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: history.map(h => new Date(h.timestamp).toLocaleTimeString()),
                        datasets: [{
                            label: 'Records Synced',
                            data: history.map(h => h.records),
                            borderColor: '#667eea',
                            backgroundColor: 'rgba(102, 126, 234, 0.1)',
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: {
                                grid: { color: '#334155' },
                                ticks: { color: '#94a3b8' }
                            },
                            y: {
                                grid: { color: '#334155' },
                                ticks: { color: '#94a3b8' }
                            }
                        }
                    }
                });

            } catch (e) {
                console.error('Failed to load chart:', e);
            }
        }
    </script>
</body>
</html>
"""


# =============================================================================
# Dashboard Application
# =============================================================================

class DashboardApp:
    """Dashboard web application"""

    def __init__(self, port: int = 8080, host: str = "0.0.0.0"):
        if not HAS_FLASK:
            raise RuntimeError("Flask is required. Install with: pip install flask")

        self.port = port
        self.host = host
        self.app = Flask(__name__)
        self._setup_routes()

        if HAS_COMPRESS:
            self.app.config['COMPRESS_MIMETYPES'] = ['text/html', 'application/json']

    def _setup_routes(self):
        """Setup API routes"""

        @self.app.route('/')
        def index():
            return render_template_string(DASHBOARD_HTML)

        @self.app.route('/api/health')
        def api_health():
            """Get health status"""
            from odoo_health import HealthChecker

            checker = HealthChecker()
            report = checker.check_all()

            return jsonify({
                "status": report.status.value,
                "checks": [
                    {
                        "name": check.name,
                        "status": check.status.value,
                        "message": check.message,
                        "details": check.details
                    }
                    for check in report.checks
                ]
            })

        @self.app.route('/api/alerts')
        def api_alerts():
            """Get recent alerts"""
            vault_path = Path(os.getenv("VAULT_PATH", "."))
            alerts_file = vault_path / "Logs" / "Alerts" / f"alerts_{datetime.now().strftime('%Y-%m')}.jsonl"

            alerts = []
            if alerts_file.exists():
                with open(alerts_file) as f:
                    for line in f:
                        if line.strip():
                            alerts.append(json.loads(line))

            # Return last 20, most recent first
            return jsonify(alerts[-20:][::-1])

        @self.app.route('/api/jobs')
        def api_jobs():
            """Get scheduled jobs"""
            from odoo_scheduler import Scheduler

            scheduler = Scheduler()
            jobs = []

            for job in scheduler.jobs.values():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "enabled": job.enabled,
                    "cron_expression": job.cron_expression,
                    "next_run": job.next_run_time().isoformat()
                })

            return jsonify(jobs)

        @self.app.route('/api/sync-history')
        def api_sync_history():
            """Get sync history"""
            vault_path = Path(os.getenv("VAULT_PATH", "."))
            history_dir = vault_path / "Logs" / "Scheduler"

            history = []
            for file in sorted(history_dir.glob("jobs_*.jsonl"), reverse=True)[:2]:
                try:
                    with open(file) as f:
                        for line in f:
                            if line.strip():
                                record = json.loads(line)
                                if record.get("status") == "success":
                                    history.append({
                                        "timestamp": record.get("start_time"),
                                        "records": record.get("context", {}).get("records_synced", 0)
                                    })
                except Exception:
                    pass

            # Take last 24 hours
            cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
            history = [h for h in history if h.get("timestamp", "") > cutoff]

            return jsonify(history[-50:])

        @self.app.route('/api/metrics')
        def api_metrics():
            """Get Prometheus metrics"""
            from odoo_metrics import get_metrics

            metrics = get_metrics()
            return Response(metrics.get_metrics_text(), mimetype='text/plain')

    def run(self, debug: bool = False):
        """Run the dashboard server"""
        from flask import Response

        self.app.run(host=self.host, port=self.port, debug=debug, use_reloader=False)


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Sync Dashboard')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    if not HAS_FLASK:
        print("Error: Flask is required")
        print("Install with: pip install flask")
        return 1

    app = DashboardApp(port=args.port, host=args.host)

    print(f"\nOdoo Sync Dashboard")
    print(f"  URL: http://{args.host}:{args.port}")
    print(f"  Health: http://{args.host}:{args.port}/api/health")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        app.run(debug=args.debug)
    except KeyboardInterrupt:
        print("\nDashboard stopped")

    return 0


if __name__ == "__main__":
    sys.exit(main())
