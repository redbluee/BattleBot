import pytest
from Battle import Character


def test_basic_aggro_generation():
    """Test basic aggro generation from different sources.

    Verifies:
    1. Direct aggro ('g' type)
    2. Damage-based aggro
    3. Healing-based aggro
    4. Aggro accumulation
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Test direct aggro
    enemy.calculate_damage({"g": 50}, "Player", characters)
    assert enemy.aggro["Player"] == 50, "Direct aggro should be added"

    # Test damage aggro
    enemy.calculate_damage({"p": 20}, "Player", characters)
    assert enemy.aggro["Player"] == 70, "Damage should add to aggro"

    # Test healing aggro
    player.health = 60
    player.heal({"h": 40}, "Player", characters)
    assert enemy.aggro["Player"] == 80, "Healing should generate aggro"


def test_aggro_from_healing():
    """Test aggro generation from healing actions.

    Verifies:
    1. Effective healing generates correct aggro
    2. Overhealing doesn't generate extra aggro
    3. Self-healing generates aggro
    4. Temp HP doesn't generate aggro
    """
    # Setup
    healer = Character("Healer", 10, 0, 0, 0, 0, 100, "player")
    target = Character("Target", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [healer, target, enemy]

    # Test effective healing
    target.health = 60
    target.heal({"h": 40}, "Healer", characters)
    assert enemy.aggro["Healer"] == 10.0, "Aggro = healing/4"

    # Test overhealing
    target.heal({"h": 40}, "Healer", characters)
    assert enemy.aggro["Healer"] == 10.0, "No aggro from overhealing"

    # Test self-healing
    healer.health = 60
    healer.heal({"h": 40}, "Healer", characters)
    assert enemy.aggro["Healer"] == 20.0, "Self-healing generates aggro"

    # Test temp HP
    target.heal({"t": 30}, "Healer", characters)
    assert enemy.aggro["Healer"] == 20.0, "Temp HP doesn't generate aggro"


def test_aggro_edge_cases():
    """Test edge cases in aggro generation.

    Current Behavior:
    1. Negative damage generates negative aggro
    2. Zero damage/healing generates no aggro
    3. Aggro persists after character death
    4. No cap on aggro accumulation
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Test negative aggro
    enemy.calculate_damage({"g": -50}, "Player", characters)
    assert enemy.aggro["Player"] == -50, "Negative aggro possible"

    # Test zero values
    enemy.calculate_damage({"p": 0}, "Player", characters)
    assert enemy.aggro["Player"] == -50, "Zero damage = no aggro"

    # Test post-death aggro
    enemy.health = 0
    enemy.calculate_damage({"g": 50}, "Player", characters)
    assert enemy.aggro["Player"] == 0, "Dead enemies shouldn't track aggro"


def test_targeting_mechanics():
    """Test target selection based on aggro.

    Future Implementation:
    1. Add target selection logic
    2. Consider range/distance factors
    3. Add targeting restrictions
    4. Implement threat multipliers
    """
    # Setup for future targeting system
    tank = Character("Tank", 10, 50, 0, 0, 0, 200, "player")
    healer = Character("Healer", 10, 0, 0, 0, 0, 100, "player")
    dps = Character("DPS", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [tank, healer, dps, enemy]

    # Document current targeting behavior
    enemy.calculate_damage({"g": 100}, "Tank", characters)
    enemy.calculate_damage({"g": 50}, "Healer", characters)
    enemy.calculate_damage({"g": 75}, "DPS", characters)

    assert enemy.aggro["Tank"] == 100, "Tank should have highest aggro"
    assert enemy.aggro["DPS"] == 75, "DPS should have medium aggro"
    assert enemy.aggro["Healer"] == 50, "Healer should have lowest aggro"
