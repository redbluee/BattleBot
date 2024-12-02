import pytest
from Battle import Character

def test_damage_calculation():
    """Test basic damage calculation."""
    char = Character("Test", 10, 50, 0, 0, 0, 100, "player")
    
    # Test physical damage with armor
    damage = char.calculate_damage({"p": 100})
    assert damage == 50, "50% armor reduces damage by half"
    
    # Test non-physical damage types
    damage = char.calculate_damage({"a": 100})
    assert damage == 100, "No reduction for arcane damage with no resist"

def test_damage_resistance():
    """Test damage resistance mechanics."""
    char = Character("Test", 10, -50, 0, 0, 0, 100, "player")
    
    # Test negative armor increases damage
    damage = char.calculate_damage({"p": 100})
    assert damage == 150, "Negative armor increases damage by 50%"
    
    # Test high armor
    char.armor = 75
    damage = char.calculate_damage({"p": 100})
    assert damage == 25, "75% armor reduces damage to 25%"

def test_damage_edge_cases():
    """Test damage calculation edge cases."""
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Test empty damage dict
    result = char.calculate_damage({})
    assert result == 0, "Empty damage dict deals no damage"
    
    # Test unknown damage type
    result = char.calculate_damage({"invalid": 100})
    assert result == 100, "Unknown damage type deals full damage"

    # Division by zero
    char.armor = 0
    result = char.calculate_damage({"p": 100})
    assert isinstance(result, (int, float)), "Division by zero handled"
    
    # Test very high armor (99%)
    char.armor = 99
    result = char.calculate_damage({"p": 100})
    assert result == 1, "Very high armor reduces damage to minimum"

def test_generate_aggro_damage():
    """Test the 'g' damage type that generates aggro without dealing damage."""
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    ]
    
    # Test 'g' type damage on enemy
    damage = chars[1].calculate_damage({"g": 50}, attacker_name="Player", characters=chars)
    assert damage == 0, "'g' type damage should deal no actual damage"
    assert chars[1].get_highest_aggro() == ["Player"], "'g' type damage should generate aggro"
    
    # Test 'g' type damage on player (should not generate aggro)
    damage = chars[0].calculate_damage({"g": 50}, attacker_name="Enemy", characters=chars)
    assert damage == 0, "'g' type damage should deal no actual damage"
    assert not hasattr(chars[0], "aggro"), "Players should not have aggro attribute"
