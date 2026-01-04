import importlib
import warnings
from pathlib import Path


_current_dir = Path(__file__).parent

for subdir in _current_dir.iterdir():
    if not subdir.is_dir():
        continue

    executor_file = subdir / "main.py"
    if executor_file.exists():
        module_name = f".{subdir.name}.main"
        try:
            importlib.import_module(module_name, package=__package__)
        except Exception as e:
            warnings.warn(f"Failed to import {module_name}: {e}", stacklevel=2)
