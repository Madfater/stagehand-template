"""
Example automation demonstrating BaseAutomation, BaseTask, and StagehandHelper.
"""

from automation.base import BaseAutomation
from automation.config import config
from automation.helper import StagehandHelper

from .tasks import LoginTask


class Example(BaseAutomation):
    """
    Example automation demonstrating three approaches:
    1. Direct Stagehand page operations
    2. Using BaseTask for complex operations with retry
    """

    async def automation(self) -> None:
        """Execute the example automation."""
        page = self.stagehand.page

        # Step 1: Navigate to target website (direct page operation)
        await page.goto("https://example.com/login")

        # Step 2: Use BaseTask for complex operations
        login_task = LoginTask(page)
        await login_task.execute()

        # Record result
        login_verified = login_task.get_execution_stats().get("login_verified")
        self.execution_result.add_detail(
            "Login Status",
            "Success" if login_verified else "Failed",
        )

        self.logger.info("Example automation completed")
