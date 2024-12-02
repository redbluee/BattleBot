import pytest
from Battle import Character

def test_damage_type_combinations():
    """Test all possible damage type combinations.
    
    Tests:
    1. Multiple damage types stacking
    2. Different resistance combinations
    3. Order independence
    """
    char = Character(
        "Test",
        10,
        50,  # 50% physical reduction
        25,  # 25% arcane reduction
        75,  # 75% light reduction
        100, # 100% nature reduction
        100,
        "player"
    )
    
    # Test single type damages
    physical = char.calculate_damage({"p": 100})
    assert physical == 50, "Physical reduction correct"
    
    arcane = char.calculate_damage({"a": 100})
    assert arcane == 75, "Arcane reduction correct"
    
    light = char.calculate_damage({"l": 100})
    assert light == 25, "Light reduction correct"
    
    nature = char.calculate_damage({"n": 100})
    assert nature == 0, "Nature reduction correct"
    
    # Test combinations
    phys_arcane = char.calculate_damage({"p": 100, "a": 100})
    assert phys_arcane == physical + arcane, "Physical + Arcane stacks correctly"
    
    all_types = char.calculate_damage({"p": 100, "a": 100, "l": 100, "n": 100})
    assert all_types == physical + arcane + light + nature, "All types stack correctly"

def test_healing_type_combinations():
    """Test combinations of healing types.
    
    Tests:
    1. Regular and temp healing combinations
    2. Multiple healing sources
    3. Order independence
    """
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    char.health = 50  # Start at half health
    
    # Test regular healing
    healing, temp = char.heal({"h": 30})
    assert healing == 30, "Regular healing works"
    assert temp == 0, "No temp healing"
    assert char.health == 80, "Health increased correctly"

    # Test temp healing
    healing, temp = char.heal({"t": 20})
    assert healing == 0, "No regular healing"
    assert temp == 20, "Temp healing works"
    assert char.temp_hp == 20, "Temp HP added correctly"

    # Test combination
    char = Character("Test", 10, 0, 0, 0, 0, 100, "player")
    char.health = 75  # Start at 75 health
    char.temp_hp = 20  # Start with 20 temp HP
    healing, temp = char.heal({"h": 25, "t": 25})
    assert healing == 25, "Regular healing in combo"
    assert temp == 25, "Temp healing in combo"
    assert char.health == 100, "Health increased correctly"
    assert char.temp_hp == 45, "Total temp HP stacked"

def test_resistance_combinations():
    """Test complex resistance interactions.
    
    Tests:
    1. Multiple resistance types
    2. Resistance stacking
    3. Negative resistance effects
    """
    char = Character(
        "Test",
        10,
        -50,  # Increases physical by 50%
        200,  # Complete arcane immunity
        75,   # 75% light reduction
        0,    # No nature resistance
        100,
        "player"
    )
    
    # Test negative resistance
    phys = char.calculate_damage({"p": 100})
    assert phys == 150, "Negative resistance increases damage"
    
    # Test over 100% resistance
    arcane = char.calculate_damage({"a": 100})
    assert arcane == -100, "Over 100% resistance results in negative damage"
    
    # Test mixed resistances
    mixed = char.calculate_damage({"p": 100, "a": 100, "l": 100, "n": 100})
    assert mixed == 150 + -100 + 25 + 100, "Mixed resistances calculated correctly"

def test_edge_case_combinations():
    """Test edge cases in damage/healing combinations.
    
    Tests:
    1. Zero value handling
    2. Negative value handling
    3. Unknown type handling
    """
    char = Character("Test", 10, 50, 0, 0, 0, 100, "player")
    
    # Test zero values
    zero_damage = char.calculate_damage({"p": 0, "a": 0})
    assert zero_damage == 0, "Zero damage handled"
    
    # Test unknown types
    unknown = char.calculate_damage({"x": 100})
    assert isinstance(unknown, (int, float)), "Unknown type handled gracefully"
    
    # Test healing edge cases
    healing, temp = char.heal({"h": 0, "t": 0})
    assert healing == 0 and temp == 0, "Zero healing handled"
    
    healing, temp = char.heal({"x": 100})
    assert healing == 0 and temp == 0, "Unknown healing type handled"
