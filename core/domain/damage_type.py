from enum import Enum, auto

class DamageType(Enum):
    """Enumeration of damage types."""
    PHYSICAL = auto()
    ARCANE = auto()
    LIGHT = auto()
    NATURE = auto()

    @staticmethod
    def parse_damage_string(damage_str: str) -> dict:
        """Parse a damage string (e.g. '40p 30l') into a damage type dictionary.
        
        Args:
            damage_str: String containing damage amounts and types (e.g. '40p 30l')
            
        Returns:
            Dictionary mapping damage types to amounts as decimals
        """
        damage_types = {}
        parts = damage_str.lower().split()
        
        type_map = {
            'p': 'physical',
            'a': 'arcane',
            'l': 'light',
            'n': 'nature'
        }
        
        for part in parts:
            if not part:
                continue
                
            try:
                amount = float(''.join(c for c in part if c.isdigit() or c == '.'))
                type_char = next((c for c in part if c in type_map), None)
                
                if type_char and amount > 0:
                    damage_type = type_map[type_char]
                    damage_types[damage_type] = amount
                    
            except (ValueError, StopIteration):
                continue
                
        return damage_types
