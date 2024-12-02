import pytest
from Battle import Character, parse_healing_input

def test_healing_system():
    """Test basic healing and temporary HP system."""
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    player.health = 60  # Take some damage first
    characters = [player]

    # Test regular healing
    healing, temp = player.heal({"h": 20}, "Player", characters)
    assert healing == 20, "Should heal 20 HP"
    assert temp == 0, "No temp HP added"
    assert player.health == 80, "Health should increase"

    # Test temp HP
    healing, temp = player.heal({"t": 30}, "Player", characters)
    assert healing == 0, "No regular healing"
    assert temp == 30, "Should add temp HP"
    assert player.temp_hp == 30, "Temp HP should be added"

def test_healing_edge_cases():
    """Test edge cases in healing mechanics.
    
    Current Implementation:
    1. Overhealing
       - Healing is capped at max health
       - Only effective healing generates aggro
    2. Mixed Healing
       - Regular healing and temp HP can be combined
       - Both types processed in same action
    3. Edge States
       - Can heal at 0 HP
       - Can heal at full HP (no effect)
       - Temp HP stacks additively
    """
    # Setup characters
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    enemy.health = 80  # Take some damage first
    characters = [player, enemy]

    # Test 1: Basic healing
    healing, temp = enemy.heal({"h": 40}, "Player", characters)
    assert healing == 20, "Healing capped at max health"
    assert enemy.health == 100, "Health capped at max"
    assert enemy.aggro["Player"] == 5.0, "Aggro based on effective healing (20/4)"

    # Test 2: Mixed healing types
    enemy.health = 60  # Reset to 60/100
    healing, temp = enemy.heal({"h": 30, "t": 20}, "Player", characters)
    assert healing == 30, "Regular healing applied"
    assert temp == 20, "Temp HP applied"
    assert enemy.health == 90, "Health increased"
    assert enemy.temp_hp == 20, "Temp HP added"
    assert enemy.aggro["Player"] == 12.5, "Aggro accumulates (5.0 + 30/4)"

    # Test 3: Edge states
    enemy.health = 0  # Test healing at 0 HP
    healing, temp = enemy.heal({"h": 50}, "Player", characters)
    assert healing == 50, "Can heal from 0 HP"
    assert enemy.health == 50, "Health restored from 0"
    assert enemy.aggro["Player"] == 25.0, "Aggro accumulates (5.0 + 7.5 + 50/4)"

    enemy.health = 100  # Test healing at full HP
    healing, temp = enemy.heal({"h": 30}, "Player", characters)
    assert healing == 0, "No healing when at full health"
    assert enemy.aggro["Player"] == 25.0, "No additional aggro when no effective healing"

def test_negative_healing_behavior():
    """Document current behavior of negative healing values.
    
    Current Implementation:
    - Negative healing values reduce health (acts like damage)
    - Negative temp HP reduces existing temp HP
    - Generates negative aggro based on healing amount
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Test negative regular healing
    enemy.health = 80
    healing, temp = enemy.heal({"h": -20}, "Player", characters)
    assert healing == -20, "Negative healing applied"
    assert enemy.health == 60, "Health reduced by negative healing"
    assert enemy.aggro["Player"] == -5.0, "Negative aggro from negative healing"

    # Test negative temp HP
    enemy.temp_hp = 30
    healing, temp = enemy.heal({"t": -10}, "Player", characters)
    assert temp == -10, "Negative temp HP applied"
    assert enemy.temp_hp == 20, "Temp HP reduced by negative value"

def test_healing_aggro_debug():
    """Debug test to understand healing aggro calculation.
    
    Current Behavior:
    - Healing is capped at max health (40 heal at 80/100 HP = 20 effective healing)
    - Aggro is based on effective healing amount (20 healing = 5 aggro)
    - No aggro generated when target is at full health
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Test overhealing aggro
    enemy.health = 80
    healing, _ = enemy.heal({"h": 40}, "Player", characters)
    assert healing == 20, "Only heals missing health"
    assert enemy.aggro["Player"] == 5.0, "Aggro based on effective healing"

    # Test full health aggro
    enemy.health = 100
    healing, _ = enemy.heal({"h": 40}, "Player", characters)
    assert healing == 0, "No healing at full health"
    assert enemy.aggro["Player"] == 5.0, "No additional aggro"
