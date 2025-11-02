"""
Custom exceptions for the Social Amplifier backend
"""
from fastapi import HTTPException, status


class SocialAmplifierException(Exception):
    """Base exception for Social Amplifier"""
    pass


class AuthenticationError(SocialAmplifierException):
    """Authentication failed"""
    pass


class PlatformConnectionError(SocialAmplifierException):
    """Failed to connect to social media platform"""
    pass


class ContentGenerationError(SocialAmplifierException):
    """Failed to generate content"""
    pass


class PublishingError(SocialAmplifierException):
    """Failed to publish content"""
    pass


class TokenExpiredError(SocialAmplifierException):
    """OAuth token has expired"""
    pass


class RateLimitError(SocialAmplifierException):
    """API rate limit exceeded"""
    pass


# HTTP Exceptions
def unauthorized_exception(detail: str = "Not authenticated"):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def forbidden_exception(detail: str = "Insufficient permissions"):
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=detail,
    )


def not_found_exception(detail: str = "Resource not found"):
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=detail,
    )


def bad_request_exception(detail: str = "Bad request"):
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail,
    )


def rate_limit_exception(detail: str = "Rate limit exceeded"):
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=detail,
    )
