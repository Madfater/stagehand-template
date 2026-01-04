# Stagehand Automation Template

A web automation framework template based on [Stagehand](https://github.com/browserbase/stagehand), providing a complete project structure and commonly used functional modules.

## Features

- **Automation Framework**: Web automation infrastructure based on Stagehand (Playwright)
- **Auto Task Registration**: Inheriting `BaseAutomation` automatically registers as an executable task
- **Notification System**: Supports LINE Bot and Email notifications
- **Logging System**: Complete logging with console and file output support
- **Configuration Management**: Type-safe configuration system using dataclass
- **CLI Interface**: Command-line execution of automation tasks

## Quick Start

### Install Dependencies

This project uses [uv](https://github.com/astral-sh/uv) as the package manager:

```bash
uv sync
```

### Set Environment Variables

```bash
cp .env.example .env
# Edit .env and fill in actual values
```

Required environment variables:
- `LOGIN_ACCOUNT` / `LOGIN_PASSWORD`: Target system login credentials
- `MODEL_PROVIDER` / `MODEL_NAME` / `MODEL_API_KEY`: LLM settings

### Run Task

```bash
# Run a task
uv run python -m automation <task_name>

# Run the example
uv run python -m automation example
```

## Tutorial

### Architecture Overview

| Class | Purpose | Use Case |
|-------|---------|----------|
| `BaseAutomation` | Main automation entry point | Complete automation workflows |
| `BaseTask` | Reusable sub-tasks with retry | Individual operations (login, extract, etc.) |
| `StagehandHelper` | Common page operations | Form filling, button clicking |

### Example

See the complete working example:

- **[automation/automations/example/main.py](automation/automations/example/main.py)** - Main automation using `BaseAutomation`
- **[automation/automations/example/tasks.py](automation/automations/example/tasks.py)** - Login task using `BaseTask` and `StagehandHelper`

### Creating Your Own Automation

**Step 1**: Create a directory under `automation/automations/`:

```bash
mkdir -p automation/automations/my_task
```

**Step 2**: Create `main.py` with a class inheriting `BaseAutomation`:

```python
# automation/automations/my_task/main.py
from automation.base import BaseAutomation


class MyTask(BaseAutomation):
    async def automation(self) -> None:
        page = self.stagehand.page
        await page.goto("https://example.com")
        await page.act("Click the login button")
```

**Step 3**: Run your automation:

```bash
uv run python -m automation my_task
```

> **Note**: Task name is derived from class name: `MyTask` → `my_task`

### BaseTask Configuration

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | StagehandPage | Stagehand page object (required) |
| `max_retries` | int | Maximum retry attempts (required) |
| `retry_delay` | float | Seconds between retries (default: 1.0) |
| `retry_on_exceptions` | tuple | Exception types to retry (default: all) |

### StagehandHelper Methods

| Method | Description |
|--------|-------------|
| `type_into_field(field_name, text)` | Fill text into an input field |
| `click_the_button(label)` | Click a button by label |

See implementation: **[automation/helper/stagehand_helper.py](automation/helper/stagehand_helper.py)**

## Project Structure

```
automation/
├── __main__.py              # CLI entry point
├── app.py                   # AutomationApp main class
├── config.py                # Configuration management
├── automations/             # Your automation tasks
│   └── example/             # Example automation
│       ├── main.py
│       └── tasks.py
├── base/                    # Base classes
│   ├── base_automation.py
│   ├── base_task.py
│   └── execution_result.py
├── helper/                  # Helper utilities
│   └── stagehand_helper.py
└── notification/            # Notification system
    └── notifiers/
```

## Core Modules

### Configuration

```python
from automation.config import config

account = config.login.ACCOUNT
api_key = config.llm.MODEL_API_KEY
```

### Notification System

Enable in `.env`:
```
ENABLED_NOTIFIERS=line,email
```

## Development

```bash
# Run tests
uv run pytest

# Code formatting
uv run ruff check --fix
uv run ruff format
```

## License

MIT License
