import pytest
from Battle import Character


def test_physical_damage_calculation():
    """Test physical damage calculation with armor.

    This test verifies that:
    1. Physical damage is properly reduced by armor percentage (50 armor = 50% reduction)
    2. The reduced damage is correctly applied to character's health
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=50,  # 50% damage reduction
        arcane_resist=0,
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player",
    )

    damage_dict = {"p": 100}  # 100 physical damage
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == 50, "Physical damage should be reduced by armor"
    assert target.health == 50, "Health should be reduced by physical damage"


def test_magical_damage_calculation():
    """Test magical damage types with different resistances."""
    target = Character(
        name="Target",
        initiative=10,
        armor=0,
        arcane_resist=25,  # 25% reduction
        light_resist=50,  # 50% reduction
        nature_resist=75,  # 75% reduction
        max_health=100,
        tag="player",
    )

    damage_dict = {"a": 100, "l": 100, "n": 100}  # arcane, light, nature
    actual_damage = target.calculate_damage(damage_dict)
    expected_damage = 75 + 50 + 25  # Based on respective resistances
    assert actual_damage == expected_damage, "Magical damage should be reduced by resistances"
    assert target.health == 0, "Health should be reduced to 0 by magical damage"


def test_magical_damage_edge_cases():
    """Test edge cases for magical damage calculation.
    
    Current Behavior:
    1. Resistances over 100% result in negative damage
       - 150% resistance = -50% damage (healing)
    2. Negative resistance validation not implemented
    
    Future Considerations:
    1. Should cap resistance at 100%
    2. Add validation for negative resistances
    3. Consider if negative damage should heal
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=0,
        arcane_resist=150,  # Over 100% resistance
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player",
    )

    damage_dict = {"a": 100}
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == -50, "Over 100% resistance results in negative damage (150% = -50% damage)"
    assert target.health == 100, "Negative damage does not currently heal"


def test_mixed_damage_types():
    """Test combinations of different damage types.

    Verifies:
    1. Multiple damage types are calculated correctly
    2. Different resistance types apply properly
    3. Total damage is sum of all reduced damages
    4. Physical and magical damage combine properly
    5. Health is clamped at 0
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=50,  # 50% physical reduction
        arcane_resist=25,  # 25% arcane reduction
        light_resist=75,  # 75% light reduction
        nature_resist=0,  # No nature reduction
        max_health=100,
        tag="player",
    )

    # Test mixed physical and magical damage
    damage_dict = {
        "p": 40,  # 20 after armor
        "a": 40,  # 30 after resist
        "l": 40,  # 10 after resist
        "n": 40,  # 40 (no resist)
    }
    actual_damage = target.calculate_damage(damage_dict)
    expected_damage = 100  # 20 + 30 + 10 + 40
    assert actual_damage == expected_damage, "Mixed damage types should combine properly"
    assert target.health == 0, "Health should be clamped at 0"


def test_zero_damage_cases():
    """Test edge cases with zero damage.

    Verifies:
    1. Zero damage input results in no damage
    2. 100% resistance blocks all damage
    3. Multiple zero damages combine correctly
    4. Mixed zero and non-zero damages work
    5. Health is clamped at 0
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=100,  # 100% physical reduction
        arcane_resist=0,
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player",
    )

    # Test zero damage input
    damage_dict = {"p": 0, "a": 0}
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == 0, "Zero damage should result in no damage"

    # Test 100% resistance
    damage_dict = {"p": 50}  # Should be reduced to 0
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == 0, "100% resistance should block all damage"
    assert target.health == 100, "No health should be lost"

    # Test mixed zero and non-zero
    damage_dict = {"p": 0, "a": 40}  # Physical blocked, arcane full
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == 40, "Only non-zero unresisted damage should apply"


def test_damage_calculation_error_handling():
    """Test error handling in damage calculation.

    NOTE: This test documents bugs in the original implementation:
    1. No validation for damage types (accepts any key)
    2. No type validation for damage values
    3. No error messages for invalid inputs
    4. Unknown damage types are applied without reduction

    These will be addressed in future refactoring.
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=50,
        arcane_resist=0,
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player",
    )

    # Test unknown damage type
    damage_dict = {"x": 50}  # Unknown type
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == 50, "Unknown damage type applied without reduction"

    # Test invalid damage value type
    damage_dict = {"p": "50"}  # String instead of number
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == 25, "String damage value converted to number"


def test_damage_types_proposed():
    """Test proposed cleanup of damage types.

    TODO: Implement after team review
    Proposed cleanup of damage types
    """
    # Only pure damage types should be accepted
    damage_input = "10p 5a 3l 2n"
    damage_dict, _ = parse_damage_input(damage_input)
    assert set(damage_dict.keys()) == {'p', 'a', 'l', 'n'}

    # 'g' type should be rejected
    with pytest.raises(ValueError):
        parse_damage_input("10g")

    # 't' type should be handled by separate system
    with pytest.raises(ValueError):
        parse_damage_input("5t")


def test_mixed_damage_types_original():
    """Test combinations of different damage types.

    Verifies:
    1. Multiple damage types are calculated correctly
    2. Different resistance types apply properly
    3. Total damage is sum of all reduced damages
    4. Physical and magical damage combine properly
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=50,
        arcane_resist=25,
        light_resist=0,
        nature_resist=75,
        max_health=100,
        tag="player",
    )

    # Mixed damage types
    damage_dict = {
        "p": 100,  # 50% reduction = 50 damage
        "a": 100,  # 25% reduction = 75 damage
        "n": 100,  # 75% reduction = 25 damage
    }
    actual_damage = target.calculate_damage(damage_dict)
    expected_damage = 50 + 75 + 25
    assert actual_damage == expected_damage, "Mixed damage types should be calculated correctly"


def test_zero_damage_cases_original():
    """Test edge cases with zero damage.

    Verifies:
    1. Zero damage input results in no damage
    2. 100% resistance blocks all damage
    3. Multiple zero damages combine correctly
    4. Mixed zero and non-zero damages work
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=100,  # 100% physical reduction
        arcane_resist=0,
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player",
    )

    # Test zero damage cases
    assert target.calculate_damage({"p": 0}) == 0, "Zero damage should result in zero"
    assert target.calculate_damage({"p": 100}) == 0, "100% resistance should block all damage"
    assert target.calculate_damage({"p": 0, "a": 0}) == 0, "Multiple zeros should combine to zero"
    
    # Mixed zero and non-zero
    damage_dict = {"p": 100, "a": 100}  # Physical blocked, arcane full
    actual_damage = target.calculate_damage(damage_dict)
    assert actual_damage == 100, "Only non-resisted damage should be applied"


def test_damage_calculation_error_handling_original():
    """Test error handling in damage calculation.

    NOTE: This test documents bugs in the original implementation:
    1. No validation for damage types (accepts any key)
    2. No type validation for damage values
    3. No error messages for invalid inputs
    4. Unknown damage types are applied without reduction

    These will be addressed in future refactoring.
    """
    target = Character(
        name="Target",
        initiative=10,
        armor=0,
        arcane_resist=0,
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player",
    )

    # Unknown damage type
    damage = target.calculate_damage({"x": 100})
    assert damage == 100, "Unknown damage type currently applies without reduction"

    # Mixed valid and invalid
    damage = target.calculate_damage({"p": 100, "x": 100})
    assert damage == 200, "Both valid and invalid damage types are processed"
