"""Pytest configuration and shared fixtures."""

import os
from unittest.mock import AsyncMock, Mock

import pytest


# Set test environment variables
os.environ["MODEL_PROVIDER"] = "anthropic"
os.environ["MODEL_NAME"] = "test-model"
os.environ["MODEL_API_KEY"] = "test-api-key"
os.environ["LOGIN_ACCOUNT"] = "test-account"
os.environ["LOGIN_PASSWORD"] = "test-password"


@pytest.fixture
def mock_config():
    """Provide test configuration."""
    from automation.config import Config

    return Config()


@pytest.fixture
def mock_stagehand_page():
    """Provide mock StagehandPage."""
    page = AsyncMock()
    page.observe = AsyncMock(return_value=[Mock()])
    page.act = AsyncMock()
    page.evaluate = AsyncMock()
    page.expect_download = AsyncMock()
    return page


@pytest.fixture
def temp_test_dir(tmp_path):
    """Provide temporary test directory."""
    return tmp_path
