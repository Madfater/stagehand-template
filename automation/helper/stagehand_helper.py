import asyncio

from stagehand import StagehandPage

from ..exceptions import StagehandAutomationError
from ..logging_config import get_logger


class StagehandHelper:
    """Helper class for common Stagehand page operations."""

    def __init__(self, page: StagehandPage, max_retries: int = 3):
        """
        Initialize the Stagehand helper.

        Args:
            page: The Stagehand page object.
            max_retries: Maximum number of retry attempts.
        """
        self.page = page
        self.max_retries = max_retries
        self.logger = get_logger(__class__.__name__)

    async def click_the_button(self, label) -> None:
        """
        Find a button element on the page and click it, with automatic retry on failure.

        Args:
            label: Natural language description of the button text, e.g., "Login".

        Raises:
            StagehandAutomationError: When all retries fail.
        """
        self.logger.info(f"Clicking the {label} button")
        for attempt in range(self.max_retries):
            try:
                await self.page.wait_for_load_state()
                button = await self.page.observe(f"find the button labeled {label}")
                await self.page.act(button[0])
                return
            except Exception as e:
                self.logger.warning(
                    f"Failed to click {label} button "
                    f"(attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)

        raise StagehandAutomationError(f"Could not find {label} button")

    async def type_into_field(
        self,
        field_name: str,
        text: str,
        clear_first: bool = True,
        log_value: bool = False,
    ) -> None:
        """
        Find an input field and fill in text, with automatic retry on failure.

        Args:
            field_name: Natural language description of the field name,
                e.g., "account", "password", "CAPTCHA".
            text: The text to fill in.
            clear_first: Whether to clear the field first (default True).
            log_value: Whether to log the filled value (default False,
                sensitive data like passwords should not be logged).

        Raises:
            StagehandAutomationError: When all retries fail.
        """
        self.logger.info(f"Filling text into {field_name} field")
        for attempt in range(self.max_retries):
            try:
                elements = await self.page.observe(
                    f"find the input field for {field_name}"
                )

                if elements and len(elements) > 0:
                    field_locator = self.page.locator(elements[0].selector)

                    if clear_first:
                        await field_locator.clear()

                    await field_locator.fill(text)

                    if log_value:
                        self.logger.info(f"Filled {field_name}: {text}")
                    else:
                        self.logger.info(f"Filled {field_name}")
                    return

            except Exception as e:
                self.logger.warning(
                    f"Failed to fill {field_name} "
                    f"(attempt {attempt + 1}/{self.max_retries}): {e}"
                )
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)

        raise StagehandAutomationError(
            f"Could not find {field_name} field or fill failed"
        )
