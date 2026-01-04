"""AutomationApp unit tests."""

from unittest.mock import patch

import pytest

from automation.app import AutomationApp


class TestAutomationApp:
    """Test AutomationApp."""

    @patch("automation.app.load_dotenv")
    @patch("automation.app.setup_logging")
    @patch("automation.app.NotificationManager")
    def test_init(
        self, _mock_notification_manager, mock_setup_logging, mock_load_dotenv
    ):
        """Test initialization."""
        app = AutomationApp()

        mock_load_dotenv.assert_called_once()
        mock_setup_logging.assert_called_once()
        assert app.notification_manager is not None

    def test_get_available_tasks(self):
        """Test getting available tasks list."""
        tasks = AutomationApp.get_available_tasks()
        assert isinstance(tasks, list)

    @pytest.mark.asyncio
    @patch("automation.app.load_dotenv")
    @patch("automation.app.setup_logging")
    @patch("automation.app.NotificationManager")
    async def test_run_automation_invalid_task(
        self, _mock_notification_manager, _mock_setup_logging, _mock_load_dotenv
    ):
        """Test executing invalid task name."""
        app = AutomationApp()

        with pytest.raises(ValueError) as exc_info:
            await app.run_automation("invalid_task_name")

        assert "Invalid task name" in str(exc_info.value)
