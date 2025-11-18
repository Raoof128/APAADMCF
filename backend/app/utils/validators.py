"""
Validators for data validation
"""

from typing import Optional, List
from datetime import date, datetime
import re


def validate_australian_phone(phone: str) -> bool:
    """
    Validate Australian phone number format

    Args:
        phone: Phone number string

    Returns:
        True if valid Australian phone format
    """
    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)

    # Check Australian formats
    patterns = [
        r'^04\d{8}$',  # Mobile: 04XX XXX XXX
        r'^\+614\d{8}$',  # Mobile international: +61 4XX XXX XXX
        r'^0[2-8]\d{8}$',  # Landline: 0X XXXX XXXX
        r'^\+61[2-8]\d{8}$',  # Landline international
        r'^13\d{4}$',  # 13 numbers
        r'^1300\d{6}$',  # 1300 numbers
        r'^1800\d{6}$',  # 1800 numbers
    ]

    return any(re.match(pattern, cleaned) for pattern in patterns)


def validate_abn(abn: str) -> bool:
    """
    Validate Australian Business Number (ABN)

    Args:
        abn: ABN string

    Returns:
        True if valid ABN
    """
    # Remove spaces
    abn = abn.replace(' ', '')

    # Must be 11 digits
    if not re.match(r'^\d{11}$', abn):
        return False

    # Apply ABN algorithm
    weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    digits = [int(d) for d in abn]

    # Subtract 1 from first digit
    digits[0] -= 1

    # Calculate weighted sum
    weighted_sum = sum(d * w for d, w in zip(digits, weights))

    # Valid if divisible by 89
    return weighted_sum % 89 == 0


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate that date range is logical

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        True if end_date >= start_date
    """
    return end_date >= start_date


def validate_score(score: Optional[int], min_val: int = 0, max_val: int = 100) -> bool:
    """
    Validate score is within range

    Args:
        score: Score value
        min_val: Minimum allowed value
        max_val: Maximum allowed value

    Returns:
        True if score is None or within range
    """
    if score is None:
        return True
    return min_val <= score <= max_val


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension

    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.docx'])

    Returns:
        True if extension is allowed
    """
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    return f'.{extension}' in [ext.lower() for ext in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = 100) -> bool:
    """
    Validate file size

    Args:
        file_size: File size in bytes
        max_size_mb: Maximum size in megabytes

    Returns:
        True if file size is within limit
    """
    max_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_bytes


def validate_postcode(postcode: str) -> bool:
    """
    Validate Australian postcode

    Args:
        postcode: Postcode string

    Returns:
        True if valid Australian postcode
    """
    return bool(re.match(r'^\d{4}$', postcode))


def sanitize_sql_identifier(identifier: str) -> str:
    """
    Sanitize SQL identifier to prevent injection

    Args:
        identifier: SQL identifier (table name, column name, etc.)

    Returns:
        Sanitized identifier
    """
    # Only allow alphanumeric and underscore
    return re.sub(r'[^a-zA-Z0-9_]', '', identifier)
