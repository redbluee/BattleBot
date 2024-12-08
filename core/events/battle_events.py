"""Domain events for the battle system."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import UUID
from datetime import datetime


@dataclass
class EventMetadata:
    """Metadata for all events."""
    aggregate_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    version: int = field(default=1)


@dataclass
class BattleStarted:
    """Event emitted when a battle starts."""
    metadata: EventMetadata
    participants: Dict[str, dict]


@dataclass
class RoundStarted:
    """Event emitted when a new round starts."""
    metadata: EventMetadata
    round_number: int
    initiative_order: List[str]


@dataclass
class CharacterTurnStarted:
    """Event emitted when a character's turn begins."""
    metadata: EventMetadata
    character_id: str
    current_stats: Dict  # Health, temp HP, etc.


@dataclass
class DamageDealt:
    """Event emitted when damage is dealt."""
    metadata: EventMetadata
    source_id: str
    target_id: str
    damage_types: Dict[str, int]
    actual_damage: int


@dataclass
class HealingReceived:
    """Event emitted when healing is received."""
    metadata: EventMetadata
    target_id: str
    healing_amount: int
    temp_hp: int = field(default=0)


@dataclass
class AggroChanged:
    """Event emitted when aggro changes."""
    metadata: EventMetadata
    enemy_id: str
    player_id: str
    aggro_change: int
    new_total: int


@dataclass
class CharacterDied:
    """Event emitted when a character dies."""
    metadata: EventMetadata
    character_id: str
    killing_blow: Optional[Dict] = field(default=None)  # Details about the killing blow


@dataclass
class BattleEnded:
    """Event emitted when the battle ends."""
    metadata: EventMetadata
    winner: str  # "players" or "enemies"
    survivors: List[str]
    rounds_taken: int = field(default=0)
