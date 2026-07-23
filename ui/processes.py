import json
import time
from pathlib import Path

from textual.widgets import Static

from ui.lake import Lake


class ProcessBar(Static):
    DEFAULT_CSS = """
    ProcessBar { height: auto; margin: 0 2; color: $text-muted; }
    """

    def on_mount(self):
        self.set_interval(1.0, self.refresh_processes)
        self.refresh_processes()

    def refresh_processes(self):
        proc_dir = Path.cwd() / ".pedalo" / "processes"
        if not proc_dir.exists():
            self.update("")
            return

        lines = []
        for meta_path in sorted(proc_dir.glob("*.json")):
            try:
                meta = json.loads(meta_path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if meta.get("finished_at") is not None:
                continue

            log_path = Path(meta["log_path"])
            if log_path.exists():
                idle = time.time() - log_path.stat().st_mtime
                if idle > 10:
                    continue
                last = self._last_line(log_path)
            else:
                last = ""

            elapsed = self._elapsed(meta["started_at"])
            command = meta["command"][:40]
            lines.append(f"⛵ [b]{command}[/b] · {elapsed} · [dim]{last[:60]}[/dim]")

        self.update("\n".join(lines))
        try:
            self.app.query_one(Lake).set_processes(len(lines))
        except Exception:
            pass

    def _last_line(self, log_path: Path) -> str:
        try:
            raw = log_path.read_bytes()[-2000:]
            try:
                text = raw.decode("utf-8", errors="replace")
            except Exception:
                text = raw.decode("cp850", errors="replace")
            for line in reversed(text.splitlines()):
                if line.strip():
                    return line.strip()
        except Exception:
            pass
        return ""

    def _elapsed(self, started_at: str) -> str:
        from datetime import datetime
        started = datetime.fromisoformat(started_at)
        seconds = int((datetime.now() - started).total_seconds())
        if seconds < 60:
            return f"{seconds}s"
        return f"{seconds // 60}m{seconds % 60:02d}s"