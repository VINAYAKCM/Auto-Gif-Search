# src/dialoGPT_reply_generator.py
from transformers import pipeline

# Using DialoGPT-large (you can also try DialoGPT-medium if resource-constrained)
model_name = "microsoft/DialoGPT-large"

# Initialize the text-generation pipeline
reply_pipeline = pipeline("text-generation", model=model_name, tokenizer=model_name)

def generate_reply(user2_message, max_length=50):
    """
    Generates a conversational reply using DialoGPT-large.
    The prompt is formatted as:
        "User2: <user2_message>\nUser1 reply:"
    and extracts the generated reply.
    """
    prompt = f"User2: {user2_message}\nUser1 reply:"
    result = reply_pipeline(prompt, max_length=max_length, num_return_sequences=1, do_sample=True, temperature=0.8, top_p=0.9)
    generated_text = result[0]['generated_text']
    
    # Extract the part after the prompt if possible.
    if "User1 reply:" in generated_text:
        reply = generated_text.split("User1 reply:")[-1].strip()
    else:
        reply = generated_text.strip()
    return reply

if __name__ == "__main__":
    sample_message = "I feel so miserable."
    reply = generate_reply(sample_message)
    print("DialoGPT-large generated reply:", reply)

