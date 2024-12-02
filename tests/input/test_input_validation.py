import pytest
from Battle import parse_damage_input, parse_healing_input

def test_damage_input_edge_cases():
    """Test edge cases in damage input parsing.
    
    Current Behavior:
    1. Empty input returns empty dict and 0 temp HP
    2. None input raises AttributeError
    3. Missing values (e.g. "p") raise ValueError
    4. Invalid types are ignored
    5. Invalid number format raises ValueError
    6. Negative values are allowed
    """
    # Empty input
    damage_dict, temp = parse_damage_input("")
    assert damage_dict == {}, "Empty input returns empty dict"
    assert temp == 0, "Empty input has no temp HP"
    
    # None input - raises AttributeError
    with pytest.raises(AttributeError):
        parse_damage_input(None)
    
    # Missing values - raises ValueError
    with pytest.raises(ValueError):
        parse_damage_input("p")
    
    # Invalid damage type
    damage_dict, temp = parse_damage_input("50x")
    assert damage_dict == {}, "Invalid damage type ignored"
    assert temp == 0, "Invalid type has no temp HP"
    
    # Invalid number format
    with pytest.raises(ValueError):
        parse_damage_input("abcp")
    
    # Negative values
    damage_dict, temp = parse_damage_input("-50p -30t")
    assert damage_dict == {"p": -50.0}, "Negative damage allowed"
    assert temp == -30.0, "Negative temp HP allowed"
    
    # Multiple spaces
    damage_dict, temp = parse_damage_input("50p  30a   20l")
    assert damage_dict == {"p": 50.0, "a": 30.0, "l": 20.0}, "Multiple spaces handled"
    assert temp == 0, "No temp HP"

def test_healing_input_edge_cases():
    """Test edge cases in healing input parsing.
    
    Current Behavior:
    1. Empty input returns empty dict
    2. None input raises AttributeError
    3. Missing values (e.g. "h") raise ValueError
    4. Invalid types are ignored
    5. Invalid number format raises ValueError
    6. Negative values are allowed
    7. Multiple spaces are handled
    """
    # Empty input
    healing_dict = parse_healing_input("")
    assert healing_dict == {}, "Empty input returns empty dict"
    
    # None input - raises AttributeError
    with pytest.raises(AttributeError):
        parse_healing_input(None)
    
    # Missing values - raises ValueError
    with pytest.raises(ValueError):
        parse_healing_input("h")
    
    # Invalid healing type
    healing_dict = parse_healing_input("50x")
    assert healing_dict == {}, "Invalid healing type ignored"
    
    # Invalid number format
    with pytest.raises(ValueError):
        parse_healing_input("abch")
    
    # Negative values
    healing_dict = parse_healing_input("-50h -30t")
    assert healing_dict == {"h": -50.0, "t": -30.0}, "Negative healing allowed"
    
    # Multiple spaces
    healing_dict = parse_healing_input("50h  30t")
    assert healing_dict == {"h": 50.0, "t": 30.0}, "Multiple spaces handled"

def test_input_retry_mechanism():
    """Test input retry mechanism for invalid inputs.
    
    Current Behavior:
    1. Invalid inputs trigger retry
    2. Empty inputs are allowed
    3. Valid inputs are accepted
    4. Max retries enforced
    """
    # Note: This test requires mock input/output to properly test
    # the retry mechanism. For now, we just document the behavior.
    pass
