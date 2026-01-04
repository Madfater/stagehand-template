"""LINE Notifier unit tests."""

from datetime import datetime
from unittest.mock import Mock, patch

from linebot.exceptions import LineBotApiError

from automation.base import ExecutionResult
from automation.notification.notifiers.line_notifier import LineNotifier


class TestLineNotifier:
    """Test LineNotifier."""

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_init_with_token(self, mock_api, mock_config):
        """Test initialization with token."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1"]

        notifier = LineNotifier()

        assert notifier.channel_access_token == "test-token"
        mock_api.assert_called_once_with("test-token")

    @patch("automation.notification.notifiers.line_notifier.config")
    def test_init_without_token(self, mock_config):
        """Test initialization without token."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = None
        mock_config.line.TARGET_IDS = []

        notifier = LineNotifier()

        assert notifier.line_bot_api is None

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_is_enabled_true(self, _mock_api, mock_config):
        """Test enabled status check - enabled."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1"]
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        notifier = LineNotifier()

        assert notifier.is_enabled() is True

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_is_enabled_false_no_token(self, _mock_api, mock_config):
        """Test enabled status check - no token."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = None
        mock_config.line.TARGET_IDS = ["target-1"]
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        notifier = LineNotifier()

        assert notifier.is_enabled() is False

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_is_enabled_false_not_in_list(self, _mock_api, mock_config):
        """Test enabled status check - not in enabled list."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1"]
        mock_config.notification.ENABLED_NOTIFIERS = ["email"]

        notifier = LineNotifier()

        assert notifier.is_enabled() is False

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_is_enabled_false_no_targets(self, _mock_api, mock_config):
        """Test enabled status check - no target recipients."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = []
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        notifier = LineNotifier()

        assert notifier.is_enabled() is False

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_send_notification_success(self, mock_api, mock_config):
        """Test sending notification successfully."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1"]
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        mock_line_bot = Mock()
        mock_api.return_value = mock_line_bot

        notifier = LineNotifier()
        result = ExecutionResult(task_name="Test Task")
        result.success = True
        result.end_time = datetime.now()

        success = notifier.send_notification(result)

        assert success is True
        mock_line_bot.push_message.assert_called_once()

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_send_notification_to_multiple_targets(self, mock_api, mock_config):
        """Test sending notification to multiple targets."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1", "target-2", "target-3"]
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        mock_line_bot = Mock()
        mock_api.return_value = mock_line_bot

        notifier = LineNotifier()
        result = ExecutionResult(task_name="Test Task")
        result.success = True
        result.end_time = datetime.now()

        success = notifier.send_notification(result)

        assert success is True
        assert mock_line_bot.push_message.call_count == 3

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_send_notification_api_error(self, mock_api, mock_config):
        """Test LINE API error handling."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1"]
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        mock_line_bot = Mock()
        mock_api.return_value = mock_line_bot

        # Mock LineBotApiError
        error = Mock()
        error.message = "Invalid token"
        api_error = LineBotApiError(status_code=400, headers={}, error=error)
        mock_line_bot.push_message.side_effect = api_error

        notifier = LineNotifier()
        result = ExecutionResult(task_name="Test Task")
        result.success = True
        result.end_time = datetime.now()

        success = notifier.send_notification(result)

        assert success is False

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_send_notification_partial_failure(self, mock_api, mock_config):
        """Test partial send failure."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1", "target-2"]
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        mock_line_bot = Mock()
        mock_api.return_value = mock_line_bot

        # First succeeds, second fails
        error = Mock()
        error.message = "Invalid target"
        api_error = LineBotApiError(status_code=400, headers={}, error=error)
        mock_line_bot.push_message.side_effect = [None, api_error]

        notifier = LineNotifier()
        result = ExecutionResult(task_name="Test Task")
        result.success = True
        result.end_time = datetime.now()

        success = notifier.send_notification(result)

        # Returns True if at least one succeeds
        assert success is True

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_send_notification_when_disabled(self, mock_api, mock_config):
        """Test no notification sent when disabled."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1"]
        mock_config.notification.ENABLED_NOTIFIERS = []  # Not enabled

        mock_line_bot = Mock()
        mock_api.return_value = mock_line_bot

        notifier = LineNotifier()
        result = ExecutionResult(task_name="Test Task")
        result.success = True
        result.end_time = datetime.now()

        success = notifier.send_notification(result)

        assert success is False
        mock_line_bot.push_message.assert_not_called()

    @patch("automation.notification.notifiers.line_notifier.config")
    @patch("automation.notification.notifiers.line_notifier.LineBotApi")
    def test_send_error_notification(self, mock_api, mock_config):
        """Test sending error notification."""
        mock_config.line.CHANNEL_ACCESS_TOKEN = "test-token"
        mock_config.line.TARGET_IDS = ["target-1"]
        mock_config.notification.ENABLED_NOTIFIERS = ["line"]

        mock_line_bot = Mock()
        mock_api.return_value = mock_line_bot

        notifier = LineNotifier()
        result = ExecutionResult(task_name="Test Task")
        result.success = False
        result.error_message = "An error occurred"
        result.end_time = datetime.now()

        success = notifier.send_notification(result)

        assert success is True
        mock_line_bot.push_message.assert_called_once()
