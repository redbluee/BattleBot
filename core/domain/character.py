"""Character domain model for the battle system."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from .damage_types import DamageType

@dataclass
class Character:
    """Core character model with all battle-relevant attributes and behaviors."""
    name: str
    initiative: int
    armor: int
    arcane_resist: int
    light_resist: int
    nature_resist: int
    max_health: int
    tag: str
    health: int = field(init=False)
    temp_hp: int = field(default=0)
    _aggro: Optional[Dict[str, float]] = field(default=None)

    def __init__(self, name: str, initiative: int, armor: int, arcane_resist: int, light_resist: int, nature_resist: int, max_health: int, tag: str):
        """Initialize character.
        
        Args:
            name: Character name
            initiative: Initiative value
            armor: Physical armor percentage (e.g., 20 for 20% damage reduction)
            arcane_resist: Arcane resistance percentage
            light_resist: Light resistance percentage
            nature_resist: Nature resistance percentage
            max_health: Maximum health points
            tag: Character tag (player/enemy)
        """
        self.name = name
        self.initiative = initiative
        self.armor = armor  # Already a percentage (e.g., 20 for 20% reduction)
        self.arcane_resist = arcane_resist
        self.light_resist = light_resist
        self.nature_resist = nature_resist
        self.max_health = max_health
        self.tag = tag
        self.health = max_health
        self.temp_hp = 0
        self._aggro = {} if tag == "enemy" else None

    @property
    def aggro(self) -> Optional[Dict[str, float]]:
        """Get aggro dictionary."""
        return self._aggro

    @aggro.setter
    def aggro(self, value: Optional[Dict[str, float]]) -> None:
        """Set aggro dictionary."""
        if self.tag != "enemy":
            return
        self._aggro = value if value is not None else {}

    def __post_init__(self):
        """Initialize health to max_health after instance creation."""
        self.health = self.max_health

    def get_resistance(self, damage_type: DamageType) -> float:
        """Get the resistance value for a given damage type."""
        resistance_map = {
            DamageType.PHYSICAL: self.armor,
            DamageType.ARCANE: self.arcane_resist,
            DamageType.LIGHT: self.light_resist,
            DamageType.NATURE: self.nature_resist
        }
        # Return resistance value directly (already a percentage)
        return resistance_map.get(damage_type, 0)

    def calculate_damage(self, damage_dict: Dict[str, float], attacker_name: Optional[str] = None) -> float:
        """Calculate and apply damage from all sources.
        
        Args:
            damage_dict: Dictionary mapping damage types to raw damage amounts
            attacker_name: Name of the attacking character (for aggro)
            
        Returns:
            Total effective damage dealt
        """
        total_damage = 0
        print(f"[DEBUG] Calculating damage for {damage_dict}")
        
        # Create a mapping of lowercase to DamageType enum
        damage_type_map = {dt.name.lower(): dt for dt in DamageType}
        
        # Calculate damage after resistances
        for damage_type_name, amount in damage_dict.items():
            try:
                # Get the enum from the lowercase name
                damage_type = damage_type_map.get(damage_type_name)
                if not damage_type:
                    print(f"[DEBUG] Unknown damage type: {damage_type_name}")
                    continue
                    
                # Get resistance as percentage
                resistance = self.get_resistance(damage_type)
                print(f"[DEBUG] {damage_type_name}: amount={amount}, resistance={resistance}%")
                # Calculate effective damage
                # Convert percentage to decimal (e.g., 20% becomes 0.20) to calculate damage reduction
                effective_damage = amount * (1 - resistance / 100)  
                print(f"[DEBUG] Effective damage: {effective_damage}")
                total_damage += effective_damage
            except Exception as e:
                print(f"[DEBUG] Error processing damage type {damage_type_name}: {e}")
                continue  # Skip unknown damage types

        # Round total damage
        total_damage = round(total_damage)
        print(f"[DEBUG] Total damage after rounding: {total_damage}")

        # Handle temp HP
        if self.temp_hp > 0:
            if total_damage <= self.temp_hp:
                self.temp_hp -= total_damage
                total_damage = 0
            else:
                total_damage -= self.temp_hp
                self.temp_hp = 0

        # Apply damage
        old_health = self.health
        self.health = max(0, self.health - total_damage)
        print(f"[DEBUG] Health reduced from {old_health} to {self.health}")

        # Handle aggro if target is enemy and attacker is specified
        if self.tag == "enemy" and attacker_name and total_damage > 0:
            self.add_aggro(attacker_name, total_damage)

        return total_damage

    def take_damage(self, damage: int) -> int:
        """Take damage, accounting for temporary HP.
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            Actual damage taken
        """
        # Handle temp HP first
        if self.temp_hp > 0:
            if damage <= self.temp_hp:
                self.temp_hp -= damage
                return 0
            else:
                remaining_damage = damage - self.temp_hp
                self.temp_hp = 0
                self.health = max(0, self.health - remaining_damage)
                return remaining_damage
        else:
            # No temp HP, just take the damage
            self.health = max(0, self.health - damage)
            return damage

    def heal(self, healing_amount: int, temp_hp: int = 0, healer_name: Optional[str] = None) -> tuple[int, int]:
        """Apply healing and temporary HP to the character.
        
        Args:
            healing_amount: Amount of regular healing
            temp_hp: Amount of temporary HP
            healer_name: Name of the healing character (for aggro)
            
        Returns:
            Tuple of (actual healing done, temp HP applied)
        """
        # Apply regular healing
        old_health = self.health
        self.health = min(self.max_health, self.health + healing_amount)
        actual_healing = self.health - old_health

        # Apply temp HP
        if temp_hp > 0:
            self.temp_hp = temp_hp

        # Add aggro if healed by player
        if self.tag == "enemy" and healer_name and actual_healing > 0:
            # Scale factor of 0.25 matches original test expectations
            aggro_amount = actual_healing * 0.25
            self.add_aggro(healer_name, aggro_amount)

        return actual_healing, temp_hp

    def add_aggro(self, player_name: str, amount: float) -> None:
        """Add aggro for a player.
        
        Args:
            player_name: Name of the player generating aggro
            amount: Amount of aggro to add
        """
        if self.tag != "enemy":
            return
        if self._aggro is None:
            self._aggro = {}
        self._aggro[player_name] = self._aggro.get(player_name, 0) + amount

    def get_highest_aggro(self) -> str | List[str]:
        """Get the player(s) with highest aggro."""
        if not self._aggro or not self._aggro.values():
            return "Aggro: none"
            
        highest_aggro = max(self._aggro.values())
        if highest_aggro <= 0:
            return "Aggro: none"
            
        return [
            player for player, aggro in self._aggro.items() 
            if aggro == highest_aggro
        ]
