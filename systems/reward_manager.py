"""Reward selection state, stack tracking, and room-clear utility helpers."""

from collections import Counter

from systems.reward import create_reward_pool, heal_player


class RewardManager:
    """Generate room reward choices and apply the selected reward."""

    def __init__(self):
        self.reward_pool = create_reward_pool()
        self.current_options = []
        self.selected_index = 0
        self.chosen_rewards = []
        self.chosen_reward_names = []
        self.reward_stacks = Counter()
        self.option_cursor = 0

    def generate_options(self, count=3):
        """Select unique available options while rotating through the pool."""
        available_rewards = [reward for reward in self.reward_pool if self.can_stack(reward)]
        if not available_rewards:
            self.current_options = []
            self.selected_index = 0
            return self.current_options

        start_index = self.option_cursor % len(available_rewards)
        ordered_rewards = available_rewards[start_index:] + available_rewards[:start_index]
        self.current_options = ordered_rewards[:count]
        self.option_cursor = (start_index + count) % len(available_rewards)
        self.selected_index = 0
        return self.current_options

    def has_options(self):
        """Return True while a reward selection is active."""
        return bool(self.current_options)

    def can_stack(self, reward):
        """Return True while a reward has not reached its configured cap."""
        return reward.max_stacks is None or self.reward_stacks[reward.reward_id] < reward.max_stacks

    def stack_count(self, reward_id):
        """Return how many confirmed copies of one reward the run owns."""
        return self.reward_stacks[reward_id]

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
        """Apply and record the selected reward if it remains stackable."""
        reward = self.selected_reward()
        if reward is None or not self.can_stack(reward):
            return None

        reward.apply(player, reward.value)
        self.chosen_rewards.append(reward.reward_id)
        self.chosen_reward_names.append(reward.display_name)
        self.reward_stacks[reward.reward_id] += 1
        self.current_options = []
        self.selected_index = 0
        return reward

    def apply_room_clear_effects(self, player):
        """Apply utility healing once when a combat room is completed."""
        heal_amount = getattr(player, "room_clear_heal", 0)
        if heal_amount > 0:
            heal_player(player, heal_amount)

    def chosen_reward_count(self):
        """Return how many rewards have been confirmed this run."""
        return len(self.chosen_rewards)

    def chosen_reward_display_names(self):
        """Return compact selected-reward labels for HUD and clear summary."""
        display_names = []
        seen_reward_ids = set()
        reward_by_id = {reward.reward_id: reward for reward in self.reward_pool}
        for reward_id in self.chosen_rewards:
            if reward_id in seen_reward_ids:
                continue
            seen_reward_ids.add(reward_id)
            reward = reward_by_id[reward_id]
            stacks = self.reward_stacks[reward_id]
            suffix = f" x{stacks}" if stacks > 1 else ""
            display_names.append(f"{reward.display_name}{suffix}")
        return display_names
