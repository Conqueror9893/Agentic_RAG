# Copy config_template.py to config.py and configure your environment variables or use a .env file.

import os
from dotenv import load_dotenv
load_dotenv()

USE_GITHUB_CONTEXT = os.getenv("USE_GITHUB_CONTEXT", "False").lower() == "true"
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN", "")
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "rag_agentic_system")
