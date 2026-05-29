"""Small physics helpers.

Keeping math helpers here makes it easier to reuse movement, gravity, and
collision rules across the player, enemies, bosses, and future objects.
"""


def clamp(value, minimum, maximum):
    """Keep a value between a minimum and maximum."""
    return max(minimum, min(value, maximum))


def clamp_x_to_screen(x, width, screen_width):
    """Keep an object's x position inside the screen."""
    return clamp(x, 0, screen_width - width)


def apply_gravity(y, velocity_y, gravity, dt):
    """Apply gravity to vertical velocity and position."""
    velocity_y += gravity * dt
    y += velocity_y * dt
    return y, velocity_y


def resolve_ground_collision(y, height, velocity_y, ground_y):
    """Stop an object exactly on top of the ground if it falls onto it."""
    ground_top = ground_y - height

    if y >= ground_top:
        return ground_top, 0, True

    return y, velocity_y, False


def move_toward_zero(value, amount):
    """Reduce a positive or negative velocity toward zero."""
    if value > 0:
        return max(0, value - amount)
    if value < 0:
        return min(0, value + amount)
    return 0


def rects_overlap(rect_a, rect_b):
    """Collision helper for future attacks, projectiles, and platforms."""
    return rect_a.colliderect(rect_b)
