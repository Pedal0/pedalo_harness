import importlib
from pathlib import Path

BUILTIN_DIR = Path(__file__).parent / "builtin"


def load_tools() -> dict:
    tools = {}

    for file in BUILTIN_DIR.glob("*.py"):
        if file.stem.startswith("_"):
            continue
        module = importlib.import_module(f"tools.builtin.{file.stem}")

        if not hasattr(module, "SCHEMA") or not hasattr(module, "run"):
            print(f"{file.name} ignored: missing SCHEMA or run function")
            continue

        name = module.SCHEMA["function"]["name"]
        tools[name] = {
            "schema": module.SCHEMA, 
            "run": module.run, 
            "confirm": getattr(module, "REQUIRES_CONFIRMATION", False)
        }

    return tools