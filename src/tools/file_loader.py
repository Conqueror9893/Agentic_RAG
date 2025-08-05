from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_documents(directory_path: str = "./data"):
    """
    Loads documents from the specified directory, splits them into chunks, and returns them.
    """
    print(f"Loading documents from {directory_path}...")
    loader = DirectoryLoader(directory_path, glob="**/*.txt", loader_cls=TextLoader)
    documents = loader.load()

    if not documents:
        print("No documents found.")
        return []

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunked_documents = text_splitter.split_documents(documents)

    print(f"Loaded and split {len(documents)} documents into {len(chunked_documents)} chunks.")

    return chunked_documents

if __name__ == "__main__":
    # This is for testing the file loader in isolation.
    # First, let's create a dummy file in the data directory.
    import os
    if not os.path.exists("./data"):
        os.makedirs("./data")
    with open("./data/sample.txt", "w") as f:
        f.write("This is a sample document about LangChain and LangGraph. " * 100)
        f.write("\n\n")
        f.write("This is another paragraph in the same document. " * 100)

    docs = load_documents()
    print(f"Successfully loaded {len(docs)} chunks.")
    print("First chunk:")
    print(docs[0].page_content)
    print("\nMetadata:")
    print(docs[0].metadata)