import curses
import json
from typing import List, Dict, Optional, Tuple
import time

# Import existing Character class and related functions
from Battle import (
    Character,
    save_game,
    load_game,
    parse_damage_input,
    parse_healing_input,
)


class BattleUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)  # Health
        curses.init_pair(2, curses.COLOR_RED, -1)  # Damage
        curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Warnings
        curses.init_pair(4, curses.COLOR_CYAN, -1)  # Info
        self.setup_windows()
        self.log_messages = []
        self.input_buffer = ""
        self.current_round = 1

    def setup_windows(self):
        height, width = self.stdscr.getmaxyx()
        # Stats window (left side, 70% height)
        self.stats_win = curses.newwin(int(height * 0.7), int(width * 0.6), 0, 0)
        self.stats_win.box()

        # Log window (right side, 70% height)
        self.log_win = curses.newwin(
            int(height * 0.7), int(width * 0.4), 0, int(width * 0.6)
        )
        self.log_win.box()

        # Input window (bottom, 30% height)
        self.input_win = curses.newwin(int(height * 0.3), width, int(height * 0.7), 0)
        self.input_win.box()

    def add_log(self, message: str):
        timestamp = time.strftime("%H:%M:%S")
        self.log_messages.append(f"[{timestamp}] {message}")
        if len(self.log_messages) > 100:  # Keep only last 100 messages
            self.log_messages.pop(0)
        self.refresh_log()

    def refresh_log(self):
        self.log_win.clear()
        self.log_win.box()
        height, width = self.log_win.getmaxyx()
        self.log_win.addstr(0, 2, "Battle Log")

        # Show last messages that fit in the window
        display_messages = self.log_messages[-(height - 2) :]
        for i, msg in enumerate(display_messages):
            if i < height - 2:  # Leave room for border
                try:
                    self.log_win.addstr(i + 1, 1, msg[: width - 2])
                except curses.error:
                    pass
        self.log_win.refresh()

    def display_stats(self, characters: List[Character], current_index: int):
        self.stats_win.clear()
        self.stats_win.box()
        self.stats_win.addstr(0, 2, f"Battle Status - Round {self.current_round}")

        for i, char in enumerate(characters):
            y_pos = i * 4 + 1
            if y_pos >= self.stats_win.getmaxyx()[0] - 4:
                break

            # Highlight current character
            if i == current_index:
                self.stats_win.attron(curses.A_BOLD)
                self.stats_win.addstr(y_pos, 1, "→ ")
            else:
                self.stats_win.addstr(y_pos, 1, "  ")

            # Display character name and tag
            self.stats_win.addstr(f"{char.name} ({char.tag})")
            self.stats_win.attroff(curses.A_BOLD)

            # Health bar
            health_percent = char.health / char.max_health
            health_color = (
                curses.color_pair(1) if health_percent > 0.3 else curses.color_pair(2)
            )
            self.stats_win.addstr(y_pos + 1, 3, f"HP: ", curses.A_DIM)
            self.stats_win.addstr(f"{char.health}/{char.max_health}", health_color)
            if char.temp_hp > 0:
                self.stats_win.addstr(f" (+{char.temp_hp})", curses.color_pair(4))

            # Resistances
            self.stats_win.addstr(
                y_pos + 2,
                3,
                f"ARM:{char.armor} ARC:{char.arcane_resist} LGT:{char.light_resist} NAT:{char.nature_resist}",
                curses.A_DIM,
            )

            # Show aggro for enemies
            if char.tag == "enemy" and hasattr(char, "aggro"):
                aggro_info = char.get_highest_aggro()
                if isinstance(aggro_info, list):
                    aggro_text = f"Aggro: {', '.join(aggro_info)}"
                else:
                    aggro_text = str(aggro_info)
                self.stats_win.addstr(y_pos + 3, 3, aggro_text, curses.color_pair(3))

        self.stats_win.refresh()

    def get_input(self, prompt: str) -> str:
        height, width = self.input_win.getmaxyx()
        self.input_win.clear()
        self.input_win.box()
        self.input_win.addstr(0, 2, "Input")
        self.input_win.addstr(1, 1, prompt)
        self.input_win.refresh()

        curses.echo()
        input_str = self.input_win.getstr(2, 1, width - 3).decode("utf-8")
        curses.noecho()
        return input_str

    def show_help(self):
        help_text = [
            "Available Commands:",
            "attack <target> <type>:<amount> - Attack a target (e.g., 'attack Goblin p:10')",
            "heal <target> <type>:<amount> - Heal a target (e.g., 'heal Warrior h:20')",
            "stats - Show detailed stats",
            "save - Save game",
            "load - Load game",
            "quit - Exit game",
            "help - Show this help",
            "",
            "Damage Types: p (physical), a (arcane), l (light), n (nature), g (aggro)",
            "Healing Types: h (healing), t (temporary HP)",
            "",
            "Press any key to continue...",
        ]

        height, width = self.input_win.getmaxyx()
        self.input_win.clear()
        self.input_win.box()
        for i, line in enumerate(help_text):
            if i < height - 2:
                self.input_win.addstr(i + 1, 1, line[: width - 2])
        self.input_win.refresh()
        self.input_win.getch()


def battle_round_ncurses(
    ui: BattleUI, characters: List[Character], round_counter: int
) -> bool:
    ui.current_round = round_counter
    # Sort characters by initiative
    characters.sort(key=lambda x: x.initiative, reverse=True)

    for current_index, current_char in enumerate(characters):
        if current_char.health <= 0:
            continue

        ui.display_stats(characters, current_index)
        ui.add_log(f"{current_char.name}'s turn")

        while True:
            command = (
                ui.get_input(
                    f"{current_char.name}'s action (type 'help' for commands): "
                )
                .strip()
                .lower()
            )

            if command == "help":
                ui.show_help()
                continue

            if command == "quit":
                return False

            if command == "stats":
                continue  # Stats are already shown

            if command.startswith("save"):
                with open("game_save.txt", "w") as file:
                    json.dump([to_dict(char) for char in characters], file)
                ui.add_log("Game saved")
                continue

            if command.startswith("load"):
                try:
                    with open("game_save.txt", "r") as file:
                        characters_data = json.load(file)
                        characters[:] = [from_dict(data) for data in characters_data]
                    ui.add_log("Game loaded")
                except (FileNotFoundError, json.JSONDecodeError):
                    ui.add_log("No save file found or file corrupted")
                continue

            if command.startswith("attack ") or command == "a":
                try:
                    _, target_name, damage_input = command.split(" ", 2)
                    target = next(
                        (
                            c
                            for c in characters
                            if c.name.lower() == target_name.lower()
                        ),
                        None,
                    )
                    if not target:
                        ui.add_log(f"Target {target_name} not found")
                        continue

                    damage_dict = parse_damage_input(damage_input)
                    damage_dealt = target.calculate_damage(
                        damage_dict, current_char.name, characters
                    )
                    ui.add_log(
                        f"{current_char.name} dealt {damage_dealt} damage to {target.name}"
                    )
                    break
                except ValueError:
                    ui.add_log(
                        "Invalid attack command. Format: attack <target> <type>:<amount>"
                    )
                    continue

            if command.startswith("heal ") or command == "h":
                try:
                    _, target_name, healing_input = command.split(" ", 2)
                    target = next(
                        (
                            c
                            for c in characters
                            if c.name.lower() == target_name.lower()
                        ),
                        None,
                    )
                    if not target:
                        ui.add_log(f"Target {target_name} not found")
                        continue

                    healing_dict = parse_healing_input(healing_input)
                    healing, temp_hp = target.heal(
                        healing_dict, current_char.name, characters
                    )
                    ui.add_log(
                        f"{current_char.name} healed {target.name} for {healing} HP and {temp_hp} temp HP"
                    )
                    break
                except ValueError:
                    ui.add_log(
                        "Invalid heal command. Format: heal <target> <type>:<amount>"
                    )
                    continue

            ui.add_log("Invalid command. Type 'help' for available commands")

        ui.display_stats(characters, current_index)

        # Check if all players or all enemies are defeated
        players_alive = any(c.health > 0 for c in characters if c.tag == "player")
        enemies_alive = any(c.health > 0 for c in characters if c.tag == "enemy")

        if not players_alive:
            ui.add_log("All players have been defeated!")
            return False
        if not enemies_alive:
            ui.add_log("All enemies have been defeated!")
            return False

    return True


def to_dict(char):
    return {
        "name": char.name,
        "initiative": char.initiative,
        "armor": char.armor,
        "arcane_resist": char.arcane_resist,
        "light_resist": char.light_resist,
        "nature_resist": char.nature_resist,
        "max_health": char.max_health,
        "tag": char.tag,
        "health": char.health,
        "temp_hp": char.temp_hp,
        "aggro": char.aggro if hasattr(char, "aggro") else None,
    }


def from_dict(data):
    char = Character(
        data["name"],
        data["initiative"],
        data["armor"],
        data["arcane_resist"],
        data["light_resist"],
        data["nature_resist"],
        data["max_health"],
        data["tag"],
    )
    # Handle optional fields with defaults
    char.health = data.get("health", char.max_health)
    char.temp_hp = data.get("temp_hp", 0)
    if char.tag == "enemy" and "aggro" in data and data["aggro"] is not None:
        char.aggro = data["aggro"]
    return char


def main(stdscr):
    # Setup
    curses.curs_set(1)  # Show cursor
    stdscr.clear()
    ui = BattleUI(stdscr)

    try:
        with open("game_save.txt", "r") as file:
            raise FileNotFoundError
            characters_data = json.load(file)
            characters = [from_dict(data) for data in characters_data]
            ui.add_log("Game loaded from save file")
    except (FileNotFoundError, json.JSONDecodeError):
        # Add default characters if no save file exists
        characters = [
            Character("Warrior", 10, 30, 10, 10, 10, 100, "player"),
            Character("Healer", 8, 10, 20, 30, 20, 80, "player"),
            Character("Goblin", 12, 20, 15, 15, 15, 60, "enemy"),
        ]
        ui.add_log("Started new game with default characters")

    round_counter = 1
    while battle_round_ncurses(ui, characters, round_counter):
        round_counter += 1
        ui.add_log(f"Starting round {round_counter}")


def run_battle_game():
    curses.wrapper(main)


if __name__ == "__main__":
    run_battle_game()
