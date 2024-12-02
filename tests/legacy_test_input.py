import pytest
from Battle import parse_damage_input, parse_healing_input, input_with_retry


def test_damage_input_parsing():
    """Test parsing of damage input strings.
    
    Verifies:
    1. Basic damage type parsing
    2. Multiple damage types
    3. Empty input handling
    """
    # Single damage type
    assert parse_damage_input("50p") == ({"p": 50}, ""), "Single physical damage"
    assert parse_damage_input("30a") == ({"a": 30}, ""), "Single arcane damage"
    
    # Multiple damage types
    result, _ = parse_damage_input("50p 30a 20l")
    assert result == {"p": 50, "a": 30, "l": 20}, "Multiple damage types"
    
    # Empty input
    assert parse_damage_input("") == ({}, ""), "Empty damage input"


def test_healing_input_parsing():
    """Test parsing of healing input strings.
    
    Verifies:
    1. Regular healing parsing
    2. Temp HP parsing
    3. Mixed healing types
    4. Empty input handling
    """
    # Single healing type
    assert parse_healing_input("40h") == ({"h": 40}, ""), "Regular healing"
    assert parse_healing_input("30t") == ({"t": 30}, ""), "Temp HP"
    
    # Mixed healing
    result, _ = parse_healing_input("40h 20t")
    assert result == {"h": 40, "t": 20}, "Mixed healing types"
    
    # Empty input
    assert parse_healing_input("") == ({}, ""), "Empty healing input"


@pytest.mark.skip(reason="Uses input() function which can't be automated")
def test_input_validation():
    """Test input validation and retry mechanism.
    
    Current Implementation:
    1. Basic type conversion
    2. Empty input handling
    3. No validation of damage/healing types
    """
    # Test string input
    result = input_with_retry("test", str, ["yes", "no"])
    assert isinstance(result, str), "Should return string"
    
    # Test numeric input
    result = input_with_retry("42", int)
    assert isinstance(result, int), "Should return integer"
    
    # Test empty input
    result = input_with_retry("", str)
    assert result == "", "Empty input should be allowed"
