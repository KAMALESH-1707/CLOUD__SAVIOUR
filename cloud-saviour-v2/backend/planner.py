from backend.models import SystemState, StepAction
from backend.decision_engine import apply_virtual_action, score_state
from backend.simulator import calculate_derivatives, get_base_workload_for_hour

def planner_lookahead(state: SystemState, task_id: str, depth: int = 2) -> StepAction:
    best_action = StepAction.DO_NOTHING
    max_score = float('-inf')
    
    actions = list(StepAction)
    
    for action in actions:
        seq_score = simulate_sequence(state, task_id, [action], depth)
        if seq_score > max_score:
            max_score = seq_score
            best_action = action
            
    return best_action

def simulate_sequence(state: SystemState, task_id: str, sequence: list, depth: int) -> float:
    current_state = state
    total_score = 0.0
    
    for act in sequence:
        current_state = apply_virtual_action(current_state, act)
        base_workload = get_base_workload_for_hour(task_id, current_state.current_hour)
        calculate_derivatives(current_state, base_workload)
        total_score += score_state(current_state)
        
    if depth > 1:
        best_next_score = float('-inf')
        for next_act in StepAction:
            next_state = apply_virtual_action(current_state, next_act)
            base_workload = get_base_workload_for_hour(task_id, next_state.current_hour)
            calculate_derivatives(next_state, base_workload)
            s = score_state(next_state)
            if s > best_next_score:
                best_next_score = s
        total_score += best_next_score
        
    return total_score
