from langchain_community.vectorstores import Chroma
import chromadb
from sentence_transformers import SentenceTransformer

VectorStore = Chroma
class SentenceTransformerEmbeddings:
    """
    A custom embedding class that uses the sentence-transformers library.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        # The model will be downloaded from the Hugging Face Hub the first time it's used.
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load SentenceTransformer model '{model_name}'. Please ensure you have an internet connection and the model name is correct. Error: {e}")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embeds a list of documents."""
        print(f"Embedding {len(texts)} documents with sentence-transformer model...")
        embeddings = self.model.encode(texts, convert_to_tensor=False).tolist()
        return embeddings

    def embed_query(self, text: str) -> list[float]:
        """Embeds a single query."""
        print(f"Embedding query with sentence-transformer model...")
        embedding = self.model.encode(text, convert_to_tensor=False).tolist()
        return embedding

def get_vector_store(collection_name: str = "rag_agentic_system", persist_directory: str = "./chroma_db"):
    """
    Initializes and returns a Chroma vector store using sentence-transformers.
    """
    print(f"Initializing vector store with sentence-transformers embeddings...")

    client = chromadb.PersistentClient(path=persist_directory)

    embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        client=client,
        persist_directory=persist_directory,
    )

    return vector_store

def add_documents_to_store(vector_store, documents):
    """
    Adds a list of documents to the vector store.
    """
    if not documents:
        print("No documents to add to the vector store.")
        return

    print(f"Adding {len(documents)} document chunks to the vector store...")
    vector_store.add_documents(documents)
    print("Documents added and persisted successfully.")


if __name__ == '__main__':
    from file_loader import load_documents
    import os

    if not os.path.exists("./data/sample.txt"):
        if not os.path.exists("./data"):
            os.makedirs("./data")
        with open("./data/sample.txt", "w") as f:
            f.write("This is a test document about vector stores using sentence-transformers.")

    documents = load_documents("./data")

    vector_store = get_vector_store()

    if documents:
        add_documents_to_store(vector_store, documents)

        query = "What are vector stores?"
        results = vector_store.similarity_search(query, k=1)

        print(f"\nSimilarity search for: '{query}'")
        if results:
            print("Found results:")
            for doc in results:
                print(doc.page_content)
        else:
            print("No results found.")
