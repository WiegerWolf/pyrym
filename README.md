# Pygame Turn-Based Game

This project is a simple turn-based game built using Pygame. Players can take turns to attack enemies, and the game manages the state of the battle.

## Project Structure

```
pygame-turn-based-game
├── src
│   ├── main.py        # Entry point of the game
│   ├── game.py        # Game logic and state management
│   ├── player.py      # Player character representation
│   ├── enemy.py       # Enemy character representation
│   └── utils.py       # Utility functions
├── requirements.txt    # Project dependencies
└── README.md           # Project documentation
```

## Installation

To run this game, you need to have Python and Pygame installed. You can install the required dependencies using the following command:

```
pip install -r requirements.txt
```

## Running the Game

After installing the dependencies, you can run the game by executing the `main.py` file:

```
python src/main.py
```

## Gameplay

- Players take turns attacking enemies.
- The game keeps track of health and attack power for both players and enemies.
- The game ends when either the player or all enemies are defeated.

## Contributing

Feel free to fork the repository and submit pull requests for any improvements or features you would like to add!