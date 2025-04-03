# src/clip_module.py
import torch
import open_clip

class TextProcessor:
    def __init__(self, model_name="ViT-B/32"):
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Device set to use {self.device}")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        self.model = self.model.to(self.device)
        self.tokenizer = open_clip.get_tokenizer('ViT-B-32')

    def get_text_embedding(self, text):
        with torch.no_grad():
            text_tokens = self.tokenizer([text]).to(self.device)
            text_features = self.model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        return text_features

# Example usage:
if __name__ == "__main__":
    processor = TextProcessor()
    sample_text = "I'm feeling excited and joyful today!"
    embedding = processor.get_text_embedding(sample_text)
    print("Text Embedding:", embedding)