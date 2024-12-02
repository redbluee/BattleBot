import pytest
from Battle import Character

def test_health_range_validation():
    """Test health value ranges.
    
    Current Behavior:
    1. Health can be negative
    2. No automatic clamping
    3. Max health is a soft limit
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Test health can be negative
    char.health = -10
    assert char.health == -10, "Health can be negative"
    
    # Test health can exceed max
    char.health = 150
    assert char.health == 150, "Health can exceed max"

def test_health_state_consistency():
    """Test health state consistency.
    
    Current Behavior:
    1. Health is independent of other stats
    2. Direct modification allowed
    3. No automatic state updates
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    initial_health = char.health
    
    # Health modification
    char.health = 50
    assert char.health == 50, "Direct health modification works"
    
    # Health independent of max_health
    char.max_health = 200
    assert char.health == 50, "Health unchanged when max_health changes"

def test_death_state():
    """Test death state behavior.
    
    Current Behavior:
    1. No automatic death state
    2. Can act at 0 or negative health
    3. Can receive healing at any health
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Can act at 0 health
    char.health = 0
    damage = char.calculate_damage({"p": 50})
    assert isinstance(damage, (int, float)), "Can deal damage at 0 health"
    
    # Can receive healing at 0 health
    healing, _ = char.heal({"h": 30})
    assert isinstance(healing, (int, float)), "Can receive healing at 0 health"
    
    # Can act at negative health
    char.health = -50
    damage = char.calculate_damage({"p": 50})
    assert isinstance(damage, (int, float)), "Can deal damage at negative health"
