"""Keyboard-driven local preferences screen."""

import pygame

from config.default_settings import SETTINGS_MENU_ITEMS
from settings import HEIGHT, WHITE, WIDTH


MENU_BG = (12, 14, 24)
PANEL = (28, 31, 44)
PANEL_SELECTED = (45, 54, 76)
ACCENT = (130, 220, 255)
TEXT_MUTED = (185, 192, 206)


class SettingsMenu:
    """Expose safe local preferences without applying risky display changes."""

    def __init__(self, settings_store, audio_manager=None, input_manager=None):
        self.settings_store = settings_store
        self.audio_manager = audio_manager
        self.input_manager = input_manager
        self.selected_index = 0

    def handle_event(self, event):
        """Navigate and persist one keyboard settings edit."""
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_w, pygame.K_UP):
            self.selected_index = (self.selected_index - 1) % len(SETTINGS_MENU_ITEMS)
            self.play_menu_select()
        elif event.key in (pygame.K_s, pygame.K_DOWN):
            self.selected_index = (self.selected_index + 1) % len(SETTINGS_MENU_ITEMS)
            self.play_menu_select()
        elif self.matches_action("move_left", event) or event.key == pygame.K_LEFT:
            self.adjust_selected(-1)
        elif self.matches_action("move_right", event) or event.key == pygame.K_RIGHT:
            self.adjust_selected(1)
        elif self.matches_action("confirm", event):
            self.toggle_selected()

    def matches_action(self, action, event):
        """Use configured input when available with legacy defaults otherwise."""
        if self.input_manager is not None:
            return self.input_manager.event_matches(action, event)
        fallback_keys = {
            "move_left": pygame.K_a,
            "move_right": pygame.K_d,
            "confirm": pygame.K_RETURN,
        }
        return event.key == fallback_keys[action]

    def adjust_selected(self, direction):
        """Change a number or toggle value with left/right input."""
        item = SETTINGS_MENU_ITEMS[self.selected_index]
        key = item["key"]
        if item["kind"] == "toggle":
            self.settings_store.set(key, not self.settings_store.get(key))
            self.refresh_audio_settings()
            return
        self.settings_store.set(key, self.settings_store.get(key) + direction * item["step"])
        self.refresh_audio_settings()

    def toggle_selected(self):
        """Toggle the selected boolean item on Enter."""
        item = SETTINGS_MENU_ITEMS[self.selected_index]
        if item["kind"] == "toggle":
            self.settings_store.set(item["key"], not self.settings_store.get(item["key"]))
            self.refresh_audio_settings()

    def refresh_audio_settings(self):
        """Apply changed volume preferences and play one menu hook."""
        if self.audio_manager is not None:
            self.audio_manager.refresh_volumes()
        self.play_menu_select()

    def play_menu_select(self):
        """Play one optional settings-navigation hook."""
        if self.audio_manager is not None:
            self.audio_manager.play_sfx("menu_select")

    def draw(self, surface):
        """Draw current values and compact keyboard instructions."""
        surface.fill(MENU_BG)
        draw_center_text(surface, "SETTINGS", 86, 58, ACCENT)
        draw_center_text(surface, "Local preferences", 132, 30, TEXT_MUTED)

        start_y = 178
        for index, item in enumerate(SETTINGS_MENU_ITEMS):
            self.draw_item(surface, start_y + index * 58, item, index == self.selected_index)

        confirm = binding_label(self.input_manager, "confirm", "Enter")
        back = binding_label(self.input_manager, "back", "Esc")
        draw_center_text(surface, f"Up/Down select   Left/Right adjust   {confirm} toggle", HEIGHT - 62, 26, TEXT_MUTED)
        draw_center_text(surface, f"{back} returns to Mode Select", HEIGHT - 32, 24, TEXT_MUTED)

    def draw_item(self, surface, y, item, selected):
        """Draw one selected or idle preference row."""
        rect = pygame.Rect(WIDTH // 2 - 330, y, 660, 44)
        pygame.draw.rect(surface, PANEL_SELECTED if selected else PANEL, rect, border_radius=6)
        pygame.draw.rect(surface, ACCENT if selected else TEXT_MUTED, rect, 2, border_radius=6)

        font = pygame.font.Font(None, 29)
        label = font.render(item["label"], True, WHITE)
        value = font.render(format_setting_value(item["key"], self.settings_store.get(item["key"])), True, ACCENT)
        surface.blit(label, (rect.left + 18, rect.top + 11))
        surface.blit(value, (rect.right - value.get_width() - 18, rect.top + 11))


def format_setting_value(key, value):
    """Return a readable value label for one preference."""
    if isinstance(value, bool):
        return "On" if value else "Off"
    if key == "camera_shake_strength":
        return f"x{value:.1f}"
    return f"{round(value * 100):d}%"


def draw_center_text(surface, text, center_y, size, color):
    """Draw one centered settings label."""
    font = pygame.font.Font(None, size)
    rendered = font.render(text, True, color)
    surface.blit(rendered, rendered.get_rect(center=(WIDTH // 2, center_y)))


def binding_label(input_manager, action, fallback):
    """Return a configured input label with a safe legacy fallback."""
    if input_manager is None:
        return fallback
    return input_manager.get_binding_label(action)
