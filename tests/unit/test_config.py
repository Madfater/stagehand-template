"""Test configuration module."""

from automation.config import Config, PathConfig


def test_config_initialization():
    """Test configuration initialization."""
    config = Config()
    assert config.llm is not None
    assert config.paths is not None
    assert config.line is not None
    assert config.login is not None


def test_path_config_creates_directories():
    """Test path configuration automatically creates directories."""
    path_config = PathConfig()
    assert path_config.TMP_DIR.exists()
    assert path_config.LOGS_DIR.exists()
    assert path_config.DOWNLOADS_DIR.exists()
    assert path_config.EXPORTS_DIR.exists()
    assert path_config.CREDENTIALS_DIR.exists()


def test_stagehand_config_default_values():
    """Test Stagehand configuration default values."""
    from automation.config import StagehandConfig

    config = StagehandConfig()
    # Default is headless mode
    assert config.HEADLESS is True
