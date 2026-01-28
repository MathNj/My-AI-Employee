#!/usr/bin/env python3
"""
Odoo Sync Script for AI Employee - Enhanced Version

Improvements:
- Redis caching for hot data (5-minute TTL)
- Incremental sync using write_date timestamp
- Exponential backoff with jitter for error handling
- Circuit breaker pattern for Odoo failures
- Configurable batch size
- Performance metrics and logging

Usage:
    python odoo_sync_enhanced.py --sync all
    python odoo_sync_enhanced.py --sync invoices --from-date 2026-01-01
    python odoo_sync_enhanced.py --sync payments --dry-run
    python odoo_sync_enhanced.py --sync all --batch-size 200
"""

from __future__ import annotations

import os
import sys
import json
import logging
import time
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

try:
    import requests
except ImportError:
    print("Installing required package: requests")
    os.system("pip install requests")
    import requests

try:
    import redis
except ImportError:
    print("Redis package not found. Caching will be disabled.")
    redis = None

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
log_dir = Path(__file__).parent.parent.parent.parent / "Logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"odoo_sync_enhanced_{datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("odoo_sync_enhanced")


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class SyncConfig:
    """Configuration for Odoo sync operations"""
    mcp_url: str = "http://localhost:8000"
    vault_path: Path = field(default_factory=lambda: Path(os.getenv("VAULT_PATH", ".")))
    timeout: int = 30
    batch_size: int = int(os.getenv("ODOO_SYNC_BATCH_SIZE", "100"))
    max_retries: int = int(os.getenv("ODOO_MAX_RETRIES", "3"))
    base_retry_delay: float = float(os.getenv("ODOO_RETRY_DELAY", "1.0"))
    retry_multiplier: float = float(os.getenv("ODOO_RETRY_MULTIPLIER", "2.0"))
    max_retry_delay: float = float(os.getenv("ODOO_MAX_RETRY_DELAY", "60.0"))
    circuit_breaker_threshold: int = int(os.getenv("ODOO_CB_THRESHOLD", "5"))
    circuit_breaker_timeout: int = int(os.getenv("ODOO_CB_TIMEOUT", "60"))
    cache_ttl: int = int(os.getenv("ODOO_CACHE_TTL", "300"))  # 5 minutes
    enable_cache: bool = os.getenv("ODOO_ENABLE_CACHE", "true").lower() == "true"
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    incremental_sync: bool = os.getenv("ODOO_INCREMENTAL_SYNC", "true").lower() == "true"

    @property
    def accounting_path(self) -> Path:
        return self.vault_path / "Accounting"


# =============================================================================
# Circuit Breaker
# =============================================================================

class CircuitBreakerState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovery


class CircuitBreaker:
    """Circuit breaker pattern for Odoo API calls"""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0

    def record_success(self):
        """Record a successful call"""
        self.failure_count = 0
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= 2:
                self.state = CircuitBreakerState.CLOSED
                self.success_count = 0
                logger.info("Circuit breaker: CLOSED (recovery confirmed)")

    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.failure_count >= self.failure_threshold:
            if self.state != CircuitBreakerState.OPEN:
                self.state = CircuitBreakerState.OPEN
                logger.warning(f"Circuit breaker: OPEN ({self.failure_count} failures)")

    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == CircuitBreakerState.CLOSED:
            return True

        if self.state == CircuitBreakerState.OPEN:
            if (datetime.now() - self.last_failure_time).total_seconds() >= self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker: HALF_OPEN (testing recovery)")
                return True
            return False

        return True  # HALF_OPEN


# =============================================================================
# Cache Layer
# =============================================================================

class CacheManager:
    """Redis-based caching for Odoo data"""

    def __init__(self, config: SyncConfig):
        self.config = config
        self.enabled = config.enable_cache and redis is not None
        self.client = None

        if self.enabled:
            try:
                self.client = redis.Redis(
                    host=config.redis_host,
                    port=config.redis_port,
                    db=config.redis_db,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                self.client.ping()
                logger.info(f"Cache enabled: Redis at {config.redis_host}:{config.redis_port}")
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False

    def _make_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}={v}")
        key_string = ":".join(key_parts)
        # Hash to avoid overly long keys
        return f"odoo:{prefix}:{hashlib.md5(key_string.encode()).hexdigest()[:12]}"

    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """Get cached value"""
        if not self.enabled:
            return None

        try:
            key = self._make_key(prefix, **kwargs)
            value = self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
        except Exception as e:
            logger.debug(f"Cache get error: {e}")

        return None

    def set(self, prefix: str, value: Any, ttl: Optional[int] = None, **kwargs):
        """Set cached value"""
        if not self.enabled:
            return

        try:
            key = self._make_key(prefix, **kwargs)
            ttl = ttl or self.config.cache_ttl
            self.client.setex(key, ttl, json.dumps(value, default=str))
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.debug(f"Cache set error: {e}")

    def invalidate(self, prefix: str, **kwargs):
        """Invalidate cache entry"""
        if not self.enabled:
            return

        try:
            key = self._make_key(prefix, **kwargs)
            self.client.delete(key)
            logger.debug(f"Cache invalidated: {key}")
        except Exception as e:
            logger.debug(f"Cache invalidate error: {e}")

    def invalidate_pattern(self, pattern: str):
        """Invalidate all cache entries matching pattern"""
        if not self.enabled:
            return

        try:
            for key in self.client.scan_iter(f"odoo:{pattern}:*"):
                self.client.delete(key)
            logger.debug(f"Cache invalidated pattern: odoo:{pattern}:*")
        except Exception as e:
            logger.debug(f"Cache invalidate pattern error: {e}")

    def get_stats(self) -> Dict:
        """Get cache statistics"""
        if not self.enabled:
            return {"enabled": False}

        try:
            info = self.client.info("stats")
            return {
                "enabled": True,
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "total_keys": self.client.dbsize()
            }
        except Exception as e:
            return {"enabled": True, "error": str(e)}


# =============================================================================
# Metrics
# =============================================================================

@dataclass
class SyncMetrics:
    """Performance metrics for sync operations"""
    start_time: float = field(default_factory=time.time)
    end_time: float = 0
    records_fetched: int = 0
    records_cached: int = 0
    records_synced: int = 0
    records_skipped: int = 0
    api_calls: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    retries: int = 0
    errors: List[str] = field(default_factory=list)

    @property
    def duration(self) -> float:
        return self.end_time - self.start_time if self.end_time else time.time() - self.start_time

    @property
    def records_per_second(self) -> float:
        return self.records_synced / self.duration if self.duration > 0 else 0

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0

    def to_dict(self) -> Dict:
        return {
            "duration_seconds": round(self.duration, 2),
            "records_fetched": self.records_fetched,
            "records_cached": self.records_cached,
            "records_synced": self.records_synced,
            "records_skipped": self.records_skipped,
            "records_per_second": round(self.records_per_second, 2),
            "api_calls": self.api_calls,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": f"{self.cache_hit_rate * 100:.1f}%",
            "retries": self.retries,
            "errors": self.errors
        }


# =============================================================================
# Enhanced Sync Client
# =============================================================================

class OdooSyncClientEnhanced:
    """Enhanced client for syncing data from Odoo via MCP server"""

    def __init__(self, config: Optional[SyncConfig] = None):
        self.config = config or SyncConfig()
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=self.config.circuit_breaker_threshold,
            timeout=self.config.circuit_breaker_timeout
        )
        self.cache = CacheManager(self.config)
        self.metrics = SyncMetrics()
        self.state = self._load_state()

        # Create accounting directories
        (self.config.accounting_path / "Invoices").mkdir(parents=True, exist_ok=True)
        (self.config.accounting_path / "Payments").mkdir(parents=True, exist_ok=True)
        (self.config.accounting_path / "Vendors").mkdir(parents=True, exist_ok=True)
        (self.config.accounting_path / "Customers").mkdir(parents=True, exist_ok=True)
        (self.config.accounting_path / "Reports").mkdir(parents=True, exist_ok=True)

    def _load_state(self) -> Dict:
        """Load sync state from file"""
        state_file = self.config.accounting_path / ".sync_state_enhanced.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        return {
            "last_sync": None,
            "invoices": {},
            "payments": {},
            "partners": {},
            "last_write_dates": {}
        }

    def _save_state(self):
        """Save sync state to file"""
        state_file = self.config.accounting_path / ".sync_state_enhanced.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _call_mcp_with_retry(self, tool_name: str, arguments: Dict,
                            use_cache: bool = True) -> Optional[Any]:
        """Call Odoo MCP server with exponential backoff retry"""
        self.metrics.api_calls += 1

        # Check cache first
        if use_cache:
            cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
            cached = self.cache.get("mcp_call", call=cache_key)
            if cached is not None:
                self.metrics.cache_hits += 1
                self.metrics.records_cached += 1
                return cached
            self.metrics.cache_misses += 1

        # Check circuit breaker
        if not self.circuit_breaker.can_execute():
            raise Exception("Circuit breaker is OPEN - Odoo API calls blocked")

        # Retry with exponential backoff
        delay = self.config.base_retry_delay
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                response = requests.post(
                    f"{self.config.mcp_url}/",
                    json={
                        "jsonrpc": "2.0",
                        "id": int(time.time() * 1000),
                        "method": "tools/call",
                        "params": {
                            "name": tool_name,
                            "arguments": arguments
                        }
                    },
                    timeout=self.config.timeout
                )
                response.raise_for_status()
                data = response.json()

                if "error" in data:
                    raise Exception(f"MCP Error: {data['error']}")

                result = data.get("result", {})

                # Extract content from MCP response
                if "content" in result and len(result["content"]) > 0:
                    text = result["content"][0].get("text", "")
                    parsed = json.loads(text) if text else result
                else:
                    parsed = result

                # Cache successful result
                if use_cache:
                    cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
                    self.cache.set("mcp_call", parsed, call=cache_key)

                self.circuit_breaker.record_success()
                return parsed

            except requests.exceptions.Timeout:
                last_error = f"Timeout after {self.config.timeout}s"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
            except requests.exceptions.RequestException as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
            except json.JSONDecodeError as e:
                last_error = f"JSON decode error: {e}"
                logger.error(f"Attempt {attempt + 1}: {last_error}")
                break  # Don't retry JSON errors
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Attempt {attempt + 1}: {last_error}")

            # Retry logic
            if attempt < self.config.max_retries - 1:
                # Add jitter to avoid thundering herd
                jitter = random.uniform(0.1, 0.3) * delay
                sleep_time = min(delay + jitter, self.config.max_retry_delay)
                logger.debug(f"Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
                delay *= self.config.retry_multiplier
                self.metrics.retries += 1

        # All retries failed
        self.circuit_breaker.record_failure()
        self.metrics.errors.append(last_error or "Unknown error")
        return None

    def _get_last_write_date(self, model: str) -> Optional[str]:
        """Get last write_date for incremental sync"""
        return self.state.get("last_write_dates", {}).get(model)

    def _update_last_write_date(self, model: str, write_date: str):
        """Update last write_date for incremental sync"""
        if "last_write_dates" not in self.state:
            self.state["last_write_dates"] = {}
        self.state["last_write_dates"][model] = write_date
        self._save_state()

    def sync_invoices(self, from_date: Optional[str] = None,
                     dry_run: bool = False,
                     force_full: bool = False) -> Dict:
        """Sync invoices from Odoo with incremental support"""
        logger.info("Syncing invoices...")

        # Determine sync start date
        if not force_full and self.config.incremental_sync and not from_date:
            last_write = self._get_last_write_date("invoices")
            if last_write:
                from_date = last_write
                logger.info(f"Incremental sync from: {from_date}")

        metrics = {
            "fetched": 0,
            "synced": 0,
            "skipped": 0,
            "newest_write_date": None
        }

        # Build domain filter
        domain = [
            ["move_type", "in", ["out_invoice", "in_invoice"]],
            ["state", "=", "posted"]
        ]

        if from_date:
            domain.append(["write_date", ">=", from_date])

        # Use pagination for large datasets
        all_invoices = []
        offset = 0
        limit = self.config.batch_size

        while True:
            result = self._call_mcp_with_retry("search_records", {
                "model": "account.move",
                "domain": domain,
                "fields": [
                    "id", "name", "move_type", "state", "payment_state",
                    "invoice_date", "partner_id", "amount_total", "amount_residual",
                    "create_date", "write_date"
                ],
                "order": "write_date asc",
                "limit": limit,
                "offset": offset
            }, use_cache=(offset == 0))  # Only cache first page

            if not result or "records" not in result:
                logger.warning("No invoices found or error occurred")
                break

            invoices = result["records"]
            metrics["fetched"] += len(invoices)

            if not invoices:
                break

            all_invoices.extend(invoices)

            # Track newest write_date for incremental sync
            for inv in invoices:
                write_date = inv.get("write_date", "")
                if write_date:
                    if not metrics["newest_write_date"] or write_date > metrics["newest_write_date"]:
                        metrics["newest_write_date"] = write_date

            if len(invoices) < limit:
                break

            offset += limit
            logger.info(f"Fetched {len(all_invoices)} invoices so far...")

        count = len(all_invoices)
        logger.info(f"Found {count} invoices to sync")

        if dry_run:
            logger.info("[DRY RUN] Would sync invoices:")
            for inv in all_invoices[:5]:
                logger.info(f"  - {inv['name']}: {inv['amount_total']}")
            return {**metrics, "synced": count}

        # Group by month and save
        by_month = {}
        for inv in all_invoices:
            month = inv.get("invoice_date", inv.get("create_date", ""))[:7]
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(inv)

        for month, month_invoices in by_month.items():
            file_path = self.config.accounting_path / "Invoices" / f"{month}.json"

            # Load existing data
            existing_ids = set()
            existing_invoices = []

            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        existing_invoices = data.get("invoices", [])
                        existing_ids = {inv["id"] for inv in existing_invoices}
                except Exception as e:
                    logger.warning(f"Failed to load existing file: {e}")

            # Merge/update
            new_count = 0
            for inv in month_invoices:
                if inv["id"] not in existing_ids:
                    existing_invoices.append(inv)
                    new_count += 1
                    metrics["synced"] += 1
                else:
                    # Update existing record
                    for i, existing_inv in enumerate(existing_invoices):
                        if existing_inv["id"] == inv["id"]:
                            existing_invoices[i] = inv
                            metrics["synced"] += 1
                            break
                    else:
                        metrics["skipped"] += 1

            # Save
            with open(file_path, 'w') as f:
                json.dump({
                    "month": month,
                    "synced_at": datetime.now().isoformat(),
                    "count": len(existing_invoices),
                    "invoices": existing_invoices
                }, f, indent=2)

            logger.info(f"Saved {len(month_invoices)} invoices to {file_path.name}")

        # Update state
        if metrics["newest_write_date"]:
            self._update_last_write_date("invoices", metrics["newest_write_date"])

        self.state["invoices"]["last_sync"] = datetime.now().isoformat()
        self.state["invoices"]["count"] = count
        self._save_state()

        # Invalidate cache for this model
        self.cache.invalidate_pattern("invoices")

        return metrics

    def sync_payments(self, from_date: Optional[str] = None,
                     dry_run: bool = False,
                     force_full: bool = False) -> Dict:
        """Sync payments from Odoo with incremental support"""
        logger.info("Syncing payments...")

        if not force_full and self.config.incremental_sync and not from_date:
            last_write = self._get_last_write_date("payments")
            if last_write:
                from_date = last_write
                logger.info(f"Incremental sync from: {from_date}")

        metrics = {
            "fetched": 0,
            "synced": 0,
            "skipped": 0,
            "newest_write_date": None
        }

        domain = [["state", "=", "posted"]]

        if from_date:
            domain.append(["write_date", ">=", from_date])

        all_payments = []
        offset = 0
        limit = self.config.batch_size

        while True:
            result = self._call_mcp_with_retry("search_records", {
                "model": "account.payment",
                "domain": domain,
                "fields": [
                    "id", "name", "payment_type", "partner_type",
                    "amount", "payment_date", "partner_id", "state",
                    "journal_id", "create_date", "write_date"
                ],
                "order": "write_date asc",
                "limit": limit,
                "offset": offset
            }, use_cache=(offset == 0))

            if not result or "records" not in result:
                break

            payments = result["records"]
            metrics["fetched"] += len(payments)

            if not payments:
                break

            all_payments.extend(payments)

            for pay in payments:
                write_date = pay.get("write_date", "")
                if write_date:
                    if not metrics["newest_write_date"] or write_date > metrics["newest_write_date"]:
                        metrics["newest_write_date"] = write_date

            if len(payments) < limit:
                break

            offset += limit

        count = len(all_payments)
        logger.info(f"Found {count} payments to sync")

        if dry_run:
            return {**metrics, "synced": count}

        # Group by month and save
        by_month = {}
        for pay in all_payments:
            month = pay.get("payment_date", pay.get("create_date", ""))[:7]
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(pay)

        for month, month_payments in by_month.items():
            file_path = self.config.accounting_path / "Payments" / f"{month}.json"

            existing_ids = set()
            existing_payments = []

            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        existing_payments = data.get("payments", [])
                        existing_ids = {pay["id"] for pay in existing_payments}
                except Exception:
                    pass

            new_count = 0
            for pay in month_payments:
                if pay["id"] not in existing_ids:
                    existing_payments.append(pay)
                    new_count += 1
                    metrics["synced"] += 1
                else:
                    for i, existing_pay in enumerate(existing_payments):
                        if existing_pay["id"] == pay["id"]:
                            existing_payments[i] = pay
                            metrics["synced"] += 1
                            break
                    else:
                        metrics["skipped"] += 1

            with open(file_path, 'w') as f:
                json.dump({
                    "month": month,
                    "synced_at": datetime.now().isoformat(),
                    "count": len(existing_payments),
                    "payments": existing_payments
                }, f, indent=2)

            logger.info(f"Saved {len(month_payments)} payments to {file_path.name}")

        if metrics["newest_write_date"]:
            self._update_last_write_date("payments", metrics["newest_write_date"])

        self.state["payments"]["last_sync"] = datetime.now().isoformat()
        self.state["payments"]["count"] = count
        self._save_state()

        self.cache.invalidate_pattern("payments")

        return metrics

    def sync_partners(self, dry_run: bool = False) -> Dict:
        """Sync customers and vendors from Odoo"""
        logger.info("Syncing partners...")

        metrics = {"customers": 0, "vendors": 0}

        # Search for customers
        customers = self._call_mcp_with_retry("search_records", {
            "model": "res.partner",
            "domain": [["customer_rank", ">", 0]],
            "fields": ["id", "name", "email", "phone", "customer_rank", "supplier_rank", "write_date"],
            "limit": 1000
        })

        if customers and "records" in customers:
            customer_list = customers["records"]
            metrics["customers"] = len(customer_list)

            if not dry_run:
                with open(self.config.accounting_path / "Customers.json", 'w') as f:
                    json.dump({
                        "synced_at": datetime.now().isoformat(),
                        "count": metrics["customers"],
                        "customers": customer_list
                    }, f, indent=2)
                logger.info(f"Saved {metrics['customers']} customers")

        # Search for vendors
        vendors = self._call_mcp_with_retry("search_records", {
            "model": "res.partner",
            "domain": [["supplier_rank", ">", 0]],
            "fields": ["id", "name", "email", "phone", "customer_rank", "supplier_rank", "write_date"],
            "limit": 1000
        })

        if vendors and "records" in vendors:
            vendor_list = vendors["records"]
            metrics["vendors"] = len(vendor_list)

            if not dry_run:
                with open(self.config.accounting_path / "Vendors.json", 'w') as f:
                    json.dump({
                        "synced_at": datetime.now().isoformat(),
                        "count": metrics["vendors"],
                        "vendors": vendor_list
                    }, f, indent=2)
                logger.info(f"Saved {metrics['vendors']} vendors")

        self.state["partners"]["last_sync"] = datetime.now().isoformat()
        self.state["partners"]["customers"] = metrics["customers"]
        self.state["partners"]["vendors"] = metrics["vendors"]
        self._save_state()

        self.cache.invalidate_pattern("partners")

        return metrics

    def sync_all(self, from_date: Optional[str] = None,
                dry_run: bool = False,
                force_full: bool = False) -> SyncMetrics:
        """Sync all accounting data from Odoo with metrics"""
        logger.info("=" * 60)
        logger.info("Odoo Sync Enhanced - Starting")
        logger.info("=" * 60)
        logger.info(f"Configuration:")
        logger.info(f"  Batch size: {self.config.batch_size}")
        logger.info(f"  Incremental sync: {self.config.incremental_sync}")
        logger.info(f"  Cache enabled: {self.cache.enabled}")
        logger.info(f"  Circuit breaker threshold: {self.config.circuit_breaker_threshold}")

        if dry_run:
            logger.info("DRY RUN MODE - No files will be modified")

        self.metrics = SyncMetrics()
        self.metrics.start_time = time.time()

        try:
            # Sync partners first
            logger.info("\n--- Syncing Partners ---")
            partners = self.sync_partners(dry_run=dry_run)
            logger.info(f"[OK] Partners: {partners['customers']} customers, {partners['vendors']} vendors")

            # Sync invoices
            logger.info("\n--- Syncing Invoices ---")
            invoices = self.sync_invoices(from_date=from_date, dry_run=dry_run, force_full=force_full)
            logger.info(f"[OK] Invoices: {invoices['synced']} synced, {invoices['skipped']} skipped")

            # Sync payments
            logger.info("\n--- Syncing Payments ---")
            payments = self.sync_payments(from_date=from_date, dry_run=dry_run, force_full=force_full)
            logger.info(f"[OK] Payments: {payments['synced']} synced, {payments['skipped']} skipped")

            # Update overall state
            self.state["last_sync"] = datetime.now().isoformat()
            self._save_state()

            self.metrics.end_time = time.time()
            self.metrics.records_fetched = invoices.get("fetched", 0) + payments.get("fetched", 0)
            self.metrics.records_synced = invoices.get("synced", 0) + payments.get("synced", 0)
            self.metrics.records_skipped = invoices.get("skipped", 0) + payments.get("skipped", 0)

            # Print summary
            logger.info("\n" + "=" * 60)
            logger.info("Sync Summary:")
            logger.info(f"  Customers: {partners['customers']}")
            logger.info(f"  Vendors: {partners['vendors']}")
            logger.info(f"  Invoices: {invoices['synced']} synced, {invoices['skipped']} skipped")
            logger.info(f"  Payments: {payments['synced']} synced, {payments['skipped']} skipped")
            logger.info(f"\nPerformance Metrics:")
            logger.info(f"  Duration: {self.metrics.duration:.2f}s")
            logger.info(f"  Records/sec: {self.metrics.records_per_second:.1f}")
            logger.info(f"  API calls: {self.metrics.api_calls}")
            logger.info(f"  Cache hit rate: {self.metrics.cache_hit_rate * 100:.1f}%")
            logger.info(f"  Retries: {self.metrics.retries}")

            cache_stats = self.cache.get_stats()
            if cache_stats.get("enabled"):
                logger.info(f"  Redis keys: {cache_stats.get('total_keys', 0)}")

            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            self.metrics.errors.append(str(e))
            raise

        return self.metrics


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Enhanced Odoo sync with caching and incremental sync",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --sync all                           Full sync with caching
  %(prog)s --sync invoices --force-full         Force full refresh
  %(prog)s --sync all --batch-size 200          Use larger batches
  %(prog)s --sync all --dry-run                 Preview sync
  %(prog)s --sync all --from-date 2026-01-01    Incremental from date
        """
    )

    parser.add_argument(
        "--sync",
        choices=["all", "invoices", "payments", "partners"],
        default="all",
        help="What to sync from Odoo"
    )

    parser.add_argument("--from-date", help="Only sync records from this date (YYYY-MM-DD)")

    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be synced without making changes")

    parser.add_argument("--force-full", action="store_true",
                       help="Force full sync (ignore incremental state)")

    parser.add_argument("--batch-size", type=int,
                       help=f"Override batch size (default: {os.getenv('ODOO_SYNC_BATCH_SIZE', '100')})")

    parser.add_argument("--no-cache", action="store_true",
                       help="Disable caching for this run")

    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")

    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    # Create config
    config = SyncConfig()
    if args.batch_size:
        config.batch_size = args.batch_size
    if args.no_cache:
        config.enable_cache = False

    # Create sync client
    client = OdooSyncClientEnhanced(config)

    # Execute sync
    try:
        if args.sync == "all":
            client.sync_all(from_date=args.from_date, dry_run=args.dry_run, force_full=args.force_full)
        elif args.sync == "invoices":
            client.sync_invoices(from_date=args.from_date, dry_run=args.dry_run, force_full=args.force_full)
        elif args.sync == "payments":
            client.sync_payments(from_date=args.from_date, dry_run=args.dry_run, force_full=args.force_full)
        elif args.sync == "partners":
            client.sync_partners(dry_run=args.dry_run)

        return 0
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
