# src/main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np

from clip_module import TextProcessor    # Your CLIP text processing module
from gif_processor import GifProcessor      # Your GIF processing module
from giphy_api import GiphyAPI              # Your Giphy API integration module
from gemma2_reply_generator import generate_reply  # Use the Gemma-2 model for reply generation

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('vader_lexicon')

app = Flask(__name__)
CORS(app)

# Global variable to store User 2's message.
last_message_from_user2 = ""

# Initialize modules.
text_processor = TextProcessor(model_name="ViT-B/32")
gif_processor = GifProcessor(model_name="ViT-B/32")
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

    # Generate a reply using the Gemma-2 model.
    generated_reply = generate_reply(last_message_from_user2, max_length=50)
    
    # Clean and truncate the generated reply for Giphy search.
    query_text = generated_reply.strip()
    max_query_length = 50  # Adjust as needed.
    if len(query_text) > max_query_length:
        query_text = query_text[:max_query_length]

    # Retrieve GIFs from Giphy using the generated reply as the query.
    gif_urls = giphy.search_gifs(query_text, limit=10)
    
    # Compute CLIP embedding for re-ranking GIFs.
    text_embedding = text_processor.get_text_embedding(query_text)
    text_embedding_np = text_embedding.cpu().numpy()

    gif_data = []
    for url in gif_urls:
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
        "query_used": query_text,
        "suggested_gifs": suggested_gifs,
        "similarity_scores": similarity_scores
    })

if __name__ == '__main__':
    app.run(debug=True)