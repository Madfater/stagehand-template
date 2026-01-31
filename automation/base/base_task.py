import asyncio
from abc import ABC, abstractmethod
from typing import Any

from stagehand import StagehandPage

from ..exceptions import StagehandAutomationError
from ..logging_config import get_logger


class BaseTask(ABC):
    """
    Base class for automation tasks.

    Provides a generic retry mechanism. Subclasses can:
    1. Implement the task() method to use the default retry mechanism.
    2. Override the execute() method to implement custom execution logic.
    """

    def __init__(
        self,
        page: StagehandPage,
        max_retries: int,
        retry_delay: float = 1.0,
        retry_on_exceptions: tuple[type[Exception], ...] | None = None,
    ):
        """
        Initialize the task.

        Args:
            page: Stagehand page object.
            max_retries: Maximum number of retry attempts.
            retry_delay: Delay in seconds between retries.
            retry_on_exceptions: Tuple of exception types to retry on.
                None means retry on all exceptions.
        """
        self.page = page
        self.max_retries = max_retries
        self.logger = get_logger(self.__class__.__name__)
        self.retry_delay = retry_delay
        self.retry_on_exceptions = retry_on_exceptions
        self.execution_stats: dict[str, Any] = {}
        self.retry_history: list[dict[str, Any]] = []

    def get_execution_stats(self) -> dict[str, Any]:
        """
        Get the execution statistics.

        Returns:
            A dictionary containing execution statistics.
        """
        return self.execution_stats

    @abstractmethod
    async def task(self) -> None:
        """
        Execute the automation sub-task (must be implemented by subclasses).

        This method should contain the actual task logic without handling retries.
        """
        pass

    def should_retry(self, exception: Exception) -> bool:
        """
        Determine whether to retry.

        Args:
            exception: The exception that occurred.

        Returns:
            Whether to retry.
        """
        if self.retry_on_exceptions is None:
            return True
        return isinstance(exception, self.retry_on_exceptions)

    async def execute(self) -> None:
        """
        Execute the task with retry mechanism.

        Subclasses can override this method to implement custom execution logic.
        """
        last_exception = None

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(f"Attempt {attempt} of {self.max_retries}")
                await self.task()
                self.logger.info("Task executed successfully")
                return

            except Exception as e:
                last_exception = e

                self.retry_history.append(
                    {
                        "attempt": attempt,
                        "error_type": type(e).__qualname__,
                        "error_message": str(e),
                    }
                )

                if not self.should_retry(e):
                    raise

                self.logger.error(f"Attempt {attempt} failed: {e}", exc_info=True)

                if attempt == self.max_retries:
                    self.logger.error(
                        f"Task failed: maximum retries ({self.max_retries}) reached",
                        exc_info=True,
                    )
                    break
                self.logger.info(f"Waiting {self.retry_delay} seconds before retry...")
                await asyncio.sleep(self.retry_delay)

        if last_exception:
            self.execution_stats["retry_history"] = self.retry_history

            if isinstance(last_exception, StagehandAutomationError):
                last_exception.context["retry_history"] = self.retry_history

            raise last_exception
