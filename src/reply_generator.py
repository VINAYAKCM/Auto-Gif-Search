from transformers import pipeline
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.tag import pos_tag
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

        # Download required NLTK data
        nltk.download('averaged_perceptron_tagger')
        nltk.download('maxent_ne_chunker')
        nltk.download('words')
        
        # Message type patterns
        self.message_patterns = {
            "question": r'\?$|\b(what|who|where|when|why|how)\b',
            "exclamation": r'!$|\b(wow|omg|oh|ah|hey|whoa)\b',
            "greeting": r'\b(hi|hello|hey|good morning|good evening|good afternoon)\b',
            "farewell": r'\b(bye|goodbye|see you|later|good night)\b',
            "agreement": r'\b(yes|yeah|sure|okay|ok|alright|agree)\b',
            "disagreement": r'\b(no|nope|disagree|not really|nah)\b',
            "gratitude": r'\b(thanks|thank you|appreciate|grateful)\b',
            "apology": r'\b(sorry|apologize|my bad|oops)\b',
            "sarcasm": r'\b(sure\.\.\.|right\.\.\.|whatever|oh really)\b',
            "celebration": r'\b(congrats|congratulations|yay|hurray|awesome)\b',
            "sympathy": r'\b(sorry to hear|that\'s tough|hope you\'re okay)\b'
        }
        
        # Emotion-specific GIF modifiers
        self.emotion_modifiers = {
            "joy": ["happy", "excited", "celebration"],
            "sadness": ["sad", "crying", "disappointed"],
            "anger": ["angry", "mad", "frustrated"],
            "fear": ["scared", "nervous", "worried"],
            "surprise": ["shocked", "amazed", "wow"],
            "disgust": ["disgusted", "gross", "ew"],
            "neutral": ["okay", "neutral", "meh"]
        }

        # Intent-specific GIF modifiers
        self.intent_modifiers = {
            "question": ["thinking", "confused", "wondering"],
            "statement": ["explaining", "talking", "saying"],
            "command": ["pointing", "directing", "ordering"],
            "request": ["asking", "pleading", "requesting"],
            "opinion": ["judging", "thinking", "considering"]
        }

    def analyze_message(self, message: str) -> Dict:
        """Analyze the message for sentiment, emotion, intent, and message type."""
        # Get sentiment scores
        sentiment_scores = self.sia.polarity_scores(message)
        
        # Get emotion scores
        emotion_scores = self.emotion_classifier(message)[0]
        emotion_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Get intent scores
        intent_scores = self.intent_classifier(message)[0]
        intent_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Identify message types
        message_types = []
        for msg_type, pattern in self.message_patterns.items():
            if re.search(pattern, message.lower()):
                message_types.append(msg_type)
        
        # POS tagging for key phrases
        tokens = word_tokenize(message)
        pos_tags = pos_tag(tokens)
        
        # Extract key phrases (nouns, verbs, adjectives)
        key_phrases = []
        for i, (word, tag) in enumerate(pos_tags):
            # Get nouns
            if tag.startswith('NN'):
                key_phrases.append(word)
            # Get verbs
            elif tag.startswith('VB'):
                key_phrases.append(word)
            # Get adjectives with their nouns
            elif tag.startswith('JJ') and i + 1 < len(pos_tags):
                next_word, next_tag = pos_tags[i + 1]
                if next_tag.startswith('NN'):
                    key_phrases.append(f"{word} {next_word}")
        
        return {
            "sentiment": sentiment_scores,
            "emotions": emotion_scores,
            "intent": intent_scores,
            "message_types": message_types,
            "key_phrases": key_phrases
        }

    def get_gif_search_terms(self, message: str, analysis: Dict) -> List[str]:
        """Generate search terms for GIFs based on detailed message analysis."""
        terms = []
        
        # Add emotion-based terms
        if "emotion" in analysis:
            emotion = analysis["emotion"]
            terms.extend(self.emotion_modifiers.get(emotion, []))
        
        # Add intent-based terms
        if "intent" in analysis:
            intent = analysis["intent"]
            terms.extend(self.intent_modifiers.get(intent, []))
        
        # Add message type specific terms
        if "types" in analysis:
            for msg_type in analysis["types"]:
                terms.append(msg_type)
        
        # Add key phrases
        if "key_phrases" in analysis:
            terms.extend(analysis["key_phrases"][:2])  # Add up to 2 key phrases
        
        # Add sentiment-based terms
        if "sentiment" in analysis:
            sentiment = analysis["sentiment"]
            if sentiment > 0.5:
                terms.extend(["positive", "happy", "great"])
            elif sentiment < -0.5:
                terms.extend(["negative", "sad", "bad"])
        
        # Clean and prioritize terms
        terms = list(set(terms))  # Remove duplicates
        
        # Sort terms by relevance (emotion and intent first, then others)
        def term_priority(term):
            if "emotion" in analysis and term in self.emotion_modifiers.get(analysis["emotion"], []):
                return 0
            if "intent" in analysis and term in self.intent_modifiers.get(analysis["intent"], []):
                return 1
            if "types" in analysis and term in analysis["types"]:
                return 2
            if "key_phrases" in analysis and term in analysis["key_phrases"]:
                return 3
            return 4
        
        terms.sort(key=term_priority)
        
        # Return top 5 most relevant terms
        return terms[:5]

    def generate_reply(self, message: str) -> Tuple[str, Dict]:
        """Generate a contextual reply based on detailed message analysis."""
        # Analyze the message
        full_analysis = self.analyze_message(message)
        
        # Extract key components for reply generation
        sentiment = full_analysis["sentiment"]["compound"]
        top_emotion = full_analysis["emotions"][0]["label"]
        top_intent = full_analysis["intent"][0]["label"]
        message_types = full_analysis["message_types"]
        
        # Build response context
        context = {
            "sentiment": sentiment,
            "emotion": top_emotion,
            "intent": top_intent,
            "types": message_types,
            "key_phrases": full_analysis["key_phrases"]
        }
        
        # Return the analysis for GIF selection
        return "", context 