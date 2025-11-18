"""
Tests for utility functions
"""

import pytest
from datetime import datetime, timedelta

from app.utils.helpers import (
    sanitize_string,
    validate_email,
    calculate_sla_due_date,
    is_overdue,
    format_percentage,
    mask_sensitive_data,
    generate_reference_number
)
from app.utils.validators import (
    validate_australian_phone,
    validate_abn,
    validate_date_range,
    validate_score,
    validate_postcode
)


class TestHelpers:
    """Test helper functions"""

    def test_sanitize_string(self):
        """Test string sanitization"""
        assert sanitize_string("  hello  ") == "hello"
        assert sanitize_string("hello\x00world") == "helloworld"
        assert sanitize_string("a" * 100, max_length=10) == "a" * 10

    def test_validate_email(self):
        """Test email validation"""
        assert validate_email("test@example.com") is True
        assert validate_email("invalid.email") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False

    def test_calculate_sla_due_date(self):
        """Test SLA due date calculation"""
        submitted = datetime(2024, 1, 1, 12, 0, 0)
        due_date = calculate_sla_due_date(submitted, sla_days=30)
        expected = datetime(2024, 1, 31, 12, 0, 0)
        assert due_date == expected

    def test_is_overdue(self):
        """Test overdue checking"""
        due_date = datetime.utcnow() - timedelta(days=1)
        assert is_overdue(due_date) is True

        due_date = datetime.utcnow() + timedelta(days=1)
        assert is_overdue(due_date) is False

    def test_format_percentage(self):
        """Test percentage formatting"""
        assert format_percentage(0.75) == "75.0%"
        assert format_percentage(0.5, decimals=2) == "50.00%"

    def test_mask_sensitive_data(self):
        """Test data masking"""
        assert mask_sensitive_data("1234567890") == "12******90"
        assert mask_sensitive_data("abc") == "***"

    def test_generate_reference_number(self):
        """Test reference number generation"""
        ref = generate_reference_number("TEST")
        assert ref.startswith("TEST-")
        assert len(ref) > 10


class TestValidators:
    """Test validator functions"""

    def test_validate_australian_phone(self):
        """Test Australian phone number validation"""
        assert validate_australian_phone("0412345678") is True
        assert validate_australian_phone("+61412345678") is True
        assert validate_australian_phone("02 1234 5678") is True
        assert validate_australian_phone("1300123456") is True
        assert validate_australian_phone("1800123456") is True
        assert validate_australian_phone("invalid") is False

    def test_validate_abn(self):
        """Test ABN validation"""
        # Valid test ABN
        assert validate_abn("51 824 753 556") is True
        # Invalid ABN
        assert validate_abn("12 345 678 901") is False
        assert validate_abn("invalid") is False

    def test_validate_date_range(self):
        """Test date range validation"""
        from datetime import date
        start = date(2024, 1, 1)
        end = date(2024, 12, 31)
        assert validate_date_range(start, end) is True
        assert validate_date_range(end, start) is False

    def test_validate_score(self):
        """Test score validation"""
        assert validate_score(50) is True
        assert validate_score(0) is True
        assert validate_score(100) is True
        assert validate_score(None) is True
        assert validate_score(-1) is False
        assert validate_score(101) is False

    def test_validate_postcode(self):
        """Test postcode validation"""
        assert validate_postcode("2000") is True
        assert validate_postcode("3000") is True
        assert validate_postcode("invalid") is False
        assert validate_postcode("200") is False
