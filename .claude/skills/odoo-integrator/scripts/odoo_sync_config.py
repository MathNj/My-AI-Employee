#!/usr/bin/env python3
"""
Odoo Sync Configuration Module

Loads configuration from:
1. YAML config file (./config.yaml or ~/.config/odoo-sync/config.yaml)
2. Environment variables
3. Command-line arguments

Priority: CLI args > Environment > Config file > Defaults
"""

from __future__ import annotations

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field, replace
from copy import deepcopy

try:
    import yaml
except ImportError:
    print("Installing required package: pyyaml")
    os.system("pip install pyyaml")
    import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Data Classes
# =============================================================================

@dataclass
class RetryStrategy:
    """Per-error-type retry strategy"""
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0


@dataclass
class OdooConfig:
    """Odoo connection configuration"""
    mcp_url: str = "http://localhost:8000"
    url: str = "http://localhost:8069"
    db: str = "odoo"
    username: str = "admin"
    api_key: str = ""


@dataclass
class DatabaseConfig:
    """Database configuration"""
    default: str = "odoo"
    additional: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class CacheConfig:
    """Cache configuration"""
    enabled: bool = True
    provider: str = "redis"
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    ttl: int = 300


@dataclass
class RateLimitConfig:
    """Rate limiting configuration"""
    enabled: bool = True
    requests_per_second: float = 10
    requests_per_minute: int = 500
    burst: int = 20


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration"""
    enabled: bool = True
    failure_threshold: int = 5
    timeout: int = 60
    success_threshold: int = 2


@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = "INFO"
    format: str = "text"
    output: List[Dict] = field(default_factory=lambda: [
        {"type": "file", "path": "./Logs/odoo_sync.log"},
        {"type": "console"}
    ])


@dataclass
class MetricsConfig:
    """Metrics configuration"""
    enabled: bool = True
    port: int = 9090
    path: str = "/metrics"


@dataclass
class NotificationConfig:
    """Notification configuration"""
    enabled: bool = False
    email_to: str = ""
    email_on_error: bool = True
    email_on_completion: bool = True
    webhook_url: str = ""
    webhook_on_error: bool = True


@dataclass
class SyncConfig:
    """Complete sync configuration"""
    # Odoo connection
    odoo: OdooConfig = field(default_factory=OdooConfig)

    # Databases
    databases: DatabaseConfig = field(default_factory=DatabaseConfig)

    # Sync settings
    batch_size: int = 100
    incremental: bool = True
    enable_validation: bool = True
    enable_compression: bool = True
    compression_threshold: int = 10240
    enable_backup: bool = True
    backup_keep: int = 5

    # Parallel processing
    parallel_enabled: bool = True
    max_workers: int = 4
    queue_size: int = 1000

    # Caching
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Rate limiting
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

    # Retry
    retry_max_attempts: int = 3
    retry_base_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_multiplier: float = 2.0
    retry_jitter: bool = True
    retry_strategies: Dict[str, RetryStrategy] = field(default_factory=dict)

    # Circuit breaker
    circuit_breaker: CircuitBreakerConfig = field(default_factory=CircuitBreakerConfig)

    # Logging
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # Metrics
    metrics: MetricsConfig = field(default_factory=MetricsConfig)

    # Notifications
    notifications: NotificationConfig = field(default_factory=NotificationConfig)

    # Paths
    vault_path: Path = field(default_factory=lambda: Path.cwd())
    accounting_path: Optional[Path] = None
    needs_action_path: Optional[Path] = None
    backup_path: Optional[Path] = None

    # Schedules
    schedules: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        """Resolve derived paths"""
        if self.accounting_path is None:
            self.accounting_path = self.vault_path / "Accounting"
        if self.needs_action_path is None:
            self.needs_action_path = self.vault_path / "Needs_Action"
        if self.backup_path is None:
            self.backup_path = self.accounting_path / ".backups"


# =============================================================================
# Configuration Loader
# =============================================================================

class ConfigLoader:
    """Loads and merges configuration from multiple sources"""

    DEFAULT_CONFIG_PATHS = [
        "./config.yaml",
        "./odoo_sync_config.yaml",
        "~/.config/odoo-sync/config.yaml",
        "/etc/odoo-sync/config.yaml",
    ]

    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path
        self.raw_config: Dict = {}
        self.config: Optional[SyncConfig] = None

    def load(self) -> SyncConfig:
        """Load configuration from all sources"""
        # 1. Load defaults
        config_dict = {}

        # 2. Load from YAML file
        yaml_config = self._load_yaml()
        if yaml_config:
            config_dict = self._deep_merge(config_dict, yaml_config)

        # 3. Override with environment variables
        env_config = self._load_env()
        config_dict = self._deep_merge(config_dict, env_config)

        # 4. Create SyncConfig object
        self.config = self._dict_to_config(config_dict)

        return self.config

    def _load_yaml(self) -> Dict:
        """Load configuration from YAML file"""
        config_file = self._find_config_file()

        if not config_file or not config_file.exists():
            logger.debug("No config file found, using defaults")
            return {}

        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from: {config_file}")
                return config or {}
        except Exception as e:
            logger.warning(f"Failed to load config from {config_file}: {e}")
            return {}

    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file"""
        # Use specified path if provided
        if self.config_path:
            return Path(self.config_path).expanduser()

        # Try default paths
        for path_str in self.DEFAULT_CONFIG_PATHS:
            path = Path(path_str).expanduser()
            if path.exists():
                return path

        return None

    def _load_env(self) -> Dict:
        """Load configuration from environment variables"""
        env_config = {}

        # Odoo settings
        if os.getenv('ODOO_MCP_URL'):
            env_config.setdefault('odoo', {})['mcp_url'] = os.getenv('ODOO_MCP_URL')
        if os.getenv('ODOO_URL'):
            env_config.setdefault('odoo', {})['url'] = os.getenv('ODOO_URL')
        if os.getenv('ODOO_DB'):
            env_config.setdefault('odoo', {})['db'] = os.getenv('ODOO_DB')
        if os.getenv('ODOO_USERNAME'):
            env_config.setdefault('odoo', {})['username'] = os.getenv('ODOO_USERNAME')
        if os.getenv('ODOO_API_KEY'):
            env_config.setdefault('odoo', {})['api_key'] = os.getenv('ODOO_API_KEY')

        # Sync settings
        if os.getenv('ODOO_SYNC_BATCH_SIZE'):
            env_config['batch_size'] = int(os.getenv('ODOO_SYNC_BATCH_SIZE'))
        if os.getenv('ODOO_INCREMENTAL_SYNC'):
            env_config['incremental'] = os.getenv('ODOO_INCREMENTAL_SYNC').lower() == 'true'
        if os.getenv('ODOO_ENABLE_VALIDATION'):
            env_config['enable_validation'] = os.getenv('ODOO_ENABLE_VALIDATION').lower() == 'true'
        if os.getenv('ODOO_ENABLE_COMPRESSION'):
            env_config['enable_compression'] = os.getenv('ODOO_ENABLE_COMPRESSION').lower() == 'true'
        if os.getenv('ODOO_ENABLE_BACKUP'):
            env_config['enable_backup'] = os.getenv('ODOO_ENABLE_BACKUP').lower() == 'true'

        # Cache
        if os.getenv('ODOO_ENABLE_CACHE'):
            env_config.setdefault('cache', {})['enabled'] = os.getenv('ODOO_ENABLE_CACHE').lower() == 'true'
        if os.getenv('REDIS_HOST'):
            env_config.setdefault('cache', {})['redis_host'] = os.getenv('REDIS_HOST')
        if os.getenv('REDIS_PORT'):
            env_config.setdefault('cache', {})['redis_port'] = int(os.getenv('REDIS_PORT'))

        # Rate limiting
        if os.getenv('ODOO_RATE_LIMIT_ENABLED'):
            env_config.setdefault('rate_limit', {})['enabled'] = os.getenv('ODOO_RATE_LIMIT_ENABLED').lower() == 'true'
        if os.getenv('ODOO_RATE_LIMIT_RPS'):
            env_config.setdefault('rate_limit', {})['requests_per_second'] = float(os.getenv('ODOO_RATE_LIMIT_RPS'))

        # Retry
        if os.getenv('ODOO_MAX_RETRIES'):
            env_config['retry_max_attempts'] = int(os.getenv('ODOO_MAX_RETRIES'))
        if os.getenv('ODOO_RETRY_DELAY'):
            env_config['retry_base_delay'] = float(os.getenv('ODOO_RETRY_DELAY'))

        # Circuit breaker
        if os.getenv('ODOO_CB_THRESHOLD'):
            env_config.setdefault('circuit_breaker', {})['failure_threshold'] = int(os.getenv('ODOO_CB_THRESHOLD'))
        if os.getenv('ODOO_CB_TIMEOUT'):
            env_config.setdefault('circuit_breaker', {})['timeout'] = int(os.getenv('ODOO_CB_TIMEOUT'))

        # Paths
        if os.getenv('VAULT_PATH'):
            env_config['vault_path'] = Path(os.getenv('VAULT_PATH'))

        # Logging
        if os.getenv('ODOO_LOG_LEVEL'):
            env_config.setdefault('logging', {})['level'] = os.getenv('ODOO_LOG_LEVEL')
        if os.getenv('ODOO_LOG_FORMAT'):
            env_config.setdefault('logging', {})['format'] = os.getenv('ODOO_LOG_FORMAT')

        # Metrics
        if os.getenv('ODOO_METRICS_ENABLED'):
            env_config.setdefault('metrics', {})['enabled'] = os.getenv('ODOO_METRICS_ENABLED').lower() == 'true'
        if os.getenv('ODOO_METRICS_PORT'):
            env_config.setdefault('metrics', {})['port'] = int(os.getenv('ODOO_METRICS_PORT'))

        return env_config

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = deepcopy(base)

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)

        return result

    def _dict_to_config(self, config_dict: Dict) -> SyncConfig:
        """Convert dictionary to SyncConfig object"""
        # Extract nested configs
        odoo_dict = config_dict.get('odoo', {})
        databases_dict = config_dict.get('databases', {})
        cache_dict = config_dict.get('cache', {})
        rate_limit_dict = config_dict.get('rate_limit', {})
        circuit_breaker_dict = config_dict.get('circuit_breaker', {})
        logging_dict = config_dict.get('logging', {})
        metrics_dict = config_dict.get('metrics', {})
        notifications_dict = config_dict.get('notifications', {})
        retry_strategies_dict = config_dict.get('retry', {}).get('strategies', {})

        # Build retry strategies
        retry_strategies = {}
        for error_type, strategy in retry_strategies_dict.items():
            retry_strategies[error_type] = RetryStrategy(
                max_attempts=strategy.get('max_attempts', config_dict.get('retry_max_attempts', 3)),
                base_delay=strategy.get('base_delay', config_dict.get('retry_base_delay', 1.0)),
                max_delay=strategy.get('max_delay', config_dict.get('retry_max_delay', 60.0))
            )

        return SyncConfig(
            # Odoo
            odoo=OdooConfig(
                mcp_url=odoo_dict.get('mcp_url', 'http://localhost:8000'),
                url=odoo_dict.get('url', 'http://localhost:8069'),
                db=odoo_dict.get('db', 'odoo'),
                username=odoo_dict.get('username', 'admin'),
                api_key=odoo_dict.get('api_key', os.getenv('ODOO_API_KEY', ''))
            ),

            # Databases
            databases=DatabaseConfig(
                default=databases_dict.get('default', 'odoo'),
                additional=databases_dict.get('additional', [])
            ),

            # Sync settings
            batch_size=config_dict.get('batch_size', 100),
            incremental=config_dict.get('incremental', True),
            enable_validation=config_dict.get('enable_validation', True),
            enable_compression=config_dict.get('enable_compression', True),
            compression_threshold=config_dict.get('compression_threshold', 10240),
            enable_backup=config_dict.get('enable_backup', True),
            backup_keep=config_dict.get('backup_keep', 5),

            # Parallel
            parallel_enabled=config_dict.get('parallel', {}).get('enabled', True),
            max_workers=config_dict.get('parallel', {}).get('max_workers', 4),
            queue_size=config_dict.get('parallel', {}).get('queue_size', 1000),

            # Cache
            cache=CacheConfig(
                enabled=cache_dict.get('enabled', True),
                provider=cache_dict.get('provider', 'redis'),
                redis_host=cache_dict.get('redis', {}).get('host', 'localhost'),
                redis_port=cache_dict.get('redis', {}).get('port', 6379),
                redis_db=cache_dict.get('redis', {}).get('db', 0),
                ttl=cache_dict.get('ttl', 300)
            ),

            # Rate limiting
            rate_limit=RateLimitConfig(
                enabled=rate_limit_dict.get('enabled', True),
                requests_per_second=rate_limit_dict.get('requests_per_second', 10),
                requests_per_minute=rate_limit_dict.get('requests_per_minute', 500),
                burst=rate_limit_dict.get('burst', 20)
            ),

            # Retry
            retry_max_attempts=config_dict.get('retry', {}).get('max_attempts', 3),
            retry_base_delay=config_dict.get('retry', {}).get('base_delay', 1.0),
            retry_max_delay=config_dict.get('retry', {}).get('max_delay', 60.0),
            retry_multiplier=config_dict.get('retry', {}).get('multiplier', 2.0),
            retry_jitter=config_dict.get('retry', {}).get('jitter', True),
            retry_strategies=retry_strategies,

            # Circuit breaker
            circuit_breaker=CircuitBreakerConfig(
                enabled=circuit_breaker_dict.get('enabled', True),
                failure_threshold=circuit_breaker_dict.get('failure_threshold', 5),
                timeout=circuit_breaker_dict.get('timeout', 60),
                success_threshold=circuit_breaker_dict.get('success_threshold', 2)
            ),

            # Logging
            logging=LoggingConfig(
                level=logging_dict.get('level', 'INFO'),
                format=logging_dict.get('format', 'text'),
                output=logging_dict.get('output', [
                    {"type": "file", "path": "./Logs/odoo_sync.log"},
                    {"type": "console"}
                ])
            ),

            # Metrics
            metrics=MetricsConfig(
                enabled=metrics_dict.get('enabled', True),
                port=metrics_dict.get('port', 9090),
                path=metrics_dict.get('path', '/metrics')
            ),

            # Notifications
            notifications=NotificationConfig(
                enabled=notifications_dict.get('enabled', False),
                email_to=notifications_dict.get('email', {}).get('to', ''),
                email_on_error=notifications_dict.get('email', {}).get('on_error', True),
                email_on_completion=notifications_dict.get('email', {}).get('on_completion', True),
                webhook_url=notifications_dict.get('webhook', {}).get('url', ''),
                webhook_on_error=notifications_dict.get('webhook', {}).get('on_error', True)
            ),

            # Paths
            vault_path=Path(config_dict.get('paths', {}).get('vault', '.')).expanduser().resolve(),

            # Schedules
            schedules=config_dict.get('schedules', {})
        )

    def apply_cli_args(self, config: SyncConfig, args: Dict) -> SyncConfig:
        """Apply CLI arguments to configuration (highest priority)"""
        result = config

        # Sync settings
        if 'batch_size' in args:
            result = replace(result, batch_size=args['batch_size'])
        if 'no_incremental' in args:
            result = replace(result, incremental=False)
        if 'force_full' in args:
            result = replace(result, incremental=False)
        if 'no_validation' in args:
            result = replace(result, enable_validation=False)
        if 'no_compression' in args:
            result = replace(result, enable_compression=False)
        if 'no_backup' in args:
            result = replace(result, enable_backup=False)
        if 'no_cache' in args:
            result = replace(result, cache=replace(result.cache, enabled=False))
        if 'max_workers' in args:
            result = replace(result, max_workers=args['max_workers'])
        if 'parallel' in args:
            result = replace(result, parallel_enabled=True)

        # Logging
        if 'verbose' in args:
            result = replace(result, logging=replace(result.logging, level='DEBUG'))

        return result


# =============================================================================
# Convenience Functions
# =============================================================================

def load_config(config_path: Optional[str] = None) -> SyncConfig:
    """Load configuration from all sources"""
    loader = ConfigLoader(config_path)
    return loader.load()


def get_config() -> SyncConfig:
    """Get current configuration (cached)"""
    if not hasattr(get_config, '_cached'):
        get_config._cached = load_config()
    return get_config._cached


def reload_config(config_path: Optional[str] = None):
    """Reload configuration"""
    get_config._cached = load_config(config_path)


# =============================================================================
# CLI Support
# =============================================================================

def add_config_args(parser):
    """Add configuration-related arguments to argument parser"""
    parser.add_argument('--config', '-c', help='Path to config file')
    parser.add_argument('--print-config', action='store_true',
                       help='Print current configuration and exit')
    parser.add_argument('--validate-config', action='store_true',
                       help='Validate configuration and exit')


def print_config(config: SyncConfig):
    """Print configuration as YAML"""
    import json
    from dataclasses import asdict

    def convert_path(obj):
        if isinstance(obj, Path):
            return str(obj)
        return obj

    config_dict = asdict(config)

    # Convert Path objects to strings
    def paths_to_str(d):
        if isinstance(d, dict):
            return {k: paths_to_str(v) for k, v in d.items()}
        elif isinstance(d, list):
            return [paths_to_str(v) for v in d]
        elif isinstance(d, Path):
            return str(d)
        return d

    config_dict = paths_to_str(config_dict)

    print(yaml.dump(config_dict, default_flow_style=False, sort_keys=False))


if __name__ == "__main__":
    # Test configuration loading
    import argparse

    parser = argparse.ArgumentParser()
    add_config_args(parser)
    args = parser.parse_args()

    config = load_config(args.config)

    if args.print_config:
        print_config(config)
    elif args.validate_config:
        print("Configuration is valid!")
        print(f"  MCP URL: {config.odoo.mcp_url}")
        print(f"  Database: {config.odoo.db}")
        print(f"  Batch size: {config.batch_size}")
        print(f"  Incremental: {config.incremental}")
        print(f"  Cache: {config.cache.enabled}")
        print(f"  Rate limit: {config.rate_limit.requests_per_second} req/s")
    else:
        print("Configuration loaded successfully")
        print(f"Config file: {ConfigLoader(args.config)._find_config_file()}")
