import pytest
from src.agents.retriever import Retriever
from unittest.mock import MagicMock
from langchain.schema import Document

def test_retriever_initialization():
    """
    Tests that the Retriever agent can be initialized with a mock vector store.
    """
    mock_vector_store = MagicMock()
    retriever = Retriever(vector_store=mock_vector_store)
    assert retriever is not None
    assert retriever.vector_store == mock_vector_store

def test_retrieve_with_dummy_data():
    """
    Tests the retrieve method with a simple list of queries and a mock vector store.
    """
    # Create mock documents
    mock_doc_1 = Document(page_content="Paris is the capital of France.", metadata={"source": "doc1"})
    mock_doc_2 = Document(page_content="The Eiffel Tower is in Paris.", metadata={"source": "doc2"})

    # Create a mock vector store and configure its similarity_search method
    mock_vector_store = MagicMock()
    mock_vector_store.similarity_search.return_value = [mock_doc_1, mock_doc_2]

    retriever = Retriever(vector_store=mock_vector_store)
    queries = ["what is the capital of France?"]

    documents = retriever.retrieve(queries)

    # Assert that similarity_search was called correctly
    mock_vector_store.similarity_search.assert_called_once_with("what is the capital of France?", k=2)

    # Assert that the content of the documents is returned
    assert len(documents) == 2
    assert "Paris is the capital of France." in documents
    assert "The Eiffel Tower is in Paris." in documents
