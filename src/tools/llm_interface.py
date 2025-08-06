import subprocess

def run_ollama_model(prompt: str, model: str = "openchat:latest") -> str:
    """
    Call the Ollama model via CLI and return the string output.
    """
    result = subprocess.run(
        ["ollama", "run", model, prompt],
        capture_output=True,
        text=True,
        check=True
    )
    return result.stdout
