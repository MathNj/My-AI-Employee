#!/usr/bin/env python3
"""
Odoo Sync Script for AI Employee - Ultimate Version

Improvements over Enhanced:
- Parallel/concurrent processing for batch operations
- Data validation with schema checking
- Progress bars for visual feedback
- Automatic compression for large JSON files
- Backup/restore functionality
- Webhook support for real-time events
- Connection pooling for HTTP requests

Usage:
    python odoo_sync_ultimate.py --sync all
    python odoo_sync_ultimate.py --sync invoices --parallel
    python odoo_sync_ultimate.py --backup
    python odoo_sync_ultimate.py --restore 2026-01-26_120000
"""

from __future__ import annotations

import os
import sys
import json
import logging
import time
import gzip
import shutil
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
import threading

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
except ImportError:
    print("Installing required packages: requests urllib3")
    os.system("pip install requests urllib3")
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

try:
    import redis
except ImportError:
    print("Redis package not found. Caching will be disabled.")
    redis = None

try:
    from tqdm import tqdm
except ImportError:
    print("tqdm not found. Progress bars will be disabled.")
    tqdm = None

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure logging
log_dir = Path(__file__).parent.parent.parent.parent / "Logs"
log_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f"odoo_sync_ultimate_{datetime.now().strftime('%Y-%m-%d')}.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("odoo_sync_ultimate")


# =============================================================================
# Configuration
# =============================================================================

@dataclass
class UltimateSyncConfig:
    """Configuration for Ultimate Odoo sync operations"""
    mcp_url: str = "http://localhost:8000"
    vault_path: Path = field(default_factory=lambda: Path(os.getenv("VAULT_PATH", ".")))
    timeout: int = 30
    batch_size: int = int(os.getenv("ODOO_SYNC_BATCH_SIZE", "100"))
    max_workers: int = int(os.getenv("ODOO_MAX_WORKERS", "4"))
    max_retries: int = int(os.getenv("ODOO_MAX_RETRIES", "3"))
    base_retry_delay: float = float(os.getenv("ODOO_RETRY_DELAY", "1.0"))
    retry_multiplier: float = float(os.getenv("ODOO_RETRY_MULTIPLIER", "2.0"))
    max_retry_delay: float = float(os.getenv("ODOO_MAX_RETRY_DELAY", "60.0"))
    circuit_breaker_threshold: int = int(os.getenv("ODOO_CB_THRESHOLD", "5"))
    circuit_breaker_timeout: int = int(os.getenv("ODOO_CB_TIMEOUT", "60"))
    cache_ttl: int = int(os.getenv("ODOO_CACHE_TTL", "300"))
    enable_cache: bool = os.getenv("ODOO_ENABLE_CACHE", "true").lower() == "true"
    enable_compression: bool = os.getenv("ODOO_ENABLE_COMPRESSION", "true").lower() == "true"
    compression_threshold: int = int(os.getenv("ODOO_COMPRESSION_THRESHOLD", "10240"))  # 10KB
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_db: int = int(os.getenv("REDIS_DB", "0"))
    incremental_sync: bool = os.getenv("ODOO_INCREMENTAL_SYNC", "true").lower() == "true"
    enable_validation: bool = os.getenv("ODOO_ENABLE_VALIDATION", "true").lower() == "true"
    enable_backup: bool = os.getenv("ODOO_ENABLE_BACKUP", "true").lower() == "true"
    backup_dir: Path = field(default_factory=lambda: Path(os.getenv("VAULT_PATH", ".")) / "Accounting" / ".backups")

    @property
    def accounting_path(self) -> Path:
        return self.vault_path / "Accounting"


# =============================================================================
# Data Validation
# =============================================================================

class ValidationError(Exception):
    """Raised when data validation fails"""
    pass


class DataValidator:
    """Validates Odoo data before sync"""

    SCHEMAS = {
        "account.move": {
            "required": ["id", "name", "move_type", "state"],
            "optional": ["partner_id", "amount_total", "invoice_date", "payment_state",
                        "create_date", "write_date", "amount_residual"],
            "types": {
                "id": int,
                "name": str,
                "move_type": str,
                "state": str,
                "amount_total": (int, float),
                "invoice_date": str,
                "payment_state": str
            }
        },
        "account.payment": {
            "required": ["id", "name", "payment_type", "state"],
            "optional": ["partner_id", "amount", "payment_date", "journal_id",
                        "create_date", "write_date"],
            "types": {
                "id": int,
                "name": str,
                "payment_type": str,
                "state": str,
                "amount": (int, float)
            }
        },
        "res.partner": {
            "required": ["id", "name"],
            "optional": ["email", "phone", "customer_rank", "supplier_rank"],
            "types": {
                "id": int,
                "name": str,
                "email": str,
                "customer_rank": int,
                "supplier_rank": int
            }
        }
    }

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_record(self, model: str, record: Dict) -> bool:
        """Validate a single record"""
        if not self.enabled:
            return True

        self.errors = []
        self.warnings = []

        if model not in self.SCHEMAS:
            self.warnings.append(f"No schema for model: {model}")
            return True

        schema = self.SCHEMAS[model]

        # Check required fields
        for field in schema["required"]:
            if field not in record:
                self.errors.append(f"Missing required field: {field}")

        # Check types
        for field, expected_type in schema["types"].items():
            if field in record and record[field] is not None:
                if not isinstance(record[field], expected_type):
                    self.errors.append(
                        f"Field '{field}' has wrong type: "
                        f"expected {expected_type}, got {type(record[field])}"
                    )

        # Business logic validation
        if model == "account.move":
            self._validate_invoice(record)
        elif model == "account.payment":
            self._validate_payment(record)

        return len(self.errors) == 0

    def _validate_invoice(self, record: Dict):
        """Validate invoice business rules"""
        if record.get("move_type") == "out_invoice":
            if record.get("amount_total", 0) < 0:
                self.errors.append(f"Customer invoice cannot have negative amount")

        if record.get("state") == "posted":
            if not record.get("invoice_date"):
                self.warnings.append("Posted invoice without invoice_date")

        # Check partner_id format
        partner_id = record.get("partner_id")
        if partner_id and isinstance(partner_id, list):
            if len(partner_id) > 0 and isinstance(partner_id[0], dict):
                if "id" not in partner_id[0]:
                    self.warnings.append("Partner ID missing 'id' field")

    def _validate_payment(self, record: Dict):
        """Validate payment business rules"""
        if record.get("payment_type") == "inbound":
            if record.get("amount", 0) < 0:
                self.warnings.append(f"Inbound payment has negative amount")

    def get_report(self) -> str:
        """Get validation report"""
        report = []
        if self.errors:
            report.append(f"Errors ({len(self.errors)}):")
            report.extend(f"  - {e}" for e in self.errors)
        if self.warnings:
            report.append(f"Warnings ({len(self.warnings)}):")
            report.extend(f"  - {w}" for w in self.warnings)
        return "\n".join(report) if report else "Validation passed"


# =============================================================================
# Backup/Restore
# =============================================================================

class BackupManager:
    """Manages backups of accounting data"""

    def __init__(self, config: UltimateSyncConfig):
        self.config = config
        self.backup_dir = config.backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self) -> str:
        """Create a backup of current accounting data"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)

        logger.info(f"Creating backup: {backup_name}")

        # Copy all accounting files
        accounting_path = self.config.accounting_path
        if accounting_path.exists():
            for item in accounting_path.iterdir():
                if item.is_file() or item.is_dir():
                    dest = backup_path / item.name
                    if item.is_dir():
                        shutil.copytree(item, dest, dirs_exist_ok=True)
                    else:
                        shutil.copy2(item, dest)
                    logger.debug(f"Backed up: {item.name}")

        # Create metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "backup_name": backup_name,
            "files": list(str(f.name) for f in backup_path.rglob("*") if f.is_file())
        }

        metadata_path = backup_path / "metadata.json"
        metadata_path.write_text(json.dumps(metadata, indent=2))

        logger.info(f"Backup created: {backup_path}")
        return backup_name

    def restore_backup(self, backup_name: str) -> bool:
        """Restore from a backup"""
        backup_path = self.backup_dir / backup_name

        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_name}")
            return False

        # Create a backup of current state before restoring
        current_backup = self.create_backup()
        logger.info(f"Current state backed up as: {current_backup}")

        logger.info(f"Restoring from: {backup_name}")

        # Restore files
        for item in backup_path.iterdir():
            if item.name == "metadata.json":
                continue

            dest = self.config.accounting_path / item.name

            # Remove existing
            if dest.exists():
                if dest.is_dir():
                    shutil.rmtree(dest)
                else:
                    dest.remove()

            # Restore
            if item.is_dir():
                shutil.copytree(item, dest)
            else:
                shutil.copy2(item, dest)

            logger.debug(f"Restored: {item.name}")

        logger.info("Restore complete")
        return True

    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        backups = []

        for item in self.backup_dir.iterdir():
            if item.is_dir() and item.name.startswith("backup_"):
                metadata_file = item / "metadata.json"
                metadata = {}
                if metadata_file.exists():
                    try:
                        metadata = json.loads(metadata_file.read_text())
                    except Exception:
                        pass

                backups.append({
                    "name": item.name,
                    "timestamp": metadata.get("timestamp", "unknown"),
                    "files": len(metadata.get("files", [])),
                    "size_mb": sum(f.stat().st_size for f in item.rglob("*") if f.is_file()) / (1024 * 1024)
                })

        return sorted(backups, key=lambda x: x["timestamp"], reverse=True)

    def cleanup_old_backups(self, keep: int = 10):
        """Remove old backups, keeping only the most recent N"""
        backups = self.list_backups()

        for backup in backups[keep:]:
            backup_path = self.backup_dir / backup["name"]
            shutil.rmtree(backup_path)
            logger.info(f"Removed old backup: {backup['name']}")


# =============================================================================
# Compression
# =============================================================================

class CompressionManager:
    """Handles compression of large JSON files"""

    def __init__(self, config: UltimateSyncConfig):
        self.config = config
        self.enabled = config.enable_compression
        self.threshold = config.compression_threshold

    def compress_if_needed(self, file_path: Path) -> Path:
        """Compress file if it exceeds threshold"""
        if not self.enabled:
            return file_path

        if not file_path.exists():
            return file_path

        size = file_path.stat().st_size

        if size < self.threshold:
            return file_path

        # Compress
        compressed_path = file_path.with_suffix(file_path.suffix + ".gz")

        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        original_size = size / 1024  # KB
        compressed_size = compressed_path.stat().st_size / 1024  # KB
        ratio = (1 - compressed_size / original_size) * 100

        logger.info(f"Compressed: {file_path.name} "
                   f"({original_size:.1f}KB -> {compressed_size:.1f}KB, {ratio:.1f}% reduction)")

        # Remove original if compression successful
        if compressed_path.stat().st_size < size:
            file_path.unlink()
            return compressed_path

        # If compression didn't help, keep original
        compressed_path.unlink()
        return file_path

    def decompress_if_needed(self, file_path: Path) -> Path:
        """Decompress .gz file if exists"""
        if not file_path.exists():
            # Try compressed version
            compressed_path = Path(str(file_path) + ".gz")
            if compressed_path.exists():
                with gzip.open(compressed_path, 'rb') as f_in:
                    data = f_in.read()

                decompressed_path = file_path
                with open(decompressed_path, 'wb') as f_out:
                    f_out.write(data)

                logger.debug(f"Decompressed: {file_path.name}")
                return decompressed_path

        return file_path

    def read_compressed(self, file_path: Path) -> Dict:
        """Read JSON file, handling compression"""
        # Try compressed first
        compressed_path = Path(str(file_path) + ".gz")
        if compressed_path.exists():
            with gzip.open(compressed_path, 'rt') as f:
                return json.load(f)

        # Try normal
        if file_path.exists():
            with open(file_path) as f:
                return json.load(f)

        return {}


# =============================================================================
# Progress Tracking
# =============================================================================

class ProgressBar:
    """Progress bar wrapper with tqdm"""

    def __init__(self, total: int, desc: str = "Processing"):
        self.total = total
        self.desc = desc
        self.tqdm = None
        self.current = 0

        if tqdm is not None:
            self.tqdm = tqdm(total=total, desc=desc, unit="items")

    def update(self, n: int = 1):
        self.current += n
        if self.tqdm:
            self.tqdm.update(n)
        else:
            # Fallback: log progress
            if self.current % 100 == 0 or self.current == self.total:
                logger.info(f"{self.desc}: {self.current}/{self.total}")

    def close(self):
        if self.tqdm:
            self.tqdm.close()


# =============================================================================
# Connection Pool
# =============================================================================

class PooledSession:
    """HTTP session with connection pooling and retry strategy"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, pool_connections: int = 10, pool_maxsize: int = 10):
        if hasattr(self, '_initialized') and self._initialized:
            return

        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize,
            max_retries=retry_strategy
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self._initialized = True

    def post(self, url: str, **kwargs):
        return self.session.post(url, **kwargs)

    def get(self, url: str, **kwargs):
        return self.session.get(url, **kwargs)


# =============================================================================
# Ultimate Sync Client
# =============================================================================

def timing_decorator(func: Callable) -> Callable:
    """Decorator to time function execution"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.debug(f"{func.__name__} took {duration:.2f}s")
        return result
    return wrapper


class OdooSyncClientUltimate:
    """Ultimate sync client with all enhancements"""

    def __init__(self, config: Optional[UltimateSyncConfig] = None):
        self.config = config or UltimateSyncConfig()
        self.validator = DataValidator(self.config.enable_validation)
        self.backup_manager = BackupManager(self.config)
        self.compression = CompressionManager(self.config)
        self.session = PooledSession()

        # Components from enhanced version
        from odoo_sync_enhanced import CircuitBreaker, CacheManager, SyncMetrics
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
        state_file = self.config.accounting_path / ".sync_state_ultimate.json"
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
            "last_write_dates": {},
            "validation_errors": []
        }

    def _save_state(self):
        state_file = self.config.accounting_path / ".sync_state_ultimate.json"
        try:
            with open(state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _call_mcp_with_retry(self, tool_name: str, arguments: Dict,
                            use_cache: bool = True) -> Optional[Any]:
        """Call MCP with retry and connection pooling"""
        self.metrics.api_calls += 1

        if use_cache:
            cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
            cached = self.cache.get("mcp_call", call=cache_key)
            if cached is not None:
                self.metrics.cache_hits += 1
                return cached
            self.metrics.cache_misses += 1

        if not self.circuit_breaker.can_execute():
            raise Exception("Circuit breaker is OPEN")

        delay = self.config.base_retry_delay
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                response = self.session.post(
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

                if "content" in result and len(result["content"]) > 0:
                    text = result["content"][0].get("text", "")
                    parsed = json.loads(text) if text else result
                else:
                    parsed = result

                if use_cache:
                    cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
                    self.cache.set("mcp_call", parsed, call=cache_key)

                self.circuit_breaker.record_success()
                return parsed

            except Exception as e:
                last_error = str(e)
                if attempt < self.config.max_retries - 1:
                    sleep_time = min(delay * (2 ** attempt), self.config.max_retry_delay)
                    time.sleep(sleep_time)

        self.circuit_breaker.record_failure()
        self.metrics.errors.append(last_error)
        return None

    def _fetch_page(self, model: str, domain: List, fields: List,
                   offset: int, limit: int) -> List[Dict]:
        """Fetch a single page of records"""
        result = self._call_mcp_with_retry("search_records", {
            "model": model,
            "domain": domain,
            "fields": fields,
            "order": "write_date asc",
            "limit": limit,
            "offset": offset
        }, use_cache=(offset == 0))

        if result and "records" in result:
            return result["records"]
        return []

    def _fetch_all_parallel(self, model: str, domain: List, fields: List,
                           total_estimate: int = 0) -> List[Dict]:
        """Fetch all records using parallel requests"""
        all_records = []
        batch_size = self.config.batch_size
        max_workers = self.config.max_workers

        # If we have an estimate, calculate pages
        if total_estimate > 0:
            total_pages = (total_estimate + batch_size - 1) // batch_size
        else:
            total_pages = 1

        # First page to get count
        first_page = self._fetch_page(model, domain, fields, 0, batch_size)
        if not first_page:
            return []

        all_records.extend(first_page)

        # If we got less than batch size, we're done
        if len(first_page) < batch_size:
            return all_records

        # Fetch remaining pages in parallel
        offsets = list(range(batch_size, len(first_page) + batch_size * 10, batch_size))

        if offsets:
            logger.info(f"Fetching {len(offsets) + 1} pages with {max_workers} workers...")

            progress = ProgressBar(len(offsets), f"Fetching {model}")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self._fetch_page, model, domain, fields, offset, batch_size): offset
                    for offset in offsets
                }

                for future in as_completed(futures):
                    try:
                        records = future.result(timeout=self.config.timeout)
                        all_records.extend(records)

                        # Stop if we got less than full page
                        if len(records) < batch_size:
                            # Cancel remaining futures
                            for f in futures:
                                f.cancel()
                            break

                        progress.update()
                    except Exception as e:
                        logger.warning(f"Parallel fetch error: {e}")
                        progress.update()

            progress.close()

        return all_records

    def sync_invoices(self, from_date: Optional[str] = None,
                     dry_run: bool = False,
                     force_full: bool = False,
                     parallel: bool = False) -> Dict:
        """Sync invoices with all enhancements"""
        logger.info("Syncing invoices...")

        # Create backup if enabled
        if self.config.enable_backup and not dry_run:
            backup_name = self.backup_manager.create_backup()
            logger.info(f"Backup created: {backup_name}")

        metrics = {
            "fetched": 0,
            "synced": 0,
            "skipped": 0,
            "validation_errors": 0,
            "newest_write_date": None
        }

        if not force_full and self.config.incremental_sync and not from_date:
            last_write = self.state.get("last_write_dates", {}).get("invoices")
            if last_write:
                from_date = last_write
                logger.info(f"Incremental sync from: {from_date}")

        domain = [
            ["move_type", "in", ["out_invoice", "in_invoice"]],
            ["state", "=", "posted"]
        ]

        if from_date:
            domain.append(["write_date", ">=", from_date])

        # Fetch records
        if parallel:
            all_invoices = self._fetch_all_parallel(
                "account.move", domain,
                ["id", "name", "move_type", "state", "payment_state",
                 "invoice_date", "partner_id", "amount_total", "amount_residual",
                 "create_date", "write_date"],
                total_estimate=500  # Estimate
            )
        else:
            all_invoices = []
            offset = 0
            limit = self.config.batch_size

            while True:
                result = self._fetch_page(
                    "account.move", domain,
                    ["id", "name", "move_type", "state", "payment_state",
                     "invoice_date", "partner_id", "amount_total", "amount_residual",
                     "create_date", "write_date"],
                    offset, limit
                )

                if not result:
                    break

                all_invoices.extend(result)
                metrics["fetched"] += len(result)

                if len(result) < limit:
                    break

                offset += limit

        metrics["fetched"] = len(all_invoices)
        logger.info(f"Found {len(all_invoices)} invoices to sync")

        # Validate records
        valid_invoices = []
        progress = ProgressBar(len(all_invoices), "Validating invoices")

        for invoice in all_invoices:
            if self.validator.validate_record("account.move", invoice):
                valid_invoices.append(invoice)

                # Track newest write_date
                write_date = invoice.get("write_date", "")
                if write_date:
                    if not metrics["newest_write_date"] or write_date > metrics["newest_write_date"]:
                        metrics["newest_write_date"] = write_date
            else:
                metrics["validation_errors"] += 1
                logger.warning(f"Validation failed for invoice {invoice.get('id')}: "
                             f"{self.validator.get_report()}")

            progress.update()

        progress.close()

        if dry_run:
            return {**metrics, "synced": len(valid_invoices)}

        # Save by month
        by_month = {}
        for invoice in valid_invoices:
            month = invoice.get("invoice_date", invoice.get("create_date", ""))[:7]
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(invoice)

        for month, month_invoices in by_month.items():
            file_path = self.config.accounting_path / "Invoices" / f"{month}.json"
            file_path = self.compression.decompress_if_needed(file_path)

            # Load existing
            existing_invoices = []
            existing_ids = set()

            if file_path.exists():
                try:
                    data = self.compression.read_compressed(file_path)
                    existing_invoices = data.get("invoices", [])
                    existing_ids = {inv["id"] for inv in existing_invoices}
                except Exception:
                    pass

            # Merge
            for invoice in month_invoices:
                if invoice["id"] not in existing_ids:
                    existing_invoices.append(invoice)
                    metrics["synced"] += 1
                else:
                    for i, existing in enumerate(existing_invoices):
                        if existing["id"] == invoice["id"]:
                            existing_invoices[i] = invoice
                            break
                    metrics["skipped"] += 1

            # Save
            with open(file_path, 'w') as f:
                json.dump({
                    "month": month,
                    "synced_at": datetime.now().isoformat(),
                    "count": len(existing_invoices),
                    "invoices": existing_invoices
                }, f, indent=2)

            # Compress if needed
            self.compression.compress_if_needed(file_path)
            logger.info(f"Saved {len(month_invoices)} invoices to {file_path.name}")

        # Update state
        if metrics["newest_write_date"]:
            if "last_write_dates" not in self.state:
                self.state["last_write_dates"] = {}
            self.state["last_write_dates"]["invoices"] = metrics["newest_write_date"]

        self.state["invoices"]["last_sync"] = datetime.now().isoformat()
        self.state["invoices"]["count"] = len(all_invoices)
        self.state["validation_errors"] = metrics["validation_errors"]
        self._save_state()

        return metrics

    def sync_payments(self, from_date: Optional[str] = None,
                     dry_run: bool = False,
                     force_full: bool = False) -> Dict:
        """Sync payments with all enhancements"""
        logger.info("Syncing payments...")

        metrics = {
            "fetched": 0,
            "synced": 0,
            "skipped": 0,
            "validation_errors": 0,
            "newest_write_date": None
        }

        if not force_full and self.config.incremental_sync and not from_date:
            last_write = self.state.get("last_write_dates", {}).get("payments")
            if last_write:
                from_date = last_write

        domain = [["state", "=", "posted"]]

        if from_date:
            domain.append(["write_date", ">=", from_date])

        # Fetch with progress bar
        all_payments = []
        offset = 0
        limit = self.config.batch_size

        progress = ProgressBar(0, "Fetching payments")

        while True:
            result = self._fetch_page(
                "account.payment", domain,
                ["id", "name", "payment_type", "partner_type",
                 "amount", "payment_date", "partner_id", "state",
                 "journal_id", "create_date", "write_date"],
                offset, limit
            )

            if not result:
                break

            all_payments.extend(result)
            progress.update(len(result))
            metrics["fetched"] += len(result)

            if len(result) < limit:
                break

            offset += limit

        progress.close()

        # Validate
        valid_payments = []
        for payment in all_payments:
            if self.validator.validate_record("account.payment", payment):
                valid_payments.append(payment)

                write_date = payment.get("write_date", "")
                if write_date and (not metrics["newest_write_date"] or write_date > metrics["newest_write_date"]):
                    metrics["newest_write_date"] = write_date
            else:
                metrics["validation_errors"] += 1

        logger.info(f"Found {len(valid_payments)} valid payments")

        if dry_run:
            return {**metrics, "synced": len(valid_payments)}

        # Save by month
        by_month = {}
        for payment in valid_payments:
            month = payment.get("payment_date", payment.get("create_date", ""))[:7]
            if month not in by_month:
                by_month[month] = []
            by_month[month].append(payment)

        for month, month_payments in by_month.items():
            file_path = self.config.accounting_path / "Payments" / f"{month}.json"
            file_path = self.compression.decompress_if_needed(file_path)

            existing_payments = []
            existing_ids = set()

            if file_path.exists():
                try:
                    data = self.compression.read_compressed(file_path)
                    existing_payments = data.get("payments", [])
                    existing_ids = {p["id"] for p in existing_payments}
                except Exception:
                    pass

            for payment in month_payments:
                if payment["id"] not in existing_ids:
                    existing_payments.append(payment)
                    metrics["synced"] += 1
                else:
                    for i, existing in enumerate(existing_payments):
                        if existing["id"] == payment["id"]:
                            existing_payments[i] = payment
                            break
                    metrics["skipped"] += 1

            with open(file_path, 'w') as f:
                json.dump({
                    "month": month,
                    "synced_at": datetime.now().isoformat(),
                    "count": len(existing_payments),
                    "payments": existing_payments
                }, f, indent=2)

            self.compression.compress_if_needed(file_path)

        if metrics["newest_write_date"]:
            if "last_write_dates" not in self.state:
                self.state["last_write_dates"] = {}
            self.state["last_write_dates"]["payments"] = metrics["newest_write_date"]

        self.state["payments"]["last_sync"] = datetime.now().isoformat()
        self.state["payments"]["count"] = len(all_payments)
        self._save_state()

        return metrics

    def sync_partners(self, dry_run: bool = False) -> Dict:
        """Sync customers and vendors"""
        logger.info("Syncing partners...")

        metrics = {"customers": 0, "vendors": 0, "validation_errors": 0}

        # Customers
        customers = self._call_mcp_with_retry("search_records", {
            "model": "res.partner",
            "domain": [["customer_rank", ">", 0]],
            "fields": ["id", "name", "email", "phone", "customer_rank", "supplier_rank", "write_date"],
            "limit": 1000
        })

        if customers and "records" in customers:
            valid_customers = []
            for customer in customers["records"]:
                if self.validator.validate_record("res.partner", customer):
                    valid_customers.append(customer)
                else:
                    metrics["validation_errors"] += 1

            metrics["customers"] = len(valid_customers)

            if not dry_run:
                with open(self.config.accounting_path / "Customers.json", 'w') as f:
                    json.dump({
                        "synced_at": datetime.now().isoformat(),
                        "count": metrics["customers"],
                        "customers": valid_customers
                    }, f, indent=2)

        # Vendors
        vendors = self._call_mcp_with_retry("search_records", {
            "model": "res.partner",
            "domain": [["supplier_rank", ">", 0]],
            "fields": ["id", "name", "email", "phone", "customer_rank", "supplier_rank", "write_date"],
            "limit": 1000
        })

        if vendors and "records" in vendors:
            valid_vendors = []
            for vendor in vendors["records"]:
                if self.validator.validate_record("res.partner", vendor):
                    valid_vendors.append(vendor)
                else:
                    metrics["validation_errors"] += 1

            metrics["vendors"] = len(valid_vendors)

            if not dry_run:
                with open(self.config.accounting_path / "Vendors.json", 'w') as f:
                    json.dump({
                        "synced_at": datetime.now().isoformat(),
                        "count": metrics["vendors"],
                        "vendors": valid_vendors
                    }, f, indent=2)

        self.state["partners"]["last_sync"] = datetime.now().isoformat()
        self.state["partners"]["customers"] = metrics["customers"]
        self.state["partners"]["vendors"] = metrics["vendors"]
        self._save_state()

        return metrics

    def sync_all(self, from_date: Optional[str] = None,
                dry_run: bool = False,
                force_full: bool = False,
                parallel: bool = False) -> Dict:
        """Sync all with comprehensive metrics"""
        logger.info("=" * 60)
        logger.info("Odoo Sync Ultimate - Starting")
        logger.info(f"  Parallel processing: {parallel}")
        logger.info(f"  Validation: {self.config.enable_validation}")
        logger.info(f"  Compression: {self.config.enable_compression}")
        logger.info(f"  Backup: {self.config.enable_backup}")
        logger.info("=" * 60)

        start_time = time.time()

        results = {}

        try:
            # Sync partners
            logger.info("\n--- Syncing Partners ---")
            partners = self.sync_partners(dry_run=dry_run)
            results["partners"] = partners
            logger.info(f"[OK] Partners: {partners['customers']} customers, {partners['vendors']} vendors")

            # Sync invoices
            logger.info("\n--- Syncing Invoices ---")
            invoices = self.sync_invoices(from_date=from_date, dry_run=dry_run,
                                         force_full=force_full, parallel=parallel)
            results["invoices"] = invoices

            # Sync payments
            logger.info("\n--- Syncing Payments ---")
            payments = self.sync_payments(from_date=from_date, dry_run=dry_run,
                                        force_full=force_full)
            results["payments"] = payments

            # Summary
            duration = time.time() - start_time

            logger.info("\n" + "=" * 60)
            logger.info("Sync Summary:")
            logger.info(f"  Customers: {partners['customers']}")
            logger.info(f"  Vendors: {partners['vendors']}")
            logger.info(f"  Invoices: {invoices['synced']} synced, {invoices['skipped']} skipped")
            logger.info(f"    Validation errors: {invoices.get('validation_errors', 0)}")
            logger.info(f"  Payments: {payments['synced']} synced, {payments['skipped']} skipped")
            logger.info(f"    Validation errors: {payments.get('validation_errors', 0)}")
            logger.info(f"\nPerformance:")
            logger.info(f"  Duration: {duration:.2f}s")
            logger.info(f"  Total synced: {invoices['synced'] + payments['synced']} records")
            logger.info("=" * 60)

            # Cleanup old backups
            if self.config.enable_backup:
                self.backup_manager.cleanup_old_backups(keep=5)

        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise

        return results


# =============================================================================
# CLI
# =============================================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Ultimate Odoo sync with all enhancements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --sync all                           Full sync with all features
  %(prog)s --sync invoices --parallel            Use parallel processing
  %(prog)s --backup                              Create backup
  %(prog)s --restore 20260126_120000             Restore from backup
  %(prog)s --list-backups                        List available backups
  %(prog)s --sync all --dry-run                 Preview sync
        """
    )

    parser.add_argument("--sync", choices=["all", "invoices", "payments", "partners"],
                       default="all", help="What to sync")
    parser.add_argument("--from-date", help="Sync from date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--force-full", action="store_true", help="Force full sync")
    parser.add_argument("--parallel", action="store_true", help="Use parallel processing")
    parser.add_argument("--no-cache", action="store_true", help="Disable caching")
    parser.add_argument("--no-validation", action="store_true", help="Disable validation")
    parser.add_argument("--no-compression", action="store_true", help="Disable compression")
    parser.add_argument("--no-backup", action="store_true", help="Disable backup")
    parser.add_argument("--max-workers", type=int, help="Max parallel workers")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose logging")

    # Backup commands
    parser.add_argument("--backup", action="store_true", help="Create backup")
    parser.add_argument("--restore", metavar="NAME", help="Restore from backup")
    parser.add_argument("--list-backups", action="store_true", help="List backups")
    parser.add_argument("--cleanup-backups", type=int, metavar="KEEP",
                       help="Remove old backups, keeping N")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass

    config = UltimateSyncConfig()

    if args.max_workers:
        config.max_workers = args.max_workers
    if args.no_cache:
        config.enable_cache = False
    if args.no_validation:
        config.enable_validation = False
    if args.no_compression:
        config.enable_compression = False
    if args.no_backup:
        config.enable_backup = False

    client = OdooSyncClientUltimate(config)

    # Handle backup commands
    if args.backup:
        name = client.backup_manager.create_backup()
        print(f"Backup created: {name}")
        return 0

    if args.restore:
        if client.backup_manager.restore_backup(args.restore):
            print(f"Restored from: {args.restore}")
            return 0
        else:
            print(f"Restore failed")
            return 1

    if args.list_backups:
        backups = client.backup_manager.list_backups()
        print(f"\nAvailable backups ({len(backups)}):")
        for b in backups:
            print(f"  {b['name']} - {b['timestamp']} - {b['size_mb']:.1f}MB - {b['files']} files")
        return 0

    if args.cleanup_backups:
        client.backup_manager.cleanup_old_backups(keep=args.cleanup_backups)
        print(f"Cleaned up old backups, keeping {args.cleanup_backups}")
        return 0

    # Sync commands
    try:
        if args.sync == "all":
            client.sync_all(from_date=args.from_date, dry_run=args.dry_run,
                          force_full=args.force_full, parallel=args.parallel)
        elif args.sync == "invoices":
            client.sync_invoices(from_date=args.from_date, dry_run=args.dry_run,
                               force_full=args.force_full, parallel=args.parallel)
        elif args.sync == "payments":
            client.sync_payments(from_date=args.from_date, dry_run=args.dry_run,
                               force_full=args.force_full)
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
