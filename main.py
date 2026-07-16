from providers.registry import load_provider_config
from providers.ollama.provider import OllamaProvider
from prompts.loader import load_prompt
from core.loop import Agent
from tools.loader import load_tools
from skills.loader import load_skills, format_skills_prompt


def main():
    config = load_provider_config("ollama")
    provider = OllamaProvider(
        model=config["default"],
        host=config["host"],
        num_ctx=config["num_ctx"]
    )
    skills = load_skills()
    system_prompt = load_prompt("system", "default") + format_skills_prompt(skills)
    tools = load_tools()
    agent = Agent(provider, system_prompt, tools)

    print(f"Harness v0 modèle : {provider.model} | {len(tools)} tools : {', '.join(tools)}  | {len(skills)} skills : {', '.join([skill['name'] for skill in skills])} | 'exit' pour quitter.\n")
    while True:
        try:
            user_input = input("vous > ").strip()
        except (KeyboardInterrupt, EOFError):
            break
        if user_input.lower() in ("exit", "quit"):
            break
        if not user_input:
            continue

        answer = agent.run(user_input)
        print(f"\nagent > {answer}\n")


if __name__ == "__main__":
    main()