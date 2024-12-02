import pytest
from Battle import parse_damage_input, parse_healing_input, input_with_retry

def test_damage_input_parsing():
    """Test damage input string parsing.
    
    Current Implementation:
    1. Basic format: "XpYm" where X,Y are numbers
    2. Supports physical (p) and magical (m) damage
    3. No input validation
    """
    # Basic physical damage
    assert parse_damage_input("50p") == {"p": 50, "m": 0}, "Single physical damage"
    
    # Basic magical damage
    assert parse_damage_input("30m") == {"p": 0, "m": 30}, "Single magical damage"
    
    # Combined damage
    assert parse_damage_input("50p30m") == {"p": 50, "m": 30}, "Combined damage"
    
    # Zero damage
    assert parse_damage_input("0p0m") == {"p": 0, "m": 0}, "Zero damage"
    
    # Empty input
    assert parse_damage_input("") == {"p": 0, "m": 0}, "Empty input defaults to zero"

def test_damage_input_edge_cases():
    """Test edge cases in damage input parsing.
    
    Current Implementation:
    1. Handles invalid formats
    2. No negative validation
    3. No upper bounds
    """
    # Missing values
    assert parse_damage_input("p") == {"p": 0, "m": 0}, "Missing number defaults to zero"
    
    # Invalid format
    assert parse_damage_input("invalid") == {"p": 0, "m": 0}, "Invalid input defaults to zero"
    
    # Negative values (if supported)
    result = parse_damage_input("-50p-30m")
    assert result.get("p", 0) <= 0 and result.get("m", 0) <= 0, "Negative damage handled"
    
    # Large values
    result = parse_damage_input("999999p999999m")
    assert isinstance(result["p"], (int, float)) and isinstance(result["m"], (int, float)), "Large numbers handled"

def test_healing_input_parsing():
    """Test healing input string parsing.
    
    Current Implementation:
    1. Basic format: "XhYt" where X,Y are numbers
    2. Supports healing (h) and temp healing (t)
    3. No input validation
    """
    # Basic healing
    assert parse_healing_input("50h") == {"h": 50, "t": 0}, "Single healing"
    
    # Basic temp healing
    assert parse_healing_input("30t") == {"h": 0, "t": 30}, "Single temp healing"
    
    # Combined healing
    assert parse_healing_input("50h30t") == {"h": 50, "t": 30}, "Combined healing"
    
    # Zero healing
    assert parse_healing_input("0h0t") == {"h": 0, "t": 0}, "Zero healing"
    
    # Empty input
    assert parse_healing_input("") == {"h": 0, "t": 0}, "Empty input defaults to zero"

def test_healing_input_edge_cases():
    """Test edge cases in healing input parsing.
    
    Current Implementation:
    1. Handles invalid formats
    2. No negative validation
    3. No upper bounds
    """
    # Missing values
    assert parse_healing_input("h") == {"h": 0, "t": 0}, "Missing number defaults to zero"
    
    # Invalid format
    assert parse_healing_input("invalid") == {"h": 0, "t": 0}, "Invalid input defaults to zero"
    
    # Negative values (if supported)
    result = parse_healing_input("-50h-30t")
    assert result.get("h", 0) <= 0 and result.get("t", 0) <= 0, "Negative healing handled"
    
    # Large values
    result = parse_healing_input("999999h999999t")
    assert isinstance(result["h"], (int, float)) and isinstance(result["t"], (int, float)), "Large numbers handled"

def test_input_retry_mechanism():
    """Test input retry mechanism for invalid inputs.
    
    Current Implementation:
    1. Returns default on invalid
    2. No retry prompt
    3. Silent failure
    """
    # Invalid inputs return defaults
    assert parse_damage_input("invalid") == {"p": 0, "m": 0}, "Invalid damage defaults"
    assert parse_healing_input("invalid") == {"h": 0, "t": 0}, "Invalid healing defaults"
    
    # Malformed inputs
    assert parse_damage_input("50x30y") == {"p": 0, "m": 0}, "Malformed damage defaults"
    assert parse_healing_input("50x30y") == {"h": 0, "t": 0}, "Malformed healing defaults"
    
    # Empty inputs
    assert parse_damage_input("") == {"p": 0, "m": 0}, "Empty damage defaults"
    assert parse_healing_input("") == {"h": 0, "t": 0}, "Empty healing defaults"

def test_input_retry_behavior():
    """Test input retry mechanism.
    
    Current Implementation:
    1. Type conversion
    2. Value validation
    3. Retry on invalid
    """
    # Test type conversion
    def mock_input(prompt):
        return "42"
    
    result = input_with_retry("Test:", int, input_func=mock_input)
    assert result == 42, "Integer conversion"
    
    # Test allowed values
    def mock_input_enum(prompt):
        return "player"
    
    result = input_with_retry("Test:", str, ["player", "enemy"], input_func=mock_input_enum)
    assert result == "player", "Enum validation"
