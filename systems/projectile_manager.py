"""Projectile ownership, updating, drawing, and enemy collision."""

from config.skill_config import KAMEHAMEHA_CONFIG, KI_BLAST_CONFIG
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
            x = player.rect.right + KI_BLAST_CONFIG["forward_offset"]
        else:
            x = player.rect.left - KI_BLAST_CONFIG["reverse_offset"]

        y = player.rect.centery - KI_BLAST_CONFIG["vertical_offset"]
        return self.spawn(
            Projectile(
                x=x,
                y=y,
                direction=direction,
                speed=KI_BLAST_CONFIG["speed"],
                damage=damage,
                lifetime=KI_BLAST_CONFIG["lifetime"],
                width=KI_BLAST_CONFIG["width"],
                height=KI_BLAST_CONFIG["height"],
                knockback=KI_BLAST_CONFIG["knockback"],
            )
        )

    def spawn_kamehameha(self, player, damage):
        """Create the user-approved beam prototype."""
        direction = getattr(player, "facing", 1)
        if direction >= 0:
            x = player.rect.right + KAMEHAMEHA_CONFIG["origin_offset"]
        else:
            x = player.rect.left - KAMEHAMEHA_CONFIG["origin_offset"]

        return self.spawn_beam(
            Beam(
                x=x,
                y=player.rect.centery,
                direction=direction,
                beam_range=KAMEHAMEHA_CONFIG["range"],
                height=KAMEHAMEHA_CONFIG["height"],
                damage=damage,
                duration=KAMEHAMEHA_CONFIG["duration"],
                knockback=KAMEHAMEHA_CONFIG["knockback"],
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
