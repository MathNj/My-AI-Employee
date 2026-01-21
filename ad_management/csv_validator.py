#!/usr/bin/env python3
"""
CSV Input Validation and Sanitization Module

Provides secure CSV reading with validation to prevent:
- CSV injection attacks
- Path traversal via filenames
- Malicious data in cells
- Oversized files causing DoS
"""

import os
import re
import pandas as pd
from pathlib import Path
from typing import List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when CSV validation fails."""
    pass


# Dangerous patterns that indicate CSV injection
# See: https://owasp.org/www-community/attacks/CSV_Injection
CSV_INJECTION_PATTERNS = [
    r'^=.*',       # Formula starting with =
    r'^\+.*',      # Formula starting with +
    r'^-.*',       # Formula starting with -
    r'^@.*',       # Formula starting with @
    r'^\t.*',      # Tab character
    r'^\r?\n.*',   # Newline characters
]

# Maximum file size (50MB)
MAX_CSV_SIZE_BYTES = 50 * 1024 * 1024

# Maximum number of rows
MAX_CSV_ROWS = 10000

# Required columns for product CSVs
REQUIRED_PRODUCT_COLUMNS = {'URL', 'Ad Name'}

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.csv', '.xlsx', '.xls'}

# Safe filename pattern (alphanumeric, underscore, hyphen, dot)
SAFE_FILENAME_PATTERN = re.compile(r'^[\w\s\-\.]+$')


def validate_file_path(file_path: str, base_dir: Optional[str] = None) -> Path:
    """
    Validate file path to prevent directory traversal attacks.

    Args:
        file_path: Path to CSV file
        base_dir: Base directory that files must be within (optional)

    Returns:
        Validated absolute Path object

    Raises:
        ValidationError: If path is invalid or outside base_dir
    """
    # Convert to Path object
    path = Path(file_path)

    # Check file extension
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f"Invalid file extension: {path.suffix}. "
            f"Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Resolve to absolute path
    try:
        abs_path = path.resolve()
    except Exception as e:
        raise ValidationError(f"Invalid path: {e}")

    # Check if path exists
    if not abs_path.exists():
        raise ValidationError(f"File does not exist: {abs_path}")

    # Check if it's a file (not directory)
    if not abs_path.is_file():
        raise ValidationError(f"Path is not a file: {abs_path}")

    # If base_dir specified, ensure file is within it
    if base_dir:
        base = Path(base_dir).resolve()
        try:
            abs_path.relative_to(base)
        except ValueError:
            raise ValidationError(
                f"File path outside base directory: {abs_path}"
            )

    return abs_path


def validate_file_size(file_path: Path) -> None:
    """
    Validate file size to prevent DoS via oversized files.

    Args:
        file_path: Path to file

    Raises:
        ValidationError: If file is too large
    """
    file_size = file_path.stat().st_size

    if file_size > MAX_CSV_SIZE_BYTES:
        raise ValidationError(
            f"File too large: {file_size:,} bytes (max: {MAX_CSV_SIZE_BYTES:,})"
        )

    if file_size == 0:
        raise ValidationError("File is empty")


def validate_csv_data(df: pd.DataFrame, required_columns: Optional[Set[str]] = None) -> pd.DataFrame:
    """
    Validate CSV data content for safety and correctness.

    Args:
        df: DataFrame read from CSV
        required_columns: Set of required column names (optional)

    Returns:
        Sanitized DataFrame

    Raises:
        ValidationError: If data validation fails
    """
    # Check row count
    if len(df) > MAX_CSV_ROWS:
        raise ValidationError(
            f"Too many rows: {len(df):,} (max: {MAX_CSV_ROWS:,})"
        )

    # Check required columns
    if required_columns:
        missing_columns = required_columns - set(df.columns)
        if missing_columns:
            raise ValidationError(
                f"Missing required columns: {', '.join(missing_columns)}"
            )

    # Check for CSV injection in string columns
    for col in df.select_dtypes(include=['object']).columns:
        for idx, value in df[col].items():
            if pd.isna(value):
                continue

            str_value = str(value).strip()

            # Check for CSV injection patterns
            for pattern in CSV_INJECTION_PATTERNS:
                if re.match(pattern, str_value, re.IGNORECASE):
                    logger.warning(
                        f"CSV injection pattern detected in row {idx}, column '{col}': {str_value[:50]}"
                    )
                    # Sanitize by prefixing with apostrophe (Excel treats as literal)
                    df.at[idx, col] = "'" + str_value

    return df


def safe_read_csv(
    file_path: str,
    base_dir: Optional[str] = None,
    required_columns: Optional[Set[str]] = None,
    **pandas_kwargs
) -> pd.DataFrame:
    """
    Safely read CSV file with comprehensive validation.

    Args:
        file_path: Path to CSV file
        base_dir: Base directory that files must be within (optional)
        required_columns: Set of required column names (optional)
        **pandas_kwargs: Additional arguments to pass to pd.read_csv

    Returns:
        Validated DataFrame

    Raises:
        ValidationError: If validation fails
        IOError: If file cannot be read

    Example:
        >>> df = safe_read_csv(
        ...     'products.csv',
        ...     base_dir='/data/ad_management',
        ...     required_columns={'URL', 'Ad Name', 'Price'}
        ... )
    """
    logger.info(f"Reading CSV file: {file_path}")

    # Step 1: Validate file path
    validated_path = validate_file_path(file_path, base_dir)

    # Step 2: Validate file size
    validate_file_size(validated_path)

    # Step 3: Read CSV with safety options
    try:
        # Set safe defaults for pandas
        safe_kwargs = {
            'encoding': 'utf-8',
            'on_bad_lines': 'warn',  # Skip malformed lines
            'dtype': str,  # Read all as string to prevent type confusion
        }
        safe_kwargs.update(pandas_kwargs)

        df = pd.read_csv(validated_path, **safe_kwargs)

    except pd.errors.EmptyDataError:
        raise ValidationError("CSV file is empty")
    except pd.errors.ParserError as e:
        raise ValidationError(f"CSV parsing error: {e}")
    except Exception as e:
        raise IOError(f"Error reading CSV: {e}")

    # Step 4: Validate data content
    df = validate_csv_data(df, required_columns)

    logger.info(f"Successfully read {len(df)} rows from CSV")

    return df


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent filesystem attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem

    Raises:
        ValidationError: If filename cannot be sanitized
    """
    # Remove path separators
    filename = os.path.basename(filename)

    # Remove dangerous characters
    filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)

    # Check if filename is safe
    if not SAFE_FILENAME_PATTERN.match(filename):
        raise ValidationError(f"Filename contains unsafe characters: {filename}")

    # Ensure filename is not empty after sanitization
    if not filename:
        raise ValidationError("Filename is empty after sanitization")

    return filename


if __name__ == "__main__":
    # Test validation
    import sys

    if len(sys.argv) < 2:
        print("Usage: python csv_validator.py <csv_file_path>")
        sys.exit(1)

    try:
        df = safe_read_csv(
            sys.argv[1],
            required_columns=REQUIRED_PRODUCT_COLUMNS
        )
        print(f"[OK] CSV validation successful: {len(df)} rows")
        print(f"  Columns: {', '.join(df.columns)}")
    except ValidationError as e:
        print(f"[ERROR] Validation failed: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"[ERROR] IO error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        sys.exit(1)
