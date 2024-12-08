# BattleBot Refactoring Guide

## Context and Goals

This guide outlines the approach for identifying and fixing DRY (Don't Repeat Yourself) violations in the BattleBot codebase while maintaining backward compatibility with existing tests.

⚠️ **Important Note**: The capitalized `Battle.py` in the root directory serves as a historical artifact, representing the system's starting point. While we maintain compatibility with its behavior through tests, new code should follow the patterns established in `core/aggregates/battle.py`.

## Current Architecture

The codebase currently has several layers:

1. **Legacy Layer** (`Battle.py`)
   - Original implementation
   - Contains test-mandated behavior
   - Used as reference for expected system behavior

2. **Adapter Layer** (`battle_adapter.py`)
   - Bridges between legacy and new implementations
   - Maintains backward compatibility
   - Currently contains some duplicated logic

3. **Core Layer** (`core/`)
   - Modern, event-sourced implementation
   - Clean domain model
   - Type-safe implementations

## Common DRY Violations to Look For

1. **Data Structure Duplication**
   - Multiple Character class definitions
   - Repeated damage type mappings
   - Redundant state tracking

2. **Logic Duplication**
   - Damage calculation in multiple places
   - Repeated parsing logic
   - Similar validation rules

3. **Configuration Duplication**
   - Hardcoded values in multiple files
   - Repeated magic numbers
   - Duplicate string constants

## Refactoring Strategy

### Phase 1: Identify
1. Start from `battle_adapter.py`
2. Map all instances where similar logic appears in multiple places
3. Note test dependencies for each duplicated piece

### Phase 2: Extract
1. Move common logic to appropriate domain models
2. Create adapter methods for legacy compatibility
3. Update tests to use new abstractions where possible

### Phase 3: Adapt
1. Keep legacy interfaces working
2. Add deprecation warnings
3. Document migration paths

## Rules for Refactoring

1. **Test Compatibility**
   - All existing tests must pass
   - Behavior must match `Battle.py`
   - Add new tests for refactored code

2. **Domain Boundaries**
   - Core logic belongs in `core/domain/`
   - Adapters handle translation
   - No domain logic in adapters

3. **Type Safety**
   - Use enums for fixed sets
   - Add type hints
   - Validate at boundaries

## Common Patterns

### Before (DRY Violation):
```python
# In battle_adapter.py
def parse_damage(damage_str):
    amount = int(damage_str[:-1])
    type_map = {"p": "physical", "a": "arcane"}
    return {type_map[damage_str[-1]]: amount}

# In Battle.py
def parse_damage_string(damage_str):
    num = int(damage_str[:-1])
    if damage_str[-1] == "p":
        return {"physical": num}
    elif damage_str[-1] == "a":
        return {"arcane": num}
```

### After (DRY Fixed):
```python
# In core/domain/damage_types.py
class DamageType(Enum):
    PHYSICAL = "p"
    ARCANE = "a"

    @classmethod
    def parse_damage_string(cls, damage_str):
        amount = int(damage_str[:-1])
        return {cls(damage_str[-1]).full_name: amount}

# In battle_adapter.py
from core.domain.damage_types import DamageType

def parse_damage(damage_str):
    return DamageType.parse_damage_string(damage_str)

# Battle.py remains unchanged for compatibility
```

## Checklist for Each Refactoring

1. [ ] Identify all occurrences of the duplicated code
2. [ ] Map test dependencies
3. [ ] Create domain model
4. [ ] Update adapter layer
5. [ ] Verify test compatibility
6. [ ] Add migration documentation

## Current Focus Areas

1. Damage Type Handling
   - [ ] Consolidate damage type definitions
   - [ ] Standardize parsing logic
   - [ ] Unify validation rules

2. Character State Management
   - [ ] Align character representations
   - [ ] Centralize state updates
   - [ ] Standardize property access

3. Battle Mechanics
   - [ ] Unify damage calculations
   - [ ] Standardize aggro handling
   - [ ] Centralize validation logic
