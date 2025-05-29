import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any

class RetrieverAgent:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initialize the retriever with embedding model and FAISS index
        
        Args:
            model_name (str): Sentence transformer model name
        """
        self.embedding_model = SentenceTransformer(model_name)
        self.faiss_index = None
        self.document_store = []
    
    def index_documents(self, documents: List[Dict[str, Any]]):
        """
        Index documents into FAISS for semantic search
        
        Args:
            documents (List[Dict[str, Any]]): List of documents to index
        """
        # Prepare embeddings
        embeddings = []
        self.document_store = []
        
        for doc in documents:
            # Convert document to a string representation
            doc_text = self._document_to_text(doc)
            
            # Generate embedding
            embedding = self.embedding_model.encode(doc_text)
            embeddings.append(embedding)
            
            # Store original document
            self.document_store.append(doc)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings_array.shape[1]
        self.faiss_index = faiss.IndexFlatL2(dimension)
        self.faiss_index.add(embeddings_array)
    
    def semantic_search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Perform semantic search on indexed documents
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
        
        Returns:
            List[Dict[str, Any]]: Top matching documents
        """
        if self.faiss_index is None:
            raise ValueError("Index not created. Call index_documents first.")
        
        # Embed query
        query_embedding = self.embedding_model.encode(query).astype('float32')
        query_embedding = query_embedding.reshape(1, -1)
        
        # Perform search
        distances, indices = self.faiss_index.search(query_embedding, top_k)
        
        # Retrieve and return top results
        results = []
        for idx in indices[0]:
            if idx < len(self.document_store):
                results.append(self.document_store[idx])
        
        return results
    
    def _document_to_text(self, doc: Dict[str, Any]) -> str:
        """
        Convert a document to a searchable text representation
        
        Args:
            doc (Dict[str, Any]): Document to convert
        
        Returns:
            str: Text representation of the document
        """
        # Combine relevant fields into a single searchable text
        text_parts = []
        
        # Handle different document types (stock data, news, etc.)
        if 'ticker' in doc:
            # Stock data document
            text_parts.append(f"Ticker: {doc.get('ticker', '')}")
            text_parts.append(f"Company: {doc.get('company_name', '')}")
            text_parts.append(f"Sector: {doc.get('sector', '')}")
            text_parts.append(f"Current Price: {doc.get('current_price', '')}")
        
        elif 'title' in doc:
            # News article document
            text_parts.append(doc.get('title', ''))
            text_parts.append(doc.get('link', ''))
        
        return " ".join(str(part) for part in text_parts if part)
    
    def combine_document_sources(self, *sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Combine multiple document sources for indexing
        
        Args:
            *sources (List[Dict[str, Any]]): Multiple document sources
        
        Returns:
            List[Dict[str, Any]]: Combined documents
        """
        combined_docs = []
        for source in sources:
            combined_docs.extend(source)
        
        return combined_docs