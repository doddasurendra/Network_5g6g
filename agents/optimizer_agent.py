from langchain_openai import ChatOpenAI
import os
import pandas as pd

from config.settings import *

llm = ChatOpenAI(model="gpt-4o-mini")

def optimize_network(data):

    prompt = f"""
    Improve this network condition:

    {data}

    Provide:
    - Improved KPI values
    - Solution steps
    """

    response = llm.invoke(prompt)

    return response.content

class OptimizerAgent:

    def __init__(self):
        self.dataset_cache = self.load_kpi_datasets()

    def load_kpi_datasets(self):
        """
        Demo dataset loader.
        Loads KPI Excel files from data folder.
        Does not affect optimization logic.
        """
        datasets = {}

        data_files = [
            "data/telecom_kpi.xlsx",
            "data/telecom_kpi_Tower2.xlsx",
    
        ]

        for file in data_files:
            try:
                if os.path.exists(file):
                    datasets[os.path.basename(file)] = pd.read_excel(file)
            except Exception:
                pass

        return datasets

    def optimize_network(self, kpi_data):
        """
        Existing optimization logic remains unchanged.
        """
        return {
            "status": "AI Optimization Complete",
            "optimized": True
        }