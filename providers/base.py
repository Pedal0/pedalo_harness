from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class ModelResponse:
    text: str = ""
    thinking: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)


class BaseProvider(ABC):
    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> ModelResponse:
        pass