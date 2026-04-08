---
title: Cloud Saviour
sdk: docker
app_port: 7860
---

# 🚀 CLOUD SAVIOUR – OpenEnv Cloud Workload Optimization Environment

## 🧠 Problem Motivation

Modern cloud systems run diverse workloads such as:
- Web services
- AI inference
- Batch processing

These workloads are often **over-provisioned**, leading to:
- High operational cost 💰
- Inefficient resource usage ⚡

At the same time, aggressive optimization can cause:
- SLA violations (latency increase)
- Quality degradation

👉 Cloud Saviour simulates this real-world trade-off and enables intelligent optimization.

---

## ⚙️ Environment Overview

Cloud Saviour is an **OpenEnv-compatible simulation environment** that models a **dynamic 24-hour cloud workload cycle**.

### It includes:

- 🌐 **Web workload** → variable traffic with caching options  
- 🤖 **AI workload** → inference with model routing (small vs large)  
- ⚙️ **Batch workload** → background jobs using spot/on-demand instances  

### Standard APIs:

- `reset()` → initialize environment  
- `step(action)` → apply optimization decision  
- `state()` → retrieve current system state  

---

## 🤖 Adaptive Baseline Agent

A lightweight reinforcement learning-inspired agent is implemented that:

- Explores actions in early steps  
- Tracks reward signals for each action  
- Reuses higher-performing strategies over time  

👉 This demonstrates **reward-driven policy improvement**, making the environment RL-ready.

---

## 🎮 Action Space

The agent can take the following actions:

- `do_nothing`  
- `enable_cache`, `disable_cache`  
- `route_ai_small`, `route_ai_large`  
- `scale_up_web`, `scale_down_web`  
- `move_batch_to_spot`, `move_batch_to_on_demand`  

---

## 📊 Observation Space

Each step returns structured system metrics:

- CPU load  
- GPU load  
- Latency (ms)  
- Monthly cost  
- Quality score  
- Resource state  

---

## 🎯 Reward Function

The reward function balances multiple objectives:

### ✅ Positive rewards:
- Reduced cost  
- Lower CPU/GPU usage  
- Maintaining SLA compliance  

### ❌ Penalties:
- High latency (SLA violation)  
- Low quality (AI degradation)  
- Resource overload  
- Inefficient decisions  

👉 The goal is **multi-objective optimization** (cost + performance + quality)

---

## 🧪 Task Definitions

### 🔹 Task 1 – Web Optimization (Easy)
Optimize caching and scaling to reduce CPU load and latency.

### 🔹 Task 2 – AI Optimization (Medium)
Optimize GPU usage and cost while maintaining acceptable AI quality.

### 🔹 Task 3 – Full System Optimization (Hard)
Optimize a combined workload (web + AI + batch) under real-world constraints.

---

## 📈 Baseline Scores

> (Update these after running inference.py)

- Web task: X.XX  
- AI task: X.XX  
- Full task: X.XX  
- Average score: X.XX  

---

## 🛠️ Setup Instructions

```bash
pip install -r requirements.txt
python -m uvicorn backend.main:app --host 0.0.0.0 --port 7860
🐳 Docker Instructions
Bash
docker build -t cloud-saviour .
docker run -p 7860:7860 cloud-saviour
🌍 Summary
Cloud Saviour provides a reproducible OpenEnv environment where agents can learn to make cloud infrastructure decisions under real-world constraints:
Cost 💰
Performance ⚡
Quality 📊
👉 It is designed as a reinforcement learning-ready system for next-generation cloud optimization.
👨‍💻 Author
KAMALESH J