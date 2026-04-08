from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from backend.baseline_agent import BaselineAgent
from backend.decision_engine import recommend_best_action
from backend.environment import CloudEnv
from backend.evaluator import compute_metrics
from backend.graders import grade_task_1, grade_task_2, grade_task_3
from backend.models import StepAction

app = FastAPI(title="Cloud Saviour Environment API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

env_instances: Dict[str, CloudEnv] = {}


class TaskRequest(BaseModel):
    task_id: str


class StepRequest(BaseModel):
    task_id: str
    action: StepAction


class EvaluationRequest(BaseModel):
    task_id: str
    history_data: List[Dict[str, Any]]


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Cloud Saviour Engine running"}


@app.post("/reset")
def reset_env(req: TaskRequest):
    if req.task_id not in env_instances:
        env_instances[req.task_id] = CloudEnv()

    env = env_instances[req.task_id]
    state = env.reset(req.task_id)
    return state.dict()


@app.post("/step")
def step_env(req: StepRequest):
    if req.task_id not in env_instances:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call /reset first.",
        )

    env = env_instances[req.task_id]
    observation, reward, done, info = env.step(req.action)

    return {
        "observation": observation.dict(),
        "reward": reward.dict(),
        "done": done,
        "info": info,
    }


@app.get("/state")
def get_state(task_id: str):
    if task_id not in env_instances:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call /reset first.",
        )

    return env_instances[task_id].state_dict()


@app.get("/recommend")
def get_recommendation(task_id: str):
    if task_id not in env_instances:
        raise HTTPException(
            status_code=400,
            detail="Environment not initialized. Call /reset first.",
        )

    env = env_instances[task_id]
    action = recommend_best_action(env.state, task_id)

    return {"recommended_action": action.value}


@app.post("/run-baseline")
def run_baseline(req: TaskRequest):
    agent = BaselineAgent(req.task_id)
    total_reward = agent.run_episode()

    return {
        "history": agent.history,
        "total_reward": total_reward,
        "best_action": agent.best_action.value if agent.best_action else None,
        "best_reward": agent.best_reward,
    }


@app.post("/evaluate")
def evaluate(req: EvaluationRequest):
    if not req.history_data:
        raise HTTPException(status_code=400, detail="History data is empty.")

    initial_state = req.history_data[0]["state"]
    metrics = compute_metrics(initial_state, req.history_data)

    if req.task_id == "web":
        score = grade_task_1(req.history_data)
    elif req.task_id == "ai":
        score = grade_task_2(req.history_data)
    else:
        score = grade_task_3(req.history_data)

    return {
        "score": score,
        "metrics": metrics,
    }


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")