from pathlib import Path

PROMPTS_DIR = Path(__file__).parent


def load_prompt(category: str, name: str) -> str:
    prompt_path = PROMPTS_DIR / category / f"{name}.md"
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")