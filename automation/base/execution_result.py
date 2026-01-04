from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ExecutionResult:
    """Task execution result data class."""

    task_name: str
    success: bool = field(default=True)
    error_message: str | None = None
    details: dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None

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
