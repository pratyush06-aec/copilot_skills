from typing import List

from rich.console import RenderableType
from rich.text import Text


class FlowchartVisualizer:
    def __init__(self) -> None:
        self.layout = [
            ("start", "[START]"),
            ("neon_club", "[Neon Club]"),
            ("hidden_alley", "[Hidden Alley]"),
            ("hacker_den", "[Hacker Den]"),
            ("corp_vault", "[Corp Vault]"),
            ("rooftop", "[Rooftop]"),
            ("data_storm", "[Data Storm]"),
            ("escape", "[Escape]"),
            ("burnout", "[Burnout]"),
        ]

    def render(self, current_node: str, visited: List[str]) -> RenderableType:
        builder = []
        for node_id, label in self.layout:
            style = "dim"
            if node_id == current_node:
                style = "bold bright_cyan"
            elif node_id in visited:
                style = "green"
            if node_id == "start":
                builder.append(self._box(label, style))
            else:
                builder.append(self._pointer(label, style))
        return Text("\n".join(builder), style="white")

    def _box(self, label: str, style: str) -> str:
        return f"╔═ {label} ═╗"

    def _pointer(self, label: str, style: str) -> str:
        return f"  ║\n  ╠═▶ {label}"
