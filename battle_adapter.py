"""Adapter module to maintain compatibility with existing battle system tests."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4
import json
import logging

from core.aggregates.battle import BattleAggregate
from core.commands.battle_commands import (
    StartBattle,
    StartRound,
    DealDamage,
    ApplyHealing,
    ModifyAggro,
    EndBattle,
)
from core.domain.character import Character as CoreCharacter
from core.domain.damage_types import DamageType
from core.logging_config import setup_logging
from Battle import parse_damage_input

# Set up module logger
logger = logging.getLogger(__name__)


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
        logger.debug(f"Creating new Character: {name} (tag: {tag})")
        self._core_char = CoreCharacter(
            name=name,
            initiative=initiative,
            armor=armor,
            arcane_resist=arcane_resist,
            light_resist=light_resist,
            nature_resist=nature_resist,
            max_health=max_health,
            tag=tag,
        )
        logger.debug(
            f"Character {name} created with stats: initiative={initiative}, armor={armor}, "
            f"resists=[arcane={arcane_resist}, light={light_resist}, nature={nature_resist}], "
            f"max_health={max_health}"
        )

    @property
    def name(self) -> str:
        return self._core_char.name

    @property
    def initiative(self) -> int:
        return self._core_char.initiative

    @property
    def armor(self) -> int:
        """Get physical armor value."""
        return self._core_char.armor

    @property
    def arcane_resist(self) -> int:
        """Get arcane resistance value."""
        return self._core_char.arcane_resist

    @property
    def light_resist(self) -> int:
        """Get light resistance value."""
        return self._core_char.light_resist

    @property
    def nature_resist(self) -> int:
        """Get nature resistance value."""
        return self._core_char.nature_resist

    @property
    def max_health(self) -> int:
        return self._core_char.max_health

    @property
    def health(self) -> int:
        """Get current health."""
        return self._core_char.health

    @health.setter
    def health(self, value: int) -> None:
        """Set current health."""
        self._core_char.health = value

    @property
    def temp_hp(self) -> int:
        """Get temporary HP."""
        return self._core_char.temp_hp

    @temp_hp.setter
    def temp_hp(self, value: int) -> None:
        """Set temporary HP."""
        self._core_char.temp_hp = value

    @property
    def tag(self) -> str:
        return self._core_char.tag

    @property
    def aggro(self) -> Dict[str, float]:
        """Get aggro dictionary."""
        return self._core_char.aggro if self.tag == "enemy" else {}

    @aggro.setter
    def aggro(self, value: Dict[str, float]) -> None:
        """Set aggro dictionary."""
        if self.tag == "enemy":
            self._core_char.aggro = value

    def add_aggro(
        self, player_name: str, amount: int, characters: List["Character"]
    ) -> None:
        """Add aggro for a player."""
        self._core_char.add_aggro(player_name, amount)

    def get_highest_aggro(self) -> str | List[str]:
        """Get the player(s) with highest aggro."""
        return self._core_char.get_highest_aggro()

    def heal(
        self, heal_dict: Dict[str, int], healer_name: str, characters: List["Character"]
    ) -> Tuple[int, int]:
        """Apply healing to the character."""
        healing = heal_dict.get("h", 0)
        temp = heal_dict.get("t", 0)
        return self._core_char.heal(healing, temp, healer_name)


def battle_round(characters: List[Character], round_counter: int) -> bool:
    """Run a battle round with the given characters.

    Args:
        characters: List of characters
        round_counter: Current round number

    Returns:
        True if round completed successfully
    """
    logger.info(f"Starting battle round {round_counter}")
    logger.debug(f"Characters in round: {[char.name for char in characters]}")

    # Convert to core characters
    core_chars = [char._core_char for char in characters]

    # Create battle aggregate
    battle_id = uuid4()
    logger.debug(f"Creating battle with ID: {battle_id}")
    battle = BattleAggregate(battle_id)

    # Start battle if first round
    if round_counter == 1:
        logger.info("Initializing new battle")
        battle.handle_start_battle(StartBattle(battle_id, core_chars))

    # Start round
    logger.debug(f"Starting round {round_counter}")
    battle.handle(StartRound(battle_id, round_counter))

    # Process each character's turn based on initiative order
    for char_name in battle.get_initiative_order():
        char = next(c for c in characters if c.name == char_name)
        while True:
            action = input(f"{char.name}'s turn > ")
            if action == "e":
                break
            elif action == "a":
                # Handle attack
                target_name = input("Target > ")
                _ = input("Block/dodge? > ")  # Ignored for now
                damage_str = input("Damage > ")

                # Parse damage string (e.g., "40p 30l" for 40 physical + 30 light)
                damage_types = DamageType.parse_damage_string(damage_str)
                if not damage_types:
                    print("Invalid damage format")
                    continue

                # Create and handle damage command
                battle.handle(
                    DealDamage(battle_id, char.name, target_name, damage_types)
                )

                # Sync character states after each action
                for c in characters:
                    c.health = battle.get_character(c.name).health
                    c.temp_hp = battle.get_character(c.name).temp_hp
                    if c.tag == "enemy":
                        c.aggro = battle.get_character(c.name).aggro.copy()

    # Final sync at end of round
    for c in characters:
        c.health = battle.get_character(c.name).health
        c.temp_hp = battle.get_character(c.name).temp_hp
        if c.tag == "enemy":
            c.aggro = battle.get_character(c.name).aggro.copy()
    return True


def main():
    """Main game loop using event-sourced battle system."""
    # Initialize logging
    setup_logging()
    logger.info("Starting BattleBot main game loop")
    game_state = {"round": 1}
    logger.debug(f"Initializing game state: {game_state}")
    characters = []
    round_counter = game_state["round"]

    while True:
        print("\nOptions:")
        print("1. Create character")
        print("2. Start battle round")
        print("3. Show characters")
        print("4. Exit")

        choice = input("\nChoice > ")

        if choice == "1":
            print("\nCreate Character:")
            name = input("Name > ")
            initiative = int(input("Initiative > "))
            armor = int(input("Armor > "))
            arcane_resist = int(input("Arcane Resist > "))
            light_resist = int(input("Light Resist > "))
            nature_resist = int(input("Nature Resist > "))
            max_health = int(input("Max Health > "))
            tag = input("Tag (player/enemy) > ")

            char = Character(
                name=name,
                initiative=initiative,
                armor=armor,
                arcane_resist=arcane_resist,
                light_resist=light_resist,
                nature_resist=nature_resist,
                max_health=max_health,
                tag=tag,
            )
            characters.append(char)
            print(f"\nCreated {char.name}!")

        elif choice == "2":
            if len(characters) < 2:
                print("\nNeed at least 2 characters to battle!")
                continue

            print("\nStarting Battle Round", round_counter)
            battle_round(characters, round_counter)
            round_counter += 1

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

            # Save game state
            logger.debug("Saving game state to file")
            with open("game_save.txt", "w") as f:
                json.dump({"round": round_counter}, f)
                logger.debug("Game state saved")

        elif choice == "3":
            print("\nCharacters:")
            for char in characters:
                print(f"\n{char.name} ({char.tag})")
                print(f"  Health: {char.health}/{char.max_health}")
                print(f"  Initiative: {char.initiative}")
                print(f"  Armor: {char.armor}")
                print(
                    f"  Resists: {char.arcane_resist}a/{char.light_resist}l/{char.nature_resist}n"
                )
                if char.tag == "enemy" and char.aggro:
                    print(f"  Aggro: {char.aggro}")

        elif choice == "4":
            print("\nThanks for playing!")
            break

        else:
            print("\nInvalid choice!")


if __name__ == "__main__":
    # Original input function reference
    original_input = input

    # Predefined inputs
    predefined_inputs = iter(
        [
            "1",
            "player1",
            "10",
            "10",
            "10",
            "10",
            "10",
            "100",
            "player",
            "1",
            "enemy1",
            "5",
            "5",
            "5",
            "5",
            "5",
            "200",
            "enemy",
            "2",
        ]
    )

    # Custom input function
    def custom_input(prompt=""):
        try:
            return next(predefined_inputs)
        except StopIteration:
            return original_input(prompt)

    input = custom_input
    main()
