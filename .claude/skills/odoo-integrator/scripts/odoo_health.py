#!/usr/bin/env python3
"""
Odoo Health Check System

Comprehensive health monitoring for the Odoo integration stack.

Checks:
- Odoo API connectivity
- MCP server health
- Redis cache status
- Database connectivity
- Disk space
- Memory usage
- Sync lag
- Error rates

Usage:
    from odoo_health import HealthChecker

    checker = HealthChecker()
    report = checker.check_all()
    print(report.to_json())
"""

from __future__ import annotations

import os
import sys
import time
import shutil
import socket
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Literal
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
import subprocess

try:
    import psutil
except ImportError:
    psutil = None

try:
    import requests
except ImportError:
    requests = None

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


# =============================================================================
# Health Status
# =============================================================================

class HealthStatus(Enum):
    """Health check status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Individual health check result"""
    name: str
    status: HealthStatus
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: float = 0
    details: Dict[str, Any] = field(default_factory=dict)
    critical: bool = False  # If True, failure affects overall health

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "details": self.details,
            "critical": self.critical
        }


@dataclass
class HealthReport:
    """Overall health report"""
    status: HealthStatus
    checks: List[HealthCheck]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    uptime_seconds: float = 0
    hostname: str = field(default_factory=lambda: socket.gethostname())

    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "timestamp": self.timestamp,
            "hostname": self.hostname,
            "uptime_seconds": self.uptime_seconds,
            "checks": [check.to_dict() for check in self.checks],
            "summary": {
                "total": len(self.checks),
                "healthy": sum(1 for c in self.checks if c.status == HealthStatus.HEALTHY),
                "degraded": sum(1 for c in self.checks if c.status == HealthStatus.DEGRADED),
                "unhealthy": sum(1 for c in self.checks if c.status == HealthStatus.UNHEALTHY),
                "critical_unhealthy": sum(1 for c in self.checks
                                        if c.critical and c.status != HealthStatus.HEALTHY)
            }
        }

    def to_json(self) -> str:
        import json
        return json.dumps(self.to_dict(), indent=2)


# =============================================================================
# Health Checks
# =============================================================================

class HealthChecker:
    """Health check executor"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.start_time = time.time()
        self.checks: List[Callable] = [
            self.check_odoo_api,
            self.check_mcp_server,
            self.check_redis_cache,
            self.check_disk_space,
            self.check_memory,
            self.check_sync_lag,
            self.check_error_rate,
            self.check_filesystem,
            self.check_network
        ]

    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load health check configuration"""
        return {
            "odoo_url": os.getenv("ODOO_URL", "http://localhost:8069"),
            "mcp_url": os.getenv("ODOO_MCP_URL", "http://localhost:8000"),
            "redis_host": os.getenv("REDIS_HOST", "localhost"),
            "redis_port": int(os.getenv("REDIS_PORT", "6379")),
            "vault_path": Path(os.getenv("VAULT_PATH", ".")),
            "disk_threshold": 90,  # Alert at 90% disk usage
            "memory_threshold": 90,  # Alert at 90% memory usage
            "sync_lag_threshold": 3600,  # Alert if sync is 1 hour behind
            "error_rate_threshold": 0.1,  # Alert at 10% error rate
            "timeout": 5
        }

    def check_all(self) -> HealthReport:
        """Run all health checks"""
        checks = []
        overall_status = HealthStatus.HEALTHY

        for check_func in self.checks:
            try:
                start = time.time()
                result = check_func()
                result.duration_ms = (time.time() - start) * 1000
                checks.append(result)

                # Update overall status
                if result.status == HealthStatus.UNHEALTHY:
                    if result.critical:
                        overall_status = HealthStatus.UNHEALTHY
                elif result.status == HealthStatus.DEGRADED:
                    if overall_status == HealthStatus.HEALTHY:
                        overall_status = HealthStatus.DEGRADED

            except Exception as e:
                checks.append(HealthCheck(
                    name=check_func.__name__,
                    status=HealthStatus.UNKNOWN,
                    message=f"Check failed: {str(e)}"
                ))

        # Calculate uptime
        uptime = time.time() - self.start_time

        return HealthReport(
            status=overall_status,
            checks=checks,
            uptime_seconds=uptime
        )

    def check_odoo_api(self) -> HealthCheck:
        """Check Odoo API connectivity"""
        try:
            if requests is None:
                return HealthCheck(
                    name="odoo_api",
                    status=HealthStatus.UNKNOWN,
                    message="requests library not available",
                    critical=False
                )

            start = time.time()
            response = requests.get(
                f"{self.config['odoo_url']}/web/version",
                timeout=self.config['timeout']
            )
            duration = (time.time() - start) * 1000

            if response.status_code == 200:
                data = response.json()
                version = data.get("version", "unknown")
                return HealthCheck(
                    name="odoo_api",
                    status=HealthStatus.HEALTHY,
                    message=f"Odoo API is reachable (version: {version})",
                    details={"version": version, "response_time_ms": round(duration, 2)},
                    critical=True
                )
            else:
                return HealthCheck(
                    name="odoo_api",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Odoo API returned status {response.status_code}",
                    details={"status_code": response.status_code},
                    critical=True
                )
        except requests.exceptions.Timeout:
            return HealthCheck(
                name="odoo_api",
                status=HealthStatus.UNHEALTHY,
                message="Odoo API request timed out",
                critical=True
            )
        except requests.exceptions.ConnectionError:
            return HealthCheck(
                name="odoo_api",
                status=HealthStatus.UNHEALTHY,
                message="Cannot connect to Odoo API",
                critical=True
            )
        except Exception as e:
            return HealthCheck(
                name="odoo_api",
                status=HealthStatus.UNKNOWN,
                message=f"Error: {str(e)}",
                critical=True
            )

    def check_mcp_server(self) -> HealthCheck:
        """Check MCP server health"""
        try:
            if requests is None:
                return HealthCheck(
                    name="mcp_server",
                    status=HealthStatus.UNKNOWN,
                    message="requests library not available",
                    critical=False
                )

            response = requests.get(
                f"{self.config['mcp_url']}/health",
                timeout=self.config['timeout']
            )

            if response.status_code == 200:
                data = response.json()
                odoo_connected = data.get("odoo_connected", False)
                status = HealthStatus.HEALTHY if odoo_connected else HealthStatus.DEGRADED

                return HealthCheck(
                    name="mcp_server",
                    status=status,
                    message=f"MCP server is {'connected to Odoo' if odoo_connected else 'running but not connected to Odoo'}",
                    details=data,
                    critical=True
                )
            else:
                return HealthCheck(
                    name="mcp_server",
                    status=HealthStatus.UNHEALTHY,
                    message=f"MCP server returned status {response.status_code}",
                    critical=True
                )
        except Exception as e:
            return HealthCheck(
                name="mcp_server",
                status=HealthStatus.UNHEALTHY,
                message=f"Cannot connect to MCP server: {str(e)}",
                critical=True
            )

    def check_redis_cache(self) -> HealthCheck:
        """Check Redis cache connectivity"""
        try:
            import redis
            client = redis.Redis(
                host=self.config['redis_host'],
                port=self.config['redis_port'],
                socket_timeout=2
            )
            client.ping()
            info = client.info('stats')

            return HealthCheck(
                name="redis_cache",
                status=HealthStatus.HEALTHY,
                message="Redis cache is reachable",
                details={
                    "connected_clients": info.get("connected_clients", 0),
                    "used_memory_human": info.get("used_memory_human", "unknown"),
                    "keyspace_hits": info.get("keyspace_hits", 0),
                    "keyspace_misses": info.get("keyspace_misses", 0)
                },
                critical=False
            )
        except Exception as e:
            return HealthCheck(
                name="redis_cache",
                status=HealthStatus.DEGRADED,
                message=f"Redis cache unavailable: {str(e)}",
                details={"error": str(e)},
                critical=False
            )

    def check_disk_space(self) -> HealthCheck:
        """Check disk space"""
        try:
            vault_path = self.config['vault_path']
            usage = shutil.disk_usage(vault_path)

            used_percent = (usage.used / usage.total) * 100
            threshold = self.config['disk_threshold']

            status = HealthStatus.HEALTHY
            message = f"Disk usage: {used_percent:.1f}%"

            if used_percent >= threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage critical: {used_percent:.1f}% (threshold: {threshold}%)"
            elif used_percent >= threshold - 10:
                status = HealthStatus.DEGRADED
                message = f"Disk usage high: {used_percent:.1f}%"

            return HealthCheck(
                name="disk_space",
                status=status,
                message=message,
                details={
                    "total_gb": round(usage.total / (1024**3), 2),
                    "used_gb": round(usage.used / (1024**3), 2),
                    "free_gb": round(usage.free / (1024**3), 2),
                    "used_percent": round(used_percent, 2),
                    "threshold": threshold
                },
                critical=True
            )
        except Exception as e:
            return HealthCheck(
                name="disk_space",
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check disk space: {str(e)}",
                critical=True
            )

    def check_memory(self) -> HealthCheck:
        """Check memory usage"""
        if psutil is None:
            return HealthCheck(
                name="memory",
                status=HealthStatus.UNKNOWN,
                message="psutil not available"
            )

        try:
            mem = psutil.virtual_memory()
            threshold = self.config['memory_threshold']

            status = HealthStatus.HEALTHY
            message = f"Memory usage: {mem.percent:.1f}%"

            if mem.percent >= threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage critical: {mem.percent:.1f}%"
            elif mem.percent >= threshold - 10:
                status = HealthStatus.DEGRADED
                message = f"Memory usage high: {mem.percent:.1f}%"

            return HealthCheck(
                name="memory",
                status=status,
                message=message,
                details={
                    "total_gb": round(mem.total / (1024**3), 2),
                    "available_gb": round(mem.available / (1024**3), 2),
                    "used_percent": round(mem.percent, 2),
                    "threshold": threshold
                },
                critical=False
            )
        except Exception as e:
            return HealthCheck(
                name="memory",
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check memory: {str(e)}"
            )

    def check_sync_lag(self) -> HealthCheck:
        """Check sync lag (time since last successful sync)"""
        try:
            vault_path = self.config['vault_path']
            state_file = vault_path / "Accounting" / ".sync_state_ultimate.json"

            if not state_file.exists():
                # Try other state files
                state_file = vault_path / "Accounting" / ".sync_state_enhanced.json"

            if not state_file.exists():
                return HealthCheck(
                    name="sync_lag",
                    status=HealthStatus.DEGRADED,
                    message="No sync state file found (sync may not have run)",
                    details={"state_file": str(state_file)},
                    critical=False
                )

            with open(state_file) as f:
                state = json.load(f)

            last_sync = state.get("last_sync")
            if not last_sync:
                return HealthCheck(
                    name="sync_lag",
                    status=HealthStatus.UNKNOWN,
                    message="No last sync timestamp in state"
                )

            last_sync_time = datetime.fromisoformat(last_sync)
            lag = (datetime.now() - last_sync_time).total_seconds()

            threshold = self.config['sync_lag_threshold']
            status = HealthStatus.HEALTHY
            message = f"Last sync: {lag / 60:.1f} minutes ago"

            if lag >= threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Sync lag critical: {lag / 3600:.1f} hours ago"
            elif lag >= threshold / 2:
                status = HealthStatus.DEGRADED
                message = f"Sync lag high: {lag / 60:.1f} minutes ago"

            return HealthCheck(
                name="sync_lag",
                status=status,
                message=message,
                details={
                    "last_sync": last_sync,
                    "lag_seconds": int(lag),
                    "lag_minutes": int(lag / 60),
                    "threshold_seconds": threshold
                },
                critical=False
            )
        except Exception as e:
            return HealthCheck(
                name="sync_lag",
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check sync lag: {str(e)}"
            )

    def check_error_rate(self) -> HealthCheck:
        """Check error rate from logs"""
        try:
            vault_path = self.config['vault_path']
            log_dir = vault_path / "Logs"

            if not log_dir.exists():
                return HealthCheck(
                    name="error_rate",
                    status=HealthStatus.UNKNOWN,
                    message="No logs directory found"
                )

            # Find latest log file
            log_files = sorted(log_dir.glob("odoo_sync_*.log"), reverse=True)

            if not log_files:
                return HealthCheck(
                    name="error_rate",
                    status=HealthStatus.UNKNOWN,
                    message="No log files found"
                )

            latest_log = log_files[0]

            # Count errors in last 100 lines
            error_count = 0
            warning_count = 0
            total_lines = 0

            with open(latest_log, 'r') as f:
                lines = deque(f, 100)
                for line in lines:
                    total_lines += 1
                    if 'ERROR' in line:
                        error_count += 1
                    elif 'WARNING' in line:
                        warning_count += 1

            error_rate = error_count / total_lines if total_lines > 0 else 0
            threshold = self.config['error_rate_threshold']

            status = HealthStatus.HEALTHY
            message = f"Error rate: {error_rate * 100:.1f}%"

            if error_rate >= threshold:
                status = HealthStatus.UNHEALTHY
                message = f"Error rate critical: {error_count} errors in last {total_lines} lines"
            elif error_rate >= threshold / 2:
                status = HealthStatus.DEGRADED
                message = f"Error rate elevated: {error_count} errors in last {total_lines} lines"

            return HealthCheck(
                name="error_rate",
                status=status,
                message=message,
                details={
                    "errors": error_count,
                    "warnings": warning_count,
                    "total_lines": total_lines,
                    "error_rate": round(error_rate, 3),
                    "threshold": threshold
                },
                critical=False
            )
        except Exception as e:
            return HealthCheck(
                name="error_rate",
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check error rate: {str(e)}"
            )

    def check_filesystem(self) -> HealthCheck:
        """Check filesystem accessibility"""
        try:
            vault_path = self.config['vault_path']

            # Check if we can read/write
            test_file = vault_path / ".health_check_test"

            try:
                test_file.write_text("test")
                test_file.unlink()
            except Exception as e:
                return HealthCheck(
                    name="filesystem",
                    status=HealthStatus.UNHEALTHY,
                    message=f"Filesystem not writable: {str(e)}",
                    critical=True
                )

            # Check important directories
            issues = []
            for dir_name in ["Accounting", "Needs_Action", "Logs", "Ralph"]:
                dir_path = vault_path / dir_name
                if dir_path.exists():
                    if not os.access(dir_path, os.W_OK):
                        issues.append(f"{dir_name} not writable")
                else:
                    issues.append(f"{dir_name} does not exist")

            status = HealthStatus.HEALTHY
            message = "Filesystem is accessible"

            if issues:
                status = HealthStatus.DEGRADED
                message = f"Filesystem issues: {', '.join(issues)}"

            return HealthCheck(
                name="filesystem",
                status=status,
                message=message,
                details={"issues": issues},
                critical=True
            )
        except Exception as e:
            return HealthCheck(
                name="filesystem",
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check filesystem: {str(e)}",
                critical=True
            )

    def check_network(self) -> HealthCheck:
        """Check network connectivity"""
        try:
            # Test DNS resolution
            try:
                socket.gethostbyname("localhost")
            except socket.gaierror:
                return HealthCheck(
                    name="network",
                    status=HealthStatus.DEGRADED,
                    message="DNS resolution failed for localhost"
                )

            # Test local ports
            ports_in_use = []
            for port in [8069, 8000, 6379, 5000]:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()

                if result == 0:
                    ports_in_use.append(port)

            return HealthCheck(
                name="network",
                status=HealthStatus.HEALTHY,
                message=f"Network is OK, services on ports: {ports_in_use if ports_in_use else 'none checked'}",
                details={"active_ports": ports_in_use},
                critical=False
            )
        except Exception as e:
            return HealthCheck(
                name="network",
                status=HealthStatus.UNKNOWN,
                message=f"Cannot check network: {str(e)}"
            )


# =============================================================================
# Health Check Server
# =============================================================================

class HealthCheckServer:
    """HTTP server for health check endpoints"""

    def __init__(self, port: int = 8080, host: str = "0.0.0.0"):
        self.port = port
        self.host = host
        self.checker = HealthChecker()

    def _handler(self):
        """Create request handler"""
        from http.server import BaseHTTPRequestHandler

        class HealthHandler(BaseHTTPRequestHandler):
            def __init__(inner_self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def do_GET(inner_self):
                if inner_self.path == '/health':
                    report = self.checker.check_all()

                    # Set response
                    inner_self.send_response(200 if report.status != HealthStatus.UNHEALTHY else 503)
                    inner_self.send_header('Content-Type', 'application/json')
                    inner_self.end_headers()
                    inner_self.wfile.write(report.to_json().encode())

                elif inner_self.path == '/health/ready':
                    # Readiness probe
                    report = self.checker.check_all()
                    ready = report.status != HealthStatus.UNHEALTHY

                    inner_self.send_response(200 if ready else 503)
                    inner_self.send_header('Content-Type', 'application/json')
                    inner_self.end_headers()
                    inner_self.wfile.write(json.dumps({"ready": ready}).encode())

                elif inner_self.path == '/health/live':
                    # Liveness probe
                    inner_self.send_response(200)
                    inner_self.send_header('Content-Type', 'application/json')
                    inner_self.end_headers()
                    inner_self.wfile.write(json.dumps({"alive": True}).encode())

                else:
                    inner_self.send_response(404)
                    inner_self.end_headers()

            def log_message(inner_self, format, *args):
                pass  # Suppress logs

        return HealthHandler

    def start(self):
        """Start health check server"""
        import http.server
        server = http.server.HTTPServer(
            (self.host, self.port),
            self._handler()
        )
        print(f"Health check server running on http://{self.host}:{self.port}/health")
        server.serve_forever()


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Odoo Health Check')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--server', action='store_true', help='Start health check server')
    parser.add_argument('--port', type=int, default=8080, help='Server port')

    args = parser.parse_args()

    checker = HealthChecker()
    report = checker.check_all()

    if args.json:
        print(report.to_json())
    else:
        # Pretty print
        status_colors = {
            HealthStatus.HEALTHY: "\033[92m",  # Green
            HealthStatus.DEGRADED: "\033[93m",  # Yellow
            HealthStatus.UNHEALTHY: "\033[91m",  # Red
            HealthStatus.UNKNOWN: "\033[94m"  # Blue
        }
        reset = "\033[0m"

        color = status_colors.get(report.status, "")
        print(f"\n{'='*60}")
        print(f"Health Status: {color}{report.status.value.upper()}{reset}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Uptime: {report.uptime_seconds / 60:.1f} minutes")
        print(f"{'='*60}\n")

        for check in report.checks:
            color = status_colors.get(check.status, "")
            symbol = "✓" if check.status == HealthStatus.HEALTHY else "✗"
            critical = " [CRITICAL]" if check.critical else ""
            print(f"{symbol} {color}{check.name}{reset}{critical}: {check.message}")
            if args.verbose and check.details:
                for key, value in check.details.items():
                    print(f"    {key}: {value}")

        summary = report.to_dict()['summary']
        print(f"\nSummary: {summary['healthy']} healthy, {summary['degraded']} degraded, {summary['unhealthy']} unhealthy")

    # Return exit code based on health
    if args.server:
        server = HealthCheckServer(port=args.port)
        server.start()
    else:
        return 0 if report.status != HealthStatus.UNHEALTHY else 1


if __name__ == "__main__":
    import json
    sys.exit(main())
