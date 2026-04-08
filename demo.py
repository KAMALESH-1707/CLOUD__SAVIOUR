import os
import sys
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "cloud-saviour-agent")


def format_bool(value: bool) -> str:
    return "true" if value else "false"


def format_reward(value) -> str:
    return f"{float(value):.2f}"


def choose_action(task_id: str, state: dict) -> str:
    cpu = float(state.get("cpu_load", 0))
    gpu = float(state.get("gpu_load", 0))
    latency = float(state.get("latency_ms", 0))
    cost = float(state.get("monthly_cost", 0))
    quality = float(state.get("quality_score", 1))

    if task_id == "web":
        if latency > 90 or cpu > 75:
            return "scale_up_web"
        if latency < 40:
            return "enable_cache"
        return "do_nothing"

    if task_id == "ai":
        if cost > 1500:
            return "route_ai_small"
        if quality < 0.85:
            return "route_ai_large"
        return "do_nothing"

    # full system
    if cost > 1800:
        return "move_batch_to_spot"
    if gpu > 80:
        return "route_ai_small"
    return "do_nothing"


def run_demo():
    task_name = "cloud-optimization"
    env_name = "cloud-saviour"
    model_name = MODEL_NAME

    steps = 0
    rewards = []
    success = False

    print(f"[START] task={task_name} env={env_name} model={model_name}")

    try:
        # Reset environment
        response = requests.post(
            f"{API_BASE_URL}/reset",
            json={"task_id": "full"},
            timeout=10
        )
        state = response.json()

        done = False

        while not done and steps < 8:
            action = choose_action("full", state)

            step_response = requests.post(
                f"{API_BASE_URL}/step",
                json={"task_id": "full", "action": action},
                timeout=10
            )

            data = step_response.json()

            reward = data["reward"]["reward"]
            done = bool(data["done"])
            state = data["observation"]["state"]

            steps += 1
            rewards.append(format_reward(reward))

            print(
                f"[STEP] step={steps} action={action} "
                f"reward={format_reward(reward)} "
                f"done={format_bool(done)} "
                f"error=null"
            )

            if done:
                success = True
                break

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

    finally:
        print(
            f"[END] success={format_bool(success)} "
            f"steps={steps} "
            f"rewards={','.join(rewards)}"
        )


if __name__ == "__main__":
    run_demo()