import json

class Character:
    def __init__(self, name, initiative, armor, arcane_resist, light_resist, nature_resist, max_health, tag):
        self.name = name
        self.initiative = initiative
        self.armor = armor
        self.arcane_resist = arcane_resist
        self.light_resist = light_resist
        self.nature_resist = nature_resist
        self.health = max_health
        self.max_health = max_health
        self.temp_hp = 0  # Neues Attribut für temporäre HP
        self.tag = tag
        if self.tag == 'enemy':
            self.aggro = {}  # Aggro-Werte für jeden Spieler


    def add_aggro(self, player_name, amount, characters):
        # Assuming 'player_name' refers to a Character object
        player = next((p for p in characters if p.name == player_name), None)
        if player and player.tag == 'player':
            if player_name in self.aggro:
                self.aggro[player_name] += amount
            else:
                self.aggro[player_name] = amount

    def get_highest_aggro(self):

        if self.aggro.values():
            highest_aggro = max(self.aggro.values())
        else:
            return "Aggro: none"
        if not self.aggro or highest_aggro <= 0:
            return "Aggro: none"
        highest_players = [player for player, aggro in self.aggro.items() if aggro == highest_aggro]
        return highest_players

    def calculate_damage(self, damage_dict, attacker_name=None, characters=None):
        total_damage = 0
        for damage_type, damage in damage_dict.items():
            if damage_type == 'p':
                effective_damage = damage * (1 - self.armor / 100)
            elif damage_type == 'a':
                effective_damage = damage * (1 - self.arcane_resist / 100)
            elif damage_type == 'l':
                effective_damage = damage * (1 - self.light_resist / 100)
            elif damage_type == 'n':
                effective_damage = damage * (1 - self.nature_resist / 100)
            elif damage_type == 'g':
                effective_damage = 0
                if attacker_name and self.tag == "enemy":
                    attacker = next((c for c in characters if c.name == attacker_name), None)
                    if attacker and attacker.tag == 'player':
                        self.add_aggro(attacker_name, damage,characters)
            else:
                effective_damage = damage

            effective_damage = int(effective_damage)
            total_damage += effective_damage

        if self.temp_hp > 0:
            if total_damage <= self.temp_hp:
                self.temp_hp -= total_damage
                total_damage = 0
            else:
                total_damage -= self.temp_hp
                self.temp_hp = 0

        self.health -= total_damage
        self.health = max(self.health, 0)  # Ensure health does not go below 0
        if self.tag == 'enemy' and attacker_name:
            attacker = next((c for c in characters if c.name == attacker_name), None)
            if attacker and attacker.tag == 'player':
                self.add_aggro(attacker_name, total_damage,characters)
        return total_damage


    def heal(self, healing_dict, healer_name=None, characters=None):
        total_healing = 0
        total_temp_hp = 0

        for healing_type, amount in healing_dict.items():
            if healing_type == 'h':
                effective_healing = int(amount)
                if self.health+effective_healing > self.max_health:
                    effective_healing=effective_healing-(self.health+effective_healing)%self.max_health
                self.health = self.health + effective_healing
                total_healing += effective_healing
            elif healing_type == 't':
                effective_temp_hp = int(amount)
                self.temp_hp += effective_temp_hp
                total_temp_hp += effective_temp_hp

        if healer_name and characters:
            healer = next((c for c in characters if c.name == healer_name), None)
            if healer and healer.tag == 'player':
                for enemy in characters:
                    if enemy.tag == 'enemy':
                        enemy.add_aggro(healer_name, total_healing / 4,characters)

        return total_healing, total_temp_hp



def save_game(characters, filename="game_save.txt"):
    with open(filename, "w") as file:
        json.dump([char.__dict__ for char in characters], file)
    print(f"Spielstand wurde in {filename} gespeichert.")

def load_game(filename="game_save.txt"):
    try:
        with open(filename, "r") as file:
            characters_data = json.load(file)
            characters = [Character(**data) for data in characters_data]
            print(f"Spielstand aus {filename} geladen.")
            return characters
    except FileNotFoundError:
        print(f"{filename} nicht gefunden.")
        return []

def show_stats(characters,current_index):
    print("aktueller Spieler ist", characters[current_index].name)
    for char in characters:
        print(f"{char.name} - HP: {char.health}/{char.max_health}, Temp HP: {char.temp_hp}, Ini: {char.initiative}, Armor: {char.armor}, Arcane Resist: {char.arcane_resist}, Light Resist: {char.light_resist}, Nature Resist: {char.nature_resist}, Tag: {char.tag}")
        if char.tag == 'enemy':
            print(f"Aggro: {char.aggro}")

def change_stat(characters):
    char_name = input("Name des Charakters: ")
    char = next((c for c in characters if c.name == char_name), None)
    if not char:
        print("Charakter nicht gefunden.")
        return

    stat = input("Zu ändernder Wert (health/temp_hp/initiative/armor/arcane_resist/light_resist/nature_resist/aggro): ")
    if stat == "aggro":
        target_name = input("Name des Spielers für Aggro-Anpassung: ")
        new_value = input_with_retry("Neuer Wert: ", float)
        char.aggro[target_name] = new_value
    else:
        new_value = input_with_retry("Neuer Wert: ", float)
        setattr(char, stat, new_value)
    print(f"{stat} von {char.name} wurde auf {new_value} geändert.")

    stat = input("Zu ändernder Wert (health/temp_hp/initiative/armor/arcane_resist/light_resist/nature_resist/aggro): ")
    if stat == "aggro":
        target_name = input("Name des Spielers für Aggro-Anpassung: ")
        new_value = input_with_retry("Neuer Wert: ", float)
        char.aggro[target_name] = new_value
    else:
        new_value = input_with_retry("Neuer Wert: ", float)
        setattr(char, stat, new_value)
    print(f"{stat} von {char.name} wurde auf {new_value} geändert.")


def change_active_char(characters):
    new_active_name = input("Gib den Namen des neuen aktiven Charakters ein: ")
    new_active = next((c for c in characters if c.name == new_active_name), None)
    if new_active:
        return new_active
    else:
        print("Charakter nicht gefunden.")
        return None

def create_character(characters):
    name = input("Name des neuen Charakters: ")
    initiative = input_with_retry("Initiative: ", float)
    armor = input_with_retry("Rüstung: ", float)
    arcane_resist = input_with_retry("Arkane Resistenz: ", float)
    light_resist = input_with_retry("Licht Resistenz: ", float)
    nature_resist = input_with_retry("Natur Resistenz: ", float)
    max_health = input_with_retry("Maximale Gesundheit: ", float)
    tag = input_with_retry("Tag (player/enemy): ", str, ["player", "enemy"])
    new_character = Character(name, initiative, armor, arcane_resist, light_resist, nature_resist, max_health, tag)
    characters.append(new_character)
    characters.sort(key=lambda x: x.initiative, reverse=True)
    print(f"Neuer Charakter {name} wurde erstellt.")

def delete_character(characters):
    char_name = input("Name des zu löschenden Charakters: ")
    char = next((c for c in characters if c.name == char_name), None)
    if char:
        characters.remove(char)
        print(f"Charakter {char.name} wurde gelöscht.")
    else:
        print("Charakter nicht gefunden.")

def parse_healing_input(healing_input):
    healing_dict = {}
    healing_types = ['h', 't']
    healing_parts = healing_input.split()
    for part in healing_parts:
        if part[-1] in healing_types:
            healing_dict[part[-1]] = float(part[:-1])
    return healing_dict

def parse_damage_input(damage_input):
    damage_dict = {}
    temp_hp = 0
    damage_types = ['p', 'a', 'l', 'n', 'g', 't']
    damage_parts = damage_input.split()
    for part in damage_parts:
        if part[-1] in damage_types:
            if part[-1] == 't':
                temp_hp = float(part[:-1])
            else:
                damage_dict[part[-1]] = float(part[:-1])
    return damage_dict, temp_hp


def confirm_action(message):
    confirmation = input_with_retry(f"{message} Bestätigen? (j/n): ", str, ["j", "n"]).lower()
    return confirmation == 'j'

def input_with_retry(prompt, input_type=str, allowed_values=None):
    while True:
        try:
            user_input = input_type(input(prompt))
            if allowed_values and user_input not in allowed_values:
                raise ValueError(f"Eingabe muss eine der folgenden sein: {allowed_values}")
            return user_input
        except ValueError as e:
            print(f"Ungültige Eingabe: {e}")

def battle_round(characters, round_counter):
    print(f"Runde: {round_counter}")
    characters.sort(key=lambda x: x.initiative, reverse=True)
    current_index = 0
    while current_index < len(characters):
        char = characters[current_index]
        print(f"{char.name} (Initiative: {char.initiative}) ist an der Reihe. Er hat {char.health} Leben und {char.temp_hp} temporäre HP")

        if char.tag == 'enemy':
            highest_aggro_players = char.get_highest_aggro()
            if highest_aggro_players == "Aggro: none":
                print("Aggro: none")
            else:
                print(f"Hohe Aggro auf {char.name}: {', '.join(highest_aggro_players)}")

        while True:
            action_type = input_with_retry("Aktion (a/h/e/adm): ", str, ["a", "h", "e", "adm"]).lower()

            if action_type == 'a':  # Attack
                target_name = input("Ziel (Name oder 'all'): ")
                dummy_check = input("Wurde geblockt und gedodged?")
                damage_input = input("Schaden eingeben (Zahl + p:physical/a:arcane/l:light/n:nature/g:Aggro): ")

                while not damage_input or not damage_input[0].isdigit():
                    damage_input = input("Schaden eingeben (Zahl + p:physical/a:arcane/l:light/n:nature/g:Aggro): ")
                damage_dict, temp_hp = parse_damage_input(damage_input)

                if target_name == 'all':
                    targets = [c for c in characters if c.tag != char.tag]
                else:
                    target = next((c for c in characters if c.name == target_name), None)
                    targets = [target] if target else []

                for target in targets:
                    if target and char.tag == target.tag:
                        if not confirm_action(f"{char.name} fügt {target.name} Schaden zu"):
                            continue

                    if target:
                        actual_damage = target.calculate_damage(damage_dict, char.name, characters)
                        print(f"{char.name} verursacht {actual_damage} Schaden an {target.name}.")
                        print(f"{target.name} hat jetzt noch {target.health} Gesundheit und {target.temp_hp} temporäre HP.")
                    else:
                        print("Ziel nicht gefunden. Aktion übersprungen.")

            elif action_type == 'h':  # Heal
                target_name = input("Ziel (Name oder 'all'): ")
                healing_input = input("Heilungsmenge eingeben (Zahl + h:healing/t:temp_hp): ")
                healing_dict = parse_healing_input(healing_input)
                

                if target_name == 'all':
                    targets = [c for c in characters if c.tag == char.tag]
                else:
                    target = next((c for c in characters if c.name == target_name), None)
                    targets = [target] if target else []

                for target in targets:
                    if target and char.tag != target.tag:
                        if not confirm_action(f"{char.name} heilt {target.name}"):
                            continue

                    if target:
                        actual_healing, actual_temp_hp = target.heal(healing_dict, char.name, characters)
                        print(f"{char.name} heilt {target.name} um {actual_healing} HP und gibt {actual_temp_hp} temporäre HP.")
                        print(f"{target.name} hat jetzt {target.health} Gesundheit und {target.temp_hp} temporäre HP.")
                    else:
                        print("Ziel nicht gefunden. Aktion übersprungen.")

            elif action_type == 'e':  # End turn
                print()
                break

            elif action_type == 'adm':  # Admin commands
                admin_command = input_with_retry("Admin-Befehl (show/change_stat/change_active_char/save/load/create/delete): ", str, ["show", "change_stat", "change_active_char", "save", "load", "create", "delete"]).lower()
                if admin_command == 'show':
                    show_stats(characters,current_index)
                elif admin_command == 'change_stat':
                    change_stat(characters)
                elif admin_command == 'change_active_char':
                    new_active_char = change_active_char(characters)
                    if new_active_char:
                        current_index = characters.index(new_active_char) - 1
                        break
                elif admin_command == 'save':
                    save_game(characters)
                elif admin_command == 'load':
                    characters = load_game()
                elif admin_command == 'create':
                    create_character(characters)
                elif admin_command == 'delete':
                    delete_character(characters)
                    current_index -=1
        current_index += 1


def main():
    characters = [
        Character("leh", 24, 10, 0, 0, 10, 80, 'player'),
        Character("val", 23, 0, 10, 30, 10, 80, 'player'),
        Character("zip", 23, 0, 20, 20, 10, 70, 'player'),
        #Character("peo", 19, 30, 0, 0, 10, 140, 'player'),
        Character("mus", 18, 10, 0, 0, 20, 130, 'player'),
        #Character("q1", 18, 10, 0, 0, 0, 60, 'enemy'),
        #Character("os", 21, 20, 10, 10, 10, 100, 'enemy'),
        Character("sr", 20, 10, 0, 0, 30, 120, 'enemy'),
        Character("ss", 20, 10, 0, 0, 30, 120, 'enemy'),
        Character("boss", 23, 20, 0, 0, 30, 400, 'enemy')
        

        #Character("shami", 20, 10, 0, 0, 20, 100, 'enemy'),
        #Character("over", 18, 40, 10, 10, 10, 120,  'enemy')

    ]  # initiative, armor, arcane_resist, light_resist, nature_resist, max_health, tag
    round_counter = 1
    while True:
        battle_round(characters, round_counter)
        round_counter += 1

if __name__ == "__main__":
    main()
