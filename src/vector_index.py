# src/vector_index.py
import numpy as np
import faiss

class VectorIndex:
    def __init__(self, embed_dim):
        self.embed_dim = embed_dim
        # Use inner product index for cosine similarity with normalized embeddings
        self.index = faiss.IndexFlatIP(embed_dim)
        self.metadata = []  # Store metadata (e.g., file paths) corresponding to each embedding

    def add_embedding(self, embedding: np.ndarray, meta: str):
        """
        Add a single normalized embedding and its metadata to the index.
        embedding: numpy array of shape (1, embed_dim)
        meta: metadata (e.g., GIF file path or URL)
        """
        self.index.add(embedding)
        self.metadata.append(meta)

    def search(self, query_embedding: np.ndarray, top_k=5):
        """
        Search for the top_k similar embeddings.
        query_embedding: numpy array of shape (1, embed_dim)
        Returns:
            indices (np.ndarray): Indices of the top matches.
            distances (np.ndarray): Corresponding similarity scores.
        """
        total = self.index.ntotal
        if top_k > total:
            top_k = total
        distances, indices = self.index.search(query_embedding, top_k)
        return indices[0], distances[0]

# Example usage:
if __name__ == "__main__":
    embed_dim = 512  # Adjust based on your CLIP model output dimension
    index = VectorIndex(embed_dim)
    
    # Add two dummy embeddings for testing:
    dummy_embedding1 = np.random.rand(1, embed_dim).astype("float32")
    dummy_embedding1 /= np.linalg.norm(dummy_embedding1)
    dummy_embedding2 = np.random.rand(1, embed_dim).astype("float32")
    dummy_embedding2 /= np.linalg.norm(dummy_embedding2)
    
    index.add_embedding(dummy_embedding1, "gif1.gif")
    index.add_embedding(dummy_embedding2, "gif2.gif")
    
    # Create a random query embedding:
    query_embedding = np.random.rand(1, embed_dim).astype("float32")
    query_embedding /= np.linalg.norm(query_embedding)
    
    indices, distances = index.search(query_embedding, top_k=3)
    print("Top indices:", indices)
    print("Similarity scores:", distances)
    for idx in indices:
        print("Retrieved GIF metadata:", index.metadata[idx])