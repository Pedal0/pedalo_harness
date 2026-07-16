import json
from pathlib import Path

PROVIDERS_DIR = Path(__file__).parent


def load_provider_config(provider_name: str) -> dict:
    config_path = PROVIDERS_DIR / provider_name / "models.json"
    if not config_path.exists():
        raise FileNotFoundError(f"No configuration for '{provider_name}' ({config_path})")
    return json.loads(config_path.read_text(encoding="utf-8"))