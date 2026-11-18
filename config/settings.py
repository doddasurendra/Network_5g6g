import os

# Secure environment configuration - NEVER hardcode API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
QISKIT_IBM_TOKEN = os.getenv("QISKIT_IBM_TOKEN", "")
