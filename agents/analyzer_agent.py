from langchain_openai import ChatOpenAI

from config.settings import *

llm = ChatOpenAI(model="gpt-4o-mini")

def analyze_issues(bad_rows):

    results = []

    for item in bad_rows[:5]:

        prompt = f"""
        Analyze telecom network issue:

        Data: {item['data']}
        Issues: {item['issues']}

        Explain root cause clearly.
        """

        response = llm.invoke(prompt)

        results.append({
            "row": item["row_index"],
            "issues": item["issues"],
            "analysis": response.content,
            "data": item["data"]
        })

    return results