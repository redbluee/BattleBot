import pytest
from Battle import Character

def test_character_lifecycle():
    """Test character creation and basic state management.
    
    Current Implementation:
    1. Character creation with stats
    2. Basic state tracking
    3. Tag system
    """
    # Basic creation
    char = Character("Test", 10, 20, 30, 40, 50, 100, "player")
    assert char.name == "Test"
    assert char.initiative == 10
    assert char.armor == 20
    assert char.piercing == 30
    assert char.healing == 40
    assert char.temp_healing == 50
    assert char.max_health == 100
    assert char.health == 100
    assert char.temp_hp == 0
    assert char.tag == "player"

def test_character_state_transitions():
    """Test character state changes and transitions.
    
    Current Implementation:
    1. Health state changes
    2. Temp HP management
    3. Death state
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    
    # Health transitions
    char.health = 50
    assert char.health == 50, "Health reduction"
    
    char.health = 0
    assert char.health == 0, "Death state"
    
    char.health = 100
    assert char.health == 100, "Health restoration"
    
    # Temp HP transitions
    char.temp_hp = 50
    assert char.temp_hp == 50, "Temp HP gain"
    
    char.temp_hp = 0
    assert char.temp_hp == 0, "Temp HP loss"

def test_character_stat_management():
    """Test character stat modifications and constraints.
    
    Current Implementation:
    1. Stat modification
    2. No upper bounds
    3. Allows negative values
    """
    char = Character("Test", 10, 20, 30, 40, 50, 100, "player")
    
    # Initiative changes
    char.initiative = 20
    assert char.initiative == 20, "Initiative can be modified"
    
    # Armor changes
    char.armor = 40
    assert char.armor == 40, "Armor can be modified"
    
    # Negative stats
    char.piercing = -10
    assert char.piercing == -10, "Negative stats allowed"
    
    # Large values
    char.healing = 1000
    assert char.healing == 1000, "No upper bound on stats"

def test_character_tag_system():
    """Test character tagging and relationships.
    
    Current Implementation:
    1. Basic tag assignment
    2. Tag-based targeting
    3. No tag validation
    """
    # Tag assignment
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    neutral = Character("Neutral", 10, 0, 0, 0, 0, 100, "neutral")
    
    assert player.tag == "player", "Player tag"
    assert enemy.tag == "enemy", "Enemy tag"
    assert neutral.tag == "neutral", "Neutral tag"
    
    # Tag relationships
    chars = [player, enemy, neutral]
    player_chars = [c for c in chars if c.tag == "player"]
    enemy_chars = [c for c in chars if c.tag == "enemy"]
    
    assert len(player_chars) == 1, "One player character"
    assert len(enemy_chars) == 1, "One enemy character"
    
    # Custom tags
    custom = Character("Custom", 10, 0, 0, 0, 0, 100, "custom_tag")
    assert custom.tag == "custom_tag", "Custom tags allowed"
