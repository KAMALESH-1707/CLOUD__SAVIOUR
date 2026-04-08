const API_BASE = "";

const els = {
    taskSelect: document.getElementById("task-select"),
    btnReset: document.getElementById("btn-reset"),
    btnRefresh: document.getElementById("btn-refresh"),
    btnBaseline: document.getElementById("btn-baseline"),
    btnRecommend: document.getElementById("btn-recommend"),
    actionBtns: document.querySelectorAll(".action-btn"),

    valHour: document.getElementById("metric-hour"),
    valQuality: document.getElementById("metric-quality"),
    valCost: document.getElementById("metric-cost"),
    valCpu: document.getElementById("metric-cpu"),
    valGpu: document.getElementById("metric-gpu"),
    valLatency: document.getElementById("metric-latency"),

    log: document.getElementById("action-log"),
    stateJson: document.getElementById("state-json"),
    recOutput: document.getElementById("recommendation-output"),
};

function logMsg(message, isReward = false) {
    const entry = document.createElement("div");
    entry.className = `log-entry ${isReward ? "reward" : ""}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    els.log.prepend(entry);
}

function updateState(state) {
    els.stateJson.textContent = JSON.stringify(state, null, 2);

    els.valHour.textContent = state.current_hour;
    els.valQuality.textContent = Number(state.quality_score).toFixed(2);
    els.valCost.textContent = `$${Number(state.monthly_cost).toFixed(2)}`;
    els.valCpu.textContent = `${Number(state.cpu_load).toFixed(1)}%`;
    els.valGpu.textContent = `${Number(state.gpu_load).toFixed(1)}%`;
    els.valLatency.textContent = `${Number(state.latency_ms).toFixed(0)}ms`;
}

async function resetEnv() {
    const taskId = els.taskSelect.value;

    try {
        const response = await fetch(`${API_BASE}/reset`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId }),
        });

        if (!response.ok) {
            throw new Error("Failed to reset environment.");
        }

        const state = await response.json();
        updateState(state);

        els.log.innerHTML = "";
        els.recOutput.textContent = "";
        logMsg(`Environment reset for task: ${taskId}`);
    } catch (error) {
        logMsg(`Error resetting environment: ${error.message}`);
    }
}

async function fetchState() {
    const taskId = els.taskSelect.value;

    try {
        const response = await fetch(`${API_BASE}/state?task_id=${taskId}`);

        if (!response.ok) {
            throw new Error("Environment not initialized. Reset first.");
        }

        const state = await response.json();
        updateState(state);
        logMsg("State refreshed.");
    } catch (error) {
        logMsg(`Error fetching state: ${error.message}`);
    }
}

async function stepEnv(action) {
    const taskId = els.taskSelect.value;

    try {
        const response = await fetch(`${API_BASE}/step`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                task_id: taskId,
                action: action,
            }),
        });

        if (!response.ok) {
            throw new Error("Step execution failed.");
        }

        const data = await response.json();
        updateState(data.observation.state);

        logMsg(`Action executed: ${action}`);
        logMsg(
            `Reward: ${Number(data.reward.reward).toFixed(2)} | Penalties: ${JSON.stringify(data.reward.penalty_details)}`,
            true
        );

        if (data.done) {
            logMsg("Episode completed (24 steps reached).", true);
        }

        els.recOutput.textContent = "";
    } catch (error) {
        logMsg(`Error executing action: ${error.message}`);
    }
}

async function getRecommendation() {
    const taskId = els.taskSelect.value;

    try {
        els.recOutput.textContent = "Calculating best action...";

        const response = await fetch(`${API_BASE}/recommend?task_id=${taskId}`);

        if (!response.ok) {
            throw new Error("Recommendation request failed.");
        }

        const data = await response.json();
        els.recOutput.textContent = `Suggested Action: ${data.recommended_action}`;
        logMsg(`Recommendation received: ${data.recommended_action}`, true);

        await fetchState();
    } catch (error) {
        els.recOutput.textContent = `Error: ${error.message}`;
        logMsg(`Recommendation error: ${error.message}`);
    }
}

async function runBaseline() {
    const taskId = els.taskSelect.value;

    try {
        logMsg(`Running baseline for task: ${taskId}...`);

        const response = await fetch(`${API_BASE}/run-baseline`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ task_id: taskId }),
        });

        if (!response.ok) {
            throw new Error("Baseline execution failed.");
        }

        const data = await response.json();
        logMsg(`Baseline completed. Episode length: ${data.history.length}`);

        const evaluationResponse = await fetch(`${API_BASE}/evaluate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                task_id: taskId,
                history_data: data.history,
            }),
        });

        if (!evaluationResponse.ok) {
            throw new Error("Evaluation failed.");
        }

        const evaluationData = await evaluationResponse.json();
        logMsg(`Final Score: ${Number(evaluationData.score).toFixed(4)}`, true);

        if (data.best_action) {
            logMsg(`Learned best action: ${data.best_action}`, true);
        }

        if (data.best_reward !== undefined) {
            logMsg(`Best reward observed: ${Number(data.best_reward).toFixed(2)}`, true);
        }

        if (data.total_reward !== undefined) {
            logMsg(`Total episode reward: ${Number(data.total_reward).toFixed(2)}`, true);
        }

        if (evaluationData.metrics) {
            logMsg(`Baseline metrics summary captured.`, true);
        }

        if (data.history.length > 0) {
            updateState(data.history[data.history.length - 1].state);
            logMsg("State updated to final baseline step.", true);
        }
    } catch (error) {
        logMsg(`Error running baseline: ${error.message}`);
    }
}

els.btnReset.addEventListener("click", resetEnv);
els.btnRefresh.addEventListener("click", fetchState);
els.btnRecommend.addEventListener("click", getRecommendation);
els.btnBaseline.addEventListener("click", runBaseline);

els.actionBtns.forEach((button) => {
    button.addEventListener("click", (event) => {
        const action = event.target.getAttribute("data-action");
        stepEnv(action);
    });
});

resetEnv();