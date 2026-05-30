"""Reward selection state and application helpers."""

from systems.reward import create_reward_pool


class RewardManager:
    """Generate room reward choices and apply the selected reward."""

    def __init__(self):
        self.reward_pool = create_reward_pool()
        self.current_options = []
        self.selected_index = 0
        self.chosen_rewards = []
        self.chosen_reward_names = []

    def generate_options(self, count=3):
        """Select a small deterministic set of reward options."""
        self.current_options = self.reward_pool[:count]
        self.selected_index = 0
        return self.current_options

    def has_options(self):
        """Return True while a reward selection is active."""
        return bool(self.current_options)

    def select_previous(self):
        """Move selection left."""
        if self.current_options:
            self.selected_index = (self.selected_index - 1) % len(self.current_options)

    def select_next(self):
        """Move selection right."""
        if self.current_options:
            self.selected_index = (self.selected_index + 1) % len(self.current_options)

    def selected_reward(self):
        """Return the currently selected reward, if any."""
        if not self.current_options:
            return None
        return self.current_options[self.selected_index]

    def apply_selected(self, player):
        """Apply and record the selected reward."""
        reward = self.selected_reward()
        if reward is None:
            return None

        reward.apply(player)
        self.chosen_rewards.append(reward.reward_id)
        self.chosen_reward_names.append(reward.display_name)
        self.current_options = []
        self.selected_index = 0
        return reward

    def chosen_reward_count(self):
        """Return how many rewards have been confirmed this run."""
        return len(self.chosen_rewards)

    def chosen_reward_display_names(self):
        """Return selected reward names for run summary UI."""
        return list(self.chosen_reward_names)
