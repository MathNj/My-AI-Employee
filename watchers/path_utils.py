#!/usr/bin/env python3
"""
Path resolution utilities for cross-platform compatibility.

Handles relative and absolute paths on Windows, Linux, and Mac.
Resolves paths relative to VAULT_PATH or watchers directory.
"""

import os
from pathlib import Path
from typing import Union


def resolve_path(
    path_str: str,
    base_path: Union[str, Path] = None,
    vault_path: Union[str, Path] = None
) -> Path:
    """
    Resolve a path string to an absolute Path object.

    Args:
        path_str: Path string (can be relative or absolute)
        base_path: Base directory for relative paths (default: watchers/ dir)
        vault_path: Override VAULT_PATH (for testing)

    Returns:
        Resolved absolute Path object

    Examples:
        >>> resolve_path("./..")
        Path(.../AI_Employee_Vault)

        >>> resolve_path("./credentials", base_path=Path("/watchers"))
        Path(/watchers/credentials)

        >>> resolve_path("/absolute/path")
        Path(/absolute/path)
    """
    # Convert to Path object
    input_path = Path(path_str)

    # If already absolute, return as-is
    if input_path.is_absolute():
        return input_path

    # Determine base path
    if base_path is None:
        # Default to watchers/ directory
        base_path = Path(__file__).parent
    else:
        base_path = Path(base_path)

    # Resolve relative path
    resolved = (base_path / input_path).resolve()

    return resolved


def get_vault_path() -> Path:
    """
    Get VAULT_PATH from environment or auto-detect.

    Returns:
        Absolute path to vault directory
    """
    # Check environment variable
    env_vault = os.environ.get('VAULT_PATH')
    if env_vault:
        vault = Path(env_vault)
        if vault.is_absolute():
            return vault
        # Resolve relative to watchers directory
        return resolve_path(env_vault)

    # Auto-detect: go up from watchers/ directory
    return resolve_path("./..")


def get_watchers_path() -> Path:
    """
    Get watchers directory path.

    Returns:
        Absolute path to watchers directory
    """
    return Path(__file__).parent.resolve()


def resolve_config_path(path_str: str, config_type: str = "watchers") -> Path:
    """
    Resolve a configuration path.

    Args:
        path_str: Path from config file (.env)
        config_type: Type of config ('watchers' or 'vault')

    Returns:
        Resolved absolute path

    Examples:
        >>> resolve_config_path("./credentials/credentials.json")
        Path(.../watchers/credentials/credentials.json)

        >>> resolve_config_path("Inbox", config_type="vault")
        Path(.../AI_Employee_Vault/Inbox)
    """
    if config_type == "vault":
        base = get_vault_path()
    else:
        base = get_watchers_path()

    return resolve_path(path_str, base_path=base)
