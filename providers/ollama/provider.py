import requests

from providers.base import BaseProvider, ModelResponse, ToolCall


class OllamaProvider(BaseProvider):
    def __init__(self, model: str, host: str, num_ctx: int = 8192):
        self.model = model
        self.host = host
        self.num_ctx = num_ctx

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> ModelResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"num_ctx": self.num_ctx},
        }
        if tools:
            payload["tools"] = tools

        resp = requests.post(f"{self.host}/api/chat", json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()

        return self._normalize(data)

    def _normalize(self, data: dict) -> ModelResponse:
        message = data.get("message", {})

        tool_calls = []
        for i, tc in enumerate(message.get("tool_calls", []) or []):
            fn = tc.get("function", {})
            tool_calls.append(ToolCall(
                id=tc.get("id", f"tool_call_{i}"),
                name=fn.get("name", ""),
                arguments=fn.get("arguments", {}),
            ))

        return ModelResponse(
            text=message.get("content", "") or "",
            tool_calls=tool_calls,
        )