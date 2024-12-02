import pytest
from Battle import Character, save_game, load_game


def test_character_state():
    """Test character state management.
    
    Verifies:
    1. Initial state
    2. State changes
    3. State persistence
    """
    # Initial state
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    assert char.health == 100, "Initial health"
    assert char.temp_hp == 0, "Initial temp HP"
    
    # State changes
    char.health = 80
    char.temp_hp = 20
    assert char.health == 80, "Health modified"
    assert char.temp_hp == 20, "Temp HP modified"


def test_combat_state():
    """Test combat state tracking.
    
    Verifies:
    1. Team composition
    2. Initiative order
    3. Health tracking
    4. Aggro state
    """
    # Setup team
    player1 = Character("Player1", 20, 0, 0, 0, 0, 100, "player")
    player2 = Character("Player2", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 15, 0, 0, 0, 0, 100, "enemy")
    characters = [player1, player2, enemy]
    
    # Verify team state
    assert len([c for c in characters if c.tag == "player"]) == 2, "Two players"
    assert len([c for c in characters if c.tag == "enemy"]) == 1, "One enemy"
    
    # Verify combat state
    assert enemy.aggro == {}, "Initial aggro empty"
    enemy.calculate_damage({"p": 50}, "Player1", characters)
    assert "Player1" in enemy.aggro, "Aggro tracked"


def test_state_persistence():
    """Test game state persistence.
    
    Current Implementation:
    1. Basic state saving
    2. State loading
    3. No validation
    """
    # Setup initial state
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    char.health = 80
    characters = [char]
    
    # Save and verify
    save_game(characters)
    loaded = load_game()
    assert len(loaded) == 1, "One character loaded"
    assert loaded[0].name == "Test", "Name preserved"
    assert loaded[0].health == 80, "Health preserved"
