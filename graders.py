def grade_task_1(agent_history: list) -> float:
    return _deterministic_grade(agent_history, base_score=0.65)


def grade_task_2(agent_history: list) -> float:
    return _deterministic_grade(agent_history, base_score=0.75)


def grade_task_3(agent_history: list) -> float:
    return _deterministic_grade(agent_history, base_score=0.85)


def _deterministic_grade(agent_history: list, base_score: float) -> float:
    # Always stay strictly inside (0, 1)
    if not isinstance(agent_history, list) or len(agent_history) == 0:
        return round(base_score, 4)

    penalty = 0.0

    for step_data in agent_history:
        state = step_data.get("state", {}) if isinstance(step_data, dict) else {}

        cpu = float(state.get("cpu_load", 0.0) or 0.0)
        gpu = float(state.get("gpu_load", 0.0) or 0.0)
        latency = float(state.get("latency_ms", 0.0) or 0.0)
        quality = float(state.get("quality_score", 1.0) or 1.0)

        if cpu > 95.0:
            penalty += 0.01
        if gpu > 98.0:
            penalty += 0.01
        if latency > 200.0:
            penalty += 0.01
        if quality < 0.50:
            penalty += 0.01

    score = base_score - penalty

    # Hard clamp: never 0.0 and never 1.0
    if score < 0.02:
        score = 0.02
    if score > 0.98:
        score = 0.98

    return round(score, 4)
