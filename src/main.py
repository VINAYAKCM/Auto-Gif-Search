# src/main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np

from clip_module import TextProcessor    # Your CLIP text processing module
from gif_processor import GifProcessor    # Your GIF processing module
from giphy_api import GiphyAPI            # Your Giphy API integration module
from reply_generator import ReplyGenerator  # New reply generator

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('vader_lexicon')

app = Flask(__name__)
CORS(app)

last_message_from_user2 = ""

# Initialize modules
text_processor = TextProcessor(model_name="ViT-B/32")
gif_processor = GifProcessor(model_name="ViT-B/32")
reply_generator = ReplyGenerator()
# Replace with your actual Giphy API key.
giphy_api_key = "dTQTdmW2kntqOKJ1jFfhatYeSoo3PWe7"
giphy = GiphyAPI(giphy_api_key)

@app.route('/')
def home():
    return "Welcome to the GIF Chat App API!"

@app.route('/send_message_user2', methods=['POST'])
def send_message_user2():
    global last_message_from_user2
    data = request.get_json()
    message = data.get("message", "")
    last_message_from_user2 = message
    return jsonify({"message": message, "info": "User 2's message stored."})

@app.route('/generate_reply_and_gifs', methods=['POST'])
def generate_reply_and_gifs():
    global last_message_from_user2
    if not last_message_from_user2:
        return jsonify({"error": "No message from User 2 stored."}), 400

    # Generate a reply and get analysis using the new ReplyGenerator
    generated_reply, analysis = reply_generator.generate_reply(last_message_from_user2)
    
    # Get search terms for GIFs
    search_terms = reply_generator.get_gif_search_terms(last_message_from_user2, analysis)
    
    # Search for GIFs using all search terms
    all_gifs = []
    for term in search_terms:
        gifs = giphy.search_gifs(term, limit=5)
        all_gifs.extend(gifs)
    
    # Remove duplicates while preserving order
    all_gifs = list(dict.fromkeys(all_gifs))
    
    # Compute CLIP embedding for re-ranking the GIFs
    text_embedding = text_processor.get_text_embedding(last_message_from_user2)
    text_embedding_np = text_embedding.cpu().numpy()

    gif_data = []
    for url in all_gifs:
        try:
            gif_embedding = gif_processor.get_gif_embedding(url)
            gif_embedding_np = gif_embedding.cpu().numpy()
            gif_data.append((url, gif_embedding_np))
        except Exception as e:
            print(f"Error processing {url}: {e}")

    if not gif_data:
        return jsonify({"suggested_gifs": [], "similarity_scores": []})
    
    similarities = []
    for url, emb in gif_data:
        sim = float(np.dot(text_embedding_np, emb.T))
        similarities.append((url, sim))
    
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_results = similarities[:6]
    suggested_gifs = [item[0] for item in top_results]
    similarity_scores = [item[1] for item in top_results]

    return jsonify({
        "generated_reply": generated_reply,
        "message_analysis": analysis,
        "search_terms": search_terms,
        "suggested_gifs": suggested_gifs,
        "similarity_scores": similarity_scores
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001)
