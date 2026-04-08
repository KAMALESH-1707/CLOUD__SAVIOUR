import json
import requests

BASE_URL = "http://localhost:7860"
TASKS = ["web", "ai", "full"]


def run_task(task_id: str) -> float:
    print(f"\n--- Running baseline for task: {task_id} ---")

    try:
        reset_response = requests.post(
            f"{BASE_URL}/reset",
            json={"task_id": task_id},
            timeout=10,
        )
        reset_response.raise_for_status()
        print("Environment reset.")

        baseline_response = requests.post(
            f"{BASE_URL}/run-baseline",
            json={"task_id": task_id},
            timeout=20,
        )
        baseline_response.raise_for_status()
        history = baseline_response.json().get("history", [])

        evaluation_payload = {
            "req": {"task_id": task_id},
            "history_data": history,
        }

        evaluation_response = requests.post(
            f"{BASE_URL}/evaluate",
            json=evaluation_payload,
            timeout=20,
        )
        evaluation_response.raise_for_status()
        evaluation_data = evaluation_response.json()

        score = evaluation_data.get("score", 0.0)
        metrics = evaluation_data.get("metrics", {})

        print(f"Task '{task_id}' completed. Score: {score:.4f}")
        print("Metrics:")
        print(json.dumps(metrics, indent=2))

        return float(score)

    except requests.RequestException as error:
        print(f"Request error while running task '{task_id}': {error}")
        return 0.0
    except Exception as error:
        print(f"Unexpected error while running task '{task_id}': {error}")
        return 0.0


if __name__ == "__main__":
    print("Cloud Saviour - Baseline Execution")

    scores = [run_task(task_id) for task_id in TASKS]
    average_score = sum(scores) / len(scores) if scores else 0.0

    print("\n--- Final Results ---")
    print(f"Average Score: {average_score:.4f}")