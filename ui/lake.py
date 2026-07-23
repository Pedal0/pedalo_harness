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
        self.phase += 0.35

        speed = 1.6 if self.activity else 0.25
        if abs(self.target - self.pos) < 1:
            self.target = random.uniform(2, width)
        self.pos += speed if self.target > self.pos else -speed
        self.pos = max(1, min(self.pos, width))

        if self.process_count and random.random() < 0.3:
            self.ripples.append([random.randint(2, max(3, width - 2)), 0.0])
        for r in self.ripples:
            r[1] += 0.7
        self.ripples = [r for r in self.ripples if r[1] < 7]

        self.update(self._draw(width))

    def _draw(self, width: int) -> str:
        size = width + 6
        x = int(self.pos)
        bob = math.sin(self.phase * 0.8) > 0 

        if self.activity:
            label = self.activity
        elif self.process_count:
            label = f"{self.process_count} process running…"
        else:
            label = "anchored…"
        label_line = " " * max(x - len(label) // 2, 0) + f"[dim]{label}[/dim]"

        surface = []
        for i in range(size):
            v = math.sin(i * 0.4 + self.phase)
            surface.append(WAVE_CHARS[int((v + 1) * 1.9) % len(WAVE_CHARS)])

        for rx, radius in self.ripples:
            for p in (rx - int(radius), rx + int(radius)):
                if 0 <= p < size:
                    surface[p] = "°"

        above = [" "] * size
        if bob:
            for i, c in enumerate("···"):
                wx = x - 3 + i
                if 0 <= wx < size:
                    above[wx] = c
            if 0 <= x < size:
                above[x] = BOAT
        else:
            if 0 <= x < size:
                surface[x] = BOAT

        deep = []
        for i in range(size):
            v = math.sin(i * 0.25 - self.phase * 0.6)
            deep.append("~" if v > 0.3 else " ")

        return (
            f"{label_line}\n"
            f"{''.join(above)}\n"
            f"[blue]{''.join(surface)}[/blue]\n"
            f"[dim blue]{''.join(deep)}[/dim blue]"
        )