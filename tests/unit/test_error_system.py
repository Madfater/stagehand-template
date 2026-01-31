"""結構化錯誤訊息系統的單元測試。"""

from datetime import datetime

import pytest

from automation.base.execution_result import ErrorInfo, ExecutionResult
from automation.exceptions import (
    CaptchaRecognitionError,
    ConfigurationError,
    GoogleSheetsError,
    LoginError,
    StagehandAutomationError,
)


class TestStagehandAutomationError:
    """Test StagehandAutomationError base exception."""

    def test_str_with_error_code(self):
        """Test __str__ includes error code."""
        exc = StagehandAutomationError("Something failed", error_code="E9999")
        assert str(exc) == "[E9999] Something failed"

    def test_str_without_error_code(self):
        """Test __str__ without error code."""
        exc = StagehandAutomationError("Something failed")
        assert str(exc) == "Something failed"

    def test_context_defaults_to_empty_dict(self):
        """Test context defaults to empty dict."""
        exc = StagehandAutomationError("error")
        assert exc.context == {}

    def test_context_is_set(self):
        """Test context is properly set."""
        ctx = {"key": "value"}
        exc = StagehandAutomationError("error", context=ctx)
        assert exc.context == ctx


class TestExceptionSubclasses:
    """Test exception subclass hierarchy and error codes."""

    def test_configuration_error_is_subclass(self):
        """Test ConfigurationError is a subclass of StagehandAutomationError."""
        exc = ConfigurationError("bad config")
        assert isinstance(exc, StagehandAutomationError)
        assert isinstance(exc, Exception)

    def test_configuration_error_default_code(self):
        """Test ConfigurationError default error code."""
        exc = ConfigurationError("bad config")
        assert str(exc) == "[E0001] bad config"

    def test_login_error_codes(self):
        """Test LoginError error code constants."""
        assert LoginError.JWT_EXPIRED == "E1001"
        assert LoginError.CAPTCHA_FAILED == "E1002"

        exc = LoginError("JWT expired", error_code=LoginError.JWT_EXPIRED)
        assert str(exc) == "[E1001] JWT expired"

    def test_captcha_recognition_error_codes(self):
        """Test CaptchaRecognitionError error code constants."""
        assert CaptchaRecognitionError.API_ERROR == "E2001"
        assert CaptchaRecognitionError.RECOGNITION_FAILED == "E2002"

        exc = CaptchaRecognitionError(
            "API failed", error_code=CaptchaRecognitionError.API_ERROR
        )
        assert str(exc) == "[E2001] API failed"

    def test_google_sheets_error_codes(self):
        """Test GoogleSheetsError error code constants."""
        assert GoogleSheetsError.AUTH_FAILED == "E3001"
        assert GoogleSheetsError.API_ERROR == "E3002"
        assert GoogleSheetsError.PERMISSION_DENIED == "E3003"

        exc = GoogleSheetsError(
            "Permission denied", error_code=GoogleSheetsError.PERMISSION_DENIED
        )
        assert str(exc) == "[E3003] Permission denied"

    def test_all_subclasses_are_stagehand_errors(self):
        """Test all custom exceptions inherit from StagehandAutomationError."""
        for cls in [
            ConfigurationError,
            LoginError,
            CaptchaRecognitionError,
            GoogleSheetsError,
        ]:
            exc = cls("test")
            assert isinstance(exc, StagehandAutomationError)


class TestErrorInfo:
    """Test ErrorInfo dataclass."""

    def test_from_plain_exception(self):
        """Test ErrorInfo.from_exception with a plain Exception."""
        try:
            raise ValueError("test value error")
        except ValueError as e:
            info = ErrorInfo.from_exception(e)

        assert info.message == "test value error"
        assert info.error_type == "ValueError"
        assert info.error_code is None
        assert info.context == {}
        assert info.stack_trace != ""
        assert info.location != ""

    def test_from_stagehand_error(self):
        """Test ErrorInfo.from_exception with StagehandAutomationError."""
        try:
            raise LoginError(
                "JWT expired",
                error_code=LoginError.JWT_EXPIRED,
                context={"user": "admin"},
            )
        except LoginError as e:
            info = ErrorInfo.from_exception(e)

        assert info.message == "[E1001] JWT expired"
        assert info.error_code == "E1001"
        assert info.error_type == "LoginError"
        assert info.context["user"] == "admin"
        assert "LoginError" in info.stack_trace

    def test_from_os_error(self):
        """Test ErrorInfo.from_exception with OSError."""
        try:
            raise FileNotFoundError(2, "No such file", "/tmp/missing.txt")
        except FileNotFoundError as e:
            info = ErrorInfo.from_exception(e)

        assert info.error_type == "FileNotFoundError"
        assert info.context.get("errno") == 2
        assert info.context.get("filename") == "/tmp/missing.txt"

    def test_from_exception_without_traceback(self):
        """Test ErrorInfo.from_exception when exception has no traceback."""
        exc = RuntimeError("no traceback")
        info = ErrorInfo.from_exception(exc)

        assert info.message == "no traceback"
        assert info.error_type == "RuntimeError"
        assert info.location == ""


class TestExecutionResultSetError:
    """Test ExecutionResult.set_error method."""

    def test_set_error_backward_compat(self):
        """Test set_error sets both error_message and error_info."""
        result = ExecutionResult(task_name="test")

        try:
            raise ValueError("something broke")
        except ValueError as e:
            result.set_error(e)

        assert result.success is False
        assert result.error_message == "something broke"

        assert result.error_info is not None
        assert result.error_info.error_type == "ValueError"
        assert result.error_info.message == "something broke"

    def test_set_error_with_stagehand_error(self):
        """Test set_error with StagehandAutomationError."""
        result = ExecutionResult(task_name="test")

        try:
            raise LoginError("login failed", error_code="E1001")
        except LoginError as e:
            result.set_error(e)

        assert result.error_info is not None
        assert result.error_info.error_code == "E1001"
        assert result.error_info.error_type == "LoginError"


class TestExecutionResultGetErrorSummary:
    """Test ExecutionResult.get_error_summary method."""

    def test_summary_without_error_info(self):
        """Test get_error_summary when error_info is None."""
        result = ExecutionResult(task_name="test")
        result.error_message = "simple error"

        assert result.get_error_summary() == "simple error"

    def test_summary_without_any_error(self):
        """Test get_error_summary when no error is set."""
        result = ExecutionResult(task_name="test")
        assert result.get_error_summary() == "Unknown error"

    def test_summary_with_error_info(self):
        """Test get_error_summary with structured error info."""
        result = ExecutionResult(task_name="test")

        try:
            raise LoginError("JWT expired", error_code="E1001")
        except LoginError as e:
            result.set_error(e)

        summary = result.get_error_summary()
        assert "[E1001]" in summary
        assert "(LoginError)" in summary
        assert "JWT expired" in summary

    def test_summary_with_plain_exception(self):
        """Test get_error_summary with a plain exception."""
        result = ExecutionResult(task_name="test")

        try:
            raise ValueError("bad value")
        except ValueError as e:
            result.set_error(e)

        summary = result.get_error_summary()
        assert "(ValueError)" in summary
        assert "bad value" in summary


class TestRetryHistoryIntegration:
    """Test retry history in exception context."""

    def test_stagehand_error_context_mutable(self):
        """Test that context dict on StagehandAutomationError is mutable."""
        exc = LoginError("fail", error_code="E1001")
        exc.context["retry_history"] = [
            {"attempt": 1, "error_type": "LoginError", "error_message": "fail"},
        ]

        info = ErrorInfo.from_exception(exc)
        assert len(info.context["retry_history"]) == 1

    def test_error_info_preserves_retry_history(self):
        """Test ErrorInfo.from_exception preserves retry history from context."""
        retry_history = [
            {"attempt": 1, "error_type": "LoginError", "error_message": "try 1"},
            {"attempt": 2, "error_type": "LoginError", "error_message": "try 2"},
        ]
        exc = LoginError("final fail", error_code="E1001", context={
            "retry_history": retry_history,
        })

        info = ErrorInfo.from_exception(exc)
        assert info.context.get("retry_history") == retry_history


class TestNotifierFormatting:
    """Test BaseNotifier format_error_message with structured errors."""

    def test_format_with_error_info(self):
        """Test format_error_message displays structured info."""
        from automation.notification.notifiers.base_notifier import BaseNotifier

        # 建立一個具體的 notifier 來測試格式化
        class TestNotifier(BaseNotifier):
            def send_notification(self, result):
                return True

            def is_enabled(self):
                return True

        notifier = TestNotifier()
        result = ExecutionResult(task_name="TestTask")
        result.end_time = datetime.now()

        try:
            raise LoginError("JWT expired", error_code="E1001")
        except LoginError as e:
            result.set_error(e)

        msg = notifier.format_error_message(result)

        assert "Error code: E1001" in msg
        assert "Error type: LoginError" in msg
        assert "Error message:" in msg
        assert "Location:" in msg

    def test_format_without_error_info(self):
        """Test format_error_message backward compat without error_info."""
        from automation.notification.notifiers.base_notifier import BaseNotifier

        class TestNotifier(BaseNotifier):
            def send_notification(self, result):
                return True

            def is_enabled(self):
                return True

        notifier = TestNotifier()
        result = ExecutionResult(task_name="TestTask")
        result.success = False
        result.error_message = "legacy error"
        result.end_time = datetime.now()

        msg = notifier.format_error_message(result)

        assert "Error message: legacy error" in msg
        assert "Error code:" not in msg
        assert "Error type:" not in msg
