"""Input validation utilities"""

import re
from typing import Optional, Tuple


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """Validate email address format

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email must be a non-empty string"

    email = email.strip()

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return False, f"Invalid email format: {email}"

    if len(email) > 254:
        return False, "Email address too long (max 254 characters)"

    return True, None


def validate_isbn(isbn: str) -> Tuple[bool, Optional[str]]:
    """Validate ISBN-10 or ISBN-13 format

    Args:
        isbn: ISBN to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isbn or not isinstance(isbn, str):
        return False, "ISBN must be a non-empty string"

    # Remove hyphens and spaces
    isbn = isbn.strip().replace("-", "").replace(" ", "")

    # Check if it's a valid ISBN-10 or ISBN-13
    if len(isbn) == 10:
        return validate_isbn10(isbn)
    elif len(isbn) == 13:
        return validate_isbn13(isbn)
    else:
        return False, f"ISBN must be 10 or 13 characters, got {len(isbn)}"


def validate_isbn10(isbn: str) -> Tuple[bool, Optional[str]]:
    """Validate ISBN-10 checksum

    Args:
        isbn: ISBN-10 string (without hyphens)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not all(c.isdigit() or c == "X" for c in isbn):
        return False, "ISBN-10 must contain only digits (and X as check digit)"

    if not isbn[-1].upper() == isbn[-1]:
        return False, "Check digit must be uppercase X"

    try:
        checksum = sum(int(digit) * (10 - i) for i, digit in enumerate(isbn[:-1]))
        check = (10 - (checksum % 10)) % 10
        check_str = "X" if check == 10 else str(check)

        if isbn[-1] != check_str:
            return False, "Invalid ISBN-10 checksum"
        return True, None
    except ValueError:
        return False, "ISBN-10 must contain only digits"


def validate_isbn13(isbn: str) -> Tuple[bool, Optional[str]]:
    """Validate ISBN-13 checksum

    Args:
        isbn: ISBN-13 string (without hyphens)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isbn.isdigit():
        return False, "ISBN-13 must contain only digits"

    try:
        checksum = sum(
            int(digit) * (1 if i % 2 == 0 else 3)
            for i, digit in enumerate(isbn[:-1])
        )
        check = (10 - (checksum % 10)) % 10

        if int(isbn[-1]) != check:
            return False, "Invalid ISBN-13 checksum"
        return True, None
    except ValueError:
        return False, "ISBN-13 must contain only digits"


def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    """Validate phone number format (basic)

    Args:
        phone: Phone number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone or not isinstance(phone, str):
        return False, "Phone number must be a non-empty string"

    phone = phone.strip().replace(" ", "").replace("-", "").replace("+", "")

    if not phone.isdigit():
        return False, "Phone number must contain only digits"

    if len(phone) < 7 or len(phone) > 15:
        return False, "Phone number must be between 7 and 15 digits"

    return True, None


def validate_search_query(query: str) -> Tuple[bool, Optional[str]]:
    """Validate search query

    Args:
        query: Search query to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not query or not isinstance(query, str):
        return False, "Search query must be a non-empty string"

    query = query.strip()

    if len(query) < 2:
        return False, "Search query must be at least 2 characters long"

    if len(query) > 500:
        return False, "Search query must not exceed 500 characters"

    return True, None
