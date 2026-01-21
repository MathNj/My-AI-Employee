import uvicorn
import pandas as pd
import os
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from jinja2 import Template

app = FastAPI()

# Load product prices from CSV
product_prices_cache = {}

def load_product_prices_from_csv() -> dict:
    """Load actual prices from URLS.csv"""
    global product_prices_cache

    if product_prices_cache:
        return product_prices_cache

    try:
        df = pd.read_csv("URLS.csv")
        for _, row in df.iterrows():
            url = str(row.get("URL", ""))
            price = float(row.get("Product_Price", 0))
            if url and url.startswith('http'):
                product_prices_cache[url] = price
        print(f"[OK] Loaded {len(product_prices_cache)} product prices from URLS.csv")
    except Exception as e:
        print(f"[ERROR] Failed to load product prices: {e}")

    return product_prices_cache

def get_product_price_from_csv(url: str) -> float:
    """Get actual product price from CSV"""
    if not isinstance(url, str) or url == "#" or not url.startswith('http'):
        return 0.0

    # Load prices if not already loaded
    if not product_prices_cache:
        load_product_prices_from_csv()

    return product_prices_cache.get(url, 0.0)

global_LOG_PATH = os.path.join("global", "Ad_Status_Log.xlsx")
HISTORY_DAYS = 90

# Simple themes - just White and Black
THEMES = {
    "white": {
        "bg": "#f8fafc",
        "bg_card": "#ffffff",
        "bg_hover": "#f1f5f9",
        "text": "#0f172a",
        "text_muted": "#64748b",
        "border": "#e2e8f0",
        "primary": "#3b82f6",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b"
    },
    "black": {
        "bg": "#0f172a",
        "bg_card": "#1e293b",
        "bg_hover": "#334155",
        "text": "#f1f5f9",
        "text_muted": "#94a3b8",
        "border": "#334155",
        "primary": "#60a5fa",
        "success": "#34d399",
        "danger": "#f87171",
        "warning": "#fbbf24"
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Burlin Analytics Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <script src="https://cdn.sheetjs.com/xlsx-0.20.0/package/dist/xlsx.full.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * { font-family: 'Inter', sans-serif; }

        :root {
            --bg: #f8fafc;
            --bg_card: #ffffff;
            --bg_hover: #f1f5f9;
            --text: #0f172a;
            --text_muted: #64748b;
            --border: #e2e8f0;
            --primary: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
        }

        body {
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            transition: background 0.3s, color 0.3s;
        }

        .card {
            background: var(--bg_card);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s;
        }

        .card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

        .btn-primary {
            background: linear-gradient(135deg, var(--primary) 0%, #2563eb 100%);
            color: #fff;
            font-weight: 600;
            border-radius: 12px;
            padding: 12px 24px;
            border: none;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3);
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }

        .btn-outline {
            background: transparent;
            border: 2px solid var(--border);
            color: var(--text);
            font-weight: 600;
            border-radius: 12px;
            padding: 10px 20px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-outline:hover {
            border-color: var(--primary);
            background: var(--primary);
            color: #fff;
        }

        .select-input {
            background: var(--bg);
            border: 2px solid var(--border);
            color: var(--text);
            font-weight: 600;
            border-radius: 12px;
            padding: 10px 16px;
            cursor: pointer;
        }

        .select-input:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
        }

        .text-muted { color: var(--text_muted); }

        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: var(--bg); }
        ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: var(--primary); }

        .modal {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.7);
            backdrop-filter: blur(8px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }
        .modal.active { display: flex; }

        .tab-btn {
            padding: 16px 24px;
            font-weight: 700;
            color: var(--text_muted);
            border-bottom: 3px solid transparent;
            cursor: pointer;
            transition: all 0.2s;
        }
        .tab-btn:hover { color: var(--text); }
        .tab-btn.active {
            color: var(--primary);
            border-bottom-color: var(--primary);
        }

        .tab-content { display: none; }
        .tab-content.active { display: block; }

        .gradient-text {
            background: linear-gradient(135deg, var(--primary) 0%, #8b5cf6 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .kpi-icon {
            width: 56px;
            height: 56px;
            border-radius: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
        }

        .badge {
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 700;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .table-row {
            border-bottom: 1px solid var(--border);
            transition: all 0.2s;
        }
        .table-row:hover { background: var(--bg_hover); }
    </style>
</head>
<body class="antialiased">
    <!-- HEADER -->
    <header class="border-b" style="background: var(--bg_card); border-color: var(--border);">
        <div class="px-6 py-4">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center shadow-lg">
                        <i class="ph-fill ph-chart-polar text-white text-xl"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-black">BURLIN ANALYTICS</h1>
                        <p class="text-xs text-muted font-semibold tracking-wide">AD MONITORING DASHBOARD</p>
                    </div>
                </div>

                <div class="flex items-center space-x-3">
                    <button onclick="toggleTheme()" class="btn-outline flex items-center space-x-2">
                        <i class="ph-bold ph-palette text-lg"></i>
                        <span class="hidden sm:inline">Theme</span>
                    </button>

                    <button onclick="exportData()" class="btn-primary flex items-center space-x-2">
                        <i class="ph-bold ph-download-simple text-lg"></i>
                        <span class="hidden sm:inline">Export</span>
                    </button>
                </div>
            </div>
        </div>
    </header>

    <!-- MAIN CONTENT -->
    <main class="p-6">
        <!-- KPI Cards -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div class="card p-5">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-xs font-bold uppercase text-muted mb-1">Currently Offline</p>
                        <p class="text-4xl font-black gradient-text">{{ count_oos }}</p>
                    </div>
                    <div class="kpi-icon bg-gradient-to-br from-red-500 to-red-600">
                        <i class="ph-fill ph-prohibit text-white"></i>
                    </div>
                </div>
                <p class="text-xs text-muted"><i class="ph-bold ph-trend-down text-red-500 mr-1"></i>ads out of stock</p>
            </div>

            <div class="card p-5">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-xs font-bold uppercase text-muted mb-1">Total Downtime</p>
                        <p class="text-4xl font-black gradient-text">{{ total_days }}</p>
                    </div>
                    <div class="kpi-icon bg-gradient-to-br from-orange-500 to-amber-600">
                        <i class="ph-fill ph-clock text-white"></i>
                    </div>
                </div>
                <p class="text-xs text-muted"><i class="ph-bold ph-calendar text-orange-500 mr-1"></i>accumulated days</p>
            </div>

            <div class="card p-5">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-xs font-bold uppercase text-muted mb-1">Revenue Impact</p>
                        <p class="text-4xl font-black text-red-500">${{ rev_loss }}</p>
                    </div>
                    <div class="kpi-icon bg-gradient-to-br from-green-500 to-emerald-600">
                        <i class="ph-fill ph-currency-dollar text-white"></i>
                    </div>
                </div>
                <p class="text-xs text-muted"><i class="ph-bold ph-chart-line-down text-red-500 mr-1"></i>@ ${{ revenue }}/day</p>
            </div>

            <div class="card p-5">
                <div class="flex items-start justify-between mb-3">
                    <div>
                        <p class="text-xs font-bold uppercase text-muted mb-1">Total Events</p>
                        <p class="text-4xl font-black gradient-text">{{ total_events }}</p>
                    </div>
                    <div class="kpi-icon bg-gradient-to-br from-blue-500 to-indigo-600">
                        <i class="ph-fill ph-lightning text-white"></i>
                    </div>
                </div>
                <p class="text-xs text-muted"><i class="ph-bold ph-database text-blue-500 mr-1"></i>{{ history_days }}-day retention</p>
            </div>
        </div>

        <!-- Top Selling Products Section -->
        <div class="card p-5 mb-6">
            <div class="flex items-center justify-between mb-4">
                <div>
                    <h3 class="text-lg font-bold">
                        <i class="ph-fill ph-trend-up text-green-500 mr-2"></i>
                        Top Selling Products
                    </h3>
                    <p class="text-xs text-muted">Ranked by revenue impact (price × downtime)</p>
                </div>
                <span class="badge bg-blue-100 text-blue-700">Priority View</span>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full">
                    <thead style="background: var(--bg_hover);">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase">Rank</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase">Product</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase">Price</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase">Status</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase">Downtime</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase">Revenue Loss</th>
                            <th class="px-4 py-3 text-right text-xs font-black uppercase">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for product in top_products[:10] %}
                        <tr class="table-row" style="border-bottom: 1px solid var(--border);">
                            <td class="px-4 py-3 font-bold text-lg">{{ loop.index }}</td>
                            <td class="px-4 py-3 font-semibold">{{ product.ad_name }}</td>
                            <td class="px-4 py-3">
                                <span class="text-green-600 font-black text-lg">PKR ${{ "{:,.0f}".format(product.product_price) }}</span>
                            </td>
                            <td class="px-4 py-3">
                                {% if product.status == 'offline' %}
                                    <span class="badge bg-gradient-to-r from-red-500 to-red-600 text-white">
                                        Offline ({{ product.days_out }}d {{ product.hours_out }}h)
                                    </span>
                                {% else %}
                                    <span class="badge bg-green-100 text-green-700">Active</span>
                                {% endif %}
                            </td>
                            <td class="px-4 py-3 text-sm">{{ product.days_out }}d {{ product.hours_out }}h</td>
                            <td class="px-4 py-3">
                                <span class="text-red-600 font-bold">${{ product.revenue_loss }}</span>
                            </td>
                            <td class="px-4 py-3 text-right">
                                <a href="{{ product.url }}" target="_blank" class="btn-outline px-3 py-1 text-xs">
                                    View
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Charts -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-6">
            <div class="card p-5 lg:col-span-2">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h3 class="text-lg font-bold">Event Activity</h3>
                        <p class="text-xs text-muted">Weekly overview</p>
                    </div>
                    <div class="flex items-center space-x-2">
                        <button onclick="setChartType('line')" class="chart-btn btn-outline px-3 py-1.5 text-xs" data-type="line">
                            <i class="ph-bold ph-chart-line-up mr-1"></i>Line
                        </button>
                        <button onclick="setChartType('bar')" class="chart-btn btn-outline px-3 py-1.5 text-xs" data-type="bar">
                            <i class="ph-bold ph-chart-bar mr-1"></i>Bar
                        </button>
                    </div>
                </div>
                <div class="h-72">
                    <canvas id="mainChart"></canvas>
                </div>
            </div>

            <div class="card p-5">
                <h3 class="text-lg font-bold mb-1">Product Impact</h3>
                <p class="text-xs text-muted mb-4">By product price + Restocks + Notifications</p>
                <div class="h-64 flex items-center justify-center">
                    <canvas id="pieChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Daily Summary Table -->
        <div class="card p-5 mb-6 overflow-hidden">
            <h3 class="text-lg font-bold mb-4">Daily Summary</h3>
            <div class="overflow-x-auto">
                <table class="w-full" style="table-layout: fixed; min-width: 900px;">
                    <thead style="background: var(--bg_hover);">
                        <tr>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 100px;">Date</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 100px;">Out of Stock</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 100px;">Back in Stock</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 100px;">Total Events</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 100px;">Unique Ads</th>
                            <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 120px;">Repeated Events</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for summary in daily_summary[:30] %}
                        <tr class="table-row" style="border-bottom: 1px solid var(--border);">
                            <td class="px-4 py-3 font-semibold text-sm whitespace-nowrap">{{ summary.date }}</td>
                            <td class="px-4 py-3 whitespace-nowrap">
                                <span class="badge bg-gradient-to-r from-red-500 to-red-600 text-white text-xs whitespace-nowrap">{{ summary.stock_out }}</span>
                            </td>
                            <td class="px-4 py-3 whitespace-nowrap">
                                <span class="badge bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs whitespace-nowrap">{{ summary.back_in_stock }}</span>
                            </td>
                            <td class="px-4 py-3 text-sm whitespace-nowrap">{{ summary.total_events }}</td>
                            <td class="px-4 py-3 text-sm whitespace-nowrap">{{ summary.unique_ads }}</td>
                            <td class="px-4 py-3 text-sm text-muted whitespace-nowrap">{{ summary.repeated_events }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Tables -->
        <div class="card overflow-hidden">
            <div class="flex border-b" style="border-color: var(--border);">
                <button onclick="switchTab('offline')" class="tab-btn active" data-tab="offline">
                    <i class="ph-fill ph-warning-circle mr-2"></i>Offline Ads <span class="badge bg-red-100 text-red-700 ml-2">{{ current_oos_list|length }}</span>
                </button>
                <button onclick="switchTab('history')" class="tab-btn" data-tab="history">
                    <i class="ph-fill ph-clock-counter-clockwise mr-2"></i>Event History <span class="badge bg-blue-100 text-blue-700 ml-2">{{ logs|length }}</span>
                </button>
            </div>

            <div id="tab-offline" class="tab-content active">
                {% if current_oos_list %}
                <div class="overflow-x-auto">
                    <table class="w-full" style="table-layout: fixed; min-width: 1400px;">
                        <thead style="background: var(--bg_hover);">
                            <tr>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 180px;">Ad Name</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 100px;">Stockout Date</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 70px;">Duration</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 80px;">Product Price</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 100px;">Revenue Loss</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 90px;">Priority Score</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 60px;">Events</th>
                                <th class="px-4 py-3 text-right text-xs font-black uppercase whitespace-nowrap" style="width: 70px;">Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for item in current_oos_list %}
                            <tr class="table-row cursor-pointer" onclick="showAdHistory('{{ item.ad_name }}')" style="border-bottom:1px solid var(--border);">
                                <td class="px-4 py-3 font-semibold text-sm">{{ item.ad_name }}</td>
                                <td class="px-4 py-3 text-sm">
                                    {{ item.since }} {{ item.since_time }}
                                </td>
                                <td class="px-4 py-3">
                                    <span class="badge bg-gradient-to-r from-red-500 to-red-600 text-white text-xs">{{ item.days_oos }}d</span>
                                </td>
                                <td class="px-4 py-3">
                                    <span class="text-green-600 font-bold">PKR ${{ "{:,.0f}".format(item.product_price) }}</span>
                                </td>
                                <td class="px-4 py-3">
                                    <span class="text-red-600 font-bold">${{ item.revenue_loss }}</span>
                                </td>
                                <td class="px-4 py-3">
                                    <span class="badge bg-orange-100 text-orange-700">{{ item.priority_score }}</span>
                                </td>
                                <td class="px-4 py-3 text-sm text-muted">{{ item.event_count }}</td>
                                <td class="px-4 py-3 text-right">
                                    <a href="{{ item.url }}" target="_blank" onclick="event.stopPropagation()" class="btn-outline px-3 py-1 text-xs">View</a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <div class="p-12 text-center">
                    <div class="w-16 h-16 rounded-full bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center mx-auto mb-3">
                        <i class="ph-fill ph-check text-white text-2xl"></i>
                    </div>
                    <p class="text-lg font-bold">All systems operational</p>
                    <p class="text-sm text-muted">No offline ads detected</p>
                </div>
                {% endif %}
            </div>

            <div id="tab-history" class="tab-content">
                <div class="overflow-x-auto">
                    <table class="w-full" style="table-layout: fixed; min-width: 1200px;">
                        <thead style="background: var(--bg_hover);">
                            <tr>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 140px;">Date/Time</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 200px;">Ad Name</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 150px;">Event</th>
                                <th class="px-4 py-3 text-left text-xs font-black uppercase whitespace-nowrap" style="width: 120px;">Action</th>
                                <th class="px-4 py-3 text-right text-xs font-black uppercase whitespace-nowrap" style="width: 80px;">Link</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for log in logs[:100] %}
                            <tr class="table-row cursor-pointer" onclick="showAdHistory('{{ log['Ad Name'] }}')" style="border-bottom: 1px solid var(--border);">
                                <td class="px-4 py-3 text-sm">
                                    {{ log.date_only }} {{ log.time_only }}
                                </td>
                                <td class="px-4 py-3 font-semibold">{{ log['Ad Name'] }}</td>
                                <td class="px-4 py-3">
                                    <span class="badge bg-blue-100 text-blue-700 text-xs">{{ log.Event }}</span>
                                </td>
                                <td class="px-4 py-3">
                                    {% if 'off' in log.Action|lower %}
                                        <span class="badge bg-gradient-to-r from-red-500 to-red-600 text-white text-xs">STOCK OUT</span>
                                    {% elif 'on' in log.Action|lower %}
                                        <span class="badge bg-gradient-to-r from-green-500 to-emerald-600 text-white text-xs">BACK IN STOCK</span>
                                    {% else %}
                                        <span class="text-xs text-muted">{{ log.Action }}</span>
                                    {% endif %}
                                </td>
                                <td class="px-4 py-3 text-right">
                                    <a href="{{ log.URL }}" target="_blank" onclick="event.stopPropagation()" class="btn-outline px-2 py-1 text-xs">
                                        <i class="ph-bold ph-arrow-square-out"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <div class="mt-6 text-center text-sm text-muted">
            <p>
                <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-yellow-100 text-yellow-800 border border-yellow-300">
                    ⚠️ Sample Data - Prices from CSV, not live scraped
                </span>
                <span class="ml-3 text-muted">|</span>
                <span class="ml-3">Last updated: {{ last_update }}</span>
                <span class="text-muted">|</span>
                Data retention: {{ history_days }} days
            </p>
        </div>
    </main>

    <!-- Modal -->
    <div id="adHistoryModal" class="modal">
        <div class="card w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden">
            <div class="px-5 py-4 border-b flex items-center justify-between" style="border-color: var(--border);">
                <div>
                    <h3 id="modalAdName" class="text-lg font-bold">Ad History</h3>
                    <p id="modalAdInfo" class="text-sm text-muted">Loading...</p>
                </div>
                <button onclick="closeModal()" class="btn-outline w-9 h-9 rounded-lg flex items-center justify-center">
                    <i class="ph-bold ph-x"></i>
                </button>
            </div>
            <div id="adHistoryContent" class="p-5 overflow-y-auto max-h-[60vh]">
                <div class="flex items-center justify-center py-8">
                    <i class="ph ph-spinner animate-spin text-2xl" style="color: var(--primary);"></i>
                    <span class="ml-2 text-muted">Loading...</span>
                </div>
            </div>
        </div>
    </div>

    <script>
        let themes = {{ THEMES | safe }};
        let currentTheme = '{{ theme }}';
        let currentRegion = '{{ region }}';
        let currentChartType = 'line';
        let mainChart, pieChart;
        let chartData = {{ chart_json | safe }};

        function applyTheme() {
            const theme = themes[currentTheme];
            const root = document.documentElement;
            root.style.setProperty('--bg', theme.bg);
            root.style.setProperty('--bg_card', theme.bg_card);
            root.style.setProperty('--bg_hover', theme.bg_hover);
            root.style.setProperty('--text', theme.text);
            root.style.setProperty('--text_muted', theme.text_muted);
            root.style.setProperty('--border', theme.border);
            root.style.setProperty('--primary', theme.primary);
            root.style.setProperty('--success', theme.success);
            root.style.setProperty('--danger', theme.danger);
            root.style.setProperty('--warning', theme.warning);

            // Update charts
            if (mainChart) updateCharts();
        }

        document.addEventListener('DOMContentLoaded', function() {
            applyTheme();
            initCharts();
            updateChartButtons();
        });

        function toggleTheme() {
            currentTheme = currentTheme === 'white' ? 'black' : 'white';
            applyTheme();
        }

        function changeRegion() {
            const region = document.getElementById('regionSelect').value;
            window.location.href = `/?region=${region}&theme=${currentTheme}`;
        }

        function initCharts() {
            initMainChart();
            initPieChart();
        }

        function initMainChart() {
            const ctx = document.getElementById('mainChart');
            if (!ctx) {
                console.error('Chart canvas not found');
                return;
            }

            const primaryColor = themes[currentTheme].primary;
            console.log('Initializing main chart with data:', chartData);

            // Ensure chartData has the correct structure
            const dates = chartData.dates || [];
            const counts = chartData.counts || [];

            console.log('Dates:', dates);
            console.log('Counts:', counts);

            if (dates.length === 0 || counts.length === 0) {
                console.log('No data available for charts');
                // Show a message in the chart area
                ctx.font = '14px Inter';
                ctx.fillStyle = theme.text_muted;
                ctx.textAlign = 'center';
                ctx.fillText('No data available', ctx.canvas.width / 2, ctx.canvas.height / 2);
                return;
            }

            mainChart = new Chart(ctx, {
                type: currentChartType,
                data: {
                    labels: dates,
                    datasets: [{
                        label: 'Events',
                        data: counts,
                        backgroundColor: currentChartType === 'bar' ? primaryColor : primaryColor + '30',
                        borderColor: primaryColor,
                        borderWidth: 2,
                        tension: 0.4,
                        fill: currentChartType === 'line',
                        pointBackgroundColor: primaryColor,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2,
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        y: { beginAtZero: true, grid: { color: themes[currentTheme].border + '60' } },
                        x: { grid: { display: false } }
                    }
                }
            });
        }

        function initPieChart() {
            const ctx = document.getElementById('pieChart');
            if (!ctx) {
                console.error('Pie chart canvas not found');
                return;
            }

            const theme = themes[currentTheme];
            const stats = chartData.stats || {ad_price_data: [], restock: 0, notification: 0};
            console.log('Initializing pie chart with stats:', stats);

            // Show individual ads with product price, plus restocks and notifications
            const adData = stats.ad_price_data || [];
            const restockCount = stats.restock || 0;
            const notificationCount = stats.notification || 0;

            if (adData.length === 0 && restockCount === 0 && notificationCount === 0) {
                console.log('No data for pie chart');
                const canvas = document.getElementById('pieChart');
                if (canvas) {
                    const ctx2 = canvas.getContext('2d');
                    ctx2.font = '14px Inter';
                    ctx2.fillStyle = theme.text_muted;
                    ctx2.textAlign = 'center';
                    ctx2.fillText('No data available', canvas.width / 2, canvas.height / 2);
                }
                return;
            }

            // Generate labels, data, and colors
            const labels = [];
            const data = [];
            const colors = [];

            // Add ads with product price
            adData.forEach(ad => {
                // Shorten ad name for display
                const shortName = ad.ad_name.length > 25 ? ad.ad_name.substring(0, 25) + '...' : ad.ad_name;
                labels.push(`${shortName} (PKR ${ad.product_price.toLocaleString()})`);
                data.push(ad.product_price);

                // Color based on price amount
                let color;
                if (ad.product_price >= 500) {
                    color = currentTheme === 'white' ? '#991b1b' : '#7f1d1d'; // Deep red for $500+
                } else if (ad.product_price >= 200) {
                    color = currentTheme === 'white' ? '#dc2626' : '#b91c1c'; // Red for $200+
                } else {
                    color = currentTheme === 'white' ? '#f87171' : '#fca5a5'; // Light red for lower
                }
                colors.push(color);
            });

            // Add restocks
            if (restockCount > 0) {
                labels.push(`Restocks (${restockCount})`);
                data.push(restockCount);
                colors.push(currentTheme === 'white' ? '#84cc16' : '#a3e635'); // Lime-green
            }

            // Add notifications
            if (notificationCount > 0) {
                labels.push(`Notifications (${notificationCount})`);
                data.push(notificationCount);
                colors.push(currentTheme === 'white' ? '#3b82f6' : '#60a5fa'); // Blue
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
                        legend: { position: 'bottom', labels: { padding: 10, usePointStyle: true, font: { size: 10 } } },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    const label = context.label || '';
                                    const value = context.parsed || 0;
                                    return label;
                                }
                            }
                        }
                    },
                    cutout: '65%'
                }
            });
        }

        function updateCharts() {
            const primaryColor = themes[currentTheme].primary;

            // Update main chart
            mainChart.data.datasets[0].backgroundColor = currentChartType === 'bar' ? primaryColor : primaryColor + '30';
            mainChart.data.datasets[0].borderColor = primaryColor;
            mainChart.data.datasets[0].pointBackgroundColor = primaryColor;
            mainChart.options.scales.y.grid.color = themes[currentTheme].border + '60';
            mainChart.update();

            // Update pie chart with theme-specific colors based on product price per ad
            const stats = chartData.stats || {ad_price_data: [], restock: 0, notification: 0};
            const adData = stats.ad_price_data || [];
            const restockCount = stats.restock || 0;
            const notificationCount = stats.notification || 0;
            const colors = [];

            // Colors for ads
            adData.forEach(ad => {
                let color;
                if (ad.product_price >= 500) {
                    color = currentTheme === 'white' ? '#991b1b' : '#7f1d1d';
                } else if (ad.product_price >= 200) {
                    color = currentTheme === 'white' ? '#dc2626' : '#b91c1c';
                } else {
                    color = currentTheme === 'white' ? '#f87171' : '#fca5a5';
                }
                colors.push(color);
            });

            // Color for restocks
            if (restockCount > 0) {
                colors.push(currentTheme === 'white' ? '#84cc16' : '#a3e635');
            }

            // Color for notifications
            if (notificationCount > 0) {
                colors.push(currentTheme === 'white' ? '#3b82f6' : '#60a5fa');
            }

            pieChart.data.datasets[0].backgroundColor = colors;
            pieChart.update();
        }

        function setChartType(type) {
            currentChartType = type;
            updateChartButtons();
            mainChart.config.type = type;
            mainChart.data.datasets[0].fill = type === 'line';
            mainChart.update();
        }

        function updateChartButtons() {
            document.querySelectorAll('.chart-btn').forEach(btn => {
                const type = btn.dataset.type;
                if (type === currentChartType) {
                    btn.classList.add('btn-primary');
                    btn.classList.remove('btn-outline');
                } else {
                    btn.classList.remove('btn-primary');
                    btn.classList.add('btn-outline');
                }
            });
        }

        function switchTab(tabName) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`.tab-btn[data-tab="${tabName}"]`).classList.add('active');
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            document.getElementById(`tab-${tabName}`).classList.add('active');
        }

        function showAdHistory(adName) {
            const modal = document.getElementById('adHistoryModal');
            const content = document.getElementById('adHistoryContent');
            document.getElementById('modalAdName').textContent = adName;
            document.getElementById('modalAdInfo').textContent = 'Loading...';
            modal.classList.add('active');

            fetch(`/api/ad-history?region=${currentRegion}&ad_name=${encodeURIComponent(adName)}`)
                .then(r => {
                    if (!r.ok) {
                        throw new Error(`Server returned ${r.status}`);
                    }
                    return r.json();
                })
                .then(data => {
                    if (data.error) {
                        content.innerHTML = `<div class="text-center text-red-500 py-8 font-semibold">${data.error}</div>`;
                        return;
                    }
                    document.getElementById('modalAdInfo').textContent = `${data.history_count} events`;
                    if (data.history.length === 0) {
                        content.innerHTML = `<div class="text-center py-8 text-muted">No history found</div>`;
                        return;
                    }
                    let html = '<div class="space-y-3">';
                    data.history.forEach(e => {
                        let bg = 'bg-gray-500';
                        let icon = 'ph-dot';
                        if (e.action === 'Ad turned off') { bg = 'bg-gradient-to-br from-red-500 to-red-600'; icon = 'ph-prohibit'; }
                        else if (e.action === 'Ad turned on') { bg = 'bg-gradient-to-br from-green-500 to-emerald-600'; icon = 'ph-check'; }
                        else { bg = 'bg-gradient-to-br from-blue-500 to-indigo-600'; icon = 'ph-bell'; }
                        html += `
                            <div class="flex items-start space-x-3 p-3 card">
                                <div class="w-9 h-9 rounded-lg ${bg} flex items-center justify-center flex-shrink-0">
                                    <i class="ph-fill ${icon} text-white text-sm"></i>
                                </div>
                                <div class="flex-1">
                                    <div class="flex justify-between text-sm">
                                        <span class="font-bold">${e.date}</span>
                                        <span class="text-muted">${e.time}</span>
                                    </div>
                                    <div class="text-sm mt-1">${e.event}</div>
                                </div>
                            </div>
                        `;
                    });
                    html += '</div>';
                    content.innerHTML = html;
                })
                .catch(err => {
                    content.innerHTML = `<div class="text-center text-red-500 py-8">Error loading history: ${err.message}</div>`;
                });
        }

        function closeModal() {
            document.getElementById('adHistoryModal').classList.remove('active');
        }

        function exportData() {
            const data = { offline: {{ current_oos_list | safe }}, logs: {{ logs_to_export | safe }} };
            const wb = XLSX.utils.book_new();

            if (data.offline.length > 0) {
                const ws1 = XLSX.utils.json_to_sheet(data.offline.map(i => ({
                    'Ad Name': i.ad_name, 'Stockout Date': i.since, 'Duration (days)': i.days_oos,
                    'Total Downtime': i.total_downtime, 'Events': i.event_count, 'URL': i.url
                })));
                XLSX.utils.book_append_sheet(wb, ws1, 'Offline Ads');
            }

            if (data.logs.length > 0) {
                const ws2 = XLSX.utils.json_to_sheet(data.logs);
                XLSX.utils.book_append_sheet(wb, ws2, 'Event Log');
            }

            XLSX.writeFile(wb, `Burlin_Analytics_${currentRegion}_${new Date().toISOString().split('T')[0]}.xlsx`);
        }

        document.getElementById('adHistoryModal').addEventListener('click', function(e) {
            if (e.target === this) closeModal();
        });
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') closeModal();
        });
    </script>
</body>
</html>
"""

def load_data(region: str) -> pd.DataFrame:
    df_global = pd.DataFrame()
    if os.path.exists(global_LOG_PATH):
        try:
            df_global = pd.read_excel(global_LOG_PATH)
            if not df_global.empty:
                df_global["Region"] = "Global"
        except Exception as e:
            print(f"Error loading global log: {e}")

    if region == "global":
        df = df_global

    if not df.empty and "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        df = df.sort_values(by="Timestamp", ascending=True)

    return df

def calculate_metrics(df: pd.DataFrame, daily_revenue: float) -> tuple:
    if df.empty:
        return 0, 0.0, 0.0, [], {}, 0, []

    total_oos_seconds = 0
    current_oos_products = []

    grouped = df.groupby("Ad Name")
    ad_price_data = []  # Track product prices per ad

    for ad_name, group in grouped:
        group = group.sort_values("Timestamp")
        is_oos = False
        oos_start_time = None
        ad_total_seconds = 0
        event_count = len(group)
        last_url = group.iloc[-1]["URL"] if "URL" in group.columns else "#"

        for _, row in group.iterrows():
            action = str(row.get("Action", "")).lower()
            timestamp = row["Timestamp"]

            if "off" in action and not is_oos:
                is_oos = True
                oos_start_time = timestamp
            elif "on" in action and is_oos and oos_start_time:
                ad_total_seconds += (timestamp - oos_start_time).total_seconds()
                is_oos = False
                oos_start_time = None

        if is_oos and oos_start_time:
            current_duration = (datetime.now() - oos_start_time).total_seconds()
            ad_total_seconds += current_duration

            current_oos_products.append({
                "ad_name": ad_name,
                "url": last_url,
                "days_oos": round(current_duration / 86400, 1),
                "since": oos_start_time.strftime("%Y-%m-%d"),
                "since_time": oos_start_time.strftime("%H:%M"),
                "total_downtime": round(ad_total_seconds / 86400, 1),
                "event_count": event_count
            })

        total_oos_seconds += ad_total_seconds

        # Get product price for this ad from CSV (not random)
        product_price = get_product_price_from_csv(last_url)
        if product_price > 0:
            ad_price_data.append({
                "ad_name": ad_name,
                "product_price": round(product_price, 2),
                "url": last_url
            })

    all_chart_data = {}
    periods = {'day': 1, 'week': 7, 'month': 30}

    for period_name, days in periods.items():
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start_date, end_date)

        period_df = df[df['Timestamp'].dt.date >= start_date]
        date_counts = period_df['Timestamp'].dt.date.value_counts().sort_index()

        chart_dates = []
        chart_counts = []
        for d in date_range:
            chart_dates.append(d.strftime("%b %d"))
            chart_counts.append(int(date_counts.get(d, 0)))

        all_chart_data[period_name] = {"dates": chart_dates, "counts": chart_counts}

    # Calculate chart stats for pie chart
    stock_out_count = len(df[df['Action'].str.contains('off', case=False, na=False)])
    restock_count = len(df[df['Action'].str.contains('on', case=False, na=False)])
    notification_count = len(df[~df['Action'].str.contains('off', case=False, na=False) & ~df['Action'].str.contains('on', case=False, na=False)])
    total_count = len(df)

    # Add stats BEFORE creating JSON
    total_revenue_loss = (total_oos_seconds / 86400) * daily_revenue
    # Sort ads by product price (descending) and take top ones for pie chart
    ad_price_sorted = sorted(ad_price_data, key=lambda x: x['product_price'], reverse=True)
    all_chart_data['week']['stats'] = {
        "stock_out": stock_out_count,
        "restock": restock_count,
        "notification": notification_count,
        "revenue_loss": round(total_revenue_loss, 2),
        "ad_price_data": ad_price_sorted[:10]  # Top 10 ads by price for pie chart
    }
    chart_json = json.dumps(all_chart_data['week'])

    logs_display = df.sort_values(by="Timestamp", ascending=False).to_dict(orient="records")
    for log in logs_display:
        if isinstance(log["Timestamp"], pd.Timestamp):
            ts = log["Timestamp"]
            log["date_only"] = ts.strftime('%Y-%m-%d')
            log["time_only"] = ts.strftime('%H:%M:%S')

    # Calculate daily summary
    daily_summary = []
    if not df.empty and "Timestamp" in df.columns:
        df['date_only'] = df['Timestamp'].dt.date
        df['is_stock_out'] = df['Action'].str.contains('off', case=False, na=False)
        df['is_back_in_stock'] = df['Action'].str.contains('on', case=False, na=False)

        grouped_by_date = df.groupby('date_only').agg({
            'is_stock_out': 'sum',
            'is_back_in_stock': 'sum',
            'Action': 'count',
            'Ad Name': lambda x: x.nunique()
        }).reset_index()
        grouped_by_date.columns = ['date', 'stock_out', 'back_in_stock', 'total_events', 'unique_ads']
        grouped_by_date['repeated_events'] = grouped_by_date['total_events'] - grouped_by_date['unique_ads']

        for _, row in grouped_by_date.sort_values('date', ascending=False).iterrows():
            daily_summary.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'stock_out': int(row['stock_out']),
                'back_in_stock': int(row['back_in_stock']),
                'total_events': int(row['total_events']),
                'unique_ads': int(row['unique_ads']),
                'repeated_events': int(row['repeated_events'])
            })

    return len(current_oos_products), total_oos_seconds / 86400, (total_oos_seconds / 86400) * daily_revenue, current_oos_products, chart_json, all_chart_data, total_count, logs_display, daily_summary


def calculate_enhanced_revenue_metrics(df: pd.DataFrame, conversion_rate: float = 0.5) -> tuple:
    """
    Calculate revenue impact with per-product pricing and priority scoring.

    Formula: Revenue Loss = (days_out) × (product_price) × (conversion_rate)
    Priority Score = (downtime_days) × (product_price)

    Args:
        df: DataFrame with ad events (must have Product_Price column)
        conversion_rate: Daily conversion rate (default: 0.5 = 50%)

    Returns:
        (count_oos, total_days, total_rev_loss, current_oos_list, ad_metrics,
         chart_json, all_chart_data, total_events, logs, daily_summary)
    """
    if df.empty:
        return 0, 0.0, 0.0, [], {}, {}, 0, [], []

    ad_metrics = []
    total_revenue_loss = 0.0
    total_downtime_days = 0.0

    for ad_name, group in df.groupby("Ad Name"):
        group = group.sort_values("Timestamp")

        # Get latest product price from logs
        latest_price = 285.0  # Default fallback
        if "Product_Price" in group.columns:
            valid_prices = group["Product_Price"].dropna()
            if not valid_prices.empty:
                latest_price = valid_prices.iloc[-1]

        # Calculate downtime in hours and days
        is_oos = False
        oos_start = None
        ad_downtime_hours = 0.0
        event_count = len(group)
        last_url = group.iloc[-1]["URL"] if "URL" in group.columns else "#"

        for _, row in group.iterrows():
            action = str(row.get("Action", "")).lower()
            timestamp = row["Timestamp"]

            if "off" in action and not is_oos:
                is_oos = True
                oos_start = timestamp
            elif "on" in action and is_oos and oos_start:
                duration_hours = (timestamp - oos_start).total_seconds() / 3600
                ad_downtime_hours += duration_hours
                is_oos = False
                oos_start = None

        # Currently offline
        if is_oos and oos_start:
            current_duration_hours = (datetime.now() - oos_start).total_seconds() / 3600
            ad_downtime_hours += current_duration_hours

        ad_downtime_days = ad_downtime_hours / 24

        # Revenue loss = (days out) × (price) × (conversion rate)
        # Assuming: 1 sale per day × conversion_rate × product_price
        daily_sales = 1 * conversion_rate
        revenue_loss = ad_downtime_days * daily_sales * latest_price

        # Priority score = downtime × price (for sorting)
        priority_score = ad_downtime_days * latest_price

        ad_metrics.append({
            "ad_name": ad_name,
            "url": last_url,
            "product_price": round(latest_price, 2),
            "days_out": round(ad_downtime_days, 1),
            "hours_out": round(ad_downtime_hours % 24, 1),
            "total_downtime": round(ad_downtime_days, 1),
            "revenue_loss": round(revenue_loss, 2),
            "priority_score": round(priority_score, 2),
            "event_count": event_count,
            "status": "offline" if is_oos else "active"
        })

        total_revenue_loss += revenue_loss
        total_downtime_days += ad_downtime_days

    # Sort by priority score (descending)
    ad_metrics.sort(key=lambda x: x["priority_score"], reverse=True)

    # Extract currently offline ads
    current_oos_list = [m for m in ad_metrics if m["status"] == "offline"]

    # Generate chart data (reuse existing logic)
    all_chart_data = {}
    periods = {'day': 1, 'week': 7, 'month': 30}

    for period_name, days in periods.items():
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        date_range = pd.date_range(start_date, end_date)

        period_df = df[df['Timestamp'].dt.date >= start_date]
        date_counts = period_df['Timestamp'].dt.date.value_counts().sort_index()

        chart_dates = []
        chart_counts = []
        for d in date_range:
            chart_dates.append(d.strftime("%b %d"))
            chart_counts.append(int(date_counts.get(d, 0)))

        all_chart_data[period_name] = {"dates": chart_dates, "counts": chart_counts}

    # Calculate chart stats for pie chart
    stock_out_count = len(df[df['Action'].str.contains('off', case=False, na=False)])
    restock_count = len(df[df['Action'].str.contains('on', case=False, na=False)])
    notification_count = len(df[~df['Action'].str.contains('off', case=False, na=False) & ~df['Action'].str.contains('on', case=False, na=False)])

    # Add ad_price_data for pie chart
    ad_price_data = [{"ad_name": m["ad_name"], "product_price": m["product_price"]} for m in ad_metrics[:10]]

    all_chart_data['week']['stats'] = {
        "stock_out": int(stock_out_count),
        "restock": int(restock_count),
        "notification": int(notification_count),
        "revenue_loss": round(float(total_revenue_loss), 2),
        "ad_price_data": ad_price_data[:10]  # Top 10 ads by price for pie chart
    }
    chart_json = json.dumps(all_chart_data['week'], default=str)

    # Prepare logs display
    logs_display = df.sort_values(by="Timestamp", ascending=False).to_dict(orient="records")
    for log in logs_display:
        if isinstance(log["Timestamp"], pd.Timestamp):
            ts = log["Timestamp"]
            log["date_only"] = ts.strftime('%Y-%m-%d')
            log["time_only"] = ts.strftime('%H:%M:%S')

    # Calculate daily summary
    daily_summary = []
    if not df.empty and "Timestamp" in df.columns:
        df['date_only'] = df['Timestamp'].dt.date
        df['is_stock_out'] = df['Action'].str.contains('off', case=False, na=False)
        df['is_back_in_stock'] = df['Action'].str.contains('on', case=False, na=False)

        grouped_by_date = df.groupby('date_only').agg({
            'is_stock_out': 'sum',
            'is_back_in_stock': 'sum',
            'Action': 'count',
            'Ad Name': lambda x: x.nunique()
        }).reset_index()
        grouped_by_date.columns = ['date', 'stock_out', 'back_in_stock', 'total_events', 'unique_ads']
        grouped_by_date['repeated_events'] = grouped_by_date['total_events'] - grouped_by_date['unique_ads']

        for _, row in grouped_by_date.sort_values('date', ascending=False).iterrows():
            daily_summary.append({
                'date': row['date'].strftime('%Y-%m-%d'),
                'stock_out': int(row['stock_out']),
                'back_in_stock': int(row['back_in_stock']),
                'total_events': int(row['total_events']),
                'unique_ads': int(row['unique_ads']),
                'repeated_events': int(row['repeated_events'])
            })

    total_count = len(df)

    return (
        len(current_oos_list),
        total_downtime_days,
        total_revenue_loss,
        current_oos_list,
        ad_metrics,
        chart_json,
        all_chart_data,
        total_count,
        logs_display,
        daily_summary
    )


@app.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    region: str = Query("global", pattern="^(global)$"),
    revenue: float = Query(100.0, ge=0),
    conversion_rate: float = Query(0.5, ge=0, le=1),  # NEW PARAMETER
    theme: str = Query("black", pattern="^(white|black)$")
):
    df = load_data(region)

    # Use enhanced revenue metrics with per-product pricing
    count_oos, total_days, rev_loss, current_oos_list, all_ad_metrics, chart_json, all_chart_data, total_events, logs, daily_summary = calculate_enhanced_revenue_metrics(df, conversion_rate)

    # Top products (all metrics, sorted by priority score)
    top_products = all_ad_metrics[:10]

    logs_for_export = []
    for log in logs[:100]:
        logs_for_export.append({
            "date_only": log["date_only"], "time_only": log["time_only"],
            "Ad Name": log["Ad Name"], "Event": log.get("Event", "N/A"),
            "Action": log.get("Action", "N/A"), "URL": log.get("URL", "#")
        })

    template = Template(HTML_TEMPLATE)
    html_content = template.render(
        region=region, theme=theme, revenue=int(revenue), conversion_rate=conversion_rate,
        count_oos=count_oos, total_days=f"{total_days:,.1f}", rev_loss=f"{rev_loss:,.2f}",
        current_oos_list=current_oos_list, top_products=top_products,  # NEW VARIABLE
        logs=logs, logs_to_export=json.dumps(logs_for_export),
        chart_json=chart_json, all_chart_data=json.dumps(all_chart_data, default=str), THEMES=json.dumps(THEMES),
        total_events=total_events, history_days=HISTORY_DAYS, last_update=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        daily_summary=daily_summary
    )
    return HTMLResponse(content=html_content)

@app.get("/api/ad-history")
async def get_ad_history(region: str = Query(...), ad_name: str = Query(...)):
    df = load_data(region)
    if df.empty:
        return JSONResponse({"error": "No data available", "history": [], "history_count": 0})
    ad_df = df[df["Ad Name"] == ad_name].copy()
    if ad_df.empty:
        return JSONResponse({"error": "Ad not found", "history": [], "history_count": 0})

    cutoff_date = datetime.now() - timedelta(days=HISTORY_DAYS)
    ad_df = ad_df[ad_df["Timestamp"] >= cutoff_date].copy()

    history = []
    for _, row in ad_df.iterrows():
        ts = row["Timestamp"]
        history.append({
            "date": ts.strftime("%Y-%m-%d"), "time": ts.strftime("%H:%M:%S"),
            "event": row.get("Event", "N/A"), "action": row.get("Action", "N/A"),
            "url": row.get("URL", "N/A")
        })

    history.sort(key=lambda x: (x["date"], x["time"]), reverse=True)
    return JSONResponse({"ad_name": ad_name, "history_count": len(history), "history": history})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8501)
