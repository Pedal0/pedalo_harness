import math
import random

from textual.widgets import Static

BOAT = "⛵"
WAVE_CHARS = "≈~-~"


class Lake(Static):
    def on_mount(self):
        self.pos = 4.0
        self.target = 10.0
        self.phase = 0.0
        self.activity = None
        self.process_count = 0
        self.ripples = []
        self.set_interval(0.12, self.tick)

    def set_activity(self, text: str | None):
        self.activity = text
        width = max(self.size.width - 10, 20)
        self.target = random.uniform(2, width)

    def set_processes(self, count: int):
        self.process_count = count

    def tick(self):
        width = max(self.size.width - 6, 20)
        self.phase += 0.15

        speed = 1.2 if self.activity else 0.15
        if abs(self.target - self.pos) < 1:
            self.target = random.uniform(2, width)
        self.pos += speed if self.target > self.pos else -speed
        self.pos = max(1, min(self.pos, width))

        if self.process_count and random.random() < 0.15:
            self.ripples.append([random.randint(2, max(3, width - 2)), 0.0])
        for r in self.ripples:
            r[1] += 0.5
        self.ripples = [r for r in self.ripples if r[1] < 8]

        self.update(self._draw(width))

    def _draw(self, width: int) -> str:
        size = width + 6
        x = int(self.pos)

        if self.activity:
            label = self.activity
        elif self.process_count:
            label = f"{self.process_count} process running…"
        else:
            label = "anchored…"

        boat_line = [" "] * size
        if 0 <= x < size:
            boat_line[x] = BOAT

        surface = []
        for i in range(size):
            v = math.sin(i * 0.3 + self.phase)
            surface.append("~" if v > 0.2 else "≈")

        for rx, radius in self.ripples:
            for p in (rx - int(radius), rx + int(radius)):
                if 0 <= p < size:
                    surface[p] = "°"

        return (
            f"[dim]{label}[/dim]\n"
            f"{''.join(boat_line)}\n"
            f"[blue]{''.join(surface)}[/blue]"
        )