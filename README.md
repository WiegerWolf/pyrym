# Turn-Based Pygame Adventure

A lightweight turn-based RPG prototype built with [Pygame](https://www.pygame.org/).  
Explore, find loot, and battle endless waves of enemies in a classic “explore → encounter → battle” gameplay loop.

![Gameplay GIF](docs/preview.gif)

## Gameplay Overview

1. **Explore** – Press **Space** to take a step. Each step may:
   * Trigger a random enemy encounter (chance starts at 10 % and rises with every safe step)
   * Find a random item (healing potion or gold pile)
2. **Battle** – Turn-based combat where you can:
   * **Space** – Attack the enemy  
   * **D** – Defend to halve the next enemy hit  
   * **P** – Drink a healing potion (if available)  
   * **F** – Attempt to flee (25 % base chance)
3. Defeat the enemy to increase your **score** and advance the **wave**.  
4. If your HP drops to zero the game ends. Close the window or press the OS window close button to quit at any time.

## Controls

| Key | Context  | Action                |
|-----|----------|-----------------------|
| `Space` | Explore & Battle | Advance / Attack |
| `P` | Both | Use potion / Heal |
| `D` | Battle | Defend |
| `F` | Battle | Attempt to flee |
| *Window close* | Any | Quit game |

## Installation

### Prerequisites

* Python **3.10** or newer
* Pygame **2.x**

### Quick start

```bash
# (recommended) create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# install dependencies
pip install pygame
```

> Optionally, add other libs to `requirements.txt` and use `pip install -r requirements.txt`.

## Running the Game

```bash
python -m src.main
# or
python src/main.py
```

A window titled *Turn-Based Game* should appear – play with the keys above!

## Project Structure

```
src/
├── abilities/          # Modular ability classes (attacks, etc.)
├── core/
│   ├── game.py         # Main loop, state machine, Pygame setup
│   ├── game_state.py   # Enum & StateManager helper
│   ├── events.py       # Maps Pygame events to high-level signals
│   └── ui.py           # Rendering helpers (health bars, text, battle screen)
├── entities/
│   ├── base.py         # Base Entity class
│   ├── player.py       # Player implementation & inventory
│   └── enemy.py        # Enemy implementation with scaling
├── items/              # Collectable items (HealingPotion, GoldPile)
├── states/
│   ├── explore.py      # Exploration state logic & rendering
│   └── battle.py       # Battle state logic & rendering
├── config.py           # All tunable constants (screen size, colours, combat stats)
├── utils.py            # Utility helpers (e.g., battle log)
└── main.py             # Thin entry point that runs Game
```

## Contributing

Contributions are welcome! To propose a change:

1. Fork the repository & create a feature branch.  
2. Commit your changes with clear messages.  
3. Open a Pull Request describing *what* and *why*.

Please follow [PEP 8](https://peps.python.org/pep-0008/) style and include docstrings where relevant.

## License

This project is licensed under the **MIT License** – see [`LICENSE`](LICENSE) for details.

## Acknowledgements

Built with [Pygame](https://www.pygame.org/) and lots of coffee ☕.