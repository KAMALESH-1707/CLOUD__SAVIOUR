import math


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


def _safe_float(value, default=0.0):
    """Convert value to float, returning default for NaN, inf, or any error."""
    try:
        result = float(value)
        if not math.isfinite(result):   # catches NaN AND +inf AND -inf
            return default
        return result
    except (TypeError, ValueError):
        return default


def _clamp(score: float) -> float:
    """Guarantee output is a finite float strictly inside (0, 1)."""
    # Step 1: sanitise â€” turn any non-finite into a safe midpoint
    if not isinstance(score, (int, float)) or not math.isfinite(score):
        return 0.50
    # Step 2: hard numeric clamp well away from 0 and 1
    score = max(0.02, min(0.98, score))
    # Step 3: round (cannot escape [0.02, 0.98] after this)
    score = round(score, 4)
    # Step 4: paranoia pass â€” explicit boundary re-check after rounding
    if score < 0.02:
        score = 0.02
    if score > 0.98:
        score = 0.98
    return float(score)


def _base_grade(
    agent_history: list,
    target_cost: float,
    max_latency: float,
    min_quality: float,
) -> float:
    try:
        if not agent_history or not isinstance(agent_history, list):
            return 0.50

        total_cost = 0.0
        total_latency = 0.0
        total_quality = 0.0
        violations = 0
        valid_steps = 0

        for step_data in agent_history:
            if not isinstance(step_data, dict):
                continue

            state = step_data.get("state", {})
            if not isinstance(state, dict):
                state = {}

            total_cost    += _safe_float(state.get("monthly_cost"),  0.0)
            total_latency += _safe_float(state.get("latency_ms"),     0.0)
            total_quality += _safe_float(state.get("quality_score"),  1.0)

            cpu = _safe_float(state.get("cpu_load"), 0.0)
            gpu = _safe_float(state.get("gpu_load"), 0.0)
            if cpu > 95.0 or gpu > 98.0:
                violations += 1

            valid_steps += 1

        if valid_steps == 0:
            return 0.50

        n = float(valid_steps)
        avg_cost    = total_cost    / n
        avg_latency = total_latency / n
        avg_quality = total_quality / n

        score = 0.88

        if avg_cost > target_cost:
            penalty = (avg_cost - target_cost) / max(1.0, target_cost * 2.0)
            score -= min(0.25, _safe_float(penalty, 0.0))

        if avg_latency > max_latency:
            penalty = (avg_latency - max_latency) / max(1.0, max_latency * 2.0)
            score -= min(0.25, _safe_float(penalty, 0.0))

        if avg_quality < min_quality:
            penalty = (min_quality - avg_quality) * 1.5
            score -= min(0.15, _safe_float(penalty, 0.0))

        violation_penalty = (violations / n) * 0.10
        score -= min(0.15, _safe_float(violation_penalty, 0.0))

        return _clamp(score)

    except Exception:
        return 0.50
