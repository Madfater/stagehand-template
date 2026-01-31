"""Exception class definitions for the automation framework.

Provides structured error codes and context information for more precise error messages.
"""

from typing import Any


class StagehandAutomationError(Exception):
    """Base exception class for Stagehand automation.

    All automation-related exceptions should inherit from this class.
    Provides error_code and context attributes for structured error information.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict[str, Any] | None = None,
    ):
        """
        Initialize the exception.

        Args:
            message: The error message.
            error_code: The error code (e.g. "E1001").
            context: Additional error context information.
        """
        self.error_code = error_code
        self.context = context or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Format the error message with error code prefix."""
        base_message = super().__str__()
        if self.error_code:
            return f"[{self.error_code}] {base_message}"
        return base_message


class ConfigurationError(StagehandAutomationError):
    """Configuration error exception."""

    INVALID_CONFIG = "E0001"
    MISSING_ENV_VAR = "E0002"

    def __init__(
        self,
        message: str,
        error_code: str = "E0001",
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code=error_code, context=context)


class LoginError(StagehandAutomationError):
    """Login-related error exception."""

    JWT_EXPIRED = "E1001"
    CAPTCHA_FAILED = "E1002"

    def __init__(
        self,
        message: str,
        error_code: str = "E1001",
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code=error_code, context=context)


class CaptchaRecognitionError(StagehandAutomationError):
    """Captcha recognition error exception."""

    API_ERROR = "E2001"
    RECOGNITION_FAILED = "E2002"

    def __init__(
        self,
        message: str,
        error_code: str = "E2001",
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code=error_code, context=context)


class GoogleSheetsError(StagehandAutomationError):
    """Google Sheets API error exception."""

    AUTH_FAILED = "E3001"
    API_ERROR = "E3002"
    PERMISSION_DENIED = "E3003"

    def __init__(
        self,
        message: str,
        error_code: str = "E3001",
        context: dict[str, Any] | None = None,
    ):
        super().__init__(message, error_code=error_code, context=context)
