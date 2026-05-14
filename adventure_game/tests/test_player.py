"""
Tests for the Player class — health, inventory, score, and status management.
"""

import pytest
from game.player import Player


# ─── Initialization ────────────────────────────────────────────────────────────

class TestPlayerInit:
    """Tests for Player default and custom initialization."""

    def test_default_name(self):
        player = Player()
        assert player.name == "Runner"

    def test_custom_name(self):
        player = Player(name="Ghost")
        assert player.name == "Ghost"

    def test_default_health(self):
        player = Player()
        assert player.health == 100
        assert player.max_health == 100

    def test_default_score(self):
        player = Player()
        assert player.score == 0

    def test_default_inventory_is_empty(self):
        player = Player()
        assert player.inventory == {}


# ─── Inventory Management ──────────────────────────────────────────────────────

class TestInventory:
    """Tests for add_item, remove_item, and has_item methods."""

    def test_add_single_item(self):
        player = Player()
        player.add_item("keycard")
        assert player.inventory == {"keycard": 1}

    def test_add_item_with_count(self):
        player = Player()
        player.add_item("ammo", 5)
        assert player.inventory == {"ammo": 5}

    def test_add_item_stacks(self):
        player = Player()
        player.add_item("ammo", 3)
        player.add_item("ammo", 2)
        assert player.inventory["ammo"] == 5

    def test_add_multiple_different_items(self):
        player = Player()
        player.add_item("keycard")
        player.add_item("bypass_module")
        assert len(player.inventory) == 2
        assert player.has_item("keycard")
        assert player.has_item("bypass_module")

    def test_remove_item_success(self):
        player = Player()
        player.add_item("keycard")
        result = player.remove_item("keycard")
        assert result is True
        assert "keycard" not in player.inventory

    def test_remove_item_partial(self):
        player = Player()
        player.add_item("ammo", 5)
        result = player.remove_item("ammo", 2)
        assert result is True
        assert player.inventory["ammo"] == 3

    def test_remove_item_fails_when_insufficient(self):
        player = Player()
        player.add_item("ammo", 2)
        result = player.remove_item("ammo", 5)
        assert result is False
        assert player.inventory["ammo"] == 2  # unchanged

    def test_remove_item_fails_when_not_owned(self):
        player = Player()
        result = player.remove_item("phantom_item")
        assert result is False

    def test_remove_item_exact_count_deletes_key(self):
        player = Player()
        player.add_item("keycard", 3)
        player.remove_item("keycard", 3)
        assert "keycard" not in player.inventory

    def test_has_item_true(self):
        player = Player()
        player.add_item("keycard")
        assert player.has_item("keycard") is True

    def test_has_item_false(self):
        player = Player()
        assert player.has_item("keycard") is False

    def test_has_item_false_after_removal(self):
        player = Player()
        player.add_item("keycard")
        player.remove_item("keycard")
        assert player.has_item("keycard") is False


# ─── Health System ─────────────────────────────────────────────────────────────

class TestHealth:
    """Tests for take_damage and heal methods."""

    def test_take_damage_reduces_health(self):
        player = Player()
        player.take_damage(30)
        assert player.health == 70

    def test_take_damage_clamps_to_zero(self):
        player = Player()
        player.take_damage(999)
        assert player.health == 0

    def test_take_zero_damage(self):
        player = Player()
        player.take_damage(0)
        assert player.health == 100

    def test_heal_restores_health(self):
        player = Player()
        player.take_damage(50)
        player.heal(20)
        assert player.health == 70

    def test_heal_clamps_to_max(self):
        player = Player()
        player.take_damage(10)
        player.heal(999)
        assert player.health == player.max_health

    def test_heal_at_full_health(self):
        player = Player()
        player.heal(50)
        assert player.health == 100

    def test_multiple_damage_and_heal_cycles(self):
        player = Player()
        player.take_damage(40)  # 60
        player.heal(10)         # 70
        player.take_damage(25)  # 45
        player.heal(5)          # 50
        assert player.health == 50


# ─── Score ─────────────────────────────────────────────────────────────────────

class TestScore:
    """Tests for score accumulation."""

    def test_add_score(self):
        player = Player()
        player.add_score(10)
        assert player.score == 10

    def test_add_score_accumulates(self):
        player = Player()
        player.add_score(10)
        player.add_score(25)
        player.add_score(5)
        assert player.score == 40

    def test_add_zero_score(self):
        player = Player()
        player.add_score(0)
        assert player.score == 0


# ─── Status & Display ─────────────────────────────────────────────────────────

class TestStatus:
    """Tests for get_status and inventory_lines methods."""

    def test_get_status_returns_correct_keys(self):
        player = Player()
        status = player.get_status()
        assert "health" in status
        assert "max_health" in status
        assert "score" in status
        assert "inventory" in status

    def test_get_status_reflects_state(self):
        player = Player()
        player.add_score(42)
        player.take_damage(15)
        player.add_item("shard")
        status = player.get_status()
        assert status["health"] == 85
        assert status["max_health"] == 100
        assert status["score"] == 42
        assert status["inventory"] == {"shard": 1}

    def test_inventory_lines_empty(self):
        player = Player()
        lines = player.inventory_lines()
        assert lines == ["[dim]Empty[/dim]"]

    def test_inventory_lines_with_items(self):
        player = Player()
        player.add_item("keycard")
        player.add_item("ammo", 3)
        lines = player.inventory_lines()
        assert "keycard x1" in lines
        assert "ammo x3" in lines
        assert len(lines) == 2
