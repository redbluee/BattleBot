import pytest
from Battle import Character, battle_round

def test_basic_targeting():
    """Test basic targeting mechanics."""
    chars = [
        Character("Player1", 20, 0, 0, 0, 0, 100, "player"),
        Character("Player2", 15, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    ]
    
    # Test cross-team targeting
    if hasattr(chars[2], "aggro"):
        chars[2].add_aggro("Player1", 100, chars)
        assert "Player1" in chars[2].aggro, "Can target across teams"

def test_aggro_targeting():
    """Test aggro-based targeting system."""
    chars = [
        Character("Player1", 20, 0, 0, 0, 0, 100, "player"),
        Character("Player2", 15, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    ]
    
    if hasattr(chars[2], "aggro"):
        # Multiple targets
        chars[2].add_aggro("Player1", 100, chars)
        chars[2].add_aggro("Player2", 50, chars)
        
        # Highest aggro targeting
        highest = chars[2].get_highest_aggro()
        assert "Player1" in highest, "Targets highest aggro"

def test_targeting_restrictions():
    """Test targeting restrictions and limitations."""
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    ]
    
    # Dead target
    chars[0].health = 0
    if hasattr(chars[1], "aggro"):
        chars[1].add_aggro("Player", 100, chars)
        assert chars[1].aggro["Player"] == 100, "Can target dead characters with modified aggro"
        
        # Dead attacker
        chars[1].health = 0
        chars[1].add_aggro("Player", 50, chars)
        assert isinstance(chars[1].get_highest_aggro(), list), "Dead characters maintain targeting"

def test_empty_aggro():
    """Test behavior when aggro dict is empty."""
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    ]
    
    # Test empty aggro dict
    assert chars[1].get_highest_aggro() == "Aggro: none", "Empty aggro dict should return 'Aggro: none'"
    
    # Test zero/negative aggro
    chars[1].add_aggro("Player", 0, chars)
    assert chars[1].get_highest_aggro() == "Aggro: none", "Zero aggro should return 'Aggro: none'"
    
    chars[1].add_aggro("Player", -10, chars)
    assert chars[1].get_highest_aggro() == "Aggro: none", "Negative aggro should return 'Aggro: none'"
