import pytest
from Battle import parse_damage_input, parse_healing_input

def test_damage_input_parsing():
    """Test damage input string parsing.
    
    Current Behavior:
    1. Parses single and multiple damage types
    2. Handles temp HP separately
    3. Converts values to float
    4. Preserves decimal values
    5. Handles all damage types: p, a, l, n
    """
    # Basic physical damage
    damage_dict, temp = parse_damage_input("50p")
    assert damage_dict == {"p": 50.0}, "Single physical damage"
    assert temp == 0, "No temp HP"
    
    # Multiple damage types
    damage_dict, temp = parse_damage_input("50p 30a 20l")
    assert damage_dict == {"p": 50.0, "a": 30.0, "l": 20.0}, "Multiple damage types"
    assert temp == 0, "No temp HP"
    
    # With temp HP
    damage_dict, temp = parse_damage_input("50p 20t")
    assert damage_dict == {"p": 50.0}, "Damage with temp HP"
    assert temp == 20.0, "Temp HP parsed"
    
    # Arcane damage
    damage_dict, temp = parse_damage_input("30a")
    assert damage_dict == {"a": 30.0}, "Single arcane damage"
    assert temp == 0, "No temp HP"
    
    # Nature damage
    damage_dict, temp = parse_damage_input("40n")
    assert damage_dict == {"n": 40.0}, "Single nature damage"
    assert temp == 0, "No temp HP"
    
    # Light damage
    damage_dict, temp = parse_damage_input("25l")
    assert damage_dict == {"l": 25.0}, "Single light damage"
    assert temp == 0, "No temp HP"
    
    # Empty input
    damage_dict, temp = parse_damage_input("")
    assert damage_dict == {}, "Empty input returns empty dict"
    assert temp == 0, "Empty input has no temp HP"
    
    # Only temp HP
    damage_dict, temp = parse_damage_input("30t")
    assert damage_dict == {}, "No damage types"
    assert temp == 30.0, "Only temp HP"
    
    # Decimal values
    damage_dict, temp = parse_damage_input("50.5p 30.5t")
    assert damage_dict == {"p": 50.5}, "Decimal values preserved"
    assert temp == 30.5, "Decimal temp HP preserved"

def test_healing_input_parsing():
    """Test healing input string parsing.
    
    Current Behavior:
    1. Parses single and multiple healing types
    2. Converts values to float
    3. Preserves decimal values
    4. Handles both healing (h) and temp HP (t)
    """
    # Basic healing
    healing_dict = parse_healing_input("50h")
    assert healing_dict == {"h": 50.0}, "Single healing"
    
    # Multiple types
    healing_dict = parse_healing_input("50h 30t")
    assert healing_dict == {"h": 50.0, "t": 30.0}, "Multiple healing types"
    
    # Only temp HP
    healing_dict = parse_healing_input("30t")
    assert healing_dict == {"t": 30.0}, "Only temp HP"
    
    # Empty input
    healing_dict = parse_healing_input("")
    assert healing_dict == {}, "Empty input returns empty dict"
    
    # Decimal values
    healing_dict = parse_healing_input("50.5h 30.5t")
    assert healing_dict == {"h": 50.5, "t": 30.5}, "Decimal values preserved"

def test_input_edge_cases():
    """Test edge cases in input parsing.
    
    Current Behavior:
    1. Handles multiple spaces
    2. Preserves order of inputs
    3. Skips invalid types
    4. Handles zero values
    """
    # Multiple spaces
    damage_dict, temp = parse_damage_input("50p  30a   20l")
    assert damage_dict == {"p": 50.0, "a": 30.0, "l": 20.0}, "Multiple spaces handled"
    
    # Mixed valid/invalid
    damage_dict, temp = parse_damage_input("50p 30x 20l")
    assert damage_dict == {"p": 50.0, "l": 20.0}, "Invalid types skipped"
    
    # Zero values
    damage_dict, temp = parse_damage_input("0p 0t")
    assert damage_dict == {"p": 0.0}, "Zero damage allowed"
    assert temp == 0.0, "Zero temp HP allowed"
