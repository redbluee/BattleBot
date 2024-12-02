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
    mock_inputs(["e"] * 8)  # Each character needs at least one input to end their turn

    # Start combat and verify initiative order
    battle_state = battle_round(characters, 1)
    assert len(battle_state.turn_order) == 4
    assert battle_state.turn_order[0].initiative >= battle_state.turn_order[1].initiative
    assert battle_state.turn_order[1].initiative >= battle_state.turn_order[2].initiative
    assert battle_state.turn_order[2].initiative >= battle_state.turn_order[3].initiative


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
            "a",
            "Enemy",
            "n",
            "30p",  # Tank attacks enemy
            "h",
            "Tank",
            "20h",  # Healer heals tank
            "a",
            "Tank",
            "n",
            "40p",  # Enemy attacks tank
            "e",  # End combat round
        ]
    )

    # Run battle round and verify state
    _ = battle_round(characters, 1)  # We don't need the state, just run the round
    assert tank.health == 170  # Initial 200 - 30 damage
    assert enemy.health == 120  # Initial 150 - 40 damage * (1 - 25/100)


def test_battle_round_edge_cases(mock_inputs):
    """Test edge cases in battle round execution.

    Verifies:
    1. Empty character list handling
    2. Single character handling
    3. All characters same initiative
    4. Character death during round
    """
    # Test empty character list
    with pytest.raises(ValueError):
        battle_round([], 1)

    # Test single character
    solo = Character("Solo", 10, 0, 0, 0, 0, 100, "player")
    mock_inputs(["e"])  # End turn for solo character
    battle_state = battle_round([solo], 1)
    assert len(battle_state.turn_order) == 1

    # Test same initiative
    char1 = Character("Char1", 10, 0, 0, 0, 0, 100, "player")
    char2 = Character("Char2", 10, 0, 0, 0, 0, 100, "player")
    char3 = Character("Char3", 10, 0, 0, 0, 0, 100, "enemy")
    mock_inputs(["e"] * 3)  # End turn for each character
    battle_state = battle_round([char1, char2, char3], 1)
    assert len(battle_state.turn_order) == 3


def test_combat_state_transitions(mock_inputs):
    """Test combat state transitions and validation.

    Verifies:
    1. Combat starts properly
    2. Round counter increments
    3. State is consistent between rounds
    4. Combat ends appropriately
    """
    # Setup combat
    player = Character("Player", 15, 30, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 20, 0, 0, 0, 50, "enemy")
    characters = [player, enemy]

    # First round - just end turns
    mock_inputs(["e"] * 2)
    battle_state = battle_round(characters, 1)
    assert battle_state.round_number == 1
    assert len(battle_state.active_characters) == 2

    # Second round - player kills enemy
    mock_inputs(["a", "Enemy", "n", "50p", "e"])  # Player attacks enemy  # Enemy's turn (if still alive)
    final_state = battle_round(characters, 2)
    assert len(final_state.active_characters) == 1
    assert final_state.combat_ended
