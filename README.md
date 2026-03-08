# matplotlib-engine
### A narrative game engine built entirely in matplotlib

![Python](https://img.shields.io/badge/python-3.11+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![Status](https://img.shields.io/badge/status-prototype-orange)

---

## What is this?

**matplotlib-engine** is a story-driven game engine that runs inside a single matplotlib figure window. You write your story in a JSON file, drop in your assets, and the engine handles the rest — conversation scenes, text scenes, and minigames, all sequenced and rendered without any game engine dependencies.

It was built as a **lightweight prototyping tool** for narrative games. The UI is intentionally minimal. The bundled minigames (Flappy Bird, Minesweeper, Tetris, etc.) are functional placeholders — you can swap them out, extend them, or replace them entirely with your own.

---

## Bundled example: Tower of Beginnings

The repo ships with a complete example story called **Tower of Beginnings** — a dark fantasy narrative about guilt, memory, and choice. It exists to demonstrate what the engine can do and to give you something to run immediately. It is not the point of the project.

Use it as a reference for how scenes, dialogue, and minigames fit together, then replace it with your own story.

---

## Requirements

- Python 3.11+
- Windows (built and tested on Windows; other platforms untested)

---

## Installation

```bash
git clone https://github.com/your-username/matplotlib-engine.git
cd matplotlib-engine

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
```

---

## Running the example story

```bash
python game.py
```

In conversation and text scenes, press **Space** or **click** to advance. Controls for each minigame are shown on screen.

---

## Writing your own story

All story content lives in `data/story.json`. The engine reads it on startup and sequences through the scenes in order.

### Scene types

**Conversation** — characters talking, with sprites and a background:
```json
{
  "type": "conversation",
  "location": "my_location",
  "conversation": [
    { "character": "Alice", "text": "Hello." },
    { "character": "Bob",   "text": "Hello yourself." }
  ]
}
```

**Text** — a single screen of prose with a title:
```json
{
  "type": "text",
  "title": "Chapter One",
  "location": "my_location",
  "content": [
    "Line one of your text.",
    "Line two.",
    "",
    "A blank line above creates a paragraph break."
  ]
}
```

**Minigame** — drops into one of the bundled games:
```json
{
  "type": "minigame",
  "game": "snake_game",
  "victory_message": "You win!",
  "defeat_message": "Try again."
}
```

**Exit** — ends the game cleanly. Always put this last:
```json
{ "type": "exit" }
```

---

### Defining characters

Characters are defined once at the top level of `story.json` and referenced by name in conversation scenes:

```json
"characters": {
  "Alice": {
    "sprite": "assets/alice.png",
    "side": "left"
  },
  "Bob": {
    "sprite": "assets/bob.png",
    "side": "right"
  },
  "Narrator": {
    "side": "center"
  }
}
```

`side` can be `"left"`, `"right"`, or `"center"`. Characters without a `sprite` render as name-only.

---

### Defining locations

Locations are backgrounds, defined at the top level and referenced by key in scenes:

```json
"settings": {
  "my_location": {
    "background": "assets/my_background.png"
  }
}
```

Supported formats: `.jpg`, `.png`, `.webp`. Recommended size: 16:9. Character sprites should be portrait orientation (3:4).

---

## Bundled minigames

| Key | Game |
|---|---|
| `flappy_bird` | Flappy Bird |
| `minesweeper` | Minesweeper |
| `nine_puzzle` | 8-tile sliding puzzle |
| `password_puzzle` | Password / riddle input |
| `pong_game` | Pong |
| `snake_game` | Snake |
| `tetris_game` | Tetris |
| `two_guards` | Two guards riddle |

Each game can be configured via extra fields in the scene JSON. See `data/story.json` for examples of each.

---

## Adding a new minigame

1. Create `scenes/your_game.py` with a class that accepts `(fig, ax)` and has a `run()` method
2. Register it in `game.py`:

```python
MINIGAME_REGISTRY = {
    ...
    "your_game": YourGame,
}
```

3. Reference it in `story.json`:

```json
{ "type": "minigame", "game": "your_game" }
```

---

## Project structure

```
matplotlib-engine/
├── game.py               # Entry point, Game and SceneManager
├── game.spec             # PyInstaller build config
├── requirements.txt
├── data/
│   └── story.json        # Your story — edit this
├── assets/               # Your backgrounds and sprites — replace these
├── scenes/               # Engine scene renderers and bundled minigames
│   ├── conversation_cutscene.py
│   ├── text_scene.py
│   ├── flappy_bird.py
│   ├── minesweeper.py
│   ├── nine_puzzle.py
│   ├── password_puzzle.py
│   ├── pong_game.py
│   ├── snake_game.py
│   ├── tetris_game.py
│   └── two_guards.py
└── tests/                # pytest test suite
```

---

## Running tests

```bash
pip install pytest pytest-cov
pytest tests/ -v
```

---

## Building a distributable .exe

```bash
pip install pyinstaller
pyinstaller game.spec
```

Output: `dist/game.exe`. Pushing to `main` runs the full CI pipeline (lint → format → test → build) and publishes a release ZIP automatically.

---

## Credits

Engine and tooling by **bellatrixesque**
Example story (*Tower of Beginnings*) by **bellatrixesque**
Example assets by **Sora**

---

© 2026 Catastrophic Game Studio