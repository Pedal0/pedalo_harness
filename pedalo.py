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
                              num_ctx=config["num_ctx"],
                              think=config.get("think", False))
    skills = load_skills()

    environment = load_prompt("system", "environment").format(
        os=platform.system(),
        shell="PowerShell" if platform.system() == "Windows" else "bash",
        project_root=project_root,
    )

    system_prompt = "\n\n".join([
        load_prompt("system", "default"),
        environment,
        load_prompt("system", "brain"),
        format_skills_prompt(skills),
    ])

    agent = Agent(provider, system_prompt, load_tools())
    PedaloApp(agent, skills, project_root).run()


if __name__ == "__main__":
    main()