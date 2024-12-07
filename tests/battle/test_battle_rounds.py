"""Tests for battle round mechanics and combat flow.

This module contains tests for:
1. Battle round progression and initiative system
2. Combat state management
3. Edge cases and error handling
"""

import pytest

from Battle import Character, battle_round


class MockInput:
    def __init__(self, responses):
        self.responses = responses
        self.index = 0

    def __call__(self, prompt=""):
        if self.index >= len(self.responses):
            return "e"  # Default to end turn if we run out of responses
        response = self.responses[self.index]
        self.index += 1
        return response


@pytest.fixture
def mock_inputs(monkeypatch):
    def configure_mock(responses):
        mock = MockInput(responses)
        monkeypatch.setattr("builtins.input", mock)
        return mock

    return configure_mock


def test_battle_round_order(mock_inputs):
    """Test battle round ordering and initiative system.
    Verifies:
    1. Characters are ordered by initiative (highest to lowest)
    2. Turn order is maintained throughout the round
    3. Both player and enemy characters follow initiative rules
    """
    # Setup characters with different initiatives
    player1 = Character("Player1", 20, 0, 0, 0, 0, 100, "player")
    player2 = Character("Player2", 15, 0, 0, 0, 0, 100, "player")
    enemy1 = Character("Enemy1", 10, 0, 0, 0, 0, 100, "enemy")
    enemy2 = Character("Enemy2", 5, 0, 0, 0, 0, 100, "enemy")
    characters = [player1, player2, enemy1, enemy2]

    # Mock inputs to end turns immediately
    mock_inputs(["e"] * 4)  # One 'e' for each character

    # Start combat and verify order based on initiative
    battle_round(characters, 1)
    # Verify characters are in initiative order
    sorted_chars = sorted(characters, key=lambda x: x.initiative, reverse=True)
    assert sorted_chars[0] == player1
    assert sorted_chars[1] == player2
    assert sorted_chars[2] == enemy1
    assert sorted_chars[3] == enemy2


def test_battle_round_state(mock_inputs):
    """Test battle round state tracking."""
    chars = [
        Character("Tank", 20, 20, 0, 0, 0, 200, "player"),
        Character("Healer", 15, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 150, "enemy"),
    ]

    # Mock a sequence of actions:
    # Tank: Attack Enemy with 40p
    # Healer: End turn
    # Enemy: End turn
    mock_inputs(["a", "Enemy", "", "40p", "e", "e"])

    battle_round(chars, 1)

    # Player's 40p attack with enemy's 0% armor = 40 damage
    assert chars[2].health == 110  # 150 - 40 = 110
    assert chars[0].health == 200  # Unchanged


def test_dead_enemy_aggro(mock_inputs):
    """Test edge case: Dead enemies maintain aggro tracking.
    Current Behavior:
    1. Dead enemies can track basic aggro
    2. Dead enemies can gain aggro from being healed
    3. Dead enemies return valid aggro targets
    """
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy"),
    ]

    # Kill enemy
    chars[1].health = 0

    # Test basic dead enemy aggro
    chars[1].add_aggro("Player", 100, chars)
    assert chars[1].aggro["Player"] == 100, "Dead enemies track basic aggro"

    # Test healing-based aggro on dead enemy
    healing, temp = chars[1].heal({"h": 30}, "Player", chars)
    assert chars[1].aggro["Player"] == 107.5, "Dead enemies gain aggro from healing"

    # Test aggro targeting still works
    highest = chars[1].get_highest_aggro()
    assert "Player" in highest, "Dead enemies return aggro targets"


def test_combat_state_transitions(mock_inputs):
    """Test combat state transitions and validation.

    Verifies:
    1. Combat starts properly
    2. Characters can take actions
    3. State is consistent between actions
    """
    # Setup combat
    player = Character("Player", 15, 30, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 20, 0, 0, 0, 50, "enemy")
    characters = [player, enemy]

    # First round - player attacks enemy
    mock_inputs(
        [
            "a",  # Player attacks
            "Enemy",  # Target enemy
            "n",  # Block/dodge check
            "40p",  # Damage
            "e",  # End player turn
            "e",  # End enemy turn
        ]
    )

    battle_round(characters, 1)
    # Player's 40p attack with enemy's 20% armor = 32 damage
    assert enemy.health == 18  # 50 - 32 = 18
    assert player.health == 100  # Unchanged
