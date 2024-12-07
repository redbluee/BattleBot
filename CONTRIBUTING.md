# Contributing to BattleBot

## Quick Start

1. Follow [README.md](README.md) for installation
2. Run `make install-dev` to set up development tools

## Development Workflow

### Make Commands
```bash
make install-dev  # Setup development environment
make format      # Format code
make lint        # Check code style
make test       # Run tests
```

### Git Basics

<details>
<summary>Understanding Git (Click to expand)</summary>

Git helps us:
- Track all changes and their authors
- Work on features without breaking the main game
- Collaborate without conflicts
- Maintain different versions

Key concepts:
- **Repository (Repo)**: Project folder with `.git` tracking
- **Commit**: Snapshot of your changes
- **Branch**: Separate line of development
- **Pull Request (PR)**: Propose changes to main

Essential commands:
```bash
git status                    # Check what's changed
git pull origin main         # Get latest updates
git add file.py             # Stage specific file
git commit -m "Add health"  # Save changes
git push origin branch      # Share your changes
```

Advanced tips:
```bash
# Save changes temporarily
git stash
git checkout -b new-branch
git stash pop

# Fix last commit
git commit --amend  # Edit message
git commit --amend --no-edit  # Add more changes

# Find bugs
git bisect start
git bisect bad    # Current version broken
git bisect good v1.0.0  # Last working version
git bisect good/bad  # Mark versions until bug found
git bisect reset  # Finish search

# Update branch
git rebase main  # Get latest main changes
git rebase -i HEAD~3  # Clean up recent commits
```
</details>

### Branch Strategy

<details>
<summary>Branch Workflow (Click to expand)</summary>

Branch naming:
- `feature/add-weapons`  # New features
- `fix/crash-on-start`   # Bug fixes
- `release/v1.2.0`      # Version releases

Complete workflow:
```bash
# Start feature
git checkout main
git pull origin main
git checkout -b feature/guns

# Make changes
git add changed_files
git commit -m "Add gun mechanics"

# More changes
git add more_files
git commit -m "Add animations"

# Share work
git push origin feature/guns

# Prepare release
git checkout main
git pull origin main
git checkout -b release/v1.2.0
git merge feature/guns
# Run tests and fix issues

# Finish
git push origin release/v1.2.0
# Create PR on GitHub
# After merge:
git checkout main
git pull origin main
git branch -d feature/guns
```
</details>

### Code Quality

<details>
<summary>Code Standards & Tools (Click to expand)</summary>

#### 1. Black (Formatting)
```python
# Before
def messy_function   (x,y ) :
    return x+y

# After
def messy_function(x, y):
    return x + y
```

#### 2. isort (Imports)
```python
# Before
import random
from typing import List
import os
from models import Player

# After
import os
import random
from typing import List

from models import Player
```

#### 3. Flake8 (Style)
```python
# Will warn about:
unused_var = 42  # Unused variable
if x == True:    # Should be: if x:
```

#### 4. MyPy (Types)
```python
# Will catch:
def get_health() -> int:
    return "100"  # Error: str ≠ int
```
</details>

### Testing

<details>
<summary>Writing & Running Tests (Click to expand)</summary>

Types of tests:
```python
# Unit test (single component)
def test_calculate_damage():
    battle = BattleManager()
    assert battle.calculate_damage(10, 5) == 5
    assert battle.calculate_damage(5, 10) == 0

# Integration test (multiple components)
def test_complete_battle():
    game = GameManager()
    player = Player("Test")
    enemy = Enemy("Boss")
    game.start_battle(player, enemy)
    assert player.is_alive()
```

Running tests:
```bash
pytest              # All tests
pytest test_file.py # Specific file
pytest -v          # Verbose output
pytest -s          # Show print output
```

Test pattern:
```python
def test_player_damage():
    # Arrange
    player = Player(health=100)
    damage = 20

    # Act
    player.take_damage(damage)

    # Assert
    assert player.health == 80
```
</details>

## Project Structure

<details>
<summary>Directory Overview (Click to expand)</summary>

```
BattleBot/
├── combat/           # Battle mechanics
│   ├── battle.py     # Core battle logic
│   └── damage.py     # Damage calculations
├── models/           # Game objects
│   ├── player.py     # Player class
│   └── weapon.py     # Weapon system
├── ui/               # User interface
│   ├── screen.py     # Display handling
│   └── input.py      # Input processing
├── utils/            # Helper functions
│   ├── config.py     # Configuration
│   └── logger.py     # Logging system
└── tests/            # Test suite
    ├── test_battle.py
    └── test_player.py
```
</details>

## Contributing Guidelines

<details>
<summary>Issue & PR Templates (Click to expand)</summary>

### Bug Report
```markdown
**Description**
Clear description of the bug.

**Steps to Reproduce**
1. Start game with '...'
2. Click on '....'
3. See error

**Expected vs Actual**
- Expected: X should happen
- Actual: Y happened

**System Info**
- OS: Windows 10
- Python: 3.9.5
- Version: 1.2.0
```

### Feature Request
```markdown
**Problem**
What problem does this solve?

**Solution**
Describe your solution.

**Alternatives**
What else did you consider?
```

### Pull Request
```markdown
**Changes**
- List of changes
- New features added
- Tests added

**Testing**
- [ ] Added tests
- [ ] All tests pass
- [ ] Manually tested
```
</details>

## Troubleshooting

<details>
<summary>Common Issues (Click to expand)</summary>

1. PATH Issues:
```bash
# Add Python Scripts to PATH
setx PATH "%PATH%;%USERPROFILE%\AppData\Roaming\Python\Python3xx\Scripts"
```

2. Manual Setup:
```bash
pip install -r requirements.txt requirements-dev.txt
python -m pre_commit install
```

3. Tool Issues:
```bash
python -m black .
python -m flake8
python -m mypy .
python -m pytest
```
</details>

## Need Help?

- Check [existing issues](https://github.com/redbluee/BattleBot/issues)
- Create new issue for bugs/features
- Follow our [code style guidelines](#code-quality)
- Write tests for new features
- Join our [community discussions](https://github.com/redbluee/BattleBot/discussions)
