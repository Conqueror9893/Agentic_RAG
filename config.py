import os
from dotenv import load_dotenv

load_dotenv()

# -----------------
# LLM Configuration
# -----------------
# We'll use OpenAI for this project, but you can easily swap it out for another provider.
# Make sure to set your OPENAI_API_KEY in a .env file in the root of the project.
#
# .env file example:
# OPENAI_API_KEY="sk-..."
#
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# It's a good practice to specify the model name in the config.
# For this project, we'll start with gpt-4o, but you can change it to "gpt-3.5-turbo" or other models.
# OPENAI_MODEL_NAME = "gpt-4o"


# ---------------------
# Vector DB Configuration
# ---------------------
# For local development, we'll use ChromaDB and store it on disk.
# You can change this path to your preferred location.
CHROMA_PERSIST_DIRECTORY = "./chroma_db"
CHROMA_COLLECTION_NAME = "rag_agentic_system"


# ---------------------
# External API Keys (for Verifier Agent)
# ---------------------
# If you want the Verifier agent to use external tools like a web search,
# you'll need to provide the API key for that service.
# For example, using Tavily Search:
# TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")


# ---------------------
# Outlook Adaptor Configuration
# ---------------------
# To use the Outlook adaptor in a headless environment, you need to register an application
# in Azure Active Directory and grant it Application permissions.
# See src/adaptors/README.md for detailed instructions.
OUTLOOK_CLIENT_ID = os.getenv("OUTLOOK_CLIENT_ID")
OUTLOOK_TENANT_ID = os.getenv("OUTLOOK_TENANT_ID")
OUTLOOK_CLIENT_SECRET = os.getenv("OUTLOOK_CLIENT_SECRET")
OUTLOOK_USER_PRINCIPAL_NAME = os.getenv("OUTLOOK_USER_PRINCIPAL_NAME")
