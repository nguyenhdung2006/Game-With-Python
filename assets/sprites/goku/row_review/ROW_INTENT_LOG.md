# Goku Row Intent Log

This file is the review memory for the Goku sheet. Each row must be reviewed,
previewed, and approved before it becomes gameplay mapping. If an intent is not
clear, keep it provisional until the user says `done all frame`.

## Workflow Rule

- Review one row at a time.
- Export slow contact sheets and GIF examples before changing gameplay config.
- Keep uncertain actions marked as `provisional`.
- After `done all frame`, compare all rows and choose the cleanest final mapping.
- Do not reuse a row for a different gameplay state unless the intent is clearer
  than the current mapping.

## Row 01 - Approved

Status: `approved`

Role: stance, intro, idle, pose variants.

Preview folder:

`assets/sprites/goku/row_review/R01`

Mapping:

| Frames | Intent | Gameplay State | Confidence | Notes |
|---|---|---|---|---|
| `R01-01 -> R01-04` | Intro / enter fight / settle into stance | `intro_entry` | High | Use before control starts. |
| `R01-05 -> R01-08` | Fight-ready transition | `fight_ready` | High | Use after intro callout or before wave start. |
| `R01-08` | Main combat idle hold | `idle_hold` | High | Stable readable stance. Return here after actions. |
| `R01-09` | Pose / light taunt / victory candidate | `pose_taunt` or `victory_candidate` | Medium | Single pose; avoid looping quickly. |
| `R01-10 -> R01-11` | Side stance / turn candidate | `side_stance` or `turn_candidate` | Medium | Useful for cinematic/preview turn, not walk. |
| `R01-12 -> R01-13` | Alt idle / calm stance / menu preview | `alt_idle` or `menu_idle` | Medium | Better for preview/menu than active combat. |

## Row 02 - Reviewed, Provisional Until Final Comparison

Status: `provisional`

Role: evasive movement, dash burst, dash exit, vanish/teleport candidate.

Core Theme:

High-speed evasive movement and instant displacement.

Movement Philosophy:

This row represents movement beyond readable foot travel. The character should
feel like they are bypassing normal locomotion through burst acceleration,
vanish movement, and momentum-based recovery.

Primary Combat Identity:

- mobility
- repositioning
- evasive traversal
- anime burst motion
- teleport-style movement

Visual Identity:

- silhouette break
- speed trail distortion
- afterimage disappearance
- explosive acceleration
- instant relocation

Do NOT Use:

- normal run cycle
- grounded walk
- standard jump loop
- hurt reaction
- attack recoil
- attack recovery

Transition Compatibility:

Preferred:

- dash chain
- vanish follow-up
- teleport strike
- air combo starter
- cinematic reposition

Avoid:

- abrupt idle snap
- grounded walk transition
- slow locomotion blend
- attack recovery transition

State Priority:

Teleport/vanish states should override normal dodge states if both systems
exist.

Preview folder:

`assets/sprites/goku/row_review/R02`

Mapping:

| Frames | Intent | Gameplay State | Confidence | Notes |
|---|---|---|---|---|
| `R02-01 -> R02-02` | Unresolved evasive / air movement candidate | `review_later` | Unresolved | Looks like a diagonal lift/evade, but final use should wait until all character rows are reviewed. Not punch recovery. Do not wire into gameplay yet. |
| `R02-03 -> R02-06` | Ground dash burst into speed trail | `dash_burst` | High | Best candidate for dash startup/travel. Do not use as normal run. |
| `R02-07 -> R02-08` | Dash exit / aerial slide recovery | `dash_exit` or `dash_recover` | Medium | Can follow `R02-03 -> R02-06`; may also support air movement recovery. |
| `R02-09 -> R02-11` | Vertical vanish / teleport afterimage | `vanish` or `teleport` | High | Best candidate for vanish/teleport visual. Keep separate from normal dodge unless design requires vanish dodge. |

Gameplay notes for Row 02:

- `R02-01 -> R02-02` should not have an attack hitbox.
- If used as dodge startup, invincibility should begin late, mainly around
  `R02-02`.
- If used as air hop, it should keep a normal hurtbox and no invincibility.
- `R02-03 -> R02-06` should belong to dash movement and should not be mixed
  with normal run.
- `R02-09 -> R02-11` should be reserved for vanish/teleport style effects.

## Row 03 - Reviewed, Provisional Until Movement Comparison

Status: `provisional`

Role: grounded locomotion candidate, combat approach, front-facing hover or
power movement candidate.

Core Theme:

Readable body travel and controlled forward movement, with a separate
front-facing powered motion group.

Movement Philosophy:

This row contains movement that stays more readable than Row 02. It appears to
cover foot-based approach movement first, then a front-facing stance/hover
motion that should not be treated as ordinary walking until later comparison.

Primary Combat Identity:

- locomotion
- combat approach
- cautious forward advance
- readable run cycle candidate
- front-facing power drift candidate

Visual Identity:

- readable silhouette travel
- grounded foot rhythm
- forward lean during approach
- controlled momentum
- front-facing hover/power bob

Do NOT Use:

- hurt state
- attack recoil
- attack recovery
- teleport or vanish effect
- high-speed dash smear
- unrelated defensive state

Transition Compatibility:

Preferred:

- idle return
- combat approach
- walk-to-run acceleration
- run-to-idle settle
- power stance loop

Avoid:

- direct transition from speed trail without recovery
- direct transition to hurt state
- mixing front-facing hover frames into side walk/run loops
- using front-facing hover as normal grounded locomotion

State Priority:

If Row 03 walk/run states and Row 02 dash/vanish states compete, Row 02 should
own instant displacement while Row 03 should own readable locomotion.

Preview folder:

`assets/sprites/goku/row_review/R03`

Mapping:

| Frames | Intent | Gameplay State | Confidence | Notes |
|---|---|---|---|---|
| `R03-01 -> R03-04` | Side walk / measured forward advance candidate | `walk_candidate` | Medium | Looks like readable grounded foot travel. Keep provisional until compared with later movement rows. |
| `R03-05 -> R03-08` | Forward run / combat approach candidate | `run_candidate` or `combat_approach` | Medium-High | Strong run/approach candidate with readable body travel. Existing config uses this as run, but final approval should wait for review. |
| `R03-09 -> R03-14` | Front-facing hover / power stance motion candidate | `power_hover_candidate` or `cinematic_forward_drift` | Medium | Front-facing and stylized. Do not mix into side locomotion. Compare later before assigning gameplay. |

Gameplay notes for Row 03:

- `R03-01 -> R03-04` can be a slow walk/cautious approach candidate if the
  loop reads well in gameplay.
- `R03-05 -> R03-08` can be a run/combat approach candidate, but should remain
  separate from Row 02 dash burst.
- `R03-09 -> R03-14` should remain provisional. It may be hover, power movement,
  front-facing cinematic drift, or menu/preview motion.
- Row 03 should not be used for hurt, attack recoil, attack recovery, vanish,
  or dash smear states.
- No Row 03 segment should get an attack hitbox by default.

## Pending Rows

Rows `R04 -> R10` are not yet finalized. Add each row here only after slow
preview and user review.
