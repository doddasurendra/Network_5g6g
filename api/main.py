from fastapi import FastAPI
from agents.graph_agent import app_graph

app = FastAPI()

@app.get("/run-system")
def run_system():

    result = app_graph.invoke({
        "file": "data/telecom_kpi.csv"
    })

    return result["final"]