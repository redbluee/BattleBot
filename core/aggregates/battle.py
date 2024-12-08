"""Battle aggregate root."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from uuid import UUID
import logging

from ..events.battle_events import (
    EventMetadata,
    BattleStarted,
    RoundStarted,
    DamageDealt,
    HealingReceived,
    AggroChanged,
    CharacterDied,
    BattleEnded,
)
from ..commands.battle_commands import (
    StartBattle,
    StartRound,
    DealDamage,
    ApplyHealing,
    ModifyAggro,
    EndBattle,
)
from ..domain.character import Character
from ..domain.damage_type import DamageType

# Set up module logger
logger = logging.getLogger(__name__)

@dataclass
class BattleAggregate:
    """Battle aggregate root."""
    id: str
    characters: Dict[str, Character] = field(default_factory=dict)
    is_active: bool = field(default=False)
    current_round: int = field(default=0)
    version: int = field(default=0)

    def __post_init__(self):
        logger.debug(f"Created new BattleAggregate with ID: {self.id}")

    def handle_start_battle(self, cmd: StartBattle) -> List[BattleStarted]:
        """Handle StartBattle command."""
        logger.info(f"Starting new battle with ID: {self.id}")
        if self.is_active:
            logger.error("Attempted to start battle that is already in progress")
            raise ValueError("Battle already in progress")

        logger.debug(f"Initializing battle with {len(cmd.participants)} participants")
        # Create event
        event = BattleStarted(
            metadata=EventMetadata(aggregate_id=self.id, version=self.version + 1),
            participants=cmd.participants
        )

        # Apply event
        self._apply_battle_started(event)
        logger.info("Battle started successfully")
        return [event]

    def handle_start_round(self, cmd: StartRound) -> List[RoundStarted]:
        """Handle StartRound command."""
        logger.info(f"Starting new round in battle with ID: {self.id}")
        if not self.is_active:
            logger.error("Attempted to start round in inactive battle")
            raise ValueError("Battle not started")

        # Sort characters by initiative
        sorted_chars = sorted(
            self.characters.keys(),
            key=lambda x: self.characters[x].initiative,
            reverse=True
        )

        # Create event
        event = RoundStarted(
            metadata=EventMetadata(aggregate_id=self.id, version=self.version + 1),
            round_number=self.current_round + 1,
            initiative_order=sorted_chars
        )

        # Apply event
        self._apply_round_started(event)
        logger.info("Round started successfully")
        return [event]

    def handle_deal_damage(self, cmd: DealDamage) -> List[DamageDealt | CharacterDied]:
        """Handle DealDamage command."""
        logger.debug(f"Processing damage command: source={cmd.source_id}, target={cmd.target_id}")
        
        if not self.is_active:
            logger.error("Attempted to deal damage in inactive battle")
            raise ValueError("Battle not in progress")
            
        if cmd.source_id not in self.characters:
            logger.error(f"Source character {cmd.source_id} not found in battle")
            raise ValueError(f"Source character {cmd.source_id} not found")
            
        if cmd.target_id not in self.characters:
            logger.error(f"Target character {cmd.target_id} not found in battle")
            raise ValueError(f"Target character {cmd.target_id} not found")

        target = self.characters[cmd.target_id]
        
        # Calculate actual damage after resistances
        total_damage = self.apply_damage(cmd.target_id, cmd.damage_types)

        # Create damage event
        events = []
        damage_event = DamageDealt(
            metadata=EventMetadata(aggregate_id=self.id, version=self.version + 1),
            source_id=cmd.source_id,
            target_id=cmd.target_id,
            damage_types=cmd.damage_types,
            actual_damage=total_damage
        )
        events.append(damage_event)

        # Apply damage event
        self._apply_damage_dealt(damage_event)
        logger.debug(f"Damage dealt successfully: {cmd.damage_types}")

        # Check if target died
        if target.health <= 0:
            death_event = CharacterDied(
                metadata=EventMetadata(
                    aggregate_id=self.id,
                    version=self.version + 2
                ),
                character_id=cmd.target_id
            )
            events.append(death_event)
            self._apply_character_died(death_event)
            logger.info(f"Character {cmd.target_id} died")

        return events

    def handle_apply_healing(self, cmd: ApplyHealing) -> List[HealingReceived]:
        """Handle ApplyHealing command."""
        logger.debug(f"Processing healing command: target={cmd.target_id}, amount={cmd.healing_amount}")
        
        if not self.is_active:
            logger.error("Attempted to apply healing in inactive battle")
            raise ValueError("Battle not in progress")
            
        if cmd.target_id not in self.characters:
            logger.error(f"Target character {cmd.target_id} not found in battle")
            raise ValueError(f"Target character {cmd.target_id} not found")

        # Create event
        event = HealingReceived(
            metadata=EventMetadata(aggregate_id=self.id, version=self.version + 1),
            target_id=cmd.target_id,
            healing_amount=cmd.healing_amount,
            temp_hp=cmd.temp_hp
        )

        # Apply event
        self._apply_healing_received(event)
        logger.debug(f"Healing applied successfully: {cmd.healing_amount}")
        return [event]

    def handle_modify_aggro(self, cmd: ModifyAggro) -> List[AggroChanged]:
        """Handle ModifyAggro command."""
        logger.debug(f"Processing aggro modification command: enemy={cmd.enemy_id}, player={cmd.player_id}")
        
        if not self.is_active:
            logger.error("Attempted to modify aggro in inactive battle")
            raise ValueError("Battle not in progress")
            
        if cmd.enemy_id not in self.characters:
            logger.error(f"Enemy character {cmd.enemy_id} not found in battle")
            raise ValueError(f"Enemy character {cmd.enemy_id} not found")
            
        if cmd.player_id not in self.characters:
            logger.error(f"Player character {cmd.player_id} not found in battle")
            raise ValueError(f"Player character {cmd.player_id} not found")

        enemy = self.characters[cmd.enemy_id]
        if not enemy.is_enemy:
            logger.error("Can only modify aggro for enemies")
            raise ValueError("Can only modify aggro for enemies")

        # Calculate new aggro total
        current = enemy.aggro.get(cmd.player_id, 0)
        new_total = current + cmd.aggro_change

        # Create event
        event = AggroChanged(
            metadata=EventMetadata(aggregate_id=self.id, version=self.version + 1),
            enemy_id=cmd.enemy_id,
            player_id=cmd.player_id,
            aggro_change=cmd.aggro_change,
            new_total=new_total
        )

        # Apply event
        self._apply_aggro_changed(event)
        logger.debug(f"Aggro modified successfully: {cmd.aggro_change}")
        return [event]

    def handle_end_battle(self, cmd: EndBattle) -> List[BattleEnded]:
        """Handle EndBattle command."""
        logger.info(f"Ending battle with ID: {self.id}")
        
        if not self.is_active:
            logger.error("Attempted to end inactive battle")
            raise ValueError("Battle not in progress")

        # Get survivors
        survivors = [
            char_id for char_id, char in self.characters.items()
            if char.health > 0
        ]

        # Create event
        event = BattleEnded(
            metadata=EventMetadata(aggregate_id=self.id, version=self.version + 1),
            winner=cmd.winner,
            survivors=survivors,
            rounds_taken=self.current_round
        )

        # Apply event
        self._apply_battle_ended(event)
        logger.info("Battle ended successfully")
        return [event]

    def apply_damage(self, target_id: str, damage_types: Dict[str, int]) -> int:
        """Apply damage to a target."""
        target = self.characters[target_id]
        total_damage = 0

        logger.debug(f"[DEBUG] Applying damage to {target_id}")
        logger.debug(f"[DEBUG] Initial health: {target.health}")
        logger.debug(f"[DEBUG] Damage types: {damage_types}")

        # Create a mapping of lowercase to DamageType enum
        damage_type_map = {
            'physical': DamageType.PHYSICAL,
            'arcane': DamageType.ARCANE,
            'light': DamageType.LIGHT,
            'nature': DamageType.NATURE
        }

        for damage_type, amount in damage_types.items():
            # Get the enum from the lowercase name
            damage_type_enum = damage_type_map.get(damage_type)
            if damage_type_enum:
                # Get resistance and convert to percentage
                resist = target.get_resistance(damage_type_enum)  # Already a percentage
                logger.debug(f"[DEBUG] {damage_type}: amount={amount}, resistance={resist}%")
                reduced_damage = amount * (1 - resist / 100)
                logger.debug(f"[DEBUG] Reduced damage: {reduced_damage}")
                total_damage += reduced_damage
            else:
                logger.debug(f"[DEBUG] Unknown damage type: {damage_type}")

        # Apply total damage (rounded to nearest integer)
        total_damage = round(total_damage)
        logger.debug(f"[DEBUG] Total damage after rounding: {total_damage}")
        target.take_damage(total_damage)
        logger.debug(f"[DEBUG] Final health: {target.health}")
        return total_damage

    def _apply_battle_started(self, event: BattleStarted) -> None:
        """Apply BattleStarted event."""
        self.characters = {
            char_id: Character(
                name=char_data["name"],
                initiative=char_data["initiative"],
                armor=int(char_data["armor"]["physical"]),  # Already a percentage
                arcane_resist=int(char_data["armor"]["arcane"]),
                light_resist=int(char_data["armor"]["light"]),
                nature_resist=int(char_data["armor"]["nature"]),
                max_health=char_data["max_health"],
                tag="enemy" if char_data["is_enemy"] else "player"
            )
            for char_id, char_data in event.participants.items()
        }
        self.is_active = True
        self.version = event.metadata.version

    def _apply_round_started(self, event: RoundStarted) -> None:
        """Apply RoundStarted event."""
        self.current_round = event.round_number
        self.version = event.metadata.version

    def _apply_damage_dealt(self, event: DamageDealt) -> None:
        """Apply DamageDealt event."""
        self.version = event.metadata.version

    def _apply_healing_received(self, event: HealingReceived) -> None:
        """Apply HealingReceived event."""
        target = self.characters[event.target_id]
        target.health = min(
            target.max_health,
            target.health + event.healing_amount
        )
        target.temp_hp = event.temp_hp
        self.version = event.metadata.version

    def _apply_aggro_changed(self, event: AggroChanged) -> None:
        """Apply AggroChanged event."""
        enemy = self.characters[event.enemy_id]
        enemy.aggro[event.player_id] = event.new_total
        self.version = event.metadata.version

    def _apply_character_died(self, event: CharacterDied) -> None:
        """Apply CharacterDied event."""
        character = self.characters[event.character_id]
        character.health = 0
        self.version = event.metadata.version

    def _apply_battle_ended(self, event: BattleEnded) -> None:
        """Apply BattleEnded event."""
        self.is_active = False
        self.version = event.metadata.version
