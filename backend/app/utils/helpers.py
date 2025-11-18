"""
Helper utilities for common operations
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uuid import UUID
import re


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input to prevent injection attacks

    Args:
        text: Input text
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove null bytes
    text = text.replace('\x00', '')

    # Strip whitespace
    text = text.strip()

    # Truncate if needed
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def validate_email(email: str) -> bool:
    """
    Validate email format

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def calculate_sla_due_date(
    submitted_at: datetime,
    sla_days: int = 30
) -> datetime:
    """
    Calculate SLA due date from submission date

    Args:
        submitted_at: Submission timestamp
        sla_days: Number of days in SLA

    Returns:
        Due date timestamp
    """
    return submitted_at + timedelta(days=sla_days)


def is_overdue(due_date: datetime, completed_at: Optional[datetime] = None) -> bool:
    """
    Check if a task is overdue

    Args:
        due_date: Due date for task
        completed_at: Completion date (None if not completed)

    Returns:
        True if overdue
    """
    check_date = completed_at or datetime.utcnow()
    return check_date > due_date


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage

    Args:
        value: Value between 0 and 1
        decimals: Number of decimal places

    Returns:
        Formatted percentage string
    """
    return f"{value * 100:.{decimals}f}%"


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_dict_get(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary value

    Args:
        data: Dictionary to query
        *keys: Keys to traverse
        default: Default value if key not found

    Returns:
        Value or default
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result


def generate_reference_number(prefix: str = "REQ") -> str:
    """
    Generate unique reference number

    Args:
        prefix: Prefix for reference number

    Returns:
        Reference number
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    import random
    random_suffix = ''.join([str(random.randint(0, 9)) for _ in range(4)])
    return f"{prefix}-{timestamp}-{random_suffix}"


def mask_sensitive_data(text: str, keep_first: int = 2, keep_last: int = 2) -> str:
    """
    Mask sensitive data for logging

    Args:
        text: Text to mask
        keep_first: Number of characters to keep at start
        keep_last: Number of characters to keep at end

    Returns:
        Masked text
    """
    if not text or len(text) <= keep_first + keep_last:
        return "*" * len(text)

    return f"{text[:keep_first]}{'*' * (len(text) - keep_first - keep_last)}{text[-keep_last:]}"
