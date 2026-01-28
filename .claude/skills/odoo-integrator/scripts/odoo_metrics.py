#!/usr/bin/env python3
"""
Odoo Sync Metrics Exporter

Prometheus-compatible metrics export for monitoring.

Usage:
    from odoo_metrics import MetricsRegistry

    metrics = MetricsRegistry()
    metrics.counter("sync_records_total").inc()

    # Start metrics server
    metrics.start_server(port=9090)
"""

from __future__ import annotations

import time
import threading
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from prometheus_client import (
    Counter, Gauge, Histogram, Summary,
    CollectorRegistry, generate_latest,
    CONTENT_TYPE_LATEST,
)
from prometheus_client.exposition import MetricsHandler

try:
    from flask import Flask, Response
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False
    from http.server import HTTPServer, BaseHTTPRequestHandler


# =============================================================================
# Metric Types
# =============================================================================

@dataclass
class MetricLabel:
    """Descriptor for a metric label"""
    name: str
    description: str = ""


@dataclass
class MetricDef:
    """Metric definition"""
    name: str
    type: str  # counter, gauge, histogram, summary
    description: str
    labels: List[str] = field(default_factory=list)
    buckets: List[float] = field(default_factory=list)  # For histograms


# =============================================================================
# Metrics Registry
# =============================================================================

class OdooMetrics:
    """Odoo sync metrics"""

    def __init__(self):
        self.registry = CollectorRegistry()

        # Sync metrics
        self.sync_duration = Histogram(
            'odoo_sync_duration_seconds',
            'Sync operation duration',
            ['operation', 'status'],
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30, 60, 120, 300],
            registry=self.registry
        )

        self.sync_records_total = Counter(
            'odoo_sync_records_total',
            'Total records synced',
            ['operation', 'model'],
            registry=self.registry
        )

        self.sync_errors_total = Counter(
            'odoo_sync_errors_total',
            'Total sync errors',
            ['operation', 'error_type'],
            registry=self.registry
        )

        self.sync_cache_hits = Counter(
            'odoo_sync_cache_hits_total',
            'Total cache hits',
            registry=self.registry
        )

        self.sync_cache_misses = Counter(
            'odoo_sync_cache_misses_total',
            'Total cache misses',
            registry=self.registry
        )

        # API metrics
        self.api_requests_total = Counter(
            'odoo_api_requests_total',
            'Total API requests',
            ['endpoint', 'method', 'status'],
            registry=self.registry
        )

        self.api_request_duration = Histogram(
            'odoo_api_request_duration_seconds',
            'API request duration',
            ['endpoint'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 2, 5, 10],
            registry=self.registry
        )

        self.api_rate_limit_hits = Counter(
            'odoo_api_rate_limit_hits_total',
            'Total rate limit hits',
            registry=self.registry
        )

        # Circuit breaker metrics
        self.circuit_breaker_state = Gauge(
            'odoo_circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['service'],
            registry=self.registry
        )

        self.circuit_breaker_failures = Counter(
            'odoo_circuit_breaker_failures_total',
            'Circuit breaker failures',
            ['service'],
            registry=self.registry
        )

        # Queue metrics
        self.queue_size = Gauge(
            'odoo_queue_size',
            'Current queue size',
            ['queue_name'],
            registry=self.registry
        )

        self.queue_processed_total = Counter(
            'odoo_queue_processed_total',
            'Total items processed from queue',
            ['queue_name', 'status'],
            registry=self.registry
        )

        # Database metrics
        self.db_connections = Gauge(
            'odoo_db_connections',
            'Active database connections',
            registry=self.registry
        )

        self.db_query_duration = Histogram(
            'odoo_db_query_duration_seconds',
            'Database query duration',
            ['query_type'],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1],
            registry=self.registry
        )

        # Webhook metrics
        self.webhook_received_total = Counter(
            'odoo_webhook_received_total',
            'Total webhooks received',
            ['event_type'],
            registry=self.registry
        )

        self.webhook_processed_total = Counter(
            'odoo_webhook_processed_total',
            'Total webhooks processed',
            ['event_type', 'status'],
            registry=self.registry
        )

        self.webhook_processing_duration = Histogram(
            'odoo_webhook_processing_duration_seconds',
            'Webhook processing duration',
            ['event_type'],
            buckets=[0.01, 0.05, 0.1, 0.5, 1, 5],
            registry=self.registry
        )

    def record_sync(self, operation: str, status: str, duration: float,
                   records: int = 0, model: str = ""):
        """Record a sync operation"""
        self.sync_duration.labels(
            operation=operation,
            status=status
        ).observe(duration)

        if records > 0:
            self.sync_records_total.labels(
                operation=operation,
                model=model or operation
            ).inc(records)

    def record_api_request(self, endpoint: str, method: str,
                          status: str, duration: float):
        """Record an API request"""
        self.api_requests_total.labels(
            endpoint=endpoint,
            method=method,
            status=status
        ).inc()

        self.api_request_duration.labels(endpoint=endpoint).observe(duration)

    def record_error(self, operation: str, error_type: str):
        """Record a sync error"""
        self.sync_errors_total.labels(
            operation=operation,
            error_type=error_type
        ).inc()

    def set_circuit_breaker_state(self, service: str, state: str):
        """Set circuit breaker state"""
        state_map = {"closed": 0, "open": 1, "half_open": 2}
        self.circuit_breaker_state.labels(service=service).set(
            state_map.get(state, 0)
        )

    def observe_cache_hit(self):
        """Record a cache hit"""
        self.sync_cache_hits.inc()

    def observe_cache_miss(self):
        """Record a cache miss"""
        self.sync_cache_misses.inc()

    def set_queue_size(self, queue_name: str, size: int):
        """Set queue size"""
        self.queue_size.labels(queue_name=queue_name).set(size)

    def record_queue_item(self, queue_name: str, status: str):
        """Record processed queue item"""
        self.queue_processed_total.labels(
            queue_name=queue_name,
            status=status
        ).inc()

    def record_webhook(self, event_type: str, status: str, duration: float):
        """Record webhook processing"""
        self.webhook_received_total.labels(event_type=event_type).inc()

        if status:
            self.webhook_processed_total.labels(
                event_type=event_type,
                status=status
            ).inc()

        self.webhook_processing_duration.labels(
            event_type=event_type
        ).observe(duration)

    def get_metrics_text(self) -> bytes:
        """Get metrics in Prometheus text format"""
        return generate_latest(self.registry)


# =============================================================================
# Metrics Server
# =============================================================================

class MetricsServer:
    """HTTP server for Prometheus metrics scraping"""

    def __init__(self, metrics: OdooMetrics, port: int = 9090,
                 host: str = "0.0.0.0"):
        self.metrics = metrics
        self.port = port
        self.host = host
        self.server = None
        self.thread = None

    def _handler(self):
        """Create request handler"""
        class MetricsRequestHandler(BaseHTTPRequestHandler):
            def __init__(inner_self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def do_GET(inner_self):
                if inner_self.path == '/metrics' or inner_self.path == '/':
                    content = self.metrics.get_metrics_text()
                    inner_self.send_response(200)
                    inner_self.send_header('Content-Type', CONTENT_TYPE_LATEST)
                    inner_self.end_headers()
                    inner_self.wfile.write(content)
                else:
                    inner_self.send_response(404)
                    inner_self.end_headers()

            def log_message(inner_self, format, *args):
                pass  # Suppress log messages

        return MetricsRequestHandler

    def start(self):
        """Start metrics server in background thread"""
        if self.thread:
            return  # Already running

        def run_server():
            self.server = HTTPServer((self.host, self.port), self._handler())
            self.server.serve_forever()

        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop metrics server"""
        if self.server:
            self.server.shutdown()
            self.server = None


# =============================================================================
# Flask-based Metrics Server (if Flask available)
# =============================================================================

if HAS_FLASK:
    class FlaskMetricsServer:
        """Flask-based metrics server with more features"""

        def __init__(self, metrics: OdooMetrics, port: int = 9090,
                     host: str = "0.0.0.0"):
            self.metrics = metrics
            self.port = port
            self.host = host
            self.app = Flask(__name__)
            self._setup_routes()

        def _setup_routes(self):
            @self.app.route('/metrics')
            def metrics():
                content = self.metrics.get_metrics_text()
                return Response(content, mimetype=CONTENT_TYPE_LATEST)

            @self.app.route('/health')
            def health():
                return {'status': 'healthy', 'timestamp': datetime.now().isoformat()}

            @self.app.route('/')
            def index():
                return '''
                <h1>Odoo Sync Metrics</h1>
                <p><a href="/metrics">Prometheus Metrics</a></p>
                <p><a href="/health">Health Check</a></p>
                '''

        def start(self):
            """Start Flask server"""
            self.app.run(host=self.host, port=self.port, debug=False)

        def run_in_thread(self):
            """Start server in background thread"""
            self.thread = threading.Thread(
                target=lambda: self.app.run(
                    host=self.host,
                    port=self.port,
                    debug=False,
                    use_reloader=False
                ),
                daemon=True
            )
            self.thread.start()


# =============================================================================
# Decorator for timing
# =============================================================================

def timed(metrics: OdooMetrics, metric_name: str = None):
    """Decorator to time function calls and record to histogram"""
    def decorator(func):
        name = metric_name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start
                # Record success
                return result
            except Exception as e:
                duration = time.time() - start
                # Record error
                raise

        return wrapper
    return decorator


# =============================================================================
# Global instance
# =============================================================================

_global_metrics: Optional[OdooMetrics] = None
_metrics_lock = threading.Lock()


def get_metrics() -> OdooMetrics:
    """Get global metrics instance"""
    global _global_metrics

    with _metrics_lock:
        if _global_metrics is None:
            _global_metrics = OdooMetrics()

    return _global_metrics


def start_metrics_server(port: int = 9090, host: str = "0.0.0.0"):
    """Start metrics server"""
    metrics = get_metrics()

    if HAS_FLASK:
        server = FlaskMetricsServer(metrics, port, host)
        server.run_in_thread()
    else:
        server = MetricsServer(metrics, port, host)
        server.start()

    return server


# =============================================================================
# Standalone test
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Sync Metrics Server')
    parser.add_argument('--port', type=int, default=9090,
                       help='Metrics server port')
    parser.add_argument('--host', default='0.0.0.0',
                       help='Metrics server host')
    parser.add_argument('--test', action='store_true',
                       help='Generate test metrics')

    args = parser.parse_args()

    metrics = get_metrics()

    if args.test:
        # Generate test metrics
        metrics.record_sync("invoices", "success", 5.2, records=100, model="account.move")
        metrics.record_sync("payments", "success", 2.1, records=50, model="account.payment")
        metrics.record_api_request("/search", "POST", "200", 0.15)
        metrics.observe_cache_hit()
        metrics.observe_cache_hit()
        metrics.observe_cache_miss()
        metrics.set_queue_size("webhook_events", 25)
        metrics.set_circuit_breaker_state("odoo_api", "closed")

        print("Test metrics generated. View at http://{}:{}/metrics".format(
            args.host, args.port))

    # Start server
    print(f"Starting metrics server on http://{args.host}:{args.port}/metrics")
    start_metrics_server(args.port, args.host)

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
