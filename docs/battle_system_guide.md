# BattleBot Battle System Guide

This guide walks you through a complete battle sequence, showing exactly what to type and what you'll see. Follow along by copying the commands exactly as shown.

## Complete Battle Round Example

Here's a complete battle round showing exact console interaction:

```
=== BattleBot Game (Event-Sourced Version) ===

Choice > 1

Create Character:
Name > Warrior
Initiative > 15
Armor > 20
Arcane Resist > 10
Light Resist > 10
Nature Resist > 10
Max Health > 100
Tag (player/enemy) > player

Created Warrior!

Choice > 1

Create Character:
Name > Goblin
Initiative > 12
Armor > 10
Arcane Resist > 5
Light Resist > 5
Nature Resist > 5
Max Health > 50
Tag (player/enemy) > enemy

Created Goblin!

Choice > 2

Starting Battle Round 1

=== Using Event-Sourced Battle System ===
Created BattleAggregate with ID: 00000001-0000-0000-0000-000000000000
Participants: {
  "Warrior": {
    "name": "Warrior",
    "initiative": 15,
    "armor": {
      "physical": 0.2,
      "arcane": 0.1,
      "light": 0.1,
      "nature": 0.1
    },
    "max_health": 100,
    "is_enemy": false
  },
  "Goblin": {
    "name": "Goblin",
    "initiative": 12,
    "armor": {
      "physical": 0.1,
      "arcane": 0.05,
      "light": 0.05,
      "nature": 0.05
    },
    "max_health": 50,
    "is_enemy": true
  }
}

Warrior's turn > a
Target > Goblin
Block/dodge? > n
Damage > 20p

Goblin's turn > a
Target > Warrior
Block/dodge? > n
Damage > 10p

Battle Round Complete!

Character Status:
Warrior: 92/100 HP
Goblin: 34/50 HP
  Aggro: {'Warrior': 5.0}
```

## Under The Hood: Step-by-Step Implementation

Let's walk through exactly what happens in the code during this battle round:

## 1. Character Creation

When you enter `Choice > 1`, the main game loop in `battle_adapter.py` handles character creation:

```python
# In battle_adapter.py main()
def main():
    """Main game loop using event-sourced battle system."""
    print("=== BattleBot Game (Event-Sourced Version) ===")
    characters = []
    round_counter = 1

    while True:
        print("\nOptions:")
        print("1. Create character")
        # ...
        
        choice = input("\nChoice > ")
        
        if choice == "1":
            print("\nCreate Character:")
            name = input("Name > ")             # You enter: "Warrior"
            initiative = int(input("Initiative > "))  # You enter: 15
            armor = int(input("Armor > "))           # You enter: 20
            arcane_resist = int(input("Arcane Resist > "))  # You enter: 10
            light_resist = int(input("Light Resist > "))    # You enter: 10
            nature_resist = int(input("Nature Resist > "))  # You enter: 10
            max_health = int(input("Max Health > "))        # You enter: 100
            tag = input("Tag (player/enemy) > ")           # You enter: "player"
            
            char = Character(
                name=name,
                initiative=initiative,
                armor=armor,
                arcane_resist=arcane_resist,
                light_resist=light_resist,
                nature_resist=nature_resist,
                max_health=max_health,
                tag=tag
            )
            characters.append(char)
            print(f"\nCreated {char.name}!")
```

This creates a Character object using the Character class:

```python
# In battle_adapter.py
class Character:
    """Character data structure compatible with existing tests."""
    def __init__(
        self,
        name: str,
        initiative: int,
        armor: int,
        arcane_resist: int,
        light_resist: int,
        nature_resist: int,
        max_health: int,
        tag: str,
    ):
        self.name = name
        self.initiative = initiative
        self.armor = armor
        self.arcane_resist = arcane_resist
        self.light_resist = light_resist
        self.nature_resist = nature_resist
        self.max_health = max_health
        self.health = max_health
        self.temp_hp = 0
        self.tag = tag
        self.aggro = {} if tag == "enemy" else None
```

The same process happens when creating the Goblin, resulting in two Character objects in memory.

## 2. Starting the Battle

When you enter `Choice > 2`, the main loop calls `battle_round`:

```python
# In battle_adapter.py main()
elif choice == "2":
    if len(characters) < 2:
        print("\nNeed at least 2 characters to battle!")
        continue
        
    print("\nStarting Battle Round", round_counter)
    battle_round(characters, round_counter)
    round_counter += 1
```

The `battle_round` function handles the entire battle sequence:

```python
def battle_round(characters: List[Character], round_counter: int) -> bool:
    """Run a battle round with the given characters."""
    print("\n=== Using Event-Sourced Battle System ===")
    
    # Create battle aggregate with deterministic ID
    battle_id = UUID(int=round_counter)  # Creates 00000001-0000-0000-0000-000000000000
    battle = BattleAggregate(id=str(battle_id))
    print(f"Created BattleAggregate with ID: {battle_id}")
    
    # Convert character stats to battle format
    participants = {
        char.name: {
            "name": char.name,
            "initiative": char.initiative,
            "armor": {
                # Convert armor values to damage reduction percentages
                "physical": char.armor / 100,        # 20 becomes 0.2 (20%)
                "arcane": char.arcane_resist / 100,  # 10 becomes 0.1 (10%)
                "light": char.light_resist / 100,
                "nature": char.nature_resist / 100
            },
            "max_health": char.max_health,
            "is_enemy": char.tag == "enemy"
        }
        for char in characters
    }
    print(f"Participants: {json.dumps(participants, indent=2)}")
```

The battle is then started using the BattleAggregate:

```python
# In battle_adapter.py battle_round()
battle.handle_start_battle(StartBattle(
    aggregate_id=battle_id,
    participants=participants
))
```

This triggers the command handler in the aggregate:

```python
# In core/aggregates/battle.py
def handle_start_battle(self, cmd: StartBattle) -> List[BattleStarted]:
    """Handle StartBattle command."""
    if self.is_active:
        raise ValueError("Battle already in progress")

    # Create event
    event = BattleStarted(
        metadata=EventMetadata(
            aggregate_id=self.id,
            version=self.version + 1
        ),
        participants=cmd.participants
    )

    # Apply event
    self._apply_battle_started(event)
    return [event]

def _apply_battle_started(self, event: BattleStarted) -> None:
    """Apply BattleStarted event."""
    # Creates internal Character objects
    self.characters = {
        char_id: Character(
            name=char_data["name"],
            initiative=char_data["initiative"],
            armor=char_data["armor"],
            max_health=char_data["max_health"],
            is_enemy=char_data["is_enemy"]
        )
        for char_id, char_data in event.participants.items()
    }
    self.is_active = True
    self.version = event.metadata.version
```

## 3. Initiative and Turn Order

After battle start, the round is started:

```python
# In battle_adapter.py battle_round()
events = battle.handle_start_round(StartRound(aggregate_id=battle_id))
round_event = events[0]
initiative_order = round_event.initiative_order
```

This triggers the round start handler:

```python
# In core/aggregates/battle.py
def handle_start_round(self, cmd: StartRound) -> List[RoundStarted]:
    """Handle StartRound command."""
    if not self.is_active:
        raise ValueError("Battle not started")

    # Sort characters by initiative
    sorted_chars = sorted(
        self.characters.keys(),
        key=lambda x: self.characters[x].initiative,
        reverse=True
    )

    # Create event
    event = RoundStarted(
        metadata=EventMetadata(
            aggregate_id=self.id,
            version=self.version + 1
        ),
        round_number=self.current_round + 1,
        initiative_order=sorted_chars
    )

    # Apply event
    self._apply_round_started(event)
    return [event]

def _apply_round_started(self, event: RoundStarted) -> None:
    """Apply RoundStarted event."""
    self.current_round = event.round_number
    self.version = event.metadata.version
```

## 4. Combat Actions

The battle_round function then processes each character's turn:

```python
# In battle_adapter.py battle_round()
for char_name in initiative_order:
    char = next(c for c in characters if c.name == char_name)
    while True:
        action = input(f"{char.name}'s turn > ")  # You enter: "a"
        if action == "e":
            break
        elif action == "a":
            # Handle attack
            target_name = input("Target > ")        # You enter: "Goblin"
            _ = input("Block/dodge? > ")            # You enter: "n"
            damage_str = input("Damage > ")         # You enter: "20p"
            
            # Parse damage string
            amount = int(damage_str[:-1])          # Extracts 20
            damage_type = "physical" if damage_str.endswith("p") else "unknown"
            
            # Create and handle damage command
            battle.handle_deal_damage(DealDamage(
                aggregate_id=battle_id,
                source_id=char.name,
                target_id=target_name,
                damage_types={damage_type: amount}
            ))
```

The damage command is handled by the aggregate:

```python
# In core/aggregates/battle.py
def handle_deal_damage(self, cmd: DealDamage) -> List[DamageDealt | CharacterDied]:
    """Handle DealDamage command."""
    if not self.is_active:
        raise ValueError("Battle not started")

    target = self.characters[cmd.target_id]
    
    # Calculate actual damage after resistances
    total_damage = self.apply_damage(cmd.target_id, cmd.damage_types)

    # Create damage event
    events = []
    damage_event = DamageDealt(
        metadata=EventMetadata(
            aggregate_id=self.id,
            version=self.version + 1
        ),
        source_id=cmd.source_id,
        target_id=cmd.target_id,
        damage_types=cmd.damage_types,
        actual_damage=total_damage
    )
    events.append(damage_event)

    # Apply damage event
    self._apply_damage_dealt(damage_event)

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

    return events
```

## 5. Round Completion

After all turns, the character states are synchronized:

```python
# In battle_adapter.py battle_round()
# Update character states from battle state
for char in characters:
    battle_char = battle.characters[char.name]
    char.health = battle_char.health      # Update health
    char.temp_hp = battle_char.temp_hp    # Update temp HP
    if char.tag == "enemy":
        char.aggro = battle_char.aggro.copy()  # Update aggro

# Back in main(), display final status
print("\nBattle Round Complete!")
print("\nCharacter Status:")
for char in characters:
    print(f"{char.name}: {char.health}/{char.max_health} HP", end="")
    if char.temp_hp > 0:
        print(f" (+{char.temp_hp} temp)")
    else:
        print()
    if char.tag == "enemy" and char.aggro:
        print(f"  Aggro: {char.aggro}")
```

This completes the battle round, showing:
```
Character Status:
Warrior: 92/100 HP         # After taking 8 damage (10 - 20% armor)
Goblin: 32/50 HP          # After taking 18 damage (20 - 10% armor)
  Aggro: {'Warrior': 4.5}  # From dealing 18 damage * 0.25
```

## Event-Sourced Battle System

The battle system uses an event-sourced architecture, where all state changes are driven by commands and recorded as events.

## Commands

Commands represent user intentions. Each command is handled by the battle aggregate to produce one or more events:

```python
# In core/commands/battle_commands.py

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
```

## Events

Events record what happened as a result of commands. Each event updates the battle state:

```python
# In core/events/battle_events.py

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
    killing_blow: Optional[Dict] = field(default=None)

@dataclass
class BattleEnded:
    """Event emitted when the battle ends."""
    metadata: EventMetadata
    winner: str  # "players" or "enemies"
    survivors: List[str]
    rounds_taken: int = field(default=0)
```

## Command -> Event Flow

Here's how a typical command flows through the system to produce events:

1. **User Action -> Command**:
```python
# User enters "a" for attack
action = input(f"{char.name}'s turn > ")  # "a"
target = input("Target > ")               # "Goblin" 
damage = input("Damage > ")               # "20p"

# Parse damage string
amount = int(damage[:-1])          # Extracts 20
damage_type = "physical" if damage.endswith("p") else "unknown"
            
# Create and handle damage command
cmd = DealDamage(
    aggregate_id=battle_id,
    source_id="Warrior",
    target_id="Goblin", 
    damage_types={damage_type: amount}
)
```

2. **Command Handler -> Events**:
```python
# BattleAggregate processes command
def handle_deal_damage(self, cmd):
    # Validate battle state
    if not self.is_active:
        raise ValueError("Battle not started")
    
    # Calculate damage with resistances
    target = self.characters[cmd.target_id]  # Get Goblin
    total_damage = self.apply_damage(
        cmd.target_id,
        cmd.damage_types
    )  # Returns 18 (20 - 10% armor)
    
    # Create damage event
    damage_event = DamageDealt(
        metadata=EventMetadata(
            aggregate_id=self.id,
            version=self.version + 1
        ),
        source_id="Warrior",
        target_id="Goblin",
        damage_types={"physical": 20},
        actual_damage=18
    )
    
    # Apply damage event
    self._apply_damage_dealt(damage_event)
    
    # Generate aggro since target is enemy
    aggro_cmd = ModifyAggro(
        aggregate_id=self.id,
        enemy_id="Goblin",
        player_id="Warrior",
        aggro_change=int(18 * 0.25)  # 4.5 aggro
    )
    
    # Handle aggro command
    aggro_events = self.handle_modify_aggro(aggro_cmd)
    
    return [damage_event] + aggro_events
```

3. **State Updates**:
- Goblin health: 50 -> 32 (after 18 damage)
- Goblin aggro: 0 -> 4.5 (for Warrior)
- Battle version: n -> n+2 (after two events)

4. **Final State Sync** (in battle_adapter.py):
```python
# Sync character states from battle aggregate
for char in characters:
    battle_char = battle.characters[char.name]
    char.health = battle_char.health      # Copy health
    char.temp_hp = battle_char.temp_hp    # Copy temp HP
    if char.tag == "enemy":
        char.aggro = battle_char.aggro.copy()  # Copy aggro
```

This event-sourced design ensures that:
1. All state changes are tracked through events
2. State can only be modified through commands
3. The battle can be replayed by replaying events
4. Complex mechanics (damage, aggro) are handled consistently

## Damage Type System

The battle system uses a centralized damage type system defined in `core/domain/damage_types.py`:

```python
from enum import Enum

class DamageType(Enum):
    """Enumeration of all damage types in the battle system."""
    PHYSICAL = "p"  # Physical damage
    ARCANE = "a"    # Arcane damage
    LIGHT = "l"     # Light damage
    NATURE = "n"    # Nature damage
    AGGRO = "g"     # Aggro changes
    TEMP_HP = "t"   # Temporary HP
    
    @property
    def full_name(self) -> str:
        """Get the full name of the damage type."""
        return {
            "p": "physical",
            "a": "arcane",
            "l": "light",
            "n": "nature",
            "g": "aggro",
            "t": "temp_hp"
        }[self.value]
    
    @classmethod
    def parse_damage_string(cls, damage_str: str) -> Dict[str, int]:
        """Parse a damage string into a dictionary of damage types and amounts."""
        # Example: "40p 30l" -> {"physical": 40, "light": 30}
        return {
            dtype.full_name: amount 
            for dtype, amount in cls._parse_parts(damage_str)
        }
```

### Damage String Format

Damage is specified using a space-separated string of amount-type pairs:

- `40p`: 40 physical damage
- `30l`: 30 light damage
- `20a`: 20 arcane damage
- `10n`: 10 nature damage
- `5g`: 5 aggro
- `15t`: 15 temporary HP

Multiple damage types can be combined:
```
40p 30l    # 40 physical + 30 light damage
20a 10n 5g # 20 arcane + 10 nature + 5 aggro
```

## Command -> Event Flow

Here's how a typical command flows through the system to produce events:

1. **User Action -> Command**:
```python
# User enters "a" for attack
action = input(f"{char.name}'s turn > ")  # "a"
target = input("Target > ")               # "Goblin" 
damage = input("Damage > ")               # "20p"

# Parse damage string using DamageType
damage_types = DamageType.parse_damage_string(damage)  # {"physical": 20}

# Creates DealDamage command
cmd = DealDamage(
    aggregate_id=battle_id,
    source_id="Warrior",
    target_id="Goblin", 
    damage_types=damage_types
)
```

## Internal Character State Management

The battle system maintains two separate character representations:

1. **External Character** (in battle_adapter.py):
```python
class Character:
    """Character data structure compatible with existing tests."""
    def __init__(
        self,
        name: str,
        initiative: int,
        armor: int,             # Raw armor value (e.g., 20)
        arcane_resist: int,     # Raw resist value (e.g., 10)
        light_resist: int,
        nature_resist: int,
        max_health: int,
        tag: str,
    ):
        self.name = name
        self.initiative = initiative
        self.armor = armor
        self.arcane_resist = arcane_resist
        self.light_resist = light_resist
        self.nature_resist = nature_resist
        self.max_health = max_health
        self.health = max_health
        self.temp_hp = 0
        self.tag = tag
        self.aggro = {} if tag == "enemy" else None
```

2. **Internal Character** (in core/aggregates/battle.py):
```python
@dataclass
class Character:
    """Internal character state."""
    name: str
    initiative: int
    armor: Dict[str, float]     # Converted to percentages (e.g., 0.2 for 20%)
    max_health: int
    is_enemy: bool
    health: int = field(init=False)
    temp_hp: int = field(default=0)
    aggro: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        self.health = self.max_health
```

The key differences are:

1. **Armor System**:
   - External: Uses raw integer values (e.g., 20 armor)
   - Internal: Converts to percentage reduction (e.g., 0.2 for 20% reduction)

2. **Enemy Tracking**:
   - External: Uses `tag == "enemy"` check
   - Internal: Uses explicit `is_enemy` boolean

3. **Aggro Management**:
   - External: Only creates aggro dict for enemies
   - Internal: Always has aggro dict, but only used for enemies

The conversion happens during battle initialization:

```python
# In battle_adapter.py battle_round()
participants = {
    char.name: {
        "name": char.name,
        "initiative": char.initiative,
        "armor": {
            # Convert raw values to percentages
            "physical": char.armor / 100,        # 20 -> 0.2
            "arcane": char.arcane_resist / 100,  # 10 -> 0.1
            "light": char.light_resist / 100,
            "nature": char.nature_resist / 100
        },
        "max_health": char.max_health,
        "is_enemy": char.tag == "enemy"
    }
    for char in characters
}

# Create battle with converted stats
battle.handle_start_battle(StartBattle(
    aggregate_id=battle_id,
    participants=participants
))
```

The battle aggregate then creates internal characters:

```python
# In core/aggregates/battle.py BattleAggregate._apply_battle_started
def _apply_battle_started(self, event: BattleStarted) -> None:
    """Apply BattleStarted event."""
    self.characters = {
        char_id: Character(
            name=char_data["name"],
            initiative=char_data["initiative"],
            armor=char_data["armor"],  # Already in percentage form
            max_health=char_data["max_health"],
            is_enemy=char_data["is_enemy"]
        )
        for char_id, char_data in event.participants.items()
    }
    self.is_active = True
    self.version = event.metadata.version
```

After each action, the states are synchronized back:

```python
# In battle_adapter.py battle_round()
# Sync character states from battle aggregate
for char in characters:
    battle_char = battle.characters[char.name]
    char.health = battle_char.health      # Copy health
    char.temp_hp = battle_char.temp_hp    # Copy temp HP
    if char.tag == "enemy":
        char.aggro = battle_char.aggro.copy()  # Copy aggro
```

This dual representation allows:
1. **Clean Interface**: External characters match the expected test interface
2. **Efficient Processing**: Internal characters use optimized data structures
3. **Type Safety**: Internal characters use strict typing and validation
4. **Separation of Concerns**: Battle logic is isolated from interface code

## Battle Aggregate Internal State

The `BattleAggregate` class maintains the battle's internal state and ensures all state changes happen through commands and events:

```python
# In core/aggregates/battle.py
class BattleAggregate:
    """Aggregate root for battle state."""
    def __init__(self, id: str):
        self.id = id
        self.version = 0
        self.is_active = False
        self.current_round = 0
        self.characters: Dict[str, Character] = {}

    def handle_start_battle(self, cmd: StartBattle) -> List[BattleStarted]:
        """Handle StartBattle command."""
        if self.is_active:
            raise ValueError("Battle already in progress")

        # Create event
        event = BattleStarted(
            metadata=EventMetadata(
                aggregate_id=self.id,
                version=self.version + 1
            ),
            participants=cmd.participants
        )

        # Apply event
        self._apply_battle_started(event)
        return [event]

    def _apply_battle_started(self, event: BattleStarted) -> None:
        """Apply BattleStarted event."""
        # Creates internal Character objects
        self.characters = {
            char_id: Character(
                name=char_data["name"],
                initiative=char_data["initiative"],
                armor=char_data["armor"],
                max_health=char_data["max_health"],
                is_enemy=char_data["is_enemy"]
            )
            for char_id, char_data in event.participants.items()
        }
        self.is_active = True
        self.version = event.metadata.version
```

The aggregate maintains several important invariants:

1. **Version Control**: Each event increments the version number
```python
def _apply_any_event(self, event: Event) -> None:
    """Apply any event to update version."""
    self.version = event.metadata.version
```

2. **Battle State**: Only one battle can be active at a time
```python
def handle_any_command(self, cmd: Command) -> List[Event]:
    """Handle any command."""
    if not self.is_active:
        raise ValueError("Battle not started")
    # ... handle command
```

3. **Character State**: Characters can only be modified through events
```python
def apply_damage(self, target_id: str, damage_types: Dict[str, int]) -> int:
    """Apply damage to a target."""
    target = self.characters[target_id]
    total_damage = 0
    
    # Calculate damage reduction from armor
    for damage_type, amount in damage_types.items():
        resist = target.armor.get(damage_type, 0)
        reduced_damage = amount * (1 - resist)
        total_damage += reduced_damage
    
    # Apply to health/temp HP
    if target.temp_hp > 0:
        absorbed = min(target.temp_hp, total_damage)
        target.temp_hp -= absorbed
        total_damage -= absorbed
    
    if total_damage > 0:
        old_health = target.health
        target.health = max(0, target.health - total_damage)
        return old_health - target.health
    
    return 0
```

4. **Event Ordering**: Events must be applied in sequence
```python
def handle_deal_damage(self, cmd: DealDamage) -> List[Event]:
    """Handle DealDamage command."""
    events = []
    
    # First apply damage
    damage_event = DamageDealt(...)
    events.append(damage_event)
    self._apply_damage_dealt(damage_event)
    
    # Then check for death
    if self.characters[cmd.target_id].health <= 0:
        death_event = CharacterDied(...)
        events.append(death_event)
        self._apply_character_died(death_event)
    
    return events
```

5. **Aggro Management**: Only enemies track aggro
```python
def handle_modify_aggro(self, cmd: ModifyAggro) -> List[AggroChanged]:
    """Handle ModifyAggro command."""
    enemy = self.characters[cmd.enemy_id]
    if not enemy.is_enemy:
        raise ValueError("Can only modify aggro for enemies")
    
    current = enemy.aggro.get(cmd.player_id, 0)
    new_total = current + cmd.aggro_change
    
    event = AggroChanged(...)
    self._apply_aggro_changed(event)
    return [event]
```

## Example: Complete Attack Flow

Let's trace a complete attack from console input to state change:

1. **User Input**:
```
Warrior's turn > a
Target > Goblin
Block/dodge? > n
Damage > 20p
```

2. **Command Creation** (in battle_adapter.py):
```python
# Parse damage input
amount = int("20"[:-1])  # Get 20 from "20p"
damage_type = "physical" # "p" indicates physical damage

# Create command
cmd = DealDamage(
    aggregate_id=battle_id,
    source_id="Warrior",
    target_id="Goblin", 
    damage_types={"physical": amount}
)
```

3. **Command Handling** (in BattleAggregate):
```python
def handle_deal_damage(self, cmd):
    # Validate battle state
    if not self.is_active:
        raise ValueError("Battle not started")
    
    # Calculate damage with resistances
    target = self.characters[cmd.target_id]  # Get Goblin
    total_damage = self.apply_damage(
        cmd.target_id,
        cmd.damage_types
    )  # Returns 18 (20 - 10% armor)
    
    # Create damage event
    damage_event = DamageDealt(
        metadata=EventMetadata(
            aggregate_id=self.id,
            version=self.version + 1
        ),
        source_id="Warrior",
        target_id="Goblin",
        damage_types={"physical": 20},
        actual_damage=18
    )
    
    # Apply damage event
    self._apply_damage_dealt(damage_event)
    
    # Generate aggro since target is enemy
    aggro_cmd = ModifyAggro(
        aggregate_id=self.id,
        enemy_id="Goblin",
        player_id="Warrior",
        aggro_change=int(18 * 0.25)  # 4.5 aggro
    )
    
    # Handle aggro command
    aggro_events = self.handle_modify_aggro(aggro_cmd)
    
    return [damage_event] + aggro_events
```

4. **State Updates**:
- Goblin health: 50 -> 32 (after 18 damage)
- Goblin aggro: 0 -> 4.5 (for Warrior)
- Battle version: n -> n+2 (after two events)

5. **Final State Sync** (in battle_adapter.py):
```python
# Sync character states from battle aggregate
for char in characters:
    battle_char = battle.characters[char.name]
    char.health = battle_char.health      # Copy health
    char.temp_hp = battle_char.temp_hp    # Copy temp HP
    if char.tag == "enemy":
        char.aggro = battle_char.aggro.copy()  # Copy aggro
```

This event-sourced design ensures that:
1. All state changes are tracked through events
2. State can only be modified through commands
3. The battle can be replayed by replaying events
4. Complex mechanics (damage, aggro) are handled consistently

## Starting the Battle System

Run the battle adapter script:
```bash
python battle_adapter.py
```

You'll see:
```
=== BattleBot Game (Event-Sourced Version) ===

Options:
1. Create character
2. Start battle round
3. Show characters
4. Exit

Choice >
```

## Creating Characters

Let's create a player character and an enemy. First, the player:

```
Choice > 1

Create Character:
Name > Warrior
Initiative > 15
Armor > 20
Arcane Resist > 10
Light Resist > 10
Nature Resist > 10
Max Health > 100
Tag (player/enemy) > player

Created Warrior!
```

Now create an enemy:

```
Choice > 1

Create Character:
Name > Goblin
Initiative > 12
Armor > 10
Arcane Resist > 5
Light Resist > 5
Nature Resist > 5
Max Health > 50
Tag (player/enemy) > enemy

Created Goblin!
```

## Checking Character Status

Let's verify our characters:

```
Choice > 3

Characters:

Warrior (player)
  Health: 100/100
  Initiative: 15
  Armor: 20
  Resists: 10a/10l/10n

Goblin (enemy)
  Health: 50/50
  Initiative: 12
  Armor: 10
  Resists: 5a/5l/5n
  Aggro: {}
```

## Combat Actions

During your turn, you can:
- Attack with `a`
- End turn with `e`

Let's attack the Goblin:

```
Warrior's turn > a
Target > Goblin
Block/dodge? > n
Damage > 20p

Goblin's turn > a
Target > Warrior
Block/dodge? > n
Damage > 10p
```

After the round completes, you'll see the updated status:

```
Battle Round Complete!

Character Status:
Warrior: 92/100 HP
Goblin: 34/50 HP
  Aggro: {'Warrior': 5.0}
```

## Ending the Game

To exit the game:

```
Choice > 4

Thanks for playing!