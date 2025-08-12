import subprocess
import shlex

class Rephraser:
    """
    This agent rephrases the user's query to improve retrieval results by generating multiple variations.
    It uses a local Ollama model via subprocess.
    """
    def __init__(self, model_name: str = "openchat:latest"):
        self.model_name = model_name

    def rephrase(self, query: str) -> list[str]:
        """
        Rephrases the given query into multiple variations.

        Args:
            query: The user's original query.

        Returns:
            A list of rephrased queries, including the original.
        """
        print(f"Rephrasing query: '{query}' using model {self.model_name}")

        prompt_template = (
            "You are a helpful assistant. Your task is to generate 3 different versions of the following user query for a search engine. "
            "The queries should be varied to cover different angles of the topic. "
            "Return *only* the rephrased queries, each on a new line, without any numbering or introduction.\n\n"
            "Original Query: '{query}'"
        )

        prompt = prompt_template.format(query=query)

        command = ["ollama", "run", self.model_name, prompt]

        try:
            print("---CALLING OLLAMA FOR REPHRASING VIA SUBPROCESS---")
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True
            )

            rephrased_queries = result.stdout.strip().split('\n')
            # Clean up any empty lines
            rephrased_queries = [q.strip() for q in rephrased_queries if q.strip()]

            print(f"---OLLAMA RESPONSE---\n{rephrased_queries}\n---END OLLAMA RESPONSE---")

            # Always include the original query as well
            all_queries = [query] + rephrased_queries
            return list(set(all_queries)) # Use set to ensure uniqueness

        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error rephrasing query: {e}. Falling back to original query.")
            return [query]
