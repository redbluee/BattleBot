# BattleBot

BattleBot is a helper program designed for gamemasters running pen and paper role-playing games. This tool assists in managing game sessions, tracking encounters, and streamlining the gameplay experience for both the gamemaster and players.

## Getting Started

This guide will help you get BattleBot up and running on your system, whether you're just playing or want to help develop the game.

### Prerequisites

Before you begin, make sure you have:
- Python 3.x installed on your computer (from [Python.org](https://www.python.org/downloads/))
- Git for Windows installed (from [Git for Windows](https://gitforwindows.org/))
- A text editor (we recommend VS Code, but any will work)

### Installation Steps

1. **Install Build Tools** (one-time setup):
   - Open PowerShell as Administrator and install Chocolatey:
     ```powershell
     Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
     ```
   - Open Command Prompt as Administrator and install Make:
     ```cmd
     choco install make -y
     ```
   - Close and reopen Command Prompt
   - Verify Make installation:
     ```cmd
     make --version
     ```

2. **Get the Code**:
   ```cmd
   git clone https://github.com/redbluee/BattleBot.git
   cd BattleBot
   ```

3. **Setup Project**:
   ```cmd
   make install-dev
   ```
   This command will:
   - Install all required packages
   - Set up development tools
   - Configure pre-commit hooks

4. **Run the Game**:
   ```cmd
   python Battle.py
   ```

### Manual Setup (if Make fails)

If you encounter issues with `make install-dev`, follow these steps:

1. **Add Python Scripts to PATH**:
   ```cmd
   setx PATH "%PATH%;%USERPROFILE%\AppData\Roaming\Python\Python3xx\Scripts"
   ```
   Replace `Python3xx` with your Python version (e.g., Python312)

2. **Close and reopen Command Prompt**

3. **Install dependencies manually**:
   ```cmd
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   python -m pre_commit install
   ```

For more detailed setup instructions and troubleshooting, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Project Overview

BattleBot is organized into several key components:

### Core Components
- `combat/` - Handles all battle mechanics and calculations
- `models/` - Defines game objects like characters and items
- `ui/` - Creates the game interface you see and interact with
- `utils/` - Contains helpful tools and functions
- `tests/` - Ensures everything works correctly

### Key Features
- Battle management system
- Character tracking
- Dice rolling and calculations
- Game state saving and loading
- Customizable rules and settings

## Development Quick Start

If you're interested in helping develop BattleBot, here's how to get started:

1. Set up your development environment:
   ```cmd
   make install-dev
   ```

2. Run the code quality tools:
   ```cmd
   make format  # Makes code look consistent
   make lint    # Checks for common mistakes
   make test    # Makes sure everything works
   ```

These tools help keep the code clean and working well. They'll run automatically when you try to commit changes.

## Want to Contribute?

We welcome contributions from developers of all experience levels! Whether you're new to coding or an experienced developer, there's a place for you here.

Check out our [CONTRIBUTING.md](CONTRIBUTING.md) guide, which includes:
- Detailed Git tutorials and tips
- Step-by-step contribution workflow
- Coding standards and tools explained
- Testing guidelines and examples
- Project structure details

Even if you're new to development, our CONTRIBUTING.md will help you get started!
