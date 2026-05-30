"""Projectile ownership, updating, drawing, and enemy collision."""

from systems.beam import Beam
from systems.projectile import Projectile


class ProjectileManager:
    """Own active projectiles without adding character-specific behavior."""

    def __init__(self):
        self.projectiles = []
        self.beams = []

    def clear(self):
        """Remove all active projectile and beam instances."""
        self.projectiles.clear()
        self.beams.clear()

    def spawn(self, projectile):
        """Add an existing Projectile instance."""
        self.projectiles.append(projectile)
        return projectile

    def spawn_beam(self, beam):
        """Add an existing Beam instance."""
        self.beams.append(beam)
        return beam

    def spawn_ki_blast(self, player, damage):
        """Create the user-approved fast Ki Blast projectile."""
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
                speed=760,
                damage=damage,
                lifetime=0.70,
                width=20,
                height=12,
                knockback=190,
            )
        )

    def spawn_kamehameha(self, player, damage):
        """Create the user-approved beam prototype."""
        direction = getattr(player, "facing", 1)
        if direction >= 0:
            x = player.rect.right + 6
        else:
            x = player.rect.left - 6

        return self.spawn_beam(
            Beam(
                x=x,
                y=player.rect.centery,
                direction=direction,
                beam_range=520,
                height=46,
                damage=damage,
                duration=0.22,
                knockback=430,
            )
        )

    def update(self, dt, enemies):
        """Update projectiles/beams and apply one-time collision damage."""
        for projectile in self.projectiles:
            projectile.update(dt)
            if projectile.active:
                self.apply_projectile_collisions(projectile, enemies)

        for beam in self.beams:
            if beam.active:
                self.apply_beam_collisions(beam, enemies)
            beam.update(dt)

        self.projectiles = [projectile for projectile in self.projectiles if projectile.active]
        self.beams = [beam for beam in self.beams if beam.active]

    def apply_projectile_collisions(self, projectile, enemies):
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

    def apply_beam_collisions(self, beam, enemies):
        """Damage each enemy at most once during one beam use."""
        for enemy in enemies:
            if getattr(enemy, "defeated", False):
                continue
            if not beam.can_hit(enemy):
                continue
            if not beam.rect.colliderect(enemy.rect):
                continue

            damage_applied = enemy.take_damage(
                beam.damage,
                beam.direction * beam.knockback,
            )
            if damage_applied:
                beam.mark_hit(enemy)

    def draw(self, surface):
        """Draw all active projectiles and beams."""
        for projectile in self.projectiles:
            projectile.draw(surface)
        for beam in self.beams:
            beam.draw(surface)
