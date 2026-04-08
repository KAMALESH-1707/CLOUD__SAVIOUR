import json
import os
import sys
from typing import Dict, List

import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:7860")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
HF_TOKEN = os.getenv("HF_TOKEN", "")

TASKS = ["web", "ai", "full"]

SAFE_ACTIONS = {
    "web": "enable_cache",
    "ai": "route_ai_small",
    "full": "move_batch_to_spot",
}


def log_start(task_id: str):
    print(f'[START] {json.dumps({"task_id": task_id})}')
    sys.stdout.flush()


def log_step(task_id: str, step: int, action: str, reward: float):
    print(
        f'[STEP] {json.dumps({"task_id": task_id, "step": step, "action": action, "reward": round(reward, 4)})}'
    )
    sys.stdout.flush()


def log_end(task_id: str, score: float):
    print(f'[END] {json.dumps({"task_id": task_id, "score": round(score, 4)})}')
    sys.stdout.flush()


def get_client() -> OpenAI:
    return OpenAI(
        api_key=HF_TOKEN if HF_TOKEN else "dummy",
        base_url=API_BASE_URL,
    )


def reset_env(task_id: str) -> Dict:
    response = requests.post(
        f"{API_BASE_URL}/reset",
        json={"task_id": task_id},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def step_env(task_id: str, action: str) -> Dict:
    payload = {
        "task_id": task_id,
        "action": action,
    }

    response = requests.post(
        f"{API_BASE_URL}/step",
        json=payload,
        timeout=30,
    )

    if not response.ok:
        print(f"ERROR /step: {response.status_code} {response.text}")
        sys.stdout.flush()

    response.raise_for_status()
    return response.json()


def evaluate_run(task_id: str, history_data: List[Dict]) -> Dict:
    payload = {
        "task_id": task_id,
        "history_data": history_data,
    }

    response = requests.post(
        f"{API_BASE_URL}/evaluate",
        json=payload,
        timeout=30,
    )

    if not response.ok:
        print(f"ERROR /evaluate: {response.status_code} {response.text}")
        sys.stdout.flush()

    response.raise_for_status()
    return response.json()


def run_task(task_id: str) -> float:
    log_start(task_id)

    reset_env(task_id)
    history: List[Dict] = []

    action = SAFE_ACTIONS[task_id]
    max_steps = 8

    for step in range(1, max_steps + 1):
        result = step_env(task_id, action)

        reward_value = float(result["reward"]["reward"])
        observation = result["observation"]
        done = bool(result["done"])

        history.append(
            {
                "step": step,
                "action": action,
                "reward": reward_value,
                "state": observation["state"],
            }
        )

        log_step(task_id, step, action, reward_value)

        if done:
            break

    evaluation = evaluate_run(task_id, history)
    score = float(evaluation.get("score", 0.0))
    log_end(task_id, score)

    return score


def main():
    _ = get_client()

    scores = []
    for task_id in TASKS:
        score = run_task(task_id)
        scores.append(score)

    average_score = sum(scores) / len(scores) if scores else 0.0
    print(json.dumps({"average_score": round(average_score, 4)}))
    sys.stdout.flush()


if __name__ == "__main__":
    main()