from dotenv import load_dotenv

# Importing the automations module automatically loads all automation task classes
from . import automations  # noqa: F401
from .base import BaseAutomation, ExecutionResult
from .logging_config import get_logger, setup_logging
from .notification import NotificationManager


class AutomationApp:
    """Main automation application class."""

    def __init__(self):
        """Initialize the application."""
        load_dotenv()
        setup_logging()

        self._setup_logging()
        self.logger = get_logger(__class__.__name__)

        self.notification_manager = NotificationManager()

    async def run_automation(
        self, task_name: str, automation: BaseAutomation | None = None
    ) -> bool:
        """
        Execute an automation task.

        Args:
            task_name: The name of the task to execute.

        Returns:
            Whether the task executed successfully.

        Examples:
            await app.run_automation("download_orders")
        """
        automation_class = BaseAutomation.get_task_class(task_name)

        if automation_class is None:
            available_tasks = ", ".join(BaseAutomation.get_registry().keys())
            raise ValueError(
                f"Invalid task name: '{task_name}'. Available tasks: {available_tasks}"
            )

        automation = automation_class()

        self.logger.info(f"Starting task execution: {task_name}")

        result: ExecutionResult = await automation.execute()

        self.notification_manager.notify(result)

        return result.success

    @classmethod
    def get_available_tasks(cls) -> list[str]:
        """
        Get all available tasks.

        Returns:
            A list of task names.
        """
        return list(BaseAutomation.get_registry().keys())
