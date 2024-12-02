import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import integers, text
from Battle import Character

# Test Strategies
# --------------
# Define reusable test data generators for property-based testing
valid_tags = st.sampled_from(['player', 'enemy'])  # Only allowed character types
valid_names = st.text(min_size=1, max_size=20)     # Non-empty names up to 20 chars
valid_resistances = integers(min_value=0, max_value=100)  # 0-100% resistance values
valid_health = integers(min_value=1, max_value=10000)     # Positive health values

# Basic Initialization Tests
# ------------------------
def test_character_initialization():
    """Test basic character creation with valid inputs.
    
    Verifies that:
    1. All attributes are correctly set
    2. Default values are properly initialized
    3. Player characters don't have aggro system
    """
    char = Character(
        name="TestChar",
        initiative=10,
        armor=20,
        arcane_resist=15,
        light_resist=15,
        nature_resist=15,
        max_health=100,
        tag="player"
    )
    
    # Basic attribute checks
    assert char.name == "TestChar"
    assert char.initiative == 10
    assert char.armor == 20
    assert char.arcane_resist == 15
    assert char.health == char.max_health == 100
    
    # Player-specific checks
    assert char.tag == "player"
    assert not hasattr(char, "aggro")  # Players don't have aggro

def test_enemy_character_initialization():
    """Test enemy-specific character creation features.
    
    Verifies that:
    1. Enemy characters are properly tagged
    2. Aggro system is initialized empty
    3. All attributes are set correctly
    """
    char = Character(
        name="Enemy1",
        initiative=15,
        armor=30,
        arcane_resist=20,
        light_resist=20,
        nature_resist=20,
        max_health=150,
        tag="enemy"
    )
    
    # Basic attribute checks
    assert char.name == "Enemy1"
    assert char.initiative == 15
    assert char.armor == 30
    assert char.arcane_resist == 20
    assert char.health == char.max_health == 150
    
    # Enemy-specific checks
    assert char.tag == "enemy"
    assert hasattr(char, "aggro")
    assert char.aggro == {}  # Empty aggro dict

# Input Validation Tests
# --------------------
def test_character_validation():
    """Test input validation rules for character creation.
    
    Current Implementation:
    1. String inputs are converted to appropriate types
    2. No validation for negative values
    3. No validation for tag values
    """
    # Test numeric conversion
    char = Character(
        name="Test",
        initiative="10",  # String
        armor="50",      # String
        arcane_resist="25",
        light_resist="0",
        nature_resist="0",
        max_health="100",
        tag="player"
    )
    
    # Values should be converted to integers
    assert isinstance(char.initiative, int)
    assert isinstance(char.armor, int)
    assert isinstance(char.max_health, int)
    
    # Test non-string name/tag
    char = Character(123, 10, 0, 0, 0, 0, 100, 456)
    assert char.name == "123"  # Converted to string
    assert char.tag == "456"   # Converted to string

# Property-Based Tests
# ------------------
@given(
    name=valid_names,
    initiative=integers(min_value=-100, max_value=100),
    armor=integers(min_value=-100, max_value=100),
    arcane=valid_resistances,
    light=valid_resistances,
    nature=valid_resistances,
    health=valid_health,
    tag=valid_tags
)
def test_valid_character_creation(name, initiative, armor, arcane, light, nature, health, tag):
    """Test character creation with randomly generated inputs.
    
    Verifies that:
    1. Character creation succeeds with various inputs
    2. All attributes are set correctly
    3. Type conversion happens as expected
    """
    char = Character(name, initiative, armor, arcane, light, nature, health, tag)
    
    # Check type conversion
    assert isinstance(char.name, str)
    assert isinstance(char.initiative, int)
    assert isinstance(char.armor, int)
    assert isinstance(char.arcane_resist, int)
    assert isinstance(char.max_health, int)
    assert isinstance(char.tag, str)
    
    # Check values
    assert char.name == str(name)
    assert char.initiative == int(initiative)
    assert char.armor == int(armor)
    assert char.arcane_resist == int(arcane)
    assert char.max_health == int(health)
    assert char.tag == str(tag)

@given(health=integers(max_value=0))
def test_invalid_health(health):
    """Test health validation.
    
    Current Implementation:
    1. No validation for non-positive health
    2. Values are converted to int
    """
    char = Character("Test", 10, 0, 0, 0, 0, health, "player")
    assert char.max_health == int(health)
    assert char.health == int(health)

@given(
    resistance_type=st.sampled_from(['armor', 'arcane_resist', 'light_resist', 'nature_resist']),
    negative_value=integers(min_value=-100, max_value=-1)
)
def test_negative_resistances(resistance_type, negative_value):
    """Test resistance validation.
    
    Current Implementation:
    1. No validation for negative resistances
    2. Values are converted to int
    """
    kwargs = {
        'name': 'Test',
        'initiative': 10,
        'armor': 0,
        'arcane_resist': 0,
        'light_resist': 0,
        'nature_resist': 0,
        'max_health': 100,
        'tag': 'player'
    }
    kwargs[resistance_type] = negative_value
    
    char = Character(**kwargs)
    assert getattr(char, resistance_type) == int(negative_value)

# Aggro System Tests
# ----------------
def test_add_aggro():
    """Test the enemy aggro system.
    
    Verifies that:
    1. Enemies can track aggro
    2. Only players generate aggro
    3. Aggro accumulates correctly
    """
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    player1 = Character("Player1", 10, 0, 0, 0, 0, 100, "player")
    player2 = Character("Player2", 10, 0, 0, 0, 0, 100, "player")
    characters = [enemy, player1, player2]
    
    # Add aggro from players
    enemy.add_aggro("Player1", 50, characters)
    enemy.add_aggro("Player2", 30, characters)
    enemy.add_aggro("Player1", 20, characters)
    
    assert enemy.aggro["Player1"] == 70
    assert enemy.aggro["Player2"] == 30

def test_get_highest_aggro():
    """Test highest aggro calculation.
    
    Verifies that:
    1. Correct highest aggro target is found
    2. Multiple equal targets are all returned
    3. No aggro returns appropriate message
    """
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    player1 = Character("Player1", 10, 0, 0, 0, 0, 100, "player")
    player2 = Character("Player2", 10, 0, 0, 0, 0, 100, "player")
    characters = [enemy, player1, player2]
    
    # Test no aggro
    assert enemy.get_highest_aggro() == "Aggro: none"
    
    # Test single highest
    enemy.add_aggro("Player1", 50, characters)
    enemy.add_aggro("Player2", 30, characters)
    assert enemy.get_highest_aggro() == ["Player1"]
    
    # Test multiple equal highest
    enemy.add_aggro("Player2", 20, characters)
    assert sorted(enemy.get_highest_aggro()) == ["Player1", "Player2"]
