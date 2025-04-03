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
            "sympathy": r'\b(sorry to hear|that\'s tough|hope you\'re okay)\b',
            "help": r'\b(help|assist|support|need|please)\b',
            "opinion": r'\b(think|believe|feel|guess|maybe|probably)\b'
        }
        
        # Emotion-specific GIF modifiers for text representation
        self.emotion_modifiers = {
            "joy": ["happy", "excited", "celebration", "cheerful"],
            "sadness": ["sad", "crying", "disappointed", "heartbroken"],
            "anger": ["angry", "mad", "frustrated", "furious"],
            "fear": ["scared", "nervous", "worried", "terrified"],
            "surprise": ["shocked", "amazed", "wow", "unexpected"],
            "disgust": ["disgusted", "gross", "ew", "yuck"],
            "neutral": ["okay", "neutral", "meh", "whatever"]
        }

        # Emotion-specific GIF modifiers for replies
        self.reply_emotion_modifiers = {
            "joy": ["celebrating with you", "happy for you", "dancing with joy"],
            "sadness": ["comforting", "sympathetic", "there there", "hugging"],
            "anger": ["calming", "understanding", "supportive reaction"],
            "fear": ["reassuring", "protective", "its okay reaction"],
            "surprise": ["shocked reaction", "surprised face", "mind blown"],
            "disgust": ["agreeing with disgust", "grossed out too"],
            "neutral": ["nodding", "listening", "understanding reaction"]
        }

        # Intent-specific GIF modifiers for text representation
        self.intent_modifiers = {
            "question": ["thinking", "confused", "wondering", "curious"],
            "statement": ["explaining", "talking", "saying", "stating"],
            "command": ["pointing", "directing", "ordering", "demanding"],
            "request": ["asking", "pleading", "requesting", "begging"],
            "opinion": ["judging", "thinking", "considering", "pondering"]
        }

        # Intent-specific GIF modifiers for replies
        self.reply_intent_modifiers = {
            "question": ["answering", "explaining reaction", "helping understand"],
            "statement": ["agreeing", "acknowledging", "reacting to statement"],
            "command": ["following along", "accepting", "yes sir reaction"],
            "request": ["granting wish", "helping out", "supportive response"],
            "opinion": ["considering opinion", "thinking about it", "processing reaction"]
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

    def get_gif_search_terms(self, message: str, analysis: Dict, is_reply: bool = False) -> List[str]:
        """Generate search terms for GIFs based on detailed message analysis."""
        terms = []
        
        # Choose appropriate modifiers based on whether this is a reply or not
        emotion_mods = self.reply_emotion_modifiers if is_reply else self.emotion_modifiers
        intent_mods = self.reply_intent_modifiers if is_reply else self.intent_modifiers
        
        # Add emotion-based terms
        if "emotion" in analysis:
            emotion = analysis["emotion"]
            terms.extend(emotion_mods.get(emotion, []))
        
        # Add intent-based terms
        if "intent" in analysis:
            intent = analysis["intent"]
            terms.extend(intent_mods.get(intent, []))
        
        # Add message type specific terms
        if "types" in analysis:
            for msg_type in analysis["types"]:
                if is_reply:
                    if msg_type == "question":
                        terms.extend(["answering question", "let me think"])
                    elif msg_type == "help":
                        terms.extend(["offering help", "supporting"])
                    elif msg_type == "greeting":
                        terms.extend(["greeting back", "waving hello"])
                    elif msg_type == "farewell":
                        terms.extend(["waving goodbye", "bye reaction"])
                    else:
                        terms.append(msg_type)
                else:
                    terms.append(msg_type)
        
        # Add key phrases
        if "key_phrases" in analysis:
            if is_reply:
                # For replies, add reaction-based versions of key phrases
                terms.extend(f"reacting to {phrase}" for phrase in analysis["key_phrases"][:2])
            else:
                terms.extend(analysis["key_phrases"][:2])
        
        # Add sentiment-based terms
        if "sentiment" in analysis:
            sentiment = analysis["sentiment"]
            if is_reply:
                if sentiment > 0.5:
                    terms.extend(["happy for you", "celebrating together", "positive reaction"])
                elif sentiment < -0.5:
                    terms.extend(["sympathetic", "supportive", "understanding reaction"])
            else:
                if sentiment > 0.5:
                    terms.extend(["positive", "happy", "great"])
                elif sentiment < -0.5:
                    terms.extend(["negative", "sad", "bad"])
        
        # Clean and prioritize terms
        terms = list(set(terms))  # Remove duplicates
        
        # Sort terms by relevance
        def term_priority(term):
            if "emotion" in analysis and term in emotion_mods.get(analysis["emotion"], []):
                return 0
            if "intent" in analysis and term in intent_mods.get(analysis["intent"], []):
                return 1
            if "types" in analysis and term in analysis["types"]:
                return 2
            if "key_phrases" in analysis and term in [f"reacting to {phrase}" for phrase in analysis["key_phrases"]]:
                return 3
            return 4
        
        terms.sort(key=term_priority)
        
        # Return top 5 most relevant terms
        return terms[:5]

    def generate_reply(self, message: str, is_reply: bool = False) -> Tuple[str, Dict]:
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