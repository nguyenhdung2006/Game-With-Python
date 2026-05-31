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

Mode select:

- `1` = Solo / Versus
- `2` = Dungeon / Wave Mode
- `3` = Team Round 3v3 locked screen
- `Esc` = quit on mode select, return to mode select from modes

Dungeon / Wave Mode:

- `A` = move left
- `D` = move right
- `W` = jump
- `Left Shift` = dash
- `J` = light attack / 3-hit combo
- `K` = parry on press, block when held
- `L` = dodge / evade
- `U` = Ki Blast
- `I` = Kamehameha
- `O` = locked skill slot
- Reward select: `A/D` or `Left/Right` changes reward, `Enter` confirms
- Room cleared: `Enter` opens reward selection
- Defeat / Dungeon Cleared: `R` retries the run, `Esc` returns to mode select

Solo / Versus Mode:

- Same movement, defense, combo, and skill controls as Dungeon / Wave Mode
- `U` = Combo Burst prototype (costs Solo energy)
- `I` = Kamehameha
- `O` = locked skill slot
- No rewards or room progression
- Victory / Defeat: `R` starts a rematch, `Esc` returns to mode select

## Project Structure

```text
project_root/
main.py
settings.py
config/
    player_config.py
    enemy_config.py
    boss_config.py
    skill_config.py
    reward_config.py
    mode_config.py
entities/
    player.py
    player_parts/
        setup.py
        combat.py
        defense.py
        movement.py
        reaction.py
        render_state.py
        render.py
    base_enemy.py
    enemy_parts/
        setup.py
        behavior.py
        render_state.py
        render.py
    elite_enemy.py
    basic_enemy.py
    fast_enemy.py
    enemy.py
managers/
    encounter_director.py
    encounter_manager.py
    encounter_profiles.py
    game_state.py
    room_manager.py
    room_state.py
modes/
    dungeon_mode.py
    solo_mode.py
systems/
    beam.py
    boss_skill_controller.py
    combat.py
    enemy_spacing.py
    player_feedback.py
    pressure_indicator.py
    projectile.py
    projectile_manager.py
    reward.py
    reward_manager.py
    render_layers.py
    reaction_feedback.py
    skill.py
    skill_manager.py
    solo_combo_burst.py
    solo_sprite_renderer.py
    sprite_loader.py
    physics.py
    effects/
        camera.py
        trail.py
        slash.py
        defense.py
        ui.py
ui/
    dungeon_hud.py
    health_bar.py
    mode_select.py
    reward_select.py
    room_banner.py
    wave_banner.py
world/
    battlefield.py
assets/
    SPRITE_PIPELINE.md
    sprites/
        player/
        enemies/
        effects/
        ui/
        backgrounds/
    sounds/
    music/
```

## Folder Responsibilities

- `main.py` starts Pygame, creates objects, runs the game loop, and calls update/draw methods.
- `settings.py` stores runtime geometry/colors and re-exports legacy tuning constants for compatibility.
- `config/` stores lightweight Python tuning modules for player, enemy, boss, skill, reward, Solo, and Dungeon values.
- `entities/` stores game objects such as the player, enemies, future bosses, and projectiles.
- `entities/player_parts/` keeps Player combat, defense, movement, setup, and rendering concerns in smaller modules.
- `entities/player_parts/reaction.py` tracks player-side whiff, landing, guard stress, and payoff feedback timers.
- `entities/player_parts/render_state.py` maps gameplay state into animation-ready player visual states.
- `entities/base_enemy.py` holds shared melee enemy behavior so new archetypes can reuse one AI/state foundation.
- `entities/enemy_parts/` keeps BaseEnemy setup, behavior, and drawing responsibilities separated.
- `entities/enemy_parts/render_state.py` maps enemy AI state into animation-ready visual states.
- `entities/elite_enemy.py` defines the heavy, readable single-enemy archetype used for the Room 3 boss foundation.
- `entities/basic_enemy.py` defines the balanced baseline enemy archetype.
- `entities/fast_enemy.py` defines the quicker, lower-health pressure archetype.
- `managers/` stores flow systems such as enemy wave spawning and encounter progression.
- `managers/game_state.py` stores top-level mode routing state.
- `managers/room_manager.py` stores the fixed dungeon room sequence and progression state.
- `managers/room_state.py` stores lightweight room type and flow-state constants.
- `managers/encounter_director.py` coordinates wave intros, activation timing, and clean attacker handoffs.
- `managers/encounter_profiles.py` stores lightweight per-wave pacing profiles so encounters can escalate without giant scripts.
- `modes/dungeon_mode.py` wraps the current playable wave-combat loop so the game can route between modes.
- `modes/solo_mode.py` owns the playable 1v1 arena sandbox without dungeon rewards or room progression.
- `systems/beam.py` defines the short-lived rectangular Kamehameha prototype hitbox.
- `systems/boss_skill_controller.py` manages neutral boss skill cooldown, telegraph, active, and recovery states.
- `systems/combat.py` stores hitbox, damage, and defense resolution helpers.
- `systems/enemy_spacing.py` keeps multi-enemy spacing and flanking behavior lightweight and reusable.
- `systems/pressure_indicator.py` draws subtle enemy intent and active-aggressor readability cues.
- `systems/player_feedback.py` draws subtle player recovery, unsafe, guard-stress, and payoff readability cues.
- `systems/projectile.py` defines the projectile primitive used by Ki Blast.
- `systems/projectile_manager.py` owns projectile and beam updates, drawing, lifetime cleanup, and enemy collision.
- `systems/reward.py` defines purely mechanical room rewards and their stat effects.
- `systems/reward_manager.py` owns reward option selection, navigation, application, and chosen reward tracking.
- `systems/render_layers.py` keeps combat-space render ordering explicit.
- `systems/reaction_feedback.py` draws small enemy vulnerability, recovery, and stagger readability effects.
- `systems/skill.py` defines neutral skill slot primitives with cooldown and resource-cost fields.
- `systems/skill_manager.py` owns the three player skill slots and routes Ki Blast, Kamehameha, and the locked slot.
- `systems/solo_combo_burst.py` sequences the Solo-only three-hit Combo Burst using existing normal attack setup.
- `systems/solo_sprite_renderer.py` loads and draws Solo-only shaman, slash, boss, and boss-technique prototype frames with safe fallbacks.
- `systems/sprite_loader.py` provides safe cached sprite loading with placeholder fallback.
- `systems/effects/` stores camera impact, trails, slash visuals, and defense-related visual effects.
- `systems/physics.py` stores shared movement and collision helpers.
- `ui/` stores reusable interface drawing code such as health bars.
- `ui/completion_overlay.py` draws shared retry and return-to-menu prompts for terminal states.
- `ui/dungeon_hud.py` draws Dungeon Mode run status, selected rewards, stat modifiers, and clear summary.
- `ui/mode_select.py` draws the mode select and locked coming-soon screens.
- `ui/reward_select.py` draws the three-choice mechanical reward selection screen.
- `ui/room_banner.py` draws dungeon room number, room clear, and dungeon clear prompts.
- `ui/wave_banner.py` draws short centered wave-intro presentation text.
- `world/` stores arena and environment drawing code.
- `assets/SPRITE_PIPELINE.md` documents sprite folder conventions and prepared visual states.
- `assets/` is reserved for future sprites, sounds, and music.

## Current Features

- Mode select screen on launch with Solo / Versus, Dungeon / Wave, and Team Round 3v3 entries
- Solo / Versus playable 1v1 arena foundation with one player and one duel enemy
- Dungeon / Wave Mode routes into the current playable combat encounter
- Dungeon room flow foundation with Room 1 encounter, Room 2 encounter, Room 3 elite/boss encounter, and Dungeon Cleared state
- Room clear flow that waits for `Enter` before advancing
- Room reward foundation with three mechanical reward choices after encounter rooms
- Dungeon HUD and run status polish showing room status, reward count, selected rewards, and mechanical stat modifiers
- Dungeon clear summary with rooms cleared, selected rewards, and final modifiers
- Completion flow foundation with Dungeon Defeat, retry, Solo rematch, and shared end-state prompts
- Room Cleared pacing cleanup that waits for `Enter` before opening reward selection
- Gameplay config foundation that moves prototype tuning into focused Python modules without adding content
- Elite/Boss foundation for Room 3 using a single heavy melee enemy with slower pacing, longer telegraphs, and clearer punish windows
- Boss readability and pacing polish with slower attack cadence, stronger downtime, and clearer recovery punish windows
- Goku skill prototype with `U` Ki Blast, `I` Kamehameha, and `O` locked
- Ki Blast as a fast projectile with cooldown, damage multiplier support, lifetime cleanup, and one-hit collision
- Kamehameha as a short-lived rectangular beam prototype that damages each enemy once per use
- Solo / Versus supports movement, jump, dash, combo attacks, Solo Combo Burst, Kamehameha, enemy chase/telegraph/attack, and Victory/Defeat overlays
- Boss skill AI foundation with cooldown spacing, readable telegraph, one-hit placeholder rectangle, and recovery punish window
- Solo sprite combat prototype with shaman player frames, close-range slash visuals, boss sprite playback, boss technique frames, energy bar, and `U` Combo Burst
- Team Round 3v3 locked / coming-soon screen
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
- Encounter readability polish with staged entrances, wave-specific pacing profiles, and subtle pressure telegraphs
- Enemy reaction and punish-window polish so vulnerability reads more clearly after hits and committed attacks
- Player-side readability polish for whiffs, landing recovery, guard stress, unsafe windows, and payoff moments
- Combat stabilization pass with cleaner damage interrupts and scalable spawn/spacing helpers
- Visual pipeline foundation with sprite-ready rendering hooks, visual-state mapping, and structured sprite folders
- Short dodge / evade with cooldown and temporary invulnerability
- Combat recovery and cancel timing for smoother action flow
- Player and enemy health bars

## Current Modes

- Solo / Versus: playable 1v1 arena sandbox
- Dungeon / Wave Mode: playable fixed room flow
- Team Round 3v3: locked / coming soon

## Solo / Versus Flow

- Press `1` from mode select to start a 1v1 arena fight
- The arena spawns the player and one duel enemy
- The player can use existing movement, combo, guard/dodge, and Kamehameha controls
- In Solo, `U` is overridden by the energy-driven three-hit Combo Burst prototype; Dungeon keeps `U` Ki Blast
- The Solo boss uses the existing chase, telegraph, attack, hurt, defeat, and Phase 31 boss-skill behavior
- Player and enemy health bars are shown
- Player energy and skill HUD are shown
- Solo attack hitboxes are shorter than their sprite visuals to keep close-range combat fair
- Enemy defeat shows `Victory`
- Player defeat shows `Defeat`
- Victory and Defeat both support `R` rematch without restarting the application
- No rewards or room progression are added; sprite playback and Combo Burst remain Solo-only prototypes rather than a full animation or skill system

## Dungeon Flow

- Room 1: encounter
- Room 2: encounter
- Room 3: elite/boss encounter
- Final state: Dungeon Cleared
- Encounter rooms pause on Room Cleared and wait for `Enter` before opening a three-choice reward screen
- `Enter` confirms selected rewards before advancing to the next room
- Player defeat shows a Dungeon Defeat overlay with `R` retry and `Esc` return-to-menu actions
- Dungeon retry resets room progression, rewards, player state, cooldowns, projectiles, beams, and enemies
- Dungeon HUD shows current room, room type, reward count, damage multiplier, dash cooldown multiplier, and max HP bonus
- Dungeon HUD shows Ki Blast, Kamehameha, and Locked slot readiness/cooldowns
- Dungeon Clear shows selected rewards and final mechanical modifiers
- Rewards are mechanical only and appear after Room 1 and Room 2 encounter clears
- The Room 3 elite/boss encounter has no post-fight reward and clears the dungeon when defeated
- Phase 28 adds skill slot and projectile infrastructure only
- Phase 29 adds user-approved Ki Blast and Kamehameha prototypes with placeholder projectile/beam visuals only; no animation, sprite work, complex VFX, transformations, new skills, reward rarity, inventory, save/load, or boss identity/theme has been added
- Phase 31 adds boss skill AI architecture with a neutral mechanical placeholder only; no final boss identity, named boss attack, animation, VFX, or assets have been added
- Phase 32 adds a Solo-only sprite combat and energy prototype: shaman body frames, slash combo visuals, boss sprite playback, technique frames attached to the preserved Phase 31 skill flow, and `U` Combo Burst. Dungeon visuals and bindings remain unchanged
- Phase 33 adds completion-flow foundation only: Dungeon Defeat and retry, Solo rematch, readable Room Cleared pacing before reward selection, and consistent retry/menu prompts. No combat, AI, animation, asset, or fantasy expansion has been added
- Phase 34 adds a lightweight gameplay config foundation: player, enemy, boss, skill, reward, Solo, and Dungeon prototype tuning now live in focused Python modules. Existing behavior is preserved; no new gameplay content has been added
- Phase 26 adds boss pacing foundation only: heavier melee tuning, longer telegraph/recovery, and punish-focused combat readability
- Phase 27 polishes boss rhythm only: clearer telegraphs, longer recovery, slower pressure cadence, and more reliable punish timing without special attacks or VFX

This structure keeps each file focused. As the game grows, combat, enemies,
bosses, effects, and UI can expand without turning `main.py` into one giant file.
