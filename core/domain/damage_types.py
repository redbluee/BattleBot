"""Damage type definitions for the battle system."""
from enum import Enum
from typing import Dict, List

class DamageType(Enum):
    """Damage types in the battle system."""
    PHYSICAL = "p"
    ARCANE = "a"
    LIGHT = "l"
    NATURE = "n"
    AGGRO = "g"  # Special type for aggro generation
    TEMP = "t"   # Special type for temporary HP

    @property
    def full_name(self) -> str:
        """Get the full name of the damage type."""
        return {
            DamageType.PHYSICAL: "physical",
            DamageType.ARCANE: "arcane",
            DamageType.LIGHT: "light",
            DamageType.NATURE: "nature",
            DamageType.AGGRO: "aggro",
            DamageType.TEMP: "temp"
        }[self]

    @classmethod
    def from_short_name(cls, short_name: str) -> "DamageType":
        """Get damage type from short name (e.g., 'p' -> PHYSICAL)."""
        for damage_type in cls:
            if damage_type.value == short_name:
                return damage_type
        raise ValueError(f"Unknown damage type: {short_name}")

    @classmethod
    def parse_damage_string(cls, damage_str: str) -> Dict[str, float]:
        """Parse a damage string into a dictionary of damage types and amounts.
        
        Args:
            damage_str: String like "40p 30a" for 40 physical + 30 arcane damage
            
        Returns:
            Dictionary mapping full damage type names to amounts
        """
        result = {}
        parts = damage_str.split()
        
        for part in parts:
            if not part[:-1].replace(".", "").isdigit():
                continue
                
            amount = float(part[:-1])
            try:
                damage_type = cls.from_short_name(part[-1])
                if damage_type != DamageType.TEMP:  # Temp HP handled separately
                    result[damage_type.full_name] = amount
            except ValueError:
                continue
                
        return result

    @classmethod
    def get_temp_hp(cls, damage_str: str) -> float:
        """Extract temporary HP amount from a damage string.
        
        Args:
            damage_str: String like "40p 30t" where 30t means 30 temp HP
            
        Returns:
            Amount of temp HP, or 0 if none specified
        """
        parts = damage_str.split()
        for part in parts:
            if not part[:-1].replace(".", "").isdigit():
                continue
                
            if part[-1] == cls.TEMP.value:
                return float(part[:-1])
        return 0
