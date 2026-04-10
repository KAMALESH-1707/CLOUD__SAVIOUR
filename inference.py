import os
import sys
import time
import subprocess
from typing import Dict, List, Optional

import requests
from openai import OpenAI

API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")
API_KEY = os.getenv("API_KEY")

if API_KEY is None:
    raise ValueError("API_KEY environment variable is required")

client = OpenAI(
    base_url=API_BASE_URL,
    api_key=API_KEY,
)

TASKS = ["web", "ai", "full"]
ENV_NAME = "cloud-saviour"
MAX_STEPS = 5


def format_bool(value: bool) -> str:
    return "true" if value else "false"


def format_reward(value: float) -> str:
    return f"{float(value):.2f}"


def safe_post(path: str, payload: Optional[Dict] = None, timeout: int = 30) -> Optional[requests.Response]:
    try:
        response = requests.post(
            f"http://127.0.0.1:7860{path}",
            json=payload,
            timeout=timeout,
        )
        return response
    except Exception:
        return None


def safe_get(path: str, params: Optional[Dict] = None, timeout: int = 10) -> Optional[requests.Response]:
    try:
        response = requests.get(
            f"http://127.0.0.1:7860{path}",
            params=params,
            timeout=timeout,
        )
        return response
    except Exception:
        return None


def server_is_ready() -> bool:
    response = safe_get("/health", timeout=3)
    return response is not None and response.ok


def start_server() -> Optional[subprocess.Popen]:
    if server_is_ready():
        return None

    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "server.app"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return None

    for _ in range(20):
        if server_is_ready():
            return process
        time.sleep(1)

    return process


def reset_env(task_id: str) -> bool:
    response = safe_post("/reset", {"task_id": task_id})
    return response is not None and response.ok


def step_env(task_id: str, action: str) -> Optional[Dict]:
    response = safe_post("/step", {"task_id": task_id, "action": action})
    if response is None or not response.ok:
        return None

    try:
        return response.json()
    except Exception:
        return None


def llm_choose_action(task_id: str) -> str:
    allowed_actions = {
        "web": ["enable_cache", "scale_up_web", "scale_down_web", "do_nothing"],
        "ai": ["route_ai_small", "route_ai_large", "do_nothing"],
        "full": ["move_batch_to_spot", "enable_cache", "route_ai_small", "do_nothing"],
    }

    prompt = (
        f"You are choosing one action for task '{task_id}'. "
        f"Return only one action from this list: {allowed_actions[task_id]}"
    )

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Return only a single valid action string."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )

        action = response.choices[0].message.content.strip()
        if action in allowed_actions[task_id]:
            return action
    except Exception:
        pass

    # Safe fallback
    fallback = {
        "web": "enable_cache",
        "ai": "route_ai_small",
        "full": "move_batch_to_spot",
    }
    return fallback[task_id]


def emit_start(task_id: str) -> None:
    print(f"[START] task={task_id} env={ENV_NAME} model={MODEL_NAME}", flush=True)


def emit_step(step: int, action: str, reward: float, done: bool, error: Optional[str]) -> None:
    error_text = error if error is not None else "null"
    print(
        f"[STEP] step={step} action={action} reward={format_reward(reward)} "
        f"done={format_bool(done)} error={error_text}",
        flush=True,
    )


def emit_end(success: bool, steps: int, rewards: List[str]) -> None:
    print(
        f"[END] success={format_bool(success)} steps={steps} rewards={','.join(rewards)}",
        flush=True,
    )


def run_episode(task_id: str) -> None:
    steps = 0
    rewards: List[str] = []
    success = False

    emit_start(task_id)

    try:
        reset_ok = reset_env(task_id)
        if not reset_ok:
            emit_end(False, 0, rewards)
            return

        done = False

        while not done and steps < MAX_STEPS:
            action = llm_choose_action(task_id)
            result = step_env(task_id, action)

            if result is None:
                steps += 1
                reward_value = 0.0
                rewards.append(format_reward(reward_value))
                emit_step(steps, action, reward_value, True, "step_failed")
                emit_end(False, steps, rewards)
                return

            try:
                reward_value = float(result["reward"]["reward"])
                done = bool(result["done"])
            except Exception:
                steps += 1
                reward_value = 0.0
                rewards.append(format_reward(reward_value))
                emit_step(steps, action, reward_value, True, "parse_failed")
                emit_end(False, steps, rewards)
                return

            steps += 1
            rewards.append(format_reward(reward_value))
            emit_step(steps, action, reward_value, done, None)

            if done:
                success = True

    except Exception:
        emit_end(False, steps, rewards)
        return

    emit_end(success, steps, rewards)


def main() -> None:
    process = start_server()

    try:
        for task_id in TASKS:
            run_episode(task_id)
    finally:
        if process is not None:
            try:
                process.terminate()
            except Exception:
                pass


if __name__ == "__main__":
    main()