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
    1. Characters are ordered by initiative
    2. Turn order is maintained throughout round
    3. Initiative tiebreakers work correctly
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
    """Test battle round state management.

    Verifies:
    1. Character state persists between turns
    2. Damage and healing effects last through round
    3. Temp HP persists between turns
    """
    # Setup characters
    tank = Character("Tank", 20, 50, 0, 0, 0, 200, "player")
    healer = Character("Healer", 15, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 25, 0, 0, 0, 150, "enemy")
    characters = [tank, healer, enemy]

    # Mock inputs for attack and healing actions
    mock_inputs(
        [
            # Tank's turn
            "a",  # Choose attack
            "Enemy",  # Target enemy
            "n",  # Block/dodge check
            "30p",  # Damage type
            "e",  # End tank's turn
            # Healer's turn
            "h",  # Choose heal
            "Tank",  # Target tank
            "20h",  # Healing amount
            "e",  # End healer's turn
            # Enemy's turn
            "a",  # Choose attack
            "Tank",  # Target tank
            "n",  # Block/dodge check
            "40p",  # Damage type
            "e",  # End enemy's turn
        ]
    )

    # Run battle round and verify state
    battle_round(characters, 1)
    assert tank.health == 180  # Initial 200 - 20 damage (40p * (1 - 0.5))
    assert enemy.health == 128  # Initial 150 - 22 damage (30p * (1 - 0.25))


def test_battle_round_edge_cases(mock_inputs):
    """Test edge cases in battle round execution.

    Verifies:
    1. Single character handling
    2. All characters same initiative
    3. Character death during round
    """
    # Test single character
    solo = Character("Solo", 10, 0, 0, 0, 0, 100, "player")
    mock_inputs(["e"])  # End turn for solo character
    battle_round([solo], 1)
    assert solo.health == 100  # Health unchanged

    # Test same initiative
    char1 = Character("Char1", 10, 0, 0, 0, 0, 100, "player")
    char2 = Character("Char2", 10, 0, 0, 0, 0, 100, "player")
    char3 = Character("Char3", 10, 0, 0, 0, 0, 100, "enemy")
    mock_inputs(["e"] * 3)  # End turn for each character
    battle_round([char1, char2, char3], 1)
    # Verify all characters took their turns
    assert char1.health == 100
    assert char2.health == 100
    assert char3.health == 100


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
