from transformers import pipeline
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import torch
from typing import Dict, List, Tuple
import re

class ReplyGenerator:
    def __init__(self):
        # Initialize sentiment analyzer
        self.sia = SentimentIntensityAnalyzer()
        
        # Initialize emotion classifier
        self.emotion_classifier = pipeline(
            "text-classification",
            model="j-hartmann/emotion-english-distilroberta-base",
            return_all_scores=True
        )
        
        # Initialize intent classifier
        self.intent_classifier = pipeline(
            "text-classification",
            model="facebook/bart-large-mnli",
            return_all_scores=True
        )
        
        # Common response patterns for different intents/emotions
        self.response_patterns = {
            "positive": [
                "That's great!",
                "Awesome!",
                "I'm happy for you!",
                "That's wonderful!"
            ],
            "negative": [
                "I'm sorry to hear that",
                "That must be tough",
                "I understand",
                "That's difficult"
            ],
            "question": [
                "Let me think about that",
                "That's an interesting question",
                "I'm not sure about that",
                "What do you think?"
            ],
            "greeting": [
                "Hi there!",
                "Hello!",
                "Hey!",
                "Good to see you!"
            ]
        }

    def analyze_message(self, message: str) -> Dict:
        """Analyze the message for sentiment, emotion, and intent."""
        # Get sentiment scores
        sentiment_scores = self.sia.polarity_scores(message)
        
        # Get emotion scores
        emotion_scores = self.emotion_classifier(message)[0]
        
        # Get intent scores
        intent_scores = self.intent_classifier(message)[0]
        
        return {
            "sentiment": sentiment_scores,
            "emotions": emotion_scores,
            "intent": intent_scores
        }

    def generate_reply(self, message: str) -> Tuple[str, Dict]:
        """Generate a contextual reply based on message analysis."""
        # Analyze the message
        analysis = self.analyze_message(message)
        
        # Determine the dominant emotion
        dominant_emotion = max(analysis["emotions"], key=lambda x: x["score"])["label"]
        
        # Determine the intent
        dominant_intent = max(analysis["intent"], key=lambda x: x["score"])["label"]
        
        # Get sentiment polarity
        sentiment = analysis["sentiment"]["compound"]
        
        # Select appropriate response pattern
        if sentiment > 0.3:
            pattern = "positive"
        elif sentiment < -0.3:
            pattern = "negative"
        elif "?" in message:
            pattern = "question"
        else:
            pattern = "greeting"
        
        # Generate reply
        import random
        reply = random.choice(self.response_patterns[pattern])
        
        return reply, {
            "sentiment": sentiment,
            "emotion": dominant_emotion,
            "intent": dominant_intent,
            "pattern": pattern
        }

    def get_gif_search_terms(self, message: str, analysis: Dict) -> List[str]:
        """Generate search terms for GIFs based on message analysis."""
        terms = []
        
        # Add emotion-based terms
        terms.append(analysis["emotion"])
        
        # Add intent-based terms
        terms.append(analysis["intent"])
        
        # Add pattern-based terms
        terms.append(analysis["pattern"])
        
        # Simple word extraction (no NLTK required)
        # Split on spaces and punctuation, keep only words
        words = re.findall(r'\b\w+\b', message.lower())
        # Remove common stop words
        stop_words = {'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're", 
                     "you've", "you'll", "you'd", 'your', 'yours', 'yourself', 'yourselves', 'he', 
                     'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it', "it's", 
                     'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 
                     'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 
                     'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 
                     'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 
                     'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 
                     'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 
                     'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 
                     'further', 'then', 'once'}
        content_words = [word for word in words if word not in stop_words]
        terms.extend(content_words[:3])  # Add up to 3 key words
        
        return list(set(terms))  # Remove duplicates 