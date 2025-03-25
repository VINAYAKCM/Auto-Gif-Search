# src/clip_module.py
import torch
import clip

class TextProcessor:
    def __init__(self, model_name="ViT-B/32", device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        # Use the OpenAI clip.load() which accepts "ViT-B/32"
        self.model, self.preprocess = clip.load(model_name, device=self.device)

    def get_text_embedding(self, text: str) -> torch.Tensor:
        """
        Returns a normalized embedding for the given text.
        """
        # Tokenize the input text
        text_tokens = clip.tokenize([text]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_embedding = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
        return text_embedding

# Example usage:
if __name__ == "__main__":
    processor = TextProcessor()
    sample_text = "I'm feeling excited and joyful today!"
    embedding = processor.get_text_embedding(sample_text)
    print("Text Embedding:", embedding)