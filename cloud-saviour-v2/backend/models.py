from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from enum import Enum

class ResourceMetric(BaseModel):
    cpu_cores: float
    memory_gb: float
    gpu_count: int

class StepAction(str, Enum):
    DO_NOTHING = "do_nothing"
    ENABLE_CACHE = "enable_cache"
    DISABLE_CACHE = "disable_cache"
    ROUTE_AI_SMALL = "route_ai_small"
    ROUTE_AI_LARGE = "route_ai_large"
    SCALE_UP_WEB = "scale_up_web"
    SCALE_DOWN_WEB = "scale_down_web"
    MOVE_BATCH_TO_SPOT = "move_batch_to_spot"
    MOVE_BATCH_TO_ON_DEMAND = "move_batch_to_on_demand"

class SystemState(BaseModel):
    current_hour: int
    cpu_load: float
    gpu_load: float
    latency_ms: float
    monthly_cost: float
    cache_hit_rate: float
    quality_score: float
    cache_enabled: bool
    ai_route_to_small_model: bool
    reserved_web_capacity: int
    batch_on_spot: bool
    resources: ResourceMetric

class StepObservation(BaseModel):
    state: SystemState
    history_summary: str

class StepReward(BaseModel):
    reward: float
    penalty_details: Dict[str, float]
