# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a web automation template based on Stagehand (Playwright), providing a complete project structure and commonly used functional modules.

### Core Features
- **Automation Framework**: Web automation infrastructure based on Stagehand
- **Auto Task Registration**: Inheriting `BaseAutomation` automatically registers as an executable task
- **Notification System**: Supports LINE Bot and Email notifications
- **Logging System**: Complete logging with console and file output support
- **Configuration Management**: Type-safe configuration system using dataclass

## Development Environment Setup

### Package Management
This project uses **uv** as the package manager:

```bash
# Install dependencies
uv sync

# Add a package
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Run CLI mode
uv run python -m automation [task_name]

# Run tests
uv run pytest
```

### Required Environment Variables
Copy `.env.example` to `.env` and fill in the actual values:

```bash
cp .env.example .env
```

Set the following environment variables in the `.env` file:

```env
# Login settings (required)
LOGIN_ACCOUNT=your-account
LOGIN_PASSWORD=your-password

# LLM settings (required)
MODEL_PROVIDER=anthropic  # or gemini
MODEL_NAME=claude-haiku-4-5-20251001
MODEL_API_KEY=your-api-key

# Notification system (optional)
ENABLED_NOTIFIERS=line,email

# Logging settings (optional)
LOG_LEVEL=INFO
LOG_CONSOLE_ENABLED=true
LOG_FILE_ENABLED=true
```

### Code Formatting
```bash
# Check code
uv run ruff check

# Auto fix
uv run ruff check --fix

# Format code
uv run ruff format
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=automation --cov-report=html
```

## Core Architecture

### Project Structure
```
stagehand-automation-template/
├── automation/
│   ├── __init__.py
│   ├── __main__.py              # CLI entry point
│   ├── app.py                   # AutomationApp main class
│   ├── config.py                # Configuration management
│   ├── exceptions.py            # Exception classes
│   ├── logging_config.py        # Logging configuration
│   │
│   ├── automations/             # Automation tasks directory
│   │   └── __init__.py          # Auto-load all tasks
│   │
│   ├── base/                    # Base classes
│   │   ├── __init__.py
│   │   ├── base_automation.py   # Automation task base class
│   │   ├── base_task.py         # Task base class
│   │   └── execution_result.py  # Execution result class
│   │
│   ├── helper/                  # Helper utilities
│   │   ├── __init__.py
│   │   └── stagehand_helper.py
│   │
│   └── notification/            # Notification system
│       ├── __init__.py
│       ├── notification_manager.py
│       └── notifiers/
│           ├── __init__.py
│           ├── base_notifier.py
│           ├── line_notifier.py
│           └── email_notifier.py
│
├── tests/                       # Test files
├── tmp/                         # Temporary files
├── logs/                        # Log files
└── credentials/                 # Credentials directory
```

### Module Responsibility Separation

#### 1. Application Core (`app.py`)
- **AutomationApp** class: Main application entry point
  - `run_automation(task_name)`: Execute a specified automation task
  - `get_available_tasks()`: Get list of all available tasks
  - Integrated notification system
  - Unified error handling and logging

#### 2. Configuration Management System (`config.py`)
Type-safe configuration management using dataclass:
- **LLMConfig**: LLM (Claude/Gemini) configuration
- **LineConfig**: LINE Bot configuration
- **EmailConfig**: Email notification configuration
- **LoginConfig**: Login configuration
- **PathConfig**: File path configuration (automatically creates required directories)
- **StagehandConfig**: Stagehand framework configuration
- **LoggingConfig**: Logging system configuration
- **Config**: Unified configuration entry point with validation

#### 3. Automation Task Module (`automations/`)

##### BaseAutomation
Base class for all automation tasks, providing:
- Stagehand instance management and initialization
- Unified error handling
- Execution result recording

After inheriting, just implement the `automation()` method:
```python
from automation.base import BaseAutomation


class MyTask(BaseAutomation):
    async def automation(self) -> None:
        page = self.stagehand.page
        await page.goto("https://example.com")
        await page.act("Click the button")
```

#### 4. Notification System (`notification/`)

Designed with **auto-registration mechanism**:

##### BaseNotifier
Notifier base class, defining a unified interface:
- `is_enabled()`: Check if enabled
- `send_notification(result)`: Send notification

##### NotificationManager
Manages all notifiers:
- Automatically discovers and registers all notifiers
- Enables/disables notifiers based on configuration
- Unified notification sending interface

#### 5. Logging System (`logging_config.py`)
Advanced logging configuration system:
- Supports dual output to console and file
- Automatic file log rotation (RotatingFileHandler)
- Module-level log control (reduces third-party package log noise)
- Unified log format

## Key Technical Implementation Details

### Anthropic API Structured Output
**Important**: Anthropic API **does not support** the `response_format` parameter.

The correct approach is to use **Tool Use (Function Calling)**:

```python
tools = [{
    "name": "tool_name",
    "description": "...",
    "input_schema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}]

message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    tools=tools,
    tool_choice={"type": "tool", "name": "tool_name"},
    ...
)

# Extract result from tool_use content block
for content in message.content:
    if content.type == "tool_use":
        result = content.input
```

### Playwright Python API Naming Convention
Playwright's Python API uses **snake_case**, not JavaScript's camelCase:

```python
# Correct
await context.set_extra_http_headers({"Authorization": token})

# Wrong (JavaScript style)
await context.setExtraHTTPHeaders({"Authorization": token})
```

### Stagehand Specific Import
`StagehandContext` is not in the top-level package, needs to be imported from submodule:

```python
from stagehand import Stagehand, StagehandPage
from stagehand.context import StagehandContext  # Note this line
```

## Key Design Patterns

### 1. Auto-Registration Pattern
Using `__init_subclass__` to implement auto-registration of tasks and notifiers:
```python
class BaseAutomation(ABC):
    _registry: dict[str, type["BaseAutomation"]] = {}

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        task_name = re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
        cls._registry[task_name] = cls
```

### 2. Template Method Pattern
Defining automation flow skeleton in BaseAutomation:
```python
class BaseAutomation:
    async def execute(self):
        try:
            await self.__init_stagehand()
            await self.automation()  # Implemented by subclass
        finally:
            await self.__close_stagehand()
```

### 3. Unified Configuration Management
Using dataclass and environment variables:
```python
from automation.config import config

# Using configuration
account = config.login.ACCOUNT
api_key = config.llm.MODEL_API_KEY
```

### 4. Logging Best Practices
```python
from automation.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Task started")
logger.error("Error occurred", exc_info=True)
```

## Adding Automation Tasks

1. Create a new subdirectory under `automation/automations/`
2. Create a `main.py` file
3. Inherit from `BaseAutomation` class
4. Implement the `automation()` method

Example:
```python
# automation/automations/my_task/main.py
from automation.base import BaseAutomation


class MyTask(BaseAutomation):
    """My automation task."""
    async def automation(self) -> None:
        page = self.stagehand.page

        # Navigate to target page
        await page.goto("https://example.com")

        # Use natural language to describe actions
        await page.act("Click the login button")
        await page.act("Enter user@example.com in the account field")

        # Observe page elements
        result = await page.observe("Get all product names")

        # Record execution result
        self.execution_result.add_detail("Product count", len(result))
```

## Adding Notifiers

1. Create a new notifier under `automation/notification/notifiers/`
2. Inherit from `BaseNotifier` class
3. Implement `is_enabled()` and `send_notification()` methods

Example:
```python
# automation/notification/notifiers/slack_notifier.py
from automation.notification.notifiers.base_notifier import BaseNotifier


class SlackNotifier(BaseNotifier):
    """Slack notifier."""

    def is_enabled(self) -> bool:
        return "slack" in config.notification.ENABLED_NOTIFIERS

    def send_notification(self, result) -> bool:
        # Implement Slack notification logic
        pass
```

## Code Style

- Use Ruff for code formatting and linting
- Use docstrings for functions and methods (Google style)
- Type hints (Type Hints)
- Code comments in English
- Keep technical terms in English
