"""
Tests for the GameEngine class — state transitions, choice execution,
item-gated paths, health-based game overs, and visited node tracking.
"""

import pytest
from unittest.mock import MagicMock, patch, call

from game.engine import GameEngine
from game.player import Player
from story.nodes import STORY_NODES, NODE_MAP


# ─── Helpers ───────────────────────────────────────────────────────────────────

def make_mock_renderer():
    """Creates a mock UIRenderer with all required methods."""
    renderer = MagicMock()
    renderer.render_intro = MagicMock()
    renderer.render_scene = MagicMock()
    renderer.render_ending = MagicMock()
    renderer.render_requirement_failure = MagicMock()
    renderer.ask_choice = MagicMock(return_value="1")
    renderer.show_invalid_choice = MagicMock()
    return renderer


MINI_STORY = [
    {
        "id": "start",
        "title": "Start",
        "description": "You begin.",
        "choices": [
            {"text": "Go A", "next": "node_a", "score": 10, "items": ["key"]},
            {"text": "Go B", "next": "node_b", "score": 5, "health": -20},
        ],
        "is_ending": False,
    },
    {
        "id": "node_a",
        "title": "Node A",
        "description": "You are at A.",
        "choices": [
            {"text": "Use key", "next": "win", "score": 50, "required_item": "key", "fallback": "lose"},
            {"text": "Go to end", "next": "win", "score": 30},
        ],
        "is_ending": False,
    },
    {
        "id": "node_b",
        "title": "Node B",
        "description": "You are at B.",
        "choices": [
            {"text": "Heal and finish", "next": "win", "score": 20, "health": 15},
        ],
        "is_ending": False,
    },
    {
        "id": "win",
        "title": "Victory",
        "description": "You won.",
        "choices": [],
        "is_ending": True,
        "ending_type": "win",
    },
    {
        "id": "lose",
        "title": "Loss",
        "description": "You lost.",
        "choices": [],
        "is_ending": True,
        "ending_type": "loss",
    },
]

MINI_NODE_MAP = {node["id"]: node for node in MINI_STORY}


# ─── Initialization ───────────────────────────────────────────────────────────

class TestEngineInit:
    """Tests for GameEngine initialization."""

    def test_starts_at_start_node(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        assert engine.current_node_id == "start"

    def test_player_initialized(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        assert isinstance(engine.player, Player)
        assert engine.player.health == 100
        assert engine.player.score == 0

    def test_visited_nodes_empty(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        assert engine.visited_nodes == []


# ─── Rendering ─────────────────────────────────────────────────────────────────

class TestRenderCurrentNode:
    """Tests for the render_current_node method."""

    def test_adds_to_visited_on_first_visit(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.render_current_node()
        assert "start" in engine.visited_nodes

    def test_does_not_duplicate_visited(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.render_current_node()
        engine.render_current_node()
        assert engine.visited_nodes.count("start") == 1

    def test_calls_renderer(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.render_current_node()
        renderer.render_scene.assert_called_once()


# ─── Choice Execution ─────────────────────────────────────────────────────────

class TestExecuteChoice:
    """Tests for execute_choice — score, health, items, and state transitions."""

    def test_score_awarded(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        node = MINI_NODE_MAP["start"]
        engine.execute_choice(node, 0)  # Go A: +10 score, +key
        assert engine.player.score == 10

    def test_item_awarded(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        node = MINI_NODE_MAP["start"]
        engine.execute_choice(node, 0)  # Go A: +key
        assert engine.player.has_item("key")

    def test_health_damage_applied(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        node = MINI_NODE_MAP["start"]
        engine.execute_choice(node, 1)  # Go B: -20 HP
        assert engine.player.health == 80

    def test_health_heal_applied(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        engine.player.take_damage(50)  # 50 HP
        node = MINI_NODE_MAP["node_b"]
        engine.execute_choice(node, 0)  # +15 HP
        assert engine.player.health == 65

    def test_transitions_to_next_node(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        node = MINI_NODE_MAP["start"]
        engine.execute_choice(node, 0)  # Go A
        assert engine.current_node_id == "node_a"

    def test_required_item_success(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        engine.player.add_item("key")
        node = MINI_NODE_MAP["node_a"]
        engine.execute_choice(node, 0)  # Use key → win
        assert engine.current_node_id == "win"
        assert engine.player.score == 50

    def test_required_item_failure_with_fallback(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        # Player does NOT have "key"
        node = MINI_NODE_MAP["node_a"]
        engine.execute_choice(node, 0)  # Use key (no key) → fallback to lose
        assert engine.current_node_id == "lose"
        renderer.render_requirement_failure.assert_called_once_with("key")

    def test_required_item_failure_no_score_awarded(self):
        renderer = make_mock_renderer()
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.node_map = MINI_NODE_MAP

        node = MINI_NODE_MAP["node_a"]
        engine.execute_choice(node, 0)  # Fail — no score
        assert engine.player.score == 0


# ─── Full Game Runs (Integration) ─────────────────────────────────────────────

class TestGameRun:
    """Integration tests for full game loop scenarios using the real story graph."""

    def test_fastest_win_path(self):
        """start → neon_club → hacker_den → data_storm → rooftop → escape → victory"""
        renderer = make_mock_renderer()
        # Simulate choices: 1, 2, 1, 1, 1, 1
        renderer.ask_choice = MagicMock(side_effect=["1", "2", "1", "1", "1", "1"])
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.run()

        assert engine.current_node_id == "victory"
        assert engine.player.score > 0
        renderer.render_ending.assert_called_once()
        ending_node = renderer.render_ending.call_args[0][0]
        assert ending_node["ending_type"] == "win"

    def test_stealth_win_path(self):
        """start → neon_club → hacker_den → data_storm → rooftop → escape → victory_stealth"""
        renderer = make_mock_renderer()
        # Choices: 1, 2, 1, 1, 1, 2
        renderer.ask_choice = MagicMock(side_effect=["1", "2", "1", "1", "1", "2"])
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.run()

        assert engine.current_node_id == "victory_stealth"
        ending_node = renderer.render_ending.call_args[0][0]
        assert ending_node["ending_type"] == "win"

    def test_burnout_via_drone_fight(self):
        """start → neon_club → hacker_den → data_storm → rooftop → fight drones → burnout"""
        renderer = make_mock_renderer()
        # Choices: 1, 2, 1, 1, 2
        renderer.ask_choice = MagicMock(side_effect=["1", "2", "1", "1", "2"])
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.run()

        # The drone fight does -40 HP (from 100-5=95 at most), plus earlier damage
        # The node itself transitions to burnout
        ending_node = renderer.render_ending.call_args[0][0]
        assert ending_node["ending_type"] == "loss"

    def test_intro_rendered_on_run(self):
        renderer = make_mock_renderer()
        renderer.ask_choice = MagicMock(side_effect=["1", "2", "1", "1", "1", "1"])
        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.run()
        renderer.render_intro.assert_called_once()

    def test_invalid_choice_retried(self):
        """Invalid input should trigger show_invalid_choice and re-prompt."""
        renderer = make_mock_renderer()
        # "abc" is invalid, then "99" is out of range, then "1" is valid → ending
        renderer.ask_choice = MagicMock(side_effect=["abc", "99", "1", "2", "1", "1", "1", "1"])

        engine = GameEngine(renderer=renderer, story_nodes=STORY_NODES)
        engine.run()

        assert renderer.show_invalid_choice.call_count >= 2
