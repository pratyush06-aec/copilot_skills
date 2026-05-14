from __future__ import annotations

from typing import Dict, List


class Player:
    def __init__(self, name: str = "Runner") -> None:
        self.name = name
        self.max_health = 100
        self.health = 100
        self.inventory: Dict[str, int] = {}
        self.score = 0

    def add_item(self, item_name: str, count: int = 1) -> None:
        self.inventory[item_name] = self.inventory.get(item_name, 0) + count

    def remove_item(self, item_name: str, count: int = 1) -> bool:
        current = self.inventory.get(item_name, 0)
        if current < count:
            return False
        if current == count:
            del self.inventory[item_name]
        else:
            self.inventory[item_name] = current - count
        return True

    def has_item(self, item_name: str) -> bool:
        return self.inventory.get(item_name, 0) > 0

    def take_damage(self, amount: int) -> None:
        self.health = max(self.health - amount, 0)

    def heal(self, amount: int) -> None:
        self.health = min(self.health + amount, self.max_health)

    def add_score(self, amount: int) -> None:
        self.score += amount

    def get_status(self) -> Dict[str, object]:
        return {
            "health": self.health,
            "max_health": self.max_health,
            "score": self.score,
            "inventory": self.inventory,
        }

    def inventory_lines(self) -> List[str]:
        if not self.inventory:
            return ["[dim]Empty[/dim]"]
        return [f"{item} x{count}" for item, count in self.inventory.items()]
