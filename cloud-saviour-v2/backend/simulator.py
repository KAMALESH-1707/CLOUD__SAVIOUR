import random
from typing import Dict

from backend.models import ResourceMetric, SystemState


def get_base_workload_for_hour(task_id: str, hour: int) -> Dict[str, float]:
    if 4 <= hour <= 23:
        time_factor = 1.0 - ((hour - 14) ** 2) / 100.0
    else:
        time_factor = 0.5

    time_factor = max(0.1, time_factor)

    if task_id == "web":
        return {"web": time_factor * 100, "ai": 0, "batch": 10}
    elif task_id == "ai":
        return {"web": 10, "ai": time_factor * 50, "batch": 5}
    else:
        return {"web": time_factor * 80, "ai": time_factor * 40, "batch": time_factor * 30}


def get_initial_state(task_id: str) -> SystemState:
    return SystemState(
        current_hour=0,
        cpu_load=20.0,
        gpu_load=0.0,
        latency_ms=50.0,
        monthly_cost=1000.0,
        cache_hit_rate=0.0,
        quality_score=1.0,
        cache_enabled=False,
        ai_route_to_small_model=False,
        reserved_web_capacity=100,
        batch_on_spot=False,
        resources=ResourceMetric(cpu_cores=16.0, memory_gb=64.0, gpu_count=2),
    )


def calculate_derivatives(state: SystemState, base_workload: Dict[str, float]) -> SystemState:
    noise = random.uniform(0.9, 1.1)

    web_load = base_workload.get("web", 0.0) * noise
    ai_load = base_workload.get("ai", 0.0) * noise
    batch_load = base_workload.get("batch", 0.0) * noise

    if state.cache_enabled:
        state.cache_hit_rate = min(0.95, state.cache_hit_rate + 0.1)
        web_load *= (1 - state.cache_hit_rate)
    else:
        state.cache_hit_rate = max(0.0, state.cache_hit_rate - 0.2)

    base_cost = 1000.0

    if state.cache_enabled:
        base_cost += 50.0

    base_cost += state.reserved_web_capacity * 2.0
    base_cost += state.resources.gpu_count * 500.0 * (0.5 if state.ai_route_to_small_model else 1.0)

    if state.batch_on_spot:
        base_cost += batch_load * 0.2
        if random.random() < 0.1:
            state.latency_ms += 50.0
    else:
        base_cost += batch_load * 0.8

    state.monthly_cost = base_cost

    state.cpu_load = (web_load * 0.5 + batch_load * 0.8) / state.resources.cpu_cores * 10.0
    state.cpu_load = min(100.0, max(0.0, state.cpu_load))

    if state.ai_route_to_small_model:
        state.gpu_load = ai_load * 0.5 / state.resources.gpu_count * 5.0
        state.quality_score = 0.8
    else:
        state.gpu_load = ai_load * 1.5 / state.resources.gpu_count * 5.0
        state.quality_score = 1.0

    state.gpu_load = min(100.0, max(0.0, state.gpu_load))

    if state.cpu_load > 80.0:
        state.latency_ms += (state.cpu_load - 80.0) * 5.0
    else:
        state.latency_ms = max(20.0, state.latency_ms - 10.0)

    if state.reserved_web_capacity > web_load * 1.5:
        state.latency_ms = max(20.0, state.latency_ms - 5.0)
    elif state.reserved_web_capacity < web_load:
        state.latency_ms += (web_load - state.reserved_web_capacity) * 2.0

    state.latency_ms = min(5000.0, state.latency_ms)

    return state


def advance_time(state: SystemState) -> SystemState:
    state.current_hour += 1
    if state.current_hour >= 24:
        state.current_hour = 0
    return state