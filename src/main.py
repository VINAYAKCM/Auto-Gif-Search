# src/main.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import numpy as np
import logging

from clip_module import TextProcessor    # Your CLIP text processing module
from gif_processor import GifProcessor    # Your GIF processing module
from giphy_api import GiphyAPI            # Your Giphy API integration module
from reply_generator import ReplyGenerator  # New reply generator

import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger_eng')
nltk.download('vader_lexicon')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

last_message_from_user2 = ""

# Initialize modules
try:
    text_processor = TextProcessor(model_name="ViT-B/32")
    gif_processor = GifProcessor(model_name="ViT-B/32")
    reply_generator = ReplyGenerator()
    logger.info("Successfully initialized all modules")
except Exception as e:
    logger.error(f"Error initializing modules: {str(e)}")
    raise

# Use a new API key - this is a development key, replace with your production key
giphy_api_key = "GlVGYHkr3WSBnllca54iNt0yFbjz7L65"  # New API key
giphy = GiphyAPI(giphy_api_key)

# Test the Giphy API on startup
try:
    test_gifs = giphy.search_gifs("test", limit=1)
    if test_gifs:
        logger.info("Successfully tested Giphy API")
    else:
        logger.warning("Giphy API test returned no results")
except Exception as e:
    logger.error(f"Error testing Giphy API: {str(e)}")

@app.route('/')
def home():
    return "Welcome to the GIF Chat App API!"

@app.route('/trending_gifs', methods=['GET'])
def get_trending_gifs():
    try:
        # Get trending GIFs from Giphy
        gifs = giphy.get_trending_gifs(limit=15)  # Limit to 15 trending GIFs
        logger.info(f"Found {len(gifs)} trending GIFs")
        return jsonify({"gifs": gifs})
    except Exception as e:
        logger.error(f"Error getting trending GIFs: {str(e)}")
        return jsonify({"error": str(e), "gifs": []}), 500

@app.route('/search_gifs', methods=['POST'])
def search_gifs():
    try:
        data = request.get_json()
        query = data.get("query", "")
        
        if not query:
            return jsonify({"error": "No search query provided"}), 400

        logger.info(f"Searching GIFs for query: {query}")
        
        # Search GIFs using the query
        gifs = giphy.search_gifs(query, limit=15)  # Limit to 15 search results
        logger.info(f"Found {len(gifs)} GIFs for query: {query}")
        
        # If we have CLIP embeddings, we can re-rank the results
        try:
            text_embedding = text_processor.get_text_embedding(query)
            text_embedding_np = text_embedding.cpu().numpy()

            gif_data = []
            for url in gifs:
                try:
                    gif_embedding = gif_processor.get_gif_embedding(url)
                    gif_embedding_np = gif_embedding.cpu().numpy()
                    gif_data.append((url, gif_embedding_np))
                except Exception as e:
                    logger.warning(f"Error processing GIF {url}: {str(e)}")
                    continue

            if gif_data:
                similarities = []
                for url, emb in gif_data:
                    sim = float(np.dot(text_embedding_np, emb.T))
                    similarities.append((url, sim))
                
                similarities.sort(key=lambda x: x[1], reverse=True)
                gifs = [item[0] for item in similarities]
                logger.info("Successfully re-ranked GIFs using CLIP")
        except Exception as e:
            logger.warning(f"Error during CLIP processing: {str(e)}")
            # If CLIP fails, we'll just use the original Giphy results
            pass

        return jsonify({"gifs": gifs})
    except Exception as e:
        logger.error(f"Error searching GIFs: {str(e)}")
        return jsonify({"error": str(e), "gifs": []}), 500

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

        logger.info(f"Generating reply for message: {message}")

        try:
            # Generate a reply and get analysis
            generated_reply, analysis = reply_generator.generate_reply(message)
            logger.info(f"Generated analysis: {analysis}")
        except Exception as e:
            logger.error(f"Error in reply generation: {str(e)}")
            return jsonify({"error": f"Reply generation failed: {str(e)}"}), 500

        try:
            # Get search terms for GIFs
            search_terms = reply_generator.get_gif_search_terms(message, analysis)
            logger.info(f"Search terms for '{message}': {search_terms}")
        except Exception as e:
            logger.error(f"Error generating search terms: {str(e)}")
            return jsonify({"error": f"Search term generation failed: {str(e)}"}), 500
        
        # Search for GIFs using all search terms
        all_gifs = []
        for term in search_terms:
            try:
                gifs = giphy.search_gifs(term, limit=3)  # Reduced limit to avoid rate limiting
                logger.info(f"Found {len(gifs)} GIFs for term '{term}'")
                all_gifs.extend(gifs)
            except Exception as e:
                logger.error(f"Error searching for term '{term}': {str(e)}")
                continue
        
        # Remove duplicates while preserving order
        all_gifs = list(dict.fromkeys(all_gifs))
        logger.info(f"Total unique GIFs found: {len(all_gifs)}")
        
        if not all_gifs:
            logger.warning("No GIFs found for any search terms")
            return jsonify({
                "generated_reply": generated_reply,
                "message_analysis": analysis,
                "search_terms": search_terms,
                "suggested_gifs": [],
                "similarity_scores": []
            })

        try:
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
                    logger.warning(f"Error processing GIF {url}: {str(e)}")
                    continue

            if not gif_data:
                logger.warning("No valid GIF embeddings generated")
                return jsonify({
                    "generated_reply": generated_reply,
                    "message_analysis": analysis,
                    "search_terms": search_terms,
                    "suggested_gifs": all_gifs[:6],  # Return unranked GIFs if CLIP fails
                    "similarity_scores": [1.0] * min(6, len(all_gifs))
                })
            
            similarities = []
            for url, emb in gif_data:
                sim = float(np.dot(text_embedding_np, emb.T))
                similarities.append((url, sim))
            
            similarities.sort(key=lambda x: x[1], reverse=True)
            top_results = similarities[:6]
            suggested_gifs = [item[0] for item in top_results]
            similarity_scores = [item[1] for item in top_results]

            logger.info(f"Successfully ranked {len(suggested_gifs)} GIFs")
            return jsonify({
                "generated_reply": generated_reply,
                "message_analysis": analysis,
                "search_terms": search_terms,
                "suggested_gifs": suggested_gifs,
                "similarity_scores": similarity_scores
            })
        except Exception as e:
            logger.error(f"Error in CLIP processing: {str(e)}")
            # If CLIP fails, return unranked GIFs
            return jsonify({
                "generated_reply": generated_reply,
                "message_analysis": analysis,
                "search_terms": search_terms,
                "suggested_gifs": all_gifs[:6],
                "similarity_scores": [1.0] * min(6, len(all_gifs))
            })
    except Exception as e:
        logger.error(f"Error in generate_reply_and_gifs: {str(e)}")
        return jsonify({
            "error": str(e),
            "suggested_gifs": [],
            "similarity_scores": []
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
