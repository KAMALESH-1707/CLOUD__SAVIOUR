from typing import Any, Dict, List, Optional
import random

from backend.environment import CloudEnv
from backend.models import StepAction


class BaselineAgent:
    def __init__(self, task_id: str):
        self.env = CloudEnv()
        self.env.reset(task_id)
        self.history: List[Dict[str, Any]] = []

        self.best_action: Optional[StepAction] = None
        self.best_reward: float = float("-inf")

        self.action_rewards: Dict[StepAction, List[float]] = {
            action: [] for action in StepAction
        }

        self.exploration_steps = 4
        self.exploit_probability = 0.8

    def choose_action(self) -> StepAction:
        current_step = len(self.history)

        if current_step < self.exploration_steps:
            return random.choice(list(StepAction))

        scored_actions = {
            action: (sum(rewards) / len(rewards)) if rewards else float("-inf")
            for action, rewards in self.action_rewards.items()
        }

        best_empirical_action = max(scored_actions, key=scored_actions.get)

        if scored_actions[best_empirical_action] == float("-inf"):
            return random.choice(list(StepAction))

        if random.random() < self.exploit_probability:
            return best_empirical_action

        other_actions = [a for a in StepAction if a != best_empirical_action]
        return random.choice(other_actions) if other_actions else best_empirical_action

    def run_episode(self) -> float:
        total_reward = 0.0
        done = False

        while not done:
            action = self.choose_action()
            observation, reward, done, info = self.env.step(action)

            total_reward += reward.reward
            self.action_rewards[action].append(reward.reward)

            if reward.reward > self.best_reward:
                self.best_reward = reward.reward
                self.best_action = action

            self.history.append(
                {
                    "step": info["step"],
                    "action": action.value,
                    "reward": reward.reward,
                    "best_reward_so_far": self.best_reward,
                    "best_action_so_far": self.best_action.value if self.best_action else None,
                    "state": observation.state.dict(),
                }
            )

        return total_reward