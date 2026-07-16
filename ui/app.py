import json
import threading
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Collapsible, Input, Markdown, Static
from textual.suggester import SuggestFromList

from ui.lake import Lake
from ui.confirm import ConfirmScreen

BANNER = """[b cyan]  ⛵ P E D A L O[/b cyan]  [dim] local harness[/dim]
[dim]provider:[/dim] {provider}   [dim]model:[/dim] {model}   [dim]tools:[/dim] {tools}   [dim]skills:[/dim] {skills}"""

class PedaloApp(App):
    CSS = """
    Screen { layout: vertical; }
    #banner { padding: 1 2; border: round cyan; margin: 1 1 0 1; height: auto; }
    #chat { margin: 0 1; }
    Lake { height: 3; margin: 0 2; }
    Input { margin: 0 1 1 1; }
    Collapsible { margin: 0 0 1 2; }
    .agent-msg { margin: 0 0 1 1; }
    """

    def __init__(self, agent, skills: list[dict]):
        super().__init__()
        self.agent = agent
        self.skills = skills
        agent.on_tool_call = self._on_tool_call
        agent.on_tool_result = self._on_tool_result
        agent.confirm = self._confirm

    def compose(self) -> ComposeResult:
        yield Static(BANNER.format(
            provider=type(self.agent.provider).__name__,
            model=self.agent.provider.model,
            tools=len(self.agent.tools),
            skills=len(self.skills),
        ), id="banner")
        yield VerticalScroll(id="chat")
        yield Lake()
        suggestions = [f"/skill {s['name']} " for s in self.skills] + ["/exit"]
        yield Input(placeholder="Your request…  (/skill <name> <request>, /exit)",
                    suggester=SuggestFromList(suggestions, case_sensitive=False))

    def on_input_submitted(self, event: Input.Submitted):
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return
        if text == "/exit":
            self.exit()
            return

        if text.startswith("/skill "):
            prompt = self._build_skill_prompt(text)
            if prompt is None:
                return
        else:
            prompt = text

        self._chat_mount(Markdown(f"**user >** {text}", classes="agent-msg"))
        self.query_one(Lake).set_activity("setting sail…")
        self.run_worker(lambda: self._run_agent(prompt), thread=True, exclusive=True)

    def _build_skill_prompt(self, text: str) -> str | None:
        parts = text.split(" ", 2)
        if len(parts) < 3:
            self._chat_mount(Static("[red]Usage: /skill <name> <request>[/red]"))
            return None
        _, name, request = parts
        skill = next((s for s in self.skills if s["name"] == name), None)
        if skill is None:
            self._chat_mount(Static(f"[red]Unknown skill: {name}[/red]"))
            return None
        content = Path(skill["path"]).read_text(encoding="utf-8")
        return f"[Skill invoked: {name}]\n{content}\n\nUser request: {request}"

    def _run_agent(self, prompt: str):
        try:
            answer = self.agent.run(prompt)
        except Exception as e:
            answer = f"*Error : {e}*"
        self.call_from_thread(self._chat_mount, Markdown(f"**⛵ pedalo >** {answer}", classes="agent-msg"))
        self.call_from_thread(self.query_one(Lake).set_activity, None)

    def _on_tool_call(self, name: str, arguments: dict):
        target = arguments.get("path") or arguments.get("command") or ""
        target = str(target)[:60]
        self.call_from_thread(self.query_one(Lake).set_activity, f"{name} → {target}")
        args = json.dumps(arguments, ensure_ascii=False)
        col = Collapsible(Static(args), title=f"⚙ {name}  [dim]{target}[/dim]", collapsed=True)
        self.call_from_thread(self._chat_mount, col)
        self._pending = col

    def _on_tool_result(self, name: str, result: str):
        preview = result if len(result) < 3000 else result[:3000] + "…"
        def fill():
            self._pending.mount(Static(f"[green]result :[/green]\n{preview}"))
        self.call_from_thread(fill)

    def _confirm(self, name: str, arguments: dict) -> str:
        done = threading.Event()
        answer = {}
        def show():
            def on_done(value):
                answer["v"] = value or "n"
                done.set()
            self.push_screen(ConfirmScreen(name, arguments), callback=on_done)
        self.call_from_thread(show)
        done.wait()
        return answer["v"]

    def _chat_mount(self, widget):
        chat = self.query_one("#chat")
        chat.mount(widget)
        chat.scroll_end(animate=False)