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
- `K` = parry on press, block when held
- `L` = dodge / evade

## Project Structure

```text
project_root/
main.py
settings.py
entities/
    player.py
    player_parts/
        setup.py
        combat.py
        defense.py
        movement.py
        render.py
    base_enemy.py
    enemy_parts/
        setup.py
        behavior.py
        render.py
    basic_enemy.py
    fast_enemy.py
    enemy.py
managers/
    encounter_director.py
    encounter_manager.py
systems/
    combat.py
    enemy_spacing.py
    physics.py
    effects/
        camera.py
        trail.py
        slash.py
        defense.py
        ui.py
ui/
    health_bar.py
    wave_banner.py
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
- `entities/player_parts/` keeps Player combat, defense, movement, setup, and rendering concerns in smaller modules.
- `entities/base_enemy.py` holds shared melee enemy behavior so new archetypes can reuse one AI/state foundation.
- `entities/enemy_parts/` keeps BaseEnemy setup, behavior, and drawing responsibilities separated.
- `entities/basic_enemy.py` defines the balanced baseline enemy archetype.
- `entities/fast_enemy.py` defines the quicker, lower-health pressure archetype.
- `managers/` stores flow systems such as enemy wave spawning and encounter progression.
- `managers/encounter_director.py` coordinates wave intros, activation timing, and clean attacker handoffs.
- `systems/combat.py` stores hitbox, damage, and defense resolution helpers.
- `systems/enemy_spacing.py` keeps multi-enemy spacing and flanking behavior lightweight and reusable.
- `systems/effects/` stores camera impact, trails, slash visuals, and defense-related visual effects.
- `systems/physics.py` stores shared movement and collision helpers.
- `ui/` stores reusable interface drawing code such as health bars.
- `ui/wave_banner.py` draws short centered wave-intro presentation text.
- `world/` stores arena and environment drawing code.
- `assets/` is reserved for future sprites, sounds, and music.

## Current Features

- Ruined battlefield arena drawn with Pygame shapes
- Player left/right movement
- Jumping with gravity and ground collision
- Short dash with cooldown and afterimage trail
- Enemy training dummy with health, hurt flash, knockback, and defeated state
- 3-hit light attack combo with different damage, hitboxes, and knockback
- Combat impact polish with attack slowdown, hitstop, and camera shake
- Basic enemy AI with chase, telegraph, and melee attack states
- Player hurt feedback, invulnerability frames, and enemy retreat spacing
- Basic directional block / guard with reduced damage from front attacks
- Timing-based parry window on guard press that staggers the enemy on success
- Parry-earned counterattack window that turns `J` into a heavy punish attack
- Enemy archetype system with a balanced BasicEnemy and a faster, lower-health FastEnemy
- Encounter wave manager with 3 hardcoded waves and encounter-cleared detection
- Encounter pacing polish with wave banners, staged wave activation, better attack turns, and cleaner multi-enemy spacing
- Short dodge / evade with cooldown and temporary invulnerability
- Combat recovery and cancel timing for smoother action flow
- Player and enemy health bars

This structure keeps each file focused. As the game grows, combat, enemies,
bosses, effects, and UI can expand without turning `main.py` into one giant file.
