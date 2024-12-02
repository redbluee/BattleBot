import pytest
from Battle import Character

def test_basic_character_creation():
    """Test basic character creation with default values."""
    char = Character(
        name="TestChar",
        initiative=20,
        armor=10,
        arcane_resist=0,
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player"
    )
    assert char.name == "TestChar", "Name should match"
    assert char.initiative == 20, "Initiative should match"
    assert char.armor == 10, "Armor should match"
    assert char.arcane_resist == 0, "Arcane resist should match"
    assert char.light_resist == 0, "Light resist should match"
    assert char.nature_resist == 0, "Nature resist should match"
    assert char.health == 100, "Health should match max_health"
    assert char.max_health == 100, "Max health should match"
    assert char.temp_hp == 0, "Temp HP should start at 0"
    assert char.tag == "player", "Tag should match"

def test_character_creation_enemy():
    """Test enemy character creation with aggro initialization."""
    char = Character(
        name="TestEnemy",
        initiative=15,
        armor=20,
        arcane_resist=10,
        light_resist=10,
        nature_resist=10,
        max_health=150,
        tag="enemy"
    )
    assert char.name == "TestEnemy", "Name should match"
    assert char.tag == "enemy", "Tag should match"
    assert hasattr(char, "aggro"), "Enemy should have aggro attribute"
    assert isinstance(char.aggro, dict), "Aggro should be a dictionary"
    assert len(char.aggro) == 0, "Enemy should start with empty aggro dict"

def test_character_creation_numeric_inputs():
    """Test character creation with different numeric inputs."""
    # Integer inputs
    char = Character(
        name="TestChar",
        initiative=20,
        armor=10,
        arcane_resist=0,
        light_resist=0,
        nature_resist=0,
        max_health=100,
        tag="player"
    )
    assert char.initiative == 20, "Initiative should be preserved"
    assert char.armor == 10, "Armor should be preserved"
    assert char.arcane_resist == 0, "Arcane resist should be preserved"
    assert char.max_health == 100, "Max health should be preserved"
    
    # Float inputs
    char = Character(
        name="TestChar",
        initiative=20.5,
        armor=10.5,
        arcane_resist=0.5,
        light_resist=0.5,
        nature_resist=0.5,
        max_health=100.5,
        tag="player"
    )
    assert char.initiative == 20.5, "Initiative should accept float"
    assert char.armor == 10.5, "Armor should accept float"
    assert char.arcane_resist == 0.5, "Arcane resist should accept float"
    assert char.max_health == 100.5, "Max health should accept float"
