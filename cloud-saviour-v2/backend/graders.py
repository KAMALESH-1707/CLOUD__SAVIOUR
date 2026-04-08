def grade_task_1(agent_history: list) -> float:
    return _base_grade(
        agent_history,
        target_cost=1500.0,
        max_latency=80.0,
        min_quality=0.95,
    )


def grade_task_2(agent_history: list) -> float:
    return _base_grade(
        agent_history,
        target_cost=1800.0,
        max_latency=120.0,
        min_quality=0.85,
    )


def grade_task_3(agent_history: list) -> float:
    return _base_grade(
        agent_history,
        target_cost=2000.0,
        max_latency=100.0,
        min_quality=0.90,
    )


def _base_grade(
    agent_history: list,
    target_cost: float,
    max_latency: float,
    min_quality: float,
) -> float:
    if not agent_history:
        return 0.0

    total_cost = 0.0
    total_latency = 0.0
    total_quality = 0.0
    violations = 0

    for step_data in agent_history:
        state = step_data["state"]

        total_cost += state["monthly_cost"]
        total_latency += state["latency_ms"]
        total_quality += state["quality_score"]

        if state["cpu_load"] > 95.0 or state["gpu_load"] > 98.0:
            violations += 1

    avg_cost = total_cost / len(agent_history)
    avg_latency = total_latency / len(agent_history)
    avg_quality = total_quality / len(agent_history)

    score = 1.0

    if avg_cost > target_cost:
        score -= min(0.35, (avg_cost - target_cost) / 1000.0)

    if avg_latency > max_latency:
        score -= min(0.35, (avg_latency - max_latency) / 100.0)

    if avg_quality < min_quality:
        score -= min(0.20, (min_quality - avg_quality) * 2.0)

    score -= violations * 0.05

    return max(0.0, min(1.0, round(score, 4)))