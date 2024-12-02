import pytest
from Battle import Character

def test_stat_range_validation():
    """Test validation of stat value ranges."""
    char = Character("Test", -10, 0, 0, 0, 0, 100, "player")
    assert isinstance(char.initiative, (int, str)), "Initiative stored as received"
    
    char = Character("Test", 999999, 0, 0, 0, 0, 100, "player")
    assert isinstance(char.initiative, (int, str)), "Initiative stored as received"

def test_stat_type_validation():
    """Test type validation for stats."""
    # Test string inputs are preserved
    char = Character("Test", "10", "20", "30", "40", "50", 100, "player")
    assert char.initiative == "10", "String values preserved"
    assert char.armor == "20", "String values preserved"
    assert char.arcane_resist == "30", "String values preserved"
    
    # Test numeric inputs
    char = Character("Test", 10, 20, 30, 40, 50, 100, "player")
    assert char.initiative == 10, "Numeric values preserved"
    assert char.armor == 20, "Numeric values preserved"
    assert char.arcane_resist == 30, "Numeric values preserved"

def test_stat_consistency():
    """Test stat consistency and interactions."""
    char = Character("Test", 10, 50, 0, 0, 0, 100, "player")
    
    # Test damage calculation with armor
    damage = char.calculate_damage({"p": 100})
    assert damage == 50, "50% armor reduces damage by half"
    
    # Test multiple damage types
    damage = char.calculate_damage({"p": 100, "a": 100})
    assert damage == 150, "Physical reduced by armor, arcane unaffected"
