"""Stagehand Automation CLI entry point."""

import argparse
import asyncio
import sys
from textwrap import dedent

from .app import AutomationApp
from .logging_config import get_logger


def create_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""
    parser = argparse.ArgumentParser(
        prog="stagehand-automation",
        description="Stagehand automation task execution tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=dedent("""
        Examples:
        # Run an automation task
        python -m automation [task_name]
        """),
    )

    parser.add_argument(
        "task",
        choices=AutomationApp.get_available_tasks(),
        help="Available tasks to execute",
    )

    return parser


async def main() -> int:
    """Main program entry point."""
    logger = get_logger(__name__)
    parser = create_parser()
    args = parser.parse_args()

    app = AutomationApp()

    try:
        success = await app.run_automation(args.task)
        return 0 if success else 1
    except Exception as e:
        logger.error(f"Error occurred while executing task: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
