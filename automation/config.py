import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from .exceptions import ConfigurationError


load_dotenv()


@dataclass
class LLMConfig:
    """LLM configuration."""

    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER")
    MODEL_NAME: str = os.getenv("MODEL_NAME")
    MODEL_API_KEY: str = os.getenv("MODEL_API_KEY")


@dataclass
class LineConfig:
    """LINE Bot configuration."""

    CHANNEL_ACCESS_TOKEN: str = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "")
    CHANNEL_SECRET: str = os.getenv("LINE_CHANNEL_SECRET", "")
    GROUP_ID: str = os.getenv("LINE_GROUP_ID", "")
    TARGET_IDS: list[str] = field(
        default_factory=lambda: (
            [
                target_id.strip()
                for target_id in os.getenv("LINE_TARGET_IDS", "").split(",")
                if target_id.strip()
            ]
        )
    )

@dataclass
class PathConfig:
    """File path configuration."""

    TMP_DIR: Path = Path("./tmp")
    LOGS_DIR: Path = Path("./logs")

    def __post_init__(self):
        """Automatically create required directories."""
        for path in [
            self.TMP_DIR,
            self.LOGS_DIR,
        ]:
            path.mkdir(exist_ok=True)


@dataclass
class StagehandConfig:
    """Stagehand automation framework configuration."""

    # Enable headless mode (true = headless, false = show browser)
    HEADLESS: bool = os.getenv("STAGEHAND_HEADLESS", "true").lower() == "true"


@dataclass
class LoggingConfig:
    """Logging configuration."""

    # Log level
    LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Console logging
    CONSOLE_ENABLED: bool = os.getenv("LOG_CONSOLE_ENABLED", "true").lower() == "true"
    CONSOLE_LEVEL: str = os.getenv("LOG_CONSOLE_LEVEL", "INFO")

    # File logging
    FILE_ENABLED: bool = os.getenv("LOG_FILE_ENABLED", "true").lower() == "true"
    FILE_LEVEL: str = os.getenv("LOG_FILE_LEVEL", "DEBUG")
    FILE_PATH: str = os.getenv("LOG_FILE_PATH", "./logs/automation.log")
    FILE_MAX_BYTES: int = int(
        os.getenv("LOG_FILE_MAX_BYTES", str(10 * 1024 * 1024))
    )  # 10MB
    FILE_BACKUP_COUNT: int = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

    # Log format
    FORMAT: str = os.getenv(
        "LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    DATE_FORMAT: str = os.getenv("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

    # Module-level logging
    MODULE_LEVELS: dict = field(
        default_factory=lambda: {
            "stagehand": os.getenv("LOG_LEVEL_STAGEHAND", "WARNING"),
            "playwright": os.getenv("LOG_LEVEL_PLAYWRIGHT", "WARNING"),
            "urllib3": os.getenv("LOG_LEVEL_URLLIB3", "WARNING"),
            "googleapiclient": os.getenv("LOG_LEVEL_GOOGLEAPICLIENT", "WARNING"),
            "LiteLLM": os.getenv(
                "LOG_LEVEL_LITELLM", "WARNING"
            ),  # Disable LiteLLM logging
        }
    )


@dataclass
class NotificationConfig:
    """Notification system configuration."""

    # Enabled notifiers list (comma-separated)
    ENABLED_NOTIFIERS: list[str] = field(
        default_factory=lambda: [
            notifier.strip().lower()
            for notifier in os.getenv("ENABLED_NOTIFIERS", "").split(",")
            if notifier.strip()
        ]
    )


@dataclass
class EmailConfig:
    """Email notification configuration."""

    SMTP_HOST: str = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("EMAIL_SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("EMAIL_SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("EMAIL_SMTP_PASSWORD", "")
    DEFAULT_RECIPIENTS: list[str] = field(
        default_factory=lambda: [
            email.strip()
            for email in os.getenv("EMAIL_DEFAULT_RECIPIENTS", "").split(",")
            if email.strip()
        ]
    )
    USE_TLS: bool = os.getenv("EMAIL_USE_TLS", "true").lower() == "true"


@dataclass
class Config:
    """Unified configuration entry point."""

    llm: LLMConfig = field(default_factory=LLMConfig)
    line: LineConfig = field(default_factory=LineConfig)
    notification: NotificationConfig = field(default_factory=NotificationConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    stagehand: StagehandConfig = field(default_factory=StagehandConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def __post_init__(self):
        """Automatically validate configuration after initialization."""
        self.validate()

    def validate(self):
        """Validate required configuration."""
        if (
            not self.llm.MODEL_PROVIDER
            or not self.llm.MODEL_NAME
            or not self.llm.MODEL_API_KEY
        ):
            raise ConfigurationError(
                "LLM environment variables not set: "
                "MODEL_PROVIDER, MODEL_NAME, MODEL_API_KEY"
            )
        if not self.login.ACCOUNT or not self.login.PASSWORD:
            raise ConfigurationError(
                "Login environment variables not set: LOGIN_ACCOUNT, LOGIN_PASSWORD"
            )


config = Config()
