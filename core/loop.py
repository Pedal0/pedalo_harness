import json

from providers.base import BaseProvider


class Agent:
    def __init__(self, provider: BaseProvider, system_prompt: str, tools: dict | None = None,
                 on_tool_call=None, on_tool_result=None, on_thinking=None, confirm=None):
        self.provider = provider
        self.tools = tools or {}
        self.messages = [{"role": "system", "content": system_prompt}]
        self.always_allowed = set()

        self.on_tool_call = on_tool_call or self._default_on_tool_call
        self.on_tool_result = on_tool_result or (lambda name, result: None)
        self.on_thinking = on_thinking or (lambda thinking: None)
        self.confirm = confirm or self._default_confirm

    def _default_on_tool_call(self, name: str, arguments: dict):
        print(f"  {name}({json.dumps(arguments, ensure_ascii=False)})")

    def _default_confirm(self, name: str, arguments: dict) -> str:
        return input("  Execute ? [y]es / [n]o / [a]lways : ").strip().lower()

    @property
    def tool_schemas(self) -> list[dict]:
        return [t["schema"] for t in self.tools.values()]

    def run(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})

        while True:
            response = self.provider.chat(self.messages, self.tool_schemas)
            if response.thinking:
                self.on_thinking(response.thinking)

            if not response.tool_calls:
                self.messages.append({"role": "assistant", "content": response.text})
                return response.text

            self.messages.append({
                "role": "assistant",
                "content": response.text,
                "tool_calls": [
                    {"id": tc.id, "function": {"name": tc.name, "arguments": tc.arguments}}
                    for tc in response.tool_calls
                ],
            })

            for tc in response.tool_calls:
                result = self._execute(tc.name, tc.arguments)
                self.on_tool_result(tc.name, result)
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
            self.on_tool_call(name, arguments)

            required_list = tool["schema"]["function"]["parameters"].get("required", [])
            if not arguments and required_list:
                required = ", ".join(required_list)
                return f"Error: tool '{name}' called without arguments. Required parameters: {required}. Retry with all required parameters filled."

            if tool.get("confirm") and name not in self.always_allowed:
                choice = self.confirm(name, arguments)
                if choice == "a":
                    self.always_allowed.add(name)
                elif choice != "y":
                    return "The user denied the execution of this command. Ask them how to proceed instead of retrying the same command."

            return str(tool["run"](**arguments))
        except Exception as e:
            return f"Error executing tool '{name}': {e}"
        

    def estimate_tokens(self) -> int:
        total_chars = 0
        for message in self.messages:
            total_chars += len(json.dumps(message, ensure_ascii=False))
        return total_chars // 4

    @property
    def context_usage(self) -> float:
        return self.estimate_tokens() / self.provider.num_ctx

    def _should_compact(self, threshold: float = 0.75) -> bool:
        return self.context_usage > threshold