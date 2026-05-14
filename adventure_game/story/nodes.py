from __future__ import annotations

from typing import Any, Dict, List

Node = Dict[str, Any]

STORY_NODES: List[Node] = [
    {
        "id": "start",
        "title": "Neon District Entrance",
        "description": "The city pulse hums in your veins. A corp tower looms ahead, shielded by night drones and neon haze. Your run begins now.",
        "choices": [
            {"text": "Slip into the Neon Club to gather intel.", "next": "neon_club", "score": 10, "items": ["keycard"]},
            {"text": "Move through the Hidden Alley to bypass security.", "next": "hidden_alley", "score": 5, "health": -5},
        ],
        "is_ending": False,
    },
    {
        "id": "neon_club",
        "title": "Neon Club",
        "description": "The club bass rattles the air as a bartender slides you a data shard. A corp agent is watching the door.",
        "choices": [
            {"text": "Offer the agent a fake ID and bluff your way through.", "next": "corp_vault", "score": 15, "health": -10},
            {"text": "Sneak out the back and contact a hacker for a backdoor.", "next": "hacker_den", "score": 10, "items": ["trusted_link"]},
        ],
        "is_ending": False,
    },
    {
        "id": "hidden_alley",
        "title": "Hidden Alley",
        "description": "Steam rises from the sewer gates. A low-level drone drifts by, scanning for unauthorized heat signatures.",
        "choices": [
            {"text": "Use a stolen keycard to jam the drone's scanner.", "next": "corp_vault", "score": 20, "required_item": "keycard", "fallback": "burnout"},
            {"text": "Dash past the drone before it turns.", "next": "data_storm", "score": 10, "health": -15},
        ],
        "is_ending": False,
    },
    {
        "id": "hacker_den",
        "title": "Hacker Den",
        "description": "Walls of monitors glow with code. Your contact raises an eyebrow and slides over a decoy uplink.",
        "choices": [
            {"text": "Install the uplink and infiltrate the corp's network.", "next": "data_storm", "score": 15, "items": ["decoy_uplink"]},
            {"text": "Bribe the hacker for a physical bypass module.", "next": "rooftop", "score": 10, "items": ["bypass_module"], "health": -5},
        ],
        "is_ending": False,
    },
    {
        "id": "corp_vault",
        "title": "Corporate Vault",
        "description": "Rows of secure pods glow. You can feel the hum of the vault's quantum locks beneath your fingertips.",
        "choices": [
            {"text": "Deploy the bypass module and force the vault open.", "next": "escape", "score": 25, "health": -20, "required_item": "bypass_module", "fallback": "burnout"},
            {"text": "Use the trusted link and extract the data remotely.", "next": "data_storm", "score": 20, "required_item": "trusted_link", "fallback": "burnout"},
        ],
        "is_ending": False,
    },
    {
        "id": "data_storm",
        "title": "Data Storm",
        "description": "Code cascades like lightning. You ride it, guiding the data through a maze of ICE and server ghosts.",
        "choices": [
            {"text": "Seize the corporate secrets and make a dash for the roof.", "next": "rooftop", "score": 30, "items": ["stolen_shard"]},
            {"text": "Plant a virus and create a diversion.", "next": "escape", "score": 20, "health": -10},
        ],
        "is_ending": False,
    },
    {
        "id": "rooftop",
        "title": "Rooftop Extraction",
        "description": "The wind tastes of ozone. A drone pack sweeps the sky, and the extraction line hums with potential escape.",
        "choices": [
            {"text": "Call the extraction and leap into the night.", "next": "escape", "score": 40},
            {"text": "Stay and fight the drone pack to keep the data safe.", "next": "burnout", "score": 20, "health": -40},
        ],
        "is_ending": False,
    },
    {
        "id": "escape",
        "title": "Escape Corridor",
        "description": "Smoke and neon blur as you sprint through the corridor. The city is almost within reach.",
        "choices": [
            {"text": "Follow the rooftop line and vault over the barrier.", "next": "victory", "score": 50},
            {"text": "Take the subway tunnel and disappear beneath the city.", "next": "victory_stealth", "score": 45},
        ],
        "is_ending": False,
    },
    {
        "id": "burnout",
        "title": "System Burnout",
        "description": "Your neural implants overload. Pain flashes and the world goes static. The run collapses in a cascade of corrupted code.",
        "choices": [],
        "is_ending": True,
        "ending_type": "loss",
    },
    {
        "id": "victory",
        "title": "High-Value Extraction",
        "description": "The extraction whines and takes you into the night. You make it out with the corp secrets and your score skyrockets.",
        "choices": [],
        "is_ending": True,
        "ending_type": "win",
    },
    {
        "id": "victory_stealth",
        "title": "Ghost Run",
        "description": "You vanish into the subway tunnels, leaving no trace. The corp never knew what hit them.",
        "choices": [],
        "is_ending": True,
        "ending_type": "win",
    },
]

NODE_MAP = {node["id"]: node for node in STORY_NODES}
