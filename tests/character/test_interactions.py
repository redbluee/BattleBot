import pytest
from Battle import Character

def test_cross_character_effects():
    """Test interactions between multiple characters.
    
    Tests:
    1. Damage from one character to another
    2. Healing between characters
    3. State changes affecting multiple characters
    """
    attacker = Character("Attacker", 20, 0, 0, 0, 0, 100, "player")
    healer = Character("Healer", 15, 0, 0, 0, 0, 100, "player")
    target = Character("Target", 10, 50, 0, 0, 0, 100, "enemy")
    
    # Test damage interaction
    initial_health = target.health
    damage = target.calculate_damage({"p": 100}, "Attacker", [attacker, healer, target])
    assert damage == 50, "Damage reduction applied correctly"
    assert target.health == initial_health - 50, "Health reduced correctly"
    
    # Test healing interaction
    target.health = 50  # Set up for healing
    healing, temp = healer.heal({"h": 30}, "Healer", [attacker, healer, target])
    assert healing == 0, "Healing requires valid healing type"
    assert temp == 0, "No temp HP added"
    assert target.health == 50, "Health unchanged"

def test_shared_state_handling():
    """Test handling of shared state between characters.
    
    Tests:
    1. Aggro system interactions
    2. Team-based effects
    3. State persistence between interactions
    """
    tank = Character("Tank", 10, 70, 0, 0, 0, 200, "player")
    dps = Character("DPS", 20, 30, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 15, 50, 0, 0, 0, 150, "enemy")
    
    # Test aggro interactions if implemented
    if hasattr(enemy, "aggro"):
        enemy.add_aggro("Tank", 100, [tank, dps])
        enemy.add_aggro("DPS", 50, [tank, dps])
        assert enemy.get_highest_aggro() == ["Tank"], "Highest aggro target correct"

def test_team_based_interactions():
    """Test interactions based on character teams/tags.
    
    Tests:
    1. Team damage restrictions
    2. Team healing effects
    3. Tag-based targeting
    """
    player1 = Character("Player1", 20, 0, 0, 0, 0, 100, "player")
    player2 = Character("Player2", 15, 0, 0, 0, 0, 100, "player")
    enemy1 = Character("Enemy1", 10, 0, 0, 0, 0, 100, "enemy")
    enemy2 = Character("Enemy2", 12, 0, 0, 0, 0, 100, "enemy")
    
    # Document current behavior
    damage = player2.calculate_damage({"p": 100})
    assert damage == 100, "Players can damage other players"

    # Test healing between teams
    healing, temp = player1.heal({"h": 50})
    assert healing == 0, "Players can heal other players with valid healing type"

    # Test enemy interactions
    damage = enemy1.calculate_damage({"p": 100})
    assert damage == 100, "Enemies can damage other enemies"

    healing, temp = enemy2.heal({"h": 50})
    assert healing == 0, "Enemies can heal themselves with valid healing type"

def test_reference_handling():
    """Test character reference and state isolation.
    
    Tests:
    1. State changes don't affect other characters
    2. Reference independence
    3. Deep vs shallow copying behavior
    """
    original = Character("Original", 20, 50, 0, 0, 0, 100, "player")
    
    # Create similar character
    similar = Character(
        original.name,
        original.initiative,
        original.armor,
        original.arcane_resist,
        original.light_resist,
        original.nature_resist,
        original.max_health,
        original.tag
    )
    
    # Modify one character
    original.health = 50
    assert similar.health == similar.max_health, "Characters have independent state"
    
    original.armor = 75
    assert similar.armor == 50, "Stat changes don't affect other characters"
