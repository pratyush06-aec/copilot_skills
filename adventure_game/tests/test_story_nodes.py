"""
Tests for story node data integrity — validates the declarative story graph
to ensure all nodes are well-formed, all references resolve, and the graph
has valid start/end points.
"""

import pytest
from story.nodes import STORY_NODES, NODE_MAP, Node


# ─── Node Data Structure ───────────────────────────────────────────────────────

class TestNodeStructure:
    """Validates that every node has the required fields."""

    def test_all_nodes_have_ids(self):
        for node in STORY_NODES:
            assert "id" in node, f"Node missing 'id': {node}"

    def test_all_ids_are_unique(self):
        ids = [node["id"] for node in STORY_NODES]
        assert len(ids) == len(set(ids)), f"Duplicate node IDs found: {ids}"

    def test_all_nodes_have_titles(self):
        for node in STORY_NODES:
            assert "title" in node, f"Node '{node['id']}' missing 'title'"
            assert len(node["title"]) > 0, f"Node '{node['id']}' has empty title"

    def test_all_nodes_have_descriptions(self):
        for node in STORY_NODES:
            assert "description" in node, f"Node '{node['id']}' missing 'description'"
            assert len(node["description"]) > 0, f"Node '{node['id']}' has empty description"

    def test_all_nodes_have_choices_list(self):
        for node in STORY_NODES:
            assert "choices" in node, f"Node '{node['id']}' missing 'choices'"
            assert isinstance(node["choices"], list), f"Node '{node['id']}' choices is not a list"

    def test_all_nodes_have_is_ending_flag(self):
        for node in STORY_NODES:
            assert "is_ending" in node, f"Node '{node['id']}' missing 'is_ending'"
            assert isinstance(node["is_ending"], bool), f"Node '{node['id']}' is_ending is not bool"


# ─── Choice Validation ─────────────────────────────────────────────────────────

class TestChoiceStructure:
    """Validates that every choice has the required fields and valid references."""

    def test_all_choices_have_text(self):
        for node in STORY_NODES:
            for i, choice in enumerate(node["choices"]):
                assert "text" in choice, f"Node '{node['id']}' choice {i} missing 'text'"
                assert len(choice["text"]) > 0

    def test_all_choices_have_next(self):
        for node in STORY_NODES:
            for i, choice in enumerate(node["choices"]):
                assert "next" in choice, f"Node '{node['id']}' choice {i} missing 'next'"

    def test_all_next_references_are_valid(self):
        valid_ids = {node["id"] for node in STORY_NODES}
        for node in STORY_NODES:
            for i, choice in enumerate(node["choices"]):
                target = choice["next"]
                assert target in valid_ids, (
                    f"Node '{node['id']}' choice {i} references unknown node '{target}'"
                )

    def test_all_fallback_references_are_valid(self):
        valid_ids = {node["id"] for node in STORY_NODES}
        for node in STORY_NODES:
            for i, choice in enumerate(node["choices"]):
                fallback = choice.get("fallback")
                if fallback:
                    assert fallback in valid_ids, (
                        f"Node '{node['id']}' choice {i} fallback references unknown node '{fallback}'"
                    )

    def test_required_items_have_fallbacks(self):
        """Every choice with a required_item should have a fallback node."""
        for node in STORY_NODES:
            for i, choice in enumerate(node["choices"]):
                if "required_item" in choice:
                    assert "fallback" in choice, (
                        f"Node '{node['id']}' choice {i} has required_item "
                        f"'{choice['required_item']}' but no fallback"
                    )

    def test_score_values_are_non_negative(self):
        for node in STORY_NODES:
            for i, choice in enumerate(node["choices"]):
                score = choice.get("score", 0)
                assert score >= 0, (
                    f"Node '{node['id']}' choice {i} has negative score: {score}"
                )

    def test_items_field_is_list(self):
        for node in STORY_NODES:
            for i, choice in enumerate(node["choices"]):
                items = choice.get("items")
                if items is not None:
                    assert isinstance(items, list), (
                        f"Node '{node['id']}' choice {i} 'items' is not a list"
                    )


# ─── Graph Topology ────────────────────────────────────────────────────────────

class TestGraphTopology:
    """Validates the overall story graph structure."""

    def test_start_node_exists(self):
        assert "start" in NODE_MAP, "Missing 'start' node"

    def test_start_node_is_not_ending(self):
        assert NODE_MAP["start"]["is_ending"] is False

    def test_start_node_has_choices(self):
        assert len(NODE_MAP["start"]["choices"]) > 0, "Start node has no choices"

    def test_at_least_one_win_ending_exists(self):
        win_endings = [n for n in STORY_NODES if n.get("ending_type") == "win"]
        assert len(win_endings) >= 1, "No win ending found"

    def test_at_least_one_loss_ending_exists(self):
        loss_endings = [n for n in STORY_NODES if n.get("ending_type") == "loss"]
        assert len(loss_endings) >= 1, "No loss ending found"

    def test_ending_nodes_have_no_choices(self):
        for node in STORY_NODES:
            if node["is_ending"]:
                assert node["choices"] == [], (
                    f"Ending node '{node['id']}' has choices but shouldn't"
                )

    def test_ending_nodes_have_ending_type(self):
        for node in STORY_NODES:
            if node["is_ending"]:
                assert "ending_type" in node, (
                    f"Ending node '{node['id']}' missing 'ending_type'"
                )
                assert node["ending_type"] in ("win", "loss"), (
                    f"Ending node '{node['id']}' has invalid ending_type: {node['ending_type']}"
                )

    def test_non_ending_nodes_have_choices(self):
        for node in STORY_NODES:
            if not node["is_ending"]:
                assert len(node["choices"]) > 0, (
                    f"Non-ending node '{node['id']}' has no choices — dead end"
                )

    def test_node_map_matches_story_nodes(self):
        assert len(NODE_MAP) == len(STORY_NODES)
        for node in STORY_NODES:
            assert node["id"] in NODE_MAP
            assert NODE_MAP[node["id"]] is node

    def test_total_node_count(self):
        assert len(STORY_NODES) == 11, f"Expected 11 nodes, got {len(STORY_NODES)}"


# ─── Reachability ──────────────────────────────────────────────────────────────

class TestReachability:
    """Ensures all nodes can be reached from the start and all paths lead to an ending."""

    def test_all_nodes_reachable_from_start(self):
        """BFS from 'start' should reach every node in the graph."""
        visited = set()
        queue = ["start"]
        while queue:
            node_id = queue.pop(0)
            if node_id in visited:
                continue
            visited.add(node_id)
            node = NODE_MAP[node_id]
            for choice in node["choices"]:
                queue.append(choice["next"])
                if "fallback" in choice:
                    queue.append(choice["fallback"])

        all_ids = {node["id"] for node in STORY_NODES}
        unreachable = all_ids - visited
        assert unreachable == set(), f"Unreachable nodes from 'start': {unreachable}"

    def test_all_paths_lead_to_ending(self):
        """DFS from every non-ending node should eventually reach an ending."""
        def can_reach_ending(node_id, seen=None):
            if seen is None:
                seen = set()
            if node_id in seen:
                return False  # cycle detected
            seen.add(node_id)
            node = NODE_MAP[node_id]
            if node["is_ending"]:
                return True
            return any(
                can_reach_ending(choice["next"], seen.copy())
                for choice in node["choices"]
            )

        for node in STORY_NODES:
            if not node["is_ending"]:
                assert can_reach_ending(node["id"]), (
                    f"Node '{node['id']}' cannot reach any ending"
                )
