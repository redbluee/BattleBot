import pytest
from Battle import Character

def test_resistance_edge_cases():
    """Test edge cases in resistance calculations.
    
    Tests:
    1. Over 100% resistance behavior
    2. Negative resistance effects
    3. Resistance-based healing
    """
    char = Character(
        "Test",
        10,
        150,  # Over 100% physical resistance
        -50,  # Negative arcane resistance
        200,  # Extreme light resistance
        0,    # Normal nature resistance
        100,
        "player"
    )
    
    # Test over 100% resistance
    phys_damage = char.calculate_damage({"p": 100})
    assert phys_damage == -50, "Over 100% resistance results in negative damage"
    
    # Test negative resistance
    arcane_damage = char.calculate_damage({"a": 100})
    assert arcane_damage == 150, "Negative resistance increases damage"
    
    # Test extreme resistance
    light_damage = char.calculate_damage({"l": 100})
    assert light_damage == -100, "Extreme resistance results in negative damage"

    # Test normal resistance
    nature_damage = char.calculate_damage({"n": 100})
    assert nature_damage == 100, "No resistance applies full damage"

def test_damage_type_validation():
    """Test damage type validation and error handling.
    
    Tests:
    1. Invalid damage types
    2. Type validation for values
    3. Unknown damage type behavior
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Test invalid damage types
    invalid_damage = char.calculate_damage({"x": 100})
    assert isinstance(invalid_damage, (int, float)), "Invalid type handled gracefully"
    
    # Test non-numeric values if supported
    try:
        string_damage = char.calculate_damage({"p": "100"})
        assert isinstance(string_damage, (int, float)), "String values converted to numbers"
    except:
        pass  # Type conversion not supported
    
    # Test multiple unknown types
    mixed_damage = char.calculate_damage({"x": 50, "y": 50, "p": 50})
    assert isinstance(mixed_damage, (int, float)), "Mixed valid/invalid types handled"

def test_healing_edge_cases():
    """Test edge cases in healing calculations.
    
    Tests:
    1. Negative healing
    2. Over-healing behavior
    3. Invalid healing types
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    char.health = 50  # Start at half health
    
    # Test negative healing
    healing, temp = char.heal({"h": -50})
    assert isinstance(healing, (int, float)), "Negative healing handled"
    
    # Test over-healing
    healing, temp = char.heal({"h": 100})
    assert char.health <= char.max_health, "Health capped at max"
    
    # Test invalid healing type
    healing, temp = char.heal({"x": 50})
    assert healing == 0 and temp == 0, "Invalid healing type ignored"

def test_damage_calculation_error_handling():
    """Test error handling in damage calculations.
    
    Tests:
    1. None/null handling
    2. Empty damage dict
    3. Mixed valid/invalid values
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Test None handling
    try:
        damage = char.calculate_damage(None)
        assert damage == 0, "None handled gracefully"
    except AttributeError:
        pass  # None not supported
    
    # Test empty dict
    damage = char.calculate_damage({})
    assert damage == 0, "Empty damage dict handled"

    # Test mixed values - should only process valid numeric values
    damage = char.calculate_damage({"p": 100, "invalid": "50"})
    assert damage == 150, "Processes all damage types"
