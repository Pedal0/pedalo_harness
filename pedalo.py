import platform
from pathlib import Path

from providers.registry import load_provider_config
from providers.ollama.provider import OllamaProvider
from prompts.loader import load_prompt
from core.loop import Agent
from tools.loader import load_tools
from skills.loader import load_skills, format_skills_prompt
from brain.scanner import ensure_brain
from ui.app import PedaloApp


def main():
    project_root = Path.cwd()
    ensure_brain(project_root)

    config = load_provider_config("ollama")
    provider = OllamaProvider(model=config["default"], host=config["host"],
                              num_ctx=config["num_ctx"])
    skills = load_skills()

    shell = "PowerShell" if platform.system() == "Windows" else "bash"
    environment = (
        f"\n\n# Environment\n\n"
        f"OS: {platform.system()}. Shell: {shell}.\n"
        f"Project root (working directory): {project_root}\n"
    )
    brain_section = (
        "\n# Project memory\n\n"
        "Your memory of this project lives in the .pedalo/ folder:\n"
        "- .pedalo/MAP.md — project structure. Read it at the start of a task.\n"
        "- .pedalo/lessons.md — past problems and their solutions.\n"
        "- .pedalo/decisions.md — decisions made on this project.\n"
        "- .pedalo/state.md — current task state.\n"
        "When you explore a file not yet described in MAP.md, append a one-line "
        "description to its line using edit_file. When an approach fails and "
        "another succeeds, record it as one line in lessons.md.\n"
    )

    system_prompt = (
        load_prompt("system", "default")
        + environment
        + brain_section
        + format_skills_prompt(skills)
    )

    agent = Agent(provider, system_prompt, load_tools())
    PedaloApp(agent, skills).run()


if __name__ == "__main__":
    main()