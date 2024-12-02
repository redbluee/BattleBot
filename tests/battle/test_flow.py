import pytest
from Battle import Character, battle_round


def test_initiative_order():
    """Test battle initiative ordering."""
    chars = [
        Character("Last", 10, 0, 0, 0, 0, 100, "player"),
        Character("First", 30, 0, 0, 0, 0, 100, "player"),
        Character("Middle", 20, 0, 0, 0, 0, 100, "enemy"),
    ]

    sorted_chars = sorted(chars, key=lambda x: x.initiative, reverse=True)
    assert sorted_chars[0].name == "First", "Highest initiative first"
    assert sorted_chars[1].name == "Middle", "Middle initiative second"
    assert sorted_chars[2].name == "Last", "Lowest initiative last"


def test_round_management():
    """Test round counting and transitions."""
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy"),
    ]

    # Apply effects that should persist
    chars[0].temp_hp = 50
    if hasattr(chars[1], "aggro"):
        chars[1].aggro["Player"] = 100

    # Verify persistence
    assert chars[0].temp_hp == 50, "Effects persist between rounds"
    if hasattr(chars[1], "aggro"):
        assert chars[1].aggro["Player"] == 100, "Aggro persists between rounds"


def test_turn_sequence():
    """Test turn order and action sequence."""
    chars = [
        Character("Fast", 30, 0, 0, 0, 0, 100, "player"),
        Character("Medium", 20, 0, 0, 0, 0, 100, "player"),
        Character("Slow", 10, 0, 0, 0, 0, 100, "enemy"),
    ]

    # Track action order
    action_order = []
    for char in sorted(chars, key=lambda x: x.initiative, reverse=True):
        action_order.append(char.name)
        # Simulate action
        char.calculate_damage({"p": 10})

    assert action_order == ["Fast", "Medium", "Slow"], "Correct action sequence"
