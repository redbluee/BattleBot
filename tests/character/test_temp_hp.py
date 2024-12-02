import pytest
from Battle import Character


def test_temp_hp_stacking():
    """Test temporary HP stacking mechanics.

    Tests:
    1. Basic temp HP application
    2. Multiple temp HP stacking
    3. No cap on accumulation
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")

    # Single temp HP application
    _, temp1 = char.heal({"t": 30})
    assert temp1 == 30, "First temp HP application"
    assert char.temp_hp == 30, "Temp HP stored correctly"

    # Multiple temp HP applications
    _, temp2 = char.heal({"t": 20})
    assert temp2 == 20, "Second temp HP application"
    assert char.temp_hp == 50, "Temp HP stacks additively"

    # Large temp HP value
    _, temp3 = char.heal({"t": 1000})
    assert temp3 == 1000, "Large temp HP application"
    assert char.temp_hp == 1050, "No cap on temp HP stacking"


def test_temp_hp_damage_absorption():
    """Test how temporary HP absorbs damage.

    Tests:
    1. Partial temp HP absorption
    2. Complete temp HP depletion
    3. Damage overflow to regular HP
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")

    # Setup temp HP
    char.heal({"t": 30})
    assert char.temp_hp == 30, "Initial temp HP"

    # Partial absorption
    damage = char.calculate_damage({"p": 20})
    assert damage == 0, "Temp HP absorbs all damage"
    assert char.temp_hp == 10, "Temp HP reduced by damage"

    # Complete depletion
    damage = char.calculate_damage({"p": 15})
    assert damage == 5, "Damage overflow to regular HP"
    assert char.temp_hp == 0, "Temp HP fully depleted"
    assert char.health == 95, "Health reduced by overflow"


def test_temp_hp_damage_types():
    """Test temp HP interaction with damage types.

    Tests:
    1. Physical damage absorption
    2. Magical damage absorption
    3. Mixed damage types
    """
    char = Character("Test", 10, 50, 50, 50, 50, 100, "player")
    char.heal({"t": 50})  # Add temp HP

    # Physical damage
    damage = char.calculate_damage({"p": 100})  # 50% reduction = 50 damage
    assert damage == 0, "Temp HP absorbs physical damage"
    assert char.temp_hp == 0, "Temp HP fully absorbed"
    assert char.health == 100, "Health unchanged"

    # Magical damage
    char.heal({"t": 50})  # Reset temp HP
    damage = char.calculate_damage(
        {"a": 100, "l": 100}
    )  # 50% reduction each = 50 + 50 = 100 damage
    assert damage == 50, "Temp HP absorbs part of magical damage"
    assert char.temp_hp == 0, "Temp HP is depleted"
    assert char.health == 50, "Health reduced by remaining magical damage"


def test_temp_hp_edge_cases():
    """Test temp HP edge cases and limitations.

    Tests:
    1. Zero temp HP healing
    2. Negative temp HP values
    3. Temp HP with dead character
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")

    # Zero temp HP
    _, temp = char.heal({"t": 0})
    assert temp == 0, "Zero temp HP handled"
    assert char.temp_hp == 0, "No temp HP added"

    # Negative temp HP (if supported)
    _, temp = char.heal({"t": -50})
    assert temp == -50, "Negative temp HP allowed"
    assert char.temp_hp == -50, "Negative temp HP stored"

    # Dead character
    char.health = 0
    _, temp = char.heal({"t": 50})
    assert isinstance(temp, (int, float)), "Dead characters can receive temp HP"
