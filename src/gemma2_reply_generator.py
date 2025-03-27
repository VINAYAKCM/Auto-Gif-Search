# src/gemma2_reply_generator.py
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Set the model identifier to the Gemma-2 2B Italian model (or English if it's been trained accordingly).
model_name = "google/gemma-2-2b-it"

# Load the tokenizer and model.
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Initialize a text-generation pipeline.
reply_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer
)

def generate_reply(user2_message, max_length=50):
    """
    Generates a conversational reply using the Gemma-2-2b-it model.
    The prompt is formatted as:
        "User2: <user2_message>\nUser1 reply:"
    and the reply is extracted from the generated text.
    """
    prompt = f"User2: {user2_message}\nUser1 reply:"
    result = reply_pipeline(
        prompt,
        max_length=max_length,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.8,
        top_p=0.9
    )
    generated_text = result[0]['generated_text']
    
    if "User1 reply:" in generated_text:
        reply = generated_text.split("User1 reply:")[-1].strip()
    else:
        reply = generated_text.strip()
        
    return reply

if __name__ == "__main__":
    sample_message = "I feel so miserable."
    reply = generate_reply(sample_message)
    print("Gemma-2 generated reply:", reply)