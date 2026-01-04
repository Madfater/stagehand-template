import logging
import logging.handlers
from pathlib import Path
from typing import Any

from .config import LoggingConfig
from .config import config as global_config


class LoggingManager:
    """Logging manager for centralized log configuration."""

    _initialized = False
    _loggers = {}

    @classmethod
    def setup_logging(
        cls, config: LoggingConfig | None = None, force: bool = False
    ) -> None:
        """
        Configure the logging system.

        Args:
            config: Logging configuration. Uses default if not provided.
            force: Whether to force reinitialization even if already initialized.
        """
        if cls._initialized and not force:
            return

        if config is None:
            config = global_config.logging

        root_logger = logging.getLogger()
        root_logger.setLevel(cls._get_log_level(config.LEVEL))

        root_logger.handlers.clear()

        formatter = logging.Formatter(fmt=config.FORMAT, datefmt=config.DATE_FORMAT)

        if config.CONSOLE_ENABLED:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(cls._get_log_level(config.CONSOLE_LEVEL))
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

        if config.FILE_ENABLED:
            log_path = Path(config.FILE_PATH)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.handlers.RotatingFileHandler(
                filename=config.FILE_PATH,
                maxBytes=config.FILE_MAX_BYTES,
                backupCount=config.FILE_BACKUP_COUNT,
                encoding="utf-8",
            )
            file_handler.setLevel(cls._get_log_level(config.FILE_LEVEL))
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)

        # Set module-level logging
        for module_name, level in config.MODULE_LEVELS.items():
            module_logger = logging.getLogger(module_name)
            module_logger.setLevel(cls._get_log_level(level))

        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Get a logger with the specified name.

        Args:
            name: Logger name (typically the module name).

        Returns:
            Logger instance.
        """
        if name not in cls._loggers:
            if not cls._initialized:
                cls.setup_logging()

            cls._loggers[name] = logging.getLogger(name)

        return cls._loggers[name]

    @staticmethod
    def _get_log_level(level_str: str) -> int:
        """
        Convert a string to a logging level.

        Args:
            level_str: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).

        Returns:
            Logging level constant.
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(level_str.upper(), logging.INFO)

    @classmethod
    def reset(cls) -> None:
        """Reset the logging system (primarily for testing)."""
        cls._initialized = False
        cls._loggers.clear()
        root_logger = logging.getLogger()
        root_logger.handlers.clear()


def setup_logging(config: LoggingConfig | None = None, force: bool = False) -> None:
    """
    Convenience function to configure the logging system.

    Args:
        config: Logging configuration.
        force: Whether to force reinitialization.
    """
    LoggingManager.setup_logging(config=config, force=force)


def get_logger(name: str) -> logging.Logger:
    """
    Convenience function to get a logger.

    Args:
        name: Logger name.

    Returns:
        Logger instance.

    Example:
        >>> logger = get_logger(__class__.__name__)
        >>> logger.info("This is a log message")
    """
    return LoggingManager.get_logger(name)


def create_stagehand_logger():
    """
    Create a Stagehand-specific logger function.

    Forwards Stagehand log output to the Python logging system.

    Returns:
        A logger function suitable for Stagehand.

    Example:
        >>> from automation.logging_config import (
        ...     get_logger,
        ...     create_stagehand_logger,
        ... )
        >>> logger = get_logger(__class__.__name__)
        >>> stagehand_logger = create_stagehand_logger()
        >>> # Pass to Stagehand initialization
        >>> stagehand = Stagehand(..., logger=stagehand_logger)
    """
    logger = LoggingManager.get_logger("Stagehand")

    def stagehand_logger_func(log_data: dict[str, Any]) -> None:
        """Stagehand custom logger function."""
        try:
            category = log_data.get("category", "stagehand")
            data: dict = log_data.get("message")
            message = data.get("message", "")
            level = data.get("level", 1)

            if level == 0:
                logger.error(f"[{category}] {message}")
            elif level == 1:
                logger.info(f"[{category}] {message}")
            else:
                logger.debug(f"[{category}] {message}")
        except Exception as e:
            logger.warning(f"Stagehand logger parsing failed: {e}, log_data={log_data}")

    return stagehand_logger_func
