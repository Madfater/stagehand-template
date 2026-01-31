"""BaseAutomation unit tests."""

from unittest.mock import AsyncMock, patch

import pytest

from automation.base.base_automation import BaseAutomation


# Create concrete test subclass
class ConcreteAutomation(BaseAutomation):
    """Concrete implementation class for testing."""

    async def automation(self) -> None:
        pass


class TestBaseAutomation:
    """Test BaseAutomation."""

    def test_init(self):
        """Test initialization."""
        automation = ConcreteAutomation()

        assert automation.stagehand is None
        assert automation._stagehand_initialized is False
        assert automation.execution_result is not None

    def test_registry(self):
        """Test auto-registration mechanism."""
        registry = BaseAutomation.get_registry()

        # ConcreteAutomation should be auto-registered
        assert "concrete_automation" in registry
        assert registry["concrete_automation"] == ConcreteAutomation

    def test_get_task_class(self):
        """Test getting task class."""
        task_class = BaseAutomation.get_task_class("concrete_automation")
        assert task_class == ConcreteAutomation

    def test_get_task_class_not_found(self):
        """Test getting non-existent task class."""
        task_class = BaseAutomation.get_task_class("non_existent_task")
        assert task_class is None

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """Test successful execution."""
        with patch("automation.base.base_automation.Stagehand") as mock_stagehand_class:
            mock_stagehand = AsyncMock()
            mock_stagehand_class.return_value = mock_stagehand

            automation = ConcreteAutomation()
            result = await automation.execute()

            assert result.success is True
            assert result.error_message is None
            mock_stagehand.init.assert_called_once()
            mock_stagehand.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        """Test execution with error."""
        with patch("automation.base.base_automation.Stagehand") as mock_stagehand_class:
            mock_stagehand = AsyncMock()
            mock_stagehand_class.return_value = mock_stagehand

            class FailingAutomation(BaseAutomation):
                async def automation(self) -> None:
                    raise ValueError("Test error")

            automation = FailingAutomation()
            result = await automation.execute()

            assert result.success is False
            assert "Test error" in result.error_message
            assert result.error_info is not None
            assert result.error_info.error_type == "ValueError"
            assert result.error_info.message == "Test error"
            assert result.error_info.error_code is None
            # Stagehand should be properly closed even on error
            mock_stagehand.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_closes_stagehand_on_exception(self):
        """Test Stagehand is properly closed on exception."""
        with patch("automation.base.base_automation.Stagehand") as mock_stagehand_class:
            mock_stagehand = AsyncMock()
            mock_stagehand_class.return_value = mock_stagehand

            class ExceptionAutomation(BaseAutomation):
                async def automation(self) -> None:
                    raise RuntimeError("Runtime error")

            automation = ExceptionAutomation()
            result = await automation.execute()

            # close should be called even on exception
            mock_stagehand.close.assert_called_once()
            assert result.success is False

    def test_cannot_instantiate_base_class(self):
        """Test cannot directly instantiate BaseAutomation."""
        with pytest.raises(TypeError):
            BaseAutomation()  # type: ignore
