from threading import Lock
from typing import Optional

from automation.base import ExecutionResult
from automation.logging_config import get_logger

from .notifiers import BaseNotifier


class NotificationManager:
    """Notification manager (Singleton pattern)."""

    _instance: Optional["NotificationManager"] = None
    _lock: Lock = Lock()

    def __new__(cls):
        """Create a new instance or return the existing singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the notification manager."""
        # Prevent re-initialization
        if hasattr(self, "_initialized"):
            return

        self.logger = get_logger(__class__.__name__)
        self.notifiers: list[BaseNotifier] = []
        self.__initialize_notifiers()
        self._initialized = True

    def __initialize_notifiers(self) -> None:
        """Initialize all notifiers (using auto-registration mechanism)."""
        self.logger.info("Initializing notification system...")

        for notifier_class in BaseNotifier.get_registry().values():
            try:
                instance = notifier_class()
                if instance.is_enabled():
                    self.notifiers.append(instance)
                    self.logger.info(f"{notifier_class.__name__} enabled")
                else:
                    self.logger.info(f"{notifier_class.__name__} not enabled")
            except Exception as e:
                self.logger.warning(
                    f"{notifier_class.__name__} initialization failed: {e}"
                )

        if not self.notifiers:
            self.logger.warning("No notifiers enabled")

    def notify(self, result: ExecutionResult) -> None:
        """
        Send notifications to all enabled notifiers.

        Args:
            result: The task execution result.
        """
        if not self.notifiers:
            self.logger.debug("No notifiers enabled, skipping notification")
            return

        success_count = 0
        for notifier in self.notifiers:
            try:
                if notifier.send_notification(result):
                    success_count += 1
            except Exception as e:
                self.logger.error(
                    f"{__class__.__name__} exception while sending notification: {e}",
                    exc_info=True,
                )

        total = len(self.notifiers)
        self.logger.info(f"Notification complete: {success_count}/{total} succeeded")
