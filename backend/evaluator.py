from typing import List, Dict, Any

def compute_metrics(initial_state: Dict[str, Any], history: List[Dict[str, Any]]) -> Dict[str, float]:
    if not history: return {}
    
    avg_cost = sum(x["state"]["monthly_cost"] for x in history) / len(history)
    avg_cpu = sum(x["state"]["cpu_load"] for x in history) / len(history)
    avg_gpu = sum(x["state"]["gpu_load"] for x in history) / len(history)
    avg_latency = sum(x["state"]["latency_ms"] for x in history) / len(history)
    avg_quality = sum(x["state"]["quality_score"] for x in history) / len(history)
    
    cost_reduction = (initial_state["monthly_cost"] - avg_cost) / initial_state["monthly_cost"] * 100
    cpu_reduction = (initial_state["cpu_load"] - avg_cpu) / initial_state["cpu_load"] * 100 
    
    if initial_state["gpu_load"] > 0:
        gpu_reduction = (initial_state["gpu_load"] - avg_gpu) / initial_state["gpu_load"] * 100
    else:
        gpu_reduction = -avg_gpu * 100 # arbitrary metric if initial is zero
        
    return {
        "cost_reduction_percent": cost_reduction,
        "cpu_reduction_percent": cpu_reduction,
        "gpu_reduction_percent": gpu_reduction,
        "latency_change": avg_latency - initial_state["latency_ms"],
        "quality_change": avg_quality - initial_state["quality_score"]
    }
