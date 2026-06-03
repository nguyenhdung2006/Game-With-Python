"""Projectile ownership, updating, drawing, and enemy collision."""

from config.goku_sprite_config import (
    GOKU_ENERGY_DISC_EFFECT_PATHS,
    GOKU_KAMEHAMEHA_EFFECT_PATH,
    GOKU_KI_BLAST_EFFECT_PATH,
    GOKU_PROJECTILE_IMPACT_EFFECT_PATHS,
    GOKU_SUPER_SAIYAN_KAMEHAMEHA_EFFECT_PATH,
)
from config.skill_config import ENERGY_DISC_CONFIG, KAMEHAMEHA_CONFIG, KI_BLAST_CONFIG
from systems.animation_timing import get_animation_dt
from systems.beam import Beam
from systems.projectile import Projectile
from systems.projectile_impact import ProjectileImpact


class ProjectileManager:
    """Own active projectiles without adding character-specific behavior."""

    def __init__(self, preferences=None):
        self.preferences = preferences if preferences is not None else {}
        self.projectiles = []
        self.beams = []
        self.pending_kamehamehas = []
        self.pending_energy_discs = []
        self.impacts = []

    def clear(self):
        """Remove all active projectile and beam instances."""
        self.projectiles.clear()
        self.beams.clear()
        self.pending_kamehamehas.clear()
        self.pending_energy_discs.clear()
        self.impacts.clear()

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
        projectile = Projectile(
            x=x,
            y=y,
            direction=direction,
            speed=KI_BLAST_CONFIG["speed"],
            damage=damage,
            lifetime=KI_BLAST_CONFIG["lifetime"],
            width=KI_BLAST_CONFIG["width"],
            height=KI_BLAST_CONFIG["height"],
            knockback=KI_BLAST_CONFIG["knockback"],
            sprite_path=GOKU_KI_BLAST_EFFECT_PATH,
            impact_sprite_paths=GOKU_PROJECTILE_IMPACT_EFFECT_PATHS,
            sprite_scale=KI_BLAST_CONFIG["sprite_scale"],
        )
        projectile.owner = player
        return self.spawn(projectile)

    def spawn_energy_disc(self, player, damage):
        """Queue the disc until the approved R12 throw animation completes."""
        pending = {
            "player": player,
            "damage": damage,
            "timer": ENERGY_DISC_CONFIG["windup_duration"],
        }
        self.pending_energy_discs.append(pending)
        return pending

    def release_energy_disc(self, player, damage):
        """Create the animated R12-05/06 disc at its release point."""
        direction = getattr(player, "facing", 1)
        if direction >= 0:
            x = player.rect.right + ENERGY_DISC_CONFIG["forward_offset"]
        else:
            x = player.rect.left - ENERGY_DISC_CONFIG["reverse_offset"]

        y = player.rect.centery - ENERGY_DISC_CONFIG["vertical_offset"]
        projectile = Projectile(
            x=x,
            y=y,
            direction=direction,
            speed=ENERGY_DISC_CONFIG["speed"],
            damage=damage,
            lifetime=ENERGY_DISC_CONFIG["lifetime"],
            width=ENERGY_DISC_CONFIG["width"],
            height=ENERGY_DISC_CONFIG["height"],
            knockback=ENERGY_DISC_CONFIG["knockback"],
            sprite_paths=GOKU_ENERGY_DISC_EFFECT_PATHS,
            sprite_frame_delay=ENERGY_DISC_CONFIG["sprite_frame_delay"],
            impact_sprite_paths=GOKU_PROJECTILE_IMPACT_EFFECT_PATHS,
        )
        projectile.owner = player
        return self.spawn(projectile)

    def spawn_kamehameha(self, player, damage):
        """Queue the beam until the approved body animation finishes winding up."""
        pending = {
            "player": player,
            "damage": damage,
            "timer": KAMEHAMEHA_CONFIG["windup_duration"],
        }
        self.pending_kamehamehas.append(pending)
        return pending

    def release_kamehameha(self, player, damage):
        """Create the user-approved beam at the player's current release point."""
        direction = getattr(player, "facing", 1)
        if direction >= 0:
            x = player.rect.right + KAMEHAMEHA_CONFIG["origin_offset"]
        else:
            x = player.rect.left - KAMEHAMEHA_CONFIG["origin_offset"]

        sprite_path = (
            GOKU_SUPER_SAIYAN_KAMEHAMEHA_EFFECT_PATH
            if getattr(player, "is_super_saiyan", False)
            else GOKU_KAMEHAMEHA_EFFECT_PATH
        )
        duration_multiplier = (
            KAMEHAMEHA_CONFIG["super_saiyan_duration_multiplier"]
            if getattr(player, "is_super_saiyan", False)
            else 1.0
        )
        beam = Beam(
            x=x,
            y=player.rect.centery,
            direction=direction,
            beam_range=KAMEHAMEHA_CONFIG["range"],
            height=KAMEHAMEHA_CONFIG["height"],
            damage=damage,
            duration=KAMEHAMEHA_CONFIG["duration"] * duration_multiplier,
            knockback=KAMEHAMEHA_CONFIG["knockback"],
            sprite_path=sprite_path,
        )
        beam.owner = player
        return self.spawn_beam(beam)

    def update(self, dt, enemies):
        """Update projectiles/beams and apply one-time collision damage."""
        animation_dt = get_animation_dt(self.preferences, dt)
        self.update_pending_kamehamehas(dt)
        self.update_pending_energy_discs(dt)
        for impact in self.impacts:
            impact.update(animation_dt)

        for projectile in self.projectiles:
            projectile.update(dt, animation_dt)
            if projectile.active:
                self.apply_projectile_collisions(projectile, enemies)

        for beam in self.beams:
            if beam.active:
                beam.refresh_hitbox(enemies)
                self.apply_beam_collisions(beam, enemies)
            beam.update(dt)

        self.projectiles = [projectile for projectile in self.projectiles if projectile.active]
        self.beams = [beam for beam in self.beams if beam.active]
        self.impacts = [impact for impact in self.impacts if impact.active]

    def update_pending_kamehamehas(self, dt):
        """Release queued beams once their R11 windup playback completes."""
        remaining = []
        for pending in self.pending_kamehamehas:
            pending["timer"] = max(0.0, pending["timer"] - dt)
            if pending["timer"] > 1e-9:
                remaining.append(pending)
                continue
            player = pending["player"]
            if not getattr(player, "defeated", False):
                self.release_kamehameha(player, pending["damage"])
        self.pending_kamehamehas = remaining

    def update_pending_energy_discs(self, dt):
        """Release queued discs once the R12-01..04 throw finishes."""
        remaining = []
        for pending in self.pending_energy_discs:
            pending["timer"] = max(0.0, pending["timer"] - dt)
            if pending["timer"] > 1e-9:
                remaining.append(pending)
                continue
            player = pending["player"]
            if not getattr(player, "defeated", False):
                self.release_energy_disc(player, pending["damage"])
        self.pending_energy_discs = remaining

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
                self.register_owner_damage(projectile, projectile.damage)
                projectile.mark_hit(enemy)
                if projectile.impact_sprite_paths:
                    self.impacts.append(
                        ProjectileImpact(projectile.rect.center, projectile.impact_sprite_paths)
                    )
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
                self.register_owner_damage(beam, beam.damage)
                beam.mark_hit(enemy)

    def register_owner_damage(self, attack, amount):
        """Charge character-specific resources without coupling projectile primitives."""
        owner = getattr(attack, "owner", None)
        if owner is not None and hasattr(owner, "register_outgoing_damage"):
            owner.register_outgoing_damage(amount)

    def draw(self, surface):
        """Draw all active projectiles and beams."""
        for projectile in self.projectiles:
            projectile.draw(surface)
        for beam in self.beams:
            beam.draw(surface)
        for impact in self.impacts:
            impact.draw(surface)
