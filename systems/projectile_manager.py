"""Projectile ownership, updating, drawing, and enemy collision."""

from systems.projectile import Projectile


class ProjectileManager:
    """Own active projectiles without adding character-specific behavior."""

    def __init__(self):
        self.projectiles = []

    def clear(self):
        """Remove all active projectile instances."""
        self.projectiles.clear()

    def spawn(self, projectile):
        """Add an existing Projectile instance."""
        self.projectiles.append(projectile)
        return projectile

    def spawn_debug_projectile(self, player):
        """Create a temporary neutral projectile for foundation validation."""
        direction = getattr(player, "facing", 1)
        if direction >= 0:
            x = player.rect.right + 8
        else:
            x = player.rect.left - 26

        y = player.rect.centery - 5
        return self.spawn(
            Projectile(
                x=x,
                y=y,
                direction=direction,
                speed=620,
                damage=8,
                lifetime=0.75,
                knockback=180,
            )
        )

    def update(self, dt, enemies):
        """Update projectiles and apply one-time collision damage."""
        for projectile in self.projectiles:
            projectile.update(dt)
            if projectile.active:
                self.apply_enemy_collisions(projectile, enemies)

        self.projectiles = [projectile for projectile in self.projectiles if projectile.active]

    def apply_enemy_collisions(self, projectile, enemies):
        """Damage the first enemy hit by a projectile and then consume it."""
        for enemy in enemies:
            if getattr(enemy, "defeated", False):
                continue
            if not projectile.can_hit(enemy):
                continue
            if not projectile.rect.colliderect(enemy.rect):
                continue

            damage_applied = enemy.take_damage(
                projectile.damage,
                projectile.direction * projectile.knockback,
            )
            if damage_applied:
                projectile.mark_hit(enemy)
                projectile.active = False
                return

    def draw(self, surface):
        """Draw all active projectiles."""
        for projectile in self.projectiles:
            projectile.draw(surface)
