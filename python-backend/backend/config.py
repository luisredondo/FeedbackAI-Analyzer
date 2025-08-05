import os
from dotenv import load_dotenv

def load_environment_variables():
    """Loads environment variables from a .env file."""
    load_dotenv()
    # Check for essential keys
    required_keys = ["OPENAI_API_KEY", "TAVILY_API_KEY", "LANGCHAIN_API_KEY"]
    for key in required_keys:
        if not os.getenv(key):
            print(f"Warning: Environment variable {key} not set.")

# Load variables on import
load_environment_variables()