from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage

from automation.base import ExecutionResult
from automation.config import config

from .base_notifier import BaseNotifier


class LineNotifier(BaseNotifier):
    """LINE Bot notifier."""

    def __init__(self):
        """Initialize the LINE notifier."""
        super().__init__()
        self.channel_access_token = config.line.CHANNEL_ACCESS_TOKEN
        self.target_ids = config.line.TARGET_IDS

        if self.channel_access_token:
            try:
                self.line_bot_api = LineBotApi(self.channel_access_token)
            except Exception as e:
                self.logger.warning(f"LINE Bot API initialization failed: {e}")
                self.line_bot_api = None
        else:
            self.line_bot_api = None

    def is_enabled(self) -> bool:
        """
        Check if LINE notification is enabled.

        Returns:
            True if enabled, False otherwise.
        """
        return (
            "line" in config.notification.ENABLED_NOTIFIERS
            and self.line_bot_api is not None
            and len(self.target_ids) > 0
        )

    def send_notification(self, result: ExecutionResult) -> bool:
        """
        Send LINE notification.

        Args:
            result: The task execution result.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.is_enabled():
            return False

        try:
            message = (
                self.format_success_message(result)
                if result.success
                else self.format_error_message(result)
            )

            # LINE message length limit is 5000 characters
            if len(message) > 5000:
                message = message[:4997] + "..."

            # Send to all target recipients
            success_count = 0
            failed_count = 0

            for target_id in self.target_ids:
                try:
                    self.line_bot_api.push_message(
                        target_id, TextSendMessage(text=message)
                    )
                    success_count += 1
                except LineBotApiError as e:
                    self.logger.error(
                        f"LINE message send failed (target: {target_id}): "
                        f"{e.status_code} - {e.error.message}"
                    )
                    failed_count += 1
                except Exception as e:
                    self.logger.error(
                        f"LINE notification error (target: {target_id}): {e}"
                    )
                    failed_count += 1

            # Log send results
            total = len(self.target_ids)
            if success_count > 0:
                self.logger.info(
                    f"LINE notification sent ({success_count}/{total} succeeded)"
                )
            if failed_count > 0:
                self.logger.warning(
                    f"Some LINE notifications failed to send "
                    f"(failed: {failed_count}/{len(self.target_ids)})"
                )

            # Return True if at least one was sent successfully
            return success_count > 0

        except Exception as e:
            self.logger.error(f"LINE notification unexpected error: {str(e)}")
            return False
