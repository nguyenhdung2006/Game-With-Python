# Sprite Pipeline

This folder is prepared for gradual sprite integration while placeholder
rectangle rendering remains the safe fallback.

## Structure

```text
assets/
    sprites/
        player/
        enemies/
            basic/
            fast/
        effects/
        ui/
        backgrounds/
```

## Naming

Use lowercase visual states with two-digit frame numbers:

```text
idle_01.png
run_03.png
attack_1_05.png
telegraph_01.png
stagger_02.png
```

Player visual states prepared in code:
`idle`, `run`, `jump`, `fall`, `dash`, `dodge`, `block`, `parry`,
`attack_1`, `attack_2`, `attack_3`, `counter`, `hurt`, `defeated`.

Enemy visual states prepared in code:
`idle`, `chase`, `telegraph`, `attack`, `hurt`, `stagger`, `recovery`,
`defeated`.

Phase 21 does not require finished art. Missing sprite files must be safe and
fall back to placeholder rendering.
