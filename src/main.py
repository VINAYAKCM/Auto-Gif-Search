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
CORS(app, resources={r"/*": {"origins": "*"}})

last_message_from_user2 = ""

# Initialize modules
text_processor = TextProcessor(model_name="ViT-B/32")
gif_processor = GifProcessor(model_name="ViT-B/32")
reply_generator = ReplyGenerator()

# Use a new API key - this is a development key, replace with your production key
giphy_api_key = "GlVGYHkr3WSBnllca54iNt0yFbjz7L65"  # New API key
giphy = GiphyAPI(giphy_api_key)

@app.route('/')
def home():
    return "Welcome to the GIF Chat App API!"

@app.route('/send_message_user2', methods=['POST'])
def send_message_user2():
    try:
        data = request.get_json()
        message = data.get("message", "")
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        global last_message_from_user2
        last_message_from_user2 = message
        return jsonify({"message": message, "info": "User 2's message stored."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/generate_reply_and_gifs', methods=['POST'])
def generate_reply_and_gifs():
    try:
        data = request.get_json()
        message = data.get("message", "")
        
        if not message:
            return jsonify({"error": "No message provided"}), 400

        # Generate a reply and get analysis
        generated_reply, analysis = reply_generator.generate_reply(message)
        
        # Get search terms for GIFs
        search_terms = reply_generator.get_gif_search_terms(message, analysis)
        print(f"Search terms for '{message}': {search_terms}")
        
        # Search for GIFs using all search terms
        all_gifs = []
        for term in search_terms:
            try:
                gifs = giphy.search_gifs(term, limit=3)  # Reduced limit to avoid rate limiting
                print(f"Found {len(gifs)} GIFs for term '{term}'")
                all_gifs.extend(gifs)
            except Exception as e:
                print(f"Error searching for term '{term}': {str(e)}")
                continue
        
        # Remove duplicates while preserving order
        all_gifs = list(dict.fromkeys(all_gifs))
        print(f"Total unique GIFs found: {len(all_gifs)}")
        
        if not all_gifs:
            return jsonify({
                "generated_reply": generated_reply,
                "message_analysis": analysis,
                "search_terms": search_terms,
                "suggested_gifs": [],
                "similarity_scores": []
            })

        # Compute CLIP embedding for re-ranking the GIFs
        text_embedding = text_processor.get_text_embedding(message)
        text_embedding_np = text_embedding.cpu().numpy()

        gif_data = []
        for url in all_gifs:
            try:
                gif_embedding = gif_processor.get_gif_embedding(url)
                gif_embedding_np = gif_embedding.cpu().numpy()
                gif_data.append((url, gif_embedding_np))
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue

        if not gif_data:
            return jsonify({
                "generated_reply": generated_reply,
                "message_analysis": analysis,
                "search_terms": search_terms,
                "suggested_gifs": [],
                "similarity_scores": []
            })
        
        similarities = []
        for url, emb in gif_data:
            sim = float(np.dot(text_embedding_np, emb.T))
            similarities.append((url, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:6]
        suggested_gifs = [item[0] for item in top_results]
        similarity_scores = [item[1] for item in top_results]

        print(f"Returning {len(suggested_gifs)} suggested GIFs")
        return jsonify({
            "generated_reply": generated_reply,
            "message_analysis": analysis,
            "search_terms": search_terms,
            "suggested_gifs": suggested_gifs,
            "similarity_scores": similarity_scores
        })
    except Exception as e:
        print(f"Error in generate_reply_and_gifs: {str(e)}")
        return jsonify({
            "error": str(e),
            "suggested_gifs": [],
            "similarity_scores": []
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
