import re
from abc import ABC, abstractmethod
from datetime import datetime

from stagehand import Stagehand

from automation import config
from automation.base.execution_result import ExecutionResult
from automation.logging_config import create_stagehand_logger, get_logger


class BaseAutomation(ABC):
    """Abstract base class for automation tasks."""

    _registry: dict[str, type["BaseAutomation"]] = {}

    def __init_subclass__(cls, **kwargs):
        """
        Automatically called when a subclass is defined, used for auto-registration.

        Args:
            **kwargs: Other arguments passed to the parent class.

        Examples:
            # Auto-registration using the class name as the task name
            class MyAutomation(BaseAutomation):
                pass

            # Specifying a task name
            class MyAutomation(BaseAutomation, task_name="my_task"):
                pass
        """
        super().__init_subclass__(**kwargs)
        task_name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

        cls._registry[task_name] = cls

    @classmethod
    def get_registry(cls) -> dict[str, type["BaseAutomation"]]:
        """Get all registered automation task classes."""
        return cls._registry.copy()

    @classmethod
    def get_task_class(cls, task_name: str) -> type["BaseAutomation"] | None:
        """Get the class corresponding to a task name."""
        return cls._registry.get(task_name)

    def __init__(self):
        """Initialize the automation task."""
        self.logger = get_logger(self.__class__.__name__)
        self.stagehand: Stagehand | None = None
        self._stagehand_initialized = False

        self.execution_result: ExecutionResult = ExecutionResult(task_name=str(self))

    async def __init_stagehand(self) -> None:
        """Initialize the Stagehand instance."""
        if not self._stagehand_initialized:
            stagehand_logger_func = create_stagehand_logger()

            self.stagehand = Stagehand(
                env="LOCAL",
                model_name=config.LLMConfig.MODEL_NAME,
                model_api_key=config.LLMConfig.MODEL_API_KEY,
                logger=stagehand_logger_func,
                local_browser_launch_options={
                    "headless": config.StagehandConfig.HEADLESS
                },
            )
            await self.stagehand.init()
            self._stagehand_initialized = True

    async def __close_stagehand(self) -> None:
        """Close the Stagehand instance."""
        if self.stagehand and self._stagehand_initialized:
            await self.stagehand.close()
            self._stagehand_initialized = False

    @abstractmethod
    async def automation(self) -> None:
        """Main automation logic (to be implemented by subclasses)."""
        pass

    async def execute(self) -> ExecutionResult:
        """Execute the automation task."""
        try:
            await self.__init_stagehand()
            await self.automation()
        except Exception as e:
            self.logger.error(
                f"Error occurred during task execution: {str(e)}", exc_info=True
            )
            self.execution_result.set_error(e)
        finally:
            self.logger.info("Task execution completed")
            self.execution_result.end_time = datetime.now()
            await self.__close_stagehand()

        return self.execution_result
