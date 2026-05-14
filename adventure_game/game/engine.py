from __future__ import annotations

from typing import Dict, List

from game.player import Player
from story.nodes import Node, NODE_MAP
from ui.display import UIRenderer


class GameEngine:
    def __init__(self, renderer: UIRenderer, story_nodes: List[Node]) -> None:
        self.renderer = renderer
        self.story_nodes = story_nodes
        self.current_node_id = "start"
        self.player = Player()
        self.visited_nodes: List[str] = []
        self.path_history: List[str] = []
        self.node_map = NODE_MAP

    def run(self) -> None:
        self.renderer.render_intro()
        while True:
            self.render_current_node()
            node = self.node_map[self.current_node_id]
            if node.get("is_ending"):
                self.renderer.render_ending(node, self.player)
                break
            choice_index = self.prompt_choice(node)
            self.execute_choice(node, choice_index)
            if self.player.health <= 0:
                self.current_node_id = "burnout"
                self.render_current_node()
                self.renderer.render_ending(self.node_map[self.current_node_id], self.player)
                break

    def render_current_node(self) -> None:
        node = self.node_map[self.current_node_id]
        if self.current_node_id not in self.visited_nodes:
            self.visited_nodes.append(self.current_node_id)
        self.renderer.render_scene(node, self.player, self.visited_nodes)

    def prompt_choice(self, node: Node) -> int:
        while True:
            choice_input = self.renderer.ask_choice(len(node["choices"]))
            if choice_input.isdigit():
                index = int(choice_input) - 1
                if 0 <= index < len(node["choices"]):
                    return index
            self.renderer.show_invalid_choice()

    def execute_choice(self, node: Node, choice_index: int) -> None:
        choice = node["choices"][choice_index]
        required = choice.get("required_item")

        if required and not self.player.has_item(required):
            self.renderer.render_requirement_failure(required)
            fallback = choice.get("fallback")
            if fallback:
                self.current_node_id = fallback
            return

        score_change = choice.get("score", 0)
        health_change = choice.get("health", 0)
        items_awarded = choice.get("items", [])
        remove_items = choice.get("remove_items", [])

        if score_change:
            self.player.add_score(score_change)
        if health_change:
            if health_change < 0:
                self.player.take_damage(-health_change)
            else:
                self.player.heal(health_change)
        for item in items_awarded:
            self.player.add_item(item)
        for item in remove_items:
            self.player.remove_item(item)

        self.current_node_id = choice["next"]
