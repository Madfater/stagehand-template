"""Logging configuration module unit tests."""

import logging
from pathlib import Path

from automation.config import LoggingConfig
from automation.logging_config import (
    LoggingManager,
    get_logger,
    setup_logging,
)


class TestLoggingConfig:
    """Test LoggingConfig."""

    def test_default_values(self):
        """Test default configuration values."""
        config = LoggingConfig()

        assert config.LEVEL == "INFO"
        assert config.CONSOLE_ENABLED is True
        assert config.CONSOLE_LEVEL == "INFO"
        assert config.FILE_ENABLED is True
        assert config.FILE_LEVEL == "DEBUG"
        assert config.FILE_PATH == "./logs/automation.log"
        assert config.FILE_MAX_BYTES == 10 * 1024 * 1024  # 10MB
        assert config.FILE_BACKUP_COUNT == 5
        assert "stagehand" in config.MODULE_LEVELS
        assert "playwright" in config.MODULE_LEVELS

    def test_config_custom_values(self):
        """Test custom configuration values."""
        # Since dataclass default values are evaluated at class definition,
        # we test that the config object can be used correctly
        config = LoggingConfig()

        # Test that config values can be modified
        config.LEVEL = "DEBUG"
        config.CONSOLE_LEVEL = "WARNING"
        config.FILE_ENABLED = False

        assert config.LEVEL == "DEBUG"
        assert config.CONSOLE_LEVEL == "WARNING"
        assert config.FILE_ENABLED is False


class TestLoggingManager:
    """Test LoggingManager."""

    def setup_method(self):
        """Reset logging system before each test."""
        LoggingManager.reset()

    def teardown_method(self):
        """Clean up after each test."""
        LoggingManager.reset()

    def test_setup_logging_basic(self):
        """Test basic logging setup."""
        config = LoggingConfig()
        config.FILE_ENABLED = False  # Disable file logging to simplify test

        LoggingManager.setup_logging(config)

        assert LoggingManager._initialized is True
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_setup_logging_with_console(self):
        """Test console logging."""
        config = LoggingConfig()
        config.FILE_ENABLED = False
        config.CONSOLE_ENABLED = True
        config.CONSOLE_LEVEL = "DEBUG"

        LoggingManager.setup_logging(config)

        root_logger = logging.getLogger()
        # Should have a StreamHandler
        handlers = [
            h for h in root_logger.handlers if isinstance(h, logging.StreamHandler)
        ]
        assert len(handlers) > 0
        assert handlers[0].level == logging.DEBUG

    def test_setup_logging_with_file(self, tmp_path):
        """Test file logging."""
        log_file = tmp_path / "test.log"
        config = LoggingConfig()
        config.FILE_ENABLED = True
        config.FILE_PATH = str(log_file)
        config.FILE_LEVEL = "WARNING"
        config.CONSOLE_ENABLED = False

        LoggingManager.setup_logging(config)

        root_logger = logging.getLogger()
        # Should have a RotatingFileHandler
        handlers = [
            h
            for h in root_logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(handlers) > 0
        assert handlers[0].level == logging.WARNING
        assert Path(log_file).parent.exists()

    def test_setup_logging_only_once(self):
        """Test logging is only initialized once."""
        config = LoggingConfig()
        config.FILE_ENABLED = False

        LoggingManager.setup_logging(config)
        root_logger = logging.getLogger()
        handler_count_1 = len(root_logger.handlers)

        # Second call should not add handlers
        LoggingManager.setup_logging(config)
        handler_count_2 = len(root_logger.handlers)

        assert handler_count_1 == handler_count_2

    def test_setup_logging_force_reinit(self):
        """Test force reinitialization."""
        config = LoggingConfig()
        config.FILE_ENABLED = False

        LoggingManager.setup_logging(config)
        assert LoggingManager._initialized is True

        # Force reinitialization
        LoggingManager.setup_logging(config, force=True)
        assert LoggingManager._initialized is True

    def test_get_logger(self):
        """Test getting logger."""
        config = LoggingConfig()
        config.FILE_ENABLED = False

        LoggingManager.setup_logging(config)
        logger = LoggingManager.get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_auto_init(self):
        """Test auto initialization."""
        # Don't call setup_logging first
        logger = LoggingManager.get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert LoggingManager._initialized is True

    def test_get_logger_cached(self):
        """Test logger caching."""
        logger1 = LoggingManager.get_logger("test_module")
        logger2 = LoggingManager.get_logger("test_module")

        assert logger1 is logger2

    def test_module_level_logging(self):
        """Test module-level logging."""
        config = LoggingConfig()
        config.FILE_ENABLED = False
        config.MODULE_LEVELS = {
            "test_module_1": "DEBUG",
            "test_module_2": "ERROR",
        }

        LoggingManager.setup_logging(config)

        logger1 = logging.getLogger("test_module_1")
        logger2 = logging.getLogger("test_module_2")

        assert logger1.level == logging.DEBUG
        assert logger2.level == logging.ERROR

    def test_get_log_level(self):
        """Test log level conversion."""
        assert LoggingManager._get_log_level("DEBUG") == logging.DEBUG
        assert LoggingManager._get_log_level("INFO") == logging.INFO
        assert LoggingManager._get_log_level("WARNING") == logging.WARNING
        assert LoggingManager._get_log_level("ERROR") == logging.ERROR
        assert LoggingManager._get_log_level("CRITICAL") == logging.CRITICAL

        # Case insensitive
        assert LoggingManager._get_log_level("debug") == logging.DEBUG

        # Invalid level returns INFO
        assert LoggingManager._get_log_level("INVALID") == logging.INFO

    def test_reset(self):
        """Test resetting logging system."""
        config = LoggingConfig()
        config.FILE_ENABLED = False

        LoggingManager.setup_logging(config)
        LoggingManager.get_logger("test")

        assert LoggingManager._initialized is True
        assert len(LoggingManager._loggers) > 0

        LoggingManager.reset()

        assert LoggingManager._initialized is False
        assert len(LoggingManager._loggers) == 0


class TestConvenienceFunctions:
    """Test convenience functions."""

    def setup_method(self):
        """Reset before each test."""
        LoggingManager.reset()

    def teardown_method(self):
        """Clean up after each test."""
        LoggingManager.reset()

    def test_setup_logging_function(self):
        """Test setup_logging function."""
        config = LoggingConfig()
        config.FILE_ENABLED = False

        setup_logging(config)

        assert LoggingManager._initialized is True

    def test_get_logger_function(self):
        """Test get_logger function."""
        logger = get_logger("test_module")

        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_logging_workflow(self, tmp_path):
        """Test complete logging workflow."""
        log_file = tmp_path / "workflow.log"

        # Set up logging
        config = LoggingConfig()
        config.FILE_ENABLED = True
        config.FILE_PATH = str(log_file)
        config.CONSOLE_ENABLED = False

        setup_logging(config)

        # Get logger and log a message
        logger = get_logger("test_workflow")
        logger.info("Test message")

        # Confirm log file was created
        assert log_file.exists()

        # Read log file to confirm content
        log_content = log_file.read_text(encoding="utf-8")
        assert "Test message" in log_content
        assert "test_workflow" in log_content
