import pytest
from Battle import Character, battle_round


def test_dead_character_interactions():
    """Test interactions involving dead characters.

    Current Behavior:
    1. Dead characters (health = 0) can still perform actions
    2. Dead characters can receive healing
    3. Dead characters maintain and generate aggro
    4. Dead characters can be targeted
    """
    char1 = Character("Living", 20, 0, 0, 0, 0, 100, "player")
    char2 = Character("Dead", 10, 0, 0, 0, 0, 100, "enemy")
    chars = [char1, char2]

    # Kill character
    char2.health = 0
    assert char2.health == 0, "Character is dead"

    # Test dead character can deal damage
    damage = char2.calculate_damage({"p": 50}, "Dead", chars)
    assert damage == 50, "Dead characters can deal full damage"

    # Test dead character can receive healing
    healing, temp = char2.heal({"h": 30, "t": 20}, "Living", chars)
    assert healing == 30, "Dead characters can receive healing"
    assert temp == 20, "Dead characters can receive temp HP"
    assert char2.health == 30, "Healing applied to dead character"
    assert char2.temp_hp == 20, "Temp HP applied to dead character"

    # Test dead character aggro
    if hasattr(char2, "aggro"):
        char2.add_aggro("Living", 100, chars)
        assert char2.aggro["Living"] == 107.5, "Dead enemies track aggro"
        highest = char2.get_highest_aggro()
        assert "Living" in highest, "Dead enemies return aggro targets"


@pytest.mark.skip(reason="Uses battle_round which requires input()")
def test_round_state_persistence():
    """Test state persistence between battle rounds.

    Current Behavior:
    1. All stat modifications persist between rounds
    2. Temp HP persists between rounds
    3. Aggro values persist between rounds
    4. Death state persists between rounds
    """
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy"),
    ]

    # Set up initial states
    chars[0].temp_hp = 50
    chars[0].health = 25
    chars[1].health = 0  # Dead
    if hasattr(chars[1], "aggro"):
        chars[1].add_aggro("Player", 100, chars)

    # Simulate round transition
    battle_round(chars, 1)

    # Verify all states persist
    assert chars[0].temp_hp == 50, "Temp HP persists"
    assert chars[0].health == 25, "Health changes persist"
    assert chars[1].health == 0, "Death state persists"
    if hasattr(chars[1], "aggro"):
        assert chars[1].aggro["Player"] == 100, "Aggro persists through death"


def test_initiative_edge_cases():
    """Test edge cases in initiative order.

    Current Behavior:
    1. Initiative order is strictly by value (highest first)
    2. Negative initiative is allowed and functions normally
    3. No upper/lower bounds on initiative
    4. Ties are maintained in original order
    """
    chars = [
        Character("First", 10, 0, 0, 0, 0, 100, "player"),
        Character("Tied1", 0, 0, 0, 0, 0, 100, "player"),
        Character("Tied2", 0, 0, 0, 0, 0, 100, "enemy"),
        Character("Negative", -5, 0, 0, 0, 0, 100, "enemy"),
        Character("Extreme", 999999, 0, 0, 0, 0, 100, "player"),
    ]

    sorted_chars = sorted(chars, key=lambda x: x.initiative, reverse=True)
    assert sorted_chars[0].name == "Extreme", "Highest initiative first"
    assert sorted_chars[1].name == "First", "Positive initiative second"
    assert sorted_chars[-1].name == "Negative", "Negative initiative last"

    # Test initiative modification during battle
    chars[0].initiative = -10
    new_sorted = sorted(chars, key=lambda x: x.initiative, reverse=True)
    assert new_sorted[-1].name == "First", "Initiative order updates dynamically"
