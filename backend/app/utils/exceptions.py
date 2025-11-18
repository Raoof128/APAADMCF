"""
Exception classes for the application
"""

from fastapi import HTTPException, status


class ADMComplianceException(Exception):
    """Base exception for ADM Compliance Framework"""
    pass


class DatabaseException(ADMComplianceException):
    """Database operation failed"""
    pass


class ValidationException(ADMComplianceException):
    """Data validation failed"""
    pass


class AuthenticationException(ADMComplianceException):
    """Authentication failed"""
    pass


class AuthorizationException(ADMComplianceException):
    """Authorization failed - insufficient permissions"""
    pass


class ResourceNotFoundException(ADMComplianceException):
    """Requested resource not found"""
    pass


class DuplicateResourceException(ADMComplianceException):
    """Resource already exists"""
    pass


class PIAException(ADMComplianceException):
    """PIA-related operation failed"""
    pass


class FairnessAssessmentException(ADMComplianceException):
    """Fairness assessment failed"""
    pass


class ReportGenerationException(ADMComplianceException):
    """Report generation failed"""
    pass


# HTTP Exception helpers
def not_found_exception(detail: str = "Resource not found"):
    """Return 404 Not Found exception"""
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail
    )


def unauthorized_exception(detail: str = "Not authenticated"):
    """Return 401 Unauthorized exception"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception(detail: str = "Insufficient permissions"):
    """Return 403 Forbidden exception"""
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail
    )


def bad_request_exception(detail: str = "Invalid request"):
    """Return 400 Bad Request exception"""
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )


def conflict_exception(detail: str = "Resource already exists"):
    """Return 409 Conflict exception"""
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=detail
    )


def internal_server_exception(detail: str = "Internal server error"):
    """Return 500 Internal Server Error exception"""
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=detail
    )
