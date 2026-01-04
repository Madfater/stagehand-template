import importlib
import warnings
from pathlib import Path

from .base_notifier import BaseNotifier


_current_dir = Path(__file__).parent

for file_path in _current_dir.glob("*_notifier.py"):
    if file_path.name == "base_notifier.py":
        continue

    module_name = f".{file_path.stem}"

    try:
        importlib.import_module(module_name, package=__package__)
    except Exception as e:
        warnings.warn(f"Failed to import {module_name}: {e}", stacklevel=2)


__all__ = ["BaseNotifier"]
