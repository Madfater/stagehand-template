"""
Example sub-task using BaseTask.

This module demonstrates how to create a reusable sub-task with built-in
retry mechanism using the BaseTask base class.
"""

from automation import config
from automation.base import BaseTask
from automation.exceptions import StagehandAutomationError
from automation.helper.stagehand_helper import StagehandHelper


class LoginTask(BaseTask):
    """
    Login task with retry mechanism.

    This task handles the login process with automatic retries
    if the login fails due to network issues or other transient errors.
    """

    def __init__(self, page, max_retries: int = 3):
        """
        Initialize the login task.

        Args:
            page: Stagehand page object.
            username: Username for login.
            password: Password for login.
            max_retries: Maximum retry attempts (default: 3).
        """
        super().__init__(
            page=page,
            max_retries=max_retries,
            retry_delay=2.0,
            retry_on_exceptions=(TimeoutError, ConnectionError),
        )

    async def task(self) -> None:
        helper = StagehandHelper(self.page)

        account = "..."
        password = "..."

        """Execute the login process."""
        self.logger.info(f"Logging in as {account}")

        await helper.type_into_field("username", account, log_value=True)
        await helper.type_into_field("password", password)
        await helper.click_the_button("Login")

        # Verify login success
        result = await self.page.observe("Check if login was successful")
        if result is not None:
            self.execution_stats["login_verified"] = True
            self.logger.info("Login completed successfully")
        else:
            self.execution_stats["login_verified"] = False
            raise StagehandAutomationError("Login verification failed")
