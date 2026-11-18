from langgraph.graph import StateGraph
from agents.monitor_agent import detect_poor_network
from agents.analyzer_agent import analyze_issues
from agents.optimizer_agent import optimize_network
from agents.quantum_agent import quantum_optimize

class NetworkState(dict):
    pass

def monitor(state):
    return {"bad_rows": detect_poor_network(state["file"])}

def analyze(state):
    return {"analyzed": analyze_issues(state["bad_rows"])}

def optimize(state):

    optimized = []

    for item in state["analyzed"]:
        sol = optimize_network(item["data"])
        optimized.append({**item, "solution": sol})

    return {"optimized": optimized}

def quantum(state):

    final = []

    for item in state["optimized"]:
        decision = quantum_optimize(item)
        final.append({**item, "quantum_decision": decision})

    return {"final": final}

graph = StateGraph(NetworkState)

graph.add_node("monitor", monitor)
graph.add_node("analyze", analyze)
graph.add_node("optimize", optimize)
graph.add_node("quantum", quantum)

graph.set_entry_point("monitor")

graph.add_edge("monitor", "analyze")
graph.add_edge("analyze", "optimize")
graph.add_edge("optimize", "quantum")

graph.set_finish_point("quantum")

app_graph = graph.compile()