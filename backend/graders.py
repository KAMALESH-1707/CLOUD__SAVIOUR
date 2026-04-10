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
        return 0.50

    total_cost = 0.0
    total_latency = 0.0
    total_quality = 0.0
    violations = 0

    for step_data in agent_history:
        state = step_data.get("state", {})

        total_cost += float(state.get("monthly_cost", 0.0))
        total_latency += float(state.get("latency_ms", 0.0))
        total_quality += float(state.get("quality_score", 1.0))

        if float(state.get("cpu_load", 0.0)) > 95.0 or float(state.get("gpu_load", 0.0)) > 98.0:
            violations += 1

    n = max(1, len(agent_history))
    avg_cost = total_cost / n
    avg_latency = total_latency / n
    avg_quality = total_quality / n

    score = 0.90

    if avg_cost > target_cost:
        score -= min(0.30, (avg_cost - target_cost) / 2000.0)

    if avg_latency > max_latency:
        score -= min(0.30, (avg_latency - max_latency) / 200.0)

    if avg_quality < min_quality:
        score -= min(0.20, (min_quality - avg_quality) * 2.0)

    score -= min(0.20, violations * 0.03)

    # Hard clamp to strict open interval (0, 1)
    score = float(score)
    if score <= 0.01:
        score = 0.01
    elif score >= 0.99:
        score = 0.99

    return round(score, 4)
