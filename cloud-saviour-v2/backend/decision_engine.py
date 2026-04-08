from backend.models import SystemState, StepAction
from typing import List, Tuple

def score_state(state: SystemState) -> float:
    score = 100.0
    score -= (state.monthly_cost / 1000.0) * 10.0
    if state.latency_ms > 100.0:
        score -= (state.latency_ms - 100.0) * 0.5
    if state.cpu_load > 90.0:
        score -= (state.cpu_load - 90.0) * 2.0
    if state.gpu_load > 95.0:
        score -= (state.gpu_load - 95.0) * 2.0
    score += state.quality_score * 20.0
    return score

def recommend_best_action(state: SystemState, task_id: str) -> StepAction:
    if state.latency_ms > 150 and not state.cache_enabled:
        return StepAction.ENABLE_CACHE
    if state.cpu_load > 85 and not state.cache_enabled:
        return StepAction.ENABLE_CACHE
    if state.gpu_load > 85 and not state.ai_route_to_small_model:
        return StepAction.ROUTE_AI_SMALL
    if state.monthly_cost > 2000 and not state.batch_on_spot:
        return StepAction.MOVE_BATCH_TO_SPOT
    if state.latency_ms > 100 and state.reserved_web_capacity < 500:
        return StepAction.SCALE_UP_WEB
    if state.reserved_web_capacity > 300 and state.cpu_load < 50:
        return StepAction.SCALE_DOWN_WEB
    
    return StepAction.DO_NOTHING

def apply_virtual_action(state: SystemState, action: StepAction) -> SystemState:
    import copy
    new_state = copy.deepcopy(state)
    if action == StepAction.ENABLE_CACHE:
        new_state.cache_enabled = True
    elif action == StepAction.DISABLE_CACHE:
        new_state.cache_enabled = False
        new_state.cache_hit_rate = 0.0
    elif action == StepAction.ROUTE_AI_SMALL:
        new_state.ai_route_to_small_model = True
    elif action == StepAction.ROUTE_AI_LARGE:
        new_state.ai_route_to_small_model = False
    elif action == StepAction.SCALE_UP_WEB:
        new_state.reserved_web_capacity += 50
    elif action == StepAction.SCALE_DOWN_WEB:
        new_state.reserved_web_capacity = max(10, new_state.reserved_web_capacity - 50)
    elif action == StepAction.MOVE_BATCH_TO_SPOT:
        new_state.batch_on_spot = True
    elif action == StepAction.MOVE_BATCH_TO_ON_DEMAND:
        new_state.batch_on_spot = False
    return new_state
