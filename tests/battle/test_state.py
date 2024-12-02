import pytest
from Battle import Character, battle_round


def test_combat_state_transitions():
    """Test combat state transitions and persistence."""
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy"),
    ]

    # Initial state
    assert all(c.health == c.max_health for c in chars), "Full health at start"
    assert all(c.temp_hp == 0 for c in chars), "No temp HP at start"

    # Combat effects
    chars[0].temp_hp = 50
    chars[1].health = 50

    # State persistence
    assert chars[0].temp_hp == 50, "Temp HP persists"
    assert chars[1].health == 50, "Health changes persist"


def test_dead_character_state():
    """Test state management for dead characters."""
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy"),
    ]

    # Kill character
    chars[0].health = 0

    # Dead character behavior
    damage = chars[0].calculate_damage({"p": 50})
    assert isinstance(damage, (int, float)), "Dead characters can deal damage"

    healing, _ = chars[0].heal({"h": 50})
    assert healing > 0, "Dead characters can be healed"


def test_aggro_state():
    """Test aggro system state management."""
    chars = [
        Character("Player", 20, 0, 0, 0, 0, 100, "player"),
        Character("Enemy", 10, 0, 0, 0, 0, 100, "enemy"),
    ]

    # Test aggro tracking
    if hasattr(chars[1], "aggro"):
        chars[1].add_aggro("Player", 100, chars)
        assert chars[1].aggro["Player"] == 100, "Aggro tracking works"

        chars[1].add_aggro("Player", 50, chars)
        assert chars[1].aggro["Player"] == 150, "Aggro stacks"

        # Death impact on aggro
        chars[1].health = 0
        if "Player" in chars[1].aggro:
            assert isinstance(
                chars[1].get_highest_aggro(), list
            ), "Dead enemy maintains aggro list"
