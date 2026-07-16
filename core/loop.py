import json
from unicodedata import name

from providers.base import BaseProvider

class Agent:
    def __init__(self, provider: BaseProvider, system_prompt: str, tools: dict | None = None):
        self.provider = provider
        self.tools = tools or {}
        self.messages = [{"role": "system", "content": system_prompt}]
        self.always_allowed = set()

    @property
    def tool_schema(self) -> list[dict]:
        return [t["schema"] for t in self.tools.values()]
    
    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        while True:
            response = self.provider.chat(self.messages, self.tool_schema)

            if not response.tool_calls:
                self.messages.append({"role": "assistant", "content": response.text})
                return response.text
            
            self.messages.append({
                "role": "assistant",
                "content": response.text,
                "tool_calls":  [
                    {"id": tc.id, "function": {tc.name: tc.arguments}} 
                    for tc in response.tool_calls
                ]
            })

            for tc in response.tool_calls:
                result = self._execute(tc.name, tc.arguments)
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })

    def _execute(self, name: str, arguments: dict) -> str:
        tool = self.tools.get(name)
        if tool is None:
            return f"Error: tool '{name}' does not exist. Available tools: {', '.join(self.tools)}"

        try:
            print(f"{name}({json.dumps(arguments, ensure_ascii=False)})")

            required_list = tool["schema"]["function"]["parameters"].get("required", [])
            if not arguments and required_list:
                required = ", ".join(required_list)
                return f"Error: tool '{name}' called without arguments. Required parameters: {required}. Retry with all required parameters filled."

            if tool.get("confirm") and name not in self.always_allowed:
                choice = input(" Execute ? [y]es / [n]o / [a]lways : ").strip().lower()
                if choice == "a":
                    self.always_allowed.add(name)
                elif choice != "y":
                    return "The user denied the execution of this command. Ask them how to proceed instead of retrying the same command."

            return str(tool["run"](**arguments))
        except Exception as e:
            return f"Error executing tool '{name}': {e}"


            