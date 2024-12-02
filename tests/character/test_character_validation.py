import pytest
from Battle import Character

def test_character_creation_validation():
    """Test character creation validation.
    
    Current Behavior:
    1. Name validation: accepts any string
    2. Stats: stored as provided, no type conversion
    3. No range validation on stats
    4. Tag system: "player" or "enemy"
    """
    # Test name validation
    char = Character("", 10, 0, 0, 0, 0, 100, "player")
    assert isinstance(char.name, str), "Empty name handled"
    
    char = Character("Test123!@#", 10, 0, 0, 0, 0, 100, "player")
    assert isinstance(char.name, str), "Special characters handled"
    
    # Test stat validation - values stored as provided
    char = Character(
        "Test",
        initiative="10",  # String initiative stored as-is
        armor=-50,        # Negative armor allowed
        arcane_resist=150,  # Over 100% resist allowed
        light_resist=0.5,   # Float resist allowed
        nature_resist=None,  # None value allowed
        max_health=100,
        tag="player"
    )
    assert char.initiative == "10", "String initiative preserved"
    assert char.armor == -50, "Negative armor allowed"
    assert char.arcane_resist == 150, "Over 100% resist allowed"
    assert char.light_resist == 0.5, "Float resist allowed"
    assert char.nature_resist is None, "None value allowed"

def test_stat_modification_validation():
    """Test stat modification validation."""
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Direct stat modification allowed
    char.armor = -100
    assert char.armor == -100, "Negative armor allowed"
    
    char.arcane_resist = 200
    assert char.arcane_resist == 200, "Over 100% resist allowed"

def test_state_validation():
    """Test state validation."""
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Health can be negative
    char.health = -50
    assert char.health == -50, "Negative health allowed"
    
    # Health can exceed max_health
    char.health = 200
    assert char.health == 200, "Health over max allowed"

def test_tag_system_validation():
    """Test tag system validation."""
    # Valid tags
    char1 = Character("Test1", 10, 0, 0, 0, 0, 100, "player")
    assert char1.tag == "player", "Player tag accepted"
    
    char2 = Character("Test2", 10, 0, 0, 0, 0, 100, "enemy")
    assert char2.tag == "enemy", "Enemy tag accepted"
    assert hasattr(char2, "aggro"), "Enemy has aggro dict"
