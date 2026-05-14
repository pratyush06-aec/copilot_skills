"""
Tests for the FlowchartVisualizer and UIRenderer display utilities.
"""

import pytest
from unittest.mock import MagicMock, patch
from io import StringIO

from rich.text import Text

from ui.flowchart import FlowchartVisualizer
from ui.display import UIRenderer
from game.player import Player


# ─── FlowchartVisualizer ──────────────────────────────────────────────────────

class TestFlowchartVisualizer:
    """Tests for the FlowchartVisualizer render logic."""

    def test_initialization(self):
        viz = FlowchartVisualizer()
        assert len(viz.layout) == 9
        assert viz.layout[0][0] == "start"

    def test_render_returns_text_object(self):
        viz = FlowchartVisualizer()
        result = viz.render(current_node="start", visited=["start"])
        assert isinstance(result, Text)

    def test_render_contains_all_labels(self):
        viz = FlowchartVisualizer()
        result = viz.render(current_node="start", visited=[])
        plain = result.plain
        for node_id, label in viz.layout:
            assert label in plain, f"Label '{label}' not found in flowchart output"

    def test_start_uses_box_format(self):
        viz = FlowchartVisualizer()
        result = viz.render(current_node="start", visited=["start"])
        plain = result.plain
        assert "╔═" in plain, "Start node should use box format"

    def test_non_start_uses_pointer_format(self):
        viz = FlowchartVisualizer()
        result = viz.render(current_node="neon_club", visited=["start", "neon_club"])
        plain = result.plain
        assert "╠═▶" in plain, "Non-start nodes should use pointer format"

    def test_box_helper(self):
        viz = FlowchartVisualizer()
        box = viz._box("[START]", "bold")
        assert "╔═" in box
        assert "[START]" in box
        assert "═╗" in box

    def test_pointer_helper(self):
        viz = FlowchartVisualizer()
        pointer = viz._pointer("[Neon Club]", "green")
        assert "╠═▶" in pointer
        assert "[Neon Club]" in pointer


# ─── UIRenderer — Unit Tests ──────────────────────────────────────────────────

class TestUIRendererHealthBar:
    """Tests for the UIRenderer's _health_bar color logic."""

    def test_health_bar_green_at_full(self):
        renderer = UIRenderer()
        panel = renderer._health_bar(100, 100)
        assert panel.border_style == "green"

    def test_health_bar_green_above_60_percent(self):
        renderer = UIRenderer()
        panel = renderer._health_bar(61, 100)
        assert panel.border_style == "green"

    def test_health_bar_yellow_at_50_percent(self):
        renderer = UIRenderer()
        panel = renderer._health_bar(50, 100)
        assert panel.border_style == "yellow"

    def test_health_bar_yellow_at_31_percent(self):
        renderer = UIRenderer()
        panel = renderer._health_bar(31, 100)
        assert panel.border_style == "yellow"

    def test_health_bar_red_at_30_percent(self):
        renderer = UIRenderer()
        panel = renderer._health_bar(30, 100)
        assert panel.border_style == "red"

    def test_health_bar_red_at_zero(self):
        renderer = UIRenderer()
        panel = renderer._health_bar(0, 100)
        assert panel.border_style == "red"

    def test_health_bar_clamps_above_max(self):
        renderer = UIRenderer()
        panel = renderer._health_bar(150, 100)
        assert panel.border_style == "green"


class TestUIRendererScorePanel:
    """Tests for the UIRenderer's _score_panel method."""

    def test_score_panel_displays_value(self):
        renderer = UIRenderer()
        panel = renderer._score_panel(42)
        assert panel.title == "Score"
        assert panel.border_style == "bright_green"

    def test_score_panel_zero(self):
        renderer = UIRenderer()
        panel = renderer._score_panel(0)
        assert panel.title == "Score"


class TestUIRendererInit:
    """Tests for UIRenderer initialization."""

    def test_console_created(self):
        renderer = UIRenderer()
        assert renderer.console is not None

    def test_flowchart_created(self):
        renderer = UIRenderer()
        assert isinstance(renderer.flowchart, FlowchartVisualizer)

    def test_figlet_created(self):
        renderer = UIRenderer()
        assert renderer.figlet is not None


class TestUIRendererRenderMethods:
    """Tests for UIRenderer render methods using a mock console."""

    def test_render_scene_calls_all_sub_methods(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        player = Player()
        node = {
            "id": "test",
            "title": "Test Node",
            "description": "Test description.",
            "choices": [{"text": "Do something", "next": "end", "score": 10}],
            "is_ending": False,
        }
        renderer.render_scene(node, player, ["test"])
        renderer.console.clear.assert_called_once()
        # The method should call print multiple times (header, flow, body, status, inventory)
        assert renderer.console.print.call_count >= 3

    def test_show_invalid_choice_prints(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        renderer.show_invalid_choice()
        renderer.console.print.assert_called_once()

    def test_render_requirement_failure_prints(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        renderer.render_requirement_failure("keycard")
        renderer.console.print.assert_called_once()

    def test_render_ending_win(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        # Mock input to avoid blocking
        with patch("builtins.input", return_value=""):
            player = Player()
            player.add_score(100)
            node = {
                "id": "win",
                "title": "Victory",
                "description": "You won!",
                "choices": [],
                "is_ending": True,
                "ending_type": "win",
            }
            renderer.render_ending(node, player)
        renderer.console.clear.assert_called_once()
        assert renderer.console.print.call_count >= 4

    def test_render_ending_loss(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        with patch("builtins.input", return_value=""):
            player = Player()
            node = {
                "id": "lose",
                "title": "Burnout",
                "description": "You lost.",
                "choices": [],
                "is_ending": True,
                "ending_type": "loss",
            }
            renderer.render_ending(node, player)
        renderer.console.clear.assert_called_once()
        assert renderer.console.print.call_count >= 4

    def test_render_body_with_choices(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        node = {
            "id": "test",
            "title": "Test",
            "description": "A test scene.",
            "choices": [
                {"text": "Choice A", "next": "a", "score": 10},
                {"text": "Choice B", "next": "b", "score": 5, "health": -10},
            ],
            "is_ending": False,
        }
        renderer.render_body(node)
        # description + empty line + 2 choices = 4 prints
        assert renderer.console.print.call_count == 4

    def test_render_inventory_empty(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        player = Player()
        renderer.render_inventory(player)
        renderer.console.print.assert_called_once()

    def test_render_inventory_with_items(self):
        renderer = UIRenderer()
        renderer.console = MagicMock()
        player = Player()
        player.add_item("keycard")
        player.add_item("shard", 2)
        renderer.render_inventory(player)
        renderer.console.print.assert_called_once()
