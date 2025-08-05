import re
import json
import subprocess

def run_ollama_model(prompt: str, model: str = "openchat:latest") -> dict:
        """
        Call the Ollama model via CLI and return parsed JSON output.
        """
        full_prompt = f"""
    You are a smart intent parser for JIRA queries. Extract the intent and parameters from user input.

    Return a JSON in this format:
    {{
    "intent": "get_user_worklogs" | "get_project_status" | "get_user_tickets" | "unsupported",
    "parameters": {{
        "user": "<username_if_applicable>",
        "project": "<project_if_applicable>"
    }}
    }}

    User query: "{prompt}"
    """
        result = subprocess.run(
            ["ollama", "run", model, full_prompt],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Try extracting the first JSON object from LLM output
        match = re.search(r'\{.*\}', result.stdout, re.DOTALL)
        if not match:
            return {"intent": "unsupported", "parameters": {}}
        
        return json.loads(match.group(0))
