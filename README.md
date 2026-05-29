# Anime Stickman Combat

A 2D Python/Pygame combat game prototype set in a ruined battlefield arena.

## How to Run

Install Pygame if needed:

```powershell
python -m pip install pygame
```

Run the game from the project root:

```powershell
python main.py
```

## Controls

- `A` = move left
- `D` = move right
- `W` = jump
- `Left Shift` = dash
- `J` = light attack / 3-hit combo

## Project Structure

```text
project_root/
main.py
settings.py
entities/
    player.py
    enemy.py
systems/
    combat.py
    physics.py
    effects.py
ui/
    health_bar.py
world/
    battlefield.py
assets/
    sprites/
    sounds/
    music/
```

## Folder Responsibilities

- `main.py` starts Pygame, creates objects, runs the game loop, and calls update/draw methods.
- `settings.py` stores shared constants such as screen size, colors, physics values, dash values, and combat values.
- `entities/` stores game objects such as the player, enemies, future bosses, and projectiles.
- `systems/` stores reusable logic for physics, combat helpers, and visual effects.
- `ui/` stores reusable interface drawing code such as health bars.
- `world/` stores arena and environment drawing code.
- `assets/` is reserved for future sprites, sounds, and music.

## Current Features

- Ruined battlefield arena drawn with Pygame shapes
- Player left/right movement
- Jumping with gravity and ground collision
- Short dash with cooldown and afterimage trail
- Enemy training dummy with health, hurt flash, knockback, and defeated state
- 3-hit light attack combo with different damage, hitboxes, and knockback
- Player and enemy health bars

This structure keeps each file focused. As the game grows, combat, enemies,
bosses, effects, and UI can expand without turning `main.py` into one giant file.
