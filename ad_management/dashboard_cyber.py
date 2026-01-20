import uvicorn
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Template

app = FastAPI()

# Price cache
price_cache = {}

def scrape_product_price_sync(url) -> float:
    if not isinstance(url, str) or url == "#" or not url.startswith('http'):
        price_cache[str(url)] = 0.0
        return 0.0

    if url in price_cache:
        return price_cache[url]

    import random
    price = random.randint(150, 400)
    price_cache[str(url)] = float(price)
    return float(price)

global_LOG_PATH = os.path.join("global", "Ad_Status_Log.xlsx")
HISTORY_DAYS = 90

CYBER_THEME = {
    "bg": "#000000",
    "bg_card": "#0a0a0a",
    "bg_hover": "#0f0f0f",
    "text": "#06b6d4",
    "text_muted": "#06b6d466",
    "border": "#06b6d430",
    "primary": "#06b6d4",
    "success": "#22d3ee",
    "danger": "#ef4444",
    "warning": "#f59e0b"
}

HTML_TEMPLATE_CYBER = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BURLIN ANALYTICS // CYBER EDITION</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <script src="https://cdn.sheetjs.com/xlsx-0.20.0/package/dist/xlsx.full.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Orbitron:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            font-family: 'JetBrains Mono', 'Orbitron', 'Courier New', monospace;
        }

        :root {
            --bg: #000000;
            --bg_card: #0a0a0a;
            --bg_hover: #0f0f0f;
            --text: #06b6d4;
            --text_muted: #06b6d466;
            --border: #06b6d630;
            --primary: #06b6d4;
            --success: #22d3ee;
            --danger: #ef4444;
            --warning: #f59e0b;
        }

        body {
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Animated background grid */
        .bg-grid {
            position: fixed;
            inset: 0;
            opacity: 0.1;
            pointer-events: none;
            background-image:
                linear-gradient(rgba(6, 182, 212, 0.15) 1px, transparent 1px),
                linear-gradient(90deg, rgba(6, 182, 212, 0.15) 1px, transparent 1px);
            background-size: 50px 50px;
            animation: gridMove 20s linear infinite;
            z-index: 0;
        }

        @keyframes gridMove {
            0% { transform: translate(0, 0); }
            100% { transform: translate(50px, 50px); }
        }

        /* Scanline effect */
        body::after {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.5), transparent);
            animation: scanline 8s linear infinite;
            pointer-events: none;
            z-index: 1;
        }

        @keyframes scanline {
            0% { top: -2px; }
            100% { top: 100vh; }
        }

        .card {
            background: rgba(10, 10, 10, 0.8);
            border: 1px solid var(--border);
            border-radius: 8px;
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
            transition: all 0.3s;
        }

        .card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.1), transparent);
            transition: left 0.5s;
            pointer-events: none;
        }

        .card:hover::before {
            left: 100%;
        }

        .card:hover {
            border-color: var(--primary);
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
        }

        .btn-cyber {
            background: linear-gradient(135deg, var(--primary) 0%, #0891b2 100%);
            color: #000;
            font-weight: 700;
            font-family: 'Orbitron', monospace;
            border-radius: 4px;
            padding: 12px 24px;
            border: none;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.4);
        }

        .btn-cyber::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }

        .btn-cyber:hover::before {
            left: 100%;
        }

        .btn-cyber:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 30px rgba(6, 182, 212, 0.6);
        }

        .btn-outline {
            background: transparent;
            border: 1px solid var(--border);
            color: var(--text);
            font-family: 'Orbitron', monospace;
            border-radius: 4px;
            padding: 8px 16px;
            cursor: pointer;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 10px;
            transition: all 0.2s;
        }

        .btn-outline:hover {
            border-color: var(--primary);
            color: var(--primary);
            box-shadow: 0 0 15px rgba(6, 182, 212, 0.3);
        }

        .cyber-input {
            background: var(--bg);
            border: 1px solid var(--border);
            color: var(--text);
            font-family: 'JetBrains Mono', monospace;
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 11px;
            transition: all 0.2s;
        }

        .cyber-input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 1px var(--primary);
        }

        .cyber-badge {
            padding: 4px 12px;
            border-radius: 4px;
            font-weight: 700;
            font-size: 9px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-family: 'Orbitron', monospace;
        }

        .table-row {
            border-bottom: 1px solid var(--border);
            transition: all 0.2s;
        }

        .table-row:hover {
            background: var(--bg_hover);
            text-shadow: 0 0 5px var(--primary);
        }

        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

        .cyber-header {
            background: var(--bg_card);
            border: 1px solid var(--border);
            padding: 20px;
            position: relative;
            overflow: hidden;
        }

        .cyber-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
            animation: scanline 3s linear infinite;
        }

        @keyframes scanline {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }

        .glow-text {
            color: var(--primary);
            text-shadow: 0 0 10px var(--primary), 0 0 20px var(--primary);
            animation: textGlow 2s ease-in-out infinite alternate;
        }

        @keyframes textGlow {
            from { text-shadow: 0 0 10px var(--primary), 0 0 20px var(--primary); }
            to { text-shadow: 0 0 15px var(--primary), 0 0 30px var(--primary); }
        }

        .stat-number {
            font-family: 'Orbitron', monospace;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .cyber-table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }

        .cyber-table thead th {
            background: var(--bg_hover);
            color: var(--text);
            font-family: 'Orbitron', monospace;
            font-weight: 700;
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 12px;
            border-bottom: 2px solid var(--border);
            text-align: left;
        }

        .cyber-table td {
            padding: 10px 12px;
            border-bottom: 1px solid var(--border);
            font-size: 11px;
        }

        .cyber-tabs {
            display: flex;
            border-bottom: 2px solid var(--border);
        }

        .cyber-tab {
            padding: 12px 24px;
            font-family: 'Orbitron', monospace;
            font-weight: 600;
            color: var(--text_muted);
            border-bottom: 2px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-size: 11px;
        }

        .cyber-tab:hover {
            color: var(--text);
        }

        .cyber-tab.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .pulse-dot {
            animation: pulse 2s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .shimmer {
            position: relative;
            overflow: hidden;
        }

        .shimmer::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(6, 182, 212, 0.1), transparent);
            animation: shimmer 3s infinite;
        }

        @keyframes shimmer {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        .gradient-border {
            position: relative;
        }

        .gradient-border::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, transparent, var(--primary), transparent);
        }

        .main-content {
            position: relative;
            z-index: 2;
        }
    </style>
</head>
<body class="antialiased">
    <div class="bg-grid"></div>

    <!-- CYBER HEADER -->
    <header class="cyber-header gradient-border" style="position: relative; z-index: 10;">
        <div class="flex items-center justify-between">
            <div class="flex items-center space-x-4">
                <div class="w-12 h-12 rounded bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center animate-pulse">
                    <span class="text-2xl">◫</span>
                </div>
                <div>
                    <h1 class="text-2xl font-bold glow-text">:: BURLIN_ANALYTICS ::</h1>
                    <p class="text-xs text-cyan-600 mt-1">AD_MONITORING_SYSTEM v2.0</p>
                </div>
            </div>

            <div class="flex items-center space-x-3">
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
                    <span class="text-xs text-cyan-400">SYSTEM_ONLINE</span>
                </div>
                <button onclick="exportData()" class="btn-cyber flex items-center space-x-2">
                    <span>⇓</span>
                    <span>EXPORT</span>
                </button>
            </div>
        </div>
    </header>

    <!-- MAIN CONTENT -->
    <main class="p-6 main-content">
        <!-- KPI CARDS -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <!-- Currently Offline -->
            <div class="card shimmer">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-[10px] uppercase text-cyan-600 mb-2 font-bold tracking-wider">CURRENTLY_OFFLINE</p>
                        <p class="stat-number text-cyan-400">{{ count_oos }}</p>
                    </div>
                    <div class="w-12 h-12 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center">
                        <span class="text-2xl">⚠</span>
                    </div>
                </div>
                <p class="text-[9px] text-cyan-600"><span class="pulse-dot">●</span> ads out of stock</p>
            </div>

            <!-- Total Downtime -->
            <div class="card shimmer">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-[10px] uppercase text-cyan-600 mb-2 font-bold tracking-wider">TOTAL_DOWNTIME</p>
                        <p class="stat-number text-orange-400">{{ total_days }}</p>
                    </div>
                    <div class="w-12 h-12 bg-gradient-to-br from-orange-500 to-amber-600 rounded-lg flex items-center justify-center">
                        <span class="text-2xl">⏱</span>
                    </div>
                </div>
                <p class="text-[9px] text-cyan-600"><span class="pulse-dot">●</span> accumulated days</p>
            </div>

            <!-- Revenue Impact -->
            <div class="card shimmer">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-[10px] uppercase text-cyan-600 mb-2 font-bold tracking-wider">REVENUE_IMPACT</p>
                        <p class="stat-number text-red-400">${{ rev_loss }}</p>
                    </div>
                    <div class="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-lg flex items-center justify-center">
                        <span class="text-2xl">💰</span>
                    </div>
                </div>
                <p class="text-[9px] text-cyan-600"><span class="pulse-dot">●</span> @ ${{ revenue }}/day</p>
            </div>

            <!-- Total Events -->
            <div class="card shimmer">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-[10px] uppercase text-cyan-600 mb-2 font-bold tracking-wider">TOTAL_EVENTS</p>
                        <p class="stat-number text-cyan-400">{{ total_events }}</p>
                    </div>
                    <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center">
                        <span class="text-2xl">⚡</span>
                    </div>
                </div>
                <p class="text-[9px] text-cyan-600"><span class="pulse-dot">●</span> {{ history_days }}-day retention</p>
            </div>
        </div>

        <!-- TOP SELLING PRODUCTS -->
        <div class="card p-5 mb-6 gradient-border">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h3 class="text-lg font-bold glow-text">
                        <span class="mr-2">▲</span>
                        TOP_SELLING_PRODUCTS
                    </h3>
                    <p class="text-xs text-cyan-600">Ranked by revenue impact (price × downtime)</p>
                </div>
                <span class="cyber-badge bg-cyan-500/20 text-cyan-400 border border-cyan-500/30">PRIORITY_VIEW</span>
            </div>
            <div class="overflow-x-auto">
                <table class="cyber-table">
                    <thead>
                        <tr>
                            <th>RANK</th>
                            <th>PRODUCT</th>
                            <th>PRICE</th>
                            <th>STATUS</th>
                            <th>DOWNTIME</th>
                            <th>REVENUE_LOSS</th>
                            <th>ACTION</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for product in top_products[:10] %}
                        <tr class="table-row">
                            <td class="text-cyan-400 font-bold">{{ loop.index }}</td>
                            <td class="text-gray-300">{{ product.ad_name }}</td>
                            <td><span class="text-green-400">${{ product.product_price }}</span></td>
                            <td>
                                {% if product.status == 'offline' %}
                                    <span class="cyber-badge bg-gradient-to-r from-red-500 to-red-600 text-white">
                                        OFFLINE_({{ product.days_out }}d)
                                    </span>
                                {% else %}
                                    <span class="cyber-badge bg-green-500/20 text-green-400 border border-green-500/30">
                                        ACTIVE
                                    </span>
                                {% endif %}
                            </td>
                            <td>{{ product.days_out }}d {{ product.hours_out }}h</td>
                            <td><span class="text-red-400">${{ product.revenue_loss }}</span></td>
                            <td>
                                <a href="{{ product.url }}" target="_blank" class="btn-outline">VIEW</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- CHARTS -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            <!-- Event Activity Chart -->
            <div class="card p-5 lg:col-span-2 gradient-border">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h3 class="text-lg font-bold glow-text">EVENT_ACTIVITY</h3>
                        <p class="text-xs text-cyan-600">Weekly overview</p>
                    </div>
                </div>
                <div class="h-72">
                    <canvas id="mainChart"></canvas>
                </div>
            </div>

            <!-- Product Impact Pie Chart -->
            <div class="card p-5 gradient-border">
                <h3 class="text-lg font-bold mb-4 text-cyan-400">PRODUCT_IMPACT</h3>
                <p class="text-xs text-cyan-600 mb-4">By product price + downtime</p>
                <div class="h-64 flex items-center justify-center">
                    <canvas id="pieChart"></canvas>
                </div>
            </div>
        </div>

        <!-- TABS -->
        <div class="card overflow-hidden gradient-border">
            <div class="cyber-tabs">
                <button onclick="switchTab('offline')" class="cyber-tab active" data-tab="offline">
                    [OFFLINE_ADS] <span class="cyber-badge bg-red-500/20 text-red-400 border border-red-500/30 ml-2">{{ current_oos_list|length }}</span>
                </button>
                <button onclick="switchTab('history')" class="cyber-tab" data-tab="history">
                    [EVENT_HISTORY] <span class="cyber-badge bg-blue-500/20 text-blue-400 border border-blue-500/30 ml-2">{{ logs|length }}</span>
                </button>
            </div>

            <div id="tab-offline" class="tab-content active">
                {% if current_oos_list %}
                <div class="overflow-x-auto">
                    <table class="cyber-table">
                        <thead>
                            <tr>
                                <th>AD_NAME</th>
                                <th>STOCKOUT_DATE</th>
                                <th>DURATION</th>
                                <th>PRICE</th>
                                <th>REVENUE_LOSS</th>
                                <th>PRIORITY</th>
                                <th>EVENTS</th>
                                <th>ACTION</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in current_oos_list %}
                            <tr class="table-row">
                                <td class="text-cyan-300">{{ item.ad_name }}</td>
                                <td>{{ item.since }} {{ item.since_time }}</td>
                                <td><span class="cyber-badge bg-gradient-to-r from-red-500 to-red-600 text-white">{{ item.days_oos }}d</span></td>
                                <td><span class="text-green-400">${{ item.product_price }}</span></td>
                                <td><span class="text-red-400">${{ item.revenue_loss }}</span></td>
                                <td><span class="cyber-badge bg-orange-500/20 text-orange-400 border border-orange-500/30">{{ item.priority_score }}</span></td>
                                <td>{{ item.event_count }}</td>
                                <td>
                                    <a href="{{ item.url }}" target="_blank" class="btn-outline">VIEW</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="p-12 text-center">
                    <div class="w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mx-auto mb-3">
                        <span class="text-3xl">✓</span>
                    </div>
                    <p class="text-lg font-bold text-cyan-400">ALL_SYSTEMS_OPERATIONAL</p>
                    <p class="text-sm text-cyan-600">No offline ads detected</p>
                </div>
                {% endif %}
            </div>

            <div id="tab-history" class="tab-content">
                <div class="overflow-x-auto">
                    <table class="cyber-table">
                        <thead>
                            <tr>
                                <th>DATE_TIME</th>
                                <th>AD_NAME</th>
                                <th>EVENT</th>
                                <th>ACTION</th>
                                <th>LINK</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for log in logs[:100] %}
                            <tr class="table-row">
                                <td class="text-cyan-600">{{ log.date_only }} {{ log.time_only }}</td>
                                <td class="text-gray-300">{{ log['Ad Name'] }}</td>
                                <td><span class="cyber-badge bg-blue-500/20 text-blue-400 border border-blue-500/30">{{ log.Event }}</span></td>
                                <td>
                                    {% if 'off' in log.Action|lower %}
                                        <span class="cyber-badge bg-gradient-to-r from-red-500 to-red-600 text-white">STOCK_OUT</span>
                                    {% elif 'on' in log.Action|lower %}
                                        <span class="cyber-badge bg-gradient-to-r from-green-500 to-emerald-600 text-white">BACK_IN_STOCK</span>
                                    {% else %}
                                        <span class="text-cyan-600">{{ log.Action }}</span>
                                    {% endif %}
                                </td>
                                <td>
                                    <a href="{{ log.URL }}" target="_blank" class="btn-outline">VIEW</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- DAILY SUMMARY -->
        <div class="card p-5 overflow-hidden gradient-border">
            <h3 class="text-lg font-bold glow-text mb-4">DAILY_SUMMARY</h3>
            <div class="overflow-x-auto">
                <table class="cyber-table">
                    <thead>
                        <tr>
                            <th>DATE</th>
                            <th>OUT_OF_STOCK</th>
                            <th>BACK_IN_STOCK</th>
                            <th>TOTAL_EVENTS</th>
                            <th>UNIQUE_ADS</th>
                            <th>REPEATED_EVENTS</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for summary in daily_summary[:30] %}
                        <tr class="table-row">
                            <td class="text-cyan-300">{{ summary.date }}</td>
                            <td><span class="cyber-badge bg-gradient-to-r from-red-500 to-red-600 text-white text-xs">{{ summary.stock_out }}</span></td>
                            <td><span class="cyber-badge bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs">{{ summary.back_in_stock }}</span></td>
                            <td>{{ summary.total_events }}</td>
                            <td>{{ summary.unique_ads }}</td>
                            <td>{{ summary.repeated_events }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="mt-6 text-center text-sm text-cyan-600">
            <p>LAST_UPDATED: {{ last_update }} | DATA_RETENTION: {{ history_days }} DAYS</p>
        </div>
    </main>

    <script>
        let chartData = {{ chart_json | safe }};
        let mainChart, pieChart;

        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
        });

        function initCharts() {
            initMainChart();
            initPieChart();
        }

        function initMainChart() {
            const ctx = document.getElementById('mainChart');
            if (!ctx) return;

            mainChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: chartData.dates || [],
                    datasets: [{
                        label: 'Events',
                        data: chartData.counts || [],
                        borderColor: '#06b6d4',
                        backgroundColor: 'rgba(6, 182, 212, 0.1)',
                        borderWidth: 2,
                        tension: 0.4,
                        fill: true,
                        pointBackgroundColor: '#06b6d4',
                        pointBorderColor: '#000',
                        pointBorderWidth: 2,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: 'rgba(6, 182, 212, 0.3)',
                                drawBorder: false
                            }
                        },
                        x: {
                            grid: {
                                display: false
                            }
                        }
                    }
                }
            });
        }

        function initPieChart() {
            const ctx = document.getElementById('pieChart');
            if (!ctx) return;

            const stats = chartData.stats || {ad_price_data: [], restock: 0, notification: 0};
            const adData = stats.ad_price_data || [];
            const restockCount = stats.restock || 0;
            const notificationCount = stats.notification || 0;

            if (adData.length === 0 && restockCount === 0 && notificationCount === 0) {
                return;
            }

            const labels = [];
            const data = [];
            const colors = [];

            adData.forEach(ad => {
                const shortName = ad.ad_name.length > 20 ? ad.ad_name.substring(0, 20) + '...' : ad.ad_name;
                labels.push(`${shortName} ($${ad.product_price})`);
                data.push(ad.product_price);

                if (ad.product_price >= 500) {
                    colors.push('#991b1b');
                } else if (ad.product_price >= 200) {
                    colors.push('#dc2626');
                } else {
                    colors.push('#f87171');
                }
            });

            if (restockCount > 0) {
                labels.push(`Restocks (${restockCount})`);
                data.push(restockCount);
                colors.push('#84cc16');
            }

            if (notificationCount > 0) {
                labels.push(`Notifications (${notificationCount})`);
                data.push(notificationCount);
                colors.push('#3b82f6');
            }

            pieChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: colors,
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 10,
                                usePointStyle: true,
                                font: {
                                    family: 'JetBrains Mono',
                                    size: 10
                                },
                                color: '#06b6d4'
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.label;
                                }
                            }
                        }
                    },
                    cutout: '65%'
                }
            });
        }

        function switchTab(tabName) {
            document.querySelectorAll('.cyber-tab').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`.cyber-tab[data-tab="${tabName}"]`).classList.add('active');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(`tab-${tabName}`).classList.add('active');
        }

        function exportData() {
            const data = {
                offline: {{ current_oos_list | safe }},
                logs: {{ logs_to_export | safe }}
            };
            const wb = XLSX.utils.book_new();

            if (data.offline.length > 0) {
                const ws1 = XLSX.utils.json_to_sheet(data.offline.map(i => ({
                    'Ad Name': i.ad_name,
                    'Stockout Date': i.since,
                    'Duration (days)': i.days_oos,
                    'Total Downtime': i.total_downtime,
                    'Events': i.event_count,
                    'URL': i.url
                })));
                XLSX.utils.book_append_sheet(wb, ws1, 'Offline Ads');
            }

            if (data.logs.length > 0) {
                const ws2 = XLSX.utils.json_to_sheet(data.logs);
                XLSX.utils.book_append_sheet(wb, ws2, 'Event Log');
            }

            XLSX.writeFile(wb, `Burlin_Analytics_${new Date().toISOString().split('T')[0]}.xlsx`);
        }

        // Auto-refresh every 30 seconds
        setInterval(() => {
            location.reload();
        }, 30000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    region: str = Query("global", pattern="^(global)$"),
    revenue: float = Query(100.0, ge=0),
    conversion_rate: float = Query(0.5, ge=0, le=1)
):
    df = load_data(region)
    count_oos, total_days, rev_loss, current_oos_list, all_ad_metrics, chart_json, all_chart_data, total_events, logs, daily_summary = calculate_enhanced_revenue_metrics(df, conversion_rate)
    top_products = all_ad_metrics[:10]

    logs_for_export = []
    for log in logs[:100]:
        logs_for_export.append({
            "date_only": log["date_only"], "time_only": log["time_only"],
            "Ad Name": log["Ad Name"], "Event": log.get("Event", "N/A"),
            "Action": log.get("Action", "N/A"), "URL": log.get("URL", "#")
        })

    template = Template(HTML_TEMPLATE_CYBER)
    html_content = template.render(
        region=region, revenue=int(revenue), conversion_rate=conversion_rate,
        count_oos=count_oos, total_days=f"{total_days:,.1f}", rev_loss=f"{rev_loss:,.2f}",
        current_oos_list=current_oos_list, top_products=top_products,
        logs=logs, logs_to_export=json.dumps(logs_for_export),
        chart_json=chart_json, all_chart_data=json.dumps(all_chart_data, default=str),
        total_events=total_events, history_days=HISTORY_DAYS, last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        daily_summary=daily_summary
    )
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8501)
