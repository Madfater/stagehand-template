from abc import ABC, abstractmethod

from automation.base import ExecutionResult
from automation.logging_config import get_logger


class BaseNotifier(ABC):
    """Abstract base class for notifiers."""

    _registry: dict[str, type["BaseNotifier"]] = {}

    def __init_subclass__(cls, **kwargs):
        """
        Automatically register subclasses.

        Called automatically when a subclass is defined, registering it to _registry.
        """
        super().__init_subclass__(**kwargs)

        notifier_name = cls.__name__.replace("Notifier", "").lower()

        cls._registry[notifier_name] = cls

    @classmethod
    def get_registry(cls) -> dict[str, type["BaseNotifier"]]:
        """Get all registered notifiers."""
        return cls._registry.copy()

    @classmethod
    def get_enabled_notifiers(cls) -> list["BaseNotifier"]:
        """
        Get all enabled notifier instances.

        Returns:
            A list of enabled notifier instances.
        """
        enabled_notifiers = []
        for notifier_class in cls._registry.values():
            try:
                instance = notifier_class()
                if instance.is_enabled():
                    enabled_notifiers.append(instance)
            except Exception:
                pass
        return enabled_notifiers

    def __init__(self):
        """Initialize the notifier."""
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    def send_notification(self, result: ExecutionResult) -> bool:
        """
        Send a notification (must be implemented by subclasses).

        Args:
            result: The task execution result.

        Returns:
            True if sent successfully, False otherwise.
        """
        pass

    @abstractmethod
    def is_enabled(self) -> bool:
        """
        Check if the notifier is enabled (must be implemented by subclasses).

        Returns:
            True if enabled, False otherwise.
        """
        pass

    def format_success_message(self, result: ExecutionResult) -> str:
        """
        Format a success message (default implementation, can be overridden).

        Args:
            result: The task execution result.

        Returns:
            The formatted success message.
        """
        lines = [f"{result.task_name} executed successfully"]
        lines.append(f"Start time: {result.start_time.strftime('%Y/%m/%d %I:%M%p')}")

        if result.details:
            lines.append("")
            for key, value in result.details.items():
                lines.append(f"• {key}: {value}")

        if result.get_execution_time() > 0:
            lines.append("")
            lines.append(
                f"Total execution time: {result.get_execution_time():.2f} seconds"
            )

        return "\n".join(lines)

    def format_error_message(self, result: ExecutionResult) -> str:
        """
        Format an error message (default implementation, can be overridden).

        When result.error_info is available, displays structured error information
        including error code, error type, location, etc.
        Backward compatible: falls back to error_message when error_info is None.

        Args:
            result: The task execution result.

        Returns:
            The formatted error message.
        """
        lines = [
            f"{result.task_name} execution failed",
            f"Start time: {result.start_time.strftime('%Y/%m/%d %I:%M%p')}",
            "",
        ]

        if result.error_info is not None:
            info = result.error_info

            if info.error_code:
                lines.append(f"Error code: {info.error_code}")

            if info.error_type:
                lines.append(f"Error type: {info.error_type}")

            lines.append(f"Error message: {info.message}")

            if info.location:
                lines.append(f"Location: {info.location}")

            if info.context.get("errno") is not None:
                lines.append(f"OS errno: {info.context['errno']}")
            if info.context.get("filename"):
                lines.append(f"File: {info.context['filename']}")

            retry_history = info.context.get("retry_history")
            if retry_history:
                lines.append(f"Retry count: {len(retry_history)}")

        else:
            lines.append(f"Error message: {result.error_message or 'Unknown error'}")

        if result.get_execution_time() > 0:
            lines.append("")
            lines.append(
                f"Total execution time: {result.get_execution_time():.2f} seconds"
            )
        return "\n".join(lines)
