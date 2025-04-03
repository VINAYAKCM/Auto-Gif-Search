# src/gif_processor.py
import torch
from PIL import Image, ImageSequence
import requests
from io import BytesIO
import open_clip

class GifProcessor:
    def __init__(self, model_name="ViT-B/32"):
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        print(f"Device set to use {self.device}")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='openai')
        self.model = self.model.to(self.device)

    def open_image(self, path_or_url):
        """
        Opens an image from a local path or a URL.
        Returns a PIL Image object.
        """
        if path_or_url.startswith("http"):
            response = requests.get(path_or_url)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else:
            return Image.open(path_or_url)

    def extract_frames(self, gif_path, max_frames=5):
        """
        Extract up to max_frames from the GIF.
        Returns a list of PIL Image objects.
        """
        frames = []
        im = self.open_image(gif_path)
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            if i >= max_frames:
                break
            # Convert each frame to RGB (ensuring consistency)
            frames.append(frame.convert("RGB"))
        return frames

    def get_gif_embedding(self, gif_path, max_frames=5):
        """
        Processes a GIF: extracts frames, computes embeddings for each frame,
        and returns an averaged, normalized embedding for the GIF.
        """
        frames = self.extract_frames(gif_path, max_frames)
        embeddings = []
        with torch.no_grad():
            for frame in frames:
                # Preprocess the frame and add a batch dimension
                input_image = self.preprocess(frame).unsqueeze(0).to(self.device)
                # Get image features using CLIP's image encoder
                img_features = self.model.encode_image(input_image)
                # Normalize the embedding
                img_features = img_features / img_features.norm(dim=-1, keepdim=True)
                embeddings.append(img_features)
            # Concatenate embeddings and compute the average embedding
            avg_embedding = torch.mean(torch.cat(embeddings, dim=0), dim=0, keepdim=True)
            # Normalize the final embedding
            avg_embedding = avg_embedding / avg_embedding.norm(dim=-1, keepdim=True)
        return avg_embedding

# Example usage:
if __name__ == "__main__":
    # Replace with a valid GIF URL from Giphy
    gif_path = "https://media3.giphy.com/media/v1.Y2lkPTIyYmM2NzRidmRjanNhdXZocWIxNGV1NWg2dzN5bTI0b3l4ZW56ZndidTh2cjI0ZiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/tFSqMSMnzPRTAdvKyr/100.gif"
    processor = GifProcessor()
    gif_embedding = processor.get_gif_embedding(gif_path)
    print("GIF Embedding:", gif_embedding)