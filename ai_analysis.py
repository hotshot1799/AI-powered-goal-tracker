# ai_analysis.py

import os
from groq import Groq

# Retrieve the API key from the environment
API_KEY = os.getenv(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)

# Initialize the Groq client
client = Groq()

# Existing function modified to integrate Groq's Llama model API with API key
def analyze_data(data):
    # Ensure the API key is present
    if not API_KEY:
        raise ValueError("API key for Groq is not set. Please set the GROQ_API_KEY environment variable.")

    # Setup parameters for the Llama model in Groq
    completion = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": data}],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=True,
        stop=None,
        headers={"Authorization": f"Bearer {API_KEY}"}
    )
    
    # Stream and collect the response
    response_text = ""
    for chunk in completion:
        content = chunk.choices[0].delta.content or ""
        response_text += content
        print(content, end="")  # Print each chunk as it arrives

    print("\nLlama Model Analysis Complete.")
    return response_text

# Main execution (for testing purposes)
if __name__ == "__main__":
    # Sample data for analysis
    data = """
        Enter your text data here for analysis using the Llama model.
    """
    result = analyze_data(data)
    
    # Print the final result
    print("\nFinal Analysis Result:")
    print(result)
