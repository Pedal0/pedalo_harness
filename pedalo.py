from providers.registry import load_provider_config
from providers.ollama.provider import OllamaProvider
from prompts.loader import load_prompt
from core.loop import Agent
from tools.loader import load_tools
from skills.loader import load_skills, format_skills_prompt
from ui.app import PedaloApp


def main():
    config = load_provider_config("ollama")
    provider = OllamaProvider(model=config["default"], host=config["host"],
                              num_ctx=config["num_ctx"])
    skills = load_skills()
    system_prompt = load_prompt("system", "default") + format_skills_prompt(skills)
    agent = Agent(provider, system_prompt, load_tools())
    PedaloApp(agent, skills).run()


if __name__ == "__main__":
    main()