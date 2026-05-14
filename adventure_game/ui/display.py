from __future__ import annotations

from time import sleep
from typing import Dict, List

from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text

from story.nodes import Node
from ui.flowchart import FlowchartVisualizer


class UIRenderer:
    def __init__(self) -> None:
        self.console = Console()
        self.flowchart = FlowchartVisualizer()
        self.figlet = Figlet(font="slant")

    def render_intro(self) -> None:
        self.console.clear()
        title = self.figlet.renderText("NEON FATE")
        title_text = Text(title, style="bold bright_cyan")
        subtitle = Text("CYBERPUNK ADVENTURE SIM", style="bold bright_magenta")
        self.console.print(Panel(title_text, border_style="cyan", subtitle=subtitle, padding=(1, 2)))
        self.console.print("")
        self.console.print(Text("Booting neural overlay...", style="bright_white"))
        with Progress(SpinnerColumn(style="bright_magenta"), "[bold cyan]Initializing systems...", TimeElapsedColumn(), transient=True) as progress:
            task = progress.add_task("boot", total=None)
            sleep(1.0)
            progress.update(task, advance=1)
            sleep(0.8)
        self.console.print(Text("Ready. Press Enter to launch your run.", style="bright_green"))
        input()

    def render_scene(self, node: Node, player: object, visited_nodes: List[str]) -> None:
        self.console.clear()
        self.render_header(node["title"], player)
        self.render_flow(node["id"], visited_nodes)
        self.render_body(node)
        self.render_status(player)
        self.render_inventory(player)

    def render_header(self, location_name: str, player: object) -> None:
        header = Table.grid(expand=True)
        header.add_column(ratio=1)
        header.add_column(ratio=2)
        header.add_column(ratio=1)
        header.add_row(
            Text("[ NEON FATE ]", style="bold bright_cyan"),
            Text(f"Location: {location_name}", style="bold bright_magenta"),
            Text(f"Score: {player.score}", style="bold green"),
        )
        self.console.print(header)
        self.console.rule(style="bright_blue")

    def render_flow(self, current_node: str, visited_nodes: List[str]) -> None:
        flow_text = self.flowchart.render(current_node=current_node, visited=visited_nodes)
        self.console.print(Panel(flow_text, title="Mission Flow", border_style="bright_magenta"))

    def render_body(self, node: Node) -> None:
        body = Text(node["description"], style="white")
        self.console.print(body)
        self.console.print("")
        for index, choice in enumerate(node["choices"], start=1):
            line = Text(f"[{index}] {choice['text']}", style="bold cyan")
            if choice.get("score"):
                line.append(Text(f"  (+{choice['score']} pts)", style="green"))
            if choice.get("health"):
                health_change = choice['health']
                color = "red" if health_change < 0 else "green"
                line.append(Text(f"  ({health_change:+} HP)", style=color))
            self.console.print(line)

    def render_status(self, player: object) -> None:
        status = Table.grid(expand=True)
        status.add_column(ratio=3)
        status.add_column(ratio=1)
        status.add_row(self._health_bar(player.health, player.max_health), self._score_panel(player.score))
        self.console.print(status)

    def _health_bar(self, health: int, max_health: int) -> Panel:
        percent = max(min(health / max_health, 1.0), 0.0)
        fill = int(percent * 20)
        empty = 20 - fill
        color = "green" if percent > 0.6 else "yellow" if percent > 0.3 else "red"
        bar = f"[{color}]" + "█" * fill + "[/]" + "░" * empty
        health_line = f"Health: {health}/{max_health}"
        return Panel(Text(bar + "\n" + health_line, style="bold"), border_style=color, title="Vitals")

    def _score_panel(self, score: int) -> Panel:
        score_text = Text(str(score), style="bold bright_green")
        return Panel(score_text, title="Score", border_style="bright_green")

    def render_inventory(self, player: object) -> None:
        inventory_table = Table(show_header=True, header_style="bold magenta")
        inventory_table.add_column("Item", justify="left")
        inventory_table.add_column("Count", justify="center")
        if player.inventory:
            for item, count in player.inventory.items():
                inventory_table.add_row(item, str(count))
        else:
            inventory_table.add_row("[dim]Empty[/dim]", "-")
        self.console.print(Panel(inventory_table, title="Inventory", border_style="bright_blue"))

    def ask_choice(self, max_choice: int) -> str:
        prompt = Text(f"Choose an action [1-{max_choice}]: ", style="bold bright_cyan")
        return self.console.input(prompt)

    def show_invalid_choice(self) -> None:
        self.console.print(Text("Invalid choice. Try again.", style="bold red"))

    def render_requirement_failure(self, required_item: str) -> None:
        self.console.print(Panel(Text(f"You need {required_item} to proceed.", style="bold yellow"), border_style="yellow"))

    def render_ending(self, node: Node, player: object) -> None:
        self.console.clear()
        title = Text(node["title"], style="bold bright_magenta")
        summary = Text(node["description"], style="white")
        self.console.print(Panel(title, subtitle="RUN COMPLETE", style="bright_blue", border_style="bright_magenta"))
        self.console.print(summary)
        self.console.print("")
        self.console.print(Text(f"Final Score: {player.score}", style="bold bright_green"))
        self.console.print(Text(f"Final Health: {player.health}/{player.max_health}", style="bold cyan"))
        self.console.print(Panel(Text("Inventory:\n" + ("\n".join(player.inventory_lines())), style="white"), title="Loot Collected", border_style="bright_blue"))
        if node.get("ending_type") == "loss":
            self.console.print(Text("[bold red]Mission failed. The city still stands. Try again.[/bold red]"))
        else:
            self.console.print(Text("[bold bright_green]Mission success. Neon Fate smiles on you.[/bold bright_green]"))
        self.console.print("")
        self.console.print(Text("Press Enter to exit.", style="bright_white"))
        input()
