# Goku Sprite Sheet Prototype

This folder keeps the original local prototype sheet separate from generated
review frames. Gameplay integration waits for user-approved frame mapping.

Place the original sheet at:

`assets/sprites/goku/source/goku_sheet.png`

Then run:

`python -B tools/cut_goku_sheet_preview.py`

For a numbered full-sheet map, run:

`python -B tools/annotate_goku_sheet_reference.py`

Output folders:

- `frames/`: transparent cropped action frames
- `preview/`: contact sheets for visual review
- `reference/`: numbered full-sheet and page references for user mapping
- `approved_player_frames/`: generated runtime frames selected by the user
- `approved_player_preview/`: contact sheets and GIFs for approved groups
- `manifest.json`: extracted frame metadata

Approved R04 jump, R06 punch, R07 kick, connected R09 hurt/death reactions,
R10 Ki Blast, R11 Kamehameha, R12 Energy Disc, R13 projectile impact, and R22
Super Saiyan transformation frames are wired into gameplay.

Super Saiyan melee uses separate runtime action ids (`super_saiyan_punch_1..5`
and `super_saiyan_kick_1..3`) so transformed attacks no longer fall back to
base-form punch/kick frames. The renderer reads `manifest.json` first, which
keeps old generated leftovers from being loaded by accident.

Super Saiyan Kamehameha uses its own body windup (`super_saiyan_skill_2`) and
beam PNG (`approved_effects/super_saiyan_kamehameha.png`). Other lower-sheet
skill effects remain review-only.
