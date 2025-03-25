# src/main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np
from clip_module import TextProcessor
from gif_processor import GifProcessor
from giphy_api import GiphyAPI

app = Flask(__name__)
CORS(app)

# Initialize CLIP modules
text_processor = TextProcessor(model_name="ViT-B/32")
gif_processor = GifProcessor(model_name="ViT-B/32")

# Initialize Giphy API with your key
giphy_api_key = "dTQTdmW2kntqOKJ1jFfhatYeSoo3PWe7"
giphy = GiphyAPI(giphy_api_key)

@app.route('/')
def home():
    return "Welcome to the GIF Chat App!"

@app.route('/get_gifs_for_text', methods=['POST'])
def get_gifs_for_text():
    """
    1. Get user text from request
    2. Search Giphy with that text
    3. For each GIF, compute CLIP embedding
    4. Compute text embedding
    5. Rank and return top 6–8
    """
    data = request.get_json()
    user_text = data.get("message", "")

    # 1. Giphy search with user_text
    # If the user text is empty, we can bail out or handle differently
    if not user_text:
        return jsonify({"suggested_gifs": [], "similarity_scores": []})

    gif_urls = giphy.search_gifs(user_text, limit=10)  # fetch 10 for better variety

    # 2. Compute text embedding
    text_embedding = text_processor.get_text_embedding(user_text)
    text_embedding_np = text_embedding.cpu().numpy()

    # 3. For each GIF URL, compute embeddings
    all_gif_data = []
    for url in gif_urls:
        try:
            gif_embedding = gif_processor.get_gif_embedding(url)
            gif_embedding_np = gif_embedding.cpu().numpy()
            all_gif_data.append((url, gif_embedding_np))
        except Exception as e:
            print(f"Error processing {url}: {e}")

    # If no GIFs could be embedded, return empty
    if not all_gif_data:
        return jsonify({"suggested_gifs": [], "similarity_scores": []})

    # 4. Compute similarity
    # We'll do a simple dot product on normalized vectors => same as cosine similarity
    # text_embedding_np is shape (1, embed_dim)
    # gif_embedding_np is shape (1, embed_dim)
    # We'll store them in a list, then compute similarities
    similarities = []
    for url, emb in all_gif_data:
        similarity = float(np.dot(text_embedding_np, emb.T))  # since they're normalized, dot=cosine
        similarities.append((url, similarity))

    # 5. Sort by similarity descending, take top 6
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_6 = similarities[:6]

    # Return the top 6 URLs + scores
    suggested_gifs = [item[0] for item in top_6]
    similarity_scores = [item[1] for item in top_6]

    return jsonify({
        "suggested_gifs": suggested_gifs,
        "similarity_scores": similarity_scores
    })

if __name__ == '__main__':
    app.run(debug=True)