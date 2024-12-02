import pytest
from Battle import Character


def test_temp_hp_mechanics():
    """Test temporary HP mechanics and interactions.

    Current Behavior:
    - Temp HP stacks additively (30 + 20 = 50)
    - No cap on temp HP accumulation
    - All damage types are absorbed by temp HP first
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Test temp HP stacking
    _, temp1 = enemy.heal({"t": 30}, "Player", characters)
    assert temp1 == 30, "First temp HP application"
    assert enemy.temp_hp == 30, "Temp HP stored correctly"

    _, temp2 = enemy.heal({"t": 20}, "Player", characters)
    assert temp2 == 20, "Second temp HP application"
    assert enemy.temp_hp == 50, "Temp HP stacks additively"


def test_temp_hp_damage_absorption():
    """Test how temporary HP absorbs damage.

    Current Behavior:
    - Temp HP absorbs damage before regular HP
    - Excess damage carries over to regular HP
    - All damage types affect temp HP first
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Give enemy some temp HP
    enemy.heal({"t": 30}, "Player", characters)
    assert enemy.temp_hp == 30, "Initial temp HP"

    # Test partial temp HP absorption
    damage = enemy.calculate_damage({"p": 20})
    assert damage == 20, "Full damage dealt"
    assert enemy.temp_hp == 10, "Temp HP reduced"
    assert enemy.health == 100, "Health unchanged"

    # Test complete temp HP depletion
    damage = enemy.calculate_damage({"p": 20})
    assert damage == 20, "Full damage dealt"
    assert enemy.temp_hp == 0, "Temp HP depleted"
    assert enemy.health == 90, "Excess damage affects health"


def test_temp_hp_mechanics_bug():
    """Test temporary HP mechanics and interactions.

    Bug Reports:
    - BUG-001: Temp HP stacks instead of taking highest value
    - BUG-002: No cap on temp HP accumulation
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Document current stacking behavior
    _, temp1 = enemy.heal({"t": 30}, "Player", characters)
    assert temp1 == 30, "First temp HP application"
    _, temp2 = enemy.heal({"t": 20}, "Player", characters)
    assert temp2 == 20, "Second temp HP application"
    assert enemy.temp_hp == 50, "Currently stacks (bug: should take highest value)"


def test_temp_hp_reduction_order():
    """Test the order of HP reduction when taking damage.

    Current Implementation:
    1. Damage is first applied to temp HP
    2. Remaining damage affects regular HP
    3. This order applies to all damage types
    4. When damage is fully absorbed by temp HP, returns 0
    """
    # Setup
    player = Character("Player", 10, 0, 0, 0, 0, 100, "player")
    enemy = Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy")
    characters = [player, enemy]

    # Give enemy temp HP and deal mixed damage
    enemy.heal({"t": 50}, "Player", characters)
    assert enemy.temp_hp == 50, "Initial temp HP"

    # Test mixed damage types
    damage_dict = {"p": 20, "a": 20}  # 40 total damage
    damage = enemy.calculate_damage(damage_dict)
    assert damage == 40, "Full damage calculated"
    assert enemy.temp_hp == 10, "Temp HP absorbs first"
    assert enemy.health == 100, "Health preserved"

    # Test final temp HP depletion
    damage = enemy.calculate_damage({"p": 20})
    assert damage == 20, "Full damage dealt"
    assert enemy.temp_hp == 0, "Temp HP fully depleted"
    assert enemy.health == 90, "Excess affects health"
