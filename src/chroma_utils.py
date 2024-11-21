import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import os
import logging
from typing import Optional, List

class ChromaDBClient:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize ChromaDB client with persistent storage"""
        # Ensure the persistence directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize the client with persistence
        self.persist_directory = persist_directory
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True
            )
        )
        
        # Initialize the embedding function
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"  # This is a lightweight, efficient model
        )
        
    def create_collection(self, collection_name: str, language: str):
        """Create or get a collection for a specific language"""
        try:
            # Delete existing collection if it exists
            try:
                self.client.delete_collection(name=f"constitution_{language.lower()}")
            except:
                pass
                
            # Create new collection
            collection = self.client.create_collection(
                name=f"constitution_{language.lower()}",
                embedding_function=self.embedding_function,
                metadata={"language": language}
            )
            return collection
        except Exception as e:
            logging.error(f"Error creating collection: {str(e)}")
            raise

    def add_documents(self, collection_name: str, texts: List[str], metadata: List[dict], ids: List[str]):
        """Add documents to a collection"""
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            
            # Add documents in batches to handle large datasets
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                end_idx = min(i + batch_size, len(texts))
                collection.add(
                    documents=texts[i:end_idx],
                    metadatas=metadata[i:end_idx],
                    ids=ids[i:end_idx]
                )
                
        except Exception as e:
            logging.error(f"Error adding documents: {str(e)}")
            raise

    def query_collection(self, collection_name: str, query_text: str, n_results: int = 5):
        """Query a collection and return relevant documents"""
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results
        except Exception as e:
            logging.error(f"Error querying collection: {str(e)}")
            # Return empty results in case of error
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

    def get_language_collection(self, language: str):
        """Get the collection for a specific language"""
        try:
            collection_name = f"constitution_{language.lower()}"
            return self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
        except Exception as e:
            logging.error(f"Error getting collection: {str(e)}")
            return None