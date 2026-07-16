import random

from textual.widgets import Static


BOAT = "⛵"
WATER = "≈"


class Lake(Static):
    def on_mount(self):
        self.pos = 4.0
        self.target = 10.0
        self.activity: str | None = None 
        self.set_interval(0.12, self.tick)

    def set_activity(self, text: str | None):
        self.activity = text
        width = max(self.size.width - 10, 20)
        self.target = random.uniform(2, width)

    def tick(self):
        width = max(self.size.width - 6, 20)
        speed = 1.6 if self.activity else 0.25 

        if abs(self.target - self.pos) < 1:
            self.target = random.uniform(2, width)
        self.pos += speed if self.target > self.pos else -speed
        self.pos = max(1, min(self.pos, width))

        x = int(self.pos)
        label = self.activity or "anchored…"
        boat_line = " " * x + BOAT
        label_line = " " * max(x - len(label) // 2, 0) + f"[dim]{label}[/dim]"
        water_line = f"[blue]{WATER * (width + 6)}[/blue]"
        self.update(f"{label_line}\n{boat_line}\n{water_line}")