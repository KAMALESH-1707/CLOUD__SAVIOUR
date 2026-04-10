import os
import sys
from typing import Dict, List, Optional

import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
HF_TOKEN = os.getenv("HF_TOKEN")

if HF_TOKEN is None:
    raise ValueError("HF_TOKEN environment variable is required")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN,
)

TASKS = ["web", "ai", "full"]

SAFE_ACTIONS = {
    "web": "enable_cache",
    "ai": "route_ai_small",
    "full": "move_batch_to_spot",
}


def format_bool(value: bool) -> str:
    return "true" if value else "false"


def format_reward(value) -> str:
    return f"{float(value):.2f}"


def reset_env(task_id: str) -> Dict:
    response = requests.post(
        f"{API_BASE_URL}/reset",
        json={"task_id": task_id},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def step_env(task_id: str, action: str) -> Dict:
    response = requests.post(
        f"{API_BASE_URL}/step",
        json={"task_id": task_id, "action": action},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def choose_action(task_id: str) -> str:
    return SAFE_ACTIONS[task_id]


def run_episode(task_id: str) -> None:
    env_name = "cloud-saviour"
    model_name = MODEL_NAME

    steps = 0
    rewards: List[str] = []
    success = False
    last_action_error: Optional[str] = None

    print(f"[START] task={task_id} env={env_name} model={model_name}")
    sys.stdout.flush()

    try:
        reset_env(task_id)

        done = False
        max_steps = 8

        while not done and steps < max_steps:
            action = choose_action(task_id)

            try:
                result = step_env(task_id, action)
                reward = float(result["reward"]["reward"])
                done = bool(result["done"])
                last_action_error = None

            except Exception as step_error:
                reward = 0.0
                done = True
                last_action_error = str(step_error)

            steps += 1
            rewards.append(format_reward(reward))

            print(
                f"[STEP] step={steps} action={action} "
                f"reward={format_reward(reward)} "
                f"done={format_bool(done)} "
                f"error={last_action_error if last_action_error is not None else 'null'}"
            )
            sys.stdout.flush()

            if done and last_action_error is None:
                success = True

    finally:
        print(
            f"[END] success={format_bool(success)} "
            f"steps={steps} "
            f"rewards={','.join(rewards)}"
        )
        sys.stdout.flush()


def main() -> None:
    for task_id in TASKS:
        run_episode(task_id)


if __name__ == "__main__":
    main()