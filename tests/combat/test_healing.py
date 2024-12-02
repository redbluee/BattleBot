import pytest
from Battle import Character

def test_healing_calculation():
    """Test basic healing calculation."""
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    char.health = 50  # Set initial health
    
    # Test regular healing
    healing, temp = char.heal({"h": 30})
    assert healing == 30, "Regular healing works"
    assert char.health == 80, "Health increased correctly"
    
    # Test healing at max health
    char.health = char.max_health
    healing, temp = char.heal({"h": 30})
    assert healing == 0, "No healing when at max health"

def test_temp_healing():
    """Test temporary HP mechanics."""
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Test temp HP application
    healing, temp = char.heal({"t": 30})
    assert temp == 30, "Temp HP applied"
    assert char.temp_hp == 30, "Temp HP stored correctly"
    
    # Test temp HP stacking
    healing, temp = char.heal({"t": 20})
    assert temp == 20, "Additional temp HP applied"
    assert char.temp_hp == 50, "Temp HP stacks"

def test_healing_edge_cases():
    """Test healing edge cases."""
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Test healing dead character
    char.health = 0
    healing, temp = char.heal({"h": 50})
    assert healing == 50, "Can heal dead character"
    assert char.health == 50, "Dead character revived"
    
    # Test empty healing dict
    healing, temp = char.heal({})
    assert healing == 0, "Empty healing dict heals nothing"
    assert temp == 0, "Empty healing dict adds no temp HP"
