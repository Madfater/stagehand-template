import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from automation.base import ExecutionResult
from automation.config import config

from .base_notifier import BaseNotifier


class EmailNotifier(BaseNotifier):
    """Email notifier (using SMTP)."""

    def __init__(self):
        """Initialize the email notifier."""
        super().__init__()
        self.smtp_host = config.email.SMTP_HOST
        self.smtp_port = config.email.SMTP_PORT
        self.smtp_username = config.email.SMTP_USERNAME
        self.smtp_password = config.email.SMTP_PASSWORD
        self.recipients = config.email.DEFAULT_RECIPIENTS
        self.use_tls = config.email.USE_TLS

    def is_enabled(self) -> bool:
        """
        Check if email notification is enabled.

        Returns:
            True if enabled, False otherwise.
        """
        return (
            "email" in config.notification.ENABLED_NOTIFIERS
            and self.smtp_host
            and self.smtp_username
            and self.smtp_password
            and self.recipients
        )

    def send_notification(self, result: ExecutionResult) -> bool:
        """
        Send email notification.

        Args:
            result: The task execution result.

        Returns:
            True if sent successfully, False otherwise.
        """
        if not self.is_enabled():
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = self._format_subject(result)
            msg["From"] = self.smtp_username
            msg["To"] = ", ".join(self.recipients)

            text_content = (
                self.format_success_message(result)
                if result.success
                else self.format_error_message(result)
            )

            html_content = self._format_html_message(result)

            msg.attach(MIMEText(text_content, "plain", "utf-8"))
            msg.attach(MIMEText(html_content, "html", "utf-8"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            recipient_count = len(self.recipients)
            self.logger.info(f"Email notification sent (recipients: {recipient_count})")
            return True

        except smtplib.SMTPException as e:
            self.logger.error(f"SMTP error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Email notification unexpected error: {str(e)}")
            return False

    def _format_subject(self, result: ExecutionResult) -> str:
        """
        Format email subject.

        Args:
            result: The task execution result.

        Returns:
            The formatted subject.
        """
        status = "Success" if result.success else "Failed"
        return f"[Automation] {result.task_name} {status}"

    def _format_html_message(self, result: ExecutionResult) -> str:
        """
        Format HTML email content.

        Args:
            result: The task execution result.

        Returns:
            The formatted HTML content.
        """
        status_emoji = "✅" if result.success else "❌"
        status_color = "#28a745" if result.success else "#dc3545"

        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
              <h2 style="color: {status_color};">
                {status_emoji} {result.task_name}
              </h2>
              <p style="font-size: 16px;">
                <strong>Status:</strong>
                <span style="color: {status_color};">
                  {"Execution successful" if result.success else "Execution failed"}
                </span>
              </p>
        """

        if not result.success and result.error_message:
            html += f"""
              <div style="background-color: #f8d7da; border: 1px solid #f5c6cb;
                         border-radius: 4px; padding: 15px; margin: 15px 0;">
                <strong>Error message:</strong><br>
                <code style="color: #721c24;">{result.error_message}</code>
              </div>
            """

        if result.details:
            html += """
              <h3>Details</h3>
              <table style="width: 100%; border-collapse: collapse;">
            """
            for key, value in result.details.items():
                html += f"""
                <tr>
                  <td style="padding: 8px; border-bottom: 1px solid #ddd;
                             font-weight: bold;">{key}</td>
                  <td style="padding: 8px; border-bottom: 1px solid #ddd;">
                    {value}
                  </td>
                </tr>
                """
            html += "</table>"

        if result.get_execution_time() > 0:
            html += f"""
              <p style="margin-top: 20px; color: #6c757d; font-size: 14px;">
                Execution time: {result.get_execution_time():.2f} seconds<br>
                Timestamp: {result.start_time.strftime("%Y-%m-%d %H:%M:%S")}
              </p>
            """

        html += """
            </div>
          </body>
        </html>
        """

        return html
