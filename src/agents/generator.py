import subprocess
import shlex

class Generator:
    """
    This agent generates a coherent answer using a local Ollama model via subprocess.
    """
    def __init__(self, model_name: str = "openchat:latest"):
        self.model_name = model_name
        # Check if ollama is available
        try:
            subprocess.run(["ollama", "--version"], check=True, encoding="utf-8", capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError("Ollama is not available in the system's PATH. Please install it to use this Generator.")

    def generate(self, query: str, documents: list[str]) -> str:
        """
        Generates an answer using the Ollama CLI.

        Args:
            query: The user's original query.
            documents: A list of retrieved document contents.

        Returns:
            The generated answer as a string.
        """
        print(f"Generating answer for query: '{query}' using model {self.model_name}")

        context = "\n\n".join(documents)

        prompt_template = (
            "You are a helpful assistant. Your task is to answer the user's query based *only* on the provided context.\n"
            "If the context does not contain the answer, state that you don't have enough information.\n\n"
            "Here is the context:\n"
            "---CONTEXT---\n"
            "{context}\n"
            "---END CONTEXT---\n\n"
            "Here is the user's query:\n"
            "---QUERY---\n"
            "{query}\n"
            "---END QUERY---\n\n"
            "Answer:"
        )

        prompt = prompt_template.format(context=context, query=query)

        # We need to be careful with how we pass the prompt to the command
        # to avoid shell injection issues, although with subprocess.run and a list of args, it's safer.
        # `ollama run` expects the prompt as a final argument.
        command = ["ollama", "run", self.model_name, prompt]

        try:
            print("---CALLING OLLAMA VIA SUBPROCESS---")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )

            generated_answer = result.stdout.strip()
            print(f"---OLLAMA RESPONSE---\n{generated_answer}\n---END OLLAMA RESPONSE---")

            return generated_answer

        except FileNotFoundError:
            return "Error: The 'ollama' command was not found. Please make sure Ollama is installed and in your PATH."
        except subprocess.CalledProcessError as e:
            error_message = f"Error executing Ollama: {e}\nStderr: {e.stderr}"
            print(error_message)
            return error_message
