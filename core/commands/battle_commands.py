"""Battle-related commands."""
from dataclasses import dataclass
from typing import Dict, Optional
from uuid import UUID


@dataclass
class Command:
    """Base class for all commands."""
    aggregate_id: UUID


@dataclass
class StartBattle(Command):
    """Command to start a new battle."""
    participants: Dict[str, Dict]  # Character details


@dataclass
class StartRound(Command):
    """Command to start a new battle round."""
    pass  # Initiative order will be determined by the aggregate


@dataclass
class DealDamage(Command):
    """Command to deal damage to a character."""
    source_id: str
    target_id: str
    damage_types: Dict[str, int]  # e.g., {"physical": 10, "fire": 5}


@dataclass
class ApplyHealing(Command):
    """Command to heal a character."""
    target_id: str
    healing_amount: int
    temp_hp: Optional[int] = None


@dataclass
class ModifyAggro(Command):
    """Command to modify aggro values."""
    enemy_id: str
    player_id: str
    aggro_change: int  # Can be positive or negative


@dataclass
class EndBattle(Command):
    """Command to end the battle."""
    reason: str  # e.g., "all_enemies_defeated", "all_players_dead", "flee"
