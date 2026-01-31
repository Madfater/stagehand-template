from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from automation.exceptions import StagehandAutomationError


@dataclass
class ErrorInfo:
    """Structured error information data class.

    Stores detailed exception information including error code, error type,
    location, stack trace, and additional context.
    """

    message: str
    error_code: str | None = None
    error_type: str = ""
    location: str = ""
    stack_trace: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_exception(cls, exc: Exception) -> ErrorInfo:
        """Automatically extract error information from an exception object.

        Args:
            exc: Any Exception object.

        Returns:
            An ErrorInfo instance containing detailed exception information.
        """
        error_type = type(exc).__qualname__

        error_code: str | None = None
        context: dict[str, Any] = {}

        if isinstance(exc, StagehandAutomationError):
            error_code = exc.error_code
            context = exc.context.copy()

        location = ""
        tb = traceback.extract_tb(exc.__traceback__)
        if tb:
            last_frame = tb[-1]
            location = f"{last_frame.filename}:{last_frame.lineno} in {last_frame.name}"

        stack_trace = "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)
        )

        if isinstance(exc, OSError):
            if exc.errno is not None:
                context["errno"] = exc.errno
            if exc.filename is not None:
                context["filename"] = exc.filename

        return cls(
            message=str(exc),
            error_code=error_code,
            error_type=error_type,
            location=location,
            stack_trace=stack_trace,
            context=context,
        )


@dataclass
class ExecutionResult:
    """Task execution result data class."""

    task_name: str
    success: bool = field(default=True)
    error_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    error_info: ErrorInfo | None = None

    def add_detail(self, key: str, value: Any) -> None:
        """
        Add detail information.

        Args:
            key: The detail key name.
            value: The detail value.
        """
        self.details[key] = value

    def get_execution_time(self) -> int:
        """
        Get the execution time in seconds.

        Returns:
            The execution time in seconds as an integer.
        """
        return int((self.end_time - self.start_time).total_seconds())

    def set_error(self, exc: Exception) -> None:
        """Set error information while maintaining backward compatibility.

        Sets success=False, error_message (backward compatible), and
        error_info (structured error information).

        Args:
            exc: The exception that occurred.
        """
        self.success = False
        self.error_message = str(exc)
        self.error_info = ErrorInfo.from_exception(exc)

    def get_error_summary(self) -> str:
        """Generate a concise error summary suitable for notification messages.

        Returns:
            A formatted error summary string.
        """
        if self.error_info is None:
            return self.error_message or "Unknown error"

        parts: list[str] = []

        if self.error_info.error_code:
            parts.append(f"[{self.error_info.error_code}]")

        if self.error_info.error_type:
            parts.append(f"({self.error_info.error_type})")

        parts.append(self.error_info.message)

        return " ".join(parts)
