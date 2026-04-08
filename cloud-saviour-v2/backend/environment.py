from typing import Dict, Optional, Tuple

from backend.models import StepAction, StepObservation, StepReward, SystemState
from backend.simulator import (
    advance_time,
    calculate_derivatives,
    get_base_workload_for_hour,
    get_initial_state,
)


class CloudEnv:
    def __init__(self):
        self.state: Optional[SystemState] = None
        self.task_id: str = "full"
        self.step_count: int = 0
        self.max_steps: int = 24

    def reset(self, task_id: str = "full") -> SystemState:
        self.task_id = task_id
        self.state = get_initial_state(task_id)
        self.step_count = 0
        return self.state

    def step(self, action: StepAction) -> Tuple[StepObservation, StepReward, bool, Dict]:
        if self.state is None:
            self.reset(self.task_id)

        advance_time(self.state)
        self.step_count += 1

        self._apply_action(action)

        base_workload = get_base_workload_for_hour(self.task_id, self.state.current_hour)
        self.state = calculate_derivatives(self.state, base_workload)

        reward, penalties = self._compute_reward()
        done = self.step_count >= self.max_steps

        observation = StepObservation(
            state=self.state,
            history_summary=f"Step {self.step_count} completed. Action: {action.value}",
        )
        step_reward = StepReward(reward=reward, penalty_details=penalties)

        return observation, step_reward, done, {"step": self.step_count}

    def _apply_action(self, action: StepAction) -> None:
        if action == StepAction.ENABLE_CACHE:
            self.state.cache_enabled = True

        elif action == StepAction.DISABLE_CACHE:
            self.state.cache_enabled = False
            self.state.cache_hit_rate = 0.0

        elif action == StepAction.ROUTE_AI_SMALL:
            self.state.ai_route_to_small_model = True

        elif action == StepAction.ROUTE_AI_LARGE:
            self.state.ai_route_to_small_model = False

        elif action == StepAction.SCALE_UP_WEB:
            self.state.reserved_web_capacity += 50

        elif action == StepAction.SCALE_DOWN_WEB:
            self.state.reserved_web_capacity = max(10, self.state.reserved_web_capacity - 50)

        elif action == StepAction.MOVE_BATCH_TO_SPOT:
            self.state.batch_on_spot = True

        elif action == StepAction.MOVE_BATCH_TO_ON_DEMAND:
            self.state.batch_on_spot = False

    def _compute_reward(self) -> Tuple[float, Dict[str, float]]:
        reward = 100.0
        penalties: Dict[str, float] = {}

        cost_penalty = (self.state.monthly_cost / 1000.0) * 10.0
        reward -= cost_penalty
        penalties["cost"] = cost_penalty

        if self.state.latency_ms > 100.0:
            latency_penalty = (self.state.latency_ms - 100.0) * 0.5
            reward -= latency_penalty
            penalties["latency"] = latency_penalty

        if self.state.cpu_load > 90.0:
            cpu_penalty = (self.state.cpu_load - 90.0) * 2.0
            reward -= cpu_penalty
            penalties["cpu_overload"] = cpu_penalty

        if self.state.gpu_load > 95.0:
            gpu_penalty = (self.state.gpu_load - 95.0) * 2.0
            reward -= gpu_penalty
            penalties["gpu_overload"] = gpu_penalty

        quality_reward = self.state.quality_score * 20.0
        reward += quality_reward

        return reward, penalties

    def state_dict(self) -> Dict:
        if self.state is None:
            self.reset(self.task_id)

        return self.state.dict()